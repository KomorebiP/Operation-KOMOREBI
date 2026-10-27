from __future__ import annotations

import pytest

from osl_lab.model import (
    TORCH_AVAILABLE,
    DeterministicVocabulary,
    ModelConfig,
    OSLTransformer,
    StableLabelEncoder,
    build_operator_vocabulary,
    canonical_json,
)
from osl_lab.training import _extract_law_specs, _semantic_equivalence_id


def test_vocabulary_is_frequency_then_lexicographically_deterministic() -> None:
    first = DeterministicVocabulary().fit(["Beta alpha alpha.", "Gamma beta!"])
    second = DeterministicVocabulary().fit(reversed(["Beta alpha alpha.", "Gamma beta!"]))
    assert first.id_to_token == second.id_to_token
    assert first.id_to_token[:4] == ["[PAD]", "[UNK]", "[CLS]", "[SEP]"]
    assert first.id_to_token[4:7] == ["alpha", "beta", "!"]


def test_pair_encoding_has_stable_boundaries_and_padding() -> None:
    vocabulary = DeterministicVocabulary().fit(["Mira saw a gate", "Is it open?"])
    encoded = vocabulary.encode_pair("Mira saw a gate", "Is it open?", max_length=14)
    assert len(encoded["input_ids"]) == 14
    assert len(encoded["attention_mask"]) == 14
    assert encoded["input_ids"][0] == vocabulary.cls_id
    assert sum(encoded["attention_mask"]) == 11
    assert encoded["token_type_ids"][0] == 0
    assert 1 in encoded["token_type_ids"]


def test_vocabulary_and_labels_round_trip() -> None:
    vocabulary = DeterministicVocabulary(lowercase=False, max_size=9).fit(["z z a", "b"])
    restored = DeterministicVocabulary.from_dict(vocabulary.to_dict())
    assert restored.id_to_token == vocabulary.id_to_token
    assert restored.lowercase is False

    labels = StableLabelEncoder().fit(["yes", "no", "yes"])
    assert labels.labels == ["no", "yes"]
    assert labels.inverse_transform(labels.transform(["yes", "no"])) == ["yes", "no"]
    assert StableLabelEncoder.from_dict(labels.to_dict()).labels == labels.labels


def test_hashed_words_preserve_unseen_identifier_identity() -> None:
    from osl_lab.generator import NONCE_POOL

    vocabulary = DeterministicVocabulary(hash_buckets=2048).fit(["known words"])
    first = vocabulary.encode_tokens(["dax", "dax", "wug"])
    assert first[0] == first[1]
    assert first[0] != first[2]
    restored = DeterministicVocabulary.from_dict(vocabulary.to_dict())
    assert restored.encode_tokens(["dax", "wug"]) == [first[0], first[2]]
    assert len(set(vocabulary.encode_tokens(NONCE_POOL))) == len(NONCE_POOL)


def test_canonical_state_and_operator_vocabulary() -> None:
    assert canonical_json({"b": 2, "a": {"z": 1}}) == '{"a":{"z":1},"b":2}'
    records = [
        {"program": [{"op": "TELL"}, {"operator": "OBSERVE"}]},
        {"program": ["TELL", {"name": "QUARANTINE"}]},
    ]
    assert build_operator_vocabulary(records) == {
        "OBSERVE": 0,
        "QUARANTINE": 1,
        "TELL": 2,
    }


def test_invalid_model_config_is_rejected() -> None:
    with pytest.raises(ValueError):
        ModelConfig(vocab_size=10, num_answers=2, d_model=15, n_heads=4)
    with pytest.raises(ValueError):
        ModelConfig(vocab_size=10, num_answers=2, arm="unknown")


def test_equivalence_context_is_not_collapsed_and_world_laws_are_loaded() -> None:
    common = {
        "world": "algebra",
        "canonical_transform_id": "t1",
        "initial_state": {"left": False, "right": False},
    }
    left_query = {**common, "question_id": "left_status"}
    right_query = {**common, "question_id": "right_status"}
    assert _semantic_equivalence_id(left_query) != _semantic_equivalence_id(right_query)
    assert _semantic_equivalence_id({**left_query, "equivalence_id": "explicit"}) == "explicit::explicit"

    laws = _extract_law_specs([left_query])
    assert laws
    assert {law["law_id"] for law in laws} >= {
        "algebra.flip_left_involution",
        "algebra.set_left_idempotent",
    }


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch is optional in lightweight test environments")
def test_transformer_forward_and_program_composition_shapes() -> None:
    import torch

    config = ModelConfig(
        vocab_size=20,
        num_answers=3,
        num_states=4,
        num_operators=3,
        max_length=12,
        d_model=16,
        n_heads=4,
        n_layers=1,
        d_ff=32,
        representation_dim=8,
        operator_dim=4,
        dropout=0.0,
        arm="combined",
    )
    model = OSLTransformer(config)
    input_ids = torch.randint(1, 20, (2, 12))
    attention_mask = torch.ones_like(input_ids)
    token_types = torch.zeros_like(input_ids)
    program_ids = torch.tensor([[0, 1, 0], [2, 0, 0]])
    program_mask = torch.tensor([[1, 1, 0], [1, 0, 0]], dtype=torch.bool)
    outputs = model(input_ids, attention_mask, token_types, program_ids, program_mask)
    assert outputs["answer_logits"].shape == (2, 3)
    assert outputs["state_logits"].shape == (2, 4)
    assert outputs["representation"].shape == (2, 8)
    assert outputs["program_matrix"].shape == (2, 4, 4)
    assert outputs["program_representation"].shape == (2, 16)
