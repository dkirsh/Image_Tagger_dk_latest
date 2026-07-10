#!/usr/bin/env python3
"""Run the cognitive-code adapters on one image against a REAL AnalysisFrame,
without the database pipeline. The fastest way to test the bank in-repo.

    cd Image_Tagger_3.4.74_vlm_lab_TL_runbook_full
    python backend/science/adapters/run_cnfa_standalone.py path/to/room.jpg
    python backend/science/adapters/run_cnfa_standalone.py --policy research --workers
"""
import argparse
import json
import os
import sys

# repo root that contains the `backend` package (three levels up from here)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", default=None)
    ap.add_argument("--policy", default="commercial", choices=["commercial", "research"])
    ap.add_argument("--workers", action="store_true", help="include model-worker adapters")
    args = ap.parse_args()

    from backend.science.core import AnalysisFrame
    from backend.science.adapters.cnfa_bridge import CNFAAdapters

    if args.image:
        rgb = np.asarray(Image.open(args.image).convert("RGB"))
    else:
        from skimage import data
        rgb = data.astronaut()

    frame = AnalysisFrame(image_id=0, original_image=rgb)
    bridge = CNFAAdapters(policy=args.policy, include_workers=args.workers)
    print("adapters:", ", ".join(a.name for a in bridge.adapters))
    bridge.analyze(frame)

    out = {k: (round(v, 5) if isinstance(v, float) else v)
           for k, v in sorted(frame.attributes.items())}
    print(json.dumps(out, indent=2))
    print(f"\n{len(frame.attributes)} cnfa attributes written to frame.attributes.")


if __name__ == "__main__":
    main()
