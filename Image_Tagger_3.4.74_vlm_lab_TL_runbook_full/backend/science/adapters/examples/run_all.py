#!/usr/bin/env python3
"""Run the adapters on one image and print the resulting cnfa.* attributes.

    python examples/run_all.py path/to/room.jpg
    python examples/run_all.py                 # uses a scikit-image sample

    # include the model-worker adapters (depth/seg/saliency), research policy:
    python examples/run_all.py room.jpg --policy research

Set AESTHETICS_TOOLBOX_PATH (or vendor the toolbox under third_party/) so the
Aesthetics-Toolbox adapter is active.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters import StandaloneFrame, run_frame, select_adapters  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", default=None)
    ap.add_argument("--policy", default="commercial", choices=["commercial", "research"])
    ap.add_argument("--workers", action="store_true", help="include model-worker adapters")
    args = ap.parse_args()

    if args.image:
        frame = StandaloneFrame.from_path(args.image)
    else:
        from skimage import data
        frame = StandaloneFrame(data.astronaut())

    adapters = select_adapters(policy=args.policy, include_workers=args.workers)
    print("Enabled adapters (%s policy): %s\n" % (
        args.policy, ", ".join(a.name for a in adapters)))
    run_frame(frame, adapters)

    out = {}
    for rec in sorted(frame.records(), key=lambda r: r.key):
        out[rec.key] = {"value": round(rec.value, 5) if isinstance(rec.value, float) else rec.value,
                        **{k: v for k, v in rec.meta.items() if k in ("units", "provenance", "confidence")}}
    print(json.dumps(out, indent=2))
    print("\n%d attributes emitted." % len(out))


if __name__ == "__main__":
    main()
