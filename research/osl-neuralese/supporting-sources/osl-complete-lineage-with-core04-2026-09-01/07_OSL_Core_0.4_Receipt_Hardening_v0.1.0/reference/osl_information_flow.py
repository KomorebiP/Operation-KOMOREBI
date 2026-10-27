"""Inherited static dependency audit used by the OSL-Core 0.4 finite profile.

The analysis is intentionally conservative and syntactic.  It proves absence of
explicit dependency paths from registered private secrets into declared public
metadata in the supported fragment.  It does not cover implicit control flow,
timing, floating-point residues, semantic operator choice, or external tools.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

try:  # pragma: no cover
    from .osl_model import Statement, digest
    from .osl_parser import parse_and_check
except ImportError:  # pragma: no cover
    from osl_model import Statement, digest  # type: ignore
    from osl_parser import parse_and_check  # type: ignore


@dataclass(frozen=True)
class InformationFlowReport:
    schema: str
    secret_names: tuple[str, ...]
    public_metadata_names: tuple[str, ...]
    dependency_edges: tuple[tuple[str, str], ...]
    leaking_paths: tuple[tuple[str, ...], ...]
    explicit_leak_count: int
    noninterference_in_supported_fragment: bool
    claim_boundary: str
    report_digest: str


def analyze_information_flow(statements: Iterable[Statement]) -> InformationFlowReport:
    statements = tuple(statements)
    graph = nx.DiGraph()
    secrets: set[str] = set()
    public: set[str] = set()

    for statement in statements:
        args = statement.args
        if statement.kind == "secret":
            node = f"secret:{args['name']}"
            graph.add_node(node, security="private")
            secrets.add(args["name"])
        elif statement.kind == "metadata":
            node = f"metadata:{args['name']}"
            graph.add_node(node, security="public")
            public.add(args["name"])
            if args["secret"] is not None:
                graph.add_edge(f"secret:{args['secret']}", node)

    paths: list[tuple[str, ...]] = []
    for secret in sorted(secrets):
        source = f"secret:{secret}"
        for metadata in sorted(public):
            target = f"metadata:{metadata}"
            if source in graph and target in graph and nx.has_path(graph, source, target):
                for path in nx.all_simple_paths(graph, source, target):
                    paths.append(tuple(path))

    edges = tuple(sorted((str(a), str(b)) for a, b in graph.edges()))
    unsigned: dict[str, Any] = {
        "schema": "osl.core.static-information-flow.v1",
        "secret_names": tuple(sorted(secrets)),
        "public_metadata_names": tuple(sorted(public)),
        "dependency_edges": edges,
        "leaking_paths": tuple(sorted(paths)),
        "explicit_leak_count": len(paths),
        "noninterference_in_supported_fragment": not paths,
        "claim_boundary": (
            "The certificate covers explicit secret-to-metadata dependencies in "
            "the finite grammar. It is not a universal noninterference theorem "
            "for timing, control flow, semantic encodings, latent vectors, or tools."
        ),
    }
    return InformationFlowReport(**unsigned, report_digest=digest(unsigned))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("program", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    statements, _report = parse_and_check(args.program.read_text(encoding="utf-8"))
    result = analyze_information_flow(statements)
    payload = asdict(result)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.noninterference_in_supported_fragment else 1


if __name__ == "__main__":
    raise SystemExit(main())
