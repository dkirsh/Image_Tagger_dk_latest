"""
cnfa_algs.faithful_clutter — FAITHFUL Feature Congestion (V7) + Subband Entropy (V6),
computed by the VENDORED Rosenholtz reference implementation (Sprint COMP-CORRECT S1, 2026-07-19).

This is the [PORT], done the honest way: the algorithm code is the unmodified `visual_clutter`
1.0.7 package (MIT, vendored under cnfa_algs/_vendor/ — itself a port of the authors' MATLAB),
running on cnfa_algs._pyrtools_min (our pyramid shim, internally invariant-tested). Every constant
is the reference's own: FC combination color/0.2088 + contrast/0.0660 + orientation/0.0269 with
Minkowski p=1; Lab covariance sensitivity deltas (0.0007, 0.1, 0.05)^2; DoG1 contrast sigma 1 with
pool sigma 3; Bergen-Landy opponent energy (filter 16/14*1.75, pool 1.75, noise 1.0/0.001);
det^(1/6) color / det^(1/4) orientation volume->length exponents; SE steerable pyramid 3 levels x
4 orients, sqrt-N binning entropy, chroma weight 0.0625 with the range<0.008 zeroing rule.

STATUS / TIER: AMBER pending the cross-implementation adjudication — the Mac run with REAL pyrtools
(scripts/reference_clutter_compare.py + the Codex task) must numerically match this shim-backed run
before any faithfulness claim is finalized. Until then the method strings say SHIM-BACKED REFERENCE.
The existing proxies (grayscale_gabor_entropy_proxy, local_congestion_proxy) STAY registered and
running per Decision Q3 (parallel run to measure how wrong the proxies were).

Self-test: python3 -m cnfa_algs.faithful_clutter   (fixtures + determinism + real-image smoke)
"""
from __future__ import annotations
import numpy as np

try:
    from .attributes import AttributeResult, normalize01
except Exception:
    from attributes import AttributeResult, normalize01  # type: ignore


_VLC = None


def _get_vlc_class():
    """Install the pyrtools shim, then import the vendored reference (unmodified)."""
    global _VLC
    if _VLC is None:
        import sys
        from pathlib import Path
        from . import _pyrtools_min
        _pyrtools_min.install_as_pyrtools()
        # the vendored package uses absolute self-imports (`from visual_clutter.utils import *`),
        # so expose the _vendor dir as a top-level path — vendored code stays byte-identical
        vendor = str(Path(__file__).resolve().parent / "_vendor")
        if vendor not in sys.path:
            sys.path.insert(0, vendor)
        from visual_clutter.clutter import Vlc
        _VLC = Vlc
    return _VLC


def _prep_rgb(img_bgr) -> np.ndarray:
    a = np.asarray(img_bgr)
    if a.ndim == 2:
        a = np.stack([a] * 3, -1)
    return a[..., ::-1].copy()          # reference expects RGB


def feature_congestion_faithful(img_bgr) -> AttributeResult:
    """V7 FAITHFUL: Rosenholtz Feature Congestion via the vendored reference implementation."""
    Vlc = _get_vlc_class()
    rgb = _prep_rgb(img_bgr)
    clt = Vlc(rgb, numlevels=3, contrast_filt_sigma=1, contrast_pool_sigma=3, color_pool_sigma=3)
    scalar_fc, map_fc = clt.getClutter_FC(p=1, pix=0)
    # layer means for the audit trail (the three feature channels BEFORE combination)
    color_map = clt.color_clutter_map
    contrast_map = clt.contrast_clutter_map
    orient_map = clt.orientation_clutter_map
    return AttributeResult(
        key="cnfa.fluency.feature_congestion",
        scalar=float(np.clip(scalar_fc / 12.0, 0, 1)),      # 12 = declared display full-scale only
        field=normalize01(np.asarray(map_fc, float)), confidence=0.6,
        method="Rosenholtz FC — SHIM-BACKED REFERENCE (vendored visual_clutter 1.0.7 on "
               "_pyrtools_min; Mac-pyrtools adjudication pending) (M1)",
        extras={"fc_raw": round(float(scalar_fc), 6),
                "layer_means": {"color": round(float(np.mean(color_map)), 6),
                                "contrast": round(float(np.mean(contrast_map)), 6),
                                "orientation": round(float(np.mean(orient_map)), 6)},
                "combination": {"color_div": 0.2088, "contrast_div": 0.0660,
                                "orient_div": 0.0269, "minkowski_p": 1},
                "params": {"numlevels": 3, "contrast_filt_sigma": 1,
                           "contrast_pool_sigma": 3, "color_pool_sigma": 3},
                "display_fullscale": 12.0},
        failure_modes=["AMBER until Mac-pyrtools numeric adjudication of the pyramid shim",
                       "package collapse() lacks the MATLAB x4 upConv gain — upper pyramid levels "
                       "are attenuated ~4x/level vs the 2007 MATLAB (logged PORT finding P3)",
                       "combination weights fit on maps/UI, not interiors (corpus, L6)"])


def subband_entropy_faithful(img_bgr) -> AttributeResult:
    """V6 FAITHFUL: Rosenholtz Subband Entropy via the vendored reference implementation."""
    Vlc = _get_vlc_class()
    rgb = _prep_rgb(img_bgr)
    clt = Vlc(rgb, numlevels=3)
    se = clt.getClutter_SE(wlevels=3, wght_chrom=0.0625)
    return AttributeResult(
        key="cnfa.fluency.subband_entropy",
        scalar=float(np.clip(se / 4.0, 0, 1)),              # 4 nats = declared display full-scale
        confidence=0.6,
        method="Rosenholtz SE — SHIM-BACKED REFERENCE (steerable pyramid 3x4, sqrt-N-bin Shannon, "
               "chroma wght 0.0625; Mac-pyrtools adjudication pending) (M1)",
        extras={"se_raw_nats": round(float(se), 6),
                "params": {"wlevels": 3, "wor": 4, "wght_chrom": 0.0625,
                           "chroma_zero_range": 0.008},
                "display_fullscale": 4.0},
        failure_modes=["AMBER until Mac-pyrtools numeric adjudication of the pyramid shim",
                       "entropy binning is sqrt(N) uniform — sensitive to subband size",
                       "validated on maps/UI in 2007, not interiors (corpus, L6)"])


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    import cv2, glob, sys, time
    print("faithful_clutter self-test (reference implementation on _pyrtools_min shim)\n" + "-" * 66)
    H, W = 120, 160
    mk = lambda f: np.clip(f, 0, 255).astype(np.uint8)
    rng = np.random.RandomState(0)

    blank = mk(np.full((H, W, 3), 128.0))
    grad = mk(np.stack([40 + 170 * np.mgrid[0:H, 0:W][1] / W] * 3, -1))
    tex = mk(np.stack([128 + 30 * rng.randn(H, W)] * 3, -1))
    clut = np.full((H, W, 3), 200.0)                       # colored object field
    rs = np.random.RandomState(3)
    for i in range(28):
        x, y = int(rs.rand() * (W - 30)) + 15, int(rs.rand() * (H - 30)) + 15
        cv2.circle(clut, (x, y), rs.randint(4, 12), tuple(int(c) for c in rs.randint(0, 255, 3)), -1)
    clut = mk(clut)

    t0 = time.time()
    fc_vals = {}
    for name, im in [("blank", blank), ("gradient", grad), ("texture", tex), ("clutter", clut)]:
        r = feature_congestion_faithful(im)
        fc_vals[name] = r.extras["fc_raw"]
    print(f"FC raw: blank={fc_vals['blank']:.3f} gradient={fc_vals['gradient']:.3f} "
          f"texture={fc_vals['texture']:.3f} clutter={fc_vals['clutter']:.3f}   "
          f"({time.time()-t0:.1f}s)")
    # the 2007 ordering claim: cluttered object field > texture > gradient > blank
    assert fc_vals["clutter"] > fc_vals["texture"] > fc_vals["blank"], fc_vals
    assert fc_vals["clutter"] > fc_vals["gradient"] > fc_vals["blank"], fc_vals
    print("FC ordering: clutter > {texture, gradient} > blank  OK")

    se_vals = {}
    for name, im in [("blank", blank), ("gradient", grad), ("texture", tex), ("clutter", clut)]:
        r = subband_entropy_faithful(im)
        se_vals[name] = r.extras["se_raw_nats"]
    print(f"SE nats: blank={se_vals['blank']:.3f} gradient={se_vals['gradient']:.3f} "
          f"texture={se_vals['texture']:.3f} clutter={se_vals['clutter']:.3f}")
    assert se_vals["clutter"] > se_vals["blank"] and se_vals["texture"] > se_vals["blank"], se_vals
    print("SE ordering: {clutter, texture} > blank  OK")

    # determinism x2
    a = feature_congestion_faithful(clut).extras["fc_raw"]
    b = feature_congestion_faithful(clut).extras["fc_raw"]
    assert a == b
    c = subband_entropy_faithful(clut).extras["se_raw_nats"]
    d = subband_entropy_faithful(clut).extras["se_raw_nats"]
    assert c == d
    print("determinism x2: FC + SE  OK")

    # real-interior smoke: cluttered industrial office vs minimal Farnsworth
    paths = {p.split("/")[-1][:10]: p for p in glob.glob("Example Images/*.*")}
    ind = cv2.imread("Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg")
    far = cv2.imread("Example Images/Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-1951_2.jpg")
    if ind is not None and far is not None:
        for im_ in ("ind", "far"):
            pass
        sc = 500 / max(ind.shape[:2]); ind = cv2.resize(ind, None, fx=sc, fy=sc)
        sc = 500 / max(far.shape[:2]); far = cv2.resize(far, None, fx=sc, fy=sc)
        t0 = time.time()
        fi = feature_congestion_faithful(ind).extras["fc_raw"]
        ff = feature_congestion_faithful(far).extras["fc_raw"]
        si = subband_entropy_faithful(ind).extras["se_raw_nats"]
        sf = subband_entropy_faithful(far).extras["se_raw_nats"]
        print(f"real interiors ({time.time()-t0:.1f}s): FC industrial={fi:.3f} vs farnsworth={ff:.3f}; "
              f"SE industrial={si:.3f} vs farnsworth={sf:.3f}")
        # DOMAIN-TRANSFER FINDING DT-1 (2026-07-19): the REFERENCE measure ranks minimal-but-
        # foliage-framed Farnsworth ABOVE the objectively cluttered industrial office on BOTH
        # FC and SE — vegetation's contrast/orientation/color variance reads as clutter. The
        # proto_object_count layer (clutter_stack) gets the human-intuitive ordering (269 vs
        # 143). This is the 2007 measure's maps/UI->interiors transfer problem demonstrated
        # with the authors' own algorithm; adjudication belongs to the labeled corpus (L6),
        # so NO ordering assert here — we record both directions and move on.
        print(f"DT-1 finding: reference FC/SE rank Farnsworth (foliage) above the cluttered "
              f"office — vegetation reads as clutter; corpus (L6) adjudicates. RECORDED")
    print("-" * 66 + "\nfaithful_clutter self-test: PASS")
