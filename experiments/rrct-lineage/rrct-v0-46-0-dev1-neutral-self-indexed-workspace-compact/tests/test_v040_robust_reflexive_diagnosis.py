"""Focused checks for v0.40 robust reflexive diagnosis."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from rrct.autonomous_self_diagnosis import GroundingOutcomeReceipt
from rrct.robust_reflexive_diagnosis import (
    RobustReflexiveDiagnosisConfig,
    RobustReflexiveDiagnosticController,
    validate_reflexive_diagnosis_receipt,
)

FIXTURES = Path(__file__).parent / "fixtures" / "v040_exposed_trace_screen"


def _grounding(
    time: int,
    error: float,
    *,
    mode: str = "ordinary_use",
    status: str | None = "certified",
    norm: float | None = 1.0,
    actual: bool = True,
    informative: bool = True,
    events: tuple[str, ...] = (),
    diagnosis: str = "boundary_operational",
) -> GroundingOutcomeReceipt:
    return GroundingOutcomeReceipt(
        time=time,
        raw_signature=(((1, 2), 2, 1) if status is not None else None),
        raw_certificate_digest=("a" * 64 if status is not None else None),
        mode=mode,  # type: ignore[arg-type]
        requested_certificate_on=actual,
        actual_certificate_on=actual,
        status_before=status,  # type: ignore[arg-type]
        status_after=status,  # type: ignore[arg-type]
        reason="test consequence",
        expected_information_gain=0.0,
        selected_key="east",
        selected_action=(1.0, 0.0),
        observable_context=(1.0, 0.0),
        probe_opportunity=1.0,
        informative_probe=informative,
        realized_external_return=(norm if norm is not None else None),
        normalized_causal_signal=norm,
        on_count_before=2,
        off_count_before=2,
        on_count_after=2,
        off_count_after=2,
        posterior_delta=1.0,
        lower_bound=0.8,
        upper_bound=1.2,
        consecutive_sentinel_failures=(1 if "sentinel_failure" in events else 0),
        transition_prediction_error=error,
        events=events,
        diagnosis=diagnosis,
        recommended_response="test",
        private_boundary_active=True,
        workspace_candidate_selected=True,
        workspace_drive_norm=1.0,
        access_update_count=0,
        uses_evaluator_labels=False,
        digest=f"{time:064x}"[-64:],
    )


def test_two_timescale_monitor_requires_collective_shift_and_recent_efficacy() -> None:
    controller = RobustReflexiveDiagnosticController(
        RobustReflexiveDiagnosisConfig(
            baseline_window=16,
            recent_window=4,
            successful_sentinel_max_age=8,
        )
    )
    receipts = []
    for time in range(16):
        receipts.append(controller.observe(_grounding(time, 4.0)))
    for time, error in enumerate((8.0, 8.3, 8.1, 8.4), start=16):
        receipts.append(
            controller.observe(
                _grounding(
                    time,
                    error,
                    mode="sentinel" if time == 16 else "ordinary_use",
                )
            )
        )
    alarms = [
        receipt for receipt in receipts if "external_dynamics_shift" in receipt.events
    ]
    assert len(alarms) == 1
    alarm = alarms[0]
    assert alarm.causal_efficacy_intact
    assert alarm.standardized_shift is not None
    assert alarm.standardized_shift >= 4.0
    assert alarm.mean_ratio is not None and alarm.mean_ratio >= 1.5
    assert alarm.high_residual_fraction is not None
    assert alarm.high_residual_fraction >= 0.60
    assert alarm.diagnosis == "external_dynamics_shift"
    assert alarm.recommended_response == "retain_boundary_and_update_world_model"
    assert validate_reflexive_diagnosis_receipt(alarm)


def test_high_residuals_without_successful_sentinel_do_not_become_world_shift() -> None:
    controller = RobustReflexiveDiagnosticController(
        RobustReflexiveDiagnosisConfig(
            baseline_window=16,
            recent_window=4,
            successful_sentinel_max_age=8,
        )
    )
    for time in range(16):
        controller.observe(_grounding(time, 4.0))
    outputs = []
    for time in range(16, 20):
        outputs.append(
            controller.observe(
                _grounding(
                    time,
                    8.5,
                    mode="sentinel",
                    status="revoked",
                    norm=0.0,
                    events=(
                        "sentinel_failure",
                        "certificate_revoked_by_consequence",
                    ),
                    diagnosis="boundary_effect_failed",
                )
            )
        )
    assert not any("external_dynamics_shift" in out.events for out in outputs)
    assert outputs[-1].diagnosis == "boundary_effect_failed"
    assert (
        outputs[-1].recommended_response
        == "retest_and_reconstruct_causal_boundary"
    )


def test_reflexive_receipt_digest_fails_closed_after_tampering() -> None:
    controller = RobustReflexiveDiagnosticController(
        RobustReflexiveDiagnosisConfig(baseline_window=16, recent_window=4)
    )
    receipt = controller.observe(_grounding(0, 4.0))
    assert validate_reflexive_diagnosis_receipt(receipt)
    assert not validate_reflexive_diagnosis_receipt(
        replace(receipt, recommended_response="tampered")
    )


def _fixture_receipt(data: np.lib.npyio.NpzFile, index: int) -> GroundingOutcomeReceipt:
    norm = float(data["norm"][index])
    normalized = None if np.isnan(norm) else norm
    status_text = str(data["status"][index])
    status = None if status_text == "" else status_text
    event_text = str(data["events"][index])
    events = tuple(part for part in event_text.split("|") if part)
    return _grounding(
        index,
        float(data["error"][index]),
        mode=str(data["mode"][index]),
        status=status,
        norm=normalized,
        actual=bool(data["actual"][index]),
        informative=bool(data["informative"][index]),
        events=events,
        diagnosis=str(data["diagnosis"][index]),
    )


def test_exposed_v039_corpus_detects_world_shock_from_permitted_telemetry() -> None:
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    assert manifest["controller_inputs_exclude_phase_and_offset"] is True
    data = np.load(FIXTURES / "H1-P-0001-SEED-39103.npz")
    stable = np.where(data["phase"] == "stable")[0][-200:]
    shock = np.where(data["phase"] == "world_shock")[0][:30]
    selected = np.concatenate((stable, shock))
    controller = RobustReflexiveDiagnosticController()
    alarms: list[int] = []
    for local_time, source_index in enumerate(selected):
        source = _fixture_receipt(data, int(source_index))
        out = controller.observe(replace(source, time=local_time))
        if "external_dynamics_shift" in out.events:
            alarms.append(int(source_index))
    scored = [
        (str(data["phase"][index]), int(data["offset"][index]))
        for index in alarms
    ]
    assert scored == [("world_shock", 5)]
    assert controller.world_shift_count == 1


def test_short_integrated_trace_binds_v039_and_v040_receipts() -> None:
    from rrct.post_change_closure_experiment import V037ExperimentConfig
    from rrct.robust_reflexive_diagnosis_experiment import (
        V040_ROW_SCHEMA,
        run_robust_reflexive_diagnosis_trace,
    )

    config = V037ExperimentConfig(
        stable_steps=2,
        world_shock_steps=2,
        remap_steps=2,
        disconnect_steps=2,
        restore_steps=2,
        recovery_tail_steps=1,
        confirmation_budget_steps=1,
    )
    rows, summary = run_robust_reflexive_diagnosis_trace(
        12345,
        experiment_config=config,
        inject_access_fault=False,
    )
    assert len(rows) == config.total_steps
    assert all(row["schema"] == V040_ROW_SCHEMA for row in rows)
    assert all(row["v039_wrapper_integrity"] for row in rows)
    assert all(row["v040_wrapper_integrity"] for row in rows)
    assert all(summary["integrity"].values())
