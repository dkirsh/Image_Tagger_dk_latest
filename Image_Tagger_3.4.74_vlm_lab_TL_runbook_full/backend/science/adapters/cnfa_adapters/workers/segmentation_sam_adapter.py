"""Segmentation worker adapter — SAM / OneFormer / Mask2Former (ADE20K classes).

Pixel masks for materials, greenery, sky, windows and furniture are the honest
path to natural-material ratio, greenery and activity zones (replacing the
lightweight biophilia proxy). The worker returns per-class area fractions and an
object/region count; this adapter maps them to `cnfa.*`.

Licence: SAM is Apache-2.0 (permissive). OneFormer/Mask2Former *code* is MIT but
some checkpoints are CC-BY-NC — set the worker to an ADE20K model with
commercial-safe weights for a shipped build; the license gate keeps NC weights
in the `research` config only.
"""
from __future__ import annotations

from ..base import License, clip01
from .worker_base import ModelWorkerAdapter

# ADE20K class names counted as "natural material" / "greenery".
NATURAL_CLASSES = ("tree", "plant", "grass", "flower", "water", "rock", "earth",
                   "sky", "wood", "field", "mountain")
GREENERY_CLASSES = ("tree", "plant", "grass", "flower", "field")


class SegmentationSamAdapter(ModelWorkerAdapter):
    name = "segmentation_sam"
    tool = "SAM+ADE20K"
    tool_version = "vit_h"
    license_class = License.PERMISSIVE  # SAM Apache; gate NC seg-weights to research
    enable_flag = "enable_segmentation"
    worker_script = "sam_worker.py"
    worker_python_env = "CNFA_SEG_PYTHON"
    provides = (
        "cnfa.biophilic.natural_material_ratio",
        "cnfa.biophilic.greenery_ratio",
        "cnfa.cognitive.activity_zones_count",
    )

    def map_result(self, frame, result: dict) -> None:
        class_fractions = result.get("class_fractions", {})  # {class_name: fraction}
        region_count = result.get("region_count")

        if class_fractions:
            natural = sum(v for k, v in class_fractions.items() if k in NATURAL_CLASSES)
            green = sum(v for k, v in class_fractions.items() if k in GREENERY_CLASSES)
            self.emit(frame, "cnfa.biophilic.natural_material_ratio", clip01(natural),
                      confidence=0.8)
            self.emit(frame, "cnfa.biophilic.greenery_ratio", clip01(green),
                      confidence=0.8)
        if region_count is not None:
            self.emit(frame, "cnfa.cognitive.activity_zones_count", float(region_count),
                      confidence=0.5, units="count")
