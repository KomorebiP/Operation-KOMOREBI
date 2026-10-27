"""Restricted NumPy reader for the small weights-only PyTorch checkpoints.

The bundled checkpoints contain only dictionaries, primitive metadata, an
OrderedDict, and contiguous CPU FloatStorage tensors.  This module does not
import PyTorch and never permits arbitrary pickle globals.
"""

from __future__ import annotations

import collections
import dataclasses
import hashlib
import io
import pickle
import zipfile
from pathlib import Path
from typing import Any

import numpy as np


EXPECTED_STATE_KEYS = (
    "state_embedding.weight",
    "operator_encoder.weight",
    "decoder.weight",
)


@dataclasses.dataclass(frozen=True)
class _StorageRef:
    key: str
    size: int


@dataclasses.dataclass(frozen=True)
class _TensorRef:
    storage: _StorageRef
    offset: int
    shape: tuple[int, ...]
    stride: tuple[int, ...]


@dataclasses.dataclass(frozen=True)
class LinearOperatorWeights:
    state_embedding: np.ndarray
    operator_encoder: np.ndarray
    decoder: np.ndarray

    def validate(self) -> None:
        expected = ((8, 8), (64, 64), (8, 8))
        observed = (
            self.state_embedding.shape,
            self.operator_encoder.shape,
            self.decoder.shape,
        )
        if observed != expected:
            raise ValueError(f"unexpected weight shapes: {observed}")
        for array in (self.state_embedding, self.operator_encoder, self.decoder):
            if array.dtype != np.float32:
                raise ValueError(f"unexpected tensor dtype: {array.dtype}")
            if not np.isfinite(array).all():
                raise ValueError("checkpoint contains a non-finite tensor")


@dataclasses.dataclass(frozen=True)
class LoadedCheckpoint:
    path: Path
    sha256: str
    metadata: dict[str, Any]
    weights: LinearOperatorWeights


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rebuild_tensor(
    storage: _StorageRef,
    offset: int,
    shape: tuple[int, ...],
    stride: tuple[int, ...],
    requires_grad: bool,
    backward_hooks: Any,
) -> _TensorRef:
    del requires_grad, backward_hooks
    if not isinstance(storage, _StorageRef):
        raise pickle.UnpicklingError("tensor did not reference an approved storage")
    return _TensorRef(storage, int(offset), tuple(map(int, shape)), tuple(map(int, stride)))


class _RestrictedCheckpointUnpickler(pickle.Unpickler):
    _FLOAT_STORAGE = ("approved_storage", "float32")

    def find_class(self, module: str, name: str) -> Any:
        key = (module, name)
        if key == ("collections", "OrderedDict"):
            return collections.OrderedDict
        if key == ("torch._utils", "_rebuild_tensor_v2"):
            return _rebuild_tensor
        if key == ("torch", "FloatStorage"):
            return self._FLOAT_STORAGE
        raise pickle.UnpicklingError(f"forbidden checkpoint global: {module}.{name}")

    def persistent_load(self, persistent_id: Any) -> _StorageRef:
        if not isinstance(persistent_id, tuple) or len(persistent_id) != 5:
            raise pickle.UnpicklingError("unexpected persistent identifier")
        tag, storage_type, key, location, size = persistent_id
        if tag != "storage" or storage_type != self._FLOAT_STORAGE or location != "cpu":
            raise pickle.UnpicklingError("only CPU FloatStorage tensors are accepted")
        if not isinstance(key, str) or not key.isdigit():
            raise pickle.UnpicklingError("invalid storage key")
        size = int(size)
        if size < 0 or size > 10_000_000:
            raise pickle.UnpicklingError("invalid storage size")
        return _StorageRef(key=key, size=size)


def _resolve_tensor(
    archive: zipfile.ZipFile,
    archive_root: str,
    tensor: _TensorRef,
    byte_order: str,
) -> np.ndarray:
    if not isinstance(tensor, _TensorRef):
        raise ValueError("state dictionary contains a non-tensor value")
    if len(tensor.shape) != len(tensor.stride) or not tensor.shape:
        raise ValueError("invalid tensor rank")
    if any(value < 0 for value in tensor.shape + tensor.stride) or tensor.offset < 0:
        raise ValueError("negative tensor metadata is not supported")
    member = f"{archive_root}/data/{tensor.storage.key}"
    raw = archive.read(member)
    if len(raw) != tensor.storage.size * 4:
        raise ValueError("storage byte length does not match declared size")
    last_element = tensor.offset
    for dimension, stride in zip(tensor.shape, tensor.stride):
        if dimension:
            last_element += (dimension - 1) * stride
    if last_element >= tensor.storage.size:
        raise ValueError("tensor view exceeds its storage")
    dtype = np.dtype("<f4" if byte_order == "little" else ">f4")
    array = np.ndarray(
        tensor.shape,
        dtype=dtype,
        buffer=raw,
        offset=tensor.offset * 4,
        strides=tuple(value * 4 for value in tensor.stride),
    ).copy()
    return array.astype(np.float32, copy=False)


def load_checkpoint(path: Path, expected_sha256: str | None = None) -> LoadedCheckpoint:
    path = Path(path).resolve()
    observed_digest = file_sha256(path)
    if expected_sha256 is not None and observed_digest != expected_sha256:
        raise ValueError(
            f"checkpoint digest mismatch for {path.name}: {observed_digest} != {expected_sha256}"
        )
    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        if any(name.startswith("/") or ".." in Path(name).parts for name in members):
            raise ValueError("unsafe archive member path")
        pickle_members = [name for name in members if name.endswith("/data.pkl")]
        if len(pickle_members) != 1:
            raise ValueError("checkpoint must contain exactly one data.pkl")
        pickle_member = pickle_members[0]
        archive_root = pickle_member.rsplit("/", 1)[0]
        if archive.getinfo(pickle_member).file_size > 1_000_000:
            raise ValueError("checkpoint metadata exceeds the size limit")
        payload = _RestrictedCheckpointUnpickler(
            io.BytesIO(archive.read(pickle_member))
        ).load()
        if not isinstance(payload, dict):
            raise ValueError("checkpoint payload must be a dictionary")
        state_dict = payload.get("state_dict")
        if not isinstance(state_dict, collections.OrderedDict):
            raise ValueError("checkpoint state_dict must be an OrderedDict")
        if tuple(state_dict.keys()) != EXPECTED_STATE_KEYS:
            raise ValueError(f"unexpected state_dict keys: {tuple(state_dict.keys())}")
        byte_order = archive.read(f"{archive_root}/byteorder").decode("ascii").strip()
        if byte_order not in {"little", "big"}:
            raise ValueError("unsupported checkpoint byte order")
        arrays = {
            key: _resolve_tensor(archive, archive_root, value, byte_order)
            for key, value in state_dict.items()
        }
    metadata = {key: value for key, value in payload.items() if key != "state_dict"}
    if not isinstance(metadata.get("config"), dict):
        raise ValueError("checkpoint config is missing")
    weights = LinearOperatorWeights(
        state_embedding=arrays["state_embedding.weight"],
        operator_encoder=arrays["operator_encoder.weight"],
        decoder=arrays["decoder.weight"],
    )
    weights.validate()
    return LoadedCheckpoint(path=path, sha256=observed_digest, metadata=metadata, weights=weights)


def restricted_loads_for_test(data: bytes) -> Any:
    """Expose the restricted metadata loader for a negative security test."""

    return _RestrictedCheckpointUnpickler(io.BytesIO(data)).load()
