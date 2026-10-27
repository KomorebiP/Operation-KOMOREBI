from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, fields
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.sparse_task import (
    AUDIT_ONLY_FIELDS,
    CONTEXT_SPLIT_COUNTS,
    CONTEXT_SPLIT_NAMESPACE,
    CONTEXT_SPLITS,
    DEMONSTRATIONS_PER_OPERATOR,
    FIELD_ORDER,
    GLOBAL_CLOSURE_WITNESS_MAX_DEPTH,
    KEY_ARM,
    MODEL_INPUT_FIELDS,
    MONOMIAL_FAMILY,
    N_ATTRIBUTES,
    N_OPERATORS,
    N_PRODUCT_STATES,
    OPERATOR_FAMILIES,
    PRIMITIVE_DIAGNOSTIC_ARM,
    SHEAR_FAMILY,
    SUPERVISION_FIELDS,
    TRAINING_WORD_LENGTHS,
    SparseModelInputs,
    SparseAffineGenerator,
    all_product_states,
    arbitrary_table_first_step_candidates,
    audit_context_splits,
    audit_train_closure,
    compose_word,
    context_audit_record,
    context_split_manifest,
    contexts_in_split,
    decode_product_state,
    direct_lookup_execute,
    encode_product_state,
    factor_combination_audit,
    get_context,
    infer_affine_map,
    monomial_torus_matrix,
    oracle_query_transitions,
    render_transition_table,
    project_model_inputs,
    require_train_closure_safe,
    solve_batch,
    solve_episode,
    solve_model_inputs,
    train_closure_audit_record,
    train_closure_witnesses,
    torus_encode,
)


EXPECTED_CATALOG_DIGESTS = {
    SHEAR_FAMILY: "87a40820648367a6c6fc6b03a51ce8335bed71e0dded4b3b39160563c92fa05a",
    MONOMIAL_FAMILY: "77d8d985a569420e1bcfdd230a6d7b36e2496498028ece9ade77a61d67fa4334",
}

EXPECTED_CLOSURE_AUDITS = {
    SHEAR_FAMILY: {
        "bounded_maps": 1192,
        "bounded_by_split": {"dev": 43, "test": 43},
        "bounded_by_depth": {"2": 52, "3": 25, "4": 9, "unwitnessed": 10},
        "bounded_digest": "e24de9b50a3b06c3d958f8b19d31216d81410cd9847d23eeb04a526be9af4190",
        "global_depth_two_maps": 13151,
        "global_by_depth": {"1": 0, "2": 95, "3": 1, "unwitnessed": 0},
        "global_digest": "a8f57ab80177320b97ed9736deb1c85b523b74cf6f0efd947f40f22923bc52f3",
    },
    MONOMIAL_FAMILY: {
        "bounded_maps": 1902,
        "bounded_by_split": {"dev": 0, "test": 0},
        "bounded_by_depth": {"2": 0, "3": 0, "4": 0, "unwitnessed": 96},
        "bounded_digest": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "global_depth_two_maps": 19861,
        "global_by_depth": {"1": 0, "2": 12, "3": 84, "unwitnessed": 0},
        "global_digest": "d72912af618d48c6517bf4913d0099b49e7f22191a8a644a935e1d21a6c7da18",
    },
}


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_frozen_context_split_has_exact_counts_and_no_context_or_operator_overlap(
    family: str,
) -> None:
    audit = audit_context_splits(family)
    assert audit.namespace == CONTEXT_SPLIT_NAMESPACE
    assert dict(CONTEXT_SPLIT_COUNTS) == {"train": 72, "dev": 24, "test": 24}
    assert dict(audit.observed_counts) == dict(CONTEXT_SPLIT_COUNTS)
    assert dict(audit.context_pairwise_intersections) == {
        "train_dev": 0,
        "train_test": 0,
        "dev_test": 0,
    }
    assert dict(audit.operator_pairwise_intersections) == {
        "train_dev": 0,
        "train_test": 0,
        "dev_test": 0,
    }
    assert audit.unique_contexts
    assert audit.unique_operators
    assert audit.complete
    assert audit.passed
    assert audit.digest == EXPECTED_CATALOG_DIGESTS[family]
    # The receipt separates literal split disjointness from closure novelty.
    receipt = json.loads(json.dumps(context_audit_record(family)))
    assert receipt["primitive_split_disjointness_passed"] is True
    assert receipt["bounded_operator_novelty_passed"] is (
        family == MONOMIAL_FAMILY
    )
    assert receipt["passed"] is (family == MONOMIAL_FAMILY)
    factors = factor_combination_audit(family)
    assert factors["combination_counts"] == {"train": 144, "dev": 48, "test": 48}
    assert factors["pairwise_combination_intersections"] == {
        "train_dev": 0,
        "train_test": 0,
        "dev_test": 0,
    }
    assert factors["passed"] is True


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_context_catalog_is_deeply_immutable(family: str) -> None:
    context = contexts_in_split("train", family)[0]
    with pytest.raises(FrozenInstanceError):
        context.split = "test"  # type: ignore[misc]
    with pytest.raises(TypeError):
        context.operators[0].matrix[0][0] = 2  # type: ignore[index]
    manifest = context_split_manifest(family)
    with pytest.raises(TypeError):
        manifest[context.context_id] = "test"  # type: ignore[index]


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_every_primitive_occurs_in_exactly_one_context_and_split(family: str) -> None:
    fingerprints_by_split = {
        split: {
            operator.fingerprint
            for context in contexts_in_split(split, family)
            for operator in context.operators
        }
        for split in CONTEXT_SPLITS
    }
    assert {split: len(values) for split, values in fingerprints_by_split.items()} == {
        "train": 144,
        "dev": 48,
        "test": 48,
    }
    assert not fingerprints_by_split["train"] & fingerprints_by_split["dev"]
    assert not fingerprints_by_split["train"] & fingerprints_by_split["test"]
    assert not fingerprints_by_split["dev"] & fingerprints_by_split["test"]
    assert len(set().union(*fingerprints_by_split.values())) == 240


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_train_closure_contamination_is_exactly_audited_and_certified(
    family: str,
) -> None:
    expected = EXPECTED_CLOSURE_AUDITS[family]
    audit = audit_train_closure(family)
    record = train_closure_audit_record(family)
    assert audit.training_lengths == TRAINING_WORD_LENGTHS == (2, 3, 4)
    assert audit.train_context_count == 72
    assert audit.train_primitive_count == 144
    assert dict(audit.heldout_primitive_counts) == {"dev": 48, "test": 48}
    assert audit.bounded_supported_map_count == expected["bounded_maps"]
    assert dict(audit.bounded_contamination_counts) == expected["bounded_by_split"]
    assert dict(audit.bounded_minimum_depth_counts) == expected["bounded_by_depth"]
    assert audit.bounded_witness_digest == expected["bounded_digest"]
    assert audit.global_witness_max_depth == GLOBAL_CLOSURE_WITNESS_MAX_DEPTH == 3
    assert audit.global_depth_two_map_count == expected["global_depth_two_maps"]
    assert dict(audit.global_contamination_counts) == {"dev": 48, "test": 48}
    assert dict(audit.global_minimum_depth_counts) == expected["global_by_depth"]
    assert audit.global_witness_digest == expected["global_digest"]
    assert audit.global_all_heldout_witnessed
    assert not audit.global_closure_exhausted
    assert not audit.unbounded_operator_novelty_passed
    assert json.loads(json.dumps(record)) == record

    train_by_fingerprint = {
        operator.fingerprint: operator
        for context in contexts_in_split("train", family)
        for operator in context.operators
    }
    heldout_by_fingerprint = {
        operator.fingerprint: operator
        for split in ("dev", "test")
        for context in contexts_in_split(split, family)
        for operator in context.operators
    }
    for scope in ("bounded_training_support", "global_generators"):
        for witness in train_closure_witnesses(family, scope=scope):
            operators = tuple(
                train_by_fingerprint[fingerprint]
                for fingerprint in witness.train_operator_fingerprints
            )
            composed = compose_word(operators, range(len(operators)))
            assert composed.fingerprint == witness.target_fingerprint
            assert composed == heldout_by_fingerprint[witness.target_fingerprint]
            assert witness.depth == len(witness.train_operator_fingerprints)
            if scope == "bounded_training_support":
                context = get_context(witness.train_context_id)
                assert all(operator in context.operators for operator in operators)


def test_closure_claim_guard_fails_closed_at_the_correct_boundaries() -> None:
    monomial = require_train_closure_safe(
        MONOMIAL_FAMILY, scope="bounded_training_support"
    )
    assert monomial.bounded_training_support_novelty_passed
    with pytest.raises(RuntimeError, match="86 held-out primitives"):
        require_train_closure_safe(SHEAR_FAMILY, scope="bounded_training_support")
    for family in OPERATOR_FAMILIES:
        with pytest.raises(RuntimeError, match="96 held-out primitives"):
            require_train_closure_safe(family, scope="global_generators")
    with pytest.raises(ValueError, match="scope"):
        require_train_closure_safe(MONOMIAL_FAMILY, scope="ambiguous")


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_sparse_batch_schema_has_no_dense_table_or_intermediate_shortcut(family: str) -> None:
    batch = SparseAffineGenerator(101, split="train", family=family).sample_batch(8, 4)
    assert batch.demo_inputs.shape == (8, N_OPERATORS, DEMONSTRATIONS_PER_OPERATOR, N_ATTRIBUTES)
    assert batch.demo_outputs.shape == batch.demo_inputs.shape
    assert batch.start_attributes.shape == (8, N_ATTRIBUTES)
    assert batch.op_slots.shape == (8, 4)
    assert batch.target_attributes.shape == (8, N_ATTRIBUTES)
    assert batch.write_masks.shape == (8, N_OPERATORS, N_ATTRIBUTES)
    assert batch.dependency_masks.shape == (8, N_OPERATORS, N_ATTRIBUTES, N_ATTRIBUTES)
    assert batch.update_read_masks.shape == batch.write_masks.shape
    assert batch.preserved_masks.shape == batch.write_masks.shape
    assert batch.family == family
    assert MODEL_INPUT_FIELDS == (
        "demo_inputs",
        "demo_outputs",
        "start_attributes",
        "op_slots",
    )
    assert SUPERVISION_FIELDS == ("target_attributes",)
    assert set(AUDIT_ONLY_FIELDS).isdisjoint(MODEL_INPUT_FIELDS)
    for forbidden in ("tables", "maps", "intermediates", "canonical_ops", "phi"):
        assert not hasattr(batch, forbidden)
    # Ten observed transition rows out of two 625-row tables is 0.8%.
    assert (N_OPERATORS * DEMONSTRATIONS_PER_OPERATOR) / (
        N_OPERATORS * N_PRODUCT_STATES
    ) == 0.008
    assert not batch.demo_inputs.flags.writeable
    with pytest.raises(ValueError):
        batch.demo_inputs.setflags(write=True)


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_nominal_model_projection_excludes_supervision_identity_and_audit_truth(
    family: str,
) -> None:
    batch = SparseAffineGenerator(102, split="train", family=family).sample_batch(8, 4)
    inputs = project_model_inputs(batch)
    assert isinstance(inputs, SparseModelInputs)
    assert tuple(field.name for field in fields(SparseModelInputs)) == MODEL_INPUT_FIELDS
    assert tuple(vars(inputs)) == MODEL_INPUT_FIELDS
    assert inputs.batch_size == batch.batch_size
    assert inputs.length == batch.length
    for name in MODEL_INPUT_FIELDS:
        projected = getattr(inputs, name)
        source = getattr(batch, name)
        assert np.array_equal(projected, source)
        assert not np.shares_memory(projected, source)
        assert not projected.flags.writeable
        with pytest.raises(ValueError):
            projected.setflags(write=True)
    for forbidden in (
        *SUPERVISION_FIELDS,
        *AUDIT_ONLY_FIELDS,
        "family",
        "split",
        "arm",
        "operators",
        "demonstrations",
    ):
        assert not hasattr(inputs, forbidden), forbidden
    assert np.array_equal(solve_model_inputs(inputs), batch.target_attributes)
    assert np.array_equal(solve_batch(batch), batch.target_attributes)
    with pytest.raises(FrozenInstanceError):
        inputs.op_slots = batch.op_slots  # type: ignore[misc]
    with pytest.raises(TypeError, match="SparseEpisodeBatch"):
        project_model_inputs(inputs)  # type: ignore[arg-type]


def test_key_arm_forbids_primitive_terminal_supervision() -> None:
    generator = SparseAffineGenerator(103, arm=KEY_ARM)
    with pytest.raises(ValueError, match="length-1"):
        generator.sample(1)
    diagnostic = SparseAffineGenerator(103, arm=PRIMITIVE_DIAGNOSTIC_ARM).sample(1)
    assert diagnostic.length == 1
    assert solve_episode(diagnostic) == diagnostic.target_attributes
    assert not hasattr(diagnostic, "intermediates")


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_five_affine_independent_demos_identify_every_frozen_operator(family: str) -> None:
    seen = 0
    for split in CONTEXT_SPLITS:
        for context in contexts_in_split(split, family):
            for operator, demonstrations in zip(context.operators, context.demonstrations):
                inferred = infer_affine_map(demonstrations)
                assert inferred.matrix == operator.matrix
                assert inferred.bias == operator.bias
                seen += 1
    assert seen == 240


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
@pytest.mark.parametrize("split", CONTEXT_SPLITS)
@pytest.mark.parametrize("length", (2, 7, 31, 129))
def test_sparse_queries_are_exactly_solvable_at_preregisterable_depths(
    family: str, split: str, length: int
) -> None:
    episode = SparseAffineGenerator(107 + length, split=split, family=family).sample(length)
    assert episode.length == length
    assert episode.split == split
    assert episode.family == family
    assert solve_episode(episode) == episode.target_attributes


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
@pytest.mark.parametrize("split", CONTEXT_SPLITS)
def test_direct_table_executor_cannot_enter_key_query_without_inference(
    family: str, split: str
) -> None:
    generator = SparseAffineGenerator(211, split=split, family=family)
    for _ in range(12):
        episode = generator.sample(9)
        observed_sources = tuple(
            {demo.source for demo in demos} for demos in episode.demonstrations
        )
        transitions = oracle_query_transitions(episode)
        assert all(source not in observed_sources[slot] for slot, source, _ in transitions)
        assert direct_lookup_execute(episode) is None
        candidates = arbitrary_table_first_step_candidates(episode)
        assert len(candidates) == N_PRODUCT_STATES - DEMONSTRATIONS_PER_OPERATOR == 620
        assert transitions[0][2] in candidates
        assert len(candidates) > 1
        # The designated hypothesis class nevertheless has a unique exact answer.
        assert solve_episode(episode) == episode.target_attributes


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_split_confinement_fails_closed(family: str) -> None:
    test_context = contexts_in_split("test", family)[0]
    with pytest.raises(ValueError, match="belongs to test"):
        SparseAffineGenerator(223, split="train", family=family).sample(
            3, context_id=test_context.context_id
        )
    other_family = MONOMIAL_FAMILY if family == SHEAR_FAMILY else SHEAR_FAMILY
    wrong_family_context = contexts_in_split("train", other_family)[0]
    with pytest.raises(ValueError, match="belongs to family"):
        SparseAffineGenerator(223, split="train", family=family).sample(
            3, context_id=wrong_family_context.context_id
        )


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_generator_stream_and_batch_solver_are_deterministic(family: str) -> None:
    first = SparseAffineGenerator(227, split="dev", family=family).sample_batch(16, 8)
    second = SparseAffineGenerator(227, split="dev", family=family).sample_batch(16, 8)
    for field in (
        "demo_inputs",
        "demo_outputs",
        "start_attributes",
        "op_slots",
        "target_attributes",
        "write_masks",
        "dependency_masks",
        "update_read_masks",
        "preserved_masks",
    ):
        assert np.array_equal(getattr(first, field), getattr(second, field)), field
    assert first.context_ids == second.context_ids
    assert first.context_fingerprints == second.context_fingerprints
    assert np.array_equal(solve_batch(first), first.target_attributes)


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_vectorized_batch_sampler_keeps_every_query_cell_unobserved(family: str) -> None:
    batch = SparseAffineGenerator(228, split="test", family=family).sample_batch(256, 32)
    for row, context_id in enumerate(batch.context_ids):
        context = get_context(context_id)
        current = tuple(int(value) for value in batch.start_attributes[row])
        for slot_value in batch.op_slots[row]:
            slot = int(slot_value)
            assert current not in {
                demo.source for demo in context.demonstrations[slot]
            }
            current = context.operators[slot].apply(current)
        assert current == tuple(int(value) for value in batch.target_attributes[row])


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_exact_composition_and_full_rendering_are_audit_only_utilities(family: str) -> None:
    context = contexts_in_split("dev", family)[3]
    word = (0, 1, 1, 0, 1, 0, 0)
    composed = compose_word(context.operators, word)
    for state in all_product_states():
        current = state
        for slot in word:
            current = context.operators[slot].apply(current)
        assert composed.apply(state) == current
    table = render_transition_table(composed)
    assert table.shape == (N_PRODUCT_STATES,)
    assert len(set(int(value) for value in table)) == N_PRODUCT_STATES
    assert not table.flags.writeable


def test_signed_monomial_family_has_exact_orthogonal_8d_torus_action() -> None:
    identity = np.eye(2 * N_ATTRIBUTES)
    for split in CONTEXT_SPLITS:
        for context in contexts_in_split(split, MONOMIAL_FAMILY):
            for operator in context.operators:
                representation = monomial_torus_matrix(operator)
                assert np.allclose(representation.T @ representation, identity, atol=1e-12)
                for state in all_product_states():
                    assert np.allclose(
                        representation @ torus_encode(state),
                        torus_encode(operator.apply(state)),
                        atol=1e-12,
                    )


def test_shear_is_explicitly_outside_the_8d_monomial_representation() -> None:
    shear = contexts_in_split("train", SHEAR_FAMILY)[0].operators[0]
    with pytest.raises(ValueError, match="signed-monomial"):
        monomial_torus_matrix(shear)


@pytest.mark.parametrize("family", OPERATOR_FAMILIES)
def test_product_attribute_interventions_separate_specificity_and_invariance(
    family: str,
) -> None:
    generator = SparseAffineGenerator(229, split="test", family=family)
    for _ in range(32):
        probe = generator.sample_intervention()
        output_attribute = probe.probed_output_attribute
        assert (
            probe.relevant_output[output_attribute]
            != probe.base_output[output_attribute]
        )
        assert (
            probe.irrelevant_output[output_attribute]
            == probe.base_output[output_attribute]
        )
        assert probe.dependency_mask[output_attribute][probe.relevant_attribute]
        assert not probe.dependency_mask[output_attribute][probe.irrelevant_attribute]
        assert probe.relevant_attribute != probe.irrelevant_attribute

        if family == MONOMIAL_FAMILY:
            continue
        changed_relevant_effects = {
            index
            for index, (base, relevant) in enumerate(
                zip(probe.base_effect, probe.relevant_effect)
            )
            if base != relevant
        }
        assert changed_relevant_effects == {
            index for index, enabled in enumerate(probe.write_mask) if enabled
        }
        assert probe.irrelevant_effect == probe.base_effect
        assert probe.update_read_mask[probe.relevant_attribute]
        assert not probe.update_read_mask[probe.irrelevant_attribute]
        for index, preserved in enumerate(probe.preserved_mask):
            if preserved:
                assert probe.base_output[index] == probe.base_input[index]


def test_product_state_encoding_is_a_bijection_and_preserves_attribute_payload() -> None:
    encoded = {encode_product_state(state) for state in all_product_states()}
    assert encoded == set(range(N_PRODUCT_STATES))
    for index in range(N_PRODUCT_STATES):
        assert encode_product_state(decode_product_state(index)) == index
    assert FIELD_ORDER == 5
