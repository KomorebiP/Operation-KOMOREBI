"""Deterministic D4 endpoint-matched word-bank construction.

This is a combinatorial prototype.  It does not load or evaluate learned
checkpoints.  The registered reference families are the repeated D4 relators
used by the v0.3.0 audit, restricted to token budgets 16, 32, and 64.

For each reference word, the dynamic program globally minimizes the first
three scientific exposure coordinates and globally applies the final two
deterministic tie-breaks for each endpoint allowed by word-length parity

    (generator-count L1, directed-bigram-count L1,
     run-second-moment error, Hamming distance, binary lexical order).

The identity endpoint is constrained to differ from the reference word.  The
four parity-complement endpoints can only be supplied in a separately frozen
B-1/B+1 "sandwich" because exact same-length controls for them are
mathematically impossible; that secondary panel is not materialized here.  The
first three score coordinates are the scientific matching objective. Hamming
and lexical order globally resolve ties to make the choice deterministic.

The dynamic program is exact for the registered reference families because
their run second moments are extremal: n**2 for a constant word and n for an
alternating word.  Conditional on a sufficient automaton state, maximizing or
minimizing accumulated squared run length is therefore monotone and admits
safe dominance pruning.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable


SCHEMA = "komorebi.neuralese.matched_control_word_bank.v2"
GENERATOR_NAMES = ("R", "F")
BUDGETS = (16, 32, 64)
RELATION_WORDS: dict[str, tuple[int, ...]] = {
    "r4": (0, 0, 0, 0),
    "f2": (1, 1),
    "frfr": (1, 0, 1, 0),
    "rfrf": (0, 1, 0, 1),
}

_R = tuple(4 * (i // 4) + ((i % 4 + 1) % 4) for i in range(8))
_F = tuple(4 * (1 - i // 4) + ((-(i % 4)) % 4) for i in range(8))
_MAPS = (_R, _F)

# Names follow token order, not an unstated left/right multiplication convention.
ENDPOINT_REPRESENTATIVE_WORDS: tuple[tuple[int, ...], ...] = (
    (),
    (0,),
    (0, 0),
    (0, 0, 0),
    (1,),
    (1, 0),
    (1, 0, 0),
    (1, 0, 0, 0),
)
ENDPOINT_NAMES = ("e", "R", "R2", "R3", "F", "FR", "FR2", "FR3")


@dataclass(frozen=True)
class WordFeatures:
    length: int
    generator_counts: tuple[int, int]
    directed_bigram_counts: tuple[int, int, int, int]
    run_lengths: tuple[tuple[int, int], ...]
    run_second_moment: int
    maximum_run_length: int


@dataclass(frozen=True)
class _Partial:
    closed_run_second_moment: int
    hamming_distance: int
    bits: int


def _apply_map(mapping: tuple[int, ...], action: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(mapping[value] for value in action)


def word_action(word: Iterable[int]) -> tuple[int, ...]:
    """Return the exact permutation induced by a canonical R/F token word."""

    action = tuple(range(8))
    for token in word:
        if token not in (0, 1):
            raise ValueError("D4 word contains a non-binary generator")
        action = _apply_map(_MAPS[int(token)], action)
    return action


_ENDPOINT_ACTIONS = tuple(word_action(word) for word in ENDPOINT_REPRESENTATIVE_WORDS)
if len(set(_ENDPOINT_ACTIONS)) != 8:
    raise ArithmeticError("D4 endpoint representatives are not distinct")
_ACTION_TO_ENDPOINT = {action: index for index, action in enumerate(_ENDPOINT_ACTIONS)}


def endpoint_index(word: Iterable[int]) -> int:
    return _ACTION_TO_ENDPOINT[word_action(word)]


def endpoint_name(word: Iterable[int]) -> str:
    return ENDPOINT_NAMES[endpoint_index(word)]


_ENDPOINT_TRANSITION = tuple(
    tuple(
        endpoint_index(ENDPOINT_REPRESENTATIVE_WORDS[endpoint] + (token,))
        for token in (0, 1)
    )
    for endpoint in range(8)
)

_CONTROL_CACHE: dict[tuple[tuple[int, ...], bool], dict[int, dict[str, object]]] = {}


def reference_word(relation: str, budget: int) -> tuple[int, ...]:
    if relation not in RELATION_WORDS:
        raise ValueError(f"unknown relation: {relation}")
    if budget not in BUDGETS:
        raise ValueError(f"unregistered matched-control budget: {budget}")
    relator = RELATION_WORDS[relation]
    if budget % len(relator):
        raise ValueError("budget is not divisible by relation length")
    word = periodic_template(relation, budget)
    if endpoint_index(word) != 0:
        raise ArithmeticError("registered reference word is not a D4 identity")
    return word


def periodic_template(relation: str, length: int) -> tuple[int, ...]:
    """Return the exact prefix of the infinitely repeated relation template."""

    if relation not in RELATION_WORDS:
        raise ValueError(f"unknown relation: {relation}")
    if length <= 0:
        raise ValueError("template length must be positive")
    relator = RELATION_WORDS[relation]
    repeats, remainder = divmod(length, len(relator))
    return relator * repeats + relator[:remainder]


def word_features(word: Iterable[int]) -> WordFeatures:
    sequence = tuple(int(token) for token in word)
    if not sequence:
        return WordFeatures(0, (0, 0), (0, 0, 0, 0), (), 0, 0)
    if any(token not in (0, 1) for token in sequence):
        raise ValueError("word contains a non-binary generator")

    counts = (sequence.count(0), sequence.count(1))
    bigrams = [0, 0, 0, 0]
    for left, right in zip(sequence, sequence[1:]):
        bigrams[2 * left + right] += 1

    runs: list[tuple[int, int]] = []
    current = sequence[0]
    length = 1
    for token in sequence[1:]:
        if token == current:
            length += 1
        else:
            runs.append((current, length))
            current = token
            length = 1
    runs.append((current, length))
    return WordFeatures(
        length=len(sequence),
        generator_counts=counts,
        directed_bigram_counts=tuple(bigrams),
        run_lengths=tuple(runs),
        run_second_moment=sum(length * length for _, length in runs),
        maximum_run_length=max(length for _, length in runs),
    )


def exposure_score(reference: Iterable[int], candidate: Iterable[int]) -> tuple[int, ...]:
    """Return the frozen total ordering used to select a control word."""

    ref = tuple(reference)
    control = tuple(candidate)
    if len(ref) != len(control):
        raise ValueError("reference and control lengths differ")
    ref_features = word_features(ref)
    control_features = word_features(control)
    generator_l1 = sum(
        abs(left - right)
        for left, right in zip(
            ref_features.generator_counts, control_features.generator_counts
        )
    )
    bigram_l1 = sum(
        abs(left - right)
        for left, right in zip(
            ref_features.directed_bigram_counts,
            control_features.directed_bigram_counts,
        )
    )
    run_second_moment_error = abs(
        ref_features.run_second_moment - control_features.run_second_moment
    )
    hamming = sum(left != right for left, right in zip(ref, control))
    lexical_integer = bits_to_integer(control)
    return (
        int(generator_l1),
        int(bigram_l1),
        int(run_second_moment_error),
        int(hamming),
        int(lexical_integer),
    )


def bits_to_integer(word: Iterable[int]) -> int:
    value = 0
    for token in word:
        if token not in (0, 1):
            raise ValueError("word contains a non-binary generator")
        value = (value << 1) | int(token)
    return value


def integer_to_bits(value: int, length: int) -> tuple[int, ...]:
    if length < 0 or value < 0 or value >= (1 << length):
        raise ValueError("integer is outside the requested binary shell")
    return tuple((value >> shift) & 1 for shift in range(length - 1, -1, -1))


def _mode_for_reference(reference: tuple[int, ...]) -> str:
    features = word_features(reference)
    length = len(reference)
    if features.run_second_moment == length * length:
        return "maximize"
    if features.run_second_moment == length:
        return "minimize"
    raise ValueError(
        "exact dominance proof currently covers only constant or alternating references"
    )


def _partial_key(partial: _Partial, mode: str) -> tuple[int, int, int]:
    directional_moment = (
        -partial.closed_run_second_moment
        if mode == "maximize"
        else partial.closed_run_second_moment
    )
    return directional_moment, partial.hamming_distance, partial.bits


def _insert_best(
    destination: dict[tuple[int, ...], _Partial],
    key: tuple[int, ...],
    candidate: _Partial,
    mode: str,
) -> None:
    incumbent = destination.get(key)
    if incumbent is None or _partial_key(candidate, mode) < _partial_key(
        incumbent, mode
    ):
        destination[key] = candidate


def best_control(
    reference: Iterable[int],
    target_endpoint: int,
    *,
    exclude_reference_when_same_endpoint: bool = True,
) -> dict[str, object]:
    """Construct the exact exposure-optimal word for one D4 endpoint.

    A reference already having the requested endpoint is excluded by a
    prefix-difference automaton bit.
    A compact certificate reports the complete final-state candidate count and
    the selected score.  Exhaustive small-n tests validate the dominance rule.
    """

    ref = tuple(int(token) for token in reference)
    if not ref:
        raise ValueError("matched controls require a positive word length")
    if any(token not in (0, 1) for token in ref):
        raise ValueError("reference contains a non-binary generator")
    if target_endpoint not in range(8):
        raise ValueError("target_endpoint must be in range(8)")
    mode = _mode_for_reference(ref)
    length = len(ref)
    cache_key = (ref, bool(exclude_reference_when_same_endpoint))
    cached = _CONTROL_CACHE.get(cache_key)
    if cached is not None:
        if target_endpoint not in cached:
            raise ArithmeticError(
                "requested endpoint is unreachable at this exact word-length parity"
            )
        return cached[target_endpoint]

    # State: endpoint, first token, last token, number of F tokens,
    # transition count, current run length, differs-from-reference flag.
    frontier: dict[tuple[int, ...], _Partial] = {}
    for token in (0, 1):
        key = (
            _ENDPOINT_TRANSITION[0][token],
            token,
            token,
            token,
            0,
            1,
            int(token != ref[0]),
        )
        _insert_best(
            frontier,
            key,
            _Partial(0, int(token != ref[0]), token),
            mode,
        )

    peak_state_count = len(frontier)
    for position in range(1, length):
        next_frontier: dict[tuple[int, ...], _Partial] = {}
        for key, partial in frontier.items():
            endpoint, first, last, ones, transitions, current_run, differs = key
            for token in (0, 1):
                changed = token != last
                next_run = 1 if changed else current_run + 1
                closed_increment = current_run * current_run if changed else 0
                next_key = (
                    _ENDPOINT_TRANSITION[endpoint][token],
                    first,
                    token,
                    ones + token,
                    transitions + int(changed),
                    next_run,
                    int(bool(differs) or token != ref[position]),
                )
                candidate = _Partial(
                    partial.closed_run_second_moment + closed_increment,
                    partial.hamming_distance + int(token != ref[position]),
                    (partial.bits << 1) | token,
                )
                _insert_best(next_frontier, next_key, candidate, mode)
        frontier = next_frontier
        peak_state_count = max(peak_state_count, len(frontier))

    ref_features = word_features(ref)
    results: dict[int, dict[str, object]] = {}
    reference_endpoint = endpoint_index(ref)
    for requested_endpoint in range(8):
        candidates: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
        for key, partial in frontier.items():
            endpoint, _first, _last, _ones, _transitions, _current_run, differs = key
            if endpoint != requested_endpoint:
                continue
            if (
                exclude_reference_when_same_endpoint
                and requested_endpoint == reference_endpoint
                and not differs
            ):
                continue
            word = integer_to_bits(partial.bits, length)
            candidates.append((exposure_score(ref, word), word))
        if not candidates:
            continue
        score, selected = min(candidates, key=lambda item: (item[0], item[1]))
        features = word_features(selected)
        results[requested_endpoint] = {
            "target_endpoint_index": int(requested_endpoint),
            "target_endpoint_name": ENDPOINT_NAMES[requested_endpoint],
            "target_representative_word": list(
                ENDPOINT_REPRESENTATIVE_WORDS[requested_endpoint]
            ),
            "word": list(selected),
            "word_binary": "".join(str(token) for token in selected),
            "endpoint_verified": endpoint_index(selected) == requested_endpoint,
            "distinct_from_reference": selected != ref,
            "features": asdict(features),
            "matching": {
                "score_fields": [
                    "generator_count_l1",
                    "directed_bigram_count_l1",
                    "run_second_moment_absolute_error",
                    "hamming_distance_tiebreak",
                    "binary_lexical_tiebreak",
                ],
                "score": list(score),
                "exact_generator_counts": (
                    features.generator_counts == ref_features.generator_counts
                ),
                "exact_directed_bigram_counts": (
                    features.directed_bigram_counts
                    == ref_features.directed_bigram_counts
                ),
                "exact_run_second_moment": (
                    features.run_second_moment == ref_features.run_second_moment
                ),
            },
            "optimality_certificate": {
                "algorithm": "exact_dynamic_program_extremal_run_moment_v1",
                "reference_run_mode": mode,
                "final_candidate_state_count": len(candidates),
                "peak_dynamic_program_state_count": peak_state_count,
                "globally_optimal_first_three_score_coordinates": True,
                "globally_optimal_complete_lexicographic_score": True,
            },
        }
    _CONTROL_CACHE[cache_key] = results
    if target_endpoint not in results:
        raise ArithmeticError(
            "requested endpoint is unreachable at this exact word-length parity"
        )
    return results[target_endpoint]


def build_word_bank(*, include_parity_sandwich: bool = False) -> dict[str, object]:
    records: list[dict[str, object]] = []
    for relation in RELATION_WORDS:
        for budget in BUDGETS:
            reference = reference_word(relation, budget)
            reference_features = word_features(reference)
            exact_reachable_endpoints = [
                endpoint
                for endpoint, representative in enumerate(
                    ENDPOINT_REPRESENTATIVE_WORDS
                )
                if len(representative) % 2 == budget % 2
            ]
            parity_complement_endpoints = [
                endpoint
                for endpoint in range(8)
                if endpoint not in exact_reachable_endpoints
            ]
            exact_controls = [
                best_control(reference, endpoint)
                for endpoint in exact_reachable_endpoints
            ]
            if {tuple(control["word"]) for control in exact_controls} & {reference}:
                raise ArithmeticError("word bank contains its excluded reference")
            if len(exact_reachable_endpoints) != 4:
                raise ArithmeticError("D4 word-length parity class is not size four")

            parity_sandwich: list[dict[str, object]] = []
            if include_parity_sandwich:
                for endpoint in parity_complement_endpoints:
                    lower_template = periodic_template(relation, budget - 1)
                    upper_template = periodic_template(relation, budget + 1)
                    lower = best_control(lower_template, endpoint)
                    upper = best_control(upper_template, endpoint)
                    parity_sandwich.append(
                        {
                            "target_endpoint_index": endpoint,
                            "target_endpoint_name": ENDPOINT_NAMES[endpoint],
                            "lower_length": budget - 1,
                            "upper_length": budget + 1,
                            "mean_length": budget,
                            "lower_template_word": list(lower_template),
                            "upper_template_word": list(upper_template),
                            "lower_control": lower,
                            "upper_control": upper,
                        }
                    )
            records.append(
                {
                    "relation": relation,
                    "budget": budget,
                    "reference_word": list(reference),
                    "reference_word_binary": "".join(str(token) for token in reference),
                    "reference_endpoint": ENDPOINT_NAMES[endpoint_index(reference)],
                    "reference_features": asdict(reference_features),
                    "exact_length_reachable_endpoint_indices": exact_reachable_endpoints,
                    "exact_length_reachable_endpoint_names": [
                        ENDPOINT_NAMES[index] for index in exact_reachable_endpoints
                    ],
                    "exact_length_controls": exact_controls,
                    "parity_complement_endpoint_indices": parity_complement_endpoints,
                    "parity_complement_endpoint_names": [
                        ENDPOINT_NAMES[index] for index in parity_complement_endpoints
                    ],
                    "parity_sandwich_controls": parity_sandwich,
                }
            )

    condition_words = [
        tuple(record["reference_word"])
        for record in records
    ] + [
        tuple(control["word"])
        for record in records
        for control in record["exact_length_controls"]
    ]
    identity_pairs = {
        tuple(
            sorted(
                (
                    tuple(record["reference_word"]),
                    tuple(
                        next(
                            control
                            for control in record["exact_length_controls"]
                            if control["target_endpoint_index"] == 0
                        )["word"]
                    ),
                )
            )
        )
        for record in records
    }
    if len(condition_words) != 60 or len(set(condition_words)) != 54:
        raise ArithmeticError("registered matched condition alias structure changed")
    if len(identity_pairs) != 9:
        raise ArithmeticError("registered identity-pair alias structure changed")

    bank: dict[str, object] = {
        "schema": SCHEMA,
        "version": "0.3.1",
        "author": "Komorebi P.",
        "scientific_status": "combinatorial_word_bank_only_no_learned_execution",
        "canonical_generators": {"0": "R", "1": "F"},
        "endpoint_names_in_token_order": list(ENDPOINT_NAMES),
        "endpoint_representative_words": [
            list(word) for word in ENDPOINT_REPRESENTATIVE_WORDS
        ],
        "budgets": list(BUDGETS),
        "relations": {name: list(word) for name, word in RELATION_WORDS.items()},
        "word_length_parity_obstruction": {
            "statement": (
                "Every D4 defining relation over R,F has even length, so word "
                "length parity is invariant. An even budget reaches exactly four "
                "of eight endpoints. Same-length controls for all endpoints do not exist."
            ),
            "primary_panel": (
                "reference plus the four exactly length-matched even-parity endpoints"
            ),
            "secondary_panel": (
                "the four odd-parity endpoints evaluated at both B-1 and B+1; "
                "this is a parity-sandwich sensitivity analysis, not exact length matching"
            ),
        },
        "matching_objective": {
            "ordering": "lexicographic",
            "coordinates": [
                "generator-count L1",
                "directed-bigram-count L1 in 00,01,10,11 order",
                "absolute run-second-moment error",
                "Hamming-distance deterministic tiebreak",
                "binary-lexical deterministic tiebreak",
            ],
            "same_endpoint_constraint": (
                "a control must differ when its matching template already has the "
                "requested endpoint"
            ),
            "optimality_scope": (
                "global over all binary words of the fixed length and requested D4 "
                "endpoint under the complete five-coordinate lexicographic ordering; "
                "the first three coordinates define scientific exposure matching, "
                "while Hamming distance and binary lexical order are deterministic "
                "tie-breaks"
            ),
        },
        "record_count": len(records),
        "exact_length_control_word_count": len(records) * 4,
        "parity_sandwich_control_word_count": (
            len(records) * 4 * 2 if include_parity_sandwich else 0
        ),
        "parity_sandwich_materialized": bool(include_parity_sandwich),
        "control_word_count": len(records) * (12 if include_parity_sandwich else 4),
        "condition_count": len(condition_words),
        "condition_word_entry_count": len(condition_words),
        "distinct_word_count": len(set(condition_words)),
        "directed_reference_identity_comparison_count": len(records),
        "reused_condition_alias_count": len(condition_words) - len(set(condition_words)),
        "unique_unordered_reference_identity_pair_count": len(identity_pairs),
        "identity_pair_alias_structure": (
            "At each budget 16, 32, and 64, the frfr reference is the rfrf "
            "identity control and the rfrf reference is the frfr identity control. "
            "Thus six condition aliases reuse another condition's word and the two "
            "directed cells encode one unordered identity-path comparison per budget."
        ),
        "records": records,
    }
    canonical = json.dumps(bank, sort_keys=True, separators=(",", ":")).encode()
    bank["content_sha256_without_this_field"] = hashlib.sha256(canonical).hexdigest()
    return bank


def write_word_bank(path: Path) -> dict[str, object]:
    bank = build_word_bank()
    payload = json.dumps(bank, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.write_text(payload, encoding="utf-8")
    return bank


__all__ = [
    "BUDGETS",
    "ENDPOINT_NAMES",
    "ENDPOINT_REPRESENTATIVE_WORDS",
    "GENERATOR_NAMES",
    "RELATION_WORDS",
    "SCHEMA",
    "best_control",
    "bits_to_integer",
    "build_word_bank",
    "endpoint_index",
    "endpoint_name",
    "exposure_score",
    "integer_to_bits",
    "periodic_template",
    "reference_word",
    "word_action",
    "word_features",
    "write_word_bank",
]
