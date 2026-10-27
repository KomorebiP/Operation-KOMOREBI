from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from osl_lab.cli import _audit_initialization_contracts, command_run_all


def test_initialization_audit_checks_label_semantics_and_parameter_bytes() -> None:
    common = {
        "tokenizer_sha256": "t" * 64,
        "answer_classes_sha256": "a" * 64,
        "model_parameter_schema_sha256": "s" * 64,
        "initial_model_sha256": "m" * 64,
    }
    experiments = [
        {"arm": arm, "initialization_contract": dict(common)}
        for arm in ("answer_only", "role_bind_augmented", "role_bind_scrambled")
    ]
    assert _audit_initialization_contracts(experiments)["status"] == "PASS"

    experiments[1]["initialization_contract"]["answer_classes_sha256"] = "b" * 64
    failed = _audit_initialization_contracts(experiments)
    assert failed["status"] == "FAIL"
    assert failed["checks"]["answer_classes_sha256"]["status"] == "FAIL"


def test_run_all_preflight_does_not_mutate_existing_run(tmp_path: Path) -> None:
    output = tmp_path / "completed"
    output.mkdir()
    marker = output / "run_metadata.json"
    original = b'{"completed":true,"status":"COMPLETED"}\n'
    marker.write_bytes(original)
    args = argparse.Namespace(
        config=None,
        preset="smoke",
        output_dir=str(output),
        force=False,
    )

    with pytest.raises(FileExistsError, match="protected artifacts"):
        command_run_all(args)

    assert marker.read_bytes() == original
