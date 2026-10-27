"""Independent verification of Core 0.5 audit intrinsics."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from osl_parser import parse_program


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


def verify_prefix(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    previous = "0" * 64
    failures: list[str] = []
    for expected_index, receipt in enumerate(receipts):
        if receipt.get("index") != expected_index:
            failures.append(f"index:{expected_index}")
        if receipt.get("previous_digest") != previous:
            failures.append(f"previous_digest:{expected_index}")
        unsigned = dict(receipt)
        observed = unsigned.pop("digest", None)
        if observed != digest(unsigned):
            failures.append(f"digest:{expected_index}")
        previous = str(observed)
    payload = {
        "schema": "osl.core.receipt-chain-verification.v1",
        "receipt_count": len(receipts),
        "chain_tip": previous,
        "failed_checks": failures,
        "all_checks_pass": not failures,
    }
    payload["verification_digest"] = digest(payload)
    return payload


def verify_intrinsic_semantics(
    source: str,
    receipts: list[dict[str, Any]],
    final_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    counters = {"receipt_chain_verifications": 0}
    try:
        statements = parse_program(source)
        if not isinstance(receipts, list) or any(
            not isinstance(receipt, dict) for receipt in receipts
        ):
            raise TypeError("receipts must be a list of mappings")

        source_by_receipt: dict[int, Any] = {}
        for boundary in receipts:
            if boundary.get("kind") not in {"statement_commit", "statement_reject"}:
                continue
            ordinal = boundary.get("statement_ordinal")
            span = boundary.get("effect_span")
            if not isinstance(ordinal, int) or not 0 <= ordinal < len(statements):
                continue
            if not isinstance(span, (list, tuple)) or len(span) != 2:
                continue
            start, end = span
            if not isinstance(start, int) or not isinstance(end, int):
                continue
            for index in range(start, end):
                source_by_receipt[index] = statements[ordinal]

        for position, receipt in enumerate(receipts):
            if receipt.get("kind") != "receipt_chain_verify":
                continue
            counters["receipt_chain_verifications"] += 1
            statement = source_by_receipt.get(position)
            if statement is None or statement.kind != "verify_receipts":
                failures.append(
                    {"code": "intrinsic_source_binding", "receipt_index": position}
                )
            expected_keys = {
                "schema",
                "core_version",
                "index",
                "state_index",
                "step",
                "kind",
                "transaction",
                "previous_digest",
                "report",
                "digest",
            }
            if set(receipt) != expected_keys:
                failures.append(
                    {
                        "code": "intrinsic_receipt_schema",
                        "receipt_index": position,
                    }
                )
            expected = verify_prefix(receipts[:position])
            if receipt.get("report") != expected:
                failures.append(
                    {
                        "code": "intrinsic_receipt_report",
                        "receipt_index": position,
                    }
                )
    except Exception as exc:
        failures.append(
            {"code": "intrinsic_malformed_input", "error": f"{type(exc).__name__}: {exc}"}
        )

    result = {
        "schema": "osl.core05.intrinsic-semantic-report.v1",
        "all_checks_pass": not failures,
        "failures": failures,
        "counters": counters,
        "claim_boundary": (
            "The report embedded by each verify_receipts statement is independently "
            "recomputed over the exact preceding receipt prefix."
        ),
    }
    result["verification_digest"] = digest(result)
    return result


__all__ = ["verify_intrinsic_semantics", "verify_prefix"]
