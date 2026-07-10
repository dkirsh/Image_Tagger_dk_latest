#!/usr/bin/env python3
"""Segmentation worker (isolated). Prints one JSON line of class-area fractions.

Preferred backend: OneFormer/Mask2Former with ADE20K labels (per-pixel class),
or SAM for class-agnostic regions + a classifier. Run in a venv with torch +
transformers:
    CNFA_SEG_PYTHON=/opt/venvs/seg/bin/python

Emits: {"ok": true, "class_fractions": {"tree": 0.12, ...}, "region_count": N}.

This scaffold includes a **naive HSV-greenery fallback** so the pipeline returns
a demonstrable greenery signal before the real segmentation model is wired in.
The fallback is clearly marked and low-confidence; replace `run_ade20k` with the
real OneFormer inference for production.
"""
import argparse
import json
import sys


def run_ade20k(image_path):
    """Real path — OneFormer/Mask2Former ADE20K semantic segmentation.

    TODO: load OneFormerProcessor + OneFormerForUniversalSegmentation (or
    Mask2Former), run post_process_semantic_segmentation, and compute per-class
    pixel fractions against the ADE20K label map. Returns (class_fractions,
    region_count) or raises if the model stack is unavailable.
    """
    raise NotImplementedError("wire OneFormer/Mask2Former ADE20K here")


def naive_greenery_fallback(image_path):
    """Placeholder: approximate greenery via an HSV green mask. NOT a substitute
    for semantic segmentation — greenery only, low confidence."""
    import numpy as np
    from PIL import Image

    rgb = np.asarray(Image.open(image_path).convert("RGB")).astype("float32") / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # Green-dominant, reasonably saturated pixels.
    green_mask = (g > r * 1.05) & (g > b * 1.05) & (g > 0.15)
    green_fraction = float(green_mask.mean())
    return {"grass": green_fraction}, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--params", default=None)
    args = ap.parse_args()
    try:
        try:
            class_fractions, region_count = run_ade20k(args.image)
            source = "ade20k"
        except Exception:
            class_fractions, region_count = naive_greenery_fallback(args.image)
            source = "naive_hsv_fallback"
        print(json.dumps({
            "ok": True,
            "source": source,
            "class_fractions": class_fractions,
            "region_count": region_count,
        }))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": repr(exc)[:200]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
