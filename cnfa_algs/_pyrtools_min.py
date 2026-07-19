"""
cnfa_algs._pyrtools_min — minimal pyrtools-compatible shim (Sprint COMP-CORRECT S1, 2026-07-19).

PURPOSE. The Rosenholtz reference implementation (vendored `visual_clutter` 1.0.7, MIT) needs three
things from pyrtools, which the sandbox cannot install: `pyramids.GaussianPyramid`,
`pyramids.SteerablePyramidFreq`, and `upConv`. This module implements exactly those, to pyrtools'
published conventions, so the UNMODIFIED reference code runs here. The Mac (where real pyrtools
installs) then adjudicates this shim numerically — any port divergence localizes HERE, not in the
reference algorithm. See scripts/reference_clutter_compare.py + the Codex Mac-run task.

PORT-CHECK notes (conventions taken from the pyrtools source/docs, to be confirmed by the Mac run):
  P1  'reflect1' edge = reflection about the edge SAMPLE (abc|cba -> like cv2 BORDER_REFLECT_101);
      'reflect2' would repeat the edge sample.
  P2  GaussianPyramid: 1-D binomial-5 filter [1,4,6,4,1]/16 applied separably via corrDn with
      step (2,1) then (1,2); pyr_coeffs[(0,0)] is the ORIGINAL image; height=n gives levels 0..n-1.
  P3  upConv: zero-interleaved upsampling then CONVOLUTION (kernel flipped) with reflect1 edges,
      NO automatic gain compensation (caller scales the filter if energy preservation is wanted).
      NOTE: the reference package's collapse() passes an unscaled unity-sum kernel, so upsampled
      maps carry a 4x-per-level attenuation relative to the original MATLAB collapse (which used
      RRoverlapconvexpand with kernel*2 per axis). We reproduce the PACKAGE (it is the declared
      reference); the MATLAB-divergence question is logged in the port findings for adjudication.
  P4  SteerablePyramidFreq: Simoncelli frequency-domain construction — raised-cosine radial
      transition of width 1 octave; angular masks sqrt(const)*cos(theta)^order with
      const = 2^(2K) K!^2 / ((K+1) (2K)!); band filters applied to the fftshifted DFT; lowpass
      recursively cropped (frequency-domain downsample by 2). Keys: 'residual_highpass',
      (level, band), 'residual_lowpass'. Power complementarity of all masks == 1 everywhere is
      asserted in the self-test (the internal correctness invariant that needs no reference).

Self-test: python3 -m cnfa_algs._pyrtools_min
"""
from __future__ import annotations
from math import factorial
import numpy as np


# ---------------------------------------------------------------- edge handling + corr/conv cores
def _pad_reflect1(im: np.ndarray, py: int, px: int) -> np.ndarray:
    return np.pad(im, ((py, py), (px, px)), mode="reflect")   # numpy 'reflect' == reflect1 (P1)


def corrDn(image: np.ndarray, filt: np.ndarray, edge_type: str = "reflect1",
           step=(1, 1), start=(0, 0)) -> np.ndarray:
    """Correlate (no kernel flip) then downsample. Only reflect1 is implemented (P1)."""
    from scipy.signal import correlate2d
    filt = np.asarray(filt, float)
    if filt.ndim == 1:
        filt = filt.reshape(-1, 1)
    py, px = filt.shape[0] // 2, filt.shape[1] // 2
    padded = _pad_reflect1(np.asarray(image, float), py, px)
    out = correlate2d(padded, filt, mode="valid")
    # 'valid' on symmetric padding returns exactly the original size for odd filters
    return out[start[0]::step[0], start[1]::step[1]]


def upConv(image: np.ndarray, filt: np.ndarray, edge_type: str = "reflect1",
           step=(2, 2), start=(0, 0), stop=None) -> np.ndarray:
    """Zero-interleave upsample by `step`, then CONVOLVE with filt (reflect1). No gain (P3)."""
    from scipy.signal import convolve2d
    image = np.asarray(image, float)
    filt = np.asarray(filt, float)
    if filt.ndim == 1:
        filt = filt.reshape(-1, 1)
    H, W = image.shape
    up = np.zeros((H * step[0], W * step[1]))
    up[start[0]::step[0], start[1]::step[1]] = image
    py, px = filt.shape[0] // 2, filt.shape[1] // 2
    padded = _pad_reflect1(up, py, px)
    out = convolve2d(padded, filt, mode="valid")
    if stop is not None:
        out = out[:stop[0], :stop[1]]
    return out


# ---------------------------------------------------------------- Gaussian pyramid (P2)
# pyrtools binomial_filter(5): binomial coefficients normalized to sum sqrt(2) — NOT unity.
# (Codex adjudication 2026-07-19: this sqrt(2) scaling was the P2 divergence; with it, ALL
# Feature Congestion and layer values match real pyrtools.) Separable x+y application gives a
# DC gain of 2 per level — the pyrtools energy convention the reference code was written against.
_BINOM5 = (np.array([1.0, 4.0, 6.0, 4.0, 1.0]) / 16.0) * np.sqrt(2.0)


class _GaussianPyramid:
    def __init__(self, image, height=None):
        image = np.asarray(image, float)
        self.pyr_coeffs = {(0, 0): image}
        levels = height if height is not None else 99
        cur = image
        for i in range(1, levels):
            if min(cur.shape) < 5:
                break
            cur = corrDn(cur, _BINOM5.reshape(-1, 1), "reflect1", step=(2, 1))
            cur = corrDn(cur, _BINOM5.reshape(1, -1), "reflect1", step=(1, 2))
            self.pyr_coeffs[(i, 0)] = cur


# ---------------------------------------------------------------- steerable pyramid, frequency domain (P4)
def _rcos_table(width=1.0, position=0.0, values=(0.0, 1.0), size=256):
    """EXACT pyrtools rcosFn (adjudication fix P4a, 2026-07-19): cos^2 transition on a
    (size+3)-point table; X remapped to [position, position+width]."""
    X = np.pi * np.arange(-size - 1, 2) / (2.0 * size)
    Y = values[0] + (values[1] - values[0]) * np.cos(X) ** 2
    Y[0] = Y[1]
    Y[size + 2] = Y[size + 1]
    X = position + (2.0 * width / np.pi) * (X + np.pi / 4.0)
    return X, Y


def _point_op(im: np.ndarray, Y: np.ndarray, origin: float, increment: float) -> np.ndarray:
    """Lookup-table application with linear interpolation (pyrtools pointOp)."""
    pos = (im - origin) / increment
    idx = np.clip(pos, 0, len(Y) - 1 - 1e-9)
    lo = np.floor(idx).astype(int)
    frac = idx - lo
    return Y[lo] * (1 - frac) + Y[np.minimum(lo + 1, len(Y) - 1)] * frac


class _SteerablePyramidFreq:
    """Analysis-only frequency-domain steerable pyramid (Simoncelli), pyrtools-compatible keys."""

    def __init__(self, image, height=3, order=3):
        im = np.asarray(image, float)
        self.num_orientations = order + 1
        M, N = im.shape
        ctrM, ctrN = int(np.ceil((M + 0.5) / 2)), int(np.ceil((N + 0.5) / 2))
        xramp, yramp = np.meshgrid((np.arange(N) - (ctrN - 1)) / (N / 2.0),
                                   (np.arange(M) - (ctrM - 1)) / (M / 2.0))
        angle = np.arctan2(yramp, xramp)
        log_rad = np.sqrt(xramp ** 2 + yramp ** 2)
        log_rad[ctrM - 1, ctrN - 1] = log_rad[ctrM - 1, ctrN - 2]
        log_rad = np.log2(log_rad)

        Xrcos, Yrcos = _rcos_table(1.0, -0.5, (0.0, 1.0))
        Yrcos = np.sqrt(Yrcos)
        YIrcos = np.sqrt(1.0 - Yrcos ** 2)
        inc = Xrcos[1] - Xrcos[0]

        lo0mask = _point_op(log_rad, YIrcos, Xrcos[0], inc)
        hi0mask = _point_op(log_rad, Yrcos, Xrcos[0], inc)

        imdft = np.fft.fftshift(np.fft.fft2(im))
        self.pyr_coeffs = {}
        self._mask_power = np.abs(hi0mask) ** 2 + np.abs(lo0mask) ** 2  # correctness invariant

        hi0dft = imdft * hi0mask
        self.pyr_coeffs["residual_highpass"] = np.real(np.fft.ifft2(np.fft.ifftshift(hi0dft)))
        lodft = imdft * lo0mask

        K = order
        const = (2.0 ** (2 * K)) * (factorial(K) ** 2) / float(self.num_orientations * factorial(2 * K))
        lut = 1024
        Xcosn = np.pi * np.arange(-(2 * lut + 1), lut + 2) / lut
        # REAL (non-complex) pyramid: pure sqrt(const)*cos^K, NO lobe mask (adjudication fix
        # P4b — the |alfa|<pi/2 mask belongs only to the complex variant)
        Ycosn = np.sqrt(const) * (np.cos(Xcosn)) ** K
        cinc = Xcosn[1] - Xcosn[0]

        for lev in range(height):
            Xrcos = Xrcos - 1.0                                   # shift transition down one octave
            himask = _point_op(log_rad, Yrcos, Xrcos[0], inc)
            band_power = np.zeros_like(himask)
            ang_power = np.zeros_like(himask)
            for b in range(self.num_orientations):
                # RAW angle lookup, origin shifted per band — the 3*pi-wide table absorbs the
                # range without rewrapping (adjudication fix P4c, matches pyrtools pointOp call)
                anglemask = _point_op(angle, Ycosn, Xcosn[0] + np.pi * b / self.num_orientations, cinc)
                banddft = ((-1j) ** K) * lodft * anglemask * himask
                self.pyr_coeffs[(lev, b)] = np.real(np.fft.ifft2(np.fft.ifftshift(banddft)))
                # steering identity for the REAL pyramid: cos^(2K) sums over K+1 orientations
                # to 1/const, so sum_b anglemask^2 == 1 with no antipode term (cos^2 covers both)
                ang_power += anglemask ** 2
            if lev == 0:
                self._ang_power = ang_power           # asserted in self-test
            # frequency-domain downsample of the lowpass by 2
            dims = np.array(lodft.shape)
            lodims = np.ceil((dims - 0.5) / 2.0).astype(int)
            loctr = np.ceil((lodims + 0.5) / 2.0).astype(int)
            ctr = np.ceil((dims + 0.5) / 2.0).astype(int)
            lostart = ctr - loctr
            loend = lostart + lodims
            # S1B-ADJUDICATED (Codex, real-pyrtools source, 2026-07-19): log_rad is cropped
            # but NEVER incremented — scale progression is represented SOLELY by the Xrcos
            # shift at each level's start. The former "+1.0 then -1.0" bookkeeping double-
            # shifted deeper levels by an extra octave each.
            log_rad = log_rad[lostart[0]:loend[0], lostart[1]:loend[1]]
            angle = angle[lostart[0]:loend[0], lostart[1]:loend[1]]
            lodft = lodft[lostart[0]:loend[0], lostart[1]:loend[1]]
            lomask = _point_op(log_rad, YIrcos, Xrcos[0], inc)
            lodft = lodft * lomask

        self.pyr_coeffs["residual_lowpass"] = np.real(np.fft.ifft2(np.fft.ifftshift(lodft)))


# ---------------------------------------------------------------- pyrtools-shaped namespace
class _Pyramids:
    GaussianPyramid = _GaussianPyramid
    SteerablePyramidFreq = _SteerablePyramidFreq


pyramids = _Pyramids()


def install_as_pyrtools():
    """Register this module under sys.modules['pyrtools'] so the vendored reference imports it."""
    import sys, types
    mod = sys.modules[__name__]
    sys.modules["pyrtools"] = mod
    return mod


# ---------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("_pyrtools_min self-test\n" + "-" * 56)
    rng = np.random.RandomState(0)
    im = rng.rand(96, 128) * 200 + 20

    # Gaussian pyramid: shapes halve; DC preserved (unity-sum filter); level0 IS the input
    gp = _GaussianPyramid(im, height=3)
    assert np.array_equal(gp.pyr_coeffs[(0, 0)], im)
    assert gp.pyr_coeffs[(1, 0)].shape == (48, 64) and gp.pyr_coeffs[(2, 0)].shape == (24, 32)
    flat = _GaussianPyramid(np.full((64, 64), 7.0), height=3)
    for i in range(3):
        # pyrtools convention: sqrt(2)-sum filter per axis -> DC gain 2 per level (P2, adjudicated)
        assert np.allclose(flat.pyr_coeffs[(i, 0)], 7.0 * (2.0 ** i), rtol=1e-10), \
            f"level {i} DC should be 7*2^{i}"
    print("GaussianPyramid: shapes halve, level0=input, DC gain 2/level (pyrtools convention)  OK")

    # upConv: adjoint shape doubling; constant image with kernel*2-per-axis stays ~constant
    k1 = np.array([[0.05, 0.25, 0.4, 0.25, 0.05]])
    k2 = (k1 * 2).T @ (k1 * 2)
    up = upConv(np.full((10, 10), 3.0), k2, "reflect1", step=[2, 2], start=[0, 0])
    assert up.shape == (20, 20)
    assert abs(up[8:12, 8:12].mean() - 3.0) < 1e-6, "energy-compensated upConv should preserve DC"
    print("upConv: doubles size; DC preserved with 2x/axis kernel  OK")

    # Steerable pyramid: key set, shapes, and the POWER-COMPLEMENTARITY invariant at stage 0
    sp = _SteerablePyramidFreq(im, height=3, order=3)
    keys = set(sp.pyr_coeffs.keys())
    assert "residual_highpass" in keys and "residual_lowpass" in keys
    assert all((lev, b) in keys for lev in range(3) for b in range(4))
    assert np.allclose(sp._mask_power, 1.0, atol=1e-8), \
        f"hi0^2+lo0^2 must ==1 everywhere (max dev {np.abs(sp._mask_power-1).max():.2e})"
    print(f"SteerablePyramidFreq: 3 levels x 4 bands + residuals; "
          f"|hi0|^2+|lo0|^2 == 1 (max dev {np.abs(sp._mask_power-1).max():.1e})  OK")

    # steering identity: the 4 cos^3 angular lobes (+ their antipodes) tile orientation space
    dev = np.abs(sp._ang_power - 1.0).max()
    assert dev < 1e-3, f"angular masks must tile to unity (max dev {dev:.2e})"
    print(f"angular steering identity: sum_b mask_b^2 == 1 (real pyramid; max dev {dev:.1e})  OK")

    # determinism
    sp2 = _SteerablePyramidFreq(im, height=3, order=3)
    assert all(np.array_equal(sp.pyr_coeffs[k], sp2.pyr_coeffs[k]) for k in sp.pyr_coeffs)
    print("determinism x2  OK")
    print("-" * 56 + "\n_pyrtools_min self-test: PASS")
