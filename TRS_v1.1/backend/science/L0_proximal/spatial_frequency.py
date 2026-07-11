"""
Global spatial frequency analysis for architectural images (L0 Proximal).

Ported from student branch: backend/science/math/spatial_frequency.py
Adapted to use level-aware AnalysisFrame API (add_proximal).

This module computes band-limited power in the Fourier domain as a
baseline for more sophisticated (regional, oriented) measures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import numpy as np

from science.contracts import fail

if TYPE_CHECKING:
    from science.core import AnalysisFrame


class SpatialFrequencyAnalyzer:
    """
    Computes low/mid/high band power and a simple low/high ratio from
    the grayscale image. This is deliberately conservative and fast.
    """

    name = "spatial_frequency"
    tier = "L0"
    requires: List[str] = ["gray_image"]
    provides: List[str] = [
        "spatial_freq.low_power",
        "spatial_freq.mid_power",
        "spatial_freq.high_power",
        "spatial_freq.low_high_ratio",
    ]

    @staticmethod
    def _radial_power_spectrum(gray: np.ndarray) -> tuple:
        # Convert to float and compute FFT
        f = np.fft.fft2(gray.astype(np.float32))
        fshift = np.fft.fftshift(f)
        ps = np.abs(fshift) ** 2

        h, w = ps.shape
        cy, cx = h // 2, w // 2
        y, x = np.indices((h, w))
        r = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        r = r / r.max()
        return ps, r

    @classmethod
    def analyze(cls, frame: "AnalysisFrame") -> None:
        gray = frame.gray_image
        if gray is None:
            fail(frame, cls.name, "missing gray_image")
            return

        ps, r = cls._radial_power_spectrum(gray)

        # Define crude bands: [0, 0.33), [0.33, 0.66), [0.66, 1.0]
        low_mask = r < 0.33
        mid_mask = (r >= 0.33) & (r < 0.66)
        high_mask = r >= 0.66

        low_power = float(ps[low_mask].mean()) if np.any(low_mask) else 0.0
        mid_power = float(ps[mid_mask].mean()) if np.any(mid_mask) else 0.0
        high_power = float(ps[high_mask].mean()) if np.any(high_mask) else 0.0

        denom = high_power if high_power > 1e-6 else 1e-6
        low_high_ratio = float(low_power / denom)

        frame.add_proximal("spatial_freq.low_power", low_power,
                           source="spatial_frequency.SpatialFrequencyAnalyzer")
        frame.add_proximal("spatial_freq.mid_power", mid_power,
                           source="spatial_frequency.SpatialFrequencyAnalyzer")
        frame.add_proximal("spatial_freq.high_power", high_power,
                           source="spatial_frequency.SpatialFrequencyAnalyzer")
        frame.add_proximal("spatial_freq.low_high_ratio", low_high_ratio,
                           source="spatial_frequency.SpatialFrequencyAnalyzer")
