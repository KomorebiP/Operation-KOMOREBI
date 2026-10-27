from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from multispace_core import (
    adjusted_overlap,
    balanced_basis,
    consensus_basis,
    fit_whitening,
    gram_from_samples,
    overlap,
    overlap_against_null,
    pairwise_overlap_matrix,
    pca_basis,
    persistent_basis,
    predictive_basis,
    principal_angles_degrees,
    random_overlap_null,
    top_eigenbasis,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Frozen Qwen multi-space engineering smoke")
    parser.add_argument("--model", required=True, help="Local Hugging Face model directory")
    parser.add_argument("--lens", required=True, help="Local JacobianLens .pt file")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    parser.add_argument("--rank", type=int, default=8)
    parser.add_argument("--positions-per-prompt", type=int, default=8)
    parser.add_argument("--future-horizon", type=int, default=2)
    parser.add_argument("--read-horizon", type=int, default=2)
    parser.add_argument("--active-topk", type=int, default=8)
    parser.add_argument("--null-replicates", type=int, default=64)
    parser.add_argument("--seed", type=int, default=610001)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def seed_everything(seed: int, torch: Any) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch, "use_deterministic_algorithms"):
        torch.use_deterministic_algorithms(True, warn_only=True)


def find_decoder_layers(hf: Any) -> Any:
    candidates = [
        getattr(hf, "model", None),
        getattr(getattr(hf, "model", None), "model", None),
        getattr(hf, "transformer", None),
    ]
    for candidate in candidates:
        if candidate is not None and hasattr(candidate, "layers"):
            return candidate.layers
        if candidate is not None and hasattr(candidate, "h"):
            return candidate.h
    raise RuntimeError("Could not locate decoder block list")


def structural_read_gram(
    decoder_layers: Any,
    source_layer: int,
    horizon: int,
    d_model: int,
    torch: Any,
) -> tuple[np.ndarray, list[str]]:
    end = min(len(decoder_layers), source_layer + 1 + horizon)
    gram = torch.zeros((d_model, d_model), dtype=torch.float64, device="cpu")
    included: list[str] = []
    preferred = ("q_proj.weight", "k_proj.weight", "v_proj.weight", "gate_proj.weight", "up_proj.weight")
    for layer_index in range(source_layer + 1, end):
        block = decoder_layers[layer_index]
        candidates = []
        fallback = []
        for name, parameter in block.named_parameters(recurse=True):
            if parameter.ndim == 2 and parameter.shape[1] == d_model:
                fallback.append((name, parameter))
                if any(name.endswith(suffix) for suffix in preferred):
                    candidates.append((name, parameter))
        if not candidates:
            candidates = fallback
        for name, parameter in candidates:
            weight = parameter.detach().float()
            local = weight.T @ weight
            trace = float(torch.trace(local).item())
            if trace <= 0 or not np.isfinite(trace):
                continue
            gram += (local / trace).double().cpu()
            included.append(f"L{layer_index}:{name}")
            del local, weight
    if not included:
        raise RuntimeError(f"No downstream read matrices found after layer {source_layer}")
    return gram.numpy(), included


def transport_orientation(lens: Any, layer: int, d_model: int, device: str, torch: Any) -> str:
    generator = torch.Generator(device=device)
    generator.manual_seed(910000 + int(layer))
    probe = torch.randn(d_model, generator=generator, device=device, dtype=torch.float32)
    matrix = lens.jacobians[layer].float()
    target = lens.transport(probe, layer).float()
    column_error = float(torch.linalg.vector_norm(matrix @ probe - target).item())
    row_error = float(torch.linalg.vector_norm(probe @ matrix - target).item())
    scale = max(float(torch.linalg.vector_norm(target).item()), 1e-12)
    if min(column_error, row_error) / scale > 1e-4:
        raise RuntimeError(
            f"Could not identify lens matrix orientation at layer {layer}: "
            f"column={column_error / scale:.3e}, row={row_error / scale:.3e}"
        )
    return "column" if column_error <= row_error else "row"


def source_verbal_covectors(
    lens: Any,
    layer: int,
    token_ids: list[int],
    unembedding_weight: Any,
    orientation: str,
    torch: Any,
) -> np.ndarray:
    if not token_ids:
        raise RuntimeError(f"No active lens tokens collected for layer {layer}")
    ids = torch.tensor(token_ids, device=unembedding_weight.device, dtype=torch.long)
    target_rows = unembedding_weight.index_select(0, ids).detach().float()
    matrix = lens.jacobians[layer].float()
    if orientation == "column":
        source_rows = target_rows @ matrix
    else:
        source_rows = target_rows @ matrix.T
    return source_rows.cpu().numpy()


def fit_independent_spaces(
    current: np.ndarray,
    future: np.ndarray,
    future_update: np.ndarray,
    incoming: np.ndarray,
    read_gram_white: np.ndarray,
    rank: int,
) -> dict[str, np.ndarray]:
    p, _ = predictive_basis(current, future_update, rank)
    t, _ = persistent_basis(current, future, rank)
    c, _ = pca_basis(incoming, rank)
    o, _ = top_eigenbasis(read_gram_white, rank)
    write_gram = gram_from_samples(incoming)
    b, _ = balanced_basis(write_gram, read_gram_white, rank)
    dynamics, _ = consensus_basis([p, t], rank)
    w, _ = consensus_basis([dynamics, b], rank)
    return {"P": p, "T": t, "C": c, "O": o, "B": b, "D": dynamics, "W": w}


def stable_rank(requested: int, sample_count: int, d_model: int) -> int:
    return max(1, min(int(requested), int(sample_count) - 2, int(d_model)))


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def main() -> int:
    args = parse_args()
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    import torch
    import transformers
    import jlens

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    device = args.device
    dtype = torch.float16 if device == "cuda" else torch.float32
    seed_everything(args.seed, torch)

    model_path = Path(args.model).resolve()
    lens_path = Path(args.lens).resolve()
    output = Path(args.output).resolve()
    if not model_path.is_dir():
        raise FileNotFoundError(f"Model directory not found: {model_path}")
    if not lens_path.is_file():
        raise FileNotFoundError(f"Lens file not found: {lens_path}")
    output.mkdir(parents=True, exist_ok=True)

    prompt_data = json.loads((ROOT / "data" / "smoke_prompts.json").read_text(encoding="utf-8"))
    prompts = prompt_data["prompts"]

    started = time.perf_counter()
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    hf = transformers.AutoModelForCausalLM.from_pretrained(
        model_path, local_files_only=True, dtype=dtype
    ).eval().to(device)
    jmodel = jlens.from_hf(hf, tokenizer)
    lens = jlens.JacobianLens.load(str(lens_path))
    source_layers = sorted(int(layer) for layer in lens.source_layers)
    d_model = int(hf.config.hidden_size)
    n_layers = int(hf.config.num_hidden_layers)
    if int(lens.d_model) != d_model:
        raise RuntimeError(f"Lens d_model={lens.d_model} does not match model d_model={d_model}")
    if any(layer < 0 or layer >= n_layers for layer in source_layers):
        raise RuntimeError("Lens contains a source layer outside the model")
    lens.jacobians = {int(layer): matrix.to(device) for layer, matrix in lens.jacobians.items()}
    unembedding_weight = hf.get_output_embeddings().weight
    decoder_layers = find_decoder_layers(hf)

    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()

    trace: dict[int, dict[str, list[np.ndarray] | list[int]]] = {
        layer: {"current": [], "future": [], "future_update": [], "incoming": [], "token_ids": []}
        for layer in source_layers
    }
    readout_records: list[dict[str, Any]] = []

    with torch.no_grad():
        for prompt_index, prompt in enumerate(prompts):
            encoded = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=64,
            ).to(device)
            result = hf(**encoded, output_hidden_states=True, use_cache=False)
            hidden = result.hidden_states
            sequence_length = int(encoded["input_ids"].shape[1])
            start = max(0, sequence_length - int(args.positions_per_prompt))
            positions = list(range(start, sequence_length))
            if not positions:
                positions = [sequence_length - 1]

            for layer in source_layers:
                current_index = layer + 1
                future_index = min(n_layers, current_index + int(args.future_horizon))
                previous_index = max(0, current_index - 1)
                current_tensor = hidden[current_index][0, positions].float()
                future_tensor = hidden[future_index][0, positions].float()
                incoming_tensor = current_tensor - hidden[previous_index][0, positions].float()
                update_tensor = future_tensor - current_tensor
                trace[layer]["current"].append(current_tensor.cpu().numpy())
                trace[layer]["future"].append(future_tensor.cpu().numpy())
                trace[layer]["future_update"].append(update_tensor.cpu().numpy())
                trace[layer]["incoming"].append(incoming_tensor.cpu().numpy())

                transported = lens.transport(current_tensor, layer)
                logits = jmodel.unembed(transported).float()
                active_ids = logits.topk(int(args.active_topk), dim=-1).indices.flatten().tolist()
                trace[layer]["token_ids"].extend(int(token_id) for token_id in active_ids)

                final_logits = logits[-1]
                log_probabilities = torch.log_softmax(final_logits, dim=-1)
                top = log_probabilities.topk(int(args.active_topk))
                readout_records.append({
                    "prompt_index": prompt_index,
                    "phase": "reading_prefill",
                    "position": sequence_length - 1,
                    "source_layer": layer,
                    "prediction_horizon": "current_and_future_disposition",
                    "tokens": [
                        {
                            "token_id": int(token_id),
                            "text": tokenizer.decode([int(token_id)]),
                            "log_probability": float(log_probability),
                        }
                        for log_probability, token_id in zip(top.values.tolist(), top.indices.tolist())
                    ],
                })
            del result, hidden

    layer_results: dict[str, Any] = {}
    overlap_rows: list[dict[str, Any]] = []
    best_layer = None
    best_excess = -float("inf")

    for layer in source_layers:
        current_raw = np.concatenate(trace[layer]["current"], axis=0)
        future_raw = np.concatenate(trace[layer]["future"], axis=0)
        update_raw = np.concatenate(trace[layer]["future_update"], axis=0)
        incoming_raw = np.concatenate(trace[layer]["incoming"], axis=0)
        rank = stable_rank(args.rank, current_raw.shape[0], d_model)
        whitening = fit_whitening(current_raw)
        current = whitening.states(current_raw)
        future = (future_raw - future_raw.mean(axis=0, keepdims=True)) @ whitening.to_white.T
        future_update = whitening.deltas(update_raw)
        incoming = whitening.deltas(incoming_raw)

        read_gram_raw, read_sources = structural_read_gram(
            decoder_layers, layer, args.read_horizon, d_model, torch
        )
        read_gram_white = whitening.from_white @ read_gram_raw @ whitening.from_white.T

        spaces = fit_independent_spaces(
            current, future, future_update, incoming, read_gram_white, rank
        )
        orientation = transport_orientation(lens, layer, d_model, device, torch)
        verbal_raw = source_verbal_covectors(
            lens,
            layer,
            list(trace[layer]["token_ids"]),
            unembedding_weight,
            orientation,
            torch,
        )
        verbal_white = whitening.covectors(verbal_raw)
        verbal, verbal_spectrum = pca_basis(verbal_white, rank, center_samples=False)
        spaces["V"] = verbal

        independent_reference = spaces["B"]
        rng = np.random.default_rng(args.seed + layer)
        shuffled_update = future_update[rng.permutation(future_update.shape[0])]
        shuffled_predictive, _ = predictive_basis(current, shuffled_update, rank)
        predictive_real = overlap(spaces["P"], independent_reference)
        predictive_shuffled = overlap(shuffled_predictive, independent_reference)

        half_a = np.arange(current.shape[0]) % 2 == 0
        half_b = ~half_a
        spaces_a = fit_independent_spaces(
            current[half_a], future[half_a], future_update[half_a], incoming[half_a], read_gram_white, rank
        )
        spaces_b = fit_independent_spaces(
            current[half_b], future[half_b], future_update[half_b], incoming[half_b], read_gram_white, rank
        )
        split_half = overlap(spaces_a["W"], spaces_b["W"])

        verbal_consensus = overlap(verbal, spaces["W"])
        random_null = random_overlap_null(
            spaces["W"], verbal.shape[1], args.null_replicates, args.seed + 1000 + layer
        )
        null_test = overlap_against_null(verbal_consensus, random_null)
        excess = verbal_consensus - float(random_null["mean"])
        if excess > best_excess:
            best_excess = excess
            best_layer = layer

        names, matrix = pairwise_overlap_matrix(spaces)
        for i, left in enumerate(names):
            for j, right in enumerate(names):
                overlap_rows.append({
                    "layer": layer,
                    "left": left,
                    "right": right,
                    "overlap": float(matrix[i, j]),
                })

        layer_results[str(layer)] = {
            "rank": rank,
            "samples": int(current.shape[0]),
            "lens_orientation": orientation,
            "read_weight_sources": read_sources,
            "whitening_ridge": whitening.ridge,
            "verbal_spectrum": verbal_spectrum[:rank].tolist(),
            "verbal_consensus_overlap": verbal_consensus,
            "verbal_consensus_adjusted_overlap": adjusted_overlap(verbal, spaces["W"]),
            "verbal_consensus_principal_angles_degrees": principal_angles_degrees(verbal, spaces["W"]),
            "verbal_consensus_random_null": {k: v for k, v in null_test.items()},
            "split_half_consensus_overlap": split_half,
            "predictive_independent_overlap": predictive_real,
            "shuffled_predictive_independent_overlap": predictive_shuffled,
            "pairwise_names": names,
            "pairwise_overlap": matrix.tolist(),
            "primary_claim_evaluated": False,
        }

    peak_vram = (
        float(torch.cuda.max_memory_allocated() / 1073741824)
        if device == "cuda"
        else 0.0
    )
    result_document = {
        "status": "PASS",
        "profile": "engineering_smoke",
        "scientific_interpretation_forbidden": True,
        "primary_claim_evaluated": False,
        "model": {
            "path": str(model_path),
            "class": hf.__class__.__name__,
            "layers": n_layers,
            "hidden_size": d_model,
            "config_commit": getattr(hf.config, "_commit_hash", None),
        },
        "lens": {
            "path": str(lens_path),
            "sha256": sha256_file(lens_path),
            "n_prompts": int(lens.n_prompts),
            "source_layers": source_layers,
            "d_model": int(lens.d_model),
            "full_sparse_cone_constructed": False,
            "smoke_proxy": "active_verbal_frame",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "jlens": getattr(jlens, "__version__", None),
            "device": device,
            "peak_vram_gb": peak_vram,
        },
        "prompts": len(prompts),
        "rank_requested": args.rank,
        "independent_estimator_families_in_smoke": 2,
        "primary_convergence_gate_requires_families": 3,
        "best_descriptive_layer": best_layer,
        "best_verbal_consensus_excess_over_random_mean": best_excess,
        "layers": layer_results,
        "elapsed_seconds": time.perf_counter() - started,
    }

    results_path = output / "multispace_results.json"
    results_path.write_text(
        json.dumps(json_safe(result_document), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    readouts_path = output / "subtext_like_readouts.json"
    readouts_path.write_text(
        json.dumps(json_safe({
            "warning": "Qualitative smoke readouts. Frames are prefill states, not generated-token causes.",
            "records": readout_records,
        }), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    csv_path = output / "overlap_matrix.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["layer", "left", "right", "overlap"])
        writer.writeheader()
        writer.writerows(overlap_rows)

    print("V061_QWEN_MULTISPACE_SMOKE=PASS")
    print(f"MODEL_CLASS={hf.__class__.__name__}")
    print(f"PROMPTS={len(prompts)}")
    print("SOURCE_LAYERS=" + ",".join(str(layer) for layer in source_layers))
    print(f"BEST_DESCRIPTIVE_LAYER={best_layer}")
    print(f"BEST_V_W_EXCESS={best_excess:.6f}")
    print(f"PEAK_VRAM_GB={peak_vram:.2f}")
    print(f"ELAPSED_SECONDS={time.perf_counter() - started:.2f}")
    print(f"RESULTS={results_path}")
    print("SCIENTIFIC_INTERPRETATION=FORBIDDEN")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"V061_QWEN_MULTISPACE_SMOKE=FAIL: {exc}", file=sys.stderr)
        raise
