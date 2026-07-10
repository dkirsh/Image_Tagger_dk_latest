#!/usr/bin/env python3
"""Memorability worker (isolated). Prints {"ok": true, "memorability": 0-1}.

Backends (non-commercial weights): ResMem (`pip install resmem`) or ViTMem
(`pip install vitmem`). Run in a venv with torch + the chosen package:
    CNFA_MEM_PYTHON=/opt/venvs/mem/bin/python
Reports ok:false if neither is installed (adapter then emits nothing).
"""
import argparse
import json
import sys


def resmem_score(path):
    from resmem import ResMem, transformer
    from PIL import Image

    model = ResMem(pretrained=True).eval()
    img = Image.open(path).convert("RGB")
    x = transformer(img).view(-1, 3, 227, 227)
    import torch
    with torch.no_grad():
        return float(model(x).item()), "resmem"


def vitmem_score(path):
    from vitmem import ViTMem
    from PIL import Image

    model = ViTMem()
    return float(model(Image.open(path).convert("RGB"))), "vitmem"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--params", default=None)
    args = ap.parse_args()
    for fn in (resmem_score, vitmem_score):
        try:
            score, source = fn(args.image)
            print(json.dumps({"ok": True, "memorability": score, "source": source}))
            sys.exit(0)
        except Exception:
            continue
    print(json.dumps({"ok": False, "error": "no memorability backend installed"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
