#!/usr/bin/env python
"""Capture raw Huginn recurrent states through the model's public step API.

The default is offline-only. Add ``--allow-download`` explicitly if the pinned
snapshot is not already cached. Remote model code is pinned because loading it
executes repository Python.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import inspect
import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np


MODEL_ID = "tomg-group-umd/huginn-0125"
MODEL_REVISION = "bb6621b65e90b6a4b9b29ef88dc83866d450470c"
RECOMMENDED_TRANSFORMERS = "4.57.6"
ROOT = Path(__file__).resolve().parents[1]


def _dtype(torch, name: str):
    values = {
        "auto": "auto",
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    return values[name]


def _load_prompt(args: argparse.Namespace) -> tuple[str, str, dict[str, Any] | None]:
    if args.prompt is not None:
        return "custom", args.prompt, None
    config_path = Path(args.prompt_config)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    rows = payload["prompts"]
    if args.prompt_id is None:
        row = rows[0]
    else:
        matches = [item for item in rows if item["id"] == args.prompt_id]
        if not matches:
            available = ", ".join(item["id"] for item in rows)
            raise ValueError(f"unknown prompt id {args.prompt_id!r}; choose from: {available}")
        row = matches[0]
    return row["id"], row["text"], {"suite": payload, "row": row}


def _parse_steps(raw: str, maximum: int) -> list[int]:
    requested = {int(value) for value in raw.split(",") if value.strip()}
    if any(value < 0 for value in requested):
        raise ValueError("logit steps must be nonnegative")
    values = sorted(value for value in requested if value <= maximum)
    if maximum not in values:
        values.append(maximum)
    return values


def _resolve_key_spans(formatted_prompt: str, offsets, key_spans: list[str]) -> dict[str, list[int]]:
    """Resolve first text occurrence of each configured span to token indices."""

    if offsets is None:
        return {}
    offset_rows = offsets[0].detach().cpu().numpy()
    resolved: dict[str, list[int]] = {}
    for span in key_spans:
        start = formatted_prompt.find(span)
        if start < 0:
            resolved[span] = []
            continue
        end = start + len(span)
        indices = [
            index
            for index, (token_start, token_end) in enumerate(offset_rows)
            if token_end > token_start and token_start < end and token_end > start
        ]
        resolved[span] = indices
    return resolved


def _normalizer(model):
    transformer = getattr(model, "transformer", None)
    layer = getattr(transformer, "ln_f", None)
    if layer is None:
        raise RuntimeError("pinned model does not expose model.transformer.ln_f")
    return layer


def _embed(model, input_ids):
    result = model.embed_inputs(input_ids, use_cache=False)
    if not isinstance(result, tuple) or len(result) != 2:
        raise RuntimeError(
            "embed_inputs API mismatch: pinned snapshot should return (input_embeds, block_idx)"
        )
    return result


def _step(model, embedded, state, block_idx, current_step: int):
    result = model.iterate_one_step(
        embedded,
        state,
        block_idx=block_idx,
        current_step=current_step,
        past_key_values=None,
    )
    if not isinstance(result, tuple) or len(result) != 3:
        raise RuntimeError("iterate_one_step API mismatch: expected three return values")
    return result


def _manual_states(model, embedded, initial_state, block_idx, depths: list[int]):
    wanted = set(depths)
    maximum = max(depths, default=0)
    state = initial_state.clone()
    current_block = block_idx
    output = {}
    for step in range(maximum + 1):
        if step in wanted:
            output[step] = state.detach().clone()
        if step < maximum:
            state, current_block, _ = _step(model, embedded, state, current_block, step)
    return output


def _forward_equivalence(model, input_ids, embedded, initial_state, block_idx, depths):
    """Compare manual iteration to ordinary forward on the same initial state."""

    normalizer = _normalizer(model)
    manual = _manual_states(model, embedded, initial_state, block_idx, depths)
    rows = []
    for depth in depths:
        kwargs = {
            "input_ids": input_ids,
            "input_states": initial_state.clone(),
            "num_steps": depth,
            "use_cache": False,
            "output_details": {
                "return_logits": True,
                "return_latents": True,
                "return_head": False,
                "return_stats": False,
            },
        }
        accepted = inspect.signature(model.forward).parameters
        kwargs = {key: value for key, value in kwargs.items() if key in accepted}
        result = model(**kwargs)
        latent = getattr(result, "latent_states", None)
        if latent is None:
            raise RuntimeError("ordinary forward did not return latent_states")
        expected = normalizer(manual[depth])
        latent_difference = latent.float() - expected.float()
        latent_denominator = max(float(expected.float().norm().item()), np.finfo(float).eps)
        manual_logits = model.predict_from_latents(manual[depth]).logits.float()
        forward_logits = result.logits.float()
        logit_difference = manual_logits - forward_logits
        logit_denominator = max(float(forward_logits.norm().item()), np.finfo(float).eps)
        rows.append(
            {
                "depth": depth,
                "latent_relative_error": float(latent_difference.norm().item()) / latent_denominator,
                "latent_max_absolute_error": float(latent_difference.abs().max().item()),
                "logit_relative_error": float(logit_difference.norm().item()) / logit_denominator,
                "logit_max_absolute_error": float(logit_difference.abs().max().item()),
            }
        )
    return rows


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _require_huginn_transformers_4(version: str) -> None:
    """Reject Transformers 5 before remote code or checkpoint loading begins.

    The pinned Huginn snapshot declares ``_tied_weights_keys`` using the
    Transformers 4.x list contract. Transformers 5 expects a target-to-source
    mapping and otherwise fails in ``post_init`` before loading the weights.
    """

    match = re.match(r"\s*(\d+)\.", version)
    if match is not None and int(match.group(1)) == 4:
        return
    raise RuntimeError(
        f"Huginn's pinned remote code requires Transformers 4.x; found {version!r}. "
        f"Install the tested release with: python -m pip install "
        f"\"transformers=={RECOMMENDED_TRANSFORMERS}\". The cached Huginn checkpoint "
        "will be reused; do not add --allow-download when retrying."
    )


def _nvidia_driver_version() -> str | None:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    values = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return values[0] if values else None


def capture(args: argparse.Namespace) -> tuple[Path, Path]:
    try:
        import torch
        import transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError("install the 'huginn' optional dependencies first") from exc

    _require_huginn_transformers_4(transformers.__version__)

    prompt_id, raw_prompt, prompt_record = _load_prompt(args)
    logit_steps = _parse_steps(args.logit_steps, args.steps)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
        torch.cuda.reset_peak_memory_stats()

    load_kwargs: dict[str, Any] = {
        "revision": args.revision,
        "trust_remote_code": True,
        "local_files_only": not args.allow_download,
    }
    quantization_compute_dtype = None
    if args.quantization != "none":
        try:
            from transformers import BitsAndBytesConfig
        except ImportError as exc:
            raise RuntimeError("quantized loading requires bitsandbytes support") from exc
        quantization_compute_dtype = (
            torch.bfloat16
            if torch.cuda.is_available() and torch.cuda.is_bf16_supported()
            else torch.float16
        )
        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=args.quantization == "4bit",
            load_in_8bit=args.quantization == "8bit",
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=quantization_compute_dtype,
        )
    else:
        load_kwargs["torch_dtype"] = _dtype(torch, args.dtype)
    if args.device_map != "none":
        load_kwargs["device_map"] = args.device_map

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, **{
        key: load_kwargs[key]
        for key in ("revision", "trust_remote_code", "local_files_only")
    })
    model = AutoModelForCausalLM.from_pretrained(args.model_id, **load_kwargs)
    model.eval()
    resolved_revision = getattr(model.config, "_commit_hash", None)
    if not args.allow_unverified_revision and resolved_revision != args.revision:
        raise RuntimeError(
            f"resolved revision {resolved_revision!r} does not match requested {args.revision!r}"
        )
    if not hasattr(model.config, "test_time_noise"):
        raise RuntimeError("pinned model config does not expose test_time_noise")
    model.config.test_time_noise = 0

    prompt = raw_prompt
    templated_prompt = False
    if prompt_record is not None:
        format_config = prompt_record["suite"].get("format", {})
        if format_config.get("use_chat_template", False):
            templated_prompt = True
            messages = []
            system_message = format_config.get("system_message")
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": raw_prompt})
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=bool(format_config.get("add_generation_prompt", True)),
            )
    tokenized = tokenizer(
        prompt,
        return_tensors="pt",
        padding=False,
        add_special_tokens=not templated_prompt,
        return_offsets_mapping=getattr(tokenizer, "is_fast", False),
    )
    offsets = tokenized.pop("offset_mapping", None)
    input_ids = tokenized["input_ids"]
    candidate_label_ids: dict[str, int] = {}
    target_label = None
    if prompt_record is not None and prompt_record["row"].get("mode") == "scored":
        candidate_labels = prompt_record["suite"].get("format", {}).get(
            "candidate_labels", []
        )
        base_ids = input_ids[0].tolist()
        for label in candidate_labels:
            extended_ids = tokenizer(
                prompt + label,
                add_special_tokens=False,
            )["input_ids"]
            if extended_ids[: len(base_ids)] != base_ids:
                raise RuntimeError(
                    f"tokenization prefix changed while resolving answer label {label!r}"
                )
            suffix = extended_ids[len(base_ids) :]
            if len(suffix) != 1:
                raise RuntimeError(
                    f"answer label {label!r} is not one token in the formatted context: {suffix}"
                )
            candidate_label_ids[label] = int(suffix[0])
        target_label = prompt_record["row"].get("target_label")
        if len(set(candidate_label_ids.values())) != len(candidate_label_ids):
            raise RuntimeError("candidate answer labels do not resolve to distinct token IDs")
        if target_label not in candidate_label_ids:
            raise RuntimeError(f"target label {target_label!r} is not in the candidate label set")
    try:
        model_device = model.get_input_embeddings().weight.device
        input_ids = input_ids.to(model_device)
    except (StopIteration, ValueError):
        pass

    with torch.inference_mode():
        embedded, block_idx = _embed(model, input_ids)
        torch.manual_seed(args.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(args.seed)
        initial_state = model.initialize_state(embedded, scale=args.initial_scale)
        if args.skip_forward_check:
            equivalence = []
        else:
            check_depths = [depth for depth in (1, 2, 4) if depth <= args.steps]
            equivalence = _forward_equivalence(
                model, input_ids, embedded, initial_state, block_idx, check_depths
            )
            if any(
                max(row["latent_relative_error"], row["logit_relative_error"])
                > args.forward_tolerance
                for row in equivalence
            ):
                raise RuntimeError(f"manual/forward equivalence failed: {equivalence}")

        sequence_length = input_ids.shape[1]
        key_span_positions = _resolve_key_spans(
            prompt,
            offsets,
            [] if prompt_record is None else prompt_record["row"].get("key_spans", []),
        )
        automatic_positions = sorted(
            {sequence_length - 1}
            | {position for rows in key_span_positions.values() for position in rows}
        )
        raw_positions = args.token_position or automatic_positions
        positions = [position if position >= 0 else sequence_length + position for position in raw_positions]
        if any(position < 0 or position >= sequence_length for position in positions):
            raise ValueError(f"token position outside sequence of length {sequence_length}")

        normalizer = _normalizer(model)
        storage_dtype = {
            "float16": torch.float16,
            "float32": torch.float32,
        }[args.storage_dtype]
        raw_states = []
        normalized_states = []
        sketches = []
        top_ids = []
        top_values = []
        full_logits = []
        candidate_logits = []
        recorded_logit_steps = []
        sketch_projection = None

        started = time.perf_counter()
        state = initial_state
        current_block = block_idx
        for step in range(args.steps + 1):
            normalized = normalizer(state)
            raw_states.append(state[0, positions].detach().cpu().to(storage_dtype).numpy())
            normalized_states.append(
                normalized[0, positions].detach().cpu().to(storage_dtype).numpy()
            )
            if args.sketch_dim > 0 and sketch_projection is None:
                generator = torch.Generator(device=normalized.device)
                generator.manual_seed(args.seed + 982451653)
                sketch_projection = torch.randn(
                    initial_state.shape[-1],
                    args.sketch_dim,
                    device=normalized.device,
                    dtype=torch.float32,
                    generator=generator,
                ) / np.sqrt(args.sketch_dim)
            if sketch_projection is not None:
                if sketch_projection.device != normalized.device:
                    sketch_projection = sketch_projection.to(normalized.device)
                sketch = normalized[0].float() @ sketch_projection
                sketches.append(sketch.detach().cpu().to(storage_dtype).numpy())
            if step in logit_steps:
                decoded = model.predict_from_latents(state)
                logits = decoded.logits[0, -1].float()
                if args.save_full_logits:
                    full_logits.append(logits.detach().cpu().to(storage_dtype).numpy())
                count = min(args.top_k, logits.numel())
                values, ids = torch.topk(logits, count)
                top_ids.append(ids.detach().cpu().numpy())
                top_values.append(values.detach().cpu().to(storage_dtype).numpy())
                if candidate_label_ids:
                    ordered_candidate_ids = [candidate_label_ids[label] for label in candidate_label_ids]
                    candidate_index = torch.as_tensor(ordered_candidate_ids, device=logits.device)
                    candidate_logits.append(
                        logits.index_select(0, candidate_index)
                        .detach()
                        .cpu()
                        .to(storage_dtype)
                        .numpy()
                    )
                recorded_logit_steps.append(step)
                del decoded
            if step < args.steps:
                state, current_block, _ = _step(
                    model, embedded, state, current_block, step
                )
        elapsed = time.perf_counter() - started

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_prompt_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", prompt_id).strip("._") or "prompt"
    stem = f"{safe_prompt_id}_seed{args.seed}_depth{args.steps}"
    data_path = output_dir / f"{stem}.npz"
    manifest_path = output_dir / f"{stem}.manifest.json"
    if not args.overwrite and (data_path.exists() or manifest_path.exists()):
        raise FileExistsError(
            f"capture already exists for this prompt/seed/depth: {data_path}; use --overwrite"
        )
    np.savez_compressed(
        data_path,
        raw_states=np.asarray(raw_states),
        normalized_states=np.asarray(normalized_states),
        all_token_sketch=np.asarray(sketches),
        selected_positions=np.asarray(positions, dtype=np.int64),
        input_ids=input_ids.detach().cpu().numpy(),
        offsets=(
            offsets.detach().cpu().numpy()
            if offsets is not None
            else np.empty((0, 2), dtype=np.int64)
        ),
        logit_steps=np.asarray(recorded_logit_steps, dtype=np.int64),
        top_token_ids=np.asarray(top_ids, dtype=np.int64),
        top_logits=np.asarray(top_values),
        full_logits=np.asarray(full_logits),
        candidate_labels=np.asarray(list(candidate_label_ids)),
        candidate_token_ids=np.asarray(list(candidate_label_ids.values()), dtype=np.int64),
        candidate_logits=np.asarray(candidate_logits),
    )
    peak_vram = (
        int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else None
    )
    peak_reserved_vram = (
        int(torch.cuda.max_memory_reserved()) if torch.cuda.is_available() else None
    )
    suite_hash = None
    if args.prompt is None:
        suite_bytes = Path(args.prompt_config).read_bytes()
        suite_hash = hashlib.sha256(suite_bytes).hexdigest()
    manifest = {
        "schema_version": "1.0",
        "model_id": args.model_id,
        "revision": args.revision,
        "resolved_revision": resolved_revision,
        "trust_remote_code": True,
        "offline_only": not args.allow_download,
        "prompt_id": prompt_id,
        "raw_prompt": raw_prompt,
        "formatted_prompt": prompt,
        "formatted_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "seed": args.seed,
        "initial_scale": args.initial_scale,
        "steps": args.steps,
        "test_time_noise": getattr(model.config, "test_time_noise", None),
        "selected_positions": positions,
        "key_span_positions": key_span_positions,
        "prompt_split": None if prompt_record is None else prompt_record["row"].get("split"),
        "prompt_family": None if prompt_record is None else prompt_record["row"].get("family"),
        "candidate_label_token_ids": candidate_label_ids,
        "target_label": target_label,
        "target_token_id": candidate_label_ids.get(target_label) if target_label else None,
        "prompt_suite_sha256": suite_hash,
        "dtype": args.dtype,
        "actual_recurrent_state_dtype": str(initial_state.dtype),
        "storage_dtype": args.storage_dtype,
        "quantization": args.quantization,
        "quantization_compute_dtype": (
            str(quantization_compute_dtype) if quantization_compute_dtype is not None else None
        ),
        "device_map_requested": args.device_map,
        "device_map_actual": getattr(model, "hf_device_map", None),
        "manual_forward_equivalence": equivalence,
        "forward_tolerance": args.forward_tolerance,
        "elapsed_seconds": elapsed,
        "peak_cuda_memory_bytes": peak_vram,
        "peak_cuda_reserved_bytes": peak_reserved_vram,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "accelerate": _package_version("accelerate"),
            "bitsandbytes": _package_version("bitsandbytes"),
            "cuda": torch.version.cuda,
            "nvidia_driver": _nvidia_driver_version(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "gpu_total_memory_bytes": (
                int(torch.cuda.get_device_properties(0).total_memory)
                if torch.cuda.is_available()
                else None
            ),
            "bf16_supported": torch.cuda.is_bf16_supported() if torch.cuda.is_available() else None,
        },
        "data_file": data_path.name,
        "notes": [
            "raw_states are recurrent states and may be fed back",
            "normalized_states are post-ln_f analysis states and must not be fed back",
            "quantized captures describe the quantized model",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    return data_path, manifest_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", default=MODEL_ID)
    parser.add_argument("--revision", default=MODEL_REVISION)
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-config", default=str(ROOT / "configs" / "prompt_suite.json"))
    parser.add_argument("--prompt-id")
    parser.add_argument("--steps", type=int, default=32)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--initial-scale", type=float, default=1.0)
    parser.add_argument("--token-position", type=int, action="append")
    parser.add_argument("--logit-steps", default="0,1,2,4,8,16,32")
    parser.add_argument("--top-k", type=int, default=64)
    parser.add_argument("--save-full-logits", action="store_true")
    parser.add_argument("--sketch-dim", type=int, default=0)
    parser.add_argument("--storage-dtype", choices=["float32", "float16"], default="float32")
    parser.add_argument("--dtype", choices=["auto", "bfloat16", "float16", "float32"], default="auto")
    parser.add_argument("--quantization", choices=["none", "4bit", "8bit"], default="none")
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--allow-unverified-revision", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-forward-check", action="store_true")
    parser.add_argument("--forward-tolerance", type=float, default=5e-4)
    parser.add_argument("--output-dir", default=str(ROOT / "outputs" / "huginn"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.steps < 1 or args.top_k < 1 or args.sketch_dim < 0:
        raise ValueError("steps/top-k must be positive and sketch-dim nonnegative")
    data_path, manifest_path = capture(args)
    print(f"Trajectory: {data_path.resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
