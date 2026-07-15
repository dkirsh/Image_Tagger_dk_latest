"""
Apple Depth Pro adapter — metric monocular depth for cnfa_algs.

Returns depth in real metres and estimated focal length in pixels,
without requiring camera intrinsics.

Env var: DEPTH_PRO_CHECKPOINT  (path to depth_pro.pt)
If unset, this adapter is unavailable and DepthProvider falls through
to DepthAnything V2 or the geometric fallback.

Install:
    git clone https://github.com/apple/ml-depth-pro
    cd ml-depth-pro && bash get_pretrained_models.sh
    pip install -e .
"""
from __future__ import annotations
import os
from typing import Tuple
import numpy as np
import cv2

_MODEL = None
_TRANSFORM = None


def is_available() -> bool:
    """Check whether Depth Pro checkpoint is configured and exists."""
    path = os.getenv("DEPTH_PRO_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


def _load():
    global _MODEL, _TRANSFORM
    if _MODEL is not None:
        return
    import torch
    import depth_pro

    ckpt = os.environ["DEPTH_PRO_CHECKPOINT"]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    _MODEL, _TRANSFORM = depth_pro.create_model_and_transforms(
        device=device,
        precision=torch.float32,
    )
    _MODEL.load_state_dict(
        torch.load(ckpt, map_location="cpu"), strict=True
    )
    _MODEL.eval()


def get_metric_depth(img_bgr: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Run Depth Pro on a BGR image.

    Returns
    -------
    depth_metres : np.ndarray (H, W) float32
        Per-pixel depth in real metres.
    focal_px : float
        Estimated focal length in pixels.
    """
    _load()
    import torch
    from PIL import Image

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    result = _MODEL.infer(
        _TRANSFORM(pil_img),
        f_px=None,  # let the model estimate focal length
    )
    depth = result["depth"].squeeze().cpu().numpy().astype(np.float32)
    focal = float(result["focallength_px"].squeeze().cpu().numpy())

    # Resize to original image dimensions
    H, W = img_bgr.shape[:2]
    if depth.shape != (H, W):
        depth = cv2.resize(depth, (W, H), interpolation=cv2.INTER_LINEAR)

    return depth, focal
