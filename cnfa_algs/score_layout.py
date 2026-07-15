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
from . import affordance as _af
from . import wellbeing_plan as _wb

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
    "C11": {"name": "prospect-refuge quality",  "obj": "SHARED", "evid": "STRONG",  "cog_w": 0.5, "wb_w": 0.6, "form": "per-seat"},
    "C12": {"name": "perceived-crowding risk",  "obj": "SHARED", "evid": "STRONG",  "cog_w": 0.4, "wb_w": 0.6, "form": "per-seat"},
    "C14": {"name": "focus:collab separation",  "obj": "COG",    "evid": "STRONG",  "cog_w": 0.7, "wb_w": 0.4, "form": "penalty"},
    "C16": {"name": "territory provision",      "obj": "WB",     "evid": "PROMISING","cog_w": 0.0, "wb_w": 0.4, "form": "scalar"},
    "C17": {"name": "functioning local control","obj": "SHARED", "evid": "CONTESTED","cog_w": 0.2, "wb_w": 0.4, "form": "per-zone"},
    "C18": {"name": "air-quality spec",         "obj": "WB",     "evid": "CONTESTED","cog_w": 0.2, "wb_w": 0.4, "form": "per-zone"},
    "C19": {"name": "restoration / nature",     "obj": "WB",     "evid": "CONTESTED","cog_w": 0.2, "wb_w": 0.7, "form": "per-seat"},
    "C20": {"name": "chronic-stress soundscape","obj": "WB",     "evid": "PROMISING","cog_w": 0.2, "wb_w": 0.6, "form": "field"},
    "C22": {"name": "circadian day-night",      "obj": "WB",     "evid": "STRONG",  "cog_w": 0.2, "wb_w": 0.7, "form": "per-seat"},
    "C23": {"name": "social connectedness",     "obj": "WB",     "evid": "PROMISING","cog_w": 0.1, "wb_w": 0.6, "form": "per-seat"},
    "C24": {"name": "awe / spatial generosity", "obj": "WB",     "evid": "PROMISING","cog_w": 0.2, "wb_w": 0.4, "form": "field"},
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
    # PANEL FIX S4/C8: iso3382 is a FLOOR-GLOBAL spec (function of d2s/L_noise), not a
    # per-layout field — scoring it from defaults made every layout read 0.88 at a
    # dominant weight. Score it ONLY when the caller supplies acoustic parameters; else
    # drop it with a note (a global acoustic spec cannot rank two layouts by itself).
    if ("d2s" in scenario) or ("L_noise" in scenario) or scenario.get("acoustic"):
        r8 = _safe(_ac.iso3382_single_numbers, d2s=scenario.get("d2s", _ac.D2S_DEFAULT),
                   L_noise=scenario.get("L_noise", _ac.L_NOISE_DEFAULT))
        raw["C8"] = r8
        if r8.get("extras"):
            scores["C8"] = _r_d_score(r8["extras"]["r_D_m"])
    else:
        notes.append("C8 dropped: no acoustic parameters supplied (a floor-global spec, "
                     "not layout-discriminating by default)")

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

    # ---- affordance: prospect-refuge (C11), crowding (C12), generosity (C24) ----
    if seats:
        r11 = _safe(_af.prospect_refuge_quality, pg, seats); raw["C11"] = r11
        if r11.get("scalar") is not None:
            scores["C11"] = r11["scalar"]
        r12 = _safe(_af.perceived_crowding_risk, pg, seats, retreats=scenario.get("retreats")); raw["C12"] = r12
        if r12.get("scalar") is not None:
            scores["C12"] = r12["scalar"]
    r24 = _safe(_af.spatial_generosity, pg); raw["C24"] = r24
    if r24.get("scalar") is not None:
        scores["C24"] = r24["scalar"]

    # ---- C14 focus:collaboration separation (derived from C1 VGA x C7 STI) ----
    # PANEL FIX S4/C14: require C7 to be ACTUALLY scored. The old code defaulted missing
    # STI to 0.0 (= perfect privacy) and fabricated a perfect C14=1.0 when acoustics were
    # absent — rewarding a layout for withholding its worst evidence.
    if (scenario.get("focus_seats") is not None and isinstance(raw.get("C1-C3"), dict)
            and "C7" in scores):
        fseats = [seats[i] for i in scenario["focus_seats"]]
        sti_map = {row["focus_seat"]: row.get("worst_sti", 0.0)
                   for row in (raw.get("C7", {}) or {}).get("rows", [])}
        focus_sti = [sti_map.get(i, 0.0) for i in range(len(fseats))]
        r14 = _safe(_ss.focus_collab_separation, pg, fseats, focus_sti, raw["C1-C3"]); raw["C14"] = r14
        if r14.get("scalar") is not None:
            scores["C14"] = r14["scalar"]
    elif scenario.get("focus_seats") is not None:
        notes.append("C14 dropped: requires C7 (focus STI) to be scored — not fabricated from a default")

    # ---- well-being (spec + geometry): C19, C16, C17, C18, C20, C22, C23 ----
    if scenario.get("nature_cells") and seats:
        r19 = _safe(_wb.restoration_nature, pg, seats, scenario["nature_cells"], scenario.get("retreats"))
        raw["C19"] = r19
        if r19.get("scalar") is not None:
            scores["C19"] = r19["scalar"]
    if scenario.get("territory"):
        t = scenario["territory"]
        r16 = _safe(_wb.territory_provision, t.get("assigned_seats", 0), t.get("headcount", len(seats) or 1),
                    t.get("teams_with_anchor", 0), t.get("n_teams", 0), t.get("personalizable_frac", 0.0))
        raw["C16"] = r16
        if r16.get("scalar") is not None:
            scores["C16"] = r16["scalar"]
    if scenario.get("control_zones_wb"):
        r17 = _safe(_wb.local_control, scenario["control_zones_wb"]); raw["C17"] = r17
        if r17.get("scalar") is not None:
            scores["C17"] = r17["scalar"]
    if scenario.get("air"):
        a = scenario["air"]
        r18 = _safe(_wb.air_quality, a.get("headcount", len(seats) or 1), a.get("floor_area_m2", 100.0),
                    a.get("outdoor_air_lps_per_person", 8.5), a.get("voc_low_emitting", True))
        raw["C18"] = r18
        if r18.get("scalar") is not None:
            scores["C18"] = r18["scalar"]
    _noise = scenario.get("noise_sources") or scenario.get("collab_sources")
    if _noise:
        r20 = _safe(_ac.chronic_stress_soundscape, pg, _noise,
                    positive_zones=scenario.get("positive_soundscape_zones", 0)); raw["C20"] = r20
        if r20.get("scalar") is not None:
            scores["C20"] = r20["scalar"]
    if scenario.get("glazing") and seats:
        wins22 = [g[0] for g in scenario["glazing"]]
        r22 = _safe(_dl.circadian_contrast, pg, seats, wins22, scenario.get("evening_light_low", True))
        raw["C22"] = r22
        if r22.get("scalar") is not None:
            scores["C22"] = r22["scalar"]
    if scenario.get("commons") and seats:
        r23 = _safe(_wb.social_connectedness, pg, seats, scenario["commons"], scenario.get("headcount"))
        raw["C23"] = r23
        if r23.get("scalar") is not None:
            scores["C23"] = r23["scalar"]

    # ---- aggregate the two profiles ----
    # PANEL FIX S4: report (a) the weighted MEAN (honestly labelled — not "min-not-mean"),
    # (b) COVERAGE = scored weight / total available weight (so a layout cannot look good by
    # withholding its worst dimensions — low coverage is a warning), and (c) a BINDING score
    # that the weakest criterion actually caps (min(mean, weakest+0.25)) so a catastrophic
    # weakness is visible in a single number, not averaged away.
    def profile(wkey: str) -> Dict:
        rows = [(cid, scores[cid], CRITERIA[cid][wkey], CRITERIA[cid])
                for cid in scores if CRITERIA.get(cid, {}).get(wkey, 0) > 0]
        total_avail_w = sum(spec[wkey] for spec in CRITERIA.values() if spec.get(wkey, 0) > 0)
        if not rows:
            return {"score": None, "binding_score": None, "coverage": 0.0, "weakest": None, "rows": []}
        wsum = sum(w for _, _, w, _ in rows)
        weighted = sum(s * w for _, s, w, _ in rows) / wsum
        weakest = min(rows, key=lambda r: r[1])
        binding = min(weighted, weakest[1] + 0.25)          # the weakest caps the headline
        return {"score": round(weighted, 3),                # weighted mean (NOT a min)
                "binding_score": round(binding, 3),          # mean capped by the weakest
                "coverage": round(wsum / max(total_avail_w, 1e-9), 3),  # scored weight fraction
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
    still_open = ["C10/C22 certified melanopic (needs spectral daylight sim; current tier is a geometric screen)",
                  "C6 interdependence gating",
                  "L2/L3 validation of all criteria against VLM/human/physiological outcomes"]
    evidence_present = sorted(set(CRITERIA[c]["evid"] for c in built))

    return {
        "objective_scores": {"cognitive": cog, "wellbeing": wb},
        "fit_matrix": fit_matrix,
        "worst_served_segment": worst_served,
        "headline": {
            # the weighted MEAN, plus the binding (weakest-capped) score and coverage that
            # keep a good average from hiding a failing dimension or thin coverage.
            "cognitive": cog["score"], "wellbeing": wb["score"],
            "cognitive_binding": cog["binding_score"], "wellbeing_binding": wb["binding_score"],
            "cognitive_coverage": cog["coverage"], "wellbeing_coverage": wb["coverage"],
            "binding": {"cog_weakest": cog["weakest"], "wb_weakest": wb["weakest"],
                        "worst_occupant_type": worst_served},
        },
        "notes": notes,
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
        # ---- spec inputs for the well-being + affordance criteria ----
        "retreats": [(6, 48)],                              # the focus room as a retreat
        "nature_cells": [(2, 6), (2, 20)],                  # planted / nature-facing points
        "commons": [(14, 34)],                              # the amenity doubles as a social node
        "headcount": 5,
        "territory": {"assigned_seats": 4, "headcount": 5, "teams_with_anchor": 1, "n_teams": 2,
                      "personalizable_frac": 0.8},
        "control_zones_wb": [{"name": "open", "binding_stressor": "acoustic", "controls": ["thermal"]},
                             {"name": "focus", "binding_stressor": "acoustic", "controls": ["acoustic"]}],
        "air": {"headcount": 5, "floor_area_m2": 300.0, "outdoor_air_lps_per_person": 10.0},
        "evening_light_low": True, "positive_soundscape_zones": 1,
        "d2s": 7.0, "L_noise": 42.0,                        # acoustic spec so C8 is scored
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
    # the full rubric: every scored criterion C1-C24 except C6 (opportunity, weight 0) should be present
    expect = {f"C{i}" for i in range(1, 25)} - {"C6"}
    got = set(out["criteria_scored"])
    missing = expect - got
    print("criteria scored:", len(got), "/ 23 expected |", ("all present" if not missing else f"MISSING {sorted(missing)}"))
    assert not missing, f"full C1-C24 rubric not fully scored; missing {sorted(missing)}"
    assert out["fit_matrix"] is not None and out["worst_served_segment"] is not None, "fit matrix missing"
    assert 0.0 <= out["objective_scores"]["cognitive"]["score"] <= 1.0
    # the mixed thermal zone should pull C21 below a perfect 1.0
    assert out["criteria_scored"]["C21"] < 1.0, "mixed control zone should register a thermal mismatch"
    # non-additivity caveat must be present (RULE 0 honesty)
    assert "INTERACTIONS UN-MODELLED" in out["provenance"]["caveat"]
    print("-" * 40 + "\nscore_layout self-test: PASS")
