"""Richer texture & shape via mahotas (MIT) — Haralick, LBP, Zernike.

scikit-image gives GLCM; mahotas adds the full rotation-invariant Haralick
feature set, Local Binary Patterns, and Zernike moments — the mid-level
surface/shape descriptors that carry material and form information (roughness,
regularity, roundness). All MIT-licensed and fast (C-accelerated).

  * Haralick contrast / correlation / entropy / ASM(energy) -> texture-variation,
    surface roughness cues (haptic);
  * LBP histogram entropy -> micro-texture richness;
  * Zernike-moment magnitude -> rotation-invariant shape complexity (geometry).
"""
from __future__ import annotations

import numpy as np

from ..base import AnalyzerAdapter, License, get_gray


class MahotasTextureAdapter(AnalyzerAdapter):
    name = "mahotas_texture"
    tool = "mahotas"
    tool_version = "1.4"
    license_class = License.PERMISSIVE  # MIT
    enable_flag = "enable_mahotas_texture"
    requires = ("mahotas",)
    provides = (
        "cnfa.haptic.haralick_contrast",
        "cnfa.haptic.haralick_correlation",
        "cnfa.haptic.haralick_entropy",
        "cnfa.haptic.haralick_energy",
        "cnfa.haptic.lbp_entropy",
        "cnfa.geometry.zernike_magnitude",
    )

    def _analyze(self, frame) -> None:
        import mahotas
        import mahotas.features as mf

        gray = get_gray(frame)

        # Haralick: 13 features x 4 directions; average over directions.
        # Indices (Haralick 1973): 1=ASM/energy, 2=contrast, 3=correlation,
        # 9=entropy (0-based: 0,1,2,8).
        har = mf.haralick(gray, return_mean=True)
        self.emit(frame, "cnfa.haptic.haralick_energy", float(har[0]))
        self.emit(frame, "cnfa.haptic.haralick_contrast", float(har[1]))
        self.emit(frame, "cnfa.haptic.haralick_correlation", float(har[2]))
        self.emit(frame, "cnfa.haptic.haralick_entropy", float(har[8]))

        # LBP histogram entropy (radius 2, 8 points).
        lbp = mf.lbp(gray, radius=2, points=8)
        p = lbp / (lbp.sum() + 1e-12)
        p = p[p > 0]
        self.emit(frame, "cnfa.haptic.lbp_entropy",
                  float(-(p * np.log2(p)).sum()) if p.size else 0.0, units="bits")

        # Zernike moments: rotation-invariant shape descriptor magnitude.
        try:
            radius = min(gray.shape) // 2
            zern = mf.zernike_moments(gray.astype(np.double), radius, degree=8)
            self.emit(frame, "cnfa.geometry.zernike_magnitude",
                      float(np.linalg.norm(zern)))
        except Exception:
            pass
