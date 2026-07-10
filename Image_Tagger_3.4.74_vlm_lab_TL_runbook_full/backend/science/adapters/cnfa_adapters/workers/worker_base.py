"""Isolated model-worker base.

The deep-learning tools (MiDaS depth, SAM/OneFormer segmentation, DeepGaze
saliency) have heavy, mutually-incompatible dependencies (different Torch
builds, GPU vs CPU) and, in some cases, non-commercial weights. The failure
mode is importing them all into one environment. So each runs as an *isolated
worker*: its own pinned Python/venv, invoked over a subprocess with a JSON
contract. The adapter (in the main science env) only shells out and maps the
returned numbers to `cnfa.*` keys; the worker owns the messy deps and can batch
and cache on the GPU.

Contract:
    <worker_python> <script.py> --image <path> [--params <json>]
    -> prints a single JSON object to stdout: {"ok": true, ...features...}
       or {"ok": false, "error": "..."}.

Configure the worker interpreter per tool with an env var (e.g.
CNFA_MIDAS_PYTHON=/opt/venvs/midas/bin/python); defaults to the current
interpreter so the scaffolding is runnable once the tool is pip-installed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Optional

from ..base import AnalyzerAdapter, get_path

_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")


class ModelWorkerAdapter(AnalyzerAdapter):
    worker_script: str = ""          # filename in scripts/
    worker_python_env: str = ""      # env var naming the worker interpreter
    worker_timeout_s: int = 120

    def _worker_python(self) -> str:
        return os.environ.get(self.worker_python_env, sys.executable)

    def _script_path(self) -> str:
        return os.path.join(_SCRIPTS_DIR, self.worker_script)

    @classmethod
    def available(cls) -> bool:
        # The worker is "available" if its script exists; whether the heavy
        # deps are installed is discovered at call time (the worker reports
        # ok:false, and analyze() handles that quietly). This keeps the
        # scaffold registerable without the models present.
        return os.path.exists(os.path.join(_SCRIPTS_DIR, cls.worker_script))

    def run_worker(self, image_path: str, params: Optional[dict] = None) -> dict:
        cmd = [self._worker_python(), self._script_path(), "--image", image_path]
        if params:
            cmd += ["--params", json.dumps(params)]
        try:
            out = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.worker_timeout_s
            )
        except Exception as exc:  # timeout / spawn failure
            return {"ok": False, "error": "spawn: %r" % exc}
        stdout = (out.stdout or "").strip()
        if not stdout:
            return {"ok": False, "error": (out.stderr or "no output")[:200]}
        try:
            # Take the last JSON line (models are chatty on stdout).
            line = [l for l in stdout.splitlines() if l.strip().startswith("{")][-1]
            return json.loads(line)
        except Exception as exc:
            return {"ok": False, "error": "parse: %r" % exc}

    def _analyze(self, frame) -> None:
        result = self.run_worker(get_path(frame), self.worker_params(frame))
        if not result.get("ok"):
            return
        self.map_result(frame, result)

    # Subclasses override these two.
    def worker_params(self, frame) -> Optional[dict]:
        return None

    def map_result(self, frame, result: dict) -> None:  # pragma: no cover
        raise NotImplementedError
