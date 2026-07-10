"""Adapter for colour-science (`colour`, BSD) plus a Hasler-Susstrunk
colourfulness helper.

Provides the perceptual colour-temperature signal (warm vs cool light, a lever
tied to arousal/comfort in the corpus) and an image colourfulness metric.

  * Correlated Colour Temperature (CCT) via colour.temperature.xy_to_CCT
    (McCamy 1992 approximation) from the image's mean chromaticity.
  * warm_vs_cool_ratio: CCT mapped to [0,1], 1 = warm (~2000 K),
    0 = cool (~6500 K). Documented linear window.
  * colourfulness: Hasler & Susstrunk (2003), "Measuring colourfulness in
    natural images", Proc. SPIE 5007. A ~6-line opponent-channel statistic.
"""
from __future__ import annotations

import numpy as np

from ..base import AnalyzerAdapter, License, clip01, get_rgb

_WARM_K = 2000.0
_COOL_K = 6500.0


def hasler_susstrunk_colourfulness(rgb: np.ndarray) -> float:
    r = rgb[:, :, 0].astype(np.float64)
    g = rgb[:, :, 1].astype(np.float64)
    b = rgb[:, :, 2].astype(np.float64)
    rg = r - g
    yb = 0.5 * (r + g) - b
    std_root = np.sqrt(rg.std() ** 2 + yb.std() ** 2)
    mean_root = np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    return float(std_root + 0.3 * mean_root)


class ColourAdapter(AnalyzerAdapter):
    name = "colour_science"
    tool = "colour-science"
    tool_version = "0.4"
    license_class = License.PERMISSIVE  # BSD
    enable_flag = "enable_colour"
    requires = ("colour",)
    provides = (
        "cnfa.light.cct_kelvin",
        "cnfa.light.warm_vs_cool_ratio",
        "cnfa.fluency.colorfulness",
    )

    def _analyze(self, frame) -> None:
        import colour

        rgb = get_rgb(frame)

        # Colourfulness (always computable).
        self.emit(frame, "cnfa.fluency.colorfulness",
                  hasler_susstrunk_colourfulness(rgb), units="Hasler-Susstrunk")

        # CCT from mean chromaticity.
        mean_rgb = (rgb.reshape(-1, 3).mean(0) / 255.0)
        try:
            XYZ = colour.sRGB_to_XYZ(mean_rgb)
            xy = colour.XYZ_to_xy(XYZ)
            cct = float(colour.temperature.xy_to_CCT(xy, method="McCamy 1992"))
        except Exception:
            return
        if not np.isfinite(cct) or cct <= 0:
            return
        self.emit(frame, "cnfa.light.cct_kelvin", cct, units="K")
        warm = clip01((_COOL_K - cct) / (_COOL_K - _WARM_K))
        self.emit(frame, "cnfa.light.warm_vs_cool_ratio", warm,
                  units="0=cool..1=warm",
                  extra={"cct_kelvin": round(cct, 1)})
