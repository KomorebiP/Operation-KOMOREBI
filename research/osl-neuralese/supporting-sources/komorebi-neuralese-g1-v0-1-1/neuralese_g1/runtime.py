from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
import os
import platform
import random
from pathlib import Path
import tempfile
from typing import Any, Iterable, Sequence

import numpy as np

try:
    import torch
    import torch.nn.functional as F
except ImportError as error:  # pragma: no cover - handled by preflight
    raise ImportError("PyTorch is required for the G1 runtime") from error

from .model import FrozenRecurrentCausalLM, gradient_norm
from .tasks import QueryExample, find_query_derangement
from .token_contract import target_token_id


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
    if hasattr(torch, "use_deterministic_algorithms"):
        torch.use_deterministic_algorithms(True)


def resolve_dtype(name: str, device: str) -> "torch.dtype":
    mapping = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    dtype = mapping[name]
    if device == "cpu" and dtype == torch.float16:
        return torch.float32
    if dtype == torch.bfloat16 and device == "cuda" and not torch.cuda.is_bf16_supported():
        raise RuntimeError("bfloat16 requested but unsupported by this CUDA device")
    return dtype


def file_inventory_fingerprint(model_path: str | Path) -> dict[str, Any]:
    root = Path(model_path).resolve()
    names = (
        "config.json",
        "generation_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "tokenizer.model",
        "vocab.json",
        "merges.txt",
        "added_tokens.json",
        "chat_template.jinja",
        "model.safetensors.index.json",
        "pytorch_model.bin.index.json",
    )
    files: list[dict[str, Any]] = []
    for name in names:
        path = root / name
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            files.append({"name": name, "size": path.stat().st_size, "sha256": digest})
    weight_paths = sorted(root.glob("*.safetensors")) + sorted(root.glob("*.bin"))
    if not weight_paths:
        raise FileNotFoundError(f"no local model weight file found in {root}")
    for path in weight_paths:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                digest.update(block)
        files.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
        )
    if not any(item["name"] == "config.json" for item in files):
        raise FileNotFoundError(f"model config missing from {root}")
    payload = json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "path": str(root),
        "files": files,
        "metadata_sha256": hashlib.sha256(payload).hexdigest(),
    }


def module_state_hash(module: "torch.nn.Module") -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(module.state_dict().items()):
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(tensor.shape)).encode("ascii"))
        digest.update(str(tensor.dtype).encode("ascii"))
        value = tensor.detach().cpu().contiguous()
        if value.dtype == torch.bfloat16:
            value = value.view(torch.uint16)
        digest.update(value.numpy().tobytes(order="C"))
    return digest.hexdigest()


def module_all_finite(module: "torch.nn.Module") -> bool:
    return all(
        bool(torch.isfinite(tensor.detach()).all().item())
        for tensor in module.state_dict().values()
    )


def capture_rng_state() -> dict[str, Any]:
    numpy_state = np.random.get_state()
    return {
        "python": random.getstate(),
        "numpy": {
            "bit_generator": numpy_state[0],
            "keys": numpy_state[1].tolist(),
            "position": int(numpy_state[2]),
            "has_gaussian": int(numpy_state[3]),
            "cached_gaussian": float(numpy_state[4]),
        },
        "torch_cpu": torch.get_rng_state(),
        "torch_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
    }


def restore_rng_state(state: dict[str, Any]) -> None:
    required = {"python", "numpy", "torch_cpu", "torch_cuda"}
    if not isinstance(state, dict) or set(state) != required:
        raise RuntimeError("checkpoint RNG state is incomplete")
    random.setstate(state["python"])
    numpy_state = state["numpy"]
    if not isinstance(numpy_state, dict) or set(numpy_state) != {
        "bit_generator",
        "keys",
        "position",
        "has_gaussian",
        "cached_gaussian",
    }:
        raise RuntimeError("checkpoint NumPy RNG state is incomplete")
    np.random.set_state(
        (
            str(numpy_state["bit_generator"]),
            np.asarray(numpy_state["keys"], dtype=np.uint32),
            int(numpy_state["position"]),
            int(numpy_state["has_gaussian"]),
            float(numpy_state["cached_gaussian"]),
        )
    )
    torch.set_rng_state(state["torch_cpu"].cpu())
    cuda_state = state["torch_cuda"]
    if cuda_state is not None:
        if not torch.cuda.is_available():
            raise RuntimeError("checkpoint contains CUDA RNG state but CUDA is unavailable")
        torch.cuda.set_rng_state_all([value.cpu() for value in cuda_state])


def atomic_torch_save(path: str | Path, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=destination.name + ".", suffix=".tmp", dir=destination.parent
    )
    os.close(descriptor)
    try:
        torch.save(value, temporary_name)
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def load_local_model(
    model_path: str | Path,
    *,
    device: str,
    dtype_name: str,
    trust_remote_code: bool,
    attention_implementation: str,
) -> tuple[Any, Any, "torch.dtype"]:
    import transformers

    path = str(Path(model_path).resolve())
    dtype = resolve_dtype(dtype_name, device)
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        path,
        local_files_only=True,
        trust_remote_code=trust_remote_code,
    )
    tokenizer.padding_side = "right"
    if tokenizer.pad_token_id is None:
        if tokenizer.eos_token_id is None:
            raise RuntimeError("tokenizer has neither pad_token nor eos_token")
        tokenizer.pad_token = tokenizer.eos_token
    load_arguments = {
        "local_files_only": True,
        "trust_remote_code": trust_remote_code,
        "attn_implementation": attention_implementation,
    }
    try:
        backbone = transformers.AutoModelForCausalLM.from_pretrained(
            path, dtype=dtype, **load_arguments
        )
    except TypeError:
        backbone = transformers.AutoModelForCausalLM.from_pretrained(
            path, torch_dtype=dtype, **load_arguments
        )
    backbone = backbone.to(device)
    backbone.eval()
    return tokenizer, backbone, dtype


def tokenize_batch(
    tokenizer: Any,
    examples: Sequence[QueryExample],
    *,
    max_length: int,
    device: str,
) -> dict[str, "torch.Tensor"]:
    if not examples:
        raise ValueError("cannot tokenize an empty batch")
    compute = tokenizer(
        [example.compute_prompt for example in examples],
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_length,
        add_special_tokens=True,
    )
    query = tokenizer(
        [example.query_prompt for example in examples],
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_length,
        add_special_tokens=True,
    )
    labels = torch.tensor(
        [target_token_id(tokenizer, example.target_text) for example in examples],
        dtype=torch.long,
    )
    return {
        "compute_input_ids": compute["input_ids"].to(device),
        "compute_attention_mask": compute["attention_mask"].to(device),
        "query_input_ids": query["input_ids"].to(device),
        "query_attention_mask": query["attention_mask"].to(device),
        "labels": labels.to(device),
    }


def chunked(values: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def train_steps(
    model: FrozenRecurrentCausalLM,
    tokenizer: Any,
    examples: Sequence[QueryExample],
    *,
    config: dict[str, Any],
    optimizer: "torch.optim.Optimizer",
    scaler: Any,
    start_step: int,
    start_overflow_retries: int,
    log_callback: Any,
    checkpoint_callback: Any,
) -> dict[str, Any]:
    training = config["training"]
    batch_size = int(training["batch_size"])
    maximum_steps = int(training["steps"])
    log_every = int(training["log_every"])
    max_length = int(config["model"]["max_sequence_length"])
    device = str(config["model"]["device"])
    if not examples:
        raise ValueError("training examples are empty")
    first_loss = None
    final_loss = None
    maximum_gradient_norm = 0.0
    maximum_state_norm = 0.0
    maximum_injection_norm = 0.0
    overflow_retries_total = int(start_overflow_retries)
    if overflow_retries_total < 0:
        raise ValueError("start_overflow_retries must be nonnegative")
    maximum_overflow_retries = int(training["max_overflow_retries"])
    model.train(True)
    completed = int(start_step)
    while completed < maximum_steps:
        retries_for_step = 0
        indices = [
            ((completed * batch_size) + offset) % len(examples)
            for offset in range(batch_size)
        ]
        batch_examples = [examples[index] for index in indices]
        while True:
            batch = tokenize_batch(
                tokenizer, batch_examples, max_length=max_length, device=device
            )
            optimizer.zero_grad(set_to_none=True)
            logits, trace = model(
                batch["compute_input_ids"],
                batch["compute_attention_mask"],
                batch["query_input_ids"],
                batch["query_attention_mask"],
                recurrence_mode="recurrent",
                answer_mode="recurrent",
            )
            loss = F.cross_entropy(logits.float(), batch["labels"])
            if not bool(torch.isfinite(loss).item()):
                raise RuntimeError(f"nonfinite loss at step {completed + 1}")
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            raw_gradient_norm = gradient_norm(model.workspace_parameters())
            if math.isfinite(raw_gradient_norm):
                break
            if not scaler.is_enabled():
                raise RuntimeError(
                    f"nonfinite unscaled workspace gradient at step {completed + 1}"
                )
            old_scale = float(scaler.get_scale())
            scaler.step(optimizer)
            scaler.update()
            new_scale = float(scaler.get_scale())
            retries_for_step += 1
            overflow_retries_total += 1
            if (
                retries_for_step > maximum_overflow_retries
                or not math.isfinite(new_scale)
                or new_scale <= 0.0
                or new_scale >= old_scale
            ):
                raise RuntimeError(
                    "gradient-scaler overflow recovery failed at "
                    f"step {completed + 1}: retries={retries_for_step}, "
                    f"old_scale={old_scale}, new_scale={new_scale}"
                )
        if raw_gradient_norm <= 0.0:
            raise RuntimeError(f"zero workspace gradient norm at step {completed + 1}")
        torch.nn.utils.clip_grad_norm_(
            model.workspace_parameters(), float(training["gradient_clip"])
        )
        scaler.step(optimizer)
        scaler.update()
        completed += 1
        value = float(loss.detach().item())
        if first_loss is None:
            first_loss = value
        final_loss = value
        maximum_gradient_norm = max(maximum_gradient_norm, raw_gradient_norm)
        trace_statistics = trace.detached_statistics()
        trace_values = [
            float(value)
            for key, values in trace_statistics.items()
            if key != "logical_steps"
            for value in values
        ]
        if not trace_values or not all(math.isfinite(value) for value in trace_values):
            raise RuntimeError(f"nonfinite recurrent trace at step {completed}")
        maximum_state_norm = max(
            maximum_state_norm, max(trace_statistics["state_mean_norm_by_step"])
        )
        maximum_injection_norm = max(
            maximum_injection_norm, max(trace_statistics["injection_mean_norm_by_step"])
        )
        if completed == 1 or completed % log_every == 0 or completed == maximum_steps:
            record = {
                "step": completed,
                "loss": value,
                "gradient_norm": raw_gradient_norm,
                "loss_scale": float(scaler.get_scale()),
                "overflow_retries_before_step": retries_for_step,
                "overflow_retries_total": overflow_retries_total,
                "optimizer_attempts_total": completed + overflow_retries_total,
                "trace": trace_statistics,
            }
            log_callback(record)
            checkpoint_callback(completed)
    return {
        "start_step": start_step,
        "completed_steps": maximum_steps,
        "first_observed_loss": first_loss,
        "final_observed_loss": final_loss,
        "maximum_gradient_norm": maximum_gradient_norm,
        "maximum_state_norm": maximum_state_norm,
        "maximum_injection_norm": maximum_injection_norm,
        "overflow_retries_total": overflow_retries_total,
    }


@torch.no_grad()
def _state_bank(
    model: FrozenRecurrentCausalLM,
    tokenizer: Any,
    examples: Sequence[QueryExample],
    *,
    recurrence_mode: str,
    batch_size: int,
    max_length: int,
    device: str,
) -> tuple["torch.Tensor", dict[str, Any]]:
    unique: dict[tuple[str, int], QueryExample] = {}
    for example in examples:
        unique.setdefault((example.split, example.counter), example)
    keys = sorted(unique)
    representatives = [unique[key] for key in keys]
    bank: dict[tuple[str, int], torch.Tensor] = {}
    trace_records: list[dict[str, Any]] = []
    for batch_examples in chunked(representatives, batch_size):
        batch = tokenize_batch(
            tokenizer, batch_examples, max_length=max_length, device=device
        )
        state, trace = model.encode(
            batch["compute_input_ids"],
            batch["compute_attention_mask"],
            mode=recurrence_mode,
        )
        for example, row in zip(batch_examples, state.detach().float().cpu()):
            bank[(example.split, example.counter)] = row
        trace_records.append(trace.detached_statistics())
    ordered = torch.stack([bank[(example.split, example.counter)] for example in examples])
    aggregate: dict[str, Any] = {"batches": len(trace_records), "records": trace_records}
    return ordered, aggregate


@torch.no_grad()
def _answer_from_bank(
    model: FrozenRecurrentCausalLM,
    tokenizer: Any,
    examples: Sequence[QueryExample],
    states: "torch.Tensor | None",
    *,
    batch_size: int,
    max_length: int,
    device: str,
) -> tuple[list[int], list[dict[str, Any]]]:
    predictions: list[int] = []
    records: list[dict[str, Any]] = []
    for start in range(0, len(examples), batch_size):
        batch_examples = examples[start : start + batch_size]
        batch = tokenize_batch(
            tokenizer, batch_examples, max_length=max_length, device=device
        )
        local_states = (
            None
            if states is None
            else states[start : start + len(batch_examples)].to(device)
        )
        logits = model.answer(
            batch["query_input_ids"], batch["query_attention_mask"], local_states
        )
        predicted = logits.argmax(dim=-1).detach().cpu().tolist()
        expected = batch["labels"].detach().cpu().tolist()
        predictions.extend(int(value) for value in predicted)
        for example, predicted_id, expected_id in zip(batch_examples, predicted, expected):
            records.append(
                {
                    "example_id": example.example_id,
                    "query_type": example.query_type,
                    "applications": example.applications,
                    "final_state": example.final_state,
                    "predicted_token_id": int(predicted_id),
                    "predicted_text": tokenizer.decode([int(predicted_id)]),
                    "target_token_id": int(expected_id),
                    "correct": int(predicted_id) == int(expected_id),
                }
            )
    return predictions, records


def _summarize_records(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise ValueError("cannot summarize empty predictions")
    by_query: dict[str, list[bool]] = defaultdict(list)
    by_depth: dict[str, list[bool]] = defaultdict(list)
    targets_by_query: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for record in records:
        by_query[str(record["query_type"])].append(bool(record["correct"]))
        by_depth[str(record["applications"])].append(bool(record["correct"]))
        targets_by_query[str(record["query_type"])][int(record["target_token_id"])] += 1
    accuracy = sum(bool(record["correct"]) for record in records) / len(records)
    return {
        "count": len(records),
        "accuracy": accuracy,
        "accuracy_by_query": {
            key: sum(values) / len(values) for key, values in sorted(by_query.items())
        },
        "majority_baseline_by_query": {
            key: max(counts.values()) / sum(counts.values())
            for key, counts in sorted(targets_by_query.items())
        },
        "accuracy_by_applications": {
            key: sum(values) / len(values) for key, values in sorted(by_depth.items())
        },
    }


@torch.no_grad()
def evaluate_split(
    model: FrozenRecurrentCausalLM,
    tokenizer: Any,
    examples: Sequence[QueryExample],
    *,
    config: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    model.train(False)
    batch_size = int(config["training"]["eval_batch_size"])
    max_length = int(config["model"]["max_sequence_length"])
    device = str(config["model"]["device"])
    recurrent_states, recurrent_trace = _state_bank(
        model,
        tokenizer,
        examples,
        recurrence_mode="recurrent",
        batch_size=batch_size,
        max_length=max_length,
        device=device,
    )
    no_feedback_states, no_feedback_trace = _state_bank(
        model,
        tokenizer,
        examples,
        recurrence_mode="no_feedback",
        batch_size=batch_size,
        max_length=max_length,
        device=device,
    )
    donor_indices = find_query_derangement(examples)
    if donor_indices is None:
        raise RuntimeError("could not construct the registered query derangement")
    state_variants = {
        "recurrent": recurrent_states,
        "zero": None,
        "shuffle": recurrent_states[torch.tensor(donor_indices, dtype=torch.long)],
        "no_feedback": no_feedback_states,
    }
    summaries: dict[str, Any] = {}
    all_records: list[dict[str, Any]] = []
    for mode, states in state_variants.items():
        _, records = _answer_from_bank(
            model,
            tokenizer,
            examples,
            states,
            batch_size=batch_size,
            max_length=max_length,
            device=device,
        )
        for record in records:
            record["mode"] = mode
        if mode == "shuffle":
            for index, record in enumerate(records):
                donor = examples[donor_indices[index]]
                record["donor_example_id"] = donor.example_id
                record["donor_final_state"] = donor.final_state
        summaries[mode] = _summarize_records(records)
        all_records.extend(records)
    summaries["state_derangement"] = {
        "rows": len(donor_indices),
        "bijection": sorted(donor_indices) == list(range(len(examples))),
        "same_query_family": all(
            examples[index].query_type == examples[donor].query_type
            for index, donor in enumerate(donor_indices)
        ),
        "fixed_state_matches": sum(
            examples[index].final_state == examples[donor].final_state
            for index, donor in enumerate(donor_indices)
        ),
        "answer_compatible_matches": sum(
            (
                examples[index].final_state % 2
                == examples[donor].final_state % 2
                if examples[index].query_type == "parity"
                else examples[index].final_state == examples[donor].final_state
            )
            for index, donor in enumerate(donor_indices)
        ),
    }
    summaries["trace"] = {
        "recurrent": recurrent_trace,
        "no_feedback": no_feedback_trace,
    }
    return summaries, all_records


def environment_report(device: str) -> dict[str, Any]:
    import transformers

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device": (
            torch.cuda.get_device_name(0) if device == "cuda" and torch.cuda.is_available() else None
        ),
    }
