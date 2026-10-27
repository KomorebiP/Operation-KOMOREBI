"""Versioned, pickle-free storage of an exact 1-D signal and its analysis settings.

This persists the source coordinate archive, not trained model parameters,
agent history, or planning state. Coordinates are recomputed on load.
The checksum detects corruption; it is not an authenticity signature.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile

import numpy as np

from .signal import SignalAnalysis1D, analyze_signal
from komorebi_arc3_offline._validation import integer, real_array


def _digest(values: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(values, dtype="<f8").tobytes()).hexdigest()


def save_signal_archive(analysis: SignalAnalysis1D, path: str | Path) -> Path:
    """Atomically replace path with a coordinate archive containing no object arrays."""
    if not isinstance(analysis, SignalAnalysis1D):
        raise ValueError("analysis must be a SignalAnalysis1D")
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    values = real_array(analysis.spatial, "archive signal", ndim=1)
    metadata = {
        "schema_version": 1, "kind": "signal_coordinates_only", "dtype": "float64",
        "length": int(values.size), "modulus": analysis.modulus,
        "effective_depth": analysis.effective_depth, "sha256": _digest(values),
    }
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".prlasm-", delete=False) as handle:
            temporary = Path(handle.name)
            np.savez_compressed(handle, signal=values, metadata=np.asarray(json.dumps(metadata, sort_keys=True)))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return target


def load_signal_archive(path: str | Path, *, maximum_bytes: int = 256 * 1024 * 1024) -> SignalAnalysis1D:
    """Validate size, schema, shape and source checksum before recomputing coordinates."""
    maximum_bytes = integer(maximum_bytes, "maximum_bytes", minimum=1)
    target = Path(path).expanduser().resolve()
    with ZipFile(target) as zipped:
        entries = zipped.infolist()
        if len(entries) != 2 or {entry.filename for entry in entries} != {"signal.npy", "metadata.npy"}:
            raise ValueError("archive must contain only signal.npy and metadata.npy")
        if sum(entry.file_size for entry in entries) > maximum_bytes:
            raise ValueError("archive exceeds the configured uncompressed size limit")
        if next(entry for entry in entries if entry.filename == "metadata.npy").file_size > 65536:
            raise ValueError("archive metadata is too large")
    with np.load(target, allow_pickle=False) as stored:
        raw_metadata = stored["metadata"]
        if raw_metadata.shape != () or raw_metadata.dtype.kind != "U":
            raise ValueError("archive metadata must be a scalar JSON string")
        metadata = json.loads(str(raw_metadata))
        if not isinstance(metadata, dict) or metadata.get("schema_version") != 1 or metadata.get("kind") != "signal_coordinates_only":
            raise ValueError("unsupported signal archive schema")
        raw = stored["signal"]
        if raw.dtype != np.dtype("float64"):
            raise ValueError("stored signal dtype must be float64")
        values = real_array(raw, "stored signal", ndim=1)
        if metadata.get("dtype") != "float64" or metadata.get("length") != values.size:
            raise ValueError("archive length or dtype metadata mismatch")
        if metadata.get("sha256") != _digest(values):
            raise ValueError("archive source checksum mismatch")
        depth = integer(metadata.get("effective_depth"), "effective_depth")
        modulus = integer(metadata.get("modulus"), "modulus", minimum=1)
        # Bound derived work too, not just the stored source payload.
        if depth > values.size.bit_length() - 1 or values.size % (2**depth):
            raise ValueError("archive depth is inconsistent with signal length")
        if (depth + 1) * values.nbytes + 256 * modulus > maximum_bytes:
            raise ValueError("derived analysis exceeds the configured size budget")
        return analyze_signal(values.copy(), modulus=modulus, maximum_depth=depth)


__all__ = ["save_signal_archive", "load_signal_archive"]
