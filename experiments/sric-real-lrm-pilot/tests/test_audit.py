from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.audit import run_causal_audit
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.schemas import AuditConfig, AuditThresholds


def test_full_fake_audit_reaches_procedure_specific():
    records = make_fixture_records(24)
    config = AuditConfig(
        max_tasks=24,
        bootstrap_replicates=100,
        thresholds=AuditThresholds(
            replay_max_abs=1e-12,
            necessity_mean=0.02,
            necessity_positive_fraction=0.9,
            order_mean=0.01,
            structure_mean=0.02,
            procedure_mean=0.02,
            procedure_positive_fraction=0.8,
            twin_abs_mean_max=1e-12,
            twin_absolute_ceiling=1e-12,
        ),
    )
    result = run_causal_audit(FakeProcedureLatentAdapter(), records, config)
    assert result["summary"]["status"] == "PROCEDURE_SPECIFIC"
    assert all(result["summary"]["gates"].values())
