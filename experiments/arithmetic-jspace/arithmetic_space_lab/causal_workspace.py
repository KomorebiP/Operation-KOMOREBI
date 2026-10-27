"""Sealed causal interventions for a discovered :mod:`balanced_space` artifact.

Answers enter only after target-blind candidate fitting and rank/layer
selection.  In this sealed causal stage they define matched counterfactual
eligibility and directional outcomes as well as score free generation.  The
functions intervene on the final prefix token at a registered residual layer
on every autoregressive recomputation.  This makes the test behavioral rather
than a teacher-forced next-token proxy.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Sequence

try:
    import torch
except ImportError as error:  # pragma: no cover - handled by package preflight
    raise ImportError("PyTorch is required for causal workspace assays.") from error

from .balanced_space import BalancedSpace
from .byte_tokenizer import ByteTokenizer
from .tiny_model import TinyDecoderLM


_INTEGER_ANSWER = re.compile(r"-?[0-9]+")


@dataclass(frozen=True)
class InterventionSpec:
    """A registered intervention basis and optional energy-matching reference."""

    name: str
    basis: "torch.Tensor"
    mean: "torch.Tensor"
    source_layer: int
    reference_basis: "torch.Tensor | None" = None

    def on(self, hidden: "torch.Tensor") -> "InterventionSpec":
        dtype = hidden.dtype
        device = hidden.device
        return InterventionSpec(
            name=self.name,
            basis=self.basis.to(device=device, dtype=dtype),
            mean=self.mean.to(device=device, dtype=dtype),
            source_layer=self.source_layer,
            reference_basis=(
                None
                if self.reference_basis is None
                else self.reference_basis.to(device=device, dtype=dtype)
            ),
        )


def _positions_tensor(
    positions: int | Sequence[int] | "torch.Tensor",
    batch: int,
    device: "torch.device",
) -> "torch.Tensor":
    if isinstance(positions, int):
        return torch.full((batch,), positions, dtype=torch.long, device=device)
    if isinstance(positions, torch.Tensor):
        result = positions.to(device=device, dtype=torch.long)
    else:
        result = torch.tensor(list(positions), dtype=torch.long, device=device)
    if result.shape != (batch,):
        raise ValueError("positions must contain one position per batch row")
    return result


def _energy_match(delta: "torch.Tensor", reference: "torch.Tensor") -> "torch.Tensor":
    target = reference.norm(dim=-1, keepdim=True)
    actual = delta.norm(dim=-1, keepdim=True)
    scale = torch.where(actual > 1e-12, target / actual.clamp_min(1e-12), torch.zeros_like(actual))
    return delta * scale


def _project(values: "torch.Tensor", basis: "torch.Tensor") -> "torch.Tensor":
    return (values @ basis) @ basis.T


def ablate_hidden(
    hidden: "torch.Tensor",
    positions: int | Sequence[int] | "torch.Tensor",
    *,
    basis: "torch.Tensor",
    mean: "torch.Tensor",
    energy_reference_basis: "torch.Tensor | None" = None,
) -> tuple["torch.Tensor", "torch.Tensor"]:
    """Replace selected coordinates by their discovery conditional mean.

    Returns the patched tensor and the norm removed from each row.  If
    ``energy_reference_basis`` is supplied, the control removal is scaled to the
    candidate removal norm for the same state.
    """

    if hidden.ndim != 3:
        raise ValueError("hidden must have shape [batch, sequence, width]")
    basis = basis.to(device=hidden.device, dtype=hidden.dtype)
    mean = mean.to(device=hidden.device, dtype=hidden.dtype)
    if basis.ndim != 2 or basis.shape[0] != hidden.shape[-1]:
        raise ValueError("basis width does not match hidden width")
    if mean.shape != (hidden.shape[-1],):
        raise ValueError("mean width does not match hidden width")
    batch = hidden.shape[0]
    position_values = _positions_tensor(positions, batch, hidden.device)
    rows = torch.arange(batch, device=hidden.device)
    selected = hidden[rows, position_values]
    centered = selected - mean
    removal = _project(centered, basis)
    if energy_reference_basis is not None:
        reference = energy_reference_basis.to(device=hidden.device, dtype=hidden.dtype)
        removal = _energy_match(removal, _project(centered, reference))
    result = hidden.clone()
    result[rows, position_values] = selected - removal
    return result, removal.float().norm(dim=-1)


def patch_hidden(
    recipient_hidden: "torch.Tensor",
    donor_hidden: "torch.Tensor",
    recipient_positions: int | Sequence[int] | "torch.Tensor",
    donor_positions: int | Sequence[int] | "torch.Tensor",
    *,
    basis: "torch.Tensor",
    energy_reference_basis: "torch.Tensor | None" = None,
) -> tuple["torch.Tensor", "torch.Tensor"]:
    """Transplant donor coordinates into recipient states."""

    if recipient_hidden.ndim != 3 or donor_hidden.ndim != 3:
        raise ValueError("hidden tensors must have shape [batch, sequence, width]")
    if recipient_hidden.shape[0] != donor_hidden.shape[0]:
        raise ValueError("recipient and donor batches must align")
    if recipient_hidden.shape[-1] != donor_hidden.shape[-1]:
        raise ValueError("recipient and donor widths must match")
    basis = basis.to(device=recipient_hidden.device, dtype=recipient_hidden.dtype)
    donor_hidden = donor_hidden.to(
        device=recipient_hidden.device, dtype=recipient_hidden.dtype
    )
    batch = recipient_hidden.shape[0]
    recipient_positions_tensor = _positions_tensor(
        recipient_positions, batch, recipient_hidden.device
    )
    donor_positions_tensor = _positions_tensor(
        donor_positions, batch, recipient_hidden.device
    )
    rows = torch.arange(batch, device=recipient_hidden.device)
    recipient = recipient_hidden[rows, recipient_positions_tensor]
    donor = donor_hidden[rows, donor_positions_tensor]
    difference = donor - recipient
    transfer = _project(difference, basis)
    if energy_reference_basis is not None:
        reference = energy_reference_basis.to(
            device=recipient_hidden.device, dtype=recipient_hidden.dtype
        )
        transfer = _energy_match(transfer, _project(difference, reference))
    result = recipient_hidden.clone()
    result[rows, recipient_positions_tensor] = recipient + transfer
    return result, transfer.float().norm(dim=-1)


def rescue_hidden(
    intervened_hidden: "torch.Tensor",
    clean_hidden: "torch.Tensor",
    positions: int | Sequence[int] | "torch.Tensor",
    *,
    basis: "torch.Tensor",
    clean_positions: int | Sequence[int] | "torch.Tensor | None" = None,
    energy_reference_basis: "torch.Tensor | None" = None,
) -> tuple["torch.Tensor", "torch.Tensor"]:
    """Restore only registered coordinates from a clean state."""

    return patch_hidden(
        intervened_hidden,
        clean_hidden,
        positions,
        positions if clean_positions is None else clean_positions,
        basis=basis,
        energy_reference_basis=energy_reference_basis,
    )


def _validate_eval_inputs(
    prefixes: Sequence[Sequence[int]],
    answers: Sequence[str],
    model: TinyDecoderLM,
    label: str,
) -> tuple[list[list[int]], list[str]]:
    if not prefixes or len(prefixes) != len(answers):
        raise ValueError(f"{label} prefixes and answers must be nonempty and aligned")
    normalized_prefixes: list[list[int]] = []
    normalized_answers: list[str] = []
    for index, (prefix, answer) in enumerate(zip(prefixes, answers)):
        tokens = [int(value) for value in prefix]
        if not tokens or len(tokens) > model.config.max_seq_len:
            raise ValueError(f"invalid {label} prefix at row {index}")
        if min(tokens) < 0 or max(tokens) >= model.config.vocab_size:
            raise ValueError(f"invalid token in {label} prefix at row {index}")
        if not isinstance(answer, str) or not answer:
            raise ValueError(f"invalid {label} answer at row {index}")
        normalized_prefixes.append(tokens)
        normalized_answers.append(answer)
    return normalized_prefixes, normalized_answers


@torch.no_grad()
def _source_hidden(
    model: TinyDecoderLM,
    prefix: Sequence[int],
    source_layer: int,
    device: "torch.device",
) -> torch.Tensor:
    ids = torch.tensor([list(prefix)], dtype=torch.long, device=device)
    _, states = model(ids, return_hidden_states=True)
    return states[source_layer].detach()


def _continue_to_layer(
    model: TinyDecoderLM,
    hidden: "torch.Tensor",
    completed_layers: int,
    target_completed_layers: int,
) -> "torch.Tensor":
    if not 0 <= completed_layers <= target_completed_layers <= model.config.n_layers:
        raise ValueError("invalid layer continuation interval")
    length = hidden.shape[1]
    rope_cos = model._rope_cos[:length].to(dtype=hidden.dtype)[None, None, :, :]
    rope_sin = model._rope_sin[:length].to(dtype=hidden.dtype)[None, None, :, :]
    for block in model.blocks[completed_layers:target_completed_layers]:
        hidden = block(hidden, rope_cos, rope_sin)
    return hidden


@torch.no_grad()
def _generate_upstream_transplant(
    model: TinyDecoderLM,
    clean_prefix: Sequence[int],
    corrupt_upstream_hidden: "torch.Tensor",
    *,
    eos_id: int,
    max_new_tokens: int,
    device: "torch.device",
    upstream_layer: int,
    source_layer: int,
    rescue_spec: InterventionSpec | None,
) -> tuple[list[int], float, float]:
    """Transplant an upstream donor state, optionally rescuing source coordinates."""

    if not 0 <= upstream_layer < source_layer < model.config.n_layers:
        raise ValueError("upstream transplant requires upstream < source < n_layers")
    sequence = [int(value) for value in clean_prefix]
    prefix_position = len(sequence) - 1
    generated: list[int] = []
    first_upstream_norm = 0.0
    first_rescue_norm = 0.0
    donor_position = corrupt_upstream_hidden.shape[1] - 1
    for step in range(max_new_tokens):
        if len(sequence) > model.config.max_seq_len:
            break
        ids = torch.tensor([sequence], dtype=torch.long, device=device)
        _, states = model(ids, return_hidden_states=True)
        clean_upstream = states[upstream_layer]
        clean_source = states[source_layer]
        transplanted_upstream = clean_upstream.clone()
        donor = corrupt_upstream_hidden.to(
            device=clean_upstream.device, dtype=clean_upstream.dtype
        )[0, donor_position]
        upstream_delta = donor - clean_upstream[0, prefix_position]
        transplanted_upstream[0, prefix_position] = donor
        corrupted_source = _continue_to_layer(
            model,
            transplanted_upstream,
            upstream_layer,
            source_layer,
        )
        if rescue_spec is None:
            intervened_source = corrupted_source
            rescue_norm = torch.zeros(1, device=device)
        else:
            local = rescue_spec.on(corrupted_source)
            intervened_source, rescue_norm = rescue_hidden(
                corrupted_source,
                clean_source,
                prefix_position,
                basis=local.basis,
                clean_positions=prefix_position,
                energy_reference_basis=local.reference_basis,
            )
        if step == 0:
            first_upstream_norm = float(upstream_delta.float().norm().item())
            first_rescue_norm = float(rescue_norm[0].item())
        logits = model.continue_from_hidden(
            intervened_source, completed_layers=source_layer
        )
        token = int(logits[0, -1].argmax().item())
        generated.append(token)
        sequence.append(token)
        if token == eos_id:
            break
    return generated, first_upstream_norm, first_rescue_norm


@torch.no_grad()
def _generate_intervened(
    model: TinyDecoderLM,
    prefix: Sequence[int],
    *,
    eos_id: int,
    max_new_tokens: int,
    device: "torch.device",
    spec: InterventionSpec,
    operation: str,
    donor_hidden: "torch.Tensor | None" = None,
) -> tuple[list[int], float]:
    if max_new_tokens <= 0:
        raise ValueError("max_new_tokens must be positive")
    sequence = [int(value) for value in prefix]
    prefix_position = len(sequence) - 1
    generated: list[int] = []
    first_energy = 0.0
    clean_prefix_hidden: torch.Tensor | None = None
    if operation == "rescue":
        clean_prefix_hidden = _source_hidden(
            model, prefix, spec.source_layer, device
        )
    for step in range(max_new_tokens):
        if len(sequence) > model.config.max_seq_len:
            break
        ids = torch.tensor([sequence], dtype=torch.long, device=device)
        _, states = model(ids, return_hidden_states=True)
        hidden = states[spec.source_layer]
        local = spec.on(hidden)
        if operation == "ablate":
            intervened, energy = ablate_hidden(
                hidden,
                prefix_position,
                basis=local.basis,
                mean=local.mean,
                energy_reference_basis=local.reference_basis,
            )
        elif operation == "patch":
            if donor_hidden is None:
                raise ValueError("patch operation requires donor_hidden")
            intervened, energy = patch_hidden(
                hidden,
                donor_hidden,
                prefix_position,
                donor_hidden.shape[1] - 1,
                basis=local.basis,
                energy_reference_basis=local.reference_basis,
            )
        elif operation == "rescue":
            if clean_prefix_hidden is None:  # pragma: no cover - initialized above
                raise AssertionError("clean rescue state missing")
            ablated, _ = ablate_hidden(
                hidden,
                prefix_position,
                basis=local.basis,
                mean=local.mean,
                energy_reference_basis=local.reference_basis,
            )
            intervened, energy = rescue_hidden(
                ablated,
                clean_prefix_hidden,
                prefix_position,
                basis=local.basis,
                clean_positions=clean_prefix_hidden.shape[1] - 1,
                energy_reference_basis=local.reference_basis,
            )
        else:
            raise ValueError(f"unknown intervention operation: {operation}")
        if step == 0:
            first_energy = float(energy[0].item())
        logits = model.continue_from_hidden(
            intervened, completed_layers=spec.source_layer
        )
        token = int(logits[0, -1].argmax().item())
        generated.append(token)
        sequence.append(token)
        if token == eos_id:
            break
    return generated, first_energy


def _generation_record(
    output_ids: Sequence[int], tokenizer: ByteTokenizer
) -> dict[str, Any]:
    """Retain the token-level facts needed for valid free-generation scoring.

    ``ByteTokenizer.completion`` intentionally ignores special tokens.  That is
    convenient for display but unsafe for an exact-match assay: ``5<SEP><EOS>``
    would otherwise decode like ``5``.  Causal scoring therefore keeps the raw
    token IDs and applies the same signed-decimal/EOS validity contract used by
    :func:`workspace_trainer.evaluate_free_generation`.
    """

    tokens = [int(value) for value in output_ids]
    has_final_eos = bool(tokens and tokens[-1] == tokenizer.eos_id)
    premature_eos = tokenizer.eos_id in tokens[:-1]
    illegal_special = any(
        token < 0
        or token >= tokenizer.vocab_size
        or token in {tokenizer.pad_id, tokenizer.bos_id, tokenizer.sep_id}
        for token in tokens
    )
    termination_valid = bool(has_final_eos and not premature_eos)
    completion = (
        "" if illegal_special else tokenizer.completion(tokens)
    )
    answer = completion.strip()
    signed_decimal = bool(answer and _INTEGER_ANSWER.fullmatch(answer))
    well_formed = bool(
        termination_valid and not illegal_special and signed_decimal
    )
    return {
        "token_ids": tokens,
        "completion": completion,
        "answer": answer,
        "terminated_by_eos": has_final_eos,
        "termination_valid": termination_valid,
        "premature_eos": premature_eos,
        "illegal_special": illegal_special,
        "nonempty_signed_decimal": signed_decimal,
        "well_formed": well_formed,
    }


def _record_exact(output: dict[str, Any], expected: str) -> bool:
    return bool(output["well_formed"] and output["answer"] == expected.strip())


def _score_outputs(
    outputs: Sequence[dict[str, Any]],
    expected: Sequence[str],
    baseline: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if len(outputs) != len(expected):
        raise ValueError("outputs and expected answers must align")
    if baseline is not None and len(baseline) != len(outputs):
        raise ValueError("baseline and outputs must align")
    exact = [_record_exact(output, target) for output, target in zip(outputs, expected)]
    well_formed = [bool(output["well_formed"]) for output in outputs]
    eos_terminated = [bool(output["terminated_by_eos"]) for output in outputs]
    illegal_special = [bool(output["illegal_special"]) for output in outputs]
    report: dict[str, Any] = {
        "exact": sum(exact) / max(1, len(exact)),
        "exact_count": sum(exact),
        "well_formed_count": sum(well_formed),
        "well_formed_rate": sum(well_formed) / max(1, len(outputs)),
        "eos_terminated_count": sum(eos_terminated),
        "eos_terminated_rate": sum(eos_terminated) / max(1, len(outputs)),
        "illegal_special_count": sum(illegal_special),
        "illegal_special_rate": sum(illegal_special) / max(1, len(outputs)),
        # Preserve the old display field while retaining token-level evidence.
        "outputs": [str(output["completion"]) for output in outputs],
        "generation_records": [dict(output) for output in outputs],
    }
    if baseline is not None:
        changed = [
            left["token_ids"] != right["token_ids"]
            for left, right in zip(outputs, baseline)
        ]
        report["changed_from_baseline"] = sum(changed) / max(1, len(changed))
        baseline_exact = [
            _record_exact(value, target) for value, target in zip(baseline, expected)
        ]
        losses = [before and not after for before, after in zip(baseline_exact, exact)]
        gains = [not before and after for before, after in zip(baseline_exact, exact)]
        report["baseline_correct_count"] = sum(baseline_exact)
        report["baseline_correct_lost_count"] = sum(losses)
        report["baseline_correct_lost"] = sum(losses) / max(1, sum(baseline_exact))
        report["baseline_error_count"] = len(baseline_exact) - sum(baseline_exact)
        report["baseline_error_rescued_count"] = sum(gains)
        report["baseline_error_rescued"] = sum(gains) / max(
            1, len(baseline_exact) - sum(baseline_exact)
        )
    return report


def _qualified_rate(successes: Sequence[bool], eligible: Sequence[bool]) -> tuple[int, int, float | None]:
    if len(successes) != len(eligible):
        raise ValueError("success and eligibility flags must align")
    denominator = sum(bool(value) for value in eligible)
    count = sum(
        bool(success) and bool(is_eligible)
        for success, is_eligible in zip(successes, eligible)
    )
    return denominator, count, None if denominator == 0 else count / denominator


def _mean(values: Iterable[float]) -> float:
    materialized = list(values)
    return sum(materialized) / max(1, len(materialized))


@torch.no_grad()
def run_causal_assay(
    model: TinyDecoderLM,
    clean_prefixes: Sequence[Sequence[int]],
    corrupt_prefixes: Sequence[Sequence[int]],
    clean_expected: Sequence[str],
    corrupt_expected: Sequence[str],
    *,
    space: BalancedSpace,
    tokenizer: ByteTokenizer,
    device: "torch.device",
    max_new_tokens: int,
    controls: Sequence[str] = ("pca", "random", "complement"),
    require_directional_donor_effect: bool = True,
    minimum_baseline_qualified_pairs: int = 1,
    minimum_directional_rescue_pairs: int = 1,
) -> dict[str, Any]:
    """Run free-generation ablation, donor-patch, and coordinate-rescue assays.

    Clean/corrupt rows must be semantically matched by the caller (for example,
    same digits except for one carry-causing column).  The report intentionally
    keeps individual decoded outputs so resampling and auditing remain possible.
    """

    clean, clean_answers = _validate_eval_inputs(
        clean_prefixes, clean_expected, model, "clean"
    )
    corrupt, corrupt_answers = _validate_eval_inputs(
        corrupt_prefixes, corrupt_expected, model, "corrupt"
    )
    if len(clean) != len(corrupt):
        raise ValueError("clean and corrupt rows must be paired")
    if not 0 <= space.source_layer < model.config.n_layers:
        raise ValueError("space source layer is outside the model")
    if space.basis.shape[0] != model.config.d_model:
        raise ValueError("space width does not match model")
    requested_controls = [str(name) for name in controls]
    missing = sorted(set(requested_controls) - set(space.control_bases))
    if missing:
        raise ValueError(f"requested controls missing from space: {missing}")
    if max_new_tokens <= 0:
        raise ValueError("max_new_tokens must be positive")
    if type(require_directional_donor_effect) is not bool:
        raise ValueError("require_directional_donor_effect must be boolean")
    if (
        type(minimum_baseline_qualified_pairs) is not int
        or minimum_baseline_qualified_pairs <= 0
    ):
        raise ValueError("minimum_baseline_qualified_pairs must be positive")
    if (
        type(minimum_directional_rescue_pairs) is not int
        or minimum_directional_rescue_pairs <= 0
    ):
        raise ValueError("minimum_directional_rescue_pairs must be positive")

    model = model.to(device).eval()
    def baseline_generations(
        rows: Sequence[Sequence[int]], phase: str
    ) -> list[list[int]]:
        generated_rows: list[list[int]] = []
        print(
            f"CAUSAL_PROGRESS PHASE={phase} PAIRS=0/{len(rows)}",
            flush=True,
        )
        for index, prefix in enumerate(rows):
            generated_rows.append(
                model.generate(prefix, tokenizer.eos_id, max_new_tokens, device)
            )
            completed = index + 1
            if completed % 100 == 0 or completed == len(rows):
                print(
                    f"CAUSAL_PROGRESS PHASE={phase} PAIRS={completed}/{len(rows)}",
                    flush=True,
                )
        return generated_rows

    baseline_clean_ids = baseline_generations(clean, "BASELINE_CLEAN")
    baseline_corrupt_ids = baseline_generations(corrupt, "BASELINE_CORRUPT")
    baseline_clean = [
        _generation_record(ids, tokenizer) for ids in baseline_clean_ids
    ]
    baseline_corrupt = [
        _generation_record(ids, tokenizer) for ids in baseline_corrupt_ids
    ]
    baseline_clean_exact = [
        _record_exact(output, target)
        for output, target in zip(baseline_clean, clean_answers)
    ]
    baseline_corrupt_exact = [
        _record_exact(output, target)
        for output, target in zip(baseline_corrupt, corrupt_answers)
    ]
    corrupt_upstream_states = [
        _source_hidden(model, prefix, space.upstream_layer, device)
        for prefix in corrupt
    ]
    clean_source_states = [
        _source_hidden(model, prefix, space.source_layer, device)
        for prefix in clean
    ]
    upstream_corrupted_outputs: list[dict[str, Any]] = []
    upstream_corruption_energy: list[float] = []
    print(
        f"CAUSAL_PROGRESS PHASE=UPSTREAM_TRANSPLANT PAIRS=0/{len(clean)}",
        flush=True,
    )
    for clean_prefix, corrupt_upstream in zip(clean, corrupt_upstream_states):
        generated, upstream_norm, _ = _generate_upstream_transplant(
            model,
            clean_prefix,
            corrupt_upstream,
            eos_id=tokenizer.eos_id,
            max_new_tokens=max_new_tokens,
            device=device,
            upstream_layer=space.upstream_layer,
            source_layer=space.source_layer,
            rescue_spec=None,
        )
        upstream_corrupted_outputs.append(_generation_record(generated, tokenizer))
        upstream_corruption_energy.append(upstream_norm)
        completed = len(upstream_corrupted_outputs)
        if completed % 100 == 0 or completed == len(clean):
            print(
                f"CAUSAL_PROGRESS PHASE=UPSTREAM_TRANSPLANT "
                f"PAIRS={completed}/{len(clean)}",
                flush=True,
            )
    report: dict[str, Any] = {
        "schema_version": "causal-workspace-assay-v2",
        "evaluation_information_used_for_discovery": False,
        "answers_used_for": (
            "sealed counterfactual construction/eligibility, directional "
            "outcomes, and free-generation scoring; never candidate fitting or "
            "selection"
        ),
        "n_pairs": len(clean),
        "registered_qualified_minima": {
            "baseline_qualified_pairs": minimum_baseline_qualified_pairs,
            "directional_rescue_pairs": minimum_directional_rescue_pairs,
            "require_directional_donor_effect": require_directional_donor_effect,
        },
        "space": space.summary(),
        "baseline": {
            "clean": _score_outputs(baseline_clean, clean_answers),
            "corrupt": _score_outputs(baseline_corrupt, corrupt_answers),
        },
        "upstream_residual_transplant": {
            **_score_outputs(
                upstream_corrupted_outputs,
                clean_answers,
                baseline=baseline_clean,
            ),
            "corrupt_expected_exact": sum(
                _record_exact(output, target)
                for output, target in zip(
                    upstream_corrupted_outputs, corrupt_answers
                )
            )
            / max(1, len(corrupt_answers)),
            "mean_first_step_upstream_intervention_norm": _mean(
                upstream_corruption_energy
            ),
            "note": (
                "Matched corrupt-prompt residual state transplanted at the upstream "
                "layer; this is independent of the downstream candidate rescue."
            ),
        },
        "independent_rescue_available": True,
        "claim_gate_flags": {
            "free_generation": True,
            "rank_matched_controls": True,
            "energy_matched_controls": True,
            "directional_donor_patch": True,
            "baseline_qualified_primary_estimands": True,
            "independent_upstream_residual_rescue_assay": True,
            "component_specific_writer_rescue": False,
            "mediation_claim_eligible": False,
        },
        "spaces": {},
        "interpretation_guard": (
            "A candidate effect is evidence only if it exceeds rank/energy-matched "
            "PCA, random, and complement controls across independent seeds."
        ),
    }

    bases = {"candidate": space.basis}
    bases.update({name: space.control_bases[name] for name in requested_controls})
    for name, basis in bases.items():
        reference_basis = None if name == "candidate" else space.basis
        spec = InterventionSpec(
            name=name,
            basis=basis,
            mean=space.mean,
            source_layer=space.source_layer,
            reference_basis=reference_basis,
        )
        ablated_outputs: list[dict[str, Any]] = []
        patched_outputs: list[dict[str, Any]] = []
        rescued_outputs: list[dict[str, Any]] = []
        ablation_energy: list[float] = []
        patch_energy: list[float] = []
        rescue_energy: list[float] = []
        print(
            f"CAUSAL_PROGRESS PHASE=INTERVENTIONS SPACE={name} PAIRS=0/{len(clean)}",
            flush=True,
        )
        for pair_index, (clean_prefix, corrupt_prefix) in enumerate(zip(clean, corrupt)):
            donor = clean_source_states[pair_index]
            generated, energy = _generate_intervened(
                model,
                clean_prefix,
                eos_id=tokenizer.eos_id,
                max_new_tokens=max_new_tokens,
                device=device,
                spec=spec,
                operation="ablate",
            )
            ablated_outputs.append(_generation_record(generated, tokenizer))
            ablation_energy.append(energy)
            generated, energy = _generate_intervened(
                model,
                corrupt_prefix,
                eos_id=tokenizer.eos_id,
                max_new_tokens=max_new_tokens,
                device=device,
                spec=spec,
                operation="patch",
                donor_hidden=donor,
            )
            patched_outputs.append(_generation_record(generated, tokenizer))
            patch_energy.append(energy)
            generated, _, energy = _generate_upstream_transplant(
                model,
                clean_prefix,
                eos_id=tokenizer.eos_id,
                max_new_tokens=max_new_tokens,
                device=device,
                corrupt_upstream_hidden=corrupt_upstream_states[pair_index],
                upstream_layer=space.upstream_layer,
                source_layer=space.source_layer,
                rescue_spec=spec,
            )
            rescued_outputs.append(_generation_record(generated, tokenizer))
            rescue_energy.append(energy)
            completed = pair_index + 1
            if completed % 100 == 0 or completed == len(clean):
                print(
                    f"CAUSAL_PROGRESS PHASE=INTERVENTIONS SPACE={name} "
                    f"PAIRS={completed}/{len(clean)}",
                    flush=True,
                )

        ablated_exact = [
            _record_exact(output, target)
            for output, target in zip(ablated_outputs, clean_answers)
        ]
        ablation_denominator, ablation_loss_count, ablation_loss_rate = (
            _qualified_rate(
                [not value for value in ablated_exact], baseline_clean_exact
            )
        )

        distinct_targets = [
            clean_target.strip() != corrupt_target.strip()
            for clean_target, corrupt_target in zip(clean_answers, corrupt_answers)
        ]
        patch_eligible = [
            bool(clean_ok and corrupt_ok and distinct)
            for clean_ok, corrupt_ok, distinct in zip(
                baseline_clean_exact, baseline_corrupt_exact, distinct_targets
            )
        ]
        patched_clean_exact = [
            _record_exact(output, target)
            for output, target in zip(patched_outputs, clean_answers)
        ]
        patched_corrupt_exact = [
            _record_exact(output, target)
            for output, target in zip(patched_outputs, corrupt_answers)
        ]
        (
            patch_denominator,
            patch_conversion_count,
            patch_conversion_rate,
        ) = _qualified_rate(patched_clean_exact, patch_eligible)
        _, patch_retention_count, patch_retention_rate = _qualified_rate(
            patched_corrupt_exact, patch_eligible
        )
        patch_changed = [
            output["token_ids"] != baseline["token_ids"]
            for output, baseline in zip(patched_outputs, baseline_corrupt)
        ]
        _, patch_changed_count, patch_changed_rate = _qualified_rate(
            patch_changed, patch_eligible
        )

        upstream_clean_exact = [
            _record_exact(output, target)
            for output, target in zip(upstream_corrupted_outputs, clean_answers)
        ]
        upstream_corrupt_exact = [
            _record_exact(output, target)
            for output, target in zip(upstream_corrupted_outputs, corrupt_answers)
        ]
        rescue_broken_eligible = [
            bool(
                clean_ok
                and corrupt_ok
                and distinct
                and not upstream_still_clean
            )
            for clean_ok, corrupt_ok, distinct, upstream_still_clean in zip(
                baseline_clean_exact,
                baseline_corrupt_exact,
                distinct_targets,
                upstream_clean_exact,
            )
        ]
        rescue_eligible = [
            bool(
                broken_ok
                and (
                    donor_direction_ok
                    if require_directional_donor_effect
                    else True
                )
            )
            for broken_ok, donor_direction_ok in zip(
                rescue_broken_eligible, upstream_corrupt_exact
            )
        ]
        rescued_clean_exact = [
            _record_exact(output, target)
            for output, target in zip(rescued_outputs, clean_answers)
        ]
        rescue_denominator, rescue_count, rescue_rate = _qualified_rate(
            rescued_clean_exact, rescue_eligible
        )
        (
            broken_denominator,
            directional_corruption_count,
            directional_corruption_rate,
        ) = (
            _qualified_rate(upstream_corrupt_exact, rescue_broken_eligible)
        )

        report["spaces"][name] = {
            "rank": int(basis.shape[1]),
            "energy_matched_to_candidate": name != "candidate",
            "ablation": {
                **_score_outputs(
                    ablated_outputs, clean_answers, baseline=baseline_clean
                ),
                "mean_first_step_intervention_norm": _mean(ablation_energy),
                "primary_estimand": {
                    "name": "loss_given_clean_baseline_correct",
                    "qualified_denominator_count": ablation_denominator,
                    "qualified_loss_count": ablation_loss_count,
                    "qualified_loss_rate": ablation_loss_rate,
                    "registered_minimum_qualified_pairs": (
                        minimum_baseline_qualified_pairs
                    ),
                    "claim_eligible": (
                        ablation_denominator >= minimum_baseline_qualified_pairs
                    ),
                },
            },
            "clean_to_corrupt_patch": {
                **_score_outputs(
                    patched_outputs, clean_answers, baseline=baseline_corrupt
                ),
                "corrupt_answer_retention": sum(
                    _record_exact(output, target)
                    for output, target in zip(patched_outputs, corrupt_answers)
                )
                / max(1, len(corrupt_answers)),
                "mean_first_step_intervention_norm": _mean(patch_energy),
                "primary_estimand": {
                    "name": (
                        "clean_answer_conversion_given_clean_and_corrupt_"
                        "baselines_correct"
                    ),
                    "eligibility_rule": (
                        "natural clean baseline correct; natural corrupt baseline "
                        "correct; expected answers differ"
                    ),
                    "qualified_denominator_count": patch_denominator,
                    "qualified_clean_conversion_count": patch_conversion_count,
                    "qualified_clean_conversion_rate": patch_conversion_rate,
                    "qualified_corrupt_retention_count": patch_retention_count,
                    "qualified_corrupt_retention_rate": patch_retention_rate,
                    "qualified_changed_count": patch_changed_count,
                    "qualified_changed_rate": patch_changed_rate,
                    "registered_minimum_qualified_pairs": (
                        minimum_baseline_qualified_pairs
                    ),
                    "claim_eligible": (
                        patch_denominator >= minimum_baseline_qualified_pairs
                    ),
                },
                "directional_items": [
                    {
                        "pair_index": index,
                        "output": output["answer"],
                        "output_completion": output["completion"],
                        "output_token_ids": output["token_ids"],
                        "output_well_formed": output["well_formed"],
                        "output_terminated_by_eos": output["terminated_by_eos"],
                        "output_illegal_special": output["illegal_special"],
                        "clean_expected": clean_target,
                        "corrupt_expected": corrupt_target,
                        "baseline_clean_correct": baseline_clean_exact[index],
                        "baseline_corrupt_correct": baseline_corrupt_exact[index],
                        "baseline_qualified": patch_eligible[index],
                        "baseline_corrupt_output": baseline_output["answer"],
                        "baseline_corrupt_token_ids": baseline_output["token_ids"],
                        "matches_clean_expected": patched_clean_exact[index],
                        "matches_corrupt_expected": patched_corrupt_exact[index],
                        "changed_from_corrupt_baseline": patch_changed[index],
                        "first_step_intervention_norm": patch_energy[index],
                    }
                    for index, (
                        output,
                        clean_target,
                        corrupt_target,
                        baseline_output,
                    ) in enumerate(
                        zip(
                            patched_outputs,
                            clean_answers,
                            corrupt_answers,
                            baseline_corrupt,
                        )
                    )
                ],
            },
            "coordinate_rescue": {
                **_score_outputs(
                    rescued_outputs,
                    clean_answers,
                    baseline=upstream_corrupted_outputs,
                ),
                "mean_first_step_intervention_norm": _mean(rescue_energy),
                "independent_rescue": True,
                # Kept as the compatibility key, but it is now the registered,
                # baseline-qualified estimand rather than an all-errors rate.
                "upstream_corruption_error_rescued": rescue_rate,
                "primary_estimand": {
                    "name": (
                        "rescue_given_both_natural_baselines_correct_and_"
                        "upstream_corruption_broke_clean_answer"
                    ),
                    "eligibility_rule": (
                        "natural clean baseline correct; natural corrupt baseline "
                        "correct; expected answers differ; upstream transplant no "
                        "longer yields the clean answer; and, when registered, the "
                        "upstream transplant yields the corrupt expected answer"
                    ),
                    "qualified_denominator_count": rescue_denominator,
                    "qualified_rescue_count": rescue_count,
                    "qualified_rescue_rate": rescue_rate,
                    "qualified_directional_corruption_count": (
                        directional_corruption_count
                    ),
                    "directional_corruption_denominator_count": broken_denominator,
                    "qualified_directional_corruption_rate": (
                        directional_corruption_rate
                    ),
                    "require_directional_donor_effect": (
                        require_directional_donor_effect
                    ),
                    "registered_minimum_qualified_pairs": (
                        minimum_directional_rescue_pairs
                    ),
                    "claim_eligible": (
                        rescue_denominator >= minimum_directional_rescue_pairs
                    ),
                },
                "items": [
                    {
                        "pair_index": index,
                        "upstream_corrupted_output": corrupted["answer"],
                        "upstream_corrupted_token_ids": corrupted["token_ids"],
                        "upstream_corrupted_well_formed": corrupted["well_formed"],
                        "rescued_output": rescued["answer"],
                        "rescued_token_ids": rescued["token_ids"],
                        "rescued_well_formed": rescued["well_formed"],
                        "clean_expected": target,
                        "baseline_clean_correct": baseline_clean_exact[index],
                        "baseline_corrupt_correct": baseline_corrupt_exact[index],
                        "baseline_qualified": rescue_eligible[index],
                        "corruption_broke_clean_answer": (
                            baseline_clean_exact[index]
                            and not upstream_clean_exact[index]
                        ),
                        "corruption_matches_corrupt_expected": (
                            upstream_corrupt_exact[index]
                        ),
                        "rescue_matches_clean_expected": rescued_clean_exact[index],
                        "first_step_rescue_norm": rescue_energy[index],
                    }
                    for index, (baseline, corrupted, rescued, target) in enumerate(
                        zip(
                            baseline_clean,
                            upstream_corrupted_outputs,
                            rescued_outputs,
                            clean_answers,
                        )
                    )
                ],
                "note": (
                    "After a matched corrupt residual transplant at an upstream "
                    "layer, restores only this space's coordinates from the clean "
                    "source-layer state. Statistical superiority to controls is still "
                    "required; this result alone MUST NOT satisfy a mediation claim."
                ),
            },
        }
    return report


__all__ = [
    "InterventionSpec",
    "ablate_hidden",
    "patch_hidden",
    "rescue_hidden",
    "run_causal_assay",
]
