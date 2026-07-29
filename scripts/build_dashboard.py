#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from complaint_ops.config import load_config
from complaint_ops.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the CFPB complaint operations data products."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config" / "pipeline.json",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Optional local CFPB-format CSV for offline or test builds.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_pipeline(load_config(args.config), source=args.source)
    receipt = {
        "row_count": result["manifest"]["row_count"],
        "quality_status": result["manifest"]["quality_status"],
        "source_sha256": result["manifest"]["sanitized_csv_sha256"],
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

