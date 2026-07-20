"""
cnfa_algs.reliable_attrs — the GREEN Tier-A reliability sprint primitives (deterministic, pure
numpy/OpenCV, no inferred-plan dependency). Each returns an AttributeResult; pure helpers are
directly unit-testable on synthetic arrays.

ALL AMBER after the Fable/Codex-2 reviews: deterministic but NOT construct-validated, and several
are declared PROXIES, not faithful implementations of the cited papers.

  V2  spectral_slope_deviation       — radial FFT 1/f slope + mid-band residual. PROXY, NOT the
                                        2-D Penacchio-Wilkins discomfort metric; scale-dependent;
                                        no FOV/angular claim. (Field 1987 for 1/f only)
  V13 edge_orientation_entropy       — Sobel 1st-order + first-neighbour co-occurrence (a PROXY for
                                        the Grebenkina pairwise-over-distances 2nd-order measure).
                                        Abstains below 40 edge px.
  V1  contour_angularity_index       — Canny+turning-angle curve/corner statistic. IMAGE-contour,
                                        NOT validated architectural valence. (Bar&Neta 2006 = obj pref)
  V6  grayscale_gabor_entropy_proxy  — grayscale Gabor-magnitude entropy PROXY, NOT Rosenholtz
                                        Subband Entropy (no CIELab, no steerable pyramid).
  V7  local_congestion_proxy         — local-variance colour/contrast/orientation PROXY, NOT
                                        Rosenholtz Feature Congestion (arbitrary weights + K).

DETERMINISM: no randomness; FFT fit band excluded from DC and the Nyquist end; float accumulation
=> audit_class replayable_tol at the socket. Each declares its constants + failure modes. Faithful
reimplementations of V2/V6/V7 remain OWED (see FABLE_REVIEW_DISPOSITION).
"""
from __future__ import annotations
import numpy as np
import cv2

try:
    from .core import AttributeResult, normalize01
except Exception:                       # allow standalone import in tests
    from cnfa_algs.core import AttributeResult, normalize01


def _gray01(img):
    if img.ndim == 3:
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        g = img
    g = g.astype(np.float32)
    return g / 255.0 if g.max() > 1.5 else g


# ============================================================ V2 spectral_discomfort_deviation
NATURAL_POWER_SLOPE = -2.0        # natural scenes: power ~ 1/f^2 (amplitude ~ 1/f); Field 1987
# Codex-2 F2 fix: FOV was ornamental (never entered the math) yet was emitted in the score,
# contradicting the registry. Removed entirely — this measure is a scale-free radial slope +
# residual and makes NO angular-subtense / discomfort-magnitude claim.


def _radial_power_spectrum(gray01):
    """Hann-windowed 2D FFT -> radially-averaged power over frequency rings."""
    h, w = gray01.shape
    wy = np.hanning(h)[:, None]; wx = np.hanning(w)[None, :]
    win = gray01 * (wy * wx)
    F = np.fft.fftshift(np.fft.fft2(win))
    P = (np.abs(F) ** 2)
    cy, cx = h // 2, w // 2
    y, x = np.mgrid[0:h, 0:w]
    r = np.sqrt((y - cy) ** 2 + (x - cx) ** 2).astype(int)
    rmax = min(cy, cx)
    tbin = np.bincount(r.ravel(), P.ravel())
    nbin = np.bincount(r.ravel())
    prof = tbin[:rmax] / np.maximum(nbin[:rmax], 1)
    return prof            # index = radial spatial frequency (cycles/image), prof = mean power


def spectral_slope_fit(prof):
    """OLS log-log slope over the mid band (exclude DC/lowest 2 and the top 15% near Nyquist)."""
    n = len(prof)
    lo = max(2, int(0.02 * n)); hi = int(0.85 * n)
    f = np.arange(lo, hi); p = prof[lo:hi]
    m = p > 0
    if m.sum() < 8:
        return 0.0, 0.0, (lo, hi)
    x = np.log(f[m]); y = np.log(p[m])
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat) ** 2)); ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 1.0
    return float(slope), float(max(0.0, min(1.0, r2))), (lo, hi)


def _csf_weight(f_norm):
    """Mannan/Wilkins-style band-pass CSF peak ~ mid spatial frequency (normalized 0..1)."""
    # simple log-Gaussian peaked at mid SF where pattern glare/discomfort concentrates
    return np.exp(-((np.log(f_norm + 1e-6) - np.log(0.25)) ** 2) / (2 * 0.5 ** 2))


def _mid_band_residual(prof, slope, intercept_band):
    """CSF-weighted positive excess of power above the 1/f fit line in the mid band
    (Penacchio & Wilkins 2015: discomfort rises with departure from the natural 1/f profile)."""
    lo, hi = intercept_band
    f = np.arange(lo, hi); p = prof[lo:hi]
    m = p > 0
    if m.sum() < 8:
        return 0.0
    x = np.log(f[m]); y = np.log(p[m])
    b = y.mean() - slope * x.mean()
    resid = y - (slope * x + b)              # positive = excess energy above 1/f
    fnorm = (f[m] - lo) / max(hi - lo, 1)
    w = _csf_weight(fnorm)
    excess = np.clip(resid, 0, None) * w
    return float(np.sum(excess) / (np.sum(w) + 1e-9))


def spectral_discomfort_deviation(img) -> AttributeResult:
    g = _gray01(img)
    prof = _radial_power_spectrum(g)
    slope, r2, band = spectral_slope_fit(prof)
    naturalness = float(np.exp(-abs(slope - NATURAL_POWER_SLOPE) / 1.0))   # 1 at slope=-2
    resid = _mid_band_residual(prof, slope, band)
    discomfort = float(np.clip(resid / 0.5, 0, 1))    # declared scale; higher = more discomfort
    conf = 0.7 if r2 >= 0.9 else 0.35
    return AttributeResult(
        key="cnfa.fluency.spectral_slope_deviation",
        scalar=discomfort, field=None, confidence=conf,
        method=f"radial FFT 1/f slope={slope:.2f}(R2={r2:.2f}) + mid-band residual; "
               f"PROXY, NOT the 2-D Penacchio-Wilkins discomfort metric; no angular calibration (M1)",
        extras={"power_slope": round(slope, 3), "r2": round(r2, 3),
                "naturalness": round(naturalness, 3),
                "mid_band_residual": round(discomfort, 4)},
        failure_modes=["scale-DEPENDENT (raster size changes the score); no angular calibration",
                       "radial averaging discards the 2-D Fourier-energy distribution the "
                       "Penacchio-Wilkins measure requires — this is a slope statistic only",
                       "defocus/JPEG shift the tail; measures the photograph, not only the room"])


# ============================================================ V13 edge_orientation_entropy
MIN_EDGE_PX = 40                 # below this the orientation distribution is undefined


def _orientation_hist(gray01, nbins=18):
    gx = cv2.Sobel(gray01, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray01, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    ang = (np.arctan2(gy, gx) % np.pi)           # 0..pi (undirected edges)
    m = mag > (0.05 * mag.max() + 1e-9)
    if m.sum() < MIN_EDGE_PX:
        # FABLE F1 FIX: do NOT impute a uniform histogram — that turned "no edges" into
        # "maximum orientation diversity" (a blank image scored entropy 1.0). Signal undefined.
        return None, mag, ang, m
    idx = np.minimum((ang[m] / np.pi * nbins).astype(int), nbins - 1)
    h = np.bincount(idx, weights=mag[m], minlength=nbins).astype(float)
    h = h / (h.sum() + 1e-12)
    return h, mag, ang, m


def _entropy(p):
    p = np.asarray(p, float); p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def edge_orientation_entropy(img) -> AttributeResult:
    g = _gray01(img)
    nb = 18
    h, mag, ang, m = _orientation_hist(g, nb)
    if h is None:                    # FABLE F1 FIX: undefined on a near-edgeless image -> abstain
        return AttributeResult(
            key="cnfa.fluency.edge_orientation_entropy", scalar=None, field=None, confidence=0.0,
            method="orientation entropy undefined: <%d edge px (M1)" % MIN_EDGE_PX,
            extras={"reason": "insufficient_edges", "edge_px": int(m.sum())})
    first = _entropy(h) / np.log2(nb)            # normalized 0..1: 1 = isotropic, 0 = single orient
    # second-order: orientation co-occurrence of NEIGHBOURING edge pixels (declared as a first-
    # neighbour proxy — NOT the full Grebenkina/Redies pairwise-over-distances measure; see note).
    oi = np.minimum((ang / np.pi * nb).astype(int), nb - 1)
    shifted = np.roll(oi, 1, axis=1)
    valid = m & np.roll(m, 1, axis=1)            # both members of the pair are real edges
    if valid.sum() >= MIN_EDGE_PX:
        pairs = oi[valid] * nb + shifted[valid]
        hp = np.bincount(pairs, minlength=nb * nb).astype(float)
        hp = hp / (hp.sum() + 1e-12)
        second = _entropy(hp) / np.log2(nb * nb)
    else:
        second = first
    scalar = float(0.5 * first + 0.5 * second)
    return AttributeResult(
        key="cnfa.fluency.edge_orientation_entropy",
        scalar=scalar, field=None, confidence=0.65,
        method="Sobel orientation-histogram entropy (1st) + first-neighbour co-occurrence (2nd) (M1)",
        extras={"first_order": round(first, 4), "second_order": round(second, 4),
                "edge_px": int(m.sum())},
        failure_modes=["2nd-order is a first-neighbour proxy, NOT the Grebenkina pairwise-over-"
                       "distances measure — construct-validate before claiming that literature",
                       "cardinal-dominance is viewpoint-dependent (roll not corrected)",
                       "abstains below %d edge px (no imputed distribution)" % MIN_EDGE_PX])


# ============================================================ V1 contour_angularity_index
# FABLE F8/D5 FIX: the previous `_straight_line_bow` multiplied its result by 0.0 — it could NEVER
# warn (dead code masquerading as a lens-distortion diagnostic). Removed. A real bow diagnostic
# needs per-image intrinsics we do not have; the honest state is: no bow warning is claimed.

def contour_angularity_index(img) -> AttributeResult:
    """Curve fraction vs sharp-corner density of linked contours. Curvilinear interiors are
    preferred / less threatening (Bar & Neta 2006/2007; Dazkir & Read 2012; Chuquichambi 2022).
    NOTE (Decision D4): Vartanian 2013 'approach decisions' claim is deliberately NOT cited —
    that paper found beauty/ACC effects, not approach. Base variant, whole-image, deterministic."""
    g = _gray01(img)
    g8 = (g * 255).astype(np.uint8)
    edges = cv2.Canny(g8, 60, 160)
    cs, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    curve_len = 0.0; corner_len = 0.0; total_len = 0.0
    for c in cs:
        if len(c) < 24:                       # ignore tiny fragments
            continue
        peri = cv2.arcLength(c, False)
        if peri < 40:
            continue
        # polygon-vertex scale (scale-robust): a circle -> many small-angle vertices; a polygon
        # -> few large-angle vertices. Per-step pixel turning is near-zero on a staircased curve.
        approx = cv2.approxPolyDP(c, 0.01 * peri, False)[:, 0, :].astype(np.float32)
        if len(approx) < 3:
            total_len += float(peri); continue        # a long straight run
        v = np.diff(approx, axis=0)
        n = np.linalg.norm(v, axis=1) + 1e-9
        u = v / n[:, None]
        dots = np.clip((u[:-1] * u[1:]).sum(1), -1, 1)
        ang = np.arccos(dots)                          # turning at each interior vertex
        seglen = (n[:-1] + n[1:]) / 2
        total_len += float(peri)
        curve_len += float(seglen[(ang > 0.08) & (ang < 0.8)].sum())   # gentle/moderate curvature
        corner_len += float(seglen[ang >= 1.0].sum())                  # sharp corners (threat)
    if total_len < 50:
        return AttributeResult(key="cnfa.geometry.contour_angularity", scalar=None,
                               confidence=0.0, method="insufficient contour (M1)",
                               extras={"reason": "no_contour"})
    curve_fraction = curve_len / total_len
    corner_density = corner_len / total_len
    # signed valence: curvature is positive, sharp corners negative
    scalar = float(np.clip(0.5 + 0.5 * (curve_fraction - corner_density), 0, 1))
    return AttributeResult(
        key="cnfa.geometry.contour_angularity",
        scalar=scalar, field=None, confidence=0.65,
        method="Canny+turning-angle: curve fraction vs sharp-corner density (M1)",
        extras={"curve_fraction": round(curve_fraction, 4),
                "corner_density": round(corner_density, 4)},
        failure_modes=["IMAGE-contour statistic, NOT validated architectural valence: object "
                       "contours (plants, fabric, people, graphics) are counted as architectural",
                       "barrel/lens distortion bows straight lines (NOT detected — no intrinsics)",
                       "Canny fragmentation in clutter biases toward short chains"])


# ============================================================ V6/V7 Rosenholtz clutter
def _oriented_energy(gray01, nscale=3, norient=4):
    """DoG-band oriented energy pyramid (steerable-ish), deterministic."""
    feats = []
    cur = gray01.copy()
    for s in range(nscale):
        for o in range(norient):
            theta = o * np.pi / norient
            k = cv2.getGaborKernel((11, 11), 2.0, theta, 6.0, 0.5, 0, ktype=cv2.CV_32F)
            feats.append(np.abs(cv2.filter2D(cur, cv2.CV_32F, k)))
        cur = cv2.pyrDown(cur)
    return feats


def subband_entropy_clutter(img) -> AttributeResult:
    """V6 — Shannon entropy of oriented-subband coefficients: how incompressible the scene is per
    glance (Rosenholtz, Li & Nakano 2007). Higher = more clutter."""
    g = _gray01(img)
    feats = _oriented_energy(g)
    ent = 0.0
    for f in feats:
        v = f.ravel(); v = v[np.isfinite(v)]
        if v.size < 16:
            continue
        hist, _ = np.histogram(v, bins=32, range=(0, v.max() + 1e-9), density=True)
        p = hist[hist > 0] / hist.sum()
        ent += float(-(p * np.log2(p)).sum())
    ent_norm = float(np.clip(ent / (len(feats) * 5.0), 0, 1))    # declared normaliser
    return AttributeResult(
        key="cnfa.fluency.grayscale_gabor_entropy_proxy",
        scalar=ent_norm, field=None, confidence=0.7,
        method="grayscale Gabor-magnitude entropy PROXY — NOT Rosenholtz Subband Entropy "
               "(no CIELab, no steerable pyramid, declared divisor) (M1)",
        extras={"raw_entropy_bits": round(ent, 3), "clutter_family": "V6"},
        failure_modes=["resolution/JPEG/defocus shift entropy — assumes homogeneous capture",
                       "one of a clutter family (V6/V7/legacy) — pick ONE for hedonics (Decision D2)"])


def feature_congestion_clutter(img) -> AttributeResult:
    """V7 — local feature-space congestion in colour, contrast, orientation (Rosenholtz, Li,
    Mansfield & Jin 2005): how 'full' the local feature distribution already is. Higher = harder
    for any new item to pop out. Deterministic."""
    lab = cv2.cvtColor(img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR),
                       cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    k = (9, 9)
    def local_var(ch):
        m = cv2.blur(ch, k); m2 = cv2.blur(ch * ch, k)
        return np.clip(m2 - m * m, 0, None)
    color_clutter = np.sqrt(local_var(A) + local_var(B) + 1e-6)
    Lb = cv2.Laplacian(L, cv2.CV_32F)
    contrast_clutter = np.sqrt(local_var(Lb) + 1e-6)
    g = _gray01(img)
    oe = _oriented_energy(g, nscale=1, norient=4)
    orient_clutter = np.sqrt(sum(local_var(cv2.resize(o, (L.shape[1], L.shape[0]))) for o in oe) + 1e-6)
    # Minkowski-ish pool (published weighting is contrast/colour-heavy — declared)
    fc = 0.5 * color_clutter + 0.3 * contrast_clutter + 0.2 * orient_clutter
    # magnitude, soft-saturated by a declared reference K (Lab-variance units); monotone in
    # congestion: flat -> ~0, busy interior -> mid, chaotic -> ~1. NOT mean/p95 (that measured
    # uniformity, so a blank image wrongly scored high).
    FC_K = 40.0
    mean_fc = float(fc.mean())
    scalar = float(mean_fc / (mean_fc + FC_K))
    return AttributeResult(
        key="cnfa.fluency.local_congestion_proxy",
        scalar=scalar, field=normalize01(fc), confidence=0.7,
        method="local-variance colour/contrast/orientation congestion PROXY — NOT Rosenholtz "
               "Feature Congestion (declared arbitrary weights + saturation K) (M1)",
        extras={"clutter_family": "V7"},
        failure_modes=["sensor noise/high ISO inflates contrast clutter",
                       "verify pooling weights vs the 2007 paper before publication",
                       "one of a clutter family (V6/V7/legacy) — pick ONE for hedonics (Decision D2)"])
