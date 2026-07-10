"""Adapter for scikit-image (BSD) texture and shape primitives.

  * GLCM (grey-level co-occurrence matrix) via feature.graycomatrix /
    graycoprops -> contrast, homogeneity, energy, correlation. Haralick's
    classic texture statistics (Haralick, Shanmugam & Dinstein, 1973).
  * shape_index (Koenderink & van Doorn, 1992) -> a local-curvature proxy for
    curvilinearity, the approach/avoidance-relevant contour property.

All arrays are made writable (compat.writable_gray) because the Cython GLCM
loop rejects the read-only buffers that PIL conversions produce.
"""
from __future__ import annotations

import numpy as np

from ..base import AnalyzerAdapter, License, clip01, get_gray


class SkimageTextureAdapter(AnalyzerAdapter):
    name = "skimage_texture"
    tool = "scikit-image"
    tool_version = "0.2x"
    license_class = License.PERMISSIVE  # BSD
    enable_flag = "enable_skimage_texture"
    requires = ("skimage",)
    provides = (
        "cnfa.haptic.texture_variation_index",
        "cnfa.haptic.glcm_homogeneity",
        "cnfa.haptic.glcm_energy",
        "cnfa.haptic.glcm_correlation",
        "cnfa.geometry.curvilinearity",
    )

    def _analyze(self, frame) -> None:
        from skimage.feature import graycomatrix, graycoprops, shape_index

        gray = get_gray(frame)  # writable uint8

        # Rotation-averaged GLCM over four directions at distance 1.
        angles = [0.0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
        glcm = graycomatrix(gray, distances=[1], angles=angles,
                            levels=256, symmetric=True, normed=True)
        contrast = float(graycoprops(glcm, "contrast").mean())
        homogeneity = float(graycoprops(glcm, "homogeneity").mean())
        energy = float(graycoprops(glcm, "energy").mean())
        correlation = float(graycoprops(glcm, "correlation").mean())

        self.emit(frame, "cnfa.haptic.texture_variation_index", contrast,
                  units="GLCM contrast")
        self.emit(frame, "cnfa.haptic.glcm_homogeneity", homogeneity)
        self.emit(frame, "cnfa.haptic.glcm_energy", energy)
        self.emit(frame, "cnfa.haptic.glcm_correlation", correlation)

        # Curvilinearity proxy: mean |shape index| over non-flat pixels,
        # normalised to [0,1] (shape_index is in [-1, 1]).
        si = shape_index(gray.astype(np.float64), sigma=1.0)
        finite = si[np.isfinite(si)]
        if finite.size:
            curvi = clip01(float(np.abs(finite).mean()))
            self.emit(frame, "cnfa.geometry.curvilinearity", curvi,
                      units="mean|shape_index|",
                      extra={"note": "proxy; 0=planar, 1=strongly curved"})
