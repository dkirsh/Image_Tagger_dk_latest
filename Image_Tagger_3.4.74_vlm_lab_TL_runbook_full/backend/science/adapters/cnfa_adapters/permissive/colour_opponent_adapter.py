"""Colour, described the way the early visual system encodes it (permissive).

Folk descriptions name colour as paint ("warm oak", "sage green"). The visual
system encodes it as opponent channels (luminance, red-green, blue-yellow) with
particular statistics — which is what actually drives colour affect and
salience. This adapter emits those deeper colour statistics:

  * CIELab means & SDs (perceptually-uniform lightness/colour spread);
  * LGN-style **opponent-channel energy** on a* (red-green) and b* (blue-yellow);
  * **hue entropy / colour variety** (HSV) — palette richness;
  * **saturation** mean & SD — vividness;
  * **dominant wavelength** (nm) via colour-science.

Uses scikit-image for colour-space conversion (BSD) and colour-science for the
dominant-wavelength colorimetry (BSD).
"""
from __future__ import annotations

import numpy as np

from ..base import AnalyzerAdapter, License, clip01, get_rgb


class ColourOpponentAdapter(AnalyzerAdapter):
    name = "colour_opponent"
    tool = "scikit-image+colour-science"
    tool_version = "1.0"
    license_class = License.PERMISSIVE  # BSD
    enable_flag = "enable_colour_opponent"
    requires = ("skimage",)
    provides = (
        "cnfa.color.lab_lightness_mean",
        "cnfa.color.lab_lightness_std",
        "cnfa.color.opponent_rg_mean",
        "cnfa.color.opponent_by_mean",
        "cnfa.color.opponent_rg_energy",
        "cnfa.color.opponent_by_energy",
        "cnfa.color.hue_entropy",
        "cnfa.color.saturation_mean",
        "cnfa.color.saturation_std",
        "cnfa.color.dominant_wavelength_nm",
    )

    def _analyze(self, frame) -> None:
        from skimage import color as skcolor

        rgb = get_rgb(frame)
        rgb01 = rgb.astype(np.float64) / 255.0

        lab = skcolor.rgb2lab(rgb01)
        L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
        self.emit(frame, "cnfa.color.lab_lightness_mean", float(L.mean()), units="L*")
        self.emit(frame, "cnfa.color.lab_lightness_std", float(L.std()), units="L*")
        self.emit(frame, "cnfa.color.opponent_rg_mean", float(a.mean()),
                  units="a* (>0 red,<0 green)")
        self.emit(frame, "cnfa.color.opponent_by_mean", float(b.mean()),
                  units="b* (>0 yellow,<0 blue)")
        self.emit(frame, "cnfa.color.opponent_rg_energy", float(np.abs(a).mean()))
        self.emit(frame, "cnfa.color.opponent_by_energy", float(np.abs(b).mean()))

        hsv = skcolor.rgb2hsv(rgb01)
        hue, sat = hsv[..., 0], hsv[..., 1]
        # hue entropy weighted by saturation (grey pixels have no meaningful hue)
        hist, _ = np.histogram(hue.ravel(), bins=36, range=(0, 1),
                               weights=sat.ravel())
        p = hist / (hist.sum() + 1e-12)
        p = p[p > 0]
        hue_entropy = float(-(p * np.log2(p)).sum()) if p.size else 0.0
        self.emit(frame, "cnfa.color.hue_entropy", hue_entropy, units="bits")
        self.emit(frame, "cnfa.color.saturation_mean", float(sat.mean()))
        self.emit(frame, "cnfa.color.saturation_std", float(sat.std()))

        # dominant wavelength from mean chromaticity
        try:
            import colour
            mean_rgb = rgb01.reshape(-1, 3).mean(0)
            XYZ = colour.sRGB_to_XYZ(mean_rgb)
            xy = colour.XYZ_to_xy(XYZ)
            wl = colour.dominant_wavelength(xy, (0.3127, 0.3290))[0]
            wl = float(np.atleast_1d(wl)[0])
            if np.isfinite(wl):
                self.emit(frame, "cnfa.color.dominant_wavelength_nm", abs(wl), units="nm")
        except Exception:
            pass
