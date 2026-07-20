"""
Regression locks for the Codex TAX attack dispositions (2026-07-19/20).
CP-2 water gate discrimination, CS-3 alpha policy, CP-1 full constant surfacing,
FC-6 threshold surfacing. Run: python3 annotation_socket/tests/test_codex_tax_fixes.py
"""
import sys
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/Users/davidusa/REPOS/Image_Tagger_dk_latest")
import numpy as np, cv2
from cnfa_algs.complexity_partition import complexity_partition
from cnfa_algs.clutter_stack import multiscale_unique_color


def test_cp2_water_discriminates():
    wall = np.full((240, 320, 3), (190, 150, 90), np.uint8)          # Codex fixture
    cv2.ellipse(wall, (160, 120), (60, 35), 0, 0, 360, (250, 245, 235), -1)
    assert complexity_partition(wall).extras["area_fracs"]["water"] < 0.10
    pool = np.full((240, 320, 3), (60, 60, 60), np.uint8)
    pool[120:240, :] = (180, 140, 60)
    rng = np.random.default_rng(7)
    ys, xs = rng.integers(130, 235, 500), rng.integers(5, 315, 500)
    pool[ys, xs] = (255, 250, 240)
    assert complexity_partition(pool).extras["area_fracs"]["water"] > 0.25
    print("  CP-2: blue wall NOT water; glinted lower-frame pool IS water  OK")


def test_cp1_constants_fully_surfaced():
    img = np.full((240, 320, 3), (90, 120, 160), np.uint8)
    img[::8, :] = 30
    c = complexity_partition(img).extras["constants"]
    for k in ["mat_texture_min", "mat_hue_std_max", "fire_lum_min", "fire_std_min",
              "periodic_peak_min", "ornament_peak_min", "coherence_min",
              "art_frame_edge_min", "merge_connectivity", "water_row_min_frac",
              "water_spec_frac"]:
        assert k in c, f"constant not surfaced: {k}"
    assert c["merge_connectivity"] == 4
    print(f"  CP-1/CP-8: {len(c)} constants surfaced incl. merge_connectivity  OK")


def test_cs3_alpha_policy():
    img = np.full((240, 320, 3), (190, 150, 90), np.uint8)
    cv2.ellipse(img, (160, 120), (60, 35), 0, 0, 360, (250, 245, 235), -1)
    rgba = np.dstack([img, np.full((240, 320), 255, np.uint8)])
    a3 = complexity_partition(img).extras["area_fracs"]
    a4 = complexity_partition(rgba).extras["area_fracs"]
    assert a3 == a4
    m3, m4 = multiscale_unique_color(img), multiscale_unique_color(rgba)
    assert m3.scalar == m4.scalar
    print("  CS-3: RGBA == BGR through partition and MUC (alpha dropped, declared)  OK")


def test_tax0_direct_invocation():
    import subprocess
    r = subprocess.run([sys.executable, "cnfa_algs/wave2_geometry.py"],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-300:]
    print("  TAX-0: direct `python3 cnfa_algs/<file>.py` runs  OK")


if __name__ == "__main__":
    for fn in [test_cp2_water_discriminates, test_cp1_constants_fully_surfaced,
               test_cs3_alpha_policy, test_tax0_direct_invocation]:
        print(fn.__name__); fn()
    print("\nCODEX TAX-FIX REGRESSION LOCKS PASSED")
