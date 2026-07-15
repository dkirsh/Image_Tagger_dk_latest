"""
cnfa_algs.geometry — single-image scene geometry: vanishing point,
boundary-plane segmentation heuristic, and depth.

Depth strategy (mirrors the Image Tagger convention):
  1. If DEPTH_ANYTHING_ONNX_PATH is set and loadable -> monocular network depth (M2).
  2. Else -> geometric ground-plane depth from the vanishing point under a
     level-camera / flat-floor assumption (M2-geo, LOW confidence):
         Z(floor pixel at row y) = f * h_cam / (y - y_horizon)
     Wall/furniture pixels inherit the depth of their floor footprint
     (nearest floor pixel below in the same column), which is exactly what
     plan projection needs.

Plane classes: 0 unknown/furniture, 1 floor, 2 ceiling, 3 wall, 4 opening/window.
Segmentation here is an honest k-means + position/brightness prior heuristic
(Med-Low confidence) with a hook to supply a real segmentation label map.
"""
from __future__ import annotations
import os
from typing import Optional, Tuple, Dict
import numpy as np
import cv2

UNKNOWN, FLOOR, CEILING, WALL, OPENING = 0, 1, 2, 3, 4

PLANE_PALETTE = {FLOOR: (60, 180, 60), CEILING: (200, 120, 40),
                 WALL: (150, 150, 150), OPENING: (60, 200, 255), UNKNOWN: (40, 40, 90)}
PLANE_LEGEND = {FLOOR: "floor", CEILING: "ceiling", WALL: "wall",
                OPENING: "opening/window", UNKNOWN: "furniture/other"}


# ------------------------------------------------------------ vanishing point

def estimate_vanishing_point(img_bgr: np.ndarray) -> Tuple[float, float, float]:
    """Least-squares intersection of oblique Hough segments.
    Returns (vx, vy, confidence)."""
    H, W = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 160)
    segs = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40,
                           minLineLength=max(20, W // 12), maxLineGap=8)
    A, b, wts = [], [], []
    if segs is not None:
        for s in segs[:, 0]:
            x1, y1, x2, y2 = map(float, s)
            dx, dy = x2 - x1, y2 - y1
            ang = abs(np.degrees(np.arctan2(dy, dx)))
            ang = min(ang, 180 - ang)
            if 8 < ang < 80:  # oblique lines only (perspective convergents)
                n = np.array([-dy, dx]); n /= (np.linalg.norm(n) + 1e-9)
                A.append(n); b.append(n @ np.array([x1, y1]))
                wts.append(np.hypot(dx, dy))
    if len(A) >= 4:
        A = np.array(A) * np.array(wts)[:, None]
        b = np.array(b) * np.array(wts)
        vp, res, *_ = np.linalg.lstsq(A, b, rcond=None)
        vx, vy = float(vp[0]), float(vp[1])
        conf = min(1.0, len(A) / 24)
        # sane clamp: horizon must be inside the vertical span (with margin)
        if -0.5 * W < vx < 1.5 * W and 0.05 * H < vy < 0.95 * H:
            return vx, vy, conf * 0.8
    return W / 2.0, H * 0.42, 0.2  # weak prior


# ------------------------------------------------------------ plane heuristic

def segment_planes(img_bgr: np.ndarray, vp: Tuple[float, float],
                   provided: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
    """Return (label_map HxW int, confidence). If `provided` is given
    (real segmentation), pass it through at high confidence.
    Known failure: indoor plants / saturated nature colors classify as OPENING
    (batch-validated 2026-07-13, Office_Grade lobby); a real segmenter fixes it."""
    if provided is not None:
        return provided.astype(np.int32), 0.9

    H, W = img_bgr.shape[:2]
    vy = int(np.clip(vp[1], 0.15 * H, 0.7 * H))
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

    # k-means over (L,a,b, x/W, y/H) — spatial-color clusters
    ys, xs = np.mgrid[0:H, 0:W]
    feats = np.stack([lab[..., 0] / 255 * 2, lab[..., 1] / 255 * 3, lab[..., 2] / 255 * 3,
                      xs / W * 1.0, ys / H * 2.0], -1).reshape(-1, 5).astype(np.float32)
    K = 12
    cv2.setRNGSeed(1234)   # panel fix S2: deterministic segmentation (was RNG-order dependent)
    _, klab, kcent = cv2.kmeans(feats, K, None,
                                (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 12, 0.5),
                                2, cv2.KMEANS_PP_CENTERS)
    klab = klab.reshape(H, W)

    out = np.zeros((H, W), np.int32)
    bright_thresh = np.percentile(gray, 96)
    for k in range(K):
        m = klab == k
        if m.sum() < 40:
            continue
        cy = ys[m].mean() / H
        sat = hsv[..., 1][m].mean() / 255
        val = gray[m].mean()
        # openings: very bright, or saturated nature colors, in the upper 2/3
        frac_bright = (gray[m] > bright_thresh).mean()
        frac_abs_bright = (gray[m] > 0.92).mean()
        hue = hsv[..., 0][m].mean()
        is_nature = sat > 0.30 and (25 < hue < 100) and cy < 0.78
        if ((frac_bright > 0.5 or frac_abs_bright > 0.45) and cy < 0.72) or is_nature:
            out[m] = OPENING
        elif cy < 0.16 and sat < 0.25:
            out[m] = CEILING
        elif cy > 0.80:
            out[m] = FLOOR
        elif sat < 0.30 and val > 0.35 and 0.12 < cy < 0.72:
            out[m] = WALL
        else:
            out[m] = UNKNOWN  # furniture / objects

    # grow floor upward from bottom strip by color continuity
    seedrow = out[int(0.97 * H)]
    floor_cols = np.where(seedrow == FLOOR)[0]
    if len(floor_cols) > 0:
        floor_mask = (out == FLOOR).astype(np.uint8)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        med_floor_val = float(np.median(gray[out == FLOOR])) if (out == FLOOR).any() else 0.5
        similar = np.abs(gray - med_floor_val) < 0.28
        out[(floor_mask > 0) & (ys > vy + 0.05 * H) & similar] = FLOOR
    conf = 0.45
    return out, conf


# ------------------------------------------------------------------- depth

class DepthProvider:
    """ONNX monocular depth if configured, geometric fallback otherwise."""

    def __init__(self):
        self.session = None
        self.method = "geometric_vp_groundplane(M2-geo)"
        path = os.getenv("DEPTH_ANYTHING_ONNX_PATH")
        if path and os.path.exists(path):
            try:
                import onnxruntime as ort
                self.session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
                self.method = "monocular_onnx(M2)"
            except Exception:
                self.session = None

    def __call__(self, img_bgr: np.ndarray, planes: np.ndarray,
                 vp: Tuple[float, float], fov_deg: float = 65.0,
                 cam_h: float = 1.5) -> Tuple[np.ndarray, np.ndarray, float]:
        """Returns (Z metric-ish HxW, disparity01 HxW for display, confidence)."""
        if self.session is not None:
            return self._onnx_depth(img_bgr, planes, cam_h)
        return self._geometric_depth(img_bgr, planes, vp, fov_deg, cam_h)

    # -- network depth, floor-plane calibrated to metric-ish scale
    def _onnx_depth(self, img_bgr, planes, cam_h):
        inp = self.session.get_inputs()[0]
        size = 518 if (inp.shape[-1] in (518, "height", None)) else int(inp.shape[-1])
        x = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), (size, size)).astype(np.float32) / 255
        x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        x = x.transpose(2, 0, 1)[None].astype(np.float32)
        disp = self.session.run(None, {inp.name: x})[0].squeeze()
        disp = cv2.resize(disp, (img_bgr.shape[1], img_bgr.shape[0]))
        disp01 = (disp - disp.min()) / (np.ptp(disp) + 1e-9)
        # scale/shift calibration: floor pixels should form a plane at height -cam_h
        Z = 1.0 / (disp01 * 0.9 + 0.1)          # crude metric mapping
        Z = Z / np.median(Z[planes == FLOOR] + 1e-9) * (2.0 * cam_h)
        return Z, disp01, 0.7

    # -- principled single-view fallback
    def _geometric_depth(self, img_bgr, planes, vp, fov_deg, cam_h):
        H, W = img_bgr.shape[:2]
        f = (W / 2) / np.tan(np.radians(fov_deg / 2))
        y_h = float(np.clip(vp[1], 0.1 * H, 0.7 * H))
        ys = np.mgrid[0:H, 0:W][0].astype(np.float32)
        Z = np.full((H, W), np.nan, np.float32)

        below = ys > (y_h + 2)
        Zg = f * cam_h / np.maximum(ys - y_h, 2.0)       # ground-plane depth
        floorish = (planes == FLOOR) & below
        Z[floorish] = Zg[floorish]

        # non-floor pixels: inherit the ground depth at their floor footprint
        # (per column: depth of the highest floor pixel = farthest visible floor)
        col_far = np.full(W, np.nan, np.float32)
        for xcol in range(W):
            rows = np.where(floorish[:, xcol])[0]
            if len(rows):
                col_far[xcol] = Zg[rows.min(), xcol]     # farthest floor in column
        med_far = np.nanmedian(col_far)
        col_far = np.where(np.isnan(col_far), med_far, col_far)
        from scipy.signal import medfilt
        col_far = medfilt(col_far, kernel_size=min(31, (W // 8) * 2 + 1))
        col_far = cv2.blur(col_far.reshape(1, -1), (1, 9)).ravel()
        colZ = np.repeat(col_far[None, :], H, 0)
        Z = np.where(np.isnan(Z), colZ, Z)
        Z = np.clip(Z, 0.3, np.nanpercentile(Z, 99))
        disp01 = 1.0 / Z
        disp01 = (disp01 - disp01.min()) / (np.ptp(disp01) + 1e-9)
        return Z, disp01, 0.35
