"""Post-seal evaluation for v0.5 finite flat packet connections.

Behavioral decisions are made from the exact native float32 logits hashed by
this module. Margins only promote those stored values to float64; hidden
states and decoders are never re-evaluated at a different precision. This
prospectively repairs the numerical mismatch that invalidated v0.4 A15.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import torch

from .algebra import N_STATES, canonical_maps
from .data import EpisodeBatch, EpisodeGenerator
from .flatness_training import relation_cell_bank, word_signature
from .packet_models import OperatorMatrixBundle, PolarIsometricTableOperatorRNN


V05_AUDIT_VERSION = "v0.5-derived-diamond-and-loop-bank-v1"
NATIVE_MARGIN_TAU = 2.0**-18


@dataclass(frozen=True)
class PathCase:
    left: tuple[int, ...]
    right: tuple[int, ...]
    suffix: tuple[int, ...]
    canonical_start: int
    left_signature: tuple[int, ...]
    right_signature: tuple[int, ...]
    left_rewrite_count: int
    right_rewrite_count: int
    template: str

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        return {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in row.items()
        }


@dataclass(frozen=True)
class LoopCase:
    prefix: tuple[int, ...]
    loop: tuple[int, ...]
    suffix: tuple[int, ...]
    repeats: int
    canonical_start: int
    rewrite_count: int
    template: str = "contiguous"

    def expanded(self) -> tuple[int, ...]:
        return self.prefix + self.loop * self.repeats + self.suffix

    def baseline(self) -> tuple[int, ...]:
        return self.prefix + self.suffix

    def to_dict(self) -> dict[str, Any]:
        return {
            "prefix": list(self.prefix),
            "loop": list(self.loop),
            "suffix": list(self.suffix),
            "repeats": self.repeats,
            "canonical_start": self.canonical_start,
            "rewrite_count": self.rewrite_count,
            "template": self.template,
        }


@dataclass(frozen=True)
class FlatnessAuditConfig:
    seed: int
    diamonds_per_length: int
    loops_per_stratum: int
    diamond_lengths: tuple[int, ...] = (8, 9, 16, 17, 24, 25, 32, 33)
    diamond_suffix_lengths: tuple[int, ...] = (4, 8, 16, 32, 64)
    loop_length: int = 8
    loop_prefix_length: int = 4
    loop_repeats: tuple[int, ...] = (1, 2, 4, 8, 16, 32)
    loop_suffix_lengths: tuple[int, ...] = (0, 4, 8, 16, 32, 64)
    minimum_rewrites: int = 3

    def validate(self) -> None:
        for name in (
            "seed",
            "diamonds_per_length",
            "loops_per_stratum",
            "loop_length",
            "loop_prefix_length",
            "minimum_rewrites",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
        if self.diamonds_per_length < 1 or self.loops_per_stratum < 1:
            raise ValueError("audit counts must be positive")
        if self.loop_length < 1 or self.loop_prefix_length < 0 or self.minimum_rewrites < 1:
            raise ValueError("audit lengths and rewrite floor are invalid")
        for name in (
            "diamond_lengths",
            "diamond_suffix_lengths",
            "loop_repeats",
            "loop_suffix_lengths",
        ):
            values = getattr(self, name)
            if not values or any(
                isinstance(value, bool) or not isinstance(value, int) or value < 0
                for value in values
            ):
                raise ValueError(f"{name} must contain nonnegative integers")
        if any(length < 8 for length in self.diamond_lengths):
            raise ValueError("derived diamonds must begin at length eight")
        if any(length < 4 for length in self.diamond_suffix_lengths):
            raise ValueError("held-out diamond suffixes must begin at length four")
        maximum = max(
            self.loop_prefix_length + self.loop_length * repeats + suffix
            for repeats in self.loop_repeats
            for suffix in self.loop_suffix_lengths
        )
        if maximum > 512:
            raise ValueError("loop-plus-suffix grid exceeds the frozen depth-512 cap")


@dataclass(frozen=True)
class FlatnessAuditBank:
    config: FlatnessAuditConfig
    diamonds: tuple[PathCase, ...]
    inequivalent: tuple[PathCase, ...]
    loops: tuple[LoopCase, ...]
    construction_pair_digest: str
    fingerprint: str

    def to_dict(self, *, include_cases: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "audit_version": V05_AUDIT_VERSION,
            "config": asdict(self.config),
            "construction_pair_digest": self.construction_pair_digest,
            "fingerprint": self.fingerprint,
            "counts": {
                "diamonds": len(self.diamonds),
                "inequivalent": len(self.inequivalent),
                "loops": len(self.loops),
            },
        }
        if include_cases:
            result["diamonds"] = [case.to_dict() for case in self.diamonds]
            result["inequivalent"] = [case.to_dict() for case in self.inequivalent]
            result["loops"] = [case.to_dict() for case in self.loops]
        return result


@dataclass(frozen=True)
class NativeDecision:
    total: int
    ordinary_correct: int
    robust_correct: int
    boundary: int
    logits_sha256: str
    minimum_margin: float | None
    margins: tuple[float, ...]
    predictions: tuple[int, ...]

    def to_dict(self, *, include_vectors: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "total": self.total,
            "ordinary_correct": self.ordinary_correct,
            "robust_correct": self.robust_correct,
            "boundary": self.boundary,
            "ordinary_accuracy": self.ordinary_correct / self.total,
            "robust_accuracy": self.robust_correct / self.total,
            "boundary_rate": self.boundary / self.total,
            "logits_sha256": self.logits_sha256,
            "minimum_margin": self.minimum_margin,
            "margin_tau": NATIVE_MARGIN_TAU,
        }
        if include_vectors:
            result["margins"] = list(self.margins)
            result["predictions"] = list(self.predictions)
        return result


def _canonical_maps() -> np.ndarray:
    return canonical_maps("d4").astype(np.int64, copy=False)


def _apply_signature(signature: Sequence[int], start: int) -> int:
    return int(signature[int(start)])


def _random_word(
    rng: np.random.Generator,
    length: int,
    *,
    balanced: bool = True,
) -> tuple[int, ...]:
    if length == 0:
        return ()
    if balanced and length >= 2:
        zeros = length // 2
        array = np.array([0] * zeros + [1] * (length - zeros), dtype=np.int64)
        rng.shuffle(array)
    else:
        array = rng.integers(0, 2, size=length, dtype=np.int64)
    return tuple(int(value) for value in array)


def _normal_form_lookup(maps: np.ndarray) -> dict[tuple[int, ...], tuple[int, ...]]:
    bank = relation_cell_bank(maps)
    return dict(zip(bank.signatures, bank.normal_forms, strict=True))


def reduction_rewrite_count(maps: np.ndarray, word: Sequence[int]) -> int:
    """Count non-tree cells used by the registered left-to-right reduction."""

    representatives = _normal_form_lookup(maps)
    current: tuple[int, ...] = ()
    count = 0
    for action in word:
        left = current + (int(action),)
        right = representatives[word_signature(maps, left)]
        if left != right:
            count += 1
        current = right
    return count


def _pair_symmetry_key(
    left: Sequence[int],
    right: Sequence[int],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    direct = tuple(left), tuple(right)
    reverse = tuple(reversed(left)), tuple(reversed(right))
    swapped = tuple(1 - value for value in left), tuple(1 - value for value in right)
    variants = (
        direct,
        (direct[1], direct[0]),
        reverse,
        (reverse[1], reverse[0]),
        swapped,
        (swapped[1], swapped[0]),
    )
    return min(variants)


def _construction_digest(
    maps: np.ndarray,
) -> tuple[str, set[tuple[tuple[int, ...], tuple[int, ...]]]]:
    bank = relation_cell_bank(maps)
    keys = {_pair_symmetry_key(left, right) for left, right in bank.cells}
    payload = [[list(left), list(right)] for left, right in sorted(keys)]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), keys


def _find_equivalent_pair(
    rng: np.random.Generator,
    maps: np.ndarray,
    length: int,
    minimum_rewrites: int,
    excluded: set[tuple[tuple[int, ...], tuple[int, ...]]],
    target_signature: tuple[int, ...] | None = None,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    for _ in range(100_000):
        zero_count = int(rng.integers(1, length))
        left_array = np.array(
            [0] * zero_count + [1] * (length - zero_count),
            dtype=np.int64,
        )
        rng.shuffle(left_array)
        left = tuple(int(value) for value in left_array)
        array = np.asarray(left, dtype=np.int64).copy()
        rng.shuffle(array)
        right = tuple(int(value) for value in array)
        if left == right or left[0] == right[0] or left[-1] == right[-1]:
            continue
        left_signature = word_signature(maps, left)
        if target_signature is not None and left_signature != target_signature:
            continue
        if left_signature != word_signature(maps, right):
            continue
        if reduction_rewrite_count(maps, left) < minimum_rewrites:
            continue
        if reduction_rewrite_count(maps, right) < minimum_rewrites:
            continue
        key = _pair_symmetry_key(left, right)
        if key in excluded:
            continue
        excluded.add(key)
        return left, right
    raise RuntimeError(f"could not construct an equivalent pair at length {length}")


def _find_inequivalent_match(
    rng: np.random.Generator,
    maps: np.ndarray,
    source: Sequence[int],
) -> tuple[int, ...]:
    source_tuple = tuple(source)
    source_signature = word_signature(maps, source_tuple)
    for _ in range(10_000):
        array = np.asarray(source_tuple, dtype=np.int64).copy()
        rng.shuffle(array)
        candidate = tuple(int(value) for value in array)
        if candidate != source_tuple and word_signature(maps, candidate) != source_signature:
            return candidate
    raise RuntimeError("could not build a histogram-matched inequivalent word")


def _find_null_loop(
    rng: np.random.Generator,
    maps: np.ndarray,
    length: int,
    minimum_rewrites: int,
    excluded_words: set[tuple[int, ...]],
) -> tuple[int, ...]:
    identity = tuple(range(N_STATES))
    for _ in range(100_000):
        candidate = _random_word(rng, length, balanced=False)
        if candidate in excluded_words:
            continue
        if word_signature(maps, candidate) != identity:
            continue
        if reduction_rewrite_count(maps, candidate) < minimum_rewrites:
            continue
        excluded_words.add(candidate)
        return candidate
    raise RuntimeError(f"could not construct a derived null loop at length {length}")


def build_flatness_audit_bank(config: FlatnessAuditConfig) -> FlatnessAuditBank:
    """Materialize the complete held-out bank without accepting a model."""

    config.validate()
    maps = _canonical_maps()
    relation_bank = relation_cell_bank(maps)
    construction_digest, excluded_pairs = _construction_digest(maps)
    rng = np.random.default_rng(config.seed)
    diamonds: list[PathCase] = []
    negatives: list[PathCase] = []
    for length_index, length in enumerate(config.diamond_lengths):
        # Word-length parity is a D4 action invariant for this two-generator
        # presentation. A fixed length can therefore cover exactly four of the
        # eight actions. Adjacent even/odd registered lengths cover all eight.
        reachable_signatures = tuple(
            signature
            for signature, normal in zip(
                relation_bank.signatures,
                relation_bank.normal_forms,
                strict=True,
            )
            if len(normal) % 2 == length % 2
        )
        if len(reachable_signatures) != 4:
            raise RuntimeError("D4 parity split did not expose four action strata")
        for index in range(config.diamonds_per_length):
            target_signature = reachable_signatures[
                index % len(reachable_signatures)
            ]
            left, right = _find_equivalent_pair(
                rng,
                maps,
                length,
                config.minimum_rewrites,
                excluded_pairs,
                target_signature,
            )
            signature = word_signature(maps, left)
            suffix_length = config.diamond_suffix_lengths[
                (index + length_index) % len(config.diamond_suffix_lengths)
            ]
            suffix = _random_word(rng, suffix_length, balanced=False)
            start = int(rng.integers(0, N_STATES))
            diamonds.append(
                PathCase(
                    left=left,
                    right=right,
                    suffix=suffix,
                    canonical_start=start,
                    left_signature=signature,
                    right_signature=signature,
                    left_rewrite_count=reduction_rewrite_count(maps, left),
                    right_rewrite_count=reduction_rewrite_count(maps, right),
                    template=f"same_histogram_length_{length}",
                )
            )
            wrong = _find_inequivalent_match(rng, maps, left)
            wrong_signature = word_signature(maps, wrong)
            discriminating = [
                state
                for state in range(N_STATES)
                if _apply_signature(signature, state)
                != _apply_signature(wrong_signature, state)
            ]
            if not discriminating:
                raise RuntimeError("unequal permutations expose no discriminating state")
            negative_start = int(discriminating[index % len(discriminating)])
            negatives.append(
                PathCase(
                    left=left,
                    right=wrong,
                    suffix=suffix,
                    canonical_start=negative_start,
                    left_signature=signature,
                    right_signature=wrong_signature,
                    left_rewrite_count=reduction_rewrite_count(maps, left),
                    right_rewrite_count=reduction_rewrite_count(maps, wrong),
                    template=f"matched_inequivalent_length_{length}",
                )
            )

    identity = tuple(range(N_STATES))
    loop_pool = tuple(
        word
        for index in range(2**config.loop_length)
        for word in (
            tuple(
                (index >> (config.loop_length - position - 1)) & 1
                for position in range(config.loop_length)
            ),
        )
        if word_signature(maps, word) == identity
        and reduction_rewrite_count(maps, word) >= config.minimum_rewrites
    )
    if not loop_pool:
        raise RuntimeError("registered loop length yields no eligible null loops")
    loops: list[LoopCase] = []
    for repeats in config.loop_repeats:
        for suffix_length in config.loop_suffix_lengths:
            for _ in range(config.loops_per_stratum):
                loop = loop_pool[int(rng.integers(0, len(loop_pool)))]
                loops.append(
                    LoopCase(
                        prefix=_random_word(
                            rng, config.loop_prefix_length, balanced=False
                        ),
                        loop=loop,
                        suffix=_random_word(rng, suffix_length, balanced=False),
                        repeats=repeats,
                        canonical_start=int(rng.integers(0, N_STATES)),
                        rewrite_count=reduction_rewrite_count(maps, loop),
                    )
                )
    provisional = {
        "audit_version": V05_AUDIT_VERSION,
        "config": asdict(config),
        "construction_pair_digest": construction_digest,
        "diamonds": [case.to_dict() for case in diamonds],
        "inequivalent": [case.to_dict() for case in negatives],
        "loops": [case.to_dict() for case in loops],
    }
    encoded = json.dumps(
        provisional,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return FlatnessAuditBank(
        config=config,
        diamonds=tuple(diamonds),
        inequivalent=tuple(negatives),
        loops=tuple(loops),
        construction_pair_digest=construction_digest,
        fingerprint=hashlib.sha256(encoded).hexdigest(),
    )


def native_decision(
    logits: torch.Tensor,
    target: torch.Tensor,
    *,
    tau: float = NATIVE_MARGIN_TAU,
) -> NativeDecision:
    """Score correctness and robust membership from one float32 tensor."""

    if logits.dtype != torch.float32:
        raise TypeError("registered native logits must use torch.float32")
    if logits.ndim != 2 or logits.shape[1] != N_STATES:
        raise ValueError(f"logits must have shape (batch, {N_STATES})")
    if target.shape != (logits.shape[0],) or target.dtype != torch.long:
        raise ValueError("target must be a torch.long vector matching the batch")
    if not math.isfinite(tau) or tau <= 0.0:
        raise ValueError("tau must be finite and positive")
    stored = logits.detach().to(device="cpu").contiguous()
    targets = target.detach().to(device="cpu")
    finite_rows = torch.isfinite(stored).all(dim=1)
    predictions = stored.argmax(dim=1)
    correct = finite_rows & predictions.eq(targets)
    promoted = stored.to(torch.float64)
    centered = promoted - promoted.mean(dim=1, keepdim=True)
    denominator = torch.linalg.vector_norm(centered, dim=1)
    true_score = promoted.gather(1, targets[:, None]).squeeze(1)
    mask = torch.nn.functional.one_hot(targets, num_classes=N_STATES).to(torch.bool)
    competitor = promoted.masked_fill(mask, -torch.inf).max(dim=1).values
    gap = true_score - competitor
    valid_norm = finite_rows & torch.isfinite(denominator) & denominator.gt(0.0)
    margin = torch.full_like(denominator, -torch.inf)
    margin[valid_norm] = gap[valid_norm] / denominator[valid_norm]
    boundary = (~valid_norm) | margin.abs().le(tau)
    robust = correct & (~boundary) & margin.gt(tau)
    if bool((robust & ~correct).any()):
        raise RuntimeError("robust membership escaped native correctness")
    finite_margins = margin[torch.isfinite(margin)]
    minimum = float(finite_margins.min()) if finite_margins.numel() else None
    return NativeDecision(
        total=int(stored.shape[0]),
        ordinary_correct=int(correct.sum()),
        robust_correct=int(robust.sum()),
        boundary=int(boundary.sum()),
        logits_sha256=hashlib.sha256(stored.numpy().tobytes()).hexdigest(),
        minimum_margin=minimum,
        margins=tuple(float(value) for value in margin.tolist()),
        predictions=tuple(int(value) for value in predictions.tolist()),
    )


def _nearest_rank(values: Sequence[float], fraction: float) -> float | None:
    finite = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not finite:
        return None
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("quantile fraction must lie in [0, 1]")
    index = int(math.floor(fraction * (len(finite) - 1) + 0.5))
    return finite[index]


def numeric_summary(values: Iterable[float]) -> dict[str, float | int | None]:
    rows = tuple(float(value) for value in values)
    finite = tuple(value for value in rows if math.isfinite(value))
    return {
        "count": len(rows),
        "finite_count": len(finite),
        "minimum": min(finite) if finite else None,
        "median": _nearest_rank(finite, 0.50),
        "p95": _nearest_rank(finite, 0.95),
        "maximum": max(finite) if finite else None,
        "mean": sum(finite) / len(finite) if finite else None,
    }


def _visible_slots(
    canonical_to_slot: torch.Tensor,
    canonical_words: torch.Tensor,
) -> torch.Tensor:
    return torch.gather(
        canonical_to_slot,
        1,
        canonical_words.to(canonical_to_slot.device),
    )


def _apply_visible_words(
    maps: torch.Tensor,
    slots: torch.Tensor,
    starts: torch.Tensor,
) -> torch.Tensor:
    current = starts.clone()
    rows = torch.arange(current.shape[0], device=current.device)
    for actions in slots.unbind(dim=1):
        selected = maps[rows, actions]
        current = selected[rows, current]
    return current


def _batched_product(codes: torch.Tensor, slots: torch.Tensor) -> torch.Tensor:
    batch, _, dimension, _ = codes.shape
    product = (
        torch.eye(dimension, dtype=codes.dtype, device=codes.device)
        .expand(batch, -1, -1)
        .clone()
    )
    rows = torch.arange(batch, device=codes.device)
    for actions in slots.unbind(dim=1):
        product = codes[rows, actions] @ product
    return product


def _normalized_centered(
    logits: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    centered = logits - logits.mean(dim=-2, keepdim=True)
    norms = torch.linalg.vector_norm(centered, dim=-2, keepdim=True)
    valid = torch.isfinite(norms) & norms.gt(0.0)
    normalized = torch.where(
        valid,
        centered / norms.clamp_min(torch.finfo(logits.dtype).tiny),
        torch.zeros_like(centered),
    )
    return normalized, valid.squeeze(-2)


def _path_geometry(
    model: PolarIsometricTableOperatorRNN,
    codes: torch.Tensor,
    left_slots: torch.Tensor,
    right_slots: torch.Tensor,
    suffix_slots: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # Geometry is diagnostic rather than behavioral.  Cast the *executed*
    # native matrices once, then perform every product in float64.  Native
    # argmax and robust membership remain tied to the untouched float32 logits
    # in ``native_decision``.
    geometry_codes = codes.to(torch.float64)
    left = _batched_product(geometry_codes, left_slots)
    right = _batched_product(geometry_codes, right_slots)
    suffix = _batched_product(geometry_codes, suffix_slots)
    dimension = geometry_codes.shape[-1]
    identity = torch.eye(
        dimension, dtype=geometry_codes.dtype, device=geometry_codes.device
    )
    holonomy = right.transpose(-1, -2) @ left
    full = torch.linalg.matrix_norm(
        holonomy - identity,
        ord="fro",
        dim=(-2, -1),
    ) / (2.0 * math.sqrt(dimension))
    anchors = model.state_anchors().transpose(0, 1).to(torch.float64)
    restricted = torch.linalg.matrix_norm(
        (left - right) @ anchors,
        ord="fro",
        dim=(-2, -1),
    ) / math.sqrt(N_STATES)
    decoder = model.decoder.weight.to(torch.float64)
    left_logits = decoder @ suffix @ left @ anchors
    right_logits = decoder @ suffix @ right @ anchors
    left_signature, left_valid = _normalized_centered(left_logits)
    right_signature, right_valid = _normalized_centered(right_logits)
    quotient = (
        (left_signature - right_signature).square().sum(dim=-2).mean(dim=-1)
        / 4.0
    )
    valid = (
        left_valid.all(dim=-1)
        & right_valid.all(dim=-1)
        & torch.isfinite(quotient)
    )
    quotient = torch.where(
        valid,
        quotient,
        torch.full_like(quotient, torch.inf),
    )
    return full, restricted, quotient


def _episode_contexts(seed: int, cases: Sequence[PathCase]) -> EpisodeBatch:
    generator = EpisodeGenerator(seed)
    raw = generator.sample(len(cases), 0, family="d4")
    canonical_starts = torch.tensor(
        [case.canonical_start for case in cases], dtype=torch.long
    )
    raw.start = raw.phi.gather(1, canonical_starts[:, None]).squeeze(1)
    raw.target = raw.start.clone()
    return raw


def evaluate_path_cases(
    model: PolarIsometricTableOperatorRNN,
    cases: Sequence[PathCase],
    *,
    seed: int,
    equivalent: bool,
    device: torch.device | str = "cpu",
) -> dict[str, Any]:
    """Evaluate derived diamonds or matched non-equivalent paths."""

    if not cases:
        raise ValueError("path case bank must be nonempty")
    groups: dict[tuple[int, int, int], list[PathCase]] = {}
    for case in cases:
        key = (len(case.left), len(case.right), len(case.suffix))
        groups.setdefault(key, []).append(case)
    all_left: list[NativeDecision] = []
    all_right: list[NativeDecision] = []
    full_defects: list[float] = []
    restricted_defects: list[float] = []
    quotient_defects: list[float] = []
    joint_correct = 0
    joint_robust = 0
    prediction_agreement = 0
    target_distinct = 0
    logit_digest = hashlib.sha256(b"v0.5-path-logits")
    model = model.to(device)
    was_training = model.training
    model.eval()
    try:
        with torch.inference_mode():
            for group_index, (_, group) in enumerate(sorted(groups.items())):
                batch = _episode_contexts(seed + group_index * 1009, group).to(device)
                left_words = torch.tensor(
                    [case.left + case.suffix for case in group],
                    dtype=torch.long,
                    device=device,
                )
                right_words = torch.tensor(
                    [case.right + case.suffix for case in group],
                    dtype=torch.long,
                    device=device,
                )
                suffix_words = torch.tensor(
                    [case.suffix for case in group],
                    dtype=torch.long,
                    device=device,
                )
                left_slots = _visible_slots(batch.canonical_to_slot, left_words)
                right_slots = _visible_slots(batch.canonical_to_slot, right_words)
                suffix_slots = _visible_slots(batch.canonical_to_slot, suffix_words)
                left_targets = _apply_visible_words(batch.maps, left_slots, batch.start)
                right_targets = _apply_visible_words(batch.maps, right_slots, batch.start)
                bundle = model.encode_operator_bundle(batch.tables)
                initial = model.initial_hidden(batch.start)
                left_trace = model.continue_from_hidden(
                    initial, bundle.matrices, left_slots
                )
                right_trace = model.continue_from_hidden(
                    initial, bundle.matrices, right_slots
                )
                left_decision = native_decision(left_trace.logits, left_targets)
                right_decision = native_decision(right_trace.logits, right_targets)
                all_left.append(left_decision)
                all_right.append(right_decision)
                logit_digest.update(bytes.fromhex(left_decision.logits_sha256))
                logit_digest.update(bytes.fromhex(right_decision.logits_sha256))
                left_correct = (
                    np.asarray(left_decision.predictions)
                    == left_targets.detach().cpu().numpy()
                )
                right_correct = (
                    np.asarray(right_decision.predictions)
                    == right_targets.detach().cpu().numpy()
                )
                left_robust = left_correct & (
                    np.asarray(left_decision.margins) > NATIVE_MARGIN_TAU
                )
                right_robust = right_correct & (
                    np.asarray(right_decision.margins) > NATIVE_MARGIN_TAU
                )
                joint_correct += int((left_correct & right_correct).sum())
                joint_robust += int((left_robust & right_robust).sum())
                prediction_agreement += int(
                    (
                        np.asarray(left_decision.predictions)
                        == np.asarray(right_decision.predictions)
                    ).sum()
                )
                target_distinct += int((left_targets != right_targets).sum())

                left_core = torch.tensor(
                    [case.left for case in group], dtype=torch.long, device=device
                )
                right_core = torch.tensor(
                    [case.right for case in group], dtype=torch.long, device=device
                )
                full, restricted, quotient = _path_geometry(
                    model,
                    bundle.matrices,
                    _visible_slots(batch.canonical_to_slot, left_core),
                    _visible_slots(batch.canonical_to_slot, right_core),
                    suffix_slots,
                )
                full_defects.extend(float(value) for value in full.detach().cpu())
                restricted_defects.extend(
                    float(value) for value in restricted.detach().cpu()
                )
                quotient_defects.extend(
                    float(value) for value in quotient.detach().cpu()
                )
    finally:
        model.train(was_training)
    total = len(cases)
    if equivalent and target_distinct != 0:
        raise RuntimeError("equivalent bank produced unequal oracle targets")
    if not equivalent and target_distinct != total:
        raise RuntimeError("non-equivalent bank lacks discriminating starts")
    ordinary_left = sum(row.ordinary_correct for row in all_left)
    ordinary_right = sum(row.ordinary_correct for row in all_right)
    robust_left = sum(row.robust_correct for row in all_left)
    robust_right = sum(row.robust_correct for row in all_right)
    boundary = sum(row.boundary for row in all_left) + sum(
        row.boundary for row in all_right
    )
    return {
        "equivalent": equivalent,
        "total": total,
        "joint_correct": joint_correct,
        "joint_correct_rate": joint_correct / total,
        "joint_robust": joint_robust,
        "joint_robust_rate": joint_robust / total,
        "left_correct": ordinary_left,
        "left_accuracy": ordinary_left / total,
        "right_correct": ordinary_right,
        "right_accuracy": ordinary_right / total,
        "left_robust": robust_left,
        "left_robust_rate": robust_left / total,
        "right_robust": robust_right,
        "right_robust_rate": robust_right / total,
        "prediction_agreement": prediction_agreement,
        "prediction_agreement_rate": prediction_agreement / total,
        "target_distinct": target_distinct,
        "boundary": boundary,
        "decision_total": 2 * total,
        "boundary_rate": boundary / (2 * total),
        "native_logits_digest": logit_digest.hexdigest(),
        "full_holonomy_defect": numeric_summary(full_defects),
        "anchor_restriction_defect": numeric_summary(restricted_defects),
        "packet_quotient_defect": numeric_summary(quotient_defects),
    }


def _loop_contexts(seed: int, cases: Sequence[LoopCase]) -> EpisodeBatch:
    generator = EpisodeGenerator(seed)
    raw = generator.sample(len(cases), 0, family="d4")
    canonical_starts = torch.tensor(
        [case.canonical_start for case in cases], dtype=torch.long
    )
    raw.start = raw.phi.gather(1, canonical_starts[:, None]).squeeze(1)
    raw.target = raw.start.clone()
    return raw


def evaluate_loop_cases(
    model: PolarIsometricTableOperatorRNN,
    cases: Sequence[LoopCase],
    *,
    seed: int,
    device: torch.device | str = "cpu",
) -> dict[str, Any]:
    if not cases:
        raise ValueError("loop case bank must be nonempty")
    groups: dict[tuple[int, int], list[LoopCase]] = {}
    for case in cases:
        groups.setdefault((case.repeats, len(case.suffix)), []).append(case)
    strata: dict[str, Any] = {}
    pooled_total = pooled_joint = pooled_agreement = pooled_boundary = 0
    pooled_loop_correct = pooled_baseline_correct = pooled_joint_robust = 0
    model = model.to(device)
    was_training = model.training
    model.eval()
    try:
        with torch.inference_mode():
            for group_index, ((repeats, suffix_length), group) in enumerate(
                sorted(groups.items())
            ):
                batch = _loop_contexts(seed + group_index * 1013, group).to(device)
                expanded = torch.tensor(
                    [case.expanded() for case in group],
                    dtype=torch.long,
                    device=device,
                )
                baseline = torch.tensor(
                    [case.baseline() for case in group],
                    dtype=torch.long,
                    device=device,
                )
                expanded_slots = _visible_slots(batch.canonical_to_slot, expanded)
                baseline_slots = _visible_slots(batch.canonical_to_slot, baseline)
                target = _apply_visible_words(batch.maps, baseline_slots, batch.start)
                loop_target = _apply_visible_words(
                    batch.maps, expanded_slots, batch.start
                )
                if not torch.equal(target, loop_target):
                    raise RuntimeError("registered null loop changed the oracle target")
                bundle = model.encode_operator_bundle(batch.tables)
                initial = model.initial_hidden(batch.start)
                loop_trace = model.continue_from_hidden(
                    initial, bundle.matrices, expanded_slots
                )
                base_trace = model.continue_from_hidden(
                    initial, bundle.matrices, baseline_slots
                )
                loop_decision = native_decision(loop_trace.logits, target)
                base_decision = native_decision(base_trace.logits, target)
                loop_predictions = np.asarray(loop_decision.predictions)
                base_predictions = np.asarray(base_decision.predictions)
                target_np = target.detach().cpu().numpy()
                loop_correct = loop_predictions == target_np
                base_correct = base_predictions == target_np
                loop_robust = loop_correct & (
                    np.asarray(loop_decision.margins) > NATIVE_MARGIN_TAU
                )
                base_robust = base_correct & (
                    np.asarray(base_decision.margins) > NATIVE_MARGIN_TAU
                )
                total = len(group)
                joint = int((loop_correct & base_correct).sum())
                joint_robust = int((loop_robust & base_robust).sum())
                agreement = int((loop_predictions == base_predictions).sum())
                key = f"repeats_{repeats}_suffix_{suffix_length}"
                strata[key] = {
                    "repeats": repeats,
                    "suffix_length": suffix_length,
                    "total": total,
                    "loop_correct": int(loop_correct.sum()),
                    "loop_accuracy": float(loop_correct.mean()),
                    "baseline_correct": int(base_correct.sum()),
                    "baseline_accuracy": float(base_correct.mean()),
                    "joint_correct": joint,
                    "joint_correct_rate": joint / total,
                    "joint_robust": joint_robust,
                    "joint_robust_rate": joint_robust / total,
                    "agreement": agreement,
                    "agreement_rate": agreement / total,
                    "accuracy_degradation": float(
                        base_correct.mean() - loop_correct.mean()
                    ),
                    "boundary": loop_decision.boundary + base_decision.boundary,
                    "boundary_rate": (
                        loop_decision.boundary + base_decision.boundary
                    )
                    / (2 * total),
                    "loop_logits_sha256": loop_decision.logits_sha256,
                    "baseline_logits_sha256": base_decision.logits_sha256,
                }
                pooled_total += total
                pooled_joint += joint
                pooled_joint_robust += joint_robust
                pooled_agreement += agreement
                pooled_boundary += loop_decision.boundary + base_decision.boundary
                pooled_loop_correct += int(loop_correct.sum())
                pooled_baseline_correct += int(base_correct.sum())
    finally:
        model.train(was_training)
    return {
        "total": pooled_total,
        "decision_total": 2 * pooled_total,
        "loop_correct": pooled_loop_correct,
        "loop_accuracy": pooled_loop_correct / pooled_total,
        "baseline_correct": pooled_baseline_correct,
        "baseline_accuracy": pooled_baseline_correct / pooled_total,
        "joint_correct": pooled_joint,
        "joint_correct_rate": pooled_joint / pooled_total,
        "joint_robust": pooled_joint_robust,
        "joint_robust_rate": pooled_joint_robust / pooled_total,
        "agreement": pooled_agreement,
        "agreement_rate": pooled_agreement / pooled_total,
        "boundary": pooled_boundary,
        "boundary_rate": pooled_boundary / (2 * pooled_total),
        "accuracy_degradation": (
            pooled_baseline_correct - pooled_loop_correct
        )
        / pooled_total,
        "strata": strata,
    }


def evaluate_deep_accuracy(
    model: PolarIsometricTableOperatorRNN,
    *,
    seed: int,
    depth: int,
    examples: int,
    family: str = "d4",
    device: torch.device | str = "cpu",
) -> dict[str, Any]:
    batch = EpisodeGenerator(seed).sample(examples, depth, family=family).to(device)
    model = model.to(device)
    was_training = model.training
    model.eval()
    try:
        with torch.inference_mode():
            trace = model.run(batch.tables, batch.op_slots, batch.start)
            decision = native_decision(trace.logits, batch.target)
    finally:
        model.train(was_training)
    return {"family": family, "depth": depth, **decision.to_dict()}


class ExactCompiledPolarRNN(PolarIsometricTableOperatorRNN):
    """Assay oracle: exact visible permutation action on P and identity on Q."""

    model_name = "exact_compiled_polar_oracle"

    def __init__(self) -> None:
        super().__init__(hidden_dim=12)
        with torch.no_grad():
            self.state_embedding.weight.zero_()
            self.state_embedding.weight[:, :N_STATES].copy_(torch.eye(N_STATES))
            self.decoder.weight.zero_()
            self.decoder.weight[:, :N_STATES].copy_(torch.eye(N_STATES))
        for parameter in self.parameters():
            parameter.requires_grad_(False)

    def _q_codes(self, tables: torch.Tensor) -> torch.Tensor:
        identity = torch.eye(4, dtype=tables.dtype, device=tables.device)
        return identity.expand(tables.shape[0], tables.shape[1], -1, -1)

    def encode_operator_bundle(self, tables: torch.Tensor) -> OperatorMatrixBundle:
        batch, operators = self._validate_tables(tables)
        matrices = torch.zeros(
            batch,
            operators,
            self.hidden_dim,
            self.hidden_dim,
            dtype=tables.dtype,
            device=tables.device,
        )
        matrices[:, :, :N_STATES, :N_STATES] = tables.transpose(-1, -2)
        matrices[:, :, N_STATES:, N_STATES:] = self._q_codes(tables)
        return OperatorMatrixBundle(
            matrices=matrices,
            residuals=None,
            raw_residuals=matrices,
        )


class QuotientCurvedPolarOracle(ExactCompiledPolarRNN):
    """Perfect semantic quotient with relation-violating Q motion."""

    model_name = "quotient_flat_full_curved_oracle"

    def _q_codes(self, tables: torch.Tensor) -> torch.Tensor:
        def plane_rotation(first: int, second: int, theta: float) -> torch.Tensor:
            matrix = torch.eye(4, dtype=tables.dtype, device=tables.device)
            c, s = math.cos(theta), math.sin(theta)
            matrix[first, first] = c
            matrix[first, second] = -s
            matrix[second, first] = s
            matrix[second, second] = c
            return matrix

        # Rotations in intersecting planes do not commute. Consequently two
        # words with the same token histogram can have identical D4 action on
        # P while retaining large path-dependent holonomy on Q.
        codes = torch.stack(
            (
                plane_rotation(0, 1, 0.73),
                plane_rotation(1, 2, 1.11),
            )
        )
        return codes.expand(tables.shape[0], -1, -1, -1)


class IdentityCollapsedPolarOracle(ExactCompiledPolarRNN):
    """Flat-but-wrong control rejected by non-equivalent sensitivity."""

    model_name = "identity_collapsed_oracle"

    def encode_operator_bundle(self, tables: torch.Tensor) -> OperatorMatrixBundle:
        batch, operators = self._validate_tables(tables)
        matrices = torch.eye(
            self.hidden_dim, dtype=tables.dtype, device=tables.device
        ).expand(batch, operators, -1, -1)
        return OperatorMatrixBundle(
            matrices=matrices,
            residuals=None,
            raw_residuals=matrices,
        )


class RandomOrthogonalPolarOracle(ExactCompiledPolarRNN):
    """Norm-stable but semantically ungrounded control."""

    model_name = "random_orthogonal_oracle"

    def __init__(self, seed: int = 73) -> None:
        super().__init__()
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        raw = torch.randn(
            2, self.hidden_dim, self.hidden_dim, generator=generator
        )
        q, _ = torch.linalg.qr(raw)
        self.register_buffer("random_codes", q)

    def encode_operator_bundle(self, tables: torch.Tensor) -> OperatorMatrixBundle:
        batch, operators = self._validate_tables(tables)
        matrices = self.random_codes.to(
            dtype=tables.dtype, device=tables.device
        ).expand(batch, operators, -1, -1)
        return OperatorMatrixBundle(
            matrices=matrices,
            residuals=None,
            raw_residuals=matrices,
        )


class SuffixVisiblePolarOracle(ExactCompiledPolarRNN):
    """Fixture whose relation residue is invisible until a later suffix.

    The fixture is intentionally tied to the registered context in
    :func:`suffix_visible_holonomy_fixture`; it exists to exercise the actual
    word conversion, recurrence, decoder, native decision, and path-geometry
    pipeline rather than serving as a second scientific control model.
    """

    model_name = "suffix_visible_holonomy_oracle"

    def encode_operator_bundle(self, tables: torch.Tensor) -> OperatorMatrixBundle:
        batch, operators = self._validate_tables(tables)
        if operators != 2:
            raise ValueError("suffix-visible fixture requires exactly two slots")
        matrices = torch.eye(
            self.hidden_dim, dtype=tables.dtype, device=tables.device
        ).repeat(batch, operators, 1, 1)

        # In the frozen fixture context canonical r is visible slot zero and
        # maps observed state 0 to observed state 2.  This suffix maps the
        # hidden Q residue into observed class 1 while preserving the baseline
        # semantic continuation 0 -> 2.
        suffix = torch.eye(self.hidden_dim, dtype=tables.dtype, device=tables.device)
        suffix[[0, 2]] = suffix[[2, 0]]
        suffix_angle = math.pi / 3.0
        suffix_c = math.cos(suffix_angle)
        suffix_s = math.sin(suffix_angle)
        suffix[1, 1] = suffix_c
        suffix[1, N_STATES] = suffix_s
        suffix[N_STATES, 1] = -suffix_s
        suffix[N_STATES, N_STATES] = suffix_c
        matrices[:, 0] = suffix

        # The second slot has an endpoint-invisible rotation.  Applying it
        # twice leaves class zero as the native argmax but stores a larger
        # component in Q, which the suffix above exposes.
        theta = math.pi / 6.0
        c = math.cos(theta)
        s = math.sin(theta)
        relation = torch.eye(
            self.hidden_dim, dtype=tables.dtype, device=tables.device
        )
        relation[0, 0] = c
        relation[0, N_STATES] = -s
        relation[N_STATES, 0] = s
        relation[N_STATES, N_STATES] = c
        matrices[:, 1] = relation
        return OperatorMatrixBundle(
            matrices=matrices,
            residuals=None,
            raw_residuals=matrices,
        )


def hard_orthogonality_residual(
    model: PolarIsometricTableOperatorRNN,
    *,
    seed: int = 991,
    contexts: int = 32,
) -> dict[str, Any]:
    batch = EpisodeGenerator(seed).sample(contexts, 0, family="d4")
    with torch.inference_mode():
        matrices = model.encode_operator_bundle(batch.tables).matrices.to(torch.float64)
    identity = torch.eye(matrices.shape[-1], dtype=torch.float64)
    residual = torch.linalg.matrix_norm(
        matrices.transpose(-1, -2) @ matrices - identity,
        ord="fro",
        dim=(-2, -1),
    )
    determinant = torch.linalg.det(matrices).abs()
    return {
        "orthogonality_residual": numeric_summary(
            float(value) for value in residual.reshape(-1)
        ),
        "determinant_magnitude_error": numeric_summary(
            float(value) for value in (determinant - 1.0).abs().reshape(-1)
        ),
    }


def suffix_visible_holonomy_fixture() -> dict[str, Any]:
    """Calibration through the real evaluator, not a standalone vector test."""

    identity = tuple(range(N_STATES))
    common = {
        "left": (1, 1),
        "right": (),
        "canonical_start": 0,
        "left_signature": identity,
        "right_signature": identity,
        "left_rewrite_count": 1,
        "right_rewrite_count": 0,
        "template": "suffix_visible_pipeline_fixture",
    }
    immediate_case = PathCase(suffix=(), **common)
    future_case = PathCase(suffix=(0,), **common)
    model = SuffixVisiblePolarOracle()
    # Seed 34 has phi(0)=0 and canonical-to-slot [0, 1], the context for which
    # the deterministic fixture matrices above are registered.
    immediate = evaluate_path_cases(
        model, (immediate_case,), seed=34, equivalent=True
    )
    future = evaluate_path_cases(model, (future_case,), seed=34, equivalent=True)
    immediate_agreement = immediate["prediction_agreement_rate"] == 1.0
    future_disagreement = future["prediction_agreement_rate"] == 0.0
    defect = future["packet_quotient_defect"]["maximum"]
    signatures_defined = (
        future["packet_quotient_defect"]["finite_count"]
        == future["packet_quotient_defect"]["count"]
    )
    return {
        "immediate_agreement": immediate_agreement,
        "immediate_joint_correct": immediate["joint_correct_rate"],
        "future_disagreement": future_disagreement,
        "future_joint_correct": future["joint_correct_rate"],
        "future_probe_defect": defect,
        "signatures_defined": signatures_defined,
        "pipeline": {
            "immediate": immediate,
            "future": future,
        },
        "pass": bool(
            immediate_agreement
            and immediate["joint_correct_rate"] == 1.0
            and future_disagreement
            and future["joint_correct_rate"] == 0.0
            and signatures_defined
            and defect is not None
            and defect > 0.01
        ),
    }


def evaluate_control_suite(
    bank: FlatnessAuditBank,
    *,
    deep_examples: int,
    device: torch.device | str = "cpu",
) -> dict[str, Any]:
    controls: Mapping[str, PolarIsometricTableOperatorRNN] = {
        "exact_compiled": ExactCompiledPolarRNN(),
        "quotient_curved": QuotientCurvedPolarOracle(),
        "identity_collapsed": IdentityCollapsedPolarOracle(),
        "random_orthogonal": RandomOrthogonalPolarOracle(),
    }
    results: dict[str, Any] = {}
    for index, (name, model) in enumerate(controls.items()):
        results[name] = {
            "diamonds": evaluate_path_cases(
                model,
                bank.diamonds,
                seed=bank.config.seed + 20_000 + index * 100,
                equivalent=True,
                device=device,
            ),
            "inequivalent": evaluate_path_cases(
                model,
                bank.inequivalent,
                seed=bank.config.seed + 30_000 + index * 100,
                equivalent=False,
                device=device,
            ),
            "loops": evaluate_loop_cases(
                model,
                bank.loops,
                seed=bank.config.seed + 40_000 + index * 100,
                device=device,
            ),
            "deep_128": evaluate_deep_accuracy(
                model,
                seed=bank.config.seed + 50_000 + index * 100,
                depth=128,
                examples=deep_examples,
                device=device,
            ),
            "geometry": hard_orthogonality_residual(model),
        }
    exact = results["exact_compiled"]
    curved = results["quotient_curved"]
    collapsed = results["identity_collapsed"]
    random_control = results["random_orthogonal"]
    suffix_fixture = suffix_visible_holonomy_fixture()
    gates = {
        "exact_behavior": bool(
            exact["diamonds"]["joint_correct_rate"] == 1.0
            and exact["diamonds"]["joint_robust_rate"] == 1.0
            and exact["diamonds"]["boundary"] == 0
            and exact["loops"]["joint_correct_rate"] == 1.0
            and exact["loops"]["joint_robust_rate"] == 1.0
            and exact["loops"]["boundary"] == 0
            and exact["inequivalent"]["joint_correct_rate"] == 1.0
            and exact["deep_128"]["ordinary_accuracy"] == 1.0
            and exact["deep_128"]["robust_accuracy"] == 1.0
            and exact["deep_128"]["boundary"] == 0
        ),
        "exact_flatness": bool(
            exact["diamonds"]["full_holonomy_defect"]["maximum"] is not None
            and exact["diamonds"]["full_holonomy_defect"]["maximum"] <= 1e-6
            and exact["diamonds"]["full_holonomy_defect"]["finite_count"]
            == exact["diamonds"]["full_holonomy_defect"]["count"]
            and exact["diamonds"]["packet_quotient_defect"]["maximum"] is not None
            and exact["diamonds"]["packet_quotient_defect"]["maximum"] <= 1e-6
            and exact["diamonds"]["packet_quotient_defect"]["finite_count"]
            == exact["diamonds"]["packet_quotient_defect"]["count"]
        ),
        "quotient_curved_separation": bool(
            curved["diamonds"]["joint_correct_rate"] == 1.0
            and curved["diamonds"]["packet_quotient_defect"]["maximum"] is not None
            and curved["diamonds"]["packet_quotient_defect"]["maximum"] <= 1e-6
            and curved["diamonds"]["full_holonomy_defect"]["median"] is not None
            and curved["diamonds"]["full_holonomy_defect"]["median"] >= 0.02
        ),
        "collapse_rejected": bool(
            collapsed["inequivalent"]["joint_correct_rate"] <= 0.20
        ),
        "random_isometry_not_semantics": bool(
            random_control["geometry"]["orthogonality_residual"]["maximum"]
            is not None
            and random_control["geometry"]["orthogonality_residual"]["maximum"]
            <= 1e-5
            and random_control["deep_128"]["ordinary_accuracy"] <= 0.40
        ),
        "suffix_visible_holonomy_detected": suffix_fixture["pass"],
    }
    return {
        "results": results,
        "suffix_visible_fixture": suffix_fixture,
        "gates": gates,
        "assay_valid": all(gates.values()),
    }


__all__ = [
    "NATIVE_MARGIN_TAU",
    "V05_AUDIT_VERSION",
    "ExactCompiledPolarRNN",
    "FlatnessAuditBank",
    "FlatnessAuditConfig",
    "IdentityCollapsedPolarOracle",
    "LoopCase",
    "NativeDecision",
    "PathCase",
    "QuotientCurvedPolarOracle",
    "RandomOrthogonalPolarOracle",
    "SuffixVisiblePolarOracle",
    "build_flatness_audit_bank",
    "evaluate_control_suite",
    "evaluate_deep_accuracy",
    "evaluate_loop_cases",
    "evaluate_path_cases",
    "hard_orthogonality_residual",
    "native_decision",
    "numeric_summary",
    "reduction_rewrite_count",
    "suffix_visible_holonomy_fixture",
]
