from __future__ import annotations

import json
import copy
import hashlib
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import arithmetic_space_lab.workspace_experiment as workspace_experiment_module

from arithmetic_space_lab.workspace_experiment import (
    PACKAGE_ROOT,
    _build_claim_summary,
    _causal_stage_passes,
    _confirmation_statistics,
    _annotate_directional_digits,
    _intervention_metric,
    _prepare_run,
    _read_analysis_lock,
    _resolve_seeds,
    _write_discovery_lock,
    Components,
    run_workspace_experiment,
    validate_profile,
)


def minimal_profile() -> dict:
    return {
        "schema_version": "4.0",
        "experiment": {"name": "unit_workspace", "study_phase": "engineering"},
        "model": {
            "vocab_size": 260,
            "d_model": 32,
            "n_layers": 2,
            "n_heads": 4,
            "max_seq_len": 24,
        },
        "data": {"min_digits": 1, "max_digits": 2, "operations": ["add", "sub"]},
        "arms": [
            {"name": "correct", "target_rule": "exact_arithmetic", "enabled": True},
            {"name": "no_carry", "target_rule": "no_transfer_subset_exact", "enabled": True},
            {"name": "pseudo_fst", "target_rule": "seeded_finite_state_transducer", "enabled": True},
            {"name": "deranged", "target_rule": "seeded_random_value_derangement", "enabled": True},
        ],
        "training": {"max_steps": 2, "progress_every_steps": 100},
        "evaluation": {"panels": {"iid": {"split": "iid", "count": 4}}},
        "competence_gates": {"probe_requires": {"iid_exact": 0.9}},
        "space": {"rank": 2, "layers": [1]},
        "causal": {
            "controls": ["candidate", "pca", "random", "complement"],
            "pairs": 2,
            "minimum_pairs": 1,
        },
        "seeds": {"development": [11], "confirmatory": [101, 103, 107], "minimum_confirmatory": 3},
        "claim_policy": {"allow_jspace_claim": False},
    }


class WorkspaceProfileTests(unittest.TestCase):
    @staticmethod
    def valid_analysis_lock() -> dict:
        profile_path = PACKAGE_ROOT / "configs" / "carry_discovery.json"
        profile_sha256 = hashlib.sha256(profile_path.read_bytes()).hexdigest()
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        seeds = list(profile["seeds"]["exploration"])
        minimum_support = profile["seeds"]["minimum_lock_support"]
        selection = {
            "source_layer": 8,
            "upstream_layer": 6,
            "rank": 24,
            "selection_rule": "modal_seed_selection_then_mean_target_blind_score",
            "supporting_seed_count": minimum_support,
        }
        return {
            "schema_version": "arithmetic-workspace-analysis-lock-v1",
            "source_profile": "carry_discovery",
            "source_profile_configuration_sha256": profile_sha256,
            "selection": selection,
            "per_seed_target_blind_selections": [
                {
                    "seed": seed,
                    "source_layer": 8 if index < minimum_support else 10,
                    "upstream_layer": 6 if index < minimum_support else 8,
                    "rank": 24 if index < minimum_support else 32,
                    "heldout_causal_prediction_fraction": 0.85,
                }
                for index, seed in enumerate(seeds)
            ],
            "locked_claim_policy": {"allow_jspace_claim": False},
            "immutable_after_confirmation_begins": True,
        }

    def test_analysis_lock_is_bound_to_bundled_discovery_protocol(self) -> None:
        valid = self.valid_analysis_lock()
        mutations = {
            "schema": lambda value: value.update({"schema_version": "made-up"}),
            "source": lambda value: value.update({"source_profile": "other"}),
            "stale_profile": lambda value: value.update(
                {"source_profile_configuration_sha256": "0" * 64}
            ),
            "selection_rule": lambda value: value["selection"].update(
                {"selection_rule": "choose_prettiest_plot"}
            ),
            "support": lambda value: value["selection"].update(
                {"supporting_seed_count": 1}
            ),
            "seed_identity": lambda value: value[
                "per_seed_target_blind_selections"
            ][0].update({"seed": 999999}),
            "out_of_sweep_layer": lambda value: (
                value["selection"].update(
                    {"source_layer": 7, "upstream_layer": 5}
                ),
                [
                    row.update({"source_layer": 7, "upstream_layer": 5})
                    for row in value["per_seed_target_blind_selections"]
                ],
            ),
            "out_of_sweep_rank": lambda value: (
                value["selection"].update({"rank": 7}),
                [
                    row.update({"rank": 7})
                    for row in value["per_seed_target_blind_selections"]
                ],
            ),
            "invalid_selection_score": lambda value: value[
                "per_seed_target_blind_selections"
            ][0].update({"heldout_causal_prediction_fraction": 1.5}),
            "claim_enabled": lambda value: value["locked_claim_policy"].update(
                {"allow_jspace_claim": True}
            ),
            "mutable": lambda value: value.update(
                {"immutable_after_confirmation_begins": False}
            ),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            valid_path = root / "valid.json"
            valid_path.write_text(json.dumps(valid), encoding="utf-8")
            loaded, digest = _read_analysis_lock(valid_path)
            self.assertEqual(loaded["selection"], valid["selection"])
            self.assertEqual(digest, hashlib.sha256(valid_path.read_bytes()).hexdigest())
            for name, mutate in mutations.items():
                with self.subTest(name=name):
                    invalid = copy.deepcopy(valid)
                    mutate(invalid)
                    invalid_path = root / f"invalid_{name}.json"
                    invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        _read_analysis_lock(invalid_path)

    def test_discovery_lock_uses_registered_two_of_three_modal_support(self) -> None:
        profile_path = PACKAGE_ROOT / "configs" / "carry_discovery.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        seeds = profile["seeds"]["exploration"]
        self.assertEqual(profile["seeds"]["minimum_lock_support"], 2)

        def result(source_layer: int, upstream_layer: int, rank: int) -> dict:
            return {
                "geometry": {
                    "correct": {
                        "candidate": {
                            "gate_pass": True,
                            "source_layer": source_layer,
                            "upstream_layer": upstream_layer,
                            "rank": rank,
                        },
                        "target_blind_layer_selection_score": 0.8,
                    }
                }
            }

        seed_results = {
            str(seeds[0]): result(8, 6, 24),
            str(seeds[1]): result(8, 6, 24),
            str(seeds[2]): result(10, 8, 32),
        }
        resolved = {
            "profile": "carry_discovery",
            "profile_configuration_sha256": hashlib.sha256(
                profile_path.read_bytes()
            ).hexdigest(),
            "claim_policy": {"allow_jspace_claim": False},
        }
        with tempfile.TemporaryDirectory() as temporary:
            telemetry: dict = {}
            lock = _write_discovery_lock(
                output=Path(temporary),
                resolved=resolved,
                seed_results=seed_results,
                telemetry=telemetry,
            )
            self.assertIsNotNone(lock)
            self.assertEqual(lock["selection"]["supporting_seed_count"], 2)
            self.assertEqual(len(lock["per_seed_target_blind_selections"]), 3)
            self.assertTrue(telemetry["written"])
            self.assertEqual(
                telemetry["reason"],
                "modal_selection_met_registered_minimum_support",
            )
            self.assertTrue(Path(telemetry["path"]).is_file())
            _read_analysis_lock(telemetry["path"])

            no_mode = {
                str(seeds[0]): result(4, 2, 8),
                str(seeds[1]): result(8, 6, 24),
                str(seeds[2]): result(10, 8, 32),
            }
            failed_telemetry: dict = {}
            missing = _write_discovery_lock(
                output=Path(temporary),
                resolved=resolved,
                seed_results=no_mode,
                telemetry=failed_telemetry,
            )
            self.assertIsNone(missing)
            self.assertFalse(failed_telemetry["written"])
            self.assertEqual(
                failed_telemetry["reason"],
                "modal_selection_support_below_minimum:1<2",
            )

    def test_profile_requires_all_four_controls(self) -> None:
        profile = minimal_profile()
        profile["arms"] = profile["arms"][:-1]
        with self.assertRaisesRegex(ValueError, "mandatory enabled arms"):
            validate_profile(profile, "bad")

    def test_progress_is_fixed_at_one_hundred(self) -> None:
        profile = minimal_profile()
        profile["training"]["progress_every_steps"] = 250
        with self.assertRaisesRegex(ValueError, "must be 100"):
            validate_profile(profile, "bad")

    def test_seed_override_does_not_invent_confirmatory_status(self) -> None:
        seeds, confirmatory, required = _resolve_seeds(
            minimal_profile()["seeds"], 999
        )
        self.assertEqual(seeds, [999])
        self.assertEqual(confirmatory, set())
        self.assertEqual(required, 3)

    def test_dry_run_materializes_a_complete_result_skeleton(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile_path = root / "profile.json"
            profile_path.write_text(json.dumps(minimal_profile()), encoding="utf-8")
            output = root / "result"
            summary = run_workspace_experiment(
                "unit",
                output,
                seed=11,
                device_name="cpu",
                dry_run=True,
                profile_path=profile_path,
            )
            self.assertEqual(summary["status"], "DRY_RUN")
            self.assertEqual(summary["JSPACE_CLAIM"], "NOT_ESTABLISHED")
            for directory in ("training", "behavior", "geometry", "causal"):
                self.assertTrue((output / directory).is_dir())
            for filename in (
                "resolved_experiment.json",
                "runtime.json",
                "progress.jsonl",
                "experiment_summary.json",
            ):
                self.assertTrue((output / filename).is_file())

    def test_prepare_run_allows_only_known_manifest_hotfix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "package"
            package.mkdir()
            manifest = package / "PACKAGE_MANIFEST.sha256"
            manifest.write_text("hotfix manifest\n", encoding="utf-8")
            target_manifest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            output = root / "result"
            original = {
                "profile": "carry_discovery",
                "training": {"max_steps": 60000},
                "package_manifest_sha256": (
                    workspace_experiment_module.LEGACY_EVENT_SAMPLER_MANIFEST_SHA256
                ),
            }
            current = copy.deepcopy(original)
            current["package_manifest_sha256"] = target_manifest
            with patch.object(workspace_experiment_module, "PACKAGE_ROOT", package):
                _prepare_run(output, original)
                _prepare_run(output, current)
                _prepare_run(output, current)
            provenance = json.loads(
                (output / workspace_experiment_module.HOTFIX_MIGRATION_FILE).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                provenance["source_package_manifest_sha256"],
                workspace_experiment_module.LEGACY_EVENT_SAMPLER_MANIFEST_SHA256,
            )
            self.assertEqual(
                provenance["target_package_manifest_sha256"], target_manifest
            )
            self.assertTrue(provenance["existing_training_state_preserved"])
            self.assertEqual(
                json.loads(
                    (output / "resolved_experiment.json").read_text(encoding="utf-8")
                ),
                original,
            )

    def test_prepare_run_rejects_manifest_hotfix_with_other_config_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "package"
            package.mkdir()
            manifest = package / "PACKAGE_MANIFEST.sha256"
            manifest.write_text("hotfix manifest\n", encoding="utf-8")
            target_manifest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            output = root / "result"
            original = {
                "profile": "carry_discovery",
                "training": {"max_steps": 60000},
                "package_manifest_sha256": (
                    workspace_experiment_module.LEGACY_EVENT_SAMPLER_MANIFEST_SHA256
                ),
            }
            changed = copy.deepcopy(original)
            changed["training"]["max_steps"] = 60001
            changed["package_manifest_sha256"] = target_manifest
            with patch.object(workspace_experiment_module, "PACKAGE_ROOT", package):
                _prepare_run(output, original)
                with self.assertRaisesRegex(ValueError, "configuration differs"):
                    _prepare_run(output, changed)

    def test_prepare_run_rejects_unknown_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "package"
            package.mkdir()
            manifest = package / "PACKAGE_MANIFEST.sha256"
            manifest.write_text("hotfix manifest\n", encoding="utf-8")
            target_manifest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            output = root / "result"
            original = {
                "profile": "carry_discovery",
                "training": {"max_steps": 60000},
                "package_manifest_sha256": "0" * 64,
            }
            current = copy.deepcopy(original)
            current["package_manifest_sha256"] = target_manifest
            with patch.object(workspace_experiment_module, "PACKAGE_ROOT", package):
                _prepare_run(output, original)
                with self.assertRaisesRegex(ValueError, "configuration differs"):
                    _prepare_run(output, current)

    def test_mocked_full_pipeline_enforces_stages_and_writes_reports(self) -> None:
        @dataclass
        class Example:
            pair_id: str
            prompt: str
            completion: str
            answer: str
            operation: str = "add"

        @dataclass
        class Pair:
            pair_id: str
            clean: Example
            corrupt: Example
            event_type: str = "carry"
            event_column: int = 0
            expected_affected_digits: tuple[int, ...] = (0, 1)
            expected_unaffected_digits: tuple[int, ...] = ()

            def to_dict(self) -> dict:
                return {
                    "pair_id": self.pair_id,
                    "event_type": self.event_type,
                    "event_column": self.event_column,
                    "expected_affected_digits": list(self.expected_affected_digits),
                    "expected_unaffected_digits": [],
                }

        class Provider:
            def __init__(self, *_args, **_kwargs):
                pass

            def audit_control(self, arm, _split, count):
                return {"valid": True, "arm": arm, "rows": count}

            def fixed_eval(self, arm, split, count, stage=None):
                del stage
                target = "7" if arm != "deranged" else "4"
                return [
                    Example(f"{split}-{index}", "3+4=", target, "7")
                    for index in range(count)
                ]

            def counterfactual_pairs(self, arm, split, count):
                del split
                target_a = "10" if arm == "correct" else "21"
                target_b = "11" if arm == "correct" else "22"
                return [
                    Pair(
                        f"pair-{index}",
                        Example(f"c-{index}", "5+5=", target_a, "10"),
                        Example(f"k-{index}", "5+6=", target_b, "11"),
                    )
                    for index in range(count)
                ]

        class SpaceConfig:
            def __init__(self, **values):
                self.values = values

        class Space:
            rank = 2

            def save(self, path):
                Path(path).write_bytes(b"space")

            def summary(self):
                return {
                    "rank": 2,
                    "source_layer": 1,
                    "upstream_layer": 0,
                    "metadata": {
                        "selected_rank": 2,
                        "prediction_fraction_threshold": 0.8,
                        "rank_selection": [
                            {
                                "rank": 2,
                                "heldout_causal_prediction_fraction": 0.9,
                            }
                        ],
                    },
                }

        def train_arm(*, config, arm, seed, output_dir, **_kwargs):
            path = Path(output_dir) / "checkpoints" / "model_step_000002.pt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"checkpoint")
            return {
                "initial_model_hash": f"initial-{seed}",
                "final_model_hash": f"final-{seed}-{arm}",
                "optimizer_steps": config["training"]["max_steps"],
                "input_stream_probe_hash": f"stream-{seed}",
                "final_checkpoint": str(path),
            }

        def evaluate(**kwargs):
            arm_target = kwargs["examples"][0].completion
            return {
                "answer_exact_match": 1.0,
                "arithmetic_oracle_exact_match": 0.0 if arm_target == "4" else 1.0,
                "malformed_rate": 0.0,
                "by_structure": {"carry": {"answer_exact_match": 1.0}},
            }

        def competence(evaluations, gates, gate_name="probe_requires"):
            del evaluations, gates
            return {"status": "PASS", "ready": True, "gate_name": gate_name}

        def causal(**_kwargs):
            section = {
                "ablation": {"baseline_correct_lost": 0.5},
                "clean_to_corrupt_patch": {
                    "baseline_error_rescued": 0.5,
                    "directional_items": [],
                },
                "coordinate_rescue": {"upstream_corruption_error_rescued": 0.5},
            }
            return {
                "claim_gate_flags": {
                    "independent_upstream_residual_rescue_assay": True,
                    "mediation_claim_eligible": False,
                },
                "spaces": {
                    "candidate": section,
                    "pca": {
                        "ablation": {"baseline_correct_lost": 0.0},
                        "clean_to_corrupt_patch": {"baseline_error_rescued": 0.0},
                        "coordinate_rescue": {"upstream_corruption_error_rescued": 0.0},
                    },
                    "random": {
                        "ablation": {"baseline_correct_lost": 0.0},
                        "clean_to_corrupt_patch": {"baseline_error_rescued": 0.0},
                        "coordinate_rescue": {"upstream_corruption_error_rescued": 0.0},
                    },
                    "complement": {
                        "ablation": {"baseline_correct_lost": 0.0},
                        "clean_to_corrupt_patch": {"baseline_error_rescued": 0.0},
                        "coordinate_rescue": {"upstream_corruption_error_rescued": 0.0},
                    },
                },
            }

        components = Components(
            provider_factory=Provider,
            train_arm=train_arm,
            evaluate_free_generation=evaluate,
            competence_report=competence,
            load_research_checkpoint=lambda checkpoint, device: (object(), {"step": 2}),
            balanced_config_type=SpaceConfig,
            discover_balanced_space=lambda **_kwargs: Space(),
            run_causal_assay=causal,
            resolve_device=lambda name: name,
            runtime_information=lambda device: {"device": device, "torch": "fake"},
        )
        profile = minimal_profile()
        profile["space"].update({"fit_items": 2, "holdout_items": 2})
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile_path = root / "profile.json"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            result = run_workspace_experiment(
                "unit",
                root / "result",
                seed=11,
                device_name="cpu",
                profile_path=profile_path,
                components=components,
            )
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["JSPACE_CLAIM"], "NOT_ESTABLISHED")
            seed = result["seed_results"]["11"]
            self.assertIn("correct", seed["geometry"])
            self.assertIn("pseudo_fst", seed["causal"])
            self.assertTrue(seed["paired_initialization"])


class ClaimLadderTests(unittest.TestCase):
    @staticmethod
    def passing_seed() -> dict:
        return {
            "behavior": {
                "correct": {
                    "competence": {"ready": True},
                    "claim_competence": {"ready": True},
                }
            },
            "geometry": {
                "candidate": {
                    "rank": 4,
                    "metadata": {
                        "selected_rank": 4,
                        "prediction_fraction_threshold": 0.8,
                        "rank_selection": [
                            {
                                "rank": 4,
                                "heldout_causal_prediction_fraction": 0.9,
                            }
                        ],
                    },
                }
            },
            "causal": {
                "pairing_claim_eligible": True,
                "claim_gate_flags": {
                    "independent_upstream_residual_rescue_assay": True,
                    "mediation_claim_eligible": True,
                },
                "claim_gates": {
                    "necessity": True,
                    "patch_and_rescue": True,
                    "mediation": True,
                    "shared_access": True,
                    "math_specificity": True,
                },
            },
        }

    def test_all_gates_and_replication_are_both_required(self) -> None:
        results = {str(seed): self.passing_seed() for seed in (101, 103, 107)}
        insufficient = _build_claim_summary(
            {key: value for key, value in list(results.items())[:2]},
            {101, 103, 107},
            3,
            {"allow_jspace_claim": True},
        )
        self.assertEqual(insufficient["status"], "NOT_ESTABLISHED")
        sufficient = _build_claim_summary(
            results,
            {101, 103, 107},
            3,
            {"allow_jspace_claim": True},
        )
        self.assertEqual(sufficient["status"], "ESTABLISHED")

    def test_profile_can_forbid_a_claim_even_if_all_assays_pass(self) -> None:
        results = {str(seed): self.passing_seed() for seed in (101, 103, 107)}
        report = _build_claim_summary(
            results,
            {101, 103, 107},
            3,
            {"allow_jspace_claim": False},
        )
        self.assertEqual(report["status"], "NOT_ESTABLISHED")

    def test_coordinate_rescue_cannot_substitute_for_independent_rescue(self) -> None:
        seed = self.passing_seed()
        seed["causal"]["claim_gate_flags"] = {
            "independent_upstream_residual_rescue_assay": False,
            "mediation_claim_eligible": True,
        }
        report = _build_claim_summary(
            {"101": seed}, {101}, 1, {"allow_jspace_claim": True}
        )
        stage = report["per_seed"]["101"]["stages"]["patch_and_rescue"]
        self.assertNotEqual(stage["status"], "PASS")
        self.assertEqual(report["status"], "NOT_ESTABLISHED")

    def test_causal_claim_metrics_prefer_baseline_qualified_estimands(self) -> None:
        patch = {
            "clean_to_corrupt_patch": {
                "exact": 1.0,
                "baseline_error_rescued": 1.0,
                "primary_estimand": {
                    "claim_eligible": False,
                    "qualified_denominator_count": 0,
                    "qualified_clean_conversion_rate": None,
                },
            }
        }
        self.assertIsNone(_intervention_metric(patch, "patch"))
        patch["clean_to_corrupt_patch"]["primary_estimand"] = {
            "claim_eligible": True,
            "qualified_denominator_count": 8,
            "registered_minimum_qualified_pairs": 4,
            "qualified_clean_conversion_rate": 0.25,
        }
        self.assertEqual(_intervention_metric(patch, "patch"), 0.25)
        patch["clean_to_corrupt_patch"]["primary_estimand"].update(
            {
                "qualified_denominator_count": 1,
                "registered_minimum_qualified_pairs": 4,
            }
        )
        self.assertIsNone(_intervention_metric(patch, "patch"))

    def test_unqualified_patch_denominator_fails_causal_stage(self) -> None:
        def section(rate: float, *, eligible: bool) -> dict:
            return {
                "ablation": {
                    "primary_estimand": {
                        "claim_eligible": True,
                        "qualified_denominator_count": 8,
                        "registered_minimum_qualified_pairs": 4,
                        "qualified_loss_rate": rate,
                    }
                },
                "clean_to_corrupt_patch": {
                    "exact": 1.0,
                    "primary_estimand": {
                        "claim_eligible": eligible,
                        "qualified_denominator_count": 8 if eligible else 0,
                        "registered_minimum_qualified_pairs": 4,
                        "qualified_clean_conversion_rate": rate if eligible else None,
                    },
                },
                "coordinate_rescue": {
                    "upstream_corruption_error_rescued": 1.0,
                    "primary_estimand": {
                        "claim_eligible": True,
                        "qualified_denominator_count": 8,
                        "registered_minimum_qualified_pairs": 4,
                        "qualified_rescue_rate": rate,
                    },
                },
            }

        report = {
            "pairing_claim_eligible": True,
            "claim_gate_flags": {
                "independent_upstream_residual_rescue_assay": True,
                "mediation_claim_eligible": False,
            },
            "spaces": {
                "candidate": section(0.8, eligible=False),
                "pca": section(0.1, eligible=True),
                "random": section(0.1, eligible=True),
                "complement": section(0.1, eligible=True),
            },
        }
        stages = _causal_stage_passes(
            report,
            {
                "control_margin_min": 0.05,
                "ablation_drop_min": 0.10,
                "patch_flip_min": 0.20,
                "rescue_rate_min": 0.20,
            },
        )
        self.assertTrue(stages["necessity"])
        self.assertFalse(stages["patch_and_rescue"])

    def test_significant_tiny_effects_fail_registered_minimum(self) -> None:
        def space(ablation_exact: float, effect: float, directional: bool) -> dict:
            return {
                "ablation": {"exact": ablation_exact},
                "clean_to_corrupt_patch": {
                    "baseline_error_rescued": effect,
                    "directional_items": [
                        {
                            "affected_digits_match_clean_donor": directional,
                            "unaffected_digits_preserve_recipient": directional,
                        }
                    ],
                },
                "coordinate_rescue": {
                    "upstream_corruption_error_rescued": effect
                },
            }

        seed_results = {}
        seeds = {101, 103, 107, 109, 113, 127, 131, 137}
        for seed in seeds:
            causal = {
                "baseline": {"clean": {"exact": 1.0}},
                "counterfactual_pair_metadata": [
                    {
                        "pair_id": f"pair-{seed}",
                        "clean": {"family_id": f"family-{seed}"},
                    }
                ],
                "spaces": {
                    # Every registered contrast is +0.01: perfectly consistent
                    # across seeds and therefore significant, but far below 0.10.
                    "candidate": space(0.89, 0.11, True),
                    "pca": space(0.90, 0.10, False),
                    "random": space(0.90, 0.10, False),
                    "complement": space(0.90, 0.10, False),
                },
            }
            seed_results[str(seed)] = {"causal": {"correct": causal}}
        report = _confirmation_statistics(
            seed_results,
            seeds,
            {
                "minimum_passing_seeds": 7,
                "familywise_alpha": 0.05,
                "confidence_level": 0.95,
                "bootstrap_samples": 100,
            },
            {"minimum_candidate_minus_random": 0.10},
        )
        self.assertTrue(report["holm_pass"])
        self.assertTrue(report["bootstrap_lower_above_zero"])
        self.assertFalse(report["registered_minimum_effect_pass"])
        self.assertFalse(report["passed"])
        self.assertEqual(report["status"], "FAIL")

    def test_directional_digit_audit_rejects_invalid_output_shape(self) -> None:
        metadata = [
            {
                "pair_id": "pair-1",
                "event_type": "carry",
                "event_column": 1,
                "expected_affected_digits": [1],
                "expected_unaffected_digits": [0, 2],
            }
        ]

        for output, well_formed in (
            ("123", False),  # matching digits but no valid EOS-terminated record
            ("-123", True),  # wrong sign
            ("9123", True),  # extra leading digit
        ):
            with self.subTest(output=output, well_formed=well_formed):
                item = {
                    "output": output,
                    "output_well_formed": well_formed,
                    "clean_expected": "123",
                    "corrupt_expected": "103",
                    "baseline_qualified": True,
                }
                report = {
                    "spaces": {
                        "candidate": {
                            "clean_to_corrupt_patch": {
                                "directional_items": [item]
                            }
                        }
                    }
                }
                _annotate_directional_digits(report, metadata)
                self.assertFalse(item["directional_output_valid"])
                self.assertFalse(item["affected_digits_match_clean_donor"])
                self.assertFalse(item["unaffected_digits_preserve_recipient"])
                self.assertEqual(
                    report["spaces"]["candidate"]["clean_to_corrupt_patch"][
                        "directional_digit_audit"
                    ]["joint_predicted_direction_count"],
                    0,
                )

        valid_item = {
            "output": "123",
            "output_well_formed": True,
            "clean_expected": "123",
            "corrupt_expected": "103",
            "baseline_qualified": True,
        }
        valid_report = {
            "spaces": {
                "candidate": {
                    "clean_to_corrupt_patch": {"directional_items": [valid_item]}
                }
            }
        }
        _annotate_directional_digits(valid_report, metadata)
        self.assertTrue(valid_item["directional_output_valid"])
        self.assertTrue(valid_item["affected_digits_match_clean_donor"])
        self.assertTrue(valid_item["unaffected_digits_preserve_recipient"])


if __name__ == "__main__":
    unittest.main()
