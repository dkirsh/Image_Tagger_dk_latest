"""
GLCM Texture Analysis (L0 Proximal).

Ported from student branch: backend/science/math/glcm.py
Adapted to use level-aware AnalysisFrame API (add_proximal).

Computes multi-scale GLCM texture features at two distances:
  - Distance 1: Micro-texture (fine detail)
  - Distance 5: Macro-structure (coarse patterns)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage.transform import resize as sk_resize

if TYPE_CHECKING:
    from science.core import AnalysisFrame


class TextureAnalyzer:
    """
    GLCM Texture Analysis.
    Updated to expose multi-scale texture detection (near vs far).
    """

    name = "texture_glcm"
    tier = "L0"
    requires: List[str] = ["gray_image"]
    provides: List[str] = [
        "texture.micro.contrast",
        "texture.micro.homogeneity",
        "texture.macro.contrast",
        "texture.macro.homogeneity",
    ]

    @staticmethod
    def analyze(frame: "AnalysisFrame") -> None:
        gray = frame.gray_image
        # Downsample for performance
        h, w = gray.shape
        if h > 512:
            scale = 512 / h
            new_h, new_w = int(h * scale), int(w * scale)
            gray = (sk_resize(gray, (new_h, new_w), anti_aliasing=True) * 255).astype(np.uint8)

        # Quantize to 64 levels
        gray = (gray // 4).astype(np.uint8)

        # Analyze at two distances: 1 (Micro-texture) and 5 (Macro-structure)
        distances = [1, 5]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]

        glcm = graycomatrix(gray, distances=distances, angles=angles,
                            levels=64, symmetric=True, normed=True)

        # Extract features and average across angles
        # property array shape: (num_distances, num_angles)
        contrast = graycoprops(glcm, 'contrast')
        homogeneity = graycoprops(glcm, 'homogeneity')

        # Micro-Texture (Distance 1)
        frame.add_proximal("texture.micro.contrast", float(np.mean(contrast[0])),
                           source="glcm.TextureAnalyzer")
        frame.add_proximal("texture.micro.homogeneity", float(np.mean(homogeneity[0])),
                           source="glcm.TextureAnalyzer")

        # Macro-Texture (Distance 5)
        frame.add_proximal("texture.macro.contrast", float(np.mean(contrast[1])),
                           source="glcm.TextureAnalyzer")
        frame.add_proximal("texture.macro.homogeneity", float(np.mean(homogeneity[1])),
                           source="glcm.TextureAnalyzer")
