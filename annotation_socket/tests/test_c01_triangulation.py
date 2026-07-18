"""
Unit test for C01 triangulation_ignition — exercises the PURE interaction core (the compound
claim) without the CV pipeline, per CLAUDE.md verification discipline (test the core in-process
when the full pipeline cannot run in-sandbox). Also asserts the M1-replay determinism contract
and a fabrication negative control at the decision layer.

Run: python3 annotation_socket/tests/test_c01_triangulation.py
"""
import sys, math
sys.path.insert(0, "/home/claude")
from annotation_socket.predicates import triangulation as T


def approx(a, b, tol=1e-9): return abs(a - b) <= tol


def test_gate_is_a_real_threshold():
    # ON the desire line -> ~1; one D0 off -> 1/e; far off -> ~0
    assert approx(T.gate(0.0), 1.0)
    assert approx(T.gate(T.D0_M), math.exp(-1.0))
    assert T.gate(4 * T.D0_M) < 0.001
    print("  gate: on-line=1.000, 1*D0=%.3f, far=%.4f  OK" % (T.gate(T.D0_M), T.gate(4*T.D0_M)))


def test_compound_beats_average_on_dead_alcove():
    """The whole point: a beautiful anchor OFF the desire line must score ~0, where a mere
    average of salience and integration would score it high."""
    sal = 0.95                      # gorgeous fountain
    integ_at_alcove = 0.20          # alcove is peripheral
    integ_if_on_path = 0.80
    # Region B: dead alcove, 8 m off the ridge
    g_B = T.gate(8.0)
    ignition_B = T.ignition(sal, integ_at_alcove, g_B)
    avg_B = (sal + integ_at_alcove) / 2      # what a NON-compound would report
    # Region A: same fountain on the cross-path, on the ridge
    g_A = T.gate(0.3)
    ignition_A = T.ignition(sal, integ_if_on_path, g_A)
    assert ignition_B < 0.02, ignition_B          # compound correctly kills the dead alcove
    assert avg_B > 0.55                            # an average would have PASSED it
    assert ignition_A > 0.6, ignition_A            # on-path fountain ignites
    assert ignition_A > 30 * max(ignition_B, 1e-6)
    print("  A-vs-B: on-path ignition=%.3f  dead-alcove=%.4f  (average would be %.2f)  OK"
          % (ignition_A, ignition_B, avg_B))


def test_ridge_percentile():
    cells = [(0, i) for i in range(10)]
    integ = [i / 9 for i in range(10)]            # 0.0 .. 1.0
    ridge = T.ridge_cells(cells, integ, pctl=85.0)
    assert all(v >= 0.85 - 1e-9 for (_, i), v in zip(ridge, [integ[c[1]] for c in ridge]))
    assert len(ridge) == 2                          # cells 9 and 8 (0.888,1.0) >= p85(=0.85*? )
    print("  ridge p85 selected %d/10 highest-integration cells  OK" % len(ridge))


def test_tri_state():
    # geometry unconfident -> UNKNOWN (fail closed)
    s, v, d = T.decide(dE=30, sal01=0.75, anchor_cell=(5, 5), reg_conf=0.9, integ_anchor01=0.8,
                       dist_m=0.5, geom_conf=0.10)
    assert s == "UNKNOWN" and v is None and d["reason"] == "geometry_unconfident"
    # no salient anchor -> genuine ZERO (a finding, not an abstention)
    s, v, d = T.decide(dE=3, sal01=0.1, anchor_cell=None, reg_conf=0.0, integ_anchor01=None,
                       dist_m=None, geom_conf=0.5)
    assert s == "ZERO" and v == 0.0 and d["reason"] == "no_salient_anchor"
    # anchor present but registration unconfident -> UNKNOWN (skeptic's fix: don't guess)
    s, v, d = T.decide(dE=30, sal01=0.75, anchor_cell=None, reg_conf=0.1, integ_anchor01=None,
                       dist_m=None, geom_conf=0.5)
    assert s == "UNKNOWN" and d["reason"] == "anchor_registration_unconfident"
    # good anchor on the ridge -> SCORED, high
    s, v, d = T.decide(dE=38, sal01=0.95, anchor_cell=(5, 5), reg_conf=0.8, integ_anchor01=0.85,
                       dist_m=0.4, geom_conf=0.5)
    assert s == "SCORED" and v > 0.6, (s, v)
    print("  tri-state: UNKNOWN(geom) / ZERO(no-anchor) / UNKNOWN(reg) / SCORED=%.3f  OK" % v)


def test_m1_replay_determinism_and_negative_control():
    """M1: recomputing the value from the SAME inputs reproduces it within TOL. A fabricated
    stored value (0.9) that the recompute does not reproduce is REJECTED (RED)."""
    args = dict(dE=38, sal01=0.95, anchor_cell=(5, 5), reg_conf=0.8, integ_anchor01=0.85,
                dist_m=0.4, geom_conf=0.5)
    _, v1, _ = T.decide(**args)
    _, v2, _ = T.decide(**args)                      # replay
    assert abs(v1 - v2) <= T.TOL                     # deterministic
    fabricated_stored = 0.90                          # a claimed high value on an off-path anchor
    _, v_true, _ = T.decide(dE=38, sal01=0.95, anchor_cell=(5, 5), reg_conf=0.8, integ_anchor01=0.85,
                            dist_m=9.0, geom_conf=0.5)   # actually 9 m off the ridge -> gate~0
    replay_mismatch = abs(fabricated_stored - v_true) > T.TOL
    assert replay_mismatch and v_true < 0.02          # M1 would RED this
    print("  M1 replay: deterministic (|Δ|<=%.0e); fabricated 0.90 vs true %.4f -> REJECT  OK"
          % (T.TOL, v_true))


if __name__ == "__main__":
    for fn in [test_gate_is_a_real_threshold, test_compound_beats_average_on_dead_alcove,
               test_ridge_percentile, test_tri_state, test_m1_replay_determinism_and_negative_control]:
        print(fn.__name__)
        fn()
    print("\nALL C01 CORE TESTS PASSED")
