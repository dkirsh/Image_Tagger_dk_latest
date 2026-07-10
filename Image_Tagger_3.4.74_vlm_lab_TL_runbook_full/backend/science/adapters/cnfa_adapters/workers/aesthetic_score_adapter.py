"""Aesthetic / quality-score worker adapter — pyiqa (NIMA, MUSIQ, CLIP-IQA) or
BUPT TANet/EAT.

These emit a single learned "beauty/quality" number. Crucially these are NOT
cognitive-code metrics — they are an *independent validation signal* to
correlate against the causal cnfa.* features (does the evidence-based bank track
a learned aesthetic score?). They are therefore written under `cnfa.evaluation.*`,
a namespace kept out of the scored feature bank.

Licence: pyiqa *code* is Apache-2.0, but several *weights* (and the AVA/TAD66K
training provenance) are research-only/non-commercial. Tagged NONCOMMERCIAL;
use the permissive-weighted metrics only, or self-train, before any commercial
use. Gate keeps it in the `research` config.
"""
from __future__ import annotations

from ..base import License
from .worker_base import ModelWorkerAdapter


class AestheticScoreAdapter(ModelWorkerAdapter):
    name = "aesthetic_score"
    tool = "pyiqa(NIMA/MUSIQ)"
    tool_version = "nima+musiq"
    license_class = License.NONCOMMERCIAL
    enable_flag = "enable_aesthetic_score"
    worker_script = "aesthetic_worker.py"
    worker_python_env = "CNFA_IQA_PYTHON"
    provides = (
        "cnfa.evaluation.aesthetic_score",
        "cnfa.evaluation.quality_score",
    )

    def map_result(self, frame, result: dict) -> None:
        aes = result.get("aesthetic")
        qual = result.get("quality")
        if aes is not None:
            self.emit(frame, "cnfa.evaluation.aesthetic_score", float(aes),
                      confidence=0.7, extra={"model": "NIMA", "role": "validation-only"})
        if qual is not None:
            self.emit(frame, "cnfa.evaluation.quality_score", float(qual),
                      confidence=0.7, extra={"model": "MUSIQ", "role": "validation-only"})
