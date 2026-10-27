from __future__ import annotations

import hashlib
from collections.abc import Iterable
from typing import Any

import numpy as np
import torch

from .algebra import N_OPERATORS, N_STATES
from .data import EpisodeGenerator
from .models import RecurrentOperatorModel
from .splits import COORDINATE_SPLITS, map_splits, validate_coordinate_split


HELDOUT_COMPOSITE_SAMPLER_NAMESPACE = (
    "komorebi-neuralese/heldout-composite-word-rejection-sampler/v1"
)


def compose_full_word_maps(maps: torch.Tensor, op_slots: torch.Tensor) -> torch.Tensor:
    """Return the exact finite-state map induced by every anonymous word.

    Unlike an endpoint calculation, this applies the word to all states in
    parallel.  The result therefore has shape ``(batch, states)`` and can be
    assigned to the frozen map-level train/dev/test partition without using the
    sampled start state.
    """

    if maps.ndim != 3:
        raise ValueError("maps must have shape (batch, operators, states)")
    if op_slots.ndim != 2 or op_slots.shape[0] != maps.shape[0]:
        raise ValueError("op_slots must have shape (batch, length)")
    batch, operators, states = maps.shape
    if operators != N_OPERATORS or states != N_STATES:
        raise ValueError(
            f"maps must have trailing shape ({N_OPERATORS}, {N_STATES})"
        )
    slots = op_slots.to(device=maps.device, dtype=torch.long)
    if slots.numel() and bool(((slots < 0) | (slots >= operators)).any()):
        raise ValueError("operator slot index out of range")

    # Each row initially represents the identity map x -> x.  Applying the
    # selected map to every current image performs exact row-action
    # composition in the same order as RecurrentOperatorModel.run.
    composite = torch.arange(states, dtype=torch.long, device=maps.device)
    composite = composite.unsqueeze(0).expand(batch, -1).clone()
    rows = torch.arange(batch, device=maps.device)
    integer_maps = maps.to(dtype=torch.long)
    for step in range(slots.shape[1]):
        selected = integer_maps[rows, slots[:, step]]
        composite = torch.gather(selected, 1, composite)
    return composite


def _depth_seed(base_seed: int, depth: int) -> int:
    payload = (
        f"{HELDOUT_COMPOSITE_SAMPLER_NAMESPACE}\x00{int(base_seed)}\x00{int(depth)}"
    ).encode("utf-8")
    # NumPy accepts an unsigned 64-bit integer as a SeedSequence input.  Hash
    # derivation makes each depth independent of request order and avoids
    # accidental overlap with training/evaluation seed offsets.
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _split_counts(labels: np.ndarray) -> dict[str, int]:
    flat = np.asarray(labels).reshape(-1)
    return {split: int(np.count_nonzero(flat == split)) for split in COORDINATE_SPLITS}


def _update_candidate_digest(
    digest: Any,
    *,
    candidate_index: int,
    primitive_maps: np.ndarray,
    slots: np.ndarray,
    start: int,
    composite_map: np.ndarray,
    composite_split: str,
) -> None:
    """Hash one complete candidate in a platform-independent byte encoding."""

    digest.update(int(candidate_index).to_bytes(8, "big", signed=False))
    digest.update(np.asarray(primitive_maps, dtype=np.uint8).tobytes(order="C"))
    digest.update(np.asarray(slots, dtype=np.uint8).tobytes(order="C"))
    digest.update(bytes((int(start),)))
    digest.update(np.asarray(composite_map, dtype=np.uint8).tobytes(order="C"))
    digest.update(composite_split.encode("ascii"))
    digest.update(b"\x00")


def split_conditioned_final_action_metrics(
    model: RecurrentOperatorModel,
    *,
    family: str,
    depths: Iterable[int],
    examples_per_depth: int,
    batch_size: int,
    seed: int,
    device: torch.device | str,
    coordinate_split: str,
    maximum_candidate_multiplier: int = 100,
) -> dict[str, Any]:
    """Evaluate endpoints only when the *whole word action* has the requested split.

    ``EpisodeGenerator(..., coordinate_split=...)`` already confines every
    visible primitive table to one frozen map partition.  That does not imply
    the word's composed map is in the same partition: two held-out primitives
    can compose to a training map.  This metric deterministically rejects such
    candidates, computes the full map on all eight states, and passes only
    accepted rows to the model.

    The returned receipts expose candidate counts by composite split, primitive
    split checks, exact rejection accounting, and SHA-256 commitments to both
    the full candidate stream and the accepted examples.  ``dev`` and ``test``
    are accepted; ``train`` is deliberately rejected because this is a held-out
    semantic-action assay.  This conditioning establishes a held-out finite-map
    target under the frozen hash partition.  It does *not* imply that the
    corresponding abstract group element, word, or equivalence class is globally
    novel relative to all training compositions.
    """

    if not isinstance(model, RecurrentOperatorModel):
        return {
            "available": False,
            "reason": "model is nonrecurrent",
            "coordinate_split": coordinate_split,
        }
    split = validate_coordinate_split(coordinate_split)
    if split not in {"dev", "test"}:
        raise ValueError("coordinate_split must be held-out 'dev' or 'test'")
    requested_depths = tuple(int(depth) for depth in depths)
    if not requested_depths:
        raise ValueError("depths must not be empty")
    if any(depth < 1 for depth in requested_depths):
        raise ValueError("held-out composite word depths must be positive")
    evaluated_depths = tuple(sorted(set(requested_depths)))
    if examples_per_depth < 1:
        raise ValueError("examples_per_depth must be positive")
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    if maximum_candidate_multiplier < 1:
        raise ValueError("maximum_candidate_multiplier must be positive")

    device = torch.device(device)
    was_training = model.training
    model.eval()
    by_depth: dict[str, Any] = {}
    overall_candidate_counts = {name: 0 for name in COORDINATE_SPLITS}
    overall_primitive_counts = {name: 0 for name in COORDINATE_SPLITS}
    overall_correct = 0
    overall_finite = 0
    overall_drawn = 0
    overall_accepted = 0
    overall_digest = hashlib.sha256(HELDOUT_COMPOSITE_SAMPLER_NAMESPACE.encode("utf-8"))

    try:
        with torch.no_grad():
            for depth in evaluated_depths:
                depth_seed = _depth_seed(seed, depth)
                generator = EpisodeGenerator(depth_seed, coordinate_split=split)
                maximum_candidates = examples_per_depth * maximum_candidate_multiplier
                candidate_digest = hashlib.sha256(
                    f"{HELDOUT_COMPOSITE_SAMPLER_NAMESPACE}|candidate|{depth}|{depth_seed}".encode(
                        "utf-8"
                    )
                )
                accepted_digest = hashlib.sha256(
                    f"{HELDOUT_COMPOSITE_SAMPLER_NAMESPACE}|accepted|{depth}|{depth_seed}".encode(
                        "utf-8"
                    )
                )
                candidate_counts = {name: 0 for name in COORDINATE_SPLITS}
                primitive_counts = {name: 0 for name in COORDINATE_SPLITS}
                accepted_unique_maps: set[bytes] = set()
                drawn = 0
                accepted = 0
                correct = 0
                finite_logits = 0
                target_consistency_violations = 0

                while accepted < examples_per_depth:
                    if drawn >= maximum_candidates:
                        raise RuntimeError(
                            "held-out composite rejection sampler exhausted its deterministic "
                            f"candidate budget at depth {depth}: accepted={accepted}, "
                            f"drawn={drawn}, requested={examples_per_depth}, split={split}, "
                            f"candidate_split_counts={candidate_counts}"
                        )
                    remaining = examples_per_depth - accepted
                    draw_size = min(batch_size, maximum_candidates - drawn, remaining)
                    batch = generator.sample(draw_size, depth, family=family)
                    primitive_maps = batch.maps.detach().cpu().numpy()
                    primitive_labels = np.asarray(map_splits(primitive_maps))
                    current_primitive_counts = _split_counts(primitive_labels)
                    for name, count in current_primitive_counts.items():
                        primitive_counts[name] += count
                    primitive_violations = int(np.count_nonzero(primitive_labels != split))
                    if primitive_violations:
                        raise RuntimeError(
                            "primitive coordinate-split confinement failed: "
                            f"depth={depth}, split={split}, violations={primitive_violations}"
                        )

                    composite_maps = compose_full_word_maps(batch.maps, batch.op_slots)
                    composite_numpy = composite_maps.detach().cpu().numpy()
                    composite_labels = np.asarray(map_splits(composite_numpy)).reshape(-1)
                    current_candidate_counts = _split_counts(composite_labels)
                    for name, count in current_candidate_counts.items():
                        candidate_counts[name] += count

                    batch_start = batch.start.detach().cpu().numpy()
                    batch_slots = batch.op_slots.detach().cpu().numpy()
                    for local_index in range(draw_size):
                        fields = {
                            "candidate_index": drawn + local_index,
                            "primitive_maps": primitive_maps[local_index],
                            "slots": batch_slots[local_index],
                            "start": int(batch_start[local_index]),
                            "composite_map": composite_numpy[local_index],
                            "composite_split": str(composite_labels[local_index]),
                        }
                        _update_candidate_digest(candidate_digest, **fields)
                        if composite_labels[local_index] == split:
                            _update_candidate_digest(accepted_digest, **fields)
                            accepted_unique_maps.add(
                                np.asarray(composite_numpy[local_index], dtype=np.uint8).tobytes()
                            )

                    selected_numpy = np.flatnonzero(composite_labels == split)
                    # draw_size never exceeds the number still needed, so every
                    # eligible candidate is accepted and accounting is exact.
                    if selected_numpy.size:
                        selected = torch.as_tensor(selected_numpy, dtype=torch.long)
                        accepted_maps = composite_maps.index_select(0, selected)
                        accepted_starts = batch.start.index_select(0, selected)
                        rows = torch.arange(selected.shape[0])
                        exact_targets = accepted_maps[rows, accepted_starts]
                        recorded_targets = batch.target.index_select(0, selected)
                        violations = int((exact_targets != recorded_targets).sum())
                        target_consistency_violations += violations
                        if violations:
                            raise RuntimeError(
                                "episode endpoint target disagrees with the independently "
                                f"composed full map at depth {depth}"
                            )

                        trace = model.run(
                            batch.tables.index_select(0, selected).to(device),
                            batch.op_slots.index_select(0, selected).to(device),
                            accepted_starts.to(device),
                        )
                        if trace.logits.ndim != 2 or trace.logits.shape != (
                            selected.shape[0],
                            N_STATES,
                        ):
                            raise RuntimeError(
                                "model logits must have shape "
                                f"({selected.shape[0]}, {N_STATES})"
                            )
                        finite_rows = torch.isfinite(trace.logits).all(dim=1)
                        prediction = trace.logits.argmax(dim=1).cpu()
                        correct += int(
                            ((prediction == exact_targets) & finite_rows.cpu()).sum()
                        )
                        finite_logits += int(finite_rows.sum())
                        accepted += int(selected.shape[0])
                    drawn += draw_size

                rejected_counts = dict(candidate_counts)
                rejected_counts[split] = 0
                accepted_counts = {name: 0 for name in COORDINATE_SPLITS}
                accepted_counts[split] = accepted
                rejected = drawn - accepted
                receipt = {
                    "sampler_namespace": HELDOUT_COMPOSITE_SAMPLER_NAMESPACE,
                    "method": "deterministic_rejection_on_full_composite_map_split",
                    "base_seed": int(seed),
                    "derived_depth_seed": depth_seed,
                    "word_depth": depth,
                    "requested_split": split,
                    "requested_examples": examples_per_depth,
                    "maximum_candidates": maximum_candidates,
                    "candidate_examples_drawn": drawn,
                    "accepted_examples": accepted,
                    "rejected_examples": rejected,
                    "candidate_composite_split_counts": candidate_counts,
                    "accepted_composite_split_counts": accepted_counts,
                    "rejected_composite_split_counts": rejected_counts,
                    "primitive_map_split_counts": primitive_counts,
                    "primitive_split_violations": 0,
                    "target_consistency_violations": target_consistency_violations,
                    "accepted_unique_composite_maps": len(accepted_unique_maps),
                    "acceptance_rate": accepted / drawn,
                    "candidate_accounting_exact": sum(candidate_counts.values()) == drawn,
                    "acceptance_accounting_exact": sum(accepted_counts.values()) == accepted,
                    "rejection_accounting_exact": sum(rejected_counts.values()) == rejected,
                    "only_accepted_examples_evaluated": True,
                    "model_evaluated_examples": accepted,
                    "model_evaluated_rejected_examples": 0,
                    "candidate_stream_sha256": candidate_digest.hexdigest(),
                    "accepted_examples_sha256": accepted_digest.hexdigest(),
                }
                by_depth[str(depth)] = {
                    "examples": accepted,
                    "correct": correct,
                    "endpoint_accuracy": correct / accepted,
                    "finite_logits_fraction": finite_logits / accepted,
                    "acceptance_receipt": receipt,
                }
                for name in COORDINATE_SPLITS:
                    overall_candidate_counts[name] += candidate_counts[name]
                    overall_primitive_counts[name] += primitive_counts[name]
                overall_correct += correct
                overall_finite += finite_logits
                overall_drawn += drawn
                overall_accepted += accepted
                overall_digest.update(depth.to_bytes(8, "big", signed=False))
                overall_digest.update(bytes.fromhex(candidate_digest.hexdigest()))
                overall_digest.update(bytes.fromhex(accepted_digest.hexdigest()))
    finally:
        model.train(was_training)

    return {
        "available": True,
        "metric": "split_conditioned_full_composite_final_action_accuracy",
        "family": family,
        "coordinate_split": split,
        "primitive_map_split": split,
        "composite_target_map_split": split,
        "primitive_split_enforced": True,
        "full_composite_split_enforced": True,
        "requested_depths": list(requested_depths),
        "evaluated_depths": list(evaluated_depths),
        "examples_per_depth": examples_per_depth,
        "endpoint_accuracy": overall_correct / overall_accepted,
        "finite_logits_fraction": overall_finite / overall_accepted,
        "by_depth": by_depth,
        "acceptance_receipt": {
            "sampler_namespace": HELDOUT_COMPOSITE_SAMPLER_NAMESPACE,
            "base_seed": int(seed),
            "batch_size": batch_size,
            "maximum_candidate_multiplier": maximum_candidate_multiplier,
            "candidate_examples_drawn": overall_drawn,
            "accepted_examples": overall_accepted,
            "rejected_examples": overall_drawn - overall_accepted,
            "acceptance_rate": overall_accepted / overall_drawn,
            "candidate_composite_split_counts": overall_candidate_counts,
            "accepted_composite_split_counts": {
                name: overall_accepted if name == split else 0
                for name in COORDINATE_SPLITS
            },
            "primitive_map_split_counts": overall_primitive_counts,
            "all_primitive_maps_in_requested_split": (
                overall_primitive_counts[split] == overall_drawn * N_OPERATORS
            ),
            "all_accepted_full_composites_in_requested_split": (
                overall_candidate_counts[split] == overall_accepted
            ),
            "only_accepted_examples_evaluated": True,
            "model_evaluated_examples": overall_accepted,
            "model_evaluated_rejected_examples": 0,
            "depth_receipts_sha256": overall_digest.hexdigest(),
        },
    }


# Backward-compatible descriptive alias.  The canonical name above is more
# careful: the assay conditions a finite-map final action on a frozen split; it
# does not certify a globally novel abstract group element.
heldout_composite_word_metrics = split_conditioned_final_action_metrics


__all__ = [
    "HELDOUT_COMPOSITE_SAMPLER_NAMESPACE",
    "compose_full_word_maps",
    "heldout_composite_word_metrics",
    "split_conditioned_final_action_metrics",
]
