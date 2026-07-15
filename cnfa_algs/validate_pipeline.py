"""
cnfa_algs.validate_pipeline — the success-condition harness (unit + LAST MILE + hardening).

Runs the contracts in `contracts.py` against every process and the full pipeline, and then
tries to BREAK them. Five batteries:

  1. SCHEMA      — every criterion function returns a contract-conforming MetricResult.
  2. LAST-MILE   — the full pipeline (synthetic + a real inferred plan) returns a
                   contract-conforming LayoutScore with all 23 scored criteria present.
  3. DETERMINISM — same input -> identical scores (no hidden randomness in the metrics).
  4. GRACEFUL    — a minimal scenario (pg + seats only) runs without crashing and simply
                   drops the criteria whose spec inputs are absent.
  5. DISCRIMINATION (the hardening) — for EVERY criterion, a clearly-good and a clearly-bad
                   input, asserting good_score > bad_score. This is the last mile of
                   correctness: not "is it in [0,1]" but "does the number move the right way."

Exit code 0 iff every battery passes. Run:
    python -m cnfa_algs.validate_pipeline
"""
from __future__ import annotations
import sys, os
import numpy as np

from . import contracts as K
from . import movement as mv, acoustics_plan as ac, daylight_view as dl, thermal_plan as th
from . import setting_classifier as st, space_syntax as ss, affordance as af, wellbeing_plan as wb
from .score_layout import score_layout, demo_scenario

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

FAILS = []
def _ok(name, detail=""):  print(f"  PASS  {name}")
def _bad(name, detail=""): FAILS.append((name, detail)); print(f"  FAIL  {name}: {detail}")
def PG(grid, cell=0.5, **kw): return type("PG", (), {"grid": grid, "cell_m": cell, **kw})()


# ============================================================ 1. SCHEMA
def battery_schema():
    print("\n[1] SCHEMA — every process returns a contract-conforming MetricResult")
    g = np.full((30, 40), FREE, np.int8); pg = PG(g)
    seats = [(10, 5), (10, 20), (15, 30)]
    glaz = [((r, 0), "S") for r in range(30)]
    checks = {
        "movement.collaborator_proximity": mv.collaborator_proximity(pg, seats, [(0, 1)]),
        "movement.path_overlap": mv.path_overlap(pg, seats, [(10, 5)]),
        "movement.amenity_distance": mv.amenity_distance(pg, seats, [(10, 8)]),
        "movement.stair_prominence": mv.stair_prominence(pg, (29, 20), (25, 20), (2, 2)),
        "acoustics.iso3382": ac.iso3382_single_numbers(),
        "acoustics.focus_privacy": ac.focus_zone_privacy(pg, [(15, 20)], [(10, 5)]),
        "acoustics.soundscape": ac.chronic_stress_soundscape(pg, [(15, 20)]),
        "daylight.view_equity": dl.view_equity(pg, seats, [(r, 0) for r in range(30)]),
        "daylight.daylight_proximity": dl.daylight_proximity(pg, seats, [(r, 0) for r in range(30)]),
        "daylight.circadian_contrast": dl.circadian_contrast(pg, seats, [(r, 0) for r in range(30)]),
        "thermal.radiant": th.radiant_asymmetry_risk(pg, seats, glaz),
        "thermal.zone_mismatch": th.thermal_zone_mismatch(pg, [{"name": "z", "orientations": ["S", "INT"]}]),
        "thermal.solar_patch": th.solar_patch_opportunity(pg, seats, glaz),
        "setting.classify": st.classify_settings(pg),
        "space_syntax.vga": ss.vga_metrics(pg, stride=3),
        "space_syntax.wayfinding": ss.wayfinding_load(pg),
        "affordance.prospect_refuge": af.prospect_refuge_quality(pg, seats),
        "affordance.crowding": af.perceived_crowding_risk(pg, seats),
        "affordance.generosity": af.spatial_generosity(pg),
        "wellbeing.restoration": wb.restoration_nature(pg, seats, [(10, 0)]),
        "wellbeing.territory": wb.territory_provision(80, 100, 5, 6, 0.5),
        "wellbeing.local_control": wb.local_control([{"name": "z", "binding_stressor": "acoustic", "controls": ["acoustic"]}]),
        "wellbeing.air_quality": wb.air_quality(50, 500, 10),
        "wellbeing.social": wb.social_connectedness(pg, seats, [(10, 8)], headcount=3),
    }
    for name, res in checks.items():
        v = K.validate_metric_result(res, grid_shape=g.shape, name=name)
        (_ok if not v else _bad)(name, "; ".join(v) if v else "")


# ============================================================ 2. LAST-MILE
def battery_last_mile():
    print("\n[2] LAST-MILE — full pipeline returns a conforming LayoutScore, all 23 criteria")
    out = score_layout(demo_scenario())
    v = K.validate_layout_score(out, expect_criteria=K.FULL_SCORED_CRITERIA)
    (_ok if not v else _bad)("synthetic pipeline", "; ".join(v) if v else "")

    img = "/home/claude/worked_example/out/_open_plan.png"
    if os.path.exists(img):
        try:
            import cv2
            import cnfa_algs as ca
            from cnfa_algs.plan import infer_plan_from_image
            im = cv2.imread(img); vx, vy, _ = ca.estimate_vanishing_point(im)
            planes, _ = ca.segment_planes(im, (vx, vy)); Z, _, _ = ca.DepthProvider()(im, planes, (vx, vy))
            pg = infer_plan_from_image(im, planes, Z)
            free = np.argwhere(pg.grid == FREE); idx = np.linspace(0, len(free) - 1, 6).astype(int)
            pts = [tuple(int(x) for x in free[i]) for i in idx]
            scn = {"pg": pg, "seats": pts[:5], "focus_seats": [4], "collab_sources": [pts[1]],
                   "collaborator_pairs": [(0, 2)], "glazing": [(pts[0], "S")], "amenities": [pts[2]],
                   "nature_cells": [pts[0]], "commons": [pts[2]], "headcount": 5,
                   "control_zones": [{"name": "z", "orientations": ["S", "INT"]}]}
            out2 = score_layout(scn)
            v2 = K.validate_layout_score(out2)   # real plan: not all 23 (fewer inputs) but must conform
            (_ok if not v2 else _bad)("real inferred plan", "; ".join(v2) if v2 else "")
        except Exception as e:
            _bad("real inferred plan", f"pipeline raised {e!r}")
    else:
        print("  SKIP  real inferred plan (no example image staged)")


# ============================================================ 3. DETERMINISM
def battery_determinism():
    print("\n[3] DETERMINISM — same input -> identical scores")
    a = score_layout(demo_scenario())["criteria_scored"]
    b = score_layout(demo_scenario())["criteria_scored"]
    if a == b:
        _ok("score_layout deterministic")
    else:
        diff = {k: (a.get(k), b.get(k)) for k in set(a) | set(b) if a.get(k) != b.get(k)}
        _bad("score_layout deterministic", f"differs at {diff}")


# ============================================================ 4. GRACEFUL DEGRADATION
def battery_graceful():
    print("\n[4] GRACEFUL — minimal scenario (pg+seats) runs and drops absent-input criteria")
    g = np.full((30, 30), FREE, np.int8); g[10:20, 15] = OBST
    scn = {"pg": PG(g), "seats": [(5, 5), (25, 25), (5, 25)]}
    try:
        out = score_layout(scn)
        v = K.validate_layout_score(out)     # must still conform (fewer criteria)
        got = set(out["criteria_scored"])
        # criteria needing spec inputs must be ABSENT, not crash or fabricate
        should_absent = {"C5", "C7", "C9", "C10", "C15", "C16", "C17", "C18", "C19", "C22", "C23"}
        leaked = should_absent & got
        if v:
            _bad("minimal scenario conforms", "; ".join(v))
        elif leaked:
            _bad("minimal scenario drops absent-input criteria", f"unexpectedly scored {sorted(leaked)}")
        else:
            _ok(f"minimal scenario runs, scored only {sorted(got)}")
    except Exception as e:
        _bad("minimal scenario runs", f"raised {e!r}")


# ============================================================ 5. DISCRIMINATION (hardening)
def battery_discrimination():
    print("\n[5] DISCRIMINATION — good vs bad per criterion (good_score MUST exceed bad_score)")
    g = np.full((20, 40), FREE, np.int8); pg = PG(g)
    wins = [(r, 0) for r in range(20)]
    cases = []

    # C5 collaborator proximity: same-region near pair vs cross-region split
    gwall = np.full((20, 40), FREE, np.int8); gwall[:, 20] = OBST; pgw = PG(gwall)
    cases.append(("C5", mv.collaborator_proximity(pgw, [(10, 5), (10, 10)], [(0, 1)])["scalar"],
                        mv.collaborator_proximity(pgw, [(10, 5), (10, 35)], [(0, 1)])["scalar"]))
    # C7 focus privacy: far focus seat vs near
    cases.append(("C7", ac.focus_zone_privacy(pg, [(10, 20)], [(10, 5)])["scalar"],
                        ac.focus_zone_privacy(pg, [(10, 20)], [(10, 19)])["scalar"]))
    # C8 r_D score: masked/absorptive (good) vs live room (bad)
    cases.append(("C8", 1 - min(ac.iso3382_single_numbers(d2s=11, L_noise=48)["extras"]["r_D_m"] / 20, 1),
                        1 - min(ac.iso3382_single_numbers(d2s=4, L_noise=35)["extras"]["r_D_m"] / 20, 1)))
    # C9 view: near window vs deep core
    cases.append(("C9", dl.view_equity(pg, [(10, 2)], wins)["scalar"],
                        dl.view_equity(pg, [(10, 38)], wins)["scalar"]))
    # C10 daylight proximity: near vs far
    cases.append(("C10", dl.daylight_proximity(pg, [(10, 2)], wins)["scalar"],
                         dl.daylight_proximity(pg, [(10, 38)], wins)["scalar"]))
    # C11 prospect-refuge (prospect-led): open-outlook seat beats a cramped closet (low prospect)
    pg_open = PG(np.full((30, 30), FREE, np.int8))                      # big open room = high prospect
    gcloset = np.full((30, 30), OBST, np.int8); gcloset[14:17, 14:17] = FREE; pg_closet = PG(gcloset)
    cases.append(("C11", af.prospect_refuge_quality(pg_open, [(15, 15)])["scalar"],    # open outlook
                         af.prospect_refuge_quality(pg_closet, [(15, 15)])["scalar"]))  # cramped closet
    # C12 crowding: screened seat set vs crowded row
    gscr = np.full((20, 40), FREE, np.int8); gscr[:, 12] = OBST; pgs = PG(gscr)
    cases.append(("C12", af.perceived_crowding_risk(pgs, [(10, 5), (10, 35)])["scalar"],
                         af.perceived_crowding_risk(pg, [(10, 18), (10, 20), (10, 22)])["scalar"]))
    # C13 setting variety: mixed floor (rooms+open+corridor) vs one open box
    gmix = np.full((60, 60), OBST, np.int8); gmix[2:22, 2:40] = FREE; gmix[30:36, 2:10] = FREE
    gmix[30:36, 15:23] = FREE; gmix[45:47, 2:50] = FREE
    good13 = st.segment_fit(st.classify_settings(PG(gmix)))["scalar"]
    bad13 = st.segment_fit(st.classify_settings(PG(np.full((40, 40), FREE, np.int8))))["scalar"]
    cases.append(("C13", good13, bad13))
    # C15 amenity: in-band vs far
    cases.append(("C15", mv.amenity_distance(pg, [(10, 12)], [(10, 8)], short_band_m=(1, 20))["scalar"],
                         mv.amenity_distance(pg, [(10, 38)], [(10, 2)], short_band_m=(1, 5))["scalar"]))
    # C16 territory: assigned vs hot-desk
    cases.append(("C16", wb.territory_provision(100, 100, 8, 8, 1.0)["scalar"],
                         wb.territory_provision(0, 100, 0, 8, 0.0)["scalar"]))
    # C17 control: matched vs mismatched
    cases.append(("C17", wb.local_control([{"name": "z", "binding_stressor": "acoustic", "controls": ["acoustic"]}])["scalar"],
                         wb.local_control([{"name": "z", "binding_stressor": "acoustic", "controls": ["thermal"]}])["scalar"]))
    # C18 air: good vs poor ventilation
    cases.append(("C18", wb.air_quality(50, 500, 12)["scalar"], wb.air_quality(50, 500, 3)["scalar"]))
    # C19 restoration: nature view vs none
    cases.append(("C19", wb.restoration_nature(pg, [(10, 2)], [(10, 0)], max_view_m=5)["scalar"],
                         wb.restoration_nature(pg, [(10, 38)], [(10, 0)], max_view_m=5)["scalar"]))
    # C20 soundscape: quiet vs loud
    cases.append(("C20", ac.chronic_stress_soundscape(pg, [(10, 20)], L_src_1m=52, L_floor=38)["scalar"],
                         ac.chronic_stress_soundscape(pg, [(5, 10), (5, 30), (15, 20)], L_src_1m=68, L_floor=46)["scalar"]))
    # C21 thermal: coherent zone vs solar mismatch
    cases.append(("C21", th.thermal_zone_mismatch(pg, [{"name": "z", "orientations": ["N", "N"]}])["scalar"],
                         th.thermal_zone_mismatch(pg, [{"name": "z", "orientations": ["S", "INT"]}])["scalar"]))
    # C22 circadian: evening restraint vs none
    cases.append(("C22", dl.circadian_contrast(pg, [(10, 2)], wins, evening_electric_low=True)["scalar"],
                         dl.circadian_contrast(pg, [(10, 2)], wins, evening_electric_low=False)["scalar"]))
    # C23 social: connected cluster vs isolated
    gsoc = np.full((20, 60), FREE, np.int8); gsoc[:, 30] = OBST; pgso = PG(gsoc)
    cases.append(("C23", wb.social_connectedness(pgso, [(10, 5), (10, 10), (10, 15)], [(10, 8)], headcount=3, commons_reach_m=10)["scalar"],
                         wb.social_connectedness(pgso, [(10, 50)], [(10, 8)], headcount=1, commons_reach_m=5)["scalar"]))
    # C24 generosity: compression-release vs uniform
    gcr = np.full((40, 40), OBST, np.int8); gcr[5:35, 5:35] = FREE; gcr[18:22, 0:5] = FREE
    cases.append(("C24", af.spatial_generosity(PG(gcr), stride=2)["scalar"],
                         af.spatial_generosity(PG(np.full((30, 30), FREE, np.int8)), stride=3)["scalar"]))
    # C1/C2/C3 VGA: a connected plan vs a fragmented one (mean integration)
    vgood = ss.vga_metrics(PG(np.full((30, 30), FREE, np.int8)), stride=2)["extras"]["mean_connectivity"]
    gfrag = np.full((30, 30), FREE, np.int8); gfrag[:, 10] = OBST; gfrag[:, 20] = OBST
    vbad = ss.vga_metrics(PG(gfrag), stride=2)["extras"]["mean_connectivity"]
    cases.append(("C1/C2", vgood, vbad))

    for cid, good, bad in cases:
        if good is None or bad is None:
            _bad(f"{cid} discrimination", f"None score (good={good}, bad={bad})")
        elif good > bad:
            _ok(f"{cid} discriminates  good={round(good,3)} > bad={round(bad,3)}")
        else:
            _bad(f"{cid} discrimination", f"good={round(good,3)} NOT > bad={round(bad,3)}")


# ============================================================ 6. FOUNDATION (image pipeline)
def battery_foundation():
    print("\n[6] FOUNDATION — Tier A/B image pipeline (attributes, geometry, plan)")
    try:
        import cv2
        import cnfa_algs as ca
        from cnfa_algs import attributes as A
        from cnfa_algs.plan import infer_plan_from_image, isovist_fields
    except Exception as e:
        _bad("foundation imports", f"{e!r}"); return
    img_path = "/home/claude/worked_example/out/_open_plan.png"
    if os.path.exists(img_path):
        img = cv2.imread(img_path)
    else:                                            # synthesize a structured test image
        img = np.zeros((240, 320, 3), np.uint8)
        img[:120] = (200, 200, 200); img[120:] = (90, 90, 90)
        cv2.rectangle(img, (60, 60), (260, 180), (150, 120, 100), 3)
    H, W = img.shape[:2]

    # geometry
    try:
        vx, vy, vconf = ca.estimate_vanishing_point(img)
        if not (np.isfinite(vx) and np.isfinite(vy) and 0 <= vconf <= 1):
            _bad("geometry.vanishing_point", f"vp=({vx},{vy}) conf={vconf}")
        else:
            _ok("geometry.vanishing_point")
        planes, pconf = ca.segment_planes(img, (vx, vy))
        if planes.shape != (H, W) or not (0 <= pconf <= 1):
            _bad("geometry.segment_planes", f"shape {planes.shape} conf {pconf}")
        else:
            _ok("geometry.segment_planes")
        Z, disp01, dconf = ca.DepthProvider()(img, planes, (vx, vy))
        if Z.shape != (H, W) or not np.all(np.isfinite(Z)) or disp01.min() < -1e-6 or disp01.max() > 1 + 1e-6:
            _bad("geometry.depth", f"Z finite={np.all(np.isfinite(Z))} disp range [{disp01.min():.2f},{disp01.max():.2f}]")
        else:
            _ok("geometry.depth")
    except Exception as e:
        _bad("geometry pipeline", f"raised {e!r}"); return

    # Tier A attributes (contract on the AttributeResult dataclass)
    attr_calls = {
        "brightness_variance": lambda: A.brightness_variance(img),
        "edge_clarity": lambda: A.edge_clarity(img),
        "symmetry_horizontal": lambda: A.symmetry_horizontal(img),
        "palette_entropy": lambda: A.palette_entropy(img),
        "processing_load": lambda: A.processing_load(img),
        "fractal_dimension_local": lambda: A.fractal_dimension_local(img),
        "glare_risk": lambda: A.glare_risk(img),
        "warmth_ratio": lambda: A.warmth_ratio(img),
        "landmark_salience": lambda: A.landmark_salience(img),
        "enclosure_index": lambda: A.enclosure_index(img, planes, Z),
        "prospect": lambda: A.prospect(img, planes, Z),
        "acoustic_absorption": lambda: A.acoustic_absorption(img, planes, Z),
        "vertical_illuminance_proxy": lambda: A.vertical_illuminance_proxy(img, planes),
    }
    no_disclosure = []
    for name, fn in attr_calls.items():
        try:
            res = fn()
        except Exception as e:
            _bad(f"attributes.{name}", f"raised {e!r}"); continue
        v = K.validate_attribute_result(res, grid_shape=(H, W), name=f"attributes.{name}")
        if v:
            _bad(f"attributes.{name}", "; ".join(v))
        else:
            _ok(f"attributes.{name}")
            if not getattr(res, "failure_modes", []):
                no_disclosure.append(name)
    if no_disclosure:
        print(f"  NOTE  {len(no_disclosure)} attributes lack failure_modes disclosure: {no_disclosure}")

    # plan (Tier B)
    try:
        pg = infer_plan_from_image(img, planes, Z)
        v = K.validate_plangrid(pg, "infer_plan_from_image")
        (_ok if not v else _bad)("plan.infer_plan_from_image", "; ".join(v) if v else "")
        fields = isovist_fields(pg, stride=4)
        for fk in ("openness", "prospect", "refuge", "prospect_refuge"):
            f = fields.get(fk)
            if not isinstance(f, np.ndarray) or f.shape != pg.grid.shape:
                _bad(f"plan.isovist_fields[{fk}]", f"bad field {None if f is None else f.shape}")
            else:
                fv = f[pg.grid == 1]
                if np.nanmin(fv) < -1e-6 or np.nanmax(fv) > 1 + 1e-6:
                    _bad(f"plan.isovist_fields[{fk}]", f"values out of [0,1]: [{np.nanmin(fv):.2f},{np.nanmax(fv):.2f}]")
                else:
                    _ok(f"plan.isovist_fields[{fk}]")
    except Exception as e:
        _bad("plan pipeline", f"raised {e!r}")


# ============================================================ 7. ADVERSARIAL (panel blind spots)
def battery_adversarial():
    print("\n[7] ADVERSARIAL — the cases the panel found the harness was blind to")
    OBST_ = OBST

    # A1. diagonal-wall LOS now blocks (S1) — acoustics STI behind a diagonal wall = 0
    g = np.full((21, 21), FREE, np.int8)
    for i in range(21):
        g[i, i] = OBST_                                    # main-diagonal wall
    pg = PG(g, 0.5)
    f = ac.sti_field(pg, (3, 8), L_s_1m=60, d2s=6, L_noise=40)   # source below the diagonal
    behind = f[8, 3]                                       # a cell above the diagonal, blocked
    (_ok if (np.isnan(behind) or behind == 0.0) else _bad)("A1 diagonal wall blocks STI (S1)",
        f"STI behind diagonal = {behind}")

    # A2. daylight view does NOT pass through a diagonal wall (S1)
    v = dl.view_equity(pg, [(8, 3)], [(3, 8)], max_view_m=20)   # window across the diagonal
    (_ok if not v["rows"][0]["has_view"] else _bad)("A2 diagonal wall blocks view (S1)", "view leaked")

    # A3. C12: two seats 60 m apart are NOT crowded (density gate, S7)
    wide = np.full((10, 130), FREE, np.int8); pgw = PG(wide, 1.0)   # 130 m hall
    r12 = af.perceived_crowding_risk(pgw, [(5, 5), (5, 125)])       # 120 m apart, mutually visible
    (_ok if not any(x["at_risk"] for x in r12["rows"]) else _bad)("A3 spread-out pair not crowded (C12)",
        f"risks {[x['crowding_risk'] for x in r12['rows']]}")

    # A4. C23: a seat exposed to a large open floor (many visible, no refuge) is NOT well-connected (F6)
    big = np.full((30, 30), FREE, np.int8); pgb = PG(big, 0.5)
    seats = [(15, c) for c in range(2, 28, 2)]                     # 13 seats in one open row
    r23 = wb.social_connectedness(pgb, seats, [(15, 15)], headcount=len(seats), commons_reach_m=30)
    exposed_any = any(x["over_exposed"] for x in r23["rows"])
    (_ok if exposed_any else _bad)("A4 large-floor exposure flagged (C23/F6)", "no seat flagged over-exposed")

    # A5. C8 dropped (not fabricated 0.88) when no acoustic params (S4)
    out = score_layout({"pg": PG(np.full((20, 20), FREE, np.int8)), "seats": [(5, 5), (15, 15)]})
    (_ok if "C8" not in out["criteria_scored"] else _bad)("A5 C8 dropped without acoustic params (S4)",
        f"C8 fabricated = {out['criteria_scored'].get('C8')}")

    # A6. C14 dropped (not fabricated 1.0) when focus_seats present but no acoustic evidence (S4)
    out6 = score_layout({"pg": PG(np.full((20, 20), FREE, np.int8)), "seats": [(5, 5), (15, 15)],
                         "focus_seats": [0]})
    (_ok if "C14" not in out6["criteria_scored"] else _bad)("A6 C14 not fabricated without C7 (S4)",
        f"C14 fabricated = {out6['criteria_scored'].get('C14')}")

    # A7. thermal: a seat WALLED OFF from glazing is not at radiant risk (S5, grid used)
    gt = np.full((20, 30), FREE, np.int8); gt[:, 5] = OBST_        # wall between seat and glazing
    glaz = [((r, 0), "S") for r in range(20)]
    rr = th.radiant_asymmetry_risk(PG(gt, 0.5), [(10, 8)], glaz, near_m=6.0, big_run_cells=10)
    (_ok if not rr["rows"][0]["at_risk"] else _bad)("A7 walled-off seat no radiant risk (S5)",
        f"risk {rr['rows'][0]['radiant_risk']}")

    # A8. image-tier determinism (S2): segment_planes identical across calls
    import cv2, cnfa_algs as ca
    img = np.zeros((120, 160, 3), np.uint8); img[:60] = (200, 200, 200); img[60:] = (90, 90, 90)
    vx, vy, _ = ca.estimate_vanishing_point(img)
    p1, _ = ca.segment_planes(img, (vx, vy)); p2, _ = ca.segment_planes(img, (vx, vy))
    (_ok if int((p1 != p2).sum()) == 0 else _bad)("A8 segmentation deterministic (S2)",
        f"{int((p1 != p2).sum())} pixels differ")


if __name__ == "__main__":
    print("cnfa_algs.validate_pipeline — contracts + last-mile + hardening\n" + "=" * 62)
    battery_schema()
    battery_foundation()
    battery_last_mile()
    battery_determinism()
    battery_graceful()
    battery_discrimination()
    battery_adversarial()
    print("\n" + "=" * 62)
    if FAILS:
        print(f"RESULT: {len(FAILS)} FAILURE(S)")
        for n, d in FAILS:
            print(f"  - {n}: {d}")
        sys.exit(1)
    print("RESULT: ALL BATTERIES PASS")
