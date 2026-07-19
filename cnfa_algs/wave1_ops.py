"""
cnfa_algs.wave1_ops — Sprint COMP-CORRECT Stage S2: the Wave-1 classical-CV operators.
(Codex Section-D triage keeps, 2026-07-18; algorithms per SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19 §4.)

Operators (all AMBER — construct validation is corpus-blocked; tier honesty in every method string):
  W1.1  luminance_gradient_contrast   v2a_004  — the room's light ARCHITECTURE (vs 31px texture)
  W1.2  shadow_softness               v2a_009  — penumbra width via illumination-vs-material edges
        (+ daylight_hard / daylight_soft flags = thresholded ends of the same measurement)
  W1.3  sun_patch_geometry            v2a_014  — bright warm polygon-like patches (CANDIDATE only)
  W1.4  evening_ambience              v2a_011  — CCT proxy (McCamy) + luminance distribution
  W1.5  temperature_mismatch          v2a_015  — max pairwise mired gap between chromaticity clusters
  W1.6  spotlight_pool_geometry       v2a_013  — top-hat bright pools (geometry only; social claim
                                                 deferred to a compound with seat inputs)
  W1.7  dark_zone_map                 v2a_081  — dark connected zones (named map, NOT "safety")
  W1.8  texture_density               v2a_088  — micro-texture after structure removal (≠ clutter)
  W1.9  orderliness_alignment         v2a_094  — LSD segment orientation order (≠ V13 pixel entropy)

Every operator: pure, deterministic, ABSTAINS (returns None scalar + reason) rather than fabricates,
declares constants in extras for exact replay. Images are BGR uint8 (cv2.imread order).

Self-test (synthetic fixtures, ordering + negative controls + determinism):
    python3 -m cnfa_algs.wave1_ops
"""
from __future__ import annotations
from typing import Dict, Optional
import numpy as np
import cv2

try:
    from .attributes import AttributeResult, normalize01
except Exception:                                       # standalone execution
    from attributes import AttributeResult, normalize01  # type: ignore


# ---------------------------------------------------------------- shared helpers
def _gray01(img_bgr) -> np.ndarray:
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0


def _srgb_to_xy(img_bgr):
    """Mean CIE 1931 chromaticity (x,y) of given pixels. Linearizes sRGB (IEC 61966-2-1 EOTF),
    then the standard sRGB->XYZ D65 matrix. Returns per-pixel x,y arrays."""
    rgb = img_bgr[..., ::-1].astype(np.float64) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    XYZ = lin @ M.T
    s = XYZ.sum(-1)
    ok = s > 1e-9
    x = np.where(ok, XYZ[..., 0] / np.maximum(s, 1e-9), 0.3127)
    y = np.where(ok, XYZ[..., 1] / np.maximum(s, 1e-9), 0.3290)
    return x, y, XYZ[..., 1]     # x, y, luminance Y (linear)


def mccamy_cct(x: float, y: float) -> Optional[float]:
    """McCamy 1992 CCT approximation from CIE 1931 (x,y). Valid roughly 2000-12500 K near the
    Planckian locus; returns None outside a sane range (the caller declares the limit)."""
    if abs(y - 0.1858) < 1e-6:
        return None
    n = (x - 0.3320) / (y - 0.1858)     # McCamy 1992: n = (x-x_e)/(y-y_e), epicenter (0.3320, 0.1858)
    cct = -449.0 * n ** 3 + 3525.0 * n ** 2 - 6823.3 * n + 5520.33
    return float(cct) if 1000.0 <= cct <= 25000.0 else None


# ================================================================ W1.1 luminance_gradient_contrast
def luminance_gradient_contrast(img_bgr) -> AttributeResult:
    """v2a_004 — the LARGE-SCALE light architecture: blur kills texture, keeps lighting; then
    (a) mean gradient of the blurred field, (b) direction coherence, (c) robust contrast ratio."""
    g = _gray01(img_bgr)
    diag = float(np.hypot(*g.shape))
    sigma = max(diag / 64.0, 2.0)
    G = cv2.GaussianBlur(g, (0, 0), sigma)
    if float(g.std()) < (2.0 / 255.0):
        return AttributeResult(key="cnfa.light.luminance_gradient_contrast", scalar=None,
                               confidence=0.0, method="ABSTAIN: near-blank image (std<2DN)",
                               failure_modes=["undefined on blank input"])
    gx = cv2.Sobel(G, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(G, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    mean_grad = float(mag.mean()) * diag                # per-image-diagonal units (scale-free)
    # direction coherence on DOUBLED angles (gradient direction is axial)
    w = mag.ravel() + 1e-12
    th = np.arctan2(gy, gx).ravel() * 2.0
    coherence = float(np.hypot((w * np.cos(th)).sum(), (w * np.sin(th)).sum()) / w.sum())
    p5, p95 = np.percentile(G, 5), np.percentile(G, 95)
    contrast_ratio = float((p95 + 1e-4) / (p5 + 1e-4))
    scalar = float(np.clip(mean_grad / 60.0, 0, 1))     # 60 = declared full-scale (real interiors 17-34, smoke 2026-07-19)
    return AttributeResult(
        key="cnfa.light.luminance_gradient_contrast", scalar=scalar,
        field=normalize01(mag), confidence=0.75,
        method=f"large-scale luminance gradient (sigma=diag/64) + coherence + p95/p5 (M1)",
        extras={"mean_grad_diagu": round(mean_grad, 4), "coherence": round(coherence, 4),
                "contrast_ratio_p95_p5": round(contrast_ratio, 3),
                "sigma_px": round(sigma, 2), "fullscale_grad": 60.0},
        failure_modes=["camera exposure/HDR shapes the field", "AMBER: no lux claim, relative only"])


# ================================================================ W1.2 shadow_softness (+hard/soft)
SHADOW_MIN_EDGES = 25          # below this the penumbra distribution is undefined -> abstain
SHADOW_CHROMA_TOL = 0.12       # max relative chromaticity change across an ILLUMINATION edge
SHADOW_LUM_RATIO_MIN = 1.3     # min luminance ratio across the edge to call it a shadow edge
PENUMBRA_HARD_FRAC = 0.004     # softness-ramp zero point (fraction of diagonal)
PENUMBRA_HARD_PX = 3.0         # HARD flag: median width at the ~2px step-edge measurement floor
PENUMBRA_SOFT_FRAC = 0.045     # softness-ramp full-scale (real interiors 0.019-0.034)
PENUMBRA_SOFT_FLAG = 0.020     # SOFT flag threshold — NEEDS corpus calibration (AMBER)


def _penumbra_widths(img_bgr, max_samples: int = 400):
    """Candidate illumination edges: LUMINANCE-TRANSITION points where chromaticity is stable but
    luminance jumps. Candidates come from the blurred-gradient field (NOT Canny — Canny misses soft
    penumbrae entirely, a survivorship bias toward hard shadows that the v1 fixture caught). At each,
    sample the luminance profile along the gradient normal; width = the 10-90% transition span."""
    g = _gray01(img_bgr)
    H, W = g.shape
    b, gr, r = [img_bgr[..., i].astype(np.float64) + 1.0 for i in range(3)]
    rg, bg = r / gr, b / gr
    G = cv2.GaussianBlur(g, (0, 0), 2.0)                 # candidate detection field only
    P0 = cv2.GaussianBlur(g, (0, 0), 0.8)                # measurement field (near-raw)
    gx = cv2.Sobel(G, cv2.CV_32F, 1, 0, 3); gy = cv2.Sobel(G, cv2.CV_32F, 0, 1, 3)
    mag = np.sqrt(gx * gx + gy * gy)
    if float(mag.max()) < 1e-4:
        return [], 0, 0
    cand = mag > 0.25 * mag.max()                        # transition band incl. soft penumbrae
    ys, xs = np.nonzero(cand)
    if len(ys) == 0:
        return [], 0, 0
    order = np.argsort(-mag[ys, xs])                     # strongest transitions first (deterministic)
    step = max(1, len(order) // max_samples)
    idx = order[::step]
    L = 24                                               # half-profile length (px) — fits sigma<=8 penumbra
    widths, n_cand, n_material = [], 0, 0
    for k in idx:
        y0, x0 = int(ys[k]), int(xs[k])
        n = np.array([gx[y0, x0], gy[y0, x0]])
        nn = np.hypot(*n)
        if nn < 1e-6:
            continue
        n = n / nn
        ts = np.arange(-L, L + 1)
        px = np.clip((x0 + ts * n[0]).round().astype(int), 0, W - 1)
        py = np.clip((y0 + ts * n[1]).round().astype(int), 0, H - 1)
        prof = P0[py, px]        # measure on the RAW (lightly smoothed) luminance — the sigma=2
                                 # candidate blur must not contaminate the width measurement
        lo, hi = prof.min(), prof.max()
        if hi < 1e-4 or (hi / max(lo, 1e-4)) < SHADOW_LUM_RATIO_MIN:
            continue
        n_cand += 1
        # chromaticity stability across the edge (dark side vs bright side means)
        dark_side = prof < (lo + 0.4 * (hi - lo)); bright_side = prof > (lo + 0.6 * (hi - lo))
        if dark_side.sum() < 2 or bright_side.sum() < 2:
            continue
        drg = abs(np.median(rg[py, px][dark_side]) - np.median(rg[py, px][bright_side]))
        dbg = abs(np.median(bg[py, px][dark_side]) - np.median(bg[py, px][bright_side]))
        rel = max(drg / (np.median(rg[py, px]) + 1e-6), dbg / (np.median(bg[py, px]) + 1e-6))
        if rel > SHADOW_CHROMA_TOL:
            n_material += 1
            continue                                     # material edge, not illumination
        # 10-90% transition width along the (sorted-by-t) profile
        t10, t90 = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)
        inside = (prof >= t10) & (prof <= t90)
        if inside.any():
            widths.append(float(inside.sum()))
    return widths, n_cand, n_material


def shadow_softness(img_bgr) -> AttributeResult:
    """v2a_009 — median penumbra width over accepted illumination edges, normalized by diagonal.
    daylight_hard / daylight_soft are declared thresholds on the same measurement (one operator,
    three consumer-visible outputs)."""
    widths, n_cand, n_material = _penumbra_widths(img_bgr)
    diag = float(np.hypot(*img_bgr.shape[:2]))
    if len(widths) < SHADOW_MIN_EDGES:
        return AttributeResult(
            key="cnfa.light.shadow_softness", scalar=None, confidence=0.0,
            method=f"ABSTAIN: {len(widths)} accepted illumination edges < {SHADOW_MIN_EDGES}",
            extras={"n_candidates": n_cand, "n_rejected_material": n_material},
            failure_modes=["undefined without sufficient shadow edges"])
    w_px = float(np.median(widths))
    w_frac = w_px / diag
    softness = float(np.clip((w_frac - PENUMBRA_HARD_FRAC) /
                             (PENUMBRA_SOFT_FRAC - PENUMBRA_HARD_FRAC), 0, 1))
    # HARD flag lives in PIXELS: a step edge measures ~2px under the sigma=0.8 measurement
    # smoothing regardless of image size, so the floor is resolution-independent.
    is_hard = bool(w_px <= PENUMBRA_HARD_PX)
    return AttributeResult(
        key="cnfa.light.shadow_softness", scalar=softness, confidence=0.6,
        method="median 10-90% penumbra width over chromaticity-stable luminance edges (M1)",
        extras={"penumbra_frac_diag": round(w_frac, 5), "n_edges": len(widths),
                "n_rejected_material": n_material,
                "daylight_hard": is_hard, "penumbra_px": round(w_px, 2),
                "daylight_soft": bool(w_frac > PENUMBRA_SOFT_FLAG),
                "thresholds": {"hard_px": PENUMBRA_HARD_PX, "hard_frac": PENUMBRA_HARD_FRAC,
                               "soft_full": PENUMBRA_SOFT_FRAC, "soft_flag": PENUMBRA_SOFT_FLAG,
                               "chroma_tol": SHADOW_CHROMA_TOL, "lum_ratio_min": SHADOW_LUM_RATIO_MIN}},
        failure_modes=["illumination/material separation is heuristic (AMBER)",
                       "defocus blur reads as soft shadow", "requires >=25 accepted edges"])


# ================================================================ W1.3 sun_patch_geometry
def sun_patch_geometry(img_bgr) -> AttributeResult:
    """v2a_014 — bright (>p92) connected patches that are WARMER than their surround and have
    straight-ish boundaries. GEOMETRY CANDIDATE only — cannot prove sun."""
    g = _gray01(img_bgr)
    # median-anchored threshold, NOT a percentile: a patch bigger than (100-pctl)% of the frame
    # swallows its own percentile and the mask comes out empty (v1 fixture failure)
    med, mx = float(np.median(g)), float(g.max())
    if mx < med + 0.15:
        return AttributeResult(key="cnfa.light.sun_patch_geometry", scalar=0.0, confidence=0.5,
                               method="no bright-over-median region (max < median+0.15) (M1)",
                               extras={"n_patches": 0, "patches": [], "thr": None},
                               failure_modes=["no claim possible without a bright region"])
    thr = med + 0.6 * (mx - med)
    mask = (g > thr).astype(np.uint8)
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    b, gr, r = [img_bgr[..., i].astype(np.float64) + 1.0 for i in range(3)]
    warm = r / b                                          # higher = warmer
    diag = float(np.hypot(*g.shape))
    total, patches = 0.0, []
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 0.001 * g.size or area > 0.5 * g.size:
            continue
        comp = (lbl == i).astype(np.uint8)
        ring = cv2.dilate(comp, np.ones((9, 9), np.uint8)) - comp
        if ring.sum() < 10:
            continue
        warmth_contrast = float(np.median(warm[comp > 0]) / (np.median(warm[ring > 0]) + 1e-9) - 1.0)
        cont, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        peri = cv2.arcLength(cont[0], True)
        approx = cv2.approxPolyDP(cont[0], 0.02 * peri, True)
        straightness = float(np.clip(1.0 - (len(approx) - 4) / 12.0, 0, 1))  # 4-gon ~ 1.0
        score = (area / g.size) * straightness * np.clip(warmth_contrast * 10, 0, 1)
        if score > 0:
            total += score
            patches.append({"bbox": [int(v) for v in stats[i, :4]],
                            "warmth_contrast": round(warmth_contrast, 4),
                            "straightness": round(straightness, 3)})
    return AttributeResult(
        key="cnfa.light.sun_patch_geometry", scalar=float(np.clip(total * 20, 0, 1)),
        confidence=0.5,
        method="bright warm straight-boundary patch geometry — sun-patch CANDIDATE, not proof (M1)",
        extras={"n_patches": len(patches), "patches": patches[:8], "thr": round(thr, 4)},
        failure_modes=["specular highlights / luminaires mimic sun patches (AMBER)",
                       "white-balance shifts the warmth test"])


# ================================================================ W1.4 evening_ambience
def evening_ambience(img_bgr) -> AttributeResult:
    """v2a_011 — CCT proxy of the lit portion (McCamy on mean chromaticity of the p60-p95
    luminance band, clipped pixels excluded) + luminance level & skew -> evening score."""
    x, y, Y = _srgb_to_xy(img_bgr)
    g = _gray01(img_bgr)
    lo, hi = np.percentile(g, 60), np.percentile(g, 95)
    band = (g >= lo) & (g <= hi) & (g < 0.98)
    clipped_frac = float((g >= 0.98).mean())
    if band.sum() < 100:
        return AttributeResult(key="cnfa.light.evening_ambience", scalar=None, confidence=0.0,
                               method="ABSTAIN: <100 usable bright-band pixels",
                               failure_modes=["undefined on clipped/blank input"])
    cct = mccamy_cct(float(x[band].mean()), float(y[band].mean()))
    mean_lum = float(g.mean())
    sd = float(g.std())
    skew = float(((g - mean_lum) ** 3).mean() / (sd ** 3 + 1e-12))
    warm_term = 0.0 if cct is None else float(np.clip((4500.0 - cct) / 2000.0, 0, 1))
    dim_term = float(np.clip((0.45 - mean_lum) / 0.30, 0, 1))
    pool_term = float(np.clip(skew / 2.0, 0, 1))
    scalar = float(np.clip(0.45 * warm_term + 0.35 * dim_term + 0.20 * pool_term, 0, 1))
    return AttributeResult(
        key="cnfa.light.evening_ambience", scalar=scalar, confidence=0.6,
        method="McCamy CCT proxy (bright band) + dimness + luminance skew (M1)",
        extras={"cct_proxy_K": None if cct is None else round(cct, 0),
                "mean_lum": round(mean_lum, 4), "lum_skew": round(skew, 3),
                "clipped_frac": round(clipped_frac, 4), "awb_unknown": True,
                "weights": [0.45, 0.35, 0.20], "warm_below_K": 4500, "dim_below": 0.45},
        failure_modes=["WHITE BALANCE confound is undeclared in consumer photos (AMBER)",
                       "CCT proxy from mixed illuminants is a mixture, not a source CCT"])


# ================================================================ W1.5 temperature_mismatch
def temperature_mismatch(img_bgr, k: int = 3) -> AttributeResult:
    """v2a_015 — seeded k-means over chromaticity of adequately-bright pixels; per-cluster CCT;
    mismatch = max pairwise |delta-mired| weighted by the smaller cluster's share (x2, capped)."""
    x, y, _ = _srgb_to_xy(img_bgr)
    g = _gray01(img_bgr)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[..., 1].astype(np.float64) / 255.0
    ok = (g > 0.15) & (g < 0.98)
    if float(sat[ok].mean() if ok.any() else 0) < 0.05:
        return AttributeResult(key="cnfa.light.temperature_mismatch", scalar=None, confidence=0.0,
                               method="ABSTAIN: mean saturation < 0.05 (chromaticity uninformative)",
                               failure_modes=["undefined on near-grayscale input"])
    pts = np.stack([x[ok], y[ok]], -1).astype(np.float32)
    cv2.setRNGSeed(1234)
    _, labels, cents = cv2.kmeans(pts, k, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1e-4), 2, cv2.KMEANS_PP_CENTERS)
    p = np.bincount(labels.ravel(), minlength=k) / len(labels)
    ccts = [mccamy_cct(float(cx), float(cy)) for cx, cy in cents]
    best, pair = 0.0, None
    for i in range(k):
        for j in range(i + 1, k):
            if ccts[i] is None or ccts[j] is None:
                continue
            dmired = abs(1e6 / ccts[i] - 1e6 / ccts[j])
            wgt = float(np.clip(2.0 * min(p[i], p[j]), 0, 1))   # a 2% stray cluster != a mismatch
            v = dmired * wgt
            if v > best:
                best, pair = v, (round(ccts[i]), round(ccts[j]), round(dmired, 1), round(wgt, 3))
    scalar = float(np.clip(best / 150.0, 0, 1))                  # 150 mired = declared full scale
    return AttributeResult(
        key="cnfa.light.temperature_mismatch", scalar=scalar, confidence=0.55,
        method="seeded chromaticity k-means -> per-cluster McCamy CCT -> max weighted mired gap (M1)",
        extras={"clusters_cct_K": [None if c is None else round(c) for c in ccts],
                "proportions": [round(float(v), 3) for v in p], "worst_pair": pair,
                "fullscale_mired": 150.0, "awb_unknown": True},
        failure_modes=["AWB confound (AMBER)", "colored SURFACES read as illuminant mismatch",
                       "McCamy invalid far from Planckian locus -> cluster dropped"])


# ================================================================ W1.6 spotlight_pool_geometry
def spotlight_pool_geometry(img_bgr) -> AttributeResult:
    """v2a_013 — top-hat bright pools: geometry substrate ONLY (count/area/elongation/centroids).
    The social-exposure CLAIM needs seat/person regions -> a Wave-3 compound, not this operator."""
    g = _gray01(img_bgr)
    diag = float(np.hypot(*g.shape))
    # SE must be LARGER than the pools it should keep (top-hat erases features bigger than the
    # element — the v1 diag/40 element erased an 18px-radius pool, keeping only its rim)
    r = int(np.clip(diag / 8, 15, 80))
    se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    tophat = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, se)
    mask = (tophat > 0.15).astype(np.uint8)
    n, lbl, stats, cents = cv2.connectedComponentsWithStats(mask, 8)
    pools = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < 0.0005 * g.size or area > 0.02 * g.size:
            continue                                     # >2% of frame = window/ceiling, not a pool
        w, h = int(stats[i, cv2.CC_STAT_WIDTH]), int(stats[i, cv2.CC_STAT_HEIGHT])
        pools.append({"bbox": [int(v) for v in stats[i, :4]], "area_frac": round(area / g.size, 5),
                      "elongation": round(max(w, h) / max(min(w, h), 1), 2),
                      "centroid": [round(float(c), 1) for c in cents[i]]})
    total_area = sum(p["area_frac"] for p in pools)
    scalar = float(1.0 - np.exp(-total_area / 0.02))   # soft saturation, declared scale
    return AttributeResult(
        key="cnfa.light.spotlight_pool_geometry", scalar=scalar,
        field=normalize01(tophat), confidence=0.7,
        method=f"morphological top-hat (r=diag/8) bright-pool geometry — NO social claim (M1)",
        extras={"n_pools": len(pools), "pools": pools[:10], "tophat_thr": 0.15,
                "se_radius_px": r},
        failure_modes=["specular reflections count as pools",
                       "social-exposure interpretation requires seat inputs (deferred compound)"])


# ================================================================ W1.7 dark_zone_map
def dark_zone_map(img_bgr) -> AttributeResult:
    """v2a_081 — connected LOW-luminance zones of the blurred field. Named a MAP, not 'safety':
    the safety construct needs localization semantics + corpus (deferred)."""
    g = _gray01(img_bgr)
    G = cv2.GaussianBlur(g, (0, 0), max(np.hypot(*g.shape) / 128.0, 2.0))
    med = float(np.median(G))
    if med < 0.02:
        return AttributeResult(key="cnfa.light.dark_zone_map", scalar=None, confidence=0.0,
                               method="ABSTAIN: image globally dark (median<0.02) — zones undefined",
                               failure_modes=["a night photo is not a dark ZONE finding"])
    mask = (G < 0.25 * med).astype(np.uint8)
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    zones = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < 0.002 * g.size:
            continue
        deficit = float(med - G[lbl == i].mean())
        x0, y0, w, h = [int(v) for v in stats[i, :4]]
        on_boundary = x0 == 0 or y0 == 0 or x0 + w >= g.shape[1] or y0 + h >= g.shape[0]
        zones.append({"bbox": [x0, y0, w, h], "area_frac": round(area / g.size, 5),
                      "depth": round(deficit, 4), "touches_boundary": bool(on_boundary)})
    scalar = float(np.clip(sum(z["area_frac"] * z["depth"] * 40 for z in zones), 0, 1))
    return AttributeResult(
        key="cnfa.light.dark_zone_map", scalar=scalar, field=1.0 - normalize01(G),
        confidence=0.7,
        method="blurred-luminance dark zones (<0.25 x median): area x depth — MAP, not 'safety' (M1)",
        extras={"n_zones": len(zones), "zones": zones[:10], "rel_thr": 0.25,
                "global_median": round(med, 4)},
        failure_modes=["exposure-dependent (AMBER)", "safety CLAIM deferred to geometry+corpus"])


# ================================================================ W1.8 texture_density
def texture_density(img_bgr) -> AttributeResult:
    """v2a_088 — micro-texture energy AFTER structure removal: 5x5 local range of luminance with
    the dilated long-edge set masked out. Distinct from clutter (global) by construction."""
    g = _gray01(img_bgr)
    if float(g.std()) < (2.0 / 255.0):
        return AttributeResult(key="cnfa.material.texture_density", scalar=None, confidence=0.0,
                               method="ABSTAIN: near-blank image", failure_modes=["undefined"])
    k = np.ones((5, 5), np.uint8)
    rng = cv2.dilate(g, k) - cv2.erode(g, k)              # local range (max-min)
    edges = cv2.Canny((g * 255).astype(np.uint8), 60, 160)
    structure = cv2.dilate(edges, np.ones((7, 7), np.uint8)) > 0
    keep = ~structure
    if keep.mean() < 0.2:
        return AttributeResult(key="cnfa.material.texture_density", scalar=None, confidence=0.0,
                               method="ABSTAIN: <20% of image left after structure removal",
                               extras={"structure_frac": round(float(structure.mean()), 3)},
                               failure_modes=["edge-dense scene: texture/structure inseparable"])
    dens = float(rng[keep].mean())
    return AttributeResult(
        key="cnfa.material.texture_density", scalar=float(np.clip(dens / 0.15, 0, 1)),
        field=normalize01(np.where(keep, rng, 0)), confidence=0.7,
        method="5x5 local-range energy on non-structure pixels (Canny+dilate masked) (M1)",
        extras={"raw_mean_range": round(dens, 5), "structure_frac": round(float(structure.mean()), 3),
                "fullscale": 0.15},
        failure_modes=["JPEG/sensor noise inflates texture (check bytes/pixel artifact flag)",
                       "defocus blur deflates it"])


# ================================================================ W1.9 orderliness_alignment
LSD_MIN_SEGMENTS = 20


def orderliness_alignment(img_bgr) -> AttributeResult:
    """v2a_094 — LSD line segments; length-weighted orientation histogram folded to [0,pi);
    orderliness = 1 - H/Hmax; alignment = length fraction within +/-5 deg of the two modes.
    Segment-scale order: deliberately distinct from V13's pixel-scale entropy."""
    g8 = (_gray01(img_bgr) * 255).astype(np.uint8)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    out = lsd.detect(g8)
    segs = out[0] if out is not None and out[0] is not None else None
    if segs is None or len(segs) < LSD_MIN_SEGMENTS:
        n = 0 if segs is None else len(segs)
        return AttributeResult(key="cnfa.geometry.orderliness_alignment", scalar=None,
                               confidence=0.0,
                               method=f"ABSTAIN: {n} segments < {LSD_MIN_SEGMENTS}",
                               failure_modes=["orientation order undefined without segments"])
    P = segs.reshape(-1, 4)
    dx, dy = P[:, 2] - P[:, 0], P[:, 3] - P[:, 1]
    length = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx) % np.pi
    nb = 36
    idx = np.minimum((ang / np.pi * nb).astype(int), nb - 1)
    h = np.bincount(idx, weights=length, minlength=nb).astype(float)
    hn = h / (h.sum() + 1e-12)
    p = hn[hn > 0]
    H = float(-(p * np.log(p)).sum() / np.log(nb))
    orderliness = 1.0 - H
    # alignment to the two dominant modes (folded)
    m1 = int(np.argmax(h)); h2 = h.copy(); lo = (m1 - 2) % nb;
    for d in range(-2, 3):
        h2[(m1 + d) % nb] = 0
    m2 = int(np.argmax(h2))
    tol = 5.0 / 180.0 * np.pi
    centers = (np.arange(nb) + 0.5) / nb * np.pi
    def near(mode):
        d = np.abs(ang - centers[mode])
        d = np.minimum(d, np.pi - d)
        return d <= tol
    aligned = float(length[near(m1) | near(m2)].sum() / (length.sum() + 1e-12))
    return AttributeResult(
        key="cnfa.geometry.orderliness_alignment", scalar=float(np.clip(orderliness, 0, 1)),
        confidence=0.7,
        method="LSD segments: 1 - length-weighted orientation entropy; alignment to 2 modes (M1)",
        extras={"n_segments": int(len(P)), "alignment_2mode": round(aligned, 4),
                "entropy_norm": round(H, 4), "nbins": nb, "mode_bins": [m1, m2],
                "total_length_px": round(float(length.sum()), 1)},
        failure_modes=["LSD sensitivity to blur/noise (declared params)",
                       "abstains below 20 segments — no imputed order"])


ALL_WAVE1 = {
    "cnfa.light.luminance_gradient_contrast": luminance_gradient_contrast,
    "cnfa.light.shadow_softness": shadow_softness,
    "cnfa.light.sun_patch_geometry": sun_patch_geometry,
    "cnfa.light.evening_ambience": evening_ambience,
    "cnfa.light.temperature_mismatch": temperature_mismatch,
    "cnfa.light.spotlight_pool_geometry": spotlight_pool_geometry,
    "cnfa.light.dark_zone_map": dark_zone_map,
    "cnfa.material.texture_density": texture_density,
    "cnfa.geometry.orderliness_alignment": orderliness_alignment,
}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("wave1_ops self-test (synthetic fixtures)\n" + "-" * 56)
    rng = np.random.RandomState(0)

    def mk(f):
        return np.clip(f, 0, 255).astype(np.uint8)

    H, W = 240, 320
    yy, xx = np.mgrid[0:H, 0:W]
    flat = mk(np.full((H, W, 3), 128.0))
    gradient = mk(np.stack([40 + 170 * xx / W] * 3, -1))

    # W1.1 ordering: flat abstains; gradient > lightly-shaded room
    r = luminance_gradient_contrast(flat); assert r.scalar is None
    g1 = luminance_gradient_contrast(gradient)
    soft = mk(np.stack([100 + 30 * xx / W] * 3, -1))
    g2 = luminance_gradient_contrast(soft)
    assert g1.scalar > g2.scalar > 0
    print(f"W1.1 flat->abstain; strong grad {g1.scalar:.3f} > soft grad {g2.scalar:.3f}  OK")

    # W1.2: hard-edged shadow vs blurred shadow; material (colored) edge rejected
    base = np.full((H, W), 200.0)
    hard = base.copy(); hard[:, W // 2:] = 90.0
    hard3 = mk(np.stack([hard] * 3, -1))
    soft_sh = cv2.GaussianBlur(hard.astype(np.float32), (0, 0), 6.0)
    soft3 = mk(np.stack([soft_sh] * 3, -1))
    rh, rs = shadow_softness(hard3), shadow_softness(soft3)
    assert rh.scalar is not None and rs.scalar is not None
    assert rs.scalar > rh.scalar, (rh.scalar, rs.scalar)
    assert rh.extras["daylight_hard"] is True and rs.extras["daylight_soft"] is True
    matl = np.full((H, W, 3), 200.0); matl[:, W // 2:, 0] = 60; matl[:, W // 2:, 1] = 90; matl[:, W // 2:, 2] = 90
    rm = shadow_softness(mk(matl))
    assert rm.scalar is None or rm.extras.get("n_rejected_material", 0) > 0
    print(f"W1.2 hard {rh.scalar:.2f} < soft {rs.scalar:.2f}; hard/soft flags OK; material edge rejected  OK")

    # W1.3: bright WARM straight-edged quad > same-luminance NEUTRAL blob > none
    sunimg = np.full((H, W, 3), 90.0)
    sunimg[60:140, 80:200] = [120, 200, 250]              # warm bright parallelogram (BGR)
    blobimg = np.full((H, W, 3), 90.0)
    cv2.circle(blobimg, (140, 100), 55, (235, 235, 235), -1)   # neutral bright disc
    spg_sun = sun_patch_geometry(mk(sunimg))
    spg_blob = sun_patch_geometry(mk(blobimg))
    spg_none = sun_patch_geometry(flat)
    assert spg_sun.scalar > spg_blob.scalar and spg_none.extras["n_patches"] == 0
    print(f"W1.3 warm quad {spg_sun.scalar:.2f} > neutral disc {spg_blob.scalar:.2f}; flat->none  OK")

    # W1.4: warm+dim evening > cool+bright day
    warm_dim = mk(np.stack([np.full((H, W), 40.0), np.full((H, W), 55.0), np.full((H, W), 90.0)], -1))
    cool_bright = mk(np.stack([np.full((H, W), 210.0), np.full((H, W), 190.0), np.full((H, W), 170.0)], -1))
    ev_w, ev_c = evening_ambience(warm_dim), evening_ambience(cool_bright)
    assert ev_w.scalar > ev_c.scalar
    print(f"W1.4 warm-dim {ev_w.scalar:.2f} > cool-bright {ev_c.scalar:.2f}  "
          f"(CCTs {ev_w.extras['cct_proxy_K']}, {ev_c.extras['cct_proxy_K']})  OK")

    # W1.5: half-warm/half-cool image >> uniform; grayscale abstains
    # plausible ILLUMINANT tints (not saturated surfaces — far-off-locus colors correctly
    # fail the McCamy validity guard): warm ~3000K zone vs cool ~8000K zone
    mixed = np.zeros((H, W, 3)); mixed[:, :W // 2] = [110, 160, 230]; mixed[:, W // 2:] = [230, 190, 160]
    tm_mix = temperature_mismatch(mk(mixed))
    tm_uni = temperature_mismatch(warm_dim)
    tm_gray = temperature_mismatch(flat)
    assert tm_gray.scalar is None and tm_mix.scalar > tm_uni.scalar
    print(f"W1.5 mixed {tm_mix.scalar:.2f} > uniform {tm_uni.scalar:.2f}; grayscale->abstain  OK")

    # W1.6: one bright pool on dark floor -> pool found; uniform -> none
    poolimg = np.full((H, W, 3), 60.0); cv2.circle(poolimg, (160, 120), 18, (240, 240, 240), -1)
    sp = spotlight_pool_geometry(mk(poolimg))
    sp0 = spotlight_pool_geometry(flat)
    assert sp.extras["n_pools"] >= 1 and sp0.extras["n_pools"] == 0
    print(f"W1.6 pool found ({sp.extras['n_pools']}), uniform none  OK")

    # W1.7: image with a dark alcove -> zone found; globally-dark image abstains
    dz = np.full((H, W, 3), 150.0); dz[150:230, 20:120] = 12.0
    rz = dark_zone_map(mk(dz)); rnight = dark_zone_map(mk(np.full((H, W, 3), 3.0)))
    assert rz.extras["n_zones"] >= 1 and rz.scalar > 0 and rnight.scalar is None
    print(f"W1.7 dark zone found (depth {rz.extras['zones'][0]['depth']}); night photo->abstain  OK")

    # W1.8: noise texture > smooth; structure (edges) masked out
    # MICRO-texture = sub-Canny amplitude (40DN noise reads as dense STRUCTURE and correctly
    # abstains via the <20%-left guard — that path is asserted below as the negative control)
    tex = mk(np.stack([128 + 10 * rng.randn(H, W)] * 3, -1))
    td_t, td_s = texture_density(tex), texture_density(gradient)
    td_dense = texture_density(mk(np.stack([128 + 60 * rng.randn(H, W)] * 3, -1)))
    assert td_dense.scalar is None, "edge-saturated input must abstain, not fabricate texture"
    assert td_t.scalar > (td_s.scalar or 0)
    print(f"W1.8 noise texture {td_t.scalar:.2f} > smooth {td_s.scalar or 0:.2f}  OK")

    # W1.9: grid of aligned lines > random sticks; blank abstains
    grid_img = np.full((H, W), 255.0)
    for xg in range(20, W, 40): cv2.line(grid_img, (xg, 0), (xg, H - 1), 0, 2)
    for yg in range(20, H, 40): cv2.line(grid_img, (0, yg), (W - 1, yg), 0, 2)
    rand_img = np.full((H, W), 255.0)
    for _ in range(60):
        p0 = rng.randint(0, [W, H]); a = rng.rand() * np.pi; L = 40
        p1 = (int(p0[0] + L * np.cos(a)), int(p0[1] + L * np.sin(a)))
        cv2.line(rand_img, tuple(p0), p1, 0, 2)
    og = orderliness_alignment(mk(np.stack([grid_img] * 3, -1)))
    orr = orderliness_alignment(mk(np.stack([rand_img] * 3, -1)))
    ob = orderliness_alignment(flat)
    assert ob.scalar is None and og.scalar > orr.scalar
    assert og.extras["alignment_2mode"] > orr.extras["alignment_2mode"]
    print(f"W1.9 grid order {og.scalar:.2f} > random {orr.scalar:.2f}; blank->abstain; "
          f"alignment {og.extras['alignment_2mode']:.2f} > {orr.extras['alignment_2mode']:.2f}  OK")

    # determinism x2 across all operators on one busy synthetic
    busy = mk(np.stack([128 + 40 * rng.randn(H, W)] * 3, -1))
    for key, fn in ALL_WAVE1.items():
        a, b = fn(busy), fn(busy)
        assert (a.scalar is None and b.scalar is None) or abs(a.scalar - b.scalar) < 1e-12, key
    print("determinism x2: all 9 operators  OK")
    print("-" * 56 + "\nwave1_ops self-test: PASS")
