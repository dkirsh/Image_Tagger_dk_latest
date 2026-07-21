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
                  "jpeg_tiles": "global_bpp", "geometry_plan": "free_cells",
                  "ssim_map": "diff_mean"}
    for ac in M.AUDIT_CLASSES:
        if ac == "geometry_plan":
            continue     # full-chain recompute; covered by the run_stage wiring path
        if ac == "operator_extract":
            continue     # parameterized (needs op=); covered by test_cc2_operator_extract
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


# S1 / A5 (2026-07-21): the 13 image-only pixel operators bound this batch. Explicitly listed so a
# dropped binding is a test failure, not a silently-shrunk count.
_S1_M1P_BATCH = [
    "glare-risk", "cnfa.cognitive.landmark_salience", "cnfa.fluency.proto_object_count",
    "cnfa.fluency.multiscale_gradient", "cnfa.fluency.multiscale_unique_color",
    "cnfa.light.luminance_gradient_contrast", "cnfa.light.sun_patch_geometry",
    "cnfa.light.evening_ambience", "cnfa.light.temperature_mismatch",
    "cnfa.light.spotlight_pool_geometry", "cnfa.light.dark_zone_map",
    "cnfa.geometry.orderliness_alignment", "cnfa.geometry.verticality_cues",
]
# Operators whose sufficient statistics are GLOBALLY TRANSLATION-INVARIANT by construction (whole-frame
# light summaries): a circular roll produces statistically the same image, so diff-image legitimately
# MATCHes. Their scalar is invariant to the roll too, so this is within M1' scope (tamper/stale/
# wrong-pipeline), not a signature weakness. Documented here so the diff-image guard stays strict for
# every spatially-discriminating op.
_M1P_ROLL_INVARIANT = {
    "cnfa.light.sun_patch_geometry", "cnfa.light.evening_ambience",
    "cnfa.light.spotlight_pool_geometry", "cnfa.light.dark_zone_map",
}


def test_operator_extract_bindings():
    """All operator_extract + ssim_map bindings (CC-2 + the S1/A5 batch) must satisfy the three hard
    guarantees on the synth fixture: DETERMINISM (emit twice -> identical digest; the anti-false-RED
    property), genuine -> MATCH, and forged-digest tamper -> STATS_MISMATCH. Diff-image discrimination
    is additionally required for every op NOT in the documented roll-invariant allowlist. Abstaining
    ops exercise the abstained-digest path (a claim of abstention is auditable like any other)."""
    img = _synth()
    rolled = np.roll(img, 9, axis=1)
    new = [pid for pid, (ac, _) in M.M1P_BINDINGS.items()
           if ac in ("ssim_map", "operator_extract")]
    missing = [pid for pid in _S1_M1P_BATCH if pid not in new]
    assert not missing, f"S1/A5 M1' bindings dropped: {missing}"
    assert len(new) >= 20, f"expected >=20 operator_extract/ssim bindings, found {len(new)}"
    n_abst = 0
    for pid in new:
        ac, params = M.M1P_BINDINGS[pid]
        m = M.emit(ac, img, **params)
        assert M.emit(ac, img, **params)["digest"] == m["digest"], f"{pid}: non-deterministic digest"
        assert M.replay(m, img, **params)[0] == M.MATCH, pid
        t = json.loads(json.dumps(m))
        t["digest"] = "sha256:" + "0" * 64
        assert M.replay(t, img, **params)[0] == M.STATS_MISMATCH, f"{pid}: tamper not caught"
        if m["stats"].get("abstained"):
            n_abst += 1
        elif pid not in _M1P_ROLL_INVARIANT:
            assert M.replay(m, rolled, **params)[0] == M.STATS_MISMATCH, \
                f"{pid}: diff image not caught (and not on the roll-invariant allowlist)"
    print(f"  operator_extract: {len(new)} bindings determ+roundtrip+tamper "
          f"({n_abst} abstained on synth, {len(_M1P_ROLL_INVARIANT)} roll-invariant allowlisted)  OK")


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
               test_bindings_point_at_registry, test_abstention_path,
               test_scalar_vs_stats_verdicts, test_operator_extract_bindings]:
        print(fn.__name__); fn()
    print("\nM1' TESTS PASSED")
