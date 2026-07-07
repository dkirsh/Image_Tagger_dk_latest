"""MPIB-compatible low-level image feature extraction.

This module installs a deterministic Python subset of the Max Planck / MPIB
"Image Decomposer" feature family into the live v3.4 science pipeline. It
keeps the historical MPIB-compatible names so downstream code can audit what
was computed.
"""

from __future__ import annotations

import math
from typing import Dict

import cv2
import numpy as np

from backend.science.core import AnalysisFrame


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


def _ensure_rgb(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    if image.ndim == 3 and image.shape[2] == 1:
        return cv2.cvtColor(image[:, :, 0], cv2.COLOR_GRAY2RGB)
    return image


def _to_gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(_ensure_rgb(image), cv2.COLOR_RGB2GRAY)


def _finite_float(value: float) -> float:
    value_f = float(value)
    if math.isfinite(value_f):
        return value_f
    return float("nan")


def get_brightness(image: np.ndarray) -> tuple[float, float]:
    rgb = _ensure_rgb(image).astype(np.float64) / 255.0
    return _finite_float(np.mean(rgb)), _finite_float(np.std(rgb))


def classify_image_colors(image: np.ndarray) -> tuple[float, float, float, float]:
    rgb = _ensure_rgb(image).astype(np.int16)
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]

    blue_mask = (b > g) & (b > r)
    green_mask = (g > b) & (g > r)
    red_mask = (r > b) & (r > g)
    neutral_mask = ~(blue_mask | green_mask | red_mask)

    total = float(rgb.shape[0] * rgb.shape[1])
    if total <= 0:
        return 0.0, 0.0, 0.0, 1.0
    return (
        _finite_float(np.count_nonzero(blue_mask) / total),
        _finite_float(np.count_nonzero(green_mask) / total),
        _finite_float(np.count_nonzero(red_mask) / total),
        _finite_float(np.count_nonzero(neutral_mask) / total),
    )


def get_contrast(image: np.ndarray) -> float:
    return _finite_float(_to_gray(image).std() / 100.0)


def get_entropy(image: np.ndarray) -> float:
    gray = _to_gray(image)
    counts = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    total = counts.sum()
    if total <= 0:
        return 0.0
    probs = counts[counts > 0] / total
    return _finite_float(-np.sum(probs * np.log2(probs)))


def get_edge_density(image: np.ndarray, sigma: float = 0.33) -> tuple[float, float, float]:
    gray = _to_gray(image)
    median = float(np.median(gray))
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))

    edged_high = cv2.Canny(gray, int(lower * 0.8), int(upper * 0.8))
    edged_low = cv2.Canny(gray, int(lower * 1.6), int(upper * 1.6))

    edges = np.zeros_like(edged_high, dtype=np.uint8)
    edges[edged_low == 255] = 2
    edges[edged_high == 255] = 1

    lines = cv2.HoughLinesP(
        edged_high,
        1,
        np.pi / 180,
        threshold=50,
        minLineLength=50,
        maxLineGap=10,
    )
    straight_mask = np.zeros_like(gray, dtype=np.uint8)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(straight_mask, (x1, y1), (x2, y2), 255, 1)

    total = float(edges.size)
    if total <= 0:
        return 0.0, 0.0, 0.0
    straight = np.sum((straight_mask > 0) & (edges > 0))
    non_straight = np.sum((straight_mask == 0) & (edges > 0))
    return (
        _finite_float(straight / total),
        _finite_float(non_straight / total),
        _finite_float(edges.mean()),
    )


def get_symmetry_mse(image: np.ndarray) -> float:
    rgb = _ensure_rgb(image).astype(np.float64)
    flipped = cv2.flip(rgb, 1)
    err = np.sum((rgb - flipped) ** 2)
    return _finite_float(err / float(rgb.shape[0] * rgb.shape[1]))


def get_symmetry_ssim(image: np.ndarray) -> float:
    gray = _to_gray(image).astype(np.float64)
    flipped = cv2.flip(gray, 1).astype(np.float64)
    c1 = (0.01 * 255.0) ** 2
    c2 = (0.03 * 255.0) ** 2
    mu_x = float(np.mean(gray))
    mu_y = float(np.mean(flipped))
    var_x = float(np.var(gray))
    var_y = float(np.var(flipped))
    cov_xy = float(np.mean((gray - mu_x) * (flipped - mu_y)))
    numerator = (2 * mu_x * mu_y + c1) * (2 * cov_xy + c2)
    denominator = (mu_x ** 2 + mu_y ** 2 + c1) * (var_x + var_y + c2)
    if denominator == 0:
        return 1.0
    return _finite_float(numerator / denominator)


def get_hsv_values(image: np.ndarray) -> tuple[float, float, float, float, float, float]:
    hsv = cv2.cvtColor(_ensure_rgb(image), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    return (
        _finite_float(np.mean(h)),
        _finite_float(np.std(h)),
        _finite_float(np.mean(s)),
        _finite_float(np.std(s)),
        _finite_float(np.mean(v)),
        _finite_float(np.std(v)),
    )


def get_power_spectrum(image: np.ndarray) -> float:
    gray = _to_gray(image).astype(np.float64)
    shifted = np.fft.fftshift(np.fft.fft2(gray))
    power = np.abs(shifted) ** 2
    return _finite_float(np.mean(power))


def extract_mpib_features(image: np.ndarray) -> Dict[str, float]:
    """Extract the MPIB-compatible deterministic low-level feature subset."""
    rgb = _ensure_rgb(image)
    nan = float("nan")
    result: Dict[str, float] = {key: nan for key in MPIB_FEATURE_KEYS}

    try:
        result["brightness_mean"], result["brightness_sd"] = get_brightness(rgb)
    except Exception:
        pass
    try:
        (
            result["color_pct_blue"],
            result["color_pct_green"],
            result["color_pct_red"],
            result["color_pct_neutral"],
        ) = classify_image_colors(rgb)
    except Exception:
        pass
    try:
        result["contrast_rms"] = get_contrast(rgb)
    except Exception:
        pass
    try:
        result["entropy_shannon"] = get_entropy(rgb)
    except Exception:
        pass
    try:
        (
            result["edge_density_straight"],
            result["edge_density_nonstraight"],
            result["edge_density_total"],
        ) = get_edge_density(rgb)
    except Exception:
        pass
    try:
        result["symmetry_mse"] = get_symmetry_mse(rgb)
    except Exception:
        pass
    try:
        result["symmetry_ssim"] = get_symmetry_ssim(rgb)
    except Exception:
        pass
    try:
        (
            result["hsv_hue_mean"],
            result["hsv_hue_sd"],
            result["hsv_saturation_mean"],
            result["hsv_saturation_sd"],
            result["hsv_value_mean"],
            result["hsv_value_sd"],
        ) = get_hsv_values(rgb)
    except Exception:
        pass
    try:
        result["power_spectrum_mean"] = get_power_spectrum(rgb)
    except Exception:
        pass

    return result


class MPIBLowLevelAnalyzer:
    """Analyzer wrapper for the live science pipeline."""

    name = "mpib_low_level"
    artifact_type = "mpib_low_level_json"
    method_version = "mpib_low_level_python_subset_v1"

    def analyze(self, frame: AnalysisFrame) -> None:
        features = extract_mpib_features(frame.original_image)
        frame.metadata[self.name] = {
            "method": self.method_version,
            "feature_count": len(MPIB_FEATURE_KEYS),
            "feature_keys": list(MPIB_FEATURE_KEYS),
            "features": features,
        }
