"""
Perceptual Color Analysis Module (L0 Proximal).

Ported from student branch: backend/science/math/color.py
Adapted to use level-aware AnalysisFrame API (add_proximal).

Moves away from RGB statistics to CIELAB perceptual space for scientific validity.
This complements (does not replace) the MPIB color features in features.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import numpy as np
from scipy.spatial import ConvexHull

if TYPE_CHECKING:
    from science.core import AnalysisFrame


class ColorAnalyzer:
    """
    Extracts color metrics using the CIELAB colorspace, which aligns
    with human visual perception (unlike RGB/HSV).
    """

    name = "color_stats"
    tier = "L0"
    requires: List[str] = ["lab_image"]
    provides: List[str] = [
        "color.perceptual_lightness",
        "color.lab_volume",
        "color.warmth_ratio",
        "color.lightness_contrast",
    ]

    @staticmethod
    def analyze(frame: "AnalysisFrame") -> None:
        # frame.lab_image is shape (H, W, 3) -> L, a, b
        lab = frame.lab_image
        l_channel = lab[:, :, 0]  # Lightness (0-100)
        a_channel = lab[:, :, 1]  # Green-Red
        b_channel = lab[:, :, 2]  # Blue-Yellow

        # 1. Perceptual Lightness (Mean L*)
        # Scaled to 0-1 for database consistency
        mean_lightness = float(np.mean(l_channel) / 100.0)
        frame.add_proximal("color.perceptual_lightness", mean_lightness,
                           source="color_stats.ColorAnalyzer")

        # 2. Color Volume (Richness)
        # Calculates the volume of the Convex Hull of the pixel distribution in ab space.
        # Higher volume = wider variety of distinct hues/saturations.
        try:
            # Downsample for performance (hull calculation is O(N log N))
            ab_pixels = lab[:, :, 1:].reshape(-1, 2)
            # Take a random sample of 1000 pixels to estimate volume
            if ab_pixels.shape[0] > 1000:
                indices = np.random.choice(ab_pixels.shape[0], 1000, replace=False)
                sample = ab_pixels[indices]
            else:
                sample = ab_pixels

            if len(sample) > 3:
                hull = ConvexHull(sample)
                # Normalize volume roughly (max theoretical area in ab plane is large)
                # A very colorful image might have vol ~3000-5000. We log-scale it.
                vol_score = float(np.log1p(hull.volume) / 10.0)
                frame.add_proximal("color.lab_volume", min(vol_score, 1.0),
                                   source="color_stats.ColorAnalyzer")
            else:
                frame.add_proximal("color.lab_volume", 0.0,
                                   source="color_stats.ColorAnalyzer")
        except Exception:
            frame.add_proximal("color.lab_volume", 0.0,
                               source="color_stats.ColorAnalyzer")

        # 3. Warm/Cool Balance (A-channel dominance)
        # Positive 'a' is Red/Magenta (Warm), Negative 'a' is Green (Cool)
        # Positive 'b' is Yellow (Warm), Negative 'b' is Blue (Cool)
        # We use a simple integration of the 'a' and 'b' channels.

        warm_mask = (a_channel > 0) | (b_channel > 0)
        warm_ratio = float(np.mean(warm_mask))
        frame.add_proximal("color.warmth_ratio", warm_ratio,
                           source="color_stats.ColorAnalyzer")

        # 4. Contrast (Lightness Standard Deviation)
        l_std = float(np.std(l_channel) / 50.0)  # Normalize roughly
        frame.add_proximal("color.lightness_contrast", min(l_std, 1.0),
                           source="color_stats.ColorAnalyzer")
