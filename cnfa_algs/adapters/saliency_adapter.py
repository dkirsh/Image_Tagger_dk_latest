"""
Deep saliency adapter — fixation prediction for landmark salience.

Replaces the spectral-residual FFT saliency (Hou & Zhang 2007) with a
deep transformer-based fixation model that predicts where humans actually
look, fixing the "bright window outsalients a memorable sculpture" failure.

Env var: TRANSALNET_CHECKPOINT (path to pretrained .pth)
If unset, ``deep_saliency()`` falls back to spectral-residual automatically.

Install:
    git clone <TranSalNet or preferred model from awesome-human-visual-attention>
    pip install torch torchvision timm
"""
from __future__ import annotations
import os
import sys
import numpy as np
import cv2

_MODEL = None


def is_available() -> bool:
    """Check whether TranSalNet checkpoint is configured and exists."""
    path = os.getenv("TRANSALNET_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch

    ckpt = os.environ["TRANSALNET_CHECKPOINT"]
    model_dir = os.path.dirname(os.path.dirname(ckpt))
    if model_dir not in sys.path:
        sys.path.insert(0, model_dir)

    # Import TranSalNet — adapt to actual repo structure
    from TranSalNet_Dense import TranSalNet  # noqa: E402
    _MODEL = TranSalNet()
    _MODEL.load_state_dict(
        torch.load(ckpt, map_location="cpu"), strict=False
    )
    _MODEL.eval()


def deep_saliency(img_bgr: np.ndarray) -> np.ndarray:
    """
    Compute a saliency map (H, W) float32 in [0, 1].

    Uses the deep TranSalNet model if available, otherwise falls back
    to spectral-residual FFT saliency.
    """
    if not is_available():
        return _spectral_residual_fallback(img_bgr)

    _load()
    import torch

    H, W = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    # TranSalNet expects 384×288 — adapt to model's expected input
    inp = cv2.resize(rgb, (384, 288)).astype(np.float32) / 255.0
    inp = torch.from_numpy(inp).permute(2, 0, 1).unsqueeze(0)

    with torch.no_grad():
        sal = _MODEL(inp)

    sal = sal.squeeze().cpu().numpy().astype(np.float32)
    sal = cv2.resize(sal, (W, H), interpolation=cv2.INTER_LINEAR)
    sal = (sal - sal.min()) / (sal.max() - sal.min() + 1e-9)
    return sal


def _spectral_residual_fallback(img_bgr: np.ndarray) -> np.ndarray:
    """Spectral-residual FFT saliency (Hou & Zhang 2007) — fallback."""
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    small = cv2.resize(g, (128, 128))
    F = np.fft.fft2(small)
    logamp = np.log(np.abs(F) + 1e-9)
    resid = logamp - cv2.blur(logamp, (3, 3))
    sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * np.angle(F)))) ** 2
    sal = cv2.GaussianBlur(sal.astype(np.float32), (9, 9), 2.5)
    sal = cv2.resize(sal, (img_bgr.shape[1], img_bgr.shape[0]))
    sal = (sal - sal.min()) / (sal.max() - sal.min() + 1e-9)
    return sal
