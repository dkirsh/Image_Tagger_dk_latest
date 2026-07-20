"""
cnfa_algs.wave2_geometry — Sprint COMP-CORRECT Stage S3 (first slice): the two [FULL]-specified
Wave-2 operators. (Codex Section-D keeps; algorithms per SPRINT_COMPCORRECT_ALGORITHMS §5.)

  W2.1  verticality_cues      v2a_080 — length fraction of LSD segments consistent with the vertical
                              vanishing direction, weighted toward long continuous runs. Rides the
                              same LSD substrate as W1.9 (orderliness) — AMBER ceiling by rule.
  W2.6  choice_richness_zones v2a_118 — Shannon evenness x coverage over the setting types visible
                              in the unit (pure reuse of the C13 classifier). AMBER (inferred plan).

S3 remainder built 2026-07-20 (CC-4): W2.2 ceiling_openness_relative, W2.3 double_height_space,
W2.4 blind_corner_index, W2.5 barrier_permeability, W2.8 threshold_emphasized. All AMBER by rule,
all ABSTAIN (scalar=None) when their substrate is absent (no ceiling / cornerless plan / no wall /
no wall-embedded aperture). Relative quantities only — metric scale is W2.7 (dormant, detector-gated).
W2.7 room_scale_estimate stays deferred (needs the Wave-3 anchor detector).

Self-test: python3 -m cnfa_algs.wave2_geometry
"""


from __future__ import annotations

# TAX-0 fix (Codex attack 2026-07-19): support direct `python3 cnfa_algs/<file>.py` invocation.
# PEP 366: bootstrap the package context so ALL relative imports (top-level and function-level)
# resolve identically to `python3 -m cnfa_algs.<file>`.
if __package__ in (None, ""):
    import sys as _sys, pathlib as _pl
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
    import cnfa_algs                     # initialize the package
    __package__ = "cnfa_algs"
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
                               extras={"n_segments": int(n), "reason": "insufficient_segments"},
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


# ================================================================ shared geometry constants
# S3 remainder (CC-4, 2026-07-20): W2.2 ceiling_openness_relative, W2.3 double_height_space,
# W2.4 blind_corner_index, W2.5 barrier_permeability, W2.8 threshold_emphasized. All AMBER by the
# Wave-2 rule (ride VP / plane-seg / inferred-plan machinery), all ABSTAIN (scalar=None) when their
# substrate is absent — never a fabricated number. Relative quantities only (no metres without the
# W2.7 scale anchor). Registered image-only: planes/Z/pg are derived from the image upstream.

_HFOV_DEG = 65.0                 # declared horizontal FOV (matches plan.infer_plan_from_image)
CEIL_MIN_FRAC = 0.01             # below this ceiling fraction the ceiling measure is undefined
DH_SPAN_THRESH = 0.55            # W2.3 double-height flag on normalized f2c span — NEEDS-CALIBRATION
BLIND_MIN_FREE = 60              # min free cells for a meaningful circulation skeleton
BLIND_CORNER_DEG = 45.0          # skeleton turn > this (from straight) counts as a corner
BLIND_STEP = 4                   # cells to step along each arm when measuring the reveal
BLIND_TAU = 0.35                 # ΔA/A above this = a genuine reveal (declared)
BLIND_SCALE = 1.5                # saturating divisor: mean per-corner reveal -> [0,1]
PERM_MIN_WALL_FRAC = 0.02        # below this WALL fraction there is no barrier to measure


def _vfov_deg(H, W):
    """Vertical FOV from the declared horizontal FOV and the raster aspect (pinhole)."""
    import math
    hf = math.radians(_HFOV_DEG)
    return math.degrees(2.0 * math.atan(math.tan(hf / 2.0) * (H / max(W, 1))))


# ================================================================ W2.2 ceiling_openness_relative
def ceiling_openness_relative(img_bgr, planes, Z=None) -> AttributeResult:
    """v2a_067 — RELATIVE ceiling openness (Manhattan-frame proxy). Reports only scale-free
    quantities (SPRINT §5 W2.2): ceiling area fraction, ceiling angular elevation above the horizon,
    and the floor-to-ceiling angular span (the openness scalar). NO metres — metric height is W2.7.
    Horizon is estimated from the floor/ceiling plane split (no VP needed here); large uncertainty
    is why this is AMBER. ABSTAINS when no ceiling is visible in frame."""
    import math
    from .geometry import CEILING, FLOOR
    H, W = planes.shape[:2]
    ceil = (planes == CEILING)
    floor = (planes == FLOOR)
    ceil_frac = float(ceil.mean())
    if ceil_frac < CEIL_MIN_FRAC:
        return AttributeResult(
            key="cnfa.geometry.ceiling_openness_relative", scalar=None, confidence=0.0,
            method=f"ABSTAIN: ceiling fraction {ceil_frac:.3f} < {CEIL_MIN_FRAC} — no ceiling in frame",
            extras={"ceiling_area_fraction": round(ceil_frac, 4)},
            failure_modes=["level camera with the ceiling out of frame reads as no-ceiling (correct abstain)"])
    ceil_rows = np.where(ceil.any(1))[0]
    ceil_top = float(ceil_rows.min())                      # highest ceiling pixel (smallest row)
    ceil_bottom = float(np.percentile(ceil_rows, 90))
    if floor.any():
        floor_rows = np.where(floor.any(1))[0]
        floor_bottom = float(floor_rows.max())             # lowest floor pixel (largest row)
        floor_top = float(np.percentile(floor_rows, 10))
        horizon_row = 0.5 * (ceil_bottom + floor_top)
    else:
        floor_bottom = float(H - 1)
        horizon_row = ceil_bottom
    vfov = _vfov_deg(H, W)
    f_v = (H / 2.0) / math.tan(math.radians(vfov) / 2.0)   # vertical focal length in px
    ang = lambda row: math.degrees(math.atan((horizon_row - row) / f_v))   # +above horizon
    ceil_elev = ang(float(ceil_rows.mean()))               # mean ceiling elevation above horizon
    span_deg = ang(ceil_top) - ang(floor_bottom)           # highest ceiling .. lowest floor
    span_norm = float(np.clip(span_deg / (vfov + 1e-9), 0, 1))
    return AttributeResult(
        key="cnfa.geometry.ceiling_openness_relative", scalar=span_norm, confidence=0.4,
        method=f"floor-to-ceiling angular span {span_deg:.1f}deg / vFOV {vfov:.1f}deg; "
               f"ceiling elevation {ceil_elev:.1f}deg above est. horizon; RELATIVE only (M1)",
        extras={"ceiling_area_fraction": round(ceil_frac, 4),
                "ceiling_elevation_deg": round(ceil_elev, 2),
                "floor_to_ceiling_span_deg": round(span_deg, 2),
                "span_normalized": round(span_norm, 4),
                "constants": {"hfov_deg": _HFOV_DEG, "vfov_deg": round(vfov, 2),
                              "ceil_min_frac": CEIL_MIN_FRAC, "horizon_row": round(horizon_row, 1)}},
        failure_modes=["AMBER: horizon estimated from plane split, not a calibrated VP",
                       "no metric height (that is W2.7 with a scale anchor)",
                       "SATURATION: full-frame interiors (ceiling at the top edge, floor at the "
                       "bottom) drive the span ~1.0 regardless of true height — the value only "
                       "discriminates when floor/ceiling are inset; ceiling_elevation_deg + "
                       "ceiling_area_fraction in extras carry the residual signal until W2.7 lands",
                       "plane-seg errors on bright textured ceilings shift the span"])


# ================================================================ W2.3 double_height_space
def double_height_space(img_bgr, planes, Z=None) -> AttributeResult:
    """arch.pattern.double_height_space — thresholded flag on W2.2's normalized angular span
    (SPRINT §5 W2.3). Until the POE high-vs-low-ceiling pair + Drive atria calibrate the threshold
    this emits the CONTINUOUS span value and carries needs_calibration=True. ABSTAINS iff W2.2 does."""
    base = ceiling_openness_relative(img_bgr, planes, Z)
    if base.scalar is None:
        return AttributeResult(
            key="cnfa.arch.double_height_space", scalar=None, confidence=0.0,
            method="ABSTAIN: ceiling openness undefined (no ceiling) — double-height undefined",
            extras=base.extras, failure_modes=base.failure_modes)
    span_norm = float(base.scalar)
    flag = bool(span_norm >= DH_SPAN_THRESH)
    return AttributeResult(
        key="cnfa.arch.double_height_space", scalar=span_norm, confidence=0.35,
        method=f"continuous f2c span {span_norm:.3f} vs double-height threshold {DH_SPAN_THRESH} "
               f"-> flag={flag} (NEEDS-CALIBRATION) (M1)",
        extras={"double_height_flag": flag, "needs_calibration": True,
                "span_normalized": round(span_norm, 4),
                "constants": {"dh_span_threshold": DH_SPAN_THRESH,
                              **base.extras.get("constants", {})}},
        failure_modes=["threshold is UNCALIBRATED engineering (POE atria pair owed) — flag advisory",
                       *base.failure_modes])


# ================================================================ W2.4 blind_corner_index
def _isovist_area(grid, r0, c0, free_val, n_rays=48, max_steps=None):
    """Polar isovist area (cell units) at (r0,c0): raycast to the first blocked cell each direction."""
    Hn, Wn = grid.shape
    if max_steps is None:
        max_steps = int(np.hypot(Hn, Wn))
    radii = np.empty(n_rays, np.float64)
    for k in range(n_rays):
        th = 2.0 * np.pi * k / n_rays
        dr, dc = np.sin(th), np.cos(th)
        step, rr, cc = 0, r0 + 0.5, c0 + 0.5
        while True:
            step += 1
            rr += dr; cc += dc
            ri, ci = int(rr), int(cc)
            if ri < 0 or ri >= Hn or ci < 0 or ci >= Wn or grid[ri, ci] != free_val or step >= max_steps:
                break
        radii[k] = step
    return 0.5 * float(np.sum(radii ** 2)) * (2.0 * np.pi / n_rays)


def blind_corner_index(pg) -> AttributeResult:
    """v2a_072 — blind corners on the inferred PlanGrid (SPRINT §5 W2.4). Walk the circulation
    SKELETON; a 'corner' is a skeleton cell that bends > BLIND_CORNER_DEG from straight (or a branch
    point). At each corner the isovist REVEAL = (max isovist a few steps down its arms - isovist at
    the corner)/isovist_at_corner; a blind corner is one whose reveal exceeds BLIND_TAU (you cannot
    see around it until you round it). We report the BOUNDED reformulation of the spec's Σ form:
    scalar = clip(mean over corners of max(0, reveal - τ) / SCALE). No transparency detector on the
    plan yet, so every occluding turn counts (declared over-count; Wave-3 glass gate refines it).
    ABSTAINS on a too-small / cornerless skeleton."""
    from .plan import FREE
    try:
        from skimage.morphology import skeletonize
    except Exception:
        return AttributeResult(
            key="cnfa.geometry.blind_corner_index", scalar=None, confidence=0.0,
            method="ABSTAIN: scikit-image (skeletonize) unavailable — fail closed",
            extras={"reason": "skimage_unavailable"},
            failure_modes=["blind-corner walk needs a morphological skeleton (skimage dependency)"])
    grid = np.asarray(pg.grid)
    free = (grid == FREE)
    n_free = int(free.sum())
    if n_free < BLIND_MIN_FREE:
        return AttributeResult(
            key="cnfa.geometry.blind_corner_index", scalar=None, confidence=0.0,
            method=f"ABSTAIN: {n_free} free cells < {BLIND_MIN_FREE} — no usable circulation skeleton",
            extras={"n_free": n_free},
            failure_modes=["degenerate/absent inferred plan -> no skeleton to walk (correct abstain)"])
    skel = skeletonize(free)
    sk = np.argwhere(skel)
    skset = {(int(r), int(c)) for r, c in sk}
    nb8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def neigh(r, c):
        return [(r + dr, c + dc) for dr, dc in nb8 if (r + dr, c + dc) in skset]

    corners = []
    for (r, c) in skset:
        ns = neigh(r, c)
        if len(ns) >= 3:                                   # branch/junction
            corners.append((r, c, ns[:2]))
            continue
        if len(ns) == 2:                                   # bend test
            (r1, c1), (r2, c2) = ns
            v1 = np.array([r1 - r, c1 - c], float); v2 = np.array([r2 - r, c2 - c], float)
            v1 /= (np.linalg.norm(v1) + 1e-9); v2 /= (np.linalg.norm(v2) + 1e-9)
            ang_between = np.degrees(np.arccos(np.clip(v1 @ v2, -1, 1)))
            if ang_between < (180.0 - BLIND_CORNER_DEG):   # bent away from straight-through
                corners.append((r, c, ns))
    if not corners:
        return AttributeResult(
            key="cnfa.geometry.blind_corner_index", scalar=0.0, confidence=0.35,
            method="no skeleton corners/junctions detected — straight-through circulation (M1)",
            extras={"n_free": n_free, "n_corners": 0, "n_blind": 0,
                    "constants": {"corner_deg": BLIND_CORNER_DEG, "tau": BLIND_TAU,
                                  "step": BLIND_STEP, "scale": BLIND_SCALE}},
            failure_modes=["single corridor / open room has no corners (correct low score)"])
    ms = int(np.hypot(*grid.shape))
    reveals = []
    for (r, c, arms) in corners:
        a0 = _isovist_area(grid, r, c, FREE, max_steps=ms)
        arm_areas = []
        for (ar, ac) in arms:
            # step BLIND_STEP cells along this arm direction (clamped into free space)
            dr = int(np.sign(ar - r)); dc = int(np.sign(ac - c))
            rr, cc = r, c
            for _ in range(BLIND_STEP):
                nr, nc = rr + dr, cc + dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1] and grid[nr, nc] == FREE:
                    rr, cc = nr, nc
                else:
                    break
            arm_areas.append(_isovist_area(grid, rr, cc, FREE, max_steps=ms))
        # apex sees BOTH arms; the tightest approach (an occluded arm-interior cell) sees least.
        # blindness = how much the apex view exceeds the tightest approach = (A_apex - min_arm)/A_apex.
        reveal = (a0 - min(arm_areas)) / (a0 + 1e-9)
        reveals.append(max(0.0, reveal - BLIND_TAU))
    n_blind = int(sum(1 for x in reveals if x > 0))
    scalar = float(np.clip((sum(reveals) / len(reveals)) / BLIND_SCALE, 0, 1))
    return AttributeResult(
        key="cnfa.geometry.blind_corner_index", scalar=scalar,
        confidence=min(0.4, float(getattr(pg, "confidence", 0.4))),
        method=f"skeleton corner isovist-reveal (bounded Σ form): {n_blind}/{len(corners)} corners "
               f"reveal>τ; mean-excess/{BLIND_SCALE} (M1)",
        extras={"n_free": n_free, "n_corners": len(corners), "n_blind": n_blind,
                "blind_fraction": round(n_blind / len(corners), 3),
                "constants": {"corner_deg": BLIND_CORNER_DEG, "tau": BLIND_TAU,
                              "step": BLIND_STEP, "scale": BLIND_SCALE, "n_rays": 48}},
        failure_modes=["AMBER: inferred-plan skeleton inherits the Tier-B geometry chain instability",
                       "no transparency detector -> glazed 'corners' over-counted (Wave-3 gate owed)",
                       "isovist area is in proportional cell units, not metres (no scale anchor)"])


# ================================================================ W2.5 barrier_permeability
def barrier_permeability(img_bgr, planes, Z=None) -> AttributeResult:
    """v2a_077 — partition permeability (SPRINT §5 W2.5). Emits TWO permeabilities and NEVER averages
    them (the rule): VISUAL = see-through fraction of the vertical-barrier envelope (aperture/glass
    over wall+aperture area; OPENING class stands in for aperture+glass — a declared heuristic until
    the Wave-3 glass gate), PHYSICAL = passable gap fraction at circulation height (the floor-adjacent
    wall band). The primary scalar is VISUAL permeability; PHYSICAL rides extras, explicitly separate.
    ABSTAINS when there is no wall/barrier in frame."""
    from .geometry import WALL, OPENING, FLOOR
    H, W = planes.shape[:2]
    wall = (planes == WALL); opening = (planes == OPENING)
    wall_px = int(wall.sum()); open_px = int(opening.sum())
    if (wall_px / float(H * W)) < PERM_MIN_WALL_FRAC:
        return AttributeResult(
            key="cnfa.geometry.barrier_permeability", scalar=None, confidence=0.0,
            method=f"ABSTAIN: wall fraction {wall_px/float(H*W):.3f} < {PERM_MIN_WALL_FRAC} — no barrier",
            extras={"wall_fraction": round(wall_px / float(H * W), 4)},
            failure_modes=["open scene with no vertical barrier -> permeability undefined (correct abstain)"])
    visual = float(open_px / (wall_px + open_px + 1e-9))
    # physical: the floor-adjacent band (circulation height) — passable = FLOOR or OPENING, blocked = WALL
    floor = (planes == FLOOR)
    if floor.any():
        band_top = int(np.percentile(np.where(floor.any(1))[0], 10))
    else:
        band_top = int(H * 0.6)
    band = slice(band_top, H)
    band_wall = int(wall[band].sum())
    band_pass = int(opening[band].sum() + floor[band].sum())
    physical = float(band_pass / (band_pass + band_wall + 1e-9))
    return AttributeResult(
        key="cnfa.geometry.barrier_permeability", scalar=visual, confidence=0.35,
        method=f"VISUAL see-through {visual:.3f} = opening/(wall+opening); PHYSICAL gap {physical:.3f} "
               f"at circulation band [rows {band_top}:{H}]; emitted SEPARATELY, never averaged (M1)",
        extras={"visual_permeability": round(visual, 4), "physical_permeability": round(physical, 4),
                "wall_px": wall_px, "opening_px": open_px, "circulation_band_top": band_top,
                "constants": {"perm_min_wall_frac": PERM_MIN_WALL_FRAC,
                              "note": "OPENING class == aperture+glass proxy (Wave-3 glass gate owed)"}},
        failure_modes=["visual and physical are DISTINCT axes — a consumer must not average them",
                       "glass vs open aperture not distinguished (OPENING proxy; declared heuristic)",
                       "AMBER: plane-seg mislabels bright walls/mirrors as OPENING -> inflated visual"])


# ================================================================ W2.8 threshold_emphasized
def threshold_emphasized(img_bgr, planes) -> AttributeResult:
    """arch.pattern.threshold_emphasized — an emphasized doorway/threshold (SPRINT §5 W2.8): a
    rectangular aperture (OPENING) set in a wall, with a luminance/material change across it and
    bounding frame edges (parallel vertical LSD segment pairs). emphasis = frame_contrast x relative
    aperture height. This op is ALLOWED TO DIE in S3 if the plane-seg can't carry doorways — it
    ABSTAINS rather than fabricate when no wall-embedded aperture is found."""
    from .geometry import WALL, OPENING
    H, W = planes.shape[:2]
    opening = (planes == OPENING).astype(np.uint8)
    if opening.sum() == 0:
        return AttributeResult(
            key="cnfa.arch.threshold_emphasized", scalar=None, confidence=0.0,
            method="ABSTAIN: no OPENING aperture in frame",
            extras={"reason": "no_aperture", "opening_px": 0},
            failure_modes=["no doorway/aperture detected by plane-seg (op may die in S3, allowed)"])
    n, lab, stats, _ = cv2.connectedComponentsWithStats(opening, connectivity=8)
    # largest opening component (ignore background label 0)
    if n <= 1:
        return AttributeResult(key="cnfa.arch.threshold_emphasized", scalar=None, confidence=0.0,
                               method="ABSTAIN: no aperture component",
                               extras={"reason": "no_aperture_component", "opening_px": int(opening.sum())},
                               failure_modes=["no aperture"])
    idx = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    x, y, w, h, area = (int(stats[idx, cv2.CC_STAT_LEFT]), int(stats[idx, cv2.CC_STAT_TOP]),
                        int(stats[idx, cv2.CC_STAT_WIDTH]), int(stats[idx, cv2.CC_STAT_HEIGHT]),
                        int(stats[idx, cv2.CC_STAT_AREA]))
    comp = (lab == idx)
    # aperture must be embedded in a wall: require WALL pixels in a dilated ring around it
    ring = cv2.dilate(comp.astype(np.uint8), np.ones((7, 7), np.uint8)) & ~comp
    wall_ring = int(((planes == WALL) & (ring > 0)).sum())
    if wall_ring < 0.10 * max(int(ring.sum()), 1):
        return AttributeResult(
            key="cnfa.arch.threshold_emphasized", scalar=None, confidence=0.0,
            method="ABSTAIN: largest aperture is not embedded in a wall (window/void, not a threshold)",
            extras={"aperture_bbox": [x, y, w, h], "wall_ring_frac": round(wall_ring / max(int(ring.sum()), 1), 3)},
            failure_modes=["free-standing opening (window/skylight) is not a passage threshold"])
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    inside = g[comp].mean() if comp.any() else 0.0
    surround = g[(ring > 0)].mean() if ring.any() else inside
    frame_contrast = float(np.clip(abs(inside - surround) / 255.0, 0, 1))
    aperture_height_frac = float(np.clip(h / float(H), 0, 1))
    # frame edges: parallel vertical LSD segment pairs bounding the aperture (evidence, not required)
    n_frame_edges = 0
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    out = lsd.detect(g.astype(np.uint8))
    if out is not None and out[0] is not None:
        P = out[0].reshape(-1, 4)
        vdx = np.abs(P[:, 2] - P[:, 0]); vdy = np.abs(P[:, 3] - P[:, 1])
        vertical = vdy > (3.0 * vdx + 1e-6)
        midx = 0.5 * (P[:, 0] + P[:, 2])
        near_l = vertical & (np.abs(midx - x) < 0.15 * W)
        near_r = vertical & (np.abs(midx - (x + w)) < 0.15 * W)
        n_frame_edges = int(near_l.any()) + int(near_r.any())
    emphasis = float(np.clip(frame_contrast * aperture_height_frac * (1.0 + 0.5 * n_frame_edges), 0, 1))
    return AttributeResult(
        key="cnfa.arch.threshold_emphasized", scalar=emphasis, confidence=0.3,
        method=f"emphasis = frame_contrast {frame_contrast:.3f} x aperture_height {aperture_height_frac:.3f} "
               f"x (1+0.5*{n_frame_edges} frame edges) (M1)",
        extras={"aperture_bbox": [x, y, w, h], "frame_contrast": round(frame_contrast, 4),
                "aperture_height_frac": round(aperture_height_frac, 4), "n_frame_edges": n_frame_edges,
                "constants": {"frame_edge_band_frac": 0.15, "ring_kernel": 7, "wall_ring_min_frac": 0.10}},
        failure_modes=["AMBER + SKETCH: plane-seg doorway quality is the limiter (op allowed to die in S3)",
                       "luminance contrast conflates lit thresholds with mere bright openings",
                       "material change is proxied by luminance only (no material classifier here)"])


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

    # ---- S3 remainder (CC-4) ----
    from cnfa_algs.geometry import UNKNOWN as GU, FLOOR as GF, CEILING as GC, WALL as GW, OPENING as GO

    # W2.2 / W2.3: tall room (ceiling high, floor low -> big span) > shallow band; no-ceiling abstains
    pl_tall = np.full((H, W), GW, np.uint8); pl_tall[0:40] = GC; pl_tall[H - 30:] = GF
    pl_short = np.full((H, W), GW, np.uint8); pl_short[80:100] = GC; pl_short[120:150] = GF
    pl_noceil = np.full((H, W), GW, np.uint8); pl_noceil[H - 40:] = GF
    dummy = mk(np.full((H, W, 3), 150.0))
    co_t = ceiling_openness_relative(dummy, pl_tall)
    co_s = ceiling_openness_relative(dummy, pl_short)
    co_n = ceiling_openness_relative(dummy, pl_noceil)
    assert co_t.scalar is not None and co_s.scalar is not None and co_n.scalar is None
    assert co_t.scalar > co_s.scalar, (co_t.scalar, co_s.scalar)
    print(f"W2.2 ceiling openness: tall span {co_t.scalar:.3f} > shallow {co_s.scalar:.3f}; "
          f"no-ceiling->abstain  OK")
    dh_t = double_height_space(dummy, pl_tall); dh_s = double_height_space(dummy, pl_short)
    dh_n = double_height_space(dummy, pl_noceil)
    assert dh_t.extras["double_height_flag"] and not dh_s.extras["double_height_flag"]
    assert dh_t.extras["needs_calibration"] and dh_n.scalar is None
    print(f"W2.3 double-height: tall flag={dh_t.extras['double_height_flag']} "
          f"shallow flag={dh_s.extras['double_height_flag']} (needs_calibration); no-ceiling->abstain  OK")

    # W2.5 barrier permeability: glazed (much OPENING) > solid wall; no-wall abstains; both axes emitted
    pl_glass = np.full((H, W), GW, np.uint8); pl_glass[:, :W // 2] = GO; pl_glass[H - 30:] = GF
    pl_solid = np.full((H, W), GW, np.uint8); pl_solid[H - 30:] = GF
    pl_nowall = np.full((H, W), GF, np.uint8)
    bp_g = barrier_permeability(dummy, pl_glass); bp_s = barrier_permeability(dummy, pl_solid)
    bp_n = barrier_permeability(dummy, pl_nowall)
    assert bp_g.scalar > bp_s.scalar and bp_n.scalar is None
    assert "visual_permeability" in bp_g.extras and "physical_permeability" in bp_g.extras
    assert abs(bp_g.scalar - bp_g.extras["visual_permeability"]) < 1e-4   # scalar IS visual, not an average
    assert abs(bp_g.scalar - 0.5 * (bp_g.extras["visual_permeability"] + bp_g.extras["physical_permeability"])) > 1e-6 \
        or bp_g.extras["visual_permeability"] == bp_g.extras["physical_permeability"]   # not the mean of the two axes
    print(f"W2.5 permeability: glazed visual {bp_g.scalar:.3f} > solid {bp_s.scalar:.3f}; "
          f"physical={bp_g.extras['physical_permeability']:.3f} (separate); no-wall->abstain  OK")

    # W2.8 threshold: doorway embedded in a wall (bright aperture) scores; free-standing / none abstain
    img_door = np.full((H, W, 3), 60, np.uint8)                  # dark wall
    pl_door = np.full((H, W), GW, np.uint8)
    pl_door[60:180, 140:180] = GO                               # aperture embedded in wall
    img_door[60:180, 140:180] = 230                            # bright through the doorway
    te = threshold_emphasized(img_door, pl_door)
    pl_float = np.full((H, W), GF, np.uint8); pl_float[60:180, 140:180] = GO   # opening in floor/void
    te_float = threshold_emphasized(img_door, pl_float)
    te_none = threshold_emphasized(dummy, np.full((H, W), GW, np.uint8))
    assert te.scalar is not None and te.scalar > 0 and te_float.scalar is None and te_none.scalar is None
    print(f"W2.8 threshold: embedded doorway emphasis {te.scalar:.3f} "
          f"(edges {te.extras['n_frame_edges']}); free-standing & none -> abstain  OK")

    # W2.4 blind corner: L-corridor (occluding turn) > straight corridor (0); tiny grid abstains
    def _Lgrid():
        g = np.full((64, 64), OBST, np.int8)
        g[10:52, 10:13] = FREE                                  # vertical arm
        g[49:52, 10:52] = FREE                                  # horizontal arm -> L
        return g
    def _straight():
        g = np.full((64, 64), OBST, np.int8); g[8:56, 30:33] = FREE
        return g
    bl_L = blind_corner_index(PG(_Lgrid(), 0.4))
    bl_S = blind_corner_index(PG(_straight(), 0.4))
    bl_tiny = blind_corner_index(PG(np.full((20, 20), OBST, np.int8), 0.4))
    assert bl_tiny.scalar is None, bl_tiny.method
    assert bl_L.scalar is not None and bl_S.scalar is not None
    assert bl_L.scalar > bl_S.scalar, (bl_L.scalar, bl_L.extras, bl_S.scalar, bl_S.extras)
    print(f"W2.4 blind corner: L-corridor {bl_L.scalar:.3f} (blind {bl_L.extras['n_blind']}/"
          f"{bl_L.extras['n_corners']}) > straight {bl_S.scalar:.3f}; tiny->abstain  OK")

    # determinism x2 (old + new)
    assert verticality_cues(mk(np.stack([col] * 3, -1))).scalar == vc.scalar
    assert choice_richness_zones(PG(g_mix, 0.5))["scalar"] == r_mix["scalar"]
    assert ceiling_openness_relative(dummy, pl_tall).scalar == co_t.scalar
    assert blind_corner_index(PG(_Lgrid(), 0.4)).scalar == bl_L.scalar
    assert barrier_permeability(dummy, pl_glass).scalar == bp_g.scalar
    print("determinism x2 (incl. W2.2/W2.4/W2.5)  OK")
    print("-" * 56 + "\nwave2_geometry self-test: PASS")
