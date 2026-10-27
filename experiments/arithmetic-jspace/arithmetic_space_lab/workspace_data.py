"""Deterministic structural arithmetic streams and matched control targets.

The workspace experiments need training data whose arithmetic structure can be
varied without quietly changing superficial properties of the target strings.
This module therefore keeps generation counter based, records carry/borrow
structure explicitly, and implements controls independently of model code.

The random-label control is ordinarily a *value* derangement, not merely a
permutation of rows. Targets are shuffled with a seeded RNG inside nuisance
strata and every assigned completion is checked to differ from the source
completion. No numeric sorting is used by the construction. A separately
reported, hard-capped synthetic-label fallback exists only for tiny width-only
strata whose empirical multiplicities make any value derangement impossible.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, OrderedDict, defaultdict
from dataclasses import asdict, dataclass, replace
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence

from .core import borrow_features, carry_features, seeded_rng, stable_hash


SUPPORTED_OPERATIONS = ("add", "sub")
SUPPORTED_STRUCTURES = ("balanced", "no_event", "event", "chain")
SUPPORTED_ARMS = ("correct", "no_carry", "pseudo_fst", "deranged")
FAMILY_PARTITIONS = 16
SYNTHETIC_DERANGEMENT_MAX_ROWS = 31
SYNTHETIC_DERANGEMENT_MAX_FRACTION = 0.001


@dataclass(frozen=True)
class StreamConfig:
    """Configuration for a counter-addressable arithmetic stream."""

    seed: int = 314159
    namespace: str = "arithmetic-workspace-v1"
    split: str = "train"
    min_digits: int = 1
    max_digits: int = 8
    operations: tuple[str, ...] = SUPPORTED_OPERATIONS
    structure_cycle: tuple[str, ...] = ("no_event", "event", "chain", "balanced")
    prompt_template: str = "{left}{symbol}{right}="
    add_symbol: str = "+"
    sub_symbol: str = "-"
    pseudo_seed: int = 271828
    pseudo_states: int = 4
    derangement_window: int = 512
    max_rejection_attempts: int = 4096
    carry_chain_min: int = 0
    carry_chain_max: int | None = None
    borrow_chain_min: int = 0
    borrow_chain_max: int | None = None
    derangement_max_abs_pearson: float | None = None
    derangement_max_prefix_excess: float | None = None
    derangement_max_suffix_excess: float | None = None

    def __post_init__(self) -> None:
        if not self.namespace.strip() or not self.split.strip():
            raise ValueError("namespace and split must be nonblank")
        if self.min_digits < 1 or self.max_digits < self.min_digits:
            raise ValueError("digit bounds must satisfy 1 <= min_digits <= max_digits")
        if self.max_digits > 64:
            raise ValueError("max_digits above 64 is unsupported by the structural sampler")
        if not self.operations or any(item not in SUPPORTED_OPERATIONS for item in self.operations):
            raise ValueError(f"operations must be drawn from {SUPPORTED_OPERATIONS}")
        if not self.structure_cycle or any(
            item not in SUPPORTED_STRUCTURES for item in self.structure_cycle
        ):
            raise ValueError(f"structure_cycle must be drawn from {SUPPORTED_STRUCTURES}")
        if "{left}" not in self.prompt_template or "{right}" not in self.prompt_template:
            raise ValueError("prompt_template must contain {left} and {right}")
        if not self.add_symbol or not self.sub_symbol:
            raise ValueError("operator symbols must be nonblank")
        if self.derangement_window < 8:
            raise ValueError("derangement_window must be at least 8")
        if self.pseudo_states < 2:
            raise ValueError("pseudo_states must be at least 2")
        if self.max_rejection_attempts < 1:
            raise ValueError("max_rejection_attempts must be positive")
        for prefix in ("carry", "borrow"):
            minimum_chain = int(getattr(self, f"{prefix}_chain_min"))
            maximum_chain = getattr(self, f"{prefix}_chain_max")
            if minimum_chain < 0 or (maximum_chain is not None and maximum_chain < minimum_chain):
                raise ValueError(f"invalid {prefix} chain bounds")
        for name in (
            "derangement_max_abs_pearson",
            "derangement_max_prefix_excess",
            "derangement_max_suffix_excess",
        ):
            threshold = getattr(self, name)
            if threshold is not None and threshold < 0:
                raise ValueError(f"{name} must be nonnegative when configured")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "StreamConfig":
        allowed = {field.name for field in cls.__dataclass_fields__.values()}
        payload = {key: item for key, item in value.items() if key in allowed}
        if "operations" in payload:
            payload["operations"] = tuple(payload["operations"])
        if "structure_cycle" in payload:
            payload["structure_cycle"] = tuple(payload["structure_cycle"])
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StructureMetadata:
    left_digits: int
    right_digits: int
    output_digits: int
    carry_count: int
    borrow_count: int
    event_count: int
    longest_chain: int
    event_columns: tuple[int, ...]
    result_width_change: int
    zero_digit_count: int
    nine_digit_count: int
    has_zero: bool
    has_nine: bool
    requested_structure: str
    observed_structure: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArithmeticExample:
    pair_id: str
    prompt: str
    completion: str
    answer: str
    operation: str
    left: int
    right: int
    counter: int
    namespace: str
    split: str
    family_id: str
    family_partition: int
    metadata: StructureMetadata
    control_arm: str = "correct"

    @property
    def difficulty(self) -> int:
        return max(self.metadata.left_digits, self.metadata.right_digits)

    @property
    def is_no_event(self) -> bool:
        return self.metadata.event_count == 0

    @property
    def operand_digit_lengths(self) -> tuple[int, int]:
        return self.metadata.left_digits, self.metadata.right_digits

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["difficulty"] = self.difficulty
        payload["is_no_event"] = self.is_no_event
        return payload


@dataclass(frozen=True)
class CounterfactualPair:
    pair_id: str
    clean: ArithmeticExample
    corrupt: ArithmeticExample
    event_type: str
    event_column: int
    expected_affected_digits: tuple[int, ...]
    expected_unaffected_digits: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "clean": self.clean.to_dict(),
            "corrupt": self.corrupt.to_dict(),
            "event_type": self.event_type,
            "event_column": self.event_column,
            "expected_affected_digits": list(self.expected_affected_digits),
            "expected_unaffected_digits": list(self.expected_unaffected_digits),
        }


@dataclass(frozen=True)
class DerangementPlan:
    seed: int
    stratum_kind: str
    active_pair_ids: tuple[str, ...]
    dropped_pair_ids: tuple[str, ...]
    assignment: dict[str, str]
    target_pair_ids: dict[str, str]
    strata: dict[str, str]
    bucket_summaries: tuple[dict[str, Any], ...]
    synthetic_pair_ids: tuple[str, ...] = ()
    synthetic_rows: int = 0
    synthetic_fraction: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "3.0",
            "seed": self.seed,
            "stratum_kind": self.stratum_kind,
            "active_pair_ids": list(self.active_pair_ids),
            "dropped_pair_ids": list(self.dropped_pair_ids),
            "assignment": dict(self.assignment),
            "target_pair_ids": dict(self.target_pair_ids),
            "strata": dict(self.strata),
            "bucket_summaries": list(self.bucket_summaries),
            "synthetic_pair_ids": list(self.synthetic_pair_ids),
            "synthetic_rows": self.synthetic_rows,
            "synthetic_fraction": self.synthetic_fraction,
        }


def _digits(value: int) -> int:
    return len(str(abs(value)))


def _structure_metadata(
    operation: str,
    left: int,
    right: int,
    answer: str,
    requested: str,
) -> StructureMetadata:
    carry_count, carry_chain = carry_features(left, right) if operation == "add" else (0, 0)
    borrow_count, borrow_chain = borrow_features(left, right) if operation == "sub" else (0, 0)
    event_count = carry_count + borrow_count
    longest_chain = max(carry_chain, borrow_chain)
    event_columns: list[int] = []
    if operation == "add":
        carry = 0
        a, b = left, right
        column = 0
        while a or b or carry:
            carry = int(a % 10 + b % 10 + carry >= 10)
            if carry:
                event_columns.append(column)
            a //= 10
            b //= 10
            column += 1
    else:
        borrow = 0
        a, b = left, right
        column = 0
        while a or b:
            borrow = int(a % 10 - borrow < b % 10)
            if borrow:
                event_columns.append(column)
            a //= 10
            b //= 10
            column += 1
    observed = "no_event" if event_count == 0 else ("chain" if longest_chain >= 2 else "event")
    operand_text = f"{left}{right}"
    output_digits = _digits(int(answer))
    max_operand_digits = max(_digits(left), _digits(right))
    return StructureMetadata(
        left_digits=_digits(left),
        right_digits=_digits(right),
        output_digits=output_digits,
        carry_count=carry_count,
        borrow_count=borrow_count,
        event_count=event_count,
        longest_chain=longest_chain,
        event_columns=tuple(event_columns),
        result_width_change=output_digits - max_operand_digits,
        zero_digit_count=operand_text.count("0"),
        nine_digit_count=operand_text.count("9"),
        has_zero="0" in operand_text,
        has_nine="9" in operand_text,
        requested_structure=requested,
        observed_structure=observed,
    )


def relation_family(operation: str, left: int, right: int, answer: str) -> tuple[str, int]:
    """Canonicalize add/sub inverse and commuted forms to one relation family."""

    if operation == "add":
        term_a, term_b, total = left, right, int(answer)
    elif operation == "sub":
        # left - right = answer is the same relation as right + answer = left.
        term_a, term_b, total = right, int(answer), left
    else:
        raise ValueError(f"unsupported operation: {operation}")
    low, high = sorted((term_a, term_b))
    identity = f"unsigned-additive-relation-v1|{low}|{high}|{total}"
    family_id = stable_hash(identity)
    partition = int(family_id[:16], 16) % FAMILY_PARTITIONS
    return family_id, partition


def split_family_partitions(split: str) -> frozenset[int]:
    """Return predeclared disjoint family partitions for study namespaces."""

    label = split.strip().lower().replace("-", "_")
    if label == "train" or label.startswith("train_"):
        return frozenset(range(8))
    if label in {"validation", "val", "dev"} or label.startswith(("validation_", "val_")):
        return frozenset({8})
    if "discovery" in label or "space_fit" in label or "geometry_fit" in label:
        return frozenset({9})
    if "space_selection" in label or "rank_selection" in label:
        return frozenset({10})
    if "intervention_calibration" in label or "patch_calibration" in label:
        return frozenset({11})
    if "causal" in label or "sealed_patch" in label or label in {"carry", "borrow"}:
        return frozenset({12})
    if label.startswith("iid") or "test_iid" in label:
        return frozenset({13})
    if "ood" in label:
        return frozenset({14})
    if label.startswith("test_"):
        return frozenset({15})
    if "final" in label or label in {"test", "holdout", "symbol_renamed"}:
        return frozenset({15})
    # Custom nontraining namespaces deterministically occupy one sealed slot.
    # Callers needing guaranteed separation between multiple custom names
    # should use the explicit discovery/causal/iid/ood/final conventions above.
    return frozenset({8 + int(stable_hash(label)[:8], 16) % 8})


def _integer_with_digits(rng: random.Random, digits: int) -> int:
    low = 0 if digits == 1 else 10 ** (digits - 1)
    return rng.randint(max(1, low), 10**digits - 1)


def _from_little_endian(digits: Sequence[int]) -> int:
    return sum(digit * (10**position) for position, digit in enumerate(digits))


def _construct_no_event(
    rng: random.Random, operation: str, left_digits: int, right_digits: int
) -> tuple[int, int]:
    """Construct exact-width operands with no carry or borrow."""

    width = max(left_digits, right_digits)
    left_out: list[int] = []
    right_out: list[int] = []
    for position in range(width):
        left_present = position < left_digits
        right_present = position < right_digits
        left_leading = position == left_digits - 1
        right_leading = position == right_digits - 1
        candidates: list[tuple[int, int]] = []
        left_range = range(10) if left_present else (0,)
        right_range = range(10) if right_present else (0,)
        for left_digit in left_range:
            if left_leading and left_digit == 0:
                continue
            for right_digit in right_range:
                if right_leading and right_digit == 0:
                    continue
                valid = (
                    left_digit + right_digit < 10
                    if operation == "add"
                    else left_digit >= right_digit
                )
                if valid:
                    candidates.append((left_digit, right_digit))
        if not candidates:
            raise AssertionError("no-event digit construction has no valid candidates")
        left_digit, right_digit = rng.choice(candidates)
        left_out.append(left_digit)
        right_out.append(right_digit)
    left = _from_little_endian(left_out)
    right = _from_little_endian(right_out)
    if operation == "sub" and left < right:
        raise AssertionError("borrow-free construction produced negative subtraction")
    return left, right


def _construct_single_event(
    rng: random.Random, operation: str, left_digits: int, right_digits: int
) -> tuple[int, int]:
    """Construct exact-width operands with exactly one carry or borrow.

    Rejection sampling two wide, otherwise-unconstrained integers is a poor
    way to request one event: the probability of exactly one carry decreases
    quickly with width.  Constructing the column constraints directly leaves
    rejection sampling responsible only for the sealed family partition.
    """

    if left_digits != right_digits:
        raise ValueError("single-event construction requires equal operand widths")
    width = left_digits
    if operation == "sub" and width < 2:
        raise ValueError("nonnegative one-column subtraction cannot borrow")
    event_column = rng.randrange(width if operation == "add" else width - 1)
    left_out: list[int] = []
    right_out: list[int] = []
    for position in range(width):
        leading = position == width - 1
        candidates: list[tuple[int, int]] = []
        for left_digit in range(10):
            if leading and left_digit == 0:
                continue
            for right_digit in range(10):
                if leading and right_digit == 0:
                    continue
                if operation == "add":
                    if position == event_column:
                        valid = left_digit + right_digit >= 10
                    elif position == event_column + 1:
                        # Absorb the incoming carry immediately.
                        valid = left_digit + right_digit <= 8
                    else:
                        valid = left_digit + right_digit <= 9
                else:
                    if position == event_column:
                        valid = left_digit < right_digit
                    elif position == event_column + 1:
                        # Repay the incoming borrow immediately.
                        valid = left_digit > right_digit
                    else:
                        valid = left_digit >= right_digit
                if valid:
                    candidates.append((left_digit, right_digit))
        if not candidates:
            raise AssertionError("single-event digit construction has no valid candidates")
        left_digit, right_digit = rng.choice(candidates)
        left_out.append(left_digit)
        right_out.append(right_digit)
    left = _from_little_endian(left_out)
    right = _from_little_endian(right_out)
    if operation == "sub" and left < right:
        raise AssertionError("single-borrow construction produced negative subtraction")
    return left, right


def _matches_structure(metadata: StructureMetadata, requested: str) -> bool:
    if requested == "balanced":
        return True
    if requested == "no_event":
        return metadata.event_count == 0
    if requested == "event":
        return metadata.event_count == 1
    if requested == "chain":
        return metadata.longest_chain >= 2
    raise ValueError(f"unknown requested structure: {requested}")


class StructuralArithmeticStream:
    """A deterministic infinite stream addressed by nonnegative counters."""

    def __init__(self, config: StreamConfig | Mapping[str, Any]):
        self.config = config if isinstance(config, StreamConfig) else StreamConfig.from_mapping(config)

    def _requested_shape(self, counter: int, constraint: str | None) -> tuple[str, int, int, str]:
        operation = self.config.operations[counter % len(self.config.operations)]
        digit_span = self.config.max_digits - self.config.min_digits + 1
        digit_index = (counter // len(self.config.operations)) % digit_span
        left_digits = self.config.min_digits + digit_index
        shape_rng = seeded_rng(
            "workspace-shape",
            self.config.seed,
            self.config.namespace,
            self.config.split,
            counter,
        )
        requested = constraint or self.config.structure_cycle[
            (counter // max(1, len(self.config.operations) * digit_span))
            % len(self.config.structure_cycle)
        ]
        if requested not in SUPPORTED_STRUCTURES:
            raise ValueError(f"unknown structural constraint: {requested}")
        minimum_feasible_width = {
            ("add", "chain"): 2,
            ("sub", "event"): 2,
            ("sub", "chain"): 3,
        }.get((operation, requested), 1)
        if self.config.max_digits < minimum_feasible_width:
            raise ValueError(
                f"structure={requested} for operation={operation} requires "
                f"max_digits >= {minimum_feasible_width}; configured "
                f"max_digits={self.config.max_digits}"
            )
        # Preserve the requested structural class.  Some classes have a
        # mathematical minimum width (for example, a nonnegative subtraction
        # needs two columns to borrow and three to form a borrow chain).
        # Promote only the selected width instead of silently relabeling the
        # request as an easier class.
        left_digits = max(left_digits, minimum_feasible_width)
        if requested in {"event", "chain"}:
            right_digits = left_digits
        else:
            right_digits = shape_rng.randint(self.config.min_digits, left_digits)
        return operation, left_digits, right_digits, requested

    def example(self, counter: int, constraint: str | None = None) -> ArithmeticExample:
        if counter < 0:
            raise ValueError("counter must be nonnegative")
        operation, left_digits, right_digits, requested = self._requested_shape(counter, constraint)
        chosen: tuple[int, int, str, str, int, StructureMetadata] | None = None
        for attempt in range(self.config.max_rejection_attempts):
            # Sealed partitions can be sparse in the finite one-digit domain.
            # Widen within the configured range after repeated misses rather
            # than leaking a relation family assigned to another split.
            available_growth = self.config.max_digits - left_digits
            growth_interval = max(
                1,
                self.config.max_rejection_attempts // max(1, available_growth + 1),
            )
            growth = min(available_growth, attempt // growth_interval)
            attempt_left_digits = left_digits + growth
            attempt_right_digits = (
                right_digits + growth
                if right_digits == left_digits
                else min(attempt_left_digits, right_digits + growth)
            )
            rng = seeded_rng(
                "workspace-example",
                self.config.seed,
                self.config.namespace,
                self.config.split,
                counter,
                attempt,
                operation,
                requested,
            )
            if requested == "no_event":
                left, right = _construct_no_event(
                    rng, operation, attempt_left_digits, attempt_right_digits
                )
            elif requested == "event":
                left, right = _construct_single_event(
                    rng, operation, attempt_left_digits, attempt_right_digits
                )
            else:
                left = _integer_with_digits(rng, attempt_left_digits)
                right = _integer_with_digits(rng, attempt_right_digits)
                if operation == "sub" and right > left:
                    left, right = right, left
            answer = str(left + right if operation == "add" else left - right)
            family_id, family_partition = relation_family(operation, left, right, answer)
            if family_partition not in split_family_partitions(self.config.split):
                continue
            metadata = _structure_metadata(operation, left, right, answer, requested)
            if operation == "add":
                minimum_chain = self.config.carry_chain_min
                maximum_chain = self.config.carry_chain_max
            else:
                minimum_chain = self.config.borrow_chain_min
                maximum_chain = self.config.borrow_chain_max
            chain_in_range = metadata.longest_chain >= minimum_chain and (
                maximum_chain is None or metadata.longest_chain <= maximum_chain
            )
            if _matches_structure(metadata, requested) and chain_in_range:
                chosen = left, right, answer, family_id, family_partition, metadata
                break
        if chosen is None:
            raise RuntimeError(
                f"could not generate structure={requested} at counter={counter} "
                f"after {self.config.max_rejection_attempts} attempts"
            )
        left, right, answer, family_id, family_partition, metadata = chosen
        prompt = self.config.prompt_template.format(
            left=left,
            right=right,
            symbol=self.config.add_symbol if operation == "add" else self.config.sub_symbol,
            operation=operation,
        )
        identity = json.dumps(
            {
                "namespace": self.config.namespace,
                "split": self.config.split,
                "counter": counter,
                "operation": operation,
                "left": left,
                "right": right,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return ArithmeticExample(
            pair_id=f"ws_{stable_hash(identity)[:24]}",
            prompt=prompt,
            completion=answer,
            answer=answer,
            operation=operation,
            left=left,
            right=right,
            counter=counter,
            namespace=self.config.namespace,
            split=self.config.split,
            family_id=family_id,
            family_partition=family_partition,
            metadata=metadata,
        )

    def batch(
        self, start: int, size: int, constraint: str | None = None
    ) -> list[ArithmeticExample]:
        if start < 0 or size < 0:
            raise ValueError("start and size must be nonnegative")
        return [self.example(counter, constraint) for counter in range(start, start + size)]

    def iter_from(self, start: int = 0, constraint: str | None = None) -> Iterator[ArithmeticExample]:
        counter = start
        while True:
            yield self.example(counter, constraint)
            counter += 1


def _direct_example(
    config: StreamConfig,
    counter: int,
    operation: str,
    left: int,
    right: int,
    requested: str,
) -> ArithmeticExample:
    answer = str(left + right if operation == "add" else left - right)
    if int(answer) < 0:
        raise ValueError("direct structural examples must have nonnegative answers")
    family_id, family_partition = relation_family(operation, left, right, answer)
    metadata = _structure_metadata(operation, left, right, answer, requested)
    prompt = config.prompt_template.format(
        left=left,
        right=right,
        symbol=config.add_symbol if operation == "add" else config.sub_symbol,
        operation=operation,
    )
    identity = json.dumps(
        {
            "namespace": config.namespace,
            "split": config.split,
            "counterfactual_counter": counter,
            "operation": operation,
            "left": left,
            "right": right,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return ArithmeticExample(
        pair_id=f"cf_{stable_hash(identity)[:24]}",
        prompt=prompt,
        completion=answer,
        answer=answer,
        operation=operation,
        left=left,
        right=right,
        counter=counter,
        namespace=config.namespace,
        split=config.split,
        family_id=family_id,
        family_partition=family_partition,
        metadata=metadata,
    )


def _counterfactual_operand_pair(
    rng: random.Random, operation: str, width: int, column: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    left_digits: list[int] = []
    right_digits: list[int] = []
    for position in range(width):
        leading = position == width - 1
        if position == column:
            if operation == "add":
                left_digit = rng.randint(1, 8)
                right_digit = 9 - left_digit
            else:
                left_digit = right_digit = rng.randint(1, 8)
        elif operation == "add":
            candidates = [
                (a, b)
                for a in range(1 if leading else 0, 8)
                for b in range(1 if leading else 0, 8)
                if a + b <= 7
            ]
            left_digit, right_digit = rng.choice(candidates)
        else:
            right_digit = rng.randint(1 if leading else 0, 5)
            left_digit = rng.randint(right_digit + 2, 9)
        left_digits.append(left_digit)
        right_digits.append(right_digit)
    clean_left = _from_little_endian(left_digits)
    clean_right = _from_little_endian(right_digits)
    if operation == "add":
        corrupt_left = clean_left + 10**column
        corrupt_right = clean_right
    else:
        corrupt_left = clean_left
        corrupt_right = clean_right + 10**column
    return (clean_left, clean_right), (corrupt_left, corrupt_right)


def _fst_transition(
    pseudo_seed: int,
    operation: str,
    state: int,
    left_digit: int,
    right_digit: int,
    states: int,
) -> tuple[int, int]:
    payload = f"pseudo-fst-v1|{pseudo_seed}|{operation}|{state}|{left_digit}|{right_digit}"
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return digest[0] % 10, digest[1] % states


def pseudo_fst_target(example: ArithmeticExample, pseudo_seed: int = 271828, states: int = 4) -> str:
    """Return a learnable finite-state pseudo-arithmetic target.

    The transducer reads aligned operand digits from least to most significant,
    just like a carry process.  It emits exactly as many digits as the true
    answer and forces the most significant emitted digit to be nonzero, keeping
    target orientation and length matched without using the arithmetic answer.
    """

    if states < 2:
        raise ValueError("states must be at least 2")
    width = example.metadata.output_digits
    left = example.left
    right = example.right
    state = int.from_bytes(
        hashlib.sha256(f"pseudo-init|{pseudo_seed}|{example.operation}".encode()).digest()[:2],
        "big",
    ) % states
    output_little_endian: list[int] = []
    for position in range(width):
        left_digit = (left // (10**position)) % 10
        right_digit = (right // (10**position)) % 10
        digit, state = _fst_transition(
            pseudo_seed, example.operation, state, left_digit, right_digit, states
        )
        output_little_endian.append(digit)
    output_little_endian[-1] = 1 + (
        output_little_endian[-1] + state + (pseudo_seed % 10)
    ) % 9
    target = "".join(str(digit) for digit in reversed(output_little_endian))
    if len(target) != len(example.answer) or target.startswith("0"):
        raise AssertionError("pseudo transducer violated output-length orientation")
    return target


def target_for(
    example: ArithmeticExample,
    arm: str,
    pseudo_seed: int = 271828,
    pseudo_states: int = 4,
) -> str:
    if arm == "correct":
        return example.answer
    if arm == "no_carry":
        if not example.is_no_event:
            raise ValueError("no_carry target requested for an example with carry/borrow events")
        return example.answer
    if arm == "pseudo_fst":
        return pseudo_fst_target(example, pseudo_seed=pseudo_seed, states=pseudo_states)
    if arm == "deranged":
        raise ValueError("deranged targets require a batch-level DerangementPlan")
    raise ValueError(f"unsupported arm: {arm}")


StratumKey = tuple[Any, ...]
StratumFunction = Callable[[ArithmeticExample], StratumKey]


def default_nuisance_stratum(example: ArithmeticExample) -> StratumKey:
    """Stratify on operator and target width, not numeric value or structure."""

    return example.operation, example.metadata.output_digits


def length_only_nuisance_stratum(example: ArithmeticExample) -> StratumKey:
    """Fallback stratum that preserves target width when an op bucket is impossible."""

    return (example.metadata.output_digits,)


def _stratum_label(key: StratumKey) -> str:
    return json.dumps(list(key), sort_keys=True, separators=(",", ":"), default=str)


def _random_value_derangement(
    indices: list[int], examples: Sequence[ArithmeticExample], rng: random.Random
) -> list[int] | None:
    """Find target indices in O(n) using seeded randomized multiset rotation."""

    source = sorted(indices, key=lambda index: examples[index].pair_id)
    # Guaranteed construction for a derangeable multiset. Answer groups and
    # rows are randomized before rotation; they are never ordered numerically.
    # Rotating contiguous value groups by the maximum group size separates
    # every group from itself whenever maximum_frequency <= n / 2.
    grouped: dict[str, list[int]] = defaultdict(list)
    for index in source:
        grouped[examples[index].completion].append(index)
    groups = list(grouped.values())
    rng.shuffle(groups)
    for group in groups:
        rng.shuffle(group)
    ordered = [index for group in groups for index in group]
    maximum = max(len(group) for group in groups)
    shifted = ordered[maximum:] + ordered[:maximum]
    mapping = dict(zip(ordered, shifted))
    targets = [mapping[index] for index in source]
    # Mix the guaranteed construction through valid transpositions.  This
    # removes the value-group adjacency of the initial rotation while staying
    # O(n), preserving the exact target multiset, and never introducing a
    # value fixed point.  It is substantially faster than rejection-shuffling
    # an entire duplicate-heavy bucket thousands of times.
    for _ in range(max(32, 8 * len(source))):
        left_position = rng.randrange(len(source))
        right_position = rng.randrange(len(source))
        if left_position == right_position:
            continue
        left_source = source[left_position]
        right_source = source[right_position]
        left_target = targets[left_position]
        right_target = targets[right_position]
        if (
            examples[left_source].completion != examples[right_target].completion
            and examples[right_source].completion != examples[left_target].completion
        ):
            targets[left_position], targets[right_position] = right_target, left_target
    if any(examples[s].completion == examples[t].completion for s, t in zip(source, targets)):
        return None
    return targets


def _is_canonical_unsigned_decimal(value: str) -> bool:
    return bool(value) and value.isdigit() and (value == "0" or not value.startswith("0"))


def _synthetic_same_width_target(
    source: str,
    *,
    seed: int,
    stratum_label: str,
    pair_id: str,
) -> str:
    """Construct a deterministic canonical decimal label unlike ``source``.

    This is intentionally not a permutation of empirical answers.  It exists
    only for a tiny nuisance stratum whose value multiplicities make an exact
    no-fixed-value permutation mathematically impossible.
    """

    if not _is_canonical_unsigned_decimal(source):
        raise ValueError("synthetic fallback requires canonical unsigned-decimal sources")
    width = len(source)
    lower = 0 if width == 1 else 10 ** (width - 1)
    cardinality = 10 if width == 1 else 9 * (10 ** (width - 1))
    digest = hashlib.sha256(
        f"workspace-synthetic-derangement-v1|{seed}|{stratum_label}|{pair_id}".encode()
    ).digest()
    offset = int.from_bytes(digest[:16], "big") % cardinality
    target = str(lower + offset)
    if target == source:
        target = str(lower + ((offset + 1) % cardinality))
    if (
        not _is_canonical_unsigned_decimal(target)
        or len(target) != width
        or target == source
    ):
        raise AssertionError("invalid synthetic same-width derangement target")
    return target


def build_derangement_plan(
    examples: Sequence[ArithmeticExample],
    seed: int,
    strata: StratumFunction = default_nuisance_stratum,
    *,
    drop_undetermined: bool = True,
    synthesize_impossible: bool = False,
) -> DerangementPlan:
    """Build a seeded, within-stratum target derangement.

    A bucket is mathematically derangeable iff no answer value occupies more
    than half of it.  Such buckets are randomized and retained; impossible
    buckets are either reported as dropped or raise when ``drop_undetermined``
    is false.  As a separately reported last resort, a mathematically
    impossible tiny output-width bucket can receive deterministic canonical
    same-width decimal labels.  That exception does not preserve its empirical
    target multiset and is only available with the output-width stratum.
    """

    if synthesize_impossible and strata is not length_only_nuisance_stratum:
        raise ValueError("synthetic fallback is restricted to output-width strata")

    pair_ids = [item.pair_id for item in examples]
    if len(pair_ids) != len(set(pair_ids)):
        raise ValueError("pair_id values must be unique")
    buckets: dict[StratumKey, list[int]] = defaultdict(list)
    for index, item in enumerate(examples):
        buckets[strata(item)].append(index)
    assignment: dict[str, str] = {}
    target_pair_ids: dict[str, str] = {}
    stratum_by_pair: dict[str, str] = {}
    active: list[str] = []
    dropped: list[str] = []
    synthetic: list[str] = []
    summaries: list[dict[str, Any]] = []
    for key in sorted(buckets, key=_stratum_label):
        indices = buckets[key]
        values = Counter(examples[index].completion for index in indices)
        maximum = max(values.values())
        label = _stratum_label(key)
        impossible = len(indices) < 2 or maximum * 2 > len(indices)
        if impossible:
            ids = sorted(examples[index].pair_id for index in indices)
            if synthesize_impossible:
                if len(indices) > SYNTHETIC_DERANGEMENT_MAX_ROWS:
                    raise ValueError(
                        "mathematically impossible output-width stratum exceeds "
                        f"synthetic fallback limit {SYNTHETIC_DERANGEMENT_MAX_ROWS}: {label}"
                    )
                for source_index in sorted(indices, key=lambda index: examples[index].pair_id):
                    source = examples[source_index]
                    target = _synthetic_same_width_target(
                        source.completion,
                        seed=int(seed),
                        stratum_label=label,
                        pair_id=source.pair_id,
                    )
                    assignment[source.pair_id] = target
                    target_pair_ids[source.pair_id] = (
                        "synthetic_" + stable_hash(
                            f"{seed}|{label}|{source.pair_id}|{target}"
                        )[:32]
                    )
                    stratum_by_pair[source.pair_id] = label
                    active.append(source.pair_id)
                    synthetic.append(source.pair_id)
                summaries.append(
                    {
                        "stratum": label,
                        "rows": len(indices),
                        "unique_values": len(values),
                        "maximum_value_frequency": maximum,
                        "status": "synthetic_same_width_not_multiset_preserving",
                    }
                )
                continue
            if not drop_undetermined:
                raise ValueError(f"nuisance stratum is not value-derangeable: {label}")
            dropped.extend(ids)
            summaries.append(
                {
                    "stratum": label,
                    "rows": len(indices),
                    "unique_values": len(values),
                    "maximum_value_frequency": maximum,
                    "status": "dropped_not_derangeable",
                }
            )
            continue
        bucket_rng = seeded_rng("workspace-derangement", seed, label)
        source_indices = sorted(indices, key=lambda index: examples[index].pair_id)
        target_indices = _random_value_derangement(source_indices, examples, bucket_rng)
        if target_indices is None:
            raise AssertionError(f"failed to construct a valid derangement for {label}")
        for source_index, target_index in zip(source_indices, target_indices):
            source = examples[source_index]
            target = examples[target_index]
            if source.completion == target.completion:
                raise AssertionError("value fixed point in derangement")
            assignment[source.pair_id] = target.completion
            target_pair_ids[source.pair_id] = target.pair_id
            stratum_by_pair[source.pair_id] = label
            active.append(source.pair_id)
        summaries.append(
            {
                "stratum": label,
                "rows": len(indices),
                "unique_values": len(values),
                "maximum_value_frequency": maximum,
                "status": "deranged",
            }
        )
    if not active:
        raise ValueError("no examples remain after derangement construction")
    active_ids = tuple(sorted(active))
    synthetic_ids = tuple(sorted(synthetic))
    synthetic_fraction = len(synthetic_ids) / len(active_ids) if active_ids else 0.0
    if synthetic_fraction > SYNTHETIC_DERANGEMENT_MAX_FRACTION:
        raise ValueError(
            "synthetic derangement fallback fraction exceeds hard cap: "
            f"{synthetic_fraction:.9f} > {SYNTHETIC_DERANGEMENT_MAX_FRACTION:.9f}"
        )
    plan = DerangementPlan(
        seed=int(seed),
        stratum_kind=(
            "operation_output_length"
            if strata is default_nuisance_stratum
            else (
                "output_length_with_synthetic_fallback"
                if synthetic_ids
                else "output_length"
            )
            if strata is length_only_nuisance_stratum
            else "custom"
        ),
        active_pair_ids=active_ids,
        dropped_pair_ids=tuple(sorted(dropped)),
        assignment=assignment,
        target_pair_ids=target_pair_ids,
        strata=stratum_by_pair,
        bucket_summaries=tuple(summaries),
        synthetic_pair_ids=synthetic_ids,
        synthetic_rows=len(synthetic_ids),
        synthetic_fraction=synthetic_fraction,
    )
    audit = audit_derangement(examples, plan, strata=strata, check_reproducibility=False)
    if not audit["valid"]:
        raise AssertionError(f"invalid derangement plan: {audit}")
    return plan


def apply_derangement(
    examples: Sequence[ArithmeticExample], plan: DerangementPlan
) -> list[ArithmeticExample]:
    by_id = {item.pair_id: item for item in examples}
    missing = set(plan.active_pair_ids) - set(by_id)
    if missing:
        raise ValueError(f"plan refers to missing pair_ids: {sorted(missing)[:3]}")
    return [
        replace(
            by_id[pair_id],
            completion=plan.assignment[pair_id],
            control_arm="deranged",
        )
        for pair_id in plan.active_pair_ids
    ]


def _prefix_length(left: str, right: str) -> int:
    count = 0
    for a, b in zip(left, right):
        if a != b:
            break
        count += 1
    return count


def _suffix_length(left: str, right: str) -> int:
    return _prefix_length(left[::-1], right[::-1])


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _pearson(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_var = sum((a - left_mean) ** 2 for a in left)
    right_var = sum((b - right_mean) ** 2 for b in right)
    if left_var <= 0.0 or right_var <= 0.0:
        return None
    return numerator / math.sqrt(left_var * right_var)


def _ranks(values: Sequence[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda index: values[index])
    result = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and values[ordered[end]] == values[ordered[start]]:
            end += 1
        average_rank = (start + 1 + end) / 2.0
        for offset in range(start, end):
            result[ordered[offset]] = average_rank
        start = end
    return result


def _chance_string_agreement(values: Sequence[str]) -> dict[str, float]:
    """Expected agreement from independent draws from a stratum multiset."""

    if not values:
        return {
            "first": 0.0,
            "last": 0.0,
            "prefix_fraction": 0.0,
            "suffix_fraction": 0.0,
            "aligned": 0.0,
        }
    count = len(values)
    width = max(len(value) for value in values)

    def match_probability(keys: Iterable[str]) -> float:
        frequencies = Counter(keys)
        return sum(amount * amount for amount in frequencies.values()) / (count * count)

    prefix_expectation = sum(
        match_probability(value[:length] for value in values)
        for length in range(1, width + 1)
    ) / width
    suffix_expectation = sum(
        match_probability(value[-length:] for value in values)
        for length in range(1, width + 1)
    ) / width
    aligned = sum(
        match_probability(value[position : position + 1] for value in values)
        for position in range(width)
    ) / width
    return {
        "first": match_probability(value[:1] for value in values),
        "last": match_probability(value[-1:] for value in values),
        "prefix_fraction": prefix_expectation,
        "suffix_fraction": suffix_expectation,
        "aligned": aligned,
    }


def _cycle_lengths(plan: DerangementPlan, active_pair_ids: Iterable[str] | None = None) -> list[int]:
    mapping = plan.target_pair_ids
    active = set(plan.active_pair_ids if active_pair_ids is None else active_pair_ids)
    visited: set[str] = set()
    lengths: list[int] = []
    for start in sorted(active):
        if start in visited:
            continue
        current = start
        length = 0
        while current not in visited:
            if current not in active or current not in mapping:
                raise AssertionError("target mapping is not a permutation of active rows")
            visited.add(current)
            length += 1
            current = mapping[current]
        lengths.append(length)
    return sorted(lengths)


def audit_derangement(
    examples: Sequence[ArithmeticExample],
    plan: DerangementPlan,
    strata: StratumFunction = default_nuisance_stratum,
    *,
    check_reproducibility: bool = True,
) -> dict[str, Any]:
    if strata is default_nuisance_stratum and plan.stratum_kind in {
        "output_length",
        "output_length_with_synthetic_fallback",
    }:
        strata = length_only_nuisance_stratum
    by_id = {item.pair_id: item for item in examples}
    active = [pair_id for pair_id in plan.active_pair_ids if pair_id in by_id]
    synthetic_declared = set(plan.synthetic_pair_ids)
    synthetic_active = synthetic_declared.intersection(active)
    exact_active = [pair_id for pair_id in active if pair_id not in synthetic_declared]
    fixed_pairs: list[str] = []
    fixed_values: list[str] = []
    width_mismatches: list[str] = []
    noncanonical_targets: list[str] = []
    source_values: list[str] = []
    target_values: list[str] = []
    exact_source_values: list[str] = []
    exact_target_values: list[str] = []
    prefix_fractions: list[float] = []
    suffix_fractions: list[float] = []
    first_agreement: list[float] = []
    last_agreement: list[float] = []
    aligned_agreement: list[float] = []
    numeric_source: list[float] = []
    numeric_target: list[float] = []
    source_by_stratum: dict[str, Counter[str]] = defaultdict(Counter)
    target_by_stratum: dict[str, Counter[str]] = defaultdict(Counter)
    exact_source_by_stratum: dict[str, Counter[str]] = defaultdict(Counter)
    exact_target_by_stratum: dict[str, Counter[str]] = defaultdict(Counter)
    synthetic_by_stratum: dict[str, int] = defaultdict(int)
    exact_by_stratum: dict[str, int] = defaultdict(int)
    pairs_by_stratum: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for pair_id in active:
        item = by_id[pair_id]
        target = plan.assignment[pair_id]
        target_pair = plan.target_pair_ids[pair_id]
        if pair_id == target_pair:
            fixed_pairs.append(pair_id)
        if item.completion == target:
            fixed_values.append(pair_id)
        if len(item.completion) != len(target):
            width_mismatches.append(pair_id)
        if not _is_canonical_unsigned_decimal(target):
            noncanonical_targets.append(pair_id)
        source_values.append(item.completion)
        target_values.append(target)
        width = max(len(item.completion), len(target), 1)
        prefix_fractions.append(_prefix_length(item.completion, target) / width)
        suffix_fractions.append(_suffix_length(item.completion, target) / width)
        first_agreement.append(float(item.completion[:1] == target[:1]))
        last_agreement.append(float(item.completion[-1:] == target[-1:]))
        pairs = list(zip(item.completion, target))
        aligned_agreement.append(sum(a == b for a, b in pairs) / max(len(pairs), 1))
        label = _stratum_label(strata(item))
        source_by_stratum[label][item.completion] += 1
        target_by_stratum[label][target] += 1
        pairs_by_stratum[label].append((item.completion, target))
        if pair_id in synthetic_declared:
            synthetic_by_stratum[label] += 1
        else:
            exact_source_values.append(item.completion)
            exact_target_values.append(target)
            exact_source_by_stratum[label][item.completion] += 1
            exact_target_by_stratum[label][target] += 1
            exact_by_stratum[label] += 1
        try:
            numeric_source.append(float(int(item.completion)))
            numeric_target.append(float(int(target)))
        except ValueError:
            pass
    per_stratum_multiset = {
        key: source_by_stratum[key] == target_by_stratum[key]
        for key in sorted(set(source_by_stratum) | set(target_by_stratum))
    }
    non_synthetic_labels = sorted(
        label for label, rows in exact_by_stratum.items() if rows > 0
    )
    per_non_synthetic_stratum_multiset = {
        label: exact_source_by_stratum[label] == exact_target_by_stratum[label]
        for label in non_synthetic_labels
    }
    mixed_synthetic_strata = sorted(
        label
        for label in set(synthetic_by_stratum) | set(exact_by_stratum)
        if synthetic_by_stratum[label] and exact_by_stratum[label]
    )
    cycles = _cycle_lengths(plan, exact_active) if exact_active else []
    reproducible: bool | None = None
    if check_reproducibility:
        rebuilt = build_derangement_plan(
            examples,
            plan.seed,
            strata=strata,
            drop_undetermined=True,
            synthesize_impossible=bool(plan.synthetic_pair_ids),
        )
        reproducible = (
            rebuilt.active_pair_ids == plan.active_pair_ids
            and rebuilt.dropped_pair_ids == plan.dropped_pair_ids
            and rebuilt.assignment == plan.assignment
            and rebuilt.target_pair_ids == plan.target_pair_ids
            and rebuilt.synthetic_pair_ids == plan.synthetic_pair_ids
            and rebuilt.synthetic_rows == plan.synthetic_rows
            and rebuilt.synthetic_fraction == plan.synthetic_fraction
        )
    global_multiset = Counter(source_values) == Counter(target_values)
    non_synthetic_global_multiset = Counter(exact_source_values) == Counter(
        exact_target_values
    )
    expected_synthetic_fraction = len(synthetic_active) / len(active) if active else 0.0
    synthetic_fraction_cap_passed = (
        expected_synthetic_fraction <= SYNTHETIC_DERANGEMENT_MAX_FRACTION
    )
    synthetic_metadata_valid = (
        synthetic_declared.issubset(set(plan.active_pair_ids))
        and len(synthetic_active) == len(synthetic_declared)
        and plan.synthetic_rows == len(synthetic_declared)
        and math.isclose(
            plan.synthetic_fraction,
            expected_synthetic_fraction,
            rel_tol=0.0,
            abs_tol=1e-15,
        )
        and not mixed_synthetic_strata
        and synthetic_fraction_cap_passed
        and (
            not synthetic_declared
            or plan.stratum_kind == "output_length_with_synthetic_fallback"
        )
    )
    valid = (
        len(active) == len(plan.active_pair_ids)
        and not fixed_pairs
        and not fixed_values
        and not width_mismatches
        and not noncanonical_targets
        and synthetic_metadata_valid
        and non_synthetic_global_multiset
        and all(per_non_synthetic_stratum_multiset.values())
        and (global_multiset if not synthetic_declared else True)
        and (reproducible is not False)
    )
    pearson = _pearson(numeric_source, numeric_target)
    spearman = (
        _pearson(_ranks(numeric_source), _ranks(numeric_target))
        if len(numeric_source) == len(active)
        else None
    )
    stratum_numeric: dict[str, dict[str, Any]] = {}
    eligible_pearson: list[tuple[int, float]] = []
    eligible_spearman: list[tuple[int, float]] = []
    all_stratum_pearson: list[tuple[int, float]] = []
    all_stratum_spearman: list[tuple[int, float]] = []
    baseline_weight = 0
    baseline_totals = {
        "first": 0.0,
        "last": 0.0,
        "prefix_fraction": 0.0,
        "suffix_fraction": 0.0,
        "aligned": 0.0,
    }
    for label, pairs_for_label in sorted(pairs_by_stratum.items()):
        source_numbers = [float(int(source)) for source, _ in pairs_for_label]
        target_numbers = [float(int(target)) for _, target in pairs_for_label]
        label_pearson = _pearson(source_numbers, target_numbers)
        label_spearman = _pearson(_ranks(source_numbers), _ranks(target_numbers))
        unique_values = len({source for source, _ in pairs_for_label})
        output_width = max(len(source) for source, _ in pairs_for_label)
        # Exact value derangement creates unavoidable negative dependence in
        # tiny one-digit alphabets. It is still fully reported, but it is not a
        # meaningful residual-correlation rejection gate. Gate eligibility is
        # reserved for adequately populated, multi-digit nuisance strata.
        gate_eligible = (
            len(pairs_for_label) >= 32 and unique_values >= 10 and output_width >= 2
        )
        stratum_numeric[label] = {
            "rows": len(pairs_for_label),
            "unique_values": unique_values,
            "output_width": output_width,
            "gate_eligible": gate_eligible,
            "pearson": label_pearson,
            "spearman": label_spearman,
        }
        if label_pearson is not None:
            all_stratum_pearson.append((len(pairs_for_label), label_pearson))
        if label_spearman is not None:
            all_stratum_spearman.append((len(pairs_for_label), label_spearman))
        if gate_eligible and label_pearson is not None:
            eligible_pearson.append((len(pairs_for_label), label_pearson))
        if gate_eligible and label_spearman is not None:
            eligible_spearman.append((len(pairs_for_label), label_spearman))
        chance = _chance_string_agreement([source for source, _ in pairs_for_label])
        baseline_weight += len(pairs_for_label)
        for key, value in chance.items():
            baseline_totals[key] += len(pairs_for_label) * value
    baseline = {
        key: value / baseline_weight if baseline_weight else None
        for key, value in baseline_totals.items()
    }

    def weighted(items: Sequence[tuple[int, float]]) -> float | None:
        total = sum(count for count, _ in items)
        return sum(count * value for count, value in items) / total if total else None

    def maximum_absolute(items: Sequence[tuple[int, float]]) -> float | None:
        return max((abs(value) for _, value in items), default=None)

    actual_first = _mean(first_agreement)
    actual_last = _mean(last_agreement)
    actual_prefix = _mean(prefix_fractions)
    actual_suffix = _mean(suffix_fractions)
    actual_aligned = _mean(aligned_agreement)
    return {
        "schema_version": "3.0",
        "valid": valid,
        "stratum_kind": plan.stratum_kind,
        "strata_coarsened": plan.stratum_kind in {
            "output_length",
            "output_length_with_synthetic_fallback",
        },
        "active_rows": len(active),
        "dropped_rows": len(plan.dropped_pair_ids),
        "synthetic_pair_ids": sorted(synthetic_declared),
        "synthetic_rows": len(synthetic_active),
        "synthetic_fraction": expected_synthetic_fraction,
        "synthetic_metadata_valid": synthetic_metadata_valid,
        "synthetic_fraction_cap": SYNTHETIC_DERANGEMENT_MAX_FRACTION,
        "synthetic_fraction_cap_passed": synthetic_fraction_cap_passed,
        "mixed_synthetic_strata": mixed_synthetic_strata,
        "synthetic_fallback_limit_rows": SYNTHETIC_DERANGEMENT_MAX_ROWS,
        "fixed_pair_count": len(fixed_pairs),
        "fixed_value_count": len(fixed_values),
        "fixed_pair_ids": fixed_pairs,
        "fixed_value_pair_ids": fixed_values,
        "width_match": not width_mismatches,
        "width_mismatch_pair_ids": width_mismatches,
        "canonical_decimal_targets": not noncanonical_targets,
        "noncanonical_target_pair_ids": noncanonical_targets,
        "global_multiset_preserved": global_multiset,
        "per_stratum_multiset_preserved": per_stratum_multiset,
        "non_synthetic_global_multiset_preserved": non_synthetic_global_multiset,
        "per_non_synthetic_stratum_multiset_preserved": (
            per_non_synthetic_stratum_multiset
        ),
        "first_digit_agreement": actual_first,
        "last_digit_agreement": actual_last,
        "mean_prefix_fraction": actual_prefix,
        "mean_suffix_fraction": actual_suffix,
        "aligned_digit_agreement": actual_aligned,
        "stratum_chance_baseline": baseline,
        "first_digit_agreement_excess": (
            actual_first - baseline["first"]
            if actual_first is not None and baseline["first"] is not None
            else None
        ),
        "last_digit_agreement_excess": (
            actual_last - baseline["last"]
            if actual_last is not None and baseline["last"] is not None
            else None
        ),
        "mean_prefix_fraction_excess": (
            actual_prefix - baseline["prefix_fraction"]
            if actual_prefix is not None and baseline["prefix_fraction"] is not None
            else None
        ),
        "mean_suffix_fraction_excess": (
            actual_suffix - baseline["suffix_fraction"]
            if actual_suffix is not None and baseline["suffix_fraction"] is not None
            else None
        ),
        "aligned_digit_agreement_excess": (
            actual_aligned - baseline["aligned"]
            if actual_aligned is not None and baseline["aligned"] is not None
            else None
        ),
        "numeric_pearson": pearson,
        "numeric_spearman": spearman,
        "numeric_by_stratum": stratum_numeric,
        "correlation_gate_policy": {
            "minimum_rows": 32,
            "minimum_unique_values": 10,
            "minimum_output_width": 2,
            "reason": "exclude unavoidable dependence from exact derangement of tiny alphabets",
        },
        "within_stratum_pearson_weighted": weighted(eligible_pearson),
        "within_stratum_spearman_weighted": weighted(eligible_spearman),
        "within_stratum_pearson_max_abs": maximum_absolute(eligible_pearson),
        "within_stratum_spearman_max_abs": maximum_absolute(eligible_spearman),
        "within_stratum_pearson_weighted_all": weighted(all_stratum_pearson),
        "within_stratum_spearman_weighted_all": weighted(all_stratum_spearman),
        "within_stratum_pearson_max_abs_all": maximum_absolute(all_stratum_pearson),
        "within_stratum_spearman_max_abs_all": maximum_absolute(all_stratum_spearman),
        "cycle_lengths": cycles,
        "one_cycles": sum(length == 1 for length in cycles),
        "deterministically_reproducible": reproducible,
    }


def _stage_value(stage: Any, name: str, default: Any) -> Any:
    if stage is None:
        return default
    if isinstance(stage, Mapping):
        return stage.get(name, default)
    return getattr(stage, name, default)


def _stage_fingerprint(stage: Any) -> str:
    if stage is None:
        return "none"
    if isinstance(stage, Mapping):
        payload = dict(stage)
    elif hasattr(stage, "__dataclass_fields__"):
        payload = asdict(stage)
    else:
        payload = {
            name: getattr(stage, name)
            for name in (
                "min_digits",
                "max_digits",
                "digits",
                "operations",
                "structure_cycle",
                "carry_chain",
                "borrow_chain",
                "symbol_renamed",
                "prompt_template",
            )
            if hasattr(stage, name)
        }
    return stable_hash(json.dumps(payload, sort_keys=True, default=str))[:16]


class WorkspaceDataProvider:
    """Trainer-facing facade over split-specific structural streams."""

    def __init__(
        self, data_config: StreamConfig | Mapping[str, Any], seed: int | None = None
    ) -> None:
        base = data_config if isinstance(data_config, StreamConfig) else StreamConfig.from_mapping(data_config)
        self.config = replace(base, seed=int(seed)) if seed is not None else base
        self._derangement_cache: OrderedDict[
            tuple[str, int, str], tuple[list[ArithmeticExample], DerangementPlan]
        ] = OrderedDict()

    def _config_for(self, split: str, stage: Any = None) -> StreamConfig:
        digit_range = _stage_value(stage, "digits", None)
        if digit_range is not None:
            minimum, maximum = map(int, digit_range)
        else:
            minimum = int(_stage_value(stage, "min_digits", self.config.min_digits))
            maximum = int(_stage_value(stage, "max_digits", self.config.max_digits))
        operations = tuple(_stage_value(stage, "operations", self.config.operations))
        requested_structures = _stage_value(stage, "structure_cycle", None)
        if requested_structures is not None:
            structures = tuple(requested_structures)
        else:
            chain_ranges = [
                value
                for value in (
                    _stage_value(stage, "carry_chain", None),
                    _stage_value(stage, "borrow_chain", None),
                )
                if value is not None
            ]
            maximum_chain = max((int(value[1]) for value in chain_ranges), default=-1)
            if maximum_chain == 0:
                structures = ("no_event",)
            elif maximum_chain == 1:
                structures = ("no_event", "event")
            elif maximum_chain > 1:
                structures = ("no_event", "event", "chain", "balanced")
            else:
                structures = self.config.structure_cycle
        symbol_renamed = bool(_stage_value(stage, "symbol_renamed", False)) or (
            "symbol_renamed" in str(split).lower()
        )
        carry_range = _stage_value(stage, "carry_chain", None)
        borrow_range = _stage_value(stage, "borrow_chain", None)
        return replace(
            self.config,
            split=str(split),
            min_digits=minimum,
            max_digits=maximum,
            operations=operations,
            structure_cycle=structures,
            prompt_template=str(
                _stage_value(stage, "prompt_template", self.config.prompt_template)
            ),
            add_symbol="⊕" if symbol_renamed else self.config.add_symbol,
            sub_symbol="⊖" if symbol_renamed else self.config.sub_symbol,
            carry_chain_min=(
                int(carry_range[0]) if carry_range is not None else self.config.carry_chain_min
            ),
            carry_chain_max=(
                int(carry_range[1]) if carry_range is not None else self.config.carry_chain_max
            ),
            borrow_chain_min=(
                int(borrow_range[0]) if borrow_range is not None else self.config.borrow_chain_min
            ),
            borrow_chain_max=(
                int(borrow_range[1]) if borrow_range is not None else self.config.borrow_chain_max
            ),
        )

    def _base_example(self, split: str, counter: int, stage: Any, arm: str) -> ArithmeticExample:
        config = self._config_for(split, stage)
        training_no_carry = arm == "no_carry" and str(split).lower().startswith("train")
        constraint = "no_event" if training_no_carry else None
        if training_no_carry:
            config = replace(
                config,
                carry_chain_min=0,
                carry_chain_max=0,
                borrow_chain_min=0,
                borrow_chain_max=0,
            )
        stream = StructuralArithmeticStream(config)
        return stream.example(counter, constraint=constraint)

    def _derangement_window(
        self, split: str, counter: int, stage: Any
    ) -> tuple[list[ArithmeticExample], DerangementPlan]:
        width = self.config.derangement_window
        window_start = (counter // width) * width
        key = (split, window_start, _stage_fingerprint(stage))
        if key not in self._derangement_cache:
            stream = StructuralArithmeticStream(self._config_for(split, stage))
            source = stream.batch(window_start, width)
            base_window_seed = int.from_bytes(
                hashlib.sha256(
                    f"provider-window|{self.config.seed}|{split}|{window_start}|{key[2]}".encode()
                ).digest()[:8],
                "big",
            )
            plan: DerangementPlan | None = None
            last_audit: dict[str, Any] | None = None
            for candidate in range(8):
                window_seed = int.from_bytes(
                    hashlib.sha256(
                        f"{base_window_seed}|candidate|{candidate}".encode()
                    ).digest()[:8],
                    "big",
                )
                try:
                    candidate_plan = build_derangement_plan(
                        source,
                        window_seed,
                        drop_undetermined=False,
                    )
                except ValueError:
                    try:
                        candidate_plan = build_derangement_plan(
                            source,
                            window_seed,
                            strata=length_only_nuisance_stratum,
                            drop_undetermined=False,
                        )
                    except ValueError:
                        candidate_plan = build_derangement_plan(
                            source,
                            window_seed,
                            strata=length_only_nuisance_stratum,
                            drop_undetermined=False,
                            synthesize_impossible=True,
                        )
                candidate_audit = audit_derangement(source, candidate_plan)
                weighted_pearson = candidate_audit["within_stratum_pearson_weighted"]
                prefix_excess = candidate_audit["mean_prefix_fraction_excess"]
                suffix_excess = candidate_audit["mean_suffix_fraction_excess"]
                pearson_ok = (
                    self.config.derangement_max_abs_pearson is None
                    or weighted_pearson is None
                    or abs(weighted_pearson) <= self.config.derangement_max_abs_pearson
                )
                prefix_ok = (
                    self.config.derangement_max_prefix_excess is None
                    or prefix_excess is None
                    or prefix_excess <= self.config.derangement_max_prefix_excess
                )
                suffix_ok = (
                    self.config.derangement_max_suffix_excess is None
                    or suffix_excess is None
                    or suffix_excess <= self.config.derangement_max_suffix_excess
                )
                last_audit = candidate_audit
                if candidate_audit["valid"] and pearson_ok and prefix_ok and suffix_ok:
                    plan = candidate_plan
                    break
            if plan is None:
                raise ValueError(
                    "no seeded derangement passed configured residual-correlation/string "
                    f"thresholds after 8 candidates; last_audit={last_audit}"
                )
            if plan.synthetic_rows:
                synthetic_strata = [
                    summary["stratum"]
                    for summary in plan.bucket_summaries
                    if summary.get("status")
                    == "synthetic_same_width_not_multiset_preserving"
                ]
                print(
                    "DERANGEMENT_SYNTHETIC_FALLBACK "
                    f"SEED={self.config.seed} SPLIT={split} "
                    f"WINDOW_START={window_start} WINDOW_ROWS={len(source)} "
                    f"SYNTHETIC_ROWS={plan.synthetic_rows} "
                    f"SYNTHETIC_FRACTION={plan.synthetic_fraction:.9f} "
                    f"FRACTION_CAP={SYNTHETIC_DERANGEMENT_MAX_FRACTION:.9f} "
                    "STRATA="
                    + json.dumps(synthetic_strata, sort_keys=True, separators=(",", ":")),
                    flush=True,
                )
            self._derangement_cache[key] = source, plan
            self._derangement_cache.move_to_end(key)
            while len(self._derangement_cache) > 2:
                self._derangement_cache.popitem(last=False)
        else:
            self._derangement_cache.move_to_end(key)
        return self._derangement_cache[key]

    def sample(
        self,
        arm: str,
        split: str,
        counter: int,
        stage: Any = None,
    ) -> ArithmeticExample:
        if arm not in SUPPORTED_ARMS:
            raise ValueError(f"arm must be one of {SUPPORTED_ARMS}")
        if arm == "deranged":
            source, plan = self._derangement_window(split, counter, stage)
            window_start = source[0].counter
            item = source[counter - window_start]
            if item.counter != counter:
                raise AssertionError("derangement window lost counter ordering")
            return replace(
                item,
                completion=plan.assignment[item.pair_id],
                control_arm="deranged",
            )
        item = self._base_example(split, counter, stage, arm)
        target_arm = (
            "correct"
            if arm == "no_carry" and not str(split).lower().startswith("train")
            else arm
        )
        return replace(
            item,
            completion=target_for(
                item,
                target_arm,
                self.config.pseudo_seed,
                self.config.pseudo_states,
            ),
            control_arm=arm,
        )

    def batch(
        self,
        arm: str,
        split: str,
        start: int,
        size: int,
        stage: Any = None,
    ) -> list[ArithmeticExample]:
        if start < 0 or size < 0:
            raise ValueError("start and size must be nonnegative")
        return [self.sample(arm, split, counter, stage) for counter in range(start, start + size)]

    def fixed_eval(
        self,
        arm: str,
        split: str,
        count: int,
        stage: Any = None,
    ) -> list[ArithmeticExample]:
        return self.batch(arm, split, 0, count, stage)

    def audit_control(
        self,
        arm: str,
        split: str,
        count: int,
        stage: Any = None,
    ) -> dict[str, Any]:
        if arm == "deranged":
            source, plan = self._derangement_window(split, 0, stage)
            audit = audit_derangement(source, plan)
            audit["requested_rows"] = count
            audit["audited_window_rows"] = len(source)
            return audit
        rows = self.fixed_eval(arm, split, count, stage)
        return {
            "schema_version": "2.0",
            "valid": len(rows) == count and all(item.completion for item in rows),
            "arm": arm,
            "rows": len(rows),
            "all_no_event": all(item.is_no_event for item in rows) if arm == "no_carry" else None,
            "target_lengths_match_answer": all(
                len(item.completion) == len(item.answer) for item in rows
            ),
            "deterministically_reproducible": rows == self.fixed_eval(arm, split, count, stage),
        }

    def counterfactual_pairs(
        self,
        arm: str,
        split: str,
        count: int,
        stage: Any = None,
    ) -> list[CounterfactualPair]:
        """Create minimally different no-event/event carry or borrow panels.

        Within each pair, changing one operand digit introduces exactly one
        carry or borrow at a known column.  Operation, operand widths, prompt
        length, and answer width remain matched.  Both relation families must
        belong to the requested sealed split partition.
        """

        if arm not in {"correct", "pseudo_fst"}:
            raise ValueError("counterfactual pairs support correct or pseudo_fst targets")
        if count < 0:
            raise ValueError("count must be nonnegative")
        config = self._config_for(split, stage)
        if config.max_digits < 2:
            raise ValueError("counterfactual carry/borrow pairs require max_digits >= 2")
        lower_width = max(2, config.min_digits)
        width_span = config.max_digits - lower_width + 1
        allowed = split_family_partitions(split)
        pairs: list[CounterfactualPair] = []
        for pair_counter in range(count):
            operation = config.operations[pair_counter % len(config.operations)]
            width = lower_width + (pair_counter // len(config.operations)) % width_span
            column = pair_counter % (width - 1)
            accepted: tuple[ArithmeticExample, ArithmeticExample] | None = None
            pair_attempts = max(config.max_rejection_attempts, 8192)
            for attempt in range(pair_attempts):
                available_growth = config.max_digits - width
                growth_interval = max(1, pair_attempts // max(1, available_growth + 1))
                effective_width = width + min(available_growth, attempt // growth_interval)
                rng = seeded_rng(
                    "workspace-counterfactual",
                    config.seed,
                    config.namespace,
                    split,
                    pair_counter,
                    attempt,
                    operation,
                    effective_width,
                    column,
                )
                clean_operands, corrupt_operands = _counterfactual_operand_pair(
                    rng, operation, effective_width, column
                )
                clean = _direct_example(
                    config,
                    pair_counter * 2,
                    operation,
                    clean_operands[0],
                    clean_operands[1],
                    "no_event",
                )
                corrupt = _direct_example(
                    config,
                    pair_counter * 2 + 1,
                    operation,
                    corrupt_operands[0],
                    corrupt_operands[1],
                    "event",
                )
                if clean.family_partition not in allowed or corrupt.family_partition not in allowed:
                    continue
                if clean.metadata.event_count != 0 or corrupt.metadata.event_count != 1:
                    continue
                if corrupt.metadata.event_columns != (column,):
                    continue
                if clean.operand_digit_lengths != corrupt.operand_digit_lengths:
                    continue
                if len(clean.answer) != len(corrupt.answer) or len(clean.prompt) != len(corrupt.prompt):
                    continue
                accepted = clean, corrupt
                break
            if accepted is None:
                raise RuntimeError(
                    f"could not construct counterfactual {operation} pair {pair_counter} "
                    f"for split={split}"
                )
            clean, corrupt = accepted
            clean = replace(
                clean,
                completion=target_for(
                    clean, arm, self.config.pseudo_seed, self.config.pseudo_states
                ),
                control_arm=arm,
            )
            corrupt = replace(
                corrupt,
                completion=target_for(
                    corrupt, arm, self.config.pseudo_seed, self.config.pseudo_states
                ),
                control_arm=arm,
            )
            output_width = clean.metadata.output_digits
            affected = (
                tuple(range(column, output_width))
                if arm == "pseudo_fst"
                else (column, column + 1)
            )
            unaffected = tuple(position for position in range(output_width) if position not in affected)
            identity = stable_hash(f"{clean.pair_id}|{corrupt.pair_id}")[:24]
            pairs.append(
                CounterfactualPair(
                    pair_id=f"cfpair_{identity}",
                    clean=clean,
                    corrupt=corrupt,
                    event_type="carry" if operation == "add" else "borrow",
                    event_column=column,
                    expected_affected_digits=affected,
                    expected_unaffected_digits=unaffected,
                )
            )
        return pairs


def make_training_batch(
    stream_or_provider: StructuralArithmeticStream | WorkspaceDataProvider,
    start: int,
    size: int,
    arm: str,
    *,
    split: str = "train",
    control_seed: int = 271828,
    stage: Any = None,
) -> list[ArithmeticExample]:
    """Small convenience API for trainers that do not need a provider object."""

    if isinstance(stream_or_provider, WorkspaceDataProvider):
        return stream_or_provider.batch(arm, split, start, size, stage)
    constraint = "no_event" if arm == "no_carry" else None
    source = stream_or_provider.batch(start, size, constraint=constraint)
    if arm == "deranged":
        plan = build_derangement_plan(source, control_seed, drop_undetermined=False)
        by_id = {item.pair_id: item for item in apply_derangement(source, plan)}
        return [by_id[item.pair_id] for item in source]
    return [
        replace(
            item,
            completion=target_for(item, arm, control_seed),
            control_arm=arm,
        )
        for item in source
    ]


__all__ = [
    "ArithmeticExample",
    "CounterfactualPair",
    "DerangementPlan",
    "StreamConfig",
    "StructuralArithmeticStream",
    "StructureMetadata",
    "SUPPORTED_ARMS",
    "SYNTHETIC_DERANGEMENT_MAX_FRACTION",
    "SYNTHETIC_DERANGEMENT_MAX_ROWS",
    "WorkspaceDataProvider",
    "apply_derangement",
    "audit_derangement",
    "build_derangement_plan",
    "default_nuisance_stratum",
    "length_only_nuisance_stratum",
    "make_training_batch",
    "pseudo_fst_target",
    "relation_family",
    "split_family_partitions",
    "target_for",
]
