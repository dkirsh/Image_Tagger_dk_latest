"""
M1' sufficient-statistic replay tests (Sprint COMP-CORRECT S0, 2026-07-19).
Locks: (1) all five audit classes MATCH/tamper-catch/diff-image-catch, (2) the _canon rounding
boundary, (3) every M1P binding points at a real registry predicate, (4) the abstention path.
Run: python3 annotation_socket/tests/test_m1_prime.py
"""
import sys, json
sys.path.insert(0, "/home/claude")
import numpy as np
from annotation_socket import m1_prime as M


def _synth():
    yy, xx = np.mgrid[0:128, 0:160]
    base = 40 + 120 * (xx / 160.0)
    base[20:50, 100:140] = 250.0
    base = base + 15 * np.sin(xx / 3.0) * np.cos(yy / 4.0)
    return np.clip(np.stack([base, base * 0.9, base * 0.8], -1), 0, 255).astype(np.uint8)


def test_all_audit_classes_roundtrip_and_tamper():
    img = _synth()
    tamper_key = {"luminance_field": "global_std", "radial_fft": "slope",
                  "orientation_hist": "n_edge_px", "box_count": "edge_px",
                  "color_palette": "entropy_norm", "edge_stats": "mean_mag_on_edges",
                  "jpeg_tiles": "global_bpp", "geometry_plan": "free_cells"}
    for ac in M.AUDIT_CLASSES:
        if ac == "geometry_plan":
            continue     # full-chain recompute; covered by the run_stage wiring path
        m = M.emit(ac, img)
        assert M.replay(m, img)[0] == M.MATCH, ac
        assert M.digest(M.AUDIT_CLASSES[ac](img)) == m["digest"], ac      # determinism
        t = json.loads(json.dumps(m))
        t["stats"][tamper_key[ac]] = float(t["stats"][tamper_key[ac]]) + 5.0
        t["digest"] = M.digest(t["stats"])                                # re-forged digest
        assert M.replay(t, img)[0] == M.STATS_MISMATCH, ac
        assert M.replay(m, np.roll(img, 7, axis=1))[0] == M.STATS_MISMATCH, ac
    print("  5 audit classes: roundtrip + tamper + diff-image  OK")


def test_canon_boundary():
    assert M.digest({"v": 0.1234567}) == M.digest({"v": 0.123457})
    assert M.digest({"v": 0.12345}) != M.digest({"v": 0.12346})
    print("  _canon 6-decimal boundary locked  OK")


def test_bindings_point_at_registry():
    from annotation_socket import registry as R
    ids = {p["id"] for p in R.PREDICATES}
    for pid, (ac, _) in M.M1P_BINDINGS.items():
        assert pid in ids, f"binding for unregistered predicate {pid}"
        assert ac in M.AUDIT_CLASSES, f"binding to unknown audit class {ac}"
    print(f"  {len(M.M1P_BINDINGS)} bindings all point at registered predicates  OK")


def test_abstention_path():
    blank = np.full((64, 64, 3), 128, np.uint8)
    b = M.emit("orientation_hist", blank)
    assert b["stats"].get("abstained") is True
    assert M.replay(b, blank)[0] == M.MATCH
    print("  blank -> abstained stats, still replayable  OK")


def test_scalar_vs_stats_verdicts():
    img = _synth()
    m = M.emit("luminance_field", img)
    assert M.replay(m, img, scalar=1.0, recomputed_scalar=9.0)[0] == M.SCALAR_MISMATCH
    assert M.replay(None, img)[0] == M.MISSING_M1P
    print("  scalar_mismatch + missing block verdicts  OK")


if __name__ == "__main__":
    for fn in [test_all_audit_classes_roundtrip_and_tamper, test_canon_boundary,
               test_bindings_point_at_registry, test_abstention_path, test_scalar_vs_stats_verdicts]:
        print(fn.__name__); fn()
    print("\nM1' TESTS PASSED")
