from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))

from osl_core import OSLError, OSLRuntime  # noqa: E402
from osl_kernel import KernelVerifier  # noqa: E402
from osl_model import OSLStaticError  # noqa: E402


def test_malformed_numeric_is_an_audited_parse_rejection() -> None:
    source = "module malformed_numeric\nspace H dim 2\ncheck_projector e tolerance e\n"
    runtime = OSLRuntime()
    with pytest.raises(OSLStaticError):
        runtime.run_text(source)

    assert [r["kind"] for r in runtime.audit_log] == [
        "program_open",
        "parse_reject",
        "program_reject",
    ]
    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
    assert report["all_checks_pass"], report


def test_failed_authorization_does_not_consume_affine_proof() -> None:
    source = """\
module atomic_proof_use
lineage LA
agent A lineage LA
observe e by A content "event" confidence 0.9
proof pa access e by A mode affine
quarantine e by A
authorize e by A for planning requires pa
"""
    runtime = OSLRuntime()
    with pytest.raises(OSLError, match="quarantined"):
        runtime.run_text(source)

    assert runtime.state.proofs["pa"].remaining_uses == 1
    failed_step = runtime.audit_log[-2]["step"]
    assert not any(
        receipt["kind"] == "proof_consume" and receipt["step"] == failed_step
        for receipt in runtime.audit_log
    )
    report = KernelVerifier().verify(
        runtime.audit_log, runtime.state.snapshot(), source=source
    )
    assert report["all_checks_pass"], report

