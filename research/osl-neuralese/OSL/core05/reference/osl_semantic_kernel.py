"""Unified independent semantic profile for OSL-Core 0.5.

The component verifiers are intentionally separate from ``OSLRuntime`` and
from one another.  This module only aggregates their fail-closed reports; it
does not rerun the interpreter or convert same-runtime replay into an
independent claim.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

from osl_semantic_contracts import verify_contract_semantics
from osl_semantic_intrinsics import verify_intrinsic_semantics
from osl_semantic_meta import verify_meta_semantics
from osl_semantic_numeric import verify_numeric_semantics
from osl_semantic_sessions import verify_session_semantics


REPORT_SCHEMA = "osl.core05.semantic-independence-suite.v1"
CORE_VERSION = "0.5"
RECEIPT_SCHEMA = "osl.core.receipt.v2"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _failed_report(domain: str, exc: Exception) -> dict[str, Any]:
    payload = {
        "schema": f"osl.core05.{domain}-semantic-failure.v1",
        "all_checks_pass": False,
        "failure_count": 1,
        "failures": [
            {
                "property": "component_verifier_exception",
                "error_type": type(exc).__name__,
            }
        ],
    }
    payload["verification_digest"] = digest(payload)
    return payload


def verify_semantic_independence(
    source: str,
    receipts: list[dict[str, Any]],
    final_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run every independent Core 0.5 semantic component fail closed."""

    components: tuple[
        tuple[str, Callable[[str, list[dict[str, Any]], dict[str, Any] | None], dict[str, Any]]],
        ...,
    ] = (
        ("numeric", verify_numeric_semantics),
        ("contracts", verify_contract_semantics),
        ("sessions", verify_session_semantics),
        ("metadata", verify_meta_semantics),
        ("intrinsics", verify_intrinsic_semantics),
    )
    reports: dict[str, dict[str, Any]] = {}
    for name, verifier in components:
        try:
            report = verifier(source, receipts, final_state)
            if not isinstance(report, dict):
                raise TypeError("component report is not a mapping")
            reports[name] = report
        except Exception as exc:
            reports[name] = _failed_report(name, exc)

    checks = {
        name: report.get("all_checks_pass") is True
        for name, report in reports.items()
    }
    source_bound = isinstance(source, str)
    if isinstance(receipts, list) and receipts and isinstance(receipts[0], dict):
        source_digest = receipts[0].get("source_digest")
    else:
        source_digest = None
    terminal = (
        receipts[-1]
        if isinstance(receipts, list) and receipts and isinstance(receipts[-1], dict)
        else {}
    )
    payload: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "core_version": CORE_VERSION,
        "receipt_schema": RECEIPT_SCHEMA,
        "source_bound": source_bound,
        "source_digest": source_digest,
        "receipt_count": len(receipts) if isinstance(receipts, list) else 0,
        "terminal_digest": terminal.get("digest"),
        "checks": checks,
        "independent_checks_pass": source_bound and all(checks.values()),
        "all_checks_pass": source_bound and all(checks.values()),
        "reports": reports,
        "independent_coverage": [
            "spaces, vectors, operators, application, transport, and finite numerical checks",
            "contract templates, feedback deadlines, and contract rollback",
            "finite session declarations, graphs, verification, advancement, and rollback",
            "secret commitments, metadata values, assertion accounting, show binding, and rollback",
            "embedded receipt-chain verification reports",
        ],
        "remaining_delegated_semantics": [
            "general truth of all fourteen assertion forms",
            "complete cross-domain transaction projection digests",
            "interpreter rejection causality outside reconstructed domain predicates",
            "diagnostic event-count reconstruction",
            "shared primary parser and static-checker correctness",
        ],
        "claim_boundary": (
            "The listed finite domains are reconstructed by implementations that "
            "do not import or invoke OSLRuntime. The result is executable finite "
            "assurance for supplied source and receipts, not a mechanized proof, "
            "principal authentication, an operating-system sandbox, or a universal "
            "security theorem."
        ),
    }
    payload["suite_digest"] = digest(payload)
    return payload


__all__ = ["verify_semantic_independence"]
