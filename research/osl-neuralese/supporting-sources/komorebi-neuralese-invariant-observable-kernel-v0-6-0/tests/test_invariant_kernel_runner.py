import hashlib
import json
from pathlib import Path

import pytest
import torch

import run_invariant_kernel as runner
from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.invariant_kernel_eval import build_suffix_word_bank
from komorebi_neuralese.invariant_kernel_training import (
    InvariantKernelTrainConfig,
    build_invariant_kernel_model,
    train_paired_invariant_kernel_panel,
)


def _seal_checkpoint_panel(directory: Path, seeds=(1,)) -> dict:
    checkpoint_dir = directory / "checkpoints"
    checkpoint_dir.mkdir()
    rows = []
    for seed in seeds:
        for arm in runner.PRIMARY_INVARIANT_KERNEL_ARMS:
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
        "schema": "komorebi.neuralese.invariant_kernel.checkpoint_seal.v1",
        "version": runner.VERSION,
        "source_digest": "a" * 64,
        "preregistration_sha256": "b" * 64,
        "count": len(rows),
        "checkpoints": rows,
    }
    seal["seal_sha256"] = hashlib.sha256(
        runner.canonical_json_bytes(seal)
    ).hexdigest()
    return seal


def test_preregistration_matches_executable_profiles_and_arm_order():
    registered = runner.validate_preregistration()
    assert registered["training_plan_version"] == runner.V06_PLAN_VERSION
    assert [row["name"] for row in registered["arms"]] == list(
        runner.PRIMARY_INVARIANT_KERNEL_ARMS
    )
    assert registered["profiles"] == {
        name: runner._profile_as_registered(profile)
        for name, profile in runner.PROFILE_CONFIG.items()
    }
    assert registered["intervention_contract"]["algebraic_suffix_lengths"] == list(
        runner.ALGEBRAIC_SUFFIX_LENGTHS
    )
    assert registered["numerical_contract"]["integer_minimum_count_equality"] == (
        "passes"
    )
    learned_objectives = next(
        row["objectives"]
        for row in registered["arms"]
        if row["name"] == "learned_intertwiner"
    )
    assert "simplex_gram" in learned_objectives
    assert "simplex_chart" not in learned_objectives
    learned_losses = registered["loss_contract"]["learned_intertwiner"]
    assert learned_losses["simplex_gram_weight"] == 0.1
    assert "simplex_chart_weight" not in learned_losses
    relation_exposure = registered["loss_contract"]["relation_exposure"]
    assert relation_exposure == {
        "selection": "first_n_accepted_rows_without_replacement",
        "contexts_per_step": 8,
        "cells_per_context": 9,
        "cells_per_step_total": 72,
        "aggregation": "mean_over_contexts_and_cells_not_sum",
        "shared_across_arms": True,
    }
    for name, profile in runner.PROFILE_CONFIG.items():
        assert profile["auxiliary_contexts"] == 8, name
        config = runner.train_config(profile, profile["seeds"][0], "cpu")
        assert config.auxiliary_contexts == profile["auxiliary_contexts"], name
        assert config.auxiliary_delay_steps == profile["auxiliary_delay_steps"], name
        assert config.auxiliary_ramp_end_step == profile["auxiliary_ramp_end_step"], name
        assert config.weights.observer_anchor_geometry == 0.1, name


def test_output_directory_must_be_empty(tmp_path):
    runner.assert_clean_output(tmp_path / "new")
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "receipt.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        runner.assert_clean_output(occupied)


def test_checkpoint_seal_is_complete_canonical_and_tamper_evident(tmp_path):
    seal = _seal_checkpoint_panel(tmp_path)
    indexed = runner.validate_checkpoint_seal(
        tmp_path,
        seal,
        {"seeds": (1,)},
        expected_source_digest="a" * 64,
        expected_preregistration_sha256="b" * 64,
    )
    assert set(indexed) == {
        (1, arm) for arm in runner.PRIMARY_INVARIANT_KERNEL_ARMS
    }
    (tmp_path / seal["checkpoints"][0]["path"]).write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="bytes do not match"):
        runner.validate_checkpoint_seal(
            tmp_path,
            seal,
            {"seeds": (1,)},
            expected_source_digest="a" * 64,
            expected_preregistration_sha256="b" * 64,
        )


def test_checkpoint_seal_rejects_noncanonical_order(tmp_path):
    seal = _seal_checkpoint_panel(tmp_path)
    seal["checkpoints"] = list(reversed(seal["checkpoints"]))
    unsigned = dict(seal)
    unsigned.pop("seal_sha256")
    seal["seal_sha256"] = hashlib.sha256(
        runner.canonical_json_bytes(unsigned)
    ).hexdigest()
    with pytest.raises(RuntimeError, match="canonical order"):
        runner.validate_checkpoint_seal(
            tmp_path,
            seal,
            {"seeds": (1,)},
            expected_source_digest="a" * 64,
            expected_preregistration_sha256="b" * 64,
        )


def test_value_summary_fails_closed_on_nonfinite_or_missing_values():
    summary = runner._value_summary([1.0, float("nan"), None])
    assert summary["count"] == 3
    assert summary["finite_count"] == 1
    assert summary["mean"] is None
    assert summary["maximum"] is None
    assert not runner._complete_numeric(summary)


def test_source_digest_excludes_result_and_cache_trees(tmp_path, monkeypatch):
    (tmp_path / "source.py").write_text("x = 1\n", encoding="utf-8")
    cache = tmp_path / ".pytest_cache"
    cache.mkdir()
    (cache / "README.md").write_text("transient\n", encoding="utf-8")
    results = tmp_path / "results"
    results.mkdir()
    (results / "RESULTS.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    digest, names = runner.source_digest()
    assert len(digest) == 64
    assert names == ["source.py"]


def test_checkpoint_payload_roundtrips_through_weights_only_loader(tmp_path):
    config = InvariantKernelTrainConfig(
        seed=31,
        steps=1,
        batch_size=8,
        warmup_steps=1,
        checkpoints=1,
    )
    trained = train_paired_invariant_kernel_panel(
        config,
        arm_names=("hard_kernel_supervised",),
    )["hard_kernel_supervised"]
    payload = runner.checkpoint_payload(
        trained,
        source_sha256="c" * 64,
        preregistration_sha256="d" * 64,
    )
    path = tmp_path / "safe.pt"
    torch.save(payload, path)
    loaded = torch.load(path, map_location="cpu", weights_only=True)
    assert set(loaded) == set(payload)
    assert runner._json_safe_tree(loaded)
    assert all(isinstance(value, torch.Tensor) for value in loaded["state_dict"].values())


def test_geometry_never_invents_L_K_split_for_learned_observer():
    config = InvariantKernelTrainConfig(seed=37, steps=1, batch_size=8)
    contexts = EpisodeGenerator(701).sample(3, 0, family="d4")
    words = build_suffix_word_bank(
        operator_count=2,
        samples_per_length=8,
        seed=702,
        lengths=runner.ALGEBRAIC_SUFFIX_LENGTHS,
    )
    learned = build_invariant_kernel_model(config, "learned_intertwiner")
    hard = build_invariant_kernel_model(config, "hard_kernel_supervised")
    learned_geometry, _ = runner.evaluate_geometry(learned, contexts, words, seed=703)
    hard_geometry, _ = runner.evaluate_geometry(hard, contexts, words, seed=704)
    assert learned_geometry["extraction"]["source"] == "registered_learned_rank7_observer"
    assert learned_geometry["typed_three_way"]["status"] == "NOT_EVALUATED"
    assert "no scientifically registered" in learned_geometry["typed_three_way"]["reason"]
    assert set(learned_geometry["two_way_audits"]["paths"]) == {
        "odd_length3",
        "even_length4",
    }
    assert all(
        row["all_finite"]
        for row in learned_geometry["two_way_audits"]["paths"].values()
    )
    assert hard_geometry["extraction"]["source"] == "registered_three_way_7_plus_1_plus_4"
    assert hard_geometry["typed_three_way"]["status"] == "EVALUATED"
    assert set(hard_geometry["typed_three_way"]["paths"]) == {
        "odd_length3",
        "even_length4",
    }


def test_hard_null_perturbation_is_nonzero_and_behaviorally_inert():
    config = InvariantKernelTrainConfig(seed=41, steps=1, batch_size=8)
    model = build_invariant_kernel_model(config, "hard_kernel_supervised")
    batches = {
        length: EpisodeGenerator(800 + length).sample(4, length, family="d4")
        for length in runner.INTERVENTION_SUFFIX_LENGTHS
    }
    result = runner.evaluate_null_perturbations(
        model,
        model.behavioral_projector(),
        batches,
        seed=805,
    )
    assert result["all_conditions_complete"]
    assert result["prediction_retention"] == 1.0
    assert result["relative_centered_logit_effect"]["maximum"] < 5e-5
    assert all(row["minimum_probe_norm"] > 0.99 for row in result["conditions"])
    assert result["memory_claim_eligible"] is False


def test_threshold_equality_fails_in_both_directions():
    assert not runner._strict_less(0.1, 0.1)
    assert not runner._strict_greater(0.1, 0.1)
    assert runner._strict_less(0.09, 0.1)
    assert runner._strict_greater(0.11, 0.1)


def test_native_boundary_gate_covers_all_claim_bearing_receipts():
    profile = {"deep_depths": (128, 512)}
    record = {
        "behavior": {
            "deep": {
                "d4": {
                    "128": {"boundary": 1, "total": 100},
                    "512": {"boundary": 2, "total": 100},
                }
            },
            "diamonds": {"boundary": 3, "decision_total": 200},
            "loops": {"boundary": 1, "decision_total": 50},
        },
        "null_perturbation": {"native_boundary": 5, "total": 100},
    }
    records = {"11": {"learned_intertwiner": record}}
    observed = runner._native_boundary_observables(
        records, (11,), "learned_intertwiner", profile
    )
    assert observed["maximum"] == pytest.approx(0.05)
    assert set(observed["per_seed_receipt_rates"]["11"]) == {
        "deep_128",
        "deep_512",
        "diamonds",
        "loops",
        "null_perturbation",
    }
    record["behavior"]["loops"]["decision_total"] = 0
    assert runner._native_boundary_observables(
        records, (11,), "learned_intertwiner", profile
    )["maximum"] is None


def test_pilot_comparisons_are_paired_by_seed_and_report_signed_gaps():
    records = {}
    for offset, seed in enumerate((1, 2, 3, 4, 5)):
        learned_depth = 0.85 + 0.01 * offset
        learned_loop = 0.90 + 0.01 * offset

        def arm_record(
            semantic: float,
            leakage: float,
            depth: float,
            loop: float,
        ) -> dict:
            return {
                "geometry": {
                    "relations": {"semantic_defect": {"median": semantic}},
                    "structure": {"generator_leakage": {"median": leakage}},
                },
                "behavior": {
                    "deep": {"d4": {"512": {"robust_accuracy": depth}}},
                    "loops": {"joint_robust_rate": loop},
                },
            }

        records[str(seed)] = {
            "learned_intertwiner": arm_record(
                0.01, 0.02, learned_depth, learned_loop
            ),
            "polar_cr": arm_record(0.10, 0.20, 0.70, 0.80),
            "polar_exact": arm_record(
                0.005, 0.01, learned_depth + 0.04, learned_loop + 0.01
            ),
        }
    observed = runner._pilot_comparative_observables(
        records, (1, 2, 3, 4, 5)
    )
    assert observed["semantic_defect_reduction_per_seed"] == pytest.approx(
        [0.9] * 5
    )
    assert observed["generator_leakage_reduction_per_seed"] == pytest.approx(
        [0.9] * 5
    )
    assert observed["depth512_mean_margin_vs_polar_cr"] == pytest.approx(0.17)
    assert observed["depth512_positive_seed_count"] == 5
    assert observed["loop_mean_margin_vs_polar_cr"] == pytest.approx(0.12)
    assert observed["loop_positive_seed_count"] == 5
    assert observed["depth512_pooled_gap_vs_polar_exact"] == pytest.approx(0.04)
    assert observed["loop_pooled_gap_vs_polar_exact"] == pytest.approx(0.01)


def test_relative_reduction_fails_closed_for_zero_or_nonfinite_baseline():
    assert runner._relative_reduction(0.1, 0.2) == pytest.approx(0.5)
    assert runner._relative_reduction(0.0, 0.0) is None
    assert runner._relative_reduction(float("nan"), 1.0) is None


def test_run_complete_write_is_textually_last_filesystem_mutation():
    source = Path(runner.__file__).read_text(encoding="utf-8")
    marker = 'write_json(output_dir / "RUN_COMPLETE.json", complete)'
    assert source.count(marker) == 1
    suffix = source.split(marker, 1)[1]
    assert "write_json(" not in suffix
    assert ".write_text(" not in suffix
    assert "torch.save(" not in suffix
