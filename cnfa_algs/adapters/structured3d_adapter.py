"""
Structured3D annotation_3d.json -> ground-truth PlanGrid.

Structured3D encodes each scene as junctions / lines / planes with semantic
types ('floor', 'ceiling', 'wall', 'door', 'window'). For the L0 validator we
need the true floor plan: floor-plane polygons = free space; wall planes
projected to the ground = obstacles; door polygons = gaps.

Best-effort parser written against the published format (junctions +
planeLineMatrix + lineJunctionMatrix + semantics); verify against the first
real scene when the annotation zip lands and adjust if their field names
drifted between releases.
"""
from __future__ import annotations
import json
from typing import Dict, List, Tuple
import numpy as np
import cv2

from ..plan import PlanGrid, FREE, OBST


def _plane_polygons(ann: Dict) -> List[Tuple[str, np.ndarray]]:
    """Return [(plane_type, polygon_xy)] by walking plane->lines->junctions."""
    junctions = np.array([j["coordinate"] for j in ann["junctions"]], float)
    lineJ = np.array(ann["lineJunctionMatrix"], dtype=bool)   # lines x junctions
    planeL = np.array(ann["planeLineMatrix"], dtype=bool)     # planes x lines
    out = []
    for pi, plane in enumerate(ann["planes"]):
        ptype = plane.get("type", "")
        line_ids = np.where(planeL[pi])[0]
        # collect this plane's junctions via its lines
        j_ids = sorted({j for li in line_ids for j in np.where(lineJ[li])[0]})
        min_pts = 2 if ptype == "wall" else 3   # walls project to segments
        if len(j_ids) < min_pts:
            continue
        pts = junctions[j_ids][:, :2]
        # order vertices around centroid (planes are near-convex loops in xy
        # for floors; walls project to segments)
        ctr = pts.mean(0)
        order = np.argsort(np.arctan2(pts[:, 1] - ctr[1], pts[:, 0] - ctr[0]))
        out.append((ptype, pts[order]))
    return out


def annotation_to_plangrid(json_path: str, grid_n: int = 260,
                           margin_m: float = 0.3) -> PlanGrid:
    ann = json.load(open(json_path))
    polys = _plane_polygons(ann)
    floors = [p for t, p in polys if t == "floor"]
    walls = [p for t, p in polys if t == "wall"]
    doors = [p for t, p in polys if t == "door"]
    if not floors:
        raise ValueError(f"no floor planes parsed from {json_path}")

    allpts = np.vstack(floors) / 1000.0   # Structured3D uses millimetres
    x0, y0 = allpts.min(0) - margin_m
    x1, y1 = allpts.max(0) + margin_m
    span = max(x1 - x0, y1 - y0)
    cell = span / grid_n

    def to_px(poly_mm):
        p = poly_mm / 1000.0
        c = ((p[:, 0] - x0) / span * (grid_n - 1)).astype(np.int32)
        r = ((y1 - p[:, 1]) / span * (grid_n - 1)).astype(np.int32)
        return np.stack([c, r], 1)

    grid = np.zeros((grid_n, grid_n), np.int8)          # unknown outside
    for f in floors:
        cv2.fillPoly(grid, [to_px(f)], FREE)
    for w in walls:                                     # wall footprint segments
        px = to_px(w)
        for i in range(len(px)):
            cv2.line(grid, tuple(px[i]), tuple(px[(i + 1) % len(px)]), OBST, 2)
    for d in doors:                                     # doors reopen gaps
        px = to_px(d)
        cv2.fillPoly(grid, [px], FREE)

    return PlanGrid(grid, cell, None, confidence=0.98,
                    method=f"Structured3D annotation_3d ground truth ({json_path})")


def plan_iou(pred: PlanGrid, truth: PlanGrid) -> Dict[str, float]:
    """Score an inferred plan against ground truth: free-space IoU after
    resampling to the truth grid, plus boundary chamfer distance (cells)."""
    a = cv2.resize((pred.grid == FREE).astype(np.uint8),
                   truth.grid.shape[::-1], interpolation=cv2.INTER_NEAREST)
    b = (truth.grid == FREE).astype(np.uint8)
    inter, union = float((a & b).sum()), float((a | b).sum())
    iou = inter / union if union else 0.0
    # boundary chamfer
    ea = cv2.Canny(a * 255, 50, 150) > 0
    eb = cv2.Canny(b * 255, 50, 150) > 0
    if ea.any() and eb.any():
        db = cv2.distanceTransform((~eb).astype(np.uint8), cv2.DIST_L2, 3)
        chamfer = float(db[ea].mean())
    else:
        chamfer = float("nan")
    return {"free_space_iou": round(iou, 3),
            "boundary_chamfer_cells": round(chamfer, 2),
            "boundary_chamfer_m": round(chamfer * truth.cell_m, 3)}
