"""
L0 Proximal — transparent pixel-level computations.

This package contains all L0 (proximal) feature extractors for the CNfA
pipeline. L0 features satisfy the inclusion test: "Can a reader reproduce
this number by reading the code and doing the math by hand on the pixel values?"

Submodules
----------
features        MPIB Berlin feature set (brightness, contrast, entropy, edges, etc.)
matlab_ports    MATLAB-ported features (CIELAB, fractal dimension, LGN, etc.)
unified         Combined extraction API for all ~50+ low-level features
regional        Per-region feature extraction using segmentation masks
glcm            GLCM texture analysis (micro/macro scale)
spatial_frequency  Fourier-domain band power analysis
color_stats     CIELAB perceptual color metrics (volume, warmth, lightness)
cli             Command-line interface for batch processing
"""

from science.L0_proximal.unified import extract_all_features, LowLevelFeatureExtractor
from science.L0_proximal.regional import RegionalFeatureExtractor, RegionalResult
from science.L0_proximal.color_stats import ColorAnalyzer
from science.L0_proximal.glcm import TextureAnalyzer
from science.L0_proximal.spatial_frequency import SpatialFrequencyAnalyzer

__all__ = [
    "extract_all_features",
    "LowLevelFeatureExtractor",
    "RegionalFeatureExtractor",
    "RegionalResult",
    "ColorAnalyzer",
    "TextureAnalyzer",
    "SpatialFrequencyAnalyzer",
]
