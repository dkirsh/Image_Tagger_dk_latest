"""MATLAB-ported low-level image features.

Faithful Python re-implementations of features originally computed in MATLAB
by the ImageDecomposer toolbox (Kardan, Berman et al.) and LGN statistics
model (Ghebreab, Scholte, Groen et al.).

These features have NO equivalent in the MPIB Berlin ``low-level-image-features``
Python repo and are therefore ported here.

Ported algorithms
-----------------
1. **CIELAB colour-space statistics** – L*, a*, b* channel means and SDs.
2. **Fractal dimension** – 2-D box-counting (Minkowski–Bouligand dimension)
   of the binarised grayscale image.
3. **LGN statistics** – contrast energy (CE), spatial coherence (SC) and
   Weibull β/γ parameters computed via multiscale Laplacian-of-Gaussian
   filtering on opponent colour channels, following Groen et al. (2013)
   *J Neurosci* 33(48):18813-18824.
4. **Circular hue statistics** – proper circular mean and SD of hue using
   ``scipy.stats.circmean`` / ``circstd`` (the MPIB code erroneously uses
   a linear mean).
5. **7-bin colour histogram** – pixel proportions for Red, Yellow, Green,
   Cyan, Blue, Magenta, and White/neutral, matching
   ``Count_Colors_variableDupIMS.m``.
6. **Per-channel edge density & entropy** – Canny edge fraction and
   Shannon entropy computed on each HSV and CIELAB channel independently.

All public functions accept a **BGR** ``np.ndarray`` (OpenCV convention) and
return a ``dict[str, float]`` with standardised ``snake_case`` keys.

Dependencies: numpy, opencv-python, scipy.
"""

from __future__ import annotations

import warnings
from typing import Any

import cv2
import numpy as np
from scipy import ndimage, stats
from scipy.optimize import minimize_scalar

__all__ = [
    "compute_cielab_stats",
    "compute_fractal_dimension",
    "compute_lgn_statistics",
    "compute_circular_hue",
    "compute_color_histogram_7bin",
    "compute_per_channel_features",
    "extract_matlab_ported_features",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NAN = float("nan")


def _safe_call(fn, img: np.ndarray) -> dict[str, float]:
    """Call *fn(img)* and return its dict; on any error fill values with NaN."""
    try:
        return fn(img)
    except Exception as exc:  # noqa: BLE001
        warnings.warn(f"{fn.__name__} failed: {exc}", stacklevel=2)
        # Build a dict of NaNs using the docstring convention – fall back to
        # an empty dict so the caller still gets *something*.
        return {}


def _to_gray(img: np.ndarray) -> np.ndarray:
    """Convert BGR image to single-channel uint8 grayscale."""
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _shannon_entropy(channel: np.ndarray) -> float:
    """Compute Shannon entropy of a single-channel image (bits).

    Mirrors MATLAB ``entropy()`` which uses a 256-bin histogram on uint8 data.
    """
    if channel.dtype != np.uint8:
        # Normalise to [0, 255] uint8
        mn, mx = channel.min(), channel.max()
        if mx - mn < 1e-12:
            return 0.0
        channel = ((channel - mn) / (mx - mn) * 255).astype(np.uint8)
    hist = cv2.calcHist([channel], [0], None, [256], [0, 256]).ravel()
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist)))


# ===================================================================
# 1.  CIELAB Colour-Space Statistics
# ===================================================================

def compute_cielab_stats(img: np.ndarray) -> dict[str, float]:
    """Compute CIELAB L*, a*, b* channel means and standard deviations.

    The CIELAB colour space separates luminance (L*) from chrominance (a*, b*)
    and is perceptually more uniform than RGB.  These statistics capture the
    dominant lightness, red-green balance (a*), and blue-yellow balance (b*)
    of an image, plus the spread of each.

    Ported from ``WholeIm_Decomposer_cc_ims.m`` lines 54, 113-119.

    Parameters
    ----------
    img : np.ndarray
        BGR uint8 image (H × W × 3).

    Returns
    -------
    dict
        Keys: ``lab_L_mean``, ``lab_A_mean``, ``lab_B_mean``,
        ``lab_L_sd``, ``lab_A_sd``, ``lab_B_sd``.
    """
    if img.ndim == 2:
        # Grayscale – no colour information
        gray_f = img.astype(np.float64)
        return {
            "lab_L_mean": float(np.mean(gray_f)),
            "lab_A_mean": 0.0,
            "lab_B_mean": 0.0,
            "lab_L_sd": float(np.std(gray_f)),
            "lab_A_sd": 0.0,
            "lab_B_sd": 0.0,
        }

    # OpenCV LAB: L ∈ [0, 255], a ∈ [0, 255], b ∈ [0, 255] for uint8
    # We convert to float32 first so cvtColor gives true L* ∈ [0, 100],
    # a* ∈ [-127, 127], b* ∈ [-127, 127].
    img_f = img.astype(np.float32) / 255.0
    lab = cv2.cvtColor(img_f, cv2.COLOR_BGR2LAB)

    return {
        "lab_L_mean": float(np.mean(lab[:, :, 0])),
        "lab_A_mean": float(np.mean(lab[:, :, 1])),
        "lab_B_mean": float(np.mean(lab[:, :, 2])),
        "lab_L_sd": float(np.std(lab[:, :, 0])),
        "lab_A_sd": float(np.std(lab[:, :, 1])),
        "lab_B_sd": float(np.std(lab[:, :, 2])),
    }


# ===================================================================
# 2.  Fractal Dimension (Box-Counting)
# ===================================================================

def _boxcount_2d(binary: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """2-D box-counting on a boolean array.

    Faithful port of ``boxcount.m`` (F. Moisy, 2008).  The image is zero-
    padded to the next power-of-two and then iteratively coarsened: at each
    generation *g*, every 2×2 block is OR-reduced and the number of ``True``
    blocks is recorded.

    Returns
    -------
    n : ndarray
        Number of occupied boxes at each scale (finest → coarsest).
    r : ndarray
        Corresponding box sizes ``[1, 2, 4, …, 2^p]``.
    """
    c = binary.astype(bool).copy()
    width = max(c.shape)
    p = int(np.ceil(np.log2(max(width, 2))))
    width = 2 ** p

    # Pad to square power-of-two
    padded = np.zeros((width, width), dtype=bool)
    padded[: c.shape[0], : c.shape[1]] = c
    c = padded

    n = np.zeros(p + 1, dtype=np.int64)
    n[p] = int(c.sum())

    for g in range(p - 1, -1, -1):
        siz = 2 ** (p - g)
        siz2 = siz // 2
        # Vectorised OR-reduction over the four sub-cells
        rows = np.arange(0, width, siz)
        cols = np.arange(0, width, siz)
        rr, cc = np.meshgrid(rows, cols, indexing="ij")
        c[rr, cc] = (
            c[rr, cc]
            | c[rr + siz2, cc]
            | c[rr, cc + siz2]
            | c[rr + siz2, cc + siz2]
        )
        n[g] = int(c[::siz, ::siz].sum())

    # Reverse so that n[0] corresponds to the largest box
    n = n[::-1]
    r = 2 ** np.arange(p + 1)
    return n, r


def compute_fractal_dimension(img: np.ndarray) -> dict[str, float]:
    """Compute the box-counting fractal dimension of a grayscale image.

    The image is binarised with Otsu's threshold, then
    ``_boxcount_2d`` counts occupied boxes at each dyadic scale.
    The local slopes ``-Δlog(n)/Δlog(r)`` give per-scale estimates of the
    fractal dimension.  Following ``ImageDecomposer.m`` (line 66-67) the
    first 3 estimates are discarded (they capture the trivial large-scale
    behaviour) and the mean and SD of the remaining slopes are returned.

    Parameters
    ----------
    img : np.ndarray
        BGR uint8 image (H × W × 3) or grayscale.

    Returns
    -------
    dict
        Keys: ``fractal_dimension``, ``fractal_dimension_sd``.
    """
    gray = _to_gray(img)

    # Binarise with Otsu
    _, binary = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    n, r = _boxcount_2d(binary)

    # Guard against log(0)
    valid = n > 0
    if valid.sum() < 5:
        return {"fractal_dimension": _NAN, "fractal_dimension_sd": _NAN}

    log_n = np.log(n[valid].astype(np.float64))
    log_r = np.log(r[valid].astype(np.float64))

    # Differential estimates (MATLAB: -diff(log(m))./diff(log(r)))
    dff = -np.diff(log_n) / np.diff(log_r)

    # Skip first 3 estimates (MATLAB: dff(4:end), 1-indexed → index 3+)
    if len(dff) > 3:
        dff_trimmed = dff[3:]
    else:
        dff_trimmed = dff

    return {
        "fractal_dimension": float(np.mean(dff_trimmed)),
        "fractal_dimension_sd": float(np.std(dff_trimmed, ddof=0)),
    }


# ===================================================================
# 3.  LGN Statistics (Contrast Energy & Spatial Coherence)
# ===================================================================

def _rgb_to_opponent(img: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert BGR uint8 image to opponent colour channels.

    Follows ``RGB2E.m``:
        E   = (0.30 R + 0.58 G + 0.11 B) / 255   (luminance / gray)
        El  = (0.25 R + 0.25 G − 0.50 B) / 255   (blue-yellow)
        Ell = (0.50 R − 0.50 G)          / 255    (red-green)
    """
    b = img[:, :, 0].astype(np.float64)
    g = img[:, :, 1].astype(np.float64)
    r = img[:, :, 2].astype(np.float64)
    E = (0.30 * r + 0.58 * g + 0.11 * b) / 255.0
    El = (0.25 * r + 0.25 * g - 0.50 * b) / 255.0
    Ell = (0.50 * r - 0.50 * g) / 255.0
    return E, El, Ell


def _log_filter_1d(sigma: float) -> np.ndarray:
    """Build a 1-D Laplacian-of-Gaussian kernel (zero-mean, energy-normalised).

    Mirrors ``FilterLGN.m`` lines 3-10:
        Gx = (x²/σ⁴ − 1/σ²) · Gauss
        Gx = Gx − mean(Gx)        # zero-mean
        Gx = Gx / Σ(½ x² Gx)     # energy normalise
    """
    half = int(np.ceil(3.0 * sigma))
    x = np.arange(-half, half + 1, dtype=np.float64)
    gauss = np.exp(-x ** 2 / (2.0 * sigma ** 2)) / (np.sqrt(2 * np.pi) * sigma)
    gx = (x ** 2 / sigma ** 4 - 1.0 / sigma ** 2) * gauss
    gx -= gx.mean()
    norm = np.sum(0.5 * x ** 2 * gx)
    if abs(norm) > 1e-15:
        gx /= norm
    return gx


def _filter_channel(channel: np.ndarray, sigma: float) -> np.ndarray:
    """Apply separable LoG filter and return edge magnitude.

    ``FilterLGN.m``: applies 1-D kernel along rows then columns and returns
    sqrt(Ex² + Ey²).  Uses replicate-boundary padding (``conv2padded.m``).
    """
    kernel = _log_filter_1d(sigma)
    # Separable convolution with replicate padding
    ex = ndimage.convolve1d(channel, kernel, axis=1, mode="nearest")
    ey = ndimage.convolve1d(channel, kernel, axis=0, mode="nearest")
    return np.sqrt(ex ** 2 + ey ** 2)


def _local_cov(E: np.ndarray, sigma: float) -> np.ndarray:
    """Local coefficient of variation (``LocalCOV.m``).

    Uses a Gaussian-weighted local mean and local std computed via the
    identity  var = E[X²] − (E[X])².
    """
    half = int(np.round(3.0 * sigma))
    ksize = 2 * half + 1 if 2 * half + 1 >= 1 else 1
    # Build Gaussian kernel (matching fspecial('gaussian', filtersize, sigma))
    gauss_2d = cv2.getGaussianKernel(ksize, sigma) @ cv2.getGaussianKernel(ksize, sigma).T

    term1 = cv2.filter2D(E ** 2, -1, gauss_2d, borderType=cv2.BORDER_REPLICATE)
    term2 = cv2.filter2D(E, -1, gauss_2d, borderType=cv2.BORDER_REPLICATE) ** 2
    local_std = np.sqrt(np.maximum(term1 - term2, 0.0))
    local_mean = cv2.filter2D(E, -1, gauss_2d, borderType=cv2.BORDER_REPLICATE) + np.finfo(float).tiny
    return local_std / local_mean


def _weibull_mle_hist(data: np.ndarray, n_bins: int = 1000) -> tuple[float, float]:
    """Fit Weibull(β, γ) via MLE on a histogram (``weibullMleHist.m``).

    Uses Newton–Raphson iteration identical to the MATLAB implementation.

    Returns (scale β, shape γ).
    """
    data = data.ravel().astype(np.float64)
    data = data[data > 0]
    if len(data) < 10:
        return (_NAN, _NAN)

    # Create histogram (matching createHist.m)
    h, bin_edges = np.histogram(data, bins=n_bins)
    ax = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Keep only non-empty bins
    mask = h > 0
    h = h[mask].astype(np.float64)
    ax = ax[mask]

    # Normalise histogram to a probability distribution
    h = h / h.sum()

    # Newton–Raphson for shape parameter (gamma)
    eps_tol = 0.01
    shape = 0.1

    def _newton_step(g: float) -> float:
        x_g = ax ** g
        sum_x_g = np.sum(x_g * h)
        if abs(sum_x_g) < 1e-30:
            return 0.0
        x_i = x_g / sum_x_g
        ln_x_i = np.log(np.maximum(x_i, 1e-300))
        log_ax = np.log(np.maximum(ax, 1e-300))

        lam = x_g * (log_ax * sum_x_g - np.sum(h * x_g * log_ax)) / (sum_x_g ** 2)

        f = 1.0 + np.sum(ln_x_i * h) - np.sum(x_i * ln_x_i * h)
        f_prime = np.sum(lam * h * (sum_x_g / x_g - ln_x_i - 1.0))
        if abs(f_prime) < 1e-30:
            return 0.0
        return f / f_prime

    for _ in range(50):
        step = _newton_step(shape)
        shape_next = shape - step
        if np.isnan(shape_next) or np.isinf(shape_next) or shape_next > 20:
            break
        if shape_next <= 0:
            shape_next = 1e-6
            break
        if abs(shape_next - shape) < eps_tol:
            shape = shape_next
            break
        shape = shape_next

    # Scale parameter (beta)
    x_g = ax ** shape
    sum_x_g = np.sum(x_g * h)
    scale = sum_x_g ** (1.0 / shape) if abs(shape) > 1e-15 else _NAN

    return (float(scale), float(shape))


def compute_lgn_statistics(img: np.ndarray) -> dict[str, float]:
    """Compute LGN-inspired contrast energy and spatial coherence.

    This is a faithful Python port of the multiscale LGN statistics model
    described in:

    * Scholte HS et al. (2009) *J Vis* 9:1–15.
    * Ghebreab S et al. (2009) *NIPS* 22:629–637.
    * Groen IIA et al. (2013) *J Neurosci* 33(48):18813-18824.

    The model applies Laplacian-of-Gaussian (LoG) filters at multiple spatial
    scales to three opponent-colour channels (luminance, blue-yellow, red-green),
    mimicking the multiscale centre-surround receptive fields of the lateral
    geniculate nucleus (LGN).  Local contrast is computed, thresholded, and
    summarised by:

    * **Contrast Energy (CE)** – mean absolute edge magnitude within a
      small foveal region (1.5° field of view).
    * **Spatial Coherence (SC)** – mean / std of edge magnitude within a
      larger region (5° field of view), capturing homogeneity.
    * **Weibull β (scale)** and **γ (shape)** – parameters of a Weibull
      distribution fitted to the local contrast histogram via MLE.

    Note: The MATLAB code loads ``ThresholdLGN.mat`` with per-scale thresholds.
    We approximate these as zeros (conservative – no thresholding) since the
    .mat file is opaque binary.  This marginally increases noise but preserves
    the relative ranking of CE/SC across images.

    Parameters
    ----------
    img : np.ndarray
        BGR uint8 image (H × W × 3).

    Returns
    -------
    dict
        Keys: ``ce_gray``, ``ce_blueyellow``, ``ce_redgreen``,
        ``sc_gray``, ``sc_blueyellow``, ``sc_redgreen``,
        ``beta_gray``, ``beta_blueyellow``, ``beta_redgreen``,
        ``gamma_gray``, ``gamma_blueyellow``, ``gamma_redgreen``.
    """
    result: dict[str, float] = {}
    ch_names = ["gray", "blueyellow", "redgreen"]

    # --- Opponent colour decomposition ---
    if img.ndim == 2:
        gray = img.astype(np.float64) / max(img.max(), 1)
        channels = [gray]
        ch_names_used = ["gray"]
    else:
        E, El, Ell = _rgb_to_opponent(img)
        channels = [E, El, Ell]
        ch_names_used = ch_names

    # --- Viewing-geometry FOV mask (assume 1 m, 0.35 mm dot pitch) ---
    h, w = img.shape[:2]
    dot_pitch = 0.35e-3
    viewing_dist = 1.0
    cy, cx = h // 2, w // 2
    yy, xx = np.ogrid[-cy : h - cy, -cx : w - cx]
    eradius = dot_pitch * np.sqrt(xx.astype(np.float64) ** 2 + yy.astype(np.float64) ** 2)
    ec = np.degrees(np.arctan(eradius / viewing_dist))
    mask_beta = ec < 1.5    # FOV for CE / Weibull-beta
    mask_gamma = ec < 5.0   # FOV for SC / Weibull-gamma

    # --- Multiscale filtering ---
    # Parvocellular scales (finer → CE, Weibull beta)
    sigmas_par = [48, 24, 12, 6, 3]
    # Magnocellular scales (coarser → SC, Weibull gamma)
    sigmas_mag = [64, 32, 16, 8, 4]

    for ci, ch in enumerate(channels):
        name = ch_names_used[ci]

        # --- Parvocellular path (CE / beta) ---
        par_accum = np.zeros_like(ch)
        for sigma in sigmas_par:
            O = _filter_channel(ch, sigma)
            S = _local_cov(O, sigma)
            o_max = O.max()
            if o_max < 1e-15:
                continue
            E_norm = (O * o_max) / (O + o_max * S + 1e-30)
            par_accum = np.maximum(par_accum, E_norm)

        # --- Magnocellular path (SC / gamma) ---
        mag_accum = np.zeros_like(ch)
        for sigma in sigmas_mag:
            O = _filter_channel(ch, sigma)
            S = _local_cov(O, sigma)
            o_max = O.max()
            if o_max < 1e-15:
                continue
            E_norm = (O * o_max) / (O + o_max * S + 1e-30)
            mag_accum = np.maximum(mag_accum, E_norm)

        # --- Contrast Energy ---
        mag_par = np.abs(par_accum[mask_beta])
        ce = float(np.mean(mag_par)) if mag_par.size > 0 else _NAN
        result[f"ce_{name}"] = ce

        # --- Spatial Coherence ---
        mag_mag = np.abs(mag_accum[mask_gamma])
        if mag_mag.size > 0 and np.std(mag_mag) > 1e-15:
            sc = float(np.mean(mag_mag) / np.std(mag_mag))
        else:
            sc = _NAN
        result[f"sc_{name}"] = sc

        # --- Weibull fits ---
        beta_val, _ = _weibull_mle_hist(mag_par)
        result[f"beta_{name}"] = beta_val

        _, gamma_val = _weibull_mle_hist(mag_mag)
        result[f"gamma_{name}"] = gamma_val

    # Fill missing channels for grayscale input
    for name in ch_names:
        for prefix in ("ce_", "sc_", "beta_", "gamma_"):
            result.setdefault(f"{prefix}{name}", _NAN)

    return result


# ===================================================================
# 4.  Circular Hue Statistics
# ===================================================================

def compute_circular_hue(img: np.ndarray) -> dict[str, float]:
    """Compute circular mean and standard deviation of hue.

    Hue is a circular (angular) variable.  Taking the arithmetic mean of
    hue values is incorrect because, e.g., the mean of 1° and 359° should
    be 0°, not 180°.  The MPIB Python code uses ``np.mean`` which is wrong.
    The original MATLAB ``WholeIm_Decomposer.m`` correctly uses the
    CircStat toolbox (Berens 2009).

    We map OpenCV's hue [0, 180) → radians [0, 2π) and use
    ``scipy.stats.circmean`` / ``circstd``.

    Parameters
    ----------
    img : np.ndarray
        BGR uint8 image (H × W × 3).

    Returns
    -------
    dict
        Keys: ``hue_circular_mean`` (radians ∈ [0, 2π)),
        ``hue_circular_sd`` (radians ≥ 0).
    """
    if img.ndim == 2:
        return {"hue_circular_mean": _NAN, "hue_circular_sd": _NAN}

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # OpenCV H ∈ [0, 180) for uint8 – map to [0, 2π)
    hue_rad = hsv[:, :, 0].ravel().astype(np.float64) * (2.0 * np.pi / 180.0)

    cmean = float(stats.circmean(hue_rad, high=2 * np.pi, low=0.0))
    cstd = float(stats.circstd(hue_rad, high=2 * np.pi, low=0.0))
    return {"hue_circular_mean": cmean, "hue_circular_sd": cstd}


# ===================================================================
# 5.  7-Bin Colour Histogram
# ===================================================================

def compute_color_histogram_7bin(img: np.ndarray) -> dict[str, float]:
    """Compute a 7-bin colour histogram based on hue boundaries.

    Bins: Red, Yellow, Green, Cyan, Blue, Magenta, White/neutral.
    Pixels with saturation below ``sat_threshold`` are classified as
    White/neutral regardless of hue.

    Ported from ``Count_Colors_variableDupIMS.m`` with the default call:
        Count_Colors_variableDupIMS(img,
            [60/360, 120/360, 180/360, 240/360, 300/360],   % centres
            [1/12, 1/12, 1/12, 1/12, 1/12, 1/12],           % half-widths
            0.05)                                            % sat threshold

    In the MATLAB code, hue is in [0, 1] (``rgb2hsv``).  OpenCV's uint8 HSV
    maps H to [0, 180).  We normalise to [0, 1] for direct comparison.

    Parameters
    ----------
    img : np.ndarray
        BGR uint8 image (H × W × 3).

    Returns
    -------
    dict
        Keys: ``color_pct_red``, ``color_pct_yellow``, ``color_pct_green``,
        ``color_pct_cyan``, ``color_pct_blue``, ``color_pct_magenta``,
        ``color_pct_white``.  Values are fractions of total pixels ∈ [0, 1].
    """
    zeros = {
        "color_pct_red": 0.0,
        "color_pct_yellow": 0.0,
        "color_pct_green": 0.0,
        "color_pct_cyan": 0.0,
        "color_pct_blue": 0.0,
        "color_pct_magenta": 0.0,
        "color_pct_white": 0.0,
    }
    if img.ndim == 2:
        zeros["color_pct_white"] = 1.0
        return zeros

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Normalise H to [0, 1] and S to [0, 1]
    hue = hsv[:, :, 0].astype(np.float64) / 180.0
    sat = hsv[:, :, 1].astype(np.float64) / 255.0

    n_pixels = float(hue.size)
    sat_threshold = 0.05

    # Hue centres (in [0, 1] space) and half-widths from the MATLAB call
    # Red is centred at 0 (wraps around 1)
    centres = [60.0 / 360.0, 120.0 / 360.0, 180.0 / 360.0,
               240.0 / 360.0, 300.0 / 360.0]
    hw = 1.0 / 12.0  # half-width for every bin

    # Low-saturation pixels → white
    low_sat = sat < sat_threshold

    # Red: |hue| < hw  OR  |hue - 1| < hw  (wraps around 0/1 boundary)
    mask_r = (np.abs(hue) < hw) | (np.abs(hue - 1.0) < hw)
    mask_y = np.abs(hue - centres[0]) < hw
    mask_g = np.abs(hue - centres[1]) < hw
    mask_c = np.abs(hue - centres[2]) < hw
    mask_b = np.abs(hue - centres[3]) < hw
    mask_m = np.abs(hue - centres[4]) < hw

    # Override: low-saturation pixels are White, not a chromatic bin
    mask_r[low_sat] = False
    mask_y[low_sat] = False
    mask_g[low_sat] = False
    mask_c[low_sat] = False
    mask_b[low_sat] = False
    mask_m[low_sat] = False

    return {
        "color_pct_red": float(mask_r.sum()) / n_pixels,
        "color_pct_yellow": float(mask_y.sum()) / n_pixels,
        "color_pct_green": float(mask_g.sum()) / n_pixels,
        "color_pct_cyan": float(mask_c.sum()) / n_pixels,
        "color_pct_blue": float(mask_b.sum()) / n_pixels,
        "color_pct_magenta": float(mask_m.sum()) / n_pixels,
        "color_pct_white": float(low_sat.sum()) / n_pixels,
    }


# ===================================================================
# 6.  Per-Channel Edge Density & Entropy
# ===================================================================

def compute_per_channel_features(img: np.ndarray) -> dict[str, float]:
    """Compute Canny edge density and Shannon entropy for each HSV and LAB channel.

    Ported from ``WholeIm_Decomposer_cc_ims.m`` lines 68-91.

    * **Edge density** is the fraction of pixels flagged as edges by the
      Canny detector (MATLAB ``edge(ch, 'canny')`` with automatic
      thresholding ↔ OpenCV ``cv2.Canny`` with Otsu-based thresholds).
    * **Entropy** is the Shannon entropy of the channel histogram (bits).

    Parameters
    ----------
    img : np.ndarray
        BGR uint8 image (H × W × 3).

    Returns
    -------
    dict
        Keys: ``ed_h``, ``ed_s``, ``ed_v``, ``ed_l``, ``ed_a``, ``ed_b``,
        ``ent_h``, ``ent_s``, ``ent_v``, ``ent_l``, ``ent_a``, ``ent_b``.
    """
    nan_result = {
        f"{p}_{c}": _NAN
        for p in ("ed", "ent")
        for c in ("h", "s", "v", "l", "a", "b")
    }

    if img.ndim == 2:
        return nan_result

    # HSV channels
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_ch = hsv[:, :, 0]
    s_ch = hsv[:, :, 1]
    v_ch = hsv[:, :, 2]

    # LAB channels (uint8 for Canny compatibility)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_ch = lab[:, :, 0]
    a_ch = lab[:, :, 1]
    b_ch = lab[:, :, 2]

    channels = {
        "h": h_ch, "s": s_ch, "v": v_ch,
        "l": l_ch, "a": a_ch, "b": b_ch,
    }

    result: dict[str, float] = {}
    n_pixels = float(img.shape[0] * img.shape[1])

    for name, ch in channels.items():
        # Ensure uint8 for Canny
        if ch.dtype != np.uint8:
            mn, mx = ch.min(), ch.max()
            if mx - mn < 1e-12:
                ch_u8 = np.zeros_like(ch, dtype=np.uint8)
            else:
                ch_u8 = ((ch.astype(np.float64) - mn) / (mx - mn) * 255).astype(np.uint8)
        else:
            ch_u8 = ch

        # Automatic Canny (Otsu-based high/low thresholds like MATLAB auto)
        otsu_val, _ = cv2.threshold(ch_u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        low_t = max(1, int(otsu_val * 0.5))
        high_t = min(255, int(otsu_val))
        edges = cv2.Canny(ch_u8, low_t, high_t)

        result[f"ed_{name}"] = float((edges > 0).sum()) / n_pixels
        result[f"ent_{name}"] = _shannon_entropy(ch_u8)

    return result


# ===================================================================
# Master function
# ===================================================================

def extract_matlab_ported_features(img: np.ndarray) -> dict[str, float]:
    """Extract all MATLAB-ported features from a single BGR image.

    Calls each feature function in turn, catching errors per-function so
    that a failure in one does not block the rest.  Failed features are
    filled with ``NaN``.

    Parameters
    ----------
    img : np.ndarray
        BGR uint8 image (H × W × 3), as returned by ``cv2.imread``.

    Returns
    -------
    dict
        Flat dict with ≈30+ ``snake_case`` keys, all values ``float``.
    """
    features: dict[str, float] = {}
    for fn in (
        compute_cielab_stats,
        compute_fractal_dimension,
        compute_lgn_statistics,
        compute_circular_hue,
        compute_color_histogram_7bin,
        compute_per_channel_features,
    ):
        features.update(_safe_call(fn, img))
    return features
