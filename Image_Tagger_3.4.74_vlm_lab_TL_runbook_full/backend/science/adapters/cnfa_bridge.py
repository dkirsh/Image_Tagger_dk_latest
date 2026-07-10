"""Bridge analyzer — run the open-source cognitive-code adapters inside the
science pipeline, matching the repo's analyzer pattern.

Usage in pipeline.py (opt-in, non-invasive):

    from backend.science.adapters.cnfa_bridge import CNFAAdapters
    # in __init__:
    self.cnfa = CNFAAdapters(policy="commercial")   # owned/permissive build
    # in process_image, alongside the other analyzers:
    if getattr(self.config, "enable_cnfa_adapters", False):
        self.cnfa.analyze(frame)

Two builds via `policy`:
  * "commercial"  -> owned build: permissive (MIT/BSD/Apache) adapters only.
  * "research"    -> adds the GPL / non-commercial workers (gated out of shipping).

The isovist adapter is included in the permissive set but no-ops unless the
frame carries a `plan` + `viewpoint` (the 3D-model / floor-plan path).
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from backend.science.adapters.cnfa_adapters import run_frame, select_adapters
    _CNFA_OK = True
except Exception as exc:  # pragma: no cover - import guarded so pipeline never breaks
    logger.warning("cnfa_adapters unavailable: %r", exc)
    _CNFA_OK = False


class CNFAAdapters:
    """Runs the cognitive-code adapters against an AnalysisFrame."""

    def __init__(self, policy: str = "commercial", include_workers: bool = False,
                 config: dict | None = None):
        self.policy = policy
        self.include_workers = include_workers
        self.adapters = []
        if _CNFA_OK:
            try:
                self.adapters = select_adapters(policy=policy, config=config,
                                                include_workers=include_workers)
            except Exception as exc:
                logger.warning("cnfa adapter selection failed: %r", exc)

    def analyze(self, frame) -> None:
        if not self.adapters:
            return
        run_frame(frame, self.adapters)

    @property
    def provided_keys(self):
        keys = []
        for a in self.adapters:
            keys.extend(a.provides)
        return keys
