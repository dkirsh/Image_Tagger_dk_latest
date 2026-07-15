"""
HAWP wireframe parser adapter — structural lines + junctions.

Detects architectural wireframe lines and junction points from a single
image.  Provides an improved vanishing-point estimator that falls back
to the existing Hough-based method when HAWP is unavailable.

Env var: HAWP_CHECKPOINT (path to hawpv3.pth or equivalent)

Install:
    git clone https://github.com/cherubicXN/hawp
    pip install -e .
    # Download pretrained weights from the Releases page.
"""
from __future__ import annotations
import os
from typing import Dict, Tuple
import numpy as np
import cv2

_MODEL = None


def is_available() -> bool:
    """Check whether HAWP checkpoint is configured and exists."""
    path = os.getenv("HAWP_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch

    ckpt = os.environ["HAWP_CHECKPOINT"]

    # HAWP's API varies by version — try the SSL-era API first, then FSL.
    try:
        from hawp.ssl.predict import WireframeDetector
        _MODEL = WireframeDetector(is_cuda=torch.cuda.is_available())
        _MODEL.load_state_dict(
            torch.load(ckpt, map_location="cpu")
        )
    except ImportError:
        from hawp.fsl.config import cfg as model_cfg
        from hawp.fsl.model import build_model
        _MODEL = build_model(model_cfg)
        state = torch.load(ckpt, map_location="cpu")
        _MODEL.load_state_dict(state.get("model", state), strict=False)
    _MODEL.eval()


def detect_wireframe(img_bgr: np.ndarray,
                     score_thresh: float = 0.9,
                     ) -> Dict[str, np.ndarray]:
    """
    Detect architectural wireframe lines and junction points.

    Returns
    -------
    dict with keys:
        lines     : np.ndarray (N, 2, 2) — each line [[x1,y1],[x2,y2]]
        scores    : np.ndarray (N,) — per-line confidence
        junctions : np.ndarray (M, 2) — [x, y] junction points
    """
    _load()
    import torch

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    with torch.no_grad():
        result = _MODEL(rgb)

    lines = result.get("lines_pred", result.get("lines", np.empty((0, 2, 2))))
    scores = result.get("lines_score", result.get("score", np.ones(len(lines))))
    juncs = result.get("juncs_pred", result.get("juncs", np.empty((0, 2))))

    if isinstance(lines, torch.Tensor):
        lines = lines.cpu().numpy()
    if isinstance(scores, torch.Tensor):
        scores = scores.cpu().numpy()
    if isinstance(juncs, torch.Tensor):
        juncs = juncs.cpu().numpy()

    mask = scores >= score_thresh
    return {
        "lines": lines[mask].reshape(-1, 2, 2),
        "scores": scores[mask],
        "junctions": juncs,
    }


def wireframe_vanishing_point(img_bgr: np.ndarray,
                              ) -> Tuple[float, float, float]:
    """
    Estimate vanishing point from HAWP-detected structural lines.

    Falls back to the existing Hough-based estimator in
    ``geometry.estimate_vanishing_point`` if HAWP is unavailable or
    returns too few lines.

    Returns (vx, vy, confidence).
    """
    if not is_available():
        from ..geometry import estimate_vanishing_point
        return estimate_vanishing_point(img_bgr)

    wf = detect_wireframe(img_bgr)
    lines = wf["lines"]
    H, W = img_bgr.shape[:2]

    if len(lines) < 4:
        from ..geometry import estimate_vanishing_point
        return estimate_vanishing_point(img_bgr)

    # Weighted least-squares VP from oblique wireframe segments
    A, b_vec, wts = [], [], []
    for seg in lines:
        (x1, y1), (x2, y2) = seg
        dx, dy = x2 - x1, y2 - y1
        ang = abs(np.degrees(np.arctan2(dy, dx)))
        ang = min(ang, 180 - ang)
        if 8 < ang < 80:  # oblique lines only
            n = np.array([-dy, dx])
            n /= (np.linalg.norm(n) + 1e-9)
            A.append(n)
            b_vec.append(n @ np.array([x1, y1]))
            wts.append(np.hypot(dx, dy))

    if len(A) >= 4:
        A_arr = np.array(A) * np.array(wts)[:, None]
        b_arr = np.array(b_vec) * np.array(wts)
        vp, *_ = np.linalg.lstsq(A_arr, b_arr, rcond=None)
        vx, vy = float(vp[0]), float(vp[1])
        conf = min(1.0, len(A) / 16) * 0.95  # higher conf than Hough
        if -0.5 * W < vx < 1.5 * W and 0.05 * H < vy < 0.95 * H:
            return vx, vy, conf

    # Fall back if VP is out of range
    from ..geometry import estimate_vanishing_point
    return estimate_vanishing_point(img_bgr)
