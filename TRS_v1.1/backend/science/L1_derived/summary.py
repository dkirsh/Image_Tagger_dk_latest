"""
Science Summary Composites (L1 Derived).

Ported from student branch: backend/science/summary.py
Adapted to use level-aware AnalysisFrame API (add_derived with formula=).

High-level science composites for Image Tagger v3.3.

This module defines ScienceSummaryAnalyzer (aliased as SummaryAnalyzer),
which computes:

  * science.visual_richness        (0.0–1.0)
  * science.organized_complexity   (0.0–1.0)
  * science.visual_richness_bin    (0=low, 1=mid, 2=high)
  * science.organized_complexity_bin (0=low, 1=mid, 2=high)

It is designed to sit on top of the lower-level analyzers in
science.L0_proximal and science.L1_derived.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

if TYPE_CHECKING:
    from science.core import AnalysisFrame


COLOR_KEYS: List[str] = []
COMPLEXITY_KEYS: List[str] = []
TEXTURE_KEYS: List[str] = ['texture.macro.homogeneity', 'texture.micro.contrast', 'texture.micro.homogeneity', 'texture.macro.contrast']
FRACTAL_KEYS: List[str] = ['fractal.D']


def _safe_avg(frame: "AnalysisFrame", keys: Sequence[str]) -> Optional[float]:
    values = [frame.attributes[k] for k in keys if k in frame.attributes]
    if not values:
        return None
    return float(sum(values) / len(values))


def _clamp01(x: float) -> float:
    if math.isnan(x):
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _to_bin(x: float) -> int:
    if x < 0.33:
        return 0
    if x < 0.66:
        return 1
    return 2


@dataclass
class SummaryAnalyzer:
    """
    Lightweight composite index builder.

    The goal is not to be "the final word" on the science, but to
    provide stable, BN-friendly scalars and discrete bins.
    """

    name: str = "summary"
    tier: str = "L1"
    requires: List[str] = None  # type: ignore[assignment]
    provides: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.requires is None:
            self.requires = []
        if self.provides is None:
            self.provides = [
                "science.visual_richness",
                "science.organized_complexity",
                "science.visual_richness_bin",
                "science.organized_complexity_bin",
            ]

    def analyze(self, frame: "AnalysisFrame") -> None:
        # 1. Visual richness: color + texture + a complexity touch.
        color = _safe_avg(frame, COLOR_KEYS)
        texture = _safe_avg(frame, TEXTURE_KEYS)
        comp = _safe_avg(frame, COMPLEXITY_KEYS)

        components = [v for v in (color, texture, comp) if v is not None]
        if components:
            raw_vr = sum(components) / len(components)
            vr = _clamp01(raw_vr)
            frame.add_derived("science.visual_richness", vr,
                              formula="mean(color_avg, texture_avg, complexity_avg)",
                              source="summary.SummaryAnalyzer",
                              confidence=1.0)
            frame.add_derived("science.visual_richness_bin", float(_to_bin(vr)),
                              formula="bin(visual_richness, [0.33, 0.66])",
                              source="summary.SummaryAnalyzer",
                              confidence=1.0)

        # 2. Organized complexity: complexity + fractals (if any).
        comp2 = _safe_avg(frame, COMPLEXITY_KEYS)
        frac = _safe_avg(frame, FRACTAL_KEYS)

        components2 = [v for v in (comp2, frac) if v is not None]
        if components2:
            raw_oc = sum(components2) / len(components2)
            oc = _clamp01(raw_oc)
            frame.add_derived("science.organized_complexity", oc,
                              formula="mean(complexity_avg, fractal_avg)",
                              source="summary.SummaryAnalyzer",
                              confidence=1.0)
            frame.add_derived("science.organized_complexity_bin", float(_to_bin(oc)),
                              formula="bin(organized_complexity, [0.33, 0.66])",
                              source="summary.SummaryAnalyzer",
                              confidence=1.0)


# Backward-compatible alias
ScienceSummaryAnalyzer = SummaryAnalyzer
