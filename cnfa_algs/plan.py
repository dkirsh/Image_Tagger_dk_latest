"""
cnfa_algs.plan — Tier B/C: floor-plan fields.

Tier B ("infer a floorplan from the 2D image"):
    depth + plane labels --backproject--> ground-plane occupancy grid
    (an *inferred mini floor plan* of the visible room), then run TRUE
    plan-space algorithms on it: isovist field, prospect field, refuge
    field, prospect-refuge seat-choice map. Confidence-discounted.

Tier C (precise): the SAME functions run on a real floor plan
    (walls dark on light, or an occupancy array) — no discount.

Grid convention: int8 array; 0=unknown, 1=free, 2=wall/obstacle.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np
import cv2

from .geometry import FLOOR, WALL, CEILING, OPENING, UNKNOWN

FREE, OBST = 1, 2


@dataclass
class PlanGrid:
    grid: np.ndarray            # int8 HxW: 0 unknown, 1 free, 2 wall
    cell_m: float               # metres per cell
    camera_rc: Optional[Tuple[int, int]] = None   # camera cell (row,col), Tier B
    confidence: float = 0.5
    method: str = ""


# ------------------------------------------------------- Tier B: infer plan

def infer_plan_from_image(img_bgr: np.ndarray, planes: np.ndarray, Z: np.ndarray,
                          fov_deg: float = 65.0, grid_n: int = 180,
                          z_max: Optional[float] = None) -> PlanGrid:
    H, W = planes.shape
    f = (W / 2) / np.tan(np.radians(fov_deg / 2))
    xs = np.mgrid[0:H, 0:W][1].astype(np.float32)
    X = (xs - W / 2) / f * Z                     # lateral position (m)
    if z_max is None:
        z_max = float(np.nanpercentile(Z[planes == FLOOR], 98)) if (planes == FLOOR).any() \
                else float(np.nanpercentile(Z, 98))
    x_half = max(1.0, float(np.nanpercentile(np.abs(X[planes == FLOOR]), 98))
                 if (planes == FLOOR).any() else 3.0)
    cell = max(2 * x_half, z_max) / grid_n

    def to_rc(Xv, Zv):
        c = ((Xv + x_half) / (2 * x_half) * (grid_n - 1)).astype(int)
        r = ((z_max - Zv) / z_max * (grid_n - 1)).astype(int)   # camera at bottom
        return r, c

    grid = np.zeros((grid_n, grid_n), np.int8)
    # free space: floor pixels
    fm = (planes == FLOOR) & np.isfinite(Z) & (Z <= z_max) & (np.abs(X) <= x_half)
    r, c = to_rc(X[fm], Z[fm])
    ok = (r >= 0) & (r < grid_n) & (c >= 0) & (c < grid_n)
    np.add.at(grid, (r[ok], c[ok]), 0)          # touch
    grid[r[ok], c[ok]] = FREE
    grid = cv2.morphologyEx(grid.astype(np.uint8), cv2.MORPH_CLOSE,
                            np.ones((5, 5), np.uint8)).astype(np.int8)
    # keep only substantial connected free components (>=15% of the largest)
    nlab, lab = cv2.connectedComponents((grid == FREE).astype(np.uint8))
    if nlab > 2:
        sizes = np.bincount(lab.ravel()); sizes[0] = 0
        keep = sizes >= max(20, 0.15 * sizes.max())
        grid[(grid == FREE) & ~keep[lab]] = 0

    # obstacles: wall + furniture pixels land at their footprint depth
    om = np.isin(planes, (WALL, UNKNOWN)) & np.isfinite(Z) & (Z <= z_max) & (np.abs(X) <= x_half)
    r, c = to_rc(X[om], Z[om])
    ok = (r >= 0) & (r < grid_n) & (c >= 0) & (c < grid_n)
    obst = np.zeros_like(grid)
    np.add.at(obst, (r[ok], c[ok]), 1)
    grid[(obst > 3) & (grid != FREE)] = OBST
    # obstacles must be adjacent to observed free space (else unknown)
    freem = (grid == FREE).astype(np.uint8)
    near_free = cv2.dilate(freem, np.ones((7, 7), np.uint8)) > 0
    grid[(grid == OBST) & ~near_free] = 0
    # boundary of free region that is not open floor -> wall
    ring = cv2.dilate(freem, np.ones((3, 3), np.uint8)) - freem
    grid[(ring > 0) & (grid == 0)] = OBST

    # viewpoint = nearest free cell to the camera position (bottom center);
    # the true camera cell may be occluded by foreground furniture.
    cam0 = np.array([grid_n - 2, grid_n // 2])
    free_rc = np.argwhere(grid == FREE)
    if len(free_rc):
        cam_rc = tuple(free_rc[np.argmin(((free_rc - cam0) ** 2).sum(1))])
    else:
        cam_rc = tuple(cam0)
        grid[cam_rc[0], cam_rc[1]] = FREE
    return PlanGrid(grid, cell, cam_rc, confidence=0.4,
                    method="inferred plan: depth backprojection of floor + footprints; "
                           "viewpoint = nearest visible-floor cell to camera (M2.5)")


# ------------------------------------------------------- Tier C: real plan

def plan_from_floorplan_image(plan_bgr: np.ndarray, cell_m: float = 0.08,
                              grid_n: int = 220) -> PlanGrid:
    """Walls dark on light background. Tier C — precise."""
    g = cv2.cvtColor(plan_bgr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (grid_n, grid_n), interpolation=cv2.INTER_AREA)
    walls = (g < 128)
    grid = np.full((grid_n, grid_n), FREE, np.int8)
    grid[walls] = OBST
    # outside the outer wall = unknown: flood fill from corners
    ff = (grid == FREE).astype(np.uint8)
    mask = np.zeros((grid_n + 2, grid_n + 2), np.uint8)
    for seed in [(0, 0), (0, grid_n - 1), (grid_n - 1, 0), (grid_n - 1, grid_n - 1)]:
        if ff[seed[1], seed[0]]:
            cv2.floodFill(ff, mask, seed, 2)
    grid[ff == 2] = 0
    return PlanGrid(grid, cell_m, None, confidence=0.95,
                    method="supplied floor plan (M3, precise)")


# --------------------------------------------------------------- ray fields

_ANGLES = None


def _ray_directions(n_rays: int):
    global _ANGLES
    if _ANGLES is None or len(_ANGLES) != n_rays:
        a = np.linspace(0, 2 * np.pi, n_rays, endpoint=False)
        _ANGLES = np.stack([np.sin(a), np.cos(a)], 1)  # (dr, dc)
    return _ANGLES


def isovist_fields(pg: PlanGrid, n_rays: int = 72, stride: int = 2,
                   refuge_radius_m: float = 1.0) -> Dict[str, np.ndarray]:
    """For every free cell: openness (mean radial), prospect (max radial),
    refuge (blocked-direction fraction within radius), compactness,
    and the prospect-refuge seat-choice map PR = .65*prospect + .35*refuge."""
    grid = pg.grid
    Hn, Wn = grid.shape
    dirs = _ray_directions(n_rays)
    max_steps = int(np.hypot(Hn, Wn))
    blocked = (grid != FREE)

    openness = np.full((Hn, Wn), np.nan, np.float32)
    prospectf = np.full((Hn, Wn), np.nan, np.float32)
    refuge = np.full((Hn, Wn), np.nan, np.float32)
    compact = np.full((Hn, Wn), np.nan, np.float32)
    rref = max(2, int(refuge_radius_m / pg.cell_m))

    free_cells = np.argwhere(grid == FREE)[::stride]
    for (r0, c0) in free_cells:
        radii = np.empty(n_rays, np.float32)
        for k, (dr, dc) in enumerate(dirs):
            step, rr, cc = 0, float(r0), float(c0)
            while True:
                step += 1
                rr += dr; cc += dc
                ri, ci = int(rr), int(cc)
                if ri < 0 or ri >= Hn or ci < 0 or ci >= Wn or blocked[ri, ci] or step >= max_steps:
                    break
            radii[k] = step
        openness[r0, c0] = radii.mean()
        prospectf[r0, c0] = radii.max()
        refuge[r0, c0] = float((radii <= rref).mean())
        # polar polygon area & perimeter -> compactness
        A = 0.5 * np.sum(radii ** 2) * (2 * np.pi / n_rays)
        pts = radii[:, None] * dirs
        P = np.sum(np.linalg.norm(np.roll(pts, -1, 0) - pts, axis=1)) + 1e-6
        compact[r0, c0] = float(4 * np.pi * A / P ** 2)

    def _fill(f):
        m = np.isnan(f) & (grid == FREE)
        if m.any():
            f = cv2.inpaint((np.nan_to_num(f) * 1).astype(np.float32),
                            m.astype(np.uint8), 3, cv2.INPAINT_NS) if stride > 1 else f
        return f

    openness, prospectf, refuge, compact = map(_fill, (openness, prospectf, refuge, compact))

    def _n01(f):
        v = f[grid == FREE]
        lo, hi = np.nanpercentile(v, 2), np.nanpercentile(v, 98)
        return np.where(grid == FREE, np.clip((f - lo) / (hi - lo + 1e-9), 0, 1), np.nan)

    o, p, rf, cp = _n01(openness), _n01(prospectf), _n01(refuge), _n01(compact)
    pr = 0.65 * p + 0.35 * rf
    return {"openness": o, "prospect": p, "refuge": rf, "compactness": cp,
            "prospect_refuge": pr,
            "openness_raw_m": openness * pg.cell_m}


def camera_isovist_polygon(pg: PlanGrid, n_rays: int = 180) -> np.ndarray:
    """Isovist polygon from the camera cell (Tier B) in grid coords."""
    if pg.camera_rc is None:
        return np.zeros((0, 2))
    r0, c0 = pg.camera_rc
    dirs = _ray_directions(n_rays)
    blocked = (pg.grid != FREE)
    Hn, Wn = pg.grid.shape
    pts = []
    for (dr, dc) in dirs:
        rr, cc = float(r0), float(c0)
        while True:
            rr += dr; cc += dc
            ri, ci = int(rr), int(cc)
            if ri < 0 or ri >= Hn or ci < 0 or ci >= Wn or blocked[ri, ci]:
                break
        pts.append([ci, ri])
    return np.array(pts)


# ---------------------------------------------------------------- rendering

def render_plan_topo(pg: PlanGrid, field01: np.ndarray, title: str,
                     iso_polygon: Optional[np.ndarray] = None,
                     px: int = 460) -> np.ndarray:
    """Matplotlib topo map: filled contours + iso-lines + walls + camera."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grid = pg.grid
    # crop to content bbox + margin for a readable plot
    ys, xs = np.where(grid != 0)
    if len(ys):
        m = 6
        r0, r1 = max(0, ys.min() - m), min(grid.shape[0], ys.max() + m)
        c0, c1 = max(0, xs.min() - m), min(grid.shape[1], xs.max() + m)
        grid = grid[r0:r1, c0:c1]
        field01 = field01[r0:r1, c0:c1]
        pg = PlanGrid(grid, pg.cell_m,
                      None if pg.camera_rc is None else (pg.camera_rc[0] - r0, pg.camera_rc[1] - c0),
                      pg.confidence, pg.method)
        if iso_polygon is not None and len(iso_polygon):
            iso_polygon = iso_polygon - np.array([c0, r0])
    fig, ax = plt.subplots(figsize=(px / 100, px / 100), dpi=100)
    f = np.ma.masked_invalid(field01)
    ax.contourf(f, levels=12, cmap="turbo")
    cs = ax.contour(f, levels=8, colors="white", linewidths=0.6)
    ax.clabel(cs, inline=True, fontsize=5, fmt="%.1f")
    wy, wx = np.where(grid == OBST)
    ax.scatter(wx, wy, s=1.2, c="black", marker="s")
    uy, ux = np.where(grid == 0)
    ax.scatter(ux, uy, s=0.4, c="#666666", marker=".", alpha=0.25)
    if iso_polygon is not None and len(iso_polygon):
        ax.plot(np.append(iso_polygon[:, 0], iso_polygon[0, 0]),
                np.append(iso_polygon[:, 1], iso_polygon[0, 1]),
                c="magenta", lw=1.2, label="camera isovist")
    if pg.camera_rc is not None:
        ax.scatter([pg.camera_rc[1]], [pg.camera_rc[0]], s=60, c="magenta", marker="^")
    ax.set_title(title, fontsize=8)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_aspect("equal")
    ax.invert_yaxis()  # row 0 at top, aligned across contours/scatter
    fig.tight_layout(pad=0.3)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[..., :3]
    plt.close(fig)
    return cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)
