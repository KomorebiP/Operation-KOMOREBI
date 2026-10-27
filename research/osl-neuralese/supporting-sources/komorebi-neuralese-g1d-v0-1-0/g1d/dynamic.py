from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import re
from typing import Any, Callable, Sequence

from .geometry import geometry_summary, matrix_spectrum, paired_geometry
from .integrity import verify_fixed_source_identity
from .probes import diagnostic_probe


CHECKPOINT_KEYS = {
    "schema",
    "completed_steps",
    "config_digest",
    "model_fingerprint",
    "package_manifest_sha256",
    "split_digests",
    "initial_workspace_hash",
    "backbone_hash_before",
    "workspace_state",
    "optimizer_state",
    "scaler_state",
    "rng_state",
    "latest_record",
}


def _state_dict_hash(state: dict[str, Any], torch: Any) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        if not torch.is_tensor(tensor) or tensor.layout != torch.strided:
            raise RuntimeError(f"workspace checkpoint value is not a dense tensor: {name}")
        if not bool(torch.isfinite(tensor).all().item()):
            raise RuntimeError(f"workspace checkpoint tensor is nonfinite: {name}")
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(tensor.shape)).encode("ascii"))
        digest.update(str(tensor.dtype).encode("ascii"))
        value = tensor.detach().cpu().contiguous()
        digest.update(value.numpy().tobytes(order="C"))
    return digest.hexdigest()


def _clean_workspace_state(checkpoint: dict[str, Any], expected: dict[str, Any], torch: Any) -> dict[str, Any]:
    if set(checkpoint) != CHECKPOINT_KEYS:
        raise RuntimeError(
            "checkpoint top-level fields differ from the registered v3 contract"
        )
    if checkpoint.get("schema") != "komorebi.neuralese.g1.checkpoint.v3":
        raise RuntimeError("checkpoint schema mismatch")
    observed = checkpoint.get("workspace_state")
    if not isinstance(observed, dict) or set(observed) != set(expected):
        raise RuntimeError("workspace checkpoint keys do not match the instantiated model")
    clean: dict[str, Any] = {}
    source_storage_pointers: set[int] = set()
    total_parameters = 0
    for name, reference in expected.items():
        tensor = observed[name]
        if (
            not torch.is_tensor(tensor)
            or tensor.layout != torch.strided
            or tensor.dtype != torch.float32
            or tuple(tensor.shape) != tuple(reference.shape)
            or not tensor.is_contiguous()
            or not bool(torch.isfinite(tensor).all().item())
        ):
            raise RuntimeError(f"invalid workspace tensor contract: {name}")
        source_pointer = int(tensor.untyped_storage().data_ptr())
        if source_pointer in source_storage_pointers:
            raise RuntimeError("workspace checkpoint tensors alias source storage")
        source_storage_pointers.add(source_pointer)
        contiguous = tensor.detach().cpu().contiguous().clone()
        total_parameters += int(contiguous.numel())
        clean[name] = contiguous
    if total_parameters != 334_529:
        raise RuntimeError(
            f"workspace parameter count mismatch: expected 334529, observed {total_parameters}"
        )
    return clean


def regenerate_splits(config: dict[str, Any]) -> dict[str, list[Any]]:
    from neuralese_g1.tasks import make_split

    task = config["task"]
    common = {"seed": int(config["seed"]), "states": int(task["states"])}
    result = {
        "train": make_split(
            **common,
            split="train",
            base_problems=int(task["train_base_problems"]),
            chain_min=int(task["train_chain_min"]),
            chain_max=int(task["train_chain_max"]),
        ),
        "validation": make_split(
            **common,
            split="validation",
            base_problems=int(task["validation_base_problems"]),
            chain_min=int(task["train_chain_min"]),
            chain_max=int(task["train_chain_max"]),
        ),
        "test_iid": make_split(
            **common,
            split="test_iid",
            base_problems=int(task["test_base_problems"]),
            chain_min=int(task["train_chain_min"]),
            chain_max=int(task["train_chain_max"]),
        ),
        "test_ood_depth": make_split(
            **common,
            split="test_ood_depth",
            base_problems=int(task["ood_base_problems"]),
            chain_min=int(task["ood_chain_min"]),
            chain_max=int(task["ood_chain_max"]),
        ),
    }
    random.Random(int(config["seed"]) + 91).shuffle(result["train"])
    return result


def unique_problems(examples: Sequence[Any]) -> list[Any]:
    unique: dict[tuple[str, int], Any] = {}
    for example in examples:
        unique.setdefault((str(example.split), int(example.counter)), example)
    return [unique[key] for key in sorted(unique)]


def balanced_subset(
    examples: Sequence[Any], *, per_state: int, states: int, seed: int = 38117
) -> list[Any]:
    groups: dict[int, list[Any]] = defaultdict(list)
    for example in unique_problems(examples):
        groups[int(example.final_state)].append(example)
    if set(groups) != set(range(states)) or any(
        len(group) < per_state for group in groups.values()
    ):
        raise RuntimeError("could not construct the balanced diagnostic subset")
    rng = random.Random(int(seed))
    selected = []
    for state in range(states):
        group = sorted(groups[state], key=lambda example: int(example.counter))
        selected.extend(rng.sample(group, per_state))
    return sorted(selected, key=lambda example: int(example.counter))


def _parse_prompt(example: Any, states: int) -> tuple[int, int, list[int]]:
    start_match = re.search(r"Start at ([0-9]+)\.", str(example.compute_prompt))
    transition_match = re.search(r"Transition: (.*?)\. Start", str(example.compute_prompt))
    if start_match is None or transition_match is None:
        raise RuntimeError(f"cannot parse registered compute prompt: {example.example_id}")
    start = int(start_match.group(1))
    mapping: dict[int, int] = {}
    for item in transition_match.group(1).split("; "):
        source, target = item.split("->")
        mapping[int(source)] = int(target)
    if set(mapping) != set(range(states)) or start not in mapping:
        raise RuntimeError(f"malformed transition mapping: {example.example_id}")
    return start, mapping[start], [mapping[index] for index in range(states)]


def metadata_tensors(examples: Sequence[Any], states: int, torch: Any) -> dict[str, Any]:
    parsed = [_parse_prompt(example, states) for example in examples]
    return {
        "counter": torch.tensor([int(example.counter) for example in examples], dtype=torch.long),
        "final_state": torch.tensor(
            [int(example.final_state) for example in examples], dtype=torch.long
        ),
        "start_state": torch.tensor([value[0] for value in parsed], dtype=torch.long),
        "transition_at_start": torch.tensor(
            [value[1] for value in parsed], dtype=torch.long
        ),
        "transition_map": torch.tensor(
            [value[2] for value in parsed], dtype=torch.long
        ),
        "applications": torch.tensor(
            [int(example.applications) for example in examples], dtype=torch.long
        ),
    }


def collect_trajectories(
    model: Any,
    tokenizer: Any,
    examples: Sequence[Any],
    *,
    mode: str,
    batch_size: int,
    max_length: int,
    device: str,
    progress: Callable[[str], None],
) -> dict[str, Any]:
    import torch

    representatives = list(examples)
    state_parts: list[list[Any]] = [[] for _ in range(model.recurrent_steps + 1)]
    injection_parts: list[list[Any]] = [[] for _ in range(model.recurrent_steps + 1)]
    source_parts: list[Any] = []
    consumed_feedback_delta_parts: list[Any] = []
    halt_parts: list[Any] = []
    gate_mean_parts: list[Any] = []
    gate_saturation_parts: list[Any] = []
    proposal_norm_parts: list[Any] = []
    transition_norm_parts: list[Any] = []
    total_batches = math.ceil(len(representatives) / batch_size)
    model.train(False)
    with torch.inference_mode():
        for batch_number, start in enumerate(range(0, len(representatives), batch_size), 1):
            batch_examples = representatives[start : start + batch_size]
            encoded = tokenizer(
                [example.compute_prompt for example in batch_examples],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length,
                add_special_tokens=True,
            )
            state, trace = model.encode(
                encoded["input_ids"].to(device),
                encoded["attention_mask"].to(device),
                mode=mode,
            )
            del state
            if (
                len(trace.states) != model.recurrent_steps + 1
                or len(trace.injections) != model.recurrent_steps
                or len(trace.feedback_states) != model.recurrent_steps + 1
                or len(trace.halt_probabilities) != model.recurrent_steps
            ):
                raise RuntimeError("recurrent trajectory length contract failed")
            for step, value in enumerate(trace.states):
                state_parts[step].append(value.detach().float().cpu())
                decoded = model.workspace.decode(value)
                injection_parts[step].append(decoded.detach().float().cpu())
            source = trace.feedback_states[0]
            source_parts.append(source.detach().float().cpu())
            consumed_feedback_delta_parts.append(
                torch.stack(
                    [
                        (value - source).detach().float().norm(dim=1).cpu()
                        for value in trace.feedback_states
                    ],
                    dim=1,
                )
            )
            halt_parts.append(
                torch.stack(
                    [value.detach().float().cpu() for value in trace.halt_probabilities],
                    dim=1,
                )
            )
            local_gate_means = []
            local_gate_saturation = []
            local_proposal_norms = []
            local_transition_norms = []
            for step in range(model.recurrent_steps):
                state_before = trace.states[step]
                feedback = torch.tanh(
                    model.workspace.context_projection(
                        trace.feedback_states[step + 1].float()
                    )
                )
                joined = torch.cat(
                    (model.workspace.state_norm(state_before), feedback), dim=-1
                )
                gate = torch.sigmoid(model.workspace.gate(joined))
                proposal = model.workspace.proposal(joined)
                local_gate_means.append(gate.mean(dim=1).detach().float().cpu())
                local_gate_saturation.append(
                    ((gate < 0.05) | (gate > 0.95))
                    .float()
                    .mean(dim=1)
                    .detach()
                    .cpu()
                )
                local_proposal_norms.append(
                    proposal.norm(dim=1).detach().float().cpu()
                )
                local_transition_norms.append(
                    (trace.states[step + 1] - state_before)
                    .norm(dim=1)
                    .detach()
                    .float()
                    .cpu()
                )
            gate_mean_parts.append(torch.stack(local_gate_means, dim=1))
            gate_saturation_parts.append(torch.stack(local_gate_saturation, dim=1))
            proposal_norm_parts.append(torch.stack(local_proposal_norms, dim=1))
            transition_norm_parts.append(torch.stack(local_transition_norms, dim=1))
            if batch_number == 1 or batch_number % 20 == 0 or batch_number == total_batches:
                progress(
                    f"G1D_FEATURES mode={mode} batch={batch_number}/{total_batches}"
                )
    states = torch.stack([torch.cat(parts, dim=0) for parts in state_parts], dim=1)
    injections = torch.stack(
        [torch.cat(parts, dim=0) for parts in injection_parts], dim=1
    )
    source = torch.cat(source_parts, dim=0)
    consumed_feedback_delta_norms = torch.cat(consumed_feedback_delta_parts, dim=0)
    halt = torch.cat(halt_parts, dim=0)
    update_diagnostics = {
        "gate_mean": torch.cat(gate_mean_parts, dim=0),
        "gate_saturation_fraction": torch.cat(gate_saturation_parts, dim=0),
        "proposal_norm": torch.cat(proposal_norm_parts, dim=0),
        "state_transition_norm": torch.cat(transition_norm_parts, dim=0),
    }
    expected_rows = len(representatives)
    if (
        states.shape != (expected_rows, model.recurrent_steps + 1, model.workspace.width)
        or injections.shape
        != (expected_rows, model.recurrent_steps + 1, model.workspace.hidden_size)
        or source.shape != (expected_rows, model.workspace.hidden_size)
        or not all(
            bool(torch.isfinite(value).all().item())
            for value in (
                states,
                injections,
                source,
                consumed_feedback_delta_norms,
                halt,
                *update_diagnostics.values(),
            )
        )
    ):
        raise RuntimeError("collected feature bank failed shape or finiteness checks")
    return {
        "states": states,
        "injections": injections,
        "source": source,
        "consumed_feedback_delta_from_initial_norms": consumed_feedback_delta_norms,
        "halt_probabilities": halt,
        "update_diagnostics": update_diagnostics,
    }


def _labels_for_probe(metadata: dict[str, Any], name: str) -> Any:
    return metadata[name]


def _categorical_heuristic_summary(
    predicted: Any, target: Any, applications: Any, states: int
) -> dict[str, Any]:
    def summarize(mask: Any) -> dict[str, Any]:
        local_prediction = predicted[mask]
        local_target = target[mask]
        recalls = []
        for state in range(states):
            class_mask = local_target == state
            if bool(class_mask.any().item()):
                recalls.append(
                    float((local_prediction[class_mask] == state).float().mean().item())
                )
        return {
            "count": int(local_target.shape[0]),
            "accuracy": float((local_prediction == local_target).float().mean().item()),
            "balanced_accuracy_over_present_classes": sum(recalls) / len(recalls),
            "present_class_count": len(recalls),
        }

    overall_mask = target == target
    depths = sorted(int(value) for value in applications.unique().tolist())
    return {
        "overall": summarize(overall_mask),
        "by_applications": {
            str(depth): summarize(applications == depth) for depth in depths
        },
    }


def run_probes(
    banks: dict[str, dict[str, Any]],
    metadata: dict[str, dict[str, Any]],
    *,
    states: int,
    recurrent_steps: int,
    seed: int,
    decoded_basis: Any,
) -> dict[str, Any]:
    import torch

    result: dict[str, Any] = {
        "final_state": {},
        "final_state_decoded_injection": {},
        "feedback_difference_final_state": {},
        "secondary": {},
    }
    splits = ("train", "validation", "test_iid", "test_ood_depth")

    def probe_features(feature_by_split: dict[str, Any], label_name: str, permutations: int, offset: int) -> dict[str, Any]:
        return diagnostic_probe(
            *(feature_by_split[split] for split in splits),
            *(_labels_for_probe(metadata[split], label_name) for split in splits),
            classes=states,
            permutation_count=permutations,
            seed=seed + offset,
        )

    def raw_metadata_features(values: dict[str, Any]) -> Any:
        pieces = [
            torch.nn.functional.one_hot(
                values["start_state"], num_classes=states
            ).float(),
            torch.nn.functional.one_hot(
                values["transition_at_start"], num_classes=states
            ).float(),
        ]
        transition_map = values["transition_map"]
        for source in range(states):
            pieces.append(
                torch.nn.functional.one_hot(
                    transition_map[:, source], num_classes=states
                ).float()
            )
        applications = values["applications"]
        if int(applications.min()) < 1 or int(applications.max()) > 10:
            raise RuntimeError("raw metadata depth is outside the registered 1..10 range")
        pieces.append(
            torch.nn.functional.one_hot(applications - 1, num_classes=10).float()
        )
        return torch.cat(pieces, dim=1)

    raw_features = {
        split: raw_metadata_features(metadata[split]) for split in splits
    }
    result["raw_metadata_baseline"] = probe_features(
        raw_features, "final_state", 127, 0
    )
    result["literal_heuristic_baselines"] = {
        split: {
            "start_state": _categorical_heuristic_summary(
                metadata[split]["start_state"],
                metadata[split]["final_state"],
                metadata[split]["applications"],
                states,
            ),
            "one_step_transition_at_start": _categorical_heuristic_summary(
                metadata[split]["transition_at_start"],
                metadata[split]["final_state"],
                metadata[split]["applications"],
                states,
            ),
        }
        for split in splits
    }

    source_features = {
        split: banks[split]["recurrent"]["source"] for split in splits
    }
    result["final_state"]["source_activation"] = probe_features(
        source_features, "final_state", 127, 1
    )
    for mode_index, mode in enumerate(("recurrent", "no_feedback")):
        for step in range(recurrent_steps + 1):
            features = {
                split: banks[split][mode]["states"][:, step, :] for split in splits
            }
            result["final_state"][f"{mode}_z{step}"] = probe_features(
                features, "final_state", 127, 100 + mode_index * 20 + step
            )
    for step in range(recurrent_steps + 1):
        features = {
            split: banks[split]["recurrent"]["injections"][:, step, :].double()
            @ decoded_basis
            for split in splits
        }
        result["final_state_decoded_injection"][f"recurrent_delta{step}"] = (
            probe_features(features, "final_state", 127, 300 + step)
        )
    no_feedback_final_injection = {
        split: banks[split]["no_feedback"]["injections"][:, recurrent_steps, :]
        .double()
        @ decoded_basis
        for split in splits
    }
    result["final_state_decoded_injection"][
        f"no_feedback_delta{recurrent_steps}"
    ] = probe_features(
        no_feedback_final_injection,
        "final_state",
        127,
        320 + recurrent_steps,
    )
    feedback_difference = {
        split: banks[split]["recurrent"]["states"][:, recurrent_steps, :]
        - banks[split]["no_feedback"]["states"][:, recurrent_steps, :]
        for split in splits
    }
    result["feedback_difference_final_state"][
        f"recurrent_minus_no_feedback_z{recurrent_steps}"
    ] = probe_features(
        feedback_difference,
        "final_state",
        127,
        400 + recurrent_steps,
    )
    for label_index, label_name in enumerate(("start_state", "transition_at_start")):
        result["secondary"][label_name] = {}
        for representation, features in (
            ("source_activation", source_features),
            (
                "recurrent_z0",
                {
                    split: banks[split]["recurrent"]["states"][:, 0, :]
                    for split in splits
                },
            ),
            (
                f"recurrent_z{recurrent_steps}",
                {
                    split: banks[split]["recurrent"]["states"][:, recurrent_steps, :]
                    for split in splits
                },
            ),
        ):
            result["secondary"][label_name][representation] = probe_features(
                features,
                label_name,
                127,
                500 + label_index * 100 + len(result["secondary"][label_name]),
            )
    raw = result["raw_metadata_baseline"]
    metadata_scores = {
        "ridge": {
            split: raw["ridge"][split]["balanced_accuracy"]
            for split in ("iid", "ood")
        },
        "nearest_centroid": {
            split: raw["nonparametric"][split]["nearest_centroid"][
                "balanced_accuracy"
            ]
            for split in ("iid", "ood")
        },
        "five_nearest_neighbors": {
            split: raw["nonparametric"][split]["five_nearest_neighbors"][
                "balanced_accuracy"
            ]
            for split in ("iid", "ood")
        },
    }
    result["raw_metadata_method_balanced_accuracy"] = metadata_scores
    for group_name in (
        "final_state",
        "final_state_decoded_injection",
        "feedback_difference_final_state",
    ):
        for probe in result[group_name].values():
            iid_balanced = probe["ridge"]["iid"]["balanced_accuracy"]
            ood_balanced = probe["ridge"]["ood"]["balanced_accuracy"]
            lifts = {
                "ridge": {
                    "iid": iid_balanced - metadata_scores["ridge"]["iid"],
                    "ood": ood_balanced - metadata_scores["ridge"]["ood"],
                }
            }
            nonparametric_candidates = []
            for method in ("nearest_centroid", "five_nearest_neighbors"):
                method_iid = probe["nonparametric"]["iid"][method][
                    "balanced_accuracy"
                ]
                method_ood = probe["nonparametric"]["ood"][method][
                    "balanced_accuracy"
                ]
                lifts[method] = {
                    "iid": method_iid - metadata_scores[method]["iid"],
                    "ood": method_ood - metadata_scores[method]["ood"],
                }
                nonparametric_candidates.append(
                    method_iid >= 0.60 and lifts[method]["iid"] >= 0.10
                )
            probe["lift_over_raw_metadata_by_method"] = lifts
            probe["iid_lift_over_raw_metadata"] = lifts["ridge"]["iid"]
            probe["ood_lift_over_raw_metadata"] = lifts["ridge"]["ood"]
            probe["nonparametric_candidate"] = bool(
                any(nonparametric_candidates)
            )
            if (
                probe["tier"] == "STRONG_LINEAR"
                and iid_balanced >= 0.60
                and lifts["ridge"]["iid"] >= 0.10
            ):
                iid_evidence = "STRONG_IID_FINAL_STATE_SIGNAL_ABOVE_METADATA"
            elif probe["tier"] == "STRONG_LINEAR":
                iid_evidence = "IID_LINEAR_SIGNAL_WITHOUT_METADATA_LIFT"
            elif probe["tier"] == "WEAK_LINEAR":
                iid_evidence = "WEAK_IID_LINEAR_SIGNAL"
            elif probe["nonparametric_candidate"]:
                iid_evidence = "IID_NONLINEAR_CANDIDATE_UNCONFIRMED"
            else:
                iid_evidence = "NO_ROBUST_IID_FINAL_STATE_SIGNAL_DETECTED"
            if (
                iid_evidence == "STRONG_IID_FINAL_STATE_SIGNAL_ABOVE_METADATA"
                and ood_balanced >= 0.50
                and probe["ridge"]["ood"]["macro_f1"] >= 0.45
                and lifts["ridge"]["ood"] >= 0.10
            ):
                ood_evidence = "OOD_GENERALIZING_FINAL_STATE_SIGNAL_ABOVE_METADATA"
            else:
                ood_evidence = "NO_OOD_GENERALIZATION_ESTABLISHED"
            probe["iid_signal_evidence"] = iid_evidence
            probe["ood_signal_evidence"] = ood_evidence
            probe["computation_evidence"] = (
                "REPRESENTATIONAL_SIGNAL_ONLY_NOT_COMPUTATION_PROOF"
            )
    return result


def decoded_injection_basis(projection: Any) -> tuple[Any, dict[str, Any]]:
    """Build an isometric basis for every vector emitted by the decoder."""

    import torch

    weight = projection.weight.detach().cpu().double()
    bias_parameter = projection.bias
    bias = (
        torch.zeros(weight.shape[0], dtype=weight.dtype)
        if bias_parameter is None
        else bias_parameter.detach().cpu().double()
    )
    left, _, _ = torch.linalg.svd(weight, full_matrices=False)
    basis = left
    bias_residual = bias - basis @ (basis.T @ bias)
    tolerance = max(float(bias.norm()) * 1e-12, 1e-14)
    if float(bias_residual.norm()) > tolerance:
        basis = torch.cat((basis, (bias_residual / bias_residual.norm()).unsqueeze(1)), dim=1)
    weight_residual = weight - basis @ (basis.T @ weight)
    final_bias_residual = bias - basis @ (basis.T @ bias)
    summary = {
        "schema": "komorebi.neuralese.g1d.decoded_basis.v1",
        "original_width": int(weight.shape[0]),
        "analysis_width": int(basis.shape[1]),
        "decoder_has_bias": bias_parameter is not None,
        "weight_relative_reconstruction_error": float(
            weight_residual.norm() / weight.norm().clamp_min(1e-30)
        ),
        "bias_relative_reconstruction_error": float(
            final_bias_residual.norm() / bias.norm().clamp_min(1e-30)
        ),
        "purpose": (
            "Orthonormal lossless-span coordinates reduce decoded injections before "
            "geometry and probes; full 896D tensors remain in feature_bank.pt."
        ),
    }
    if (
        summary["weight_relative_reconstruction_error"] > 1e-10
        or summary["bias_relative_reconstruction_error"] > 1e-10
    ):
        raise RuntimeError("decoded-injection analysis basis is not lossless")
    return basis, summary


def run_geometry(
    banks: dict[str, dict[str, Any]],
    metadata: dict[str, dict[str, Any]],
    *,
    recurrent_steps: int,
    decoded_basis: Any,
    decoded_basis_summary: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    geometry: dict[str, Any] = {
        "decoded_injection_analysis_basis": decoded_basis_summary
    }
    recurrence: dict[str, Any] = {}
    for split in ("train", "validation", "test_iid", "test_ood_depth"):
        labels = metadata[split]["final_state"]
        geometry[split] = {
            "source_activation": geometry_summary(
                banks[split]["recurrent"]["source"], labels
            ),
            "recurrent": {},
            "no_feedback": {},
        }
        recurrence[split] = {"state": {}, "injection": {}}
        for mode in ("recurrent", "no_feedback"):
            for step in range(recurrent_steps + 1):
                geometry[split][mode][f"z{step}"] = {
                    "state": geometry_summary(
                        banks[split][mode]["states"][:, step, :], labels
                    ),
                    "decoded_injection": geometry_summary(
                        banks[split][mode]["injections"][:, step, :].double()
                        @ decoded_basis,
                        labels,
                    ),
                }
        for step in range(recurrent_steps + 1):
            recurrence[split]["state"][f"z{step}"] = paired_geometry(
                banks[split]["recurrent"]["states"][:, step, :],
                banks[split]["no_feedback"]["states"][:, step, :],
            )
            recurrence[split]["injection"][f"z{step}"] = paired_geometry(
                banks[split]["recurrent"]["injections"][:, step, :].double()
                @ decoded_basis,
                banks[split]["no_feedback"]["injections"][:, step, :].double()
                @ decoded_basis,
            )
        recurrence[split]["consumed_feedback_delta_from_initial_norm_mean_by_step"] = {
            mode: [
                float(value)
                for value in banks[split][mode][
                    "consumed_feedback_delta_from_initial_norms"
                ].mean(dim=0)
            ]
            for mode in ("recurrent", "no_feedback")
        }
        recurrence[split]["workspace_update_mean_by_step"] = {
            mode: {
                name: [float(value) for value in tensor.mean(dim=0)]
                for name, tensor in banks[split][mode]["update_diagnostics"].items()
            }
            for mode in ("recurrent", "no_feedback")
        }
    return geometry, recurrence


def _semantic_target(example: Any, state: int) -> str:
    if example.query_type == "direct":
        return str(state)
    if example.query_type == "parity":
        return "E" if state % 2 == 0 else "O"
    if example.query_type == "codebook":
        match = re.search(r"A codebook is now revealed: (.*?)\. Use", example.query_prompt)
        if match is None:
            raise RuntimeError(f"cannot parse codebook query: {example.example_id}")
        mapping = {
            int(source): symbol
            for source, symbol in (item.split("=") for item in match.group(1).split("; "))
        }
        return mapping[int(state)]
    raise RuntimeError(f"unknown query type: {example.query_type}")


def donor_indices(representatives: Sequence[Any], states: int) -> tuple[list[int], list[int]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for index, example in enumerate(representatives):
        groups[int(example.final_state)].append(index)
    if set(groups) != set(range(states)) or len({len(value) for value in groups.values()}) != 1:
        raise RuntimeError("diagnostic donor construction requires balanced final states")
    same = [-1] * len(representatives)
    incompatible = [-1] * len(representatives)
    for state in range(states):
        receivers = sorted(groups[state], key=lambda index: int(representatives[index].counter))
        same_donors = receivers[1:] + receivers[:1]
        wrong_donors = sorted(
            groups[(state + 3) % states],
            key=lambda index: int(representatives[index].counter),
        )
        for receiver, same_donor, wrong_donor in zip(
            receivers, same_donors, wrong_donors
        ):
            same[receiver] = same_donor
            incompatible[receiver] = wrong_donor
    if (
        sorted(same) != list(range(len(representatives)))
        or sorted(incompatible) != list(range(len(representatives)))
        or any(index == donor for index, donor in enumerate(same))
        or any(
            int(representatives[index].final_state)
            == int(representatives[donor].final_state)
            for index, donor in enumerate(incompatible)
        )
    ):
        raise RuntimeError("diagnostic donor contract failed")
    return same, incompatible


def _expand_problem_states(examples: Sequence[Any], representatives: Sequence[Any], states: Any) -> Any:
    import torch

    by_counter = {int(example.counter): index for index, example in enumerate(representatives)}
    indices = torch.tensor([by_counter[int(example.counter)] for example in examples], dtype=torch.long)
    return states.index_select(0, indices)


def answer_condition(
    model: Any,
    tokenizer: Any,
    examples: Sequence[Any],
    states: Any | None,
    donor_final_states: Sequence[int] | None,
    *,
    condition: str,
    target_token_map: dict[str, int],
    batch_size: int,
    max_length: int,
    device: str,
) -> list[dict[str, Any]]:
    import torch

    registered_text = sorted(target_token_map, key=lambda value: int(target_token_map[value]))
    registered_ids = torch.tensor(
        [int(target_token_map[value]) for value in registered_text],
        dtype=torch.long,
        device=device,
    )
    family_text = {
        "direct": [str(value) for value in range(6)],
        "parity": ["E", "O"],
        "codebook": list("ABCDEF"),
    }
    records: list[dict[str, Any]] = []
    model.train(False)
    with torch.inference_mode():
        for start in range(0, len(examples), batch_size):
            batch_examples = examples[start : start + batch_size]
            local_states = (
                None
                if states is None
                else states[start : start + len(batch_examples)].to(device)
            )
            query = tokenizer(
                [example.query_prompt for example in batch_examples],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length,
                add_special_tokens=True,
            )
            logits = model.answer(
                query["input_ids"].to(device),
                query["attention_mask"].to(device),
                local_states,
            ).float()
            predicted_ids = logits.argmax(dim=1)
            log_probabilities = torch.log_softmax(logits, dim=1)
            registered_logits = logits.index_select(1, registered_ids)
            for local_index, example in enumerate(batch_examples):
                receiver_text = str(example.target_text)
                receiver_id = int(target_token_map[receiver_text])
                family_ids = [int(target_token_map[value]) for value in family_text[example.query_type]]
                wrong_ids = [value for value in family_ids if value != receiver_id]
                donor_state = (
                    None
                    if donor_final_states is None
                    else int(donor_final_states[start + local_index])
                )
                donor_text = (
                    None if donor_state is None else _semantic_target(example, donor_state)
                )
                predicted_id = int(predicted_ids[local_index].item())
                record = {
                    "condition": condition,
                    "split": str(example.split),
                    "example_id": str(example.example_id),
                    "counter": int(example.counter),
                    "query_type": str(example.query_type),
                    "final_state": int(example.final_state),
                    "donor_final_state": donor_state,
                    "predicted_token_id": predicted_id,
                    "predicted_text": tokenizer.decode([predicted_id]),
                    "receiver_target_text": receiver_text,
                    "receiver_target_token_id": receiver_id,
                    "receiver_correct": predicted_id == receiver_id,
                    "donor_target_text": donor_text,
                    "donor_target_token_id": (
                        None if donor_text is None else int(target_token_map[donor_text])
                    ),
                    "donor_correct": (
                        None
                        if donor_text is None
                        else predicted_id == int(target_token_map[donor_text])
                    ),
                    "receiver_target_log_probability": float(
                        log_probabilities[local_index, receiver_id].item()
                    ),
                    "receiver_target_margin_family": float(
                        logits[local_index, receiver_id].item()
                        - logits[local_index, wrong_ids].max().item()
                    ),
                    "registered_logits": {
                        text: float(value)
                        for text, value in zip(
                            registered_text, registered_logits[local_index].tolist()
                        )
                    },
                }
                if donor_text is not None:
                    donor_id = int(target_token_map[donor_text])
                    donor_wrong = [value for value in family_ids if value != donor_id]
                    record["donor_target_log_probability"] = float(
                        log_probabilities[local_index, donor_id].item()
                    )
                    record["donor_target_margin_family"] = float(
                        logits[local_index, donor_id].item()
                        - logits[local_index, donor_wrong].max().item()
                    )
                records.append(record)
    return records


def _mean_ci99_by_counter(records: Sequence[dict[str, Any]], field: str) -> list[float]:
    values: dict[int, list[float]] = defaultdict(list)
    for record in records:
        value = record.get(field)
        if value is not None:
            values[int(record["counter"])].append(float(value))
    clustered = [sum(group) / len(group) for group in values.values()]
    if not clustered:
        return [0.0, 0.0]
    mean = sum(clustered) / len(clustered)
    if len(clustered) == 1:
        return [mean, mean]
    variance = sum((value - mean) ** 2 for value in clustered) / (len(clustered) - 1)
    radius = 2.5758293035489004 * math.sqrt(variance / len(clustered))
    return [mean - radius, mean + radius]


def summarize_interventions(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["split"], record["condition"])].append(record)
    result: dict[str, Any] = {}
    for (split, condition), rows in sorted(grouped.items()):
        split_result = result.setdefault(split, {})
        donor_rows = [row for row in rows if row.get("donor_correct") is not None]
        split_result[condition] = {
            "count": len(rows),
            "receiver_accuracy": sum(bool(row["receiver_correct"]) for row in rows)
            / len(rows),
            "receiver_accuracy_by_query": {
                query: sum(
                    bool(row["receiver_correct"])
                    for row in rows
                    if row["query_type"] == query
                )
                / sum(row["query_type"] == query for row in rows)
                for query in ("direct", "parity", "codebook")
            },
            "donor_accuracy": (
                None
                if not donor_rows
                else sum(bool(row["donor_correct"]) for row in donor_rows)
                / len(donor_rows)
            ),
            "donor_accuracy_by_query": (
                None
                if not donor_rows
                else {
                    query: sum(
                        bool(row["donor_correct"])
                        for row in donor_rows
                        if row["query_type"] == query
                    )
                    / sum(row["query_type"] == query for row in donor_rows)
                    for query in ("direct", "parity", "codebook")
                }
            ),
            "receiver_margin_mean": sum(
                float(row["receiver_target_margin_family"]) for row in rows
            )
            / len(rows),
            "receiver_margin_clustered_99pct": _mean_ci99_by_counter(
                rows, "receiver_target_margin_family"
            ),
            "donor_margin_mean": (
                None
                if not donor_rows
                else sum(float(row["donor_target_margin_family"]) for row in donor_rows)
                / len(donor_rows)
            ),
            "donor_margin_clustered_99pct": (
                None
                if not donor_rows
                else _mean_ci99_by_counter(donor_rows, "donor_target_margin_family")
            ),
            "prediction_counts": dict(
                sorted(Counter(str(row["predicted_text"]) for row in rows).items())
            ),
        }
    family_text = {
        "direct": [str(value) for value in range(6)],
        "parity": ["E", "O"],
        "codebook": list("ABCDEF"),
    }

    def probabilities(record: dict[str, Any]) -> list[float]:
        logits = [float(record["registered_logits"][name]) for name in family_text[record["query_type"]]]
        maximum = max(logits)
        weights = [math.exp(value - maximum) for value in logits]
        total = sum(weights)
        return [value / total for value in weights]

    def js_divergence(left: list[float], right: list[float]) -> float:
        middle = [(a + b) / 2.0 for a, b in zip(left, right)]
        result = 0.0
        for distribution in (left, right):
            result += 0.5 * sum(
                value * math.log(value / center)
                for value, center in zip(distribution, middle)
                if value > 0.0
            )
        return result

    for split in ("test_iid", "test_ood_depth"):
        base_rows = {
            row["example_id"]: row
            for row in grouped[(split, "own_z4")]
        }
        sensitivity: dict[str, Any] = {}
        for (candidate_split, condition), rows in sorted(grouped.items()):
            if candidate_split != split or condition == "own_z4":
                continue
            aligned = [(base_rows[row["example_id"]], row) for row in rows]
            same = sum(
                left["predicted_token_id"] == right["predicted_token_id"]
                for left, right in aligned
            )
            js_values = [
                js_divergence(probabilities(left), probabilities(right))
                for left, right in aligned
            ]
            target_log_probability_shift = [
                float(right["receiver_target_log_probability"])
                - float(left["receiver_target_log_probability"])
                for left, right in aligned
            ]
            sensitivity[condition] = {
                "top1_agreement_with_own_z4": same / len(aligned),
                "changed_count": len(aligned) - same,
                "mean_family_js_divergence": sum(js_values) / len(js_values),
                "mean_receiver_target_log_probability_shift": sum(
                    target_log_probability_shift
                )
                / len(target_log_probability_shift),
            }
        result[split]["sensitivity_to_own_z4"] = sensitivity
        incompatible_rows = grouped[(split, "incompatible_state_donor")]
        preference_rows = []
        for row in incompatible_rows:
            own = base_rows[row["example_id"]]
            donor_text = str(row["donor_target_text"])
            receiver_text = str(row["receiver_target_text"])
            shifted_preference = (
                float(row["registered_logits"][donor_text])
                - float(row["registered_logits"][receiver_text])
                - float(own["registered_logits"][donor_text])
                + float(own["registered_logits"][receiver_text])
            )
            preference_rows.append(
                {
                    "counter": row["counter"],
                    "query_type": row["query_type"],
                    "shift": shifted_preference,
                }
            )
        overall_mean = sum(row["shift"] for row in preference_rows) / len(
            preference_rows
        )
        result[split]["incompatible_donor_semantic_transport"] = {
            "definition": (
                "Change from own-z4 to incompatible-donor state in donor-target "
                "logit minus receiver-target logit. Positive values follow donor semantics."
            ),
            "mean_preference_shift": overall_mean,
            "clustered_99pct": _mean_ci99_by_counter(preference_rows, "shift"),
            "by_query": {
                query: {
                    "mean_preference_shift": sum(
                        row["shift"]
                        for row in preference_rows
                        if row["query_type"] == query
                    )
                    / sum(row["query_type"] == query for row in preference_rows),
                    "clustered_99pct": _mean_ci99_by_counter(
                        [
                            row
                            for row in preference_rows
                            if row["query_type"] == query
                        ],
                        "shift",
                    ),
                }
                for query in ("direct", "parity", "codebook")
            },
        }
    return result


def run_interventions(
    model: Any,
    tokenizer: Any,
    splits: dict[str, list[Any]],
    representatives: dict[str, list[Any]],
    banks: dict[str, dict[str, Any]],
    *,
    target_token_map: dict[str, int],
    config: dict[str, Any],
    progress: Callable[[str], None],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    import torch

    all_records: list[dict[str, Any]] = []
    state_count = int(config["task"]["states"])
    final_step = int(config["workspace"]["steps"])
    projection = model.workspace.output_projection
    original_projection = projection.weight.detach().clone()
    with torch.no_grad():
        analysis_projection = original_projection.detach().cpu().float()
        left, singular, right = torch.linalg.svd(
            analysis_projection, full_matrices=False
        )
        rank_one_projection = (
            left[:, :1] * singular[:1]
        ) @ right[:1, :]
        residual_projection = analysis_projection - rank_one_projection
    training_final_mean = banks["train"]["recurrent"]["states"][
        :, final_step, :
    ].mean(dim=0, keepdim=True)
    for split in ("test_iid", "test_ood_depth"):
        examples = splits[split]
        reps = representatives[split]
        rec_states = banks[split]["recurrent"]["states"]
        nf_states = banks[split]["no_feedback"]["states"]
        same, incompatible = donor_indices(reps, state_count)
        same_tensor = rec_states[torch.tensor(same), final_step, :]
        incompatible_tensor = rec_states[
            torch.tensor(incompatible), final_step, :
        ]
        mean_tensor = training_final_mean.expand(len(reps), -1)
        condition_rows: list[tuple[str, Any | None, list[int] | None]] = []
        for step in range(final_step + 1):
            condition_rows.append((f"own_z{step}", rec_states[:, step, :], None))
        condition_rows.extend(
            [
                ("no_feedback_z4", nf_states[:, final_step, :], None),
                (
                    "same_final_state_donor",
                    same_tensor,
                    [int(reps[index].final_state) for index in same],
                ),
                (
                    "incompatible_state_donor",
                    incompatible_tensor,
                    [int(reps[index].final_state) for index in incompatible],
                ),
                ("mean_state", mean_tensor, None),
                (
                    "mean_centered_own_z4",
                    rec_states[:, final_step, :]
                    - training_final_mean,
                    None,
                ),
                ("zero", None, None),
            ]
        )
        for condition_index, (condition, base_states, donor_base_states) in enumerate(
            condition_rows, 1
        ):
            progress(
                f"G1D_INTERVENTION split={split} condition={condition} "
                f"{condition_index}/{len(condition_rows)}"
            )
            expanded = (
                None
                if base_states is None
                else _expand_problem_states(examples, reps, base_states)
            )
            donor_expanded = None
            if donor_base_states is not None:
                donor_by_counter = {
                    int(rep.counter): int(donor_base_states[index])
                    for index, rep in enumerate(reps)
                }
                donor_expanded = [
                    donor_by_counter[int(example.counter)] for example in examples
                ]
            all_records.extend(
                answer_condition(
                    model,
                    tokenizer,
                    examples,
                    expanded,
                    donor_expanded,
                    condition=condition,
                    target_token_map=target_token_map,
                    batch_size=int(config["training"]["eval_batch_size"]),
                    max_length=int(config["model"]["max_sequence_length"]),
                    device=str(config["model"]["device"]),
                )
            )
        expanded_own_final = _expand_problem_states(
            examples, reps, rec_states[:, final_step, :]
        )
        try:
            for projection_name, projection_value in (
                ("rank1_projection_own_z4", rank_one_projection),
                ("residual_projection_own_z4", residual_projection),
            ):
                progress(
                    f"G1D_PROJECTION_INTERVENTION split={split} "
                    f"condition={projection_name}"
                )
                with torch.no_grad():
                    projection.weight.copy_(
                        projection_value.to(
                            device=projection.weight.device,
                            dtype=projection.weight.dtype,
                        )
                    )
                all_records.extend(
                    answer_condition(
                        model,
                        tokenizer,
                        examples,
                        expanded_own_final,
                        None,
                        condition=projection_name,
                        target_token_map=target_token_map,
                        batch_size=int(config["training"]["eval_batch_size"]),
                        max_length=int(config["model"]["max_sequence_length"]),
                        device=str(config["model"]["device"]),
                    )
                )
        finally:
            with torch.no_grad():
                projection.weight.copy_(original_projection)
    return summarize_interventions(all_records), all_records


def replay_check(
    intervention_records: Sequence[dict[str, Any]], saved_predictions: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    condition_to_mode = {
        "own_z4": "recurrent",
        "no_feedback_z4": "no_feedback",
        "zero": "zero",
    }
    result: dict[str, Any] = {}
    for condition, mode in condition_to_mode.items():
        expected_rows = [row for row in saved_predictions if row.get("mode") == mode]
        rows = [row for row in intervention_records if row.get("condition") == condition]
        expected: dict[tuple[str, str], int] = {}
        observed: dict[tuple[str, str], int] = {}
        for row in expected_rows:
            key = (str(row["split"]), str(row["example_id"]))
            if key in expected:
                raise RuntimeError(f"duplicate saved replay key for mode {mode}: {key}")
            expected[key] = int(row["predicted_token_id"])
        for row in rows:
            key = (str(row["split"]), str(row["example_id"]))
            if key in observed:
                raise RuntimeError(
                    f"duplicate intervention replay key for condition {condition}: {key}"
                )
            observed[key] = int(row["predicted_token_id"])
        if not expected or set(observed) != set(expected):
            raise RuntimeError(
                f"replay key set mismatch for {condition}: "
                f"expected={len(expected)}, observed={len(observed)}"
            )
        matches = sum(
            observed[key] == expected[key] for key in expected
        )
        result[condition] = {
            "mode": mode,
            "matches": matches,
            "count": len(expected),
            "exact": matches == len(expected),
        }
    if not all(value["exact"] for value in result.values()):
        raise RuntimeError(f"dynamic replay did not reproduce saved predictions: {result}")
    return result


def checkpoint_spectrum(workspace_state: dict[str, Any]) -> dict[str, Any]:
    matrices = {
        name: matrix_spectrum(value)
        for name, value in sorted(workspace_state.items())
        if value.ndim == 2
    }
    output = matrices.get("output_projection.weight")
    if output is None:
        raise RuntimeError("workspace output projection is missing")
    return {
        "schema": "komorebi.neuralese.g1d.checkpoint_spectrum.v1",
        "matrices": matrices,
        "output_projection_rank_collapse_signature": bool(
            output["top1_energy_fraction"] >= 0.95 and output["stable_rank"] <= 1.5
        ),
    }


def classify_localization(
    *,
    source_robust: bool,
    initial_iid: bool,
    initial_robust: bool,
    final_iid: bool,
    final_robust: bool,
    decoded_iid: bool,
    projection_collapse: bool,
    rank1_dominance: bool,
    same_state_invariant: bool,
    positive_semantic_transport_established: bool,
) -> str:
    """Return a cautious localization hypothesis, never a causal proof claim."""

    if source_robust and not initial_iid and not final_iid:
        return "CONSISTENT_WITH_INITIALIZER_SIGNAL_LOSS"
    if initial_robust and not final_iid:
        return "CONSISTENT_WITH_RECURRENT_SIGNAL_ERASURE"
    if final_iid and not decoded_iid and projection_collapse and rank1_dominance:
        return "CONSISTENT_WITH_OUTPUT_PROJECTION_BOTTLENECK"
    if (
        decoded_iid
        and same_state_invariant
        and not positive_semantic_transport_established
    ):
        return "CONSISTENT_WITH_DOWNSTREAM_ANSWER_INTERFACE_NONUSE"
    if final_iid and not final_robust:
        return "IID_STATE_SIGNAL_WITHOUT_OOD_GENERALIZATION"
    if projection_collapse and not final_iid and not decoded_iid:
        return "RANK_ONE_STEERING_WITH_NO_ROBUST_FINAL_STATE_SIGNAL_DETECTED"
    if not final_iid and not decoded_iid:
        return "NO_ROBUST_FINAL_STATE_SIGNAL_DETECTED"
    return "INCONCLUSIVE_OR_MIXED_LOCALIZATION"


def load_and_diagnose(
    *,
    model_path: str | Path,
    run_dir: str | Path,
    static_analysis: dict[str, Any],
    progress: Callable[[str], None],
) -> dict[str, Any]:
    import torch

    from neuralese_g1.config import validate_config, config_digest
    from neuralese_g1.model import FrozenRecurrentCausalLM
    from neuralese_g1.results import verify_run_directory
    from neuralese_g1.runtime import (
        file_inventory_fingerprint,
        load_local_model,
        module_state_hash,
        seed_everything,
    )
    from neuralese_g1.tasks import split_digest
    from neuralese_g1.token_contract import validate_single_token_targets

    run_root = Path(run_dir).resolve()
    model_root = Path(model_path).resolve()
    progress("G1D_VERIFY_SOURCE_RUN=START")
    verification = verify_run_directory(run_root, require_checkpoint_validation=True)
    fixed_source_verification = verify_fixed_source_identity(run_root, verification)
    config = json.loads((run_root / "resolved_config.json").read_text(encoding="utf-8"))
    unsigned = dict(config)
    stored_digest = unsigned.pop("config_digest")
    validate_config(unsigned)
    if config_digest(unsigned) != stored_digest:
        raise RuntimeError("diagnostic config digest mismatch")
    preflight = json.loads((run_root / "preflight.json").read_text(encoding="utf-8"))
    import numpy
    import transformers

    recorded_environment = preflight.get("environment", {})
    observed_environment = {
        "python": platform.python_version(),
        "torch": str(torch.__version__),
        "transformers": str(transformers.__version__),
        "numpy": str(numpy.__version__),
        "cuda_device": (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        ),
    }
    recorded_runtime = {
        name: str(recorded_environment.get(name)) for name in observed_environment
    }
    if observed_environment != recorded_runtime:
        raise RuntimeError(
            "diagnostic runtime differs from the pilot runtime: "
            f"observed={observed_environment}, recorded={recorded_runtime}"
        )
    fingerprint = file_inventory_fingerprint(model_root)
    if (
        fingerprint["files"] != preflight["model"]["files"]
        or fingerprint["metadata_sha256"] != preflight["model"]["metadata_sha256"]
    ):
        raise RuntimeError("local model bytes do not match the pilot model fingerprint")
    relocation_warning = str(model_root) != str(preflight["model"]["path"])

    seed_everything(int(config["seed"]))
    device = str(config["model"]["device"])
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")
    progress("G1D_MODEL_LOAD=START")
    tokenizer, backbone, dtype = load_local_model(
        model_root,
        device=device,
        dtype_name=str(config["model"]["dtype"]),
        trust_remote_code=bool(config["model"]["trust_remote_code"]),
        attention_implementation=str(config["model"]["attention_implementation"]),
    )
    observed_identity = {
        "model_type": str(backbone.config.model_type),
        "architecture": backbone.__class__.__name__,
        "hidden_size": int(backbone.config.hidden_size),
        "layers": int(backbone.config.num_hidden_layers),
    }
    if observed_identity != preflight["model_identity"]:
        raise RuntimeError("loaded model identity differs from the pilot")
    model = FrozenRecurrentCausalLM(
        backbone,
        source_layer=int(config["model"]["source_layer"]),
        workspace_width=int(config["workspace"]["width"]),
        recurrent_steps=int(config["workspace"]["steps"]),
        injection_scale=float(config["workspace"]["injection_scale"]),
        state_clip=float(config["workspace"]["state_clip"]),
        dropout=float(config["workspace"]["dropout"]),
    ).to(device)
    checkpoint = torch.load(
        run_root / "checkpoint.pt", map_location="cpu", weights_only=True
    )
    if not isinstance(checkpoint, dict):
        raise RuntimeError("restricted checkpoint root is not a dictionary")
    expected_state = model.workspace.state_dict()
    clean_state = _clean_workspace_state(checkpoint, expected_state, torch)
    if checkpoint["completed_steps"] != int(config["training"]["steps"]):
        raise RuntimeError("checkpoint step count mismatch")
    if checkpoint["config_digest"] != stored_digest:
        raise RuntimeError("checkpoint config digest mismatch")
    if checkpoint["model_fingerprint"] != preflight["model"]:
        raise RuntimeError("checkpoint model provenance mismatch")
    workspace_hash = _state_dict_hash(clean_state, torch)
    if workspace_hash != json.loads(
        (run_root / "run_summary.json").read_text(encoding="utf-8")
    )["training"]["workspace_hash_after"]:
        raise RuntimeError("workspace checkpoint hash mismatch")
    spectrum = checkpoint_spectrum(clean_state)
    del checkpoint
    model.workspace.load_state_dict(clean_state, strict=True)
    del clean_state
    if not model.backbone_is_frozen:
        raise RuntimeError("diagnostic model backbone is not frozen")

    progress("G1D_BACKBONE_HASH_BEFORE=START")
    backbone_hash_before = module_state_hash(model.backbone)
    if backbone_hash_before != preflight["backbone_hash_before"]:
        raise RuntimeError("loaded backbone tensor hash differs from the pilot")
    workspace_hash_before = module_state_hash(model.workspace)

    splits = regenerate_splits(config)
    expected_digests = preflight["split_digests"]
    if {name: split_digest(rows) for name, rows in splits.items()} != expected_digests:
        raise RuntimeError("regenerated diagnostic splits differ from the pilot")
    all_examples = [example for rows in splits.values() for example in rows]
    token_map = validate_single_token_targets(tokenizer, all_examples)
    if token_map != preflight["single_token_targets"]:
        raise RuntimeError("diagnostic tokenizer contract differs from the pilot")

    state_count = int(config["task"]["states"])
    reps = {
        "train": balanced_subset(
            splits["train"],
            per_state=80,
            states=state_count,
            seed=int(config["seed"]) + 38117,
        ),
        "validation": unique_problems(splits["validation"]),
        "test_iid": unique_problems(splits["test_iid"]),
        "test_ood_depth": unique_problems(splits["test_ood_depth"]),
    }
    selection = {}
    for split, rows in reps.items():
        payload = [
            {
                "counter": int(example.counter),
                "example_id": str(example.example_id),
                "final_state": int(example.final_state),
            }
            for example in rows
        ]
        selection[split] = {
            "rows": len(payload),
            "sha256": hashlib.sha256(
                json.dumps(
                    payload, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest(),
        }
    metadata = {
        split: metadata_tensors(rows, state_count, torch) for split, rows in reps.items()
    }
    banks: dict[str, dict[str, Any]] = {}
    for split in ("train", "validation", "test_iid", "test_ood_depth"):
        banks[split] = {}
        for mode in ("recurrent", "no_feedback"):
            progress(f"G1D_FEATURE_BANK split={split} mode={mode}")
            banks[split][mode] = collect_trajectories(
                model,
                tokenizer,
                reps[split],
                mode=mode,
                batch_size=int(config["training"]["eval_batch_size"]),
                max_length=int(config["model"]["max_sequence_length"]),
                device=device,
                progress=progress,
            )

    decoded_basis, decoded_basis_summary = decoded_injection_basis(
        model.workspace.output_projection
    )
    progress("G1D_GEOMETRY=START")
    geometry, recurrence = run_geometry(
        banks,
        metadata,
        recurrent_steps=int(config["workspace"]["steps"]),
        decoded_basis=decoded_basis,
        decoded_basis_summary=decoded_basis_summary,
    )
    progress("G1D_PROBES=START")
    probes = run_probes(
        banks,
        metadata,
        states=state_count,
        recurrent_steps=int(config["workspace"]["steps"]),
        seed=int(config["seed"]),
        decoded_basis=decoded_basis,
    )
    progress("G1D_INTERVENTIONS=START")
    intervention_summary, intervention_records = run_interventions(
        model,
        tokenizer,
        splits,
        reps,
        banks,
        target_token_map=token_map,
        config=config,
        progress=progress,
    )
    saved_predictions = [
        json.loads(line)
        for line in (run_root / "predictions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    replay = replay_check(intervention_records, saved_predictions)

    feature_bank = {
        "schema": "komorebi.neuralese.g1d.feature_bank.v1",
        "source_run_config_digest": stored_digest,
        "selection": selection,
        "decoded_injection_analysis_basis": decoded_basis,
        "decoded_injection_analysis_basis_summary": decoded_basis_summary,
        "metadata": metadata,
        "representations": {
            split: {
                mode: {
                    "states_z0_to_z4": banks[split][mode]["states"],
                    "decoded_injections_z0_to_z4": banks[split][mode][
                        "injections"
                    ],
                    "source_activation": banks[split][mode]["source"]
                    if mode == "recurrent"
                    else None,
                    "consumed_feedback_delta_from_initial_norms": banks[split][mode][
                        "consumed_feedback_delta_from_initial_norms"
                    ],
                    "halt_probabilities": banks[split][mode]["halt_probabilities"],
                    "update_diagnostics": banks[split][mode]["update_diagnostics"],
                }
                for mode in ("recurrent", "no_feedback")
            }
            for split in banks
        },
    }

    output_projection = spectrum["matrices"]["output_projection.weight"]
    final_step = int(config["workspace"]["steps"])
    final_probe = probes["final_state"][f"recurrent_z{final_step}"]
    source_probe = probes["final_state"]["source_activation"]
    initial_probe = probes["final_state"]["recurrent_z0"]
    nf_probe = probes["final_state"][f"no_feedback_z{final_step}"]
    decoded_probe = probes["final_state_decoded_injection"][
        f"recurrent_delta{final_step}"
    ]
    feedback_difference_probe = probes["feedback_difference_final_state"][
        f"recurrent_minus_no_feedback_z{final_step}"
    ]
    same_iid = intervention_summary["test_iid"]["same_final_state_donor"]
    wrong_iid = intervention_summary["test_iid"]["incompatible_state_donor"]
    sensitivity_iid = intervention_summary["test_iid"]["sensitivity_to_own_z4"]
    sensitivity_ood = intervention_summary["test_ood_depth"][
        "sensitivity_to_own_z4"
    ]
    transport_iid = intervention_summary["test_iid"][
        "incompatible_donor_semantic_transport"
    ]
    transport_ood = intervention_summary["test_ood_depth"][
        "incompatible_donor_semantic_transport"
    ]
    recurrence_probe_gain = (
        final_probe["ridge"]["iid"]["balanced_accuracy"]
        - nf_probe["ridge"]["iid"]["balanced_accuracy"]
    )

    def strong_iid(probe: dict[str, Any]) -> bool:
        return (
            probe.get("iid_signal_evidence")
            == "STRONG_IID_FINAL_STATE_SIGNAL_ABOVE_METADATA"
        )

    def robust(probe: dict[str, Any]) -> bool:
        return strong_iid(probe) and (
            probe.get("ood_signal_evidence")
            == "OOD_GENERALIZING_FINAL_STATE_SIGNAL_ABOVE_METADATA"
        )

    def probe_view(probe: dict[str, Any]) -> dict[str, Any]:
        return {
            "tier": probe["tier"],
            "iid_signal_evidence": probe["iid_signal_evidence"],
            "ood_signal_evidence": probe["ood_signal_evidence"],
            "iid_balanced_accuracy": probe["ridge"]["iid"]["balanced_accuracy"],
            "ood_balanced_accuracy": probe["ridge"]["ood"]["balanced_accuracy"],
            "iid_lift_over_raw_metadata": probe["iid_lift_over_raw_metadata"],
            "ood_lift_over_raw_metadata": probe["ood_lift_over_raw_metadata"],
            "permutation_p_value": probe["permutation_null"]["p_value"],
        }

    rank1_agreement = sensitivity_iid["rank1_projection_own_z4"][
        "top1_agreement_with_own_z4"
    ]
    residual_agreement = sensitivity_iid["residual_projection_own_z4"][
        "top1_agreement_with_own_z4"
    ]
    same_iid_sensitivity = sensitivity_iid["same_final_state_donor"]
    same_ood_sensitivity = sensitivity_ood["same_final_state_donor"]
    same_state_invariant_iid = bool(
        same_iid_sensitivity["top1_agreement_with_own_z4"] >= 0.99
        and same_iid_sensitivity["mean_family_js_divergence"] <= 0.01
    )
    same_state_invariant_ood = bool(
        same_ood_sensitivity["top1_agreement_with_own_z4"] >= 0.99
        and same_ood_sensitivity["mean_family_js_divergence"] <= 0.01
    )
    positive_transport_iid = float(transport_iid["clustered_99pct"][0]) > 0.0
    positive_transport_ood = float(transport_ood["clustered_99pct"][0]) > 0.0
    projection_collapse = bool(
        spectrum["output_projection_rank_collapse_signature"]
    )
    rank1_dominance = bool(rank1_agreement >= 0.99)
    primary_diagnosis = classify_localization(
        source_robust=robust(source_probe),
        initial_iid=strong_iid(initial_probe),
        initial_robust=robust(initial_probe),
        final_iid=strong_iid(final_probe),
        final_robust=robust(final_probe),
        decoded_iid=strong_iid(decoded_probe),
        projection_collapse=projection_collapse,
        rank1_dominance=rank1_dominance,
        same_state_invariant=same_state_invariant_iid,
        positive_semantic_transport_established=positive_transport_iid,
    )
    final_state_pair = recurrence["test_iid"]["state"][f"z{final_step}"]
    registered_feedback_delta = static_analysis["iid_causal_deltas"][
        "recurrent_minus_no_feedback"
    ]

    verdict = {
        "schema": "komorebi.neuralese.g1d.verdict.v1",
        "claim": "DIAGNOSTIC_ONLY",
        "source_claim": static_analysis["source_run"]["claim"],
        "primary_diagnosis": primary_diagnosis,
        "primary_localization_is_causal_proof": False,
        "generic_steering_behavior": bool(static_analysis["generic_steering_signature"]),
        "output_projection_rank_collapse": projection_collapse,
        "output_projection_top1_energy_fraction": output_projection[
            "top1_energy_fraction"
        ],
        "probe_evidence": {
            "source_activation": probe_view(source_probe),
            "initial_workspace_state": probe_view(initial_probe),
            "final_workspace_state": probe_view(final_probe),
            "final_decoded_injection": probe_view(decoded_probe),
            "final_no_feedback_state": probe_view(nf_probe),
            "final_recurrent_minus_no_feedback_state": probe_view(
                feedback_difference_probe
            ),
        },
        "raw_metadata_baseline": {
            "method_balanced_accuracy": probes[
                "raw_metadata_method_balanced_accuracy"
            ],
            "literal_heuristics": probes["literal_heuristic_baselines"],
        },
        "source_final_state_probe_tier": source_probe["tier"],
        "initial_state_final_state_probe_tier": initial_probe["tier"],
        "final_state_probe_tier": final_probe["tier"],
        "final_state_probe_iid_balanced_accuracy": final_probe["ridge"]["iid"][
            "balanced_accuracy"
        ],
        "no_feedback_probe_iid_balanced_accuracy": nf_probe["ridge"]["iid"][
            "balanced_accuracy"
        ],
        "recurrence_probe_gain": recurrence_probe_gain,
        "same_final_state_donor_receiver_accuracy": same_iid["receiver_accuracy"],
        "incompatible_donor_receiver_accuracy": wrong_iid["receiver_accuracy"],
        "incompatible_donor_target_accuracy": wrong_iid["donor_accuracy"],
        "same_state_donor_invariance": {
            "iid_established_at_declared_thresholds": same_state_invariant_iid,
            "ood_established_at_declared_thresholds": same_state_invariant_ood,
            "top1_agreement_threshold": 0.99,
            "family_js_divergence_threshold": 0.01,
            "iid": same_iid_sensitivity,
            "ood": same_ood_sensitivity,
        },
        "paired_incompatible_donor_semantic_transport": {
            "iid": transport_iid,
            "ood": transport_ood,
            "iid_positive_at_99pct": positive_transport_iid,
            "ood_positive_at_99pct": positive_transport_ood,
        },
        "rank1_projection_top1_agreement_with_full": rank1_agreement,
        "residual_projection_top1_agreement_with_full": residual_agreement,
        "mean_centered_state_top1_agreement_with_full": sensitivity_iid[
            "mean_centered_own_z4"
        ]["top1_agreement_with_own_z4"],
        "feedback_evidence": {
            "trajectory_changed_numerically": bool(
                final_state_pair["maximum_l2_difference"] > 1e-8
            ),
            "final_state_pair_geometry_iid": final_state_pair,
            "feedback_difference_probe": probe_view(feedback_difference_probe),
            "recurrent_minus_no_feedback_probe_iid_balanced_accuracy_gain": recurrence_probe_gain,
            "registered_recurrent_minus_no_feedback_accuracy": registered_feedback_delta,
            "registered_prediction_changed_fraction": 1.0
            - static_analysis["cross_mode_prediction_agreement"]["test_iid"][
                "recurrent__no_feedback"
            ]["agreement"],
        },
        "behavioral_state_use_established": bool(
            positive_transport_iid
            and positive_transport_ood
            and same_state_invariant_iid
            and same_state_invariant_ood
        ),
        "behavioral_feedback_use_established": False,
        "g1_scientific_claim_changed": False,
        "interpretation_boundary": (
            "Probe accuracy establishes only decodability relative to declared controls; "
            "it does not prove iterative computation. Post-hoc interventions can localize "
            "this failed registered pilot but cannot convert it into a G1 pass, establish "
            "replication, or establish general Neuralese."
        ),
    }

    progress("G1D_BACKBONE_HASH_AFTER=START")
    backbone_hash_after = module_state_hash(model.backbone)
    workspace_hash_after = module_state_hash(model.workspace)
    if backbone_hash_after != backbone_hash_before:
        raise RuntimeError("backbone changed during read-only diagnostics")
    if workspace_hash_after != workspace_hash_before:
        raise RuntimeError("workspace changed during read-only diagnostics")
    return {
        "verification": verification,
        "fixed_source_verification": fixed_source_verification,
        "model": {
            "fingerprint": fingerprint,
            "relocated": relocation_warning,
            "identity": observed_identity,
            "resolved_dtype": str(dtype),
            "runtime": observed_environment,
            "backbone_hash_before": backbone_hash_before,
            "backbone_hash_after": backbone_hash_after,
            "workspace_hash_before": workspace_hash_before,
            "workspace_hash_after": workspace_hash_after,
        },
        "spectrum": spectrum,
        "geometry": geometry,
        "recurrence": recurrence,
        "probes": probes,
        "selection": selection,
        "intervention_summary": intervention_summary,
        "intervention_records": intervention_records,
        "replay": replay,
        "feature_bank": feature_bank,
        "verdict": verdict,
    }
