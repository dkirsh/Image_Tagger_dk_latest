"""
cnfa_algs.space_syntax — the CONFIGURATIONAL SUBSTRATE (CRITERIA.md C1-C4).

The keystone paper (via CRITERIA §0.1) separates the eight experiential dimensions from
the space-syntax substrate C1-C6 — the layer that predicts WHERE people are and WHOSE
PATHS CROSS, on which the experiential dimensions ride. movement.py covered C5/C6; this
module supplies the visibility-graph half: real VGA (Turner et al. 2001), sampled.

  vga_metrics       — build a visibility graph over sampled free cells and compute:
      C1 visual INTEGRATION  (global; encounter/co-presence)   = 1 / relative asymmetry
      C2 visual CONNECTIVITY (local; movement/footfall)        = # cells each cell sees
      C3 INTELLIGIBILITY     (legibility)                      = R^2(connectivity, integration)
  wayfinding_load   — C4: decision-point count on the free-space skeleton + a
      goal-visibility proxy (fraction of junctions that can see a landmark cell).

METHOD / SCOPE. Integration is the graph-theoretic Turner VGA measure (mean visual depth
-> relative asymmetry -> integration), computed on cells SAMPLED at a stride for
tractability (full VGA is O(N^2); sampling ranks correctly, magnitudes are approximate).
Intelligibility is Hillier's connectivity-vs-integration correlation. Wayfinding load is a
skeleton/junction proxy, not a validated cognitive-map-error predictor (that is L3).
This is L0/L1 machinery: it orders spaces correctly; absolute values want depthmapX
cross-checking before publication.

Self-test (analytic L0):
    python -m cnfa_algs.space_syntax
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

RC = Tuple[int, int]


from .los import segment_is_free as _los   # supercover LOS (diagonal walls block) — panel fix S1


def _sample_cells(grid: np.ndarray, stride: int, max_cells: int = 500) -> np.ndarray:
    free = np.argwhere(grid == FREE)[::stride]
    if len(free) > max_cells:                       # cap for tractability
        idx = np.linspace(0, len(free) - 1, max_cells).astype(int)
        free = free[idx]
    return free


def vga_metrics(pg, stride: int = 3, max_cells: int = 500) -> Dict:
    """C1-C3 — visibility-graph analysis on sampled free cells.
    Returns integration/connectivity summaries + intelligibility (R^2)."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cells = _sample_cells(grid, stride, max_cells)
    N = len(cells)
    if N < 4:
        return {"key": "cnfa.plan.vga", "criterion": "C1-C3", "scalar": None,
                "extras": {"n_cells": N}, "confidence": 0.0,
                "method": "too few free cells for VGA", "failure_modes": ["degenerate plan"]}

    # adjacency via mutual line-of-sight
    adj = np.zeros((N, N), bool)
    for i in range(N):
        ai = tuple(cells[i])
        for j in range(i + 1, N):
            if _los(grid, ai, tuple(cells[j])):
                adj[i, j] = adj[j, i] = True

    connectivity = adj.sum(1).astype(float)         # C2: cells each cell sees

    # graph distances (unweighted visual steps) -> mean depth -> integration (Turner)
    from scipy.sparse.csgraph import shortest_path
    from scipy.sparse import csr_matrix
    dmat = shortest_path(csr_matrix(adj.astype(int)), method="D", unweighted=True)
    finite = np.isfinite(dmat)
    md = np.array([dmat[i, finite[i]].sum() / max(finite[i].sum() - 1, 1) for i in range(N)])  # mean depth
    # relative asymmetry RA = 2(MD-1)/(N-2) in [0,1]; integration = 1/RA (Turner units).
    # PANEL FIX S3: the old integration_norm was a within-plan percentile SKEWNESS statistic
    # (`_norm`) that INVERTED ranks — an open studio scored 0.0, a snake corridor 0.378. The
    # bounded ABSOLUTE integration score is 1-RA (higher = shallower mean depth = more
    # integrated), which ranks correctly and is comparable across plans.
    ra = 2 * (md - 1) / max(N - 2, 1)
    integration = 1.0 / np.clip(ra, 1e-6, None)          # Turner integration (reporting)
    # bounded, monotonic, DISCRIMINATING map I/(I+K): open studio -> ~1, deep/snake -> low,
    # without the mid-range saturation of 1-RA (K sets the office-relevant midpoint).
    _K_INTEG = 3.0
    integ_score01 = integration / (integration + _K_INTEG)

    # C3 intelligibility = R^2 of connectivity vs integration across cells
    if np.std(connectivity) > 1e-9 and np.std(integration) > 1e-9:
        r = float(np.corrcoef(connectivity, integration)[0, 1])
        intelligibility = r * r
    else:
        intelligibility = float("nan")

    conn_frac = float(np.mean(connectivity) / max(N - 1, 1))   # absolute: mean fraction of cells seen

    return {"key": "cnfa.plan.vga", "criterion": "C1-C3",
            "scalar": (None if np.isnan(intelligibility) else round(intelligibility, 3)),  # C3 headline
            "extras": {"n_cells": N,
                       "mean_integration": round(float(np.mean(integration)), 3),
                       "integration_spread": round(float(np.std(integration)), 3),
                       "mean_connectivity": round(float(np.mean(connectivity)), 2),
                       "intelligibility_R2": (None if np.isnan(intelligibility) else round(intelligibility, 3)),
                       "integration_norm": round(float(np.mean(integ_score01)), 3),   # C1: absolute, higher=better
                       "connectivity_norm": round(conn_frac, 3)},                     # C2: fraction visible
            "cells": cells, "integration": integration, "integration_score01": integ_score01,
            "connectivity": connectivity,
            "confidence": 0.5,
            "method": "sampled visibility-graph VGA (Turner 2001): integration, connectivity, intelligibility",
            "failure_modes": ["cells sampled at a stride -> magnitudes approximate (ranks ok)",
                              "cross-check absolute values against depthmapX before publication",
                              "single-plan; multi-floor VGA needs stacked/linked graphs"]}


def integration_at(vga_result: Dict, points: Sequence[RC]) -> List[float]:
    """ABSOLUTE [0,1] visual integration (1-RA) at each point (nearest sampled VGA cell).
    PANEL FIX S3: uses the bounded absolute score, NOT a per-call percentile normalization
    (which made C14's 'high-integration' threshold collapse to nobody on a uniform plan,
    so C14 passed the unzoned floor it exists to catch)."""
    cells = vga_result.get("cells")
    norm = vga_result.get("integration_score01")
    if norm is None:                                  # fallback: derive from Turner integration
        integ = vga_result.get("integration")
        norm = None if integ is None else (np.asarray(integ, float) / (np.asarray(integ, float) + 3.0))
    if cells is None or norm is None or len(cells) == 0:
        return [float("nan")] * len(points)
    norm = np.asarray(norm, float)
    cells = np.asarray(cells)
    out = []
    for p in points:
        d2 = (cells[:, 0] - p[0]) ** 2 + (cells[:, 1] - p[1]) ** 2
        out.append(float(norm[int(d2.argmin())]))
    return out


def focus_collab_separation(pg, focus_seats: Sequence[RC], focus_sti: Sequence[float],
                            vga_result: Optional[Dict] = None, stride: int = 3) -> Dict:
    """C14 — focus:collaboration separation. A focus seat that is BOTH in a high-encounter
    (high visual-integration) location AND acoustically intruded (STI >= 0.5) is a zoning
    FAILURE: focus and collaboration were not separated. Score = fraction of focus seats
    that avoid that double-bind (STATE_OF_KNOWLEDGE G3 / CRITERIA §4 conflict penalty)."""
    if vga_result is None:
        vga_result = vga_metrics(pg, stride=stride)
    integ = integration_at(vga_result, focus_seats)
    rows, fails = [], 0
    for k, seat in enumerate(focus_seats):
        ig = integ[k] if k < len(integ) else float("nan")
        sti = float(focus_sti[k]) if k < len(focus_sti) else 0.0
        fail = bool((not np.isnan(ig)) and ig > 0.6 and sti >= 0.5)
        fails += int(fail)
        rows.append({"focus_seat": k, "integration_norm": (None if np.isnan(ig) else round(ig, 3)),
                     "sti": round(sti, 3), "separation_fail": fail})
    return {"key": "cnfa.plan.focus_collab_separation", "criterion": "C14",
            "rows": rows,
            "scalar": (round(1 - fails / len(focus_seats), 3) if focus_seats else None),
            "extras": {"n_focus_seats": len(focus_seats), "n_separation_fails": fails},
            "confidence": 0.45,
            "method": "focus seat in high-integration AND speech-intruded = zoning failure (conflict penalty)",
            "failure_modes": ["derived from C1 (integration) x C7 (STI) at focus seats",
                              "thresholds (integ>0.6, STI>=0.5) are conventions to tune at L3",
                              "which seats are 'focus' is a spec input (the zoning intent)"]}


def wayfinding_load(pg, landmarks: Optional[List[RC]] = None, stride: int = 3) -> Dict:
    """C4 — decision-point proxy: free cells that are 'junctions' (open in >=3 of the 4
    cardinal directions to a meaningful distance), and the fraction of those junctions
    with line-of-sight to a landmark/goal (goal-visibility reduces navigation error)."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    H, W = grid.shape
    cells = _sample_cells(grid, stride)
    look = max(3, int(2.0 / float(getattr(pg, "cell_m", 1.0))))   # ~2 m corridor reach
    junctions = []
    for (r, c) in cells:
        opens = 0
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc, ok = r, c, True
            for _ in range(look):
                rr += dr; cc += dc
                if not (0 <= rr < H and 0 <= cc < W) or grid[rr, cc] != FREE:
                    ok = False; break
            if ok:
                opens += 1
        if opens >= 3:                            # >=3 directions open = a decision point
            junctions.append((int(r), int(c)))
    goal_vis = None
    if landmarks and junctions:
        seen = sum(1 for j in junctions if any(_los(grid, j, lm) for lm in landmarks))
        goal_vis = round(seen / len(junctions), 3)
    # fewer decision points + higher goal visibility = lower wayfinding load = better.
    # score: goal-visibility if landmarks given, else inverse junction density.
    density = len(junctions) / max(len(cells), 1)
    score = goal_vis if goal_vis is not None else round(float(np.clip(1 - density, 0, 1)), 3)
    return {"key": "cnfa.plan.wayfinding_load", "criterion": "C4",
            "scalar": score,
            "extras": {"n_decision_points": len(junctions), "junction_density": round(density, 3),
                       "goal_visibility_frac": goal_vis, "n_landmarks": (len(landmarks) if landmarks else 0)},
            "confidence": 0.4,
            "method": "decision-point (junction) proxy + landmark line-of-sight at junctions",
            "failure_modes": ["junction = >=3 open cardinal directions (a heuristic decision-point proxy)",
                              "not a validated cognitive-map-error predictor (that is L3)",
                              "landmarks are a spec input (what is salient/goal-relevant)"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.space_syntax self-test (analytic L0)\n" + "-" * 46)

    # --- convex open room: everyone sees everyone -> high connectivity, high intelligibility-degenerate ---
    g = np.full((30, 30), FREE, np.int8)
    pg = type("PG", (), {"grid": g, "cell_m": 0.5})()
    v = vga_metrics(pg, stride=2, max_cells=300)
    print("convex room: mean_conn=", v["extras"]["mean_connectivity"], "n=", v["extras"]["n_cells"])
    # in a fully convex room each sampled cell sees ~all others
    assert v["extras"]["mean_connectivity"] > 0.8 * (v["extras"]["n_cells"] - 1), "convex room should be near-complete graph"

    # --- dumbbell: two rooms joined by a corridor -> corridor MORE integrated than room interiors ---
    g2 = np.full((30, 60), OBST, np.int8)
    g2[5:25, 3:20] = FREE          # left room
    g2[5:25, 40:57] = FREE         # right room
    g2[13:17, 20:40] = FREE        # connecting corridor
    pg2 = type("PG", (), {"grid": g2, "cell_m": 0.4})()
    v2 = vga_metrics(pg2, stride=2, max_cells=400)
    cells = v2["cells"]; integ = v2["integration"]
    # corridor cells (cols 20..40) vs deep room cells (cols <18 or >42)
    corr_mask = (cells[:, 1] >= 20) & (cells[:, 1] < 40)
    room_mask = (cells[:, 1] < 18) | (cells[:, 1] >= 42)
    corr_int = integ[corr_mask].mean(); room_int = integ[room_mask].mean()
    print(f"dumbbell   : corridor integration={corr_int:.3f} vs room interior={room_int:.3f} (corridor should be >)")
    print(f"           : intelligibility R2={v2['scalar']}")
    assert corr_int > room_int, "the connecting corridor must be more integrated than the room interiors"
    assert v2["scalar"] is None or 0.0 <= v2["scalar"] <= 1.0, "intelligibility must be an R^2 in [0,1]"

    # --- wayfinding: a junction (crossroads) is detected; a plain corridor cell is not ---
    g3 = np.full((21, 21), OBST, np.int8)
    g3[10, :] = FREE; g3[:, 10] = FREE          # a plus-shaped crossroads
    pg3 = type("PG", (), {"grid": g3, "cell_m": 0.5})()
    w = wayfinding_load(pg3, landmarks=[(0, 10)], stride=1)
    print("wayfinding : decision points=", w["extras"]["n_decision_points"],
          "goal_vis=", w["extras"]["goal_visibility_frac"])
    assert w["extras"]["n_decision_points"] >= 1, "the crossroads centre should be a decision point"

    print("-" * 46 + "\nspace_syntax self-test: PASS")
