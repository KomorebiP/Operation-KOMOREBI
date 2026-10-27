"""Command-line interface for the OSL Discovery Bridge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .adapter import emit_osl
from .core import synthesize, verify_certificate
from .registry import append_admission, verify_registry
from .worlds import canonical_json


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path: str, value: Any) -> None:
    Path(path).write_text(canonical_json(value) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="osl-discovery")
    commands = parser.add_subparsers(dest="command", required=True)
    synth = commands.add_parser("synthesize")
    synth.add_argument("proposal")
    synth.add_argument("output")
    verify = commands.add_parser("verify")
    verify.add_argument("proposal")
    verify.add_argument("certificate")
    register = commands.add_parser("register")
    register.add_argument("certificate")
    register.add_argument("registry")
    verify_reg = commands.add_parser("verify-registry")
    verify_reg.add_argument("registry")
    verify_reg.add_argument("--expected-tip")
    render = commands.add_parser("emit-osl")
    render.add_argument("proposal")
    render.add_argument("certificate")
    render.add_argument("output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "synthesize":
        certificate = synthesize(_load(args.proposal))
        _write(args.output, certificate)
        print(canonical_json({"status": certificate["status"], "certificate_digest": certificate["certificate_digest"]}))
        return 0
    if args.command == "verify":
        report = verify_certificate(_load(args.proposal), _load(args.certificate))
        print(canonical_json(report))
        return 0 if report["valid"] else 1
    if args.command == "register":
        entry = append_admission(args.registry, _load(args.certificate))
        print(canonical_json(entry))
        return 0
    if args.command == "verify-registry":
        report = verify_registry(args.registry, expected_tip=args.expected_tip)
        print(canonical_json(report))
        return 0 if report["valid"] else 1
    proposal = _load(args.proposal)
    certificate = _load(args.certificate)
    Path(args.output).write_text(emit_osl(proposal, certificate), encoding="utf-8", newline="\n")
    print(canonical_json({"output": args.output, "decision": certificate["decision"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
