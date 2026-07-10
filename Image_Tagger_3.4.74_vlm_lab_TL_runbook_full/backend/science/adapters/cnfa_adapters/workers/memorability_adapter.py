"""Memorability worker adapter — ResMem / ViTMem.

Image memorability is a robust, intrinsic image property (Isola, Khosla, Oliva,
Torralba) — how likely a scene is to be remembered — with clear relevance to
wayfinding, landmark legibility and the "identity" of a space. ResMem
(Needell & Bainbridge, UChicago; trained on MIT LaMem) and ViTMem (Hagen &
Espeseth, 2023) are the modern single-image predictors.

Licence: **non-commercial**. The ResMem weights are released under a UChicago
non-commercial licence (for-profit *internal research* is allowed; shipping in a
product needs a licence). Tagged NONCOMMERCIAL, so the licence gate keeps this
out of a commercial build and in the `research` config only.
"""
from __future__ import annotations

from ..base import License, clip01
from .worker_base import ModelWorkerAdapter


class MemorabilityAdapter(ModelWorkerAdapter):
    name = "memorability"
    tool = "ResMem/ViTMem"
    tool_version = "resmem"
    license_class = License.NONCOMMERCIAL
    enable_flag = "enable_memorability"
    worker_script = "memorability_worker.py"
    worker_python_env = "CNFA_MEM_PYTHON"
    provides = ("cnfa.cognitive.memorability",)

    def map_result(self, frame, result: dict) -> None:
        mem = result.get("memorability")
        if mem is not None:
            self.emit(frame, "cnfa.cognitive.memorability", clip01(mem),
                      confidence=0.8, extra={"model": result.get("source")})
