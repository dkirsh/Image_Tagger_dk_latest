"""Registry-integrity tests — no heavy dependencies required.

Mirrors the repo's `test_feature_registry_coverage` discipline: the set of keys
the adapters claim to fill must stay in sync with the cheat-sheet, and the
licence gate must actually gate.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters import ALL_ADAPTERS, PERMISSIVE_ADAPTERS, WORKER_ADAPTERS  # noqa: E402
from cnfa_adapters import License, STUB_TO_FUNCTION, select_adapters  # noqa: E402
from cnfa_adapters.mapping import PROXIMAL_DISTAL  # noqa: E402


def test_every_provided_key_is_in_cheatsheet():
    missing = []
    for cls in ALL_ADAPTERS:
        for key in cls.provides:
            if key not in STUB_TO_FUNCTION:
                missing.append((cls.__name__, key))
    assert not missing, "provides keys absent from STUB_TO_FUNCTION: %s" % missing


def test_permissive_adapters_do_not_collide():
    """No two permissive adapters may silently own the same cnfa key."""
    seen = {}
    for cls in PERMISSIVE_ADAPTERS:
        for key in cls.provides:
            assert key not in seen, "key %s owned by both %s and %s" % (
                key, seen[key], cls.__name__)
            seen[key] = cls.__name__


def test_commercial_policy_excludes_nonpermissive():
    commercial = select_adapters(policy="commercial", include_workers=True)
    assert all(a.license_class == License.PERMISSIVE for a in commercial)
    # The research-only saliency adapter must NOT be in a commercial build.
    names = {a.name for a in commercial}
    assert "saliency_deepgaze" not in names


def test_research_policy_includes_workers():
    research = select_adapters(policy="research", include_workers=True)
    names = {a.name for a in research}
    assert {"depth_midas", "segmentation_sam", "saliency_deepgaze"} <= names


def test_enable_flags_are_unique():
    flags = [c.enable_flag for c in ALL_ADAPTERS]
    assert len(flags) == len(set(flags)), "duplicate enable_flags: %s" % flags


def test_mapping_keys_are_real_attributes():
    """Every proximal->distal link must reference a key the adapters can fill."""
    bad = [l.key for l in PROXIMAL_DISTAL if l.key not in STUB_TO_FUNCTION]
    assert not bad, "mapping references unknown cnfa keys: %s" % bad


def test_mapping_status_values_are_valid():
    allowed = {"established", "supported-with-debate", "proxy", "exploratory"}
    bad = [(l.key, l.status) for l in PROXIMAL_DISTAL if l.status not in allowed]
    assert not bad, "invalid status values: %s" % bad


if __name__ == "__main__":
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, "__name__", "").startswith("test_"):
            fn()
            print("PASS", fn.__name__)
    print("registry tests OK")
