"""
cnfa_algs.wave2_geometry — Sprint COMP-CORRECT Stage S3 (first slice): the two [FULL]-specified
Wave-2 operators. (Codex Section-D keeps; algorithms per SPRINT_COMPCORRECT_ALGORITHMS §5.)

  W2.1  verticality_cues      v2a_080 — length fraction of LSD segments consistent with the vertical
                              vanishing direction, weighted toward long continuous runs. Rides the
                              same LSD substrate as W1.9 (orderliness) — AMBER ceiling by rule.
  W2.6  choice_richness_zones v2a_118 — Shannon evenness x coverage over the setting types visible
                              in the unit (pure reuse of the C13 classifier). AMBER (inferred plan).

Deferred to the next S3 slice (need the vanishing-frame machinery hardened first): W2.2 ceiling
openness, W2.3 double-height flag, W2.4 blind corners, W2.5 barrier permeability, W2.8 thresholds.

Self-test: python3 -m cnfa_algs.wave2_geometry
"""
from __future__ import annotations
import numpy as np
import cv2

try:
    from .attributes import AttributeResult
except Exception:
    from attributes import AttributeResult  # type: ignore

VERT_TOL_DEG = 8.0        # a segment within this of image-vertical counts as a vertical cue
VERT_MIN_SEGMENTS = 20    # below this the measure is undefined (abstain)
LONG_RUN_FRAC = 0.15      # segments longer than this fraction of image height are "long runs"


# ================================================================ W2.1 verticality_cues
def verticality_cues(img_bgr) -> AttributeResult:
    """v2a_080 — vertical-line dominance. HONEST SCOPE: 'vertical' here = image-plane vertical
    within VERT_TOL_DEG. On a level camera this approximates the vertical vanishing direction; on a
    tilted/rolled camera it degrades — the roll estimate is emitted and large roll ABSTAINS.
    Long continuous runs (columns, mullions, full-height glazing) are up-weighted 2x."""
    g8 = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    Hpx = g8.shape[0]
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    out = lsd.detect(g8)
    segs = out[0] if out is not None and out[0] is not None else None
    if segs is None or len(segs) < VERT_MIN_SEGMENTS:
        n = 0 if segs is None else len(segs)
        return AttributeResult(key="cnfa.geometry.verticality_cues", scalar=None, confidence=0.0,
                               method=f"ABSTAIN: {n} segments < {VERT_MIN_SEGMENTS}",
                               failure_modes=["verticality undefined without line segments"])
    P = segs.reshape(-1, 4)
    dx, dy = P[:, 2] - P[:, 0], P[:, 3] - P[:, 1]
    length = np.hypot(dx, dy)
    # angle from image-vertical, folded (0 = vertical)
    ang_from_vert = np.abs(np.degrees(np.arctan2(np.abs(dx), np.abs(dy))))
    # ROLL GATE FIRST (v1 bug: gating after the vertical count means a 20deg-rolled colonnade has
    # zero 'near-vertical' segments and the gate never fires). Estimate roll from the length-weighted
    # median signed deviation of all segments within 30 deg of vertical.
    signed = np.degrees(np.arctan2(dx, dy))               # 0 = straight down in image coords
    signed = np.where(signed > 90, signed - 180, np.where(signed < -90, signed + 180, signed))
    wideband = ang_from_vert <= 30.0
    roll_est = None
    if wideband.any() and length[wideband].sum() > 0.25 * length.sum():
        order_w = np.argsort(signed[wideband])
        cum = np.cumsum(length[wideband][order_w])
        roll_est = float(signed[wideband][order_w][np.searchsorted(cum, cum[-1] / 2)])
        if abs(roll_est) > 12.0:
            return AttributeResult(
                key="cnfa.geometry.verticality_cues", scalar=None, confidence=0.0,
                method=f"ABSTAIN: estimated camera roll {roll_est:.1f} deg > 12 — "
                       "image-vertical no longer proxies world-vertical",
                extras={"roll_est_deg": round(roll_est, 2), "n_segments": int(len(P))},
                failure_modes=["rolled camera: measure undefined without rectification"])
    vert = ang_from_vert <= VERT_TOL_DEG
    if not vert.any():
        return AttributeResult(
            key="cnfa.geometry.verticality_cues", scalar=0.0, confidence=0.6,
            method=f"LSD vertical-length fraction (tol {VERT_TOL_DEG} deg); no vertical segments (M1)",
            extras={"n_segments": int(len(P)), "roll_est_deg": roll_est},
            failure_modes=["camera tilt/roll shifts image-vertical away from world-vertical"])
    roll_est = 0.0 if roll_est is None else roll_est
    long_run = length >= LONG_RUN_FRAC * Hpx
    w = length * np.where(long_run & vert, 2.0, 1.0)      # long vertical runs count double
    scalar = float(np.clip((w[vert].sum()) / (w.sum() + 1e-12), 0, 1))
    return AttributeResult(
        key="cnfa.geometry.verticality_cues", scalar=scalar, confidence=0.6,
        method=f"LSD length-fraction within {VERT_TOL_DEG} deg of image-vertical, long runs x2 (M1)",
        extras={"n_segments": int(len(P)), "n_vertical": int(vert.sum()),
                "n_long_vertical_runs": int((long_run & vert).sum()),
                "roll_est_deg": round(roll_est, 2),
                "constants": {"tol_deg": VERT_TOL_DEG, "long_run_frac": LONG_RUN_FRAC,
                              "roll_abstain_deg": 12.0}},
        failure_modes=["image-vertical proxies world-vertical only on a ~level camera (roll gate 12deg)",
                       "AMBER: no rectification; wide-angle distortion bends verticals at the frame edge"])


# ================================================================ W2.6 choice_richness_zones
def choice_richness_zones(pg) -> dict:
    """v2a_118 — agency through setting choice: how many DISTINCT usable setting types does the
    visible floor offer, and how evenly? richness = evenness(Shannon over type areas) x coverage
    (types present / 3). Pure reuse of the C13 classifier on the (inferred) PlanGrid -> AMBER."""
    from .setting_classifier import classify_settings
    cs = classify_settings(pg)
    areas = np.array([a for a in cs["extras"]["area_by_type_m2"].values() if a > 0], float)
    n_types = len(cs["extras"]["types_present"])
    if len(areas) == 0:
        return {"key": "cnfa.plan.choice_richness", "status": "unknown",
                "reason": "no_classified_regions", "method": "C13 classifier returned no regions"}
    p = areas / areas.sum()
    evenness = float(-(p * np.log(p)).sum() / np.log(len(p))) if len(p) > 1 else 0.0
    richness = float(np.clip(evenness * (n_types / 3.0), 0, 1))
    return {"key": "cnfa.plan.choice_richness", "status": "scored",
            "scalar": round(richness, 4),
            "extras": {"evenness": round(evenness, 4), "types_present": cs["extras"]["types_present"],
                       "area_by_type_m2": cs["extras"]["area_by_type_m2"],
                       "upstream": "cnfa.plan.setting_variety"},
            "confidence": min(0.4, cs["confidence"]),
            "method": "Shannon evenness x type-coverage over C13 setting classification (M1)",
            "failure_modes": cs["failure_modes"] + ["choice != mere variety: usable-choice needs "
                                                    "occupancy/affordance labels (corpus, L6)"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("wave2_geometry self-test\n" + "-" * 56)
    H, W = 240, 320
    mk = lambda f: np.clip(f, 0, 255).astype(np.uint8)

    # W2.1: colonnade (long verticals) > horizontal shelving > blank abstains
    col = np.full((H, W), 255.0)
    for x in range(15, W, 25): cv2.line(col, (x, 10), (x, H - 10), 0, 3)   # 13 columns -> ~26 segs
    horiz = np.full((H, W), 255.0)
    for y in range(15, H, 18): cv2.line(horiz, (10, y), (W - 10, y), 0, 3)
    vc = verticality_cues(mk(np.stack([col] * 3, -1)))
    hc = verticality_cues(mk(np.stack([horiz] * 3, -1)))
    bc = verticality_cues(mk(np.full((H, W, 3), 128.0)))
    assert bc.scalar is None and vc.scalar > 0.9 and hc.scalar < 0.1
    print(f"W2.1 colonnade {vc.scalar:.2f} (long runs {vc.extras['n_long_vertical_runs']}) > "
          f"shelving {hc.scalar:.2f}; blank->abstain  OK")

    # W2.1 roll gate: rotate the colonnade 20 deg -> abstain naming roll
    Mrot = cv2.getRotationMatrix2D((W / 2, H / 2), 20.0, 1.0)
    rot = cv2.warpAffine(col, Mrot, (W, H), borderValue=255.0)
    rc = verticality_cues(mk(np.stack([rot] * 3, -1)))
    assert rc.scalar is None and "roll" in rc.method
    print(f"W2.1 rolled 20deg -> ABSTAIN ({rc.method[:52]}...)  OK")

    # W2.6: mixed plan (rooms + open + corridor) > monoculture open field
    from cnfa_algs.plan import FREE, OBST
    class PG:
        def __init__(s, grid, cell): s.grid, s.cell_m = grid, cell
    g_mix = np.full((60, 90), FREE, np.int8)
    g_mix[:, 0] = OBST; g_mix[:, -1] = OBST; g_mix[0, :] = OBST; g_mix[-1, :] = OBST
    g_mix[1:9, 8] = OBST; g_mix[8, 1:9] = OBST              # 7x7-cell room (12.25 m2 <= 15)
    g_mix[20, 1:89] = OBST; g_mix[23, 1:89] = OBST          # 2-cell (1.0 m) corridor, 44 m long
    r_mix = choice_richness_zones(PG(g_mix, 0.5))
    assert set(r_mix["extras"]["types_present"]) == {"enclosed_room", "circulation", "open_field"}, \
        r_mix["extras"]
    g_open = np.full((60, 90), FREE, np.int8)
    g_open[:, 0] = OBST; g_open[:, -1] = OBST; g_open[0, :] = OBST; g_open[-1, :] = OBST
    r_open = choice_richness_zones(PG(g_open, 0.5))
    assert r_mix["scalar"] > r_open["scalar"], (r_mix["scalar"], r_open["scalar"])
    print(f"W2.6 mixed plan {r_mix['scalar']:.3f} ({r_mix['extras']['types_present']}) > "
          f"open monoculture {r_open['scalar']:.3f}  OK")

    # determinism x2
    assert verticality_cues(mk(np.stack([col] * 3, -1))).scalar == vc.scalar
    assert choice_richness_zones(PG(g_mix, 0.5))["scalar"] == r_mix["scalar"]
    print("determinism x2  OK")
    print("-" * 56 + "\nwave2_geometry self-test: PASS")
