#!/usr/bin/env python3
"""Seal and verify the prospective v0.3 D4 calibration/evaluation bank.

This module is intentionally checkpoint-free.  It samples one 256-bit root
from the operating system only after the complete design commit has been
validated, immediately writes an exclusive draw receipt, and derives every
random stream from that root with domain-separated HKDF-SHA256.

The draw receipt makes a failed or interrupted draw terminal: ``seal`` never
overwrites an existing bank, seal receipt, draw receipt, or symbolic link.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import stat
import sys
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np


AUTHOR = "Komorebi P."
VERSION = "0.3.0"

BANK_SCHEMA = "komorebi.neuralese.semantic_retraction.fresh_bank.v1"
DRAW_SCHEMA = "komorebi.neuralese.semantic_retraction.fresh_bank_draw.v1"
SEAL_SCHEMA = "komorebi.neuralese.semantic_retraction.fresh_bank_seal.v1"
DESIGN_SCHEMA = "komorebi.neuralese.semantic_retraction.design_commit.v1"
REGISTRY_SCHEMA = "komorebi.neuralese.semantic_retraction.spent_bank_registry.v1"
PROTOCOL_SCHEMA = "komorebi.neuralese.semantic_retraction_factorial_protocol.v1"

DESIGN_STATUS = "DESIGN_FROZEN_NO_PRODUCTION_ENTROPY"
PROTOCOL_STATUS = "FROZEN_PROSPECTIVE_FRESH_BANK_FACTORIAL"
REGISTRY_STATUS = "IMMUTABLE_PRIOR_BANK_EXCLUSIONS"
BANK_STATUS = "SEALED_FRESH_BANK_UNSPENT"
DRAW_STATUS = "PRODUCTION_ROOT_DRAWN_ONCE"
SEAL_STATUS = "SEALED_AND_VERIFIED"

CONTEXTS_PER_SPLIT = 64
PATHS_PER_SPLIT = 8
PRIMARY_PATH_DEPTH = 64
MIN_FREE_BYTES_BEFORE_DRAW = 64 * 1024 * 1024
N_STATES = 8
N_OPERATORS = 2

KDF_SALT = b"komorebi.neuralese.semantic_retraction.fresh_bank.v1\x00hkdf-extract"
KDF_INFO_PREFIX = b"komorebi.neuralese.semantic_retraction.fresh_bank.v1\x00"
KDF_DESCRIPTION = "HKDF-SHA256; fixed salt; info=prefix || UTF-8 domain"
RNG_DESCRIPTION = "numpy.random.Generator(numpy.random.PCG64(unsigned-big-endian-256-bit-seed))"
NUMPY_VERSION = np.__version__
REGISTRY_CONTEXT_KEY_DEFINITION = (
    "sha256(float32 D4 tables C-bytes || int64 canonical_to_slot C-bytes)"
)
REGISTRY_PATH_HASH_DEFINITION = "sha256(canonical compact JSON integer word)"

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DEFAULT_DESIGN_COMMIT = HERE / "DESIGN_COMMIT.json"
DEFAULT_REGISTRY = PROJECT_ROOT / "lineage" / "SPENT_BANK_REGISTRY.json"
DEFAULT_BANK = HERE / "FRESH_BANK.json"
DEFAULT_DRAW_RECEIPT = HERE / "FRESH_BANK_DRAW_RECEIPT.json"
DEFAULT_SEAL_RECEIPT = HERE / "FRESH_BANK_SEAL.json"

PARENT_RELEASE_NAME = (
    "Komorebi_Neuralese_Semantic_Retraction_v0.2.0_"
    "ABORTED_PRIMARY_WITH_POSTHOC_CROSSCHECK.zip"
)

DESIGN_FILE_MAP = {
    "protocol_sha256": ("prospective", "PROTOCOL.json"),
    "frozen_protocol_receipt_sha256": (
        "prospective",
        "FROZEN_PROTOCOL.sha256",
    ),
    "scientific_boundaries_sha256": (
        "reports",
        "SCIENTIFIC_BOUNDARIES.md",
    ),
    "factorial_runner_sha256": ("prospective", "run_factorial_probe.py"),
    "factorial_test_sha256": ("prospective", "test_factorial_probe.py"),
    "fresh_bank_implementation_sha256": ("prospective", "fresh_bank.py"),
    "fresh_bank_test_sha256": ("prospective", "test_fresh_bank.py"),
    "lifecycle_test_sha256": ("prospective", "test_lifecycle.py"),
    "projector_test_sha256": ("preflight", "test_projector_semantics.py"),
    "parameter_preflight_sha256": ("preflight", "PREFLIGHT.json"),
    "synthetic_tests_sha256": ("preflight", "SYNTHETIC_TESTS.json"),
    "spent_bank_registry_sha256": ("lineage", "SPENT_BANK_REGISTRY.json"),
    "spent_registry_builder_sha256": ("lineage", "build_spent_registry.py"),
    "parent_release_sha256": ("lineage", "immutable", PARENT_RELEASE_NAME),
}

DESIGN_METADATA_FIELDS = {
    "schema",
    "version",
    "status",
    "production_entropy_present",
    "numpy_version",
}

PROTOCOL_IMPLEMENTATION_FIELDS = (
    "factorial_runner_sha256",
    "factorial_test_sha256",
    "fresh_bank_implementation_sha256",
    "fresh_bank_test_sha256",
    "lifecycle_test_sha256",
    "projector_test_sha256",
    "spent_registry_builder_sha256",
)

SYNTHETIC_IMPLEMENTATION_FIELDS = (
    "factorial_runner_sha256",
    "factorial_test_sha256",
    "fresh_bank_implementation_sha256",
    "fresh_bank_test_sha256",
    "lifecycle_test_sha256",
    "projector_test_sha256",
)


def canonical_json_bytes(value: object) -> bytes:
    """Return the one permitted JSON serialization for sealed artifacts."""

    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_json_digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_hex_digest(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        bytes.fromhex(value)
    except ValueError:
        return False
    return value == value.lower()


def _assert_regular_file(path: Path, *, label: str) -> Path:
    """Reject links and non-regular inputs before resolving their contents."""

    path = Path(path).absolute()
    _assert_directory_chain_has_no_symlink(path.parent)
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"missing {label}: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise ValueError(f"{label} must not be a symbolic link: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{label} must be a regular file: {path}")
    return path.resolve(strict=True)


def _assert_directory_chain_has_no_symlink(path: Path) -> Path:
    """Return an absolute existing directory after checking every component."""

    path = Path(path).absolute()
    if not path.exists():
        raise FileNotFoundError(f"output parent does not exist: {path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        metadata = current.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"output path traverses symbolic link: {current}")
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"output parent component is not a directory: {current}")
    return path.resolve(strict=True)


def _prepare_new_file(path: Path, *, label: str) -> Path:
    path = Path(path).absolute()
    parent = _assert_directory_chain_has_no_symlink(path.parent)
    normalized = parent / path.name
    if os.path.lexists(normalized):
        metadata = normalized.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"refusing symbolic-link {label}: {normalized}")
        raise FileExistsError(f"refusing to overwrite existing {label}: {normalized}")
    return normalized


def _exclusive_write(path: Path, payload: bytes, *, label: str) -> None:
    """Create one durable file without an overwrite or rename window."""

    path = _prepare_new_file(path, label=label)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        _write_reserved_file(descriptor, payload)
    except BaseException:
        # The possibly partial file is deliberately retained.  Its existence
        # prevents a second production entropy draw.
        raise
    _fsync_directory(path.parent)


def _fsync_directory(path: Path) -> None:
    """Durably publish directory entries where the platform exposes it."""

    directory_flag = getattr(os, "O_DIRECTORY", None)
    if directory_flag is None:
        # Windows does not expose O_DIRECTORY through Python.  Exclusive file
        # creation still enforces process-level no-overwrite semantics there.
        return
    descriptor = os.open(path, os.O_RDONLY | directory_flag)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _reserve_new_file(path: Path, *, label: str) -> int:
    """Exclusively reserve a terminal marker before any irreversible action."""

    path = _prepare_new_file(path, label=label)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        # Persist the empty terminal marker and its directory entry before the
        # OS entropy call.  Thus even a power loss cannot normally erase the
        # evidence that a production draw was begun.
        os.fsync(descriptor)
        _fsync_directory(path.parent)
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _write_reserved_file(descriptor: int, payload: bytes) -> None:
    """Fill and durably close a file already reserved with ``O_EXCL``."""

    try:
        handle = os.fdopen(descriptor, "wb", closefd=True)
    except BaseException:
        # fdopen has not taken ownership if construction itself fails.
        os.close(descriptor)
        raise
    with handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _read_exact_json(path: Path, *, label: str) -> tuple[dict[str, Any], bytes, Path]:
    resolved = _assert_regular_file(path, label=label)
    payload = resolved.read_bytes()
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON in {label}: {resolved}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain one JSON object")
    if canonical_json_bytes(value) != payload:
        raise ValueError(f"{label} is not exact canonical JSON: {resolved}")
    return value, payload, resolved


def _read_hashed_json(path: Path, *, label: str) -> tuple[dict[str, Any], bytes, Path]:
    """Read an immutable JSON input whose exact raw bytes are hash-bound.

    The historical registry predates the compact serialization used for new
    receipts.  Its formatting is therefore not rewritten or normalized; the
    design commit binds its exact bytes, while semantic validation binds its
    decoded content.
    """

    resolved = _assert_regular_file(path, label=label)
    payload = resolved.read_bytes()
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON in {label}: {resolved}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain one JSON object")
    return value, payload, resolved


def validate_registry_document(registry: Mapping[str, Any]) -> dict[str, Any]:
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise ValueError("spent-bank registry schema mismatch")
    if registry.get("version") != VERSION:
        raise ValueError("spent-bank registry version mismatch")
    if registry.get("status") != REGISTRY_STATUS:
        raise ValueError("spent-bank registry is not immutable/frozen")
    if registry.get("author") != AUTHOR:
        raise ValueError("spent-bank registry author mismatch")
    if registry.get("context_key_definition") != REGISTRY_CONTEXT_KEY_DEFINITION:
        raise ValueError("spent-bank registry context-key definition mismatch")
    if registry.get("path_word_sha256_definition") != REGISTRY_PATH_HASH_DEFINITION:
        raise ValueError("spent-bank registry path-hash definition mismatch")

    fields: dict[str, tuple[str, ...]] = {}
    for name in ("forbidden_context_keys", "forbidden_path_word_sha256"):
        values = registry.get(name)
        if not isinstance(values, list) or not all(_is_hex_digest(item) for item in values):
            raise ValueError(f"registry {name} must be a list of lowercase SHA-256 values")
        if values != sorted(set(values)):
            raise ValueError(f"registry {name} must be strictly sorted and unique")
        fields[name] = tuple(values)
    counts = registry.get("counts")
    expected_counts = {
        "unique_context_keys": len(fields["forbidden_context_keys"]),
        "unique_path_words": len(fields["forbidden_path_word_sha256"]),
    }
    if counts != expected_counts:
        raise ValueError("spent-bank registry declared counts do not match its exclusions")
    parent_release = registry.get("parent_release")
    if not isinstance(parent_release, Mapping) or not _is_hex_digest(
        parent_release.get("sha256")
    ):
        raise ValueError("spent-bank registry lacks its parent-release SHA-256")
    return {
        "forbidden_context_keys": fields["forbidden_context_keys"],
        "forbidden_path_word_sha256": fields["forbidden_path_word_sha256"],
        "parent_release_sha256": parent_release["sha256"],
    }


def validate_protocol_for_entropy_draw(protocol: Mapping[str, Any]) -> None:
    """Require the hash-bound protocol to be frozen and bank-compatible."""

    if protocol.get("schema") != PROTOCOL_SCHEMA:
        raise ValueError("protocol schema does not authorize production entropy")
    if protocol.get("version") != VERSION:
        raise ValueError("protocol version does not authorize production entropy")
    if protocol.get("status") != PROTOCOL_STATUS:
        raise ValueError("protocol is not frozen for production entropy")
    if protocol.get("author") != AUTHOR:
        raise ValueError("protocol author mismatch")
    if protocol.get("runtime_contract", {}).get("numpy_version") != NUMPY_VERSION:
        raise ValueError("protocol NumPy runtime does not match the entropy sealer")
    expected_bank_design = {
        "calibration_contexts": CONTEXTS_PER_SPLIT,
        "evaluation_contexts": CONTEXTS_PER_SPLIT,
        "calibration_prefixes": PATHS_PER_SPLIT,
        "evaluation_prefixes": PATHS_PER_SPLIT,
        "prefix_length": PRIMARY_PATH_DEPTH,
        "entropy_available_before_design_commit": False,
        "calibration_evaluation_disjoint": True,
        "prior_bank_exclusion_required": True,
    }
    if protocol.get("fresh_bank_design") != expected_bank_design:
        raise ValueError("protocol fresh-bank design is not the frozen sealer contract")


def validate_design_commit(
    design_commit_path: Path,
    *,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Validate the exact commit and every local artifact it freezes."""

    design, raw, resolved = _read_exact_json(design_commit_path, label="design commit")
    if design.get("schema") != DESIGN_SCHEMA:
        raise ValueError("design-commit schema mismatch")
    if design.get("version") != VERSION:
        raise ValueError("design-commit version mismatch")
    if design.get("status") != DESIGN_STATUS:
        raise ValueError("design commit is not frozen before production entropy")
    if design.get("production_entropy_present") is not False:
        raise ValueError("design commit must state production_entropy_present=false")
    if design.get("numpy_version") != NUMPY_VERSION:
        raise ValueError(
            f"design commit must freeze the executing NumPy version {NUMPY_VERSION}"
        )

    expected_fields = DESIGN_METADATA_FIELDS | set(DESIGN_FILE_MAP)
    if set(design) != expected_fields:
        missing = sorted(expected_fields - set(design))
        unexpected = sorted(set(design) - expected_fields)
        raise ValueError(
            "design commit fields differ from the frozen contract: "
            f"missing={missing}, unexpected={unexpected}"
        )
    root = Path(project_root) if project_root is not None else resolved.parent.parent
    root = _assert_directory_chain_has_no_symlink(root)
    checked: dict[str, dict[str, Any]] = {}
    for field, parts in DESIGN_FILE_MAP.items():
        expected = design[field]
        if not _is_hex_digest(expected):
            raise ValueError(f"design commit {field} is not a lowercase SHA-256 digest")
        artifact = _assert_regular_file(root.joinpath(*parts), label=field)
        observed = sha256_file(artifact)
        if observed != expected:
            raise ValueError(f"design commit hash mismatch for {field}")
        checked[field] = {
            "relative_path": "/".join(parts),
            "sha256": observed,
            "bytes": artifact.stat().st_size,
        }
    freeze_receipt = root / "prospective" / "FROZEN_PROTOCOL.sha256"
    freeze_tokens = freeze_receipt.read_text(encoding="utf-8").strip().split()
    if (
        len(freeze_tokens) != 2
        or freeze_tokens[0] != design["protocol_sha256"]
        or freeze_tokens[1] != "PROTOCOL.json"
    ):
        raise ValueError("frozen protocol receipt does not bind the committed protocol")
    protocol, protocol_raw, _ = _read_exact_json(
        root / "prospective" / "PROTOCOL.json",
        label="frozen protocol",
    )
    if sha256_bytes(protocol_raw) != design["protocol_sha256"]:
        raise ValueError("frozen protocol bytes differ from the design commit")
    validate_protocol_for_entropy_draw(protocol)
    expected_protocol_receipts = {
        field: design[field] for field in PROTOCOL_IMPLEMENTATION_FIELDS
    }
    if protocol.get("implementation_receipts") != expected_protocol_receipts:
        raise ValueError("protocol implementation receipts differ from the design commit")
    if protocol.get("preflight") != {
        "sha256": design["parameter_preflight_sha256"],
        "evaluation_bank_generated_or_opened": False,
    }:
        raise ValueError("protocol preflight receipt differs from the design commit")
    if protocol.get("synthetic_tests") != {
        "sha256": design["synthetic_tests_sha256"]
    }:
        raise ValueError("protocol synthetic-test receipt differs from the design commit")
    if protocol.get("scientific_boundaries") != {
        "sha256": design["scientific_boundaries_sha256"]
    }:
        raise ValueError("protocol scientific-boundary receipt differs from the design commit")
    if protocol.get("lineage", {}).get("parent_release_sha256") != design[
        "parent_release_sha256"
    ]:
        raise ValueError("protocol parent lineage differs from the design commit")

    preflight, _, _ = _read_exact_json(
        root / "preflight" / "PREFLIGHT.json",
        label="parameter preflight",
    )
    if (
        preflight.get("schema")
        != "komorebi.neuralese.semantic_retraction.parameter_preflight.v1"
        or preflight.get("version") != VERSION
        or preflight.get("status") != "PASS"
        or preflight.get("preflight_integrity_pass") is not True
        or preflight.get("projection_diagnostic_is_nonblocking_for_core_factorial")
        is not True
        or preflight.get("evaluation_bank_generated_or_opened") is not False
        or preflight.get("behavioral_rollout_generated") is not False
        or preflight.get("prior_v0.4_evaluation_bank_opened") is not False
        or preflight.get("runner_sha256") != design["factorial_runner_sha256"]
    ):
        raise ValueError("parameter preflight is not the frozen bank-free PASS receipt")

    synthetic, _, _ = _read_exact_json(
        root / "preflight" / "SYNTHETIC_TESTS.json",
        label="synthetic tests",
    )
    expected_synthetic_receipts = {
        field: design[field] for field in SYNTHETIC_IMPLEMENTATION_FIELDS
    }
    if (
        synthetic.get("schema")
        != "komorebi.neuralese.semantic_retraction.synthetic_tests.v1"
        or synthetic.get("version") != VERSION
        or synthetic.get("status") != "PASS"
        or synthetic.get("learned_checkpoint_opened") is not False
        or synthetic.get("production_bank_generated_or_opened") is not False
        or synthetic.get("checkpoint_free_unit_tests", {}).get("status") != "PASS"
        or synthetic.get("full_shape_synthetic_checkpoint", {}).get("status") != "PASS"
        or synthetic.get("full_shape_synthetic_checkpoint", {}).get(
            "packed_evidence_recomputation"
        )
        != "PASS"
        or synthetic.get("full_shape_synthetic_checkpoint", {}).get(
            "learned_checkpoint_opened"
        )
        is not False
        or synthetic.get("full_shape_synthetic_checkpoint", {}).get(
            "production_entropy_used"
        )
        is not False
        or synthetic.get("implementation_receipts")
        != expected_synthetic_receipts
    ):
        raise ValueError("synthetic-test receipt is not the frozen checkpoint-free PASS receipt")
    # The implementation performing the entropy draw must itself be the exact
    # bytes frozen by the commit.  A relocated byte-identical copy is allowed;
    # stale or substituted executable bytes are not.
    executing_bindings = {
        "fresh_bank_implementation_sha256": Path(__file__).resolve(strict=True),
        "fresh_bank_test_sha256": (HERE / "test_fresh_bank.py").resolve(strict=True),
    }
    for field, executing_path in executing_bindings.items():
        if sha256_file(executing_path) != design[field]:
            raise ValueError(f"executing source does not match design commit: {field}")
    return {
        "document": design,
        "bytes": raw,
        "path": resolved,
        "sha256": sha256_bytes(raw),
        "artifacts": checked,
        "project_root": root,
    }


def _assert_fixed_production_targets(
    design_result: Mapping[str, Any],
    *,
    bank_path: Path,
    draw_receipt_path: Path,
    seal_receipt_path: Path,
) -> None:
    """Bind the one-draw state to one fixed location in the frozen project."""

    prospective = Path(design_result["project_root"]) / "prospective"
    expected = (
        prospective / "FRESH_BANK.json",
        prospective / "FRESH_BANK_DRAW_RECEIPT.json",
        prospective / "FRESH_BANK_SEAL.json",
    )
    observed = (Path(bank_path), Path(draw_receipt_path), Path(seal_receipt_path))
    if observed != expected:
        raise ValueError(
            "fresh-bank production paths are fixed by the project; alternate paths cannot redraw"
        )


def _assert_fixed_provenance_paths(
    design_result: Mapping[str, Any],
    *,
    registry_path: Path,
) -> None:
    root = Path(design_result["project_root"])
    expected_design = root / "prospective" / "DESIGN_COMMIT.json"
    expected_registry = root / "lineage" / "SPENT_BANK_REGISTRY.json"
    if Path(design_result["path"]) != expected_design:
        raise ValueError("design commit must occupy its fixed project path")
    if Path(registry_path) != expected_registry:
        raise ValueError("spent-bank registry must occupy its fixed project path")


def hkdf_sha256(root_entropy: bytes, domain: str, length: int = 32) -> bytes:
    """Derive bytes with an explicit domain under a fixed HKDF-SHA256 suite."""

    if not isinstance(root_entropy, bytes) or len(root_entropy) != 32:
        raise ValueError("root entropy must contain exactly 32 bytes")
    if not isinstance(domain, str) or not domain or "\x00" in domain:
        raise ValueError("KDF domain must be a nonempty NUL-free string")
    if length < 1 or length > 255 * hashlib.sha256().digest_size:
        raise ValueError("invalid HKDF output length")
    info = KDF_INFO_PREFIX + domain.encode("utf-8")
    pseudorandom_key = hmac.new(KDF_SALT, root_entropy, hashlib.sha256).digest()
    output = bytearray()
    previous = b""
    counter = 1
    while len(output) < length:
        previous = hmac.new(
            pseudorandom_key,
            previous + info + bytes((counter,)),
            hashlib.sha256,
        ).digest()
        output.extend(previous)
        counter += 1
    return bytes(output[:length])


def rng_for_domain(root_entropy: bytes, domain: str) -> tuple[np.random.Generator, str]:
    seed_bytes = hkdf_sha256(root_entropy, domain, 32)
    seed = int.from_bytes(seed_bytes, "big", signed=False)
    return np.random.Generator(np.random.PCG64(seed)), seed_bytes.hex()


def canonical_d4_maps() -> np.ndarray:
    rotation = np.asarray(
        [4 * (index // 4) + ((index % 4 + 1) % 4) for index in range(N_STATES)],
        dtype=np.int64,
    )
    reflection = np.asarray(
        [4 * (1 - index // 4) + (-(index % 4) % 4) for index in range(N_STATES)],
        dtype=np.int64,
    )
    return np.stack((rotation, reflection), axis=0)


def state_map_for_word(word: Sequence[int]) -> np.ndarray:
    maps = canonical_d4_maps()
    current = np.arange(N_STATES, dtype=np.int64)
    for action in word:
        if int(action) not in (0, 1):
            raise ValueError("canonical D4 words may contain only 0 and 1")
        current = maps[int(action), current]
    return current


def path_word_sha256(word: Sequence[int]) -> str:
    """Hash the registry's exact canonical JSON-list representation."""

    payload = json.dumps(
        [int(symbol) for symbol in word],
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256_bytes(payload)


def maximum_symbol_run(word: Sequence[int]) -> int:
    if not word:
        return 0
    maximum = 1
    current = 1
    for left, right in zip(word, word[1:]):
        if int(left) == int(right):
            current += 1
            maximum = max(maximum, current)
        else:
            current = 1
    return maximum


def _tensor_receipt(value: np.ndarray) -> dict[str, Any]:
    source = np.asarray(value)
    storage_dtype_by_kind = {
        ("f", 4): np.dtype("<f4"),
        ("i", 8): np.dtype("<i8"),
    }
    try:
        storage_dtype = storage_dtype_by_kind[(source.dtype.kind, source.dtype.itemsize)]
    except KeyError as exc:
        raise ValueError(f"unsupported sealed tensor dtype: {source.dtype}") from exc
    array = np.ascontiguousarray(source, dtype=storage_dtype)
    return {
        "dtype": storage_dtype.str,
        "shape": list(array.shape),
        "sha256": sha256_bytes(array.tobytes(order="C")),
    }


def _context_candidate(rng: np.random.Generator) -> dict[str, np.ndarray]:
    phi = np.argsort(rng.random(N_STATES), kind="stable").astype(np.int64)
    inverse = np.argsort(phi, kind="stable")
    canonical = canonical_d4_maps()
    canonical_maps = np.empty((N_OPERATORS, N_STATES), dtype=np.int64)
    for operator in range(N_OPERATORS):
        canonical_target = canonical[operator][inverse]
        canonical_maps[operator] = np.take_along_axis(phi, canonical_target, axis=0)
    swap = int(rng.integers(0, 2, dtype=np.int64))
    maps = canonical_maps[[swap, 1 - swap]].astype(np.int64, copy=False)
    canonical_to_slot = np.asarray((swap, 1 - swap), dtype=np.int64)
    tables = np.eye(N_STATES, dtype=np.float32)[maps]
    return {
        "tables": np.ascontiguousarray(tables, dtype=np.float32),
        "maps": np.ascontiguousarray(maps, dtype=np.int64),
        "phi": np.ascontiguousarray(phi, dtype=np.int64),
        "canonical_to_slot": np.ascontiguousarray(canonical_to_slot, dtype=np.int64),
    }


def context_key(context: Mapping[str, np.ndarray]) -> str:
    # The historical registry was produced on little-endian hardware.  Freeze
    # that storage order explicitly so exclusion keys remain portable.
    tables = np.ascontiguousarray(context["tables"], dtype=np.dtype("<f4"))
    slots = np.ascontiguousarray(context["canonical_to_slot"], dtype=np.dtype("<i8"))
    return sha256_bytes(tables.tobytes(order="C") + slots.tobytes(order="C"))


def generate_context_bank(
    root_entropy: bytes,
    *,
    split: str,
    forbidden_keys: Iterable[str],
    count: int = CONTEXTS_PER_SPLIT,
) -> dict[str, Any]:
    if split not in {"calibration", "evaluation"}:
        raise ValueError("context split must be calibration or evaluation")
    if count != CONTEXTS_PER_SPLIT:
        raise ValueError(f"v0.3 requires exactly {CONTEXTS_PER_SPLIT} contexts per split")
    forbidden = set(forbidden_keys)
    if not all(_is_hex_digest(value) for value in forbidden):
        raise ValueError("forbidden context keys contain a malformed digest")
    rng, seed_hex = rng_for_domain(root_entropy, f"context/{split}")
    retained: list[dict[str, np.ndarray]] = []
    keys: list[str] = []
    observed = set(forbidden)
    draws = 0
    rejected_prior = 0
    rejected_duplicate = 0
    while len(retained) < count:
        if draws >= 1_000_000:
            raise RuntimeError(f"could not create the frozen {split} context bank")
        candidate = _context_candidate(rng)
        key = context_key(candidate)
        draws += 1
        if key in observed:
            if key in forbidden:
                rejected_prior += 1
            else:
                rejected_duplicate += 1
            continue
        observed.add(key)
        keys.append(key)
        retained.append(candidate)

    stacked = {
        name: np.stack([row[name] for row in retained], axis=0)
        for name in ("tables", "maps", "phi", "canonical_to_slot")
    }
    contexts = []
    for index, (key, row) in enumerate(zip(keys, retained)):
        contexts.append(
            {
                "index": index,
                "context_key": key,
                "tables": row["tables"].astype(int).tolist(),
                "maps": row["maps"].tolist(),
                "phi": row["phi"].tolist(),
                "canonical_to_slot": row["canonical_to_slot"].tolist(),
                "tensor_receipts": {
                    name: _tensor_receipt(row[name])
                    for name in ("tables", "maps", "phi", "canonical_to_slot")
                },
            }
        )
    core = {
        "split": split,
        "domain": f"context/{split}",
        "derived_seed_hex": seed_hex,
        "rng": RNG_DESCRIPTION,
        "family": "d4",
        "count": count,
        "draw_count": draws,
        "rejections": {
            "forbidden": rejected_prior,
            "within_split_duplicate": rejected_duplicate,
        },
        "context_key_rule": (
            "sha256(float32 tables row C-bytes || int64 canonical_to_slot row C-bytes)"
        ),
        "context_keys": keys,
        "stacked_tensor_receipts": {
            name: _tensor_receipt(array) for name, array in stacked.items()
        },
        "contexts": contexts,
    }
    return {**core, "receipt_sha256": canonical_json_digest(core)}


def generate_identity_path_bank(
    root_entropy: bytes,
    *,
    split: str,
    forbidden_hashes: Iterable[str],
    count: int = PATHS_PER_SPLIT,
    depth: int = PRIMARY_PATH_DEPTH,
) -> dict[str, Any]:
    if split not in {"calibration", "evaluation"}:
        raise ValueError("path split must be calibration or evaluation")
    if count != PATHS_PER_SPLIT:
        raise ValueError(f"v0.3 freezes exactly {PATHS_PER_SPLIT} paths per split")
    if depth != PRIMARY_PATH_DEPTH:
        raise ValueError(f"v0.3 primary paths must have exact depth {PRIMARY_PATH_DEPTH}")
    forbidden = set(forbidden_hashes)
    if not all(_is_hex_digest(value) for value in forbidden):
        raise ValueError("forbidden path hashes contain a malformed digest")
    rng, seed_hex = rng_for_domain(root_entropy, f"path/{split}")
    identity = np.arange(N_STATES, dtype=np.int64)
    observed = set(forbidden)
    records: list[dict[str, Any]] = []
    draws = 0
    rejected_forbidden = 0
    rejected_duplicate = 0
    rejected_histogram = 0
    rejected_nonidentity = 0
    while len(records) < count:
        if draws >= 1_000_000:
            raise RuntimeError(f"could not create the frozen {split} identity-path bank")
        word_array = rng.integers(0, 2, size=depth, dtype=np.uint8)
        word = tuple(int(value) for value in word_array)
        digest = path_word_sha256(word)
        draws += 1
        if digest in observed:
            if digest in forbidden:
                rejected_forbidden += 1
            else:
                rejected_duplicate += 1
            continue
        number_r = int(np.count_nonzero(word_array == 0))
        number_f = depth - number_r
        if number_r != number_f:
            rejected_histogram += 1
            continue
        full_map = state_map_for_word(word)
        if not np.array_equal(full_map, identity):
            rejected_nonidentity += 1
            continue
        observed.add(digest)
        records.append(
            {
                "index": len(records),
                "word": list(word),
                "word_sha256": digest,
                "exact_length": depth,
                "generator_histogram": {"r": number_r, "f": number_f},
                "maximum_symbol_run": maximum_symbol_run(word),
                "full_state_map": full_map.tolist(),
                "identity_on_all_eight_starts": True,
            }
        )
    core = {
        "split": split,
        "domain": f"path/{split}",
        "derived_seed_hex": seed_hex,
        "rng": RNG_DESCRIPTION,
        "family": "d4",
        "count": count,
        "exact_depth": depth,
        "semantic_endpoint": "identity",
        "balanced_generator_histogram": {"r": depth // 2, "f": depth // 2},
        "word_hash_rule": "sha256(canonical JSON list bytes; separators=(',',':'); no newline)",
        "draw_count": draws,
        "rejections": {
            "forbidden": rejected_forbidden,
            "within_split_duplicate": rejected_duplicate,
            "unbalanced_generator_histogram": rejected_histogram,
            "nonidentity_action": rejected_nonidentity,
        },
        "word_sha256": [record["word_sha256"] for record in records],
        "paths": records,
    }
    return {**core, "receipt_sha256": canonical_json_digest(core)}


def build_bank_document(
    root_entropy: bytes,
    *,
    design_commit_sha256: str,
    registry: Mapping[str, Any],
    registry_sha256: str,
    draw_receipt_sha256: str,
) -> dict[str, Any]:
    """Deterministically build both splits from one already-drawn root."""

    if not all(
        _is_hex_digest(value)
        for value in (design_commit_sha256, registry_sha256, draw_receipt_sha256)
    ):
        raise ValueError("bank provenance contains a malformed SHA-256 digest")
    exclusions = validate_registry_document(registry)
    prior_contexts = set(exclusions["forbidden_context_keys"])
    prior_paths = set(exclusions["forbidden_path_word_sha256"])

    calibration_contexts = generate_context_bank(
        root_entropy,
        split="calibration",
        forbidden_keys=prior_contexts,
    )
    evaluation_contexts = generate_context_bank(
        root_entropy,
        split="evaluation",
        forbidden_keys=prior_contexts | set(calibration_contexts["context_keys"]),
    )
    calibration_paths = generate_identity_path_bank(
        root_entropy,
        split="calibration",
        forbidden_hashes=prior_paths,
    )
    evaluation_paths = generate_identity_path_bank(
        root_entropy,
        split="evaluation",
        forbidden_hashes=prior_paths | set(calibration_paths["word_sha256"]),
    )

    calibration_context_keys = set(calibration_contexts["context_keys"])
    evaluation_context_keys = set(evaluation_contexts["context_keys"])
    calibration_path_hashes = set(calibration_paths["word_sha256"])
    evaluation_path_hashes = set(evaluation_paths["word_sha256"])
    audits = {
        "calibration_evaluation_context_intersection": sorted(
            calibration_context_keys & evaluation_context_keys
        ),
        "new_prior_context_intersection": sorted(
            (calibration_context_keys | evaluation_context_keys) & prior_contexts
        ),
        "calibration_evaluation_path_intersection": sorted(
            calibration_path_hashes & evaluation_path_hashes
        ),
        "new_prior_path_intersection": sorted(
            (calibration_path_hashes | evaluation_path_hashes) & prior_paths
        ),
    }
    if any(audits.values()):
        raise RuntimeError("fresh-bank exact disjointness audit failed")

    payload = {
        "author": AUTHOR,
        "version": VERSION,
        "design_commit_sha256": design_commit_sha256,
        "spent_bank_registry": {
            "schema": REGISTRY_SCHEMA,
            "status": REGISTRY_STATUS,
            "sha256": registry_sha256,
            "forbidden_context_key_count": len(prior_contexts),
            "forbidden_path_word_sha256_count": len(prior_paths),
        },
        "draw_receipt_sha256": draw_receipt_sha256,
        "root_entropy": {
            "source": "os.urandom(32)",
            "bytes": len(root_entropy),
            "hex": root_entropy.hex(),
            "sha256": sha256_bytes(root_entropy),
            "sampled_only_after_design_commit_validation": True,
        },
        "derivation": {
            "kdf": KDF_DESCRIPTION,
            "rng": RNG_DESCRIPTION,
            "numpy_version": NUMPY_VERSION,
            "portability_contract": (
                "exact root regeneration requires the sealed NumPy version; emitted arrays and hashes "
                "remain independently auditable"
            ),
            "domains": [
                "context/calibration",
                "context/evaluation",
                "path/calibration",
                "path/evaluation",
            ],
        },
        "splits": {
            "calibration": {
                "permitted_use": "prototype construction and calibration only",
                "context_bank": calibration_contexts,
                "identity_path_bank": calibration_paths,
            },
            "evaluation": {
                "permitted_use": "terminal preregistered scoring only",
                "context_bank": evaluation_contexts,
                "identity_path_bank": evaluation_paths,
            },
        },
        "exact_disjointness": {**audits, "pass": True},
    }
    payload_sha256 = canonical_json_digest(payload)
    bank_id = sha256_bytes(
        b"komorebi.neuralese.semantic_retraction.bank_id.v1\x00"
        + canonical_json_bytes(payload)
    )
    return {
        "schema": BANK_SCHEMA,
        "version": VERSION,
        "status": BANK_STATUS,
        "bank_id": bank_id,
        "payload_sha256": payload_sha256,
        "payload": payload,
    }


def _draw_receipt_document(
    root_entropy: bytes,
    *,
    design_commit_sha256: str,
    registry_sha256: str,
    bank_filename: str,
) -> dict[str, Any]:
    return {
        "schema": DRAW_SCHEMA,
        "version": VERSION,
        "status": DRAW_STATUS,
        "design_commit_sha256": design_commit_sha256,
        "spent_bank_registry_sha256": registry_sha256,
        "bank_filename": bank_filename,
        "entropy_source": "os.urandom(32)",
        "numpy_version": NUMPY_VERSION,
        "root_entropy_hex": root_entropy.hex(),
        "root_entropy_sha256": sha256_bytes(root_entropy),
        "ordering": "design and all frozen artifact hashes validated before this sole draw",
        "redraw_permitted": False,
    }


def _seal_receipt_document(
    *,
    bank_path: Path,
    bank_bytes: bytes,
    bank_id: str,
    draw_receipt_path: Path,
    draw_receipt_bytes: bytes,
    design_commit_sha256: str,
    registry_sha256: str,
) -> dict[str, Any]:
    return {
        "schema": SEAL_SCHEMA,
        "version": VERSION,
        "status": SEAL_STATUS,
        "bank_id": bank_id,
        "bank": {
            "filename": bank_path.name,
            "bytes": len(bank_bytes),
            "sha256": sha256_bytes(bank_bytes),
        },
        "draw_receipt": {
            "filename": draw_receipt_path.name,
            "bytes": len(draw_receipt_bytes),
            "sha256": sha256_bytes(draw_receipt_bytes),
        },
        "design_commit_sha256": design_commit_sha256,
        "spent_bank_registry_sha256": registry_sha256,
        "exact_canonical_json": True,
    }


def seal_fresh_bank(
    *,
    design_commit_path: Path = DEFAULT_DESIGN_COMMIT,
    registry_path: Path = DEFAULT_REGISTRY,
    bank_path: Path = DEFAULT_BANK,
    draw_receipt_path: Path = DEFAULT_DRAW_RECEIPT,
    seal_receipt_path: Path = DEFAULT_SEAL_RECEIPT,
    entropy_source: Callable[[int], bytes] = os.urandom,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Make the single permitted production draw and seal its derived banks."""

    raw_targets = [Path(bank_path), Path(draw_receipt_path), Path(seal_receipt_path)]
    # Check all targets before validating design and, most importantly, before
    # asking the operating system for entropy.
    targets = [
        _prepare_new_file(path, label=label)
        for path, label in zip(
            raw_targets,
            ("fresh bank", "draw receipt", "seal receipt"),
        )
    ]
    if len(set(targets)) != len(targets):
        raise ValueError("bank, draw receipt, and seal receipt paths must be distinct")
    bank_path, draw_receipt_path, seal_receipt_path = targets

    design_result = validate_design_commit(
        design_commit_path,
        project_root=project_root,
    )
    _assert_fixed_production_targets(
        design_result,
        bank_path=bank_path,
        draw_receipt_path=draw_receipt_path,
        seal_receipt_path=seal_receipt_path,
    )
    registry, registry_bytes, registry_resolved = _read_hashed_json(
        registry_path,
        label="spent-bank registry",
    )
    _assert_fixed_provenance_paths(
        design_result,
        registry_path=registry_resolved,
    )
    validate_registry_document(registry)
    registry_sha256 = sha256_bytes(registry_bytes)
    expected_registry_sha256 = design_result["document"]["spent_bank_registry_sha256"]
    if registry_sha256 != expected_registry_sha256:
        raise ValueError("registry file is not the registry frozen by the design commit")
    if registry["parent_release"]["sha256"] != design_result["document"]["parent_release_sha256"]:
        raise ValueError("registry and design commit disagree on the immutable parent release")

    free_bytes = int(shutil.disk_usage(Path(bank_path).parent).free)
    if free_bytes < MIN_FREE_BYTES_BEFORE_DRAW:
        raise OSError(
            f"insufficient free space before production entropy draw: "
            f"{free_bytes} < {MIN_FREE_BYTES_BEFORE_DRAW}"
        )

    # Reserve the durable no-redraw marker *before* entropy access.  O_EXCL
    # closes the otherwise subtle two-process race in which both processes
    # could draw a root before either one wrote its receipt.  A crash or bad
    # entropy source leaves this reservation in place and makes the draw
    # terminal rather than silently permitting replacement.
    draw_descriptor = _reserve_new_file(Path(draw_receipt_path), label="draw receipt")
    try:
        # There is exactly one entropy call, after design, artifact, registry,
        # path, and exclusive no-redraw checks have all passed.
        root_entropy = entropy_source(32)
        if not isinstance(root_entropy, bytes) or len(root_entropy) != 32:
            raise RuntimeError("OS entropy source did not return exactly 32 bytes")
        draw_document = _draw_receipt_document(
            root_entropy,
            design_commit_sha256=design_result["sha256"],
            registry_sha256=registry_sha256,
            bank_filename=Path(bank_path).name,
        )
        draw_bytes = canonical_json_bytes(draw_document)
        # Ownership passes to fdopen inside _write_reserved_file.  Clear the
        # outer sentinel first so a flush/fsync exception cannot double-close
        # the descriptor and mask the original durability failure.
        owned_descriptor = draw_descriptor
        draw_descriptor = -1
        _write_reserved_file(owned_descriptor, draw_bytes)
    finally:
        if draw_descriptor >= 0:
            os.close(draw_descriptor)

    bank = build_bank_document(
        root_entropy,
        design_commit_sha256=design_result["sha256"],
        registry=registry,
        registry_sha256=registry_sha256,
        draw_receipt_sha256=sha256_bytes(draw_bytes),
    )
    bank_bytes = canonical_json_bytes(bank)
    _exclusive_write(Path(bank_path), bank_bytes, label="fresh bank")

    seal = _seal_receipt_document(
        bank_path=Path(bank_path),
        bank_bytes=bank_bytes,
        bank_id=bank["bank_id"],
        draw_receipt_path=Path(draw_receipt_path),
        draw_receipt_bytes=draw_bytes,
        design_commit_sha256=design_result["sha256"],
        registry_sha256=registry_sha256,
    )
    seal_bytes = canonical_json_bytes(seal)
    _exclusive_write(Path(seal_receipt_path), seal_bytes, label="seal receipt")
    return {
        "status": SEAL_STATUS,
        "bank_id": bank["bank_id"],
        "bank_sha256": sha256_bytes(bank_bytes),
        "draw_receipt_sha256": sha256_bytes(draw_bytes),
        "seal_receipt_sha256": sha256_bytes(seal_bytes),
    }


def verify_fresh_bank(
    *,
    design_commit_path: Path = DEFAULT_DESIGN_COMMIT,
    registry_path: Path = DEFAULT_REGISTRY,
    bank_path: Path = DEFAULT_BANK,
    draw_receipt_path: Path = DEFAULT_DRAW_RECEIPT,
    seal_receipt_path: Path = DEFAULT_SEAL_RECEIPT,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Read-only exact verification; this path never draws entropy or writes."""

    design_result = validate_design_commit(design_commit_path, project_root=project_root)
    observed_paths = tuple(
        _assert_regular_file(path, label=label)
        for path, label in (
            (bank_path, "fresh bank"),
            (draw_receipt_path, "draw receipt"),
            (seal_receipt_path, "seal receipt"),
        )
    )
    _assert_fixed_production_targets(
        design_result,
        bank_path=observed_paths[0],
        draw_receipt_path=observed_paths[1],
        seal_receipt_path=observed_paths[2],
    )
    registry, registry_bytes, registry_resolved = _read_hashed_json(
        registry_path,
        label="spent-bank registry",
    )
    _assert_fixed_provenance_paths(
        design_result,
        registry_path=registry_resolved,
    )
    validate_registry_document(registry)
    registry_sha256 = sha256_bytes(registry_bytes)
    if registry_sha256 != design_result["document"]["spent_bank_registry_sha256"]:
        raise ValueError("registry does not match design commit")
    if registry["parent_release"]["sha256"] != design_result["document"]["parent_release_sha256"]:
        raise ValueError("registry and design commit disagree on the immutable parent release")
    draw, draw_bytes, _ = _read_exact_json(draw_receipt_path, label="draw receipt")
    bank, bank_bytes, _ = _read_exact_json(bank_path, label="fresh bank")
    seal, seal_bytes, _ = _read_exact_json(seal_receipt_path, label="seal receipt")

    if draw.get("schema") != DRAW_SCHEMA or draw.get("status") != DRAW_STATUS:
        raise ValueError("draw receipt schema/status mismatch")
    if draw.get("redraw_permitted") is not False:
        raise ValueError("draw receipt does not prohibit redraw")
    root_hex = draw.get("root_entropy_hex")
    if not isinstance(root_hex, str):
        raise ValueError("draw receipt lacks root entropy")
    try:
        root_entropy = bytes.fromhex(root_hex)
    except ValueError as exc:
        raise ValueError("draw receipt root entropy is malformed") from exc
    if len(root_entropy) != 32 or sha256_bytes(root_entropy) != draw.get("root_entropy_sha256"):
        raise ValueError("draw receipt entropy hash mismatch")
    if draw.get("design_commit_sha256") != design_result["sha256"]:
        raise ValueError("draw receipt design hash mismatch")
    if draw.get("spent_bank_registry_sha256") != registry_sha256:
        raise ValueError("draw receipt registry hash mismatch")
    expected_draw = _draw_receipt_document(
        root_entropy,
        design_commit_sha256=design_result["sha256"],
        registry_sha256=registry_sha256,
        bank_filename=Path(bank_path).name,
    )
    if draw != expected_draw or draw_bytes != canonical_json_bytes(expected_draw):
        raise ValueError("draw receipt does not exactly match its frozen schema and provenance")

    expected_bank = build_bank_document(
        root_entropy,
        design_commit_sha256=design_result["sha256"],
        registry=registry,
        registry_sha256=registry_sha256,
        draw_receipt_sha256=sha256_bytes(draw_bytes),
    )
    if bank != expected_bank or bank_bytes != canonical_json_bytes(expected_bank):
        raise ValueError("fresh bank does not exactly regenerate from its sealed root")
    if bank.get("schema") != BANK_SCHEMA or bank.get("status") != BANK_STATUS:
        raise ValueError("fresh bank schema/status mismatch")

    expected_seal = _seal_receipt_document(
        bank_path=Path(bank_path),
        bank_bytes=bank_bytes,
        bank_id=bank["bank_id"],
        draw_receipt_path=Path(draw_receipt_path),
        draw_receipt_bytes=draw_bytes,
        design_commit_sha256=design_result["sha256"],
        registry_sha256=registry_sha256,
    )
    if seal != expected_seal or seal_bytes != canonical_json_bytes(expected_seal):
        raise ValueError("seal receipt does not exactly match bank and provenance")
    return {
        "status": "VERIFIED_READ_ONLY",
        "bank_id": bank["bank_id"],
        "bank_sha256": sha256_bytes(bank_bytes),
        "draw_receipt_sha256": sha256_bytes(draw_bytes),
        "seal_receipt_sha256": sha256_bytes(seal_bytes),
        "context_count_per_split": CONTEXTS_PER_SPLIT,
        "identity_path_count_per_split": PATHS_PER_SPLIT,
        "primary_path_depth": PRIMARY_PATH_DEPTH,
        "exact_disjointness": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("seal", "verify"):
        child = subparsers.add_parser(command)
        child.add_argument("--design-commit", type=Path, default=DEFAULT_DESIGN_COMMIT)
        child.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
        child.add_argument("--bank", type=Path, default=DEFAULT_BANK)
        child.add_argument("--draw-receipt", type=Path, default=DEFAULT_DRAW_RECEIPT)
        child.add_argument("--seal-receipt", type=Path, default=DEFAULT_SEAL_RECEIPT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    keywords = {
        "design_commit_path": arguments.design_commit,
        "registry_path": arguments.registry,
        "bank_path": arguments.bank,
        "draw_receipt_path": arguments.draw_receipt,
        "seal_receipt_path": arguments.seal_receipt,
    }
    if arguments.command == "seal":
        result = seal_fresh_bank(**keywords)
    else:
        result = verify_fresh_bank(**keywords)
    sys.stdout.write(canonical_json_bytes(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
