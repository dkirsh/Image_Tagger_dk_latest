"""
Adapter smoke test — validates that all new adapters import and that
availability checks run without error (even when no checkpoints are present).
Requires only numpy + opencv-python (already project deps).
"""
import sys
import os
import traceback

RESULTS = []


def _check(name, fn):
    try:
        fn()
        RESULTS.append((name, "PASS", ""))
    except Exception as e:
        RESULTS.append((name, "FAIL", str(e)))
        traceback.print_exc()


def test_depth_pro_availability():
    from cnfa_algs.adapters.depth_pro_adapter import is_available
    avail = is_available()
    assert isinstance(avail, bool)
    print(f"  Depth Pro available: {avail}")


def test_hawp_availability():
    from cnfa_algs.adapters.hawp_adapter import is_available
    avail = is_available()
    assert isinstance(avail, bool)
    print(f"  HAWP available: {avail}")


def test_ulayout_availability():
    from cnfa_algs.adapters.ulayout_adapter import is_available
    avail = is_available()
    assert isinstance(avail, bool)
    print(f"  uLayout available: {avail}")


def test_esanet_availability():
    from cnfa_algs.adapters.esanet_adapter import is_available
    avail = is_available()
    assert isinstance(avail, bool)
    print(f"  ESANet available: {avail}")


def test_marigold_availability():
    from cnfa_algs.adapters.marigold_adapter import is_available
    avail = is_available()
    assert isinstance(avail, bool)
    print(f"  Marigold available: {avail}")


def test_saliency_adapter_import():
    from cnfa_algs.adapters.saliency_adapter import is_available, deep_saliency
    avail = is_available()
    assert isinstance(avail, bool)
    print(f"  TranSalNet available: {avail}")


def test_composition_rot_synthetic():
    """Rule of thirds on a synthetic image — always works (pure code)."""
    import numpy as np
    from cnfa_algs.composition import rule_of_thirds
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[150:170, 200:220] = [255, 200, 100]  # bright patch near RoT point
    result = rule_of_thirds(img)
    assert result.key == "cnfa.composition.rule_of_thirds"
    assert 0 <= result.scalar <= 1
    assert result.field is not None
    print(f"  RoT score: {result.scalar:.3f}")


def test_composition_balance_synthetic():
    """Visual balance on a synthetic image."""
    import numpy as np
    from cnfa_algs.composition import visual_balance
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128
    result = visual_balance(img)
    assert result.key == "cnfa.composition.visual_balance"
    assert 0 <= result.scalar <= 1
    print(f"  Balance score: {result.scalar:.3f}")


def test_saliency_fallback_on_synthetic():
    """Deep saliency with fallback to spectral-residual on synthetic image."""
    import numpy as np
    from cnfa_algs.adapters.saliency_adapter import deep_saliency
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    img[100:140, 130:190] = [0, 255, 0]
    sal = deep_saliency(img)
    assert sal.shape == (240, 320)
    assert sal.min() >= 0 and sal.max() <= 1.01
    print(f"  Saliency shape OK, range [{sal.min():.2f}, {sal.max():.2f}]")


def test_depth_provider_init():
    """DepthProvider should init without error regardless of env."""
    from cnfa_algs.geometry import DepthProvider
    dp = DepthProvider()
    assert dp.method in (
        "geometric_vp_groundplane(M2-geo)",
        "monocular_onnx(M2)",
        "depth_pro_metric(M2-metric)",
    )
    print(f"  DepthProvider method: {dp.method}")


def test_landmark_salience_with_fallback():
    """landmark_salience should work with deep or FFT saliency."""
    import numpy as np
    from cnfa_algs.attributes import landmark_salience
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    img[80:160, 100:220] = [200, 180, 50]
    result = landmark_salience(img)
    assert result.key == "cnfa.cognitive.landmark_salience"
    assert 0 <= result.scalar <= 1
    print(f"  Landmark salience: {result.scalar:.3f}, method: {result.method[:40]}...")


def main():
    tests = [
        ("Depth Pro is_available", test_depth_pro_availability),
        ("HAWP is_available", test_hawp_availability),
        ("uLayout is_available", test_ulayout_availability),
        ("ESANet is_available", test_esanet_availability),
        ("Marigold is_available", test_marigold_availability),
        ("Saliency adapter import", test_saliency_adapter_import),
        ("Composition: rule_of_thirds", test_composition_rot_synthetic),
        ("Composition: visual_balance", test_composition_balance_synthetic),
        ("Saliency fallback (synthetic)", test_saliency_fallback_on_synthetic),
        ("DepthProvider init", test_depth_provider_init),
        ("landmark_salience + fallback", test_landmark_salience_with_fallback),
    ]

    print("=" * 60)
    print("ADAPTER INTEGRATION SMOKE TEST")
    print("=" * 60)
    for name, fn in tests:
        print(f"\n[TEST] {name}")
        _check(name, fn)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for name, status, err in RESULTS:
        mark = "✅" if status == "PASS" else "❌"
        line = f"  {mark} {name}"
        if err:
            line += f" — {err[:80]}"
        print(line)

    n_pass = sum(1 for _, s, _ in RESULTS if s == "PASS")
    n_fail = sum(1 for _, s, _ in RESULTS if s == "FAIL")
    print(f"\n{n_pass} passed, {n_fail} failed out of {len(RESULTS)}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    # Ensure project root is on path
    proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if proj not in sys.path:
        sys.path.insert(0, proj)
    sys.exit(main())
