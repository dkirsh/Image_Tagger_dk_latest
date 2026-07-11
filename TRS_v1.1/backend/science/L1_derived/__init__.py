"""
L1 Derived — explicit formulas over L0 features.

This package contains all L1 (derived) analyzers for the CNfA pipeline.
L1 features satisfy the inclusion test: "Is this an explicit, documented
formula over L0 features with a literature citation?"

Submodules
----------
complexity     Visual complexity (Shannon entropy, spatial entropy, edge density)
naturalness    Naturalness proxies (green/blue/earth hue ratios)
fluency        Perceptual fluency (inverse of clutter/complexity)
biophilia      Biophilia composite index (naturalness + fractal signals)
summary        High-level composite indices (visual richness, organized complexity)
"""

from science.L1_derived.complexity import ComplexityAnalyzer
from science.L1_derived.naturalness import NaturalnessAnalyzer
from science.L1_derived.fluency import FluencyAnalyzer
from science.L1_derived.biophilia import BiophiliaAnalyzer
from science.L1_derived.summary import SummaryAnalyzer

__all__ = [
    "ComplexityAnalyzer",
    "NaturalnessAnalyzer",
    "FluencyAnalyzer",
    "BiophiliaAnalyzer",
    "SummaryAnalyzer",
]
