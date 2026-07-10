#!/usr/bin/env python3
"""MiDaS depth worker (isolated). Prints one JSON line of depth statistics.

Run in a venv that has torch + timm installed:
    CNFA_MIDAS_PYTHON=/opt/venvs/midas/bin/python
    python midas_worker.py --image room.jpg

Emits: near_fraction, far_fraction, vertical_gradient, gradient_magnitude.
If torch/MiDaS is not installed, prints {"ok": false, "error": ...} and exits 0
so the adapter degrades quietly. MiDaS is MIT-licensed.
"""
import argparse
import json
import sys


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--params", default=None)
    args = ap.parse_args()

    try:
        import numpy as np
        import torch
        from PIL import Image

        model_type = "DPT_Large"
        midas = torch.hub.load("intel-isl/MiDaS", model_type)
        transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        transform = transforms.dpt_transform
        device = "cuda" if torch.cuda.is_available() else "cpu"
        midas.to(device).eval()

        img = np.asarray(Image.open(args.image).convert("RGB"))
        batch = transform(img).to(device)
        with torch.no_grad():
            pred = midas(batch)
            pred = torch.nn.functional.interpolate(
                pred.unsqueeze(1), size=img.shape[:2],
                mode="bicubic", align_corners=False,
            ).squeeze()
        depth = pred.cpu().numpy().astype("float64")
        # MiDaS returns inverse depth: large = near. Normalise to [0,1].
        d = (depth - depth.min()) / (np.ptp(depth) + 1e-9)
        near_fraction = float((d > 0.75).mean())
        far_fraction = float((d < 0.25).mean())
        rows = d.mean(axis=1)
        vertical_gradient = float(rows[: len(rows) // 3].mean() - rows[-len(rows) // 3:].mean())
        gy, gx = np.gradient(d)
        gradient_magnitude = float(np.sqrt(gx ** 2 + gy ** 2).mean())

        print(json.dumps({
            "ok": True,
            "near_fraction": near_fraction,
            "far_fraction": far_fraction,
            "vertical_gradient": vertical_gradient,
            "gradient_magnitude": gradient_magnitude,
        }))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": repr(exc)[:200]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
