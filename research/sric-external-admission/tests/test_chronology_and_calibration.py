from __future__ import annotations

from sric_real_lrm import semantic as semantic_module
from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.dataset import (
    deterministic_calibration_audit_split,
    deterministic_group_split,
)
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.pipeline import run_block24_pipeline
from sric_real_lrm.schemas import AuditConfig


def test_covariance_calibration_is_group_disjoint_from_causal_audit():
    config = AuditConfig.load("configs/fake_fixture.json")
    records = make_fixture_records(48)
    split = deterministic_calibration_audit_split(
        records,
        seed=config.seed,
        calibration_fraction=config.causal_calibration_fraction,
    )
    cal_groups = {record.group_id for record in split["calibration"]}
    audit_groups = {record.group_id for record in split["audit"]}
    assert cal_groups
    assert audit_groups
    assert not (cal_groups & audit_groups)

    result = run_block24_pipeline(
        FakeProcedureLatentAdapter(num_latents=config.num_latents, seed=config.seed),
        records,
        config,
    )
    calibration_ids = set(result["causal_calibration"]["task_ids"])
    audit_ids = {row["task_id"] for row in result["causal_admission"]["rows"]}
    assert calibration_ids
    assert not (calibration_ids & audit_ids)
    assert result["causal_admission"]["summary"]["covariance_source"] == "calibration_support"


def test_semantic_final_support_is_collected_only_after_quotient_seal(monkeypatch):
    config = AuditConfig.load("configs/fake_fixture.json")
    records = make_fixture_records(48)
    expected = deterministic_group_split(
        records,
        seed=config.seed,
        discovery_fraction=config.semantic_discovery_fraction,
        calibration_fraction=config.semantic_calibration_fraction,
    )
    calls: list[list[str]] = []
    original = semantic_module.collect_semantic_dataset

    def recording_collect(adapter, subset, current_config):
        calls.append([record.task_id for record in subset])
        return original(adapter, subset, current_config)

    monkeypatch.setattr(semantic_module, "collect_semantic_dataset", recording_collect)
    result = semantic_module.run_semantic_escalation(
        FakeProcedureLatentAdapter(num_latents=config.num_latents, seed=config.seed),
        records,
        config,
    )
    assert calls == [
        [record.task_id for record in expected["discovery"]],
        [record.task_id for record in expected["calibration"]],
        [record.task_id for record in expected["final"]],
    ]
    chronology = result["chronology"]
    assert chronology.index("semantic_quotient_sealed") < chronology.index("final_support_captured")
    assert result["final_support_captured_before_seal"] is False
