from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

from g1d.dynamic import (
    CHECKPOINT_KEYS,
    _parse_prompt,
    balanced_subset,
    classify_localization,
    donor_indices,
    run_probes,
    unique_problems,
)
from g1d.integrity import directory_hashes, verify_fixed_source_identity
from g1d.static_analysis import analyze_run_artifacts


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "input_run" / "pilot-711001"
VENDOR = ROOT / "vendor" / "g1_v0_1_1"


def upstream_run_verifier():
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))
    from neuralese_g1.results import verify_run_directory

    return verify_run_directory


class FixedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analysis = analyze_run_artifacts(RUN)

    def test_registered_metrics_reproduce(self) -> None:
        accuracy = self.analysis["accuracy"]["test_iid"]
        self.assertEqual(accuracy["recurrent"]["correct_count"], 401)
        self.assertEqual(accuracy["zero"]["correct_count"], 80)
        self.assertEqual(accuracy["shuffle"]["correct_count"], 401)
        self.assertEqual(accuracy["no_feedback"]["correct_count"], 400)
        self.assertAlmostEqual(
            self.analysis["iid_causal_deltas"]["recurrent_minus_shuffle"], 0.0
        )

    def test_prediction_collapse_reproduces(self) -> None:
        recurrent = self.analysis["prediction_distributions"]["test_iid"][
            "recurrent"
        ]
        self.assertEqual(recurrent["direct"]["counts"], {"3": 480})
        self.assertEqual(recurrent["parity"]["counts"], {"E": 480})
        self.assertEqual(recurrent["codebook"]["counts"]["C"], 365)

    def test_cross_mode_replay_targets_reproduce(self) -> None:
        agreement = self.analysis["cross_mode_prediction_agreement"]
        self.assertEqual(
            agreement["test_iid"]["recurrent__shuffle"]["same_count"], 1426
        )
        self.assertEqual(
            agreement["test_iid"]["recurrent__no_feedback"]["same_count"], 1430
        )
        self.assertEqual(
            agreement["test_ood_depth"]["recurrent__shuffle"]["same_count"],
            1432,
        )
        self.assertEqual(
            agreement["test_ood_depth"]["recurrent__no_feedback"]["same_count"],
            1433,
        )

    def test_generic_steering_signature_is_fixed(self) -> None:
        self.assertTrue(self.analysis["generic_steering_signature"])
        self.assertTrue(all(self.analysis["signatures"].values()))

    def test_checkpoint_and_checkpoint_schema_are_fixed(self) -> None:
        digest = hashlib.sha256((RUN / "checkpoint.pt").read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "ea0f9506334f6958c43e73596eb7404f785abd92be7668024b0c01efac1eae75",
        )
        self.assertEqual(len(CHECKPOINT_KEYS), 13)
        self.assertIn("workspace_state", CHECKPOINT_KEYS)
        self.assertIn("optimizer_state", CHECKPOINT_KEYS)

    def test_static_analysis_does_not_mutate_input(self) -> None:
        before = directory_hashes(RUN)
        analyze_run_artifacts(RUN)
        self.assertEqual(before, directory_hashes(RUN))

    def test_exact_upstream_run_verification_passes(self) -> None:
        before = directory_hashes(RUN)
        verification = upstream_run_verifier()(
            RUN, require_checkpoint_validation=False
        )
        self.assertEqual(verification["status"], "PASS")
        self.assertEqual(verification["profile"], "pilot")
        self.assertEqual(verification["seed"], 711001)
        self.assertEqual(verification["claim"], "G1_ENGINEERING_PASS")
        self.assertEqual(verification["training_records"], 101)
        self.assertEqual(verification["prediction_records"], 11520)
        self.assertEqual(
            verification["config_digest"],
            "872349b749392924dab4b70eefe516751667d8d74ed91f73bb325b8277ce2a41",
        )
        self.assertEqual(
            verification["package_manifest_sha256"],
            "fb3a29e2c799fc1139fc7378b6bdf92f8d0dafc775ba8250021662a4ba0632d7",
        )
        self.assertFalse(verification["checkpoint_validated"])
        self.assertEqual(before, directory_hashes(RUN))

    def test_exact_upstream_run_verification_rejects_cross_file_tamper(self) -> None:
        verify_run_directory = upstream_run_verifier()
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "pilot-711001"
            shutil.copytree(RUN, tampered)
            gates_path = tampered / "gates.json"
            gates = json.loads(gates_path.read_text(encoding="utf-8"))
            gates["claim"] = "G1_SCIENTIFIC_PASS"
            gates_path.write_text(
                json.dumps(gates, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "run summary and gate claim"):
                verify_run_directory(
                    tampered, require_checkpoint_validation=False
                )

    def test_fixed_source_contract_rejects_forged_identity(self) -> None:
        verification = upstream_run_verifier()(
            RUN, require_checkpoint_validation=False
        )
        fixed = verify_fixed_source_identity(RUN, verification)
        self.assertEqual(
            fixed["checkpoint_sha256"],
            "ea0f9506334f6958c43e73596eb7404f785abd92be7668024b0c01efac1eae75",
        )
        forged = dict(verification)
        forged["seed"] = 711002
        with self.assertRaisesRegex(RuntimeError, "fixed registered pilot"):
            verify_fixed_source_identity(RUN, forged)

    def test_fixed_source_contract_rejects_inventory_drift(self) -> None:
        verification = upstream_run_verifier()(
            RUN, require_checkpoint_validation=False
        )
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "pilot-711001"
            shutil.copytree(RUN, copied)
            (copied / "unexpected.txt").write_text("drift\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "seed-711001 identity"):
                verify_fixed_source_identity(copied, verification)


class DonorTests(unittest.TestCase):
    @staticmethod
    def examples(per_state: int = 3) -> list[SimpleNamespace]:
        values = []
        counter = 0
        for state in range(6):
            for _ in range(per_state):
                values.append(
                    SimpleNamespace(
                        split="test_iid", counter=counter, final_state=state
                    )
                )
                counter += 1
        return values

    def test_unique_problem_deduplication(self) -> None:
        values = self.examples()
        tripled = [value for value in values for _ in range(3)]
        unique = unique_problems(tripled)
        self.assertEqual(len(unique), len(values))
        self.assertEqual([value.counter for value in unique], list(range(len(values))))

    def test_balanced_subset(self) -> None:
        selected = balanced_subset(self.examples(4), per_state=2, states=6)
        self.assertEqual(len(selected), 12)
        self.assertEqual(
            {state: sum(value.final_state == state for value in selected) for state in range(6)},
            {state: 2 for state in range(6)},
        )

    def test_balanced_subset_is_seeded_and_not_a_prefix(self) -> None:
        examples = self.examples(8)
        selected = balanced_subset(examples, per_state=3, states=6, seed=17)
        repeated = balanced_subset(examples, per_state=3, states=6, seed=17)
        changed_seed = balanced_subset(examples, per_state=3, states=6, seed=18)
        self.assertEqual(
            [example.counter for example in selected],
            [example.counter for example in repeated],
        )
        self.assertNotEqual(
            [example.counter for example in selected],
            [example.counter for example in changed_seed],
        )
        prefix = [
            example.counter
            for state in range(6)
            for example in self.examples(8)[state * 8 : state * 8 + 3]
        ]
        self.assertNotEqual([example.counter for example in selected], prefix)

    def test_prompt_parser_includes_transition_at_start(self) -> None:
        example = SimpleNamespace(
            example_id="synthetic",
            compute_prompt=(
                "Finite state task. Transition: 0->4; 1->0; 2->5; "
                "3->2; 4->1; 5->3. Start at 3. Apply the transition "
                "exactly 2 times. Build and retain the final state internally."
            ),
        )
        start, transition_at_start, transition_map = _parse_prompt(example, 6)
        self.assertEqual(start, 3)
        self.assertEqual(transition_at_start, 2)
        self.assertEqual(transition_map, [4, 0, 5, 2, 1, 3])

    def test_donor_maps_are_bijective_and_semantic(self) -> None:
        values = self.examples()
        same, incompatible = donor_indices(values, 6)
        self.assertEqual(sorted(same), list(range(len(values))))
        self.assertEqual(sorted(incompatible), list(range(len(values))))
        for index, donor in enumerate(same):
            self.assertNotEqual(index, donor)
            self.assertEqual(values[index].final_state, values[donor].final_state)
        for index, donor in enumerate(incompatible):
            self.assertEqual(
                values[donor].final_state, (values[index].final_state + 3) % 6
            )
            self.assertNotEqual(
                values[index].final_state % 2, values[donor].final_state % 2
            )


class LocalizationDecisionTests(unittest.TestCase):
    DEFAULTS = {
        "source_robust": False,
        "initial_iid": False,
        "initial_robust": False,
        "final_iid": False,
        "final_robust": False,
        "decoded_iid": False,
        "projection_collapse": False,
        "rank1_dominance": False,
        "same_state_invariant": False,
        "positive_semantic_transport_established": False,
    }

    def test_cautious_localization_branches(self) -> None:
        cases = {
            "initializer": (
                {"source_robust": True},
                "CONSISTENT_WITH_INITIALIZER_SIGNAL_LOSS",
            ),
            "recurrent_erasure": (
                {"initial_iid": True, "initial_robust": True},
                "CONSISTENT_WITH_RECURRENT_SIGNAL_ERASURE",
            ),
            "output_projection": (
                {
                    "final_iid": True,
                    "projection_collapse": True,
                    "rank1_dominance": True,
                },
                "CONSISTENT_WITH_OUTPUT_PROJECTION_BOTTLENECK",
            ),
            "downstream_nonuse": (
                {
                    "decoded_iid": True,
                    "same_state_invariant": True,
                },
                "CONSISTENT_WITH_DOWNSTREAM_ANSWER_INTERFACE_NONUSE",
            ),
            "iid_without_ood": (
                {"final_iid": True},
                "IID_STATE_SIGNAL_WITHOUT_OOD_GENERALIZATION",
            ),
            "rank_one_no_signal": (
                {"projection_collapse": True},
                "RANK_ONE_STEERING_WITH_NO_ROBUST_FINAL_STATE_SIGNAL_DETECTED",
            ),
            "mixed": (
                {
                    "final_iid": True,
                    "final_robust": True,
                    "decoded_iid": True,
                    "same_state_invariant": True,
                    "positive_semantic_transport_established": True,
                },
                "INCONCLUSIVE_OR_MIXED_LOCALIZATION",
            ),
        }
        for name, (overrides, expected) in cases.items():
            with self.subTest(name=name):
                inputs = dict(self.DEFAULTS)
                inputs.update(overrides)
                self.assertEqual(classify_localization(**inputs), expected)


class SourceSafetyTests(unittest.TestCase):
    def test_restricted_checkpoint_load_is_explicit(self) -> None:
        source = (ROOT / "g1d" / "dynamic.py").read_text(encoding="utf-8")
        self.assertIn('map_location="cpu", weights_only=True', source)
        self.assertNotIn("optimizer.load_state_dict", source)
        self.assertNotIn("restore_rng_state", source)

    def test_raw_metadata_baseline_includes_transition_at_start(self) -> None:
        source = inspect.getsource(run_probes)
        self.assertIn('values["transition_at_start"]', source)

    def test_upstream_package_manifest_remains_valid(self) -> None:
        if str(VENDOR) not in sys.path:
            sys.path.insert(0, str(VENDOR))
        from neuralese_g1.integrity import verify_package_manifest

        result = verify_package_manifest(VENDOR)
        self.assertEqual(result["entry_count"], 29)
        self.assertEqual(
            result["manifest_sha256"],
            "fb3a29e2c799fc1139fc7378b6bdf92f8d0dafc775ba8250021662a4ba0632d7",
        )


if __name__ == "__main__":
    unittest.main()
