"""operators_v2 — the flagship five, as first-class canonical operators.

Per the Codex recommendation: a curated layer exposing exactly the five
psych-adjacent operators under their canonical `cnfa.*` names, each computed
permissively (no research weights), so they can seed the search/annotation
corpus without leaning on VLM speculation. Status flags follow the mapping
discipline (established / supported-with-debate / proxy / exploratory).

  1. cnfa.contour.curvilinear_ratio      — dedicated contour-curvature operator
  2. cnfa.salience.attention_concentration — permissive spectral-residual saliency
  3. cnfa.biophilic.green_view_ratio      — ExG vegetation index (green view)
  4. cnfa.spatial.depth_openness_index    — from frame.depth_map when present
  5. cnfa.fluency.pattern_rhythm_regularity — already provided by the
     aesthetics_toolbox adapter (Homogeneity); listed here for completeness and
     NOT re-emitted, to keep single ownership of the key.
"""
from __future__ import annotations

import numpy as np

from ..base import AnalyzerAdapter, License, clip01, get_gray, get_rgb


def _curvilinear_ratio(gray: np.ndarray) -> float | None:
    """Fraction of edge-contour length that is smoothly curved (not straight,
    not a sharp corner). A dedicated contour-curvature operator distinct from
    the shape-index proxy."""
    import cv2

    edges = cv2.Canny(np.ascontiguousarray(gray), 80, 160)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    curved = 0
    total = 0
    k = 3
    for c in contours:
        pts = c[:, 0, :].astype(np.float64)
        if len(pts) < 3 * k + 2:
            continue
        v = pts[k:] - pts[:-k]                       # local direction vectors
        ang = np.arctan2(v[:, 1], v[:, 0])
        dang = np.abs(np.diff(ang))
        dang = np.minimum(dang, 2 * np.pi - dang)    # wrap to [0, pi]
        # curved: sustained moderate turning; straight ~0; corner: sharp spike
        curved += int(np.sum((dang > 0.06) & (dang < 0.60)))
        total += int(dang.size)
    if total == 0:
        return None
    return clip01(curved / total)


def _attention_concentration(gray: np.ndarray) -> float:
    """1 - normalised entropy of a spectral-residual saliency map (Hou & Zhang,
    2007) — how concentrated attention is on a dominant region. Permissive."""
    import cv2
    from scipy.ndimage import uniform_filter

    img = cv2.resize(np.ascontiguousarray(gray), (128, 128)).astype(np.float64)
    F = np.fft.fft2(img)
    log_amp = np.log(np.abs(F) + 1e-9)
    phase = np.angle(F)
    sr = log_amp - uniform_filter(log_amp, size=3)
    sal = np.abs(np.fft.ifft2(np.exp(sr + 1j * phase))) ** 2
    sal = uniform_filter(sal, size=3)
    sal = (sal - sal.min()) / (np.ptp(sal) + 1e-9)
    p = sal / (sal.sum() + 1e-9)
    ent = -(p * np.log(p + 1e-12)).sum()
    max_ent = np.log(p.size)
    return clip01(1.0 - ent / max_ent) if max_ent > 0 else 0.0


def _green_view_ratio(rgb: np.ndarray) -> float:
    """Excess-Green (ExG = 2G - R - B) vegetation index -> visible-green ratio,
    the street-view 'green view index' analogue. Permissive proxy for visible
    nature (not a mental-health claim)."""
    r = rgb[..., 0].astype(np.float64) / 255.0
    g = rgb[..., 1].astype(np.float64) / 255.0
    b = rgb[..., 2].astype(np.float64) / 255.0
    exg = 2 * g - r - b
    return float((exg > 0.08).mean())


def _pattern_rhythm_regularity_native(gray: np.ndarray) -> float:
    """Strongest off-centre autocorrelation peak -> periodicity/rhythm of the
    pattern. (Not emitted by default; the aesthetics_toolbox adapter owns the
    canonical key. Kept for reference / fallback.)"""
    import cv2

    g = cv2.resize(gray.astype(np.float64), (128, 128))
    g = g - g.mean()
    F = np.fft.fft2(g)
    ac = np.fft.fftshift(np.fft.ifft2(F * np.conj(F)).real)
    ac /= (ac.max() + 1e-9)
    h, w = ac.shape
    yy, xx = np.indices((h, w))
    rr = np.hypot(xx - w // 2, yy - h // 2)
    ring = (rr > 4) & (rr < min(h, w) // 2)
    return clip01(float(ac[ring].max())) if ring.any() else 0.0


class OperatorsV2Adapter(AnalyzerAdapter):
    name = "operators_v2"
    tool = "cnfa-operators_v2(native)"
    tool_version = "1.0"
    license_class = License.PERMISSIVE
    enable_flag = "enable_operators_v2"
    requires = ("cv2", "scipy", "skimage")
    provides = (
        "cnfa.contour.curvilinear_ratio",
        "cnfa.salience.attention_concentration",
        "cnfa.biophilic.green_view_ratio",
        "cnfa.spatial.depth_openness_index",
    )

    def _analyze(self, frame) -> None:
        gray = get_gray(frame)
        rgb = get_rgb(frame)

        cr = _curvilinear_ratio(gray)
        if cr is not None:
            self.emit(frame, "cnfa.contour.curvilinear_ratio", cr,
                      extra={"note": "contour curvature; 1=all curved, 0=all straight"})

        self.emit(frame, "cnfa.salience.attention_concentration",
                  _attention_concentration(gray),
                  extra={"model": "spectral-residual (permissive)"})

        self.emit(frame, "cnfa.biophilic.green_view_ratio", _green_view_ratio(rgb),
                  extra={"index": "ExG"})

        # depth-openness from the frame's depth map, when the pipeline populated it
        dm = getattr(frame, "depth_map", None)
        if dm is not None:
            d = np.asarray(dm, dtype=np.float64)
            if d.size and np.ptp(d) > 0:
                d = (d - d.min()) / (np.ptp(d) + 1e-9)
                self.emit(frame, "cnfa.spatial.depth_openness_index", float(d.mean()),
                          confidence=0.6,
                          extra={"note": "mean normalised depth; convention-dependent"})
