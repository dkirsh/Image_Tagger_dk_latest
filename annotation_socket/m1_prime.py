"""
annotation_socket.m1_prime — M1' SUFFICIENT-STATISTIC REPLAY (the Layer-2 upgrade Codex specced,
CNFA_DEEPENED_CONSTRUCTION_PLAN_CODEX_2026-07-18.md §"M1' Sufficient-Statistic Replay").

M1 (verify._replay) re-derives the final SCALAR and demands a match — that catches a fabricated or
defaulted number, but NOT a scalar that happens to equal the pipeline output by a DIFFERENT procedure
(a faithful-method failure). M1' additionally emits, per SCORED value, the *sufficient statistics* that
make the scalar defensible, and the checker recomputes those stats from the image bytes and compares a
canonical digest. A scalar-match with a stats-mismatch is demoted; a stats-match with a scalar-mismatch
is RED.

This module is PURE and standalone (no controller/queue import) so it can be unit-tested and dispatched
from verify.py by `audit_class`. It ships two real audit classes first (the two most-used pixel operators):
  - luminance_field  (brightness_variance: 31px local-SD, matches cnfa_algs.attributes)
  - radial_fft       (spectral_slope_deviation / V2 proxy: Hann-windowed radial power slope)
Adding an audit class = add a pure `stats_<class>(gray, **params)` fn + a row in AUDIT_CLASSES.

Determinism: fixed rounding (canonical_json) makes the digest reproducible across machines; that IS the
Mac<->sandbox exact-replay check for these statistics.

Self-test (proves genuine->MATCH, tampered-stat->caught, determinism):
    python3 annotation_socket/m1_prime.py
"""
from __future__ import annotations
import hashlib
import json
from typing import Dict, Optional, Tuple

import numpy as np

STATS_VERSION = "cnfa-m1p-2026-07-19"

# verdict tokens (mirror verify.py's M1_PRIME:* convention)
MATCH = "MATCH"
STATS_MISMATCH = "stats_mismatch"      # scalar ok, sufficient stats differ  -> AMBER/RED
SCALAR_MISMATCH = "scalar_mismatch"    # stats ok, scalar differs            -> RED
MISSING_M1P = "missing_m1_prime"       # no m1_prime block emitted


# ------------------------------------------------------------------ canonicalization + digest
def _canon(obj):
    """Deterministic, machine-independent canonical form: floats rounded to a fixed grid, arrays as
    rounded nested lists with an explicit shape tag, dict keys sorted. This fixed rounding is what makes
    the digest survive Mac<->sandbox float jitter (the cross-environment replay guarantee)."""
    if isinstance(obj, (np.floating, float)):
        # round to 6 sig-figs-ish absolute grid; -0.0 -> 0.0
        r = round(float(obj), 6)
        return 0.0 if r == 0 else r
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.ndarray,)):
        return {"__shape__": list(obj.shape), "__data__": [_canon(x) for x in obj.ravel().tolist()]}
    if isinstance(obj, (list, tuple)):
        return [_canon(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _canon(obj[k]) for k in sorted(obj)}
    return obj


def canonical_json(stats: Dict) -> str:
    return json.dumps(_canon(stats), separators=(",", ":"), ensure_ascii=True, sort_keys=True)


def digest(stats: Dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(stats).encode("ascii")).hexdigest()


# ------------------------------------------------------------------ audit-class statistic computers
def _to_gray(img) -> np.ndarray:
    """BT.601 luminance from an HxWx3 uint8/float array, or pass through a 2-D array. Fixed weights so
    the 'conversion' tag is exact and replayable."""
    a = np.asarray(img, dtype=np.float64)
    if a.ndim == 2:
        return a
    w = np.array([0.299, 0.587, 0.114])
    return a[..., :3] @ w


def stats_luminance_field(img, window: int = 31) -> Dict:
    """Sufficient stats for the brightness_variance operator (scalar = global luminance SD).
    Emits global mean/std, local-SD quantiles, bright-pixel fraction — the pre-scalar signature.
    3-channel input is assumed BGR (cv2.imread order) and flipped so BT601 weights land correctly."""
    a = np.asarray(img)
    g = _to_gray(a[..., ::-1] if a.ndim == 3 else a)
    # local SD via integral-image box filter (deterministic, no cv2 dependency)
    H, W = g.shape
    k = window
    pad = k // 2
    gp = np.pad(g, pad, mode="reflect")                # (H+2pad, W+2pad)

    def _integral(a):
        ii = np.zeros((a.shape[0] + 1, a.shape[1] + 1), dtype=np.float64)
        ii[1:, 1:] = np.cumsum(np.cumsum(a, 0), 1)     # leading zero row/col -> exclusive prefix sums
        return ii

    def _boxsum(integ):
        r0 = np.arange(H); c0 = np.arange(W)
        r1 = r0 + k; c1 = c0 + k                        # window [i, i+k) x [j, j+k) in padded coords
        S = lambda rr, cc: integ[np.ix_(rr, cc)]
        return S(r1, c1) - S(r0, c1) - S(r1, c0) + S(r0, c0)

    n = k * k
    s1 = _boxsum(_integral(gp))
    s2 = _boxsum(_integral(gp * gp))
    local_var = np.maximum(s2 / n - (s1 / n) ** 2, 0.0)
    local_sd = np.sqrt(local_var)
    thr = float(g.mean() + 2.0 * g.std())
    return {
        "audit_class": "luminance_field",
        "conversion": "BT601",
        "window": int(window),
        "global_mean": float(g.mean()),
        "global_std": float(g.std()),
        "local_sd_q": {"p5": float(np.percentile(local_sd, 5)),
                       "p50": float(np.percentile(local_sd, 50)),
                       "p95": float(np.percentile(local_sd, 95)),
                       "p99": float(np.percentile(local_sd, 99))},
        "bright_fraction": float((g > thr).mean()),
        "shape": [int(g.shape[0]), int(g.shape[1])],
    }


def stats_radial_fft(img, n_bins: int = 32, fit_lo: float = 0.10, fit_hi: float = 0.80) -> Dict:
    """Sufficient stats for the spectral_slope_deviation / V2 radial-1/f proxy: Hann-windowed 2-D FFT,
    radially-binned log power, and the log-log slope/intercept/R2 over a fit band. The radial profile
    digest is the faithfulness check — a different procedure that hits the same slope fails here.
    3-channel input is assumed BGR (cv2.imread order)."""
    a = np.asarray(img)
    g = _to_gray(a[..., ::-1] if a.ndim == 3 else a)
    g = g - g.mean()
    H, W = g.shape
    wr = np.hanning(H)[:, None]
    wc = np.hanning(W)[None, :]
    gw = g * wr * wc
    F = np.fft.fftshift(np.fft.fft2(gw))
    P = (np.abs(F) ** 2)
    cy, cx = H / 2.0, W / 2.0
    yy, xx = np.mgrid[0:H, 0:W]
    rad = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    rad = rad / rad.max()
    bins = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(rad.ravel(), bins) - 1, 0, n_bins - 1)
    prof = np.zeros(n_bins)
    cnt = np.zeros(n_bins)
    np.add.at(prof, idx, P.ravel())
    np.add.at(cnt, idx, 1.0)
    prof = prof / np.maximum(cnt, 1.0)
    centers = 0.5 * (bins[:-1] + bins[1:])
    band = (centers >= fit_lo) & (centers <= fit_hi) & (prof > 0)
    x = np.log(centers[band])
    y = np.log(prof[band])
    A = np.vstack([x, np.ones_like(x)]).T
    (slope, intercept), *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ np.array([slope, intercept])
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {
        "audit_class": "radial_fft",
        "conversion": "BT601",
        "window_fn": "hann2d",
        "n_bins": int(n_bins),
        "fit_band": [float(fit_lo), float(fit_hi)],
        "radial_logpower": [float(v) for v in np.log(np.maximum(prof, 1e-12))],
        "slope": float(slope),
        "intercept": float(intercept),
        "r2": float(r2),
        "shape": [int(H), int(W)],
    }


def stats_orientation_hist(img, nbins: int = 18, mag_frac: float = 0.05, min_edge_px: int = 40) -> Dict:
    """Sufficient stats for V13 edge_orientation_entropy — mirrors reliable_attrs._orientation_hist
    EXACTLY (Sobel k=3 on gray01, undirected angles, mask = mag > 0.05*max, 18 bins, magnitude-weighted).
    Below min_edge_px the distribution is undefined (F1 rule): emitted as abstained=True, no histogram."""
    import cv2
    g = _to_gray(img[..., ::-1] if np.asarray(img).ndim == 3 else img) / 255.0
    g = g.astype(np.float32)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    ang = (np.arctan2(gy, gx) % np.pi)
    m = mag > (mag_frac * mag.max() + 1e-9)
    n_edge = int(m.sum())
    out = {"audit_class": "orientation_hist", "conversion": "BT601-on-RGB/255",
           "nbins": int(nbins), "mag_frac": float(mag_frac), "min_edge_px": int(min_edge_px),
           "n_edge_px": n_edge, "shape": [int(g.shape[0]), int(g.shape[1])]}
    if n_edge < min_edge_px:
        out["abstained"] = True
        return out
    idx = np.minimum((ang[m] / np.pi * nbins).astype(int), nbins - 1)
    h = np.bincount(idx, weights=mag[m], minlength=nbins).astype(float)
    h = h / (h.sum() + 1e-12)
    p = h[h > 0]
    out["hist"] = [float(v) for v in h]
    out["entropy_norm"] = float(-(p * np.log(p)).sum() / np.log(nbins))
    return out


def stats_box_count(img, canny_lo: int = 60, canny_hi: int = 160) -> Dict:
    """Sufficient stats for fractal_dimension / V9 — mirrors attributes._boxcount_D_r2 EXACTLY
    (Canny(60,160) on uint8 gray, occupancy at box sizes 2/4/8/16 by max-pooling, log-log polyfit)."""
    import cv2
    g = _to_gray(img[..., ::-1] if np.asarray(img).ndim == 3 else img)
    g8 = np.clip(g, 0, 255).astype(np.uint8)
    e = cv2.Canny(g8, canny_lo, canny_hi)
    out = {"audit_class": "box_count", "conversion": "BT601-on-RGB uint8",
           "canny": [int(canny_lo), int(canny_hi)], "edge_px": int((e > 0).sum()),
           "shape": [int(e.shape[0]), int(e.shape[1])]}
    sizes, counts, series = [], [], []
    for s in (2, 4, 8, 16):
        Ht, Wt = (e.shape[0] // s) * s, (e.shape[1] // s) * s
        if Ht == 0 or Wt == 0:
            continue
        S = int((e[:Ht, :Wt].reshape(Ht // s, s, Wt // s, s).max(axis=(1, 3)) > 0).sum())
        series.append([int(s), S])
        if S > 0:
            sizes.append(np.log(1 / s)); counts.append(np.log(S))
    out["series"] = series
    if (e > 0).sum() < 20 or len(sizes) < 3:
        out["abstained"] = True
        return out
    x, y = np.array(sizes), np.array(counts)
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    ss_res = float(((y - yhat) ** 2).sum()); ss_tot = float(((y - y.mean()) ** 2).sum())
    out["D"] = float(slope)
    out["R2"] = float(max(0.0, min(1.0, 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 1.0)))
    return out


def stats_color_palette(img, k: int = 8) -> Dict:
    """Sufficient stats for color_palette_entropy — mirrors attributes.palette_entropy (Lab kmeans,
    cv2.setRNGSeed(1234), k=8, attempts=2, PP centers). Centers are canonicalized by sorting on
    (L,a,b) and COARSELY rounded (1 decimal; proportions 3) because kmeans float paths may differ
    at fine precision across BLAS builds — the digest is over the rounded, sorted stats."""
    import cv2
    a = np.asarray(img)
    if a.ndim != 3:
        a = np.stack([a] * 3, -1).astype(np.uint8)
    lab = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    cv2.setRNGSeed(1234)
    _, labels, cents = cv2.kmeans(lab, k, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0), 2, cv2.KMEANS_PP_CENTERS)
    p = np.bincount(labels.ravel(), minlength=k) / len(labels)
    H = float(-(p[p > 0] * np.log(p[p > 0])).sum() / np.log(k))
    order = np.lexsort((cents[:, 2], cents[:, 1], cents[:, 0]))
    return {"audit_class": "color_palette", "colorspace": "cv2-BGR2LAB", "k": int(k),
            "seed": 1234, "attempts": 2,
            "centers": [[round(float(c), 1) for c in cents[i]] for i in order],
            "proportions": [round(float(p[i]), 3) for i in order],
            "entropy_norm": round(H, 4),
            "shape": [int(a.shape[0]), int(a.shape[1])]}


def stats_edge_stats(img, canny_lo: int = 60, canny_hi: int = 160) -> Dict:
    """Sufficient stats for edge_clarity_mean — mirrors attributes.edge_clarity EXACTLY
    (Sobel k=3 magnitude on gray01, Canny(60,160) support, mean magnitude on edges)."""
    import cv2
    a = np.asarray(img)
    g = (_to_gray(a[..., ::-1] if a.ndim == 3 else a) / 255.0).astype(np.float32)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)
    edges = cv2.Canny((g * 255).astype(np.uint8), canny_lo, canny_hi) > 0
    n_edge = int(edges.sum())
    return {"audit_class": "edge_stats", "conversion": "BT601-on-RGB/255",
            "canny": [int(canny_lo), int(canny_hi)], "n_edge_px": n_edge,
            "mean_mag_on_edges": float(mag[edges].mean()) if n_edge else 0.0,
            "mag_q": {"p50": float(np.percentile(mag, 50)), "p95": float(np.percentile(mag, 95))},
            "shape": [int(g.shape[0]), int(g.shape[1])]}


def stats_jpeg_tiles(img, quality: int = 75, tile: int = 32) -> Dict:
    """Sufficient stats for processing_load_proxy — mirrors attributes.processing_load (global
    bytes/pixel at JPEG Q75 + 32px tile map; the tile map is digested via its quantiles)."""
    import cv2
    a = np.asarray(img).astype(np.uint8)
    ok, buf = cv2.imencode(".jpg", a, [cv2.IMWRITE_JPEG_QUALITY, quality])
    bpp = len(buf) / (a.shape[0] * a.shape[1])
    tiles = []
    for i in range(0, a.shape[0], tile):
        for j in range(0, a.shape[1], tile):
            t = a[i:i + tile, j:j + tile]
            ok, b = cv2.imencode(".jpg", t, [cv2.IMWRITE_JPEG_QUALITY, quality])
            tiles.append(len(b) / max(t.size, 1))
    tiles = np.array(tiles)
    return {"audit_class": "jpeg_tiles", "quality": int(quality), "tile": int(tile),
            "global_bpp": float(bpp), "n_tiles": int(len(tiles)),
            "tile_bpp_q": {"p5": float(np.percentile(tiles, 5)), "p50": float(np.percentile(tiles, 50)),
                           "p95": float(np.percentile(tiles, 95))},
            "shape": [int(a.shape[0]), int(a.shape[1])]}


def stats_geometry_plan(img) -> Dict:
    """Sufficient stats for the SHARED Tier-B geometry chain (C1-C4/C13/C24/C01/C29 all ride it):
    re-runs vanishing->planes->depth->plan->VGA deterministically and digests the results. A plan
    metric whose grid_hash or VGA quantiles differ from this recompute was not produced by the
    declared chain. EXPENSIVE (full geometry recompute) — bound to ONE representative predicate."""
    import cnfa_algs as ca
    from cnfa_algs.plan import infer_plan_from_image, FREE as _FREE
    from cnfa_algs import space_syntax as ss
    from annotation_socket import derivation as _D
    a = np.asarray(img)
    vx, vy, vconf = ca.estimate_vanishing_point(a)
    planes, pconf = ca.segment_planes(a, (vx, vy))
    Z, _, dconf = ca.DepthProvider()(a, planes, (vx, vy))
    pg = infer_plan_from_image(a, planes, Z)
    vga = ss.vga_metrics(pg, stride=3)
    return {"audit_class": "geometry_plan",
            "vanishing_point": [round(float(vx), 1), round(float(vy), 1)],
            "grid_hash": _D.grid_hash(pg.grid),
            "free_cells": int((pg.grid == _FREE).sum()),
            "cell_m": round(float(pg.cell_m), 4),
            "integration_norm": float(vga["extras"]["integration_norm"]),
            "connectivity_norm": float(vga["extras"]["connectivity_norm"]),
            "shape": [int(a.shape[0]), int(a.shape[1])]}


# ------------------------------------------------------------------ CC-2 additions (2026-07-19)
def stats_ssim_map(img, tile: int = 2) -> Dict:
    """Sufficient stats for symmetry_score_horizontal: |g - fliplr(g)| asymmetry map digested as
    global mean/std + a tile-grid of means. Computed DIRECTLY (no operator import) — the mirror
    diff is the method's core, so this is an independent recomputation of its pre-scalar stage."""
    a = np.asarray(img)
    g = _to_gray(a[..., ::-1] if a.ndim == 3 else a)
    d = np.abs(g - g[:, ::-1])
    H, W = d.shape
    ty, tx = max(1, H // (H // (tile + 1) + 1)), 0  # noqa — grid below
    grid = [[round(float(d[i * H // 2:(i + 1) * H // 2, j * W // 2:(j + 1) * W // 2].mean()), 6)
             for j in range(2)] for i in range(2)]
    return {"audit_class": "ssim_map", "diff_mean": round(float(d.mean()), 6),
            "diff_std": round(float(d.std()), 6), "quadrant_means": grid,
            "shape": [int(H), int(W)]}


# Operator-extract audit classes: the sufficient statistic IS the operator's own declared
# pre-scalar signature (scalar + selected extras), recomputed from image bytes at replay.
# BOUNDARY (stated per RULE 0 discipline): this catches TAMPERED, STALE, or WRONG-PIPELINE
# scores — it can NOT catch an algorithmic bug, because producer and checker share the operator
# code. Algorithm correctness is the adversarial (Codex/panel) layer's job, not M1's.
_OPX = {
    # op name -> (import path, callable, extras keys kept in the digest, zone condenser?)
    "feature_congestion": ("cnfa_algs.faithful_clutter", "feature_congestion_faithful",
                           ["fc_raw", "layer_means", "combination", "params"], None),
    "subband_entropy":    ("cnfa_algs.faithful_clutter", "subband_entropy_faithful",
                           ["se_raw_nats", "params"], None),
    "complexity_partition": ("cnfa_algs.complexity_partition", "complexity_partition",
                             ["n_zones", "area_fracs", "tile_px"], "zones"),
    "texture_density":    ("cnfa_algs.wave1_ops", "texture_density",
                           ["raw_mean_range", "structure_frac", "fullscale"], None),
    "contour_angularity": ("cnfa_algs.reliable_attrs", "contour_angularity_index",
                           ["corner_density", "curve_fraction"], None),
    "shadow_softness":    ("cnfa_algs.wave1_ops", "shadow_softness",
                           ["penumbra_px", "penumbra_frac_diag", "n_edges",
                            "n_rejected_material"], None),
    # --- S1 / A5 M1' coverage batch (2026-07-21): the 13 image-only pixel operators ---
    # (single-arg fn(img)->AttributeResult). Keys = the op's declared numeric pre-scalar
    # signature + fixed constants; variable-length detail lists (patches/pools/zones) are
    # deliberately excluded to keep the digest cross-env stable. glare_risk/landmark_salience
    # carry no extras -> scalar-only digest (still tamper/stale/abstain-auditable).
    "glare_risk":         ("cnfa_algs.attributes", "glare_risk", [], None),
    "landmark_salience":  ("cnfa_algs.attributes", "landmark_salience", [], None),
    "proto_object_count": ("cnfa_algs.clutter_stack", "proto_object_count",
                           ["count", "density_per_mpx", "size_entropy", "n_regions_raw",
                            "constants"], None),
    "multiscale_gradient": ("cnfa_algs.clutter_stack", "multiscale_gradient",
                            ["per_scale", "raw_mean", "scales", "fullscale"], None),
    "multiscale_unique_color": ("cnfa_algs.clutter_stack", "multiscale_unique_color",
                                ["per_config", "spatial_scales", "bins", "raw_mean",
                                 "fullscale"], None),
    "luminance_gradient_contrast": ("cnfa_algs.wave1_ops", "luminance_gradient_contrast",
                                    ["mean_grad_diagu", "coherence", "contrast_ratio_p95_p5",
                                     "sigma_px", "fullscale_grad"], None),
    "sun_patch_geometry": ("cnfa_algs.wave1_ops", "sun_patch_geometry",
                           ["n_patches", "thr"], None),
    "evening_ambience":   ("cnfa_algs.wave1_ops", "evening_ambience",
                           ["cct_proxy_K", "mean_lum", "lum_skew", "clipped_frac",
                            "awb_unknown", "weights", "warm_below_K", "dim_below"], None),
    "temperature_mismatch": ("cnfa_algs.wave1_ops", "temperature_mismatch",
                             ["clusters_cct_K", "proportions", "worst_pair",
                              "fullscale_mired", "awb_unknown"], None),
    "spotlight_pool_geometry": ("cnfa_algs.wave1_ops", "spotlight_pool_geometry",
                                ["n_pools", "tophat_thr", "se_radius_px"], None),
    "dark_zone_map":      ("cnfa_algs.wave1_ops", "dark_zone_map",
                           ["n_zones", "rel_thr", "global_median"], None),
    "orderliness_alignment": ("cnfa_algs.wave1_ops", "orderliness_alignment",
                              ["n_segments", "alignment_2mode", "modes_adjacent",
                               "mode_bin_separation", "entropy_norm", "nbins", "mode_bins",
                               "total_length_px"], None),
    "verticality_cues":   ("cnfa_algs.wave2_geometry", "verticality_cues",
                           ["n_segments", "n_vertical", "n_long_vertical_runs",
                            "roll_est_deg", "constants"], None),
}


def stats_operator_extract(img, op: str = "") -> Dict:
    """Generic CC-2 computer: run the named operator on the (already loader-normalized) image and
    digest scalar + declared extras keys. Abstention digests as {'abstained': True} — a record
    claiming SCORED whose replay abstains is RED, and vice versa."""
    import importlib
    mod_path, fn_name, keys, condense = _OPX[op]
    fn = getattr(importlib.import_module(mod_path), fn_name)
    r = fn(np.asarray(img))
    if r.scalar is None:
        return {"audit_class": f"opx:{op}", "abstained": True,
                "method_head": (r.method or "")[:80]}
    ex = getattr(r, "extras", None) or {}
    st: Dict = {"audit_class": f"opx:{op}", "scalar": round(float(r.scalar), 6)}
    for k in keys:
        if k in ex:
            st[k] = ex[k]
    if condense == "zones":
        st["zones_condensed"] = [[z["class"],
                                  None if z.get("D") is None else round(float(z["D"]), 4),
                                  round(float(z["area_frac"]), 4)]
                                 for z in ex.get("zones", [])]
    return st


AUDIT_CLASSES = {
    "luminance_field": stats_luminance_field,
    "radial_fft": stats_radial_fft,
    "orientation_hist": stats_orientation_hist,
    "box_count": stats_box_count,
    "color_palette": stats_color_palette,
    "edge_stats": stats_edge_stats,
    "jpeg_tiles": stats_jpeg_tiles,
    "geometry_plan": stats_geometry_plan,
    "ssim_map": stats_ssim_map,
    "operator_extract": stats_operator_extract,
}

# predicate -> (audit_class, image_prep) producer/checker binding. image_prep names the array the
# stats fn expects: 'bgr' = as loaded by cv2.imread (the stats fns handle conversion internally).
# Shared by annotator (emit) and verify (replay) so the two sides cannot drift apart.
M1P_BINDINGS = {
    "cnfa.light.brightness_variance":        ("luminance_field", {}),
    "cnfa.fluency.spectral_slope_deviation": ("radial_fft", {}),
    "cnfa.fluency.edge_orientation_entropy": ("orientation_hist", {}),
    "cnfa.fractal_dimension":                ("box_count", {}),
    "cnfa.fluency.color_palette_entropy":    ("color_palette", {}),
    "cnfa.fluency.edge_clarity_mean":        ("edge_stats", {}),
    "cnfa.fluency.processing_load_proxy":    ("jpeg_tiles", {}),
    # geometry chain digested ONCE, bound to C1 (the chain's first consumer); every other plan
    # metric shares the same upstream, so one binding audits the substrate without 8x recompute
    "C1.visual_integration":                 ("geometry_plan", {}),
    # CC-2 (2026-07-19): owed classes. operator_extract digests the operator's own pre-scalar
    # signature (tamper/staleness audit; algorithm correctness stays with the adversarial layer)
    "cnfa.fluency.symmetry_score_horizontal": ("ssim_map", {}),
    "cnfa.fluency.feature_congestion":       ("operator_extract", {"op": "feature_congestion"}),
    "cnfa.fluency.subband_entropy":          ("operator_extract", {"op": "subband_entropy"}),
    "cnfa.fluency.complexity_partition":     ("operator_extract", {"op": "complexity_partition"}),
    "cnfa.material.texture_density":         ("operator_extract", {"op": "texture_density"}),
    "cnfa.geometry.contour_angularity":      ("operator_extract", {"op": "contour_angularity"}),
    "cnfa.light.shadow_softness":            ("operator_extract", {"op": "shadow_softness"}),
    # --- S1 / A5 M1' coverage batch (2026-07-21): 13 image-only pixel operators ---
    "glare-risk":                            ("operator_extract", {"op": "glare_risk"}),
    "cnfa.cognitive.landmark_salience":      ("operator_extract", {"op": "landmark_salience"}),
    "cnfa.fluency.proto_object_count":       ("operator_extract", {"op": "proto_object_count"}),
    "cnfa.fluency.multiscale_gradient":      ("operator_extract", {"op": "multiscale_gradient"}),
    "cnfa.fluency.multiscale_unique_color":  ("operator_extract", {"op": "multiscale_unique_color"}),
    "cnfa.light.luminance_gradient_contrast":("operator_extract", {"op": "luminance_gradient_contrast"}),
    "cnfa.light.sun_patch_geometry":         ("operator_extract", {"op": "sun_patch_geometry"}),
    "cnfa.light.evening_ambience":           ("operator_extract", {"op": "evening_ambience"}),
    "cnfa.light.temperature_mismatch":       ("operator_extract", {"op": "temperature_mismatch"}),
    "cnfa.light.spotlight_pool_geometry":    ("operator_extract", {"op": "spotlight_pool_geometry"}),
    "cnfa.light.dark_zone_map":              ("operator_extract", {"op": "dark_zone_map"}),
    "cnfa.geometry.orderliness_alignment":   ("operator_extract", {"op": "orderliness_alignment"}),
    "cnfa.geometry.verticality_cues":        ("operator_extract", {"op": "verticality_cues"}),
}


# ------------------------------------------------------------------ shared loader
def load_for_m1p(image_path: str):
    """EXACTLY the annotator's load+resize pipeline (cv2.imread BGR, downscale to max-dim 900 with
    INTER_AREA). Producer and checker must see identical pixels; this is the single shared definition
    the checker uses. If annotate_image's loader ever changes, this must change with it — the wiring
    test (same-image digest equality) catches drift immediately."""
    import cv2
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"unreadable image: {image_path}")
    scale = 900 / max(img.shape[:2])
    if scale < 1:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return img


# ------------------------------------------------------------------ emit + replay
def emit(audit_class: str, img, **params) -> Dict:
    """Producer side: compute the sufficient stats and package the M1' block for AttributeResult.extras."""
    if audit_class not in AUDIT_CLASSES:
        raise KeyError(f"unknown audit_class {audit_class!r}; known: {sorted(AUDIT_CLASSES)}")
    stats = AUDIT_CLASSES[audit_class](img, **params)
    return {"audit_class": audit_class, "stats_version": STATS_VERSION,
            "stats": stats, "digest": digest(stats)}


def replay(m1p: Optional[Dict], img, scalar: Optional[float] = None,
           recomputed_scalar: Optional[float] = None, tol: float = 0.02,
           **params) -> Tuple[str, Dict]:
    """Checker side. Recompute the stats from image bytes, compare the canonical digest, and (if given)
    compare the scalar. Returns (verdict_token, detail). Pure over its inputs + the recompute."""
    if not m1p:
        return MISSING_M1P, {"reason": "no m1_prime block emitted"}
    ac = m1p.get("audit_class")
    if ac not in AUDIT_CLASSES:
        return STATS_MISMATCH, {"reason": f"unknown audit_class {ac!r}"}
    fresh = AUDIT_CLASSES[ac](img, **params)
    fresh_digest = digest(fresh)
    claimed_digest = m1p.get("digest")
    stats_ok = (fresh_digest == claimed_digest)
    # also verify the claimed digest actually matches the claimed stats (anti-forgery of the digest field)
    self_consistent = (claimed_digest == digest(m1p.get("stats", {})))
    scalar_ok = True
    if scalar is not None and recomputed_scalar is not None:
        scalar_ok = abs(float(scalar) - float(recomputed_scalar)) <= tol
    detail = {"audit_class": ac, "claimed_digest": claimed_digest, "fresh_digest": fresh_digest,
              "digest_self_consistent": self_consistent, "stats_ok": stats_ok, "scalar_ok": scalar_ok}
    if not scalar_ok:
        return SCALAR_MISMATCH, detail
    if not stats_ok:
        return STATS_MISMATCH, detail
    return MATCH, detail


# ------------------------------------------------------------------ self-test
if __name__ == "__main__":
    print("m1_prime self-test\n" + "-" * 48)
    rng = np.random.RandomState(0)
    # a deterministic synthetic image with structure (gradient + a bright patch + texture)
    H, W = 128, 160
    yy, xx = np.mgrid[0:H, 0:W]
    base = 40 + 120 * (xx / W)
    base[20:50, 100:140] = 250.0                       # bright patch
    base = base + 15 * np.sin(xx / 3.0) * np.cos(yy / 4.0)
    img = np.clip(np.stack([base, base * 0.9, base * 0.8], -1), 0, 255).astype(np.uint8)

    # --- _canon rounding-boundary lock (S0.4): the 6-decimal grid is a threshold; prove it ---
    assert digest({"v": 0.1234567}) == digest({"v": 0.123457}), "1e-7 difference must collapse"
    assert digest({"v": 0.12345}) != digest({"v": 0.12346}), "1e-5 difference must distinguish"
    assert _canon(-0.0) == 0.0 and canonical_json({"a": np.float64(1.5)}) == '{"a":1.5}'
    print("  _canon boundary: 1e-7 collapses, 1e-5 distinguishes, -0.0 normalized  OK")

    for ac in ("luminance_field", "radial_fft", "orientation_hist", "box_count", "color_palette"):
        m = emit(ac, img)
        # 1. genuine record replays MATCH
        v, d = replay(m, img)
        assert v == MATCH, (ac, v, d)
        # 2. determinism: recompute digest twice
        assert digest(AUDIT_CLASSES[ac](img)) == m["digest"]
        # 3. a TAMPERED statistic (keep the old digest) is caught as stats_mismatch
        tampered = json.loads(json.dumps(m))
        tamper_key = {"luminance_field": "global_std", "radial_fft": "slope",
                      "orientation_hist": "n_edge_px", "box_count": "edge_px",
                      "color_palette": "entropy_norm"}[ac]
        tampered["stats"][tamper_key] = float(tampered["stats"][tamper_key]) + 5.0
        # attacker forges a matching digest for the tampered stats -> caught because RECOMPUTE differs
        tampered["digest"] = digest(tampered["stats"])
        v2, d2 = replay(tampered, img)
        assert v2 == STATS_MISMATCH, (ac, "tamper not caught", v2, d2)
        # 4. a DIFFERENT image must not replay-match the original stats
        v3, _ = replay(m, np.roll(img, 7, axis=1))
        assert v3 == STATS_MISMATCH, (ac, "different image matched!", v3)
        print(f"  {ac:16s}  genuine->MATCH  tamper->caught  diff-image->caught   "
              f"digest={m['digest'][:14]}...")

    # scalar path: stats ok but scalar disagrees -> RED (scalar_mismatch)
    m = emit("luminance_field", img)
    v, d = replay(m, img, scalar=10.0, recomputed_scalar=99.0)
    assert v == SCALAR_MISMATCH, (v, d)
    print("  scalar disagreement (stats ok) -> scalar_mismatch  OK")
    # missing block
    assert replay(None, img)[0] == MISSING_M1P
    print("  missing m1_prime block -> flagged  OK")
    print("-" * 48 + "\nm1_prime self-test: PASS")
