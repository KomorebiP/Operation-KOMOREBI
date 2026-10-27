import pytest
from sric_real_lrm.schemas import AuditConfig
from sric_real_lrm.sealing import build_protocol_seal, verify_seal


def test_seal_detects_mutation():
    seal = build_protocol_seal(
        AuditConfig(),
        external_repository={"commit": "abc"},
        model_fingerprint={"sha256": "def"},
        dataset_fingerprint={"sha256": "ghi"},
        donor_plan_digest="jkl",
        output_contract={"maximum_claim": "PROCEDURE_SPECIFIC"},
    )
    verify_seal(seal)
    seal["donor_plan_digest"] = "mutated"
    with pytest.raises(ValueError):
        verify_seal(seal)
