from __future__ import annotations

import json
import unittest
from collections import Counter
from dataclasses import replace
from pathlib import Path

from arithmetic_space_lab.workspace_data import (
    SUPPORTED_ARMS,
    StreamConfig,
    StructuralArithmeticStream,
    WorkspaceDataProvider,
    apply_derangement,
    audit_derangement,
    build_derangement_plan,
    length_only_nuisance_stratum,
    pseudo_fst_target,
    relation_family,
    split_family_partitions,
)


class StructuralStreamTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = StreamConfig(
            seed=12345,
            namespace="workspace-data-test",
            split="train",
            min_digits=1,
            max_digits=5,
            derangement_window=256,
        )

    def test_counter_stream_is_deterministic_and_answer_only(self) -> None:
        first = StructuralArithmeticStream(self.config).batch(0, 96)
        second = StructuralArithmeticStream(self.config).batch(0, 96)
        self.assertEqual(first, second)
        self.assertEqual(len({item.pair_id for item in first}), len(first))
        for item in first:
            expected = item.left + item.right if item.operation == "add" else item.left - item.right
            self.assertEqual(item.answer, str(expected))
            self.assertEqual(item.completion, item.answer)
            self.assertTrue(item.prompt.endswith("="))
            self.assertEqual(item.prompt.count("="), 1)
            self.assertEqual(item.metadata.event_count, item.metadata.carry_count + item.metadata.borrow_count)
            self.assertEqual(item.metadata.output_digits, len(item.answer))
            self.assertEqual(
                item.metadata.result_width_change,
                len(item.answer) - max(len(str(item.left)), len(str(item.right))),
            )
            self.assertEqual(item.metadata.has_zero, "0" in f"{item.left}{item.right}")
            self.assertEqual(item.metadata.has_nine, "9" in f"{item.left}{item.right}")

    def test_no_event_constraint_is_constructive(self) -> None:
        stream = StructuralArithmeticStream(self.config)
        rows = stream.batch(0, 256, constraint="no_event")
        self.assertTrue(all(item.is_no_event for item in rows))
        self.assertTrue(all(item.metadata.longest_chain == 0 for item in rows))

    def test_wide_single_event_constraint_is_constructive_in_sealed_split(self) -> None:
        # Regression for carry_discovery's first full evaluation.  Counter 18
        # in this exact 10-digit OOD stream exhausted 4096 unconstrained
        # rejection attempts before single-event operands were constructive.
        config = StreamConfig(
            seed=314159,
            namespace="arithmetic-workspace-v1",
            split="test_ood_plus2",
            min_digits=10,
            max_digits=10,
            operations=("add", "sub"),
            structure_cycle=("no_event", "event", "chain", "balanced"),
        )
        stream = StructuralArithmeticStream(config)
        failed_row = stream.example(18)
        rows = [stream.example(counter, constraint="event") for counter in range(64)]
        self.assertEqual(failed_row.metadata.event_count, 1)
        self.assertTrue(all(item.metadata.event_count == 1 for item in rows))
        self.assertTrue(all(item.metadata.longest_chain == 1 for item in rows))
        self.assertTrue(
            all(item.family_partition in split_family_partitions(config.split) for item in rows)
        )

    def test_short_structural_requests_promote_width_without_relabeling(self) -> None:
        cases = (
            ("sub", "event", 2),
            ("add", "chain", 2),
            ("sub", "chain", 3),
        )
        for operation, requested, expected_width in cases:
            with self.subTest(operation=operation, requested=requested):
                stream = StructuralArithmeticStream(
                    StreamConfig(
                        seed=7,
                        namespace="width-promotion-test",
                        split="train",
                        min_digits=1,
                        max_digits=expected_width,
                        operations=(operation,),
                        structure_cycle=(requested,),
                    )
                )
                row = stream.example(0)
                self.assertEqual(row.metadata.requested_structure, requested)
                self.assertEqual(row.metadata.left_digits, expected_width)
                self.assertEqual(row.metadata.right_digits, expected_width)
                if requested == "event":
                    self.assertEqual(row.metadata.event_count, 1)
                else:
                    self.assertGreaterEqual(row.metadata.longest_chain, 2)

    def test_infeasible_structural_width_fails_before_rejection(self) -> None:
        cases = (
            ("sub", "event", 1, 2),
            ("add", "chain", 1, 2),
            ("sub", "chain", 2, 3),
        )
        for operation, requested, maximum, required in cases:
            with self.subTest(operation=operation, requested=requested):
                stream = StructuralArithmeticStream(
                    StreamConfig(
                        seed=7,
                        namespace="infeasible-width-test",
                        split="train",
                        min_digits=1,
                        max_digits=maximum,
                        operations=(operation,),
                        structure_cycle=(requested,),
                    )
                )
                with self.assertRaisesRegex(
                    ValueError,
                    rf"structure={requested}.*operation={operation}.*max_digits >= {required}",
                ):
                    stream.example(0)

    def test_namespaces_and_splits_change_identity(self) -> None:
        base = StructuralArithmeticStream(self.config).example(11)
        other_namespace = StructuralArithmeticStream(
            StreamConfig(**{**self.config.to_dict(), "namespace": "other"})
        ).example(11)
        other_split = StructuralArithmeticStream(
            StreamConfig(**{**self.config.to_dict(), "split": "validation"})
        ).example(11)
        self.assertNotEqual(base.pair_id, other_namespace.pair_id)
        self.assertNotEqual(base.pair_id, other_split.pair_id)

    def test_pseudo_fst_is_deterministic_length_matched_and_state_sensitive(self) -> None:
        rows = StructuralArithmeticStream(self.config).batch(0, 128)
        four_state = [pseudo_fst_target(item, pseudo_seed=77, states=4) for item in rows]
        repeated = [pseudo_fst_target(item, pseudo_seed=77, states=4) for item in rows]
        eight_state = [pseudo_fst_target(item, pseudo_seed=77, states=8) for item in rows]
        self.assertEqual(four_state, repeated)
        self.assertTrue(any(left != right for left, right in zip(four_state, eight_state)))
        for item, target in zip(rows, four_state):
            self.assertEqual(len(target), len(item.answer))
            self.assertFalse(target.startswith("0"))


class RelationPartitionTests(unittest.TestCase):
    def test_add_sub_inverse_and_commuted_forms_share_family(self) -> None:
        addition = relation_family("add", 123, 456, "579")
        commuted = relation_family("add", 456, 123, "579")
        inverse_left = relation_family("sub", 579, 123, "456")
        inverse_right = relation_family("sub", 579, 456, "123")
        self.assertEqual(addition, commuted)
        self.assertEqual(addition, inverse_left)
        self.assertEqual(addition, inverse_right)

    def test_declared_study_namespaces_have_disjoint_partitions(self) -> None:
        splits = (
            "train",
            "validation",
            "discovery_fit",
            "space_selection",
            "intervention_calibration",
            "sealed_causal",
            "test_iid",
            "test_ood_digits",
            "final_test",
        )
        partitions = {split: split_family_partitions(split) for split in splits}
        for index, left in enumerate(splits):
            for right in splits[index + 1 :]:
                self.assertTrue(partitions[left].isdisjoint(partitions[right]), (left, right))

    def test_generated_family_ids_do_not_cross_sealed_splits(self) -> None:
        splits = ("train", "validation", "discovery", "causal", "final_test")
        families: dict[str, set[str]] = {}
        for split in splits:
            config = StreamConfig(
                seed=991,
                namespace="family-test",
                split=split,
                min_digits=2,
                max_digits=6,
            )
            rows = StructuralArithmeticStream(config).batch(0, 128)
            families[split] = {item.family_id for item in rows}
            allowed = split_family_partitions(split)
            self.assertTrue(all(item.family_partition in allowed for item in rows))
        for index, left in enumerate(splits):
            for right in splits[index + 1 :]:
                self.assertTrue(families[left].isdisjoint(families[right]))

    def test_behavior_test_namespaces_do_not_collide_with_causal(self) -> None:
        causal = split_family_partitions("causal_sealed")
        for split in ("test_no_transfer", "test_carry", "test_borrow"):
            self.assertEqual(split_family_partitions(split), frozenset({15}))
            self.assertTrue(split_family_partitions(split).isdisjoint(causal))


class DerangementTests(unittest.TestCase):
    def setUp(self) -> None:
        config = StreamConfig(
            seed=8181,
            namespace="derangement-test",
            split="train",
            min_digits=2,
            max_digits=6,
            derangement_window=512,
        )
        self.examples = StructuralArithmeticStream(config).batch(0, 1024)

    def test_plan_has_no_value_fixed_points_and_preserves_stratum_multisets(self) -> None:
        plan = build_derangement_plan(self.examples, seed=2027, drop_undetermined=False)
        audit = audit_derangement(self.examples, plan)
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["fixed_pair_count"], 0)
        self.assertEqual(audit["fixed_value_count"], 0)
        self.assertTrue(audit["global_multiset_preserved"])
        self.assertTrue(all(audit["per_stratum_multiset_preserved"].values()))
        self.assertEqual(audit["one_cycles"], 0)
        self.assertTrue(audit["deterministically_reproducible"])
        self.assertIn("within_stratum_pearson_weighted", audit)
        self.assertIn("within_stratum_pearson_max_abs", audit)
        self.assertIn("mean_prefix_fraction_excess", audit)
        self.assertIn("mean_suffix_fraction_excess", audit)

    def test_seeded_assignment_is_order_invariant_and_not_value_sorted(self) -> None:
        forward = build_derangement_plan(self.examples, seed=99, drop_undetermined=False)
        reverse = build_derangement_plan(list(reversed(self.examples)), seed=99, drop_undetermined=False)
        self.assertEqual(forward.assignment, reverse.assignment)
        source_numeric = {item.pair_id: int(item.completion) for item in self.examples}
        deltas = [
            abs(source_numeric[pair_id] - int(target))
            for pair_id, target in forward.assignment.items()
        ]
        self.assertGreater(max(deltas), 10)
        self.assertGreater(len(set(forward.assignment.values())), 20)

    def test_application_keeps_length_and_exact_target_multiset(self) -> None:
        plan = build_derangement_plan(self.examples, seed=551, drop_undetermined=False)
        changed = apply_derangement(self.examples, plan)
        source_by_id = {item.pair_id: item for item in self.examples}
        self.assertEqual(
            Counter(item.completion for item in changed),
            Counter(source_by_id[pair_id].completion for pair_id in plan.active_pair_ids),
        )
        for item in changed:
            self.assertEqual(item.control_arm, "deranged")
            self.assertNotEqual(item.completion, source_by_id[item.pair_id].completion)
            self.assertEqual(len(item.completion), len(source_by_id[item.pair_id].completion))

    def test_tiny_impossible_width_stratum_uses_explicit_synthetic_fallback(self) -> None:
        rows = []
        for index in range(4096):
            item = self.examples[index % len(self.examples)]
            value = ("4", "4", "5")[index] if index < 3 else str(10 + index % 3)
            rows.append(
                replace(
                    item,
                    pair_id=f"synthetic-fallback-{index:05d}",
                    completion=value,
                    answer=value,
                    metadata=replace(item.metadata, output_digits=len(value)),
                )
            )
        with self.assertRaisesRegex(ValueError, "not value-derangeable"):
            build_derangement_plan(
                rows,
                seed=130363,
                strata=length_only_nuisance_stratum,
                drop_undetermined=False,
            )
        plan = build_derangement_plan(
            rows,
            seed=130363,
            strata=length_only_nuisance_stratum,
            drop_undetermined=False,
            synthesize_impossible=True,
        )
        audit = audit_derangement(rows, plan)
        self.assertTrue(audit["valid"])
        self.assertEqual(plan.synthetic_rows, 3)
        self.assertEqual(len(plan.synthetic_pair_ids), 3)
        self.assertAlmostEqual(plan.synthetic_fraction, 3 / 4096)
        self.assertEqual(audit["synthetic_rows"], 3)
        self.assertEqual(audit["synthetic_fraction_cap"], 0.001)
        self.assertTrue(audit["synthetic_fraction_cap_passed"])
        self.assertFalse(audit["global_multiset_preserved"])
        self.assertTrue(audit["non_synthetic_global_multiset_preserved"])
        self.assertTrue(
            all(audit["per_non_synthetic_stratum_multiset_preserved"].values())
        )
        self.assertTrue(audit["width_match"])
        self.assertTrue(audit["canonical_decimal_targets"])
        self.assertEqual(audit["fixed_value_count"], 0)
        self.assertTrue(audit["deterministically_reproducible"])
        by_id = {item.pair_id: item for item in rows}
        for pair_id in plan.synthetic_pair_ids:
            target = plan.assignment[pair_id]
            self.assertEqual(len(target), len(by_id[pair_id].completion))
            self.assertNotEqual(target, by_id[pair_id].completion)
            self.assertTrue(target == "0" or (target.isdigit() and not target.startswith("0")))

        corrupted_assignment = dict(plan.assignment)
        corrupted_pair = plan.synthetic_pair_ids[0]
        corrupted_assignment[corrupted_pair] = by_id[corrupted_pair].completion
        corrupted = replace(plan, assignment=corrupted_assignment)
        self.assertFalse(audit_derangement(rows, corrupted)["valid"])

        with self.assertRaisesRegex(ValueError, "fraction exceeds hard cap"):
            build_derangement_plan(
                rows[:64],
                seed=130363,
                strata=length_only_nuisance_stratum,
                drop_undetermined=False,
                synthesize_impossible=True,
            )

    def test_confirmatory_impossible_windows_are_valid_and_fully_reported(self) -> None:
        profile_path = Path(__file__).resolve().parents[1] / "configs" / "carry_confirmatory.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        stage = next(
            item
            for item in profile["training"]["curriculum"]
            if item["name"] == "multi_propagation"
        )
        expected_rows = {
            (130363, 0): 5,
            (283051, 0): 3,
            (130363, 1_638_400): 1,
            (283051, 1_638_400): 0,
        }
        for (seed, counter), expected in expected_rows.items():
            with self.subTest(seed=seed, counter=counter):
                provider = WorkspaceDataProvider(profile["data"], seed=seed)
                source, plan = provider._derangement_window("train", counter, stage)
                audit = audit_derangement(source, plan)
                self.assertTrue(audit["valid"])
                self.assertEqual(audit["synthetic_rows"], expected)
                self.assertAlmostEqual(audit["synthetic_fraction"], expected / len(source))
                self.assertEqual(
                    plan.stratum_kind == "output_length_with_synthetic_fallback",
                    expected > 0,
                )
                self.assertEqual(audit["global_multiset_preserved"], expected == 0)
                self.assertTrue(audit["non_synthetic_global_multiset_preserved"])
                self.assertTrue(audit["synthetic_fraction_cap_passed"])
                self.assertTrue(audit["width_match"])
                self.assertTrue(audit["canonical_decimal_targets"])
                self.assertEqual(audit["fixed_value_count"], 0)


class ProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = WorkspaceDataProvider(
            {
                "seed": 9090,
                "namespace": "provider-test",
                "min_digits": 1,
                "max_digits": 4,
                "pseudo_states": 8,
                "derangement_window": 128,
                "derangement_max_abs_pearson": 0.25,
                "derangement_max_prefix_excess": 0.20,
                "unknown_profile_key_is_tolerated": True,
            }
        )

    def test_all_trainer_arms_are_reproducible(self) -> None:
        for arm in SUPPORTED_ARMS:
            first = self.provider.batch(arm, "train", 0, 32)
            second = self.provider.batch(arm, "train", 0, 32)
            self.assertEqual(first, second)
            self.assertTrue(self.provider.audit_control(arm, "train", 32)["valid"])
        self.assertTrue(all(item.is_no_event for item in self.provider.batch("no_carry", "train", 0, 64)))

    def test_derangement_cache_is_bounded(self) -> None:
        width = self.provider.config.derangement_window
        for window in range(5):
            self.provider.sample("deranged", "train", window * width)
        self.assertLessEqual(len(self.provider._derangement_cache), 2)

    def test_stage_ranges_and_symbol_renaming(self) -> None:
        rows = self.provider.fixed_eval(
            "correct",
            "symbol_renamed",
            32,
            {"digits": [2, 3], "structure_cycle": ["no_event"], "symbol_renamed": True},
        )
        self.assertTrue(all(2 <= item.difficulty <= 3 for item in rows))
        self.assertTrue(all(item.is_no_event for item in rows))
        self.assertTrue(all("⊕" in item.prompt or "⊖" in item.prompt for item in rows))

    def test_no_carry_training_filter_does_not_replace_common_eval_prompts(self) -> None:
        stage = {
            "digits": [2, 4],
            "operations": ["add"],
            "structure_cycle": ["event"],
        }
        correct = self.provider.fixed_eval("correct", "test_carry", 64, stage)
        no_carry = self.provider.fixed_eval("no_carry", "test_carry", 64, stage)
        self.assertEqual(
            [(item.prompt, item.completion) for item in correct],
            [(item.prompt, item.completion) for item in no_carry],
        )
        self.assertTrue(all(item.metadata.event_count >= 1 for item in no_carry))
        training = self.provider.fixed_eval("no_carry", "train", 64, stage)
        self.assertTrue(all(item.is_no_event for item in training))

    def test_counterfactual_pairs_are_minimally_matched(self) -> None:
        pairs = self.provider.counterfactual_pairs(
            "correct", "sealed_causal", 16, {"digits": [2, 4]}
        )
        self.assertEqual(len(pairs), 16)
        for pair in pairs:
            self.assertEqual(pair.clean.operation, pair.corrupt.operation)
            self.assertEqual(pair.clean.operand_digit_lengths, pair.corrupt.operand_digit_lengths)
            self.assertEqual(len(pair.clean.prompt), len(pair.corrupt.prompt))
            self.assertEqual(len(pair.clean.answer), len(pair.corrupt.answer))
            self.assertEqual(pair.clean.metadata.event_count, 0)
            self.assertEqual(pair.corrupt.metadata.event_count, 1)
            self.assertEqual(pair.corrupt.metadata.event_columns, (pair.event_column,))
            prompt_differences = sum(
                left != right for left, right in zip(pair.clean.prompt, pair.corrupt.prompt)
            )
            self.assertEqual(prompt_differences, 1)
            self.assertIn(pair.event_column, pair.expected_affected_digits)
            self.assertIn(pair.event_column + 1, pair.expected_affected_digits)

    def test_pseudo_counterfactual_direction_follows_fst_causality(self) -> None:
        pairs = self.provider.counterfactual_pairs(
            "pseudo_fst", "causal_sealed", 12, {"digits": [3, 5]}
        )
        for pair in pairs:
            expected = tuple(range(pair.event_column, pair.clean.metadata.output_digits))
            self.assertEqual(pair.expected_affected_digits, expected)
            self.assertTrue(
                all(position < pair.event_column for position in pair.expected_unaffected_digits)
            )

    def test_shipped_discovery_first_stage_control_and_chain_bounds(self) -> None:
        root = Path(__file__).resolve().parents[1]
        profile = json.loads((root / "configs" / "carry_discovery.json").read_text("utf-8"))
        provider = WorkspaceDataProvider(profile["data"], seed=314159)
        stages = profile["training"]["curriculum"]
        audit = provider.audit_control("deranged", "train", 4096, stages[0])
        self.assertTrue(audit["valid"])
        self.assertLessEqual(
            abs(audit["within_stratum_pearson_weighted"]),
            profile["data"]["derangement_max_abs_pearson"],
        )
        # Tiny one-digit strata remain reported but are excluded from the
        # residual-correlation gate because exact derangement forces negative
        # dependence in such a small alphabet.
        self.assertGreater(
            audit["within_stratum_pearson_max_abs_all"],
            audit["within_stratum_pearson_max_abs"],
        )
        for stage in stages[1:3]:
            rows = provider.fixed_eval("correct", "train", 512, stage)
            for item in rows:
                bounds = stage[
                    "carry_chain" if item.operation == "add" else "borrow_chain"
                ]
                self.assertGreaterEqual(item.metadata.longest_chain, bounds[0])
                self.assertLessEqual(item.metadata.longest_chain, bounds[1])
        single_event_rows = provider.fixed_eval(
            "correct", "train_single_event", 512, stages[1]
        )
        self.assertTrue(
            all(item.metadata.event_count == 1 for item in single_event_rows)
        )

    def test_shipped_discovery_iid_panel_preserves_requested_structures(self) -> None:
        root = Path(__file__).resolve().parents[1]
        profile = json.loads((root / "configs" / "carry_discovery.json").read_text("utf-8"))
        panel = next(
            item for item in profile["evaluation"]["panels"] if item["name"] == "iid_2_8"
        )
        provider = WorkspaceDataProvider(profile["data"], seed=314159)
        rows = provider.fixed_eval(
            "correct", panel["split"], panel["count"], panel["stage"]
        )
        self.assertEqual(
            {item.metadata.requested_structure for item in rows},
            {"no_event", "event", "chain", "balanced"},
        )
        for item in rows:
            requested = item.metadata.requested_structure
            if requested == "no_event":
                self.assertEqual(item.metadata.event_count, 0)
            elif requested == "event":
                self.assertEqual(item.metadata.event_count, 1)
            elif requested == "chain":
                self.assertGreaterEqual(item.metadata.longest_chain, 2)

    def test_shipped_discovery_no_event_resume_stream_is_unchanged(self) -> None:
        root = Path(__file__).resolve().parents[1]
        profile = json.loads((root / "configs" / "carry_discovery.json").read_text("utf-8"))
        provider = WorkspaceDataProvider(profile["data"], seed=314159)
        stage = profile["training"]["curriculum"][0]
        expected = {
            0: ("add", 7, 1, "8", "ws_4aef8bca1c2265452192999f"),
            1: ("sub", 9, 8, "1", "ws_8e5cad79bb2760e34dda97f3"),
            127999: ("sub", 5899, 1073, "4826", "ws_6516b472876f0ae84d83d28d"),
            128000: ("add", 2, 4, "6", "ws_e56d95ea63e6a75dc8780d66"),
        }
        observed = {}
        for counter in expected:
            item = provider.sample("correct", "train", counter, stage)
            observed[counter] = (
                item.operation,
                item.left,
                item.right,
                item.answer,
                item.pair_id,
            )
            self.assertEqual(item.metadata.requested_structure, "no_event")
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
