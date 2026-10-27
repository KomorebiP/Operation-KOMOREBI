from dataclasses import replace

from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.pipeline import run_block24_pipeline
from sric_real_lrm.schemas import AuditConfig, AuditThresholds


def test_engineered_pipeline_reaches_causal_validation():
    config = AuditConfig.load("configs/fake_fixture.json")
    records = make_fixture_records(48)
    result = run_block24_pipeline(
        FakeProcedureLatentAdapter(num_latents=config.num_latents, seed=config.seed),
        records,
        config,
    )
    assert result["overall_status"] == "CAUSALLY_VALIDATED"
    assert result["causal_admission"]["summary"]["status"] == "CONTENT_SPECIFIC"
    semantic = result["semantic_escalation"]
    assert semantic["selected"]["method"] == "joint"
    assert semantic["selected"]["rank"] == 3
    assert semantic["post_seal_proof_witness"]["used_during_construction"] is False
    assert semantic["causal_patching"]["passed"] is True
    assert result["causal_admission"]["summary"]["mode_controls"]["verbalized"]["reason"] == "reserved_for_post_seal_witness"
    assert semantic["post_seal_explicit_cot_witness"]["used_during_construction"] is False
    assert semantic["chronology"][-1] == "explicit_cot_witness_revealed"
    assert semantic["final_support_captured_before_seal"] is False
    assert semantic["chronology"].index("semantic_quotient_sealed") < semantic["chronology"].index("final_support_captured")


def test_semantic_escalation_is_gated_by_causal_admission():
    base = AuditConfig.load("configs/fake_fixture.json")
    config = replace(
        base,
        thresholds=replace(base.thresholds, procedure_mean=1e6),
    )
    result = run_block24_pipeline(
        FakeProcedureLatentAdapter(num_latents=config.num_latents, seed=config.seed),
        make_fixture_records(48),
        config,
    )
    assert result["overall_status"] == "LATENT_GENERIC"
    assert result["semantic_escalation"]["status"] == "SEMANTIC_ESCALATION_NOT_ADMISSIBLE"
