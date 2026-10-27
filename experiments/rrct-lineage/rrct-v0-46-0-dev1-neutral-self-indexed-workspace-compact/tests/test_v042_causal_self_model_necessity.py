"""Focused checks for v0.42 causal self-model necessity."""
from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
import shutil

import pytest

from rrct.autonomous_self_diagnosis import (
    _digest as _grounding_digest,
    _grounding_receipt_payload,
)
from rrct.autonomous_self_diagnosis_experiment import _agent_v039
from rrct.causal_self_model_necessity import (
    CausalSelfModelInterventionConfig,
    CausalSelfModelNecessityUnifiedCausalLoop,
    validate_self_model_action_authorization_receipt,
    validate_self_model_commit_event_receipt,
    validate_self_model_counterfactual_receipt,
    validate_self_model_intervention_receipt,
    validate_self_model_receipt_chain,
)
from rrct.causal_self_model_necessity_analysis import (
    ArchivedArmOutcome,
    ArchivedCausalContrastReceipt,
    analyze_summary_directory,
    validate_archived_causal_contrast_receipt,
)
from rrct.post_change_closure_experiment import (
    V037ExperimentConfig,
    run_post_change_closure_trace,
)
from rrct.robust_reflexive_diagnosis import RobustReflexiveDiagnosticController
from rrct.temporal_self_identity import (
    TemporalSelfIdentityConfig,
    _digest as _temporal_digest,
)
from rrct.unified_causal_loop_experiment import _boundary_config
from tests.test_v039_autonomous_self_diagnosis import (
    _certificate,
    _outcome,
    _result,
    _selection,
)
from tests.test_v041_temporal_self_identity import _grounding, _observe


def _rehashed_grounding(receipt, *, signature, certificate_digest):
    updated = replace(
        receipt,
        raw_signature=signature,
        raw_certificate_digest=certificate_digest,
        digest="",
    )
    return replace(
        updated,
        digest=_grounding_digest(_grounding_receipt_payload(updated)),
    )


def _runtime_with_two_grounded_identities(mode: str):
    seed = 42001
    runtime = CausalSelfModelNecessityUnifiedCausalLoop(
        _agent_v039(_boundary_config(seed), seed),
        temporal_identity_config=TemporalSelfIdentityConfig(
            historical_prior_enabled=True,
            history_policy="keyed",
        ),
        intervention_config=CausalSelfModelInterventionConfig(
            mode=mode,  # type: ignore[arg-type]
            target_known_return_ordinal=1,
        ),
    )
    temporal = runtime.temporal_identity
    robust = RobustReflexiveDiagnosticController()

    # Identity A, with a consequence prototype near ON=1 and OFF=0.
    _observe(
        temporal,
        robust,
        _grounding(0, epoch=1, events=("initial_boundary_certified",)),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            1,
            epoch=1,
            events=("certificate_revoked_by_consequence",),
            status_after="revoked",
            diagnosis="boundary_effect_failed",
        ),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            2,
            epoch=None,
            actual=False,
            status_before=None,
            status_after=None,
            events=("boundary_absent",),
            diagnosis="boundary_absent",
        ),
    )

    # Identity B is deliberately given a different prototype and grounded later,
    # so generic history selects it while keyed history still selects A.
    b_signature = ((3, 4), 2, 2)
    temporal._fresh_evidence[b_signature] = {
        "on": [(3, 0.35), (3, 0.40)],
        "off": [(3, -0.20), (3, -0.15)],
    }
    b_grounding = _rehashed_grounding(
        _grounding(3, epoch=2, events=("boundary_remapped",)),
        signature=b_signature,
        certificate_digest="b" * 64,
    )
    _observe(temporal, robust, b_grounding)
    _observe(
        temporal,
        robust,
        _rehashed_grounding(
            _grounding(
                4,
                epoch=2,
                events=("certificate_revoked_by_consequence",),
                status_after="revoked",
                diagnosis="boundary_effect_failed",
            ),
            signature=b_signature,
            certificate_digest="b" * 64,
        ),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            5,
            epoch=None,
            actual=False,
            status_before=None,
            status_after=None,
            events=("boundary_absent",),
            diagnosis="boundary_absent",
        ),
    )
    return runtime


def _runtime_with_one_grounded_identity(mode: str):
    seed = 42000
    runtime = CausalSelfModelNecessityUnifiedCausalLoop(
        _agent_v039(_boundary_config(seed), seed),
        temporal_identity_config=TemporalSelfIdentityConfig(
            historical_prior_enabled=True,
            history_policy="keyed",
        ),
        intervention_config=CausalSelfModelInterventionConfig(
            mode=mode,  # type: ignore[arg-type]
            target_known_return_ordinal=1,
        ),
    )
    temporal = runtime.temporal_identity
    robust = RobustReflexiveDiagnosticController()
    _observe(
        temporal,
        robust,
        _grounding(0, epoch=1, events=("initial_boundary_certified",)),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            1,
            epoch=1,
            events=("certificate_revoked_by_consequence",),
            status_after="revoked",
            diagnosis="boundary_effect_failed",
        ),
    )
    _observe(
        temporal,
        robust,
        _grounding(
            2,
            epoch=None,
            actual=False,
            status_before=None,
            status_after=None,
            events=("boundary_absent",),
            diagnosis="boundary_absent",
        ),
    )
    return runtime


def test_surgical_intervention_is_model_triggered_and_policy_specific() -> None:
    for mode in ("intact", "withhold_target", "swap_target"):
        runtime = _runtime_with_two_grounded_identities(mode)
        certificate = replace(_certificate(epoch=3), digest="e" * 64)
        signature = certificate.structural_signature
        ordinal = runtime._known_return_ordinal(signature)
        assert ordinal == 1
        counterfactual = runtime._build_counterfactual(
            time=6,
            signature=signature,
            ordinal=ordinal,
        )
        runtime._target_signature = signature
        runtime._target_counterfactual = counterfactual
        policy = "generic" if mode == "swap_target" else "keyed"
        issued = runtime.temporal_identity.prepare_historical_prior(
            certificate,
            time=6,
            policy_override=policy,
            exclude_target_key=(policy == "generic"),
        )
        delivered, intervention = runtime._intervention_for(
            time=6,
            signature=signature,
            issued=issued,
            ordinal=ordinal,
        )
        assert validate_self_model_counterfactual_receipt(counterfactual)
        assert validate_self_model_intervention_receipt(intervention)
        assert not counterfactual.uses_evaluator_labels
        assert not intervention.uses_evaluator_labels
        predictions = {item.mode: item for item in counterfactual.predictions}
        assert predictions["intact"].minimum_fresh_on_samples == 1
        assert predictions["intact"].minimum_fresh_off_samples == 1
        assert predictions["withhold_target"].minimum_fresh_on_samples == 2
        assert predictions["swap_target"].minimum_fresh_off_samples == 2

        if mode == "intact":
            assert delivered is not None
            assert delivered.history_policy == "keyed"
            assert delivered.source_identity_id == "identity-0001"
        elif mode == "withhold_target":
            assert delivered is None
            assert intervention.issued_prior_policy == "keyed"
        else:
            assert delivered is not None
            assert delivered.history_policy == "generic"
            assert delivered.source_identity_id == "identity-0002"
            assert delivered.source_signature[:2] != signature[:2]
            assert (
                intervention.issued_source_signature[:2]
                != intervention.target_signature[:2]
            )


def test_wrong_source_prior_is_removed_after_fresh_consequence_mismatch() -> None:
    runtime = _runtime_with_two_grounded_identities("swap_target")
    certificate = replace(_certificate(epoch=3), digest="e" * 64)
    signature = certificate.structural_signature
    ordinal = runtime._known_return_ordinal(signature)
    assert ordinal == 1
    runtime._target_signature = signature
    runtime._target_counterfactual = runtime._build_counterfactual(
        time=6,
        signature=signature,
        ordinal=ordinal,
    )
    issued = runtime.temporal_identity.prepare_historical_prior(
        certificate,
        time=6,
        policy_override="generic",
        exclude_target_key=True,
    )
    delivered, _receipt = runtime._intervention_for(
        time=6,
        signature=signature,
        issued=issued,
        ordinal=ordinal,
    )
    assert delivered is not None
    assert runtime.grounding.apply_historical_prior(
        certificate, delivered, time=6
    ) is not None
    assert runtime.grounding.compatibility_for(signature) == "pending"

    plan = runtime.grounding.plan(
        time=6,
        raw_certificate=certificate,
        result=_result(),
    )
    runtime.grounding.finalize_gate(
        plan, certificate if plan.requested_certificate_on else None
    )
    runtime.grounding.bind_selection(plan, _selection(6))
    actual_value = 1.0 if plan.actual_certificate_on else 0.0
    runtime.grounding.observe(plan, _outcome(6, actual_value))
    assert runtime.grounding.compatibility_for(signature) == "quarantined"
    assert runtime.grounding.prior_for(signature) is None


def test_swap_control_fails_closed_without_a_nonmatching_identity_source() -> None:
    runtime = _runtime_with_one_grounded_identity("swap_target")
    certificate = replace(_certificate(epoch=3), digest="e" * 64)
    signature = certificate.structural_signature
    ordinal = runtime._known_return_ordinal(signature)
    assert ordinal == 1
    with pytest.raises(
        RuntimeError,
        match="requires one grounded nonmatching source episode",
    ):
        runtime._build_counterfactual(
            time=3,
            signature=signature,
            ordinal=ordinal,
        )



def test_direct_commit_and_action_receipts_bind_the_target_episode() -> None:
    for mode in ("intact", "withhold_target", "swap_target"):
        runtime = _runtime_with_two_grounded_identities(mode)
        certificate = replace(_certificate(epoch=3), digest="e" * 64)
        signature = certificate.structural_signature
        ordinal = runtime._known_return_ordinal(signature)
        assert ordinal == 1
        counterfactual = runtime._build_counterfactual(
            time=6, signature=signature, ordinal=ordinal
        )
        runtime._target_signature = signature
        runtime._target_counterfactual = counterfactual
        policy = "generic" if mode == "swap_target" else "keyed"
        issued = runtime.temporal_identity.prepare_historical_prior(
            certificate,
            time=6,
            policy_override=policy,
            exclude_target_key=(policy == "generic"),
        )
        delivered, intervention = runtime._intervention_for(
            time=6, signature=signature, issued=issued, ordinal=ordinal
        )
        runtime._target_intervention = intervention
        runtime._target_issued_prior = issued

        active_prior = delivered if mode == "intact" else None
        compatibility = (
            "compatible"
            if mode == "intact"
            else ("quarantined" if mode == "swap_target" else None)
        )
        if active_prior is not None:
            runtime.grounding.apply_historical_prior(
                certificate, active_prior, time=6
            )
            runtime.grounding._historical_prior_compatibility[signature] = (
                "compatible"
            )

        grounding = _grounding(7, epoch=3, digest_char="e",
            events=("boundary_restored",), on_count=2, off_count=2)
        temporal = _observe(
            runtime.temporal_identity,
            RobustReflexiveDiagnosticController(),
            grounding,
            active_prior,
        )
        assert "known_identity_returned_grounded" in temporal.events
        runtime._last_temporal_identity_outcome = temporal
        runtime._last_grounding_outcome = grounding
        runtime._last_historical_grounding_prior = active_prior
        runtime._last_issued_historical_grounding_prior = None
        runtime._last_historical_prior_compatibility = compatibility

        commit = runtime._build_commit_receipt()
        assert commit is not None
        assert validate_self_model_commit_event_receipt(commit)
        assert commit.intervention_receipt_digest == intervention.digest
        assert commit.counterfactual_receipt_digest == counterfactual.digest
        assert commit.issued_historical_prior_digest == issued.digest
        if mode == "intact":
            assert commit.historical_prior_used
            assert commit.fresh_on_samples == 1
            assert commit.fresh_off_samples == 1
        else:
            assert not commit.historical_prior_used
            assert commit.fresh_on_samples == 2
            assert commit.fresh_off_samples == 2
        if mode == "swap_target":
            assert commit.quarantined_prior_excluded_from_commit

        runtime._commit_by_episode[commit.episode_id] = commit
        authorization_digest = (
            runtime.temporal_identity.ordinary_action_authorization_digest(
                signature, certificate.digest
            )
        )
        assert authorization_digest is not None
        authorization = runtime._authorization_receipt(
            time=8,
            raw=certificate,
            authorization_digest=authorization_digest,
        )
        assert validate_self_model_action_authorization_receipt(authorization)
        assert authorization.commit_event_digest == commit.digest
        assert authorization.episode_id == commit.episode_id
        assert validate_self_model_receipt_chain(
            counterfactual,
            intervention,
            commit,
            authorization,
        )
        tampered = replace(
            authorization,
            commit_event_digest="0" * 64,
            digest="",
        )
        payload = asdict(tampered)
        payload.pop("digest")
        tampered = replace(tampered, digest=_temporal_digest(payload))
        assert validate_self_model_action_authorization_receipt(tampered)
        assert not validate_self_model_receipt_chain(
            counterfactual,
            intervention,
            commit,
            tampered,
        )

def test_compact_archived_causal_adjudication_meets_all_endpoints() -> None:
    root = (
        Path(__file__).parents[1]
        / "validation"
        / "v0.42.0_causal_self_model_necessity"
        / "input_summaries"
    )
    report = analyze_summary_directory(root)
    assert report["all_endpoints_met"]
    assert report["aggregate"]["primary_contrast_count"] == 8
    assert report["aggregate"]["strict_primary_contrast_success_count"] == 8
    assert (
        report["aggregate"][
            "keyed_fresh_sample_reduction_fraction_vs_withheld"
        ]
        == 0.5
    )
    modes = report["aggregate"][
        "mode_aggregates_over_all_grounded_known_returns"
    ]
    assert modes["intact"]["total_fresh_samples"] == 40
    assert modes["withhold_target"]["total_fresh_samples"] == 80
    assert modes["swap_target"]["total_fresh_samples"] == 80
    assert all(
        validate_archived_causal_contrast_receipt(
            ArchivedCausalContrastReceipt(
                **{
                    **item,
                    "intact": ArchivedArmOutcome(**item["intact"]),
                    "withheld": ArchivedArmOutcome(**item["withheld"]),
                    "wrong_source": ArchivedArmOutcome(
                        **item["wrong_source"]
                    ),
                }
            )
        )
        for item in report["primary_yoked_contrasts"]
    )


def test_compact_adjudicator_rejects_a_summary_changed_after_manifest(
    tmp_path: Path,
) -> None:
    source_root = (
        Path(__file__).parents[1]
        / "validation"
        / "v0.42.0_causal_self_model_necessity"
    )
    copied_root = tmp_path / source_root.name
    shutil.copytree(source_root, copied_root)
    changed = next(
        (copied_root / "input_summaries").glob("seed-*/*.summary.json")
    )
    changed.write_text(
        changed.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    with pytest.raises(
        ValueError,
        match="does not match compact input manifest",
    ):
        analyze_summary_directory(copied_root / "input_summaries")


def test_post_change_runner_can_stream_without_retaining_rows() -> None:
    config = V037ExperimentConfig(
        stable_steps=2,
        world_shock_steps=2,
        remap_steps=2,
        disconnect_steps=2,
        restore_steps=2,
        recovery_tail_steps=1,
        confirmation_budget_steps=1,
    )
    streamed = []

    def summary_factory(
        seed,
        experiment_config,
        boundary_config,
        runtime_config,
        rows,
        runtime,
        runtime_instance_digest,
        phase_model_counts,
        control_model_counts,
    ):
        del (
            seed,
            boundary_config,
            runtime_config,
            runtime,
            runtime_instance_digest,
            phase_model_counts,
            control_model_counts,
        )
        return {
            "retained_count": len(rows),
            "streamed_count": len(streamed),
            "expected_count": experiment_config.total_steps,
        }

    rows, summary = run_post_change_closure_trace(
        42002,
        experiment_config=config,
        summary_factory=summary_factory,
        sealed_row_sink=lambda row: streamed.append(int(row["transition_index"])),
        retain_rows=False,
    )
    assert rows == []
    assert summary == {
        "retained_count": 0,
        "streamed_count": config.total_steps,
        "expected_count": config.total_steps,
    }
