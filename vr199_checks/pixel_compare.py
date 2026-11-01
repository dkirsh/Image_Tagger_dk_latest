#!/usr/bin/env python3
"""pixel_compare.py — compare one surface's colour between two renders of the same view (condition A vs B).

For each region it reports the median colour as sRGB and as CIE Lab (D65), the CIE xy chromaticity of the median
linear colour (which, unlike Lab chroma, does not move when only the amount of light changes), the local texture
contrast, and the B-minus-A differences. It then classifies the pair as one of:

  no_measurable_difference   |dL*| < 1 and chromaticity shift < 0.002 and texture contrast within 10%, every region
  chroma_differs             chromaticity shift >= 0.004 in any region: the surface colour (material) or the light's
                             colour changed, not just the amount of light
  texture_differs            texture contrast changes by more than 25% in a region whose chromaticity is stable
  lighting_only              chromaticity stable in every region, lightness differs: same material, different light
  ambiguous                  anything between those thresholds

Regions are pixel sets on a common mask (pixels that are the surface in BOTH renders): "lit" and "shadow" are the
top and bottom deciles of A's luminance inside the mask, used unchanged in B; any --patch x0,y0,x1,y1[:name] adds a
fixed rectangle (intersected with the mask).

    python3 vr199_checks/pixel_compare.py A.png B.png --seg-a A_seg.png --seg-b B_seg.png --seg-rgb 255,0,0 \
        [--clip x0,y0,x1,y1] [--patch x0,y0,x1,y1:name ...] [--json out.json]

Pure numpy + Pillow. Thresholds are stated constants, not tuned to any one pair. It reads two images and,
optionally, their flat-colour segmentation frames; producing those renders is outside this module.

Lane: Image_Tagger_dk_latest (tanishq). Never imports New_VR_Platform code.

Limit: chromaticity separates material from lighting cleanly only where one light colour dominates. Where two
lights of different colour mix (a warm downlight on a neutral ambient), changing their ratio moves chromaticity
on an unchanged surface, so a "chroma_differs" there should be confirmed against the scene's material ids.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from PIL import Image

NONE_DL, NONE_DXY, NONE_TEX = 1.0, 0.002, 0.10
CHROMA_DXY, TEX_RATIO = 0.004, 0.25

_M = np.array([[0.4124564, 0.3575761, 0.1804375],      # linear sRGB -> XYZ (D65)
               [0.2126729, 0.7151522, 0.0721750],
               [0.0193339, 0.1191920, 0.9503041]])
_WHITE = np.array([0.95047, 1.0, 1.08883])


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_lab(lin: np.ndarray) -> np.ndarray:
    xyz = lin @ _M.T / _WHITE
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def chromaticity_xy(lin: np.ndarray) -> np.ndarray:
    xyz = lin @ _M.T
    s = xyz.sum(axis=-1, keepdims=True)
    return (xyz / np.where(s == 0, 1, s))[..., :2]


def load_rgb(path: str) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float64)


def seg_mask(seg: np.ndarray, rgb: tuple[int, int, int], tol: int = 8) -> np.ndarray:
    return np.all(np.abs(seg - np.array(rgb, dtype=np.float64)) <= tol, axis=-1)


def region_stats(img: np.ndarray, sel: np.ndarray) -> dict:
    px = img[sel]
    lin = srgb_to_linear(px)
    lab = linear_to_lab(lin)
    med_rgb = np.median(px, axis=0)
    med_lin = np.median(lin, axis=0)
    med_lab = np.median(lab, axis=0)
    return {"n": int(sel.sum()), "rgb": [round(float(v), 2) for v in med_rgb],
            "lab": [round(float(v), 3) for v in med_lab],
            "chroma": round(float(np.hypot(med_lab[1], med_lab[2])), 3),
            "xy": [round(float(v), 5) for v in chromaticity_xy(med_lin)],
            "texture_L_iqr": round(float(np.subtract(*np.percentile(lab[:, 0], [75, 25]))), 3)}


def compare(a: np.ndarray, b: np.ndarray, mask: np.ndarray, patches: dict[str, tuple[int, int, int, int]] | None = None) -> dict:
    if a.shape != b.shape or a.shape[:2] != mask.shape:
        raise ValueError("A, B and the mask must have the same size")
    if mask.sum() < 50:
        raise ValueError(f"mask holds only {int(mask.sum())} pixels")
    lum = (srgb_to_linear(a) @ _M[1])
    lo, hi = np.percentile(lum[mask], [10, 90])
    regions = {"lit": mask & (lum >= hi), "shadow": mask & (lum <= lo)}
    for name, (x0, y0, x1, y1) in (patches or {}).items():
        r = np.zeros_like(mask)
        r[y0:y1, x0:x1] = True
        regions[name] = mask & r
    out = {}
    for name, sel in regions.items():
        if sel.sum() < 20:
            out[name] = {"skipped": f"{int(sel.sum())} pixels"}
            continue
        sa, sb = region_stats(a, sel), region_stats(b, sel)
        d = {"dL": round(sb["lab"][0] - sa["lab"][0], 3), "da": round(sb["lab"][1] - sa["lab"][1], 3),
             "db": round(sb["lab"][2] - sa["lab"][2], 3), "dChroma": round(sb["chroma"] - sa["chroma"], 3),
             "dRGB": [round(y - x, 2) for x, y in zip(sa["rgb"], sb["rgb"])],
             "dxy": round(float(np.hypot(sb["xy"][0] - sa["xy"][0], sb["xy"][1] - sa["xy"][1])), 5),
             "texture_ratio": round(sb["texture_L_iqr"] / sa["texture_L_iqr"], 3) if sa["texture_L_iqr"] > 0 else None}
        d["dE76"] = round(float(np.sqrt(d["dL"] ** 2 + d["da"] ** 2 + d["db"] ** 2)), 3)
        out[name] = {"kind": "decile" if name in ("lit", "shadow") else "patch", "A": sa, "B": sb, "B_minus_A": d}
    basis = "patches" if any(r.get("kind") == "patch" and "B_minus_A" in r for r in out.values()) else "deciles"
    return {"regions": out, "verdict": classify(out), "verdict_basis": basis}


def classify(regions: dict) -> str:
    """Decide on fixed patches when any are given. Decile regions are chosen by A's luminance, so when the light
    pattern moves between A and B they sample a different mix of light sources in B (shifting chromaticity without
    any material change), and their texture spread is biased by the selection itself; they then stay descriptive."""
    use = [r for r in regions.values() if r.get("kind") == "patch" and "B_minus_A" in r] or \
          [r for r in regions.values() if "B_minus_A" in r]
    ds = [r["B_minus_A"] for r in use]
    if not ds:
        return "ambiguous"
    tex = [abs(d["texture_ratio"] - 1) for d in ds if d["texture_ratio"] is not None]
    if all(abs(d["dL"]) < NONE_DL and d["dxy"] < NONE_DXY for d in ds) and all(t <= NONE_TEX for t in tex):
        return "no_measurable_difference"
    if any(d["dxy"] >= CHROMA_DXY for d in ds):
        return "chroma_differs"
    if any(t > TEX_RATIO for t in tex):
        return "texture_differs"
    if all(d["dxy"] < NONE_DXY for d in ds):
        return "lighting_only"
    return "ambiguous"


def _rect(s: str) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = (int(v) for v in s.split(","))
    return x0, y0, x1, y1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--seg-a"); ap.add_argument("--seg-b")
    ap.add_argument("--seg-rgb", default="255,0,0")
    ap.add_argument("--clip", type=_rect, help="keep only this rectangle of the mask")
    ap.add_argument("--patch", action="append", default=[], help="x0,y0,x1,y1:name")
    ap.add_argument("--json")
    a_ = ap.parse_args(argv)
    A, B = load_rgb(a_.a), load_rgb(a_.b)
    mask = np.ones(A.shape[:2], bool)
    rgb = tuple(int(v) for v in a_.seg_rgb.split(","))
    for s in (a_.seg_a, a_.seg_b):
        if s:
            mask &= seg_mask(load_rgb(s), rgb)
    if a_.clip:
        x0, y0, x1, y1 = a_.clip
        c = np.zeros_like(mask); c[y0:y1, x0:x1] = True; mask &= c
    patches = {}
    for p in a_.patch:
        r, _, name = p.partition(":")
        patches[name or r] = _rect(r)
    res = compare(A, B, mask, patches)
    res["mask_pixels"] = int(mask.sum())
    text = json.dumps(res, indent=1)
    if a_.json:
        open(a_.json, "w").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
