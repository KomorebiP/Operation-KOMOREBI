#!/usr/bin/env python3
"""Build the inert v0.3 exclusion registry from the immutable v0.2 release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


PARENT_SHA256 = "dc380967c8ee0aa5bd039fe9d9765b21d22ce534044e4df304962fb691cbf4e6"
PARENT_BYTES = 2_338_597
PARENT_PREFIX = "neuralese_semantic_retraction_v0.2.0"
PRIMARY_MANIFEST_SHA256 = "5feaba6abc4ba70f44e027f4f8675f81726e24b5ae96b41f7fb6ce35752d20e8"
PRIMARY_SPEND_SHA256 = "65b399852d338569e4775bbbe7177a94094619d8acd70f8c72017e79843f9c01"
NULL_CONTEXTS = 64
NULL_SEED_BASE = 530_000
N_STATES = 8


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def path_digest(word: Sequence[int]) -> str:
    return sha256_bytes(canonical_json_bytes([int(symbol) for symbol in word]))


def derive_seed(base: int, *parts: object) -> int:
    return int.from_bytes(
        hashlib.sha256(canonical_json_bytes([int(base), *parts])).digest()[:8],
        "little",
    ) % (2**31 - 1)


def canonical_d4_maps() -> np.ndarray:
    rotation = np.array(
        [4 * (index // 4) + ((index % 4 + 1) % 4) for index in range(N_STATES)],
        dtype=np.int64,
    )
    reflection = np.array(
        [4 * (1 - index // 4) + ((-(index % 4)) % 4) for index in range(N_STATES)],
        dtype=np.int64,
    )
    return np.stack((rotation, reflection), axis=0)


def old_null_context_keys() -> list[str]:
    rng = np.random.default_rng(derive_seed(NULL_SEED_BASE, "null"))
    phi = np.argsort(rng.random((NULL_CONTEXTS, N_STATES)), axis=1).astype(np.int64)
    inverse = np.argsort(phi, axis=1)
    canonical = canonical_d4_maps()
    canonical_maps = np.empty((NULL_CONTEXTS, 2, N_STATES), dtype=np.int64)
    for operator in range(2):
        target = canonical[operator][inverse]
        canonical_maps[:, operator] = np.take_along_axis(phi, target, axis=1)
    swap = rng.integers(0, 2, size=NULL_CONTEXTS, dtype=np.int64)
    maps = np.empty_like(canonical_maps)
    maps[:, 0] = np.where(
        swap[:, None].astype(bool), canonical_maps[:, 1], canonical_maps[:, 0]
    )
    maps[:, 1] = np.where(
        swap[:, None].astype(bool), canonical_maps[:, 0], canonical_maps[:, 1]
    )
    canonical_to_slot = np.stack((swap, 1 - swap), axis=1)
    tables = np.eye(N_STATES, dtype=np.float32)[maps]
    return [
        sha256_bytes(
            np.ascontiguousarray(tables[index]).tobytes()
            + np.ascontiguousarray(canonical_to_slot[index]).tobytes()
        )
        for index in range(NULL_CONTEXTS)
    ]


def primary_path_words(manifest: dict[str, Any]) -> Iterable[tuple[str, Sequence[int]]]:
    for split in ("calibration", "evaluation"):
        for pair in manifest["path_manifests"][split]["pairs"]:
            yield f"v0.2_primary_{split}", pair["word_a"]
            yield f"v0.2_primary_{split}", pair["word_b"]
    for word in manifest["path_manifests"]["stress"]["words"]:
        if isinstance(word, dict):
            selected = word.get("word")
            if selected is None:
                raise ValueError("unrecognized primary stress-word record")
            yield "v0.2_primary_stress", selected
        else:
            yield "v0.2_primary_stress", word


def publish_exclusive(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite registry: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload, indent=2, sort_keys=True, allow_nan=False
    ).encode("utf-8") + b"\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path, follow_symlinks=False)
        directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    parent = arguments.parent.resolve(strict=True)
    if parent.stat().st_size != PARENT_BYTES or sha256_file(parent) != PARENT_SHA256:
        raise RuntimeError("immutable v0.2 parent release mismatch")

    with zipfile.ZipFile(parent) as archive:
        manifest_bytes = archive.read(
            f"{PARENT_PREFIX}/primary_probe/MANIFEST_DRY_RUN.json"
        )
        spend_bytes = archive.read(
            f"{PARENT_PREFIX}/primary_probe/EVALUATION_BANK_SPENT.json"
        )
    if sha256_bytes(manifest_bytes) != PRIMARY_MANIFEST_SHA256:
        raise RuntimeError("v0.2 primary manifest mismatch")
    if sha256_bytes(spend_bytes) != PRIMARY_SPEND_SHA256:
        raise RuntimeError("v0.2 spend receipt mismatch")
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    spend = json.loads(spend_bytes.decode("utf-8"))

    primary_context_keys: list[str] = []
    context_sources: dict[str, int] = {}
    for split in ("prior", "calibration", "evaluation"):
        keys = [str(value) for value in manifest["context_manifests"][split]["context_keys"]]
        primary_context_keys.extend(keys)
        context_sources[f"v0.2_primary_{split}"] = len(keys)
    null_keys = old_null_context_keys()
    context_sources["v0.2_independent_null"] = len(null_keys)
    all_context_keys = sorted(set(primary_context_keys + null_keys))

    path_records: list[dict[str, object]] = []
    for source, word in primary_path_words(manifest):
        normalized = [int(symbol) for symbol in word]
        path_records.append(
            {
                "source": source,
                "length": len(normalized),
                "sha256": path_digest(normalized),
            }
        )
    independent_words = {
        "v0.2_independent_r4_x16": [0, 0, 0, 0] * 16,
        "v0.2_independent_f2_x16": [1, 1] * 16,
        "v0.2_independent_frfr_x16": [1, 0, 1, 0] * 16,
    }
    for source, word in independent_words.items():
        path_records.append(
            {"source": source, "length": len(word), "sha256": path_digest(word)}
        )
    all_path_hashes = sorted({str(record["sha256"]) for record in path_records})

    payload = {
        "schema": "komorebi.neuralese.semantic_retraction.spent_bank_registry.v1",
        "version": "0.3.0",
        "author": "Komorebi P.",
        "status": "IMMUTABLE_PRIOR_BANK_EXCLUSIONS",
        "context_key_definition": "sha256(float32 D4 tables C-bytes || int64 canonical_to_slot C-bytes)",
        "path_word_sha256_definition": "sha256(canonical compact JSON integer word)",
        "parent_release": {
            "file": parent.name,
            "bytes": PARENT_BYTES,
            "sha256": PARENT_SHA256,
            "primary_status": "ABORTED_INVALID_NO_COMMIT",
            "primary_spend_receipt_file_sha256": PRIMARY_SPEND_SHA256,
            "spent_context_bank_sha256": spend["evaluation_context_sha256"],
            "spent_path_bank_sha256": spend["evaluation_path_sha256"],
            "spent_continuation_bank_sha256": spend["continuation_sha256"],
            "spent_random_key_manifest_sha256": spend["random_key_manifest_sha256"],
        },
        "sources": {
            "context_counts_before_deduplication": context_sources,
            "path_records_before_deduplication": len(path_records),
            "v0.2_primary_manifest_sha256": PRIMARY_MANIFEST_SHA256,
        },
        "forbidden_context_keys": all_context_keys,
        "forbidden_path_word_sha256": all_path_hashes,
        "counts": {
            "unique_context_keys": len(all_context_keys),
            "unique_path_words": len(all_path_hashes),
        },
    }
    publish_exclusive(arguments.output.resolve(strict=False), payload)
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(arguments.output.resolve()),
                "sha256": sha256_file(arguments.output.resolve()),
                "counts": payload["counts"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
