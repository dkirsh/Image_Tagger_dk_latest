"""
cnfa_algs.wellbeing_plan — well-being plan metrics that mix geometry + spec (CRITERIA.md C16-C19, C23).

These criteria are not pure geometry: they consume a spec/policy input (the seating policy,
the control inventory, the ventilation design, the greenery/commons schedule) and compute
the criterion from it. Each is real and testable given its input; where the input is a spec
the caller must supply, that is stated (not hidden as if geometry-derived).

  C19 restoration_nature   — % seats with a nature view (LOS to greenery/nature-window in
                             range) + retreat proximity (A1-A3, E6 of WELLBEING).
  C16 territory_provision  — assigned-seat ratio + team-anchor provision (F3). Spec input.
  C17 local_control        — credit control ONLY where it targets the zone's binding
                             stressor (G5/A5 conditionality). Spec input.
  C18 air_quality          — steady-state CO2 at design occupancy + L/s/person + VOC class
                             (C1-C4 of WELLBEING). Ventilation calc, reported as a RANGE.
  C23 social_connectedness — commons provision per N + isolated-seat detection (co-presence
                             in the isovist), refuge-paired so exposure != connectedness (F6).

Self-test (analytic L0):
    python -m cnfa_algs.wellbeing_plan
"""
from __future__ import annotations
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

RC = Tuple[int, int]
_CO2_OUTDOOR = 420.0        # ppm ambient
_CO2_GEN_LPS = 0.0052       # L/s CO2 generation per sedentary person


from .los import segment_is_free as _los   # supercover LOS (diagonal walls block) — panel fix S1


# ------------------------------------------------------------------ C19 restoration / nature
def restoration_nature(pg, seats: Sequence[RC], nature_cells: Sequence[RC],
                       retreats: Optional[Sequence[RC]] = None,
                       max_view_m: float = 10.0, retreat_reach_m: float = 15.0) -> Dict:
    """C19 — per-seat restorative access: line-of-sight to nature (greenery / nature-facing
    glazing) within view range, plus a nearby retreat. Nature-view is the single most
    operationalizable well-being variable (WELLBEING A1)."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    nat = np.array(nature_cells) if len(nature_cells) else np.zeros((0, 2))
    ret = np.array(retreats) if retreats else np.zeros((0, 2))
    rows = []
    for k, s in enumerate(seats):
        has_nat = False
        if len(nat):
            d = np.hypot(nat[:, 0] - s[0], nat[:, 1] - s[1]) * cell
            for idx in np.argsort(d):
                if d[idx] > max_view_m:
                    break
                if _los(grid, s, (int(nat[idx, 0]), int(nat[idx, 1]))):
                    has_nat = True; break
        near_retreat = bool(len(ret) and (np.hypot(ret[:, 0] - s[0], ret[:, 1] - s[1]) * cell).min() <= retreat_reach_m)
        rows.append({"seat": k, "nature_view": has_nat, "retreat_within_reach": near_retreat,
                     "restorative": bool(has_nat or near_retreat)})
    n_nat = sum(1 for r in rows if r["nature_view"])
    n_rest = sum(1 for r in rows if r["restorative"])
    return {"key": "cnfa.wellbeing.restoration", "criterion": "C19",
            "rows": rows,
            "scalar": (round(n_rest / len(seats), 3) if seats else None),
            "extras": {"n_seats": len(seats), "n_nature_view": n_nat, "n_restorative": n_rest},
            "confidence": 0.45,
            "method": "per-seat LOS-to-nature + retreat proximity (WELLBEING A1-A3)",
            "failure_modes": ["nature cells are a spec input (greenery / nature-facing glazing locations)",
                              "view CONTENT (real nature vs blank) needs the image layer, not the plan",
                              "CONTESTED office effect sizes; direction STRONG, magnitude soft"]}


# ------------------------------------------------------------------ C16 territory provision
def territory_provision(assigned_seats: int, headcount: int,
                        teams_with_anchor: int = 0, n_teams: int = 0,
                        personalizable_frac: float = 0.0) -> Dict:
    """C16 — assigned-seat ratio + team-anchor provision (F3). Pure spec/policy calc;
    hot-desking cost is implementation-dependent, so this scores provision, not a verdict."""
    assigned_ratio = (assigned_seats / headcount) if headcount else 0.0
    anchor_frac = (teams_with_anchor / n_teams) if n_teams else 0.0
    score = 0.5 * float(np.clip(assigned_ratio, 0, 1)) + 0.3 * anchor_frac + 0.2 * float(np.clip(personalizable_frac, 0, 1))
    return {"key": "cnfa.wellbeing.territory", "criterion": "C16",
            "scalar": round(score, 3),
            "extras": {"assigned_ratio": round(assigned_ratio, 3), "team_anchor_frac": round(anchor_frac, 3),
                       "personalizable_frac": round(personalizable_frac, 3)},
            "confidence": 0.4,
            "method": "0.5*assigned-ratio + 0.3*team-anchor + 0.2*personalizable (F3 provision)",
            "failure_modes": ["pure spec/policy input (seating policy, not geometry)",
                              "hot-desk cost is implementation-dependent (ABW neighborhoods can preserve belonging)",
                              "CONTESTED/PROMISING; largely qualitative evidence"]}


# ------------------------------------------------------------------ C17 functioning local control
def local_control(zones: Sequence[Dict]) -> Dict:
    """C17 — credit control ONLY where it targets the zone's binding stressor (G5). Each
    zone: {"name", "binding_stressor": 'acoustic'|'thermal'|'visual'|..., "controls": [stressor,...]}.
    A thermostat in a zone whose binding stressor is noise earns nothing."""
    rows = []
    for z in zones:
        binding = z.get("binding_stressor")
        controls = [c.lower() for c in z.get("controls", [])]
        credited = bool(binding and binding.lower() in controls)
        rows.append({"zone": z.get("name", "?"), "binding_stressor": binding,
                     "controls": z.get("controls", []), "credited": credited})
    n_ok = sum(1 for r in rows if r["credited"])
    return {"key": "cnfa.wellbeing.local_control", "criterion": "C17",
            "rows": rows,
            "scalar": (round(n_ok / len(rows), 3) if rows else None),
            "extras": {"n_zones": len(rows), "n_credited": n_ok},
            "confidence": 0.4,
            "method": "control credited only vs the binding local stressor (G5 conditionality)",
            "failure_modes": ["binding stressor + control inventory are spec inputs",
                              "a flat 'has controls' bonus is NOT supported (the whole point of C17)",
                              "CONTESTED (control-as-king) / STRONG (the conditionality qualifier)"]}


# ------------------------------------------------------------------ C18 air quality
def air_quality(headcount: int, floor_area_m2: float, outdoor_air_lps_per_person: float,
                voc_low_emitting: bool = True) -> Dict:
    """C18 — steady-state CO2 at design occupancy + L/s/person + VOC class, reported as a
    RANGE not a cognition promise (WELLBEING C1-C4). CO2 is a ventilation PROXY."""
    Q = max(outdoor_air_lps_per_person, 1e-6)
    co2 = _CO2_OUTDOOR + (_CO2_GEN_LPS / Q) * 1e6
    co2_rating = "good" if co2 < 800 else ("fair" if co2 <= 1000 else "poor")
    vent_rating = "good" if outdoor_air_lps_per_person >= 8.5 else ("fair" if outdoor_air_lps_per_person >= 5 else "poor")
    # score from CO2 (proxy): <=700->1, >=1100->0, linear; VOC low-emitting is a small bonus
    co2_score = float(np.clip((1100 - co2) / 400.0, 0, 1))
    score = 0.9 * co2_score + 0.1 * (1.0 if voc_low_emitting else 0.0)
    return {"key": "cnfa.wellbeing.air_quality", "criterion": "C18",
            "scalar": round(score, 3),
            "extras": {"predicted_co2_ppm": round(co2, 0), "co2_rating": co2_rating,
                       "outdoor_air_lps_person": outdoor_air_lps_per_person, "ventilation_rating": vent_rating,
                       "voc_low_emitting": voc_low_emitting, "area_per_person_m2": round(floor_area_m2 / max(headcount, 1), 1)},
            "confidence": 0.45,
            "method": "steady-state CO2 (ventilation proxy) + L/s/person + VOC class — a RANGE, not a cognition ROI",
            "failure_modes": ["ventilation rate & VOC class are spec inputs (HVAC/materials design)",
                              "CO2 is a ventilation PROXY, not a direct cognitive toxicant (CONTESTED)",
                              "do NOT attach the Allen COGfx 61/101% figures (over-claim watchlist)"]}


# ------------------------------------------------------------------ C23 social connectedness
def social_connectedness(pg, seats: Sequence[RC], commons_cells: Sequence[RC],
                         headcount: Optional[int] = None,
                         commons_target_per_n: float = 0.1, isolate_max_visible: int = 1,
                         commons_reach_m: float = 30.0) -> Dict:
    """C23 — commons provision per N + isolated-seat detection. A seat that sees <=
    isolate_max_visible other seats along its isovist and has no commons within reach is a
    loneliness-risk seat. Exposure != connectedness, so this is about VOLUNTARY contact
    opportunity, not forced visibility (F6)."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    N = headcount or len(seats)
    commons = np.array(commons_cells) if len(commons_cells) else np.zeros((0, 2))
    provision = (len(commons_cells) / max(N, 1))            # commons cells per occupant (proxy)
    provision_ok = provision >= commons_target_per_n
    from .affordance import _seat_isovist          # for the refuge term (F6 pairing)
    rows = []
    n_seats = len(seats)
    for k, s in enumerate(seats):
        visible = sum(1 for j, t in enumerate(seats) if j != k and _los(grid, s, t))
        near_commons = bool(len(commons) and (np.hypot(commons[:, 0] - s[0], commons[:, 1] - s[1]) * cell).min() <= commons_reach_m)
        isolated = bool(visible <= isolate_max_visible and not near_commons)
        # PANEL FIX S7/C23: implement the F6 refuge pairing the docstring promised. A
        # maximally EXPOSED seat (sees ~everyone, no protected back) is surveilled, not
        # connected — count it neither isolated NOR well-connected.
        _, _, refuge = _seat_isovist(grid, s, 32, cell)
        # surveilled = seen by MANY with no protected back (not merely by a couple of
        # neighbours) — an absolute floor prevents small clusters reading as "exposed".
        exposed = bool(refuge < 0.10 and visible >= 8 and visible >= 0.6 * max(n_seats - 1, 1))
        well_connected = bool((not isolated) and (not exposed))
        rows.append({"seat": k, "visible_seats": visible, "commons_within_reach": near_commons,
                     "refuge_frac": round(float(refuge), 3),
                     "loneliness_risk": isolated, "over_exposed": exposed,
                     "well_connected": well_connected})
    n_iso = sum(1 for r in rows if r["loneliness_risk"])
    n_exposed = sum(1 for r in rows if r["over_exposed"])
    connected_frac = sum(1 for r in rows if r["well_connected"]) / max(n_seats, 1)
    score = 0.5 * connected_frac + 0.5 * (1.0 if provision_ok else float(np.clip(provision / commons_target_per_n, 0, 1)))
    return {"key": "cnfa.wellbeing.social_connectedness", "criterion": "C23",
            "rows": rows,
            "scalar": round(float(score), 3),
            "extras": {"n_seats": n_seats, "n_loneliness_risk": n_iso, "n_over_exposed": n_exposed,
                       "commons_provision_per_occupant": round(provision, 3), "provision_ok": provision_ok},
            "confidence": 0.4,
            "method": "commons-per-N + isolated-seat + F6 refuge pairing (exposure != connectedness)",
            "failure_modes": ["commons cells & headcount are spec inputs",
                              "provision != use (needs policy + culture + survey to confirm connection)",
                              "keep separate from task-collaboration (C5/C6) — do not double-count co-presence"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.wellbeing_plan self-test (analytic L0)\n" + "-" * 48)

    # C19: seat with LOS to greenery vs a walled-off seat
    g = np.full((20, 30), FREE, np.int8)
    pg = type("PG", (), {"grid": g, "cell_m": 0.5})()
    nature = [(10, 0)]                                   # greenery on the left wall
    r19 = restoration_nature(pg, [(10, 3), (10, 25)], nature, retreats=[(2, 2)], max_view_m=5)
    print("C19:", [(x["seat"], x["nature_view"], x["restorative"]) for x in r19["rows"]], "score=", r19["scalar"])
    assert r19["rows"][0]["nature_view"] and not r19["rows"][1]["nature_view"], "near seat sees nature, far does not"

    # C16 territory: fully assigned + team anchors scores high; all hot-desk scores low
    hi = territory_provision(assigned_seats=100, headcount=100, teams_with_anchor=8, n_teams=8, personalizable_frac=1.0)
    lo = territory_provision(assigned_seats=0, headcount=100, teams_with_anchor=0, n_teams=8, personalizable_frac=0.0)
    print("C16: assigned score=", hi["scalar"], "| hot-desk score=", lo["scalar"])
    assert hi["scalar"] > 0.9 and lo["scalar"] < 0.1, "assigned>>hot-desk"

    # C17 control: a control matching the binding stressor is credited; a mismatched one is not
    r17 = local_control([{"name": "dense-open", "binding_stressor": "acoustic", "controls": ["thermal"]},
                         {"name": "focus", "binding_stressor": "acoustic", "controls": ["acoustic", "visual"]}])
    print("C17:", [(x["zone"], x["credited"]) for x in r17["rows"]], "score=", r17["scalar"])
    assert not r17["rows"][0]["credited"] and r17["rows"][1]["credited"], "mismatched control earns nothing"

    # C18 air: good ventilation -> low CO2 -> high score; poor -> high CO2 -> low
    good = air_quality(headcount=50, floor_area_m2=500, outdoor_air_lps_per_person=12)
    poor = air_quality(headcount=50, floor_area_m2=500, outdoor_air_lps_per_person=3)
    print(f"C18: good CO2={good['extras']['predicted_co2_ppm']} score={good['scalar']} | "
          f"poor CO2={poor['extras']['predicted_co2_ppm']} score={poor['scalar']}")
    assert good["extras"]["predicted_co2_ppm"] < 900 and poor["extras"]["predicted_co2_ppm"] > 1500
    assert good["scalar"] > poor["scalar"], "better ventilation should score higher"

    # C23 social: an isolated seat with no commons is flagged; a connected one is not
    g2 = np.full((20, 60), FREE, np.int8)
    g2[:, 30] = OBST                                    # wall isolating the right side
    pg2 = type("PG", (), {"grid": g2, "cell_m": 0.5})()
    seats = [(10, 5), (10, 10), (10, 15), (10, 50)]     # 0-2 clustered left; 3 alone right
    r23 = social_connectedness(pg2, seats, commons_cells=[(10, 8)], headcount=4, commons_reach_m=10)
    print("C23:", [(x["seat"], x["visible_seats"], x["loneliness_risk"]) for x in r23["rows"]], "score=", r23["scalar"])
    assert r23["rows"][3]["loneliness_risk"], "the isolated right-side seat should be loneliness-risk"
    assert not r23["rows"][0]["loneliness_risk"], "a clustered seat near commons is not isolated"

    print("-" * 48 + "\nwellbeing_plan self-test: PASS")
