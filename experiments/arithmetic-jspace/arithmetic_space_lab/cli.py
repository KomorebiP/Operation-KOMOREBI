from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .audit import AuditFailure, audit_dataset
from .config import load_config
from .generate import generate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arithmetic-space-lab",
        description="Generate and validate deterministic exact-arithmetic training corpora.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="generate a corpus")
    generate_parser.add_argument("--config", required=True, help="path to a JSON configuration")
    generate_parser.add_argument("--output", required=True, help="new output directory")
    generate_parser.add_argument("--seed", type=int, help="override the configured seed")
    generate_parser.add_argument("--train", type=int, help="override the train count")
    generate_parser.add_argument("--validation", type=int, help="override the validation count")
    generate_parser.add_argument("--test-iid", type=int, help="override the IID test count")
    generate_parser.add_argument("--overwrite", action="store_true", help="replace an existing output directory")

    audit_parser = subparsers.add_parser("audit", help="audit a generated corpus")
    audit_parser.add_argument("--data", required=True, help="generated corpus directory")
    audit_parser.add_argument("--no-report", action="store_true", help="do not write audit_report.json")
    return parser


def _print_generation(manifest: dict) -> None:
    print("ARITHMETIC_GENERATION=PASS")
    print(f"DATASET={manifest['dataset_name']}")
    print(f"RECORDS={manifest['unique_samples']}")
    print(f"UNIQUE_FAMILIES={manifest['unique_families']}")
    print(f"COUNTS={json.dumps(manifest['actual_counts'], sort_keys=True)}")
    print(f"OPERATIONS={json.dumps(manifest['statistics']['operation'], sort_keys=True)}")
    print(f"RECORDS_PER_SECOND={manifest['records_per_second']}")


def _print_audit(report: dict) -> None:
    print(f"ARITHMETIC_AUDIT={report['status']}")
    print(f"CANONICAL_RECORDS={report['canonical_records']}")
    print(f"UNIQUE_FAMILIES={report['unique_families']}")
    print(f"FAMILY_SPLIT_LEAKAGE={report['family_split_leakage']}")
    print(f"ATOMIC_RELATION_SPLIT_LEAKAGE={report['atomic_relation_split_leakage']}")
    print(f"COUNTS={json.dumps(report['counts'], sort_keys=True)}")
    print(f"REGIMES={json.dumps(report['regime_counts'], sort_keys=True)}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "generate":
            config = load_config(args.config)
            if args.seed is not None:
                config["seed"] = args.seed
            overrides = {"train": args.train, "validation": args.validation, "test_iid": args.test_iid}
            for split, value in overrides.items():
                if value is not None:
                    if value < 0:
                        raise ValueError(f"{split} count cannot be negative")
                    config["counts"][split] = value
            manifest = generate(config, Path(args.output), overwrite=args.overwrite)
            _print_generation(manifest)
            return 0
        report = audit_dataset(args.data, write_report=not args.no_report)
        _print_audit(report)
        return 0
    except (AuditFailure, FileExistsError, OSError, RuntimeError, ValueError) as error:
        print(f"ARITHMETIC_LAB=FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
