"""
annotation_socket.predicates.stranded_amenity — C29 `stranded_amenity_index`.

C01's DIAGNOSTIC INVERSE (panel 2026-07-15, rank 8, Wave-1). Whyte's finding: an attractive
amenity delivers social life ONLY where people already move; the same amenity off the desire
line is admired and empty. C29 is a WARNING FLAG — high value = high appeal but ~0 delivered
encounter:

    stranded = appeal01 * (1 - gate(dist_to_desire_line)) * seat_affordance01

The interaction is the point: appeal alone (a sculpture in a busy hall -> 1-gate ~ 0), or
off-path distance alone (a bare dead-end -> appeal ~ 0), or flat wall art (seat_affordance ~ 0)
each drive it to ~0. Only appeal AND off-path AND a usable dwell surface CO-OCCURRING flags a
genuine stranded amenity. A high value is BAD NEWS — a redesign flag.

Reuses C01's verified machinery verbatim (L9: shared function is a contract): `gate`,
`ridge_cells`, `dist_to_ridge_m`, `pixel_to_plan_cell` from `triangulation.py`.

TIER B / ceiling AMBER (same inferred-plan + cross-tier registration as C01).
AUDIT CLASS replayable_tol. Own diagnostic field — excluded from score_layout aggregation.
"""
from __future__ import annotations
import math
from typing import Dict, Optional, Tuple

from .. import derivation as D
from . import triangulation as T          # reuse gate/ridge/registration — do NOT duplicate

PRED_ID = "C29.stranded_amenity_index"
TIER_HINT = "AMBER"

SALIENCE_FLOOR = T.SALIENCE_FLOOR         # same amenity-presence floor as C01
REG_FLOOR = T.REG_FLOOR
GEOM_FLOOR = T.GEOM_FLOOR
TOL = T.TOL
# plane labels (cnfa_algs.PLANE_LEGEND): 0 furniture/other, 1 floor = usable amenity surface;
# 2 ceiling, 3 wall, 4 window = flat decoration (not a sittable/usable amenity).
USABLE_PLANES = (0, 1)


# ============================================================ PURE INTERACTION CORE
def seat_affordance01(planes, bbox) -> float:
    """Fraction of the anchor bbox on a USABLE plane (furniture/floor) vs flat wall/ceiling/
    window. A fountain/bench scores high; a picture on a wall or a window scores ~0."""
    import numpy as np
    x0, y0, x1, y1 = [int(v) for v in bbox]
    H, W = planes.shape[:2]
    x0, x1 = max(0, x0), min(W, x1); y0, y1 = max(0, y0), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    win = planes[y0:y1, x0:x1]
    return float(np.isin(win, USABLE_PLANES).mean())


def stranded(appeal01: float, one_minus_gate: float, seat01: float) -> float:
    """THE COMPOUND: appeal x off-path-ness x usability. Any one low collapses it toward 0."""
    v = float(appeal01) * float(one_minus_gate) * float(seat01)
    return max(0.0, min(1.0, v))


def decide(dE: float, appeal01: float, seat01: float,
           anchor_cell: Optional[Tuple[int, int]], reg_conf: float,
           dist_m: Optional[float], geom_conf: float) -> Tuple[str, Optional[float], Dict]:
    """Pure tri-state over already-computed inputs. `dE` = raw salience for the presence floor;
    `appeal01` = normalized amenity appeal; `seat01` = usable-surface fraction."""
    if not math.isfinite(geom_conf) or geom_conf < GEOM_FLOOR:
        return "UNKNOWN", None, {"reason": "geometry_unconfident", "geom_conf": geom_conf}
    if dE < SALIENCE_FLOOR:
        return "ZERO", 0.0, {"reason": "no_salient_amenity", "dE": dE, "floor": SALIENCE_FLOOR}
    if anchor_cell is None or reg_conf < REG_FLOOR:
        return "UNKNOWN", None, {"reason": "anchor_registration_unconfident", "reg_conf": reg_conf}
    g = T.gate(dist_m if dist_m is not None else float("inf"))
    omg = 1.0 - g
    val = stranded(appeal01, omg, seat01)
    return "SCORED", val, {"dE": round(dE, 2), "appeal01": round(float(appeal01), 4),
                           "seat01": round(float(seat01), 4),
                           "dist_m": round(float(dist_m), 3), "one_minus_gate": round(omg, 4),
                           "anchor_cell": [int(anchor_cell[0]), int(anchor_cell[1])],
                           "ridge_pctl": T.RIDGE_PCTL, "D0_m": T.D0_M}


# ============================================================ FULL COMPUTE (pipeline entry)
def compute(img, planes, Z, pg, vga_result: Dict, geom_conf: float, chain: list) -> Dict:
    """Produce the C29 record through the derivation chokepoint. Shares geometry + VGA with the
    annotator (never recomputes them); reuses C01's registration + ridge."""
    from cnfa_algs import attributes as A
    from cnfa_algs import space_syntax as ss
    from cnfa_algs.plan import FREE

    res = A.landmark_salience(img)
    appeal01 = float(getattr(res, "scalar", 0.0) or 0.0)
    regions = getattr(res, "regions", None) or []
    dE = float(regions[0]["value"]) if regions else 0.0
    bbox = None
    if regions and regions[0].get("coords"):
        x, y, w, h = regions[0]["coords"]
        bbox = [int(x), int(y), int(x + w), int(y + h)]

    if dE < SALIENCE_FLOOR or bbox is None:
        state, val, det = decide(dE, appeal01, 0.0, None, 0.0, None, geom_conf)
    else:
        x0, y0, x1, y1 = bbox
        seat01 = seat_affordance01(planes, bbox)
        cell, reg_conf = T.pixel_to_plan_cell(pg, Z, planes, int((x0 + x1) / 2), int(y1))
        if cell is None:
            state, val, det = decide(dE, appeal01, seat01, None, reg_conf, None, geom_conf)
        elif T.ridge_is_degenerate(list(vga_result["integration"])):
            # FABLE F7: without a usable desire-line ridge, off-path-ness is undefined -> a
            # degenerate field would otherwise make EVERY amenity read 'stranded'. Fail closed.
            state, val, det = "UNKNOWN", None, {"reason": "integration_field_degenerate"}
        else:
            ridge = T.ridge_cells([tuple(c) for c in vga_result["cells"]],
                                  list(vga_result["integration"]))
            dm = T.dist_to_ridge_m(cell, ridge, pg.cell_m)
            state, val, det = decide(dE, appeal01, seat01, cell, reg_conf, dm, geom_conf)
            det["anchor_bbox"] = [int(x0), int(y0), int(x1), int(y1)]

    gh = D.grid_hash(pg.grid)
    if state == "UNKNOWN":
        return D.unknown(PRED_ID, det["reason"])
    if state == "ZERO":
        ev = D.evidence_image("global_image", "full_frame",
                              f"stranded: no amenity above dE floor {SALIENCE_FLOOR} (M1)",
                              min(0.5, geom_conf), upstream=chain)
        return D.scored(PRED_ID, 0.0, ev, TIER_HINT, img.shape)
    ev = D.evidence_image(
        "plan_chain",
        {"grid_hash": gh, "free_cells": int((pg.grid == FREE).sum()),
         "anchor_cell": det["anchor_cell"], "anchor_bbox": det.get("anchor_bbox"),
         "dist_to_ridge_m": det["dist_m"], "one_minus_gate": det["one_minus_gate"],
         "appeal01": det["appeal01"], "seat_affordance01": det["seat01"],
         "ridge_pctl": T.RIDGE_PCTL},
        f"stranded = appeal01*{det['one_minus_gate']}(off-path)*seat01 (M1)",
        min(0.5, geom_conf), upstream=chain)
    return D.scored(PRED_ID, val, ev, TIER_HINT, img.shape)
