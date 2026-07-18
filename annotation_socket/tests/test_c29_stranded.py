"""
Unit test for C29 stranded_amenity_index — pure interaction core + the two negative controls
(on-ridge amenity and blank off-ridge wall must both read ~0) + M1 determinism.
Run: python3 annotation_socket/tests/test_c29_stranded.py
"""
import sys
sys.path.insert(0, "/home/claude")
from annotation_socket.predicates import stranded_amenity as C29
from annotation_socket.predicates import triangulation as T


def test_flag_fires_only_on_the_conjunction():
    """appeal AND off-path AND usable -> high; drop any one -> ~0 (not a disguised sum)."""
    appeal, seat = 0.9, 0.9
    # stranded: gorgeous usable lounge 8 m off the ridge
    omg_off = 1 - T.gate(8.0)                       # ~1
    v_stranded = C29.stranded(appeal, omg_off, seat)
    # NOT stranded: same lounge ON the ridge
    omg_on = 1 - T.gate(0.2)                        # ~0
    v_onpath = C29.stranded(appeal, omg_on, seat)
    # NOT stranded: off-ridge but blank wall art (seat ~0)
    v_wall = C29.stranded(appeal, omg_off, 0.05)
    # NOT stranded: off-ridge, usable, but no appeal
    v_dull = C29.stranded(0.05, omg_off, seat)
    assert v_stranded > 0.7, v_stranded
    assert v_onpath < 0.05, v_onpath               # on the path -> not wasted
    assert v_wall < 0.1, v_wall                    # wall art -> not a dwell amenity
    assert v_dull < 0.1, v_dull                    # nothing to strand
    print("  conjunction: stranded=%.3f  on-path=%.3f  wall-art=%.3f  dull=%.3f  OK"
          % (v_stranded, v_onpath, v_wall, v_dull))


def test_tri_state():
    # geometry unconfident -> UNKNOWN
    s, v, d = C29.decide(dE=30, appeal01=0.8, seat01=0.8, anchor_cell=(5, 5), reg_conf=0.9,
                         dist_m=8.0, geom_conf=0.10)
    assert s == "UNKNOWN" and d["reason"] == "geometry_unconfident"
    # no salient amenity -> genuine ZERO
    s, v, d = C29.decide(dE=3, appeal01=0.1, seat01=0.0, anchor_cell=None, reg_conf=0.0,
                         dist_m=None, geom_conf=0.5)
    assert s == "ZERO" and v == 0.0 and d["reason"] == "no_salient_amenity"
    # registration unconfident -> UNKNOWN (don't guess)
    s, v, d = C29.decide(dE=30, appeal01=0.8, seat01=0.8, anchor_cell=None, reg_conf=0.1,
                         dist_m=None, geom_conf=0.5)
    assert s == "UNKNOWN" and d["reason"] == "anchor_registration_unconfident"
    # salient usable amenity far off the ridge -> SCORED high (a real warning)
    s, v, d = C29.decide(dE=30, appeal01=0.85, seat01=0.9, anchor_cell=(5, 5), reg_conf=0.8,
                         dist_m=8.0, geom_conf=0.5)
    assert s == "SCORED" and v > 0.7, (s, v)
    print("  tri-state: UNKNOWN(geom) / ZERO(no-amenity) / UNKNOWN(reg) / SCORED=%.3f  OK" % v)


def test_m1_determinism_and_negative_controls():
    """M1: recompute reproduces within TOL; a fabricated high value that the recompute does not
    reproduce (amenity actually ON the ridge, or blank wall) is REJECTED."""
    args = dict(dE=30, appeal01=0.85, seat01=0.9, anchor_cell=(5, 5), reg_conf=0.8,
                dist_m=8.0, geom_conf=0.5)
    _, v1, _ = C29.decide(**args)
    _, v2, _ = C29.decide(**args)
    assert abs(v1 - v2) <= C29.TOL
    # negative control A: claimed 0.9 but amenity is ON the ridge -> true ~0
    _, v_on, _ = C29.decide(dE=30, appeal01=0.85, seat01=0.9, anchor_cell=(5, 5), reg_conf=0.8,
                            dist_m=0.2, geom_conf=0.5)
    # negative control B: claimed 0.9 but it is blank wall art -> true ~0
    _, v_wall, _ = C29.decide(dE=30, appeal01=0.85, seat01=0.04, anchor_cell=(5, 5), reg_conf=0.8,
                              dist_m=8.0, geom_conf=0.5)
    assert abs(0.9 - v_on) > C29.TOL and v_on < 0.05
    assert abs(0.9 - v_wall) > C29.TOL and v_wall < 0.1
    print("  M1: deterministic; fabricated 0.90 vs on-ridge %.4f / wall-art %.4f -> REJECT  OK"
          % (v_on, v_wall))


if __name__ == "__main__":
    for fn in [test_flag_fires_only_on_the_conjunction, test_tri_state,
               test_m1_determinism_and_negative_controls]:
        print(fn.__name__)
        fn()
    print("\nALL C29 CORE TESTS PASSED")
