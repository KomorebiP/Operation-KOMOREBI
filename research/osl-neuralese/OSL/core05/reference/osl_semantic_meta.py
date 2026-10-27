"""Independent Core 0.5 verifier for metadata-facing semantics.

This module intentionally does not import or invoke ``OSLRuntime``.  It
reconstructs secret commitments, public metadata records, assertion accounting,
and ``show`` bindings from source statements and native receipt-v2 evidence.
The surrounding strict receipt kernel remains responsible for the common
envelope, hash chain, and terminal lifecycle.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict
from typing import Any

from osl_parser import parse_program


COMMON_RECEIPT_KEYS = {
    "schema",
    "core_version",
    "index",
    "state_index",
    "step",
    "kind",
    "transaction",
    "previous_digest",
    "digest",
}

META_RECEIPT_KEYS = {
    "secret_register": {"name", "value_digest"},
    "metadata_publish": {
        "name",
        "source",
        "from_secret",
        "metadata_digest",
    },
    "assert_pass": {"assertion", "assertion_count"},
    "show": {"semantic_digest"},
}


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


def _failure(code: str, **details: Any) -> dict[str, Any]:
    return {"code": code, **details}


class MetaSemanticVerifier:
    """Fail-closed receipt-driven reconstruction of metadata semantics."""

    def __init__(self) -> None:
        self.failures: list[dict[str, Any]] = []
        self.secret_values: dict[str, Any] = {}
        self.secret_digests: dict[str, str] = {}
        self.metadata: dict[str, dict[str, Any]] = {}
        self.assertions = 0
        self.transaction_checkpoint: dict[str, Any] | None = None
        self.transaction_name: str | None = None
        self.counters = {
            "secret_registers": 0,
            "metadata_publications": 0,
            "assertions": 0,
            "shows": 0,
            "transaction_restores": 0,
        }

    def fail(self, code: str, **details: Any) -> None:
        self.failures.append(_failure(code, **details))

    def expect(self, condition: bool, code: str, **details: Any) -> None:
        if not condition:
            self.fail(code, **details)

    @staticmethod
    def _boundary_map(
        statements: tuple[Any, ...], receipts: list[dict[str, Any]]
    ) -> tuple[dict[int, tuple[Any, dict[str, Any]]], list[dict[str, Any]]]:
        mapping: dict[int, tuple[Any, dict[str, Any]]] = {}
        failures: list[dict[str, Any]] = []
        for boundary in receipts:
            if boundary.get("kind") not in {"statement_commit", "statement_reject"}:
                continue
            ordinal = boundary.get("statement_ordinal")
            span = boundary.get("effect_span")
            if not isinstance(ordinal, int) or not (0 <= ordinal < len(statements)):
                failures.append(_failure("meta_boundary_ordinal", ordinal=ordinal))
                continue
            if (
                not isinstance(span, (list, tuple))
                or len(span) != 2
                or not all(isinstance(item, int) for item in span)
            ):
                failures.append(_failure("meta_boundary_span", ordinal=ordinal))
                continue
            start, end = span
            if start < 0 or end < start or end > len(receipts):
                failures.append(
                    _failure("meta_boundary_span_range", ordinal=ordinal, span=list(span))
                )
                continue
            for index in range(start, end):
                if index in mapping:
                    failures.append(
                        _failure("meta_boundary_overlap", receipt_index=index)
                    )
                mapping[index] = (statements[ordinal], boundary)
        return mapping, failures

    def _check_schema(self, receipt: dict[str, Any]) -> None:
        kind = receipt.get("kind")
        expected = COMMON_RECEIPT_KEYS | META_RECEIPT_KEYS[str(kind)]
        self.expect(
            set(receipt) == expected,
            "meta_receipt_schema",
            receipt_index=receipt.get("index"),
            kind=kind,
            missing=sorted(expected - set(receipt)),
            extra=sorted(set(receipt) - expected),
        )

    def _begin_transaction(self, receipt: dict[str, Any]) -> None:
        name = receipt.get("transaction")
        if not isinstance(name, str) or not name:
            name = receipt.get("name")
        self.expect(
            self.transaction_checkpoint is None,
            "meta_nested_transaction",
            receipt_index=receipt.get("index"),
        )
        self.transaction_name = str(name) if name is not None else None
        self.transaction_checkpoint = {
            "secret_values": copy.deepcopy(self.secret_values),
            "secret_digests": copy.deepcopy(self.secret_digests),
            "metadata": copy.deepcopy(self.metadata),
            "assertions": self.assertions,
        }

    def _commit_transaction(self, receipt: dict[str, Any]) -> None:
        self.expect(
            self.transaction_checkpoint is not None,
            "meta_commit_without_begin",
            receipt_index=receipt.get("index"),
        )
        self.transaction_checkpoint = None
        self.transaction_name = None

    def _rollback_transaction(self, receipt: dict[str, Any]) -> None:
        if self.transaction_checkpoint is None:
            self.fail(
                "meta_rollback_without_begin", receipt_index=receipt.get("index")
            )
            return
        checkpoint = self.transaction_checkpoint
        self.secret_values = copy.deepcopy(checkpoint["secret_values"])
        self.secret_digests = copy.deepcopy(checkpoint["secret_digests"])
        self.metadata = copy.deepcopy(checkpoint["metadata"])
        self.assertions = int(checkpoint["assertions"])
        self.transaction_checkpoint = None
        self.transaction_name = None
        self.counters["transaction_restores"] += 1

    def _apply_secret(
        self, receipt: dict[str, Any], statement: Any, boundary: dict[str, Any]
    ) -> None:
        self.expect(
            statement.kind == "secret",
            "secret_source_kind",
            receipt_index=receipt.get("index"),
        )
        args = statement.args
        value = args.get("value")
        expected_digest = digest(value)
        self.expect(
            receipt.get("name") == args.get("name"),
            "secret_source_name",
            receipt_index=receipt.get("index"),
        )
        self.expect(
            receipt.get("value_digest") == expected_digest,
            "secret_value_digest",
            receipt_index=receipt.get("index"),
        )
        name = str(args.get("name"))
        self.secret_values[name] = copy.deepcopy(value)
        self.secret_digests[name] = expected_digest
        self.counters["secret_registers"] += 1

    def _apply_metadata(
        self, receipt: dict[str, Any], statement: Any, boundary: dict[str, Any]
    ) -> None:
        self.expect(
            statement.kind == "metadata",
            "metadata_source_kind",
            receipt_index=receipt.get("index"),
        )
        args = statement.args
        secret_name = args.get("secret")
        from_secret = secret_name is not None
        if from_secret:
            self.expect(
                secret_name in self.secret_values,
                "metadata_secret_exists",
                receipt_index=receipt.get("index"),
                secret=secret_name,
            )
            value = copy.deepcopy(self.secret_values.get(str(secret_name)))
        else:
            value = copy.deepcopy(args.get("value"))
        source = args.get("source")
        step = receipt.get("step")
        self.expect(
            isinstance(step, int) and step >= 0,
            "metadata_step",
            receipt_index=receipt.get("index"),
        )
        payload = {"value": value, "source": source, "step": step}
        payload["digest"] = digest(payload)
        self.expect(
            receipt.get("name") == args.get("name"),
            "metadata_source_name",
            receipt_index=receipt.get("index"),
        )
        self.expect(
            receipt.get("source") == source,
            "metadata_source_label",
            receipt_index=receipt.get("index"),
        )
        self.expect(
            receipt.get("from_secret") is from_secret,
            "metadata_secret_flag",
            receipt_index=receipt.get("index"),
        )
        self.expect(
            receipt.get("metadata_digest") == payload["digest"],
            "metadata_digest",
            receipt_index=receipt.get("index"),
        )
        self.metadata[str(args.get("name"))] = payload
        self.counters["metadata_publications"] += 1

    def _apply_assertion(
        self, receipt: dict[str, Any], statement: Any, boundary: dict[str, Any]
    ) -> None:
        self.expect(
            statement.kind == "assert",
            "assert_source_kind",
            receipt_index=receipt.get("index"),
        )
        body = statement.args.get("body")
        self.assertions += 1
        self.expect(
            receipt.get("assertion") == body,
            "assert_source_body",
            receipt_index=receipt.get("index"),
        )
        self.expect(
            receipt.get("assertion_count") == self.assertions,
            "assert_count",
            receipt_index=receipt.get("index"),
        )
        self.counters["assertions"] += 1

    def _apply_show(
        self, receipt: dict[str, Any], statement: Any, boundary: dict[str, Any]
    ) -> None:
        self.expect(
            statement.kind == "show",
            "show_source_kind",
            receipt_index=receipt.get("index"),
        )
        self.expect(
            receipt.get("semantic_digest") == boundary.get("after_semantic_digest"),
            "show_boundary_semantic_digest",
            receipt_index=receipt.get("index"),
        )
        self.counters["shows"] += 1

    def verify(
        self,
        source: str,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            statements = parse_program(source)
        except Exception as exc:  # fail closed for malformed source
            self.fail("meta_source_parse", error=f"{type(exc).__name__}: {exc}")
            statements = ()

        if not isinstance(receipts, list) or any(
            not isinstance(receipt, dict) for receipt in receipts
        ):
            self.fail("meta_receipts_type")
            receipts = []

        boundary_map, boundary_failures = self._boundary_map(statements, receipts)
        self.failures.extend(boundary_failures)
        seen_by_ordinal: dict[int, list[str]] = {}

        for position, receipt in enumerate(receipts):
            kind = receipt.get("kind")
            if kind == "transaction_begin":
                self._begin_transaction(receipt)
                continue
            if kind == "transaction_commit":
                self._commit_transaction(receipt)
                continue
            if kind == "transaction_rollback":
                self._rollback_transaction(receipt)
                continue
            if kind not in META_RECEIPT_KEYS:
                continue
            self._check_schema(receipt)
            self.expect(
                receipt.get("index") == position,
                "meta_receipt_position",
                receipt_index=receipt.get("index"),
                position=position,
            )
            bound = boundary_map.get(position)
            if bound is None:
                self.fail(
                    "meta_receipt_without_statement", receipt_index=receipt.get("index")
                )
                continue
            statement, boundary = bound
            ordinal = int(boundary.get("statement_ordinal", -1))
            seen_by_ordinal.setdefault(ordinal, []).append(str(kind))
            if kind == "secret_register":
                self._apply_secret(receipt, statement, boundary)
            elif kind == "metadata_publish":
                self._apply_metadata(receipt, statement, boundary)
            elif kind == "assert_pass":
                self._apply_assertion(receipt, statement, boundary)
            elif kind == "show":
                self._apply_show(receipt, statement, boundary)

        expected_kind = {
            "secret": "secret_register",
            "metadata": "metadata_publish",
            "assert": "assert_pass",
            "show": "show",
        }
        boundaries_by_ordinal = {
            int(receipt["statement_ordinal"]): receipt
            for receipt in receipts
            if receipt.get("kind") in {"statement_commit", "statement_reject"}
            and isinstance(receipt.get("statement_ordinal"), int)
        }
        for ordinal, statement in enumerate(statements):
            if statement.kind not in expected_kind or ordinal not in boundaries_by_ordinal:
                continue
            boundary = boundaries_by_ordinal[ordinal]
            observed = seen_by_ordinal.get(ordinal, [])
            if boundary.get("kind") == "statement_commit":
                self.expect(
                    observed == [expected_kind[statement.kind]],
                    "meta_statement_effect_cardinality",
                    ordinal=ordinal,
                    expected=expected_kind[statement.kind],
                    observed=observed,
                )
            else:
                self.expect(
                    len(observed) <= 1,
                    "meta_rejected_effect_cardinality",
                    ordinal=ordinal,
                    observed=observed,
                )

        if self.transaction_checkpoint is not None:
            self.fail("meta_transaction_left_active", transaction=self.transaction_name)

        reconstructed = {
            "metadata": {
                key: copy.deepcopy(value) for key, value in sorted(self.metadata.items())
            },
            "secret_digests": dict(sorted(self.secret_digests.items())),
            "assertions": self.assertions,
        }
        if final_state is not None:
            self.expect(isinstance(final_state, dict), "meta_final_state_type")
            if isinstance(final_state, dict):
                for field in ("metadata", "secret_digests", "assertions"):
                    self.expect(
                        final_state.get(field) == reconstructed[field],
                        "meta_final_state_mismatch",
                        field=field,
                    )

        result = {
            "schema": "osl.core05.meta-semantic-report.v1",
            "all_checks_pass": not self.failures,
            "failures": self.failures,
            "counters": self.counters,
            "reconstructed": reconstructed,
            "claim_boundary": (
                "Secret commitments, metadata values and labels, assertion receipt "
                "accounting, show-to-boundary binding, and category rollback are "
                "independently reconstructed. General assertion truth is not "
                "independently evaluated by this module."
            ),
        }
        result["verification_digest"] = digest(result)
        return result


def verify_meta_semantics(
    source: str,
    receipts: list[dict[str, Any]],
    final_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify metadata-facing semantics without invoking the runtime."""

    try:
        return MetaSemanticVerifier().verify(source, receipts, final_state)
    except Exception as exc:  # final fail-closed guard
        result = {
            "schema": "osl.core05.meta-semantic-report.v1",
            "all_checks_pass": False,
            "failures": [
                _failure(
                    "meta_internal_error", error=f"{type(exc).__name__}: {exc}"
                )
            ],
            "counters": {},
            "reconstructed": {},
            "claim_boundary": "Verification failed closed before a claim was established.",
        }
        result["verification_digest"] = digest(result)
        return result


__all__ = ["MetaSemanticVerifier", "verify_meta_semantics"]
