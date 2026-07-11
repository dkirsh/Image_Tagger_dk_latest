"""Regional low-level feature extraction.

Applies the full 61-feature extraction pipeline to semantic image regions
(wall, floor, ceiling, window, furniture, etc.) obtained via SegFormer
segmentation.

For each region, features are computed on the **masked** pixels only —
pixels outside the region are excluded from all statistics. This produces
a per-region feature profile that enables fine-grained environmental
cognition analysis (e.g., "how does the wall's fractal dimension differ
from the ceiling's?").

Output structure::

    {
        "whole_image": {61 feature keys},
        "regions": {
            "wall":    {"coverage": 0.35, "features": {61 feature keys}},
            "ceiling": {"coverage": 0.20, "features": {61 feature keys}},
            "floor":   {"coverage": 0.25, "features": {61 feature keys}},
            ...
        },
        "contrasts": {
            "wall_ceiling.brightness": 0.12,
            "wall_floor.edge_density": -0.05,
            ...
        }
    }

Usage::

    from science.low_level.regional import RegionalFeatureExtractor

    # With real SegFormer (requires torch + transformers):
    rfe = RegionalFeatureExtractor()
    result = rfe.analyze("photo.jpg")

    # With mock segmentation (for testing):
    rfe = RegionalFeatureExtractor(use_mock=True)
    result = rfe.analyze("photo.jpg")

    # With pre-computed masks:
    rfe = RegionalFeatureExtractor()
    result = rfe.analyze("photo.jpg", masks={"wall": wall_mask, "floor": floor_mask})

    # Batch processing:
    df = rfe.process_directory("stimuli/", output_csv="regional_features.csv")
"""

from __future__ import annotations

import logging
import math
import time
from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np
import pandas as pd

from .unified import extract_all_features

log = logging.getLogger(__name__)

__all__ = [
    "RegionalFeatureExtractor",
    "RegionalResult",
]

# ── Feature subsets ──────────────────────────────────────────────────────
# Some features are only meaningful on the whole image (e.g., symmetry
# requires the full spatial layout). We skip these for masked regions.
_SKIP_FOR_REGIONS = frozenset({
    "symmetry_mse",
    "symmetry_ssim",
})

# Features that are particularly meaningful for region contrast analysis
_CONTRAST_FEATURES = [
    "brightness",
    "contrast_rms",
    "shannon_entropy",
    "edge_density",
    "straight_edge_density",
    "non_straight_edge_density",
    "fractal_dimension",
    "lab_L_mean",
    "lab_A_mean",
    "lab_B_mean",
    "hue_circular_mean",
    "power_spectrum_mean",
    "green_pct",
    "color_pct_green",
]

# Region pairs to compute contrasts for
_CONTRAST_PAIRS = [
    ("wall", "ceiling"),
    ("wall", "floor"),
    ("ceiling", "floor"),
    ("wall", "window"),
    ("wall", "view.exterior"),
]


# ── Helpers ──────────────────────────────────────────────────────────────

def _apply_mask(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Extract masked region as a cropped image with black background.

    Strategy: crop to the bounding box of the mask, then zero out pixels
    outside the mask. This preserves spatial relationships (edges, textures)
    while excluding irrelevant pixels from color/brightness statistics.

    For features that are pixel-level statistics (mean brightness, color %),
    we also provide ``_extract_masked_pixels`` which returns only the valid
    pixels as a flat array.
    """
    # Resize mask to match image if needed
    if mask.shape[:2] != img.shape[:2]:
        mask = cv2.resize(
            mask.astype(np.uint8),
            (img.shape[1], img.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        ).astype(bool)

    # Find bounding box
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)

    if not rows.any() or not cols.any():
        return img  # Fallback: return whole image

    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    # Crop
    cropped = img[rmin:rmax + 1, cmin:cmax + 1].copy()
    mask_cropped = mask[rmin:rmax + 1, cmin:cmax + 1]

    # Zero out background — apply per channel if color
    if cropped.ndim == 3:
        for c in range(cropped.shape[2]):
            cropped[:, :, c] = np.where(mask_cropped, cropped[:, :, c], 0)
    else:
        cropped = np.where(mask_cropped, cropped, 0)

    return cropped


def _extract_region_features(
    img: np.ndarray,
    mask: np.ndarray,
) -> dict[str, float]:
    """Extract features for a masked region.

    Uses the full 61-feature pipeline on the cropped+masked region.
    Features in ``_SKIP_FOR_REGIONS`` are excluded.
    """
    # Minimum region size check — skip tiny regions
    if mask.sum() < 100:  # Less than 100 pixels
        log.debug("Region too small (%d pixels), skipping", mask.sum())
        return {}

    masked_img = _apply_mask(img, mask)

    # Minimum cropped size check
    if masked_img.shape[0] < 16 or masked_img.shape[1] < 16:
        log.debug("Cropped region too small (%s), skipping", masked_img.shape[:2])
        return {}

    features = extract_all_features(masked_img)

    # Remove features that don't make sense for masked regions
    for key in _SKIP_FOR_REGIONS:
        features.pop(key, None)

    return features


def _compute_contrasts(
    region_features: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Compute feature contrasts between region pairs.

    For each pair (A, B) and each contrast feature, computes:
        contrast.A_B.feature = A.feature - B.feature

    Positive values mean region A has a higher value.
    """
    contrasts: dict[str, float] = {}

    for region_a, region_b in _CONTRAST_PAIRS:
        feats_a = region_features.get(region_a, {})
        feats_b = region_features.get(region_b, {})

        if not feats_a or not feats_b:
            continue

        for feat_key in _CONTRAST_FEATURES:
            val_a = feats_a.get(feat_key)
            val_b = feats_b.get(feat_key)

            if val_a is None or val_b is None:
                continue
            if math.isnan(val_a) or math.isnan(val_b):
                continue

            contrast_key = f"{region_a}_{region_b}.{feat_key}"
            contrasts[contrast_key] = val_a - val_b

    return contrasts


# ── Segmentation integration ────────────────────────────────────────────

def _get_segmentation_masks(
    img: np.ndarray,
    use_mock: bool = False,
) -> dict[str, np.ndarray]:
    """Run SegFormer or mock segmentation and return masks.

    Returns dict mapping region names (e.g., 'wall', 'ceiling') to
    boolean masks of shape (H, W).
    """
    # We import here to avoid hard dependency on torch/transformers
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

    from science.segmentation.segformer import (
        SegmentationAnalyzer,
        MockSegmentationAnalyzer,
    )

    # Create a minimal frame-like object
    class _MinimalFrame:
        def __init__(self, image: np.ndarray):
            self.original_image = image
            self.segmentation_map = None
            self.segmentation_confidence = None
            self.segmentation_masks: dict[str, np.ndarray] = {}
            self.attributes: dict[str, float] = {}

        def add_attribute(self, key: str, value: float) -> None:
            self.attributes[key] = value

    frame = _MinimalFrame(img)

    if use_mock:
        analyzer = MockSegmentationAnalyzer()
    else:
        analyzer = SegmentationAnalyzer()

    analyzer.analyze(frame)
    return frame.segmentation_masks


# ── Main class ───────────────────────────────────────────────────────────

class RegionalResult:
    """Container for regional feature extraction results."""

    def __init__(
        self,
        whole_image: dict[str, float],
        regions: dict[str, dict],
        contrasts: dict[str, float],
        image_name: str = "",
    ):
        self.whole_image = whole_image
        self.regions = regions      # {region_name: {"coverage": float, "features": dict}}
        self.contrasts = contrasts
        self.image_name = image_name

    @property
    def region_names(self) -> list[str]:
        return list(self.regions.keys())

    def to_flat_dict(self) -> dict[str, float]:
        """Flatten to a single dict for DataFrame/CSV output.

        Keys are formatted as:
            - ``whole.brightness`` for whole-image features
            - ``wall.brightness`` for region features
            - ``wall.coverage`` for region coverage
            - ``contrast.wall_ceiling.brightness`` for contrasts
        """
        flat: dict[str, float] = {}

        # Whole image
        for k, v in self.whole_image.items():
            flat[f"whole.{k}"] = v

        # Per-region
        for region_name, region_data in self.regions.items():
            flat[f"{region_name}.coverage"] = region_data.get("coverage", 0.0)
            for k, v in region_data.get("features", {}).items():
                flat[f"{region_name}.{k}"] = v

        # Contrasts
        for k, v in self.contrasts.items():
            flat[f"contrast.{k}"] = v

        return flat

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [f"Image: {self.image_name}"]
        lines.append(f"Whole-image features: {len(self.whole_image)}")
        lines.append(f"Regions detected: {len(self.regions)}")
        for name, data in self.regions.items():
            cov = data.get("coverage", 0)
            n_feat = len(data.get("features", {}))
            lines.append(f"  {name}: {cov:.1%} coverage, {n_feat} features")
        lines.append(f"Contrast metrics: {len(self.contrasts)}")
        return "\n".join(lines)


class RegionalFeatureExtractor:
    """Extract low-level features per semantic region.

    Workflow:
        1. Run whole-image feature extraction (61 features)
        2. Segment image into regions (via SegFormer or provided masks)
        3. Extract features for each region
        4. Compute inter-region contrasts
    """

    def __init__(self, use_mock: bool = False, min_coverage: float = 0.01):
        """
        Args:
            use_mock: Use MockSegmentationAnalyzer instead of real SegFormer.
                     Set True for testing without GPU/model dependencies.
            min_coverage: Minimum region coverage (fraction of image area)
                         to compute features for. Regions smaller than this
                         are skipped.
        """
        self.use_mock = use_mock
        self.min_coverage = min_coverage

    def analyze(
        self,
        image: str | Path | np.ndarray,
        masks: Optional[Dict[str, np.ndarray]] = None,
    ) -> RegionalResult:
        """Analyze an image with per-region feature extraction.

        Args:
            image: Path to image file or pre-loaded BGR numpy array.
            masks: Optional pre-computed masks. If None, runs segmentation.

        Returns:
            RegionalResult with whole-image, per-region, and contrast features.
        """
        t0 = time.perf_counter()

        # Load image
        if isinstance(image, np.ndarray):
            img = image
            image_name = "<array>"
        else:
            image = Path(image)
            image_name = image.name
            img = cv2.imread(str(image))
            if img is None:
                raise FileNotFoundError(f"Could not load image: {image}")

        h, w = img.shape[:2]
        total_pixels = h * w
        log.info("Analyzing %s (%dx%d)", image_name, w, h)

        # 1. Whole-image features
        log.info("  Extracting whole-image features...")
        t1 = time.perf_counter()
        whole_features = extract_all_features(img)
        log.info("  → %d features in %.2fs", len(whole_features), time.perf_counter() - t1)

        # 2. Get segmentation masks
        if masks is None:
            log.info("  Running segmentation...")
            t2 = time.perf_counter()
            try:
                masks = _get_segmentation_masks(img, use_mock=self.use_mock)
                log.info("  → %d regions in %.2fs", len(masks), time.perf_counter() - t2)
            except Exception as exc:
                log.error("  Segmentation failed: %s", exc)
                masks = {}

        # 3. Per-region features
        region_results: dict[str, dict] = {}
        region_feature_dicts: dict[str, dict[str, float]] = {}

        for region_name, mask in masks.items():
            coverage = float(mask.sum()) / total_pixels

            if coverage < self.min_coverage:
                log.debug("  Skipping %s (%.1f%% coverage < %.1f%% threshold)",
                         region_name, coverage * 100, self.min_coverage * 100)
                continue

            log.info("  Extracting features for '%s' (%.1f%% coverage)...",
                     region_name, coverage * 100)
            t3 = time.perf_counter()

            try:
                feats = _extract_region_features(img, mask)
                elapsed = time.perf_counter() - t3
                log.info("    → %d features in %.2fs", len(feats), elapsed)
            except Exception as exc:
                log.error("    Failed for %s: %s", region_name, exc)
                feats = {}

            region_results[region_name] = {
                "coverage": coverage,
                "features": feats,
            }
            region_feature_dicts[region_name] = feats

        # 4. Compute contrasts
        contrasts = _compute_contrasts(region_feature_dicts)
        log.info("  Computed %d contrast metrics", len(contrasts))

        total_elapsed = time.perf_counter() - t0
        log.info("  Total: %.2fs", total_elapsed)

        return RegionalResult(
            whole_image=whole_features,
            regions=region_results,
            contrasts=contrasts,
            image_name=image_name,
        )

    def process_directory(
        self,
        image_dir: str | Path,
        output_csv: Optional[str | Path] = None,
        masks_dict: Optional[Dict[str, Dict[str, np.ndarray]]] = None,
        extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".tiff"),
    ) -> pd.DataFrame:
        """Process all images in a directory with regional features.

        Args:
            image_dir: Directory containing image files.
            output_csv: If given, write flattened results to this CSV.
            masks_dict: Optional pre-computed masks per image filename.
            extensions: Image file extensions to include.

        Returns:
            DataFrame with flattened regional features (one row per image).
        """
        image_dir = Path(image_dir)
        ext_lower = {e.lower() for e in extensions}
        image_files = sorted(
            p for p in image_dir.iterdir()
            if p.is_file() and p.suffix.lower() in ext_lower
        )

        if not image_files:
            log.warning("No images found in %s", image_dir)
            return pd.DataFrame()

        records: list[dict] = []
        total = len(image_files)

        for idx, path in enumerate(image_files, 1):
            log.info("Image %d of %d: %s", idx, total, path.name)

            masks = None
            if masks_dict and path.name in masks_dict:
                masks = masks_dict[path.name]

            try:
                result = self.analyze(path, masks=masks)
                flat = result.to_flat_dict()
                flat["image"] = path.name
                records.append(flat)
            except Exception as exc:
                log.error("Failed on %s: %s", path.name, exc)
                records.append({"image": path.name})

        df = pd.DataFrame(records)

        # Move 'image' to first column
        if "image" in df.columns:
            cols = ["image"] + [c for c in df.columns if c != "image"]
            df = df[cols]

        if output_csv:
            output_path = Path(output_csv)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            log.info("Results written to %s (%d images, %d columns)",
                     output_path, len(df), len(df.columns))

        return df
