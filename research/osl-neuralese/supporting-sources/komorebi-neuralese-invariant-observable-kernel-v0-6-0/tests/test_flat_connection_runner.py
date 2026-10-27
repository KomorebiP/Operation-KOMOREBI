import hashlib
import json

import pytest

import run_flat_connection as runner


def _seal_checkpoint_panel(directory, seeds=(1,)):
    checkpoint_dir = directory / "checkpoints"
    checkpoint_dir.mkdir()
    rows = []
    for seed in seeds:
        for arm in runner.PRIMARY_FLATNESS_ARMS:
            relative = f"checkpoints/{arm}_seed{seed}.pt"
            path = directory / relative
            path.write_bytes(f"{seed}:{arm}".encode("ascii"))
            rows.append(
                {
                    "path": relative,
                    "sha256": runner.sha256_file(path),
                    "arm": arm,
                    "seed": seed,
                    "state_digest": hashlib.sha256(relative.encode()).hexdigest(),
                }
            )
    rows.sort(key=lambda row: (row["seed"], row["arm"]))
    seal = {
        "schema": "komorebi.flat_packet_connection.checkpoint_seal.v1",
        "version": runner.VERSION,
        "source_digest": "a" * 64,
        "count": len(rows),
        "checkpoints": rows,
    }
    seal["seal_sha256"] = hashlib.sha256(
        runner.canonical_json_bytes(seal)
    ).hexdigest()
    return seal


def test_checkpoint_seal_is_complete_and_detects_tampering(tmp_path):
    seal = _seal_checkpoint_panel(tmp_path)
    indexed = runner.validate_checkpoint_seal(
        tmp_path, seal, {"seeds": (1,)}, expected_source_digest="a" * 64
    )
    assert set(indexed) == {
        (1, arm) for arm in runner.PRIMARY_FLATNESS_ARMS
    }
    (tmp_path / seal["checkpoints"][0]["path"]).write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="bytes do not match"):
        runner.validate_checkpoint_seal(
            tmp_path, seal, {"seeds": (1,)}, expected_source_digest="a" * 64
        )


def test_checkpoint_seal_requires_canonical_order(tmp_path):
    seal = _seal_checkpoint_panel(tmp_path)
    seal["checkpoints"] = list(reversed(seal["checkpoints"]))
    unsigned = dict(seal)
    unsigned.pop("seal_sha256")
    seal["seal_sha256"] = hashlib.sha256(
        runner.canonical_json_bytes(unsigned)
    ).hexdigest()
    with pytest.raises(RuntimeError, match="canonical"):
        runner.validate_checkpoint_seal(
            tmp_path, seal, {"seeds": (1,)}, expected_source_digest="a" * 64
        )


def test_pilot_contract_binds_full_registered_design():
    preregistration = json.loads(runner.PREREGISTRATION.read_text(encoding="utf-8"))
    profile = {
        key: list(value) if isinstance(value, tuple) else value
        for key, value in runner.PROFILE_CONFIG["pilot"].items()
    }
    preregistration_sha256 = runner.sha256_file(runner.PREREGISTRATION)
    contract = {
        "schema": "komorebi.flat_packet_connection.contract.v1",
        "version": runner.VERSION,
        "author": "Komorebi P.",
        "source_digest": "b" * 64,
        "profile_name": "pilot",
        "arms": list(runner.PRIMARY_FLATNESS_ARMS),
        "pilot_profile": profile,
        "thresholds": dict(runner.FROZEN_THRESHOLDS),
        "numerical_contract": preregistration["numerical_contract"],
        "preregistration_sha256": preregistration_sha256,
    }
    design = {
        field: contract[field] for field in runner.REGISTERED_DESIGN_FIELDS
    }
    contract["registered_design_sha256"] = hashlib.sha256(
        runner.canonical_json_bytes(design)
    ).hexdigest()
    runner.validate_pilot_contract(
        contract,
        source_sha256="b" * 64,
        preregistration_sha256=preregistration_sha256,
        preregistration=preregistration,
    )
    contract["thresholds"]["deep_512_pooled"] = 0.0
    with pytest.raises(RuntimeError, match="complete frozen design"):
        runner.validate_pilot_contract(
            contract,
            source_sha256="b" * 64,
            preregistration_sha256=preregistration_sha256,
            preregistration=preregistration,
        )


def test_value_summary_fails_closed_on_nonfinite_values():
    summary = runner._value_summary([1.0, float("nan"), None])
    assert summary["count"] == 3
    assert summary["finite_count"] == 1
    assert summary["mean"] is None
    assert summary["median"] is None
    assert summary["maximum"] is None


def test_source_digest_excludes_cache_directories(tmp_path, monkeypatch):
    (tmp_path / "source.py").write_text("x = 1\n", encoding="utf-8")
    cache = tmp_path / ".pytest_cache"
    cache.mkdir()
    (cache / "README.md").write_text("transient\n", encoding="utf-8")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    digest, names = runner.source_digest()
    assert len(digest) == 64
    assert names == ["source.py"]


def test_preregistration_matches_executable_contract():
    registered = runner.validate_preregistration()
    assert registered["schema"].endswith(".v2")

