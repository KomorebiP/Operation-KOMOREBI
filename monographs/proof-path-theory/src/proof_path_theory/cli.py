from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .certificate import (
    certificate_cost,
    minimum_certificate,
    unique_and_dag_certificate,
    validate_certificate,
)
from .io import (
    bundled_schema,
    certificate_to_dict,
    load_certificate,
    load_proof_field,
    save_certificate,
)


def _targets(values: Sequence[str] | None) -> frozenset[str] | None:
    return frozenset(values) if values else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proof-path",
        description="Validate and analyze finite Proof Path Theory objects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a proof field")
    validate.add_argument("field")

    core = subparsers.add_parser("core", help="extract the unique AND-DAG core")
    core.add_argument("field")
    core.add_argument("--target", action="append", dest="targets")
    core.add_argument("--output")

    minimum = subparsers.add_parser(
        "minimum",
        help="find an exact minimum certificate in a small alternative-derivation field",
    )
    minimum.add_argument("field")
    minimum.add_argument("--target", action="append", dest="targets")
    minimum.add_argument("--output")
    minimum.add_argument("--max-search-states", type=int, default=250_000)

    audit = subparsers.add_parser("audit", help="audit a certificate against a field")
    audit.add_argument("field")
    audit.add_argument("certificate")

    schema = subparsers.add_parser("schema", help="print a bundled JSON Schema")
    schema.add_argument(
        "kind",
        nargs="?",
        choices=("proof-field", "certificate"),
        default="proof-field",
    )

    wire = subparsers.add_parser("wire-check", help="check a canonical indexed trace certificate")
    wire.add_argument("problem")
    wire.add_argument("certificate")

    export = subparsers.add_parser("wire-export", help="solve a protected field and export its checked trace")
    export.add_argument("field")
    export.add_argument("--positive", action="append", default=[])
    export.add_argument("--negative", action="append", default=[])
    export.add_argument("--output-prefix", required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "wire-check":
        from .trace_codec import DEFAULT_MAX_BYTES, WireFormatError, WireResourceError, check_trace_json
        try:
            with Path(args.problem).open("rb") as f:
                problem = f.read(DEFAULT_MAX_BYTES + 1)
            with Path(args.certificate).open("rb") as f:
                certificate = f.read(DEFAULT_MAX_BYTES + 1)
            valid = check_trace_json(problem, certificate)
        except WireResourceError as exc:
            print(json.dumps({"status": "RESOURCE_LIMIT", "message": str(exc)}))
            return 2
        except (WireFormatError, OSError) as exc:
            print(json.dumps({"status": "INPUT_ERROR", "message": str(exc)}))
            return 2
        print(json.dumps({"status": "ACCEPTED" if valid else "REJECTED", "valid": valid,
                          "scope": "Fixed declared indexed problem; rejection is not infeasibility."}))
        return 0 if valid else 1

    if args.command == "wire-export":
        from .views import ProofFieldViews
        from .extension import solve_extension
        from .trace_codec import export_trace_exchange
        try:
            field = load_proof_field(args.field)
            views = ProofFieldViews(field)
            result = solve_extension(views, positive=args.positive, negative=args.negative)
            binding, problem, certificate = export_trace_exchange(
                views, result, positive=args.positive, negative=args.negative)
            prefix = Path(args.output_prefix)
            prefix.parent.mkdir(parents=True, exist_ok=True)
            problem_path = Path(str(prefix) + ".problem.json")
            certificate_path = Path(str(prefix) + ".certificate.json")
            binding_path = Path(str(prefix) + ".binding.json")
            problem_path.write_bytes(problem + b"\n")
            certificate_path.write_bytes(certificate + b"\n")
            binding_path.write_text(json.dumps({"node_names": binding.node_names,
                "rule_names": binding.rule_names, "source_field": str(args.field),
                "scope": "Address book, not a semantic proof of the source adapter."}, indent=2) + "\n")
        except (OSError, ValueError) as exc:
            print(json.dumps({"status": "INPUT_ERROR", "message": str(exc)}))
            return 2
        print(json.dumps({"status": "EXPORTED_CHECKED", "feasible": result.feasible,
                          "problem": str(problem_path), "certificate": str(certificate_path),
                          "binding": str(binding_path)}, indent=2))
        return 0

    if args.command == "schema":
        print(json.dumps(bundled_schema(args.kind), indent=2, sort_keys=True))
        return 0

    if args.command == "validate":
        field = load_proof_field(args.field)
        payload = {
            "valid": True,
            "nodes": len(field.nodes),
            "justifications": len(field.justifications),
            "premises": sorted(field.premises),
            "targets": sorted(field.targets),
            "topological_order": list(field.topological_order),
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command in {"core", "minimum"}:
        field = load_proof_field(args.field)
        targets = _targets(args.targets)
        if args.command == "core":
            certificate = unique_and_dag_certificate(field, targets)
        else:
            certificate = minimum_certificate(
                field,
                targets,
                max_search_states=args.max_search_states,
            )
        if args.output:
            save_certificate(certificate, Path(args.output))
        payload = certificate_to_dict(certificate)
        payload["cost"] = certificate_cost(field, certificate)
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "audit":
        field = load_proof_field(args.field)
        certificate = load_certificate(args.certificate)
        report = validate_certificate(field, certificate)
        payload = {
            "valid": report.valid,
            "derived_nodes": sorted(report.derived_nodes),
            "missing_targets": sorted(report.missing_targets),
            "missing_required_premises": sorted(report.missing_required_premises),
            "missing_node_references": sorted(report.missing_node_references),
            "missing_justification_references": sorted(
                report.missing_justification_references
            ),
            "uncertified_justifications": sorted(report.uncertified_justifications),
            "unused_nodes": sorted(report.unused_nodes),
        }
        print(json.dumps(payload, indent=2))
        return 0 if report.valid else 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
