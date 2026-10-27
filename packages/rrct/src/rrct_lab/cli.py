from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

from .config import load_config, validate_config
from .contracts import audit_config, enforce_contract
from .dependencies import doctor
from .features import feature_rows
from .freeze import audit_run, create_freeze, run_frozen, verify_freeze
from .registry import list_experiments
from .runner import project_root, run_config
from .sweep import run_sweep
from .verify import verify_manifest, verify_vendor


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="rrct-lab")
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("list")
    sub.add_parser("features")
    validate = sub.add_parser("validate")
    validate.add_argument("config", type=pathlib.Path)
    validate.add_argument("--set", action="append", default=[])
    contract = sub.add_parser("contract")
    contract.add_argument("config", type=pathlib.Path)
    contract.add_argument("--set", action="append", default=[])
    run = sub.add_parser("run")
    run.add_argument("config", type=pathlib.Path)
    run.add_argument("--set", action="append", default=[])
    resume = sub.add_parser("resume")
    resume.add_argument("run_directory", type=pathlib.Path)
    sweep = sub.add_parser("sweep")
    sweep.add_argument("config", type=pathlib.Path)
    sweep.add_argument("--set", action="append", default=[])
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--config", type=pathlib.Path, default=None)
    smoke.add_argument("--set", action="append", default=[])
    freeze = sub.add_parser("freeze")
    freeze.add_argument("config", type=pathlib.Path)
    freeze.add_argument("--output", type=pathlib.Path, required=True)
    freeze.add_argument("--set", action="append", default=[])
    holdout = sub.add_parser("holdout")
    holdout.add_argument("freeze", type=pathlib.Path)
    verify_freeze_cmd = sub.add_parser("verify-freeze")
    verify_freeze_cmd.add_argument("freeze", type=pathlib.Path)
    audit = sub.add_parser("audit")
    audit.add_argument("run_directory", type=pathlib.Path)
    sub.add_parser("verify")
    legacy = sub.add_parser("legacy")
    legacy_sub = legacy.add_subparsers(dest="legacy_command", required=True)
    legacy_sub.add_parser("list")
    extract = legacy_sub.add_parser("extract")
    extract.add_argument("version")
    extract.add_argument("destination", type=pathlib.Path)
    return root


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = project_root()
    if args.command == "doctor":
        _print(doctor())
        return 0
    if args.command == "list":
        _print(list_experiments())
        return 0
    if args.command == "features":
        _print(feature_rows())
        return 0
    if args.command == "validate":
        config = load_config(args.config, args.set)
        validate_config(config)
        contract = enforce_contract(config)
        _print(
            {
                "status": "valid",
                "family": config["experiment"]["family"],
                "feature_contract": contract,
            }
        )
        return 0
    if args.command == "contract":
        config = load_config(args.config, args.set)
        _print(audit_config(config))
        return 0
    if args.command == "run":
        config = load_config(args.config, args.set)
        _print(run_config(config))
        return 0
    if args.command == "resume":
        resolved = args.run_directory / "resolved_config.json"
        if not resolved.is_file():
            print(f"missing resolved configuration: {resolved}", file=sys.stderr)
            return 2
        config = json.loads(resolved.read_text(encoding="utf-8"))
        config["run"]["resume"] = True
        _print(run_config(config, resume_directory=args.run_directory))
        return 0
    if args.command == "sweep":
        config = load_config(args.config, args.set)
        _print(run_sweep(config))
        return 0
    if args.command == "smoke":
        path = args.config or root / "configs/00_smoke.toml"
        config = load_config(path, args.set)
        _print(run_config(config))
        return 0
    if args.command == "freeze":
        config = load_config(args.config, args.set)
        _print(create_freeze(config, args.output))
        return 0
    if args.command == "holdout":
        _print(run_frozen(args.freeze))
        return 0
    if args.command == "verify-freeze":
        payload = verify_freeze(args.freeze)
        _print(payload)
        return 0 if payload["all_checks_pass"] else 1
    if args.command == "audit":
        payload = audit_run(args.run_directory)
        _print(payload)
        return 0 if payload["all_checks_pass"] else 1
    if args.command == "verify":
        manifest = verify_manifest(root)
        vendor = verify_vendor(root)
        payload = {
            "manifest": manifest,
            "vendor": vendor,
            "all_checks_pass": bool(
                manifest["all_checks_pass"] and vendor["all_checks_pass"]
            ),
        }
        _print(payload)
        return 0 if payload["all_checks_pass"] else 1
    if args.command == "legacy":
        index = json.loads((root / "vendor/RELEASE_INDEX.json").read_text(encoding="utf-8"))
        if args.legacy_command == "list":
            _print(index)
            return 0
        if args.legacy_command == "extract":
            import zipfile

            release = next(
                (item for item in index["releases"] if item["version"] == args.version),
                None,
            )
            if release is None:
                print(f"unknown version: {args.version}", file=sys.stderr)
                return 2
            archive = root / "vendor/releases" / release["archive"]
            args.destination.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive) as handle:
                handle.extractall(args.destination)
            _print(
                {
                    "status": "extracted",
                    "archive": str(archive),
                    "destination": str(args.destination),
                }
            )
            return 0
    return 2
