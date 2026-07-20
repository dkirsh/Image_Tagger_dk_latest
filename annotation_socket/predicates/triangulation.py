"""
annotation_socket.predicates.triangulation — C01 `triangulation_ignition_field`.

THE COMPOUND (panel 2026-07-15, rank 9, the flagship social attribute).
Whyte's triangulation, made computable: a salient shared ANCHOR ignites conversation between
co-present strangers ONLY when it sits ON a path people already take. The value is therefore
NOT anchor-salience and NOT integration — it is their THRESHOLD-GATED SPATIAL PRODUCT:

    ignition = salience01(anchor) * integration01(anchor_cell) * gate(dist_to_desire_line)

where gate -> 0 once the anchor is more than ~D0 metres off the maximum-integration ridge
(the desire line). An average of salience and integration would wrongly score a beautiful
dead-alcove fountain highly; the co-location gate correctly zeros it. That gate IS the
compound — this is why C01 predicts triggered conversation where a single primitive cannot.

BASE MEASURES COMPOSED (all already computed upstream — this predicate never recomputes them):
  - landmark_salience(img)              -> anchor image bbox + Lab-contrast salience dE   [Tier A]
  - space_syntax.vga_metrics(pg)        -> per-cell integration_score01 (the desire line) [Tier B]
  - the shared geometry chain (vp -> planes -> depth -> PlanGrid) for cross-tier registration

TRI-STATE (fabrication-proof, via annotation_socket.derivation chokepoint):
  SCORED   anchor detected AND registered to a plan cell with confidence >= REG_FLOOR:
           value in [0,1], evidence = plan_chain{anchor bbox, anchor cell, ridge pctl,
           dist_m, gate, integ} + the geometry upstream.
  SCORED=0 no salient anchor above the floor: a genuine zero (no triangulation prop present),
           evidence = global_image naming the floor — NOT an abstention, a real finding.
  UNKNOWN  anchor detected but cross-tier registration is unconfident -> DO NOT guess the
           centroid (skeptic's fix); or geometry itself unconfident. Routes RED, never a number.

TIER/CEILING: Tier B, ceiling AMBER — rides the inferred plan grid + cross-tier registration,
so it can never self-claim GREEN (registry `tier_hint`).
AUDIT CLASS: replayable_tol — deterministic (spectral-residual salience + seeded kmeans plane
seg + deterministic Turner VGA), so verify() re-derives from image bytes and demands a match
within TOL. A fabricated value cannot survive replay.

DOUBLE-COUNTING GUARD (panel caution): landmark_salience and C1 integration also feed the
hedonics/score layer. C01 is its OWN social field and MUST NOT be summed back into the general
valence score, or the shared signals get re-weighted. score_layout must exclude C01.
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Sequence, Tuple

from .. import derivation as D

PRED_ID = "C01.triangulation_ignition"
TIER_HINT = "AMBER"

# ---- declared constants (DATA, emitted with every score so replay is exact) ----
DE_REF = 40.0          # Lab-contrast dE that maps salience -> 1.0 (declared reference)
SALIENCE_FLOOR = 8.0   # dE below which "no salient anchor is present" (genuine zero)
RIDGE_PCTL = 85.0      # integration percentile defining the desire-line ridge
D0_M = 2.5             # gate scale (m): permissible-reason-to-speak band around the ridge
REG_FLOOR = 0.35       # min cross-tier registration confidence to SCORE (else UNKNOWN)
GEOM_FLOOR = 0.20      # min geometry confidence to attempt C01 at all
TOL = 1e-3             # replay tolerance (replayable_tol)


# ============================================================ PURE INTERACTION CORE
# These functions contain the whole compound claim and are unit-tested WITHOUT the CV
# pipeline (CLAUDE.md verification rule: exercise the core logic in-process).

def salience01(dE: float) -> float:
    """Normalize Lab-contrast salience to [0,1] against the declared reference."""
    return max(0.0, min(1.0, float(dE) / DE_REF))


def gate(dist_m: float, d0: float = D0_M) -> float:
    """Gaussian co-location gate: 1 on the desire line, -> 0 by ~2*d0 off it.
    This is the threshold that turns a sum into a genuine compound."""
    if dist_m < 0 or not math.isfinite(dist_m):
        return 0.0
    return math.exp(-(dist_m / d0) ** 2)


RIDGE_MIN_RELIQR = 0.05      # min interquartile range / |median| of RAW integration; below = no ridge


def _percentile(sorted_v, q):
    if not sorted_v:
        return 0.0
    k = (len(sorted_v) - 1) * q
    lo = int(k)
    return sorted_v[lo] if lo >= len(sorted_v) - 1 else \
        sorted_v[lo] + (k - lo) * (sorted_v[lo + 1] - sorted_v[lo])


def ridge_is_degenerate(integ_raw: Sequence[float]) -> bool:
    """FABLE F7 (+ Codex-2 hardening): a uniform integration field makes the percentile ridge the
    WHOLE plan, so the gate cannot discriminate. Test RELATIVE spread on the RAW Turner integration.
    Uses the ROBUST interquartile range / |median|, NOT the coefficient of variation — CV is
    inflated by the single clipped 1e6 outlier the VGA produces, so a genuinely flat field + one
    outlier passed the old CV guard (Codex-2). IQR ignores the outlier: a flat field has IQR=0
    whether or not one cell is clipped. Also degenerate if the ridge threshold has no cells strictly
    below it (everything tied at/above p85)."""
    v = sorted(float(x) for x in integ_raw if x is not None and x == x)
    if len(v) < 4:
        return True
    med = _percentile(v, 0.5)
    if abs(med) < 1e-9:
        return True
    iqr = _percentile(v, 0.75) - _percentile(v, 0.25)
    if (iqr / abs(med)) < RIDGE_MIN_RELIQR:
        return True
    # belt-and-braces: the ridge (>= p85) must leave a real off-ridge population
    thr = _percentile(v, RIDGE_PCTL / 100.0)
    below = sum(1 for x in v if x < thr)
    return below < max(4, int(0.25 * len(v)))


def ridge_cells(cells: Sequence[Tuple[int, int]], integ01: Sequence[float],
                pctl: float = RIDGE_PCTL) -> List[Tuple[int, int]]:
    """The desire-line ridge = sampled cells at/above the integration percentile
    (Hillier natural-movement: integration predicts the paths people take). Returns [] when the
    field is degenerate (caller must treat that as UNKNOWN, not as 'every cell on-ridge')."""
    if not cells or ridge_is_degenerate(integ01):
        return []
    vals = sorted(integ01)
    k = (len(vals) - 1) * (pctl / 100.0)
    lo = int(math.floor(k))
    thr = vals[lo] if lo >= len(vals) - 1 else vals[lo] + (k - lo) * (vals[lo + 1] - vals[lo])
    return [tuple(c) for c, v in zip(cells, integ01) if v >= thr]


def dist_to_ridge_m(anchor_cell: Tuple[int, int], ridge: Sequence[Tuple[int, int]],
                    cell_m: float) -> float:
    """Euclidean distance (m) from the anchor cell to the nearest ridge cell."""
    if not ridge:
        return float("inf")
    ar, ac = anchor_cell
    best = min((ar - r) ** 2 + (ac - c) ** 2 for r, c in ridge)
    return math.sqrt(best) * float(cell_m)


def ignition(sal01: float, integ_anchor01: float, g: float) -> float:
    """THE COMPOUND: threshold-gated spatial product. All three must be high; any one low
    (dim anchor / peripheral cell / off the desire line) collapses the value toward 0."""
    return max(0.0, min(1.0, float(sal01) * float(integ_anchor01) * float(g)))


# ============================================================ TRI-STATE ASSEMBLY
def decide(dE: float, sal01: float, anchor_cell: Optional[Tuple[int, int]], reg_conf: float,
           integ_anchor01: Optional[float], dist_m: Optional[float],
           geom_conf: float) -> Tuple[str, Optional[float], Dict]:
    """Pure tri-state decision over already-computed inputs. `dE` is the raw Lab-contrast used
    ONLY for the presence floor; `sal01` is landmark_salience's own normalized [0,1] salience
    (the value that enters the product). Returns (state, value_or_None, detail); state in
    {'SCORED','ZERO','UNKNOWN'}. No I/O, fully testable."""
    if not math.isfinite(geom_conf) or geom_conf < GEOM_FLOOR:
        return "UNKNOWN", None, {"reason": "geometry_unconfident", "geom_conf": geom_conf}
    if dE < SALIENCE_FLOOR:
        return "ZERO", 0.0, {"reason": "no_salient_anchor", "dE": dE, "floor": SALIENCE_FLOOR}
    if anchor_cell is None or reg_conf < REG_FLOOR:
        # skeptic's fix: do NOT guess the centroid onto the plan — fail closed.
        return "UNKNOWN", None, {"reason": "anchor_registration_unconfident", "reg_conf": reg_conf}
    g = gate(dist_m if dist_m is not None else float("inf"))
    s01 = max(0.0, min(1.0, float(sal01)))
    val = ignition(s01, integ_anchor01 or 0.0, g)
    return "SCORED", val, {"dE": round(dE, 2), "sal01": round(s01, 4),
                           "integ01": round(float(integ_anchor01 or 0.0), 4),
                           "dist_m": round(float(dist_m), 3), "gate": round(g, 4),
                           "anchor_cell": [int(anchor_cell[0]), int(anchor_cell[1])],
                           "ridge_pctl": RIDGE_PCTL, "D0_m": D0_M, "DE_REF": DE_REF}


# ============================================================ CROSS-TIER REGISTRATION
def pixel_to_plan_cell(pg, Z, planes, px: int, py: int,
                       fov_deg: float = 65.0) -> Tuple[Optional[Tuple[int, int]], float]:
    """Register an image pixel (the anchor's floor-contact point) onto the PlanGrid, mirroring
    plan.infer_plan_from_image's mapping. Returns (cell|None, registration_confidence).
    Confidence degrades if the mapped cell is out of grid or not FREE/known (the anchor is
    not standing on measured floor) — in which case the caller fails closed to UNKNOWN."""
    import numpy as np
    from cnfa_algs.plan import FREE
    grid = pg.grid
    grid_n = grid.shape[0]
    H, W = Z.shape[:2]
    py = int(np.clip(py, 0, H - 1)); px = int(np.clip(px, 0, W - 1))
    zdepth = float(Z[py, px])
    if not np.isfinite(zdepth) or zdepth <= 0:
        return None, 0.0
    x_half = float(np.tan(np.radians(fov_deg) / 2.0)) * zdepth
    xv = (px - W / 2.0) / (W / 2.0) * x_half          # metric x at the pixel's depth
    z_max = max(zdepth, float(np.nanpercentile(Z[Z > 0], 95)) if np.any(Z > 0) else zdepth)
    c = int((xv + x_half) / (2 * x_half + 1e-9) * (grid_n - 1))
    r = int((z_max - zdepth) / (z_max + 1e-9) * (grid_n - 1))
    if not (0 <= r < grid_n and 0 <= c < grid_n):
        return None, 0.0
    # confidence: fraction of a small footprint window that is known FREE floor
    r0, r1 = max(0, r - 1), min(grid_n, r + 2)
    c0, c1 = max(0, c - 1), min(grid_n, c + 2)
    win = grid[r0:r1, c0:c1]
    free_frac = float((win == FREE).mean()) if win.size else 0.0
    return (r, c), free_frac


# ============================================================ FULL COMPUTE (pipeline entry)
def compute(img, planes, Z, pg, vga_result: Dict, geom_conf: float,
            chain: list) -> Dict:
    """Produce the C01 record through the derivation chokepoint. Called by the annotator with
    the already-computed shared geometry + VGA (never recomputes them)."""
    import numpy as np
    from cnfa_algs import attributes as A
    from cnfa_algs import space_syntax as ss
    from cnfa_algs.plan import FREE

    # 1. anchor: strongest salient region. landmark_salience returns a normalized `scalar`
    #    [0,1] salience and the top region in `regions[0]` = {coords:[x,y,w,h], value:dE}.
    res = A.landmark_salience(img)
    sal01 = float(getattr(res, "scalar", 0.0) or 0.0)
    regions = getattr(res, "regions", None) or []
    dE = float(regions[0]["value"]) if regions else 0.0
    bbox = None
    if regions and regions[0].get("coords"):
        x, y, w, h = regions[0]["coords"]                  # [x,y,w,h] -> [x0,y0,x1,y1]
        bbox = [int(x), int(y), int(x + w), int(y + h)]

    if dE < SALIENCE_FLOOR or bbox is None:
        state, val, det = decide(dE, sal01, None, 0.0, None, None, geom_conf)
    else:
        x0, y0, x1, y1 = bbox
        foot_px, foot_py = int((x0 + x1) / 2), int(y1)     # bottom-centre = floor contact
        cell, reg_conf = pixel_to_plan_cell(pg, Z, planes, foot_px, foot_py)
        if cell is None:
            state, val, det = decide(dE, sal01, None, reg_conf, None, None, geom_conf)
        elif ridge_is_degenerate(list(vga_result["integration"])):
            # FABLE F7: no usable desire-line ridge (uniform integration) -> the gate cannot
            # discriminate on/off-path; fail closed rather than call everything on-ridge.
            state, val, det = "UNKNOWN", None, {"reason": "integration_field_degenerate"}
        else:
            iv = ss.integration_at(vga_result, [cell])[0]
            integ = 0.0 if (iv is None or not (iv == iv)) else float(iv)   # nan-safe
            # ridge from RAW integration ranks (real structure); anchor VALUE from score01 [0,1]
            raw = list(vga_result["integration"])
            ridge = ridge_cells([tuple(c) for c in vga_result["cells"]], raw)
            dm = dist_to_ridge_m(cell, ridge, pg.cell_m)
            state, val, det = decide(dE, sal01, cell, reg_conf, integ, dm, geom_conf)
            det["anchor_bbox"] = [int(x0), int(y0), int(x1), int(y1)]
            # Codex F7 audit diagnostics: expose the raw ridge set + anchor rank, not just gate.
            anchor_raw = raw[min(range(len(raw)),
                                 key=lambda i: (tuple(vga_result["cells"][i])[0]-cell[0])**2
                                             + (tuple(vga_result["cells"][i])[1]-cell[1])**2)] if raw else 0.0
            det["ridge_count"] = len(ridge)
            det["n_cells"] = len(raw)
            det["ridge_frac"] = round(len(ridge) / max(len(raw), 1), 3)
            det["anchor_rank_pctl"] = round(100.0 * sum(1 for x in raw if x <= anchor_raw) / max(len(raw), 1), 1)

    gh = D.grid_hash(pg.grid)
    if state == "UNKNOWN":
        return D.unknown(PRED_ID, det["reason"])
    if state == "ZERO":
        ev = D.evidence_image("global_image", "full_frame",
                              f"triangulation: no anchor above dE floor {SALIENCE_FLOOR} (M1)",
                              min(0.5, geom_conf), upstream=chain)
        return D.scored(PRED_ID, 0.0, ev, TIER_HINT, img.shape)
    ev = D.evidence_image(
        "plan_chain",
        {"grid_hash": gh, "free_cells": int((pg.grid == FREE).sum()),
         "anchor_cell": det["anchor_cell"], "anchor_bbox": det.get("anchor_bbox"),
         "dist_to_ridge_m": det["dist_m"], "gate": det["gate"],
         "salience01": det["sal01"], "integration01": det["integ01"], "ridge_pctl": RIDGE_PCTL,
         "ridge_count": det.get("ridge_count"), "n_cells": det.get("n_cells"),
         "ridge_frac": det.get("ridge_frac"), "anchor_rank_pctl": det.get("anchor_rank_pctl")},
        f"triangulation ignition = sal01*integ01*gate(dist={det['dist_m']}m) (M1)",
        min(0.5, geom_conf), upstream=chain)
    return D.scored(PRED_ID, val, ev, TIER_HINT, img.shape)
