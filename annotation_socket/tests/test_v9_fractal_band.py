"""
Unit test for V9 fractal_mid_d_band_score — pure response core + coverage + M1 determinism +
a dependency-fabrication negative control. Run: python3 annotation_socket/tests/test_v9_fractal_band.py
"""
import sys
sys.path.insert(0, "/home/claude")
from annotation_socket.predicates import fractal_band as V9


def approx(a, b, t=1e-9): return abs(a - b) <= t


def test_band_response_is_an_inverted_U():
    assert approx(V9.band_response(1.40), 1.0)          # in band -> 1
    assert approx(V9.band_response(1.30), 1.0)          # edge inclusive
    assert V9.band_response(0.85) < 0.2                 # sterile/blank -> low
    assert V9.band_response(1.95) < 0.2                 # chaotic overload -> low
    assert V9.band_response(1.40) > V9.band_response(1.10) > V9.band_response(0.80)  # monotone toward peak
    print("  response: peak@1.4=%.2f  blank@0.85=%.2f  chaos@1.95=%.2f  OK"
          % (V9.band_response(1.40), V9.band_response(0.85), V9.band_response(1.95)))


def test_coverage_ignores_empty_tiles():
    import numpy as np
    fld = np.array([[1.40, 1.45, 0.0], [1.90, 0.0, 1.35]])   # 3 in-band, 1 out, 2 empty
    cov = V9.band_coverage(fld)
    assert approx(cov, 3 / 4), cov                             # 3 of 4 non-empty tiles in band
    assert V9.band_coverage(np.zeros((3, 3))) == 0.0           # all empty -> 0, not fabricated
    print("  coverage: in-band=%.2f (empty tiles ignored)  OK" % cov)


def test_m1_determinism_and_dependency_control():
    import numpy as np
    fld = np.array([[1.40, 1.42], [1.35, 1.48]])
    b1, c1 = V9.score(1.41, fld)
    b2, c2 = V9.score(1.41, fld)
    assert approx(b1, b2) and approx(c1, c2)                   # deterministic (M1)
    # a "chaotic" scene claimed as high band score is impossible: score follows D
    b_chaos, _ = V9.score(2.0, fld)
    assert b_chaos < 0.2                                       # cannot fabricate a mid-D score
    print("  M1: deterministic; chaotic D=2.0 -> band=%.3f (cannot be laundered high)  OK" % b_chaos)


if __name__ == "__main__":
    for fn in [test_band_response_is_an_inverted_U, test_coverage_ignores_empty_tiles,
               test_m1_determinism_and_dependency_control]:
        print(fn.__name__)
        fn()
    print("\nALL V9 CORE TESTS PASSED")
