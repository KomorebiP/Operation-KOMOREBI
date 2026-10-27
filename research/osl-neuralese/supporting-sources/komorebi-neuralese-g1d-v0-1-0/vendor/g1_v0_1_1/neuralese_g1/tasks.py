from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from typing import Iterable, Sequence


QUERY_TYPES = ("direct", "parity", "codebook")
CODE_SYMBOLS = tuple("ABCDEFJHKM")
ANSWER_CUE = "Answer:\n"
ALLOCATION_MODULUS = 16
IID_SPLIT_RESIDUES = {
    "train": tuple(range(12)),
    "validation": (12, 13),
    "test_iid": (14, 15),
}
REGISTERED_SPLITS = (*IID_SPLIT_RESIDUES, "test_ood_depth")


@dataclass(frozen=True)
class BaseProblem:
    split: str
    counter: int
    permutation: tuple[int, ...]
    start_state: int
    applications: int
    final_state: int
    codebook: tuple[str, ...]
    task_ordinal: int


@dataclass(frozen=True)
class QueryExample:
    example_id: str
    split: str
    counter: int
    query_type: str
    compute_prompt: str
    query_prompt: str
    target_text: str
    final_state: int
    applications: int
    task_ordinal: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def apply_permutation(permutation: Sequence[int], start: int, applications: int) -> int:
    state = int(start)
    for _ in range(int(applications)):
        state = int(permutation[state])
    return state


def _stable_seed(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _unrank_permutation(rank: int, size: int) -> tuple[int, ...]:
    if rank < 0 or rank >= math.factorial(size):
        raise ValueError("permutation rank is outside the registered domain")
    available = list(range(size))
    permutation: list[int] = []
    remainder = int(rank)
    for remaining in range(size, 0, -1):
        block = math.factorial(remaining - 1)
        index, remainder = divmod(remainder, block)
        permutation.append(available.pop(index))
    return tuple(permutation)


def _coprime_multiplier(seed: int, modulus: int) -> int:
    candidate = _stable_seed("g1-affine-multiplier", seed, modulus) % modulus
    if candidate == 0:
        candidate = 1
    while math.gcd(candidate, modulus) != 1:
        candidate = (candidate + 1) % modulus
        if candidate == 0:
            candidate = 1
    return candidate


def _allocation_position(split: str, counter: int) -> int:
    if counter < 0:
        raise ValueError("counter must be nonnegative")
    if split == "test_ood_depth":
        return counter
    if split not in IID_SPLIT_RESIDUES:
        raise ValueError(f"unregistered split: {split}")
    residues = IID_SPLIT_RESIDUES[split]
    block, within = divmod(counter, len(residues))
    return block * ALLOCATION_MODULUS + residues[within]


def _task_ordinal(
    *,
    seed: int,
    split: str,
    counter: int,
    states: int,
    chain_min: int,
    chain_max: int,
) -> tuple[int, int]:
    chain_count = chain_max - chain_min + 1
    domain_size = (math.factorial(states) - 1) * states * chain_count
    position = _allocation_position(split, counter)
    if position >= domain_size:
        raise ValueError(
            f"split {split!r} requests allocation position {position}, but the finite "
            f"task domain contains only {domain_size} positions"
        )
    multiplier = _coprime_multiplier(
        _stable_seed("g1-affine-family", seed, states, chain_min, chain_max),
        domain_size,
    )
    offset = _stable_seed(
        "g1-affine-offset", seed, states, chain_min, chain_max
    ) % domain_size
    return (multiplier * position + offset) % domain_size, domain_size


def make_problem(
    *,
    seed: int,
    split: str,
    counter: int,
    states: int,
    chain_min: int,
    chain_max: int,
) -> BaseProblem:
    if split not in REGISTERED_SPLITS:
        raise ValueError(f"unregistered split: {split}")
    if not 2 <= states <= len(CODE_SYMBOLS):
        raise ValueError(f"states must be from 2 through {len(CODE_SYMBOLS)}")
    if chain_min <= 0 or chain_max < chain_min:
        raise ValueError("invalid chain range")
    ordinal, _domain_size = _task_ordinal(
        seed=seed,
        split=split,
        counter=counter,
        states=states,
        chain_min=chain_min,
        chain_max=chain_max,
    )
    chain_count = chain_max - chain_min + 1
    application_offset = ordinal % chain_count
    quotient = ordinal // chain_count
    start = quotient % states
    nonidentity_permutation_rank = quotient // states
    permutation = _unrank_permutation(nonidentity_permutation_rank + 1, states)
    applications = chain_min + application_offset
    final_state = apply_permutation(permutation, start, applications)
    rng = random.Random(
        _stable_seed("g1-codebook", seed, states, chain_min, chain_max, ordinal)
    )
    symbols = list(CODE_SYMBOLS[:states])
    rng.shuffle(symbols)
    return BaseProblem(
        split=split,
        counter=counter,
        permutation=permutation,
        start_state=start,
        applications=applications,
        final_state=final_state,
        codebook=tuple(symbols),
        task_ordinal=ordinal,
    )


def compute_prompt(problem: BaseProblem) -> str:
    mapping = "; ".join(
        f"{source}->{target}" for source, target in enumerate(problem.permutation)
    )
    return (
        "Finite state task. "
        f"Transition: {mapping}. "
        f"Start at {problem.start_state}. "
        f"Apply the transition exactly {problem.applications} times. "
        "Build and retain the final state internally."
    )


def query_for(problem: BaseProblem, query_type: str) -> tuple[str, str]:
    if query_type == "direct":
        return (
            f"Use the retained state. Answer with its digit only. {ANSWER_CUE}",
            str(problem.final_state),
        )
    if query_type == "parity":
        target = "E" if problem.final_state % 2 == 0 else "O"
        return (
            f"Use the retained state. Answer E for even or O for odd. {ANSWER_CUE}",
            target,
        )
    if query_type == "codebook":
        mapping = "; ".join(
            f"{state}={symbol}" for state, symbol in enumerate(problem.codebook)
        )
        target = problem.codebook[problem.final_state]
        return (
            f"A codebook is now revealed: {mapping}. Use the retained state and answer "
            f"with its code symbol only. {ANSWER_CUE}",
            target,
        )
    raise ValueError(f"unknown query type: {query_type}")


def expand_problem(problem: BaseProblem) -> list[QueryExample]:
    first = compute_prompt(problem)
    examples: list[QueryExample] = []
    for query_type in QUERY_TYPES:
        query, target = query_for(problem, query_type)
        examples.append(
            QueryExample(
                example_id=f"{problem.split}-{problem.counter:07d}-{query_type}",
                split=problem.split,
                counter=problem.counter,
                query_type=query_type,
                compute_prompt=first,
                query_prompt=query,
                target_text=target,
                final_state=problem.final_state,
                applications=problem.applications,
                task_ordinal=problem.task_ordinal,
            )
        )
    return examples


def make_split(
    *,
    seed: int,
    split: str,
    base_problems: int,
    states: int,
    chain_min: int,
    chain_max: int,
) -> list[QueryExample]:
    if base_problems <= 0:
        raise ValueError("base_problems must be positive")
    quotient, remainder = divmod(base_problems, states)
    quotas = {
        state: quotient + (1 if state < remainder else 0) for state in range(states)
    }
    accepted = Counter()
    problems: list[BaseProblem] = []
    raw_counter = 0
    while len(problems) < base_problems:
        problem = make_problem(
            seed=seed,
            split=split,
            counter=raw_counter,
            states=states,
            chain_min=chain_min,
            chain_max=chain_max,
        )
        raw_counter += 1
        if accepted[problem.final_state] >= quotas[problem.final_state]:
            continue
        accepted[problem.final_state] += 1
        problems.append(problem)
    expanded = [example for problem in problems for example in expand_problem(problem)]
    return sorted(expanded, key=lambda item: (QUERY_TYPES.index(item.query_type), item.counter))


def split_digest(examples: Iterable[QueryExample]) -> str:
    digest = hashlib.sha256()
    for example in examples:
        encoded = json.dumps(
            example.as_dict(), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        digest.update(encoded + b"\n")
    return digest.hexdigest()


def find_state_derangement(values: Sequence[int]) -> list[int] | None:
    """Return a bijective donor assignment with a different state for every row."""
    size = len(values)
    if size < 2:
        return None
    counts = Counter(values)
    maximum_count = max(counts.values())
    if maximum_count * 2 > size:
        return None
    ordered = sorted(range(size), key=lambda index: (values[index], index))
    proposal = [-1] * size
    for position, receiver in enumerate(ordered):
        proposal[receiver] = ordered[(position + maximum_count) % size]
    if sorted(proposal) != list(range(size)):
        raise AssertionError("internal derangement construction was not bijective")
    if any(values[index] == values[donor] for index, donor in enumerate(proposal)):
        raise AssertionError("internal derangement construction retained a state match")
    return proposal


def find_query_derangement(examples: Sequence[QueryExample]) -> list[int] | None:
    """Return the registered within-family, answer-incompatible donor bijection."""

    groups: dict[str, list[int]] = defaultdict(list)
    for index, example in enumerate(examples):
        groups[example.query_type].append(index)
    if set(groups) != set(QUERY_TYPES):
        return None
    donors = [-1] * len(examples)
    for query_type in QUERY_TYPES:
        global_indices = groups[query_type]
        values = [
            (
                examples[index].final_state % 2
                if query_type == "parity"
                else examples[index].final_state
            )
            for index in global_indices
        ]
        local_donors = find_state_derangement(values)
        if local_donors is None:
            return None
        for local_receiver, local_donor in enumerate(local_donors):
            donors[global_indices[local_receiver]] = global_indices[local_donor]
    if sorted(donors) != list(range(len(examples))):
        raise AssertionError("query derangement is not a global bijection")
    return donors
