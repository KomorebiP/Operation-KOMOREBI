from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import random
import tempfile
from types import SimpleNamespace
import unittest

from neuralese_g1.config import load_config, validate_config
from neuralese_g1.gates import adjudicate
from neuralese_g1.integrity import (
    acquire_run_lock,
    atomic_json,
    release_run_lock,
    sha256_file,
)
from neuralese_g1.results import verify_run_directory
from neuralese_g1.tasks import (
    ANSWER_CUE,
    QUERY_TYPES,
    find_query_derangement,
    find_state_derangement,
    make_split,
    split_digest,
)
from neuralese_g1.token_contract import validate_single_token_targets


ROOT = Path(__file__).resolve().parents[1]


class _BoundaryTokenizer:
    all_special_ids = [99]

    def __init__(self, *, merge_boundary: bool = False) -> None:
        self.merge_boundary = merge_boundary

    def encode(self, text, *, add_special_tokens):
        if text == "0" and not add_special_tokens:
            return [10]
        if text == "Use state. Answer:\n" and add_special_tokens:
            return [1, 2, 3]
        if text == "Use state. Answer:\n0" and add_special_tokens:
            return [1, 2, 30] if self.merge_boundary else [1, 2, 3, 10]
        raise AssertionError(f"unexpected tokenizer input: {text!r}")

    def decode(self, identifiers, **_kwargs):
        return "0" if list(identifiers) == [10] else ""


def _examples(config: dict, split: str):
    task = config["task"]
    if split == "train":
        count = task["train_base_problems"]
        lower, upper = task["train_chain_min"], task["train_chain_max"]
    elif split == "validation":
        count = task["validation_base_problems"]
        lower, upper = task["train_chain_min"], task["train_chain_max"]
    elif split == "test_iid":
        count = task["test_base_problems"]
        lower, upper = task["train_chain_min"], task["train_chain_max"]
    else:
        count = task["ood_base_problems"]
        lower, upper = task["ood_chain_min"], task["ood_chain_max"]
    return make_split(
        seed=config["seed"],
        split=split,
        base_problems=count,
        states=task["states"],
        chain_min=lower,
        chain_max=upper,
    )


def _engineering(value: bool = True) -> dict[str, bool]:
    return {
        key: value
        for key in (
            "local_model_loaded",
            "single_token_targets",
            "answer_token_boundary",
            "backbone_frozen",
            "optimizer_excludes_backbone",
            "finite_loss",
            "nonzero_finite_gradient",
            "nonzero_finite_parameter_delta",
            "nonzero_finite_state",
            "artifacts_complete",
        )
    } | {"canonical_scientific_profile": True}


def _evaluation(accuracy: float = 0.9, control: float = 0.2) -> dict:
    recurrent = {
        "accuracy": accuracy,
        "accuracy_by_query": {query: accuracy for query in QUERY_TYPES},
        "majority_baseline_by_query": {
            "direct": 1.0 / 6.0,
            "parity": 0.5,
            "codebook": 1.0 / 6.0,
        },
    }
    return {
        "iid": {
            "recurrent": recurrent,
            "zero": {"accuracy": control},
            "shuffle": {"accuracy": control},
            "no_feedback": {"accuracy": control},
        },
        "ood": {
            "recurrent": {"accuracy": accuracy},
            "zero": {"accuracy": control},
            "shuffle": {"accuracy": control},
            "no_feedback": {"accuracy": control},
        },
    }


class ConfigTests(unittest.TestCase):
    def test_registered_profiles_validate(self) -> None:
        for profile in ("wiring", "smoke", "pilot"):
            with self.subTest(profile=profile):
                config = load_config(ROOT / "configs" / f"{profile}.json")
                self.assertEqual(config["profile"], profile)
                self.assertEqual(len(config["config_digest"]), 64)

    def test_fail_closed_mutations(self) -> None:
        base = load_config(ROOT / "configs" / "pilot.json")
        base.pop("config_digest")
        mutations = []
        value = copy.deepcopy(base)
        value["unexpected"] = True
        mutations.append(value)
        value = copy.deepcopy(base)
        value["model"]["source_layer"] = True
        mutations.append(value)
        value = copy.deepcopy(base)
        value["workspace"]["injection_scale"] = 0.0
        mutations.append(value)
        value = copy.deepcopy(base)
        value["replication_seeds"] = [1, 1, 2]
        mutations.append(value)
        value = copy.deepcopy(base)
        value["model"]["strict_backbone_hash"] = False
        mutations.append(value)
        value = copy.deepcopy(base)
        value["training"]["loss_scale_initial"] = 0.0
        mutations.append(value)
        value = copy.deepcopy(base)
        value["training"]["max_overflow_retries"] = 0
        mutations.append(value)
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_config(mutation)

    def test_only_registered_pilot_seed_overrides(self) -> None:
        profile = ROOT / "configs" / "pilot.json"
        self.assertEqual(load_config(profile, {"seed": 711002})["seed"], 711002)
        with self.assertRaises(ValueError):
            load_config(profile, {"seed": 999999})


class TokenContractTests(unittest.TestCase):
    def test_accepts_stable_bare_continuation(self) -> None:
        example = SimpleNamespace(
            example_id="contract-pass",
            query_prompt="Use state. Answer:\n",
            target_text="0",
        )
        self.assertEqual(
            validate_single_token_targets(_BoundaryTokenizer(), [example]), {"0": 10}
        )

    def test_rejects_boundary_merge(self) -> None:
        example = SimpleNamespace(
            example_id="contract-merge",
            query_prompt="Use state. Answer:\n",
            target_text="0",
        )
        with self.assertRaises(ValueError):
            validate_single_token_targets(
                _BoundaryTokenizer(merge_boundary=True), [example]
            )

    def test_rejects_leading_whitespace_regression(self) -> None:
        example = SimpleNamespace(
            example_id="contract-space",
            query_prompt="Use state. Answer:\n",
            target_text=" 0",
        )
        with self.assertRaises(ValueError):
            validate_single_token_targets(_BoundaryTokenizer(), [example])


class TaskTests(unittest.TestCase):
    def test_answer_labels_are_bare_and_separator_is_in_prompt(self) -> None:
        config = load_config(ROOT / "configs" / "wiring.json")
        rows = _examples(config, "train")
        self.assertTrue(rows)
        self.assertTrue(all(row.query_prompt.endswith(ANSWER_CUE) for row in rows))
        self.assertTrue(
            all(row.target_text and row.target_text == row.target_text.strip() for row in rows)
        )

    def test_splits_are_unique_balanced_and_disjoint(self) -> None:
        profiles_and_seeds = []
        for profile in ("wiring", "smoke", "pilot"):
            base = load_config(ROOT / "configs" / f"{profile}.json")
            seeds = base.get("replication_seeds", [base["seed"]])
            profiles_and_seeds.extend((profile, seed) for seed in seeds)
        for profile, seed in profiles_and_seeds:
            with self.subTest(profile=profile, seed=seed):
                config = load_config(
                    ROOT / "configs" / f"{profile}.json", {"seed": seed}
                )
                prompts: dict[str, set[str]] = {}
                for split in ("train", "validation", "test_iid", "test_ood_depth"):
                    rows = _examples(config, split)
                    split_prompts = {row.compute_prompt for row in rows}
                    prompts[split] = split_prompts
                    self.assertEqual(len(rows), 3 * len(split_prompts))
                    counts = {
                        state: sum(
                            row.query_type == "direct" and row.final_state == state
                            for row in rows
                        )
                        for state in range(config["task"]["states"])
                    }
                    self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)
                names = tuple(prompts)
                for left_index, left in enumerate(names):
                    for right in names[left_index + 1 :]:
                        self.assertFalse(prompts[left] & prompts[right])

    def test_registered_query_derangements_are_answer_incompatible(self) -> None:
        for profile in ("wiring", "smoke", "pilot"):
            config = load_config(ROOT / "configs" / f"{profile}.json")
            for split in ("test_iid", "test_ood_depth"):
                rows = _examples(config, split)
                for query in QUERY_TYPES:
                    family = [row for row in rows if row.query_type == query]
                    values = [
                        row.final_state % 2 if query == "parity" else row.final_state
                        for row in family
                    ]
                    donors = find_state_derangement(values)
                    self.assertIsNotNone(donors)
                    assert donors is not None
                    self.assertEqual(sorted(donors), list(range(len(values))))
                    self.assertTrue(
                        all(values[index] != values[donor] for index, donor in enumerate(donors))
                    )


class GateTests(unittest.TestCase):
    def test_pilot_pass_requires_engineering_and_complete_queries(self) -> None:
        config = load_config(ROOT / "configs" / "pilot.json")
        passing = adjudicate(config, _engineering(), _evaluation())
        self.assertEqual(passing["claim"], "G1_SINGLE_SEED_PILOT_PASS")
        failed_engineering = _engineering()
        failed_engineering["artifacts_complete"] = False
        blocked = adjudicate(config, failed_engineering, _evaluation())
        self.assertEqual(blocked["claim"], "G1_NOT_ESTABLISHED")
        incomplete = _evaluation()
        del incomplete["iid"]["recurrent"]["accuracy_by_query"]["parity"]
        malformed = adjudicate(config, _engineering(), incomplete)
        self.assertFalse(malformed["scientific"]["passed"])
        nonfinite = _evaluation()
        nonfinite["iid"]["recurrent"]["accuracy"] = float("inf")
        rejected = adjudicate(config, _engineering(), nonfinite)
        self.assertFalse(rejected["scientific"]["passed"])

    def test_noncanonical_pilot_is_exploratory(self) -> None:
        config = load_config(ROOT / "configs" / "pilot.json")
        engineering = _engineering()
        engineering["canonical_scientific_profile"] = False
        result = adjudicate(config, engineering, _evaluation())
        self.assertEqual(result["claim"], "G1_ENGINEERING_PASS")


class ResultVerificationTests(unittest.TestCase):
    def test_cross_file_verification_and_tamper_detection(self) -> None:
        config = load_config(ROOT / "configs" / "wiring.json")
        engineering = _engineering()
        regenerated = {
            split: _examples(config, split)
            for split in ("train", "validation", "test_iid", "test_ood_depth")
        }
        random.Random(int(config["seed"]) + 91).shuffle(regenerated["train"])
        target_texts = sorted(
            {row.target_text for rows in regenerated.values() for row in rows}
        )
        target_token_map = {
            target_text: index + 10 for index, target_text in enumerate(target_texts)
        }
        prompt_sets = {
            key: {row.compute_prompt for row in rows} for key, rows in regenerated.items()
        }
        overlap_counts = {}
        split_names = tuple(prompt_sets)
        for left_index, left in enumerate(split_names):
            for right in split_names[left_index + 1 :]:
                overlap_counts[f"{left}__{right}"] = len(
                    prompt_sets[left] & prompt_sets[right]
                )
        evaluation: dict = {
            "schema": "komorebi.neuralese.g1.evaluation.v1",
            "validation_not_used_for_selection": True,
            "claim_ceiling": "G1_SMALL_MODEL_SINGLE_SEED",
        }
        prediction_records = []
        for split, evaluation_key in (
            ("test_iid", "iid"),
            ("test_ood_depth", "ood"),
        ):
            rows = regenerated[split]
            donors = find_query_derangement(rows)
            assert donors is not None
            split_summary = {}
            for mode in ("recurrent", "zero", "shuffle", "no_feedback"):
                mode_records = []
                for row in rows:
                    target = target_token_map[row.target_text]
                    correct = mode == "recurrent"
                    record = {
                        "split": split,
                        "mode": mode,
                        "example_id": row.example_id,
                        "query_type": row.query_type,
                        "applications": row.applications,
                        "final_state": row.final_state,
                        "predicted_token_id": target if correct else target + 1000,
                        "target_token_id": target,
                        "correct": correct,
                    }
                    if mode == "shuffle":
                        donor = rows[donors[len(mode_records)]]
                        record["donor_example_id"] = donor.example_id
                        record["donor_final_state"] = donor.final_state
                    mode_records.append(record)
                    prediction_records.append(record)
                by_query = {
                    query: sum(
                        bool(record["correct"])
                        for record in mode_records
                        if record["query_type"] == query
                    )
                    / sum(record["query_type"] == query for record in mode_records)
                    for query in QUERY_TYPES
                }
                majority = {}
                for query in QUERY_TYPES:
                    targets = [
                        record["target_token_id"]
                        for record in mode_records
                        if record["query_type"] == query
                    ]
                    majority[query] = max(targets.count(value) for value in set(targets)) / len(
                        targets
                    )
                split_summary[mode] = {
                    "count": len(mode_records),
                    "accuracy": sum(bool(record["correct"]) for record in mode_records)
                    / len(mode_records),
                    "accuracy_by_query": by_query,
                    "majority_baseline_by_query": majority,
                    "accuracy_by_applications": {},
                }
            split_summary["state_derangement"] = {
                "rows": len(rows),
                "bijection": True,
                "same_query_family": True,
                "fixed_state_matches": 0,
                "answer_compatible_matches": 0,
            }
            split_summary["trace"] = {}
            evaluation[evaluation_key] = split_summary
        gates = adjudicate(config, engineering, evaluation)
        model_files = [
            {"name": "config.json", "size": 1, "sha256": "a" * 64},
            {"name": "model.safetensors", "size": 1, "sha256": "b" * 64},
        ]
        model_digest = hashlib.sha256(
            json.dumps(model_files, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        registered_identity = {
            "model_type": config["model"]["expected_model_type"],
            "architecture": config["model"]["expected_architecture"],
            "hidden_size": config["model"]["expected_hidden_size"],
            "layers": config["model"]["expected_layers"],
        }
        answer_token_contract = {
            "schema": "komorebi.neuralese.g1.answer_token_contract.v1",
            "status": "PASS",
            "answer_cue": ANSWER_CUE,
            "target_count": len(target_token_map),
            "prompt_target_pair_count": len(
                {
                    (row.query_prompt, row.target_text)
                    for rows in regenerated.values()
                    for row in rows
                }
            ),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            atomic_json(root / "resolved_config.json", config)
            atomic_json(
                root / "preflight.json",
                {
                    "schema": "komorebi.neuralese.g1.preflight.v1",
                    "status": "PASS",
                    "profile": config["profile"],
                    "seed": config["seed"],
                    "config_digest": config["config_digest"],
                    "model": {
                        "path": "C:\\registered-model",
                        "files": model_files,
                        "metadata_sha256": model_digest,
                    },
                    "model_identity": registered_identity,
                    "expected_model_identity": registered_identity,
                    "compute_prompt_overlap_counts": overlap_counts,
                    "canonical_claim_eligible": True,
                    "package_manifest_sha256": sha256_file(ROOT / "PACKAGE_MANIFEST.json"),
                    "gradient_scaler_enabled": True,
                    "gradient_scaler_registered_initial_scale": 1024.0,
                    "gradient_scaler_start_scale": 1024.0,
                    "resumed": False,
                    "single_token_targets": target_token_map,
                    "answer_token_contract": answer_token_contract,
                    "split_counts": {
                        key: len(value) for key, value in regenerated.items()
                    },
                    "split_digests": {
                        key: split_digest(value) for key, value in regenerated.items()
                    },
                },
            )
            (root / "training.jsonl").write_text(
                "\n".join(
                    json.dumps(
                        {
                            "step": step,
                            "loss": 1.0,
                            "gradient_norm": 1.0,
                            "loss_scale": 1024.0,
                            "overflow_retries_before_step": 0,
                            "overflow_retries_total": 0,
                            "optimizer_attempts_total": step,
                        }
                    )
                    for step in (1, 2)
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "checkpoint.pt").write_bytes(b"checkpoint")
            atomic_json(root / "evaluation.json", evaluation)
            (root / "predictions.jsonl").write_text(
                "\n".join(json.dumps(record) for record in prediction_records) + "\n",
                encoding="utf-8",
            )
            atomic_json(root / "gates.json", gates)
            atomic_json(
                root / "run_summary.json",
                {
                    "schema": "komorebi.neuralese.g1.run_summary.v1",
                    "status": gates["claim"],
                    "profile": config["profile"],
                    "seed": config["seed"],
                    "gates": gates,
                    "training": {
                        "logged_records": 2,
                        "first_logged_loss": 1.0,
                        "last_logged_loss": 1.0,
                        "maximum_gradient_norm": 1.0,
                        "overflow_retries_total": 0,
                        "workspace_hash_before": "b" * 64,
                        "workspace_hash_after": "c" * 64,
                    },
                    "evaluation": {
                        "iid_recurrent_accuracy": evaluation["iid"]["recurrent"]["accuracy"],
                        "iid_zero_accuracy": evaluation["iid"]["zero"]["accuracy"],
                        "iid_shuffle_accuracy": evaluation["iid"]["shuffle"]["accuracy"],
                        "iid_no_feedback_accuracy": evaluation["iid"]["no_feedback"]["accuracy"],
                        "ood_recurrent_accuracy": evaluation["ood"]["recurrent"]["accuracy"],
                    },
                    "backbone_hash_before": None,
                    "backbone_hash_after": None,
                },
            )
            self.assertEqual(
                verify_run_directory(root, require_checkpoint_validation=False)["status"],
                "PASS",
            )
            evaluation["iid"]["recurrent"]["accuracy"] = 0.5
            atomic_json(root / "evaluation.json", evaluation)
            with self.assertRaises(RuntimeError):
                verify_run_directory(root, require_checkpoint_validation=False)

    def test_output_lock_is_exclusive_and_reusable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".g1.lock"
            first = acquire_run_lock(path)
            try:
                with self.assertRaises(RuntimeError):
                    acquire_run_lock(path)
            finally:
                release_run_lock(first)
            second = acquire_run_lock(path)
            release_run_lock(second)


if __name__ == "__main__":
    unittest.main()
