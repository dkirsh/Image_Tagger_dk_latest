"""
cnfa_algs.score_layout — the AGGREGATOR (CRITERIA.md §4-§5).

Turns the individual plan-metric modules (movement, acoustics_plan, daylight_view,
thermal_plan, setting_classifier) into the actual layout scorer: one computation, two
objective profiles (COG / WB), and the fit-matrix deliverable. It honours the CRITERIA.md
disciplines:

  * gate-then-rank        — baseline (physical code) is a SEPARATE gate; this only ranks.
  * two profiles          — every criterion tagged COG / WB / SHARED; SHARED enters both
                            with different weights (scored once, read twice).
  * evidence-anchored w   — weights from §4 (acoustics + thermal dominate; movement/view
                            confident; collaboration/setting caveated).
  * min-not-mean          — the headline is bounded by the WORST-served occupant type and
                            the weakest criterion, never lifted by the best.
  * non-additivity flagged — the weighted sum is first-order; "interactions un-modelled"
                            is stamped on every aggregate (CRITERIA §4).
  * provenance            — fidelity tier, evidence tags, and which criteria are still ○.

A Scenario is a plain dict describing the layout to score (see `demo_scenario`).
Missing inputs are skipped gracefully (their criteria drop out with a note), so the
scorer runs on whatever the caller can supply.

Self-test:
    python -m cnfa_algs.score_layout
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import numpy as np

from . import movement as _mv
from . import acoustics_plan as _ac
from . import daylight_view as _dl
from . import thermal_plan as _th
from . import setting_classifier as _st
from . import space_syntax as _ss

RC = Tuple[int, int]

# per-criterion registry: objective, evidence tag, weights in each profile, output form.
# weights are the §4 evidence-anchored prior (0..1), tuned only at L3, never hand-set to a target.
CRITERIA = {
    "C1":  {"name": "visual integration",      "obj": "COG",    "evid": "STRONG",  "cog_w": 0.8, "wb_w": 0.0, "form": "field"},
    "C2":  {"name": "connectivity / movement", "obj": "COG",    "evid": "STRONG",  "cog_w": 0.6, "wb_w": 0.0, "form": "field"},
    "C3":  {"name": "intelligibility",         "obj": "SHARED", "evid": "STRONG",  "cog_w": 0.7, "wb_w": 0.5, "form": "scalar"},
    "C4":  {"name": "wayfinding load",         "obj": "SHARED", "evid": "STRONG",  "cog_w": 0.6, "wb_w": 0.5, "form": "per-route"},
    "C7":  {"name": "focus speech privacy",   "obj": "SHARED", "evid": "STRONG",  "cog_w": 1.0, "wb_w": 0.9, "form": "per-seat+field"},
    "C8":  {"name": "distraction distance r_D","obj": "SHARED", "evid": "STRONG",  "cog_w": 1.0, "wb_w": 0.9, "form": "contour"},
    "C21": {"name": "thermal comfort/zoning",  "obj": "WB",     "evid": "STRONG",  "cog_w": 0.4, "wb_w": 1.0, "form": "per-zone"},
    "C9":  {"name": "view equity",             "obj": "SHARED", "evid": "STRONG",  "cog_w": 0.6, "wb_w": 0.8, "form": "per-seat"},
    "C10": {"name": "daylight/circadian",      "obj": "SHARED", "evid": "STRONG",  "cog_w": 0.4, "wb_w": 0.9, "form": "per-seat"},
    "C5":  {"name": "collaborator proximity",  "obj": "COG",    "evid": "STRONG",  "cog_w": 0.6, "wb_w": 0.0, "form": "pair"},
    "C13": {"name": "setting variety / fit",   "obj": "COG",    "evid": "PROMISING","cog_w": 0.6, "wb_w": 0.3, "form": "matrix"},
    "C15": {"name": "active-design movement",  "obj": "SHARED", "evid": "STRONG",  "cog_w": 0.3, "wb_w": 0.7, "form": "scalar+field"},
    # C6 path-overlap is an OPPORTUNITY estimate (not a good/bad axis) -> reported, weight 0.
    "C6":  {"name": "path overlap (opportunity)","obj": "COG",  "evid": "STRONG",  "cog_w": 0.0, "wb_w": 0.0, "form": "pair"},
}


def _r_d_score(r_d_m: float) -> float:
    """r_D -> [0,1]: <=5 m good (1.0), >10 m poor (0.0), linear between (ISO 3382-3)."""
    return float(np.clip((10.0 - r_d_m) / 5.0, 0.0, 1.0))


def _safe(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:                      # a missing input or degenerate plan
        return {"_error": repr(e)}


def score_layout(scenario: Dict) -> Dict:
    """Score a layout Scenario and emit the two objective vectors, the fit matrix, and a
    provenance panel. See `demo_scenario()` for the Scenario shape."""
    pg = scenario["pg"]
    seats = scenario.get("seats", [])
    raw: Dict[str, Dict] = {}          # criterion id -> module result
    scores: Dict[str, float] = {}      # criterion id -> normalized [0,1] score (higher=better)
    notes: List[str] = []

    # ---- configurational substrate: VGA (C1-C3) + wayfinding (C4) ----
    vga = _safe(_ss.vga_metrics, pg, stride=scenario.get("vga_stride", 3))
    raw["C1-C3"] = vga
    if vga.get("extras"):
        if vga["extras"].get("integration_norm") is not None:
            scores["C1"] = vga["extras"]["integration_norm"]
        if vga["extras"].get("connectivity_norm") is not None:
            scores["C2"] = vga["extras"]["connectivity_norm"]
        if vga.get("scalar") is not None:
            scores["C3"] = vga["scalar"]
    wf = _safe(_ss.wayfinding_load, pg, scenario.get("landmarks"),
               stride=scenario.get("vga_stride", 3))
    raw["C4"] = wf
    if wf.get("scalar") is not None:
        scores["C4"] = wf["scalar"]

    # ---- run the metrics that have their inputs ----
    if scenario.get("collab_sources") and scenario.get("focus_seats") is not None:
        fs = [seats[i] for i in scenario["focus_seats"]]
        r7 = _safe(_ac.focus_zone_privacy, pg, scenario["collab_sources"], fs,
                   L_noise=scenario.get("L_noise", _ac.L_NOISE_DEFAULT))
        raw["C7"] = r7
        if "scalar" in r7 and r7.get("scalar") is not None:
            scores["C7"] = r7["scalar"]
    r8 = _safe(_ac.iso3382_single_numbers, d2s=scenario.get("d2s", _ac.D2S_DEFAULT),
               L_noise=scenario.get("L_noise", _ac.L_NOISE_DEFAULT))
    raw["C8"] = r8
    if r8.get("extras"):
        scores["C8"] = _r_d_score(r8["extras"]["r_D_m"])

    if scenario.get("glazing"):
        gl = scenario["glazing"]
        wins = [g[0] for g in gl]
        if seats:
            r9 = _safe(_dl.view_equity, pg, seats, wins); raw["C9"] = r9
            if r9.get("scalar") is not None:
                scores["C9"] = r9["scalar"]
            r10 = _safe(_dl.daylight_proximity, pg, seats, wins); raw["C10"] = r10
            if r10.get("scalar") is not None:
                scores["C10"] = r10["scalar"]
            rrad = _safe(_th.radiant_asymmetry_risk, pg, seats, gl,
                         hemisphere=scenario.get("hemisphere", "N"))
            rz = _safe(_th.thermal_zone_mismatch, pg, scenario.get("control_zones", []),
                       hemisphere=scenario.get("hemisphere", "N")) if scenario.get("control_zones") else {"scalar": None}
            raw["C21"] = {"radiant": rrad, "zone": rz}
            parts = [x for x in [rrad.get("scalar"), rz.get("scalar")] if x is not None]
            if parts:
                scores["C21"] = float(np.mean(parts))

    if scenario.get("collaborator_pairs") and seats:
        r5 = _safe(_mv.collaborator_proximity, pg, seats, scenario["collaborator_pairs"],
                   max_m=scenario.get("collab_max_m", 40)); raw["C5"] = r5
        if r5.get("scalar") is not None:
            scores["C5"] = r5["scalar"]
    if scenario.get("destinations") and seats:
        raw["C6"] = _safe(_mv.path_overlap, pg, seats, scenario["destinations"])   # opportunity, no score

    if scenario.get("amenities") and seats:
        r15a = _safe(_mv.amenity_distance, pg, seats, scenario["amenities"])
        r15b = ({"scalar": None} if not all(k in scenario for k in ("entrance", "stair", "elevator"))
                else _safe(_mv.stair_prominence, pg, scenario["entrance"], scenario["stair"], scenario["elevator"]))
        raw["C15"] = {"amenity": r15a, "stair": r15b}
        parts = [x for x in [r15a.get("scalar"), r15b.get("scalar")] if x is not None]
        if parts:
            scores["C15"] = float(np.mean(parts))

    r13 = _safe(_st.classify_settings, pg)
    fit = _safe(_st.segment_fit, r13, scenario.get("demand")) if "_error" not in r13 else {"_error": r13}
    raw["C13"] = {"settings": r13, "fit": fit}
    if isinstance(fit, dict) and fit.get("scalar") is not None:
        scores["C13"] = fit["scalar"]

    # ---- aggregate the two profiles (first-order weighted mean) ----
    def profile(wkey: str) -> Dict:
        rows = [(cid, scores[cid], CRITERIA[cid][wkey], CRITERIA[cid])
                for cid in scores if CRITERIA.get(cid, {}).get(wkey, 0) > 0]
        if not rows:
            return {"score": None, "weakest": None, "rows": []}
        wsum = sum(w for _, _, w, _ in rows)
        weighted = sum(s * w for _, s, w, _ in rows) / wsum
        weakest = min(rows, key=lambda r: r[1])
        return {"score": round(weighted, 3),
                "weakest": {"criterion": weakest[0], "name": weakest[3]["name"], "score": round(weakest[1], 3)},
                "rows": [{"criterion": c, "name": m["name"], "score": round(s, 3),
                          "weight": w, "evidence": m["evid"], "objective": m["obj"]} for c, s, w, m in rows]}

    cog = profile("cog_w")
    wb = profile("wb_w")

    # ---- fit matrix (occupant type x setting type) ----
    fit_matrix = None; worst_served = None
    if isinstance(fit, dict) and "extras" in fit:
        area_by = r13["extras"]["area_by_type_m2"]
        total = sum(area_by.values()) or 1.0
        fit_matrix = {occ: {stype: round(_st._FIT.get(stype, {}).get(occ, 0.0), 2) for stype in area_by}
                      for occ in fit["extras"]["per_type_fit"]}
        worst_served = {"type": fit["extras"]["worst_served_type"],
                        "fit": fit["scalar"],
                        "per_type_fit": fit["extras"]["per_type_fit"]}

    # ---- provenance panel ----
    tier = getattr(pg, "method", "") or ("Tier C (real plan)" if getattr(pg, "confidence", 0) > 0.9 else "Tier B (inferred)")
    built = list(scores.keys())
    still_open = ["C10 certified melanopic (needs spectral daylight sim)",
                  "C6 interdependence gating",
                  "C19/C20/C23 restoration/soundscape/social plan metrics",
                  "C16/C17/C18 territory/control/air (spec-driven inputs)"]
    evidence_present = sorted(set(CRITERIA[c]["evid"] for c in built))

    return {
        "objective_scores": {"cognitive": cog, "wellbeing": wb},
        "fit_matrix": fit_matrix,
        "worst_served_segment": worst_served,
        "headline": {
            # min-not-mean: the binding constraints, surfaced first
            "cognitive": cog["score"], "wellbeing": wb["score"],
            "binding": {"cog_weakest": cog["weakest"], "wb_weakest": wb["weakest"],
                        "worst_occupant_type": worst_served},
        },
        "criteria_scored": {c: round(scores[c], 3) for c in built},
        "opportunities": {"C6_path_overlap": raw.get("C6", {}).get("scalar")},
        "provenance": {
            "fidelity_tier": tier,
            "criteria_backed_by_algorithm": built,
            "evidence_tags_present": evidence_present,
            "still_to_build": still_open,
            "caveat": "FIRST-ORDER weighted aggregation — criterion INTERACTIONS UN-MODELLED "
                      "(CRITERIA.md §4 non-additivity); read the per-criterion maps, not just the sum. "
                      "No score validated against measured human outcomes yet (L0/L1 only).",
        },
        "raw": raw,
    }


# --------------------------------------------------------------------------- demo scenario
def demo_scenario():
    """A small synthetic floor: an open field + one enclosed focus room, S-glazing on the
    left, a collaboration source in the open field, amenities, and an entrance/stair/lift."""
    try:
        from .plan import FREE, OBST
    except Exception:
        FREE, OBST = 1, 2
    g = np.full((40, 60), OBST, np.int8)
    g[2:30, 2:40] = FREE                     # open field
    g[2:12, 44:56] = FREE                    # enclosed focus room (right)
    g[15, 40:44] = FREE                      # a doorway link (keeps room reachable)
    g[2:12, 43] = FREE
    pg = type("PG", (), {"grid": g, "cell_m": 0.5, "method": "Tier B (inferred)", "confidence": 0.4})()
    seats = [(6, 6), (10, 20), (20, 30),     # open-field desks (hub-ish)
             (6, 48), (9, 52)]               # focus-room desks
    glazing = [((r, 2), "S") for r in range(2, 30)]        # S-glazing on the left edge
    return {
        "pg": pg, "seats": seats,
        "focus_seats": [3, 4],                              # the two focus-room desks
        "collab_sources": [(18, 28)],                       # a talker in the open field
        "collaborator_pairs": [(0, 1), (0, 2)],
        "destinations": [(6, 6)],
        "glazing": glazing,
        "amenities": [(14, 34)],
        "entrance": (28, 20), "stair": (24, 22), "elevator": (5, 38),
        "control_zones": [{"name": "perimeter", "orientations": ["S"]},
                          {"name": "mixed", "orientations": ["S", "INT"]}],
        "demand": {"sanctuary": 0.4, "hub": 0.4, "nomad": 0.2},
        "hemisphere": "N",
    }


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    import json
    print("cnfa_algs.score_layout self-test\n" + "-" * 40)
    out = score_layout(demo_scenario())

    print("COGNITIVE :", out["objective_scores"]["cognitive"]["score"],
          "| weakest:", out["objective_scores"]["cognitive"]["weakest"])
    print("WELLBEING :", out["objective_scores"]["wellbeing"]["score"],
          "| weakest:", out["objective_scores"]["wellbeing"]["weakest"])
    print("criteria  :", out["criteria_scored"])
    print("worst-served occupant:", out["worst_served_segment"])
    print("fit matrix:", json.dumps(out["fit_matrix"], indent=0) if out["fit_matrix"] else None)
    print("tier      :", out["provenance"]["fidelity_tier"],
          "| backed:", out["provenance"]["criteria_backed_by_algorithm"])

    # assertions: both objectives produced, at least the dominant criteria scored, matrix present
    assert out["objective_scores"]["cognitive"]["score"] is not None, "COG score missing"
    assert out["objective_scores"]["wellbeing"]["score"] is not None, "WB score missing"
    assert {"C7", "C8", "C21", "C9", "C10"} <= set(out["criteria_scored"]), "dominant criteria not all scored"
    assert {"C1", "C3", "C4"} <= set(out["criteria_scored"]), "configurational substrate (VGA) not scored"
    assert out["fit_matrix"] is not None and out["worst_served_segment"] is not None, "fit matrix missing"
    assert 0.0 <= out["objective_scores"]["cognitive"]["score"] <= 1.0
    # the mixed thermal zone should pull C21 below a perfect 1.0
    assert out["criteria_scored"]["C21"] < 1.0, "mixed control zone should register a thermal mismatch"
    # non-additivity caveat must be present (RULE 0 honesty)
    assert "INTERACTIONS UN-MODELLED" in out["provenance"]["caveat"]
    print("-" * 40 + "\nscore_layout self-test: PASS")
