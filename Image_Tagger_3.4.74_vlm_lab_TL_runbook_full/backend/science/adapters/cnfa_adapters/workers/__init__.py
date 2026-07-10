"""Isolated model-worker adapters (depth / segmentation / saliency).

Each shells out to a pinned worker interpreter over a JSON contract, so their
heavy and sometimes non-commercial-weighted dependencies never enter the main
science environment. See worker_base.ModelWorkerAdapter.
"""
from .aesthetic_score_adapter import AestheticScoreAdapter
from .depth_midas_adapter import DepthMidasAdapter
from .material_from_image_adapter import MaterialFromImageAdapter
from .memorability_adapter import MemorabilityAdapter
from .saliency_deepgaze_adapter import SaliencyDeepGazeAdapter
from .segmentation_sam_adapter import SegmentationSamAdapter

__all__ = [
    "DepthMidasAdapter",
    "SegmentationSamAdapter",
    "SaliencyDeepGazeAdapter",
    "MemorabilityAdapter",
    "AestheticScoreAdapter",
    "MaterialFromImageAdapter",
]
