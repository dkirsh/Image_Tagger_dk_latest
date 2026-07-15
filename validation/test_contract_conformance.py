"""
Level 1 contract-conformance tests for cnfa_algs.

Tests every attribute function and the composition module against the
output contract defined in cnfa_algs/CONTRACT.md §3 and the last-mile
gates LM-1, LM-2, LM-3.

Runs on ANY machine — uses a synthetic image, no model weights needed.

Usage:
    python3 validation/test_contract_conformance.py
"""
import sys
import os
import traceback
import numpy as np

# Ensure project root on path
proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj not in sys.path:
    sys.path.insert(0, proj)

from cnfa_algs.core import AttributeResult

# ─── The canonical registry of valid keys ────────────────────────────────
# This is the contract's LM-2: every key produced must be in this set.
# Add keys here as new attributes are implemented.
REGISTERED_KEYS = {
    # Stage 1a: pixel-only (M1)
    "cnfa.light.brightness_variance",
    "cnfa.fluency.edge_clarity_mean",
    "cnfa.perceptual.symmetry_horizontal",
    "cnfa.fluency.color_palette_entropy",
    "cnfa.fluency.processing_load_proxy",
    "cnfa.fractal_dimension",
    "glare-risk",  # TODO: rename to cnfa.light.glare_risk — CONTRACT VIOLATION
    "cnfa.light.warm_vs_cool_ratio",  # TODO: rename to cnfa.light.warmth_ratio
    "cnfa.cognitive.landmark_salience",
    # Composition (M1)
    "cnfa.composition.rule_of_thirds",
    "cnfa.composition.visual_balance",
    # Stage 1b: depth/plane-dependent (M2)
    "cnfa.light.vertical_illuminance_proxy",
    "cnfa.spatial.enclosure_index",
    "cnfa.spatial.prospect",
    # Stage 1b: material-dependent
    "acoustic_absorption_proxy",  # TODO: rename to cnfa.acoustics.absorption_proxy — CONTRACT VIOLATION
    # Sociopetal (needs seats list — tested separately)
    "cnfa.social.sociopetal_seating",
}

# ─── Test fixtures ───────────────────────────────────────────────────────

def make_synthetic_image():
    """A 480×640 BGR image with some structure (not all-black, not all-white)."""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Bright patch (furniture-like)
    img[100:200, 150:300] = [180, 160, 120]
    # Window-like bright region
    img[50:150, 400:550] = [240, 240, 255]
    # Dark floor area
    img[350:480, :] = [60, 55, 50]
    # Wall-like grey
    img[0:350, 0:150] = [150, 145, 140]
    return img


def make_planes(shape):
    """Fake plane label map."""
    H, W = shape
    planes = np.zeros((H, W), np.int32)
    planes[350:, :] = 1     # floor
    planes[:80, :] = 2      # ceiling
    planes[:350, :150] = 3  # wall
    planes[50:150, 400:550] = 4  # opening
    return planes


def make_depth(shape):
    """Fake depth map (linear gradient, like a simple room)."""
    H, W = shape
    Z = np.linspace(5.0, 1.0, H).reshape(-1, 1).repeat(W, axis=1).astype(np.float32)
    return Z


# ─── Contract checks ────────────────────────────────────────────────────

def check_contract(result, img_shape, fn_name):
    """Verify a single AttributeResult against CONTRACT §3 + LM-1..LM-3."""
    errors = []

    # Type check
    if not isinstance(result, AttributeResult):
        return [f"{fn_name}: returned {type(result).__name__}, not AttributeResult"]

    # LM-1: valid scalar
    if result.scalar is not None:
        if not np.isfinite(result.scalar):
            errors.append(f"{fn_name}: scalar is not finite ({result.scalar})")
        if result.scalar < 0.0 or result.scalar > 1.0:
            errors.append(f"{fn_name}: scalar {result.scalar:.4f} outside [0,1]")
    # scalar=None is allowed (some attributes may legitimately not have a global scalar)

    # LM-2: key registered
    if result.key not in REGISTERED_KEYS:
        errors.append(f"{fn_name}: key '{result.key}' NOT in REGISTERED_KEYS")

    # Key format
    if not result.key.startswith("cnfa."):
        errors.append(f"{fn_name}: key '{result.key}' does not start with 'cnfa.'")

    # LM-3: field shape match
    if result.field is not None:
        expected_shape = img_shape[:2]
        if result.field.shape != expected_shape:
            errors.append(
                f"{fn_name}: field shape {result.field.shape} != image shape {expected_shape}"
            )
        if result.field.min() < -0.01 or result.field.max() > 1.01:
            errors.append(
                f"{fn_name}: field range [{result.field.min():.3f}, {result.field.max():.3f}] outside [0,1]"
            )

    # Confidence
    if not (0.0 <= result.confidence <= 1.0):
        errors.append(f"{fn_name}: confidence {result.confidence} outside [0,1]")
    if result.confidence == 0.0:
        errors.append(f"{fn_name}: confidence is 0.0 — result will be ignored downstream")

    # Method
    if not result.method:
        errors.append(f"{fn_name}: method is empty string")

    # Failure modes type check
    if not isinstance(result.failure_modes, list):
        errors.append(f"{fn_name}: failure_modes is {type(result.failure_modes)}, not list")

    return errors


# ─── Test runner ─────────────────────────────────────────────────────────

def main():
    from cnfa_algs import attributes
    from cnfa_algs.composition import rule_of_thirds, visual_balance

    img = make_synthetic_image()
    planes = make_planes(img.shape[:2])
    depth = make_depth(img.shape[:2])

    # Functions that take only img
    pixel_fns = [
        ("brightness_variance", lambda: attributes.brightness_variance(img)),
        ("edge_clarity",        lambda: attributes.edge_clarity(img)),
        ("symmetry_horizontal", lambda: attributes.symmetry_horizontal(img)),
        ("palette_entropy",     lambda: attributes.palette_entropy(img)),
        ("processing_load",     lambda: attributes.processing_load(img)),
        ("fractal_dimension_local", lambda: attributes.fractal_dimension_local(img)),
        ("glare_risk",          lambda: attributes.glare_risk(img)),
        ("warmth_ratio",        lambda: attributes.warmth_ratio(img)),
        ("landmark_salience",   lambda: attributes.landmark_salience(img)),
        ("rule_of_thirds",      lambda: rule_of_thirds(img)),
        ("visual_balance",      lambda: visual_balance(img)),
    ]

    # Functions that need planes and/or depth
    structural_fns = [
        ("vertical_illuminance_proxy", lambda: attributes.vertical_illuminance_proxy(img, planes)),
        ("enclosure_index",            lambda: attributes.enclosure_index(img, planes, depth)),
        ("prospect",                   lambda: attributes.prospect(img, planes, depth)),
        ("acoustic_absorption",        lambda: attributes.acoustic_absorption(img, planes, depth)),
    ]

    all_errors = []
    results = []

    print("=" * 70)
    print("CONTRACT CONFORMANCE TEST (Level 1)")
    print("=" * 70)

    for name, fn in pixel_fns + structural_fns:
        print(f"\n[TEST] {name}")
        try:
            result = fn()
            errs = check_contract(result, img.shape, name)
            if errs:
                for e in errs:
                    print(f"  ❌ {e}")
                all_errors.extend(errs)
            else:
                print(f"  ✅ key={result.key}, scalar={result.scalar:.4f}, conf={result.confidence:.2f}")
            results.append((name, result, errs))
        except Exception as e:
            msg = f"{name}: RAISED {type(e).__name__}: {e}"
            print(f"  💥 {msg}")
            traceback.print_exc()
            all_errors.append(msg)

    # ── Summary ──
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    n_tested = len(pixel_fns) + len(structural_fns)
    n_pass = sum(1 for _, _, errs in results if not errs)
    n_error_fns = sum(1 for _, _, errs in results if errs)
    n_crash = n_tested - len(results)

    print(f"  Functions tested: {n_tested}")
    print(f"  Fully conformant: {n_pass}")
    print(f"  Contract violations: {n_error_fns} functions with {len(all_errors)} total violations")
    if n_crash > 0:
        print(f"  Exceptions (crashed): {n_crash}")

    # ── Key coverage ──
    produced_keys = {r.key for _, r, _ in results if r is not None}
    missing_keys = REGISTERED_KEYS - produced_keys - {"cnfa.social.sociopetal_seating"}  # needs seats
    if missing_keys:
        print(f"\n  ⚠️  Registered keys not tested: {sorted(missing_keys)}")

    print(f"\n{'PASS' if len(all_errors) == 0 else 'FAIL'}")
    return 0 if len(all_errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
