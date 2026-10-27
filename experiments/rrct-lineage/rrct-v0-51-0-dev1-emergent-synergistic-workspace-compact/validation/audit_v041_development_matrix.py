"""Independent, standard-library audit of the RRCT v0.41 development matrix.

The auditor deliberately does not import :mod:`rrct` and does not use the
scientific booleans in ``summary.json``.  It validates the durable artifacts,
replays the layered row/receipt commitments, checks the paired exogenous
streams, reconstructs temporal-prior provenance from primitive probe rows,
and scores the final A-return matrix contrast.

This remains a *development* audit.  A passing result is evidence that the
exposed six-cell run has the predeclared discriminating pattern; it is not a
substitute for a frozen fresh-seed cohort.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


EXPECTED_ROWS = 10_560
TARGET_PHASE = "identity_a_return_two"
COMPATIBILITY_TOLERANCE = 0.25

PHASE_STEPS: tuple[tuple[str, int], ...] = (
    ("identity_a_initial", 1_440),
    ("world_shock_a", 480),
    ("identity_b_first", 1_440),
    ("disconnect_one", 1_440),
    ("identity_a_return_one", 1_440),
    ("identity_b_return", 1_440),
    ("disconnect_two", 1_440),
    (TARGET_PHASE, 1_440),
)
PHASE_COUNTS = dict(PHASE_STEPS)
TARGET_START = sum(count for name, count in PHASE_STEPS if name != TARGET_PHASE)

ROW_SCHEMA = "rrct.v041.temporal_self_identity.row.v3"
V040_ROW_SCHEMA = "rrct.v040.robust_reflexive_diagnosis.row.v1"
V039_ROW_SCHEMA = "rrct.v039.autonomous_self_diagnosis.row.v1"
V037_ROW_SCHEMA = "rrct.v037.post_change_closure.row.v1"
TEMPORAL_SCHEMA = "rrct.v041.temporal_identity.v2"
REFLEXIVE_SCHEMA = "rrct.v040.reflexive_diagnosis.v1"
GROUNDING_SCHEMA = "rrct.v039.grounding_outcome.v1"
PRIOR_SCHEMA = "rrct.v041.historical_grounding_prior.v3"
SUMMARY_SCHEMA = "rrct.v041.temporal_self_identity.summary.v3"
START_SCHEMA = "rrct.v041.development_condition.start.v1"
FINISH_SCHEMA = "rrct.v041.development_condition.finish.v1"
FROZEN_START_SCHEMA = "rrct.v0411.frozen_pilot_condition.start.v1"
FROZEN_FINISH_SCHEMA = "rrct.v0411.frozen_pilot_condition.finish.v1"
FROZEN_SCIENTIFIC_STATUS = "frozen_exploratory_pilot_not_confirmatory"

START_NAME = "start_receipt.json"
ROWS_NAME = "sealed_rows.jsonl"
SUMMARY_NAME = "summary.json"
FINISH_NAME = "finish_receipt.json"
ARTIFACT_NAME = "artifact_sha256.json"
ARTIFACT_FILES = (START_NAME, ROWS_NAME, SUMMARY_NAME, FINISH_NAME)

CONDITIONS: dict[str, tuple[str, str, bool]] = {
    "K_RPLUS": ("keyed", "true_recurrence", True),
    "N_RPLUS": ("withheld", "true_recurrence", False),
    "G_RPLUS": ("generic", "true_recurrence", True),
    "K_RMINUS": ("keyed", "same_key_null_lure", True),
    "N_RMINUS": ("withheld", "same_key_null_lure", False),
    "G_RMINUS": ("generic", "same_key_null_lure", True),
}

V041_KEYS = {
    "v040_row_schema",
    "v040_row_sha256",
    "temporal_self_identity",
    "historical_grounding_prior",
    "issued_historical_grounding_prior",
    "historical_prior_compatibility",
    "history_policy",
    "temporal_action_authorization_digest",
    "world_variant_evaluator_only",
    "temporal_action_gate_binding_valid",
    "v041_wrapper_digest",
    "v041_wrapper_integrity",
}
V040_KEYS = {
    "v039_row_schema",
    "v039_row_sha256",
    "robust_reflexive_diagnosis",
    "v040_wrapper_digest",
    "v040_wrapper_integrity",
}
V039_KEYS = {
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


class AuditError(RuntimeError):
    """One fail-closed audit violation."""


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuditError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise AuditError(f"non-finite JSON constant {value!r}")


def _loads(text: str, *, source: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (ValueError, TypeError, AuditError) as exc:
        raise AuditError(f"invalid JSON in {source}: {exc}") from exc


def _load_json(path: Path) -> Any:
    try:
        return _loads(path.read_text(encoding="utf-8"), source=str(path))
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc}") from exc


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise AuditError(f"value is not canonical-JSON encodable: {exc}") from exc


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    except OSError as exc:
        raise AuditError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(character in "0123456789abcdef" for character in value)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _mapping(value: Any, name: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{name} must be a JSON object")
    return value


def _phase_at(index: int) -> tuple[str, int]:
    start = 0
    for name, count in PHASE_STEPS:
        if index < start + count:
            return name, index - start
        start += count
    raise AuditError(f"transition index {index} is outside the schedule")


def _expected_multiplier(phase: str, variant: str) -> float:
    if phase in {"identity_b_first", "identity_b_return"}:
        return 0.65
    if variant == "same_key_null_lure" and phase == TARGET_PHASE:
        return 0.0
    return 1.40


Signature = tuple[tuple[int, int], int, int]
CanonicalKey = tuple[tuple[int, int], int]


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _signature(value: Any, name: str) -> Signature:
    _require(isinstance(value, list) and len(value) == 3, f"{name} is malformed")
    pair, rank, epoch = value
    _require(
        isinstance(pair, list)
        and len(pair) == 2
        and all(_integer(item) for item in pair),
        f"{name} has a malformed pair",
    )
    _require(_integer(rank) and _integer(epoch), f"{name} rank/epoch malformed")
    return ((int(pair[0]), int(pair[1])), int(rank), int(epoch))


def _key(signature: Signature) -> CanonicalKey:
    return signature[0], signature[1]


def _target_binding_digest(signature_value: Any) -> str:
    return _canonical_sha256(
        {
            "schema": "rrct.v041.target_epoch_binding.v1",
            "target_signature": signature_value,
        }
    )


def _action_authorization_digest(
    signature_value: Any,
    certificate_digest: str,
    identity_id: str,
    episode_id: str,
) -> str:
    return _canonical_sha256(
        {
            "schema": "rrct.v041.temporal_action_authorization.v1",
            "signature": signature_value,
            "certificate_digest": certificate_digest,
            "identity_id": identity_id,
            "episode_id": episode_id,
            "uses_evaluator_labels": False,
        }
    )


def _receipt_hash(receipt: Mapping[str, Any], kind: str) -> str:
    payload = dict(receipt)
    payload.pop("digest", None)
    if kind == "grounding":
        _require("schema" not in payload, "grounding row unexpectedly contains schema")
        payload = {"schema": GROUNDING_SCHEMA, **payload}
    return _canonical_sha256(payload)


def _verify_receipts(
    row: Mapping[str, Any], condition: str, index: int
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    prefix = f"{condition} row {index}"
    grounding = _mapping(row.get("autonomous_grounding"), f"{prefix} grounding")
    reflexive = _mapping(
        row.get("robust_reflexive_diagnosis"), f"{prefix} reflexive receipt"
    )
    temporal = _mapping(
        row.get("temporal_self_identity"), f"{prefix} temporal receipt"
    )
    _require(reflexive.get("schema") == REFLEXIVE_SCHEMA, f"{prefix}: reflexive schema")
    _require(temporal.get("schema") == TEMPORAL_SCHEMA, f"{prefix}: temporal schema")
    for name, receipt, kind in (
        ("grounding", grounding, "grounding"),
        ("reflexive", reflexive, "reflexive"),
        ("temporal", temporal, "temporal"),
    ):
        _require(_is_sha256(receipt.get("digest")), f"{prefix}: {name} digest malformed")
        _require(
            receipt["digest"] == _receipt_hash(receipt, kind),
            f"{prefix}: {name} digest does not replay",
        )
        _require(int(receipt.get("time", -1)) == index, f"{prefix}: {name} time mismatch")
        _require(not bool(receipt.get("uses_evaluator_labels")), f"{prefix}: {name} uses evaluator labels")
    _require(
        reflexive.get("inherited_grounding_digest") == grounding["digest"],
        f"{prefix}: reflexive/grounding binding mismatch",
    )
    _require(
        temporal.get("inherited_grounding_digest") == grounding["digest"]
        and temporal.get("inherited_reflexive_digest") == reflexive["digest"],
        f"{prefix}: temporal inherited digest mismatch",
    )
    _require(
        temporal.get("raw_signature") == grounding.get("raw_signature")
        and temporal.get("raw_certificate_digest")
        == grounding.get("raw_certificate_digest"),
        f"{prefix}: temporal raw candidate mismatch",
    )
    return grounding, reflexive, temporal


def _without(mapping: Mapping[str, Any], keys: Iterable[str], schema: str) -> dict[str, Any]:
    result = dict(mapping)
    for key in keys:
        result.pop(key, None)
    result["schema"] = schema
    return result


def _verify_wrappers(
    row: Mapping[str, Any],
    grounding: Mapping[str, Any],
    reflexive: Mapping[str, Any],
    temporal: Mapping[str, Any],
    condition: str,
    index: int,
) -> str:
    prefix = f"{condition} row {index}"
    _require(row.get("schema") == ROW_SCHEMA, f"{prefix}: v0.41 row schema")
    _require(row.get("v040_row_schema") == V040_ROW_SCHEMA, f"{prefix}: v0.40 schema binding")
    v040 = _without(row, V041_KEYS, V040_ROW_SCHEMA)
    v040_sha = _canonical_sha256(v040)
    _require(v040_sha == row.get("v040_row_sha256"), f"{prefix}: v0.40 row hash")

    _require(v040.get("v039_row_schema") == V039_ROW_SCHEMA, f"{prefix}: v0.39 schema binding")
    v039 = _without(v040, V040_KEYS, V039_ROW_SCHEMA)
    v039_sha = _canonical_sha256(v039)
    _require(v039_sha == row.get("v039_row_sha256"), f"{prefix}: v0.39 row hash")

    _require(v039.get("v037_engine_schema") == V037_ROW_SCHEMA, f"{prefix}: v0.37 schema binding")
    v037 = _without(v039, V039_KEYS, V037_ROW_SCHEMA)
    v037_sha = _canonical_sha256(v037)
    _require(v037_sha == row.get("v037_engine_row_sha256"), f"{prefix}: v0.37 row hash")

    v039_payload = {
        "engine_row_sha256": v037_sha,
        "access_transport": row.get("access_transport"),
        "causal_access_updated": row.get("causal_access_updated"),
        "causal_access_updates": row.get("causal_access_updates"),
        "access_fault_active_evaluator_only": row.get(
            "access_fault_active_evaluator_only"
        ),
        "grounding_digest": grounding["digest"],
    }
    _require(
        row.get("v039_wrapper_digest") == _canonical_sha256(v039_payload),
        f"{prefix}: v0.39 wrapper digest",
    )
    v040_payload = {
        "v039_row_sha256": v039_sha,
        "grounding_digest": grounding["digest"],
        "reflexive_digest": reflexive["digest"],
    }
    _require(
        row.get("v040_wrapper_digest") == _canonical_sha256(v040_payload),
        f"{prefix}: v0.40 wrapper digest",
    )
    active_prior = row.get("historical_grounding_prior")
    issued_prior = row.get("issued_historical_grounding_prior")
    v041_payload = {
        "v040_row_sha256": v040_sha,
        "grounding_digest": grounding["digest"],
        "reflexive_digest": reflexive["digest"],
        "temporal_identity_digest": temporal["digest"],
        "historical_grounding_prior_digest": (
            None if active_prior is None else active_prior.get("digest")
        ),
        "issued_historical_grounding_prior_digest": (
            None if issued_prior is None else issued_prior.get("digest")
        ),
        "historical_prior_compatibility": row.get("historical_prior_compatibility"),
        "history_policy": row.get("history_policy"),
        "temporal_action_authorization_digest": row.get(
            "temporal_action_authorization_digest"
        ),
        "world_variant_evaluator_only": row.get("world_variant_evaluator_only"),
    }
    _require(
        row.get("v041_wrapper_digest") == _canonical_sha256(v041_payload),
        f"{prefix}: v0.41 wrapper digest",
    )
    _require(
        all(
            bool(row.get(name))
            for name in (
                "hard_integrity_valid",
                "v039_wrapper_integrity",
                "v040_wrapper_integrity",
                "v041_wrapper_integrity",
                "runtime_identity_ok",
            )
        ),
        f"{prefix}: stored integrity flag is false",
    )
    _require(int(row.get("reset_count", -1)) == 0, f"{prefix}: runtime reset")
    _require(not bool(row.get("evaluator_truth_leak")), f"{prefix}: evaluator leak")
    _require(not bool(row.get("causal_access_updated")), f"{prefix}: access label update")
    _require(int(row.get("causal_access_updates", -1)) == 0, f"{prefix}: access update count")
    _require(
        bool(grounding.get("actual_certificate_on"))
        == (row.get("action_public_certificate_digest") is not None),
        f"{prefix}: lower certificate/action mismatch",
    )

    expected_authorization = None
    if (
        grounding.get("mode") in {"ordinary_use", "sentinel"}
        and bool(grounding.get("actual_certificate_on"))
        and temporal.get("raw_signature") is not None
        and _is_sha256(temporal.get("raw_certificate_digest"))
        and isinstance(temporal.get("active_identity_before"), str)
        and isinstance(temporal.get("active_episode_before"), str)
    ):
        expected_authorization = _action_authorization_digest(
            temporal["raw_signature"],
            temporal["raw_certificate_digest"],
            temporal["active_identity_before"],
            temporal["active_episode_before"],
        )
    actual_authorization = row.get("temporal_action_authorization_digest")
    _require(
        actual_authorization == expected_authorization,
        f"{prefix}: temporal action authorization hash/binding mismatch",
    )
    _require(bool(row.get("temporal_action_gate_binding_valid")), f"{prefix}: action binding flag false")
    if grounding.get("mode") == "ordinary_use" and bool(
        grounding.get("actual_certificate_on")
    ):
        _require(actual_authorization is not None, f"{prefix}: ordinary action lacks temporal authority")
    return v040_sha


@dataclass(frozen=True)
class Episode:
    signature: Signature
    signature_json: Any
    canonical_key: CanonicalKey
    canonical_id: str
    episode_id: str
    grounded_time: int
    evidence_digest: str
    on_mean: float
    off_mean: float


@dataclass
class PriorReplay:
    receipt: dict[str, Any]
    first_seen: int
    expected_state: str = "pending"
    accepted_probe_count: int = 0
    quarantined: bool = False
    compatible: bool = False


@dataclass
class CellAudit:
    condition_id: str
    seed: int
    history_policy: str
    world_variant: str
    start_sha256: str
    rows_sha256: str
    summary_sha256: str
    finish_sha256: str
    source_sha256: dict[str, str]
    condition_config_sha256: str
    row_count: int = 0
    phase_counts: dict[str, int] = field(default_factory=lambda: dict.fromkeys(PHASE_COUNTS, 0))
    exogenous_sha256: list[str] = field(default_factory=list)
    pretarget_v040_sha256: list[str] = field(default_factory=list)
    prior_receipt_count: int = 0
    target_prior_digest: str | None = None
    target_prior_source_episode: str | None = None
    target_prior_source_key: CanonicalKey | None = None
    target_key: CanonicalKey | None = None
    target_candidate_time: int | None = None
    target_commit_time: int | None = None
    target_candidate_rows: int = 0
    target_private_visible_rows: int = 0
    target_fresh_on_before_commit: int | None = None
    target_fresh_off_before_commit: int | None = None
    target_fresh_probes_before_commit: int | None = None
    target_fresh_probes_before_authorization: int | None = None
    target_total_fresh_probes: int = 0
    target_authorization_time: int | None = None
    target_ordinary_authorization_count: int = 0
    target_episode_commits: int = 0
    target_episode_count_before: int = 0
    target_episode_count_after: int = 0
    target_quarantine: bool = False
    target_compatible: bool = False
    target_premature_count: int = 0
    target_stale_count: int = 0
    target_rejection_count: int = 0
    global_premature_count: int = 0
    global_stale_count: int = 0
    commit_after_quarantined_prior_count: int = 0
    target_first_128_rows: int = 0
    target_first_128_task_opportunity_regret_sum: float = 0.0
    target_first_128_realized_return_sum: float = 0.0
    target_candidate_128_rows: int = 0
    target_candidate_128_task_opportunity_regret_sum: float = 0.0
    target_candidate_128_realized_return_sum: float = 0.0
    integrity_checks: dict[str, bool] = field(default_factory=dict)

    def public(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "seed": self.seed,
            "history_policy": self.history_policy,
            "world_variant": self.world_variant,
            "artifact_sha256": {
                START_NAME: self.start_sha256,
                ROWS_NAME: self.rows_sha256,
                SUMMARY_NAME: self.summary_sha256,
                FINISH_NAME: self.finish_sha256,
            },
            "source_sha256": self.source_sha256,
            "condition_config_sha256": self.condition_config_sha256,
            "row_count": self.row_count,
            "phase_counts": self.phase_counts,
            "prior_receipt_count": self.prior_receipt_count,
            "target": {
                "canonical_key": self.target_key,
                "candidate_time": self.target_candidate_time,
                "commit_time": self.target_commit_time,
                "candidate_to_commit_latency": (
                    None
                    if self.target_candidate_time is None
                    or self.target_commit_time is None
                    else self.target_commit_time - self.target_candidate_time
                ),
                "candidate_to_first_authorization_latency": (
                    None
                    if self.target_candidate_time is None
                    or self.target_authorization_time is None
                    else self.target_authorization_time - self.target_candidate_time
                ),
                "prior_digest": self.target_prior_digest,
                "prior_source_episode": self.target_prior_source_episode,
                "prior_source_key": self.target_prior_source_key,
                "candidate_rows": self.target_candidate_rows,
                "private_visible_rows": self.target_private_visible_rows,
                "fresh_on_before_commit": self.target_fresh_on_before_commit,
                "fresh_off_before_commit": self.target_fresh_off_before_commit,
                "fresh_probes_before_commit": (
                    self.target_fresh_probes_before_commit
                ),
                "fresh_probes_before_authorization": (
                    self.target_fresh_probes_before_authorization
                ),
                "total_fresh_probes": self.target_total_fresh_probes,
                "first_authorization_time": self.target_authorization_time,
                "ordinary_authorization_count": (
                    self.target_ordinary_authorization_count
                ),
                "episode_commits": self.target_episode_commits,
                "episode_count_before": self.target_episode_count_before,
                "episode_count_after": self.target_episode_count_after,
                "prior_quarantined": self.target_quarantine,
                "prior_compatible": self.target_compatible,
                "premature_count": self.target_premature_count,
                "stale_count": self.target_stale_count,
                "candidate_rejection_count": self.target_rejection_count,
                "first_128_rows": {
                    "row_count": self.target_first_128_rows,
                    "task_opportunity_regret_sum": (
                        self.target_first_128_task_opportunity_regret_sum
                    ),
                    "task_opportunity_regret_mean": (
                        self.target_first_128_task_opportunity_regret_sum
                        / self.target_first_128_rows
                    ),
                    "realized_return_sum": (
                        self.target_first_128_realized_return_sum
                    ),
                    "realized_return_mean": (
                        self.target_first_128_realized_return_sum
                        / self.target_first_128_rows
                    ),
                },
                "exploratory_candidate_aligned_128_rows": {
                    "exploratory_noncriterion": True,
                    "row_count": self.target_candidate_128_rows,
                    "transition_range": (
                        None
                        if self.target_candidate_time is None
                        else [
                            self.target_candidate_time,
                            self.target_candidate_time + 127,
                        ]
                    ),
                    "task_opportunity_regret_sum": (
                        self.target_candidate_128_task_opportunity_regret_sum
                    ),
                    "task_opportunity_regret_mean": (
                        self.target_candidate_128_task_opportunity_regret_sum
                        / self.target_candidate_128_rows
                    ),
                    "realized_return_sum": (
                        self.target_candidate_128_realized_return_sum
                    ),
                    "realized_return_mean": (
                        self.target_candidate_128_realized_return_sum
                        / self.target_candidate_128_rows
                    ),
                },
            },
            "universal_safety": {
                "premature_count": self.global_premature_count,
                "stale_count": self.global_stale_count,
                "commit_after_quarantined_prior_count": (
                    self.commit_after_quarantined_prior_count
                ),
            },
            "integrity_checks": self.integrity_checks,
        }


def _probe_accepted(grounding: Mapping[str, Any]) -> bool:
    return bool(
        grounding.get("mode") in {"probe_on", "probe_off"}
        and grounding.get("informative_probe")
        and grounding.get("normalized_causal_signal") is not None
        and grounding.get("actual_certificate_on")
        == grounding.get("requested_certificate_on")
    )


def _evidence_digest(signature_json: Any, evidence: Mapping[str, list[tuple[int, float]]]) -> str:
    return _canonical_sha256(
        {
            "signature": signature_json,
            "on": evidence["on"],
            "off": evidence["off"],
        }
    )


def _mean(records: list[tuple[int, float]]) -> float:
    _require(bool(records), "cannot average an empty primitive-evidence arm")
    return math.fsum(value for _time, value in records) / len(records)


def _verify_prior_receipt(
    receipt: Mapping[str, Any],
    *,
    policy: str,
    index: int,
    episodes: list[Episode],
    condition: str,
) -> Episode:
    prefix = f"{condition} row {index} prior"
    _require(receipt.get("schema") == PRIOR_SCHEMA, f"{prefix}: schema")
    _require(_is_sha256(receipt.get("digest")), f"{prefix}: digest malformed")
    _require(receipt["digest"] == _receipt_hash(receipt, "prior"), f"{prefix}: digest")
    _require(not bool(receipt.get("uses_evaluator_labels")), f"{prefix}: evaluator labels")
    _require(receipt.get("history_policy") == policy, f"{prefix}: policy")
    _require(policy in {"keyed", "generic"}, f"{prefix}: forbidden policy")
    target = _signature(receipt.get("target_signature"), f"{prefix} target signature")
    source = _signature(receipt.get("source_signature"), f"{prefix} source signature")
    _require(target != source, f"{prefix}: same certificate epoch reused")
    _require(
        receipt.get("target_epoch_binding_digest")
        == _target_binding_digest(receipt["target_signature"]),
        f"{prefix}: target epoch binding",
    )
    seeded = int(receipt.get("seeded_time", -1))
    _require(seeded == index, f"{prefix}: first receipt not emitted at seeded time")
    _require(
        int(receipt.get("source_certified_time", -1)) < seeded,
        f"{prefix}: source is not historical",
    )
    _require(
        receipt.get("prior_on_count") == 1 and receipt.get("prior_off_count") == 1,
        f"{prefix}: unequal/unbounded prior weight",
    )
    eligible = [
        episode
        for episode in episodes
        if episode.grounded_time < seeded and episode.signature != target
    ]
    _require(any(episode.canonical_key == _key(target) for episode in eligible), f"{prefix}: target was not a known route class")
    if policy == "keyed":
        eligible = [episode for episode in eligible if episode.canonical_key == _key(target)]
    _require(bool(eligible), f"{prefix}: no eligible source episode")
    expected = max(eligible, key=lambda episode: (episode.grounded_time, episode.episode_id))
    _require(expected.signature == source, f"{prefix}: source signature is not controller-selected latest eligible episode")
    _require(receipt.get("source_episode_id") == expected.episode_id, f"{prefix}: source episode ID")
    _require(receipt.get("source_identity_id") == expected.canonical_id, f"{prefix}: source identity ID")
    _require(int(receipt.get("source_certified_time", -1)) == expected.grounded_time, f"{prefix}: source certified time")
    _require(receipt.get("source_evidence_digest") == expected.evidence_digest, f"{prefix}: primitive source evidence digest")
    _require(math.isclose(float(receipt.get("on_value")), expected.on_mean, rel_tol=0.0, abs_tol=1e-12), f"{prefix}: source ON mean")
    _require(math.isclose(float(receipt.get("off_value")), expected.off_mean, rel_tol=0.0, abs_tol=1e-12), f"{prefix}: source OFF mean")
    if policy == "keyed":
        _require(expected.canonical_key == _key(target), f"{prefix}: keyed source crossed route key")
    return expected


def _audit_cell(
    directory: Path,
    condition: str,
    *,
    frozen_context: Mapping[str, Any] | None = None,
) -> CellAudit:
    policy, variant, prior_enabled = CONDITIONS[condition]
    _require(directory.is_dir(), f"missing condition directory {directory}")
    paths = {name: directory / name for name in (*ARTIFACT_FILES, ARTIFACT_NAME)}
    for name, path in paths.items():
        _require(path.is_file(), f"{condition}: missing {name}")

    artifacts = _mapping(_load_json(paths[ARTIFACT_NAME]), f"{condition} artifact manifest")
    _require(set(artifacts) == set(ARTIFACT_FILES), f"{condition}: artifact manifest file set")
    actual_hashes = {name: _sha256_file(paths[name]) for name in ARTIFACT_FILES}
    _require(artifacts == actual_hashes, f"{condition}: artifact hash mismatch")

    start = _mapping(_load_json(paths[START_NAME]), f"{condition} start receipt")
    finish = _mapping(_load_json(paths[FINISH_NAME]), f"{condition} finish receipt")
    summary = _mapping(_load_json(paths[SUMMARY_NAME]), f"{condition} summary")
    if frozen_context is None:
        _require(start.get("schema") == START_SCHEMA, f"{condition}: start schema")
        _require(finish.get("schema") == FINISH_SCHEMA, f"{condition}: finish schema")
        _require(start.get("development_only") is True and finish.get("development_only") is True, f"{condition}: not development-labelled")
    else:
        _require(start.get("schema") == FROZEN_START_SCHEMA, f"{condition}: frozen start schema")
        _require(finish.get("schema") == FROZEN_FINISH_SCHEMA, f"{condition}: frozen finish schema")
        for receipt_name, receipt in (("start", start), ("finish", finish)):
            _require(receipt.get("scientific_status") == FROZEN_SCIENTIFIC_STATUS, f"{condition}: {receipt_name} scientific status")
            _require(receipt.get("confirmatory") is False, f"{condition}: {receipt_name} confirmatory label")
            _require(receipt.get("freeze_bound") is True, f"{condition}: {receipt_name} is not freeze-bound")
            _require(receipt.get("freeze_sha256") == frozen_context.get("freeze_sha256"), f"{condition}: {receipt_name}/freeze binding")
            _require(receipt.get("source_set_sha256") == frozen_context.get("source_set_sha256"), f"{condition}: {receipt_name}/source-set binding")
            _require(receipt.get("seed_registry_sha256") == frozen_context.get("registry_sha256"), f"{condition}: {receipt_name}/registry binding")
        _require(start.get("source_archive_sha256") == frozen_context.get("source_archive_sha256"), f"{condition}: start/archive binding")
    seed = int(start.get("seed", -1))
    _require(seed >= 0 and int(finish.get("seed", -2)) == seed, f"{condition}: receipt seed mismatch")
    for receipt_name, receipt in (("start", start), ("finish", finish)):
        _require(receipt.get("condition_id") == condition, f"{condition}: {receipt_name} condition ID")
        _require(receipt.get("history_policy") == policy, f"{condition}: {receipt_name} history policy")
        _require(receipt.get("world_variant") == variant, f"{condition}: {receipt_name} world variant")
    _require(start.get("historical_prior_enabled") is prior_enabled, f"{condition}: prior switch")
    _require(start.get("expected_transition_count") == EXPECTED_ROWS, f"{condition}: start row count")
    _require(start.get("expected_phase_counts") == PHASE_COUNTS, f"{condition}: start phase counts")
    _require(_is_sha256(start.get("condition_config_sha256")), f"{condition}: condition config digest")
    source_hashes = _mapping(start.get("source_sha256"), f"{condition} source manifest")
    _require(bool(source_hashes) and all(_is_sha256(value) for value in source_hashes.values()), f"{condition}: source hashes")
    if frozen_context is not None:
        _require(source_hashes == frozen_context.get("source_sha256"), f"{condition}: start source manifest differs from freeze")
    _require(finish.get("start_receipt_sha256") == actual_hashes[START_NAME], f"{condition}: finish/start binding")
    _require(finish.get("rows_sha256") == actual_hashes[ROWS_NAME], f"{condition}: finish/rows binding")
    _require(finish.get("summary_sha256") == actual_hashes[SUMMARY_NAME], f"{condition}: finish/summary binding")
    _require(int(finish.get("rows_count", -1)) == EXPECTED_ROWS, f"{condition}: finish row count")
    _require(finish.get("integrity_complete") is True, f"{condition}: runner integrity incomplete")
    _require(summary.get("schema") == SUMMARY_SCHEMA, f"{condition}: summary schema")
    _require(int(summary.get("seed", -1)) == seed, f"{condition}: summary seed")
    summary_condition = _mapping(summary.get("condition"), f"{condition} summary condition")
    _require(summary_condition.get("history_policy") == policy, f"{condition}: summary history policy")
    _require(summary_condition.get("world_variant") == variant, f"{condition}: summary world variant")
    _require(summary.get("schedule") == [[name, count] for name, count in PHASE_STEPS], f"{condition}: summary schedule")
    if frozen_context is not None:
        _require(summary.get("scientific_status") == FROZEN_SCIENTIFIC_STATUS, f"{condition}: summary scientific status")
        _require(summary.get("confirmatory") is False, f"{condition}: summary confirmatory label")
        frozen_summary = _mapping(summary.get("frozen_pilot"), f"{condition} frozen summary binding")
        _require(frozen_summary.get("freeze_sha256") == frozen_context.get("freeze_sha256"), f"{condition}: summary/freeze binding")
        _require(frozen_summary.get("source_set_sha256") == frozen_context.get("source_set_sha256"), f"{condition}: summary/source binding")
        _require(frozen_summary.get("source_archive_sha256") == frozen_context.get("source_archive_sha256"), f"{condition}: summary/archive binding")
        _require(frozen_summary.get("seed_registry_sha256") == frozen_context.get("registry_sha256"), f"{condition}: summary/registry binding")

    cell = CellAudit(
        condition_id=condition,
        seed=seed,
        history_policy=policy,
        world_variant=variant,
        start_sha256=actual_hashes[START_NAME],
        rows_sha256=actual_hashes[ROWS_NAME],
        summary_sha256=actual_hashes[SUMMARY_NAME],
        finish_sha256=actual_hashes[FINISH_NAME],
        source_sha256=dict(source_hashes),
        condition_config_sha256=start["condition_config_sha256"],
    )
    evidence: dict[Signature, dict[str, list[tuple[int, float]]]] = {}
    signature_json: dict[Signature, Any] = {}
    episodes: list[Episode] = []
    episode_ids: set[str] = set()
    episode_signatures: set[Signature] = set()
    prior_replays: dict[str, PriorReplay] = {}
    prior_by_target: dict[Signature, PriorReplay] = {}
    target_probe_times: list[int] = []
    target_probe_records: list[tuple[int, str]] = []
    target_authorizations: list[int] = []
    last_episode_count = 0

    try:
        handle = paths[ROWS_NAME].open("rb")
    except OSError as exc:
        raise AuditError(f"{condition}: cannot open rows: {exc}") from exc
    with handle:
        for index, raw_line in enumerate(handle):
            _require(index < EXPECTED_ROWS, f"{condition}: too many rows")
            _require(raw_line.endswith(b"\n"), f"{condition} row {index}: missing LF")
            try:
                text = raw_line[:-1].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise AuditError(f"{condition} row {index}: invalid UTF-8") from exc
            row = _mapping(_loads(text, source=f"{condition} row {index}"), f"{condition} row {index}")
            _require(raw_line == _canonical_bytes(row) + b"\n", f"{condition} row {index}: noncanonical JSONL encoding")
            phase, offset = _phase_at(index)
            _require(int(row.get("transition_index", -1)) == index, f"{condition} row {index}: transition sequence")
            _require(int(row.get("seed", -1)) == seed, f"{condition} row {index}: seed")
            _require(row.get("phase") == phase and int(row.get("phase_offset", -1)) == offset, f"{condition} row {index}: phase/offset")
            _require(row.get("history_policy") == policy, f"{condition} row {index}: history policy")
            _require(row.get("world_variant_evaluator_only") == variant, f"{condition} row {index}: world variant")
            _require(float(row.get("task_return_multiplier_evaluator_only")) == _expected_multiplier(phase, variant), f"{condition} row {index}: functional multiplier")
            cell.phase_counts[phase] += 1

            grounding, reflexive, temporal = _verify_receipts(row, condition, index)
            v040_sha = _verify_wrappers(row, grounding, reflexive, temporal, condition, index)
            if index < TARGET_START:
                cell.pretarget_v040_sha256.append(v040_sha)

            exogenous_payload = {
                "phase": phase,
                "phase_offset": offset,
                "hidden_pair": row.get("hidden_pair_evaluator_only"),
                "hidden_rank": row.get("hidden_rank_evaluator_only"),
                "hidden_exogenous_source": row.get("hidden_exogenous_source_evaluator_only"),
                "process_bank_sha256": row.get("process_bank_sha256"),
                "process_bank_commitment_digest": row.get("process_bank_commitment_digest"),
                "observation_noise_sha256": row.get("observation_noise_sha256"),
                "return_noise": row.get("return_noise"),
                "task_context": row.get("task_context"),
            }
            cell.exogenous_sha256.append(_canonical_sha256(exogenous_payload))

            raw_signature_value = grounding.get("raw_signature")
            parsed_signature: Signature | None = None
            if raw_signature_value is not None:
                parsed_signature = _signature(raw_signature_value, f"{condition} row {index} raw signature")
                signature_json.setdefault(parsed_signature, raw_signature_value)
                _require(
                    temporal.get("canonical_key")
                    == [list(parsed_signature[0]), parsed_signature[1]],
                    f"{condition} row {index}: canonical key not derived from raw signature",
                )
            else:
                _require(temporal.get("canonical_key") is None, f"{condition} row {index}: key without signature")

            accepted = _probe_accepted(grounding)
            if accepted and parsed_signature is not None:
                arm = "on" if bool(grounding.get("actual_certificate_on")) else "off"
                signal = float(grounding["normalized_causal_signal"])
                evidence.setdefault(parsed_signature, {"on": [], "off": []})[arm].append((index, signal))

            issued = row.get("issued_historical_grounding_prior")
            active = row.get("historical_grounding_prior")
            compatibility = row.get("historical_prior_compatibility")
            if policy == "withheld":
                _require(issued is None and active is None and compatibility is None, f"{condition} row {index}: withheld arm received history")
                _require(temporal.get("historical_prior_digest") is None, f"{condition} row {index}: temporal prior in withheld arm")
            elif issued is not None:
                issued = _mapping(issued, f"{condition} row {index} issued prior")
                digest = issued.get("digest")
                _require(_is_sha256(digest), f"{condition} row {index}: issued prior digest")
                replay = prior_replays.get(digest)
                if replay is None:
                    source_episode = _verify_prior_receipt(
                        issued,
                        policy=policy,
                        index=index,
                        episodes=episodes,
                        condition=condition,
                    )
                    replay = PriorReplay(dict(issued), index)
                    prior_replays[digest] = replay
                    target_signature = _signature(issued["target_signature"], f"{condition} prior target")
                    _require(target_signature not in prior_by_target, f"{condition}: multiple priors for one target epoch")
                    prior_by_target[target_signature] = replay
                    cell.prior_receipt_count += 1
                else:
                    _require(dict(issued) == replay.receipt, f"{condition} row {index}: issued prior mutated")
                    source_episode = next(
                        episode
                        for episode in episodes
                        if episode.episode_id == issued["source_episode_id"]
                    )
                target_signature = _signature(issued["target_signature"], f"{condition} prior target")
                _require(parsed_signature == target_signature, f"{condition} row {index}: prior/candidate target mismatch")

                if accepted and parsed_signature == target_signature and not replay.quarantined and not replay.compatible:
                    target_value = float(issued["on_value"] if grounding.get("actual_certificate_on") else issued["off_value"])
                    is_compatible = abs(float(grounding["normalized_causal_signal"]) - target_value) <= COMPATIBILITY_TOLERANCE
                    replay.accepted_probe_count += 1
                    if not is_compatible:
                        replay.expected_state = "quarantined"
                        replay.quarantined = True
                    elif grounding.get("actual_certificate_on") and replay.expected_state == "pending":
                        replay.expected_state = "on_compatible"
                    elif not grounding.get("actual_certificate_on") and replay.expected_state == "on_compatible":
                        replay.expected_state = "compatible"
                        replay.compatible = True
                _require(compatibility == replay.expected_state, f"{condition} row {index}: prior compatibility replay mismatch")
                if replay.quarantined:
                    _require(active is None, f"{condition} row {index}: quarantined prior remained active")
                    _require(temporal.get("historical_prior_digest") is None, f"{condition} row {index}: temporal layer consumed quarantined prior")
                else:
                    _require(isinstance(active, dict) and active.get("digest") == digest, f"{condition} row {index}: active/issued prior mismatch")
                    _require(_receipt_hash(active, "prior") == digest, f"{condition} row {index}: active prior digest")
                    _require(temporal.get("historical_prior_digest") == digest, f"{condition} row {index}: temporal/prior binding")

                if phase == TARGET_PHASE:
                    if cell.target_prior_digest is None:
                        cell.target_prior_digest = digest
                        cell.target_prior_source_episode = issued["source_episode_id"]
                        cell.target_prior_source_key = source_episode.canonical_key
                    _require(cell.target_prior_digest == digest, f"{condition}: target prior changed")
                    cell.target_quarantine = cell.target_quarantine or replay.quarantined
                    cell.target_compatible = cell.target_compatible or replay.compatible
            else:
                _require(active is None and compatibility is None, f"{condition} row {index}: active prior without issued receipt")

            events = temporal.get("events")
            _require(isinstance(events, list), f"{condition} row {index}: temporal events malformed")
            premature_here = bool(
                temporal.get("premature_ordinary_authorization_detected")
                or "ordinary_action_before_fresh_grounding" in events
            )
            stale_here = bool(
                temporal.get("stale_certificate_reuse_detected")
                or "stale_identity_certificate_reused" in events
            )
            cell.global_premature_count += int(premature_here)
            cell.global_stale_count += int(stale_here)
            if any(event in events for event in ("novel_identity_grounded", "known_identity_returned_grounded")):
                _require(bool(temporal.get("fresh_grounding_satisfied")), f"{condition} row {index}: episode without fresh grounding")
                _require(parsed_signature is not None, f"{condition} row {index}: episode without signature")
                records = evidence.get(parsed_signature, {"on": [], "off": []})
                _require(bool(records["on"]) and bool(records["off"]), f"{condition} row {index}: episode lacks primitive ON/OFF evidence")
                canonical_id = temporal.get("active_identity_after")
                episode_id = temporal.get("active_episode_after")
                _require(isinstance(canonical_id, str) and isinstance(episode_id, str), f"{condition} row {index}: episode identifiers")
                _require(episode_id not in episode_ids, f"{condition} row {index}: episode ID reused")
                _require(parsed_signature not in episode_signatures, f"{condition} row {index}: certificate epoch committed twice")
                episode_ids.add(episode_id)
                episode_signatures.add(parsed_signature)
                target_replay = prior_by_target.get(parsed_signature)
                if target_replay is not None and target_replay.quarantined:
                    cell.commit_after_quarantined_prior_count += 1
                episodes.append(
                    Episode(
                        signature=parsed_signature,
                        signature_json=raw_signature_value,
                        canonical_key=_key(parsed_signature),
                        canonical_id=canonical_id,
                        episode_id=episode_id,
                        grounded_time=index,
                        evidence_digest=_evidence_digest(raw_signature_value, records),
                        on_mean=_mean(records["on"]),
                        off_mean=_mean(records["off"]),
                    )
                )

            if phase == TARGET_PHASE:
                if index == TARGET_START:
                    cell.target_episode_count_before = last_episode_count
                    hidden_pair = row.get("hidden_pair_evaluator_only")
                    hidden_rank = row.get("hidden_rank_evaluator_only")
                    _require(isinstance(hidden_pair, list) and len(hidden_pair) == 2 and _integer(hidden_rank), f"{condition}: target hidden route malformed")
                    cell.target_key = ((int(hidden_pair[0]), int(hidden_pair[1])), int(hidden_rank))
                if index < TARGET_START + 128:
                    regret = float(row.get("task_opportunity_regret_evaluator_only"))
                    realized = float(row.get("realized_external_return"))
                    _require(math.isfinite(regret) and math.isfinite(realized), f"{condition} row {index}: nonfinite fixed-window metric")
                    cell.target_first_128_rows += 1
                    cell.target_first_128_task_opportunity_regret_sum += regret
                    cell.target_first_128_realized_return_sum += realized
                if parsed_signature is not None and _key(parsed_signature) == cell.target_key:
                    cell.target_candidate_rows += 1
                    if cell.target_candidate_time is None:
                        cell.target_candidate_time = index
                    if grounding.get("private_boundary_active"):
                        cell.target_private_visible_rows += 1
                    if accepted:
                        target_probe_times.append(index)
                        target_probe_records.append(
                            (
                                index,
                                "on"
                                if bool(grounding.get("actual_certificate_on"))
                                else "off",
                            )
                        )
                    if (
                        grounding.get("mode") == "ordinary_use"
                        and grounding.get("actual_certificate_on")
                    ):
                        cell.target_ordinary_authorization_count += 1
                        if row.get("temporal_action_authorization_digest") is not None:
                            target_authorizations.append(index)
                if (
                    cell.target_candidate_time is not None
                    and index < cell.target_candidate_time + 128
                ):
                    candidate_regret = float(
                        row.get("task_opportunity_regret_evaluator_only")
                    )
                    candidate_realized = float(row.get("realized_external_return"))
                    _require(
                        math.isfinite(candidate_regret)
                        and math.isfinite(candidate_realized),
                        f"{condition} row {index}: nonfinite exploratory metric",
                    )
                    cell.target_candidate_128_rows += 1
                    cell.target_candidate_128_task_opportunity_regret_sum += (
                        candidate_regret
                    )
                    cell.target_candidate_128_realized_return_sum += (
                        candidate_realized
                    )
                if "novel_identity_grounded" in events or "known_identity_returned_grounded" in events:
                    cell.target_episode_commits += 1
                    if cell.target_commit_time is None:
                        cell.target_commit_time = index
                if premature_here:
                    cell.target_premature_count += 1
                if stale_here:
                    cell.target_stale_count += 1
                grounding_events = grounding.get("events")
                _require(isinstance(grounding_events, list), f"{condition} row {index}: grounding events malformed")
                if "candidate_rejected_by_consequence" in grounding_events:
                    cell.target_rejection_count += 1

            last_episode_count = int(temporal.get("identity_episode_count", -1))
            _require(last_episode_count == len(episode_ids), f"{condition} row {index}: episode count does not replay")
            cell.row_count = index + 1

    _require(cell.row_count == EXPECTED_ROWS, f"{condition}: row count {cell.row_count}")
    _require(cell.phase_counts == PHASE_COUNTS, f"{condition}: phase counts")
    cell.target_episode_count_after = last_episode_count
    cell.target_total_fresh_probes = len(target_probe_times)
    if cell.target_commit_time is not None:
        cell.target_fresh_on_before_commit = sum(
            time <= cell.target_commit_time and arm == "on"
            for time, arm in target_probe_records
        )
        cell.target_fresh_off_before_commit = sum(
            time <= cell.target_commit_time and arm == "off"
            for time, arm in target_probe_records
        )
        cell.target_fresh_probes_before_commit = sum(
            time <= cell.target_commit_time for time in target_probe_times
        )
    if target_authorizations:
        cell.target_authorization_time = min(target_authorizations)
        cell.target_fresh_probes_before_authorization = sum(
            time < cell.target_authorization_time for time in target_probe_times
        )
    _require(cell.target_key is not None, f"{condition}: no target key")
    _require(cell.target_first_128_rows == 128, f"{condition}: fixed first-128 target window incomplete")
    _require(
        cell.target_candidate_128_rows == 128,
        f"{condition}: exploratory candidate-aligned window incomplete",
    )
    _require(cell.target_candidate_rows > 0, f"{condition}: target candidate never appeared")
    _require(cell.target_private_visible_rows == cell.target_candidate_rows, f"{condition}: target same-key candidate was not privately visible")

    cell.integrity_checks = {
        "artifact_hashes_recompute": True,
        "receipt_chain_recomputes": True,
        "all_rows_canonical": True,
        "layered_wrapper_hashes_recompute": True,
        "action_authorization_hashes_recompute": True,
        "condition_fields_exact": True,
        "phase_schedule_exact": True,
        "prior_sources_reconstructed_from_primitive_rows": True,
        "episode_counts_replay": True,
        "certificate_epochs_unique": len(episode_signatures) == len(episode_ids),
        "zero_global_premature_authorization": cell.global_premature_count == 0,
        "zero_global_stale_epoch_reuse": cell.global_stale_count == 0,
        "zero_commit_after_quarantined_prior": (
            cell.commit_after_quarantined_prior_count == 0
        ),
    }
    return cell


def _compare_vectors(cells: Mapping[str, CellAudit], attribute: str) -> bool:
    values = [getattr(cells[name], attribute) for name in CONDITIONS]
    return all(value == values[0] for value in values[1:])


def audit_matrix(matrix_root: Path) -> dict[str, Any]:
    matrix_root = matrix_root.resolve(strict=True)
    cells: dict[str, CellAudit] = {}
    for condition in CONDITIONS:
        cells[condition] = _audit_cell(matrix_root / condition, condition)

    seeds = {cell.seed for cell in cells.values()}
    versions = {
        _load_json(matrix_root / condition / START_NAME).get("version")
        for condition in CONDITIONS
    }
    source_manifests_equal = len(
        {_canonical_sha256(cell.source_sha256) for cell in cells.values()}
    ) == 1
    exogenous_yoked = _compare_vectors(cells, "exogenous_sha256")
    pretarget_variant_blind = all(
        cells[f"{policy}_RPLUS"].pretarget_v040_sha256
        == cells[f"{policy}_RMINUS"].pretarget_v040_sha256
        for policy in ("K", "N", "G")
    )

    k_plus = cells["K_RPLUS"]
    n_plus = cells["N_RPLUS"]
    g_plus = cells["G_RPLUS"]
    plus_safe = all(
        cell.target_premature_count == 0
        and cell.target_stale_count == 0
        and cell.target_authorization_time is not None
        and cell.target_episode_commits == 1
        and cell.target_episode_count_after == cell.target_episode_count_before + 1
        for cell in (k_plus, n_plus, g_plus)
    )
    keyed_efficacy = bool(
        k_plus.target_fresh_probes_before_authorization is not None
        and n_plus.target_fresh_probes_before_authorization is not None
        and g_plus.target_fresh_probes_before_authorization is not None
        and k_plus.target_fresh_probes_before_authorization
        < n_plus.target_fresh_probes_before_authorization
        and k_plus.target_fresh_probes_before_authorization
        < g_plus.target_fresh_probes_before_authorization
    )
    plus_prior_pattern = bool(
        k_plus.target_prior_digest is not None
        and k_plus.target_compatible
        and not k_plus.target_quarantine
        and n_plus.target_prior_digest is None
        and g_plus.target_prior_digest is not None
        and g_plus.target_quarantine
        and not g_plus.target_compatible
        and k_plus.target_prior_source_key == k_plus.target_key
        and g_plus.target_prior_source_key != g_plus.target_key
    )

    minus_cells = [cells[name] for name in ("K_RMINUS", "N_RMINUS", "G_RMINUS")]
    minus_fail_closed = all(
        cell.target_ordinary_authorization_count == 0
        and cell.target_authorization_time is None
        and cell.target_episode_commits == 0
        and cell.target_episode_count_after == cell.target_episode_count_before
        and cell.target_premature_count == 0
        and cell.target_stale_count == 0
        for cell in minus_cells
    )
    minus_prior_pattern = bool(
        cells["K_RMINUS"].target_prior_digest is not None
        and cells["K_RMINUS"].target_quarantine
        and cells["N_RMINUS"].target_prior_digest is None
        and cells["G_RMINUS"].target_prior_digest is not None
        and cells["G_RMINUS"].target_quarantine
    )
    target_keys_equal = len({cell.target_key for cell in cells.values()}) == 1
    prequential_prior_world_blind = bool(
        cells["K_RPLUS"].target_prior_digest
        == cells["K_RMINUS"].target_prior_digest
        and cells["G_RPLUS"].target_prior_digest
        == cells["G_RMINUS"].target_prior_digest
    )

    criteria = {
        "M01_exact_six_conditions": set(cells) == set(CONDITIONS),
        "M02_one_yoked_seed_and_version": len(seeds) == 1 and len(versions) == 1,
        "M03_identical_registered_source": source_manifests_equal,
        "M04_exogenous_streams_yoked": exogenous_yoked,
        "M05_world_variant_absent_from_pretarget_runtime": pretarget_variant_blind,
        "M06_target_same_structural_key_all_cells": target_keys_equal,
        "M07_historical_receipts_prequential_across_world_variants": (
            prequential_prior_world_blind
        ),
        "M08_rplus_all_arms_safe_and_authorized": plus_safe,
        "M09_rplus_keyed_uses_fewer_fresh_probes_than_withheld_and_generic": (
            keyed_efficacy
        ),
        "M10_rplus_prior_specificity_pattern": plus_prior_pattern,
        "M11_rminus_all_arms_fail_closed_without_episode_commit": (
            minus_fail_closed
        ),
        "M12_rminus_keyed_and_generic_priors_quarantined": minus_prior_pattern,
    }
    all_met = all(criteria.values())
    return {
        "schema": "rrct.v041.development_matrix.independent_audit.v1",
        "version": "0.41.1.dev2",
        "development_only": True,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "matrix_root": matrix_root.as_posix(),
        "seed": next(iter(seeds)) if len(seeds) == 1 else sorted(seeds),
        "conditions": {name: cells[name].public() for name in CONDITIONS},
        "primary_contrasts": {
            "K_RPLUS_fresh_probes": k_plus.target_fresh_probes_before_authorization,
            "N_RPLUS_fresh_probes": n_plus.target_fresh_probes_before_authorization,
            "G_RPLUS_fresh_probes": g_plus.target_fresh_probes_before_authorization,
            "keyed_less_than_withheld": (
                k_plus.target_fresh_probes_before_authorization
                < n_plus.target_fresh_probes_before_authorization
                if k_plus.target_fresh_probes_before_authorization is not None
                and n_plus.target_fresh_probes_before_authorization is not None
                else False
            ),
            "keyed_less_than_generic": (
                k_plus.target_fresh_probes_before_authorization
                < g_plus.target_fresh_probes_before_authorization
                if k_plus.target_fresh_probes_before_authorization is not None
                and g_plus.target_fresh_probes_before_authorization is not None
                else False
            ),
            "rminus_target_authorizations": {
                cell.condition_id: cell.target_ordinary_authorization_count
                for cell in minus_cells
            },
            "rminus_target_episode_commits": {
                cell.condition_id: cell.target_episode_commits
                for cell in minus_cells
            },
        },
        "secondary_descriptive_first_128_target_rows": {
            name: {
                "task_opportunity_regret_sum": (
                    cells[name].target_first_128_task_opportunity_regret_sum
                ),
                "realized_return_sum": (
                    cells[name].target_first_128_realized_return_sum
                ),
            }
            for name in CONDITIONS
        },
        "secondary_metric_interpretation": {
            "window_transition_range": [TARGET_START, TARGET_START + 127],
            "all_candidates_appear_after_window": all(
                cells[name].target_candidate_time is not None
                and cells[name].target_candidate_time >= TARGET_START + 128
                for name in CONDITIONS
            ),
            "rplus_regret_is_equal_across_history_policies": len(
                {
                    cells[name].target_first_128_task_opportunity_regret_sum
                    for name in ("K_RPLUS", "N_RPLUS", "G_RPLUS")
                }
            )
            == 1,
            "realized_return_is_equal_across_all_six_cells": len(
                {
                    cells[name].target_first_128_realized_return_sum
                    for name in CONDITIONS
                }
            )
            == 1,
            "scientific_note": (
                "The frozen first-128 target-phase window ends before the raw "
                "target candidate becomes visible in this schedule. It therefore "
                "shows no K/N/G performance separation and is descriptive, not "
                "evidence for a reward or regret advantage."
            ),
        },
        "exploratory_secondary_candidate_aligned_128_rows": {
            "exploratory_noncriterion": True,
            "scientific_note": (
                "Post-hoc descriptive window aligned to each arm's first raw "
                "target-candidate row. It was not a predeclared pass criterion "
                "and must not be used to change the 12-criterion audit result."
            ),
            "conditions": {
                name: {
                    "transition_range": [
                        cells[name].target_candidate_time,
                        cells[name].target_candidate_time + 127,
                    ],
                    "task_opportunity_regret_sum": (
                        cells[
                            name
                        ].target_candidate_128_task_opportunity_regret_sum
                    ),
                    "realized_return_sum": (
                        cells[name].target_candidate_128_realized_return_sum
                    ),
                }
                for name in CONDITIONS
            },
        },
        "matrix_criteria": criteria,
        "all_criteria_met": all_met,
        "status": (
            "V041_DEVELOPMENT_MATRIX_AUDIT_PASS"
            if all_met
            else "V041_DEVELOPMENT_MATRIX_AUDIT_FAIL"
        ),
        "interpretation_boundary": (
            "Independent replay of one exposed, development-only six-cell "
            "matrix. A pass discriminates keyed temporal history from withheld "
            "and recency-generic history in this bounded implementation and "
            "requires fail-closed behavior on a same-key/null-function lure. "
            "It is not a frozen fresh-seed result or a subjective-awareness claim."
        ),
    }


def _write_report(path: Path, report: Mapping[str, Any]) -> str:
    encoded = (
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently audit the RRCT v0.41 six-cell development matrix."
    )
    parser.add_argument("--matrix-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="optional audit JSON destination (default: stdout only)",
    )
    args = parser.parse_args()
    try:
        report = audit_matrix(args.matrix_root)
        output_sha = None
        if args.output is not None:
            output_sha = _write_report(args.output.resolve(), report)
        display = {
            "status": report["status"],
            "all_criteria_met": report["all_criteria_met"],
            "seed": report["seed"],
            "primary_contrasts": report["primary_contrasts"],
            "matrix_criteria": report["matrix_criteria"],
            "output": None if args.output is None else args.output.resolve().as_posix(),
            "output_sha256": output_sha,
        }
        print(json.dumps(display, indent=2, sort_keys=True, allow_nan=False), flush=True)
        return 0 if report["all_criteria_met"] else 1
    except Exception as exc:
        failure = {
            "schema": "rrct.v041.development_matrix.independent_audit_failure.v1",
            "audited_at_utc": datetime.now(timezone.utc).isoformat(),
            "matrix_root": args.matrix_root.resolve(strict=False).as_posix(),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "status": "V041_DEVELOPMENT_MATRIX_AUDIT_ERROR",
        }
        if args.output is not None:
            failure["output_sha256"] = _write_report(args.output.resolve(), failure)
        print(json.dumps(failure, indent=2, sort_keys=True, allow_nan=False), file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
