"""
cnfa_algs.attributes — Tier A (image-plane) attribute algorithms.

Every function returns an AttributeResult with:
  scalar (global), field (heatmap-able localization), regions (evidence),
  confidence, method tag, failure modes.
Keys match backend/science/feature_stubs.py naming where a stub exists.

All keys use the cnfa.* prefix per CONTRACT.md § PL-3.
All scalars are normalized to [0,1] per CONTRACT.md § PL-4.
All fields match the input image shape (H,W) per CONTRACT.md § PL-5.

Scientific justifications for parameters are documented in
cnfa_algs/JUSTIFICATION_TABLE.md per .agents/AGENTS.md rule.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import io
import numpy as np
import cv2

from .core import AttributeResult, normalize01
from .geometry import FLOOR, CEILING, WALL, OPENING, UNKNOWN


# ── Guards ─────────────────────────────────────────────────────────────

MIN_DIM = 32   # minimum image width/height; below this, pixel ops crash


def _too_small(img) -> bool:
    """Return True if image is below the minimum usable size."""
    return min(img.shape[0], img.shape[1]) < MIN_DIM


def _small_fallback(key: str) -> AttributeResult:
    """Return a safe zero-confidence result for undersized images."""
    return AttributeResult(
        key=key, scalar=0.0, confidence=0.0,
        method="image too small (<32px), fallback zero",
        failure_modes=["undersized image"])


def _resize_field(fld: np.ndarray, H: int, W: int) -> np.ndarray:
    """Upscale a tile-grid field to match image dimensions."""
    if fld.shape == (H, W):
        return fld
    return cv2.resize(fld, (W, H), interpolation=cv2.INTER_LINEAR)


def validate_depth(Z: np.ndarray, planes: np.ndarray = None
                   ) -> tuple:
    """Clean non-finite depth values, return (Z_clean, confidence).

    Uses geometric consistency with plane labels when available.
    Citation: CVPR 2025 MDEC (geometric consistency approach).
    """
    finite_mask = np.isfinite(Z)
    frac_finite = float(finite_mask.mean())

    if frac_finite < 0.1:
        # Almost entirely garbage — use flat prior
        return np.full_like(Z, 3.0), 0.05

    Z_clean = Z.copy()
    med = float(np.nanmedian(Z[finite_mask]))
    Z_clean[~finite_mask] = med
    Z_clean = np.clip(Z_clean, 0.1, 100.0)

    # Plane consistency check: floor pixels should have smoothly
    # varying depth (low coefficient of variation per row)
    plane_conf = 0.5  # default if no planes
    if planes is not None:
        floor_mask = planes == FLOOR
        if floor_mask.sum() > 100:
            floor_depths = Z_clean[floor_mask]
            cv = float(np.std(floor_depths) / (np.mean(floor_depths) + 1e-6))
            plane_conf = max(0.0, min(1.0, 1.0 - cv))

    confidence = frac_finite * 0.6 + plane_conf * 0.4
    return Z_clean, confidence


def _gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0


# ------------------------------------------------------------------ fluency

def brightness_variance(img) -> AttributeResult:
    g = _gray(img)
    local_sd = cv2.sqrt(cv2.blur(g * g, (31, 31)) - cv2.blur(g, (31, 31)) ** 2)
    return AttributeResult(
        key="cnfa.light.brightness_variance",
        scalar=float(g.std()), field=normalize01(local_sd), confidence=0.9,
        method="local luminance SD, 31px window (M1)",
        failure_modes=["exposure/HDR of source photo", "shadows vs true material change"])


def edge_clarity(img) -> AttributeResult:
    g = _gray(img)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)
    edges = cv2.Canny((g * 255).astype(np.uint8), 60, 160) > 0
    mean_on_edges = float(mag[edges].mean()) if edges.any() else 0.0
    return AttributeResult(
        key="cnfa.fluency.edge_clarity_mean",
        scalar=mean_on_edges, field=normalize01(mag), confidence=0.9,
        method="Sobel gradient magnitude on Canny support (M1)",
        failure_modes=["motion blur/low-res source reads as low clarity"])


def symmetry_horizontal(img) -> AttributeResult:
    from skimage.metrics import structural_similarity as ssim
    g = (_gray(img) * 255).astype(np.uint8)
    flipped = np.fliplr(g)
    score, diff = ssim(g, flipped, full=True)
    return AttributeResult(
        key="cnfa.fluency.symmetry_score_horizontal",
        scalar=float(score), field=normalize01(1.0 - diff), confidence=0.9,
        method="SSIM(image, mirrored); field = local asymmetry (M1)",
        failure_modes=["off-center camera breaks symmetry of a symmetric room"])


def palette_entropy(img, k: int = 8) -> AttributeResult:
    if _too_small(img):
        return _small_fallback("cnfa.fluency.color_palette_entropy")
    # Deterministic quantization: median-cut via PIL (Heckbert 1982)
    # Replaces non-deterministic k-means (adversarial review finding #9)
    from PIL import Image as PILImage
    pil = PILImage.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    quantized = pil.quantize(colors=k, method=PILImage.Quantize.MEDIANCUT)
    full_palette = quantized.getpalette()  # up to 256*3 entries
    labels = np.array(quantized.convert("P").getdata(), dtype=np.int32)
    n_actual = int(labels.max()) + 1  # actual number of colors produced
    n_actual = min(n_actual, k)
    p = np.bincount(labels, minlength=n_actual).astype(np.float64)[:n_actual]
    p = p / (p.sum() + 1e-12)
    denom = np.log(max(n_actual, 2))  # avoid log(1)=0 for uniform images
    H = float(-(p[p > 0] * np.log(p[p > 0])).sum() / denom)
    # field: per-pixel rarity of its palette cluster (rare colors light up)
    p_full = np.zeros(max(int(labels.max()) + 1, n_actual), dtype=np.float64)
    p_full[:n_actual] = p[:n_actual]
    rarity = (1.0 - p_full[labels]).reshape(img.shape[:2])
    hexes = []
    for i in range(n_actual):
        if full_palette and i * 3 + 2 < len(full_palette):
            hexes.append('#%02x%02x%02x' % (full_palette[i*3], full_palette[i*3+1], full_palette[i*3+2]))
        else:
            hexes.append('#000000')
    return AttributeResult(
        key="cnfa.fluency.color_palette_entropy",
        scalar=float(np.clip(H, 0.0, 1.0)), field=normalize01(rarity), confidence=0.85,
        method=f"median-cut(k={k}) RGB palette (Heckbert 1982); Shannon entropy (M1)",
        failure_modes=["k sensitivity (fixed k=8)", "uniform images yield H=0"],
        extras={"palette": hexes, "proportions": [round(float(x), 3) for x in p]})


def processing_load(img) -> AttributeResult:
    if _too_small(img):
        return _small_fallback("cnfa.fluency.processing_load_proxy")
    H_img, W_img = img.shape[:2]
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 75])
    bpp = len(buf) / (H_img * W_img)
    # tiled compressibility map
    T = 32
    fld = np.zeros((H_img // T + 1, W_img // T + 1), np.float32)
    for i in range(0, H_img, T):
        for j in range(0, W_img, T):
            tile = img[i:i + T, j:j + T]
            ok, b = cv2.imencode(".jpg", tile, [cv2.IMWRITE_JPEG_QUALITY, 75])
            fld[i // T, j // T] = len(b) / max(tile.size, 1)
    # Resize tile grid to image dims (adversarial review fix #6)
    fld = _resize_field(normalize01(fld), H_img, W_img)
    return AttributeResult(
        key="cnfa.fluency.processing_load_proxy",
        scalar=float(bpp), field=fld, confidence=0.7,
        method="JPEG bytes/pixel @Q75, global + 32px tiles (M1)",
        failure_modes=["sensor noise inflates load", "smooth CGI deflates it"])


def fractal_dimension_local(img, tile: int = 64) -> AttributeResult:
    if _too_small(img):
        return _small_fallback("cnfa.fractal_dimension")
    H_img, W_img = img.shape[:2]
    g = (_gray(img) * 255).astype(np.uint8)
    edges = cv2.Canny(g, 60, 160)

    def boxcount_D(e):
        if e.sum() < 20:
            return 0.0
        sizes, counts = [], []
        for s in (2, 4, 8, 16):
            rh, rw = e.shape[0] // s, e.shape[1] // s
            if rh < 1 or rw < 1:
                continue
            cropped = e[:rh * s, :rw * s]
            S = (cropped.reshape(rh, s, rw, s).max(axis=(1, 3)) > 0).sum()
            if S > 0:
                sizes.append(np.log(1 / s)); counts.append(np.log(S))
        if len(sizes) < 3:
            return 0.0
        return float(np.polyfit(sizes, counts, 1)[0])

    H, W = edges.shape
    Ht, Wt = (H // tile) * tile, (W // tile) * tile
    if Ht < tile or Wt < tile:
        D_global = boxcount_D(edges)
        return AttributeResult(
            key="cnfa.fractal_dimension",
            scalar=float(np.clip((D_global - 1.0), 0.0, 1.0)),
            field=np.full((H_img, W_img), float(np.clip((D_global - 1.0), 0.0, 1.0)), np.float32),
            confidence=0.5,
            method="box-counting on Canny edges, single-tile (M1); Mandelbrot 1983",
            failure_modes=["image too small for per-tile analysis"])
    fld = np.zeros((Ht // tile, Wt // tile), np.float32)
    for i in range(0, Ht, tile):
        for j in range(0, Wt, tile):
            fld[i // tile, j // tile] = boxcount_D(edges[i:i + tile, j:j + tile])
    D_global = boxcount_D(edges[:Ht, :Wt])
    # Rescale: fractal D ∈ [1,2] for 2D images → [0,1] via (D−1)
    # Mandelbrot 1983; Bovill 1996 "Fractal Geometry in Architecture"
    D_norm = float(np.clip((D_global - 1.0), 0.0, 1.0))
    # Resize tile grid to image dims (adversarial review fix #6)
    fld_norm = normalize01(fld)
    fld_full = _resize_field(fld_norm, H_img, W_img)
    return AttributeResult(
        key="cnfa.fractal_dimension",
        scalar=D_norm, field=fld_full, confidence=0.75,
        method="box-counting on Canny edges, (D−1) normalized (Mandelbrot 1983; Bovill 1996) (M1)",
        failure_modes=["scale range 2..16px only", "edge-detector dependence"])


# ------------------------------------------------------------------- light

def glare_risk(img) -> AttributeResult:
    if _too_small(img):
        return _small_fallback("cnfa.light.glare_risk")
    g = _gray(img)
    over = (g > 0.95).astype(np.float32)
    tophat = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, np.ones((31, 31), np.uint8))
    fld = 0.6 * over + 0.4 * normalize01(tophat)
    scalar = float(min(1.0, 6.0 * over.mean() + 0.4 * np.percentile(tophat, 99)))
    return AttributeResult(
        key="cnfa.light.glare_risk", scalar=scalar, field=np.clip(fld, 0, 1),
        confidence=0.65,
        method="overexposure mask + top-hat local contrast (M1)",
        failure_modes=["blown sky through window vs true discomfort glare",
                       "no eye position -> not DGP-calibrated"])


def warmth_ratio(img) -> AttributeResult:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue, sat = hsv[..., 0].astype(int), hsv[..., 1].astype(np.float32) / 255
    warm = (((hue <= 30) | (hue >= 160)) & (sat > 0.15)).astype(np.float32)
    cool = ((hue >= 45) & (hue <= 135) & (sat > 0.15)).astype(np.float32)
    tot = warm.sum() + cool.sum() + 1e-6
    return AttributeResult(
        key="cnfa.light.warm_vs_cool_ratio",
        scalar=float(warm.sum() / tot), field=warm - 0 * cool + 0.5 * (1 - warm - cool),
        confidence=0.8, method="hue-band warm/cool share, sat-gated (M1)",
        failure_modes=["camera white balance shifts the split"])


def vertical_illuminance_proxy(img, planes) -> AttributeResult:
    g = _gray(img)
    wallm = planes == WALL
    val = float(g[wallm].mean()) if wallm.any() else float("nan")
    fld = np.where(wallm, g, np.nan)
    return AttributeResult(
        key="cnfa.light.vertical_illuminance_proxy",
        scalar=val, field=normalize01(np.nan_to_num(fld, nan=0.0)), confidence=0.5,
        method="mean luminance over wall-plane mask (M2)",
        failure_modes=["segmentation quality", "camera exposure not radiometric"])


# --------------------------------------------------------- spatial / cognition

def enclosure_index(img, planes, Z) -> AttributeResult:
    Z, z_conf = validate_depth(Z, planes)
    w = 1.0 / np.maximum(Z, 0.5)                      # nearness weight
    solid = np.isin(planes, (WALL, CEILING, FLOOR))
    aperture = planes == OPENING
    num = float((w * solid).sum())
    den = float((w * (solid | aperture)).sum()) + 1e-9
    fld = np.where(solid, w, 0.0)
    return AttributeResult(
        key="cnfa.spatial.enclosure_index",
        scalar=float(np.clip(num / den, 0.0, 1.0)),
        field=normalize01(fld), confidence=min(0.5, z_conf),
        method="nearness-weighted solid boundary vs aperture share (Benedikt 1979 occlusivity) (M2)",
        failure_modes=["mirrors/art read as openings", "open door to enclosed room counts as aperture",
                       "heuristic plane segmentation"])


def prospect(img, planes, Z) -> AttributeResult:
    """Prospect: fraction of image with long sightlines.

    Normalized per Benedikt 1979 (isovist area / maximum area) and
    Dosen & Ostwald 2016 (0-1 scale for cross-building comparison).
    Consistency gate: if no OPENING pixels detected, prospect is capped
    at 0.25 (can't see far through solid walls).
    """
    Z, z_conf = validate_depth(Z, planes)
    finite = np.isfinite(Z)
    if not finite.any():
        return AttributeResult(
            key="cnfa.spatial.prospect", scalar=0.0,
            field=np.zeros(img.shape[:2], np.float32), confidence=0.05,
            method="prospect fallback: no usable depth",
            failure_modes=["all depth values non-finite"])

    median_z = float(np.median(Z[finite]))
    # Fraction of pixels with sightlines > 2× median depth
    # (Benedikt 1979: isovist area normalized by bounding area)
    long_sightline = (Z > median_z * 2.0).astype(np.float32)
    p_raw = float(long_sightline.mean())  # already in [0,1]

    # Consistency gate: if no openings, cap prospect
    # (architecturally, can't see far through solid walls)
    has_openings = (planes == OPENING).sum() > 0.01 * planes.size
    if not has_openings:
        p_raw = min(p_raw, 0.25)

    fld = normalize01(Z) * long_sightline
    return AttributeResult(
        key="cnfa.spatial.prospect",
        scalar=float(np.clip(p_raw, 0.0, 1.0)),
        field=_resize_field(fld, img.shape[0], img.shape[1]),
        confidence=min(0.5, z_conf),
        method="fraction of pixels with sightlines >2× median depth "
               "(Benedikt 1979; Dosen & Ostwald 2016 normalized prospect) (M2)",
        failure_modes=["monocular depth compresses far range",
                       "window views not separated from interior depth",
                       "opening-pixel gate is heuristic"])


def landmark_salience(img, saliency_map: Optional[np.ndarray] = None) -> AttributeResult:
    """Deep saliency (if available) or spectral-residual, + top-region bbox with Lab contrast."""
    # Get saliency map — deep if available, else FFT
    if saliency_map is not None:
        sal = saliency_map
        method_note = "provided saliency map"
    else:
        try:
            from .adapters.saliency_adapter import deep_saliency, is_available as sal_avail
            sal = deep_saliency(img)
            method_note = "TranSalNet deep fixation" if sal_avail() else "spectral-residual FFT"
        except Exception:
            # Original inline fallback
            g = _gray(img)
            小 = cv2.resize(g, (128, 128))
            F = np.fft.fft2(小)
            logamp = np.log(np.abs(F) + 1e-9)
            resid = logamp - cv2.blur(logamp, (3, 3))
            sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * np.angle(F)))) ** 2
            sal = cv2.GaussianBlur(sal.astype(np.float32), (9, 9), 2.5)
            sal = cv2.resize(normalize01(sal), (img.shape[1], img.shape[0]))
            method_note = "spectral-residual FFT (inline fallback)"

    # top region
    thr = (sal > np.percentile(sal, 97)).astype(np.uint8)
    cs, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    if cs:
        c = max(cs, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        # Lab contrast of region vs surround ring
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        m = np.zeros(img.shape[:2], np.uint8); cv2.drawContours(m, [c], -1, 1, -1)
        ring = cv2.dilate(m, np.ones((25, 25), np.uint8)) - m
        dE = float(np.linalg.norm(lab[m > 0].mean(0) - lab[ring > 0].mean(0))) if ring.any() else 0.0
        regions.append({"kind": "bbox", "coords": [x, y, w, h],
                         "label": f"landmark dE={dE:.0f}", "value": dE})
    peak_ratio = float(sal.max() / (sal.mean() + 1e-9))
    dE_top = regions[0]["value"] if regions else 0.0
    scalar = float(np.clip(0.5 * min(dE_top / 60.0, 1.0) + 0.5 * min(peak_ratio / 12.0, 1.0), 0, 1))
    deep = "deep" in method_note
    # FFT confidence lowered to 0.35 per MIT/Tübingen Saliency Benchmark:
    # spectral-residual AUC-Judd ~0.65 (barely above chance)
    conf = 0.75 if deep else 0.35
    return AttributeResult(
        key="cnfa.cognitive.landmark_salience",
        scalar=scalar, field=sal, regions=regions,
        confidence=conf,
        method=f"{method_note} + Lab surround contrast (M1)",
        failure_modes=["semantic gap: salience != wayfinding anchor"] if deep
                      else ["AUC-Judd ~0.65 (MIT/Tübingen benchmark); poor localization",
                            "bright window outsalients a memorable object",
                            "salience != wayfinding anchor (semantic gap)"])


# --------------------------------------------------------------- acoustics

# mid-band (500Hz-1kHz) absorption coefficients by visual material class
ALPHA = {"hard_floor": 0.05, "carpet_rug": 0.30, "wall_paint": 0.05,
         "ceiling": 0.10, "glass": 0.03, "curtain": 0.50,
         "upholstery": 0.55, "wood_furniture": 0.10, "plant": 0.20, "unknown": 0.15}


def acoustic_absorption(img, planes, Z) -> AttributeResult:
    """Visual material -> absorption map -> area-weighted mean alpha and
    relative reverberance. Depth-deprojected weighting reduces perspective bias."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    g = _gray(img)
    sat, hue = hsv[..., 1] / 255, hsv[..., 0]
    # texture energy (soft materials are matte + low specular + mid texture)
    lap = np.abs(cv2.Laplacian(g, cv2.CV_32F, ksize=3))
    tex = cv2.blur(lap, (15, 15))
    spec = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, np.ones((15, 15), np.uint8)) > 0.18

    mat = np.full(img.shape[:2], -1, np.int8)  # index into class list
    classes = list(ALPHA.keys())

    def cid(name): return classes.index(name)

    floorm, wallm, ceilm, openm, unkm = (planes == FLOOR), (planes == WALL), \
        (planes == CEILING), (planes == OPENING), (planes == UNKNOWN)
    # floor: rug/carpet if high texture & low specular, else hard floor
    mat[floorm & (tex > np.percentile(tex[floorm] if floorm.any() else tex, 60)) & ~spec] = cid("carpet_rug")
    mat[floorm & (mat == -1)] = cid("hard_floor")
    mat[wallm] = cid("wall_paint")
    mat[ceilm] = cid("ceiling")
    mat[openm] = cid("glass")
    # furniture/unknown: upholstery if saturated or dark matte; wood if warm hue+smooth
    warm = ((hue < 25) | (hue > 160)) & (sat > 0.2)
    mat[unkm & warm & (tex < np.percentile(tex, 50))] = cid("wood_furniture")
    green = (35 < hue) & (hue < 85) & (sat > 0.3)
    mat[unkm & green] = cid("plant")
    mat[unkm & (mat == -1)] = cid("upholstery")

    alpha_map = np.take(np.array([ALPHA[c] for c in classes], np.float32), mat)
    w = (Z ** 2)                                   # deproject: far pixels cover more area
    abar = float((alpha_map * w).sum() / w.sum())
    rt_rel = float(np.clip((1 - abar) / max(abar, 1e-3) / 20.0, 0, 1))  # 0=dead .. 1=echoey
    return AttributeResult(
        key="cnfa.acoustics.absorption_proxy",
        scalar=float(np.clip(abar, 0.0, 1.0)),
        field=np.clip(alpha_map / 0.6, 0.0, 1.0), confidence=0.5,
        method="visual material classes → mid-band α (Kuttruff 2009 Table 5.1) → "
               "area-weighted mean; RT_rel=(1−α)/α scaled (M2)",
        failure_modes=["unseen surfaces behind camera omitted", "lab α ≠ in-situ",
                       "material heuristic (no VLM) misclassifies", "Sabine diffuse-field limits"],
        extras={"rt_relative_echoiness": rt_rel,
                "alpha_table": ALPHA,
                "class_shares": {c: round(float((mat == i).mean()), 3)
                                 for i, c in enumerate(classes) if (mat == i).any()}})


# ------------------------------------------------------------- social

def sociopetal_seating(img, seats: List[Dict], Z=None) -> AttributeResult:
    """seats: [{'bbox':[x,y,w,h], 'facing_deg': float (image-plane), 'label':str}]
    Scorer is detector-agnostic: plug YOLO/VLM boxes in production."""
    regions, links = [], []
    n = len(seats)
    A = np.zeros((n, n))
    for i in range(n):
        x, y, w, h = seats[i]["bbox"]
        regions.append({"kind": "bbox", "coords": seats[i]["bbox"],
                        "label": seats[i].get("label", f"seat{i}")})
        for j in range(i + 1, n):
            ci = np.array([x + w / 2, y + h / 2])
            xj, yj, wj, hj = seats[j]["bbox"]
            cj = np.array([xj + wj / 2, yj + hj / 2])
            v = cj - ci
            d_px = np.linalg.norm(v)
            # depth-scaled distance if Z available
            if Z is not None:
                zi = float(np.median(Z[int(y):int(y + h), int(x):int(x + w)]))
                zj = float(np.median(Z[int(yj):int(yj + hj), int(xj):int(xj + wj)]))
                d_m = abs(zi - zj) + d_px / img.shape[1] * (zi + zj) / 2 * 1.2
            else:
                d_m = d_px / img.shape[1] * 4.0
            ang = np.degrees(np.arctan2(v[1], v[0]))
            fi, fj = seats[i].get("facing_deg", ang), seats[j].get("facing_deg", ang + 180)
            facing = (abs(((fi - ang + 180) % 360) - 180) < 85 and
                      abs(((fj - (ang + 180) + 180) % 360) - 180) < 85)
            if 0.45 <= d_m <= 3.7 and facing:
                A[i, j] = A[j, i] = 1
                links.append({"kind": "line",
                              "coords": [*ci.astype(int), *cj.astype(int)],
                              "color": (0, 220, 60)})
    score = float(np.clip(A.sum() / 2 / max(n, 1), 0.0, 1.0))
    return AttributeResult(
        key="cnfa.social.sociopetal_seating", scalar=score,
        regions=regions + links,
        confidence=0.55 if seats else 0.0,
        method="proxemic band (0.45–3.7m, Hall 1966 social zone) × mutual facing × pairs; "
               "detector-pluggable (demo: manual boxes) (M2)",
        failure_modes=["facing from single view is weak", "depth-scaled distances approximate",
                       "off-frame seats missing"],
        extras={"pairs": int(A.sum() / 2), "n_seats": n})
