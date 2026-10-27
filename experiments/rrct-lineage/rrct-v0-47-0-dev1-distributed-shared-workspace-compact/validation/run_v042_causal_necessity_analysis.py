#!/usr/bin/env python3
"""Recompute the compact RRCT v0.42 causal-necessity adjudication."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rrct.causal_self_model_necessity_analysis import write_analysis_artifacts


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    default_root = (
        project_root
        / "validation"
        / "v0.42.0_causal_self_model_necessity"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=default_root / "input_summaries",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_root / "results",
    )
    args = parser.parse_args()
    hashes = write_analysis_artifacts(args.input, args.output)
    report = json.loads(
        (args.output / "causal_necessity_analysis.json").read_text(
            encoding="utf-8"
        )
    )
    print(report["status"])
    print(f"all_endpoints_met={report['all_endpoints_met']}")
    print(
        "primary_contrasts="
        f"{report['aggregate']['strict_primary_contrast_success_count']}/"
        f"{report['aggregate']['primary_contrast_count']}"
    )
    print(
        "fresh_sample_reduction="
        f"{100.0 * report['aggregate']['keyed_fresh_sample_reduction_fraction_vs_withheld']:.1f}%"
    )
    print(f"output={args.output.resolve()}")
    print(json.dumps(hashes, sort_keys=True))
    return 0 if report["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
