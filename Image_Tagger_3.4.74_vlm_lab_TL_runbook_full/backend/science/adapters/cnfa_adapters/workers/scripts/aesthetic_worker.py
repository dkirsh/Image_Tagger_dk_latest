#!/usr/bin/env python3
"""Aesthetic/quality worker (isolated). Prints {"ok": true, "aesthetic":, "quality":}.

Backend: pyiqa (IQA-PyTorch). Run in a venv with torch + pyiqa:
    CNFA_IQA_PYTHON=/opt/venvs/iqa/bin/python
NIMA -> aesthetic (~1-10), MUSIQ -> quality. Reports ok:false if pyiqa absent.
Weights are research/non-commercial for several models — see adapter licence.
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
        import pyiqa
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        out = {"ok": True}
        try:
            nima = pyiqa.create_metric("nima", device=device)
            out["aesthetic"] = float(nima(args.image).item())
        except Exception:
            pass
        try:
            musiq = pyiqa.create_metric("musiq", device=device)
            out["quality"] = float(musiq(args.image).item())
        except Exception:
            pass
        if "aesthetic" not in out and "quality" not in out:
            out = {"ok": False, "error": "no IQA metric produced a score"}
        print(json.dumps(out))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": repr(exc)[:200]}))
    sys.exit(0)


if __name__ == "__main__":
    main()
