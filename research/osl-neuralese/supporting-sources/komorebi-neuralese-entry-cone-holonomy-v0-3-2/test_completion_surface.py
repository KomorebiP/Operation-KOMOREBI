from __future__ import annotations

import importlib
import itertools
import unittest
from pathlib import Path

import numpy as np

from checkpoint_io import LinearOperatorWeights, load_checkpoint
from core import (
    D4_RELATIONS,
    N_STATES,
    canonical_maps,
    compose_maps,
    encode_tables,
    positive_ray_angle,
    sample_batch,
    slots_for_word,
)
from relator_witness import (
    REGISTERED_RELATIONS,
    registered_relation_configurations,
)
from run_completion_surface import (
    analyze_completion_surface,
    build_episode_tree,
    canonical_word_to_slots,
    compare_scoped_signature_ids,
    downset_violations,
    expected_history_count,
    expected_suffix_count,
    explicit_prediction_signature,
    hard_partition_metrics,
    insert_word_at_cut,
    intern_hard_signatures,
    normalize_fail_closed,
    recursive_future_aggregates,
    softmax_fail_closed,
    summarize_cell,
    validate_downset,
    validate_execution_freeze,
)
from soft_surface import compute_soft_completion_surface


ROOT = Path(__file__).resolve().parent


def perfect_weights(decoder: np.ndarray | None = None) -> LinearOperatorWeights:
    """An exact, transparent implementation of the table task."""

    encoder = np.zeros((N_STATES * N_STATES, N_STATES * N_STATES), dtype=np.float32)
    for target in range(N_STATES):
        for source in range(N_STATES):
            output_index = target * N_STATES + source
            input_index = source * N_STATES + target
            encoder[output_index, input_index] = 1.0
    weights = LinearOperatorWeights(
        state_embedding=np.eye(N_STATES, dtype=np.float32),
        operator_encoder=encoder,
        decoder=(
            np.eye(N_STATES, dtype=np.float32)
            if decoder is None
            else np.asarray(decoder, dtype=np.float32)
        ),
    )
    weights.validate()
    return weights


def independently_apply(maps: np.ndarray, start: int, word: tuple[int, ...]) -> int:
    state = int(start)
    for operator in word:
        state = int(maps[int(operator), state])
    return state


def all_words_through(horizon: int) -> list[tuple[int, ...]]:
    return [
        word
        for depth in range(horizon + 1)
        for word in itertools.product(range(2), repeat=depth)
    ]


class EnvironmentInvariantTests(unittest.TestCase):
    def test_perfect_weights_replay_each_table_exactly(self) -> None:
        weights = perfect_weights()
        batch = sample_batch(np.random.default_rng(101), 13, 0, family="d4")
        flat = batch.tables.reshape(-1, 64)
        encoded = (flat @ weights.operator_encoder.T).reshape(-1, 8, 8)
        expected = np.swapaxes(batch.tables, -1, -2).reshape(-1, 8, 8)
        np.testing.assert_array_equal(encoded, expected)

    def test_canonical_to_slot_swap_preserves_semantics(self) -> None:
        batch = sample_batch(np.random.default_rng(202), 32, 0, family="d4")
        canonical = canonical_maps("d4")
        word = (0, 1, 0, 0, 1)
        expected = compose_maps(canonical, word)
        slot_words = slots_for_word(batch.canonical_to_slot, word)
        for episode in range(batch.tables.shape[0]):
            observed = compose_maps(batch.maps[episode], slot_words[episode])
            conjugated_expected = batch.phi[episode, expected[np.argsort(batch.phi[episode])]]
            np.testing.assert_array_equal(observed, conjugated_expected)

    def test_registered_relations_and_matched_controls(self) -> None:
        identity = np.arange(N_STATES, dtype=np.int64)
        maps = canonical_maps("d4")
        for name, relation in D4_RELATIONS.items():
            with self.subTest(relation=name):
                np.testing.assert_array_equal(compose_maps(maps, relation), identity)
                control = relation[:-1] + (1 - relation[-1],)
                self.assertFalse(np.array_equal(compose_maps(maps, control), identity))

    def test_positive_and_negative_rays_are_distinct(self) -> None:
        ray = np.array([[1.0, -2.0, 3.0, -4.0, 5.0, -6.0, 7.0, -8.0]])
        self.assertAlmostEqual(float(positive_ray_angle(ray, 7.0 * ray)[0]), 0.0)
        self.assertAlmostEqual(float(positive_ray_angle(ray, -7.0 * ray)[0]), np.pi)


class ExactTreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.weights = perfect_weights()
        self.batch = sample_batch(np.random.default_rng(303), 2, 0, family="d4")

    def tree(self, episode: int = 0, depth: int = 6):
        return build_episode_tree(
            self.weights,
            self.batch.tables[episode],
            self.batch.maps[episode],
            self.batch.canonical_to_slot[episode],
            depth,
            episode_id=f"synthetic:{episode}",
        )

    def test_vectorized_tree_matches_independent_scalar_semantics(self) -> None:
        tree = self.tree(depth=4)
        mapping = self.batch.canonical_to_slot[0]
        maps = self.batch.maps[0]
        for depth in range(5):
            observed: list[int] = []
            for start in range(N_STATES):
                for word in itertools.product(range(2), repeat=depth):
                    slots = canonical_word_to_slots(mapping, word)
                    observed.append(independently_apply(maps, start, tuple(slots)))
            np.testing.assert_array_equal(tree.semantic_by_depth[depth], observed)
            np.testing.assert_array_equal(
                tree.predictions_by_depth[depth], tree.semantic_by_depth[depth]
            )

    def test_vectorized_hidden_and_logits_match_float64_scalar_oracle(self) -> None:
        rng = np.random.default_rng(304)
        weights = LinearOperatorWeights(
            state_embedding=rng.normal(size=(8, 8)).astype(np.float32),
            operator_encoder=(0.2 * rng.normal(size=(64, 64))).astype(np.float32),
            decoder=rng.normal(size=(8, 8)).astype(np.float32),
        )
        weights.validate()
        tree = build_episode_tree(
            weights,
            self.batch.tables[0],
            self.batch.maps[0],
            self.batch.canonical_to_slot[0],
            3,
            episode_id="numeric-oracle",
        )
        slot_codes = encode_tables(weights, self.batch.tables[0][None], np.float64)[0]
        canonical_codes = slot_codes[self.batch.canonical_to_slot[0]]
        decoder = weights.decoder.astype(np.float64)
        for depth in range(4):
            expected_hidden: list[np.ndarray] = []
            for start in range(N_STATES):
                for word in itertools.product(range(2), repeat=depth):
                    state = weights.state_embedding[start].astype(np.float64).copy()
                    for operator in word:
                        state = canonical_codes[operator] @ state
                        state = state / np.linalg.norm(state)
                    expected_hidden.append(state)
            expected = np.stack(expected_hidden)
            np.testing.assert_allclose(tree.hidden_by_depth[depth], expected, rtol=1e-12, atol=1e-12)
            np.testing.assert_allclose(tree.logits_by_depth[depth], expected @ decoder.T, rtol=1e-12, atol=1e-12)

    def test_recursive_signature_ids_equal_explicit_suffix_profiles(self) -> None:
        tree = self.tree(depth=7)
        signatures = intern_hard_signatures(
            tree.predictions_by_depth,
            3,
            episode_id=tree.episode_id,
            episode_scope=tree.scope_token,
        )
        for horizon in range(4):
            for depth in range(5 - horizon):
                ids = signatures.ids(horizon, depth)
                profiles = [
                    explicit_prediction_signature(
                        tree.predictions_by_depth, depth, index, horizon
                    )
                    for index in range(ids.size)
                ]
                for left in range(ids.size):
                    for right in range(ids.size):
                        self.assertEqual(
                            bool(ids[left] == ids[right]),
                            profiles[left] == profiles[right],
                        )

    def test_registered_count_formulas(self) -> None:
        for L in range(9):
            self.assertEqual(expected_history_count(L), 8 * (2 ** (L + 1) - 1))
            self.assertEqual(expected_history_count(L, "exact"), 8 * 2**L)
        for H in range(9):
            self.assertEqual(expected_suffix_count(H), 2 ** (H + 1) - 1)
            self.assertEqual(expected_suffix_count(H, "exact"), 2**H)

    def test_perfect_surface_passes_all_hard_soft_and_diagonal_checks(self) -> None:
        tree = self.tree(depth=6)
        result = analyze_completion_surface(tree, 3, 3, include_soft=True)
        self.assertTrue(result["hard_rectangle_passed"])
        self.assertTrue(result["downset_passed"])
        self.assertTrue(result["diagonal_action"]["passed"])
        self.assertTrue(
            result["soft_interfaces"]["both_interfaces_exact_on_cumulative_rectangle"]
        )
        final = result["cumulative_cells"][-1]
        self.assertEqual(final["history_count"], 8 * 15)
        self.assertEqual(final["suffix_count"], 15)
        self.assertEqual(final["decision_count"], 8 * 15 * 15)

    def test_recursive_future_aggregate_matches_explicit_decisions(self) -> None:
        tree = self.tree(depth=5)
        aggregates = recursive_future_aggregates(tree, 3)
        for horizon in range(4):
            suffix_count = expected_suffix_count(horizon)
            for depth in range(5 - horizon):
                self.assertTrue(np.all(aggregates.correct_counts[horizon][depth] == suffix_count))
                self.assertTrue(np.all(aggregates.all_correct[horizon][depth]))

    def test_signature_scope_is_object_identity_not_display_name(self) -> None:
        tree = self.tree(depth=3)
        left = intern_hard_signatures(tree.predictions_by_depth, 1, episode_id="same")
        right = intern_hard_signatures(tree.predictions_by_depth, 1, episode_id="same")
        with self.assertRaises(ValueError):
            compare_scoped_signature_ids(left, right, 1, 0)

    def test_fail_closed_normalization_and_softmax(self) -> None:
        with self.assertRaises(ArithmeticError):
            normalize_fail_closed(np.zeros((1, N_STATES)))
        with self.assertRaises(ArithmeticError):
            normalize_fail_closed(np.full((1, N_STATES), np.nan))
        with self.assertRaises(ArithmeticError):
            softmax_fail_closed(np.full((1, N_STATES), np.inf))

    def test_soft_surface_detects_history_microstate_without_changing_hard_code(self) -> None:
        tree = self.tree(depth=4)
        centered = tuple(x - x.mean(axis=1, keepdims=True) for x in tree.logits_by_depth)
        exact = compute_soft_completion_surface(
            tree.probabilities_by_depth,
            centered,
            tree.semantic_by_depth,
            max_history_depth=2,
            max_future_horizon=2,
        )
        self.assertTrue(exact["both_interfaces_exact_on_cumulative_rectangle"])
        changed_probabilities = [row.copy() for row in tree.probabilities_by_depth]
        changed_probabilities[2][0, 0] += 1e-4
        changed_probabilities[2][0, 1] -= 1e-4
        changed = compute_soft_completion_surface(
            tuple(changed_probabilities),
            centered,
            tree.semantic_by_depth,
            max_history_depth=2,
            max_future_horizon=2,
        )
        self.assertFalse(
            changed["interfaces"]["probability"]
            ["all_cumulative_cells_exact_soft_collapse"]
        )


class PartitionAndOrderTests(unittest.TestCase):
    def test_partition_fixtures_distinguish_split_merge_and_wrong(self) -> None:
        labels = np.repeat(np.arange(N_STATES), 2)
        coherent = np.repeat(np.arange(N_STATES), 2)
        good = hard_partition_metrics(labels, coherent)
        self.assertEqual(good["signature_class_count"], 8)
        self.assertEqual(good["maximum_split_multiplicity"], 1)
        self.assertEqual(good["maximum_merge_multiplicity"], 1)
        self.assertEqual(good["semantic_label_completion_fraction"], 1.0)

        split = coherent.copy()
        split[1] = 99
        split_result = hard_partition_metrics(labels, split)
        self.assertEqual(split_result["maximum_split_multiplicity"], 2)

        merged = coherent.copy()
        merged[labels == 1] = 0
        merge_result = hard_partition_metrics(labels, merged)
        self.assertEqual(merge_result["maximum_merge_multiplicity"], 2)

        correctness = np.ones(labels.size, dtype=bool)
        correctness[0] = False
        wrong = hard_partition_metrics(labels, coherent, correctness)
        self.assertEqual(wrong["maximum_split_multiplicity"], 1)
        self.assertLess(wrong["semantic_label_completion_fraction"], 1.0)

    def test_downset_validator_accepts_and_rejects_expected_masks(self) -> None:
        valid = np.array(
            [[True, True, False], [True, False, False], [False, False, False]],
            dtype=bool,
        )
        self.assertTrue(validate_downset(valid))
        invalid = valid.copy()
        invalid[2, 2] = True
        self.assertTrue(downset_violations(invalid))
        with self.assertRaises(ValueError):
            validate_downset(invalid)

    def test_inserted_word_preserves_declared_order(self) -> None:
        self.assertEqual(insert_word_at_cut((0, 1, 1), (0, 0), 2), (0, 1, 0, 0, 1))
        with self.assertRaises(ValueError):
            insert_word_at_cut((0,), (1,), 2)

    def test_all_registered_repeats_are_identity_and_controls_nonidentity(self) -> None:
        maps = canonical_maps("d4")
        identity = np.arange(N_STATES)
        configurations = registered_relation_configurations()
        self.assertEqual(len(configurations), 21)
        observed_budgets: dict[str, list[int]] = {}
        for item in configurations:
            observed_budgets.setdefault(item.relation, []).append(item.inserted_token_budget)
            np.testing.assert_array_equal(compose_maps(maps, item.identity_word), identity)
            self.assertFalse(np.array_equal(compose_maps(maps, item.control_word), identity))
            self.assertEqual(len(item.identity_word), len(item.control_word))
            self.assertEqual(item.identity_word[:-1], item.control_word[:-1])
            self.assertNotEqual(item.identity_word[-1], item.control_word[-1])
        self.assertEqual(observed_budgets["f2"], [2, 4, 8, 16, 32, 64])
        for name in ("r4", "frfr", "rfrf"):
            self.assertEqual(observed_budgets[name], [4, 8, 16, 32, 64])

    def test_named_relator_table_matches_module_contract(self) -> None:
        self.assertEqual(
            dict(REGISTERED_RELATIONS),
            {
                "r4": (0, 0, 0, 0),
                "f2": (1, 1),
                "frfr": (1, 0, 1, 0),
                "rfrf": (0, 1, 0, 1),
            },
        )

    def test_canonical_execution_freeze_and_lineage_are_self_consistent(self) -> None:
        record = validate_execution_freeze()
        self.assertTrue(record["passed"])
        self.assertGreaterEqual(record["validated_file_count"], 12)
        self.assertGreaterEqual(record["structural_test_count"], 18)


if __name__ == "__main__":
    unittest.main(verbosity=2)
