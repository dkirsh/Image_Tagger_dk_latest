#!/usr/bin/env python3
"""Material-from-image worker (isolated).
Prints {"ok": true, "gloss":, "albedo":, "metallic":}.

Backends (research / academic-use): perceived-gloss (Guerrero-Viu 2024),
Intrinsic Image Diffusion (Kocsis 2024), or compphoto/Intrinsic (Careaga).
Run in a venv with torch + the chosen model:
    CNFA_MATERIAL_PYTHON=/opt/venvs/material/bin/python

This is a research scaffold: wire the chosen model in `run_model`. If no model
is present it reports ok:false (the adapter then emits nothing). For a
commercial build, use the permissive Motoyoshi luminance/sub-band-skew gloss
cue in ProximalStatsAdapter instead of this worker.
"""
import argparse
import json
import sys


def run_model(image_path):
    """TODO: load a perceived-gloss / intrinsic-decomposition model and return
    a dict with any of {gloss, albedo, metallic} in [0, 1]."""
    raise NotImplementedError("wire a material-from-image model here")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--params", default=None)
    args = ap.parse_args()
    try:
        result = run_model(args.image)
        result["ok"] = True
        print(json.dumps(result))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": repr(exc)[:200]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
