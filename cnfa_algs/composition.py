"""
cnfa_algs.composition — image composition analysis.

Pure image-processing (M1) — no external model required.
Optionally uses a deep saliency map if available (from saliency_adapter).

Attributes computed:
    cnfa.composition.rule_of_thirds   — subject alignment with RoT grid
    cnfa.composition.visual_balance   — center-of-visual-mass vs image center
"""
from __future__ import annotations
from typing import Optional
import numpy as np
import cv2

from .core import AttributeResult, normalize01


def _get_saliency(img_bgr: np.ndarray,
                  provided: Optional[np.ndarray] = None,
                  ) -> np.ndarray:
    """Get a saliency map — provided, deep, or FFT fallback."""
    if provided is not None:
        return provided
    try:
        from .adapters.saliency_adapter import deep_saliency
        return deep_saliency(img_bgr)
    except Exception:
        # Inline spectral-residual fallback (never fails)
        g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        small = cv2.resize(g, (128, 128))
        F = np.fft.fft2(small)
        logamp = np.log(np.abs(F) + 1e-9)
        resid = logamp - cv2.blur(logamp, (3, 3))
        sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * np.angle(F)))) ** 2
        sal = cv2.GaussianBlur(sal.astype(np.float32), (9, 9), 2.5)
        sal = cv2.resize(sal, (img_bgr.shape[1], img_bgr.shape[0]))
        return normalize01(sal)


def rule_of_thirds(img_bgr: np.ndarray,
                   saliency: Optional[np.ndarray] = None,
                   ) -> AttributeResult:
    """
    How well visual mass aligns with the rule-of-thirds grid.

    Measures the concentration of saliency near the four RoT intersection
    points relative to the image-wide average.
    """
    sal = _get_saliency(img_bgr, saliency)
    H, W = sal.shape

    # RoT intersection points (4 hotspots)
    hotspots = [
        (W / 3, H / 3), (2 * W / 3, H / 3),
        (W / 3, 2 * H / 3), (2 * W / 3, 2 * H / 3),
    ]

    # Measure saliency in a window around each hotspot
    r = int(min(H, W) * 0.08)  # window radius ~8% of image size
    scores = []
    for hx, hy in hotspots:
        x1, y1 = max(0, int(hx - r)), max(0, int(hy - r))
        x2, y2 = min(W, int(hx + r)), min(H, int(hy + r))
        region_sal = float(sal[y1:y2, x1:x2].mean()) if (y2 > y1 and x2 > x1) else 0.0
        scores.append(region_sal)

    best = max(scores)
    rot_score = float(np.clip(best / (sal.mean() + 1e-9) / 3.0, 0, 1))

    # Build a field showing proximity to RoT grid
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    grid_dist = np.ones((H, W), np.float32) * 999
    for hx, hy in hotspots:
        d = np.sqrt((xs - hx) ** 2 + (ys - hy) ** 2)
        grid_dist = np.minimum(grid_dist, d)
    grid_field = normalize01(1.0 / (grid_dist + 1))

    return AttributeResult(
        key="cnfa.composition.rule_of_thirds",
        scalar=rot_score,
        field=normalize01(sal * grid_field),
        confidence=0.7,
        method="saliency-weighted RoT hotspot proximity (M1)",
        failure_modes=["not all compositions benefit from RoT",
                       "saliency quality limits accuracy"],
        extras={"hotspot_scores": [round(s, 4) for s in scores]},
    )


def visual_balance(img_bgr: np.ndarray,
                   saliency: Optional[np.ndarray] = None,
                   ) -> AttributeResult:
    """
    How well visual weight is balanced around the image center.

    Computes the center-of-visual-mass from the saliency map and measures
    its offset from the geometric center.  Score 1 = perfectly centered,
    0 = extreme corner.
    """
    sal = _get_saliency(img_bgr, saliency)
    H, W = sal.shape

    # Center of visual mass
    total = sal.sum() + 1e-9
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    cx = float((xs * sal).sum() / total)
    cy = float((ys * sal).sum() / total)

    # Offset from image center, normalized
    dx = abs(cx - W / 2) / (W / 2)
    dy = abs(cy - H / 2) / (H / 2)
    offset = float(np.sqrt(dx ** 2 + dy ** 2))

    # Balance score: 1 = perfectly centered, 0 = extreme corner
    balance = float(np.clip(1.0 - offset, 0, 1))

    return AttributeResult(
        key="cnfa.composition.visual_balance",
        scalar=balance,
        field=sal,
        confidence=0.75,
        method="saliency-weighted center-of-mass offset from image center (M1)",
        failure_modes=["intentional asymmetric compositions penalized",
                       "saliency quality limits accuracy"],
        extras={"center_of_mass": [round(cx, 1), round(cy, 1)],
                "offset_normalized": round(offset, 3)},
    )
