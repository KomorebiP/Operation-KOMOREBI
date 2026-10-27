from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import torch
from torch.nn import functional as F

from .algebra import D4_EQUIVALENT_PATHS, D4_RELATIONS, N_STATES
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


def intervention_metrics(
    model: torch.nn.Module,
    examples: int,
    batch_size: int,
    seed: int,
    device: torch.device,
    length: int = 8,
    split: int = 4,
    operator_step: int = 3,
) -> dict[str, Any]:
    if not isinstance(model, RecurrentOperatorModel):
        return {"available": False, "reason": "model is nonrecurrent"}
    generator = EpisodeGenerator(seed)
    torch_rng = torch.Generator(device=device).manual_seed(seed + 77)
    counts = {
        "state_patch": 0,
        "random_state_patch": 0,
        "random_absolute_state": 0,
        "zero_state_lesion_original": 0,
        "operator_patch": 0,
        "random_operator_patch": 0,
        "native_original": 0,
    }
    total = 0
    model.eval()
    with torch.no_grad():
        for current_batch in _chunks(examples, batch_size):
            batch = generator.sample(current_batch, length, family="d4").to(device)
            rows = torch.arange(current_batch, device=device)
            prefix = batch.op_slots[:, :split]
            suffix = batch.op_slots[:, split:]
            donor_start = (batch.start + torch.randint(1, N_STATES, (current_batch,), generator=torch_rng, device=device)) % N_STATES

            donor_prefix = model.run(batch.tables, prefix, donor_start)
            recipient_prefix = model.run(batch.tables, prefix, batch.start)
            codes = donor_prefix.operator_codes
            patched = model.continue_from_hidden(donor_prefix.hidden[-1], codes, suffix)
            donor_mid = apply_slots_torch(batch.maps, donor_start, prefix)
            donor_expected = apply_slots_torch(batch.maps, donor_mid, suffix)
            counts["state_patch"] += int((patched.logits.argmax(dim=1) == donor_expected).sum())

            # Strong control: apply a random displacement from the recipient state with
            # exactly the donor-minus-recipient displacement norm. This matches the
            # intervention geometry without inserting the causally correct state.
            state_delta = donor_prefix.hidden[-1] - recipient_prefix.hidden[-1]
            random_delta = _norm_matched_random(state_delta, torch_rng)
            random_hidden = recipient_prefix.hidden[-1] + random_delta
            random_patched = model.continue_from_hidden(random_hidden, codes, suffix)
            counts["random_state_patch"] += int((random_patched.logits.argmax(dim=1) == donor_expected).sum())

            # Retain the weaker off-manifold absolute-vector control as a secondary diagnostic.
            random_absolute = _norm_matched_random(donor_prefix.hidden[-1], torch_rng)
            random_absolute_result = model.continue_from_hidden(random_absolute, codes, suffix)
            counts["random_absolute_state"] += int(
                (random_absolute_result.logits.argmax(dim=1) == donor_expected).sum()
            )

            zero = torch.zeros_like(recipient_prefix.hidden[-1])
            zero_result = model.continue_from_hidden(zero, recipient_prefix.operator_codes, suffix)
            counts["zero_state_lesion_original"] += int((zero_result.logits.argmax(dim=1) == batch.target).sum())

            native = model.run(batch.tables, batch.op_slots, batch.start)
            counts["native_original"] += int((native.logits.argmax(dim=1) == batch.target).sum())

            operator_codes = native.operator_codes
            hidden = model.initial_hidden(batch.start)
            counterfactual_slots = batch.op_slots.clone()
            counterfactual_slots[:, operator_step] = 1 - counterfactual_slots[:, operator_step]
            random_hidden_operator = model.initial_hidden(batch.start)
            for t in range(length):
                original_code = operator_codes[rows, batch.op_slots[:, t]]
                if t == operator_step:
                    alternate_code = operator_codes[rows, 1 - batch.op_slots[:, t]]
                    hidden = model.step_hidden(hidden, alternate_code)
                    delta = alternate_code - original_code
                    random_delta = _norm_matched_random(delta, torch_rng)
                    random_hidden_operator = model.step_hidden(random_hidden_operator, original_code + random_delta)
                else:
                    hidden = model.step_hidden(hidden, original_code)
                    random_hidden_operator = model.step_hidden(random_hidden_operator, original_code)
            expected_counterfactual = apply_slots_torch(batch.maps, batch.start, counterfactual_slots)
            counts["operator_patch"] += int((model.decode_hidden(hidden).argmax(dim=1) == expected_counterfactual).sum())
            counts["random_operator_patch"] += int(
                (model.decode_hidden(random_hidden_operator).argmax(dim=1) == expected_counterfactual).sum()
            )
            total += current_batch

    return {
        "available": True,
        "examples": total,
        "length": length,
        "state_split": split,
        "operator_step": operator_step,
        **{name + "_accuracy": value / total for name, value in counts.items()},
    }


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
