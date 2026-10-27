from __future__ import annotations

import pytest

from osl_lab.model import TORCH_AVAILABLE, OSLTransformer
from osl_lab.training import (
    TrainingConfig,
    _build_encoders,
    _build_model_config,
    _model_state_digest,
    _ordered_corpus_digest,
    set_deterministic_seed,
)


def test_ordered_corpus_digest_is_deterministic_and_order_sensitive() -> None:
    records = [
        {"id": "first", "answer": "A"},
        {"id": "second", "answer": "B"},
    ]

    digest = _ordered_corpus_digest(records)

    assert len(digest) == 64
    assert digest == _ordered_corpus_digest(records)
    assert digest != _ordered_corpus_digest(list(reversed(records)))


def _central_fixture() -> tuple[list[dict], list[dict], list[dict]]:
    base = [
        {
            "id": "base-a",
            "world": "algebra",
            "story": "Left is lit.",
            "question": "What is left?",
            "answer": "lit",
            "final_state": {"left": True, "right": False},
            "program": [],
        },
        {
            "id": "base-b",
            "world": "resources",
            "story": "No capability remains.",
            "question": "How many remain?",
            "answer": "zero",
            "final_state": {
                "cap": 0,
                "proof": "absent",
                "relay_a": False,
                "relay_b": False,
                "last": "none",
            },
            "program": [],
        },
    ]
    augmented = [base[0]]
    scrambled = [{**base[0], "id": "scrambled", "story": "Calibration is permuted."}]
    return base, augmented, scrambled


def test_central_model_configs_use_one_declared_answer_ontology() -> None:
    base, augmented, scrambled = _central_fixture()
    shared_tokenizer_records = base + augmented + scrambled
    structural_configs = []
    answer_sets = []
    for arm, records in (
        ("answer_only", base),
        ("role_bind_augmented", augmented),
        ("role_bind_scrambled", scrambled),
    ):
        config = TrainingConfig(
            arm=arm,
            max_length=16,
            hash_buckets=8,
            model={"d_model": 16, "n_heads": 4, "n_layers": 1, "d_ff": 32},
        )
        tokenizer, answers, states, operators = _build_encoders(
            records, config, shared_tokenizer_records
        )
        model_config = _build_model_config(config, tokenizer, answers, states, operators)
        answer_sets.append(answers.labels)
        structural_configs.append(
            {key: value for key, value in model_config.to_dict().items() if key != "arm"}
        )
    assert answer_sets[0] == answer_sets[1] == answer_sets[2]
    assert len(answer_sets[0]) == 21
    assert structural_configs[0] == structural_configs[1] == structural_configs[2]


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch is optional in lightweight test environments")
def test_central_models_start_from_byte_identical_parameters() -> None:
    base, augmented, scrambled = _central_fixture()
    shared_tokenizer_records = base + augmented + scrambled
    hashes = []
    for arm, records in (
        ("answer_only", base),
        ("role_bind_augmented", augmented),
        ("role_bind_scrambled", scrambled),
    ):
        config = TrainingConfig(
            arm=arm,
            max_length=16,
            hash_buckets=8,
            model={"d_model": 16, "n_heads": 4, "n_layers": 1, "d_ff": 32},
        )
        tokenizer, answers, states, operators = _build_encoders(
            records, config, shared_tokenizer_records
        )
        set_deterministic_seed(1729)
        model = OSLTransformer(_build_model_config(config, tokenizer, answers, states, operators))
        hashes.append(_model_state_digest(model))
    assert len(set(hashes)) == 1
