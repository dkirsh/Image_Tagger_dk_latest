"""
Analyzer protocol and tier definitions for the CNfA pipeline.

Every analyzer conforms to the ``Analyzer`` protocol: it has a ``name``,
declares what it ``requires`` and ``provides``, and exposes an ``analyze``
method that populates an AnalysisFrame.

Tiers
-----
L0  Proximal     — transparent computation, no learned weights
L1  Derived      — explicit formula over L0, with citation
L2  Structural   — learned model, transparent I/O
L3  Semantic     — VLM / human judgment (hypotheses)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from science.core import AnalysisFrame

logger = logging.getLogger(__name__)


@runtime_checkable
class Analyzer(Protocol):
    """Protocol that all science analyzers must satisfy."""

    name: str
    """Human-readable name (e.g. 'fractal_analyzer')."""

    tier: str
    """Epistemic level: 'L0', 'L1', 'L2', or 'L3'."""

    requires: List[str]
    """Frame attributes or representations this analyzer needs
    (e.g. ['gray_image', 'edges'] or ['segmentation_masks'])."""

    provides: List[str]
    """Attribute keys this analyzer writes
    (e.g. ['fractal_dimension', 'fractal_dimension_sd'])."""

    def analyze(self, frame: "AnalysisFrame") -> None:
        """Run analysis and populate frame with results."""
        ...


def fail(
    frame: "AnalysisFrame",
    analyzer_name: str,
    reason: str,
    *,
    level: str = "warning",
) -> None:
    """
    Record an analyzer failure in the frame metadata.

    Use this instead of raising exceptions when an analyzer cannot run
    (e.g. missing depth map, segmentation not available).  Downstream
    analyzers can check frame.metadata for these failure records.

    Args:
        frame:         The AnalysisFrame to annotate.
        analyzer_name: Which analyzer failed.
        reason:        Human-readable explanation.
        level:         Severity ('info', 'warning', 'error').
    """
    failure_key = f"_failure.{analyzer_name}"
    frame.metadata[failure_key] = {
        "reason": reason,
        "level": level,
    }
    log_fn = getattr(logger, level, logger.warning)
    log_fn("Analyzer '%s' skipped: %s", analyzer_name, reason)


def check_requirements(
    frame: "AnalysisFrame",
    analyzer_name: str,
    requirements: List[str],
) -> bool:
    """
    Verify that an AnalysisFrame has the required representations.

    Returns True if all requirements are met, False otherwise (and records
    failure via ``fail()``).

    Recognized requirement strings:
        'gray_image', 'edges', 'lab_image'  → frame.gray_image is not None, etc.
        'depth_map'                          → frame.depth_map is not None
        'segmentation_masks'                 → len(frame.segmentation_masks) > 0
        'segmentation_masks.wall'            → 'wall' in frame.segmentation_masks
        Any other string                     → key in frame.attributes
    """
    REPR_ATTRS = {
        "gray_image", "edges", "lab_image",
        "depth_map", "segmentation_map", "segmentation_confidence",
        "original_image",
    }

    for req in requirements:
        if req in REPR_ATTRS:
            if getattr(frame, req, None) is None:
                fail(frame, analyzer_name, f"missing {req}")
                return False
        elif req == "segmentation_masks":
            if not frame.segmentation_masks:
                fail(frame, analyzer_name, "no segmentation masks available")
                return False
        elif req.startswith("segmentation_masks."):
            mask_name = req.split(".", 1)[1]
            if mask_name not in frame.segmentation_masks:
                fail(frame, analyzer_name, f"missing segmentation mask: {mask_name}")
                return False
        else:
            if req not in frame.attributes:
                fail(frame, analyzer_name, f"missing attribute: {req}")
                return False

    return True


# ---------------------------------------------------------------------------
# Analyzer tier registry — used by the pipeline to validate ordering
# ---------------------------------------------------------------------------

TIER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def validate_tier_ordering(analyzers: List[Analyzer]) -> List[str]:
    """
    Check that analyzers are ordered by tier.

    Returns a list of warning messages for any ordering violations.
    The pipeline can still run with violations, but they indicate
    possible dependency issues.
    """
    warnings = []
    prev_tier = "L0"
    for analyzer in analyzers:
        tier = getattr(analyzer, "tier", "L0")
        if TIER_ORDER.get(tier, 0) < TIER_ORDER.get(prev_tier, 0):
            warnings.append(
                f"Analyzer '{analyzer.name}' (tier {tier}) runs after "
                f"a {prev_tier} analyzer — possible dependency issue"
            )
        prev_tier = tier
    return warnings
