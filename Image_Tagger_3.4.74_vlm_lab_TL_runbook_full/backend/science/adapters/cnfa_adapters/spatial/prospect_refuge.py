"""Prospect, refuge, privacy, dead-ground and first-detection — on the isovist.

Corrects the naive `prospect = isovist_area` proxy. Prospect is surveillance of
the *approach*: warning depth (how far you see) + freedom from dead ground
(near-field space you cannot see, through which a covert approach is possible).
The payoff metric is `first_detection_distance`: for the least-visible
("stalker's") path to a position, the range at which the intruder first enters
that position's isovist.

Also provides the privacy/exposure and social-co-visibility measures:
  * refuge/enclosure  — solid-boundary fraction of the isovist;
  * visual_exposure   — how visible a position is from a public set (privacy = 1 - exposure);
  * dead_ground_ratio — near-field unseen fraction within a threat radius;
  * first_detection_distance — min-exposure path detection range;
  * social co-visibility — integrated/occupied space you can see (interaction potential).

References: Appleton 1975; Benedikt 1979; Fisher & Nasar 1992 (prospect-refuge-
escape, offender concealment); Nasar, Fisher & Grannis 1993; Marzouqi & Jarvis
2011 (covert path planning); Hillier & Hanson 1984 (integration/co-presence).
"""
from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..base import AnalyzerAdapter, License
from .isovist import Plan, isovist_measures, line_of_sight, visibility_graph

Point = Tuple[float, float]


def visible_mask(plan: Plan, origin: Point, n_rays: int = 1440, step: float = 0.5) -> np.ndarray:
    """Boolean grid of free cells visible from `origin` (ray-march fill)."""
    mask = np.zeros_like(plan.free, dtype=bool)
    ox, oy = origin
    max_d = math.hypot(plan.w, plan.h)
    for a in np.linspace(0.0, 2 * math.pi, n_rays, endpoint=False):
        ca, sa = math.cos(a), math.sin(a)
        d = 0.0
        while d <= max_d:
            x = ox + ca * d
            y = oy + sa * d
            ix, iy = int(x), int(y)
            if not plan.in_bounds(x, y) or not plan.free[iy, ix]:
                break
            mask[iy, ix] = True
            d += step
    if plan.in_bounds(*origin):
        mask[int(oy), int(ox)] = True
    return mask


def default_entrances(plan: Plan) -> List[Tuple[int, int]]:
    """Free cells touching the plan boundary = 'coming from outside'. Falls back
    to nothing if the plan is fully walled."""
    ent = []
    h, w = plan.h, plan.w
    ys, xs = np.nonzero(plan.free)
    for x, y in zip(xs.tolist(), ys.tolist()):
        if x == 0 or y == 0 or x == w - 1 or y == h - 1:
            ent.append((x, y))
    return ent


def dead_ground_ratio(plan: Plan, origin: Point, threat_radius: float,
                      vmask: Optional[np.ndarray] = None) -> float:
    """Fraction of free space within `threat_radius` of origin that is NOT
    visible from origin (the covert-approach lane)."""
    if vmask is None:
        vmask = visible_mask(plan, origin)
    yy, xx = np.indices(plan.free.shape)
    within = (np.hypot(xx - origin[0], yy - origin[1]) <= threat_radius) & plan.free
    n = int(within.sum())
    if n == 0:
        return 0.0
    dead = within & ~vmask
    return float(dead.sum()) / n


def visual_exposure(plan: Plan, target: Point,
                    public_cells: Sequence[Tuple[int, int]]) -> float:
    """Fraction of `public_cells` with line of sight to `target`. Privacy = 1 - this."""
    if not public_cells:
        return 0.0
    seen = sum(1 for p in public_cells if line_of_sight(plan, p, target))
    return seen / len(public_cells)


def first_detection_distance(plan: Plan, target: Point,
                             entrances: Sequence[Tuple[int, int]],
                             penalty: float = 6.0,
                             vmask: Optional[np.ndarray] = None,
                             cell_size: Optional[float] = None) -> Optional[float]:
    """Range at which a minimum-exposure approach to `target` is first seen.

    Dijkstra from `entrances` over free cells, where stepping into a cell
    visible from the target costs `penalty` extra (so the path hugs dead
    ground). Then walk the path outward from the target: the distance to the
    first cell that is NOT visible is where the intruder becomes visible.
    Large = good prospect (seen from far off); small = ambushable.
    """
    if vmask is None:
        vmask = visible_mask(plan, target)
    if cell_size is None:
        cell_size = plan.cell_size
    h, w = plan.h, plan.w
    tx, ty = int(round(target[0])), int(round(target[1]))
    if not plan.free[ty, tx]:
        return None
    entrances = [(int(ex), int(ey)) for ex, ey in entrances
                 if plan.in_bounds(ex, ey) and plan.free[int(ey), int(ex)]]
    if not entrances:
        return None

    INF = float("inf")
    dist = np.full((h, w), INF)
    prev = {}
    heap = []
    for ex, ey in entrances:
        c = 1.0 + (penalty if vmask[ey, ex] else 0.0)
        if c < dist[ey, ex]:
            dist[ey, ex] = c
            heapq.heappush(heap, (c, (ex, ey)))
    target_cell = (tx, ty)
    while heap:
        d, (x, y) = heapq.heappop(heap)
        if d > dist[y, x]:
            continue
        if (x, y) == target_cell:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or not plan.free[ny, nx]:
                continue
            step_cost = 1.0 + (penalty if vmask[ny, nx] else 0.0)
            nd = d + step_cost
            if nd < dist[ny, nx]:
                dist[ny, nx] = nd
                prev[(nx, ny)] = (x, y)
                heapq.heappush(heap, (nd, (nx, ny)))
    if not np.isfinite(dist[ty, tx]):
        return None

    # reconstruct path target -> entrance, walk outward to first non-visible cell
    path = [target_cell]
    cur = target_cell
    while cur in prev:
        cur = prev[cur]
        path.append(cur)
    for (px, py) in path:
        if not vmask[py, px]:
            return float(math.hypot(px - target[0], py - target[1]) * cell_size)
    # entire approach visible -> detection at the entrance (best case)
    ex, ey = path[-1]
    return float(math.hypot(ex - target[0], ey - target[1]) * cell_size)


def social_covisibility(plan: Plan, origin: Point, stride: int = 4,
                        vmask: Optional[np.ndarray] = None) -> float:
    """Integration-weighted visible area — how much *used* space you can see
    (interaction potential). Sum of visibility-graph integration over sampled
    cells visible from origin, normalised by the graph's total integration."""
    if vmask is None:
        vmask = visible_mask(plan, origin)
    vg = visibility_graph(plan, stride=stride)
    tot = sum(vg.integration.values()) or 1.0
    seen = 0.0
    for (x, y), integ in vg.integration.items():
        if vmask[y, x]:
            seen += integ
    return float(seen / tot)


def annotate_prospect_refuge(plan: Plan, viewpoint: Point,
                             entrances: Optional[Sequence[Tuple[int, int]]] = None,
                             public_cells: Optional[Sequence[Tuple[int, int]]] = None,
                             threat_radius: Optional[float] = None,
                             with_social: bool = True) -> Dict[str, float]:
    """The full prospect/refuge/privacy/dead-ground/first-detection bundle."""
    out: Dict[str, float] = {}
    m = isovist_measures(plan, viewpoint)
    vmask = visible_mask(plan, viewpoint)
    if threat_radius is None:
        threat_radius = min(plan.h, plan.w) / 4.0
    if entrances is None:
        entrances = default_entrances(plan)
    if public_cells is None:
        public_cells = entrances

    # prospect = warning depth (max sightline), not area
    out["cnfa.spatial.prospect_depth"] = float(m["max_radial"])
    # refuge = solid-boundary fraction (enclosure)
    peri = m["perimeter"] or 1.0
    enclosure = max(0.0, min(1.0, m["real_surface_perimeter"] / peri))
    out["cnfa.spatial.refuge_enclosure"] = enclosure
    # dead ground (near-field unseen)
    out["cnfa.spatial.dead_ground_ratio"] = dead_ground_ratio(plan, viewpoint, threat_radius, vmask)
    # first-detection distance (min-exposure path)
    fdd = first_detection_distance(plan, viewpoint, entrances, vmask=vmask)
    if fdd is not None:
        out["cnfa.spatial.first_detection_distance"] = fdd
    # exposure / privacy
    exp = visual_exposure(plan, viewpoint, public_cells)
    out["cnfa.spatial.visual_exposure"] = exp
    out["cnfa.spatial.privacy_index"] = 1.0 - exp
    # prospect-refuge index: long warning depth AND enclosed AND low dead ground
    depth_norm = min(1.0, m["max_radial"] / (math.hypot(plan.w, plan.h) * plan.cell_size))
    out["cnfa.spatial.prospect_refuge_index"] = float(
        depth_norm * enclosure * (1.0 - out["cnfa.spatial.dead_ground_ratio"]))
    if with_social:
        out["cnfa.social.covisibility_potential"] = social_covisibility(plan, viewpoint, vmask=vmask)
    return out


class ProspectRefugeAdapter(AnalyzerAdapter):
    """Emit prospect/refuge/privacy/dead-ground/first-detection from a plan.

    Reads frame.plan (Plan) + frame.viewpoint (x, y); optional frame.entrances,
    frame.public_set, frame.threat_radius. No-ops on image-only frames. Owned
    (clean-room) build.
    """

    name = "prospect_refuge"
    tool = "cnfa-prospect-refuge(clean-room)"
    tool_version = "1.0"
    license_class = License.PERMISSIVE
    enable_flag = "enable_prospect_refuge"
    requires = ()
    provides = (
        "cnfa.spatial.prospect_depth",
        "cnfa.spatial.refuge_enclosure",
        "cnfa.spatial.dead_ground_ratio",
        "cnfa.spatial.first_detection_distance",
        "cnfa.spatial.visual_exposure",
        "cnfa.spatial.privacy_index",
        "cnfa.spatial.prospect_refuge_index",
        "cnfa.social.covisibility_potential",
    )

    def _analyze(self, frame) -> None:
        plan = getattr(frame, "plan", None)
        viewpoint = getattr(frame, "viewpoint", None)
        if plan is None or viewpoint is None:
            return
        bundle = annotate_prospect_refuge(
            plan, viewpoint,
            entrances=getattr(frame, "entrances", None),
            public_cells=getattr(frame, "public_set", None),
            threat_radius=getattr(frame, "threat_radius", None),
            with_social=getattr(frame, "social_covisibility", True),
        )
        for key, value in bundle.items():
            self.emit(frame, key, value)
