"""Isovists and the full isovist measure set — clean-room, permissive.

An isovist is the region of space visible from a vantage point. From a 2D plan
(an occupancy grid: which cells are floor vs wall/obstacle) and a viewpoint, we
cast rays to the first occluder and derive the classical Benedikt (1979) measure
set plus the space-syntax visibility-graph measures (connectivity, mean depth,
integration, clustering). This is our own implementation — no GPL depthmapX — so
it belongs to the owned build; the research build can additionally call
depthmapX to cross-validate it.

Coordinates: points are (x, y) = (column, row); `free[y, x]` is True for
walkable/visible space.

References: Benedikt (1979), *Environment and Planning B*; Turner et al. (2001),
"From isovists to visibility graphs"; Hillier & Hanson (1984), *The Social Logic
of Space* (integration).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

Point = Tuple[float, float]


class Plan:
    """A 2D occupancy plan. `free[y, x]` True = open/visible space."""

    def __init__(self, free: np.ndarray, cell_size: float = 1.0):
        self.free = np.asarray(free, dtype=bool)
        self.h, self.w = self.free.shape
        self.cell_size = float(cell_size)

    @classmethod
    def from_walls(cls, walls: np.ndarray, cell_size: float = 1.0) -> "Plan":
        """`walls` True = obstacle."""
        return cls(~np.asarray(walls, dtype=bool), cell_size)

    @classmethod
    def from_image(cls, gray: np.ndarray, threshold: Optional[float] = None,
                   dark_is_wall: bool = True, cell_size: float = 1.0) -> "Plan":
        """Build a plan from a floor-plan raster (dark ink = walls by default)."""
        g = np.asarray(gray, dtype=float)
        if threshold is None:
            threshold = float(g.mean())
        walls = g < threshold if dark_is_wall else g > threshold
        return cls.from_walls(walls, cell_size)

    def in_bounds(self, x: float, y: float) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def is_free(self, x: float, y: float) -> bool:
        ix, iy = int(x), int(y)
        return self.in_bounds(ix, iy) and self.free[iy, ix]

    def free_points(self, stride: int = 1) -> List[Tuple[int, int]]:
        ys, xs = np.nonzero(self.free)
        pts = list(zip(xs.tolist(), ys.tolist()))
        if stride > 1:
            pts = [(x, y) for (x, y) in pts if x % stride == 0 and y % stride == 0]
        return pts


def line_of_sight(plan: Plan, p0: Point, p1: Point) -> bool:
    """True if a straight segment p0->p1 stays in free space (Bresenham/DDA)."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    steps = int(max(abs(dx), abs(dy)) * 2) + 1
    for i in range(steps + 1):
        t = i / steps
        if not plan.is_free(x0 + dx * t, y0 + dy * t):
            return False
    return True


def cast_rays(plan: Plan, origin: Point, n_rays: int = 720,
              step: float = 0.5, max_dist: Optional[float] = None):
    """Cast n_rays uniformly in [0, 2π) from origin until an occluder/boundary.

    Returns (angles, radial, hit_pts, blocked_by_wall):
      radial[i]          = distance to the first occluder along ray i
      hit_pts[i]         = (x, y) of that first occluder / boundary
      blocked_by_wall[i] = True if stopped by a real surface, False if by the
                           plan boundary (an open edge).
    """
    ox, oy = origin
    if max_dist is None:
        max_dist = math.hypot(plan.w, plan.h)
    angles = np.linspace(0.0, 2 * math.pi, n_rays, endpoint=False)
    radial = np.zeros(n_rays)
    hit_x = np.zeros(n_rays)
    hit_y = np.zeros(n_rays)
    blocked = np.zeros(n_rays, dtype=bool)
    for i, a in enumerate(angles):
        ca, sa = math.cos(a), math.sin(a)
        d = step
        last_x, last_y = ox, oy
        while d <= max_dist:
            x = ox + ca * d
            y = oy + sa * d
            if not plan.in_bounds(x, y):
                blocked[i] = False          # ran off the open edge of the plan
                break
            if not plan.free[int(y), int(x)]:
                blocked[i] = True           # hit a real surface
                break
            last_x, last_y = x, y
            d += step
        radial[i] = d
        hit_x[i] = ox + ca * d
        hit_y[i] = oy + sa * d
    return angles, radial, np.stack([hit_x, hit_y], axis=1), blocked


def isovist_measures(plan: Plan, origin: Point, n_rays: int = 720,
                     step: float = 0.5, occlusion_jump: float = 3.0) -> Dict[str, float]:
    """The full Benedikt isovist measure set at `origin`.

    Keys: area, perimeter, real_surface_perimeter, occlusivity, min_radial,
    max_radial, mean_radial, radial_variance, radial_skewness, compactness,
    circularity, elongation, jaggedness, drift_magnitude, drift_angle,
    dispersion, n_vertices, closed (all in plan/cell units).
    """
    angles, r, pts, blocked = cast_rays(plan, origin, n_rays, step)
    dtheta = 2 * math.pi / n_rays
    cs = plan.cell_size

    # Area via the fan of triangles between consecutive rays.
    r_next = np.roll(r, -1)
    area = 0.5 * math.sin(dtheta) * float(np.sum(r * r_next)) * cs * cs

    # Perimeter as the polyline through the hit points; classify each edge as
    # real surface vs occluding (radial) via depth discontinuity / open edge.
    seg = np.roll(pts, -1, axis=0) - pts
    seg_len = np.hypot(seg[:, 0], seg[:, 1]) * cs
    perimeter = float(seg_len.sum())
    depth_jump = np.abs(r - r_next) * cs
    occluding_edge = (depth_jump > occlusion_jump) | (~blocked) | (~np.roll(blocked, -1))
    occlusivity = float(seg_len[occluding_edge].sum())
    real_surface_perimeter = perimeter - occlusivity

    rr = r * cs
    min_radial = float(rr.min())
    max_radial = float(rr.max())
    mean_radial = float(rr.mean())
    var_radial = float(rr.var())
    std = math.sqrt(var_radial) if var_radial > 0 else 0.0
    skew_radial = float(((rr - mean_radial) ** 3).mean() / (std ** 3)) if std > 0 else 0.0

    # Isovist centroid and drift (vantage -> centroid).
    cx = float((pts[:, 0]).mean())
    cy = float((pts[:, 1]).mean())
    drift_mag = math.hypot(cx - origin[0], cy - origin[1]) * cs
    drift_ang = math.atan2(cy - origin[1], cx - origin[0])

    compactness = (4 * math.pi * area / (perimeter ** 2)) if perimeter > 0 else 0.0  # circularity
    elongation = (max_radial / min_radial) if min_radial > 1e-6 else float("inf")
    jaggedness = (perimeter ** 2) / area if area > 0 else float("inf")
    dispersion = std / mean_radial if mean_radial > 0 else 0.0

    return {
        "area": area,
        "perimeter": perimeter,
        "real_surface_perimeter": real_surface_perimeter,
        "occlusivity": occlusivity,
        "min_radial": min_radial,
        "max_radial": max_radial,
        "mean_radial": mean_radial,
        "radial_variance": var_radial,
        "radial_skewness": skew_radial,
        "compactness": compactness,
        "circularity": compactness,
        "elongation": elongation,
        "jaggedness": jaggedness,
        "drift_magnitude": drift_mag,
        "drift_angle": drift_ang,
        "dispersion": dispersion,
        "closed": float(bool(blocked.all())),
    }


@dataclass
class VisibilityGraphResult:
    connectivity: Dict[Tuple[int, int], int]
    mean_depth: Dict[Tuple[int, int], float]
    integration: Dict[Tuple[int, int], float]
    clustering: Dict[Tuple[int, int], float]
    intelligibility: float           # R^2 of connectivity vs integration
    mean_integration: float
    n_nodes: int


def visibility_graph(plan: Plan, stride: int = 4, max_nodes: int = 400) -> VisibilityGraphResult:
    """Space-syntax visibility-graph measures over a sampled grid of free cells.

    connectivity = # of other sampled cells visible; mean_depth = mean graph
    (visual) distance; integration = 1/RRA (Hillier); clustering = local
    clustering coefficient; intelligibility = R^2 between connectivity and
    integration (how well local view predicts global position).
    """
    pts = plan.free_points(stride=stride)
    if len(pts) > max_nodes:                       # subsample to bound O(n^2)
        idx = np.linspace(0, len(pts) - 1, max_nodes).astype(int)
        pts = [pts[i] for i in idx]
    n = len(pts)
    adj: List[set] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if line_of_sight(plan, pts[i], pts[j]):
                adj[i].add(j)
                adj[j].add(i)

    connectivity = {pts[i]: len(adj[i]) for i in range(n)}

    # BFS mean depth per node (visual steps), then RA/RRA -> integration.
    def bfs_mean_depth(src: int) -> float:
        dist = [-1] * n
        dist[src] = 0
        queue = [src]
        head = 0
        total = 0
        reached = 0
        while head < len(queue):
            u = queue[head]; head += 1
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    total += dist[v]
                    reached += 1
                    queue.append(v)
        return total / reached if reached else float("inf")

    mean_depth = {}
    integration = {}
    for i in range(n):
        md = bfs_mean_depth(i)
        mean_depth[pts[i]] = md
        if n > 2 and math.isfinite(md) and md > 1:
            ra = 2 * (md - 1) / (n - 2)
            # Teklenburg D_n normalisation factor.
            dn = (2 * (n * (math.log2((n + 2) / 3) - 1) + 1)) / ((n - 1) * (n - 2))
            rra = ra / dn if dn > 0 else float("inf")
            integration[pts[i]] = (1.0 / rra) if rra > 0 else 0.0
        else:
            integration[pts[i]] = 0.0

    # Local clustering coefficient.
    clustering = {}
    for i in range(n):
        neigh = list(adj[i])
        k = len(neigh)
        if k < 2:
            clustering[pts[i]] = 0.0
            continue
        links = 0
        for a_i in range(k):
            for b_i in range(a_i + 1, k):
                if neigh[b_i] in adj[neigh[a_i]]:
                    links += 1
        clustering[pts[i]] = 2 * links / (k * (k - 1))

    # Intelligibility: R^2 between connectivity and integration.
    c = np.array([connectivity[p] for p in pts], dtype=float)
    g = np.array([integration[p] for p in pts], dtype=float)
    if c.std() > 1e-9 and g.std() > 1e-9:
        intelligibility = float(np.corrcoef(c, g)[0, 1] ** 2)
    else:
        intelligibility = 0.0

    mean_integration = float(np.mean([integration[p] for p in pts])) if pts else 0.0
    return VisibilityGraphResult(connectivity, mean_depth, integration, clustering,
                                 intelligibility, mean_integration, n)
