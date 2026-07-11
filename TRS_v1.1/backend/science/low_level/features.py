"""
Low-level image feature extraction (MPIB feature set).

Ported from the original click-based CLI tool into a clean library module.
All functions accept BGR numpy arrays (as returned by cv2.imread) and return
numeric values.  The master function ``extract_mpib_features`` runs every
feature extractor and returns a flat dict with standardized keys.

Dependencies: numpy, opencv-python (cv2), scikit-image (skimage), scipy.
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import cv2
import numpy as np
from skimage import measure
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_bgr(image: np.ndarray) -> np.ndarray:
    """Convert a grayscale image to 3-channel BGR if needed.

    Parameters
    ----------
    image : np.ndarray
        Input image, either (H, W) grayscale or (H, W, 3) BGR.

    Returns
    -------
    np.ndarray
        Guaranteed 3-channel BGR image with dtype preserved.
    """
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.ndim == 3 and image.shape[2] == 1:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def _to_gray(image: np.ndarray) -> np.ndarray:
    """Convert an image to single-channel grayscale.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR or already grayscale.

    Returns
    -------
    np.ndarray
        Single-channel grayscale uint8 image.
    """
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# ---------------------------------------------------------------------------
# Individual feature extractors
# ---------------------------------------------------------------------------


def get_brightness(image: np.ndarray) -> Tuple[float, float]:
    """Compute mean brightness and its standard deviation.

    Brightness is calculated across all channels by normalising pixel
    values to [0, 1].

    Parameters
    ----------
    image : np.ndarray
        BGR image (H, W, 3) with dtype uint8.

    Returns
    -------
    tuple[float, float]
        ``(mean_brightness, sd_brightness)`` both in [0, 1].
    """
    image = _ensure_bgr(image)
    flat = image.flatten().astype(np.float64)
    total_brightness = np.sum(flat)
    tot_pix = image.shape[0] * image.shape[1] * image.shape[2]
    mean_brightness = (total_brightness / tot_pix) / 255.0
    sd_brightness = float(np.std(flat / 255.0))
    return float(mean_brightness), sd_brightness


def classify_image_colors(image: np.ndarray) -> Tuple[float, float, float, float]:
    """Classify pixels by dominant colour channel (vectorized).

    Each pixel is assigned to the channel with the highest value, or to
    *neutral* when no single channel dominates.  This is a fully vectorized
    re-implementation of the original per-pixel Python loop.

    The input is expected in **BGR** order.  Internally the image is
    converted to BGR colour-comparison space (same as the original code
    which converted RGB→BGR before comparison).

    Parameters
    ----------
    image : np.ndarray
        BGR image (H, W, 3) with dtype uint8.

    Returns
    -------
    tuple[float, float, float, float]
        ``(pct_blue, pct_green, pct_red, pct_neutral)`` — fractions of
        total pixels belonging to each category, summing to 1.0.

    Notes
    -----
    The original code received an RGB image from ``skimage.io.imread``,
    then immediately converted it to BGR via ``cv.cvtColor(img,
    cv.COLOR_RGB2BGR)``.  Since this library module receives BGR input
    directly (from ``cv2.imread``), no additional conversion is needed —
    channel 0 is already Blue, channel 1 Green, channel 2 Red.
    """
    image = _ensure_bgr(image)
    b = image[:, :, 0].astype(np.int16)
    g = image[:, :, 1].astype(np.int16)
    r = image[:, :, 2].astype(np.int16)

    # A pixel is "blue" if B > G *and* B > R, etc.
    blue_mask = (b > g) & (b > r)
    green_mask = (g > b) & (g > r)
    red_mask = (r > b) & (r > g)
    neutral_mask = ~(blue_mask | green_mask | red_mask)

    total = float(image.shape[0] * image.shape[1])
    return (
        float(np.count_nonzero(blue_mask) / total),
        float(np.count_nonzero(green_mask) / total),
        float(np.count_nonzero(red_mask) / total),
        float(np.count_nonzero(neutral_mask) / total),
    )


def get_contrast(image: np.ndarray) -> float:
    """Compute RMS contrast of the image.

    The grayscale standard deviation is divided by 100 to match the
    original scaling.

    Parameters
    ----------
    image : np.ndarray
        BGR image (H, W, 3).

    Returns
    -------
    float
        Scaled RMS contrast value.
    """
    gray = _to_gray(_ensure_bgr(image))
    return float(gray.std() / 100.0)


def get_entropy(image: np.ndarray) -> float:
    """Compute Shannon entropy of the grayscale image.

    Parameters
    ----------
    image : np.ndarray
        BGR or grayscale image.

    Returns
    -------
    float
        Shannon entropy (bits).
    """
    gray = _to_gray(_ensure_bgr(image))
    return float(measure.shannon_entropy(gray))


def get_edge_density(
    image: np.ndarray,
    sigma: float = 0.33,
) -> Tuple[float, float, float]:
    """Compute straight, non-straight, and total edge densities.

    Uses Canny edge detection at two sensitivity levels and probabilistic
    Hough line detection to separate straight from non-straight edges.

    Parameters
    ----------
    image : np.ndarray
        BGR or grayscale image.
    sigma : float, optional
        Fraction controlling the adaptive Canny thresholds (default 0.33).

    Returns
    -------
    tuple[float, float, float]
        ``(straight_edge_density, non_straight_edge_density, total_edge_mean)``
    """
    gray = _to_gray(_ensure_bgr(image))
    v = float(np.median(gray))
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))

    edged_high = cv2.Canny(gray, lower * 0.8, upper * 0.8)
    edged_low = cv2.Canny(gray, lower * 1.6, upper * 1.6)

    edges = np.zeros_like(edged_high)
    edges[edged_low == 255] = 2
    edges[edged_high == 255] = 1

    lines = cv2.HoughLinesP(
        edged_high, 1, np.pi / 180, threshold=50,
        minLineLength=50, maxLineGap=10,
    )

    straight_mask = np.zeros_like(gray, dtype=np.uint8)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(straight_mask, (x1, y1), (x2, y2), 255, 1)

    total = edges.size
    straight = np.sum((straight_mask > 0) & (edges > 0))
    non_straight = np.sum((straight_mask == 0) & (edges > 0))

    return (
        float(straight / total),
        float(non_straight / total),
        float(edges.mean()),
    )


def get_symmetry_mse(image: np.ndarray) -> float:
    """Mean Square Error between the image and its horizontal mirror.

    A smaller value indicates greater bilateral symmetry.

    Parameters
    ----------
    image : np.ndarray
        BGR image (H, W, 3).

    Returns
    -------
    float
        MSE value.
    """
    image = _ensure_bgr(image)
    flipped = cv2.flip(image, 1)
    err = np.sum((image.astype(np.float64) - flipped.astype(np.float64)) ** 2)
    err /= float(image.shape[0] * image.shape[1])
    return float(err)


def get_symmetry_ssim(image: np.ndarray) -> float:
    """Structural Similarity Index between the image and its mirror.

    SSIM ranges from -1 to 1 where 1 indicates perfect symmetry.

    Parameters
    ----------
    image : np.ndarray
        BGR image (H, W, 3).

    Returns
    -------
    float
        SSIM value.
    """
    image = _ensure_bgr(image)
    flipped = cv2.flip(image, 1)
    return float(ssim(image, flipped, win_size=3, channel_axis=2))


def get_hsv_values(image: np.ndarray) -> Tuple[float, float, float, float, float, float]:
    """Compute mean and standard deviation of each HSV channel.

    Parameters
    ----------
    image : np.ndarray
        BGR image (H, W, 3).

    Returns
    -------
    tuple[float, float, float, float, float, float]
        ``(hue_mean, hue_sd, saturation_mean, saturation_sd, value_mean,
        value_sd)``
    """
    image = _ensure_bgr(image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    return (
        float(np.mean(h)), float(np.std(h)),
        float(np.mean(s)), float(np.std(s)),
        float(np.mean(v)), float(np.std(v)),
    )


def get_power_spectrum(image: np.ndarray) -> float:
    """Compute the mean power of the 2-D Fourier spectrum.

    Parameters
    ----------
    image : np.ndarray
        BGR or grayscale image.

    Returns
    -------
    float
        Mean power spectrum value.
    """
    gray = _to_gray(_ensure_bgr(image))
    f = np.fft.fft2(gray.astype(np.float64))
    fshift = np.fft.fftshift(f)
    power = np.abs(fshift) ** 2
    return float(np.mean(power))


# ---------------------------------------------------------------------------
# Master extraction function
# ---------------------------------------------------------------------------

#: Canonical output keys produced by :func:`extract_mpib_features`.
MPIB_FEATURE_KEYS = [
    "brightness_mean",
    "brightness_sd",
    "color_pct_blue",
    "color_pct_green",
    "color_pct_red",
    "color_pct_neutral",
    "contrast_rms",
    "entropy_shannon",
    "edge_density_straight",
    "edge_density_nonstraight",
    "edge_density_total",
    "symmetry_mse",
    "symmetry_ssim",
    "hsv_hue_mean",
    "hsv_hue_sd",
    "hsv_saturation_mean",
    "hsv_saturation_sd",
    "hsv_value_mean",
    "hsv_value_sd",
    "power_spectrum_mean",
]


def extract_mpib_features(img: np.ndarray) -> Dict[str, float]:
    """Extract all MPIB low-level image features.

    Each feature group is computed independently inside its own try/except
    block so that a failure in one group does not prevent the others from
    being returned.  Failed features are set to ``float('nan')``.

    Parameters
    ----------
    img : np.ndarray
        Input image as read by ``cv2.imread`` (BGR, uint8).  Grayscale
        images are automatically promoted to 3-channel BGR.

    Returns
    -------
    dict[str, float]
        Flat dictionary with the following keys (all values are ``float``):

        - ``brightness_mean``
        - ``brightness_sd``
        - ``color_pct_blue``
        - ``color_pct_green``
        - ``color_pct_red``
        - ``color_pct_neutral``
        - ``contrast_rms``
        - ``entropy_shannon``
        - ``edge_density_straight``
        - ``edge_density_nonstraight``
        - ``edge_density_total``
        - ``symmetry_mse``
        - ``symmetry_ssim``
        - ``hsv_hue_mean``
        - ``hsv_hue_sd``
        - ``hsv_saturation_mean``
        - ``hsv_saturation_sd``
        - ``hsv_value_mean``
        - ``hsv_value_sd``
        - ``power_spectrum_mean``
    """
    img = _ensure_bgr(img)
    nan = float("nan")

    # Initialise every key to NaN so partial failures are still returned.
    result: Dict[str, float] = {k: nan for k in MPIB_FEATURE_KEYS}

    # --- Brightness ---
    try:
        b_mean, b_sd = get_brightness(img)
        result["brightness_mean"] = b_mean
        result["brightness_sd"] = b_sd
    except Exception:
        logger.warning("Failed to compute brightness features", exc_info=True)

    # --- Colour classification ---
    try:
        blue, green, red, neutral = classify_image_colors(img)
        result["color_pct_blue"] = blue
        result["color_pct_green"] = green
        result["color_pct_red"] = red
        result["color_pct_neutral"] = neutral
    except Exception:
        logger.warning("Failed to compute colour features", exc_info=True)

    # --- Contrast ---
    try:
        result["contrast_rms"] = get_contrast(img)
    except Exception:
        logger.warning("Failed to compute contrast", exc_info=True)

    # --- Entropy ---
    try:
        result["entropy_shannon"] = get_entropy(img)
    except Exception:
        logger.warning("Failed to compute entropy", exc_info=True)

    # --- Edge density ---
    try:
        sed, nsed, total = get_edge_density(img)
        result["edge_density_straight"] = sed
        result["edge_density_nonstraight"] = nsed
        result["edge_density_total"] = total
    except Exception:
        logger.warning("Failed to compute edge density", exc_info=True)

    # --- Symmetry (MSE) ---
    try:
        result["symmetry_mse"] = get_symmetry_mse(img)
    except Exception:
        logger.warning("Failed to compute symmetry MSE", exc_info=True)

    # --- Symmetry (SSIM) ---
    try:
        result["symmetry_ssim"] = get_symmetry_ssim(img)
    except Exception:
        logger.warning("Failed to compute symmetry SSIM", exc_info=True)

    # --- HSV ---
    try:
        h_m, h_sd, s_m, s_sd, v_m, v_sd = get_hsv_values(img)
        result["hsv_hue_mean"] = h_m
        result["hsv_hue_sd"] = h_sd
        result["hsv_saturation_mean"] = s_m
        result["hsv_saturation_sd"] = s_sd
        result["hsv_value_mean"] = v_m
        result["hsv_value_sd"] = v_sd
    except Exception:
        logger.warning("Failed to compute HSV features", exc_info=True)

    # --- Power spectrum ---
    try:
        result["power_spectrum_mean"] = get_power_spectrum(img)
    except Exception:
        logger.warning("Failed to compute power spectrum", exc_info=True)

    return result
