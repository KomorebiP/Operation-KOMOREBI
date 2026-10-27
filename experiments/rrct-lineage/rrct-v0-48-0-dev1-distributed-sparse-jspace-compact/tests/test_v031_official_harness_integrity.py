import ast
import copy
import hashlib
import json
import shutil
from dataclasses import asdict
from pathlib import Path

import pytest

import validation.freeze_v031 as freeze_module
import validation.v031_official_integrity as integrity_module
from rrct.conditional_rank_inference_experiment import (
    V031_FROZEN_CANDIDATE_CONFIG,
    V031_SCHEMA,
)
import rrct.conditional_rank_inference_experiment as experiment_module
from validation.v031_official_integrity import (
    EXPECTED_EXPERIMENT_SCHEMA,
    EXPECTED_NUMPY_VERSION,
    EXPECTED_OFFICIAL_RUNTIME,
    EXPECTED_PYTHON_VERSION,
    EXPECTED_ROWS_PER_SEED,
    EXPECTED_SCENARIOS,
    EXPECTED_THREAD_ENVIRONMENT,
    PermanentPilotJournal,
    PermanentSeedJournal,
    recompute_seed_summary,
    verify_completed_seed_journal,
    verify_completed_pilot_journal,
    verify_freeze_manifest,
    verify_official_part_payload,
    verify_official_runtime,
    write_pickle_atomic_once,
)


def _digest(label):
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _canonical_json(payload):
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _model_fields(
    *,
    prefix,
    fit_performed,
    fit_pair,
    fit_rank,
    selected_pair,
    selected_rank,
    acquired,
    event,
    candidate_pair,
    candidate_rank,
    candidate_streak,
    candidate_last,
    candidate_renewed,
):
    fit_handle, fit_source = (None, None) if fit_pair is None else fit_pair
    selected_handle, selected_source = (
        (None, None) if selected_pair is None else selected_pair
    )
    candidate_handle, candidate_source = (
        (None, None) if candidate_pair is None else candidate_pair
    )
    return {
        f"{prefix}_fit_performed": fit_performed,
        f"{prefix}_fit_handle": fit_handle,
        f"{prefix}_fit_source": fit_source,
        f"{prefix}_fit_rank": fit_rank,
        f"{prefix}_fit_confidence": 0.0 if fit_rank == 0 else 0.5,
        f"{prefix}_selected_handle": selected_handle,
        f"{prefix}_selected_source": selected_source,
        f"{prefix}_selected_rank": selected_rank,
        f"{prefix}_selected_confidence": 0.0 if selected_rank == 0 else 0.5,
        f"{prefix}_acquired": acquired,
        f"{prefix}_revised": False,
        f"{prefix}_structural_event": event,
        f"{prefix}_candidate_handle": candidate_handle,
        f"{prefix}_candidate_source": candidate_source,
        f"{prefix}_candidate_rank": candidate_rank,
        f"{prefix}_candidate_streak": candidate_streak,
        f"{prefix}_candidate_last_evidence_count": candidate_last,
        f"{prefix}_candidate_renewed": candidate_renewed,
    }


def _synthetic_official_payload(seed=17, freeze_digest=None):
    target_pair = (0, 1)
    structure_digest = _digest(f"structure-{seed}")
    if freeze_digest is None:
        freeze_digest = "b" * 64
    rows = []
    for scenario, steps, target_rank, state_expected in EXPECTED_SCENARIOS:
        for step in range(steps):
            fit_performed = step >= 479 and (step - 479) % 480 == 0
            fit_pair = target_pair if fit_performed and target_rank > 0 else None
            fit_rank = target_rank if fit_performed else 0
            acquired = bool(state_expected and step == steps - 1)
            selected_pair = target_pair if acquired else None
            selected_rank = target_rank if acquired else 0
            if not fit_performed:
                event = "none"
            elif acquired:
                event = "acquisition"
            elif fit_rank > 0:
                event = "acquisition_candidate"
            else:
                event = "null_fit"
            if target_rank > 0 and state_expected and 479 <= step < 959:
                candidate_pair = target_pair
                candidate_rank = target_rank
                candidate_streak = 1
                candidate_last = 480
                candidate_renewed = step == 479
            elif target_rank > 0 and not state_expected and step == steps - 1:
                candidate_pair = target_pair
                candidate_rank = target_rank
                candidate_streak = 1
                candidate_last = 480
                candidate_renewed = True
            else:
                candidate_pair = None
                candidate_rank = 0
                candidate_streak = 0
                candidate_last = None
                candidate_renewed = bool(acquired)
            commitment = _digest(f"commitment-{scenario}-{step}")
            transition = _digest(f"transition-{scenario}-{step}")
            outcome = _digest(f"outcome-{scenario}-{step}")
            row = {
                "schema": V031_SCHEMA,
                "seed": seed,
                "scenario": scenario,
                "scenario_step": step,
                "target_handle": target_pair[0],
                "target_source": target_pair[1],
                "target_rank": target_rank,
                "structure_digest": structure_digest,
                **_model_fields(
                    prefix="conditional",
                    fit_performed=fit_performed,
                    fit_pair=fit_pair,
                    fit_rank=fit_rank,
                    selected_pair=selected_pair,
                    selected_rank=selected_rank,
                    acquired=acquired,
                    event=event,
                    candidate_pair=candidate_pair,
                    candidate_rank=candidate_rank,
                    candidate_streak=candidate_streak,
                    candidate_last=candidate_last,
                    candidate_renewed=candidate_renewed,
                ),
                **_model_fields(
                    prefix="global",
                    fit_performed=fit_performed,
                    fit_pair=fit_pair,
                    fit_rank=fit_rank,
                    selected_pair=selected_pair,
                    selected_rank=selected_rank,
                    acquired=acquired,
                    event=event,
                    candidate_pair=candidate_pair,
                    candidate_rank=candidate_rank,
                    candidate_streak=candidate_streak,
                    candidate_last=candidate_last,
                    candidate_renewed=candidate_renewed,
                ),
                "commitments_equal": True,
                "conditional_pre_state_digest": _digest(
                    f"conditional-state-{scenario}-{step}"
                ),
                "conditional_post_state_digest": _digest(
                    f"conditional-state-{scenario}-{step + 1}"
                ),
                "conditional_commitment_digest": commitment,
                "conditional_transition_digest": transition,
                "conditional_outcome_digest": outcome,
                "global_pre_state_digest": _digest(
                    f"global-state-{scenario}-{step}"
                ),
                "global_post_state_digest": _digest(
                    f"global-state-{scenario}-{step + 1}"
                ),
                "global_commitment_digest": commitment,
                "global_transition_digest": transition,
                "global_outcome_digest": outcome,
                "conditional_prequential_chain": True,
                "global_prequential_chain": True,
                "source_energy_error": 0.0,
                "hidden_truth_passed_to_model": False,
            }
            rows.append(row)
    summary = recompute_seed_summary(
        rows,
        seed=seed,
        expected_schema=V031_SCHEMA,
        structure_digest=structure_digest,
    )
    return {
        "schema": V031_SCHEMA,
        "seed": seed,
        "cohort": "official",
        "config": asdict(V031_FROZEN_CANDIDATE_CONFIG),
        "seed_summary": summary,
        "rows": rows,
        "receipt": {
            "seed": seed,
            "cohort": "official",
            "structure_digest": structure_digest,
            "world_seed_never_passed_to_model": True,
            "learner_rng_independent_of_world_seed": True,
            "hidden_pair_never_passed_to_model": True,
            "hidden_rank_never_passed_to_model": True,
            "hidden_bases_never_passed_to_model": True,
            "scenario_labels_never_passed_to_model": True,
            "rank_test_method": (
                "cross_fitted_reduced_rank_randomization_bootstrap"
            ),
            "rank_test_exact": False,
            "rank_test_semantics": (
                "conditional one-step add-one composite-null bootstrap on two "
                "disjoint confirmation folds with observed history held fixed"
            ),
            "observed_history_held_fixed": True,
            "interventions_reversible_and_synthetic": True,
        },
        "freeze_manifest_sha256": freeze_digest,
    }


def _verify(payload):
    verify_official_part_payload(
        payload,
        seed=payload["seed"],
        expected_schema=V031_SCHEMA,
        expected_config=asdict(V031_FROZEN_CANDIDATE_CONFIG),
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


def _manifest_fixture(tmp_path):
    root = tmp_path / "project"
    validation = root / "validation"
    source = root / "src" / "frozen.py"
    validation.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    source.write_bytes(b"frozen\n")
    manifest = validation / "V0_31_PREOUTCOME_FREEZE.json"
    checksum = validation / "V0_31_PREOUTCOME_FREEZE.json.sha256"
    payload = {
        "experiment": {
            "config_defaults": {"block_size": 20},
            "schema": EXPECTED_EXPERIMENT_SCHEMA,
        },
        "files": {
            "src/frozen.py": {
                "size": source.stat().st_size,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        },
        "official_seed_access_before_freeze": "none",
        "official_seeds": [6001, 6007, 6013, 6019, 6029, 6037, 6043, 6053],
        "pilot_seeds": [5901, 5907, 5913, 5919],
        "official_runtime": EXPECTED_OFFICIAL_RUNTIME,
        "schema": "rrct.v031.preoutcome_freeze.v1",
        "status": "sealed_before_official_outcomes",
        "version": "0.31.0.dev1",
    }
    raw = _canonical_json(payload)
    manifest.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    checksum.write_text(f"{digest}  {manifest.name}\n", encoding="ascii")
    return root, source, manifest, checksum, digest


def test_v031_producer_and_independent_verifier_schemas_match_exactly():
    tree = ast.parse(Path(experiment_module.__file__).read_text(encoding="utf-8"))
    literal_key_sets = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        try:
            literal_key_sets.append(
                {ast.literal_eval(key) for key in node.keys}
            )
        except (TypeError, ValueError):
            continue

    row = next(keys for keys in literal_key_sets if "conditional_fit_performed" in keys)
    receipt = next(keys for keys in literal_key_sets if "rank_test_method" in keys)
    episode = next(
        keys
        for keys in literal_key_sets
        if "conditional_state_transition_exact" in keys
    )
    assert row == integrity_module._ROW_KEYS
    assert receipt == integrity_module._RECEIPT_KEYS
    assert episode == integrity_module._EPISODE_SUMMARY_KEYS


def test_v031_exact_row_schedule_and_full_summary_recompute_pass():
    payload = _synthetic_official_payload()
    assert V031_SCHEMA == EXPECTED_EXPERIMENT_SCHEMA
    assert len(payload["rows"]) == EXPECTED_ROWS_PER_SEED == 3840
    integration = payload["seed_summary"]["episodes"]["rank_two_integration"]
    assert integration["scenario_steps"] == 960
    assert integration["conditional_exact"]
    assert integration["conditional_state_exact"]
    assert integration["conditional_acquired"]
    assert integration["conditional_fit_steps"] == [479, 959]
    assert integration["conditional_all_fits_exact"]
    assert integration["conditional_acquisition_count"] == 1
    assert integration["conditional_state_transition_exact"]
    one_window = payload["seed_summary"]["episodes"]["rank_two_baseline"]
    assert not one_window["state_admission_expected"]
    assert one_window["conditional_state_exact"]
    assert not one_window["conditional_acquired"]
    assert one_window["conditional_fit_steps"] == [479]
    assert one_window["conditional_state_transition_exact"]
    _verify(payload)


def test_v031_payload_rejects_tampered_recomputed_summary():
    payload = _synthetic_official_payload()
    payload["seed_summary"]["episodes"]["rank_three"]["conditional_rank"] = 2
    with pytest.raises(ValueError, match="summary mismatch"):
        _verify(payload)


def test_v031_payload_rejects_tampered_fit_sequence_summary_and_rows():
    integration_start = 6 * 480
    first_fit = integration_start + 479
    payload = _synthetic_official_payload()
    payload["seed_summary"]["episodes"]["rank_two_integration"][
        "conditional_state_transition_exact"
    ] = False
    with pytest.raises(ValueError, match="summary mismatch"):
        _verify(payload)

    payload = _synthetic_official_payload()
    payload["rows"][first_fit]["conditional_candidate_streak"] = 2
    with pytest.raises(ValueError, match="summary mismatch"):
        _verify(payload)

    payload = _synthetic_official_payload()
    payload["rows"][first_fit]["conditional_fit_source"] = 2
    with pytest.raises(ValueError, match="summary mismatch"):
        _verify(payload)


@pytest.mark.parametrize(
    ("field", "wrong"),
    (
        ("scenario", "rank_three"),
        ("scenario_step", 4),
        ("target_rank", 7),
        ("seed", 99),
    ),
)
def test_v031_payload_rejects_schedule_identity_tampering(field, wrong):
    payload = _synthetic_official_payload()
    payload["rows"][0][field] = wrong
    with pytest.raises(ValueError, match="schedule"):
        _verify(payload)


def test_v031_payload_rejects_missing_row_and_wrong_fit_time():
    payload = _synthetic_official_payload()
    payload["rows"].pop(10)
    with pytest.raises(ValueError, match="row count"):
        _verify(payload)

    payload = _synthetic_official_payload()
    payload["rows"][10]["conditional_fit_performed"] = True
    with pytest.raises(ValueError, match="fit schedule"):
        _verify(payload)


def test_v031_payload_rejects_target_and_structure_substitution():
    payload = _synthetic_official_payload()
    payload["rows"][700]["target_source"] = 2
    with pytest.raises(ValueError, match="target-pair"):
        _verify(payload)

    payload = _synthetic_official_payload()
    payload["rows"][700]["structure_digest"] = "c" * 64
    with pytest.raises(ValueError, match="structure receipt"):
        _verify(payload)


def test_v031_payload_rejects_broken_state_and_paired_world_digest_chains():
    payload = _synthetic_official_payload()
    payload["rows"][10]["conditional_pre_state_digest"] = "c" * 64
    with pytest.raises(ValueError, match="state digest chain"):
        _verify(payload)

    payload = _synthetic_official_payload()
    payload["rows"][10]["global_outcome_digest"] = "d" * 64
    with pytest.raises(ValueError, match="paired-world outcome_digest"):
        _verify(payload)


def test_v031_payload_rejects_hidden_exposure_and_history_semantics_tampering():
    payload = _synthetic_official_payload()
    payload["rows"][0]["hidden_truth_passed_to_model"] = True
    with pytest.raises(ValueError, match="hidden-truth exposure"):
        _verify(payload)

    payload = _synthetic_official_payload()
    payload["receipt"]["observed_history_held_fixed"] = False
    with pytest.raises(ValueError, match="receipt attestation mismatch"):
        _verify(payload)


def test_v031_official_runtime_exact_receipt_and_mismatches(monkeypatch):
    _set_valid_official_runtime(monkeypatch)
    assert verify_official_runtime() == EXPECTED_OFFICIAL_RUNTIME
    monkeypatch.setattr(
        integrity_module.sys,
        "version_info",
        (3, 12, 12, "final", 0),
    )
    with pytest.raises(RuntimeError, match="official Python runtime mismatch"):
        verify_official_runtime()

    _set_valid_official_runtime(monkeypatch)
    monkeypatch.setattr(integrity_module.np, "__version__", "2.2.5")
    with pytest.raises(RuntimeError, match="official NumPy runtime mismatch"):
        verify_official_runtime()

    _set_valid_official_runtime(monkeypatch)
    monkeypatch.setenv("OMP_NUM_THREADS", "2")
    with pytest.raises(RuntimeError, match="thread environment mismatch"):
        verify_official_runtime()


def test_v031_freeze_manifest_detects_file_and_companion_tampering(tmp_path):
    root, source, manifest, checksum, digest = _manifest_fixture(tmp_path)
    assert verify_freeze_manifest(manifest, checksum, project_root=root) == digest
    source.write_bytes(b"broken\n")
    with pytest.raises(ValueError, match="sha256 mismatch|size mismatch"):
        verify_freeze_manifest(manifest, checksum, project_root=root)

    source.write_bytes(b"frozen\n")
    checksum.write_text(f"{'0' * 64}  {manifest.name}\n", encoding="ascii")
    with pytest.raises(ValueError, match="checksum companion mismatch"):
        verify_freeze_manifest(manifest, checksum, project_root=root)


def test_v031_permanent_journal_blocks_replay_and_binds_output(tmp_path):
    final = tmp_path / "17.pkl"
    temporary = tmp_path / "17.pkl.tmp"
    journal_path = tmp_path / "17.lock"
    digest = "a" * 64
    journal = PermanentSeedJournal.create(
        journal_path,
        seed=17,
        output_basename=final.name,
        freeze_manifest_sha256=digest,
    )
    with pytest.raises(FileExistsError):
        PermanentSeedJournal.create(
            journal_path,
            seed=17,
            output_basename=final.name,
            freeze_manifest_sha256=digest,
        )
    size, output_hash = write_pickle_atomic_once(
        {"seed": 17, "cohort": "official"}, final, temporary
    )
    journal.append(
        "completed",
        seed=17,
        output=final.name,
        freeze_manifest_sha256=digest,
        output_size=size,
        output_sha256=output_hash,
    )
    journal.close()
    verify_completed_seed_journal(
        journal_path,
        seed=17,
        output_path=final,
        freeze_manifest_sha256=digest,
    )
    with pytest.raises(ValueError, match="manifest mismatch"):
        verify_completed_seed_journal(
            journal_path,
            seed=17,
            output_path=final,
            freeze_manifest_sha256="b" * 64,
        )


def test_v031_atomic_publish_never_clobbers_concurrently_created_final(
    tmp_path, monkeypatch
):
    final = tmp_path / "17.pkl"
    temporary = tmp_path / "17.pkl.tmp"
    original_link = integrity_module.os.link

    def concurrent_link(source, destination, *, follow_symlinks):
        Path(destination).write_bytes(b"concurrent-final")
        return original_link(
            source, destination, follow_symlinks=follow_symlinks
        )

    monkeypatch.setattr(integrity_module.os, "link", concurrent_link)
    with pytest.raises(FileExistsError):
        write_pickle_atomic_once({"seed": 17}, final, temporary)
    assert final.read_bytes() == b"concurrent-final"
    assert temporary.is_file()


def test_v031_permanent_pilot_journal_blocks_replay_and_binds_runtime(tmp_path):
    final = tmp_path / "17.pkl"
    temporary = tmp_path / "17.pkl.tmp"
    journal_path = tmp_path / "17.lock"
    journal = PermanentPilotJournal.create(
        journal_path,
        seed=17,
        output_basename=final.name,
        runtime_receipt=EXPECTED_OFFICIAL_RUNTIME,
    )
    with pytest.raises(FileExistsError):
        PermanentPilotJournal.create(
            journal_path,
            seed=17,
            output_basename=final.name,
            runtime_receipt=EXPECTED_OFFICIAL_RUNTIME,
        )
    size, output_hash = write_pickle_atomic_once(
        {"seed": 17, "cohort": "pilot"}, final, temporary
    )
    journal.append(
        "completed",
        seed=17,
        output=final.name,
        experiment_schema=V031_SCHEMA,
        runtime_receipt=EXPECTED_OFFICIAL_RUNTIME,
        output_size=size,
        output_sha256=output_hash,
    )
    journal.close()
    verify_completed_pilot_journal(
        journal_path,
        seed=17,
        output_path=final,
        runtime_receipt=EXPECTED_OFFICIAL_RUNTIME,
    )


def test_v031_payload_copy_has_no_accidental_shared_summary_mutation():
    payload = _synthetic_official_payload()
    clone = copy.deepcopy(payload)
    clone["seed_summary"]["integrity"] = False
    assert payload["seed_summary"]["integrity"] is True


def test_v031_freezer_validates_complete_retained_development_evidence():
    experiment = (
        freeze_module.PROJECT_ROOT
        / "src/rrct/conditional_rank_inference_experiment.py"
    )
    row_fields = freeze_module._literal_dict_fieldnames(
        experiment, "conditional_fit_performed"
    )
    episode_fields = freeze_module._literal_dict_fieldnames(
        experiment, "conditional_state_transition_exact"
    )
    config = freeze_module._literal_dataclass_defaults(
        experiment, "V031RunConfig"
    )
    pilot = freeze_module._verify_pilot(config, row_fields, episode_fields)
    calibration = freeze_module._verify_calibration()
    histories = freeze_module._verify_preserved_histories()
    assert pilot["retained_rows"] == 15_360
    assert pilot["primary_gates_passed"] == 10
    assert calibration["retained_worlds"] == 200
    assert calibration["primary_gates_passed"] == 9
    assert {value["file_count"] for value in histories.values()} == {4, 400}


def test_v031_frozen_set_covers_source_tests_protocol_and_all_histories():
    paths = set(freeze_module._frozen_paths())
    for directory in (
        freeze_module.PROJECT_ROOT / "src",
        freeze_module.PROJECT_ROOT / "tests",
    ):
        for path in directory.rglob("*"):
            if (
                path.is_file()
                and not path.is_symlink()
                and "__pycache__" not in path.parts
                and ".pytest_cache" not in path.parts
            ):
                assert path.relative_to(freeze_module.PROJECT_ROOT) in paths
    for name in freeze_module.V031_VALIDATION_FILES:
        assert Path(name) in paths
    for directory in (
        freeze_module.PILOT_OUTPUT,
        freeze_module.PILOT_PARTS,
        freeze_module.CALIBRATION_OUTPUT,
        freeze_module.CALIBRATION_PARTS,
        *freeze_module.PRESERVED_DIRECTORIES,
    ):
        for path in directory.iterdir():
            assert path.relative_to(freeze_module.PROJECT_ROOT) in paths
    assert not any(
        set(path.parts) & {"build", "dist", "__pycache__", ".pytest_cache"}
        for path in paths
    )


def test_v031_static_seed_parser_rejects_bool_and_float_coercion(tmp_path):
    source = tmp_path / "declarations.py"
    source.write_text("SEEDS = tuple(range(3, 6))\n", encoding="utf-8")
    assert freeze_module._static_integer_sequence(source, "SEEDS") == (3, 4, 5)
    source.write_text("SEEDS = (3, True, 5)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="static integer sequence"):
        freeze_module._static_integer_sequence(source, "SEEDS")
    source.write_text("SEEDS = {3, 4, 5}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="static integer sequence"):
        freeze_module._static_integer_sequence(source, "SEEDS")
    source.write_text("SEEDS = {3: 4, 5: 6}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="static integer sequence"):
        freeze_module._static_integer_sequence(source, "SEEDS")
    source.write_text("SEEDS = (3, 4.0, 5)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="static integer sequence"):
        freeze_module._static_integer_sequence(source, "SEEDS")


def test_v031_exact_declaration_comparison_rejects_bool_float_drift():
    assert not freeze_module._exact_literal_equal(True, 1)
    assert not freeze_module._exact_literal_equal(4.0, 4)
    assert not freeze_module._exact_literal_equal(
        (31_211.0, 31_213), (31_211, 31_213)
    )
    assert not freeze_module._exact_literal_equal(
        ((None, 240.0), (240, 360), (360, 480)),
        ((None, 240), (240, 360), (360, 480)),
    )
    changed_config = dict(freeze_module.EXPECTED_CONFIG_DEFAULTS)
    changed_config["null_permutations"] = 128.0
    assert not freeze_module._exact_literal_equal(
        changed_config, freeze_module.EXPECTED_CONFIG_DEFAULTS
    )
    changed_scenarios = list(freeze_module.SOURCE_SCENARIOS)
    name, strengths, _rank = changed_scenarios[1]
    changed_scenarios[1] = (name, strengths, True)
    assert not freeze_module._exact_literal_equal(
        tuple(changed_scenarios), freeze_module.SOURCE_SCENARIOS
    )


def test_v031_immutable_evidence_roots_reject_coherent_hash_updates(
    tmp_path, monkeypatch
):
    copied = tmp_path / freeze_module.PILOT_OUTPUT.name
    shutil.copytree(freeze_module.PILOT_OUTPUT, copied)
    summary_path = copied / "v031_conditional_rank_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["seed_summaries"][0]["episodes"]["rank_one_baseline"][
        "conditional_rank"
    ] = 0
    summary_path.write_bytes(freeze_module._canonical_json(summary))
    hashes_path = copied / "v031_conditional_rank_sha256.json"
    hashes = json.loads(hashes_path.read_text(encoding="utf-8"))
    hashes[summary_path.name] = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    hashes_path.write_bytes(freeze_module._canonical_json(hashes))
    monkeypatch.setattr(freeze_module, "PILOT_OUTPUT", copied)
    with pytest.raises(ValueError, match="immutable evidence tree root mismatch"):
        freeze_module._evidence_tree_receipt(copied)


def test_v031_preserved_history_root_rejects_substitution(tmp_path):
    original = freeze_module.PRESERVED_DIRECTORIES[0]
    copied = tmp_path / original.name
    shutil.copytree(original, copied)
    summary_path = copied / "v031_conditional_rank_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["all_primary_gates_pass"] = False
    summary_path.write_bytes(freeze_module._canonical_json(summary))
    with pytest.raises(ValueError, match="immutable evidence tree root mismatch"):
        freeze_module._evidence_tree_receipt(copied)


def test_v031_calibration_root_rejects_coherent_gate_and_hash_tamper(tmp_path):
    copied = tmp_path / freeze_module.CALIBRATION_OUTPUT.name
    shutil.copytree(freeze_module.CALIBRATION_OUTPUT, copied)
    summary_path = copied / "v031_rank_calibration_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["counts"]["conditional_fold_a_rejections"] = 0
    summary_path.write_bytes(freeze_module._canonical_json(summary))
    hashes_path = copied / "v031_rank_calibration_sha256.json"
    hashes = json.loads(hashes_path.read_text(encoding="utf-8"))
    hashes[summary_path.name] = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    hashes_path.write_bytes(freeze_module._canonical_json(hashes))
    with pytest.raises(ValueError, match="immutable evidence tree root mismatch"):
        freeze_module._evidence_tree_receipt(copied)


def test_v031_source_declarations_match_explicit_freeze_constants():
    experiment = (
        freeze_module.PROJECT_ROOT
        / "src/rrct/conditional_rank_inference_experiment.py"
    )
    calibration = (
        freeze_module.PROJECT_ROOT
        / "src/rrct/conditional_rank_calibration_diagnostic.py"
    )
    assert (
        freeze_module._literal_assignment(experiment, "V031_SCENARIOS")
        == freeze_module.SOURCE_SCENARIOS
    )
    assert freeze_module._literal_dataclass_defaults(
        experiment, "V031RunConfig"
    ) == freeze_module.EXPECTED_CONFIG_DEFAULTS
    assert freeze_module._assignment_matches_expression(
        experiment,
        "V031_SCENARIO_WINDOWS",
        "{name: (2 if name == 'rank_two_integration' else 1) "
        "for name, _, _ in V031_SCENARIOS}",
    )
    assert freeze_module._assignment_matches_expression(
        experiment, "V031_FROZEN_CANDIDATE_CONFIG", "V031RunConfig()"
    )
    assert all(
        freeze_module._literal_assignment(calibration, name) == expected
        for name, expected in freeze_module.EXPECTED_CALIBRATION_CONSTANTS.items()
    )


def test_v031_freezer_refuses_opened_or_broken_link_official_paths(
    tmp_path, monkeypatch
):
    opened = tmp_path / "official"
    opened.mkdir()
    monkeypatch.setattr(freeze_module, "OFFICIAL_DIRECTORIES", (opened,))
    with pytest.raises(FileExistsError, match="already opened"):
        freeze_module._verify_official_unopened()

    broken = tmp_path / "official-parts"
    broken.symlink_to(tmp_path / "missing-target", target_is_directory=True)
    monkeypatch.setattr(freeze_module, "OFFICIAL_DIRECTORIES", (broken,))
    with pytest.raises(FileExistsError, match="already opened"):
        freeze_module._verify_official_unopened()


def test_v031_freezer_is_ast_only_canonical_and_one_shot(tmp_path, monkeypatch):
    root = tmp_path / "project"
    experiment = root / "src/rrct/conditional_rank_inference_experiment.py"
    calibration = root / "src/rrct/conditional_rank_calibration_diagnostic.py"
    version = root / "src/rrct/_version.py"
    test_file = root / "tests/test_frozen.py"
    validation = root / "validation"
    for parent in (experiment.parent, test_file.parent, validation):
        parent.mkdir(parents=True, exist_ok=True)
    experiment.write_text(
        "raise RuntimeError('must never import experiment')\n"
        f"V031_SCHEMA = {freeze_module.EXPERIMENT_SCHEMA!r}\n"
        f"V031_PILOT_SEEDS = {freeze_module.PILOT_SEEDS!r}\n"
        f"V031_OFFICIAL_SEEDS = {freeze_module.OFFICIAL_SEEDS!r}\n"
        "V031_OBSERVATION_DIM = 12\nV031_PROCESS_DIM = 8\n"
        "V031_SOURCE_COUNT = 6\nV031_HANDLE_COUNT = 4\n"
        f"V031_SCENARIOS = {freeze_module.SOURCE_SCENARIOS!r}\n"
        "V031_SCENARIO_WINDOWS = {name: (2 if name == "
        "'rank_two_integration' else 1) for name, _, _ in V031_SCENARIOS}\n"
        "class V031RunConfig:\n"
        + "".join(
            f"    {name}: {type(value).__name__} = {value!r}\n"
            for name, value in freeze_module.EXPECTED_CONFIG_DEFAULTS.items()
        )
        + "V031_FROZEN_CANDIDATE_CONFIG = V031RunConfig()\n",
        encoding="utf-8",
    )
    calibration.write_text(
        f"V031_CALIBRATION_SCHEMA = {freeze_module.CALIBRATION_SCHEMA!r}\n"
        "V031_CALIBRATION_SEEDS = tuple(range(891000, 891200))\n"
        + "".join(
            f"{name} = {value!r}\n"
            for name, value in freeze_module.EXPECTED_CALIBRATION_CONSTANTS.items()
        )
        + "V031_CALIBRATION_CONFIG = V031RunConfig("
        "null_permutations=V031_CALIBRATION_RANDOMIZATIONS, "
        "half_null_permutations=V031_CALIBRATION_RANDOMIZATIONS, "
        "null_quantile=V031_CALIBRATION_QUANTILE)\n"
        "def run_rank_calibration_world():\n"
        "    proposal = values[:240]\n"
        "    confirmation_a = values[240:360]\n"
        "    confirmation_b = values[360:480]\n"
        "    _conditional_fold_result(salt=31211)\n"
        "    _conditional_fold_result(salt=31213)\n"
        "    _global_sharp_null_fold_result(salt=31501)\n"
        "    _global_sharp_null_fold_result(salt=31503)\n",
        encoding="utf-8",
    )
    version.write_text(
        f"__version__ = {freeze_module.VERSION!r}\n", encoding="utf-8"
    )
    test_file.write_text("def test_frozen(): pass\n", encoding="utf-8")
    (root / "MANIFEST.in").write_text("include README.md\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    manifest = validation / "V0_31_PREOUTCOME_FREEZE.json"
    checksum = validation / "V0_31_PREOUTCOME_FREEZE.json.sha256"
    frozen = (
        Path("MANIFEST.in"),
        Path("pyproject.toml"),
        experiment.relative_to(root),
        calibration.relative_to(root),
        version.relative_to(root),
        test_file.relative_to(root),
    )
    row_fields = tuple(f"field_{index}" for index in range(59))
    monkeypatch.setattr(freeze_module, "PROJECT_ROOT", root)
    monkeypatch.setattr(freeze_module, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(freeze_module, "CHECKSUM_PATH", checksum)
    monkeypatch.setattr(
        freeze_module, "_verify_runtime", lambda: freeze_module.OFFICIAL_RUNTIME
    )
    monkeypatch.setattr(freeze_module, "_verify_official_unopened", lambda: None)
    monkeypatch.setattr(
        freeze_module,
        "_verify_parent_receipts",
        lambda: {"preoutcome_freeze_sha256": "a" * 64},
    )
    monkeypatch.setattr(
        freeze_module,
        "_literal_dict_fieldnames",
        lambda _path, marker: row_fields
        if marker == "conditional_fit_performed"
        else ("scenario",),
    )
    monkeypatch.setattr(
        freeze_module, "_verify_pilot", lambda *_args: {"status": "PASS"}
    )
    monkeypatch.setattr(
        freeze_module, "_verify_calibration", lambda: {"status": "PASS"}
    )
    monkeypatch.setattr(
        freeze_module, "_verify_preserved_histories", lambda: {"history": "bound"}
    )
    monkeypatch.setattr(freeze_module, "_frozen_paths", lambda: frozen)
    digest = freeze_module.freeze(passed=375, skipped=2, subtests=89)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest.read_bytes() == freeze_module._canonical_json(payload)
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == digest
    assert checksum.read_text(encoding="ascii") == f"{digest}  {manifest.name}\n"
    assert set(payload["files"]) == {path.as_posix() for path in frozen}
    assert payload["official_seed_access_before_freeze"] == "none"
    with pytest.raises(FileExistsError, match="already exists"):
        freeze_module.freeze(passed=375, skipped=2, subtests=89)
