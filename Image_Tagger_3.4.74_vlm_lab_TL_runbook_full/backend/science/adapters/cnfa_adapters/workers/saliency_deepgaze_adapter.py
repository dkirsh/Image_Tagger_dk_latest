"""Saliency worker adapter — DeepGaze IIE/III (matthias-k).

A fixation-density (saliency) map yields where the eye goes: the peak
concentration is a landmark-salience signal, and how cleanly one region
dominates is a figure-ground-clarity signal.

Licence: the DeepGaze *code* is usable but the pretrained *weights* are
research-only, so this adapter is tagged RESEARCH and the license gate keeps it
out of a commercial build. Swap in a permissively-weighted saliency model, or a
classical Itti-Koch map (via pliers), for a shipped product.
"""
from __future__ import annotations

from ..base import License, clip01
from .worker_base import ModelWorkerAdapter


class SaliencyDeepGazeAdapter(ModelWorkerAdapter):
    name = "saliency_deepgaze"
    tool = "DeepGaze"
    tool_version = "IIE"
    license_class = License.RESEARCH  # weights research-only
    enable_flag = "enable_saliency"
    worker_script = "deepgaze_worker.py"
    worker_python_env = "CNFA_SALIENCY_PYTHON"
    provides = (
        "cnfa.cognitive.landmark_salience",
        "cnfa.fluency.figure_ground_clarity",
    )

    def map_result(self, frame, result: dict) -> None:
        peak = result.get("peak_salience")        # max of normalised map
        concentration = result.get("concentration")  # 1 - normalised entropy
        if peak is not None:
            self.emit(frame, "cnfa.cognitive.landmark_salience", clip01(peak),
                      confidence=0.7)
        if concentration is not None:
            self.emit(frame, "cnfa.fluency.figure_ground_clarity", clip01(concentration),
                      confidence=0.7)
