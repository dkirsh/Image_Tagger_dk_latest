"""
Marigold diffusion depth adapter — high-quality relative depth maps.

Marigold uses a diffusion prior to produce visually superior depth maps.
It produces RELATIVE depth (not metric). Use Depth Pro for metric depth;
use Marigold when you want the highest visual quality for rendering/display.

No env var needed by default — loads from HuggingFace on first use.
Set MARIGOLD_MODEL to override the model ID or point to a local path.

Install:
    pip install diffusers torch accelerate
"""
from __future__ import annotations
import os
import numpy as np
import cv2

_PIPE = None


def is_available() -> bool:
    """Check whether the diffusers library is installed."""
    try:
        import diffusers  # noqa: F401
        return True
    except ImportError:
        return False


def _load():
    global _PIPE
    if _PIPE is not None:
        return
    from diffusers import MarigoldDepthPipeline
    import torch

    model_id = os.getenv("MARIGOLD_MODEL", "prs-eth/marigold-depth-v1-1")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    _PIPE = MarigoldDepthPipeline.from_pretrained(model_id).to(device)


def get_marigold_depth(img_bgr: np.ndarray,
                       num_inference_steps: int = 10,
                       ensemble_size: int = 5,
                       ) -> np.ndarray:
    """
    Run Marigold diffusion depth estimation.

    Parameters
    ----------
    img_bgr             : BGR image
    num_inference_steps  : diffusion steps (lower = faster, lower quality)
    ensemble_size        : number of ensemble predictions to average

    Returns
    -------
    depth_relative : np.ndarray (H, W) float32 in [0, 1] (0=far, 1=near)
    """
    _load()
    from PIL import Image

    H, W = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    output = _PIPE(
        pil_img,
        num_inference_steps=num_inference_steps,
        ensemble_size=ensemble_size,
    )
    depth = output.prediction.squeeze().cpu().numpy().astype(np.float32)

    if depth.shape != (H, W):
        depth = cv2.resize(depth, (W, H), interpolation=cv2.INTER_LINEAR)

    return depth
