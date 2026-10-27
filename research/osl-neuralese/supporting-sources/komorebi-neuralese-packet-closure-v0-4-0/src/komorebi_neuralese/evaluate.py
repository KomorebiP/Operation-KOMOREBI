from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import torch
from torch.nn import functional as F

from .algebra import D4_EQUIVALENT_PATHS, D4_RELATIONS, N_STATES, canonical_maps
from .data import EpisodeBatch, EpisodeGenerator
from .models import LinearHyperOperatorRNN, RecurrentOperatorModel


@dataclass(frozen=True)
class EvaluationConfig:
    examples_per_length: int = 2048
    intervention_examples: int = 2048
    batch_size: int = 512
    lengths: tuple[int, ...] = (1, 2, 3, 4, 6, 8, 10, 12)


def _chunks(total: int, size: int) -> Iterable[int]:
    remaining = total
    while remaining:
        current = min(size, remaining)
        yield current
        remaining -= current


def apply_slots_torch(maps: torch.Tensor, start: torch.Tensor, slots: torch.Tensor) -> torch.Tensor:
    current = start.clone()
    rows = torch.arange(start.shape[0], device=start.device)
    for t in range(slots.shape[1]):
        selected = maps[rows, slots[:, t]]
        current = selected[rows, current]
    return current


def accuracy_by_length(
    model: torch.nn.Module,
    family: str,
    lengths: tuple[int, ...],
    examples_per_length: int,
    batch_size: int,
    seed: int,
    device: torch.device,
) -> dict[str, float]:
    generator = EpisodeGenerator(seed)
    model.eval()
    results: dict[str, float] = {}
    with torch.no_grad():
        for length in lengths:
            correct = 0
            count = 0
            for current_batch in _chunks(examples_per_length, batch_size):
                batch = generator.sample(current_batch, length, family=family).to(device)
                logits = model(batch.tables, batch.op_slots, batch.start)
                correct += int((logits.argmax(dim=1) == batch.target).sum())
                count += current_batch
            results[str(length)] = correct / count
    return results


def relation_metrics(
    model: torch.nn.Module,
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    generator = EpisodeGenerator(seed)
    output: dict[str, Any] = {}
    model.eval()
    with torch.no_grad():
        for name, word in D4_RELATIONS.items():
            correct = 0
            count = 0
            hidden_l2: list[float] = []
            ambient_residual: list[float] = []
            for current_batch in _chunks(examples, batch_size):
                batch = generator.sample(current_batch, 0, family="d4").to(device)
                slots = EpisodeGenerator.slots_for_word(batch.canonical_to_slot, word)
                if isinstance(model, RecurrentOperatorModel):
                    trace = model.run(batch.tables, slots, batch.start)
                    logits = trace.logits
                    h0, h1 = trace.hidden[0], trace.hidden[-1]
                    residual = (h1 - h0).norm(dim=1) / h0.norm(dim=1).clamp_min(1e-8)
                    hidden_l2.extend(residual.cpu().tolist())
                    if isinstance(model, LinearHyperOperatorRNN):
                        codes = trace.operator_codes
                        rows = torch.arange(current_batch, device=device)
                        matrices = [codes[rows, batch.canonical_to_slot[:, op]] for op in word]
                        product = torch.eye(model.hidden_dim, device=device).expand(current_batch, -1, -1).clone()
                        for matrix in matrices:
                            product = torch.bmm(matrix, product)
                        identity = torch.eye(model.hidden_dim, device=device).expand_as(product)
                        value = (product - identity).flatten(1).norm(dim=1) / identity.flatten(1).norm(dim=1)
                        ambient_residual.extend(value.cpu().tolist())
                else:
                    logits = model(batch.tables, slots, batch.start)
                correct += int((logits.argmax(dim=1) == batch.start).sum())
                count += current_batch
            output[name] = {
                "endpoint_accuracy": correct / count,
                "hidden_return_normalized_l2_mean": float(np.mean(hidden_l2)) if hidden_l2 else None,
                "hidden_return_normalized_l2_median": float(np.median(hidden_l2)) if hidden_l2 else None,
                "ambient_matrix_relation_residual_mean": float(np.mean(ambient_residual)) if ambient_residual else None,
            }
    return output


def equivalent_path_metrics(
    model: torch.nn.Module,
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    generator = EpisodeGenerator(seed)
    output: dict[str, Any] = {}
    model.eval()
    with torch.no_grad():
        for name, (left_word, right_word) in D4_EQUIVALENT_PATHS.items():
            agreement = 0
            both_exact = 0
            count = 0
            cosines: list[float] = []
            normalized_l2: list[float] = []
            for current_batch in _chunks(examples, batch_size):
                batch = generator.sample(current_batch, 0, family="d4").to(device)
                left_slots = EpisodeGenerator.slots_for_word(batch.canonical_to_slot, left_word)
                right_slots = EpisodeGenerator.slots_for_word(batch.canonical_to_slot, right_word)
                target = apply_slots_torch(batch.maps, batch.start, left_slots)
                if isinstance(model, RecurrentOperatorModel):
                    left = model.run(batch.tables, left_slots, batch.start)
                    right = model.run(batch.tables, right_slots, batch.start)
                    left_hidden, right_hidden = left.hidden[-1], right.hidden[-1]
                    cosines.extend(F.cosine_similarity(left_hidden, right_hidden, dim=1).cpu().tolist())
                    scale = left_hidden.norm(dim=1).clamp_min(1e-8)
                    normalized_l2.extend(((left_hidden - right_hidden).norm(dim=1) / scale).cpu().tolist())
                    left_logits, right_logits = left.logits, right.logits
                else:
                    left_logits = model(batch.tables, left_slots, batch.start)
                    right_logits = model(batch.tables, right_slots, batch.start)
                left_prediction = left_logits.argmax(dim=1)
                right_prediction = right_logits.argmax(dim=1)
                agreement += int((left_prediction == right_prediction).sum())
                both_exact += int(((left_prediction == target) & (right_prediction == target)).sum())
                count += current_batch
            output[name] = {
                "output_agreement": agreement / count,
                "both_paths_exact": both_exact / count,
                "hidden_cosine_mean": float(np.mean(cosines)) if cosines else None,
                "hidden_normalized_l2_mean": float(np.mean(normalized_l2)) if normalized_l2 else None,
            }
    return output


def _norm_matched_random(reference: torch.Tensor, generator: torch.Generator) -> torch.Tensor:
    random = torch.randn(reference.shape, generator=generator, device=reference.device, dtype=reference.dtype)
    flat_random = random.flatten(1)
    flat_reference = reference.flatten(1)
    random_norm = flat_random.norm(dim=1).clamp_min(1e-8)
    reference_norm = flat_reference.norm(dim=1)
    shape = (-1,) + (1,) * (reference.ndim - 1)
    return random * (reference_norm / random_norm).reshape(shape)


def _angle_matched_random_state(
    recipient: torch.Tensor,
    donor: torch.Tensor,
    generator: torch.Generator,
    *,
    endpoint_tolerance: float = 1e-6,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Sample unit-sphere controls at the donor's exact recipient angle.

    The random direction is Haar-isotropic in the tangent space orthogonal to
    the recipient ray.  Near-coincident and near-antipodal donor rays are
    reported as undefined because their matched sphere degenerates to the
    donor itself.
    """

    if recipient.shape != donor.shape or recipient.ndim != 2:
        raise ValueError("recipient and donor must share shape (batch, hidden)")
    recipient_norm = recipient.norm(dim=1, keepdim=True).clamp_min(1e-12)
    donor_norm = donor.norm(dim=1, keepdim=True).clamp_min(1e-12)
    recipient_unit = recipient / recipient_norm
    donor_unit = donor / donor_norm
    target_cosine = (recipient_unit * donor_unit).sum(dim=1).clamp(-1.0, 1.0)
    sine = (1.0 - target_cosine.square()).clamp_min(0.0).sqrt()
    defined = sine > float(endpoint_tolerance)

    random = torch.randn(
        recipient.shape,
        generator=generator,
        device=recipient.device,
        dtype=recipient.dtype,
    )
    tangent = random - (random * recipient_unit).sum(dim=1, keepdim=True) * recipient_unit
    tangent_norm = tangent.norm(dim=1, keepdim=True)
    # A deterministic fallback prevents an accidental zero tangent from
    # introducing NaNs without concealing a degenerate donor angle.
    basis_index = recipient_unit.abs().argmin(dim=1)
    basis = torch.zeros_like(recipient_unit)
    basis.scatter_(1, basis_index[:, None], 1.0)
    fallback = basis - (basis * recipient_unit).sum(dim=1, keepdim=True) * recipient_unit
    tangent = torch.where(tangent_norm > 1e-10, tangent, fallback)
    tangent_unit = tangent / tangent.norm(dim=1, keepdim=True).clamp_min(1e-12)
    control_unit = (
        target_cosine[:, None] * recipient_unit
        + sine[:, None] * tangent_unit
    )
    control = control_unit * donor_norm
    observed_cosine = (
        recipient_unit
        * (control / control.norm(dim=1, keepdim=True).clamp_min(1e-12))
    ).sum(dim=1)
    norm_error = (control.norm(dim=1) - donor.norm(dim=1)).abs()
    cosine_error = (observed_cosine - target_cosine).abs()
    return control, {
        "defined_fraction": float(defined.to(torch.float64).mean()),
        "maximum_norm_error": float(norm_error.max()),
        "maximum_cosine_error": float(cosine_error.max()),
        "minimum_target_sine": float(sine.min()),
    }


def _relative_conjugacy_matched_orthogonal_control(
    original: torch.Tensor,
    alternate: torch.Tensor,
    generator: torch.Generator,
    *,
    separation_tolerance: float = 1e-5,
    attempts: int = 4,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Construct an orthogonal control preserving relative conjugacy data.

    For orthogonal original ``O`` and alternate ``A``, let ``R=A O^T`` and
    return ``C=(S R S^T) O`` for a random orthogonal ``S``.  This preserves
    the determinant component, spectrum of the relative intervention, and
    Frobenius chord distance from ``O`` while normally changing its task
    semantics.  Central relative transforms are explicitly reported as
    undefined rather than counted as controls.
    """

    if original.shape != alternate.shape or original.ndim != 3:
        raise ValueError("original and alternate must share shape (batch, d, d)")
    if original.shape[-1] != original.shape[-2]:
        raise ValueError("operator controls require square matrices")
    batch, dimension, _ = original.shape
    relative = alternate @ original.transpose(-1, -2)
    chosen = alternate.clone()
    defined = torch.zeros(batch, dtype=torch.bool, device=original.device)
    separation = torch.zeros(batch, dtype=original.dtype, device=original.device)
    for _ in range(int(attempts)):
        noise = torch.randn(
            (batch, dimension, dimension),
            generator=generator,
            device=original.device,
            dtype=original.dtype,
        )
        orthogonal, triangular = torch.linalg.qr(noise)
        signs = torch.where(
            torch.diagonal(triangular, dim1=-2, dim2=-1) >= 0,
            torch.ones(batch, dimension, device=original.device, dtype=original.dtype),
            -torch.ones(batch, dimension, device=original.device, dtype=original.dtype),
        )
        orthogonal = orthogonal * signs.unsqueeze(-2)
        candidate = (
            orthogonal @ relative @ orthogonal.transpose(-1, -2) @ original
        )
        candidate_separation = torch.linalg.matrix_norm(
            candidate - alternate, ord="fro", dim=(-2, -1)
        )
        accept = (~defined) & (candidate_separation > float(separation_tolerance))
        chosen = torch.where(accept[:, None, None], candidate, chosen)
        separation = torch.where(accept, candidate_separation, separation)
        defined |= accept

    identity = torch.eye(dimension, dtype=original.dtype, device=original.device)
    original_distance = torch.linalg.matrix_norm(
        alternate - original, ord="fro", dim=(-2, -1)
    )
    control_distance = torch.linalg.matrix_norm(
        chosen - original, ord="fro", dim=(-2, -1)
    )
    orthogonality = torch.linalg.matrix_norm(
        chosen.transpose(-1, -2) @ chosen - identity,
        ord="fro",
        dim=(-2, -1),
    )
    determinant_match = (
        torch.sign(torch.linalg.det(chosen))
        == torch.sign(torch.linalg.det(alternate))
    )
    return chosen, {
        "defined_fraction": float(defined.to(torch.float64).mean()),
        "maximum_chord_distance_error": float(
            (control_distance - original_distance).abs().max()
        ),
        "maximum_orthogonality_defect": float(orthogonality.max()),
        "determinant_component_match_fraction": float(
            determinant_match.to(torch.float64).mean()
        ),
        "minimum_separation_from_alternate": float(separation.min()),
    }


def _select_cross_context_operator_control_slots(
    original_tables: torch.Tensor,
    alternate_tables: torch.Tensor,
    candidate_tables: torch.Tensor,
    base_choices: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    """Select a balanced independent slot outside both primary semantics.

    Selection is model-independent: the frozen row-balanced base slot is kept
    unless its concrete permutation table equals either the original or the
    alternate table in the primary episode.  With exactly two visible slots,
    a colliding base choice is flipped once.  A row with no admissible slot is
    rejected rather than silently admitting a semantic-table collision.
    """

    if original_tables.ndim != 2 or alternate_tables.shape != original_tables.shape:
        raise ValueError("primary operator tables must share shape (batch, states)")
    if (
        candidate_tables.ndim != 3
        or candidate_tables.shape[0] != original_tables.shape[0]
        or candidate_tables.shape[1] != 2
        or candidate_tables.shape[2] != original_tables.shape[1]
    ):
        raise ValueError(
            "cross-context candidates must have shape (batch, 2, states)"
        )
    if base_choices.shape != (original_tables.shape[0],):
        raise ValueError("base choices must have shape (batch,)")
    if base_choices.dtype == torch.bool or base_choices.is_floating_point():
        raise TypeError("base choices must be integer slot indices")
    if bool(((base_choices < 0) | (base_choices > 1)).any()):
        raise ValueError("base choices must contain only the two visible slots")

    rows = torch.arange(original_tables.shape[0], device=candidate_tables.device)
    original_collisions = (
        candidate_tables == original_tables[:, None, :]
    ).all(dim=-1)
    alternate_collisions = (
        candidate_tables == alternate_tables[:, None, :]
    ).all(dim=-1)
    excluded = original_collisions | alternate_collisions
    base_original_collision = original_collisions[rows, base_choices]
    base_alternate_collision = alternate_collisions[rows, base_choices]
    selected_choices = torch.where(
        excluded[rows, base_choices], 1 - base_choices, base_choices
    )
    selected_original_collision = original_collisions[rows, selected_choices]
    selected_alternate_collision = alternate_collisions[rows, selected_choices]
    if bool((selected_original_collision | selected_alternate_collision).any()):
        raise RuntimeError(
            "independent cross-context control has no slot outside both "
            "primary operator tables"
        )
    return selected_choices, {
        "base_original_table_collision": base_original_collision,
        "base_alternate_table_collision": base_alternate_collision,
        "selected_original_table_collision": selected_original_collision,
        "selected_alternate_table_collision": selected_alternate_collision,
    }


def _slice_episode_batch(batch: EpisodeBatch, start: int, stop: int) -> EpisodeBatch:
    """Slice one episode bank without regenerating any evaluation content."""

    return EpisodeBatch(
        tables=batch.tables[start:stop],
        maps=batch.maps[start:stop],
        op_slots=batch.op_slots[start:stop],
        canonical_ops=batch.canonical_ops[start:stop],
        start=batch.start[start:stop],
        target=batch.target[start:stop],
        intermediates=batch.intermediates[start:stop],
        canonical_to_slot=batch.canonical_to_slot[start:stop],
        phi=batch.phi[start:stop],
        family=batch.family,
    )


def _validate_intervention_bank(
    batch: EpisodeBatch,
    *,
    examples: int,
    length: int,
    name: str,
) -> None:
    """Fail closed on malformed or internally inconsistent D4 banks."""

    if not isinstance(batch, EpisodeBatch):
        raise TypeError(f"{name} must be an EpisodeBatch")
    if batch.family != "d4":
        raise ValueError(f"{name} must contain D4 episodes")
    expected_shapes = {
        "tables": (examples, 2, N_STATES, N_STATES),
        "maps": (examples, 2, N_STATES),
        "op_slots": (examples, length),
        "canonical_ops": (examples, length),
        "start": (examples,),
        "target": (examples,),
        "intermediates": (examples, length),
        "canonical_to_slot": (examples, 2),
        "phi": (examples, N_STATES),
    }
    for field, shape in expected_shapes.items():
        tensor = getattr(batch, field)
        if not isinstance(tensor, torch.Tensor) or tuple(tensor.shape) != shape:
            raise ValueError(f"{name}.{field} does not have shape {shape}")
    if not bool(torch.isfinite(batch.tables).all()):
        raise ValueError(f"{name}.tables contains non-finite values")
    expected_tables = F.one_hot(batch.maps.to(torch.long), N_STATES).to(
        dtype=batch.tables.dtype
    )
    if not torch.equal(batch.tables.cpu(), expected_tables.cpu()):
        raise ValueError(f"{name}.tables is not the one-hot realization of maps")
    rows = torch.arange(examples)
    state_order = torch.arange(N_STATES).expand(examples, -1)
    slot_order = torch.arange(2).expand(examples, -1)
    if not torch.equal(torch.sort(batch.phi.cpu(), dim=1).values, state_order):
        raise ValueError(f"{name}.phi rows are not state permutations")
    if not torch.equal(
        torch.sort(batch.canonical_to_slot.cpu(), dim=1).values, slot_order
    ):
        raise ValueError(f"{name}.canonical_to_slot rows are not slot permutations")
    if bool(((batch.canonical_ops < 0) | (batch.canonical_ops >= 2)).any()):
        raise ValueError(f"{name}.canonical_ops contains an invalid action")
    for field in ("start", "target", "intermediates", "maps"):
        tensor = getattr(batch, field)
        if bool(((tensor < 0) | (tensor >= N_STATES)).any()):
            raise ValueError(f"{name}.{field} contains an invalid state")
    mapped_slots = torch.gather(batch.canonical_to_slot, 1, batch.canonical_ops)
    if not torch.equal(mapped_slots, batch.op_slots):
        raise ValueError(f"{name}.op_slots disagrees with canonical_to_slot")
    canonical = torch.from_numpy(canonical_maps("d4")).to(torch.long)
    phi = batch.phi.to(torch.long)
    for action in range(2):
        slots = batch.canonical_to_slot[:, action]
        selected = batch.maps[rows, slots]
        actual = torch.gather(selected, 1, phi)
        expected = phi[:, canonical[action]]
        if not torch.equal(actual, expected):
            raise ValueError(f"{name}.maps does not realize D4 under phi")
    current = batch.start.clone()
    for step in range(length):
        selected = batch.maps[rows, batch.op_slots[:, step]]
        current = selected[rows, current]
        if not torch.equal(current, batch.intermediates[:, step]):
            raise ValueError(f"{name}.intermediates contains an inexact state")
    if not torch.equal(current, batch.target):
        raise ValueError(f"{name} contains inexact terminal targets")


def intervention_metrics(
    model: torch.nn.Module,
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device,
    length: int = 8,
    split: int = 4,
    operator_step: int = 3,
    episode_batch: EpisodeBatch | None = None,
    operator_control_batch: EpisodeBatch | None = None,
    control_seed: int | None = None,
) -> dict[str, Any]:
    if not isinstance(model, RecurrentOperatorModel):
        return {"available": False, "reason": "model is nonrecurrent"}
    episode_bank_was_supplied = episode_batch is not None
    operator_control_bank_was_supplied = operator_control_batch is not None
    if episode_batch is None:
        episode_batch = EpisodeGenerator(seed).sample(examples, length, family="d4")
    if operator_control_batch is None:
        operator_control_batch = EpisodeGenerator(seed + 1).sample(
            examples, length, family="d4"
        )
    for name, candidate in (
        ("episode_batch", episode_batch),
        ("operator_control_batch", operator_control_batch),
    ):
        _validate_intervention_bank(
            candidate,
            examples=examples,
            length=length,
            name=name,
        )
    if all(
        torch.equal(getattr(episode_batch, field), getattr(operator_control_batch, field))
        for field in (
            "tables",
            "maps",
            "op_slots",
            "canonical_ops",
            "start",
            "canonical_to_slot",
            "phi",
        )
    ):
        raise ValueError("primary and cross-context operator-control banks are identical")
    resolved_control_seed = seed + 77 if control_seed is None else int(control_seed)
    torch_rng = torch.Generator(device=device).manual_seed(resolved_control_seed)
    counts = {
        "state_patch": 0,
        "random_state_patch": 0,
        "angle_matched_state_control": 0,
        "reachable_state_control": 0,
        "random_absolute_state": 0,
        "zero_state_lesion_original": 0,
        "operator_patch": 0,
        "random_operator_patch": 0,
        "relative_conjugacy_operator_control": 0,
        "cross_context_operator_control": 0,
        "native_original": 0,
    }
    defined_counts = {name: 0 for name in counts}
    state_geometry_rows: list[dict[str, float]] = []
    operator_geometry_rows: list[dict[str, float]] = []
    state_transition_eligible = 0
    operator_transition_eligible = 0
    state_transition_counts = {
        "state_patch": 0,
        "angle_matched_state_control": 0,
        "reachable_state_control": 0,
        "random_state_patch": 0,
    }
    operator_transition_counts = {
        "operator_patch": 0,
        "random_operator_patch": 0,
        "relative_conjugacy_operator_control": 0,
        "cross_context_operator_control": 0,
    }
    state_distinct_targets = 0
    operator_distinct_targets = 0
    polar_operator_control_available = getattr(model, "model_name", None) == "polar_isometric_table"
    total = 0
    offset = 0
    model.eval()
    with torch.no_grad():
        for current_batch in _chunks(examples, batch_size):
            batch = _slice_episode_batch(
                episode_batch, offset, offset + current_batch
            ).to(device)
            independent_batch = _slice_episode_batch(
                operator_control_batch, offset, offset + current_batch
            ).to(device)
            rows = torch.arange(current_batch, device=device)
            original_slots_for_control = batch.op_slots[:, operator_step]
            alternate_slots_for_control = 1 - batch.op_slots[:, operator_step]
            original_tables_for_control = batch.maps[
                rows, original_slots_for_control
            ]
            alternate_tables_for_control = batch.maps[
                rows, alternate_slots_for_control
            ]
            base_cross_choice = (
                torch.arange(
                    offset,
                    offset + current_batch,
                    device=device,
                    dtype=torch.long,
                )
                % independent_batch.maps.shape[1]
            )
            cross_choice, cross_collision_receipt = (
                _select_cross_context_operator_control_slots(
                    original_tables_for_control,
                    alternate_tables_for_control,
                    independent_batch.maps,
                    base_cross_choice,
                )
            )
            prefix = batch.op_slots[:, :split]
            suffix = batch.op_slots[:, split:]
            donor_start = (batch.start + torch.randint(1, N_STATES, (current_batch,), generator=torch_rng, device=device)) % N_STATES

            donor_prefix = model.run(batch.tables, prefix, donor_start)
            recipient_prefix = model.run(batch.tables, prefix, batch.start)
            codes = donor_prefix.operator_codes
            patched = model.continue_from_hidden(donor_prefix.hidden[-1], codes, suffix)
            donor_mid = apply_slots_torch(batch.maps, donor_start, prefix)
            donor_expected = apply_slots_torch(batch.maps, donor_mid, suffix)
            patched_defined = torch.isfinite(patched.logits).all(dim=1)
            patched_prediction = patched.logits.argmax(dim=1)
            defined_counts["state_patch"] += int(patched_defined.sum())
            counts["state_patch"] += int(
                (patched_defined & (patched_prediction == donor_expected)).sum()
            )

            angle_control, angle_geometry = _angle_matched_random_state(
                recipient_prefix.hidden[-1], donor_prefix.hidden[-1], torch_rng
            )
            angle_result = model.continue_from_hidden(angle_control, codes, suffix)
            angle_defined = torch.isfinite(angle_result.logits).all(dim=1)
            angle_prediction = angle_result.logits.argmax(dim=1)
            defined_counts["angle_matched_state_control"] += int(
                angle_defined.sum()
            )
            counts["angle_matched_state_control"] += int(
                (angle_defined & (angle_prediction == donor_expected)).sum()
            )
            state_geometry_rows.append(angle_geometry)

            # This control remains on the model's reachable same-prefix state
            # set but carries the wrong semantic state.  Its start is
            # deterministically distinct from both recipient and donor.
            reachable_control_start = (donor_start + 1) % N_STATES
            reachable_control_start = torch.where(
                reachable_control_start == batch.start,
                (reachable_control_start + 1) % N_STATES,
                reachable_control_start,
            )
            if bool(((reachable_control_start == donor_start) | (reachable_control_start == batch.start)).any()):
                raise RuntimeError("reachable state control did not exclude recipient and donor")
            reachable_prefix = model.run(batch.tables, prefix, reachable_control_start)
            reachable_expected = apply_slots_torch(
                batch.maps, reachable_control_start, batch.op_slots
            )
            if bool((reachable_expected == donor_expected).any()):
                raise RuntimeError("reachable state control shares the donor counterfactual target")
            reachable_result = model.continue_from_hidden(
                reachable_prefix.hidden[-1], codes, suffix
            )
            reachable_defined = torch.isfinite(reachable_result.logits).all(dim=1)
            reachable_prediction = reachable_result.logits.argmax(dim=1)
            defined_counts["reachable_state_control"] += int(
                reachable_defined.sum()
            )
            counts["reachable_state_control"] += int(
                (reachable_defined & (reachable_prediction == donor_expected)).sum()
            )

            # Strong control: apply a random displacement from the recipient state with
            # exactly the donor-minus-recipient displacement norm. This matches the
            # intervention geometry without inserting the causally correct state.
            state_delta = donor_prefix.hidden[-1] - recipient_prefix.hidden[-1]
            random_delta = _norm_matched_random(state_delta, torch_rng)
            random_hidden = recipient_prefix.hidden[-1] + random_delta
            random_patched = model.continue_from_hidden(random_hidden, codes, suffix)
            random_state_defined = torch.isfinite(random_patched.logits).all(dim=1)
            random_state_prediction = random_patched.logits.argmax(dim=1)
            defined_counts["random_state_patch"] += int(random_state_defined.sum())
            counts["random_state_patch"] += int(
                (random_state_defined & (random_state_prediction == donor_expected)).sum()
            )

            # Retain the weaker off-manifold absolute-vector control as a secondary diagnostic.
            random_absolute = _norm_matched_random(donor_prefix.hidden[-1], torch_rng)
            random_absolute_result = model.continue_from_hidden(random_absolute, codes, suffix)
            random_absolute_defined = torch.isfinite(
                random_absolute_result.logits
            ).all(dim=1)
            defined_counts["random_absolute_state"] += int(
                random_absolute_defined.sum()
            )
            counts["random_absolute_state"] += int(
                (
                    random_absolute_defined
                    & (random_absolute_result.logits.argmax(dim=1) == donor_expected)
                ).sum()
            )

            zero = torch.zeros_like(recipient_prefix.hidden[-1])
            zero_result = model.continue_from_hidden(zero, recipient_prefix.operator_codes, suffix)
            zero_defined = torch.isfinite(zero_result.logits).all(dim=1)
            defined_counts["zero_state_lesion_original"] += int(zero_defined.sum())
            counts["zero_state_lesion_original"] += int(
                (zero_defined & (zero_result.logits.argmax(dim=1) == batch.target)).sum()
            )

            native = model.run(batch.tables, batch.op_slots, batch.start)
            native_defined = torch.isfinite(native.logits).all(dim=1)
            native_prediction = native.logits.argmax(dim=1)
            native_correct = native_defined & (native_prediction == batch.target)
            defined_counts["native_original"] += int(native_defined.sum())
            counts["native_original"] += int(native_correct.sum())
            state_distinct = donor_expected != batch.target
            state_distinct_targets += int(state_distinct.sum())
            state_eligible = native_correct & state_distinct
            state_transition_eligible += int(state_eligible.sum())
            state_transition_counts["state_patch"] += int(
                (
                    state_eligible
                    & patched_defined
                    & (patched_prediction == donor_expected)
                ).sum()
            )
            state_transition_counts["angle_matched_state_control"] += int(
                (
                    state_eligible
                    & angle_defined
                    & (angle_prediction == donor_expected)
                ).sum()
            )
            state_transition_counts["reachable_state_control"] += int(
                (
                    state_eligible
                    & reachable_defined
                    & (reachable_prediction == donor_expected)
                ).sum()
            )
            state_transition_counts["random_state_patch"] += int(
                (
                    state_eligible
                    & random_state_defined
                    & (random_state_prediction == donor_expected)
                ).sum()
            )

            independent_trace = model.run(
                independent_batch.tables,
                independent_batch.op_slots,
                independent_batch.start,
            )

            operator_codes = native.operator_codes
            independent_codes = independent_trace.operator_codes
            if operator_codes is None or independent_codes is None:
                raise TypeError("recurrent operator intervention requires operator codes")
            hidden = model.initial_hidden(batch.start)
            counterfactual_slots = batch.op_slots.clone()
            counterfactual_slots[:, operator_step] = 1 - counterfactual_slots[:, operator_step]
            random_hidden_operator = model.initial_hidden(batch.start)
            relative_control_hidden = model.initial_hidden(batch.start)
            cross_context_hidden = model.initial_hidden(batch.start)
            for t in range(length):
                original_code = operator_codes[rows, batch.op_slots[:, t]]
                if t == operator_step:
                    alternate_code = operator_codes[rows, 1 - batch.op_slots[:, t]]
                    hidden = model.step_hidden(hidden, alternate_code)
                    delta = alternate_code - original_code
                    random_delta = _norm_matched_random(delta, torch_rng)
                    random_hidden_operator = model.step_hidden(random_hidden_operator, original_code + random_delta)
                    cross_candidates = independent_codes
                    cross_original_distances = torch.linalg.matrix_norm(
                        cross_candidates - original_code[:, None],
                        ord="fro",
                        dim=(-2, -1),
                    )
                    cross_alternate_distances = torch.linalg.matrix_norm(
                        cross_candidates - alternate_code[:, None],
                        ord="fro",
                        dim=(-2, -1),
                    )
                    cross_context_code = cross_candidates[rows, cross_choice]
                    cross_separation_from_original = cross_original_distances[
                        rows, cross_choice
                    ]
                    cross_separation_from_alternate = cross_alternate_distances[
                        rows, cross_choice
                    ]
                    cross_defined = (
                        (cross_separation_from_original > 1e-5)
                        & (cross_separation_from_alternate > 1e-5)
                    )
                    cross_context_hidden = model.step_hidden(
                        cross_context_hidden, cross_context_code
                    )
                    if polar_operator_control_available:
                        relative_control, relative_geometry = (
                            _relative_conjugacy_matched_orthogonal_control(
                                original_code, alternate_code, torch_rng
                            )
                        )
                        relative_control_hidden = model.step_hidden(
                            relative_control_hidden, relative_control
                        )
                        relative_geometry["cross_context_defined_fraction"] = float(
                            cross_defined.to(torch.float64).mean()
                        )
                        relative_geometry[
                            "minimum_cross_context_separation_from_original"
                        ] = float(cross_separation_from_original.min())
                        relative_geometry[
                            "minimum_cross_context_separation_from_alternate"
                        ] = float(cross_separation_from_alternate.min())
                        relative_geometry[
                            "cross_context_base_original_table_collision_count"
                        ] = int(
                            cross_collision_receipt[
                                "base_original_table_collision"
                            ].sum()
                        )
                        relative_geometry[
                            "cross_context_base_alternate_table_collision_count"
                        ] = int(
                            cross_collision_receipt[
                                "base_alternate_table_collision"
                            ].sum()
                        )
                        relative_geometry[
                            "cross_context_selected_original_table_collision_count"
                        ] = int(
                            cross_collision_receipt[
                                "selected_original_table_collision"
                            ].sum()
                        )
                        relative_geometry[
                            "cross_context_selected_alternate_table_collision_count"
                        ] = int(
                            cross_collision_receipt[
                                "selected_alternate_table_collision"
                            ].sum()
                        )
                        operator_geometry_rows.append(relative_geometry)
                    else:
                        relative_control_hidden = model.step_hidden(
                            relative_control_hidden, original_code + random_delta
                        )
                else:
                    hidden = model.step_hidden(hidden, original_code)
                    random_hidden_operator = model.step_hidden(random_hidden_operator, original_code)
                    relative_control_hidden = model.step_hidden(
                        relative_control_hidden, original_code
                    )
                    cross_context_hidden = model.step_hidden(
                        cross_context_hidden, original_code
                    )
            expected_counterfactual = apply_slots_torch(batch.maps, batch.start, counterfactual_slots)
            operator_logits = model.decode_hidden(hidden)
            random_operator_logits = model.decode_hidden(random_hidden_operator)
            relative_control_logits = model.decode_hidden(relative_control_hidden)
            cross_context_logits = model.decode_hidden(cross_context_hidden)
            operator_prediction = operator_logits.argmax(dim=1)
            random_operator_prediction = random_operator_logits.argmax(dim=1)
            relative_control_prediction = relative_control_logits.argmax(dim=1)
            cross_context_prediction = cross_context_logits.argmax(dim=1)
            operator_defined = torch.isfinite(operator_logits).all(dim=1)
            random_operator_defined = torch.isfinite(random_operator_logits).all(dim=1)
            relative_control_defined = torch.isfinite(relative_control_logits).all(dim=1)
            cross_context_defined_output = torch.isfinite(cross_context_logits).all(dim=1)
            defined_counts["operator_patch"] += int(operator_defined.sum())
            defined_counts["random_operator_patch"] += int(
                random_operator_defined.sum()
            )
            defined_counts["relative_conjugacy_operator_control"] += int(
                relative_control_defined.sum()
            )
            defined_counts["cross_context_operator_control"] += int(
                cross_context_defined_output.sum()
            )
            counts["operator_patch"] += int(
                (operator_defined & (operator_prediction == expected_counterfactual)).sum()
            )
            counts["random_operator_patch"] += int(
                (
                    random_operator_defined
                    & (random_operator_prediction == expected_counterfactual)
                ).sum()
            )
            counts["relative_conjugacy_operator_control"] += int(
                (
                    relative_control_defined
                    & (relative_control_prediction == expected_counterfactual)
                ).sum()
            )
            counts["cross_context_operator_control"] += int(
                (
                    cross_context_defined_output
                    & (cross_context_prediction == expected_counterfactual)
                ).sum()
            )
            operator_distinct = expected_counterfactual != batch.target
            operator_distinct_targets += int(operator_distinct.sum())
            operator_eligible = native_correct & operator_distinct
            operator_transition_eligible += int(operator_eligible.sum())
            operator_transition_counts["operator_patch"] += int(
                (
                    operator_eligible
                    & operator_defined
                    & (operator_prediction == expected_counterfactual)
                ).sum()
            )
            operator_transition_counts["random_operator_patch"] += int(
                (
                    operator_eligible
                    & random_operator_defined
                    & (random_operator_prediction == expected_counterfactual)
                ).sum()
            )
            operator_transition_counts[
                "relative_conjugacy_operator_control"
            ] += int(
                (
                    operator_eligible
                    & relative_control_defined
                    & (relative_control_prediction == expected_counterfactual)
                ).sum()
            )
            operator_transition_counts["cross_context_operator_control"] += int(
                (
                    operator_eligible
                    & cross_context_defined_output
                    & (cross_context_prediction == expected_counterfactual)
                ).sum()
            )
            total += current_batch
            offset += current_batch

    result: dict[str, Any] = {
        "available": True,
        "examples": total,
        "length": length,
        "state_split": split,
        "operator_step": operator_step,
        "episode_bank_supplied": episode_bank_was_supplied,
        "operator_control_bank_supplied": operator_control_bank_was_supplied,
        "control_seed": resolved_control_seed,
        **{name + "_accuracy": value / total for name, value in counts.items()},
        **{
            name + "_defined_fraction": value / total
            for name, value in defined_counts.items()
        },
        "state_counterfactual_target_distinct_fraction": (
            state_distinct_targets / total
        ),
        "operator_counterfactual_target_distinct_fraction": (
            operator_distinct_targets / total
        ),
        "state_transition_eligible_examples": state_transition_eligible,
        "operator_transition_eligible_examples": operator_transition_eligible,
        **{
            name + "_transition_accuracy": (
                value / state_transition_eligible
                if state_transition_eligible > 0
                else None
            )
            for name, value in state_transition_counts.items()
        },
        **{
            name + "_transition_accuracy": (
                value / operator_transition_eligible
                if operator_transition_eligible > 0
                else None
            )
            for name, value in operator_transition_counts.items()
        },
    }
    if not polar_operator_control_available:
        # Relative conjugacy is an O(d)-specific geometry match. The raw
        # Euclidean-normalized cells retain their random perturbation and
        # independent cross-context controls, but must not relabel the random
        # perturbation as a conjugacy-matched intervention.
        result["relative_conjugacy_operator_control_accuracy"] = None
        result["relative_conjugacy_operator_control_defined_fraction"] = None
        result["relative_conjugacy_operator_control_transition_accuracy"] = None
    result["state_control_geometry"] = {
        "control": "unit_sphere_recipient_angle_matched_random_tangent",
        "defined_fraction": min(row["defined_fraction"] for row in state_geometry_rows),
        "maximum_norm_error": max(row["maximum_norm_error"] for row in state_geometry_rows),
        "maximum_cosine_error": max(row["maximum_cosine_error"] for row in state_geometry_rows),
        "minimum_target_sine": min(row["minimum_target_sine"] for row in state_geometry_rows),
    }
    result["operator_control_geometry"] = {
        "control": "relative_conjugacy_matched_orthogonal",
        "cross_context_control": (
            "independent_context_balanced_slot_with_exact_original_and_alternate_"
            "table_collision_exclusion"
        ),
        "available": polar_operator_control_available,
        "defined_fraction": (
            min(row["defined_fraction"] for row in operator_geometry_rows)
            if operator_geometry_rows
            else None
        ),
        "maximum_chord_distance_error": (
            max(row["maximum_chord_distance_error"] for row in operator_geometry_rows)
            if operator_geometry_rows
            else None
        ),
        "maximum_orthogonality_defect": (
            max(row["maximum_orthogonality_defect"] for row in operator_geometry_rows)
            if operator_geometry_rows
            else None
        ),
        "determinant_component_match_fraction": (
            min(row["determinant_component_match_fraction"] for row in operator_geometry_rows)
            if operator_geometry_rows
            else None
        ),
        "minimum_separation_from_alternate": (
            min(row["minimum_separation_from_alternate"] for row in operator_geometry_rows)
            if operator_geometry_rows
            else None
        ),
        "cross_context_defined_fraction": (
            min(row["cross_context_defined_fraction"] for row in operator_geometry_rows)
            if operator_geometry_rows
            else None
        ),
        "minimum_cross_context_separation_from_original": (
            min(
                row["minimum_cross_context_separation_from_original"]
                for row in operator_geometry_rows
            )
            if operator_geometry_rows
            else None
        ),
        "minimum_cross_context_separation_from_alternate": (
            min(
                row["minimum_cross_context_separation_from_alternate"]
                for row in operator_geometry_rows
            )
            if operator_geometry_rows
            else None
        ),
        "cross_context_base_original_table_collision_count": sum(
            int(row["cross_context_base_original_table_collision_count"])
            for row in operator_geometry_rows
        ),
        "cross_context_base_alternate_table_collision_count": sum(
            int(row["cross_context_base_alternate_table_collision_count"])
            for row in operator_geometry_rows
        ),
        "cross_context_selected_original_table_collision_count": sum(
            int(row["cross_context_selected_original_table_collision_count"])
            for row in operator_geometry_rows
        ),
        "cross_context_selected_alternate_table_collision_count": sum(
            int(row["cross_context_selected_alternate_table_collision_count"])
            for row in operator_geometry_rows
        ),
    }
    return result


def full_evaluation(
    model: torch.nn.Module,
    config: EvaluationConfig,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    accuracy = {
        family: accuracy_by_length(
            model,
            family,
            config.lengths,
            config.examples_per_length,
            config.batch_size,
            seed + offset,
            device,
        )
        for family, offset in (("d4", 0), ("c8", 1000), ("mixed_cycle", 2000), ("random", 3000))
    }
    return {
        "accuracy": accuracy,
        "relations": relation_metrics(model, config.intervention_examples, config.batch_size, seed + 4000, device),
        "equivalent_paths": equivalent_path_metrics(
            model, config.intervention_examples, config.batch_size, seed + 5000, device
        ),
        "interventions": intervention_metrics(
            model, config.intervention_examples, config.batch_size, seed + 6000, device
        ),
    }
