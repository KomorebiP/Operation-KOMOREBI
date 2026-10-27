#!/usr/bin/env python3
"""Independent numerical/operator semantics for OSL-Core receipts.

This module deliberately does not import the OSL parser or runtime.  It parses
the bounded numerical fragment from the supplied source, binds each executed
statement to its receipt effect span, recomputes the numerical transition, and
compares the reconstructed spaces, vectors, and operators with the terminal
and optional final-state tables.

The checker is finite and executable rather than a proof assistant artifact.
It uses NumPy as an independent implementation of the published matrix
semantics.  Receipt hashes provide byte integrity only; source binding and
semantic reconstruction are what reject a consistently rehashed false trace.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np


REPORT_SCHEMA = "osl.semantic.numeric.verification.v1"
REPORT_CORE_VERSION = "0.5"
RECEIPT_SCHEMA = "osl.core.receipt.v2"
RECEIPT_CORE_VERSION = "0.5"
ZERO_DIGEST = "0" * 64
DEFAULT_COMPARISON_ATOL = 1e-12
PROJECTOR_DECLARATION_ATOL = 1e-9
OPERATOR_KINDS = {"linear", "projector", "transport", "external"}

IDENT = r"[A-Za-z_][\w-]*"
REAL = r"[-+]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][-+]?\d+)?"

NUMERIC_KINDS = {
    "space",
    "vector",
    "operator",
    "apply",
    "transport",
    "check_projector",
    "check_intertwiner",
}

PRIMARY_RECEIPT = {
    "space": "space_declare",
    "vector": "vector_declare",
    "operator": "operator",
    "apply": "operator_apply",
    "transport": "transport",
    "check_projector": "projector_check",
    "check_intertwiner": "intertwiner_check",
}

NUMERIC_RECEIPT_KINDS = set(PRIMARY_RECEIPT.values())
TRANSACTION_KINDS = {
    "begin_transaction",
    "commit_transaction",
    "rollback_transaction",
}

BASE_RECEIPT_KEYS = {
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

NUMERIC_RECEIPT_KEYS = {
    "space_declare": {"space"},
    "vector_declare": {"vector"},
    "operator": {"operator"},
    "operator_apply": {"target", "operator", "vector", "result"},
    "transport": {"source_operator", "transport", "result"},
    "projector_check": {"operator", "residual", "tolerance"},
    "intertwiner_check": {
        "transport",
        "left",
        "right",
        "residual",
        "tolerance",
    },
}

COMMIT_BOUNDARY_KEYS = BASE_RECEIPT_KEYS | {
    "statement_ordinal",
    "line_number",
    "statement_kind",
    "source_digest",
    "node_digest",
    "before_semantic_digest",
    "after_semantic_digest",
    "emitted_receipt_indices",
    "effect_span",
}

REJECT_BOUNDARY_KEYS = COMMIT_BOUNDARY_KEYS | {"rolled_back", "error"}

TRANSACTION_RECEIPT_KEYS = {
    "transaction_begin": BASE_RECEIPT_KEYS
    | {"begin_audit_index", "checkpoint_digest"},
    "transaction_commit": BASE_RECEIPT_KEYS
    | {
        "begin_audit_index",
        "begin_step",
        "body_effect_span",
        "final_state_digest",
    },
    "transaction_rollback": BASE_RECEIPT_KEYS
    | {
        "automatic",
        "reason",
        "begin_audit_index",
        "begin_step",
        "body_effect_span",
        "checkpoint_digest",
        "pre_restore_digest",
        "discarded_chain_tip",
        "discarded_receipt_count",
        "restored_state_digest",
    },
}


def canonical_json(value: Any) -> str:
    """Return the canonical JSON encoding used by the receipt protocol."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _without_digest(receipt: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(receipt)
    payload.pop("digest", None)
    return payload


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_real(value: Any) -> bool:
    return (
        isinstance(value, (int, float, np.integer, np.floating))
        and not isinstance(value, (bool, np.bool_))
        and math.isfinite(float(value))
    )


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _literal(text: str) -> Any:
    """Parse literals independently using the public JSON/Python subset."""

    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return ast.literal_eval(text)


@dataclass(frozen=True)
class SourceStatement:
    ordinal: int
    line_number: int
    source: str
    kind: str
    args: dict[str, Any] | None

    @property
    def is_numeric(self) -> bool:
        return self.kind in NUMERIC_KINDS

    @property
    def is_transaction(self) -> bool:
        return self.kind in TRANSACTION_KINDS

    def manifest(self) -> dict[str, Any]:
        if self.args is None:
            raise ValueError("manifest arguments unavailable for this statement")
        payload = {
            "ordinal": self.ordinal,
            "line_number": self.line_number,
            "kind": self.kind,
            "source": self.source,
            "args": self.args,
        }
        payload["node_digest"] = digest(payload)
        return payload


class NumericSemanticError(ValueError):
    """A source-authorized numerical transition is not defined."""


class NumericSourceError(ValueError):
    """The bounded numerical source fragment cannot be parsed."""


def _parse_known_line(line: str) -> tuple[str, dict[str, Any] | None]:
    if match := re.fullmatch(rf"space\s+({IDENT})\s+dim\s+(\d+)", line):
        return "space", {"name": match.group(1), "dim": int(match.group(2))}

    if match := re.fullmatch(rf"vector\s+({IDENT})\s+in\s+({IDENT})\s+values\s+(.+)", line):
        return "vector", {
            "name": match.group(1),
            "space": match.group(2),
            "values": _literal(match.group(3)),
        }

    if match := re.fullmatch(
        rf"operator\s+({IDENT})\s*:\s*({IDENT})\s*->\s*({IDENT})"
        rf"\s+kind\s+({IDENT})\s+matrix\s+(.+)",
        line,
    ):
        return "operator", {
            "name": match.group(1),
            "source_space": match.group(2),
            "target_space": match.group(3),
            "operator_kind": match.group(4),
            "matrix": _literal(match.group(5)),
        }

    if match := re.fullmatch(rf"apply\s+({IDENT})\s*=\s*({IDENT})\(({IDENT})\)", line):
        return "apply", {
            "target": match.group(1),
            "operator": match.group(2),
            "vector": match.group(3),
        }

    if match := re.fullmatch(
        rf"transport\s+({IDENT})\s+via\s+({IDENT})\s+as\s+({IDENT})", line
    ):
        return "transport", {
            "operator": match.group(1),
            "transport": match.group(2),
            "result": match.group(3),
        }

    if match := re.fullmatch(
        rf"check_projector\s+({IDENT})(?:\s+tolerance\s+({REAL}))?", line
    ):
        return "check_projector", {
            "operator": match.group(1),
            "tolerance": float(match.group(2) or "1e-9"),
        }

    if match := re.fullmatch(
        rf"check_intertwiner\s+({IDENT})\s+between\s+({IDENT})\s+and\s+({IDENT})"
        rf"(?:\s+tolerance\s+({REAL}))?",
        line,
    ):
        return "check_intertwiner", {
            "transport": match.group(1),
            "left": match.group(2),
            "right": match.group(3),
            "tolerance": float(match.group(4) or "1e-9"),
        }

    if match := re.fullmatch(rf"begin_transaction\s+({IDENT})", line):
        return "begin_transaction", {"name": match.group(1)}
    if match := re.fullmatch(rf"commit_transaction\s+({IDENT})", line):
        return "commit_transaction", {"name": match.group(1)}
    if match := re.fullmatch(rf"rollback_transaction\s+({IDENT})", line):
        return "rollback_transaction", {"name": match.group(1)}

    first = line.split(maxsplit=1)[0] if line else ""
    if first in NUMERIC_KINDS | TRANSACTION_KINDS:
        raise NumericSourceError(f"unrecognized {first!r} statement: {line}")
    return first, None


def parse_numeric_source(source: str) -> tuple[SourceStatement, ...]:
    """Parse source line positions plus the independent numerical fragment."""

    if not isinstance(source, str):
        raise NumericSourceError("source must be text")
    statements: list[SourceStatement] = []
    for line_number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            kind, args = _parse_known_line(line)
        except (SyntaxError, TypeError, ValueError) as exc:
            if isinstance(exc, NumericSourceError):
                raise
            raise NumericSourceError(
                f"line {line_number}: invalid numerical literal: {exc}"
            ) from exc
        statements.append(
            SourceStatement(
                ordinal=len(statements),
                line_number=line_number,
                source=line,
                kind=kind,
                args=args,
            )
        )
    return tuple(statements)


class NumericSemanticReconstructor:
    """Fail-closed verifier for the OSL numerical/operator receipt fragment."""

    def __init__(self, *, comparison_atol: float = DEFAULT_COMPARISON_ATOL) -> None:
        if not _is_real(comparison_atol) or float(comparison_atol) < 0.0:
            raise ValueError("comparison_atol must be a finite nonnegative number")
        self.comparison_atol = float(comparison_atol)
        self._reset()

    def _reset(self) -> None:
        self.failures: list[dict[str, Any]] = []
        self.spaces: dict[str, dict[str, Any]] = {}
        self.vectors: dict[str, dict[str, Any]] = {}
        self.operators: dict[str, dict[str, Any]] = {}
        self.projector_checks: list[dict[str, Any]] = []
        self.intertwiner_checks: list[dict[str, Any]] = []
        self.numeric_rejections: list[dict[str, Any]] = []
        self.active_transaction: str | None = None
        self.transaction_checkpoint: dict[str, Any] | None = None
        self.counters = {
            "source_statements": 0,
            "numeric_statements": 0,
            "executed_numeric_statements": 0,
            "numeric_receipts": 0,
            "spaces": 0,
            "vectors_declared": 0,
            "operators_declared": 0,
            "applications": 0,
            "transports": 0,
            "projector_checks": 0,
            "intertwiner_checks": 0,
            "numeric_rejections": 0,
            "transaction_checkpoints": 0,
            "transaction_commits": 0,
            "transaction_rollbacks": 0,
        }

    def _fail(self, property_name: str, message: str, **context: Any) -> None:
        item: dict[str, Any] = {"property": property_name, "message": message}
        if context:
            item["context"] = context
        self.failures.append(item)

    def _expect(
        self,
        condition: bool,
        property_name: str,
        message: str,
        **context: Any,
    ) -> bool:
        if not condition:
            self._fail(property_name, message, **context)
            return False
        return True

    def _exact_keys(
        self,
        value: Any,
        expected: set[str],
        property_name: str,
        **context: Any,
    ) -> bool:
        return self._expect(
            isinstance(value, dict) and set(value) == expected,
            property_name,
            "object keys do not match the strict schema",
            expected=sorted(expected),
            observed=sorted(value) if isinstance(value, dict) else type(value).__name__,
            **context,
        )

    def _numeric_equal(self, observed: Any, expected: Any, *, atol: float | None = None) -> bool:
        try:
            observed_array = np.asarray(observed, dtype=float)
            expected_array = np.asarray(expected, dtype=float)
        except (TypeError, ValueError, OverflowError):
            return False
        if observed_array.shape != expected_array.shape:
            return False
        if not np.all(np.isfinite(observed_array)) or not np.all(np.isfinite(expected_array)):
            return False
        threshold = self.comparison_atol if atol is None else atol
        return bool(np.allclose(observed_array, expected_array, atol=threshold, rtol=0.0))

    def _validate_receipt_envelopes(self, receipts: list[Any]) -> None:
        previous = ZERO_DIGEST
        previous_step = -1
        for expected_index, raw in enumerate(receipts):
            if not isinstance(raw, dict):
                self._fail(
                    "receipt_base_schema",
                    "receipt is not an object",
                    receipt_index=expected_index,
                )
                continue
            missing = BASE_RECEIPT_KEYS - set(raw)
            self._expect(
                not missing,
                "receipt_base_schema",
                "receipt is missing base fields",
                receipt_index=expected_index,
                missing=sorted(missing),
            )
            self._expect(
                raw.get("schema") == RECEIPT_SCHEMA,
                "receipt_schema",
                "unexpected receipt schema",
                receipt_index=expected_index,
            )
            self._expect(
                raw.get("core_version") == RECEIPT_CORE_VERSION,
                "receipt_core_version",
                "unexpected receipt core version",
                receipt_index=expected_index,
            )
            self._expect(
                raw.get("index") == expected_index and raw.get("state_index") == expected_index,
                "receipt_index",
                "receipt indices are not contiguous",
                receipt_index=expected_index,
            )
            self._expect(
                raw.get("previous_digest") == previous,
                "receipt_hash_chain",
                "receipt does not bind the preceding digest",
                receipt_index=expected_index,
            )
            try:
                expected_digest = digest(_without_digest(raw))
            except (TypeError, ValueError, OverflowError) as exc:
                expected_digest = None
                self._fail(
                    "receipt_digest",
                    "receipt cannot be canonically hashed",
                    receipt_index=expected_index,
                    error=str(exc),
                )
            self._expect(
                expected_digest is not None and raw.get("digest") == expected_digest,
                "receipt_digest",
                "receipt digest is invalid",
                receipt_index=expected_index,
            )
            step = raw.get("step")
            self._expect(
                _is_int(step) and int(step) >= previous_step,
                "receipt_step",
                "receipt step is not a monotone integer",
                receipt_index=expected_index,
            )
            if _is_int(step):
                previous_step = int(step)
            transaction = raw.get("transaction")
            self._expect(
                transaction is None or isinstance(transaction, str),
                "receipt_transaction",
                "transaction field must be null or text",
                receipt_index=expected_index,
            )
            previous = str(raw.get("digest"))

    def _validate_boundary(
        self,
        statement: SourceStatement,
        index: int,
        boundary: dict[str, Any],
        receipts: list[dict[str, Any]],
    ) -> tuple[int, ...]:
        expected_keys = (
            COMMIT_BOUNDARY_KEYS
            if boundary.get("kind") == "statement_commit"
            else REJECT_BOUNDARY_KEYS
        )
        self._exact_keys(
            boundary,
            expected_keys,
            "statement_boundary_schema",
            receipt_index=index,
            statement_ordinal=statement.ordinal,
        )
        self._expect(
            boundary.get("statement_ordinal") == statement.ordinal,
            "statement_boundary_ordinal",
            "boundary ordinal differs from source order",
            receipt_index=index,
        )
        if statement.is_numeric or statement.is_transaction:
            self._expect(
                boundary.get("line_number") == statement.line_number,
                "statement_boundary_line",
                "boundary line differs from source",
                receipt_index=index,
            )
            self._expect(
                boundary.get("statement_kind") == statement.kind,
                "statement_boundary_kind",
                "boundary kind differs from source",
                receipt_index=index,
            )
            self._expect(
                boundary.get("source_digest") == digest(statement.source),
                "statement_boundary_source",
                "boundary source commitment is invalid",
                receipt_index=index,
            )
            try:
                expected_node = statement.manifest()["node_digest"]
            except (TypeError, ValueError) as exc:
                expected_node = None
                self._fail(
                    "statement_boundary_node",
                    "source statement cannot be canonically manifested",
                    receipt_index=index,
                    error=str(exc),
                )
            self._expect(
                expected_node is not None and boundary.get("node_digest") == expected_node,
                "statement_boundary_node",
                "boundary AST node commitment is invalid",
                receipt_index=index,
            )
            self._expect(
                boundary.get("step") == statement.ordinal + 1,
                "statement_boundary_step",
                "boundary step differs from source ordinal",
                receipt_index=index,
            )

        raw_span = boundary.get("effect_span")
        if not (
            isinstance(raw_span, (list, tuple))
            and len(raw_span) == 2
            and all(_is_int(item) for item in raw_span)
        ):
            self._fail(
                "statement_effect_span",
                "effect span is not a pair of integer indices",
                receipt_index=index,
            )
            return ()
        start, end = int(raw_span[0]), int(raw_span[1])
        expected = tuple(range(start, end)) if 0 <= start <= end == index else ()
        self._expect(
            end == index and 0 <= start <= end,
            "statement_effect_span",
            "effect span does not end immediately before its boundary",
            receipt_index=index,
            observed=[start, end],
        )
        raw_emitted = boundary.get("emitted_receipt_indices")
        emitted = tuple(raw_emitted) if isinstance(raw_emitted, (list, tuple)) else ()
        self._expect(
            emitted == expected,
            "statement_effect_partition",
            "emitted receipt indices do not equal the contiguous effect span",
            receipt_index=index,
            expected=list(expected),
            observed=list(emitted),
        )
        for item in emitted:
            self._expect(
                _is_int(item) and 0 <= int(item) < len(receipts),
                "statement_effect_index",
                "effect span contains an invalid receipt index",
                receipt_index=index,
                effect_index=item,
            )
        return tuple(int(item) for item in emitted if _is_int(item) and 0 <= int(item) < len(receipts))

    def _validate_numeric_receipt_schema(
        self, receipt: dict[str, Any], receipt_index: int
    ) -> None:
        kind = str(receipt.get("kind"))
        expected = BASE_RECEIPT_KEYS | NUMERIC_RECEIPT_KEYS.get(kind, set())
        self._exact_keys(
            receipt,
            expected,
            f"{kind}_schema",
            receipt_index=receipt_index,
        )

    def _validate_transaction_receipt_schema(
        self, receipt: dict[str, Any], receipt_index: int
    ) -> None:
        kind = str(receipt.get("kind"))
        expected = TRANSACTION_RECEIPT_KEYS.get(kind)
        if expected is not None:
            self._exact_keys(
                receipt,
                expected,
                f"{kind}_schema",
                receipt_index=receipt_index,
            )

    def _space(self, name: str) -> dict[str, Any]:
        try:
            return self.spaces[name]
        except KeyError as exc:
            raise NumericSemanticError(f"unknown space {name!r}") from exc

    def _vector(self, name: str) -> dict[str, Any]:
        try:
            return self.vectors[name]
        except KeyError as exc:
            raise NumericSemanticError(f"unknown vector {name!r}") from exc

    def _operator(self, name: str) -> dict[str, Any]:
        try:
            return self.operators[name]
        except KeyError as exc:
            raise NumericSemanticError(f"unknown operator {name!r}") from exc

    def _validate_space_payload(
        self, observed: Any, expected: dict[str, Any], receipt_index: int
    ) -> None:
        if not self._exact_keys(
            observed, {"name", "dim"}, "space_payload_schema", receipt_index=receipt_index
        ):
            return
        self._expect(
            observed == expected,
            "space_payload",
            "space receipt differs from source declaration",
            receipt_index=receipt_index,
            expected=expected,
            observed=observed,
        )

    def _validate_vector_payload(
        self, observed: Any, expected: dict[str, Any], receipt_index: int, property_prefix: str
    ) -> None:
        if not self._exact_keys(
            observed,
            {"name", "space", "value"},
            f"{property_prefix}_payload_schema",
            receipt_index=receipt_index,
        ):
            return
        self._expect(
            observed.get("name") == expected["name"]
            and observed.get("space") == expected["space"],
            f"{property_prefix}_identity",
            "vector identity differs from the recomputed transition",
            receipt_index=receipt_index,
        )
        self._expect(
            self._numeric_equal(observed.get("value"), expected["value"]),
            f"{property_prefix}_value",
            "vector value differs from the recomputed transition",
            receipt_index=receipt_index,
            expected=expected["value"],
            observed=observed.get("value"),
        )

    def _validate_operator_payload(
        self, observed: Any, expected: dict[str, Any], receipt_index: int, property_prefix: str
    ) -> None:
        if not self._exact_keys(
            observed,
            {"name", "source", "target", "kind", "matrix"},
            f"{property_prefix}_payload_schema",
            receipt_index=receipt_index,
        ):
            return
        self._expect(
            all(observed.get(key) == expected[key] for key in ("name", "source", "target", "kind")),
            f"{property_prefix}_identity",
            "operator identity differs from the recomputed transition",
            receipt_index=receipt_index,
        )
        self._expect(
            self._numeric_equal(observed.get("matrix"), expected["matrix"]),
            f"{property_prefix}_matrix",
            "operator matrix differs from the recomputed transition",
            receipt_index=receipt_index,
            expected=expected["matrix"],
            observed=observed.get("matrix"),
        )

    def _execute_space(
        self, statement: SourceStatement, receipt: dict[str, Any] | None, receipt_index: int | None
    ) -> None:
        assert statement.args is not None
        name = str(statement.args["name"])
        dim = statement.args["dim"]
        if not _is_int(dim) or dim <= 0:
            raise NumericSemanticError("space dimension must be positive")
        if name in self.spaces:
            raise NumericSemanticError(f"space {name!r} already declared")
        expected = {"name": name, "dim": int(dim)}
        if receipt is not None and receipt_index is not None:
            self._validate_space_payload(receipt.get("space"), expected, receipt_index)
        self.spaces[name] = expected
        self.counters["spaces"] += 1

    def _execute_vector(
        self, statement: SourceStatement, receipt: dict[str, Any] | None, receipt_index: int | None
    ) -> None:
        assert statement.args is not None
        name = str(statement.args["name"])
        space_name = str(statement.args["space"])
        space = self._space(space_name)
        if name in self.vectors:
            raise NumericSemanticError(f"vector {name!r} already declared")
        try:
            value = np.asarray(statement.args["values"], dtype=float)
        except (TypeError, ValueError, OverflowError) as exc:
            raise NumericSemanticError(f"vector {name!r} has a nonnumeric value") from exc
        expected_shape = (int(space["dim"]),)
        if value.shape != expected_shape:
            raise NumericSemanticError(
                f"vector {name!r} has shape {value.shape}, expected {expected_shape}"
            )
        if not np.all(np.isfinite(value)):
            raise NumericSemanticError(f"vector {name!r} contains a nonfinite value")
        expected = {"name": name, "space": space_name, "value": value.tolist()}
        if receipt is not None and receipt_index is not None:
            self._validate_vector_payload(
                receipt.get("vector"), expected, receipt_index, "vector_declare"
            )
        self.vectors[name] = expected
        self.counters["vectors_declared"] += 1

    def _execute_operator(
        self, statement: SourceStatement, receipt: dict[str, Any] | None, receipt_index: int | None
    ) -> None:
        assert statement.args is not None
        name = str(statement.args["name"])
        source_name = str(statement.args["source_space"])
        target_name = str(statement.args["target_space"])
        source = self._space(source_name)
        target = self._space(target_name)
        if name in self.operators:
            raise NumericSemanticError(f"operator {name!r} already declared")
        try:
            matrix = np.asarray(statement.args["matrix"], dtype=float)
        except (TypeError, ValueError, OverflowError) as exc:
            raise NumericSemanticError(f"operator {name!r} has a nonnumeric matrix") from exc
        expected_shape = (int(target["dim"]), int(source["dim"]))
        if matrix.shape != expected_shape:
            raise NumericSemanticError(
                f"operator {name!r} has shape {matrix.shape}, expected {expected_shape}"
            )
        if not np.all(np.isfinite(matrix)):
            raise NumericSemanticError(f"operator {name!r} contains a nonfinite value")
        operator_kind = str(statement.args["operator_kind"])
        if operator_kind not in OPERATOR_KINDS:
            raise NumericSemanticError(f"unknown operator kind {operator_kind!r}")
        if operator_kind == "projector":
            if source_name != target_name or matrix.shape[0] != matrix.shape[1]:
                raise NumericSemanticError("projector must be a square endomorphism")
            if not np.allclose(
                matrix @ matrix,
                matrix,
                atol=PROJECTOR_DECLARATION_ATOL,
                rtol=0.0,
            ):
                raise NumericSemanticError(
                    f"operator {name!r} declared projector but is not idempotent"
                )
        expected = {
            "name": name,
            "source": source_name,
            "target": target_name,
            "kind": operator_kind,
            "matrix": matrix.tolist(),
        }
        if receipt is not None and receipt_index is not None:
            self._validate_operator_payload(
                receipt.get("operator"), expected, receipt_index, "operator_declare"
            )
        self.operators[name] = expected
        self.counters["operators_declared"] += 1

    def _execute_apply(
        self, statement: SourceStatement, receipt: dict[str, Any] | None, receipt_index: int | None
    ) -> None:
        assert statement.args is not None
        target_name = str(statement.args["target"])
        operator_name = str(statement.args["operator"])
        vector_name = str(statement.args["vector"])
        operator = self._operator(operator_name)
        vector = self._vector(vector_name)
        if target_name in self.vectors:
            raise NumericSemanticError(f"vector {target_name!r} already declared")
        if vector["space"] != operator["source"]:
            raise NumericSemanticError("operator source space does not match vector space")
        matrix = np.asarray(operator["matrix"], dtype=float)
        value = np.asarray(vector["value"], dtype=float)
        result_value = matrix @ value
        if not np.all(np.isfinite(result_value)):
            raise NumericSemanticError("operator application produced a nonfinite value")
        result = {
            "name": target_name,
            "space": operator["target"],
            "value": result_value.tolist(),
        }
        if receipt is not None and receipt_index is not None:
            self._expect(
                receipt.get("target") == target_name
                and receipt.get("operator") == operator_name
                and receipt.get("vector") == vector_name,
                "operator_apply_source_fields",
                "application receipt names differ from source",
                receipt_index=receipt_index,
            )
            self._validate_vector_payload(
                receipt.get("result"), result, receipt_index, "operator_apply"
            )
        self.vectors[target_name] = result
        self.counters["applications"] += 1

    def _execute_transport(
        self, statement: SourceStatement, receipt: dict[str, Any] | None, receipt_index: int | None
    ) -> None:
        assert statement.args is not None
        operator_name = str(statement.args["operator"])
        transport_name = str(statement.args["transport"])
        result_name = str(statement.args["result"])
        operator = self._operator(operator_name)
        transport = self._operator(transport_name)
        if result_name in self.operators:
            raise NumericSemanticError(f"operator {result_name!r} already declared")
        if operator["source"] != operator["target"]:
            raise NumericSemanticError("transported operator must be an endomorphism")
        if (
            transport["source"] != operator["source"]
            or transport["target"] != operator["source"]
        ):
            raise NumericSemanticError("transport operator must act on the same space")
        transport_matrix = np.asarray(transport["matrix"], dtype=float)
        try:
            inverse = np.linalg.inv(transport_matrix)
        except np.linalg.LinAlgError as exc:
            raise NumericSemanticError("transport matrix must be invertible") from exc
        matrix = transport_matrix @ np.asarray(operator["matrix"], dtype=float) @ inverse
        if not np.all(np.isfinite(matrix)):
            raise NumericSemanticError("operator transport produced a nonfinite matrix")
        result = {
            "name": result_name,
            "source": operator["source"],
            "target": operator["target"],
            "kind": operator["kind"],
            "matrix": matrix.tolist(),
        }
        if receipt is not None and receipt_index is not None:
            self._expect(
                receipt.get("source_operator") == operator_name
                and receipt.get("transport") == transport_name,
                "transport_source_fields",
                "transport receipt names differ from source",
                receipt_index=receipt_index,
            )
            self._validate_operator_payload(
                receipt.get("result"), result, receipt_index, "transport"
            )
        self.operators[result_name] = result
        self.counters["transports"] += 1

    def _execute_projector_check(
        self, statement: SourceStatement, receipt: dict[str, Any] | None, receipt_index: int | None
    ) -> None:
        assert statement.args is not None
        operator_name = str(statement.args["operator"])
        tolerance = float(statement.args["tolerance"])
        if not math.isfinite(tolerance) or tolerance < 0.0:
            raise NumericSemanticError(
                "projector tolerance must be finite and nonnegative"
            )
        operator = self._operator(operator_name)
        if operator["source"] != operator["target"]:
            raise NumericSemanticError(
                "projector check requires a square endomorphism"
            )
        matrix = np.asarray(operator["matrix"], dtype=float)
        residual = float(np.linalg.norm(matrix @ matrix - matrix))
        report = {
            "statement_ordinal": statement.ordinal,
            "operator": operator_name,
            "residual": residual,
            "tolerance": tolerance,
            "passed": residual <= tolerance,
        }
        self.projector_checks.append(report)
        self.counters["projector_checks"] += 1
        if residual > tolerance:
            raise NumericSemanticError(
                f"projector residual {residual:.6g} exceeds tolerance {tolerance:.6g}"
            )
        if receipt is not None and receipt_index is not None:
            self._expect(
                receipt.get("operator") == operator_name,
                "projector_check_operator",
                "projector check names a different operator",
                receipt_index=receipt_index,
            )
            self._expect(
                _is_real(receipt.get("tolerance"))
                and float(receipt["tolerance"]) == tolerance,
                "projector_check_tolerance",
                "projector check tolerance differs from source",
                receipt_index=receipt_index,
            )
            self._expect(
                _is_real(receipt.get("residual"))
                and math.isclose(
                    float(receipt["residual"]),
                    residual,
                    rel_tol=0.0,
                    abs_tol=self.comparison_atol,
                ),
                "projector_check_residual",
                "projector residual differs from independent recomputation",
                receipt_index=receipt_index,
                expected=residual,
                observed=receipt.get("residual"),
            )

    def _execute_intertwiner_check(
        self, statement: SourceStatement, receipt: dict[str, Any] | None, receipt_index: int | None
    ) -> None:
        assert statement.args is not None
        transport_name = str(statement.args["transport"])
        left_name = str(statement.args["left"])
        right_name = str(statement.args["right"])
        tolerance = float(statement.args["tolerance"])
        if not math.isfinite(tolerance) or tolerance < 0.0:
            raise NumericSemanticError(
                "intertwiner tolerance must be finite and nonnegative"
            )
        transport = self._operator(transport_name)
        left = self._operator(left_name)
        right = self._operator(right_name)
        if not (
            left["source"] == left["target"] == transport["source"]
            and right["source"] == right["target"] == transport["target"]
        ):
            raise NumericSemanticError("intertwiner spaces are incompatible")
        transport_matrix = np.asarray(transport["matrix"], dtype=float)
        left_matrix = np.asarray(left["matrix"], dtype=float)
        right_matrix = np.asarray(right["matrix"], dtype=float)
        residual = float(
            np.linalg.norm(transport_matrix @ left_matrix - right_matrix @ transport_matrix)
        )
        report = {
            "statement_ordinal": statement.ordinal,
            "transport": transport_name,
            "left": left_name,
            "right": right_name,
            "residual": residual,
            "tolerance": tolerance,
            "passed": residual <= tolerance,
        }
        self.intertwiner_checks.append(report)
        self.counters["intertwiner_checks"] += 1
        if residual > tolerance:
            raise NumericSemanticError(
                f"intertwiner residual {residual:.6g} exceeds tolerance {tolerance:.6g}"
            )
        if receipt is not None and receipt_index is not None:
            self._expect(
                receipt.get("transport") == transport_name
                and receipt.get("left") == left_name
                and receipt.get("right") == right_name,
                "intertwiner_check_operators",
                "intertwiner receipt names differ from source",
                receipt_index=receipt_index,
            )
            self._expect(
                _is_real(receipt.get("tolerance"))
                and float(receipt["tolerance"]) == tolerance,
                "intertwiner_check_tolerance",
                "intertwiner check tolerance differs from source",
                receipt_index=receipt_index,
            )
            self._expect(
                _is_real(receipt.get("residual"))
                and math.isclose(
                    float(receipt["residual"]),
                    residual,
                    rel_tol=0.0,
                    abs_tol=self.comparison_atol,
                ),
                "intertwiner_check_residual",
                "intertwiner residual differs from independent recomputation",
                receipt_index=receipt_index,
                expected=residual,
                observed=receipt.get("residual"),
            )

    def _execute_numeric(
        self,
        statement: SourceStatement,
        receipt: dict[str, Any] | None,
        receipt_index: int | None,
    ) -> None:
        handlers = {
            "space": self._execute_space,
            "vector": self._execute_vector,
            "operator": self._execute_operator,
            "apply": self._execute_apply,
            "transport": self._execute_transport,
            "check_projector": self._execute_projector_check,
            "check_intertwiner": self._execute_intertwiner_check,
        }
        handlers[statement.kind](statement, receipt, receipt_index)

    def _snapshot_numeric_tables(self) -> dict[str, Any]:
        return {
            "spaces": copy.deepcopy(self.spaces),
            "vectors": copy.deepcopy(self.vectors),
            "operators": copy.deepcopy(self.operators),
        }

    def _restore_numeric_tables(self) -> None:
        if self.transaction_checkpoint is None:
            self._fail(
                "transaction_numeric_checkpoint",
                "rollback has no numerical checkpoint",
            )
            return
        self.spaces = copy.deepcopy(self.transaction_checkpoint["spaces"])
        self.vectors = copy.deepcopy(self.transaction_checkpoint["vectors"])
        self.operators = copy.deepcopy(self.transaction_checkpoint["operators"])

    def _transaction_receipts(
        self,
        effects: Iterable[tuple[int, dict[str, Any]]],
        kind: str,
    ) -> list[tuple[int, dict[str, Any]]]:
        return [(index, receipt) for index, receipt in effects if receipt.get("kind") == kind]

    def _process_transaction_statement(
        self,
        statement: SourceStatement,
        boundary: dict[str, Any],
        effects: list[tuple[int, dict[str, Any]]],
    ) -> None:
        assert statement.args is not None
        name = str(statement.args["name"])
        expected_receipt_kind = {
            "begin_transaction": "transaction_begin",
            "commit_transaction": "transaction_commit",
            "rollback_transaction": "transaction_rollback",
        }[statement.kind]
        matching = self._transaction_receipts(effects, expected_receipt_kind)
        self._expect(
            len(matching) == 1,
            "transaction_numeric_lifecycle",
            "transaction statement does not own exactly one matching receipt",
            statement_ordinal=statement.ordinal,
            expected=expected_receipt_kind,
            observed=len(matching),
        )
        if not matching:
            return
        receipt_index, receipt = matching[0]
        self._validate_transaction_receipt_schema(receipt, receipt_index)
        self._expect(
            receipt.get("transaction") == name,
            "transaction_numeric_source",
            "transaction receipt name differs from source",
            receipt_index=receipt_index,
        )

        if statement.kind == "begin_transaction":
            self._expect(
                boundary.get("kind") == "statement_commit" and self.active_transaction is None,
                "transaction_numeric_begin",
                "numerical transaction begin is not a unique committed begin",
                statement_ordinal=statement.ordinal,
            )
            if self.active_transaction is None:
                self.transaction_checkpoint = self._snapshot_numeric_tables()
                self.active_transaction = name
                self.counters["transaction_checkpoints"] += 1
            return

        self._expect(
            self.active_transaction == name,
            "transaction_numeric_active_name",
            "transaction close differs from the active numerical checkpoint",
            statement_ordinal=statement.ordinal,
            expected=self.active_transaction,
            observed=name,
        )
        if statement.kind == "commit_transaction":
            self._expect(
                boundary.get("kind") == "statement_commit",
                "transaction_numeric_commit",
                "transaction commit statement rejected",
                statement_ordinal=statement.ordinal,
            )
            self.active_transaction = None
            self.transaction_checkpoint = None
            self.counters["transaction_commits"] += 1
        else:
            self._expect(
                receipt.get("automatic") is False,
                "transaction_numeric_explicit_rollback",
                "explicit rollback is marked automatic",
                receipt_index=receipt_index,
            )
            self._restore_numeric_tables()
            self.active_transaction = None
            self.transaction_checkpoint = None
            self.counters["transaction_rollbacks"] += 1

    def _process_automatic_rollback(
        self,
        statement: SourceStatement,
        boundary: dict[str, Any],
        effects: list[tuple[int, dict[str, Any]]],
    ) -> None:
        rollbacks = self._transaction_receipts(effects, "transaction_rollback")
        if statement.kind == "rollback_transaction":
            return
        if not rollbacks:
            if boundary.get("kind") == "statement_reject" and self.active_transaction is not None:
                self._fail(
                    "transaction_numeric_rollback_missing",
                    "rejection inside a transaction did not restore the numerical checkpoint",
                    statement_ordinal=statement.ordinal,
                )
            return
        self._expect(
            len(rollbacks) == 1
            and boundary.get("kind") == "statement_reject"
            and self.active_transaction is not None,
            "transaction_numeric_automatic_rollback",
            "automatic rollback is not attached to one rejected active statement",
            statement_ordinal=statement.ordinal,
        )
        receipt_index, receipt = rollbacks[0]
        self._validate_transaction_receipt_schema(receipt, receipt_index)
        self._expect(
            receipt.get("automatic") is True
            and receipt.get("transaction") == self.active_transaction,
            "transaction_numeric_automatic_source",
            "automatic rollback does not name the active transaction",
            receipt_index=receipt_index,
        )
        self._restore_numeric_tables()
        self.active_transaction = None
        self.transaction_checkpoint = None
        self.counters["transaction_rollbacks"] += 1

    def _compare_spaces(self, observed: Any, source_name: str) -> None:
        if not isinstance(observed, dict):
            self._fail(
                f"{source_name}_spaces_correspondence",
                "spaces table is not an object",
            )
            return
        self._expect(
            set(observed) == set(self.spaces),
            f"{source_name}_spaces_correspondence",
            "space names differ from independent reconstruction",
            expected=sorted(self.spaces),
            observed=sorted(observed),
        )
        for name, expected in self.spaces.items():
            item = observed.get(name)
            if self._exact_keys(
                item,
                {"name", "dim"},
                f"{source_name}_space_schema",
                space=name,
            ):
                self._expect(
                    item == expected,
                    f"{source_name}_spaces_correspondence",
                    "space entry differs from independent reconstruction",
                    space=name,
                    expected=expected,
                    observed=item,
                )

    def _compare_vectors(self, observed: Any, source_name: str) -> None:
        if not isinstance(observed, dict):
            self._fail(
                f"{source_name}_vectors_correspondence",
                "vectors table is not an object",
            )
            return
        self._expect(
            set(observed) == set(self.vectors),
            f"{source_name}_vectors_correspondence",
            "vector names differ from independent reconstruction",
            expected=sorted(self.vectors),
            observed=sorted(observed),
        )
        for name, expected in self.vectors.items():
            item = observed.get(name)
            if not self._exact_keys(
                item,
                {"name", "space", "value"},
                f"{source_name}_vector_schema",
                vector=name,
            ):
                continue
            self._expect(
                item.get("name") == name and item.get("space") == expected["space"],
                f"{source_name}_vectors_correspondence",
                "vector identity differs from independent reconstruction",
                vector=name,
            )
            self._expect(
                self._numeric_equal(item.get("value"), expected["value"]),
                f"{source_name}_vectors_correspondence",
                "vector value differs from independent reconstruction",
                vector=name,
                expected=expected["value"],
                observed=item.get("value"),
            )

    def _compare_operators(self, observed: Any, source_name: str) -> None:
        if not isinstance(observed, dict):
            self._fail(
                f"{source_name}_operators_correspondence",
                "operators table is not an object",
            )
            return
        self._expect(
            set(observed) == set(self.operators),
            f"{source_name}_operators_correspondence",
            "operator names differ from independent reconstruction",
            expected=sorted(self.operators),
            observed=sorted(observed),
        )
        for name, expected in self.operators.items():
            item = observed.get(name)
            if not self._exact_keys(
                item,
                {"name", "source", "target", "kind", "matrix"},
                f"{source_name}_operator_schema",
                operator=name,
            ):
                continue
            self._expect(
                all(item.get(key) == expected[key] for key in ("name", "source", "target", "kind")),
                f"{source_name}_operators_correspondence",
                "operator identity differs from independent reconstruction",
                operator=name,
            )
            self._expect(
                self._numeric_equal(item.get("matrix"), expected["matrix"]),
                f"{source_name}_operators_correspondence",
                "operator matrix differs from independent reconstruction",
                operator=name,
                expected=expected["matrix"],
                observed=item.get("matrix"),
            )

    def _compare_tables(self, state: Any, source_name: str) -> None:
        if not isinstance(state, dict):
            self._fail(
                f"{source_name}_numeric_state",
                "state containing numerical tables is not an object",
            )
            return
        for key in ("spaces", "vectors", "operators"):
            self._expect(
                key in state,
                f"{source_name}_numeric_state",
                "state is missing a numerical table",
                table=key,
            )
        self._compare_spaces(state.get("spaces"), source_name)
        self._compare_vectors(state.get("vectors"), source_name)
        self._compare_operators(state.get("operators"), source_name)

    def _result(self, source_bound: bool) -> dict[str, Any]:
        checks = {
            "source_binding": not any(
                failure["property"].startswith(("numeric_source", "statement_boundary"))
                for failure in self.failures
            ),
            "receipt_integrity": not any(
                failure["property"].startswith("receipt_") for failure in self.failures
            ),
            "strict_schemas": not any(
                "schema" in failure["property"] for failure in self.failures
            ),
            "numerical_semantics": not any(
                failure["property"].startswith(
                    (
                        "space_",
                        "vector_",
                        "operator_",
                        "transport_",
                        "projector_",
                        "intertwiner_",
                        "numeric_",
                    )
                )
                for failure in self.failures
            ),
            "transaction_projection": not any(
                failure["property"].startswith("transaction_numeric")
                for failure in self.failures
            ),
            "final_tables": not any(
                failure["property"].startswith(("terminal_", "final_"))
                for failure in self.failures
            ),
        }
        payload: dict[str, Any] = {
            "schema": REPORT_SCHEMA,
            "core_version": REPORT_CORE_VERSION,
            "receipt_core_version": RECEIPT_CORE_VERSION,
            "source_bound": source_bound,
            "comparison_atol": self.comparison_atol,
            "checks": checks,
            "all_checks_pass": source_bound and not self.failures,
            "counters": dict(self.counters),
            "reconstructed": {
                "spaces": copy.deepcopy(dict(sorted(self.spaces.items()))),
                "vectors": copy.deepcopy(dict(sorted(self.vectors.items()))),
                "operators": copy.deepcopy(dict(sorted(self.operators.items()))),
            },
            "projector_checks": copy.deepcopy(self.projector_checks),
            "intertwiner_checks": copy.deepcopy(self.intertwiner_checks),
            "numeric_rejections": copy.deepcopy(self.numeric_rejections),
            "failure_count": len(self.failures),
            "failures": copy.deepcopy(self.failures),
            "claim_boundary": (
                "Independent executable reconstruction covers spaces, vectors, "
                "operators, application, coordinate transport, projector checks, "
                "intertwiner checks, and their numerical transaction rollback "
                "projection. It is finite NumPy evidence, not mechanized proof; "
                "SHA-256 is content integrity rather than principal authentication."
            ),
        }
        payload["verification_digest"] = digest(payload)
        return payload

    def _verify_strict(
        self,
        source: str,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any] | None,
    ) -> dict[str, Any]:
        statements = parse_numeric_source(source)
        self.counters["source_statements"] = len(statements)
        self.counters["numeric_statements"] = sum(item.is_numeric for item in statements)

        self._validate_receipt_envelopes(receipts)
        statement_by_ordinal = {statement.ordinal: statement for statement in statements}
        boundaries: list[tuple[int, dict[str, Any]]] = [
            (index, receipt)
            for index, receipt in enumerate(receipts)
            if isinstance(receipt, dict)
            and receipt.get("kind") in {"statement_commit", "statement_reject"}
        ]
        seen_ordinals: set[int] = set()
        owner: dict[int, int] = {}

        for boundary_index, boundary in boundaries:
            ordinal = boundary.get("statement_ordinal")
            if not _is_int(ordinal) or int(ordinal) not in statement_by_ordinal:
                self._fail(
                    "statement_boundary_ordinal",
                    "boundary ordinal does not identify a source statement",
                    receipt_index=boundary_index,
                    observed=ordinal,
                )
                continue
            ordinal = int(ordinal)
            self._expect(
                ordinal not in seen_ordinals,
                "statement_boundary_unique",
                "source statement has more than one boundary",
                statement_ordinal=ordinal,
            )
            seen_ordinals.add(ordinal)
            statement = statement_by_ordinal[ordinal]
            emitted = self._validate_boundary(statement, boundary_index, boundary, receipts)
            effects = [(item, receipts[item]) for item in emitted if isinstance(receipts[item], dict)]
            for effect_index, _ in effects:
                self._expect(
                    effect_index not in owner,
                    "statement_effect_overlap",
                    "receipt belongs to more than one statement effect span",
                    receipt_index=effect_index,
                )
                owner[effect_index] = ordinal

            if statement.is_transaction:
                self._process_transaction_statement(statement, boundary, effects)
                continue

            if statement.is_numeric:
                self.counters["executed_numeric_statements"] += 1
                primary_kind = PRIMARY_RECEIPT[statement.kind]
                primary = [
                    (effect_index, receipt)
                    for effect_index, receipt in effects
                    if receipt.get("kind") == primary_kind
                ]
                other_numeric = [
                    (effect_index, receipt)
                    for effect_index, receipt in effects
                    if receipt.get("kind") in NUMERIC_RECEIPT_KINDS
                    and receipt.get("kind") != primary_kind
                ]
                self._expect(
                    not other_numeric,
                    "numeric_effect_kind",
                    "statement owns a numerical receipt of the wrong kind",
                    statement_ordinal=statement.ordinal,
                    observed=[receipt.get("kind") for _, receipt in other_numeric],
                )
                self._expect(
                    len(primary) <= 1,
                    "numeric_primary_unique",
                    "statement owns duplicate primary numerical receipts",
                    statement_ordinal=statement.ordinal,
                    observed=len(primary),
                )
                operation_receipt: dict[str, Any] | None = None
                operation_index: int | None = None
                if primary:
                    operation_index, operation_receipt = primary[0]
                    self.counters["numeric_receipts"] += 1
                    self._validate_numeric_receipt_schema(operation_receipt, operation_index)
                    self._expect(
                        operation_receipt.get("step") == statement.ordinal + 1,
                        "numeric_receipt_step",
                        "numerical receipt step differs from its statement",
                        receipt_index=operation_index,
                    )
                    self._expect(
                        operation_receipt.get("transaction") == self.active_transaction,
                        "numeric_receipt_transaction",
                        "numerical receipt has the wrong transaction scope",
                        receipt_index=operation_index,
                        expected=self.active_transaction,
                        observed=operation_receipt.get("transaction"),
                    )

                semantic_error: NumericSemanticError | None = None
                try:
                    self._execute_numeric(statement, operation_receipt, operation_index)
                except NumericSemanticError as exc:
                    semantic_error = exc

                if semantic_error is not None:
                    self._expect(
                        operation_receipt is None,
                        "numeric_receipt_before_failure",
                        "receipt exists for a numerical transition that must reject",
                        statement_ordinal=statement.ordinal,
                        error=str(semantic_error),
                    )
                    self._expect(
                        boundary.get("kind") == "statement_reject",
                        "numeric_rejection_boundary",
                        "invalid numerical transition committed",
                        statement_ordinal=statement.ordinal,
                        error=str(semantic_error),
                    )
                    if boundary.get("kind") == "statement_reject":
                        self._expect(
                            isinstance(boundary.get("error"), str)
                            and str(semantic_error) in str(boundary.get("error")),
                            "numeric_rejection_causality",
                            "rejection error does not contain the independently derived cause",
                            statement_ordinal=statement.ordinal,
                            expected=str(semantic_error),
                            observed=boundary.get("error"),
                        )
                    rejection = {
                        "statement_ordinal": statement.ordinal,
                        "statement_kind": statement.kind,
                        "reason": str(semantic_error),
                    }
                    self.numeric_rejections.append(rejection)
                    self.counters["numeric_rejections"] += 1
                else:
                    self._expect(
                        operation_receipt is not None,
                        "numeric_primary_missing",
                        "defined numerical transition has no primary receipt",
                        statement_ordinal=statement.ordinal,
                        expected=primary_kind,
                    )

            self._process_automatic_rollback(statement, boundary, effects)

        for receipt_index, receipt in enumerate(receipts):
            if not isinstance(receipt, dict) or receipt.get("kind") not in NUMERIC_RECEIPT_KINDS:
                continue
            ordinal = owner.get(receipt_index)
            statement = statement_by_ordinal.get(ordinal) if ordinal is not None else None
            self._expect(
                statement is not None
                and statement.is_numeric
                and PRIMARY_RECEIPT[statement.kind] == receipt.get("kind"),
                "numeric_receipt_source_owner",
                "numerical receipt is not owned by its exact source statement",
                receipt_index=receipt_index,
                statement_ordinal=ordinal,
            )

        self._expect(
            self.active_transaction is None,
            "transaction_numeric_closed",
            "verification ended with an active numerical transaction checkpoint",
            transaction=self.active_transaction,
        )

        terminal = receipts[-1] if receipts and isinstance(receipts[-1], dict) else None
        terminal_state = terminal.get("final_semantic_state") if terminal is not None else None
        if isinstance(terminal_state, dict):
            self._compare_tables(terminal_state, "terminal")
        else:
            self._fail(
                "terminal_numeric_state",
                "trace terminal does not expose a final semantic state",
            )
        if final_state is not None:
            self._compare_tables(final_state, "final")

        return self._result(source_bound=True)

    def verify(
        self,
        source: str,
        receipts: list[dict[str, Any]],
        final_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Verify untrusted numerical evidence and return failures as data."""

        self._reset()
        try:
            if not isinstance(source, str):
                self._fail("numeric_source_required", "source must be supplied as text")
                return self._result(source_bound=False)
            if not isinstance(receipts, list):
                self._fail("receipt_input", "receipts must be supplied as a list")
                return self._result(source_bound=True)
            if final_state is not None and not isinstance(final_state, dict):
                self._fail("final_numeric_state", "final_state must be an object or null")
                return self._result(source_bound=True)
            return self._verify_strict(source, receipts, final_state)
        except Exception as exc:  # fail closed at the public trust boundary
            self._fail(
                "malformed_numeric_verifier_input",
                "numerical verifier rejected malformed input",
                error_type=type(exc).__name__,
                error=str(exc),
            )
            return self._result(source_bound=isinstance(source, str))


def verify_numeric_semantics(
    source: str,
    receipts: list[dict[str, Any]],
    final_state: dict[str, Any] | None = None,
    *,
    comparison_atol: float = DEFAULT_COMPARISON_ATOL,
) -> dict[str, Any]:
    """Functional entry point for the independent numerical verifier."""

    return NumericSemanticReconstructor(comparison_atol=comparison_atol).verify(
        source, receipts, final_state
    )


__all__ = [
    "NumericSemanticReconstructor",
    "NumericSemanticError",
    "NumericSourceError",
    "parse_numeric_source",
    "verify_numeric_semantics",
]
