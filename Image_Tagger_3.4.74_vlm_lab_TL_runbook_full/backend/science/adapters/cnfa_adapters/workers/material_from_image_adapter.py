"""Material-from-image worker adapter — learned perceptual material attributes.

Recovers material properties from a single image, the honest counterpart to the
permissive Motoyoshi image-statistics gloss cue in ProximalStatsAdapter.
Candidate backends:
  * Guerrero-Viu et al. (2024), "Predicting Perceived Gloss" (Zaragoza) —
    perceived gloss from one image;
  * Kocsis et al. (2024), Intrinsic Image Diffusion — albedo/roughness/metallic
    maps for indoor images;
  * Careaga & Aksoy, compphoto/Intrinsic — albedo/shading (academic-use).

Licence: mixed — several are academic-use / GPL. Tagged RESEARCH; the licence
gate keeps this in the `research` config. For a commercial build, rely on the
permissive luminance/sub-band-skew gloss cues (ProximalStatsAdapter) until a
commercially-licensed material model is available.
"""
from __future__ import annotations

from ..base import License, clip01
from .worker_base import ModelWorkerAdapter


class MaterialFromImageAdapter(ModelWorkerAdapter):
    name = "material_from_image"
    tool = "perceived-gloss/intrinsic"
    tool_version = "research"
    license_class = License.RESEARCH
    enable_flag = "enable_material_from_image"
    worker_script = "material_worker.py"
    worker_python_env = "CNFA_MATERIAL_PYTHON"
    provides = (
        "cnfa.material.perceived_gloss",
        "cnfa.material.albedo_mean",
        "cnfa.material.metallicness",
    )

    def map_result(self, frame, result: dict) -> None:
        if (g := result.get("gloss")) is not None:
            self.emit(frame, "cnfa.material.perceived_gloss", clip01(g), confidence=0.6)
        if (a := result.get("albedo")) is not None:
            self.emit(frame, "cnfa.material.albedo_mean", clip01(a), confidence=0.6)
        if (m := result.get("metallic")) is not None:
            self.emit(frame, "cnfa.material.metallicness", clip01(m), confidence=0.5)
