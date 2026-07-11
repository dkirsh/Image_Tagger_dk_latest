"""
AnalysisFrame — the unit of analysis for the CNfA image tagger pipeline.

Every computed attribute is tagged with an epistemic level (L0–L3) and
carries provenance metadata.  See LEVELS.md for inclusion conditions.

Levels:
    L0  Proximal:    transparent computation on pixels, no learned weights
    L1  Derived:     explicit formula over L0 features, with citation
    L2  Structural:  learned model with transparent I/O (masks, depth, labels)
    L3  Semantic:    human or VLM judgment — hypotheses, not measurements
    L4  Causal:      discovered relationships (research output, not computed here)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class EpistemicLevel(str, Enum):
    """Epistemic level for a computed attribute."""
    L0_PROXIMAL = "L0"
    L1_DERIVED = "L1"
    L2_STRUCTURAL = "L2"
    L3_SEMANTIC = "L3"
    L4_CAUSAL = "L4"


@dataclass
class AttributeRecord:
    """
    A single computed attribute with full provenance.

    Attributes:
        value:      The numeric value.
        level:      Epistemic level (L0–L4).
        source:     Module or function that produced this value.
        confidence: How reliable this measurement is (0.0–1.0).
        metadata:   Additional provenance (formula, model version, prompt hash, etc.)
    """
    value: float
    level: EpistemicLevel
    source: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisFrame:
    """
    Standard unit of analysis for the CNfA pipeline.

    Holds the original image, derived representations (grayscale, edges, LAB),
    segmentation masks, depth map, and all computed attributes with provenance.

    Usage:
        frame = AnalysisFrame(image_id=42, original_image=rgb_array)
        # L0: transparent computation
        frame.add_proximal("fractal_dimension", 1.37, source="matlab_ports.compute_fractal_dimension")
        # L1: formula over L0
        frame.add_derived("complexity_composite", 0.65, formula="0.4*edge_density + 0.3*entropy + 0.3*spectral_slope")
        # L2: learned model
        frame.add_structural("room_type", 0.92, model_version="places365-resnet50-v1.0")
        # L3: VLM judgment (hypothesis!)
        frame.add_hypothesis("cognitive_mystery", 0.7, source="gpt-4o-2024-08-06", prompt_hash="a3b1c9")
    """
    image_id: int
    original_image: np.ndarray  # RGB, uint8, shape (H, W, 3)

    # ---------- derived representations (populated lazily in __post_init__) ----------
    gray_image: Optional[np.ndarray] = None
    lab_image: Optional[np.ndarray] = None
    edges: Optional[np.ndarray] = None

    # ---------- structural representations (populated by L2 analyzers) ----------
    depth_map: Optional[np.ndarray] = None
    segmentation_map: Optional[np.ndarray] = None
    segmentation_masks: Dict[str, np.ndarray] = field(default_factory=dict)
    segmentation_confidence: Optional[np.ndarray] = None
    wall_regions: List[Any] = field(default_factory=list)

    # ---------- attributes with provenance ----------
    _records: Dict[str, AttributeRecord] = field(default_factory=dict)

    # ---------- flat access (backward-compatible) ----------
    attributes: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Legacy alias
    metrics: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            import cv2
        except ImportError:
            logger.warning("cv2 not available — grayscale and edges will not be computed")
            self.metrics = self.attributes
            return

        if self.gray_image is None:
            self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)

        if self.edges is None:
            self.edges = cv2.Canny(self.gray_image, 50, 150, L2gradient=True)

        if self.lab_image is None:
            try:
                from skimage import color
                self.lab_image = color.rgb2lab(self.original_image)
            except ImportError:
                # Fall back to cv2 LAB (less accurate but functional)
                bgr = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2BGR)
                self.lab_image = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

        # Legacy alias — writes to attributes are unified
        self.metrics = self.attributes

    # -------------------------------------------------------------------------
    # Level-aware attribute setters
    # -------------------------------------------------------------------------

    def add_proximal(
        self,
        key: str,
        value: float,
        source: str = "",
        confidence: float = 1.0,
        **extra_metadata,
    ) -> None:
        """
        Add an L0 (proximal) attribute.

        L0 inclusion test: Can a reader reproduce this number by reading the
        code and doing the math by hand on the pixel values?

        Args:
            key:        Attribute name (e.g. "fractal_dimension").
            value:      Numeric value.
            source:     Function/module that computed this (e.g. "matlab_ports.compute_fractal_dimension").
            confidence: Measurement reliability (default 1.0 for deterministic computations).
        """
        self._set(key, value, EpistemicLevel.L0_PROXIMAL, source, confidence, extra_metadata)

    def add_derived(
        self,
        key: str,
        value: float,
        formula: str = "",
        source: str = "",
        confidence: float = 1.0,
        **extra_metadata,
    ) -> None:
        """
        Add an L1 (derived) attribute.

        L1 inclusion test: Is this an explicit, documented formula over L0
        features with a literature citation?

        Args:
            key:        Attribute name (e.g. "complexity_composite").
            value:      Numeric value.
            formula:    The formula as a string (e.g. "0.4*edge_density + 0.3*entropy + 0.3*spectral_slope").
            source:     Module that computed this.
            confidence: How well-validated the formula is (default 1.0).
        """
        meta = dict(extra_metadata)
        if formula:
            meta["formula"] = formula
        self._set(key, value, EpistemicLevel.L1_DERIVED, source, confidence, meta)

    def add_structural(
        self,
        key: str,
        value: float,
        model_version: str = "",
        source: str = "",
        confidence: float = 1.0,
        **extra_metadata,
    ) -> None:
        """
        Add an L2 (structural) attribute.

        L2 inclusion test: Does this require a trained model, but its output
        is a transparent structure (mask, depth, bounding box, class label)?

        Args:
            key:            Attribute name (e.g. "region.wall.coverage").
            value:          Numeric value.
            model_version:  Model checkpoint identifier (e.g. "nvidia/segformer-b5-finetuned-ade-640-640").
            source:         Module that computed this.
            confidence:     Model confidence for this prediction.
        """
        meta = dict(extra_metadata)
        if model_version:
            meta["model_version"] = model_version
        self._set(key, value, EpistemicLevel.L2_STRUCTURAL, source, confidence, meta)

    def add_hypothesis(
        self,
        key: str,
        value: float,
        source: str = "",
        prompt_hash: str = "",
        prompt_version: str = "",
        model_name: str = "",
        confidence: float = 0.5,
        **extra_metadata,
    ) -> None:
        """
        Add an L3 (semantic/cognitive) attribute.

        L3 inclusion test: Does this require a judgment about meaning,
        experience, or quality — from a human rater or VLM?

        WARNING: L3 features are HYPOTHESES, not measurements.  They are
        dependent variables.  Never use L3 as a predictor of another L3
        without explicit justification.

        Args:
            key:             Attribute name (e.g. "cognitive.mystery").
            value:           Numeric value (typically 0.0–1.0).
            source:          Who/what produced this ("gpt-4o-2024-08-06", "human_rater_042").
            prompt_hash:     Hash of the prompt text (for VLM reproducibility).
            prompt_version:  Version label of the prompt (e.g. "kaplan_v2.1").
            model_name:      VLM model name (e.g. "claude-sonnet-4-20250514").
            confidence:      How reliable this judgment is (default 0.5 — VLM judgments
                            should start pessimistic).
        """
        meta = dict(extra_metadata)
        meta["is_hypothesis"] = True
        if prompt_hash:
            meta["prompt_hash"] = prompt_hash
        if prompt_version:
            meta["prompt_version"] = prompt_version
        if model_name:
            meta["model_name"] = model_name
        self._set(key, value, EpistemicLevel.L3_SEMANTIC, source, confidence, meta)

    # -------------------------------------------------------------------------
    # Backward-compatible setter (used by legacy code)
    # -------------------------------------------------------------------------

    def add_attribute(self, key: str, value: float, confidence: float = 1.0) -> None:
        """
        Legacy setter — adds attribute without level tagging.

        Prefer add_proximal(), add_derived(), add_structural(), or
        add_hypothesis() for new code.  This method exists for backward
        compatibility and defaults to L0.
        """
        self._set(key, value, EpistemicLevel.L0_PROXIMAL, "", confidence, {})

    # -------------------------------------------------------------------------
    # Query helpers
    # -------------------------------------------------------------------------

    def get_by_level(self, level: EpistemicLevel) -> Dict[str, float]:
        """Return all attributes at a given epistemic level."""
        return {
            k: rec.value
            for k, rec in self._records.items()
            if rec.level == level
        }

    def get_proximal(self) -> Dict[str, float]:
        """Return all L0 features."""
        return self.get_by_level(EpistemicLevel.L0_PROXIMAL)

    def get_derived(self) -> Dict[str, float]:
        """Return all L1 features."""
        return self.get_by_level(EpistemicLevel.L1_DERIVED)

    def get_structural(self) -> Dict[str, float]:
        """Return all L2 features."""
        return self.get_by_level(EpistemicLevel.L2_STRUCTURAL)

    def get_hypotheses(self) -> Dict[str, float]:
        """Return all L3 features (hypotheses)."""
        return self.get_by_level(EpistemicLevel.L3_SEMANTIC)

    def get_record(self, key: str) -> Optional[AttributeRecord]:
        """Return the full provenance record for an attribute."""
        return self._records.get(key)

    def get_provenance_report(self) -> Dict[str, Dict[str, Any]]:
        """Return a full provenance report for all attributes, grouped by level."""
        report: Dict[str, Dict[str, Any]] = {}
        for level in EpistemicLevel:
            level_attrs = {
                k: {
                    "value": rec.value,
                    "source": rec.source,
                    "confidence": rec.confidence,
                    "metadata": rec.metadata,
                }
                for k, rec in self._records.items()
                if rec.level == level
            }
            if level_attrs:
                report[level.value] = level_attrs
        return report

    # -------------------------------------------------------------------------
    # Internal
    # -------------------------------------------------------------------------

    def _set(
        self,
        key: str,
        value: float,
        level: EpistemicLevel,
        source: str,
        confidence: float,
        extra_metadata: Dict[str, Any],
    ) -> None:
        """Write an attribute to both the provenance store and the flat dict."""
        float_val = float(value)
        self._records[key] = AttributeRecord(
            value=float_val,
            level=level,
            source=source,
            confidence=confidence,
            metadata=extra_metadata,
        )
        # Flat access for backward compatibility
        self.attributes[key] = float_val
        self.metadata[key] = {
            "level": level.value,
            "confidence": confidence,
            "source": source,
            **extra_metadata,
        }
