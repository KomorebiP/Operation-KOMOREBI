from __future__ import annotations

from typing import Any, Sequence

from .tasks import ANSWER_CUE, QueryExample


def target_token_id(tokenizer: Any, target_text: str) -> int:
    if not target_text or target_text != target_text.strip():
        raise ValueError(
            f"registered target {target_text!r} must be a bare non-whitespace label"
        )
    identifiers = tokenizer.encode(target_text, add_special_tokens=False)
    if len(identifiers) != 1:
        raise ValueError(
            f"registered target {target_text!r} is {len(identifiers)} tokens rather than one"
        )
    return int(identifiers[0])


def validate_single_token_targets(
    tokenizer: Any, examples: Sequence[QueryExample]
) -> dict[str, int]:
    targets = sorted({example.target_text for example in examples})
    result = {target: target_token_id(tokenizer, target) for target in targets}
    if len(set(result.values())) != len(result):
        raise ValueError("two registered target strings resolve to the same token ID")
    special_ids = {int(value) for value in getattr(tokenizer, "all_special_ids", [])}
    if any(identifier in special_ids for identifier in result.values()):
        raise ValueError("a registered target resolves to a tokenizer special token")
    for target, identifier in result.items():
        decoded = tokenizer.decode(
            [identifier],
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        )
        if decoded != target:
            raise ValueError(
                f"registered target {target!r} does not round-trip exactly; decoded={decoded!r}"
            )
    checked_pairs: set[tuple[str, str]] = set()
    for example in examples:
        pair = (example.query_prompt, example.target_text)
        if pair in checked_pairs:
            continue
        checked_pairs.add(pair)
        if not example.query_prompt.endswith(ANSWER_CUE):
            raise ValueError(
                f"query {example.example_id} does not end with the registered answer cue"
            )
        prefix = list(tokenizer.encode(example.query_prompt, add_special_tokens=True))
        joint = list(
            tokenizer.encode(
                example.query_prompt + example.target_text,
                add_special_tokens=True,
            )
        )
        expected = [*prefix, result[example.target_text]]
        if joint != expected:
            raise ValueError(
                "tokenizer continuation boundary is not one-token stable for "
                f"{example.example_id}: prompt_tokens={len(prefix)}, "
                f"joint_tokens={len(joint)}"
            )
    return result
