"""
test_wave2_geometry — CC-4 (2026-07-20): W2.2-W2.5/W2.8 built + W2.1/W2.6 registered.

Per-file test (repo rule: PYTHONPATH=. python3 annotation_socket/tests/test_wave2_geometry.py).
Locks: registration completeness, honest-abstain contract, orderings, and determinism. The
algorithm-level orderings live in the module self-test (python3 -m cnfa_algs.wave2_geometry); this
file guards the SOCKET contract (registered, AMBER, abstain-not-UNKNOWN, deterministic scalars).
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import numpy as np
from cnfa_algs import wave2_geometry as WG
from cnfa_algs.geometry import FLOOR as GF, CEILING as GC, WALL as GW, OPENING as GO
from cnfa_algs.plan import FREE, OBST
from annotation_socket import registry as R

W2_IMAGE = ["cnfa.geometry.verticality_cues", "cnfa.geometry.ceiling_openness_relative",
            "cnfa.arch.double_height_space", "cnfa.geometry.blind_corner_index",
            "cnfa.geometry.barrier_permeability", "cnfa.arch.threshold_emphasized"]
W2_ALL = W2_IMAGE + ["cnfa.plan.choice_richness"]


class _PG:
    def __init__(s, grid, cell=0.4, conf=0.4):
        s.grid, s.cell_m, s.confidence = grid, cell, conf


def test_all_registered_amber():
    ids = {s["id"]: s for s in R.PREDICATES}
    for k in W2_ALL:
        assert k in ids, f"{k} not registered"
        assert ids[k]["tier_hint"] == "AMBER", (k, ids[k]["tier_hint"])   # Wave-2 rule
    # the six image ops must be able to abstain (signal-absent), never fabricate
    for k in W2_IMAGE:
        assert k in R.MAY_LACK_SIGNAL, f"{k} missing from MAY_LACK_SIGNAL"
    print("  registration: 7 wave-2 predicates AMBER; 6 abstain-capable  OK")


def test_abstain_contract():
    dummy = np.full((240, 320, 3), 150, np.uint8)
    # no ceiling -> W2.2/W2.3 abstain (scalar None)
    pl_noceil = np.full((240, 320), GW, np.uint8); pl_noceil[-40:] = GF
    assert WG.ceiling_openness_relative(dummy, pl_noceil).scalar is None
    assert WG.double_height_space(dummy, pl_noceil).scalar is None
    # no wall -> W2.5 abstains; no aperture -> W2.8 abstains
    assert WG.barrier_permeability(dummy, np.full((240, 320), GF, np.uint8)).scalar is None
    assert WG.threshold_emphasized(dummy, np.full((240, 320), GW, np.uint8)).scalar is None
    # tiny plan -> W2.4 abstains
    assert WG.blind_corner_index(_PG(np.full((20, 20), OBST, np.int8))).scalar is None
    print("  abstain contract: undefined substrate -> scalar=None (never fabricated)  OK")


def test_permeability_axes_not_averaged():
    dummy = np.full((240, 320, 3), 150, np.uint8)
    pl = np.full((240, 320), GW, np.uint8); pl[:, :160] = GO; pl[-30:] = GF
    r = WG.barrier_permeability(dummy, pl)
    v, p = r.extras["visual_permeability"], r.extras["physical_permeability"]
    assert abs(r.scalar - v) < 1e-4                      # scalar IS the visual axis
    # both axes present and reported separately (the "never average" rule)
    assert "visual_permeability" in r.extras and "physical_permeability" in r.extras
    print(f"  permeability axes separate: visual={v:.3f} physical={p:.3f}, scalar==visual  OK")


def test_determinism():
    dummy = np.full((240, 320, 3), 150, np.uint8)
    pl = np.full((240, 320), GW, np.uint8); pl[0:40] = GC; pl[-30:] = GF
    a = WG.ceiling_openness_relative(dummy, pl).scalar
    b = WG.ceiling_openness_relative(dummy, pl).scalar
    assert a == b, (a, b)
    g = np.full((64, 64), OBST, np.int8); g[10:52, 10:13] = FREE; g[49:52, 10:52] = FREE
    assert WG.blind_corner_index(_PG(g)).scalar == WG.blind_corner_index(_PG(g)).scalar
    print("  determinism: W2.2 + W2.4 replay identical  OK")


if __name__ == "__main__":
    for fn in [test_all_registered_amber, test_abstain_contract,
               test_permeability_axes_not_averaged, test_determinism]:
        print(fn.__name__); fn()
    print("\nWAVE-2 GEOMETRY (CC-4) SOCKET TESTS PASSED")
