"""
Approximate 2.5D isovist analysis based on a depth map.

This is an intentionally cautious implementation: until a high-quality
depth model is wired in, we treat the outputs as low-confidence proxies.

Ported to L2_structural with add_structural() API.
"""

from __future__ import annotations

import numpy as np

from science.core import AnalysisFrame
from science.contracts import fail, check_requirements


class Isovist25DAnalyzer:
    name = "isovist_25d"
    tier = "L2"
    requires = ["depth_map"]
    provides = [
        "isovist.area_25d",
        "isovist.compactness_25d",
        "isovist.confidence",
    ]

    @staticmethod
    def _perimeter(mask: np.ndarray) -> float:
        from scipy.ndimage import binary_erosion

        eroded = binary_erosion(mask)
        border = mask ^ eroded
        return float(border.sum())

    @classmethod
    def analyze(cls, frame: AnalysisFrame) -> None:
        depth = frame.depth_map
        if depth is None:
            fail(frame, cls.name, "no depth_map available")
            return

        _MODEL_VERSION = "depth_isovist_25d_v1"

        # Simple near-space threshold as a proxy for "occupied" region.
        thresh = np.percentile(depth, 60.0)
        free = depth < thresh
        area = free.mean()
        perim = cls._perimeter(free)
        compactness = (4.0 * np.pi * area) / (perim ** 2 + 1e-9)

        # Low confidence until depth model is validated.
        confidence = 0.4

        frame.add_structural("isovist.area_25d", float(area), model_version=_MODEL_VERSION, source="isovist_25d.Isovist25DAnalyzer.analyze")
        frame.add_structural("isovist.compactness_25d", float(compactness), model_version=_MODEL_VERSION, source="isovist_25d.Isovist25DAnalyzer.analyze")
        frame.metadata["isovist_25d"] = {
            "threshold_percentile": 60.0,
            "confidence": confidence,
        }
        frame.add_structural("isovist.confidence", confidence, model_version=_MODEL_VERSION, source="isovist_25d.Isovist25DAnalyzer.analyze")
