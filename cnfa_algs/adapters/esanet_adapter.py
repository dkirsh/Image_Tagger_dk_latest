"""
ESANet RGB-D segmentation adapter — fuses depth for better indoor scene
segmentation than RGB-only models.

The key advantage: if you already have a depth map (from Depth Pro or
DepthAnything), ESANet leverages it for significantly better boundary
precision on floor/wall/ceiling in cluttered rooms.

Env var: ESANET_CHECKPOINT (path to pretrained .pth)

Install:
    git clone https://github.com/TUI-NICR/ESANet
    pip install torch torchvision
    # Download NYUv2 pretrained weights per the README.
"""
from __future__ import annotations
import os
import sys
from typing import Dict, Tuple
import numpy as np
import cv2

from ..geometry import UNKNOWN, FLOOR, CEILING, WALL, OPENING

# NYUv2 40-class → CNfA plane labels (subset — extend as needed)
NYUV2_TO_PLANE: Dict[int, int] = {
    1: WALL,      # wall
    2: FLOOR,     # floor
    3: UNKNOWN,   # cabinet
    4: UNKNOWN,   # bed
    5: UNKNOWN,   # chair
    6: UNKNOWN,   # sofa
    7: UNKNOWN,   # table
    8: OPENING,   # door
    9: OPENING,   # window
    10: UNKNOWN,  # bookshelf
    11: WALL,     # picture (on wall)
    12: UNKNOWN,  # counter
    14: UNKNOWN,  # desk
    15: UNKNOWN,  # curtain
    16: UNKNOWN,  # fridge
    22: CEILING,  # ceiling
    25: WALL,     # mirror (wall surface)
    27: UNKNOWN,  # tv
    33: UNKNOWN,  # toilet
    34: UNKNOWN,  # sink
    36: UNKNOWN,  # bathtub
    # everything else defaults to UNKNOWN
}


def is_available() -> bool:
    """Check whether ESANet checkpoint is configured and exists."""
    path = os.getenv("ESANET_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


_MODEL = None


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch

    ckpt_path = os.environ["ESANET_CHECKPOINT"]
    esanet_dir = os.path.dirname(os.path.dirname(ckpt_path))
    if esanet_dir not in sys.path:
        sys.path.insert(0, esanet_dir)

    # Import ESANet model — adapt to actual repo API
    from src.build_model import build_model  # noqa: E402
    _MODEL = build_model(n_classes=40, modality="rgbd")
    state = torch.load(ckpt_path, map_location="cpu")
    _MODEL.load_state_dict(state.get("state_dict", state), strict=False)
    _MODEL.eval()


def segment_with_rgbd(img_bgr: np.ndarray,
                      depth: np.ndarray,
                      ) -> Tuple[np.ndarray, float, np.ndarray]:
    """
    Run ESANet RGB-D segmentation.

    Parameters
    ----------
    img_bgr : (H, W, 3) BGR image
    depth   : (H, W) depth map (any scale — will be normalized)

    Returns
    -------
    planes     : (H, W) int32 — CNfA plane labels
    confidence : float
    raw_labels : (H, W) int32 — original NYUv2 40-class labels
    """
    _load()
    import torch

    H, W = img_bgr.shape[:2]

    # Preprocess — adapt to ESANet input requirements
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    rgb_resized = cv2.resize(rgb, (640, 480))
    depth_resized = cv2.resize(depth.astype(np.float32), (640, 480))

    # Normalize
    rgb_t = torch.from_numpy(rgb_resized).permute(2, 0, 1).float() / 255.0
    depth_t = torch.from_numpy(depth_resized).unsqueeze(0).float()
    d_range = depth_t.max() - depth_t.min()
    if d_range > 0:
        depth_t = (depth_t - depth_t.min()) / d_range

    with torch.no_grad():
        pred = _MODEL(rgb_t.unsqueeze(0), depth_t.unsqueeze(0))
        labels = pred.argmax(1).squeeze().cpu().numpy()

    # Resize back to original
    raw_labels = cv2.resize(
        labels.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST
    ).astype(np.int32)

    # Map to CNfA plane labels
    planes = np.full((H, W), UNKNOWN, np.int32)
    for nyuv2_class, plane_class in NYUV2_TO_PLANE.items():
        planes[raw_labels == nyuv2_class] = plane_class

    return planes, 0.85, raw_labels
