import copy
import hashlib
import json
from dataclasses import asdict

import pytest

import validation.freeze_v030 as freeze_module
import validation.v030_official_integrity as integrity_module
from rrct.structural_self_model_revision_experiment import (
    V030_FROZEN_CONFIG,
    V030_SCHEMA,
)
from validation.aggregate_v030 import _validate_official_parts_parent
from validation.run_v030_one_seed import _validate_official_request
from validation.v030_official_integrity import (
    EXPECTED_NUMPY_VERSION,
    EXPECTED_OFFICIAL_RUNTIME,
    EXPECTED_PYTHON_VERSION,
    EXPECTED_THREAD_ENVIRONMENT,
    PermanentSeedJournal,
    verify_completed_seed_journal,
    verify_freeze_manifest,
    verify_official_part_payload,
    verify_official_runtime,
    write_pickle_atomic_once,
)


def _canonical_json(payload):
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _manifest_fixture(tmp_path):
    root = tmp_path / "project"
    validation = root / "validation"
    source = root / "src" / "frozen.py"
    validation.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    source.write_bytes(b"frozen\n")
    manifest = validation / "V0_30_PREOUTCOME_FREEZE.json"
    checksum = validation / "V0_30_PREOUTCOME_FREEZE.json.sha256"
    payload = {
        "experiment": {
            "config_defaults": {"block_size": 20},
            "schema": "rrct.v030.structural_self_model_revision.v1",
        },
        "files": {
            "src/frozen.py": {
                "size": source.stat().st_size,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        },
        "official_seed_access_before_freeze": "none",
        "official_seeds": [5801, 5807, 5813, 5819, 5821, 5827, 5839, 5843],
        "official_runtime": {
            "python": "3.12.13",
            "numpy": "2.2.6",
            "thread_environment": {
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
            },
        },
        "parent_v029": {
            "preoutcome_freeze_sha256": (
                "3f0afb3b41de78db6b80f6b358be8079a7efddd772197a28096360b99f59b5a1"
            ),
            "result_sha256s_sha256": (
                "99b34c7a54c07373ad4b5ac8bd8c3df76cbc494810708b9b3ebadd9bf93f4e97"
            ),
            "source_and_evidence_archive_sha256": (
                "f1ae10c8b5b107918041630910f4ba991e7f8cf2371defac2dcd185a556682a7"
            ),
        },
        "pilot_seeds": [5701, 5707, 5713, 5719],
        "schema": "rrct.v030.preoutcome_freeze.v1",
        "status": "sealed_before_official_outcomes",
        "version": "0.30.0.dev1",
    }
    raw = _canonical_json(payload)
    manifest.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    checksum.write_text(f"{digest}  {manifest.name}\n", encoding="ascii")
    return root, source, manifest, checksum, digest


def _synthetic_row(
    *,
    seed,
    structure_digest,
    branch,
    phase,
    time,
    phase_step,
    target_rank,
):
    return {
        "schema": V030_SCHEMA,
        "time": time,
        "phase": phase,
        "target_handle": 0,
        "target_source": 1,
        "target_rank": target_rank,
        "selected_handle": 0,
        "selected_source": 1,
        "selected_rank": target_rank,
        "committed_exact": True,
        "internal_overlap": 1.0,
        "sensory_overlap": 1.0,
        "epoch": 1,
        "confidence_before": 0.5,
        "confidence_after": 0.5,
        "confidence_is_probability": False,
        "confidence_semantics": (
            "minimum correctly paired normalized randomization margin"
        ),
        "fit_performed": False,
        "fit_handle": None,
        "fit_source": None,
        "fit_rank": 0,
        "fit_confidence": 0.0,
        "fit_exact": False,
        "candidate_handle": None,
        "candidate_source": None,
        "candidate_rank": 0,
        "candidate_streak": 0,
        "candidate_last_evidence_count": None,
        "candidate_renewed": False,
        "null_streak": 0,
        "null_last_evidence_count": None,
        "null_renewed": False,
        "candidate_pair_matches": True,
        "structural_event": "none",
        "acquired": False,
        "revised": False,
        "revoked": False,
        "rank_changed": False,
        "previous_rank": target_rank,
        "pre_state_digest": "1" * 64,
        "post_state_digest": "2" * 64,
        "commitment_digest": "3" * 64,
        "transition_digest": "4" * 64,
        "outcome_digest": "5" * 64,
        "prequential_chain": True,
        "source_energy_error": 0.0,
        "hidden_truth_passed_to_model": False,
        "seed": seed,
        "branch": branch,
        "phase_step": phase_step,
        "legacy_immediate_rank": target_rank,
        "legacy_immediate_exact": True,
        "overlap_confirmation_handle": 0,
        "overlap_confirmation_source": 1,
        "overlap_confirmation_rank": target_rank,
        "overlap_confirmation_exact": True,
        "overlap_confirmation_revised": False,
        "structure_digest": structure_digest,
    }


def _synthetic_official_payload(seed=17, freeze_digest=None):
    config = asdict(V030_FROZEN_CONFIG)
    structure_digest = "a" * 64
    if freeze_digest is None:
        freeze_digest = "b" * 64
    calibration_steps = config["calibration_blocks"] * config["block_size"]
    stable_steps = config["stable_blocks"] * config["block_size"]
    recovery_steps = (
        config["transient_recovery_blocks"] * config["block_size"]
    )
    contraction_steps = config["contraction_blocks"] * config["block_size"]
    restoration_steps = config["restoration_blocks"] * config["block_size"]
    schedule = (
        ("calibration", "calibration", 0, calibration_steps, 2),
        ("stable", "stable_shock", calibration_steps, stable_steps, 2),
        (
            "transient",
            "transient_dropout",
            calibration_steps,
            config["transient_rows"],
            2,
        ),
        (
            "transient",
            "transient_recovery",
            calibration_steps + config["transient_rows"],
            recovery_steps,
            2,
        ),
        (
            "sustained",
            "sustained_contraction",
            calibration_steps,
            contraction_steps,
            1,
        ),
        (
            "sustained",
            "sustained_restoration",
            calibration_steps + contraction_steps,
            restoration_steps,
            2,
        ),
    )
    rows = [
        _synthetic_row(
            seed=seed,
            structure_digest=structure_digest,
            branch=branch,
            phase=phase,
            time=start_time + phase_step,
            phase_step=phase_step,
            target_rank=target_rank,
        )
        for branch, phase, start_time, steps, target_rank in schedule
        for phase_step in range(steps)
    ]
    summary = {
        "seed": seed,
        "acquisition_terminal_exact": True,
        "acquisition_rank": 2,
        "stable_exact_accuracy": 1.0,
        "stable_rank_revisions": 0,
        "transient_exact_accuracy": 1.0,
        "transient_rank_revisions": 0,
        "transient_rank_one_proposals": 0,
        "transient_rank_one_candidate_starts_or_renewals": 0,
        "transient_rank_one_max_fit_streak": 0,
        "transient_legacy_false_rank_rate": 0.0,
        "transient_overlap_false_rank_rate": 0.0,
        "transient_overlap_rank_revisions": 0,
        "contraction_terminal_tail_accuracy": 1.0,
        "restoration_terminal_tail_accuracy": 1.0,
        "contraction_revision_latency": None,
        "restoration_revision_latency": None,
        "contraction_rank_revisions": 0,
        "restoration_rank_revisions": 0,
        "contraction_pair_retained": True,
        "restoration_pair_retained": True,
        "candidate_support_decays": False,
        "active_support_positive": True,
        "active_fit_support_positive": False,
        "prequential_chain_all": True,
        "equal_energy_all": True,
        "hidden_truth_isolated": True,
        "stable_terminal_exact": True,
        "transient_terminal_exact": True,
        "sustained_terminal_exact": True,
        "integrity": True,
    }
    receipt = {
        "seed": seed,
        "cohort": "official",
        "structure_digest": structure_digest,
        "hidden_pair_never_passed_to_model": True,
        "hidden_rank_never_passed_to_model": True,
        "hidden_projectors_never_passed_to_model": True,
        "phase_labels_never_passed_to_model": True,
        "world_seed_never_passed_to_model": True,
        "learner_rng_independent_of_world_seed": True,
        "confidence_is_calibrated_probability": False,
        "confidence_semantics": (
            "minimum correctly paired normalized randomization margin"
        ),
        "interventions_reversible_and_synthetic": True,
    }
    return {
        "schema": V030_SCHEMA,
        "seed": seed,
        "cohort": "official",
        "config": config,
        "seed_summary": summary,
        "rows": rows,
        "receipt": receipt,
        "freeze_manifest_sha256": freeze_digest,
    }


def _verify_synthetic_payload(payload):
    verify_official_part_payload(
        payload,
        seed=payload["seed"],
        expected_schema=V030_SCHEMA,
        expected_config=asdict(V030_FROZEN_CONFIG),
        freeze_manifest_sha256=payload["freeze_manifest_sha256"],
    )


def _set_valid_official_runtime(monkeypatch):
    monkeypatch.setattr(
        integrity_module.sys,
        "version_info",
        (*EXPECTED_PYTHON_VERSION, "final", 0),
    )
    monkeypatch.setattr(
        integrity_module.np,
        "__version__",
        EXPECTED_NUMPY_VERSION,
    )
    for name, value in EXPECTED_THREAD_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)


def test_official_request_rejects_nonexact_path_and_unreserved_seed(tmp_path):
    with pytest.raises(ValueError, match="basename must be exactly 17.pkl"):
        _validate_official_request(
            17,
            tmp_path / "wrong.pkl",
            reserved_seeds=(17,),
            expected_parent=tmp_path,
        )
    with pytest.raises(ValueError, match="not a reserved"):
        _validate_official_request(
            19,
            tmp_path / "19.pkl",
            reserved_seeds=(17,),
            expected_parent=tmp_path,
        )
    with pytest.raises(ValueError, match="output parent must be exactly"):
        _validate_official_request(
            17,
            tmp_path / "other" / "17.pkl",
            reserved_seeds=(17,),
            expected_parent=tmp_path,
        )
    _validate_official_request(
        17,
        tmp_path / "17.pkl",
        reserved_seeds=(17,),
        expected_parent=tmp_path,
    )
    with pytest.raises(ValueError, match="parts directory must be exactly"):
        _validate_official_parts_parent(tmp_path / "other", expected=tmp_path)
    _validate_official_parts_parent(tmp_path, expected=tmp_path)


def test_official_runtime_exact_receipt_passes(monkeypatch):
    _set_valid_official_runtime(monkeypatch)
    assert EXPECTED_PYTHON_VERSION == (3, 12, 13)
    assert EXPECTED_NUMPY_VERSION == "2.2.6"
    assert EXPECTED_THREAD_ENVIRONMENT == {
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
    }
    assert verify_official_runtime() == EXPECTED_OFFICIAL_RUNTIME


def test_official_runtime_rejects_python_patch_mismatch(monkeypatch):
    _set_valid_official_runtime(monkeypatch)
    monkeypatch.setattr(
        integrity_module.sys,
        "version_info",
        (3, 12, 12, "final", 0),
    )
    with pytest.raises(RuntimeError, match="official Python runtime mismatch"):
        verify_official_runtime()


def test_official_runtime_rejects_numpy_patch_mismatch(monkeypatch):
    _set_valid_official_runtime(monkeypatch)
    monkeypatch.setattr(integrity_module.np, "__version__", "2.2.5")
    with pytest.raises(RuntimeError, match="official NumPy runtime mismatch"):
        verify_official_runtime()


@pytest.mark.parametrize("name", tuple(EXPECTED_THREAD_ENVIRONMENT))
def test_official_runtime_rejects_each_non_single_thread_setting(
    monkeypatch, name
):
    _set_valid_official_runtime(monkeypatch)
    monkeypatch.setenv(name, "2")
    with pytest.raises(
        RuntimeError,
        match="official numerical thread environment mismatch",
    ):
        verify_official_runtime()


def test_permanent_seed_journal_exclusively_blocks_a_second_attempt(tmp_path):
    path = tmp_path / "17.lock"
    digest = "a" * 64
    first = PermanentSeedJournal.create(
        path,
        seed=17,
        output_basename="17.pkl",
        freeze_manifest_sha256=digest,
    )
    first.close()
    with pytest.raises(FileExistsError):
        PermanentSeedJournal.create(
            path,
            seed=17,
            output_basename="17.pkl",
            freeze_manifest_sha256=digest,
        )
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert [record["event"] for record in records] == ["started"]


def test_freeze_manifest_detects_listed_file_and_companion_tampering(tmp_path):
    root, source, manifest, checksum, digest = _manifest_fixture(tmp_path)
    assert verify_freeze_manifest(manifest, checksum, project_root=root) == digest

    source.write_bytes(b"broken\n")
    with pytest.raises(ValueError, match="sha256 mismatch"):
        verify_freeze_manifest(manifest, checksum, project_root=root)

    source.write_bytes(b"frozen\n")
    checksum.write_text(f"{'0' * 64}  {manifest.name}\n", encoding="ascii")
    with pytest.raises(ValueError, match="checksum companion mismatch"):
        verify_freeze_manifest(manifest, checksum, project_root=root)


def test_completed_journal_binds_output_to_freeze_digest(tmp_path):
    expected_digest = "b" * 64
    final = tmp_path / "17.pkl"
    temporary = tmp_path / "17.pkl.tmp"
    journal_path = tmp_path / "17.lock"
    journal = PermanentSeedJournal.create(
        journal_path,
        seed=17,
        output_basename=final.name,
        freeze_manifest_sha256=expected_digest,
    )
    size, output_hash = write_pickle_atomic_once(
        {"seed": 17, "cohort": "official"},
        final,
        temporary,
    )
    journal.append(
        "completed",
        seed=17,
        output=final.name,
        freeze_manifest_sha256=expected_digest,
        output_size=size,
        output_sha256=output_hash,
    )
    journal.close()
    verify_completed_seed_journal(
        journal_path,
        seed=17,
        output_path=final,
        freeze_manifest_sha256=expected_digest,
    )
    with pytest.raises(ValueError, match="manifest mismatch"):
        verify_completed_seed_journal(
            journal_path,
            seed=17,
            output_path=final,
            freeze_manifest_sha256="c" * 64,
        )


def test_freeze_is_ast_only_and_one_shot(tmp_path, monkeypatch):
    root = tmp_path / "project"
    validation = root / "validation"
    source = root / "src" / "rrct"
    tests = root / "tests"
    fixtures = tests / "fixtures"
    validation.mkdir(parents=True)
    source.mkdir(parents=True)
    fixtures.mkdir(parents=True)

    (root / "MANIFEST.in").write_text("include README.md\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nversion = "0.30.0.dev1"\n', encoding="utf-8"
    )
    (source / "_version.py").write_text(
        '__version__ = "0.30.0.dev1"\n', encoding="utf-8"
    )
    (source / "structural_self_model_revision_experiment.py").write_text(
        "raise RuntimeError('the freeze must not import this module')\n"
        "V030_SCHEMA = 'rrct.v030.structural_self_model_revision.v1'\n"
        "V030_PILOT_SEEDS = (17,)\n"
        "V030_OFFICIAL_SEEDS = (23,)\n"
        "class V030RunConfig:\n"
        "    block_size: int = 20\n"
        "    phase_blocks: tuple[int, int] = (2, 4)\n",
        encoding="utf-8",
    )
    (source / "other.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tests / "test_frozen.py").write_text("def test_value(): pass\n", encoding="utf-8")
    (fixtures / "trace.json").write_text("{}\n", encoding="utf-8")
    (validation / "freeze_v030.py").write_text("# frozen harness\n", encoding="utf-8")
    parent_freeze = validation / "V0_29_PREOUTCOME_FREEZE.json"
    parent_results = validation / "V0_29_RESULT_SHA256SUMS.txt"
    parent_freeze.write_bytes(b"parent freeze\n")
    parent_results.write_bytes(b"parent results\n")

    manifest = validation / "V0_30_PREOUTCOME_FREEZE.json"
    checksum = validation / "V0_30_PREOUTCOME_FREEZE.json.sha256"
    monkeypatch.setattr(freeze_module, "PROJECT_ROOT", root)
    monkeypatch.setattr(freeze_module, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(freeze_module, "CHECKSUM_PATH", checksum)
    monkeypatch.setattr(freeze_module, "PILOT_SEEDS", (17,))
    monkeypatch.setattr(freeze_module, "OFFICIAL_SEEDS", (23,))
    monkeypatch.setattr(freeze_module, "V029_EXPOSED_SEEDS", (5,))
    monkeypatch.setattr(
        freeze_module,
        "V030_VALIDATION_FILES",
        ("validation/freeze_v030.py",),
    )
    monkeypatch.setattr(
        freeze_module,
        "PARENT_V029_FREEZE_MANIFEST_SHA256",
        hashlib.sha256(parent_freeze.read_bytes()).hexdigest(),
    )
    monkeypatch.setattr(
        freeze_module,
        "PARENT_V029_RESULT_SHA256SUMS_SHA256",
        hashlib.sha256(parent_results.read_bytes()).hexdigest(),
    )

    digest = freeze_module.freeze(passed=3, skipped=1, subtests=2)
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == digest
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["official_seeds"] == [23]
    assert payload["pilot_seeds"] == [17]
    assert payload["official_runtime"] == {
        "python": "3.12.13",
        "numpy": "2.2.6",
        "thread_environment": {
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
        },
    }
    assert payload["experiment"]["config_defaults"] == {
        "block_size": 20,
        "phase_blocks": [2, 4],
    }
    assert "src/rrct/other.py" in payload["files"]
    assert "tests/fixtures/trace.json" in payload["files"]
    with pytest.raises(FileExistsError, match="already exists or is incomplete"):
        freeze_module.freeze(passed=3, skipped=1, subtests=2)


def test_synthetic_exact_official_rows_and_summary_envelope_passes():
    _verify_synthetic_payload(_synthetic_official_payload())


def test_official_payload_rejects_tampered_recomputed_summary_metric():
    payload = _synthetic_official_payload()
    payload["seed_summary"]["stable_exact_accuracy"] = 0.5
    with pytest.raises(ValueError, match="summary"):
        _verify_synthetic_payload(payload)


@pytest.mark.parametrize(
    ("field", "wrong_value"),
    (
        ("phase", "transient_dropout"),
        ("time", -1),
        ("branch", "transient"),
        ("phase_step", 7),
    ),
)
def test_official_payload_rejects_phase_schedule_identity_tampering(
    field, wrong_value
):
    payload = _synthetic_official_payload()
    first_stable = (
        payload["config"]["calibration_blocks"] * payload["config"]["block_size"]
    )
    payload["rows"][first_stable][field] = wrong_value
    with pytest.raises(ValueError, match="schedule"):
        _verify_synthetic_payload(payload)


@pytest.mark.parametrize("mutation", ("missing", "duplicate"))
def test_official_payload_rejects_missing_or_duplicate_schedule_rows(mutation):
    payload = _synthetic_official_payload()
    first_stable = (
        payload["config"]["calibration_blocks"] * payload["config"]["block_size"]
    )
    if mutation == "missing":
        payload["rows"].pop(first_stable)
    else:
        payload["rows"][first_stable + 1] = copy.deepcopy(
            payload["rows"][first_stable]
        )
    with pytest.raises(ValueError, match="schedule|row count"):
        _verify_synthetic_payload(payload)


def test_official_payload_rejects_hidden_truth_exposure():
    payload = _synthetic_official_payload()
    payload["rows"][0]["hidden_truth_passed_to_model"] = True
    with pytest.raises(ValueError, match="hidden-truth exposure"):
        _verify_synthetic_payload(payload)


def test_official_payload_rejects_row_structure_digest_substitution():
    payload = _synthetic_official_payload()
    payload["rows"][0]["structure_digest"] = "c" * 64
    with pytest.raises(ValueError, match="structure receipt"):
        _verify_synthetic_payload(payload)


@pytest.mark.parametrize(
    "attestation",
    (
        "world_seed_never_passed_to_model",
        "learner_rng_independent_of_world_seed",
    ),
)
def test_official_payload_rejects_world_seed_independence_attestation_tampering(
    attestation,
):
    payload = _synthetic_official_payload()
    payload["receipt"][attestation] = False
    with pytest.raises(ValueError, match="receipt attestation mismatch"):
        _verify_synthetic_payload(payload)
