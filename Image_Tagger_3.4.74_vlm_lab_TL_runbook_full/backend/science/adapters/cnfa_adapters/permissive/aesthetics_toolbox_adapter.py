"""Adapter for the Aesthetics-Toolbox (rbartho) — the maintained, MIT-licensed
successor to the Max Planck / Redies "quantitative image properties" (QIP)
tradition. Paper: Bartho et al. (2025), *Behavior Research Methods*,
doi:10.3758/s13428-025-02632-3.

This single adapter is the anchor: it fills fractal, spectral-slope, entropy,
edge, symmetry, balance, PHOG (self-similarity / complexity / anisotropy) and
colour-entropy keys. Function names and their call conventions are read from
the toolbox source (AT/*_qips.py) and mirror the toolbox's own
`QIP_machine_script.py` preprocessing:

    img_rgb  = np.asarray(Image.open(path).convert('RGB'))
    img_gray = np.asarray(Image.open(path).convert('L'))   # uint8 [0,255]

Note on scales: these QIPs are raw statistics on their own natural scales
(fractal D in ~[1,2]; Fourier slope ~ -1 to -3; entropy in bits [0,8];
mirror-symmetry / balance / homogeneity are the toolbox's own indices). We emit
them faithfully rather than squashing them into a misleading [0,1] "score";
documented normalisation windows live in registry.py / LICENSING.md.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

import numpy as np

from ..base import AnalyzerAdapter, License, get_gray, get_rgb


def _locate_toolbox() -> Optional[str]:
    """Find the aesthetics-toolbox source so `import AT.*` works.

    Resolution order: env var AESTHETICS_TOOLBOX_PATH, then a vendored copy
    under third_party/, then whatever is already importable.
    """
    env = os.environ.get("AESTHETICS_TOOLBOX_PATH")
    candidates = []
    if env:
        candidates.append(env)
    here = os.path.dirname(__file__)
    candidates += [
        os.path.abspath(os.path.join(here, "..", "..", "third_party", "aesthetics-toolbox")),
        os.path.abspath(os.path.join(here, "..", "..", "third_party", "aesthetics_toolbox")),
    ]
    for c in candidates:
        if c and os.path.isdir(os.path.join(c, "AT")):
            return c
    return None


_TB = _locate_toolbox()
if _TB and _TB not in sys.path:
    sys.path.insert(0, _TB)


class AestheticsToolboxAdapter(AnalyzerAdapter):
    name = "aesthetics_toolbox"
    tool = "aesthetics-toolbox(rbartho)"
    tool_version = "2025.bartho"
    license_class = License.PERMISSIVE  # MIT
    enable_flag = "enable_aesthetics_toolbox"
    requires = ("AT.fractal_dimension_qips",)  # presence of the toolbox on path
    provides = (
        "cnfa.fractal_dimension",
        "cnfa.fluency.spectral_slope",
        "cnfa.fluency.visual_entropy_spatial",
        "cnfa.fluency.second_order_entropy",
        "cnfa.fluency.edge_clarity_mean",
        "cnfa.fluency.symmetry_score_horizontal",
        "cnfa.fluency.pattern_rhythm_regularity",
        "cnfa.fluency.balance_qip",
        "cnfa.fluency.self_similarity",
        "cnfa.fluency.hierarchy_depth",
        "cnfa.fluency.anisotropy",
        "cnfa.fluency.color_palette_entropy",
    )

    def _analyze(self, frame) -> None:
        from AT import balance_qips as BAL
        from AT import color_and_simple_qips as COL
        from AT import edge_entropy_qips as EE
        from AT import fractal_dimension_qips as FD
        from AT import PHOG_qips as PHOG

        gray = get_gray(frame)
        rgb = get_rgb(frame)
        # Near-constant images have no edges, and the toolbox's edge-orientation
        # entropy / PHOG / Fourier routines degenerate (do_counting runs away).
        # Gate that group on real structure; the cheap, safe QIPs always run.
        structured = float(np.asarray(gray, dtype=float).std()) >= 1.0

        # --- always-safe, cheap QIPs (each isolated) ------------------------
        self._try(frame, "cnfa.fractal_dimension",
                  lambda: FD.fractal_dimension_2d(gray), units="box-counting D")
        self._try(frame, "cnfa.fluency.symmetry_score_horizontal",
                  lambda: BAL.Mirror_symmetry(gray), units="QIP mirror-symmetry index",
                  extra={"note": "Redies QIP mirror-symmetry statistic, not a [0,1] score"})
        self._try(frame, "cnfa.fluency.balance_qip",
                  lambda: BAL.Balance(gray), units="DCM imbalance (0=balanced)")
        self._try(frame, "cnfa.fluency.pattern_rhythm_regularity",
                  lambda: BAL.Homogeneity(gray), units="QIP homogeneity index")

        def _col_ent():
            v = COL.shannonentropy_channels(rgb)
            return float(np.mean(np.asarray(v, dtype=float)))
        self._try(frame, "cnfa.fluency.color_palette_entropy", _col_ent, units="bits")

        if not structured:
            return

        # --- edge-orientation entropy + edge density (structured images only)
        try:
            first_e, second_e, edge_density = \
                EE.do_first_and_second_order_entropy_and_edge_density(gray)
            self.emit(frame, "cnfa.fluency.visual_entropy_spatial", first_e, units="bits")
            self.emit(frame, "cnfa.fluency.second_order_entropy", second_e, units="bits")
            self.emit(frame, "cnfa.fluency.edge_clarity_mean", edge_density, units="edge-density")
        except Exception:
            pass

        # --- PHOG: self-similarity, complexity, anisotropy (Redies family)
        try:
            self_sim, complexity, anisotropy = PHOG.PHOGfromImage(
                rgb, section=2, bins=16, angle=360, levels=3, re=-1, sesfweight=[1, 1, 1])
            self.emit(frame, "cnfa.fluency.self_similarity", self_sim)
            self.emit(frame, "cnfa.fluency.hierarchy_depth", complexity,
                      extra={"note": "PHOG complexity (pyramid HOG)"})
            self.emit(frame, "cnfa.fluency.anisotropy", anisotropy)
        except Exception:
            pass

        # --- Fourier spectral slope (the 1/f statistic). Needs statsmodels.
        try:
            from AT import fourier_qips as FOU
            self.emit(frame, "cnfa.fluency.spectral_slope",
                      FOU.fourier_slope_branka_Spehar_Isherwood(gray),
                      units="log-log power-spectrum slope")
        except Exception:
            pass

    def _try(self, frame, key, fn, **kw):
        try:
            self.emit(frame, key, fn(), **kw)
        except Exception:
            pass
