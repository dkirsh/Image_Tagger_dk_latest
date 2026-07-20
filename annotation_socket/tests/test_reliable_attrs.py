"""
Core tests for the reliability-sprint Tier-A primitives (synthetic inputs, deterministic).
Run: python3 annotation_socket/tests/test_reliable_attrs.py
"""
import sys
sys.path.insert(0, "/home/claude")
import numpy as np
import cv2
from cnfa_algs import reliable_attrs as R


def _oneoverf_noise(n=256, beta=2.0, seed=0):
    """Synthetic image with a known power-law spectrum P(f) ~ 1/f^beta (deterministic)."""
    rng = np.random.RandomState(seed)
    white = rng.randn(n, n)
    F = np.fft.fftshift(np.fft.fft2(white))
    cy, cx = n // 2, n // 2
    y, x = np.mgrid[0:n, 0:n]
    f = np.sqrt((y - cy) ** 2 + (x - cx) ** 2); f[cy, cx] = 1
    F = F / (f ** (beta / 2.0))
    img = np.real(np.fft.ifft2(np.fft.ifftshift(F)))
    img = (R.normalize01(img) * 255).astype(np.uint8)
    return img


# ---------- V2 ----------
def test_v2_slope_recovery():
    """The author's own check: on synthetic 1/f^2 noise the fitted power slope ≈ -2."""
    img = _oneoverf_noise(beta=2.0, seed=1)
    prof = R._radial_power_spectrum(R._gray01(img))
    slope, r2, band = R.spectral_slope_fit(prof)
    assert -2.6 < slope < -1.4, slope           # recovers ~ -2
    assert r2 > 0.9, r2
    print("  V2 slope-recovery: 1/f^2 -> fitted slope=%.2f (R2=%.2f)  OK" % (slope, r2))


def test_v2_discomfort_ordering_and_determinism():
    natural = _oneoverf_noise(beta=2.0, seed=2)          # natural statistics
    # striped/gridded pattern = excess mid-band energy = higher discomfort
    n = 256; xx = np.arange(n)
    stripes = (np.sin(xx[None, :] / 3.0) * 127 + 128).astype(np.uint8)
    stripes = np.repeat(stripes, n, axis=0)[:n]
    d_nat = R.spectral_discomfort_deviation(natural).scalar
    d_str = R.spectral_discomfort_deviation(stripes).scalar
    d_nat2 = R.spectral_discomfort_deviation(natural).scalar
    assert abs(d_nat - d_nat2) < 1e-9                    # deterministic (M1)
    assert d_str > d_nat, (d_str, d_nat)                 # stripes more uncomfortable than 1/f
    print("  V2 discomfort: stripes=%.3f > natural=%.3f ; deterministic  OK" % (d_str, d_nat))


# ---------- V13 ----------
def test_v13_entropy_ordering():
    n = 200
    grid = np.zeros((n, n), np.uint8)                    # cardinal grid -> low orientation entropy
    grid[::10, :] = 255; grid[:, ::10] = 255
    rng = np.random.RandomState(3)
    iso = (rng.rand(n, n) * 255).astype(np.uint8)        # isotropic noise -> high entropy
    e_grid = R.edge_orientation_entropy(grid).scalar
    e_iso = R.edge_orientation_entropy(iso).scalar
    e_grid2 = R.edge_orientation_entropy(grid).scalar
    assert abs(e_grid - e_grid2) < 1e-9                  # deterministic
    assert e_iso > e_grid, (e_iso, e_grid)               # isotropic > cardinal grid
    # FABLE F1: a near-edgeless blank image must ABSTAIN (scalar=None), not score max entropy
    blank=np.full((200,200),128,np.uint8)
    rb=R.edge_orientation_entropy(blank)
    assert rb.scalar is None and rb.extras.get("reason")=="insufficient_edges", rb.scalar
    print("  V13 F1-fix: blank image abstains (scalar=None), not 1.0  OK")
    print("  V13 entropy: isotropic=%.3f > cardinal-grid=%.3f ; deterministic  OK" % (e_iso, e_grid))



# ---------- V1 ----------
def test_v1_curves_vs_angles():
    n=240
    curvy=np.zeros((n,n),np.uint8)
    for rad in (40,70,100):
        cv2.circle(curvy,(n//2,n//2),rad,255,2)
    angular=np.zeros((n,n),np.uint8)
    for s in (30,60,90):
        cv2.rectangle(angular,(n//2-s,n//2-s),(n//2+s,n//2+s),255,2)
    a_curvy=R.contour_angularity_index(curvy)
    a_ang=R.contour_angularity_index(angular)
    a_curvy2=R.contour_angularity_index(curvy)
    assert abs(a_curvy.scalar-a_curvy2.scalar)<1e-9
    assert a_curvy.extras["curve_fraction"]>a_ang.extras["curve_fraction"], (a_curvy.extras,a_ang.extras)
    assert a_curvy.scalar>a_ang.scalar
    print("  V1 angularity: curves scalar=%.3f > angles scalar=%.3f (curve_frac %.2f vs %.2f) OK"
          %(a_curvy.scalar,a_ang.scalar,a_curvy.extras["curve_fraction"],a_ang.extras["curve_fraction"]))


# ---------- V6/V7 ----------
def test_v6_v7_clutter_ordering():
    n=200
    blank=np.full((n,n,3),128,np.uint8)
    rng=np.random.RandomState(7)
    cluttered=(rng.rand(n,n,3)*255).astype(np.uint8)
    for f,name in [(R.subband_entropy_clutter,"V6"),(R.feature_congestion_clutter,"V7")]:
        c_blank=f(blank).scalar; c_clut=f(cluttered).scalar; c_blank2=f(blank).scalar
        assert abs(c_blank-c_blank2)<1e-9, name
        assert c_clut>c_blank, (name,c_clut,c_blank)
        print("  %s clutter: cluttered=%.3f > blank=%.3f ; deterministic  OK"%(name,c_clut,c_blank))


if __name__ == "__main__":
    for fn in [test_v2_slope_recovery, test_v2_discomfort_ordering_and_determinism,
               test_v13_entropy_ordering, test_v1_curves_vs_angles, test_v6_v7_clutter_ordering]:
        print(fn.__name__); fn()
    print("\nALL RELIABLE-ATTR CORE TESTS PASSED (V2, V13, V1, V6, V7)")
