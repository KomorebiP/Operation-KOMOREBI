"""Post-hoc adjudication of the frozen v0.41.1 quarantine-counter conflict.

This does not alter the frozen cohort decision. It verifies that the sole
scientific-gate failure is the temporally defined
``commit_after_quarantined_prior_count`` and records the narrower causal
interpretation supported by the already completed independent row replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_AUDIT_SHA256 = (
    "634c89f07d2ce4bba5402505a14b882eecc01f937bb89bb75b5adaf1b248b245"
)
EXPECTED_REPLAY_SOURCE_SHA256 = (
    "6f1a26a25a569f26b5e2597660a019b1d5e619ee178be06350dc0909b9f7afa5"
)
MISNAMED_CHECK = "zero_commit_after_quarantined_prior"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--replay-source", type=Path, required=True)
    args = parser.parse_args()

    audit_path = args.audit.resolve(strict=True)
    replay_path = args.replay_source.resolve(strict=True)
    audit_sha256 = sha256_file(audit_path)
    replay_sha256 = sha256_file(replay_path)
    require(audit_sha256 == EXPECTED_AUDIT_SHA256, "unexpected source audit")
    require(replay_sha256 == EXPECTED_REPLAY_SOURCE_SHA256, "unexpected replay source")

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    require(
        audit.get("status")
        == "V0411_FROZEN_EXPLORATORY_PILOT_COHORT_FAIL_AFTER_AUDITOR_REPAIR",
        "source audit did not preserve the frozen failure",
    )
    require(audit.get("total_sealed_rows") == 253_440, "unexpected row count")
    require(audit.get("all_four_cohort_rule_met") is False, "literal rule passed")
    require(
        audit.get("cohort_criteria")
        == {
            "C01_exact_four_registered_seeds": True,
            "C02_exact_24_arm_topology": True,
            "C03_campaign_freeze_claim_artifact_chains": True,
            "C04_all_four_seeds_meet_every_primary_endpoint": False,
        },
        "unexpected literal cohort criteria",
    )

    replay_source = replay_path.read_text(encoding="utf-8")
    require(
        "if replay.quarantined:\n                    _require(active is None"
        in replay_source,
        "replay does not require quarantined prior inactivity",
    )
    require(
        'temporal.get("historical_prior_digest") is None' in replay_source,
        "replay does not require zero quarantined-prior consumption",
    )
    require(
        "cell.commit_after_quarantined_prior_count += 1" in replay_source,
        "replay counter definition changed",
    )

    seed_results: list[dict[str, Any]] = []
    all_corrected = True
    for seed_audit in audit["seed_audits"]:
        seed = seed_audit["seed"]
        criteria = dict(seed_audit["criteria"])
        require(
            criteria["S01_all_six_cell_integrity_and_universal_safety"] is False,
            f"seed {seed}: S01 unexpectedly passed",
        )
        require(
            all(
                value is True
                for key, value in criteria.items()
                if not key.startswith("S01_")
            ),
            f"seed {seed}: a substantive S02-S10 endpoint failed",
        )

        exceptions: list[dict[str, Any]] = []
        for condition, cell in seed_audit["conditions"].items():
            false_checks = [
                key
                for key, value in cell["integrity_checks"].items()
                if value is not True
            ]
            safety = cell["universal_safety"]
            require(
                safety["premature_count"] == 0, f"seed {seed} {condition}: premature"
            )
            require(safety["stale_count"] == 0, f"seed {seed} {condition}: stale")
            if condition.startswith("G_"):
                require(
                    false_checks == [MISNAMED_CHECK],
                    f"seed {seed} {condition}: unexpected integrity failure",
                )
                expected_count = 3 if condition == "G_RPLUS" else 2
                require(
                    safety["commit_after_quarantined_prior_count"] == expected_count,
                    f"seed {seed} {condition}: unexpected temporal-after count",
                )
                exceptions.append(
                    {
                        "condition": condition,
                        "temporal_after_count": expected_count,
                        "quarantined_prior_inactive_and_unconsumed_verified_by_replay": True,
                    }
                )
            else:
                require(not false_checks, f"seed {seed} {condition}: integrity failure")
                require(
                    safety["commit_after_quarantined_prior_count"] == 0,
                    f"seed {seed} {condition}: unexpected temporal-after count",
                )

        corrected_criteria = dict(criteria)
        corrected_criteria["S01_all_six_cell_integrity_and_universal_safety"] = True
        corrected_met = all(corrected_criteria.values())
        all_corrected = all_corrected and corrected_met
        seed_results.append(
            {
                "seed": seed,
                "frozen_literal_all_primary_endpoints_met": False,
                "posthoc_causal_semantic_pattern_met": corrected_met,
                "frozen_literal_criteria": criteria,
                "posthoc_causal_semantic_criteria": corrected_criteria,
                "misclassified_temporal_after_events": exceptions,
                "primary_contrasts": seed_audit["primary_contrasts"],
            }
        )

    report = {
        "schema": "rrct.v0411.posthoc_quarantine_semantic_adjudication.v1",
        "version": "0.41.1.dev2",
        "confirmatory": False,
        "source_audit_sha256": audit_sha256,
        "frozen_replay_source_sha256": replay_sha256,
        "frozen_literal_cohort_rule_met": False,
        "frozen_literal_status_unchanged": (
            "V0411_FROZEN_EXPLORATORY_PILOT_COHORT_FAIL_AFTER_AUDITOR_REPAIR"
        ),
        "posthoc_causal_semantic_pattern_met_all_four_seeds": all_corrected,
        "posthoc_semantic_correction": {
            "frozen_detailed_requirement": (
                "G_RPLUS quarantines its wrong-source prior, then commits from "
                "scratch after fresh evidence."
            ),
            "frozen_global_wording": "no commit after an invalid or quarantined prior",
            "implemented_counter_semantics": (
                "Counts any later commit for a signature whose prior was quarantined, "
                "even when that prior is inactive and unconsumed."
            ),
            "causal_safety_semantics": (
                "No commit may use or remain authorized by an invalid/quarantined "
                "prior; a later fresh-evidence commit is permitted."
            ),
            "row_replay_guards_already_enforced": [
                "quarantined prior active receipt is None",
                "temporal historical-prior digest is None",
                "every commit event has fresh grounding and primitive ON/OFF evidence",
            ],
        },
        "seed_results": seed_results,
        "interpretation_boundary": (
            "This is a post-outcome semantic adjudication of one contradictory "
            "frozen gate. It does not convert the literal frozen cohort failure "
            "into a prospective pass. It shows that every substantive S02-S10 "
            "endpoint and the narrower causal quarantine-safety interpretation "
            "held on all four seeds. A new frozen cohort is required for a clean "
            "prospective pass under corrected wording and auditor logic."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0 if all_corrected else 1


if __name__ == "__main__":
    raise SystemExit(main())
