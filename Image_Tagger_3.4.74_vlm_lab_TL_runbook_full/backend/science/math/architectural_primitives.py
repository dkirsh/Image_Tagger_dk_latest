"""Deterministic architectural direct-statistics analyzer.

Sprint S1 implements cheap, no-VLM image statistics for canonical CNfA
feature keys that already exist in backend/science/features_canonical.jsonl.

Outputs:
    cnfa.fluency.processing_load_proxy
    cnfa.light.brightness_variance
    cnfa.fluency.edge_clarity_mean
    cnfa.fluency.color_palette_entropy
    cnfa.fluency.symmetry_score_horizontal
    cnfa.fractal_dimension
"""

from __future__ import annotations

import math
import zlib
from typing import Dict

import cv2
import numpy as np

from backend.science.core import AnalysisFrame


CNFA_DIRECT_STATS_KEYS = (
    "cnfa.fluency.processing_load_proxy",
    "cnfa.light.brightness_variance",
    "cnfa.fluency.edge_clarity_mean",
    "cnfa.fluency.color_palette_entropy",
    "cnfa.fluency.symmetry_score_horizontal",
    "cnfa.fractal_dimension",
)


def _clamp01(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _as_rgb_uint8(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image)
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    if arr.ndim != 3 or arr.shape[-1] < 3:
        raise ValueError("Expected grayscale or RGB-like image array.")
    arr = arr[..., :3]
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    return arr


def _as_gray_uint8(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image)
    if arr.ndim == 2:
        gray = arr
    else:
        rgb = _as_rgb_uint8(arr)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    if gray.dtype != np.uint8:
        gray = np.clip(gray, 0, 255).astype(np.uint8)
    return gray


def compute_brightness_variance(image: np.ndarray) -> float:
    """Normalized luminance variance in [0,1]."""
    gray = _as_gray_uint8(image).astype(np.float32) / 255.0
    return _clamp01(float(np.var(gray)))


def compute_color_palette_entropy(image: np.ndarray, bins_per_channel: int = 8) -> float:
    """Deterministic RGB palette entropy using a quantized color histogram."""
    rgb = _as_rgb_uint8(image)
    bins = int(bins_per_channel)
    if bins <= 1:
        raise ValueError("bins_per_channel must be > 1")

    quant = np.clip(rgb.astype(np.int32) * bins // 256, 0, bins - 1)
    codes = (
        quant[..., 0] * bins * bins
        + quant[..., 1] * bins
        + quant[..., 2]
    ).reshape(-1)

    counts = np.bincount(codes, minlength=bins ** 3).astype(np.float64)
    probs = counts[counts > 0] / float(codes.size)
    entropy = -np.sum(probs * np.log2(probs))
    max_entropy = math.log2(bins ** 3)
    return _clamp01(float(entropy / max_entropy) if max_entropy > 0 else 0.0)


def compute_edge_clarity_mean(image: np.ndarray) -> float:
    """Mean Sobel gradient strength on Canny edge pixels, normalized to [0,1]."""
    gray = _as_gray_uint8(image)
    edges = cv2.Canny(gray, 50, 150, L2gradient=True)
    edge_mask = edges > 0
    if not np.any(edge_mask):
        return 0.0

    gray_f = gray.astype(np.float32) / 255.0
    gx = cv2.Sobel(gray_f, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_f, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)

    # Sobel magnitude on normalized images can exceed 1 at sharp edges.
    # Dividing by 4 gives a stable 0-1 proxy without making it binary.
    return _clamp01(float(np.mean(mag[edge_mask]) / 4.0))


def compute_symmetry_score_horizontal(image: np.ndarray) -> float:
    """Left-right mirror similarity after horizontal flip, in [0,1].

    The canonical feature description uses cv2.flip(image, 1), so this measures
    bilateral left-right symmetry even though the feature name says horizontal.
    """
    gray = _as_gray_uint8(image).astype(np.float32)
    h, w = gray.shape
    if h < 4 or w < 4:
        return 0.0

    z = (gray - float(gray.mean())) / (float(gray.std()) + 1e-6)
    left = z[:, : w // 2]
    right = z[:, w - left.shape[1] :][:, ::-1]

    a = left.reshape(-1)
    b = right.reshape(-1)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b)) + 1e-6
    if denom <= 0:
        return 0.0
    corr = float(np.dot(a, b) / denom)
    return _clamp01((corr + 1.0) / 2.0)


def compute_fractal_dimension(image: np.ndarray) -> float:
    """Normalized box-counting fractal dimension proxy in [0,1]."""
    gray = _as_gray_uint8(image)
    edges = cv2.Canny(gray, 50, 150, L2gradient=True) > 0
    if not np.any(edges):
        return 0.0

    h, w = edges.shape
    p = min(h, w)
    if p < 8:
        return 0.0

    max_power = int(np.floor(np.log2(p)))
    sizes = 2 ** np.arange(max_power, 1, -1)
    counts = []

    for size in sizes:
        box_count = 0
        for y in range(0, h, size):
            for x in range(0, w, size):
                patch = edges[y : y + size, x : x + size]
                if np.any(patch):
                    box_count += 1
        if box_count > 0:
            counts.append((size, box_count))

    if len(counts) < 2:
        return 0.0

    sizes_arr = np.asarray([s for s, _ in counts], dtype=np.float64)
    counts_arr = np.asarray([c for _, c in counts], dtype=np.float64)

    coeffs = np.polyfit(np.log(1.0 / sizes_arr), np.log(counts_arr), 1)
    dimension = float(coeffs[0])

    # Edges usually live between D=1 line-like and D=2 area-filling.
    return _clamp01(dimension - 1.0)


def compute_processing_load_proxy(image: np.ndarray) -> float:
    """Compression/entropy proxy for visual processing load in [0,1]."""
    rgb = _as_rgb_uint8(image)
    gray = _as_gray_uint8(rgb)

    raw = rgb.tobytes()
    if not raw:
        return 0.0

    compressed = zlib.compress(raw, level=9)
    compression_ratio = len(compressed) / float(len(raw))

    brightness_var = compute_brightness_variance(gray)
    palette_entropy = compute_color_palette_entropy(rgb)
    edge_density = float(np.count_nonzero(cv2.Canny(gray, 50, 150, L2gradient=True))) / float(gray.size)

    score = (
        0.35 * _clamp01(compression_ratio)
        + 0.30 * palette_entropy
        + 0.20 * _clamp01(edge_density * 8.0)
        + 0.15 * brightness_var
    )
    return _clamp01(score)


def compute_direct_stats(image: np.ndarray) -> Dict[str, float]:
    """Compute all Sprint S1 direct-stat values for a raw image array."""
    return {
        "cnfa.fluency.processing_load_proxy": compute_processing_load_proxy(image),
        "cnfa.light.brightness_variance": compute_brightness_variance(image),
        "cnfa.fluency.edge_clarity_mean": compute_edge_clarity_mean(image),
        "cnfa.fluency.color_palette_entropy": compute_color_palette_entropy(image),
        "cnfa.fluency.symmetry_score_horizontal": compute_symmetry_score_horizontal(image),
        "cnfa.fractal_dimension": compute_fractal_dimension(image),
    }


class ArchitecturalPrimitivesAnalyzer:
    """Adds deterministic S1 CNfA direct-statistics attributes to a frame."""

    def analyze(self, frame: AnalysisFrame) -> None:
        values = compute_direct_stats(frame.original_image)

        # Keep these add_attribute calls in this exact literal form so
        # tests/test_feature_registry_coverage.py can detect implemented keys.
        frame.add_attribute("cnfa.fluency.processing_load_proxy", _clamp01(values["cnfa.fluency.processing_load_proxy"]), confidence=1.0)
        frame.add_attribute("cnfa.light.brightness_variance", _clamp01(values["cnfa.light.brightness_variance"]), confidence=1.0)
        frame.add_attribute("cnfa.fluency.edge_clarity_mean", _clamp01(values["cnfa.fluency.edge_clarity_mean"]), confidence=1.0)
        frame.add_attribute("cnfa.fluency.color_palette_entropy", _clamp01(values["cnfa.fluency.color_palette_entropy"]), confidence=1.0)
        frame.add_attribute("cnfa.fluency.symmetry_score_horizontal", _clamp01(values["cnfa.fluency.symmetry_score_horizontal"]), confidence=1.0)
        frame.add_attribute("cnfa.fractal_dimension", _clamp01(values["cnfa.fractal_dimension"]), confidence=1.0)

        frame.metadata["cnfa_direct_stats"] = {
            "method": "deterministic_opencv_numpy_v1",
            "feature_keys": list(CNFA_DIRECT_STATS_KEYS),
            "known_failure_modes": [
                "2D image statistics cannot infer true 3D geometry",
                "edge metrics are sensitive to blur, resolution, and compression",
                "palette entropy can increase from noise or artifacts",
                "symmetry score measures pixel-level mirror similarity, not semantic symmetry",
                "fractal dimension is a box-counting proxy over Canny edges",
            ],
        }
