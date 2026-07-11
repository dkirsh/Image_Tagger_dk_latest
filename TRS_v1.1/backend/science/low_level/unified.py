"""Unified low-level image feature extraction.

Combines:
- **MPIB Berlin features** (21 features) — from ``features.py``
- **MATLAB-ported features** (30+ features) — from ``matlab_ports.py``
- **Total**: ~50+ features per image

Usage::

    from science.low_level.unified import extract_all_features

    # Single image
    features = extract_all_features('path/to/image.jpg')
    # → dict with ~50 feature keys

    # Batch processing
    extractor = LowLevelFeatureExtractor()
    df = extractor.process_directory('stimuli/', output_csv='features.csv')
"""

from __future__ import annotations

import logging
import time
import warnings
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pandas as pd

from .matlab_ports import extract_matlab_ported_features

log = logging.getLogger(__name__)

__all__ = [
    "extract_all_features",
    "LowLevelFeatureExtractor",
]


# ---------------------------------------------------------------------------
# Inline MPIB feature functions
# ---------------------------------------------------------------------------
# The original MPIB repo (low-level-image-features/main.py) is a CLI script
# with no importable API.  We re-wrap its pure functions here so that
# ``unified.py`` has zero dependency on that repo's layout.
# ---------------------------------------------------------------------------

def _mpib_brightness(img: np.ndarray) -> tuple[float, float]:
    """Average brightness and SD (MPIB ``get_brightness``)."""
    flat = img.ravel().astype(np.float64) / 255.0
    return float(np.mean(flat)), float(np.std(flat))


def _mpib_contrast(img: np.ndarray) -> float:
    """RMS contrast of grayscale (MPIB ``get_contrast``)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    return float(gray.std()) / 100.0


def _mpib_entropy(img: np.ndarray) -> float:
    """Shannon entropy (MPIB ``get_entropy``)."""
    from skimage import measure  # type: ignore[import-untyped]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    return float(measure.shannon_entropy(gray))


def _mpib_edge_density(img: np.ndarray, sigma: float = 0.33) -> tuple[float, float, float]:
    """Straight, non-straight edge density and total (MPIB ``get_edge_density``)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    v = float(np.median(gray))
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))

    edged_high = cv2.Canny(gray, int(lower * 0.8), int(upper * 0.8))
    edged_low = cv2.Canny(gray, int(lower * 1.6), int(upper * 1.6))

    edges = np.zeros_like(edged_high, dtype=np.uint8)
    edges[edged_low == 255] = 2
    edges[edged_high == 255] = 1

    lines = cv2.HoughLinesP(edged_high, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)
    straight_mask = np.zeros_like(gray, dtype=np.uint8)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(straight_mask, (x1, y1), (x2, y2), 255, 1)

    total = edges.size
    sed = float(np.sum((straight_mask > 0) & (edges > 0))) / total
    nsed = float(np.sum((straight_mask == 0) & (edges > 0))) / total
    ed = float(edges.mean())
    return sed, nsed, ed


def _mpib_hsv(img: np.ndarray) -> dict[str, float]:
    """HSV channel means and SDs (MPIB ``get_hsv_values``)."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) if img.ndim == 3 else img
    return {
        "hue_mean": float(np.mean(hsv[:, :, 0])),
        "hue_sd": float(np.std(hsv[:, :, 0])),
        "saturation_mean": float(np.mean(hsv[:, :, 1])),
        "saturation_sd": float(np.std(hsv[:, :, 1])),
        "value_mean": float(np.mean(hsv[:, :, 2])),
        "value_sd": float(np.std(hsv[:, :, 2])),
    }


def _mpib_color_ratios(img: np.ndarray) -> dict[str, float]:
    """Dominant-channel colour classification (MPIB ``classify_image_colors``).

    Vectorised reimplementation (the original uses nested Python loops).
    """
    if img.ndim == 2:
        return {"blue_pct": 0.0, "green_pct": 0.0, "red_pct": 0.0, "neutral_pct": 1.0}

    bgr = img.astype(np.int16)
    b, g, r = bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2]
    n = float(img.shape[0] * img.shape[1])

    is_blue = (b > g) & (b > r)
    is_green = (g > b) & (g > r) & ~is_blue
    is_red = (r > b) & (r > g) & ~is_blue & ~is_green
    is_neutral = ~is_blue & ~is_green & ~is_red

    return {
        "blue_pct": float(is_blue.sum()) / n,
        "green_pct": float(is_green.sum()) / n,
        "red_pct": float(is_red.sum()) / n,
        "neutral_pct": float(is_neutral.sum()) / n,
    }


def _mpib_symmetry(img: np.ndarray) -> dict[str, float]:
    """Horizontal-flip symmetry via MSE and SSIM (MPIB)."""
    from skimage.metrics import structural_similarity as ssim  # type: ignore[import-untyped]

    flipped = cv2.flip(img, 1)
    err = float(np.sum((img.astype(np.float64) - flipped.astype(np.float64)) ** 2))
    mse = err / float(img.shape[0] * img.shape[1])

    # SSIM – channel_axis required in modern skimage
    try:
        s = float(ssim(img, flipped, channel_axis=2 if img.ndim == 3 else None, win_size=3))
    except TypeError:
        s = float(ssim(img, flipped, multichannel=(img.ndim == 3), win_size=3))
    return {"symmetry_mse": mse, "symmetry_ssim": s}


def _mpib_power_spectrum(img: np.ndarray) -> float:
    """Mean power spectrum (MPIB ``get_power_spectrum``)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    f = np.fft.fft2(gray.astype(np.float64))
    fshift = np.fft.fftshift(f)
    ps = np.abs(fshift) ** 2
    return float(np.mean(ps))


def _extract_mpib_features(img: np.ndarray) -> dict[str, float]:
    """Extract MPIB Berlin low-level features (21 keys).

    Wraps the individual functions with per-feature error handling so that a
    failure in one does not block the rest.
    """
    feats: dict[str, float] = {}
    nan = float("nan")

    # Brightness
    try:
        b, sd_b = _mpib_brightness(img)
        feats["brightness"] = b
        feats["brightness_sd"] = sd_b
    except Exception:
        feats["brightness"] = feats["brightness_sd"] = nan

    # Contrast
    try:
        feats["contrast_rms"] = _mpib_contrast(img)
    except Exception:
        feats["contrast_rms"] = nan

    # Entropy
    try:
        feats["shannon_entropy"] = _mpib_entropy(img)
    except Exception:
        feats["shannon_entropy"] = nan

    # Edge density
    try:
        sed, nsed, ed = _mpib_edge_density(img)
        feats["straight_edge_density"] = sed
        feats["non_straight_edge_density"] = nsed
        feats["edge_density"] = ed
    except Exception:
        feats["straight_edge_density"] = nan
        feats["non_straight_edge_density"] = nan
        feats["edge_density"] = nan

    # HSV
    try:
        feats.update(_mpib_hsv(img))
    except Exception:
        for k in ("hue_mean", "hue_sd", "saturation_mean", "saturation_sd", "value_mean", "value_sd"):
            feats[k] = nan

    # Color ratios
    try:
        feats.update(_mpib_color_ratios(img))
    except Exception:
        for k in ("blue_pct", "green_pct", "red_pct", "neutral_pct"):
            feats[k] = nan

    # Symmetry
    try:
        feats.update(_mpib_symmetry(img))
    except Exception:
        feats["symmetry_mse"] = nan
        feats["symmetry_ssim"] = nan

    # Power spectrum
    try:
        feats["power_spectrum_mean"] = _mpib_power_spectrum(img)
    except Exception:
        feats["power_spectrum_mean"] = nan

    return feats


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_all_features(image_path: str | Path | np.ndarray) -> dict[str, float]:
    """Extract all low-level features from an image.

    Combines MPIB Berlin features (~21 keys) and MATLAB-ported features
    (~30+ keys) into a single flat dictionary.

    Parameters
    ----------
    image_path : str | Path | np.ndarray
        Path to an image file **or** a pre-loaded BGR ``np.ndarray``.

    Returns
    -------
    dict[str, float]
        ~50+ feature keys with ``float`` values.
        Features that fail to compute are set to ``NaN``.

    Raises
    ------
    FileNotFoundError
        If *image_path* is a path and the file cannot be loaded.
    """
    if isinstance(image_path, np.ndarray):
        img = image_path
    else:
        img = cv2.imread(str(image_path))
        if img is None:
            raise FileNotFoundError(f"Could not load image: {image_path}")

    features: dict[str, float] = {}
    features.update(_extract_mpib_features(img))
    features.update(extract_matlab_ported_features(img))
    return features


class LowLevelFeatureExtractor:
    """Batch processor for low-level image features.

    Example::

        extractor = LowLevelFeatureExtractor()
        df = extractor.process_directory('stimuli/', output_csv='features.csv')
        print(df.head())
    """

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def process_single(self, image_path: str | Path) -> dict[str, float]:
        """Process a single image file and return its feature dictionary.

        Parameters
        ----------
        image_path : str | Path
            Path to an image file.

        Returns
        -------
        dict[str, float]
            Feature dictionary (same keys as ``extract_all_features``).
        """
        return extract_all_features(image_path)

    def process_directory(
        self,
        image_dir: str | Path,
        output_csv: Optional[str | Path] = None,
        extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".tiff"),
    ) -> pd.DataFrame:
        """Process all images in *image_dir* and return a ``DataFrame``.

        Parameters
        ----------
        image_dir : str | Path
            Directory containing image files.
        output_csv : str | Path | None
            If given, write results to this CSV file.
        extensions : tuple[str, ...]
            Image file extensions to include (case-insensitive).

        Returns
        -------
        pd.DataFrame
            One row per image.  The first column is ``image`` (filename);
            remaining columns are feature values.
        """
        image_dir = Path(image_dir)
        if not image_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {image_dir}")

        ext_lower = {e.lower() for e in extensions}
        image_files = sorted(
            p for p in image_dir.iterdir()
            if p.is_file() and p.suffix.lower() in ext_lower
        )

        if not image_files:
            log.warning("No images found in %s with extensions %s", image_dir, extensions)
            return pd.DataFrame()

        records: list[dict[str, object]] = []
        total = len(image_files)

        for idx, path in enumerate(image_files, 1):
            log.info("Processing image %d of %d: %s", idx, total, path.name)
            t0 = time.perf_counter()

            try:
                feats = extract_all_features(str(path))
            except Exception as exc:  # noqa: BLE001
                log.error("Failed on %s: %s", path.name, exc)
                feats = {}

            elapsed = time.perf_counter() - t0
            log.info("  → %d features in %.2fs", len(feats), elapsed)

            records.append({"image": path.name, **feats})

        df = pd.DataFrame(records)

        if output_csv is not None:
            output_path = Path(output_csv)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            log.info("Results written to %s", output_path)

        return df
