"""
F7 ridge-degeneracy boundary + outlier tests (Codex 2026-07-18 asked for the threshold to be
locked by tests, not just asserted). Run: python3 annotation_socket/tests/test_f7_ridge_boundary.py
"""
import sys
sys.path.insert(0, "/home/claude")
from annotation_socket.predicates import triangulation as T


def test_outlier_cannot_defeat_the_guard():
    # a genuinely flat field + one clipped 1e6 outlier must still read degenerate (the Codex-2 bug)
    assert T.ridge_is_degenerate([500.0] * 99 + [1e6]) is True
    assert T.ridge_is_degenerate([500.0] * 50 + [500.0] * 49 + [1e6]) is True
    print("  flat + 1e6 outlier -> degenerate  OK")


def test_structured_field_not_degenerate():
    assert T.ridge_is_degenerate([float(i * i + 250) for i in range(1, 101)]) is False
    print("  structured i^2 field -> not degenerate  OK")


def test_threshold_boundary_is_documented():
    # a two-valued field: below the RELIQR threshold -> degenerate; above -> passes. This LOCKS the
    # known sharp boundary Codex flagged, so a future change to RIDGE_MIN_RELIQR is caught by a test.
    lo = [1.0] * 90 + [1.02] * 10          # tiny spread -> IQR/median ~0 -> degenerate
    hi = [1.0] * 50 + [2.0] * 50           # clear bimodal -> IQR/median large -> passes
    assert T.ridge_is_degenerate(lo) is True
    assert T.ridge_is_degenerate(hi) is False
    print(f"  boundary locked: near-flat -> degenerate; bimodal -> passes "
          f"(RIDGE_MIN_RELIQR={T.RIDGE_MIN_RELIQR})  OK")


if __name__ == "__main__":
    for fn in [test_outlier_cannot_defeat_the_guard, test_structured_field_not_degenerate,
               test_threshold_boundary_is_documented]:
        print(fn.__name__); fn()
    print("\nF7 RIDGE BOUNDARY TESTS PASSED")
