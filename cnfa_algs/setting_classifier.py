"""
cnfa_algs.setting_classifier — SETTING VARIETY & SEGMENT FIT (CRITERIA.md C13).

A floor must serve heterogeneous occupants (sanctuary / hub / nomad; STATE_OF_KNOWLEDGE
G1-G3), so the score is MINIMUM fit across types, not the average — and a monoculture
(all open, or all cellular) fails by construction. This module computes the raw material
for that: it classifies the free space into SETTING TYPES and reports the variety and the
enclosed:open balance.

  classify_settings — label each free-space REGION as enclosed_room / open_field /
                      circulation from geometry (area, elongation, interior openness),
                      then report per-type area, the count of distinct setting types
                      present, the enclosed:open ratio, and a variety scalar.
  segment_fit       — given an occupant-type demand profile (share of sanctuary/hub/nomad)
                      and the setting mix, the MINIMUM fit across types (the binding
                      constraint), which is what C13 actually scores.

HONEST SCOPE. Classification is at the connected-free-REGION level, so it separates walled
rooms, corridors, and an open field cleanly — but an open-plan floor that mixes desks and
aisles in ONE un-partitioned region is a single "open_field" here; separating desk-field
from aisle inside one region needs the isovist/morphological layer (a later refinement).
Occupant-type FIT weights are a defensible prior, to be tuned at L3, not measured truth.

Self-test (analytic L0):
    python -m cnfa_algs.setting_classifier
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

# how each setting type serves each occupant type (prior; 0..1). Rows=setting, cols=type.
# sanctuary wants enclosure/quiet; hub wants open/visible; nomad wants variety/any surface.
_FIT = {
    "enclosed_room": {"sanctuary": 1.0, "hub": 0.3, "nomad": 0.6},
    "open_field":    {"sanctuary": 0.2, "hub": 1.0, "nomad": 0.7},
    "circulation":   {"sanctuary": 0.0, "hub": 0.3, "nomad": 0.4},
}


def _label(free: np.ndarray):
    try:
        import cv2
        n, lab = cv2.connectedComponents(free.astype(np.uint8), connectivity=8)
        return lab, n
    except Exception:
        from scipy.ndimage import label
        lab, n = label(free, structure=np.ones((3, 3)))
        return lab, n + 1


def classify_settings(pg, room_max_m2: float = 15.0, corridor_aspect: float = 3.0,
                      corridor_max_width_m: float = 2.2, min_type_m2: float = 2.0) -> Dict:
    """Classify each free REGION into enclosed_room / open_field / circulation and
    summarize the variety and enclosed:open balance of the floor."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    a_cell = cell * cell
    free = (grid == FREE)
    lab, n = _label(free)
    try:
        from scipy.ndimage import distance_transform_edt
        dist = distance_transform_edt(free) * cell        # metres to nearest wall
    except Exception:
        dist = np.zeros_like(free, float)

    regions = []
    for rid in range(1, n):
        m = (lab == rid)
        area_cells = int(m.sum())
        if area_cells == 0:
            continue
        area_m2 = area_cells * a_cell
        ys, xs = np.where(m)
        h = (ys.max() - ys.min() + 1) * cell
        w = (xs.max() - xs.min() + 1) * cell
        long_side, short_side = max(h, w), min(h, w)
        aspect = long_side / max(short_side, 1e-6)
        max_open = float(dist[m].max())                   # interior openness (half-width-ish)
        if aspect >= corridor_aspect and (2 * max_open) <= corridor_max_width_m:
            stype = "circulation"
        elif area_m2 <= room_max_m2:
            stype = "enclosed_room"
        else:
            stype = "open_field"
        regions.append({"region": rid, "type": stype, "area_m2": round(area_m2, 1),
                        "aspect": round(aspect, 2), "interior_openness_m": round(max_open, 2)})

    # aggregate per type
    by_type: Dict[str, float] = {}
    for r in regions:
        by_type[r["type"]] = by_type.get(r["type"], 0.0) + r["area_m2"]
    types_present = [t for t, a in by_type.items() if a >= min_type_m2]
    enclosed = by_type.get("enclosed_room", 0.0)
    openf = by_type.get("open_field", 0.0)
    ratio = (round(enclosed / openf, 3) if openf > 0 else None)
    variety = round(len(types_present) / 3.0, 3)          # of {enclosed, open, circulation}
    return {"key": "cnfa.plan.setting_variety", "criterion": "C13",
            "regions": regions,
            "scalar": variety,
            "extras": {"area_by_type_m2": {k: round(v, 1) for k, v in by_type.items()},
                       "types_present": types_present, "n_regions": len(regions),
                       "enclosed_to_open_ratio": ratio},
            "confidence": 0.4,
            "method": "connected free-region classification by area/elongation/interior-openness",
            "failure_modes": ["region-level: one un-partitioned open-plan floor = single open_field",
                              "desk-field vs aisle inside a region needs the isovist/morphology layer",
                              "thresholds (room<=15 m2, aspect>=3) are conventions, tune per project"]}


def segment_fit(setting_result: Dict,
                demand: Optional[Dict[str, float]] = None) -> Dict:
    """C13 core — MINIMUM fit across occupant types (the binding constraint), given the
    setting mix and a demand profile (share of sanctuary/hub/nomad; defaults equal).
    Fit for a type = area-weighted coverage by settings that serve it; the score is the
    WORST-served type, not the average (a floor good on average can fail a quartile)."""
    demand = demand or {"sanctuary": 1 / 3, "hub": 1 / 3, "nomad": 1 / 3}
    area_by_type = setting_result["extras"]["area_by_type_m2"]
    total = sum(area_by_type.values()) or 1.0
    per_type_fit = {}
    for occ in demand:
        # area-weighted mean fit that this occupant type gets from the setting mix
        num = sum(area * _FIT.get(stype, {}).get(occ, 0.0) for stype, area in area_by_type.items())
        per_type_fit[occ] = round(num / total, 3)
    min_occ = min(per_type_fit, key=per_type_fit.get)
    return {"key": "cnfa.plan.segment_fit", "criterion": "C13",
            "scalar": per_type_fit[min_occ],                 # the MINIMUM-fit (binding) score
            "extras": {"per_type_fit": per_type_fit, "worst_served_type": min_occ,
                       "demand": demand},
            "confidence": 0.4,
            "method": "area-weighted setting->occupant fit; score = worst-served type (min, not mean)",
            "failure_modes": ["fit weights are a prior (tune at L3), not measured",
                              "demand profile is a spec input (from the site Q-sort)",
                              "min-not-mean is deliberate: penalizes monoculture plans"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.setting_classifier self-test (analytic L0)\n" + "-" * 52)

    # build a floor with FOUR separated free regions (walls between them):
    #  - a big open field, two small rooms, one long thin corridor
    cell = 0.5
    g = np.full((60, 60), OBST, np.int8)                  # start solid, carve free regions
    g[2:22, 2:40] = FREE      # open field: 20x38 cells = 10 m x 19 m = 190 m2
    g[30:36, 2:10] = FREE     # room A: 6x8 = 3 m x 4 m = 12 m2 (<=15 -> enclosed)
    g[30:36, 15:23] = FREE    # room B: same, enclosed
    g[45:47, 2:50] = FREE     # corridor: 2x48 = 1 m x 24 m, aspect 24 -> circulation
    pg = type("PG", (), {"grid": g, "cell_m": cell})()

    res = classify_settings(pg, room_max_m2=15, corridor_aspect=3, corridor_max_width_m=2.2)
    types = {r["region"]: r["type"] for r in res["regions"]}
    areas = res["extras"]["area_by_type_m2"]
    print("regions   :", [(r["type"], r["area_m2"], r["aspect"]) for r in res["regions"]])
    print("by type   :", areas, "| variety=", res["scalar"], "| encl:open=", res["extras"]["enclosed_to_open_ratio"])
    tset = set(res["extras"]["types_present"])
    assert {"open_field", "enclosed_room", "circulation"} <= tset, f"all three setting types expected, got {tset}"
    assert res["scalar"] == 1.0, "variety should be full (3/3 types present)"

    # segment fit: an all-open floor should badly fail the sanctuary type
    open_only = {"key": "x", "extras": {"area_by_type_m2": {"open_field": 200.0}}}
    sf = segment_fit(open_only)
    print("all-open  : per-type fit=", sf["extras"]["per_type_fit"], "-> worst:", sf["extras"]["worst_served_type"])
    assert sf["extras"]["worst_served_type"] == "sanctuary" and sf["scalar"] <= 0.25, "monoculture must fail sanctuary"

    # a mixed floor lifts the minimum fit
    sf2 = segment_fit(res)
    print("mixed floor: per-type fit=", sf2["extras"]["per_type_fit"], "min=", sf2["scalar"])
    assert sf2["scalar"] > sf["scalar"], "a varied floor should raise the worst-served fit vs all-open"

    print("-" * 52 + "\nsetting_classifier self-test: PASS")
