"""
SpatialLM structured-layout text -> PlanGrid + seats.

SpatialLM (manycore-research, NeurIPS 2025) takes a point cloud (from monocular
video via MASt3R-SLAM/SLAM3R, RGB-D, or LiDAR) and emits a structured layout:

    wall_0=Wall(ax,ay,az,bx,by,bz,height,thickness)
    door_0=Door(wall_id,position_x,position_y,position_z,width,height)
    window_0=Window(wall_id,position_x,position_y,position_z,width,height)
    bbox_0=Bbox(class,position_x,position_y,position_z,angle_z,scale_x,scale_y,scale_z)

This adapter parses that text (tolerantly) and rasterizes it into our PlanGrid,
turning their state-of-the-art layout model into a Tier-B++ front end: an
inferred plan at model confidence (0.8) instead of our geometric heuristic
(0.4). Furniture bboxes with seat-like classes also become the seat list for
attributes.sociopetal_seating — a real detector replacing manual demo boxes.

Run SpatialLM itself on a GPU machine (their repo, Python 3.11 + CUDA); only
the layout .txt travels here.
"""
from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

from ..plan import PlanGrid, FREE, OBST

SEAT_CLASSES = {"chair", "armchair", "sofa", "couch", "stool", "bench", "bed",
                "swivel chair", "office_chair", "dining_chair"}

_CALL = re.compile(r"^\s*(\w+)\s*=\s*(\w+)\s*\((.*)\)\s*$")


def parse_layout(text: str) -> Dict[str, List[dict]]:
    """Parse SpatialLM layout text into {'walls': [...], 'doors': [...],
    'windows': [...], 'bboxes': [...]}. Tolerant of extra whitespace and
    string class names with or without quotes."""
    out = {"walls": [], "doors": [], "windows": [], "bboxes": []}
    for line in text.splitlines():
        m = _CALL.match(line)
        if not m:
            continue
        name, kind, argstr = m.groups()
        args = [a.strip().strip("'\"") for a in argstr.split(",") if a.strip() != ""]

        def fl(i):
            try:
                return float(args[i])
            except (ValueError, IndexError):
                return None

        k = kind.lower()
        if k == "wall" and len(args) >= 6:
            out["walls"].append({"id": name,
                                 "a": (fl(0), fl(1), fl(2)), "b": (fl(3), fl(4), fl(5)),
                                 "height": fl(6), "thickness": fl(7) or 0.1})
        elif k in ("door", "window") and len(args) >= 4:
            entry = {"id": name, "wall_id": args[0],
                     "pos": (fl(1), fl(2), fl(3)),
                     "width": fl(4) or 0.9, "height": fl(5) or 2.0}
            out["doors" if k == "door" else "windows"].append(entry)
        elif k == "bbox" and len(args) >= 8:
            out["bboxes"].append({"id": name, "class": args[0].lower(),
                                  "pos": (fl(1), fl(2), fl(3)), "angle_z": fl(4) or 0.0,
                                  "scale": (fl(5) or 0.5, fl(6) or 0.5, fl(7) or 0.5)})
    return out


def layout_to_plangrid(layout: Dict, grid_n: int = 220, margin_m: float = 0.5,
                       doors_open: bool = True) -> Tuple[PlanGrid, List[dict]]:
    """Rasterize a parsed layout to a PlanGrid (+ seat list in grid coords).
    Walls -> OBST segments (thickness respected); doors -> gaps (traversable);
    windows -> stay solid in plan (not walkable) but are recorded in extras;
    furniture bboxes -> OBST footprints; seat-class bboxes -> seats with facing.
    """
    walls = layout["walls"]
    if not walls:
        raise ValueError("layout contains no walls")
    xs = [p for w in walls for p in (w["a"][0], w["b"][0])]
    ys = [p for w in walls for p in (w["a"][1], w["b"][1])]
    x0, x1 = min(xs) - margin_m, max(xs) + margin_m
    y0, y1 = min(ys) - margin_m, max(ys) + margin_m
    span = max(x1 - x0, y1 - y0)
    cell = span / grid_n

    def to_rc(x, y):
        c = int((x - x0) / span * (grid_n - 1))
        r = int((y1 - y) / span * (grid_n - 1))
        return r, c

    grid = np.full((grid_n, grid_n), FREE, np.int8)
    wall_px = np.zeros((grid_n, grid_n), np.uint8)
    for w in walls:
        ra, ca = to_rc(w["a"][0], w["a"][1])
        rb, cb = to_rc(w["b"][0], w["b"][1])
        t = max(1, int((w["thickness"] or 0.1) / cell))
        cv2.line(wall_px, (ca, ra), (cb, rb), 1, thickness=t)

    # doors: carve gaps in their wall
    if doors_open:
        wall_by_id = {w["id"]: w for w in walls}
        for d in layout["doors"]:
            w = wall_by_id.get(d["wall_id"])
            if not w or d["pos"][0] is None:
                continue
            r, c = to_rc(d["pos"][0], d["pos"][1])
            gap = max(2, int((d["width"] or 0.9) / cell))
            cv2.circle(wall_px, (c, r), gap // 2 + 1, 0, -1)

    grid[wall_px > 0] = OBST

    # outside = unknown (flood from corners through free space)
    ff = (grid == FREE).astype(np.uint8)
    mask = np.zeros((grid_n + 2, grid_n + 2), np.uint8)
    for seed in [(0, 0), (0, grid_n - 1), (grid_n - 1, 0), (grid_n - 1, grid_n - 1)]:
        if ff[seed[1], seed[0]]:
            cv2.floodFill(ff, mask, seed, 2)
    grid[ff == 2] = 0

    # furniture bboxes -> obstacles + seats
    seats = []
    for b in layout["bboxes"]:
        if b["pos"][0] is None:
            continue
        r, c = to_rc(b["pos"][0], b["pos"][1])
        sx = max(1, int(b["scale"][0] / cell / 2))
        sy = max(1, int(b["scale"][1] / cell / 2))
        raw = b["angle_z"] or 0.0
        # SpatialLM emits radians; tolerate degrees in hand-written files
        ang = (np.degrees(raw) if abs(raw) <= 2 * np.pi + 1e-6 else raw) % 360.0
        box = cv2.boxPoints(((c, r), (2 * sx, 2 * sy), -ang)).astype(np.int32)
        if 0 <= r < grid_n and 0 <= c < grid_n and grid[r, c] != 0:
            cv2.fillPoly(grid, [box], OBST)
        if any(s in b["class"] for s in SEAT_CLASSES):
            seats.append({"grid_rc": (r, c), "facing_deg": ang,
                          "class": b["class"], "id": b["id"]})

    pg = PlanGrid(grid, cell, None, confidence=0.8,
                  method="SpatialLM structured layout -> rasterized plan (M2.75)")
    return pg, seats
