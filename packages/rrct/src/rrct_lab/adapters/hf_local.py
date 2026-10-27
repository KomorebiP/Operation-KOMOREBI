"""Strictly local, optional Hugging Face decoder instrumentation.

Importing this module requires only NumPy.  PyTorch and Transformers are loaded
only when a model or hook is requested.  Model identifiers are never accepted:
the caller must supply an existing local path, and both model and tokenizer are
opened with ``local_files_only=True`` and ``trust_remote_code=False``.
"""

from __future__ import annotations

import hashlib
import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from rrct_lab.exceptions import DependencyError


_REMOTE_PREFIXES = (
    "http://",
    "https://",
    "hf://",
    "s3://",
    "gs://",
    "ftp://",
)
_SUPPORTED_DTYPES = ("float32", "float16", "bfloat16")


def _finite_array(value: Any, *, name: str, ndim: int | None = None) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite numeric array") from error
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"{name} must be a {ndim}-D array")
    if array.ndim == 0 or any(size <= 0 for size in array.shape):
        raise ValueError(f"{name} must not be scalar or empty")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return np.array(array, dtype=np.float64, copy=True)


def _integer(value: Any, *, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be an integer")
    return int(value)


def resolve_bounded_index(index: int, size: int, *, name: str) -> int:
    """Resolve a Python-style positive or negative index with clear bounds."""

    selected = _integer(index, name=name)
    length = _integer(size, name=f"{name}_size")
    if length <= 0:
        raise ValueError(f"{name}_size must be positive")
    if selected < 0:
        selected += length
    if not 0 <= selected < length:
        raise ValueError(f"{name} is outside [0, {length})")
    return selected


def validate_local_model_path(model_path: str | Path) -> Path:
    """Return a resolved existing local file or directory, rejecting URIs."""

    if not isinstance(model_path, (str, Path)):
        raise ValueError("model_path must be a local filesystem path")
    raw = str(model_path).strip()
    if not raw:
        raise ValueError("model_path must not be empty")
    if raw.lower().startswith(_REMOTE_PREFIXES) or "://" in raw:
        raise ValueError("remote model locations are not allowed")
    path = Path(raw).expanduser()
    if not path.exists():
        raise ValueError("model_path must already exist locally")
    if not path.is_dir() and not path.is_file():
        raise ValueError("model_path must be a regular local file or directory")
    return path.resolve(strict=True)


def validate_projector(projector: Any, *, dimension: int | None = None) -> np.ndarray:
    """Validate a finite symmetric idempotent projector."""

    matrix = _finite_array(projector, name="projector", ndim=2)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("projector must be square")
    if dimension is not None:
        expected = _integer(dimension, name="dimension")
        if expected <= 0 or matrix.shape != (expected, expected):
            raise ValueError("projector has the wrong residual dimension")
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-9):
        raise ValueError("projector must be symmetric")
    if not np.allclose(matrix @ matrix, matrix, rtol=0.0, atol=1e-8):
        raise ValueError("projector must be idempotent")
    return matrix


def norm_matched_residual_patch(source: Any, target: Any) -> np.ndarray:
    """Scale a source residual to the target residual's Euclidean norm."""

    source_vector = _finite_array(source, name="source", ndim=1)
    target_vector = _finite_array(target, name="target", ndim=1)
    if source_vector.shape != target_vector.shape:
        raise ValueError("source and target residual shapes differ")
    source_norm = float(np.linalg.norm(source_vector))
    target_norm = float(np.linalg.norm(target_vector))
    tolerance = 64.0 * np.finfo(np.float64).eps
    if source_norm <= tolerance:
        if target_norm <= tolerance:
            return np.zeros_like(target_vector)
        raise ValueError("a zero-norm source cannot match a nonzero target")
    return np.asarray(source_vector * (target_norm / source_norm), dtype=np.float64)


def projector_ablate(residual: Any, projector: Any) -> np.ndarray:
    """Remove a validated projector from a vector or row-major residual batch."""

    values = _finite_array(residual, name="residual")
    if values.ndim not in (1, 2):
        raise ValueError("residual must be a vector or row-major matrix")
    matrix = validate_projector(projector, dimension=values.shape[-1])
    return np.asarray(values - values @ matrix, dtype=np.float64)


def _require_torch() -> Any:
    try:
        return importlib.import_module("torch")
    except (ImportError, ModuleNotFoundError) as error:
        raise DependencyError(
            "The local transformer adapter requires optional dependency 'torch'."
        ) from error


def _require_hf_dependencies() -> tuple[Any, Any]:
    torch = _require_torch()
    try:
        transformers = importlib.import_module("transformers")
    except (ImportError, ModuleNotFoundError) as error:
        raise DependencyError(
            "The local transformer adapter requires optional dependency "
            "'transformers'."
        ) from error
    return torch, transformers


def resolve_decoder_layers(model: Any) -> tuple[tuple[Any, ...], str]:
    """Find common decoder-block containers without importing model classes."""

    layouts = (
        (("model", "layers"), "model.layers"),
        (("transformer", "h"), "transformer.h"),
        (("gpt_neox", "layers"), "gpt_neox.layers"),
    )
    for attributes, label in layouts:
        current = model
        for attribute in attributes:
            if not hasattr(current, attribute):
                break
            current = getattr(current, attribute)
        else:
            try:
                layers = tuple(current)
            except TypeError:
                continue
            if layers:
                return layers, label
    raise ValueError(
        "unsupported decoder layout; expected model.layers, transformer.h, "
        "or gpt_neox.layers"
    )


@dataclass(frozen=True)
class LocalCausalLMBundle:
    """Loaded local model objects and non-sensitive adapter metadata."""

    model_path: str
    model: Any = field(repr=False, compare=False)
    tokenizer: Any = field(repr=False, compare=False)
    layers: tuple[Any, ...] = field(repr=False, compare=False)
    layer_layout: str
    device: str
    dtype: str | None

    def metadata(self) -> dict[str, Any]:
        return {
            "model_path": self.model_path,
            "layer_layout": self.layer_layout,
            "layer_count": len(self.layers),
            "device": self.device,
            "dtype": self.dtype,
            "local_files_only": True,
            "trust_remote_code": False,
            "training": False,
            "network_access": False,
        }


def load_local_causal_lm(
    model_path: str | Path,
    *,
    device: str = "cpu",
    dtype: str | None = None,
) -> LocalCausalLMBundle:
    """Load a causal LM and tokenizer exclusively from an existing local path."""

    path = validate_local_model_path(model_path)
    if not isinstance(device, str) or not device.strip():
        raise ValueError("device must be a nonempty string")
    selected_device = device.strip()
    if not (
        selected_device == "cpu"
        or selected_device == "mps"
        or selected_device == "cuda"
        or (
            selected_device.startswith("cuda:")
            and selected_device[5:].isdigit()
        )
    ):
        raise ValueError("device must be cpu, mps, cuda, or cuda:<index>")
    if dtype is not None and dtype not in _SUPPORTED_DTYPES:
        raise ValueError(f"dtype must be one of {_SUPPORTED_DTYPES} or None")

    torch, transformers = _require_hf_dependencies()
    load_options: dict[str, Any] = {}
    if dtype is not None:
        load_options["torch_dtype"] = getattr(torch, dtype)
    source = str(path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        source,
        local_files_only=True,
        trust_remote_code=False,
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
        source,
        local_files_only=True,
        trust_remote_code=False,
        **load_options,
    )
    model.eval()
    model.to(selected_device)
    layers, layout = resolve_decoder_layers(model)
    return LocalCausalLMBundle(
        model_path=source,
        model=model,
        tokenizer=tokenizer,
        layers=layers,
        layer_layout=layout,
        device=selected_device,
        dtype=dtype,
    )


def _primary_hidden(output: Any) -> Any:
    if isinstance(output, (tuple, list)):
        if not output:
            raise RuntimeError("decoder layer returned an empty output")
        return output[0]
    return output


def _replace_primary_hidden(output: Any, replacement: Any) -> Any:
    if isinstance(output, tuple):
        return (replacement, *output[1:])
    if isinstance(output, list):
        return [replacement, *output[1:]]
    return replacement


def make_norm_matched_patch_hook(
    source_residual: Any,
    *,
    token_index: int,
) -> Any:
    """Build a decoder forward hook that installs a norm-matched residual."""

    source = _finite_array(source_residual, name="source_residual", ndim=1)
    selected_token = _integer(token_index, name="token_index")
    torch = _require_torch()

    def hook(_module: Any, _inputs: Any, output: Any) -> Any:
        hidden = _primary_hidden(output)
        if getattr(hidden, "ndim", None) != 3:
            raise RuntimeError("decoder residual must have shape (batch, tokens, hidden)")
        token = resolve_bounded_index(
            selected_token, int(hidden.shape[1]), name="token_index"
        )
        if int(hidden.shape[2]) != source.shape[0]:
            raise RuntimeError("patch residual has the wrong hidden dimension")
        patch = torch.as_tensor(source, dtype=hidden.dtype, device=hidden.device)
        current = hidden[:, token, :]
        source_norm = torch.linalg.vector_norm(patch)
        target_norm = torch.linalg.vector_norm(current, dim=-1, keepdim=True)
        tolerance = torch.finfo(hidden.dtype).eps * 64.0
        if bool((source_norm <= tolerance).item()):
            if bool(torch.any(target_norm > tolerance).item()):
                raise RuntimeError("a zero patch cannot match a nonzero residual")
            replacement = torch.zeros_like(current)
        else:
            replacement = patch.unsqueeze(0) * (target_norm / source_norm)
        modified = hidden.clone()
        modified[:, token, :] = replacement
        return _replace_primary_hidden(output, modified)

    return hook


def make_projector_ablation_hook(
    projector: Any,
    *,
    token_index: int,
) -> Any:
    """Build a decoder forward hook that removes a finite projector."""

    matrix = validate_projector(projector)
    selected_token = _integer(token_index, name="token_index")
    torch = _require_torch()

    def hook(_module: Any, _inputs: Any, output: Any) -> Any:
        hidden = _primary_hidden(output)
        if getattr(hidden, "ndim", None) != 3:
            raise RuntimeError("decoder residual must have shape (batch, tokens, hidden)")
        token = resolve_bounded_index(
            selected_token, int(hidden.shape[1]), name="token_index"
        )
        if int(hidden.shape[2]) != matrix.shape[0]:
            raise RuntimeError("projector has the wrong hidden dimension")
        tensor_projector = torch.as_tensor(
            matrix, dtype=hidden.dtype, device=hidden.device
        )
        current = hidden[:, token, :]
        modified = hidden.clone()
        modified[:, token, :] = current - current @ tensor_projector
        return _replace_primary_hidden(output, modified)

    return hook


def _target_ids(values: Sequence[int]) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError("target_token_ids must be an integer sequence")
    try:
        result = tuple(_integer(value, name="target_token_id") for value in values)
    except TypeError as error:
        raise ValueError("target_token_ids must be an integer sequence") from error
    if not result:
        raise ValueError("target_token_ids must not be empty")
    if any(value < 0 for value in result):
        raise ValueError("target_token_ids must be nonnegative")
    if len(set(result)) != len(result):
        raise ValueError("target_token_ids must be unique")
    return result


def _finite_json_array(value: Any, *, name: str) -> list[Any]:
    array = _finite_array(value, name=name)
    return array.tolist()


def probe_target_token_vjps(
    bundle: LocalCausalLMBundle,
    prompt: str,
    target_token_ids: Sequence[int],
    *,
    layer_index: int = -1,
    residual_token_index: int = -1,
    prediction_token_index: int = -1,
    max_length: int | None = None,
) -> dict[str, Any]:
    """Capture a token residual and target-logit VJPs at one decoder layer."""

    if not isinstance(bundle, LocalCausalLMBundle):
        raise ValueError("bundle must be a LocalCausalLMBundle")
    if not isinstance(prompt, str) or not prompt:
        raise ValueError("prompt must be a nonempty string")
    targets = _target_ids(target_token_ids)
    selected_layer = resolve_bounded_index(
        layer_index, len(bundle.layers), name="layer_index"
    )
    if max_length is not None:
        maximum = _integer(max_length, name="max_length")
        if maximum <= 0:
            raise ValueError("max_length must be positive")
    else:
        maximum = None

    torch, _ = _require_hf_dependencies()
    tokenizer_options: dict[str, Any] = {
        "return_tensors": "pt",
        "add_special_tokens": True,
    }
    if maximum is not None:
        tokenizer_options.update({"truncation": True, "max_length": maximum})
    encoded = bundle.tokenizer(prompt, **tokenizer_options)
    if "input_ids" not in encoded:
        raise RuntimeError("tokenizer did not return input_ids")
    inputs = {
        str(name): tensor.to(bundle.device)
        for name, tensor in encoded.items()
        if hasattr(tensor, "to")
    }
    input_ids = inputs.get("input_ids")
    if input_ids is None or getattr(input_ids, "ndim", None) != 2:
        raise RuntimeError("input_ids must have shape (batch, tokens)")
    if int(input_ids.shape[0]) != 1 or int(input_ids.shape[1]) <= 0:
        raise ValueError("the probe requires exactly one nonempty token sequence")

    captured: dict[str, Any] = {}

    def capture(_module: Any, _inputs: Any, output: Any) -> None:
        hidden = _primary_hidden(output)
        if getattr(hidden, "ndim", None) != 3:
            raise RuntimeError("decoder residual must have shape (batch, tokens, hidden)")
        if not bool(getattr(hidden, "requires_grad", False)):
            raise RuntimeError("captured residual does not support gradients")
        hidden.retain_grad()
        captured["hidden"] = hidden

    handle = bundle.layers[selected_layer].register_forward_hook(capture)
    bundle.model.zero_grad(set_to_none=True)
    try:
        with torch.enable_grad():
            outputs = bundle.model(**inputs, use_cache=False)
    finally:
        handle.remove()
    if "hidden" not in captured:
        raise RuntimeError("selected decoder layer did not execute")
    hidden = captured["hidden"]
    logits = getattr(outputs, "logits", None)
    if logits is None and isinstance(outputs, (tuple, list)) and outputs:
        logits = outputs[0]
    if logits is None or getattr(logits, "ndim", None) != 3:
        raise RuntimeError("causal LM did not return rank-three logits")

    residual_token = resolve_bounded_index(
        residual_token_index, int(hidden.shape[1]), name="residual_token_index"
    )
    prediction_token = resolve_bounded_index(
        prediction_token_index,
        int(logits.shape[1]),
        name="prediction_token_index",
    )
    vocabulary_size = int(logits.shape[2])
    if any(target >= vocabulary_size for target in targets):
        raise ValueError("target_token_id is outside the model vocabulary")

    vjp_rows: list[dict[str, Any]] = []
    for target_position, target in enumerate(targets):
        score = logits[0, prediction_token, target]
        gradient = torch.autograd.grad(
            score,
            hidden,
            retain_graph=target_position + 1 < len(targets),
            create_graph=False,
            allow_unused=False,
        )[0][0, residual_token, :]
        gradient_array = gradient.detach().to("cpu").to(torch.float64).numpy()
        logit_value = float(score.detach().to("cpu").item())
        if not np.isfinite(logit_value):
            raise RuntimeError("target logit is not finite")
        vjp_rows.append(
            {
                "target_token_id": int(target),
                "target_logit": logit_value,
                "vjp": _finite_json_array(gradient_array, name="target_vjp"),
                "vjp_norm": float(np.linalg.norm(gradient_array)),
            }
        )

    residual = hidden[0, residual_token, :].detach().to("cpu").to(torch.float64)
    token_id_values = input_ids[0].detach().to("cpu").tolist()
    try:
        target_tokens = [
            str(value) for value in bundle.tokenizer.convert_ids_to_tokens(list(targets))
        ]
    except (AttributeError, TypeError, ValueError):
        target_tokens = []
    model_type = str(getattr(getattr(bundle.model, "config", None), "model_type", ""))
    return {
        "schema": "rrct_lab.local_jspace_probe.v1",
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "model_path": bundle.model_path,
        "model_type": model_type,
        "layer_layout": bundle.layer_layout,
        "layer_index": selected_layer,
        "residual_token_index": residual_token,
        "prediction_token_index": prediction_token,
        "input_token_ids": [int(value) for value in token_id_values],
        "target_token_ids": [int(value) for value in targets],
        "target_tokens": target_tokens,
        "residual": _finite_json_array(residual.numpy(), name="residual"),
        "residual_norm": float(np.linalg.norm(residual.numpy())),
        "residual_dimension": int(hidden.shape[2]),
        "residual_dtype": str(hidden.dtype),
        "target_vjps": vjp_rows,
        "local_files_only": True,
        "trust_remote_code": False,
        "training": False,
        "network_access": False,
    }

