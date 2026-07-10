"""Test configuration: locate the vendored Aesthetics-Toolbox if present.

The AestheticsToolboxAdapter resolves the toolbox via the
AESTHETICS_TOOLBOX_PATH env var or a third_party/ copy. For local runs where
you have the toolbox cloned elsewhere, export AESTHETICS_TOOLBOX_PATH before
running the suite. This conftest only fills in a sensible default and never
overrides an explicit setting.
"""
import os

_here = os.path.dirname(__file__)
_candidates = [
    os.path.abspath(os.path.join(_here, "..", "third_party", "aesthetics-toolbox")),
    os.path.abspath(os.path.join(_here, "..", "third_party", "aesthetics_toolbox")),
]
if "AESTHETICS_TOOLBOX_PATH" not in os.environ:
    for c in _candidates:
        if os.path.isdir(os.path.join(c, "AT")):
            os.environ["AESTHETICS_TOOLBOX_PATH"] = c
            break
