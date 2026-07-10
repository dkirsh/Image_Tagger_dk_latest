"""Depth worker adapter — MiDaS (isl-org, MIT) monocular depth.

A depth map turns a single photo or render into the spatial family. The worker
returns summary statistics of the inverse-depth map; this adapter reduces them
to `cnfa.spatial.*` and `cnfa.dynamic.texture_gradient`.

SCAFFOLD STATUS: the depth->isovist reduction here is a documented first
approximation (near/far fractions, vertical gradient). The rigorous versions of
enclosure_index / isovist_openness / prospect_to_refuge come from the repo's
isovist.py run on the depth-recovered pseudo-geometry (or, for a 3D model, from
the mesh directly). Marked so the placeholder maths is never mistaken for the
validated computation.

Licence: MiDaS is MIT (permissive). Prefer MiDaS or Depth-Anything-V2-small
(Apache) over Depth-Anything-V2-large (CC-BY-NC) for a shipped product.
"""
from __future__ import annotations

from ..base import License, clip01
from .worker_base import ModelWorkerAdapter


class DepthMidasAdapter(ModelWorkerAdapter):
    name = "depth_midas"
    tool = "MiDaS"
    tool_version = "DPT_Large"
    license_class = License.PERMISSIVE  # MiDaS MIT
    enable_flag = "enable_depth_midas"
    worker_script = "midas_worker.py"
    worker_python_env = "CNFA_MIDAS_PYTHON"
    provides = (
        "cnfa.spatial.enclosure_index",
        "cnfa.spatial.isovist_openness",
        "cnfa.spatial.ceiling_height_avg",
        "cnfa.spatial.prospect_to_refuge_ratio",
        "cnfa.dynamic.texture_gradient",
    )

    def map_result(self, frame, result: dict) -> None:
        near = result.get("near_fraction")       # fraction of pixels close
        far = result.get("far_fraction")         # fraction of pixels distant
        vgrad = result.get("vertical_gradient")  # mean top->bottom depth slope
        grad_mag = result.get("gradient_magnitude")

        if near is not None:
            self.emit(frame, "cnfa.spatial.enclosure_index", clip01(near),
                      confidence=0.6, extra={"note": "depth-proxy; prefer isovist.py"})
        if far is not None:
            self.emit(frame, "cnfa.spatial.isovist_openness", clip01(far),
                      confidence=0.6, extra={"note": "depth-proxy"})
        if near is not None and far is not None and near > 1e-6:
            self.emit(frame, "cnfa.spatial.prospect_to_refuge_ratio", float(far / near),
                      confidence=0.5, extra={"note": "depth-proxy far/near"})
        if vgrad is not None:
            self.emit(frame, "cnfa.spatial.ceiling_height_avg", float(vgrad),
                      confidence=0.4, units="relative", extra={"note": "proxy only"})
        if grad_mag is not None:
            self.emit(frame, "cnfa.dynamic.texture_gradient", float(grad_mag),
                      confidence=0.6)
