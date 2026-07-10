"""cnfa_adapters — wrap open-source visual toolboxes as repo-compatible
analyzers that fill the `cnfa.*` stubs of the Image Tagger cognitive-code bank.

Quick start (standalone, outside the repo):

    from cnfa_adapters import StandaloneFrame, select_adapters, run_frame
    frame = StandaloneFrame.from_path("room.jpg")
    run_frame(frame, select_adapters(policy="commercial", include_workers=False))
    print(frame.as_dict())

Dropping into the repo: copy this package under backend/science/adapters/,
register each adapter behind its enable_flag in pipeline.py, and move the keys
it `provides` out of STUB_FEATURE_KEYS.
"""
from .base import AnalyzerAdapter, License
from .frame import StandaloneFrame
from .registry import (
    ALL_ADAPTERS,
    PERMISSIVE_ADAPTERS,
    STUB_TO_FUNCTION,
    WORKER_ADAPTERS,
    run_frame,
    select_adapters,
)

__all__ = [
    "AnalyzerAdapter",
    "License",
    "StandaloneFrame",
    "ALL_ADAPTERS",
    "PERMISSIVE_ADAPTERS",
    "WORKER_ADAPTERS",
    "STUB_TO_FUNCTION",
    "select_adapters",
    "run_frame",
]
