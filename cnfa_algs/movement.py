"""
cnfa_algs.movement — plan-level MOVEMENT & PROXIMITY metrics (CRITERIA.md C5, C6, C15).

Converts three ○ ("to build") criteria in CRITERIA.md into real algorithms on the
existing PlanGrid (plan.py: grid HxW with FREE=1/OBST=2/0=unknown, cell_m metres):

  C5  collaborator_proximity  — walking distance between must-collaborate seat pairs,
                                same-region check, cross-region ("cross-floor") penalty.
  C6  path_overlap            — shared route length between desk pairs to common
                                destinations (collision/collaboration potential).
  C15 amenity_distance        — mean/distribution of seat->nearest-amenity walking
                                distance (active-design "short walk" band).
      stair_prominence        — stair inside the entrance isovist AND nearer than the
                                elevator (active-design stair-first rule, C15/D1).

All distances are true GEODESIC (network) distances over free space, not Euclidean —
which is the whole point (functional/path proximity beats straight-line; STATE_OF_
KNOWLEDGE A5). Uses skimage.graph.MCP_Geometric (Dijkstra with correct diagonal
metric + path traceback); a manual heap-Dijkstra fallback is provided if skimage is
absent so the module never hard-fails.

Self-test (analytic L0 ground truth):
    python -m cnfa_algs.movement
"""
from __future__ import annotations
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

try:                                    # plan-grid constants (match plan.py)
    from .plan import FREE, OBST, PlanGrid
except Exception:                       # allow standalone import in tests
    FREE, OBST = 1, 2
    PlanGrid = None

RC = Tuple[int, int]                    # (row, col) cell


# --------------------------------------------------------------------------- core
def _grid_of(pg) -> np.ndarray:
    return pg.grid if hasattr(pg, "grid") else np.asarray(pg)


def _cell_m(pg) -> float:
    return float(getattr(pg, "cell_m", 1.0))


def _costs(grid: np.ndarray) -> np.ndarray:
    """Traversal-cost array for MCP: 1.0 on FREE, +inf elsewhere."""
    c = np.full(grid.shape, np.inf, dtype=float)
    c[grid == FREE] = 1.0
    return c


def geodesic_field(pg, source: RC) -> np.ndarray:
    """Geodesic distance (METRES) from `source` to every free cell; inf elsewhere.

    Distance is the length of the shortest path *through free space*, with diagonal
    steps correctly weighted sqrt(2). Off-region / unreachable cells are +inf."""
    grid = _grid_of(pg)
    if grid[source[0], source[1]] != FREE:
        # snap source to the nearest free cell (callers often pass approximate seats)
        source = _nearest_free(grid, source)
    cells_dist = _mcp_costs(grid, [source])
    return cells_dist * _cell_m(pg)


def walking_distance_m(pg, a: RC, b: RC) -> Tuple[float, List[RC]]:
    """Geodesic distance (metres) and the path (list of cells) between two cells."""
    grid = _grid_of(pg)
    a = a if grid[a[0], a[1]] == FREE else _nearest_free(grid, a)
    b = b if grid[b[0], b[1]] == FREE else _nearest_free(grid, b)
    dist_cells, path = _mcp_path(grid, a, b)
    return dist_cells * _cell_m(pg), path


# ------------------------------------------------------- MCP (skimage) + fallback
def _mcp_costs(grid: np.ndarray, sources: List[RC]) -> np.ndarray:
    try:
        from skimage.graph import MCP_Geometric
        mcp = MCP_Geometric(_costs(grid))
        cum, _ = mcp.find_costs(sources)
        cum = np.asarray(cum, float)
        cum[~np.isfinite(cum)] = np.inf
        return cum
    except Exception:
        return _dijkstra_field(grid, sources)


def _mcp_path(grid: np.ndarray, a: RC, b: RC) -> Tuple[float, List[RC]]:
    try:
        from skimage.graph import MCP_Geometric
        mcp = MCP_Geometric(_costs(grid))
        cum, _ = mcp.find_costs([a])
        d = float(cum[b[0], b[1]])
        if not np.isfinite(d):
            return np.inf, []
        return d, [tuple(p) for p in mcp.traceback(b)]
    except Exception:
        field = _dijkstra_field(grid, [a])
        d = float(field[b[0], b[1]])
        return (d if np.isfinite(d) else np.inf), []


def _dijkstra_field(grid: np.ndarray, sources: List[RC]) -> np.ndarray:
    """Heap Dijkstra fallback (8-connected, sqrt2 diagonals), distance in CELLS."""
    import heapq
    H, W = grid.shape
    INF = np.inf
    dist = np.full((H, W), INF)
    pq = []
    for r, c in sources:
        dist[r, c] = 0.0
        heapq.heappush(pq, (0.0, r, c))
    nbrs = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.4142135623730951), (-1, 1, 1.4142135623730951),
            (1, -1, 1.4142135623730951), (1, 1, 1.4142135623730951)]
    while pq:
        d, r, c = heapq.heappop(pq)
        if d > dist[r, c]:
            continue
        for dr, dc, w in nbrs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W and grid[nr, nc] == FREE:
                nd = d + w
                if nd < dist[nr, nc]:
                    dist[nr, nc] = nd
                    heapq.heappush(pq, (nd, nr, nc))
    return dist


def _nearest_free(grid: np.ndarray, rc: RC) -> RC:
    free = np.argwhere(grid == FREE)
    if len(free) == 0:
        raise ValueError("PlanGrid has no free cells")
    d2 = (free[:, 0] - rc[0]) ** 2 + (free[:, 1] - rc[1]) ** 2
    return tuple(free[int(d2.argmin())])


def _region_labels(grid: np.ndarray) -> np.ndarray:
    """Connected free-space regions (8-conn). Region id 0 = non-free."""
    try:
        import cv2
        n, lab = cv2.connectedComponents((grid == FREE).astype(np.uint8), connectivity=8)
        return lab
    except Exception:
        from scipy.ndimage import label
        lab, _ = label(grid == FREE, structure=np.ones((3, 3)))
        return lab


# ---------------------------------------------------------------- C5: collaborator proximity
def collaborator_proximity(pg, seats: Sequence[RC],
                           pairs: Sequence[Tuple[int, int]],
                           max_m: float = 40.0) -> Dict:
    """C5 — for each must-collaborate seat PAIR (indices into `seats`): geodesic
    walking distance, whether both seats are in the same free region (proxy for
    same-floor/corridor), and a heavy penalty for cross-region splits.

    Returns per-pair rows + summary. STATE_OF_KNOWLEDGE C5 threshold: same-floor &
    corridor, <= ~30-50 m; cross-floor splits heavily penalized."""
    grid = _grid_of(pg)
    lab = _region_labels(grid)
    rows = []
    for (i, j) in pairs:
        si = seats[i] if grid[seats[i][0], seats[i][1]] == FREE else _nearest_free(grid, seats[i])
        sj = seats[j] if grid[seats[j][0], seats[j][1]] == FREE else _nearest_free(grid, seats[j])
        same_region = bool(lab[si[0], si[1]] == lab[sj[0], sj[1]] and lab[si[0], si[1]] != 0)
        if same_region:
            d, _ = walking_distance_m(pg, si, sj)
        else:
            d = np.inf                          # cross-region: no walking path
        rows.append({"pair": (int(i), int(j)), "walk_m": (None if not np.isfinite(d) else round(float(d), 2)),
                     "same_region": same_region,
                     "over_threshold": bool((not np.isfinite(d)) or d > max_m),
                     "cross_region_split": (not same_region)})
    reachable = [r["walk_m"] for r in rows if r["walk_m"] is not None]
    n = len(rows)
    n_ok = sum(1 for r in rows if not r["over_threshold"])
    n_split = sum(1 for r in rows if r["cross_region_split"])
    return {"key": "cnfa.plan.collaborator_proximity", "criterion": "C5",
            "rows": rows,
            "scalar": (round(n_ok / n, 3) if n else None),   # fraction of pairs within threshold
            "extras": {"median_walk_m": (round(float(np.median(reachable)), 2) if reachable else None),
                       "n_pairs": n, "n_within_threshold": n_ok,
                       "n_cross_region_splits": n_split, "max_m": max_m},
            "confidence": 0.6,
            "method": "geodesic MCP walking distance on PlanGrid free-space + region containment",
            "failure_modes": ["region==floor is a proxy (single-plan; multi-floor needs stacked grids)",
                              "seats snapped to nearest free cell if off-grid",
                              "interdependence/demand profile must be supplied (which pairs)"]}


# ---------------------------------------------------------------- C6: path overlap
def path_overlap(pg, seats: Sequence[RC],
                 destinations: Sequence[RC]) -> Dict:
    """C6 — shared route length between desk pairs on the way to their nearest common
    destination. Each seat routes to its nearest destination; the overlap of two seats'
    paths (shared cells x cell_m) is the collision/collaboration potential. Gate by
    interdependence upstream (only score interdependent pairs)."""
    grid = _grid_of(pg)
    cm = _cell_m(pg)
    # each seat's path to its nearest destination
    seat_paths: List[set] = []
    seat_dest = []
    for s in seats:
        s = s if grid[s[0], s[1]] == FREE else _nearest_free(grid, s)
        best = (np.inf, [], None)
        for k, dst in enumerate(destinations):
            dst2 = dst if grid[dst[0], dst[1]] == FREE else _nearest_free(grid, dst)
            d, path = walking_distance_m(pg, s, dst2)
            if d < best[0]:
                best = (d, path, k)
        seat_paths.append(set(best[1]))
        seat_dest.append(best[2])
    rows = []
    N = len(seats)
    for i in range(N):
        for j in range(i + 1, N):
            shared = len(seat_paths[i] & seat_paths[j])
            if shared:
                rows.append({"pair": (i, j), "overlap_m": round(shared * cm, 2),
                             "same_destination": bool(seat_dest[i] == seat_dest[j])})
    rows.sort(key=lambda r: -r["overlap_m"])
    overlaps = [r["overlap_m"] for r in rows]
    return {"key": "cnfa.plan.path_overlap", "criterion": "C6",
            "rows": rows,
            "scalar": (round(float(np.mean(overlaps)), 2) if overlaps else 0.0),
            "extras": {"n_pairs_with_overlap": len(rows),
                       "max_overlap_m": (max(overlaps) if overlaps else 0.0)},
            "confidence": 0.55,
            "method": "geodesic path traceback (MCP) -> shared-cell length between seat pairs",
            "failure_modes": ["single nearest-destination per seat (extend to multi-destination)",
                              "overlap needs interdependence gating to be meaningful (C6 direction)",
                              "traceback unavailable in Dijkstra fallback -> overlap 0 (install skimage)"]}


# ---------------------------------------------------------------- C15: amenity distance
def amenity_distance(pg, seats: Sequence[RC],
                     amenities: Sequence[RC],
                     short_band_m: Tuple[float, float] = (10.0, 60.0)) -> Dict:
    """C15 — per-seat geodesic distance to the NEAREST amenity; summary + fraction of
    seats inside the 'designed short walk' band (not minimized, not excessive)."""
    grid = _grid_of(pg)
    # one geodesic field per amenity, take per-cell min
    fields = []
    for a in amenities:
        a = a if grid[a[0], a[1]] == FREE else _nearest_free(grid, a)
        fields.append(geodesic_field(pg, a))
    if not fields:
        return {"key": "cnfa.plan.amenity_distance", "criterion": "C15", "scalar": None,
                "rows": [], "extras": {}, "confidence": 0.0, "method": "no amenities given",
                "failure_modes": ["no amenities supplied"]}
    nearest = np.min(np.stack(fields, 0), axis=0)
    rows, dists = [], []
    lo, hi = short_band_m
    for k, s in enumerate(seats):
        s = s if grid[s[0], s[1]] == FREE else _nearest_free(grid, s)
        d = float(nearest[s[0], s[1]])
        in_band = bool(np.isfinite(d) and lo <= d <= hi)
        rows.append({"seat": k, "nearest_amenity_m": (None if not np.isfinite(d) else round(d, 2)),
                     "in_short_walk_band": in_band})
        if np.isfinite(d):
            dists.append(d)
    n_band = sum(1 for r in rows if r["in_short_walk_band"])
    return {"key": "cnfa.plan.amenity_distance", "criterion": "C15",
            "rows": rows,
            "scalar": (round(n_band / len(seats), 3) if seats else None),  # fraction in band
            "field": nearest,
            "extras": {"mean_m": (round(float(np.mean(dists)), 2) if dists else None),
                       "median_m": (round(float(np.median(dists)), 2) if dists else None),
                       "band_m": short_band_m, "n_seats": len(seats), "n_in_band": n_band},
            "confidence": 0.6,
            "method": "per-amenity geodesic field (MCP) -> per-seat nearest distance",
            "failure_modes": ["short-walk band is a design target, not an evidence-based cutoff",
                              "amenity schedule is a spec input (where the coffee actually goes)"]}


# ---------------------------------------------------------------- C15/D1: stair prominence
def stair_prominence(pg, entrance: RC, stair: RC, elevator: RC,
                     n_rays: int = 180) -> Dict:
    """C15/D1 — active-design stair-first test: is the stair inside the entrance's
    isovist (visible on arrival) AND nearer to the entrance than the elevator?
    Returns a pass flag + the two walking distances + a prominence ratio."""
    grid = _grid_of(pg)
    d_stair, _ = walking_distance_m(pg, entrance, stair)
    d_elev, _ = walking_distance_m(pg, entrance, elevator)
    stair_visible = _visible(grid, entrance, stair)
    nearer = bool(np.isfinite(d_stair) and (not np.isfinite(d_elev) or d_stair <= d_elev))
    ratio = (round(float(d_elev / d_stair), 2)
             if (np.isfinite(d_stair) and d_stair > 0 and np.isfinite(d_elev)) else None)
    return {"key": "cnfa.plan.stair_prominence", "criterion": "C15/D1",
            "scalar": 1.0 if (stair_visible and nearer) else 0.0,
            "extras": {"stair_in_entrance_isovist": stair_visible,
                       "stair_nearer_than_elevator": nearer,
                       "walk_to_stair_m": (None if not np.isfinite(d_stair) else round(d_stair, 2)),
                       "walk_to_elevator_m": (None if not np.isfinite(d_elev) else round(d_elev, 2)),
                       "elevator_over_stair_ratio": ratio},
            "confidence": 0.6,
            "method": "entrance->stair Bresenham visibility + geodesic distances vs elevator",
            "failure_modes": ["single entrance point (average several door points for real lobbies)",
                              "visibility is 2D line-of-sight; ignores stair finish/daylight quality (spec)"]}


from .los import segment_is_free as _visible   # supercover LOS (diagonal walls block) — panel fix S1


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.movement self-test (analytic L0)\n" + "-" * 44)
    cell = 0.1  # 10 cm cells

    # --- 1. open field: geodesic ~ Euclidean ---
    grid = np.full((30, 30), FREE, np.int8)
    pg = type("PG", (), {"grid": grid, "cell_m": cell})()
    d_edge, _ = walking_distance_m(pg, (0, 0), (0, 29))     # straight along a row
    d_diag, _ = walking_distance_m(pg, (0, 0), (29, 29))    # diagonal
    exp_edge = 29 * cell
    exp_diag = 29 * np.sqrt(2) * cell
    print(f"open edge : geodesic={d_edge:.3f} m  expected~{exp_edge:.3f}  err={abs(d_edge-exp_edge):.4f}")
    print(f"open diag : geodesic={d_diag:.3f} m  expected~{exp_diag:.3f}  err={abs(d_diag-exp_diag):.4f}")
    assert abs(d_edge - exp_edge) < 0.02, "open-field edge distance wrong"
    assert abs(d_diag - exp_diag) < 0.05, "open-field diagonal distance wrong"

    # --- 2. wall forces a detour: geodesic > Euclidean ---
    g2 = np.full((21, 21), FREE, np.int8)
    g2[0:15, 10] = OBST                       # a wall from the top down to row 14, at col 10
    pg2 = type("PG", (), {"grid": g2, "cell_m": cell})()
    a, b = (2, 2), (2, 18)                     # must go around the wall (down past row14, back up)
    d_detour, path = walking_distance_m(pg2, a, b)
    d_euclid = np.hypot(0, 16) * cell
    print(f"detour    : geodesic={d_detour:.3f} m  euclid={d_euclid:.3f} m  (must be >)  pathlen={len(path)}")
    assert d_detour > d_euclid + 0.5, "wall detour should exceed straight-line by a clear margin"

    # --- 3. collaborator proximity: same region within/over threshold + a split ---
    g3 = np.full((20, 40), FREE, np.int8)
    g3[:, 19:21] = OBST                        # a full-height wall splits left/right regions
    pg3 = type("PG", (), {"grid": g3, "cell_m": 1.0})()  # 1 m cells
    seats = [(5, 5), (5, 12), (5, 33)]         # 0,1 left region; 2 right region
    res5 = collaborator_proximity(pg3, seats, pairs=[(0, 1), (0, 2)], max_m=40)
    print("C5 rows   :", [(r["pair"], r["walk_m"], r["same_region"], r["cross_region_split"]) for r in res5["rows"]])
    assert res5["rows"][0]["same_region"] and res5["rows"][0]["walk_m"] is not None, "pair 0-1 same region"
    assert res5["rows"][1]["cross_region_split"], "pair 0-2 should be a cross-region split"

    # --- 4. amenity distance + stair prominence sanity ---
    res15 = amenity_distance(pg3, seats=[(5, 5), (5, 12)], amenities=[(5, 8)], short_band_m=(1, 20))
    print("C15 amenity:", res15["scalar"], res15["extras"])
    assert res15["extras"]["mean_m"] is not None

    g4 = np.full((20, 20), FREE, np.int8)
    prom = stair_prominence(type("PG", (), {"grid": g4, "cell_m": 1.0})(),
                            entrance=(19, 10), stair=(15, 10), elevator=(2, 2))
    print("stair prom :", prom["scalar"], prom["extras"])
    assert prom["scalar"] == 1.0, "visible + nearer stair should pass"

    print("-" * 44 + "\nmovement self-test: PASS")
