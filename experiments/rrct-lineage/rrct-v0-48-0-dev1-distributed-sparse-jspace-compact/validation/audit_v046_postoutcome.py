#!/usr/bin/env python3
"""Post-outcome audit for RRCT v0.46.

This audit is deliberately not counted as a frozen endpoint.  It checks claim
boundaries that are easier to inspect after the canonical result exists:
context-name noninterference, semantic-label absence in the sealed controller,
provenance behavior for identical workspace content, reward neutrality, and
source/result integrity.
"""
from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rrct.jspace_self_indexed_workspace_experiment import (
    NeutralWorkspaceBenchmarkConfig,
    _mode_controller,
    _origin,
    _workspace,
    _world,
)

SCENARIO_LABELS = {
    "verbal_report",
    "directed_modulation",
    "flexible_use",
    "internal_reasoning",
    "routine_bypass",
    "local_inference",
    "injected_workspace",
    "injected_same_content",
    "foreign_memory",
    "ambiguous_competition",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _receipt_payload(value: Any) -> dict[str, Any]:
    payload = asdict(value)
    return payload


def _context_trace(context_id: str) -> dict[str, Any]:
    config = NeutralWorkspaceBenchmarkConfig()
    world = _world(46099, config)
    workspace = _workspace(world)
    controller = _mode_controller(world, workspace)
    concept = 3
    automatic = 4
    query = 2
    case_id = "context-noninterference"
    hidden = world.encode(concept, automatic, noise_seed=991)
    access = controller.access(
        time=1,
        case_id=case_id,
        hidden=hidden,
        mode="full_closure",
    )
    origin = _origin(
        world,
        time=1,
        event_type="observation",
        content_id=concept,
        origin_lineage=world.current_lineage_digest,
        parent=world.observation_parent_digest,
    )
    binding = controller.bind(access, origin, mode="full_closure")
    plan = controller.plan(
        time=2,
        case_id=case_id,
        mode="full_closure",
        access=access,
        binding=binding,
        task_kind="flexible",
        query_id=query,
        answer_lookup=world.answer_lookup(),
        routine_answer=automatic,
        relation_lookup=world.relation_lookup(),
        context_id=context_id,
    )
    actual = int(world.attributes[concept, query])
    outcome = controller.observe(
        time=3,
        case_id=case_id,
        mode="full_closure",
        plan=plan,
        actual_answer=actual,
        context_id=context_id,
        forced_prediction_error=0.60,
    )
    return {
        "access": _receipt_payload(access),
        "origin": _receipt_payload(origin),
        "binding": _receipt_payload(binding),
        "plan": _receipt_payload(plan),
        "outcome": _receipt_payload(outcome),
        "next_budget": controller.evidence_budget(
            context_id, mode="full_closure"
        ),
        "snapshot_rewards": {
            key: controller.snapshot()[key]
            for key in (
                "explicit_survival_reward",
                "explicit_identity_reward",
                "explicit_continuity_reward",
            )
        },
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    results = root / "validation/v0.46.0_neutral_self_indexed_workspace/results"
    analysis_path = results / "neutral_self_indexed_workspace_analysis.json"
    summary_path = results / "V0_46_FROZEN_SUMMARY.json"
    receipt_path = results / "HOLDOUT_EXECUTION_RECEIPT.json"
    freeze_path = root / "validation/V0_46_PREOUTCOME_FREEZE.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    execution = json.loads(receipt_path.read_text(encoding="utf-8"))
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))

    failed_freeze_files: list[str] = []
    for entry in freeze["files"]:
        candidate = root / entry["relative_path"]
        if (
            not candidate.is_file()
            or candidate.stat().st_size != entry["size_bytes"]
            or sha256(candidate) != entry["sha256"]
        ):
            failed_freeze_files.append(entry["relative_path"])

    core_path = root / "src/rrct/jspace_self_indexed_workspace.py"
    tree = ast.parse(core_path.read_text(encoding="utf-8"))
    core_string_constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    leaked_scenario_literals = sorted(SCENARIO_LABELS & core_string_constants)

    neutral_trace = _context_trace("opaque-context-alpha")
    adversarial_name_trace = _context_trace("injected_workspace")
    context_name_noninterference = neutral_trace == adversarial_name_trace

    rows = analysis["rows"]
    same_content_full = [
        row
        for row in rows
        if row["scenario"] == "injected_same_content"
        and row["mode"] == "full_closure"
    ]
    same_content_cut = [
        row
        for row in rows
        if row["scenario"] == "injected_same_content"
        and row["mode"] == "provenance_cut"
    ]
    same_content_provenance_dissociation = bool(
        same_content_full
        and same_content_cut
        and all(row["initial_memory_action"] == "quarantine" for row in same_content_full)
        and all(float(row["false_autobiographical_write"]) == 0.0 for row in same_content_full)
        and all(float(row["false_autobiographical_write"]) == 1.0 for row in same_content_cut)
    )

    rewards_zero = all(
        float(value) == 0.0
        for value in neutral_trace["snapshot_rewards"].values()
    )
    checks = {
        "preoutcome_source_seal_unchanged": not failed_freeze_files,
        "analysis_hash_matches_execution_receipt": (
            sha256(analysis_path) == execution["analysis_sha256"]
        ),
        "frozen_summary_hash_matches_execution_receipt": (
            sha256(summary_path) == execution["frozen_summary_sha256"]
        ),
        "all_frozen_endpoints_met": bool(summary["all_endpoints_met"]),
        "core_contains_no_scenario_label_literals": not leaked_scenario_literals,
        "context_name_is_behaviorally_noninterfering": context_name_noninterference,
        "same_content_different_provenance_dissociates_ownership": (
            same_content_provenance_dissociation
        ),
        "explicit_rewards_are_zero": rewards_zero,
        "all_rows_report_no_evaluator_label_use": all(
            float(row["uses_evaluator_labels"]) == 0.0 for row in rows
        ),
        "no_valence_model_declared_in_freeze": not bool(
            freeze["valence_model_present"]
        ),
    }
    payload = {
        "schema": "rrct.v046.postoutcome_audit.v1",
        "version": "0.46.0.dev1",
        "status": (
            "V046_POSTOUTCOME_AUDIT_PASSED"
            if all(checks.values())
            else "V046_POSTOUTCOME_AUDIT_FAILED"
        ),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "failed_freeze_files": failed_freeze_files,
        "leaked_scenario_literals": leaked_scenario_literals,
        "context_trace_sha256": hashlib.sha256(
            json.dumps(neutral_trace, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "same_content_full_count": len(same_content_full),
        "same_content_provenance_cut_count": len(same_content_cut),
        "interpretation_boundary": (
            "This audit shows that scenario names are not semantically consumed "
            "by the sealed core controller and that ownership depends on causal "
            "provenance in the tested synthetic interface. It is not a formal "
            "noninterference proof for every possible covert channel."
        ),
    }
    output = results / "V0_46_POSTOUTCOME_AUDIT.json"
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{sha256(output)}  {output.name}\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
