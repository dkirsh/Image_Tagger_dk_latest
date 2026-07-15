"""
cnfa_algs.thermal_plan — SOLAR-GAIN & THERMAL-ZONING screen (CRITERIA.md C21; also C6, C7 of the WB synthesis).

Thermal comfort is the top empirical dissatisfier (STATE_OF_KNOWLEDGE G4; WELLBEING C9),
and its DOMINANT failure mode is GEOMETRIC: a single control zone spanning differently
solar-loaded orientations, and desks placed against large cold/hot glazing (radiant
asymmetry). Those are computable from plan + façade orientation. This module provides:

  radiant_asymmetry_risk  — per-seat local-discomfort risk from proximity to large
                            glazing (ASHRAE 55 cool-window / warm-ceiling asymmetry);
                            worst near big high-solar (summer overheat) or any big cold
                            (winter downdraft) glazing.  (C21 / WB C6)
  thermal_zone_mismatch   — flag control ZONES whose seats are served by conflicting
                            solar loads (e.g. S/W-glazed + interior on one thermostat) —
                            the classic one-thermostat-many-loads failure.  (C21 / WB C9)
  solar_patch_opportunity — seats that can catch a winter solar patch = thermal-PLEASURE
                            (alliesthesia) opportunity, not just neutral comfort.  (WB C7)

HONEST SCOPE. This is an orientation-driven SCREEN/RANK, not a thermal simulation: it
has no air temperature, MRT in kelvin, or PMV. A certified PMV/PPD or MRT field needs an
energy/CFD model with the HVAC system, glazing U-value/SHGC, and climate file. What is
defensible from geometry alone is the *relative* solar load by orientation, the *near-
glazing radiant-risk* seats, and the *zoning mismatch* — which is exactly the dominant
failure the literature names. Solar-gain indices flip by hemisphere.

Self-test (analytic L0):
    python -m cnfa_algs.thermal_plan
"""
from __future__ import annotations
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2
from .los import segment_is_free   # panel fix S5: glazing effects must not pass through walls

RC = Tuple[int, int]

# Relative annual solar-gain load by façade orientation (northern hemisphere).
# S highest; W high AND worst for afternoon overheating/glare; E moderate; N lowest.
_SOLAR_N_HEMISPHERE = {"S": 1.0, "SW": 0.95, "W": 0.85, "SE": 0.8,
                       "E": 0.6, "NW": 0.55, "NE": 0.4, "N": 0.2}


def solar_gain_index(orientation: str, hemisphere: str = "N") -> float:
    """Relative solar-gain load [0..1] for a façade orientation. Flips S<->N below eq."""
    o = orientation.upper()
    if hemisphere.upper() == "S":                 # mirror N<->S (swap the N/S component)
        swap = {"N": "S", "S": "N", "NE": "SE", "SE": "NE", "NW": "SW", "SW": "NW"}
        o = swap.get(o, o)
    return float(_SOLAR_N_HEMISPHERE.get(o, 0.5))


def _glazing_arrays(glazing: Sequence[Tuple[RC, str]]):
    cells = np.array([g[0] for g in glazing], float) if len(glazing) else np.zeros((0, 2))
    orients = [g[1] for g in glazing]
    return cells, orients


# ------------------------------------------------------- C21 / C6: radiant asymmetry
def radiant_asymmetry_risk(pg, seats: Sequence[RC], glazing: Sequence[Tuple[RC, str]],
                           near_m: float = 1.5, big_run_cells: int = 10,
                           hemisphere: str = "N") -> Dict:
    """Per-seat radiant-discomfort risk from being close to LARGE glazing. Risk rises
    when a seat is within `near_m` of a glazing run and that run is big; weighted up for
    high-solar orientations (summer overheat) — any large glazing also carries winter
    cold-radiant risk. Returns per-seat risk [0..1] and a flag."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    cells, orients = _glazing_arrays(glazing)
    # size of each glazing RUN by orientation (proxy: count of glazing cells sharing orientation)
    run_by_orient: Dict[str, int] = {}
    for o in orients:
        run_by_orient[o] = run_by_orient.get(o, 0) + 1
    rows = []
    for k, s in enumerate(seats):
        risk = 0.0; drivers = []
        if len(cells):
            d = np.hypot(cells[:, 0] - s[0], cells[:, 1] - s[1]) * cell
            for idx in np.where(d <= near_m)[0]:
                o = orients[idx]
                run = run_by_orient.get(o, 1)
                if run < big_run_cells:              # only LARGE glazing drives asymmetry
                    continue
                if not segment_is_free(grid, s, (int(cells[idx, 0]), int(cells[idx, 1]))):
                    continue                         # S5: a wall between seat & glazing blocks radiant effect
                proximity = 1.0 - 0.5 * (min(d[idx], near_m) / near_m)  # 1.0 at glazing -> 0.5 at near_m
                solar = solar_gain_index(o, hemisphere)
                # summer(solar-weighted) OR winter(cold, orientation-independent) — take worst
                r = proximity * max(0.4 + 0.6 * solar, 0.6)
                if r > risk:
                    risk = r; drivers = [o]
        rows.append({"seat": k, "radiant_risk": round(float(risk), 3),
                     "at_risk": bool(risk >= 0.5), "driver_orientation": (drivers[0] if drivers else None)})
    n_risk = sum(1 for r in rows if r["at_risk"])
    return {"key": "cnfa.thermal.radiant_asymmetry", "criterion": "C21",
            "rows": rows,
            "scalar": (round(1 - n_risk / len(seats), 3) if seats else None),  # fraction NOT at radiant risk
            "extras": {"n_seats": len(seats), "n_at_risk": n_risk, "near_m": near_m,
                       "big_run_cells": big_run_cells},
            "confidence": 0.4,
            "method": "geometric near-large-glazing radiant-risk screen (ASHRAE 55 asymmetry direction)",
            "failure_modes": ["screen only — no MRT in kelvin / PMV (needs energy+glazing U/SHGC model)",
                              "glazing size proxied by cell count per orientation",
                              "penalize desks <~1 m from large cold/hot façades (the actionable rule)"]}


# ------------------------------------------------------- C21 / C9: thermal-zone mismatch
def thermal_zone_mismatch(pg, zones: Sequence[Dict], hemisphere: str = "N",
                          mismatch_gap: float = 0.4) -> Dict:
    """Flag control ZONES that span conflicting solar loads. Each zone dict:
    {"name": str, "orientations": [str,...]} = the façade orientations whose glazing
    serves that thermostat zone (include 'INT' for interior/no-glazing). A zone is
    mismatched if the spread of solar-gain indices across its served orientations
    exceeds `mismatch_gap` — one setpoint cannot satisfy both a hot and a cool load."""
    # PANEL FIX S7/C21: a solar-INDEX spread alone misses the textbook failures. East and
    # West have SIMILAR annual indices but OPPOSITE peak TIMES (morning vs afternoon sun) —
    # one thermostat cannot serve both; likewise any perimeter+interior mix. Add an explicit
    # peak-time / perimeter-vs-core opposition test alongside the index spread.
    def _bucket(o):
        o = o.upper()
        if o in ("INT", "INTERIOR", "CORE"):
            return "core"
        if "E" in o and "W" not in o:
            return "am"          # east-ish: morning peak
        if "W" in o:
            return "pm"          # west-ish: afternoon peak
        return "mid"             # N/S: no strong am/pm bias
    rows = []
    for z in zones:
        os = z.get("orientations", [])
        loads = [0.0 if o.upper() in ("INT", "INTERIOR", "CORE") else solar_gain_index(o, hemisphere) for o in os]
        spread = (max(loads) - min(loads)) if loads else 0.0
        buckets = {_bucket(o) for o in os}
        peak_conflict = ("am" in buckets and "pm" in buckets)              # E + W
        perimeter_core = ("core" in buckets and len(buckets - {"core"}) > 0 and max(loads) >= 0.6)  # glazed + interior
        mismatch = bool(spread > mismatch_gap or peak_conflict or perimeter_core)
        rows.append({"zone": z.get("name", "?"), "orientations": os,
                     "load_spread": round(float(spread), 3),
                     "peak_time_conflict": peak_conflict, "perimeter_core_mix": perimeter_core,
                     "mismatch": mismatch})
    n_bad = sum(1 for r in rows if r["mismatch"])
    return {"key": "cnfa.thermal.zone_mismatch", "criterion": "C21",
            "rows": rows,
            "scalar": (round(1 - n_bad / len(rows), 3) if rows else None),  # fraction of zones coherent
            "extras": {"n_zones": len(rows), "n_mismatched": n_bad, "mismatch_gap": mismatch_gap},
            "confidence": 0.5,
            "method": "solar-load spread across each control zone's served orientations",
            "failure_modes": ["orientations-per-zone is a spec input (from the HVAC zoning plan)",
                              "solar index is relative/annual; a climate+SHGC model refines it",
                              "the dominant real thermal failure — worth weighting despite being a screen"]}


# ------------------------------------------------------- WB C7: solar-patch pleasure
def solar_patch_opportunity(pg, seats: Sequence[RC], glazing: Sequence[Tuple[RC, str]],
                            near_m: float = 4.0, hemisphere: str = "N") -> Dict:
    """WB C7 (alliesthesia) — seats that can catch a low-angle winter solar patch from a
    sun-facing (high-solar) window = a thermal-PLEASURE opportunity, provided they are
    NOT flagged for summer radiant overheat. A design POSITIVE, scored separately."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    cells, orients = _glazing_arrays(glazing)
    # PANEL FIX S7/WB-C7: the docstring promised an overheat exclusion that did not exist.
    # Compute the radiant-overheat set (seats at risk from large high-solar glazing) and
    # EXCLUDE them from the pleasure opportunity — a seat cannot be both at-risk and a patch.
    overheat = {r["seat"] for r in radiant_asymmetry_risk(pg, seats, glazing,
                                                          hemisphere=hemisphere)["rows"] if r["at_risk"]}
    rows = []
    for k, s in enumerate(seats):
        opp = 0.0; o_hit = None
        if k not in overheat and len(cells):
            d = np.hypot(cells[:, 0] - s[0], cells[:, 1] - s[1]) * cell
            for idx in np.where(d <= near_m)[0]:
                solar = solar_gain_index(orients[idx], hemisphere)
                if solar >= 0.8 and segment_is_free(grid, s, (int(cells[idx, 0]), int(cells[idx, 1]))):
                    score = solar * (1.0 - d[idx] / near_m)
                    if score > opp:
                        opp = score; o_hit = orients[idx]
        rows.append({"seat": k, "solar_patch_score": round(float(opp), 3),
                     "has_opportunity": bool(opp >= 0.3), "overheat_excluded": bool(k in overheat),
                     "orientation": o_hit})
    n_opp = sum(1 for r in rows if r["has_opportunity"])
    return {"key": "cnfa.thermal.solar_patch", "criterion": "WB-C7",
            "rows": rows,
            "scalar": (round(n_opp / len(seats), 3) if seats else None),
            "extras": {"n_seats": len(seats), "n_with_opportunity": n_opp, "near_m": near_m},
            "confidence": 0.35,
            "method": "proximity to sun-facing glazing as a winter thermal-pleasure (alliesthesia) opportunity",
            "failure_modes": ["pleasure needs non-uniformity & seasonality — a positive, not a comfort floor",
                              "must be reconciled with summer overheat (same window, opposite sign)",
                              "no sun-path geometry — a screen; a solar sim refines the patch location/timing"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.thermal_plan self-test (analytic L0)\n" + "-" * 46)

    # solar index sanity (N hemisphere): S > W > E > N; flips in S hemisphere
    assert solar_gain_index("S") > solar_gain_index("W") > solar_gain_index("E") > solar_gain_index("N")
    assert solar_gain_index("N", "S") > solar_gain_index("S", "S")   # hemisphere flip
    print(f"solar idx: S={solar_gain_index('S')} W={solar_gain_index('W')} "
          f"E={solar_gain_index('E')} N={solar_gain_index('N')}  (N-hemi, S>W>E>N ok)")

    # room 30 wide; big S-glazing run along left wall (col 0), interior to the right
    grid = np.full((20, 30), FREE, np.int8)
    pg = type("PG", (), {"grid": grid, "cell_m": 0.5})()
    glaz = [((r, 0), "S") for r in range(20)]              # 20-cell S-glazing run (big)

    # seat 1 m from big S-glazing = radiant risk; seat 10 m away = safe
    res = radiant_asymmetry_risk(pg, seats=[(10, 2), (10, 24)], glazing=glaz, near_m=1.5, big_run_cells=10)
    print("C21 radiant:", [(r["seat"], r["radiant_risk"], r["at_risk"], r["driver_orientation"]) for r in res["rows"]])
    assert res["rows"][0]["at_risk"] and not res["rows"][1]["at_risk"], "near-glazing seat at risk, far seat safe"

    # zone mismatch: S+INT (perimeter+core), E+W (peak-time conflict) both fail; N+N coherent
    zres = thermal_zone_mismatch(pg, zones=[
        {"name": "Z1", "orientations": ["S", "INT"]},      # hot glazing + cool interior -> mismatch
        {"name": "Z2", "orientations": ["N", "N"]},        # coherent
        {"name": "Z3", "orientations": ["E", "W"]},        # opposite peak TIMES -> mismatch (was missed)
    ], mismatch_gap=0.4)
    print("C21 zones :", [(r["zone"], r["load_spread"], r["peak_time_conflict"], r["mismatch"]) for r in zres["rows"]])
    assert zres["rows"][0]["mismatch"] and not zres["rows"][1]["mismatch"], "S+INT mismatched, N+N coherent"
    assert zres["rows"][2]["mismatch"] and zres["rows"][2]["peak_time_conflict"], "E+W is a peak-time conflict"

    # solar-patch pleasure: a seat SET BACK from S-glazing (winter patch, not summer overheat)
    # gets the opportunity; a seat pressed against the large glazing is overheat-EXCLUDED.
    sp = solar_patch_opportunity(pg, seats=[(10, 4), (10, 1), (10, 25)], glazing=glaz, near_m=4.0)
    print("WB-C7 sun :", [(r["seat"], r["solar_patch_score"], r["has_opportunity"], r["overheat_excluded"]) for r in sp["rows"]])
    assert sp["rows"][0]["has_opportunity"], "set-back seat gets the winter patch"
    assert sp["rows"][1]["overheat_excluded"], "seat against large S-glazing is overheat-excluded (not a patch)"
    assert not sp["rows"][2]["has_opportunity"], "far interior seat: no patch"

    print("-" * 46 + "\nthermal_plan self-test: PASS")
