"""Adapter for visual-clutter (kargaranamir) — a Python port of Rosenholtz's
Feature Congestion and Subband Entropy clutter measures.

Rosenholtz, R., Li, Y., & Nakano, L. (2007). Measuring visual clutter.
*Journal of Vision*, 7(2), 17. A validated, citable clutter measure — the
principled replacement for a home-grown object count.

The `Vlc` class is constructed on an image *path* (not an array), so the
adapter uses base.get_path(frame), which materialises a temp PNG from the RGB
buffer when the frame has no path. The compat shim (imported via base) restores
`PIL.Image.ANTIALIAS` so the upstream code runs unmodified on modern Pillow.
"""
from __future__ import annotations

import numpy as np

from ..base import AnalyzerAdapter, License, get_path


def _scalar(x):
    """getClutter_FC returns (scalar, map); getClutter_SE returns a scalar."""
    if isinstance(x, tuple):
        return float(np.asarray(x[0]).mean())
    return float(np.asarray(x).mean())


class VisualClutterAdapter(AnalyzerAdapter):
    name = "visual_clutter"
    tool = "visual-clutter(kargaranamir)"
    tool_version = "1.0"
    license_class = License.PERMISSIVE  # MIT/BSD
    enable_flag = "enable_visual_clutter"
    requires = ("visual_clutter",)
    provides = (
        "cnfa.fluency.clutter_density_count",
        "cnfa.fluency.subband_entropy_clutter",
    )

    def _analyze(self, frame) -> None:
        import os
        import tempfile
        from visual_clutter import Vlc

        path = os.path.abspath(get_path(frame))

        # visual-clutter writes intermediate map PNGs into the current working
        # directory; run it inside a throwaway temp dir so it never litters the
        # repo, then restore cwd.
        prev = os.getcwd()
        tmp = tempfile.mkdtemp(prefix="cnfa_vlc_")
        try:
            os.chdir(tmp)
            v = Vlc(path, numlevels=3, contrast_filt_sigma=1,
                    contrast_pool_sigma=3, color_pool_sigma=3)
            fc = v.getClutter_FC(p=1, pix=1)   # Feature Congestion (overall)
            se = v.getClutter_SE()             # Subband Entropy (encoding cost)
        finally:
            os.chdir(prev)
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

        self.emit(frame, "cnfa.fluency.clutter_density_count", _scalar(fc),
                  units="feature-congestion")
        # cross-check on spatial entropy vs the Aesthetics-Toolbox first-order entropy
        self.emit(frame, "cnfa.fluency.subband_entropy_clutter", _scalar(se),
                  units="subband-entropy")
