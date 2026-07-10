"""Proximal-stimulus statistics — implemented natively (permissive).

These are the "light on the eye" Level-0 statistics of the deep-attribute
review: quantities computed directly from the image, each with a causal
literature behind it. Implemented here with numpy/scipy/scikit-image/OpenCV so
there is no external-package licence to clear.

Highlights (proximal -> the perceptual/neural thing it is a cue for):
  * luminance-histogram **skewness / kurtosis** -> perceived **gloss / surface
    quality** (Motoyoshi, Nishida, Sharan & Adelson, 2007, *Nature*);
  * **sub-band skew** (skew of the high-pass luminance) -> the stronger gloss
    predictor from the same work;
  * **RMS contrast** -> contrast sensitivity / visual salience;
  * **straight-vs-curved edge ratio** -> rectilinearity vs curvilinearity, the
    approach/avoidance contour cue (Bar & Neta, 2006; Vartanian et al., 2013);
  * **blur / depth-of-field** -> focal guidance and photographic depth;
  * **radial 1/f spectral slope** -> naturalness / processing fluency
    (Graham & Field, 2007; Redies);
  * **mirror-symmetry correlations** (L-R, T-B) -> symmetry preference / fluency.
"""
from __future__ import annotations

import numpy as np

from ..base import AnalyzerAdapter, License, clip01, get_gray, get_rgb


def _luminance(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (0.2126 * r + 0.7152 * g + 0.0722 * b).astype(np.float64)


class ProximalStatsAdapter(AnalyzerAdapter):
    name = "proximal_stats"
    tool = "cnfa-native(numpy/scipy/skimage/opencv)"
    tool_version = "1.0"
    license_class = License.PERMISSIVE
    enable_flag = "enable_proximal_stats"
    requires = ("scipy", "skimage")
    provides = (
        "cnfa.light.luminance_mean",
        "cnfa.light.rms_contrast",
        "cnfa.material.luminance_skew",
        "cnfa.material.luminance_kurtosis",
        "cnfa.material.subband_skew",
        "cnfa.geometry.edge_density_canny",
        "cnfa.geometry.straight_edge_ratio",
        "cnfa.dynamic.depth_of_field",
        "cnfa.fluency.radial_spectral_slope",
        "cnfa.fluency.symmetry_lr_corr",
        "cnfa.fluency.symmetry_tb_corr",
    )

    def _analyze(self, frame) -> None:
        from scipy import ndimage, stats

        rgb = get_rgb(frame)
        gray = get_gray(frame)
        lum = _luminance(rgb)

        # --- luminance level & contrast
        mean_l = float(lum.mean())
        self.emit(frame, "cnfa.light.luminance_mean", mean_l / 255.0, units="0-1")
        rms = float(lum.std() / (mean_l + 1e-9))
        self.emit(frame, "cnfa.light.rms_contrast", rms)

        # --- Motoyoshi gloss cues: skew / kurtosis of luminance histogram
        self.emit(frame, "cnfa.material.luminance_skew", float(stats.skew(lum, axis=None)),
                  extra={"cue": "perceived gloss (Motoyoshi 2007)"})
        self.emit(frame, "cnfa.material.luminance_kurtosis",
                  float(stats.kurtosis(lum, axis=None)))
        # sub-band skew: high-pass = lum - gaussian(lum)
        hp = lum - ndimage.gaussian_filter(lum, sigma=2.0)
        self.emit(frame, "cnfa.material.subband_skew", float(stats.skew(hp, axis=None)),
                  extra={"cue": "stronger gloss predictor (sub-band skew)"})

        # --- edges: density + straight-vs-curved ratio (rectilinearity)
        edges, straight_ratio, edge_density = self._edge_stats(gray)
        self.emit(frame, "cnfa.geometry.edge_density_canny", edge_density)
        if straight_ratio is not None:
            self.emit(frame, "cnfa.geometry.straight_edge_ratio", clip01(straight_ratio),
                      extra={"note": "Hough-line pixels / edge pixels; 1=rectilinear"})

        # --- blur / depth-of-field
        try:
            from skimage.measure import blur_effect
            blur = float(blur_effect(gray))  # 0 sharp .. 1 blurred
            self.emit(frame, "cnfa.dynamic.depth_of_field", blur,
                      extra={"note": "0=sharp everywhere, 1=blurred (DoF proxy)"})
        except Exception:
            pass

        # --- radial 1/f power-spectrum slope (native cross-check on AT's)
        slope = self._radial_slope(lum)
        if slope is not None:
            self.emit(frame, "cnfa.fluency.radial_spectral_slope", slope,
                      units="log-log slope", extra={"note": "cross-check on spectral_slope"})

        # --- mirror-symmetry correlations (interpretable [0,1])
        lr = self._mirror_corr(lum, axis=1)
        tb = self._mirror_corr(lum, axis=0)
        if lr is not None:
            self.emit(frame, "cnfa.fluency.symmetry_lr_corr", lr)
        if tb is not None:
            self.emit(frame, "cnfa.fluency.symmetry_tb_corr", tb)

    # ---- helpers ----------------------------------------------------------
    @staticmethod
    def _edge_stats(gray):
        try:
            import cv2
            g = np.ascontiguousarray(gray)
            edges = cv2.Canny(g, 80, 160)
            n_edge = int((edges > 0).sum())
            edge_density = n_edge / edges.size
            if n_edge < 50:
                return edges, None, edge_density
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50,
                                    minLineLength=max(10, gray.shape[0] // 12),
                                    maxLineGap=5)
            if lines is None:
                return edges, 0.0, edge_density
            # count edge pixels lying on detected straight segments
            mask = np.zeros_like(edges)
            for x1, y1, x2, y2 in lines[:, 0, :]:
                cv2.line(mask, (x1, y1), (x2, y2), 255, 2)
            straight = int(((edges > 0) & (mask > 0)).sum())
            return edges, straight / max(n_edge, 1), edge_density
        except Exception:
            return None, None, 0.0

    @staticmethod
    def _radial_slope(lum):
        try:
            f = np.fft.fftshift(np.fft.fft2(lum - lum.mean()))
            power = np.abs(f) ** 2
            h, w = power.shape
            cy, cx = h // 2, w // 2
            y, x = np.indices((h, w))
            r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2).astype(int)
            rmax = min(cx, cy)
            radial = np.array([power[r == i].mean() for i in range(1, rmax)])
            freqs = np.arange(1, rmax)
            good = radial > 0
            if good.sum() < 10:
                return None
            slope = np.polyfit(np.log(freqs[good]), np.log(radial[good]), 1)[0]
            return float(slope)
        except Exception:
            return None

    @staticmethod
    def _mirror_corr(lum, axis):
        try:
            if axis == 1:
                h, w = lum.shape
                a = lum[:, : w // 2]
                b = lum[:, w - w // 2:][:, ::-1]
            else:
                h, w = lum.shape
                a = lum[: h // 2, :]
                b = lum[h - h // 2:, :][::-1, :]
            a = a.ravel().astype(np.float64)
            b = b.ravel().astype(np.float64)
            if a.std() < 1e-6 or b.std() < 1e-6:
                return None
            c = float(np.corrcoef(a, b)[0, 1])
            return clip01((c + 1.0) / 2.0)  # map [-1,1] -> [0,1]
        except Exception:
            return None
