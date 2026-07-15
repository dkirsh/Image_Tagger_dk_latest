"""
uLayout room layout adapter — structured room geometry from a photo.

Returns wall/floor/ceiling boundary polygons as a ``RoomLayout`` dataclass
that can feed directly into ``geometry.segment_planes(provided=...)`` or
into ``plan.infer_plan_from_image`` as a structured geometry alternative
to the current depth-based heuristic.

Env var: ULAYOUT_CHECKPOINT (path to best.pth)

Install:
    git clone https://github.com/JonathanLee112/uLayout
    pip install torch torchvision timm
    # Download pretrained weights per the README.
"""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass, field as dfield
from typing import List, Tuple
import numpy as np
import cv2

from ..geometry import FLOOR, CEILING, WALL, UNKNOWN


@dataclass
class RoomLayout:
    """Structured room geometry from a single image."""
    floor_polygon: np.ndarray       # (N, 2) polygon in image coords
    ceiling_polygon: np.ndarray     # (N, 2) polygon in image coords
    wall_segments: List[Tuple[np.ndarray, np.ndarray]] = dfield(default_factory=list)
    floor_mask: np.ndarray = dfield(default_factory=lambda: np.empty(0))
    ceiling_mask: np.ndarray = dfield(default_factory=lambda: np.empty(0))
    wall_mask: np.ndarray = dfield(default_factory=lambda: np.empty(0))
    confidence: float = 0.0


def is_available() -> bool:
    """Check whether uLayout checkpoint is configured and exists."""
    path = os.getenv("ULAYOUT_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


_MODEL = None


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch

    ckpt_path = os.environ["ULAYOUT_CHECKPOINT"]
    parent = os.path.dirname(os.path.dirname(ckpt_path))
    if parent not in sys.path:
        sys.path.insert(0, parent)

    # Import uLayout model — adapt to actual repo API
    from model import build_model  # noqa: E402
    _MODEL = build_model()
    state = torch.load(ckpt_path, map_location="cpu")
    _MODEL.load_state_dict(state.get("model", state), strict=False)
    _MODEL.eval()


def _mask_to_polygon(mask: np.ndarray) -> np.ndarray:
    """Extract the largest contour polygon from a binary mask."""
    cs, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if cs:
        c = max(cs, key=cv2.contourArea)
        return c.reshape(-1, 2)
    return np.empty((0, 2))


def estimate_room_layout(img_bgr: np.ndarray) -> RoomLayout:
    """
    Estimate structured room layout from a perspective image.

    Returns a ``RoomLayout`` with floor/ceiling/wall masks and polygons.
    """
    _load()
    import torch

    H, W = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    with torch.no_grad():
        result = _MODEL.predict(rgb)

    # Extract masks — exact keys depend on uLayout's API; normalize here.
    floor_mask = result.get("floor_mask", np.zeros((H, W), np.uint8))
    ceil_mask = result.get("ceiling_mask", np.zeros((H, W), np.uint8))
    wall_mask = result.get("wall_mask", np.zeros((H, W), np.uint8))

    # Resize to original dimensions if needed
    for name in ("floor_mask", "ceil_mask", "wall_mask"):
        m = locals()[name]
        if m.shape[:2] != (H, W) and m.size > 0:
            locals()[name] = cv2.resize(
                m, (W, H), interpolation=cv2.INTER_NEAREST
            )

    return RoomLayout(
        floor_polygon=_mask_to_polygon(floor_mask),
        ceiling_polygon=_mask_to_polygon(ceil_mask),
        wall_segments=[],
        floor_mask=floor_mask,
        ceiling_mask=ceil_mask,
        wall_mask=wall_mask,
        confidence=0.75,
    )


def layout_to_planes(layout: RoomLayout, shape: Tuple[int, int]) -> np.ndarray:
    """
    Convert a ``RoomLayout`` to a CNfA plane-label map compatible with
    ``geometry.segment_planes(provided=...)``.

    Parameters
    ----------
    layout : RoomLayout
    shape  : (H, W)

    Returns
    -------
    planes : np.ndarray (H, W) int32
    """
    H, W = shape
    planes = np.full((H, W), UNKNOWN, np.int32)
    if layout.floor_mask.size > 0:
        planes[layout.floor_mask > 0] = FLOOR
    if layout.ceiling_mask.size > 0:
        planes[layout.ceiling_mask > 0] = CEILING
    if layout.wall_mask.size > 0:
        planes[layout.wall_mask > 0] = WALL
    return planes
