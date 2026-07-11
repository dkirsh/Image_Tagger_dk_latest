#!/usr/bin/env python3
"""Command-line interface for low-level image feature extraction.

Usage:
    # Single image (whole-image features):
    python -m science.low_level.cli --image path/to/image.jpg

    # Single image with regional features (mock segmentation):
    python -m science.low_level.cli --image path/to/image.jpg --regional --mock

    # Single image with regional features (real SegFormer):
    python -m science.low_level.cli --image path/to/image.jpg --regional

    # Batch directory:
    python -m science.low_level.cli --dir stimuli/ --output features.csv

    # Batch with regional features:
    python -m science.low_level.cli --dir stimuli/ --regional --mock -o regional_features.csv

    # JSON output for single image:
    python -m science.low_level.cli --image photo.jpg --format json --regional
"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract low-level image features (MPIB + MATLAB-ported)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", type=str, help="Path to a single image file")
    group.add_argument("--dir", type=str, help="Path to directory of images")

    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output file path (CSV or XLSX). Defaults to stdout for single image.",
    )
    parser.add_argument(
        "--format", choices=["csv", "json", "xlsx"], default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--extensions", type=str, default=".jpg,.jpeg,.png,.bmp,.tiff",
        help="Comma-separated image extensions (default: .jpg,.jpeg,.png,.bmp,.tiff)",
    )
    parser.add_argument(
        "--regional", action="store_true",
        help="Enable per-region feature extraction (requires segmentation)",
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="Use mock segmentation (geometric approximation, no GPU needed)",
    )
    parser.add_argument(
        "--min-coverage", type=float, default=0.01,
        help="Minimum region coverage to extract features (default: 0.01 = 1%%)",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    if args.regional:
        _run_regional(args)
    else:
        _run_whole_image(args)


def _run_whole_image(args) -> None:
    """Whole-image feature extraction (original 61 features)."""
    from .unified import extract_all_features, LowLevelFeatureExtractor

    if args.image:
        path = Path(args.image)
        if not path.exists():
            log.error("Image not found: %s", path)
            sys.exit(1)

        t0 = time.perf_counter()
        features = extract_all_features(str(path))
        elapsed = time.perf_counter() - t0
        log.info("Extracted %d features in %.2fs", len(features), elapsed)

        if args.format == "json":
            output = json.dumps(
                {"image": path.name, "features": features, "elapsed_seconds": round(elapsed, 3)},
                indent=2,
                default=str,
            )
            if args.output:
                Path(args.output).write_text(output)
                log.info("Written to %s", args.output)
            else:
                print(output)
        else:
            df = pd.DataFrame([{"image": path.name, **features}])
            if args.output:
                if args.format == "xlsx":
                    df.to_excel(args.output, index=False)
                else:
                    df.to_csv(args.output, index=False)
                log.info("Written to %s", args.output)
            else:
                print(df.to_csv(index=False))

    else:
        extractor = LowLevelFeatureExtractor()
        extensions = tuple(e.strip() for e in args.extensions.split(","))
        output_path = args.output or "low_level_features.csv"

        df = extractor.process_directory(
            args.dir,
            output_csv=output_path if args.format != "json" else None,
            extensions=extensions,
        )

        if args.format == "json":
            records = df.to_dict(orient="records")
            output = json.dumps(records, indent=2, default=str)
            if args.output:
                Path(args.output).write_text(output)
            else:
                print(output)
        elif args.format == "xlsx" and args.output:
            df.to_excel(args.output, index=False)

        log.info("Processed %d images → %s", len(df), output_path)


def _run_regional(args) -> None:
    """Per-region feature extraction (61 × N_regions + contrasts)."""
    from .regional import RegionalFeatureExtractor

    rfe = RegionalFeatureExtractor(
        use_mock=args.mock,
        min_coverage=args.min_coverage,
    )

    if args.image:
        path = Path(args.image)
        if not path.exists():
            log.error("Image not found: %s", path)
            sys.exit(1)

        result = rfe.analyze(str(path))

        if args.format == "json":
            output = json.dumps(
                {
                    "image": path.name,
                    "whole_image": result.whole_image,
                    "regions": result.regions,
                    "contrasts": result.contrasts,
                },
                indent=2,
                default=str,
            )
            if args.output:
                Path(args.output).write_text(output)
                log.info("Written to %s", args.output)
            else:
                print(output)
        else:
            flat = result.to_flat_dict()
            df = pd.DataFrame([{"image": path.name, **flat}])
            if args.output:
                if args.format == "xlsx":
                    df.to_excel(args.output, index=False)
                else:
                    df.to_csv(args.output, index=False)
                log.info("Written to %s", args.output)
            else:
                print(result.summary())

    else:
        extensions = tuple(e.strip() for e in args.extensions.split(","))
        output_path = args.output or "regional_features.csv"

        df = rfe.process_directory(
            args.dir,
            output_csv=output_path if args.format != "json" else None,
            extensions=extensions,
        )

        if args.format == "json":
            records = df.to_dict(orient="records")
            output = json.dumps(records, indent=2, default=str)
            if args.output:
                Path(args.output).write_text(output)
            else:
                print(output)
        elif args.format == "xlsx" and args.output:
            df.to_excel(args.output, index=False)

        log.info("Processed %d images → %s", len(df), output_path)


if __name__ == "__main__":
    main()
