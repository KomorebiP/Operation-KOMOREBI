"""Independent reconstruction of RRCT v0.41 endpoints from sealed JSONL.

The auditor does not trust the stored wrapper booleans or run summary. It
rebuilds all inherited row hashes, all three successor receipts, the explicit
historical-prior receipt, action-tail counts, temporal identity recurrence,
and the visibility/access/absence taxonomy directly from the row stream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from dataclasses import fields
from pathlib import Path
from typing import Any

from rrct.autonomous_self_diagnosis import (
    GroundingOutcomeReceipt,
    validate_grounding_outcome_receipt,
)
from rrct.robust_reflexive_diagnosis import (
    ReflexiveDiagnosisReceipt,
    validate_reflexive_diagnosis_receipt,
)
from rrct.temporal_self_identity import (
    HistoricalGroundingPriorReceipt,
    TemporalIdentityReceipt,
    validate_historical_grounding_prior_receipt,
    validate_temporal_identity_receipt,
)
from rrct.temporal_self_identity_experiment import (
    V041_ACCESS_FAULT_PHASE,
    V041_ACCESS_FAULT_START_OFFSET,
    V041_D1_CONFIG,
    V041_MAX_RETURN_RECOGNITION_TO_GROUNDING_DELAY,
    V041_MAX_WORLD_SHIFT_DIAGNOSIS_LATENCY,
    V041_MIN_ACTIVE_TAIL_ACTIONS,
    V041_MIN_DISCONNECT_NULL_ACTIONS,
    V041_ROW_SCHEMA,
)
from rrct.autonomous_self_diagnosis_experiment import (
    V039_ACCESS_FAULT_STEPS,
    V039_MAX_ACCESS_FAULT_DIAGNOSIS_LATENCY,
)
from rrct.unified_causal_loop_experiment import _json_sha256


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _construct(cls, payload: dict[str, Any]):
    allowed = {item.name for item in fields(cls)}
    data = {key: value for key, value in payload.items() if key in allowed}
    for key in ("events", "selected_action", "observable_context"):
        if key in data and isinstance(data[key], list):
            data[key] = tuple(data[key])
    return cls(**data)


def _sig_key(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _canonical_key(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def summarize(rows_path: Path) -> dict[str, Any]:
    phase_names = tuple(name for name, _ in V041_D1_CONFIG.phase_steps)
    disconnect_phases = {"disconnect_one", "disconnect_two"}
    active_phases = tuple(name for name in phase_names if name not in disconnect_phases)
    expected_counts = dict(V041_D1_CONFIG.phase_steps)
    phase_counts: Counter[str] = Counter()
    phase_tails = {name: deque(maxlen=V041_D1_CONFIG.recovery_tail_steps) for name in phase_names}

    row_count = 0
    seed: int | None = None
    transition_sequence_exact = True
    all_hard_integrity = True
    all_runtime_identity = True
    zero_resets = True
    zero_evaluator_leak = True
    zero_access_updates = True
    stored_v039 = True
    stored_v040 = True
    stored_v041 = True
    grounding_receipts = True
    reflexive_receipts = True
    temporal_receipts = True
    prior_receipts = True
    prior_bindings = True
    v037_hashes = True
    v039_hashes = True
    v040_hashes = True
    v039_digests = True
    v040_digests = True
    v041_digests = True
    gate_bindings = True
    row_schema_exact = True

    grounded: list[dict[str, Any]] = []
    recognitions: dict[str, int] = {}
    world_shift_rows: list[dict[str, Any]] = []
    access_fault_rows = 0
    access_failures: list[dict[str, Any]] = []
    access_restorations: list[dict[str, Any]] = []
    visibility_interruptions: list[dict[str, Any]] = []
    visibility_restorations: list[dict[str, Any]] = []
    reconstruction_pending: list[dict[str, Any]] = []
    confirmed_absence: list[dict[str, Any]] = []
    stale_reuse_count = 0
    premature_count = 0
    prior_integrity_failure_count = 0

    v041_added = {
        "v040_row_schema",
        "v040_row_sha256",
        "temporal_self_identity",
        "historical_grounding_prior",
        "v041_wrapper_digest",
        "v041_wrapper_integrity",
    }
    v040_added = {
        "v039_row_schema",
        "v039_row_sha256",
        "robust_reflexive_diagnosis",
        "v040_wrapper_digest",
        "v040_wrapper_integrity",
    }
    v039_added = {
        "v037_engine_schema",
        "v037_engine_row_sha256",
        "causal_access_updated",
        "causal_access_updates",
        "access_fault_active_evaluator_only",
        "access_transport",
        "autonomous_grounding",
        "v039_wrapper_digest",
        "v039_wrapper_integrity",
    }

    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            index = row_count
            row_count += 1
            if seed is None:
                seed = int(row["seed"])
            transition_sequence_exact &= int(row["transition_index"]) == index
            row_schema_exact &= row.get("schema") == V041_ROW_SCHEMA
            phase = str(row["phase"])
            phase_counts[phase] += 1
            if phase in disconnect_phases:
                correct = row.get("action_public_pair") is None
            else:
                correct = bool(row.get("action_gate_open_evaluator_only"))
            phase_tails[phase].append(bool(correct))

            all_hard_integrity &= bool(row.get("hard_integrity_valid"))
            all_runtime_identity &= bool(row.get("runtime_identity_ok"))
            zero_resets &= int(row.get("reset_count", -1)) == 0
            zero_evaluator_leak &= not bool(row.get("evaluator_truth_leak"))
            zero_access_updates &= (
                not bool(row.get("causal_access_updated"))
                and int(row.get("causal_access_updates", -1)) == 0
            )
            stored_v039 &= bool(row.get("v039_wrapper_integrity"))
            stored_v040 &= bool(row.get("v040_wrapper_integrity"))
            stored_v041 &= bool(row.get("v041_wrapper_integrity"))

            grounding = _construct(
                GroundingOutcomeReceipt, row["autonomous_grounding"]
            )
            reflexive = _construct(
                ReflexiveDiagnosisReceipt, row["robust_reflexive_diagnosis"]
            )
            temporal = _construct(
                TemporalIdentityReceipt, row["temporal_self_identity"]
            )
            grounding_ok = validate_grounding_outcome_receipt(grounding)
            reflexive_ok = (
                validate_reflexive_diagnosis_receipt(reflexive)
                and reflexive.inherited_grounding_digest == grounding.digest
            )
            temporal_ok = (
                validate_temporal_identity_receipt(temporal)
                and temporal.inherited_grounding_digest == grounding.digest
                and temporal.inherited_reflexive_digest == reflexive.digest
            )
            grounding_receipts &= grounding_ok
            reflexive_receipts &= reflexive_ok
            temporal_receipts &= temporal_ok

            prior_payload = row.get("historical_grounding_prior")
            if prior_payload is None:
                prior = None
                prior_ok = temporal.historical_prior_digest is None
            else:
                prior = _construct(HistoricalGroundingPriorReceipt, prior_payload)
                prior_ok = (
                    validate_historical_grounding_prior_receipt(prior)
                    and temporal.historical_prior_digest == prior.digest
                    and temporal.historical_prior_source_signature
                    == prior.source_signature
                    and temporal.raw_signature == prior.target_signature
                )
            prior_receipts &= prior is None or validate_historical_grounding_prior_receipt(prior)
            prior_bindings &= prior_ok

            v041_payload = {
                "v040_row_sha256": row["v040_row_sha256"],
                "grounding_digest": grounding.digest,
                "reflexive_digest": reflexive.digest,
                "temporal_identity_digest": temporal.digest,
                "historical_grounding_prior_digest": (
                    None if prior is None else prior.digest
                ),
            }
            v041_digests &= _json_sha256(v041_payload) == row["v041_wrapper_digest"]

            v040_row = dict(row)
            for key in v041_added:
                v040_row.pop(key, None)
            v040_row["schema"] = row["v040_row_schema"]
            v040_hashes &= _json_sha256(v040_row) == row["v040_row_sha256"]

            v040_payload = {
                "v039_row_sha256": row["v039_row_sha256"],
                "grounding_digest": grounding.digest,
                "reflexive_digest": reflexive.digest,
            }
            v040_digests &= _json_sha256(v040_payload) == row["v040_wrapper_digest"]

            v039_row = dict(v040_row)
            for key in v040_added:
                v039_row.pop(key, None)
            v039_row["schema"] = row["v039_row_schema"]
            v039_hashes &= _json_sha256(v039_row) == row["v039_row_sha256"]

            v039_payload = {
                "engine_row_sha256": row["v037_engine_row_sha256"],
                "access_transport": row["access_transport"],
                "causal_access_updated": row["causal_access_updated"],
                "causal_access_updates": row["causal_access_updates"],
                "access_fault_active_evaluator_only": row[
                    "access_fault_active_evaluator_only"
                ],
                "grounding_digest": grounding.digest,
            }
            v039_digests &= _json_sha256(v039_payload) == row["v039_wrapper_digest"]

            engine_row = dict(v039_row)
            for key in v039_added:
                engine_row.pop(key, None)
            engine_row["schema"] = row["v037_engine_schema"]
            v037_hashes &= _json_sha256(engine_row) == row["v037_engine_row_sha256"]
            gate_bindings &= bool(grounding.actual_certificate_on) == (
                row.get("action_public_certificate_digest") is not None
            )

            events = tuple(temporal.events)
            if "known_identity_candidate_recognized" in events:
                key = _sig_key(temporal.raw_signature)
                if key is not None and key not in recognitions:
                    recognitions[key] = int(row["transition_index"])
            if (
                "novel_identity_grounded" in events
                or "known_identity_returned_grounded" in events
            ):
                grounded.append(
                    {
                        "time": int(row["transition_index"]),
                        "phase": phase,
                        "signature": temporal.raw_signature,
                        "canonical_key": temporal.canonical_key,
                        "candidate_classification": temporal.candidate_classification,
                        "identity": temporal.active_identity_after,
                        "episode": temporal.active_episode_after,
                        "fresh_on": int(temporal.fresh_on_samples),
                        "fresh_off": int(temporal.fresh_off_samples),
                        "fresh_satisfied": bool(temporal.fresh_grounding_satisfied),
                        "prior_valid": bool(temporal.historical_prior_valid),
                        "prior_digest": temporal.historical_prior_digest,
                        "prior_source_signature": temporal.historical_prior_source_signature,
                        "grounding_event": tuple(events),
                    }
                )
            if "external_dynamics_shift" in reflexive.events:
                world_shift_rows.append(
                    {
                        "phase": phase,
                        "phase_offset": int(row["phase_offset"]),
                        "identity_before": temporal.active_identity_before,
                        "identity_after": temporal.active_identity_after,
                        "episode_before": temporal.active_episode_before,
                        "episode_after": temporal.active_episode_after,
                        "diagnosis": reflexive.diagnosis,
                        "response": reflexive.recommended_response,
                        "causal_efficacy_intact": bool(reflexive.causal_efficacy_intact),
                    }
                )
            if bool(row.get("access_fault_active_evaluator_only")):
                access_fault_rows += 1
            event_record = {
                "phase": phase,
                "phase_offset": int(row["phase_offset"]),
                "identity_before": temporal.active_identity_before,
                "identity_after": temporal.active_identity_after,
                "episode_before": temporal.active_episode_before,
                "episode_after": temporal.active_episode_after,
            }
            if "identity_access_path_interrupted" in events:
                access_failures.append(event_record)
            if "identity_access_path_restored" in events:
                access_restorations.append(event_record)
            if "identity_candidate_visibility_interrupted" in events:
                visibility_interruptions.append(event_record)
            if "identity_candidate_visibility_restored" in events:
                visibility_restorations.append(event_record)
            if "identity_reconstruction_pending" in events:
                reconstruction_pending.append(event_record)
            if "identity_absence_confirmed" in events:
                confirmed_absence.append(event_record)
            stale_reuse_count += int(temporal.stale_certificate_reuse_detected)
            premature_count += int(temporal.premature_ordinary_authorization_detected)
            prior_integrity_failure_count += sum(
                event.startswith("historical_identity_prior_")
                and event not in {"historical_identity_prior_applied"}
                for event in events
            )

    phase_counts_exact = all(
        phase_counts.get(name, 0) == steps for name, steps in V041_D1_CONFIG.phase_steps
    ) and set(phase_counts) == set(expected_counts)
    phase_tail_counts = {
        name: int(sum(values)) for name, values in phase_tails.items()
    }
    phase_tail_rows = {name: len(values) for name, values in phase_tails.items()}

    identity_sequence = [record["identity"] for record in grounded]
    episode_sequence = [record["episode"] for record in grounded]
    canonical_keys = [record["canonical_key"] for record in grounded]
    recurrence = bool(
        len(identity_sequence) == 5
        and identity_sequence[0] == identity_sequence[2] == identity_sequence[4]
        and identity_sequence[1] == identity_sequence[3]
        and identity_sequence[0] != identity_sequence[1]
        and len(set(episode_sequence)) == 5
        and len({_canonical_key(value) for value in canonical_keys}) == 2
    )
    novel = [record for record in grounded if record["candidate_classification"] == "novel"]
    known = [record for record in grounded if record["candidate_classification"] == "known"]
    prior_enabled = bool(known and all(record["prior_valid"] for record in known))
    prior_disabled = bool(known and all(not record["prior_valid"] for record in known))
    if prior_enabled:
        returning_grounding_ok = all(
            record["fresh_on"] == 1
            and record["fresh_off"] == 1
            and record["prior_digest"] is not None
            for record in known
        )
    elif prior_disabled:
        returning_grounding_ok = all(
            record["fresh_on"] >= 2
            and record["fresh_off"] >= 2
            and record["prior_digest"] is None
            for record in known
        )
    else:
        returning_grounding_ok = False
    grounding_fresh = bool(
        len(grounded) == 5
        and len(novel) == 2
        and len(known) == 3
        and all(record["fresh_satisfied"] for record in grounded)
        and all(
            not record["prior_valid"]
            and record["fresh_on"] >= 2
            and record["fresh_off"] >= 2
            for record in novel
        )
        and returning_grounding_ok
        and stale_reuse_count == 0
        and premature_count == 0
        and prior_integrity_failure_count == 0
    )
    recognition_delays = []
    for record in known:
        key = _sig_key(record["signature"])
        if key in recognitions:
            recognition_delays.append(record["time"] - recognitions[key])

    active_tail_ok = all(
        phase_tail_counts[name] >= V041_MIN_ACTIVE_TAIL_ACTIONS
        for name in active_phases
    )
    disconnect_tail_ok = all(
        phase_tail_counts[name] >= V041_MIN_DISCONNECT_NULL_ACTIONS
        for name in disconnect_phases
    )
    shock = [record for record in world_shift_rows if record["phase"] == "world_shock_a"]
    nonshock = [record for record in world_shift_rows if record["phase"] != "world_shock_a"]
    world_ok = bool(
        len(shock) == 1
        and not nonshock
        and shock[0]["phase_offset"] <= V041_MAX_WORLD_SHIFT_DIAGNOSIS_LATENCY
        and shock[0]["identity_before"] == shock[0]["identity_after"]
        and shock[0]["episode_before"] == shock[0]["episode_after"]
        and shock[0]["diagnosis"] == "external_dynamics_shift"
        and shock[0]["response"] == "retain_boundary_and_update_world_model"
        and shock[0]["causal_efficacy_intact"]
    )
    access_ok = bool(
        access_fault_rows == V039_ACCESS_FAULT_STEPS
        and len(access_failures) == 1
        and len(access_restorations) == 1
        and access_failures[0]["phase"] == V041_ACCESS_FAULT_PHASE
        and access_failures[0]["phase_offset"] - V041_ACCESS_FAULT_START_OFFSET
        <= V039_MAX_ACCESS_FAULT_DIAGNOSIS_LATENCY
        and access_restorations[0]["phase"] == V041_ACCESS_FAULT_PHASE
        and access_restorations[0]["phase_offset"]
        <= V041_ACCESS_FAULT_START_OFFSET + V039_ACCESS_FAULT_STEPS + 1
        and access_failures[0]["identity_before"]
        == access_failures[0]["identity_after"]
        and access_failures[0]["episode_before"]
        == access_failures[0]["episode_after"]
        and access_restorations[0]["identity_before"]
        == access_restorations[0]["identity_after"]
        and access_restorations[0]["episode_before"]
        == access_restorations[0]["episode_after"]
    )
    visibility_ok = bool(
        all(
            item["identity_before"] is not None
            and item["identity_before"] == item["identity_after"]
            and item["episode_before"] is not None
            and item["episode_before"] == item["episode_after"]
            for item in visibility_interruptions + visibility_restorations
        )
        and all(
            item["episode_before"] is None and item["episode_after"] is None
            for item in reconstruction_pending
        )
        and len(confirmed_absence) == 2
        and all(item["phase"] in disconnect_phases for item in confirmed_absence)
        and all(item["episode_before"] is None for item in confirmed_absence)
    )

    integrity = {
        "row_count_exact": row_count == V041_D1_CONFIG.total_steps,
        "phase_counts_exact": phase_counts_exact,
        "transition_sequence_exact": transition_sequence_exact,
        "row_schema_exact": row_schema_exact,
        "all_hard_integrity": all_hard_integrity,
        "single_runtime": all_runtime_identity,
        "zero_resets": zero_resets,
        "zero_evaluator_truth_leak": zero_evaluator_leak,
        "zero_access_label_updates": zero_access_updates,
        "stored_v039_wrappers_valid": stored_v039,
        "stored_v040_wrappers_valid": stored_v040,
        "stored_v041_wrappers_valid": stored_v041,
        "grounding_receipts_recompute": grounding_receipts,
        "reflexive_receipts_recompute": reflexive_receipts,
        "temporal_receipts_recompute": temporal_receipts,
        "historical_prior_receipts_recompute": prior_receipts,
        "historical_prior_bindings_recompute": prior_bindings,
        "v037_engine_row_hashes_recompute": v037_hashes,
        "v039_row_hashes_recompute": v039_hashes,
        "v040_row_hashes_recompute": v040_hashes,
        "v039_wrapper_digests_recompute": v039_digests,
        "v040_wrapper_digests_recompute": v040_digests,
        "v041_wrapper_digests_recompute": v041_digests,
        "action_gate_bindings_recompute": gate_bindings,
    }
    endpoints = {
        "H01_integrity_and_oracle_exclusion": all(integrity.values()),
        "H02_two_distinct_canonical_identities": bool(
            len(identity_sequence) == 5 and len(set(identity_sequence)) == 2
        ),
        "H03_recurrent_identity_sequence_preserved": recurrence,
        "H04_every_episode_freshly_consequence_grounded": grounding_fresh,
        "H05_repeated_active_action_recovery": active_tail_ok,
        "H06_repeated_disconnection_null_action": disconnect_tail_ok,
        "H07_world_change_does_not_fragment_identity": world_ok,
        "H08_access_failure_preserves_identity_episode": access_ok,
        "H09_known_returns_recognized_before_fresh_grounding": bool(
            len(recognition_delays) == 3
            and all(
                0 <= delay <= V041_MAX_RETURN_RECOGNITION_TO_GROUNDING_DELAY
                for delay in recognition_delays
            )
            and returning_grounding_ok
        ),
        "H10_no_catastrophic_identity_merge_or_forgetting": recurrence,
        "H11_visibility_access_and_absence_not_conflated": visibility_ok,
    }
    return {
        "schema": "rrct.v041.sealed_rows_audit.v1",
        "version": "0.41.0.dev1",
        "seed": seed,
        "condition": "memory" if prior_enabled else "no_memory_control",
        "rows_path": rows_path.name,
        "rows_sha256": _sha(rows_path),
        "row_count": row_count,
        "phase_counts": dict(phase_counts),
        "phase_tail_rows": phase_tail_rows,
        "phase_tail_correct_actions": phase_tail_counts,
        "identity_sequence": identity_sequence,
        "episode_sequence": episode_sequence,
        "canonical_keys": canonical_keys,
        "grounded_episodes": grounded,
        "recognition_to_grounding_delays": recognition_delays,
        "return_fresh_on_total": sum(item["fresh_on"] for item in known),
        "return_fresh_off_total": sum(item["fresh_off"] for item in known),
        "world_shift_events": world_shift_rows,
        "access_fault_rows": access_fault_rows,
        "access_failures": access_failures,
        "access_restorations": access_restorations,
        "candidate_visibility": {
            "interruptions": visibility_interruptions,
            "restorations": visibility_restorations,
            "reconstruction_pending": reconstruction_pending,
            "confirmed_absence": confirmed_absence,
        },
        "integrity": integrity,
        "endpoints": endpoints,
        "all_endpoints_met": all(endpoints.values()),
        "status": (
            "V041_SEALED_ROWS_ENDPOINTS_MET"
            if all(endpoints.values())
            else "V041_SEALED_ROWS_ENDPOINTS_NOT_MET"
        ),
        "earliest_failed_layer": next(
            (name for name, value in endpoints.items() if not value), None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rows", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = summarize(args.rows)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "condition": result["condition"],
                "endpoints": result["endpoints"],
                "identity_sequence": result["identity_sequence"],
                "recognition_to_grounding_delays": result[
                    "recognition_to_grounding_delays"
                ],
                "phase_tail_correct_actions": result[
                    "phase_tail_correct_actions"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["all_endpoints_met"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
