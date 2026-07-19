"""
cnfa_algs.clutter_stack — the post-2007 clutter layers (David's ask, 2026-07-19; grounded in
docs/PAPER_NOTE_ROSENHOLTZ_CLUTTER_2007_AND_AFTER_2026-07-19.md).

The 2014-2025 literature says clutter is not one number: pixel-statistics (FC/SE, already built as
AMBER proxies) sit UNDER a proto-object layer (numerosity of perceptual units — Yu, Samaras &
Zelinsky 2014, JoV: mean-shift superpixels + merging BEATS Feature Congestion on clutter judgments)
and an interpretable structural/chromatic pair (multi-scale gradient + multi-scale unique colors —
"Complexity in Complexity", arXiv:2501.15890, 2025: r~.84-.87 across 16 datasets). This module adds
those three layers as SEPARATE, honestly-named operators:

  C-CLUT-2a proto_object_count      — mean-shift segmentation (cv2.pyrMeanShiftFiltering, the same
                                      family as Yu et al.) -> quantize -> connected regions >= min
                                      area -> count + density + size-entropy. PROXY for the full
                                      parametric merging model; AMBER.
  C-CLUT-2b multiscale_gradient     — MSG-inspired: mean Sobel magnitude at scales 1,1/2,1/4,1/8.
                                      Named proxy of the 2025 paper's MSG (exact formula not yet
                                      ported); AMBER.
  C-CLUT-2c multiscale_unique_color — MUC-inspired: unique quantized colors at multiple spatial &
                                      color resolutions, normalized. Named proxy; AMBER.

DELIBERATELY NOT PROVIDED: a combined "clutter v2" scalar. The 2007 lesson (hand-fit global weights)
is not repeated — layer weights for INTERIORS await the labeled A/B corpus. Consumers get the layer
profile; fitting is a corpus-time act. The semantic-surprise layer (VLM-tier) is a Wave-3 candidate,
out of scope here.

Self-test: python3 -m cnfa_algs.clutter_stack
"""
from __future__ import annotations
import numpy as np
import cv2

try:
    from .attributes import AttributeResult, normalize01
except Exception:
    from attributes import AttributeResult, normalize01  # type: ignore

# ---- proto-object segmentation constants (declared; Yu et al. used adaptive versions) ----
MS_SPATIAL_R = 12       # mean-shift spatial window (px, on the <=900px working image)
MS_COLOR_R = 18         # mean-shift color window (in 8-bit color units)
QUANT_STEP = 24         # post-shift color quantization step (merges residual speckle)
MIN_REGION_FRAC = 0.0005  # regions smaller than this fraction of the image are noise, not objects
PROTO_FULLSCALE = 400   # declared full-scale count (real interiors 143-269, smoke 2026-07-19)

MSG_SCALES = (1.0, 0.5, 0.25, 0.125)
MUC_SPATIAL = (1.0, 0.25)        # full res + quarter res
MUC_BINS = (8, 16)               # color bins per channel
MUC_FULLSCALE = 0.60             # unique-color fraction full scale (real interiors 0.047-0.445)


# ================================================================ C-CLUT-2a proto-object count
def proto_object_count(img_bgr) -> AttributeResult:
    """Numerosity layer: mean-shift posterization -> quantize -> connected same-color regions
    above the noise floor. Emits count, density (per Mpx), and region-size entropy. The count is
    the construct the 2014 line found dominant; the size entropy separates 'many similar bits'
    from 'few big things + crumbs'."""
    if float(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).std()) < 2.0:
        return AttributeResult(key="cnfa.fluency.proto_object_count", scalar=None, confidence=0.0,
                               method="ABSTAIN: near-blank image (no segmentable structure)",
                               extras={"std_dn": round(float(cv2.cvtColor(
                                   img_bgr, cv2.COLOR_BGR2GRAY).std()), 3)},
                               failure_modes=["undefined on blank input"])
    ms = cv2.pyrMeanShiftFiltering(img_bgr, MS_SPATIAL_R, MS_COLOR_R)
    q = (ms // QUANT_STEP).astype(np.int32)
    key = q[..., 0] * 10000 + q[..., 1] * 100 + q[..., 2]     # one int per quantized color
    H, W = key.shape
    # connected components per color value: label the color-key image via cv2 on a per-value mask is
    # expensive; instead label the "color boundary" complement — regions = components of the map
    # where 4-neighbours share the same key.
    diff_r = np.zeros((H, W), np.uint8); diff_c = np.zeros((H, W), np.uint8)
    diff_r[1:, :] = (key[1:, :] != key[:-1, :]); diff_c[:, 1:] = (key[:, 1:] != key[:, :-1])
    boundary = (diff_r | diff_c).astype(np.uint8)
    n, lbl, stats, _ = cv2.connectedComponentsWithStats((1 - boundary).astype(np.uint8), connectivity=4)
    min_area = MIN_REGION_FRAC * H * W
    areas = stats[1:, cv2.CC_STAT_AREA].astype(float)
    keep = areas >= min_area
    count = int(keep.sum())
    if count == 0:
        return AttributeResult(key="cnfa.fluency.proto_object_count", scalar=0.0, confidence=0.55,
                               method="mean-shift proto-object count: no supra-noise regions (M1)",
                               extras={"n_regions_raw": int(n - 1), "min_area_px": round(min_area, 1)},
                               failure_modes=["segmentation-proxy (AMBER)"])
    p = areas[keep] / areas[keep].sum()
    size_entropy = float(-(p * np.log(p)).sum() / np.log(max(count, 2)))
    density_mpx = count / (H * W / 1e6)
    return AttributeResult(
        key="cnfa.fluency.proto_object_count",
        scalar=float(np.clip(count / PROTO_FULLSCALE, 0, 1)),
        field=None, confidence=0.55,
        method="mean-shift (Yu-et-al-family) segmentation -> supra-noise region COUNT (M1)",
        extras={"count": count, "density_per_mpx": round(density_mpx, 1),
                "size_entropy": round(size_entropy, 4), "n_regions_raw": int(n - 1),
                "constants": {"ms_spatial_r": MS_SPATIAL_R, "ms_color_r": MS_COLOR_R,
                              "quant_step": QUANT_STEP, "min_region_frac": MIN_REGION_FRAC,
                              "fullscale_count": PROTO_FULLSCALE}},
        failure_modes=["PROXY for Yu et al. 2014 parametric proto-object merging (AMBER)",
                       "mean-shift params are declared engineering constants pending corpus refit",
                       "texture/noise regions fall below the noise floor BY DESIGN — this counts "
                       "object-like units, not micro-texture (see texture_density for that)"])


# ================================================================ C-CLUT-2b multi-scale gradient
def multiscale_gradient(img_bgr) -> AttributeResult:
    """Structural layer (MSG-inspired, arXiv:2501.15890): mean Sobel magnitude averaged over
    4 dyadic scales. Multi-scale averaging is what lets it see BOTH fine busy-ness and large-scale
    structure — the property that beat plain Canny edge density on 5/16 datasets."""
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    if float(g.std()) < 2.0 / 255.0:
        return AttributeResult(key="cnfa.fluency.multiscale_gradient", scalar=None, confidence=0.0,
                               method="ABSTAIN: near-blank image",
                               extras={"std_dn": round(float(g.std()) * 255, 3)},
                               failure_modes=["undefined on blank input"])
    per_scale = []
    for s in MSG_SCALES:
        gs = g if s == 1.0 else cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        gx = cv2.Sobel(gs, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gs, cv2.CV_32F, 0, 1, ksize=3)
        per_scale.append(float(np.sqrt(gx * gx + gy * gy).mean()))
    msg = float(np.mean(per_scale))
    return AttributeResult(
        key="cnfa.fluency.multiscale_gradient",
        scalar=float(np.clip(msg / 0.80, 0, 1)),      # 0.80 = declared full scale (real interiors 0.23-0.51)
        confidence=0.7,
        method="MSG-inspired PROXY: mean Sobel magnitude over scales 1,1/2,1/4,1/8 (M1)",
        extras={"per_scale": [round(v, 5) for v in per_scale], "raw_mean": round(msg, 5),
                "scales": list(MSG_SCALES), "fullscale": 0.80},
        failure_modes=["named PROXY of the 2025 MSG (exact formula not yet ported) — AMBER",
                       "exposure/sharpening of source photo shifts magnitudes"])


# ================================================================ C-CLUT-2c multi-scale unique color
def multiscale_unique_color(img_bgr) -> AttributeResult:
    """Chromatic layer (MUC-inspired, arXiv:2501.15890): fraction of occupied color-quantization
    bins, averaged over spatial scales x color resolutions. Distinct from palette ENTROPY (which
    measures balance among 8 clusters): MUC measures VARIETY — how much of color space is used."""
    a = np.asarray(img_bgr)
    vals = []
    for s in MUC_SPATIAL:
        im = a if s == 1.0 else cv2.resize(a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        for b in MUC_BINS:
            qq = (im.astype(np.int32) * b) // 256
            key = (qq[..., 0] * b + qq[..., 1]) * b + qq[..., 2]
            vals.append(len(np.unique(key)) / float(b ** 3))
    muc = float(np.mean(vals))
    return AttributeResult(
        key="cnfa.fluency.multiscale_unique_color",
        scalar=float(np.clip(muc / MUC_FULLSCALE, 0, 1)),
        confidence=0.7,
        method="MUC-inspired PROXY: occupied color-bin fraction over spatial x color scales (M1)",
        extras={"per_config": [round(v, 5) for v in vals],
                "spatial_scales": list(MUC_SPATIAL), "bins": list(MUC_BINS),
                "raw_mean": round(muc, 6), "fullscale": MUC_FULLSCALE},
        failure_modes=["named PROXY of the 2025 MUC (exact formula not yet ported) — AMBER",
                       "white-balance/JPEG chroma subsampling shift bin occupancy"])


ALL_CLUTTER_STACK = {
    "cnfa.fluency.proto_object_count": proto_object_count,
    "cnfa.fluency.multiscale_gradient": multiscale_gradient,
    "cnfa.fluency.multiscale_unique_color": multiscale_unique_color,
}


def clutter_profile(img_bgr) -> dict:
    """Convenience: the FULL clutter profile — the three new layers + the two 2007-family proxies
    already registered (FC-proxy, SE-proxy via their modules). NO combined scalar: layer weights
    for interiors are a corpus-time fit (the 2007 hand-fit-weights lesson, not repeated)."""
    from . import reliable_attrs as RA
    from . import attributes as A
    out = {}
    for k, fn in ALL_CLUTTER_STACK.items():
        r = fn(img_bgr)
        out[k] = None if r.scalar is None else round(r.scalar, 4)
    out["cnfa.fluency.local_congestion_proxy(FC-proxy)"] = round(
        RA.feature_congestion_clutter(img_bgr).scalar, 4)
    out["cnfa.fluency.grayscale_gabor_entropy_proxy(SE-proxy)"] = round(
        RA.subband_entropy_clutter(img_bgr).scalar, 4)
    out["cnfa.fluency.processing_load_proxy(legacy)"] = round(
        A.processing_load(img_bgr).scalar, 4)
    out["_note"] = "layer profile only; combined scalar awaits corpus-fitted weights"
    return out


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("clutter_stack self-test\n" + "-" * 56)
    H, W = 240, 320
    mk = lambda f: np.clip(f, 0, 255).astype(np.uint8)
    rng = np.random.RandomState(0)
    flat = mk(np.full((H, W, 3), 128.0))

    # C-CLUT-2a: 3 blobs < 24 blobs; blank abstains; noise stays LOW (not objects)
    def blob_img(nb):
        im = np.full((H, W, 3), 230.0)
        rs = np.random.RandomState(7)
        for i in range(nb):
            x, y = int(rs.rand() * (W - 40)) + 20, int(rs.rand() * (H - 40)) + 20
            col = tuple(int(c) for c in rs.randint(0, 200, 3))
            cv2.circle(im, (x, y), 12, col, -1)
        return mk(im)
    p3 = proto_object_count(blob_img(3))
    p24 = proto_object_count(blob_img(24))
    pb = proto_object_count(flat)
    pn = proto_object_count(mk(np.stack([128 + 60 * rng.randn(H, W)] * 3, -1)))
    assert pb.scalar is None and p24.extras["count"] > p3.extras["count"] >= 3
    assert pn.extras["count"] < p24.extras["count"], "noise must not read as many objects"
    print(f"2a proto-objects: 3-blob={p3.extras['count']} < 24-blob={p24.extras['count']}; "
          f"blank->abstain; noise count={pn.extras['count']} (low)  OK")

    # C-CLUT-2b: blank abstain < gradient < checkerboard
    grad = mk(np.stack([40 + 170 * np.mgrid[0:H, 0:W][1] / W] * 3, -1))
    check = mk(np.stack([255.0 * ((np.mgrid[0:H, 0:W][0] // 8 + np.mgrid[0:H, 0:W][1] // 8) % 2)] * 3, -1))
    mg, mc = multiscale_gradient(grad), multiscale_gradient(check)
    assert multiscale_gradient(flat).scalar is None and mc.scalar > mg.scalar
    print(f"2b MSG: checker {mc.scalar:.3f} > gradient {mg.scalar:.3f}; blank->abstain  OK")

    # C-CLUT-2c: 1 color < 4 colors < many colors
    four = np.zeros((H, W, 3)); four[:H//2, :W//2] = [200, 30, 30]; four[:H//2, W//2:] = [30, 200, 30]
    four[H//2:, :W//2] = [30, 30, 200]; four[H//2:, W//2:] = [200, 200, 30]
    many = mk(rng.randint(0, 255, (H, W, 3)).astype(float))
    u1, u4, um = multiscale_unique_color(flat), multiscale_unique_color(mk(four)), multiscale_unique_color(many)
    assert u1.scalar < u4.scalar < um.scalar
    print(f"2c MUC: 1-color {u1.scalar:.3f} < 4-color {u4.scalar:.3f} < noise {um.scalar:.3f}  OK")

    # determinism x2
    for k, fn in ALL_CLUTTER_STACK.items():
        a, b = fn(blob_img(10)), fn(blob_img(10))
        assert (a.scalar is None and b.scalar is None) or a.scalar == b.scalar, k
    print("determinism x2: all 3 layers  OK")
    print("-" * 56 + "\nclutter_stack self-test: PASS")
