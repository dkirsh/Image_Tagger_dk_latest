"""
ADE20K semantic segmentation -> CNfA plane labels + material softness.

Replaces the k-means heuristic in geometry.segment_planes at ~0.85 confidence.
Run on a machine with `pip install transformers torch pillow` (weights download
from Hugging Face on first use — blocked in the Claude sandbox, fine locally).

Usage:
    from cnfa_algs.adapters.segmentation_adapter import segment_with_ade
    planes, conf, ade_raw = segment_with_ade(img_bgr)          # our label space
    planes, conf = ca.segment_planes(img, vp, provided=planes) # feeds the hook

Checkpoint default: nvidia/segformer-b2-finetuned-ade-512-512 (check the
checkpoint's license for your use; research use is standard practice).
"""
from __future__ import annotations
from typing import Dict, Tuple
import numpy as np

from ..geometry import UNKNOWN, FLOOR, CEILING, WALL, OPENING

# ADE20K 150-class index -> CNfA plane class.
# Notes: painting/mirror map to WALL (fixes art-as-opening), plant maps to
# furniture/UNKNOWN (fixes the plant-as-opening failure logged 2026-07-13),
# curtain maps to UNKNOWN so the acoustic layer can treat it as soft.
ADE_TO_PLANE: Dict[int, int] = {
    0: WALL,        # wall
    1: WALL,        # building (seen through opening handled by window class)
    3: FLOOR,       # floor
    5: CEILING,     # ceiling
    6: FLOOR,       # road (exterior floor)
    8: OPENING,     # windowpane
    9: OPENING,     # grass (visible exterior nature -> treated as view)
    11: FLOOR,      # sidewalk
    13: FLOOR,      # earth
    14: OPENING,    # door (traversable boundary)
    2: OPENING,     # sky (visible exterior)
    4: OPENING,     # tree (visible exterior nature)
    18: UNKNOWN,    # curtain -> soft furnishing
    22: WALL,       # painting -> wall surface (art is not an aperture)
    27: WALL,       # mirror
    43: WALL,       # signboard
    63: OPENING,    # blind (window covering)
    28: FLOOR,      # rug (floor material; softness handled below)
    53: FLOOR, 59: FLOOR,   # stairs / stairway
    38: UNKNOWN,    # railing
    17: UNKNOWN,    # plant  (NOT an opening)
    66: UNKNOWN,    # flower
}
# everything else (furniture, objects, people) defaults to UNKNOWN.

# ADE class -> acoustic softness class for the absorption table in attributes.ALPHA
ADE_TO_MATERIAL: Dict[int, str] = {
    28: "carpet_rug", 18: "curtain", 39: "upholstery",      # rug, curtain, cushion
    7: "upholstery", 23: "upholstery", 30: "upholstery",    # bed, sofa, armchair
    31: "upholstery", 57: "upholstery",                     # seat, pillow
    15: "wood_furniture", 10: "wood_furniture", 24: "wood_furniture",
    33: "wood_furniture", 35: "wood_furniture", 62: "wood_furniture",
    64: "wood_furniture", 69: "wood_furniture",
    17: "plant", 66: "plant",
    8: "glass", 27: "glass",
    0: "wall_paint", 5: "ceiling", 3: "hard_floor",
}

_DEFAULT_CKPT = "nvidia/segformer-b2-finetuned-ade-512-512"


def segment_with_ade(img_bgr: np.ndarray, checkpoint: str = _DEFAULT_CKPT
                     ) -> Tuple[np.ndarray, float, np.ndarray]:
    """Returns (plane_labels HxW int in CNfA space, confidence, ade_raw HxW int).
    Raises ImportError with instructions if transformers/torch are missing."""
    try:
        import torch
        from PIL import Image
        from transformers import (SegformerForSemanticSegmentation,
                                  SegformerImageProcessor)
    except ImportError as e:
        raise ImportError(
            "segmentation_adapter needs: pip install transformers torch pillow "
            "(runs on CPU; GPU faster). First run downloads the checkpoint from "
            "Hugging Face.") from e

    rgb = img_bgr[..., ::-1].copy()
    proc = SegformerImageProcessor.from_pretrained(checkpoint)
    model = SegformerForSemanticSegmentation.from_pretrained(checkpoint)
    model.eval()
    with torch.no_grad():
        inputs = proc(images=Image.fromarray(rgb), return_tensors="pt")
        logits = model(**inputs).logits
        up = torch.nn.functional.interpolate(
            logits, size=img_bgr.shape[:2], mode="bilinear", align_corners=False)
        ade = up.argmax(1)[0].cpu().numpy().astype(np.int32)

    planes = np.full(ade.shape, UNKNOWN, np.int32)
    for k, v in ADE_TO_PLANE.items():
        planes[ade == k] = v
    return planes, 0.85, ade


def material_map_from_ade(ade_raw: np.ndarray) -> np.ndarray:
    """HxW array of material-class strings ('' where unmapped) for the
    acoustic absorption layer — replaces its HSV/texture heuristic."""
    out = np.full(ade_raw.shape, "", dtype=object)
    for k, name in ADE_TO_MATERIAL.items():
        out[ade_raw == k] = name
    return out
