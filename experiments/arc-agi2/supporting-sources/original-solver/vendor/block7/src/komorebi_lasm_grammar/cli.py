"""Command-line entry points for Persistent Grammar Promotion."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .audit import main as audit_main
from .runtime import PersistentGrammarCompiler


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Komorebi PR-LASM Persistent Grammar Promotion")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="run the complete Block 7 audit")
    audit_parser.add_argument("--challenges", type=Path, required=True)
    audit_parser.add_argument("--solutions", type=Path, required=True)
    audit_parser.add_argument("--block6-submission", type=Path, required=True)
    audit_parser.add_argument("--block6-records", type=Path, required=True)
    audit_parser.add_argument("--output", type=Path, required=True)
    audit_parser.add_argument("--order-trials", type=int, default=64)
    audit_parser.add_argument("--partition-trials", type=int, default=32)

    compile_parser = subparsers.add_parser("compile", help="apply a frozen macro bank to one task")
    compile_parser.add_argument("--bank", type=Path, required=True)
    compile_parser.add_argument("--task", type=Path, required=True)
    compile_parser.add_argument("--output", type=Path)

    args = parser.parse_args(argv)
    if args.command == "audit":
        return audit_main([
            "--challenges", str(args.challenges),
            "--solutions", str(args.solutions),
            "--block6-submission", str(args.block6_submission),
            "--block6-records", str(args.block6_records),
            "--output", str(args.output),
            "--order-trials", str(args.order_trials),
            "--partition-trials", str(args.partition_trials),
        ])

    task = json.loads(args.task.read_text(encoding="utf-8"))
    decision = PersistentGrammarCompiler.from_json(args.bank).compile(task)
    payload = json.dumps(decision.to_record(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if decision.committed else 3


if __name__ == "__main__":
    raise SystemExit(main())
