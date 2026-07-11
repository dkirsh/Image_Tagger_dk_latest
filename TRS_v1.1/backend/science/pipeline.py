"""
Science Pipeline Orchestrator — runs analyzers in epistemic level order.

The pipeline enforces the level hierarchy:

    L0 (proximal)  →  L1 (derived)  →  L2 (structural)  →  L3 (semantic)

L0 runs first because L1 composites depend on L0 values.
L2 can run in parallel with L0/L1 (segmentation doesn't need fractal D).
L3 runs last and its outputs are tagged as hypotheses.

Usage:
    from science.core import AnalysisFrame
    from science.pipeline import SciencePipeline, PipelineConfig

    config = PipelineConfig(enable_l3=False)  # Skip VLM analyzers
    pipeline = SciencePipeline(config)

    frame = AnalysisFrame(image_id=42, original_image=rgb_array)
    pipeline.run(frame)

    # Inspect results by level
    print(frame.get_proximal())     # L0 features
    print(frame.get_derived())      # L1 composites
    print(frame.get_structural())   # L2 structures
    print(frame.get_hypotheses())   # L3 hypotheses (if enabled)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from science.core import AnalysisFrame, EpistemicLevel
from science.contracts import Analyzer, validate_tier_ordering

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """
    Controls which analyzers run and in what configuration.

    Attributes:
        enable_l0:      Run L0 proximal features (default True).
        enable_l1:      Run L1 derived composites (default True).
        enable_l2:      Run L2 structural models (default False — heavy).
        enable_l3:      Run L3 semantic/VLM hypotheses (default False — requires VLM).

        enable_regional:    Run per-region L0 extraction (default False — slow).
        enable_depth:       Run monocular depth estimation (default False — requires ONNX).
        enable_segmentation: Run semantic segmentation (default False — requires torch).
        enable_materials:    Run material detection (default False).
        enable_room_detection: Run room type classification (default False).
        enable_affordance:  Run affordance prediction (default False — requires model).
        enable_cognitive:   Run Kaplan VLM dimensions (default False — requires VLM key).
        enable_style:       Run style VLM classification (default False).
    """
    # Level toggles
    enable_l0: bool = True
    enable_l1: bool = True
    enable_l2: bool = False
    enable_l3: bool = False

    # L0 sub-toggles
    enable_regional: bool = False

    # L2 sub-toggles
    enable_depth: bool = False
    enable_segmentation: bool = False
    enable_materials: bool = False
    enable_room_detection: bool = False
    enable_wall_separation: bool = False
    enable_localized: bool = False

    # L3 sub-toggles
    enable_affordance: bool = False
    enable_cognitive: bool = False
    enable_style: bool = False
    enable_arch_patterns: bool = False

    @classmethod
    def full(cls) -> "PipelineConfig":
        """Enable everything (for comprehensive analysis runs)."""
        return cls(
            enable_l0=True,
            enable_l1=True,
            enable_l2=True,
            enable_l3=True,
            enable_regional=True,
            enable_depth=True,
            enable_segmentation=True,
            enable_materials=True,
            enable_room_detection=True,
            enable_wall_separation=True,
            enable_localized=True,
            enable_affordance=True,
            enable_cognitive=True,
            enable_style=True,
            enable_arch_patterns=True,
        )

    @classmethod
    def proximal_only(cls) -> "PipelineConfig":
        """Only L0 + L1 — fast, no models, no VLMs."""
        return cls(enable_l0=True, enable_l1=True, enable_l2=False, enable_l3=False)

    @classmethod
    def structural(cls) -> "PipelineConfig":
        """L0 + L1 + L2 segmentation + depth — no VLMs."""
        return cls(
            enable_l0=True,
            enable_l1=True,
            enable_l2=True,
            enable_depth=True,
            enable_segmentation=True,
            enable_wall_separation=True,
            enable_localized=True,
        )

    def to_dict(self) -> Dict[str, bool]:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, bool)}


@dataclass
class PipelineResult:
    """Result of a pipeline run."""
    image_id: int
    n_attributes: int
    level_counts: Dict[str, int]
    elapsed_seconds: float
    errors: List[str] = field(default_factory=list)
    analyzer_timings: Dict[str, float] = field(default_factory=dict)


class SciencePipeline:
    """
    Orchestrates science analyzers in epistemic level order.

    The pipeline is lazy: analyzers are instantiated only when their
    level is enabled and only on first use.
    """

    def __init__(self, config: Optional[PipelineConfig] = None) -> None:
        self.config = config or PipelineConfig()
        self._analyzers: Optional[List[Analyzer]] = None

    def run(self, frame: AnalysisFrame) -> PipelineResult:
        """
        Run the full analysis pipeline on a frame.

        Returns a PipelineResult with counts, timings, and any errors.
        """
        start = time.monotonic()
        errors: List[str] = []
        timings: Dict[str, float] = {}

        analyzers = self._get_analyzers()

        # Validate ordering
        warnings = validate_tier_ordering(analyzers)
        for w in warnings:
            logger.warning(w)

        # Run each analyzer
        for analyzer in analyzers:
            name = getattr(analyzer, "name", analyzer.__class__.__name__)
            tier = getattr(analyzer, "tier", "L0")
            t0 = time.monotonic()

            try:
                analyzer.analyze(frame)
                timings[name] = time.monotonic() - t0
                logger.info(
                    "Analyzer '%s' (%s) completed in %.3fs",
                    name, tier, timings[name],
                )
            except Exception as e:
                elapsed = time.monotonic() - t0
                timings[name] = elapsed
                error_msg = f"{name} ({tier}): {type(e).__name__}: {e}"
                errors.append(error_msg)
                logger.error(
                    "Analyzer '%s' (%s) FAILED after %.3fs: %s",
                    name, tier, elapsed, e,
                    exc_info=True,
                )

        total_elapsed = time.monotonic() - start

        # Count attributes by level
        level_counts: Dict[str, int] = {}
        for level in EpistemicLevel:
            count = len(frame.get_by_level(level))
            if count > 0:
                level_counts[level.value] = count

        result = PipelineResult(
            image_id=frame.image_id,
            n_attributes=len(frame.attributes),
            level_counts=level_counts,
            elapsed_seconds=total_elapsed,
            errors=errors,
            analyzer_timings=timings,
        )

        logger.info(
            "Pipeline complete: %d attributes (%s) in %.3fs, %d errors",
            result.n_attributes,
            ", ".join(f"{k}={v}" for k, v in level_counts.items()),
            total_elapsed,
            len(errors),
        )

        return result

    def _get_analyzers(self) -> List[Analyzer]:
        """Build the analyzer chain based on config."""
        if self._analyzers is not None:
            return self._analyzers

        analyzers: List[Any] = []

        # ── L0: Proximal ─────────────────────────────────────────────
        if self.config.enable_l0:
            analyzers.append(self._make_l0_analyzer())

            if self.config.enable_regional:
                regional = self._try_import_regional()
                if regional is not None:
                    analyzers.append(regional)

        # ── L1: Derived ──────────────────────────────────────────────
        if self.config.enable_l1:
            analyzers.extend(self._make_l1_analyzers())

        # ── L2: Structural ───────────────────────────────────────────
        if self.config.enable_l2:
            if self.config.enable_segmentation:
                seg = self._try_import("L2_structural.segmentation.segformer", "SegmentationAnalyzer")
                if seg:
                    analyzers.append(seg)

            if self.config.enable_depth:
                depth = self._try_import("L2_structural.depth.depth_estimator", "DepthAnalyzer")
                if depth:
                    analyzers.append(depth)

            if self.config.enable_wall_separation:
                ws = self._try_import("L2_structural.wall_separation", "WallSeparationAnalyzer")
                if ws:
                    analyzers.append(ws)

            if self.config.enable_localized:
                loc = self._try_import("L2_structural.localized_pipeline", "LocalizedAnalyzer")
                if loc:
                    analyzers.append(loc)

            if self.config.enable_room_detection:
                room = self._try_import("L2_structural.room_detection", "RoomDetectionAnalyzer")
                if room:
                    analyzers.append(room)

            if self.config.enable_materials:
                mat = self._try_import("L2_structural.materials", "MaterialAnalyzer")
                if mat:
                    analyzers.append(mat)

        # ── L3: Semantic ─────────────────────────────────────────────
        if self.config.enable_l3:
            if self.config.enable_cognitive:
                cog = self._try_import("L3_semantic.cognitive_vlm", "CognitiveStateAnalyzer")
                if cog:
                    analyzers.append(cog)

            if self.config.enable_style:
                style = self._try_import("L3_semantic.style_vlm", "SemanticTagAnalyzer")
                if style:
                    analyzers.append(style)

            if self.config.enable_affordance:
                aff = self._try_import("L3_semantic.affordance", "AffordanceAnalyzer")
                if aff:
                    analyzers.append(aff)

            if self.config.enable_arch_patterns:
                arch = self._try_import("L3_semantic.arch_patterns_vlm", "ArchPatternsVLMAnalyzer")
                if arch:
                    analyzers.append(arch)

        self._analyzers = analyzers
        return analyzers

    # -----------------------------------------------------------------
    # Factory helpers (lazy imports to avoid loading heavy models)
    # -----------------------------------------------------------------

    def _make_l0_analyzer(self) -> Any:
        """Create the unified L0 feature extractor wrapper."""
        return _L0UnifiedWrapper()

    def _make_l1_analyzers(self) -> List[Any]:
        """Create all L1 composite analyzers."""
        analyzers = []

        for module_name, class_name in [
            ("L1_derived.complexity", "ComplexityAnalyzer"),
            ("L1_derived.naturalness", "NaturalnessAnalyzer"),
            ("L1_derived.fluency", "FluencyAnalyzer"),
            ("L1_derived.biophilia", "BiophiliaAnalyzer"),
            ("L1_derived.summary", "SummaryAnalyzer"),
        ]:
            analyzer = self._try_import(module_name, class_name)
            if analyzer:
                analyzers.append(analyzer)

        return analyzers

    def _try_import_regional(self) -> Optional[Any]:
        """Try to import the regional feature extractor."""
        return self._try_import("L0_proximal.regional", "RegionalFeatureExtractor")

    def _try_import(self, module_path: str, class_name: str) -> Optional[Any]:
        """
        Try to import and instantiate an analyzer.

        Returns None (with a warning) if the import fails (e.g. missing
        dependencies like torch, onnxruntime, etc.)
        """
        full_module = f"science.{module_path}"
        try:
            import importlib
            module = importlib.import_module(full_module)
            cls = getattr(module, class_name)
            return cls()
        except ImportError as e:
            logger.warning(
                "Skipping %s.%s — missing dependency: %s",
                full_module, class_name, e,
            )
            return None
        except Exception as e:
            logger.warning(
                "Failed to instantiate %s.%s: %s",
                full_module, class_name, e,
            )
            return None


class _L0UnifiedWrapper:
    """
    Wrapper that runs the unified L0 feature extractor and writes
    results to the AnalysisFrame as proximal attributes.
    """
    name = "l0_unified"
    tier = "L0"
    requires = ["original_image"]
    provides = []  # Dynamic — depends on which features succeed

    def analyze(self, frame: AnalysisFrame) -> None:
        """Extract all L0 features and write to frame."""
        try:
            from science.L0_proximal.unified import extract_all_features
        except ImportError:
            # Fall back to old location
            from science.low_level.unified import extract_all_features

        features = extract_all_features(frame.original_image)

        for key, value in features.items():
            if value is not None and not (isinstance(value, float) and (value != value)):  # skip NaN
                frame.add_proximal(
                    key,
                    float(value),
                    source="L0_proximal.unified.extract_all_features",
                )

        logger.info("L0 unified: wrote %d proximal features", len(features))
