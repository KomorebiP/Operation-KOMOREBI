"""Macro-schema evidence, promotion, and task-ID-free runtime banks."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping

from komorebi_lasm_compiler.model import canonical_value, sha256_record

from .families import SCHEMA_FAMILIES, family_sketches
from .model import MacroSchemaEvidence, MacroStatus


def build_schema_evidence(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    minimum_support: int = 2,
) -> tuple[dict[str, Any], dict[str, Any]]:
    from .audit import candidate_correct

    state: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "families": set(), "activation_count": 0, "exact_count": 0, "wrong_count": 0,
        "exact_task_ids": set(), "wrong_task_ids": set(), "signature_hashes": set(),
    })
    for task_id, record in records.items():
        for candidate in record.get("candidates", []):
            program = candidate["program"]
            schema = str(program["macro_schema"])
            item = state[schema]
            item["families"].add(str(program["family"]))
            item["activation_count"] += 1
            item["signature_hashes"].add(str(program["signature_hash"]))
            correct = candidate_correct(candidate, solutions[task_id])
            if correct:
                item["exact_count"] += 1
                item["exact_task_ids"].add(str(task_id))
            else:
                item["wrong_count"] += 1
                item["wrong_task_ids"].add(str(task_id))
    audit: dict[str, Any] = {}
    runtime_macros: list[dict[str, Any]] = []
    for schema in sorted(SCHEMA_FAMILIES):
        item = state[schema]
        exact_source_tasks = len(item["exact_task_ids"])
        wrong = int(item["wrong_count"])
        if wrong:
            status = MacroStatus.RETIRED
        elif exact_source_tasks >= minimum_support:
            status = MacroStatus.STABLE
        elif exact_source_tasks >= 1:
            status = MacroStatus.PROVISIONAL
        else:
            status = MacroStatus.CANDIDATE
        evidence_digest = sha256_record({
            "schema": schema,
            "exact_task_ids": sorted(item["exact_task_ids"]),
            "wrong_task_ids": sorted(item["wrong_task_ids"]),
            "signature_hashes": sorted(item["signature_hashes"]),
        })
        evidence = MacroSchemaEvidence(
            schema=schema,
            families=tuple(sorted(SCHEMA_FAMILIES[schema])),
            activation_count=int(item["activation_count"]),
            exact_count=int(item["exact_count"]),
            wrong_count=wrong,
            exact_source_tasks=exact_source_tasks,
            status=status,
            minimum_support=minimum_support,
            evidence_digest=evidence_digest,
        )
        audit[schema] = {
            **evidence.to_runtime_record(),
            "exact_count": int(item["exact_count"]),
            "exact_task_ids": sorted(item["exact_task_ids"]),
            "wrong_task_ids": sorted(item["wrong_task_ids"]),
            "signature_hashes": sorted(item["signature_hashes"]),
        }
        if status in {MacroStatus.STABLE, MacroStatus.PROVISIONAL}:
            runtime_macros.append(evidence.to_runtime_record())
    runtime = {
        "schema": "komorebi.lasm_obstruction_macro_bank",
        "schema_version": 1,
        "minimum_support": minimum_support,
        "macros": runtime_macros,
        "sketches": [sketch.to_record() for sketch in family_sketches()],
    }
    runtime["bank_id"] = sha256_record(runtime)
    runtime["content_hash"] = sha256_record(runtime)
    return audit, runtime


def permitted_schemas(runtime_bank: Mapping[str, Any], *, stable_only: bool = False) -> set[str]:
    allowed = set()
    for macro in runtime_bank.get("macros", []):
        status = str(macro.get("status"))
        if status == MacroStatus.STABLE.value or (not stable_only and status == MacroStatus.PROVISIONAL.value):
            allowed.add(str(macro["macro_schema"]))
    return allowed


__all__ = ["build_schema_evidence", "permitted_schemas"]
