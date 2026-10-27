"""Deterministic corpus generation for the Micro OSL offline laboratory."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import random
import re
from typing import Any, Iterable, Mapping, Sequence

from .renderers import (
    RENDERERS,
    render_answer,
    render_question,
    render_renaming_episode,
    render_trace,
)
from .worlds import (
    WORLDS,
    canonical_json,
    canonical_transformation_id,
    enumerate_states,
    execute,
    get_world,
    query_answers,
)


GENERATOR_VERSION = "0.1.1"
DATASET_SCHEMA_VERSION = "0.1.1"
RENAMING_SCRAMBLED_TRAIN_SPLIT = "renaming_scrambled_train"

TRAINING_SPLITS = (
    "train",
    "renaming_train",
    RENAMING_SCRAMBLED_TRAIN_SPLIT,
)
VALIDATION_SPLITS = ("iid_validation",)
EVALUATION_SPLITS = (
    "iid_test",
    "lexical",
    "heldout_pair",
    "heldout_triple",
    "law",
    "length",
    "counterfactual",
    "renaming",
)
SPLITS = TRAINING_SPLITS + VALIDATION_SPLITS + EVALUATION_SPLITS

DEFAULT_SPLIT_SIZES = {
    "train": 1200,
    "renaming_train": 240,
    "renaming_scrambled_train": 240,
    "iid_validation": 240,
    "iid_test": 240,
    "lexical": 240,
    "heldout_pair": 240,
    "heldout_triple": 240,
    "law": 240,
    "length": 240,
    "counterfactual": 240,
    "renaming": 240,
}


HELDOUT_PAIRS: dict[str, tuple[tuple[str, ...], ...]] = {
    "algebra": (
        ("flip_left", "set_right"),
        ("clear_left", "flip_right"),
    ),
    "provenance": (
        ("observe_a", "imagine_b"),
        ("observe_b", "quarantine_a"),
    ),
    "resources": (
        ("grant_two", "use_cap_a"),
        ("issue_proof", "use_cap_b"),
    ),
}

HELDOUT_TRIPLES: dict[str, tuple[tuple[str, ...], ...]] = {
    "algebra": (
        ("set_left", "flip_right", "flip_left"),
        ("clear_right", "flip_left", "flip_right"),
    ),
    "provenance": (
        ("observe_a", "tell_a_b", "quarantine_b"),
        ("observe_b", "tell_b_a", "endorse_a"),
    ),
    "resources": (
        ("grant_two", "use_cap_a", "use_cap_b"),
        ("issue_proof", "consume_proof_a", "consume_proof_b"),
    ),
}

TRAIN_NONCE_POOL = (
    "dax",
    "wug",
    "zorp",
    "kiv",
    "bem",
    "luf",
    "toma",
    "siv",
    "nex",
    "pav",
    "rilo",
    "gim",
)

EVALUATION_NONCE_POOL = (
    "fep",
    "nib",
    "vos",
    "ral",
    "jek",
    "mup",
    "caz",
    "hod",
    "qen",
    "tiv",
    "bex",
    "sul",
)

TRAIN_SURFACE_MARKER_POOLS = (
    (
        "bavel", "bamel", "banel", "barel", "basel", "batel", "balel", "bakel",
        "davel", "damel", "danel", "darel", "dasel", "datel", "dalel", "dakel",
    ),
    (
        "bovir", "bomir", "bonir", "borir", "bosir", "botir", "bolir", "bokir",
        "dovir", "domir", "donir", "dorir", "dosir", "dotir", "dolir", "dokir",
    ),
)

LEXICAL_SURFACE_MARKER_POOLS = (
    (
        "bevun", "bemun", "benun", "berun", "besun", "betun", "belun", "bekun",
        "devun", "demun", "denun", "derun", "desun", "detun", "delun", "dekun",
    ),
    (
        "bivas", "bimas", "binas", "biras", "bisas", "bitas", "bilas", "bikas",
        "divas", "dimas", "dinas", "diras", "disas", "ditas", "dilas", "dikas",
    ),
)

# Complete public inventory retained for callers that previously imported
# NONCE_POOL. Generation always selects one of the disjoint role-specific pools.
NONCE_POOL = TRAIN_NONCE_POOL + EVALUATION_NONCE_POOL

if set(TRAIN_NONCE_POOL) & set(EVALUATION_NONCE_POOL):
    raise RuntimeError("training and evaluation nonce pools must be disjoint")


def _surface_marker(render_seed: int, lexicon: str) -> dict[str, str]:
    """Return a reusable label-independent alphabetic nuisance marker."""

    if lexicon == "train":
        family = "train"
        first_pool, second_pool = TRAIN_SURFACE_MARKER_POOLS
    elif lexicon == "lexical":
        family = "lexical"
        first_pool, second_pool = LEXICAL_SURFACE_MARKER_POOLS
    else:
        raise ValueError(f"unknown marker lexicon {lexicon!r}")
    digest = sha256(f"surface-marker|{render_seed}|{lexicon}".encode("utf-8")).digest()
    first = first_pool[int.from_bytes(digest[:8], "big") % len(first_pool)]
    second = second_pool[int.from_bytes(digest[8:16], "big") % len(second_pool)]
    return {"family": family, "first": first, "second": second}


@dataclass(frozen=True)
class DatasetConfig:
    """JSON-serializable corpus configuration."""

    seed: int = 1729
    worlds: tuple[str, ...] = ("algebra", "provenance", "resources")
    renderers: tuple[str, ...] = RENDERERS
    split_sizes: Mapping[str, int] = field(
        default_factory=lambda: dict(DEFAULT_SPLIT_SIZES)
    )
    train_min_length: int = 1
    train_max_length: int = 4
    length_test_min: int = 5
    length_test_max: int = 8
    include_formal_fields: bool = True

    def __post_init__(self) -> None:
        unknown_worlds = sorted(set(self.worlds) - set(WORLDS))
        if unknown_worlds:
            raise ValueError(f"unknown worlds: {unknown_worlds}")
        unknown_renderers = sorted(set(self.renderers) - set(RENDERERS))
        if unknown_renderers:
            raise ValueError(f"unknown renderers: {unknown_renderers}")
        unknown_splits = sorted(set(self.split_sizes) - set(SPLITS))
        if unknown_splits:
            raise ValueError(f"unknown splits: {unknown_splits}")
        if not self.worlds or not self.renderers:
            raise ValueError("at least one world and renderer are required")
        if self.train_min_length < 1 or self.train_max_length < self.train_min_length:
            raise ValueError("invalid training length interval")
        if self.length_test_min <= self.train_max_length:
            raise ValueError("length_test_min must exceed train_max_length")
        if self.length_test_max < self.length_test_min:
            raise ValueError("invalid length test interval")
        if any(type(size) is not int or size < 0 for size in self.split_sizes.values()):
            raise ValueError("split sizes must be nonnegative integers")
        if self.split_sizes.get("renaming_train", 0) != self.split_sizes.get(
            "renaming_scrambled_train", 0
        ):
            raise ValueError(
                "renaming_train and renaming_scrambled_train sizes must match"
            )
        if self.split_sizes.get("renaming", 0) % 3:
            raise ValueError("renaming split size must be divisible by three")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DatasetConfig":
        """Build a config from parsed JSON, filling omitted split sizes."""

        payload = dict(data)
        if "worlds" in payload:
            payload["worlds"] = tuple(payload["worlds"])
        if "renderers" in payload:
            payload["renderers"] = tuple(payload["renderers"])
        if "split_sizes" in payload:
            merged = dict(DEFAULT_SPLIT_SIZES)
            merged.update({key: int(value) for key, value in payload["split_sizes"].items()})
            if "renaming_scrambled_train" not in payload["split_sizes"]:
                merged["renaming_scrambled_train"] = merged["renaming_train"]
            payload["split_sizes"] = merged
        return cls(**payload)

    @classmethod
    def from_json(cls, path: str | Path) -> "DatasetConfig":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["worlds"] = list(self.worlds)
        payload["renderers"] = list(self.renderers)
        payload["split_sizes"] = dict(self.split_sizes)
        return payload


def _hash_id(prefix: str, value: Any, length: int = 24) -> str:
    digest = sha256(canonical_json(value).encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}"


def _split_role(split: str) -> str:
    if split in TRAINING_SPLITS:
        return "training"
    if split in VALIDATION_SPLITS:
        return "validation"
    if split in EVALUATION_SPLITS:
        return "evaluation"
    raise ValueError(f"unknown split {split!r}")


def _split_rng(seed: int, split: str) -> random.Random:
    """Give each shard an independent deterministic random stream."""

    material = f"{GENERATOR_VERSION}|{seed}|{split}".encode("utf-8")
    return random.Random(int.from_bytes(sha256(material).digest()[:8], "big"))


def _balanced_strata(
    config: DatasetConfig,
    count: int,
) -> tuple[tuple[str, str, int], ...]:
    """Plan world/query strata with count differences of at most one.

    The third value is the zero-based occurrence within that world. It lets
    callers cycle held-out compositions and laws without coupling to retries.
    """

    occurrences = {world: 0 for world in config.worlds}
    plan: list[tuple[str, str, int]] = []
    for index in range(count):
        world = config.worlds[index % len(config.worlds)]
        occurrence = occurrences[world]
        query_ids = get_world(world).query_ids
        query_id = query_ids[occurrence % len(query_ids)]
        plan.append((world, query_id, occurrence))
        occurrences[world] += 1
    return tuple(plan)


def _rendered_input_key(record: Mapping[str, Any]) -> tuple[str, str]:
    return str(record.get("story", "")), str(record.get("question", ""))


def _contains_subsequence(program: Sequence[str], subsequence: Sequence[str]) -> bool:
    size = len(subsequence)
    if size == 0:
        return True
    return any(tuple(program[index : index + size]) == tuple(subsequence) for index in range(len(program) - size + 1))


def _reserved_transformations(config: DatasetConfig) -> dict[str, set[str]]:
    reserved: dict[str, set[str]] = {world: set() for world in config.worlds}
    for world in config.worlds:
        for program in HELDOUT_PAIRS[world] + HELDOUT_TRIPLES[world]:
            reserved[world].add(canonical_transformation_id(world, program))
    return reserved


def _forbidden_training_pattern(world: str, program: Sequence[str]) -> bool:
    structural = HELDOUT_PAIRS[world] + HELDOUT_TRIPLES[world]
    law_patterns = tuple(
        law.left for law in get_world(world).laws if len(law.left) >= 2
    )
    return any(_contains_subsequence(program, pattern) for pattern in structural + law_patterns)


def _sample_program(
    rng: random.Random,
    world: str,
    minimum: int,
    maximum: int,
) -> tuple[str, ...]:
    length = rng.randint(minimum, maximum)
    operators = get_world(world).operators
    return tuple(rng.choice(operators) for _ in range(length))


def _sample_initial(rng: random.Random, world: str) -> dict[str, Any]:
    return rng.choice(enumerate_states(world))


def _semantic_id(world: str, initial_state: Mapping[str, Any], program: Sequence[str]) -> str:
    return _hash_id(
        "sem",
        {"world": world, "initial_state": dict(initial_state), "program": list(program)},
    )


def _make_record(
    *,
    split: str,
    world: str,
    initial_state: Mapping[str, Any],
    program: Sequence[str],
    query_id: str,
    renderer: str,
    lexicon: str,
    render_seed: int,
    include_formal_fields: bool,
    metadata: Mapping[str, Any] | None = None,
    story_override: str | None = None,
) -> dict[str, Any]:
    execution = execute(world, initial_state, program)
    abstract_answers = query_answers(world, execution.final_state)
    answer = abstract_answers[query_id]
    answer_text = render_answer(world, query_id, answer, lexicon)
    episode_story = story_override or render_trace(
        world, initial_state, program, renderer, lexicon, render_seed
    )
    surface_marker = _surface_marker(render_seed, lexicon)
    story = (
        f"Case markers {surface_marker['first']} and {surface_marker['second']} "
        f"were assigned before review. {episode_story}"
    )
    question = render_question(world, query_id, renderer, lexicon, render_seed)
    semantic_id = _semantic_id(world, initial_state, program)
    transform_id = canonical_transformation_id(world, program)
    record_metadata: dict[str, Any] = {
        "lexicon": lexicon,
        "program_length": len(program),
    }
    if metadata:
        record_metadata.update(dict(metadata))
    record_metadata["split_role"] = _split_role(split)
    record_metadata["surface_marker"] = surface_marker
    identity_payload = {
        "split": split,
        "semantic_id": semantic_id,
        "renderer": renderer,
        "query_id": query_id,
        "story": story,
        "metadata": record_metadata,
    }
    record: dict[str, Any] = {
        "id": _hash_id("rec", identity_payload),
        "split": split,
        "world": world,
        "semantic_id": semantic_id,
        "renderer": renderer,
        "story": story,
        "question_id": query_id,
        "question": question,
        "answer": answer,
        "answer_text": answer_text,
        "metadata": record_metadata,
    }
    if include_formal_fields:
        record.update(
            {
                "initial_state": dict(initial_state),
                "program": [{"op": operator} for operator in program],
                "canonical_transform_id": transform_id,
                "state_trace": [dict(state) for state in execution.states],
                "final_state": dict(execution.final_state),
            }
        )
    return record


def _random_standard_record(
    rng: random.Random,
    config: DatasetConfig,
    split: str,
    reserved: Mapping[str, set[str]],
    lexical: bool = False,
    long: bool = False,
    world: str | None = None,
    query_id: str | None = None,
) -> dict[str, Any] | None:
    selected_world = world or rng.choice(config.worlds)
    if long:
        minimum, maximum = config.length_test_min, config.length_test_max
    else:
        minimum, maximum = config.train_min_length, config.train_max_length
    program = _sample_program(rng, selected_world, minimum, maximum)
    if split == "train":
        if _forbidden_training_pattern(selected_world, program):
            return None
        if canonical_transformation_id(selected_world, program) in reserved[selected_world]:
            return None
    initial = _sample_initial(rng, selected_world)
    renderer = rng.choice(config.renderers)
    selected_query = query_id or rng.choice(get_world(selected_world).query_ids)
    render_seed = rng.getrandbits(63)
    return _make_record(
        split=split,
        world=selected_world,
        initial_state=initial,
        program=program,
        query_id=selected_query,
        renderer=renderer,
        lexicon="lexical" if lexical else "train",
        render_seed=render_seed,
        include_formal_fields=config.include_formal_fields,
        metadata={"evaluation_family": split},
    )


def _heldout_record(
    rng: random.Random,
    config: DatasetConfig,
    split: str,
    world: str,
    query_id: str,
    world_occurrence: int,
) -> dict[str, Any]:
    table = HELDOUT_PAIRS if split == "heldout_pair" else HELDOUT_TRIPLES
    program = table[world][
        (world_occurrence // len(get_world(world).query_ids)) % len(table[world])
    ]
    initial = _sample_initial(rng, world)
    renderer = rng.choice(config.renderers)
    return _make_record(
        split=split,
        world=world,
        initial_state=initial,
        program=program,
        query_id=query_id,
        renderer=renderer,
        lexicon="train",
        render_seed=rng.getrandbits(63),
        include_formal_fields=config.include_formal_fields,
        metadata={
            "evaluation_family": split,
            "heldout_composition": list(program),
        },
    )


def _law_record(
    rng: random.Random,
    config: DatasetConfig,
    world: str,
    query_id: str,
    world_occurrence: int,
) -> dict[str, Any]:
    laws = get_world(world).laws
    law_cycle = world_occurrence // len(get_world(world).query_ids)
    law = laws[law_cycle % len(laws)]
    side = "left" if (law_cycle // len(laws)) % 2 == 0 else "right"
    program = law.left if side == "left" else law.right
    initial = _sample_initial(rng, world)
    renderer = rng.choice(config.renderers)
    return _make_record(
        split="law",
        world=world,
        initial_state=initial,
        program=program,
        query_id=query_id,
        renderer=renderer,
        lexicon="train",
        render_seed=rng.getrandbits(63),
        include_formal_fields=config.include_formal_fields,
        metadata={
            "evaluation_family": "law",
            "law_id": law.law_id,
            "law_kind": law.kind,
            "law_side": side,
            "paired_program": list(law.right if side == "left" else law.left),
        },
    )


def _nonce_mapping(
    rng: random.Random,
    world: str,
    pool: Sequence[str],
) -> dict[str, str]:
    operators = list(get_world(world).operators)
    if len(pool) < len(operators):
        raise ValueError(f"nonce pool is too small for {world}")
    nonces = list(pool)
    rng.shuffle(nonces)
    return dict(zip(operators, nonces[: len(operators)], strict=True))


_STORY_TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]", re.UNICODE)


def _scramble_calibration_labels(
    episode_story: str,
    used_nonces: Sequence[str],
    render_seed: int,
) -> tuple[str, dict[str, str]]:
    """Permute calibration labels while leaving target commands byte-identical."""

    ordered = tuple(dict.fromkeys(str(nonce) for nonce in used_nonces))
    if len(ordered) < 2:
        raise ValueError("scrambled calibration requires at least two distinct nonces")
    shift = 1 + (render_seed % (len(ordered) - 1))
    rotated = ordered[shift:] + ordered[:shift]
    permutation = dict(zip(ordered, rotated, strict=True))
    target_marker = "At the start of the target episode,"
    if target_marker not in episode_story:
        raise ValueError("renaming story lacks target episode marker")
    calibration, target = episode_story.split(target_marker, 1)
    pattern = re.compile(r"\b(?:" + "|".join(map(re.escape, ordered)) + r")\b")
    scrambled_calibration = pattern.sub(lambda match: permutation[match.group(0)], calibration)
    scrambled = scrambled_calibration + target_marker + target
    if sorted(_STORY_TOKEN_PATTERN.findall(episode_story)) != sorted(
        _STORY_TOKEN_PATTERN.findall(scrambled)
    ):
        raise RuntimeError("calibration scrambling changed the story token multiset")
    return scrambled, permutation


def _renaming_training_bundle(
    rng: random.Random,
    config: DatasetConfig,
    episode_index: int,
    reserved: Mapping[str, set[str]],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    world = rng.choice(config.worlds)
    program = _sample_program(
        rng,
        world,
        max(2, config.train_min_length),
        max(2, config.train_max_length),
    )
    if len(set(program)) < 2:
        return None
    if _forbidden_training_pattern(world, program):
        return None
    if canonical_transformation_id(world, program) in reserved[world]:
        return None
    initial = _sample_initial(rng, world)
    operator_to_nonce = _nonce_mapping(rng, world, TRAIN_NONCE_POOL)
    render_seed = rng.getrandbits(63)
    correct_story = render_renaming_episode(
        world,
        initial,
        program,
        operator_to_nonce,
        lexicon="train",
        seed=render_seed,
    )
    query_id = rng.choice(get_world(world).query_ids)
    renderer = rng.choice(config.renderers)
    target_commands = [operator_to_nonce[operator] for operator in program]
    used_nonces = tuple(dict.fromkeys(target_commands))
    scrambled_story, permutation = _scramble_calibration_labels(
        correct_story,
        used_nonces,
        render_seed,
    )
    mapping = {nonce: operator for operator, nonce in operator_to_nonce.items()}
    pair_id = _hash_id(
        "rename_train",
        {
            "episode_index": episode_index,
            "world": world,
            "initial": initial,
            "program": program,
            "query_id": query_id,
            "mapping": mapping,
        },
    )
    shared_metadata = {
        "episode_id": f"train_episode_{episode_index:08d}",
        "pair_id": pair_id,
        "paired_variants": ["correct", "scrambled"],
        "nonce_pool": "training",
        "operator_mapping": mapping,
        "target_commands": target_commands,
        "render_seed": render_seed,
    }
    correct = _make_record(
        split="renaming_train",
        world=world,
        initial_state=initial,
        program=program,
        query_id=query_id,
        renderer=renderer,
        lexicon="train",
        render_seed=render_seed,
        include_formal_fields=config.include_formal_fields,
        story_override=correct_story,
        metadata={
            **shared_metadata,
            "evaluation_family": "renaming_training",
            "variant": "correct",
            "calibration_label_permutation": {
                nonce: nonce for nonce in used_nonces
            },
        },
    )
    scrambled = _make_record(
        split="renaming_scrambled_train",
        world=world,
        initial_state=initial,
        program=program,
        query_id=query_id,
        renderer=renderer,
        lexicon="train",
        render_seed=render_seed,
        include_formal_fields=config.include_formal_fields,
        story_override=scrambled_story,
        metadata={
            **shared_metadata,
            "evaluation_family": "renaming_scrambled_training",
            "variant": "scrambled",
            "calibration_label_permutation": permutation,
        },
    )
    return correct, scrambled


def _renaming_evaluation_bundle(
    rng: random.Random,
    config: DatasetConfig,
    episode_index: int,
    world: str,
    query_id: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    """Return a canonical/correct-renamed/scrambled evaluation triplet."""

    program = _sample_program(
        rng,
        world,
        max(2, config.train_min_length),
        max(2, config.train_max_length),
    )
    if len(set(program)) < 2:
        return None
    initial = _sample_initial(rng, world)
    operator_to_nonce = _nonce_mapping(rng, world, EVALUATION_NONCE_POOL)
    render_seed = rng.getrandbits(63)
    renderer = rng.choice(config.renderers)
    mapping = {nonce: operator for operator, nonce in operator_to_nonce.items()}
    pair_id = _hash_id(
        "rename",
        {
            "episode_index": episode_index,
            "world": world,
            "initial": initial,
            "program": program,
            "query_id": query_id,
            "mapping": mapping,
        },
    )
    shared_metadata = {
        "evaluation_family": "episodic_renaming",
        "episode_id": f"evaluation_episode_{episode_index:08d}",
        "pair_id": pair_id,
        "paired_variants": ["canonical", "renamed", "scrambled"],
        "render_seed": render_seed,
    }
    canonical = _make_record(
        split="renaming",
        world=world,
        initial_state=initial,
        program=program,
        query_id=query_id,
        renderer=renderer,
        lexicon="lexical",
        render_seed=render_seed,
        include_formal_fields=config.include_formal_fields,
        metadata={**shared_metadata, "variant": "canonical"},
    )
    renamed_story = render_renaming_episode(
        world,
        initial,
        program,
        operator_to_nonce,
        lexicon="lexical",
        seed=render_seed,
    )
    target_commands = [operator_to_nonce[operator] for operator in program]
    used_nonces = tuple(dict.fromkeys(target_commands))
    scrambled_story, permutation = _scramble_calibration_labels(
        renamed_story,
        used_nonces,
        render_seed,
    )
    renamed = _make_record(
        split="renaming",
        world=world,
        initial_state=initial,
        program=program,
        query_id=query_id,
        renderer=renderer,
        lexicon="lexical",
        render_seed=render_seed,
        include_formal_fields=config.include_formal_fields,
        story_override=renamed_story,
        metadata={
            **shared_metadata,
            "variant": "renamed",
            "nonce_pool": "evaluation",
            "operator_mapping": mapping,
            "target_commands": target_commands,
            "calibration_label_permutation": {
                nonce: nonce for nonce in used_nonces
            },
        },
    )
    scrambled = _make_record(
        split="renaming",
        world=world,
        initial_state=initial,
        program=program,
        query_id=query_id,
        renderer=renderer,
        lexicon="lexical",
        render_seed=render_seed,
        include_formal_fields=config.include_formal_fields,
        story_override=scrambled_story,
        metadata={
            **shared_metadata,
            "variant": "scrambled",
            "nonce_pool": "evaluation",
            "operator_mapping": mapping,
            "target_commands": target_commands,
            "calibration_label_permutation": permutation,
        },
    )
    return canonical, renamed, scrambled


def _counterfactual_bundle(
    rng: random.Random,
    config: DatasetConfig,
    world: str,
) -> tuple[dict[str, Any], ...]:
    for _ in range(1000):
        program = list(_sample_program(rng, world, 2, max(2, config.train_max_length)))
        intervention_index = rng.randrange(len(program))
        replacements = [op for op in get_world(world).operators if op != program[intervention_index]]
        counterfactual_program = list(program)
        counterfactual_program[intervention_index] = rng.choice(replacements)
        initial = _sample_initial(rng, world)
        base_final = execute(world, initial, program).final_state
        counter_final = execute(world, initial, counterfactual_program).final_state
        base_answers = query_answers(world, base_final)
        counter_answers = query_answers(world, counter_final)
        changed = [key for key in get_world(world).query_ids if base_answers[key] != counter_answers[key]]
        if not changed:
            continue
        renderer = rng.choice(config.renderers)
        render_seed = rng.getrandbits(63)
        pair_payload = {
            "world": world,
            "initial": initial,
            "base": program,
            "counterfactual": counterfactual_program,
            "index": intervention_index,
        }
        pair_id = _hash_id("cf", pair_payload)
        shared_metadata = {
            "evaluation_family": "counterfactual",
            "pair_id": pair_id,
            "intervention_index": intervention_index,
            "changed_query_ids": changed,
            "bundle_query_ids": list(get_world(world).query_ids),
        }
        records: list[dict[str, Any]] = []
        for query_id in get_world(world).query_ids:
            query_metadata = {
                **shared_metadata,
                "query_expected_to_change": query_id in changed,
            }
            records.append(
                _make_record(
                    split="counterfactual",
                    world=world,
                    initial_state=initial,
                    program=program,
                    query_id=query_id,
                    renderer=renderer,
                    lexicon="train",
                    render_seed=render_seed,
                    include_formal_fields=config.include_formal_fields,
                    metadata={**query_metadata, "variant": "base"},
                )
            )
            records.append(
                _make_record(
                    split="counterfactual",
                    world=world,
                    initial_state=initial,
                    program=counterfactual_program,
                    query_id=query_id,
                    renderer=renderer,
                    lexicon="train",
                    render_seed=render_seed,
                    include_formal_fields=config.include_formal_fields,
                    metadata={**query_metadata, "variant": "counterfactual"},
                )
            )
        return tuple(records)
    raise RuntimeError("failed to construct a nontrivial counterfactual bundle")


def _counterfactual_world_plan(config: DatasetConfig, requested_records: int) -> list[str]:
    """Find a record-balanced complete-bundle plan at or above the target."""

    if requested_records <= 0:
        return []
    world_names = tuple(config.worlds)
    bundle_sizes = [2 * len(get_world(world).query_ids) for world in world_names]

    # A nonempty counterfactual test always covers every configured world. The
    # complete-bundle constraint can therefore round small smoke targets up.
    counts = [1] * len(world_names)
    record_counts = list(bundle_sizes)
    while sum(record_counts) < requested_records:
        candidates: list[tuple[int, int, int]] = []
        for index, bundle_size in enumerate(bundle_sizes):
            proposed = list(record_counts)
            proposed[index] += bundle_size
            candidates.append((max(proposed) - min(proposed), max(proposed), index))
        selected = min(candidates)[2]
        counts[selected] += 1
        record_counts[selected] += bundle_sizes[selected]

    remaining = list(counts)
    interleaved: list[str] = []
    while any(remaining):
        for index, world in enumerate(world_names):
            if remaining[index]:
                interleaved.append(world)
                remaining[index] -= 1
    return interleaved


def _append_unique(
    records: list[dict[str, Any]],
    seen: set[str],
    record: dict[str, Any],
) -> bool:
    if record["id"] in seen:
        return False
    seen.add(record["id"])
    records.append(record)
    return True


def _append_clean(
    records: list[dict[str, Any]],
    seen_ids: set[str],
    seen_inputs: set[tuple[str, str]],
    forbidden_inputs: set[tuple[str, str]],
    record: dict[str, Any],
) -> bool:
    key = _rendered_input_key(record)
    if record["id"] in seen_ids or key in seen_inputs or key in forbidden_inputs:
        return False
    seen_ids.add(record["id"])
    seen_inputs.add(key)
    records.append(record)
    return True


def generate_dataset(
    config: DatasetConfig | Mapping[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Generate all requested splits in memory with exact deterministic labels."""

    if config is None:
        resolved = DatasetConfig()
    elif isinstance(config, DatasetConfig):
        resolved = config
    else:
        resolved = DatasetConfig.from_dict(config)
    reserved = _reserved_transformations(resolved)
    dataset: dict[str, list[dict[str, Any]]] = {split: [] for split in SPLITS}

    # Training shards are generated first. Any clean validation or evaluation
    # input that exactly matches any training shard is rejected later.
    train_like_inputs: set[tuple[str, str]] = set()
    train_rng = _split_rng(resolved.seed, "train")
    train_target = int(resolved.split_sizes.get("train", 0))
    train_seen_ids: set[str] = set()
    train_seen_inputs: set[tuple[str, str]] = set()
    attempts = 0
    while len(dataset["train"]) < train_target:
        attempts += 1
        if attempts > max(10000, train_target * 500):
            raise RuntimeError(f"could not generate {train_target} unique records for train")
        record = _random_standard_record(
            train_rng,
            resolved,
            "train",
            reserved,
        )
        if record is None:
            continue
        if _append_clean(
            dataset["train"],
            train_seen_ids,
            train_seen_inputs,
            train_like_inputs,
            record,
        ):
            train_like_inputs.add(_rendered_input_key(record))

    renaming_target = int(resolved.split_sizes.get("renaming_train", 0))
    renaming_rng = _split_rng(resolved.seed, "renaming_train")
    renaming_seen_ids: set[str] = set()
    scrambled_seen_ids: set[str] = set()
    renaming_seen_inputs: set[tuple[str, str]] = set()
    scrambled_seen_inputs: set[tuple[str, str]] = set()
    attempts = 0
    while len(dataset["renaming_train"]) < renaming_target:
        attempts += 1
        if attempts > max(10000, renaming_target * 500):
            raise RuntimeError(
                f"could not generate {renaming_target} matched renaming training pairs"
            )
        bundle = _renaming_training_bundle(
            renaming_rng,
            resolved,
            attempts - 1,
            reserved,
        )
        if bundle is None:
            continue
        correct, scrambled = bundle
        correct_key = _rendered_input_key(correct)
        scrambled_key = _rendered_input_key(scrambled)
        if correct_key == scrambled_key:
            continue
        if correct["id"] in renaming_seen_ids or scrambled["id"] in scrambled_seen_ids:
            continue
        if correct_key in renaming_seen_inputs or scrambled_key in scrambled_seen_inputs:
            continue
        if correct_key in train_like_inputs or scrambled_key in train_like_inputs:
            continue
        renaming_seen_ids.add(correct["id"])
        scrambled_seen_ids.add(scrambled["id"])
        renaming_seen_inputs.add(correct_key)
        scrambled_seen_inputs.add(scrambled_key)
        dataset["renaming_train"].append(correct)
        dataset["renaming_scrambled_train"].append(scrambled)
        train_like_inputs.update((correct_key, scrambled_key))

    # Single-record clean shards use a fixed balanced world/query plan. Retries
    # alter only surface/sample choices, never the assigned stratum.
    protected_inputs = set(train_like_inputs)
    ordinary_clean_splits = tuple(
        split
        for split in VALIDATION_SPLITS + EVALUATION_SPLITS
        if split not in {"counterfactual", "renaming"}
    )
    for split in ordinary_clean_splits:
        rng = _split_rng(resolved.seed, split)
        target = int(resolved.split_sizes.get(split, 0))
        seen_ids: set[str] = set()
        seen_inputs: set[tuple[str, str]] = set()
        for stratum_index, (world, query_id, world_occurrence) in enumerate(
            _balanced_strata(resolved, target)
        ):
            for attempt in range(max(10000, target * 500)):
                if split in {"iid_validation", "iid_test", "lexical", "length"}:
                    record = _random_standard_record(
                        rng,
                        resolved,
                        split,
                        reserved,
                        lexical=split == "lexical",
                        long=split == "length",
                        world=world,
                        query_id=query_id,
                    )
                    if record is None:
                        continue
                elif split in {"heldout_pair", "heldout_triple"}:
                    record = _heldout_record(
                        rng,
                        resolved,
                        split,
                        world,
                        query_id,
                        world_occurrence,
                    )
                elif split == "law":
                    record = _law_record(
                        rng,
                        resolved,
                        world,
                        query_id,
                        world_occurrence,
                    )
                else:  # pragma: no cover - guarded by ordinary_clean_splits
                    raise RuntimeError(f"unhandled clean split {split}")
                if _append_clean(
                    dataset[split],
                    seen_ids,
                    seen_inputs,
                    protected_inputs,
                    record,
                ):
                    protected_inputs.add(_rendered_input_key(record))
                    break
            else:
                raise RuntimeError(
                    f"could not generate clean stratum {stratum_index} for {split}"
                )

    requested_counterfactual = int(resolved.split_sizes.get("counterfactual", 0))
    counterfactual_plan = _counterfactual_world_plan(resolved, requested_counterfactual)
    counterfactual_rng = _split_rng(resolved.seed, "counterfactual")
    seen_counterfactual: set[str] = set()
    seen_pair_ids: set[str] = set()
    for world in counterfactual_plan:
        for _ in range(max(10000, requested_counterfactual * 500)):
            bundle = _counterfactual_bundle(counterfactual_rng, resolved, world)
            pair_id = str(bundle[0]["metadata"]["pair_id"])
            if pair_id in seen_pair_ids:
                continue
            if any(record["id"] in seen_counterfactual for record in bundle):
                continue
            bundle_inputs = [_rendered_input_key(record) for record in bundle]
            if len(set(bundle_inputs)) != len(bundle_inputs):
                continue
            if any(key in protected_inputs for key in bundle_inputs):
                continue
            seen_pair_ids.add(pair_id)
            for record in bundle:
                _append_unique(dataset["counterfactual"], seen_counterfactual, record)
                protected_inputs.add(_rendered_input_key(record))
            break
        else:
            raise RuntimeError("could not generate a clean counterfactual bundle")

    requested_renaming = int(resolved.split_sizes.get("renaming", 0))
    renaming_bundle_count = requested_renaming // 3
    renaming_rng = _split_rng(resolved.seed, "renaming")
    seen_renaming: set[str] = set()
    seen_renaming_pairs: set[str] = set()
    for episode_index, (world, query_id, _) in enumerate(
        _balanced_strata(resolved, renaming_bundle_count)
    ):
        for retry in range(max(10000, requested_renaming * 500)):
            bundle = _renaming_evaluation_bundle(
                renaming_rng,
                resolved,
                episode_index + retry * max(1, renaming_bundle_count),
                world,
                query_id,
            )
            if bundle is None:
                continue
            pair_id = str(bundle[0]["metadata"]["pair_id"])
            bundle_inputs = [_rendered_input_key(record) for record in bundle]
            if pair_id in seen_renaming_pairs:
                continue
            if any(record["id"] in seen_renaming for record in bundle):
                continue
            if len(set(bundle_inputs)) != 3 or any(
                key in protected_inputs for key in bundle_inputs
            ):
                continue
            seen_renaming_pairs.add(pair_id)
            for record in bundle:
                _append_unique(dataset["renaming"], seen_renaming, record)
                protected_inputs.add(_rendered_input_key(record))
            break
        else:
            raise RuntimeError("could not generate a clean renaming pair")

    return dataset


def dataset_digest(records: Iterable[Mapping[str, Any]]) -> str:
    """Hash semantic/protocol content independently of surface realization."""

    digest = sha256()
    for record in records:
        projection = {
            key: value
            for key, value in record.items()
            if key not in {"id", "renderer", "story", "question", "answer_text"}
        }
        metadata = projection.get("metadata")
        if isinstance(metadata, Mapping):
            projection["metadata"] = {
                key: value
                for key, value in metadata.items()
                if key not in {"lexicon", "renderer", "render_seed", "surface_marker"}
            }
        digest.update(canonical_json(projection).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def write_dataset(
    output_dir: str | Path,
    config: DatasetConfig | Mapping[str, Any] | None = None,
    dataset: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Write JSONL shards plus a reproducibility manifest."""

    if config is None:
        resolved = DatasetConfig()
    elif isinstance(config, DatasetConfig):
        resolved = config
    else:
        resolved = DatasetConfig.from_dict(config)
    generated = generate_dataset(resolved) if dataset is None else {
        split: [dict(record) for record in records] for split, records in dataset.items()
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    files: dict[str, Any] = {}
    for split in SPLITS:
        records = generated.get(split, [])
        path = destination / f"{split}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(canonical_json(record) + "\n")
        files[split] = {
            "path": path.name,
            "records": len(records),
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "semantic_sha256": dataset_digest(records),
        }
    manifest = {
        "format": "micro-osl-jsonl-v1.1",
        "schema_version": DATASET_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "config": resolved.to_dict(),
        "files": files,
    }
    manifest_path = destination / "manifest.json"
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def load_dataset(directory: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Load every known JSONL split found in ``directory``."""

    root = Path(directory)
    dataset: dict[str, list[dict[str, Any]]] = {}
    for split in SPLITS:
        path = root / f"{split}.jsonl"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            dataset[split] = [json.loads(line) for line in handle if line.strip()]
    return dataset


__all__ = [
    "DATASET_SCHEMA_VERSION",
    "DEFAULT_SPLIT_SIZES",
    "EVALUATION_NONCE_POOL",
    "EVALUATION_SPLITS",
    "GENERATOR_VERSION",
    "HELDOUT_PAIRS",
    "HELDOUT_TRIPLES",
    "LEXICAL_SURFACE_MARKER_POOLS",
    "NONCE_POOL",
    "RENAMING_SCRAMBLED_TRAIN_SPLIT",
    "SPLITS",
    "TRAINING_SPLITS",
    "TRAIN_NONCE_POOL",
    "TRAIN_SURFACE_MARKER_POOLS",
    "VALIDATION_SPLITS",
    "DatasetConfig",
    "dataset_digest",
    "generate_dataset",
    "load_dataset",
    "write_dataset",
]
