#!/usr/bin/env python3
"""Checked import, publication and querying of a fixed Bool3 cost-closure library.

The candidate file is data only. Every process revalidates it using the executed
Lean checker; a stored checksum or earlier success flag never replaces checking.
Charges are per-invocation declared tariffs, not a physical-cost or payment ledger.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTORS = ["avoc-global-cost-library-v1", "bool3-not-and-or-xor-v1",
               "lexicographic-false-first-bit0", "eager-tree-nodes-v1"]
MAX_BYTES = 2 * 1024 * 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_constants(s: str) -> None:
    raise ValueError("nonfinite JSON number: " + s)


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("duplicate JSON key: " + k)
        result[k] = v
    return result


def decode(raw: bytes) -> Any:
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                      parse_constant=reject_constants)


def read_snapshot(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("expected a regular non-symlink file")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("input exceeds two-megabyte cap")
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError("input grew beyond byte cap")
    return raw


def nat(x: Any, high: int, label: str) -> int:
    if type(x) is not int or not 0 <= x <= high:
        raise ValueError(label + " must be a bounded exact integer")
    return x


def program(p: Any, fuel: int = 64) -> int:
    if fuel <= 0 or not isinstance(p, list) or not p or not isinstance(p[0], str):
        raise ValueError("malformed or excessively nested expression")
    tag = p[0]
    if tag == "literal" and len(p) == 2 and type(p[1]) is bool:
        return 1
    if tag == "variable" and len(p) == 2:
        nat(p[1], 2, "variable")
        return 1
    arity = {"not": 1, "and": 2, "or": 2, "xor": 2}.get(tag)
    if arity is None or len(p) != arity + 1:
        raise ValueError("unsupported program constructor")
    n = 1 + sum(program(q, fuel - 1) for q in p[1:])
    if n > 4096:
        raise ValueError("expression node cap")
    return n


def certificate_shape(c: Any) -> None:
    if not isinstance(c, list) or len(c) != 5 or c[:4] != DESCRIPTORS:
        raise ValueError("incompatible certificate envelope")
    if not isinstance(c[4], list) or len(c[4]) != 256:
        raise ValueError("exactly 256 indexed rows required")
    for row in c[4]:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError("invalid certificate row")
        bits, size, p = row
        if not isinstance(bits, list) or len(bits) != 8 or any(type(x) is not bool for x in bits):
            raise ValueError("eight Boolean truth entries required")
        nat(size, 4096, "node count")
        program(p)


def verify_checker_sources() -> tuple[Path, dict[str, str]]:
    pins = decode((ROOT / "library_source_pins.json").read_bytes())
    for rel, expected in pins.items():
        f = ROOT / rel
        if not f.is_file() or sha(f.read_bytes()) != expected:
            raise ValueError("reviewed checker source changed: " + rel)
    build = ROOT / ".lake/build/lib/lean"
    visited: set[str] = set()

    def verify_module(module: str) -> None:
        if module in visited:
            return
        visited.add(module)
        src = ROOT / (module.replace(".", "/") + ".lean")
        artifact = build / (module.replace(".", "/") + ".olean")
        record = ROOT / "results/v0.27.0" / ("clean_" + src.stem + ".json")
        if not artifact.is_file() or not record.is_file():
            raise ValueError("missing fresh compilation: " + module)
        r = decode(record.read_bytes())
        if (r.get("returncode") != 0 or r.get("timed_out") or
                not r.get("imports_unchanged") or not r.get("source_unchanged") or
                r.get("source_sha256") != sha(src.read_bytes()) or
                r.get("output_sha256") != sha(artifact.read_bytes())):
            raise ValueError("stale/failed compilation: " + module)
        for dep, digest in r.get("import_outputs", {}).items():
            verify_module(dep)
            q = build / (dep.replace(".", "/") + ".olean")
            if sha(q.read_bytes()) != digest:
                raise ValueError("stale imported output: " + dep)

    verify_module("AVOC.SemanticLibraryCodec")
    kit = Path(os.environ.get("AVOC_LEAN_KIT",
               "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2")).resolve()
    lean = kit / "toolchain/bin/lean"
    if not lean.is_file():
        raise ValueError("set AVOC_LEAN_KIT to the pinned Lean kit")
    env = os.environ.copy()
    env["LEAN_PATH"] = str(build)
    return lean, env


def invoke(certificate: Any, credit: int, queries: Any, timeout: int) -> dict[str, Any]:
    certificate_shape(certificate)
    nat(credit, 10**9, "credit")
    if not isinstance(queries, list) or len(queries) > 512:
        raise ValueError("queries must be a list with at most 512 expressions")
    for p in queries:
        program(p)
    lean, env = verify_checker_sources()
    request = ["avoc-library-load-v1", certificate, credit, queries]
    with tempfile.TemporaryDirectory(prefix="avoc-library-") as tmp:
        path = Path(tmp) / "request.json"
        path.write_text(json.dumps(request, separators=(",", ":")), encoding="utf-8")
        t = time.perf_counter()
        process = subprocess.run([str(lean), "--run", str(ROOT / "tools/SemanticLibraryMain.lean"), str(path)],
                                 cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
        elapsed = time.perf_counter() - t
    if process.returncode not in (0, 2) or not process.stdout.strip():
        raise ValueError("Lean process failed: " + (process.stderr + process.stdout)[-2000:])
    result = decode(process.stdout.encode("utf-8"))
    result["process_seconds"] = elapsed
    result["checker_source_sha256"] = sha((ROOT / "AVOC/SemanticLibraryCodec.lean").read_bytes())
    return result


def write_fsynced(path: Path, raw: bytes) -> None:
    with path.open("xb") as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())


def publish(source: Path, destination: Path, credit: int, timeout: int) -> dict[str, Any]:
    # The exact bytes below are both checked and retained, even if source later changes.
    if destination.exists() or destination.is_symlink():
        raise ValueError("refusing to overwrite an existing store")
    raw = read_snapshot(source)
    result = invoke(decode(raw), credit, [], timeout)
    if result.get("status") != "globally_certified":
        result["published"] = False
        return result
    destination.mkdir(mode=0o700, parents=False, exist_ok=False)
    # READY is written last. An interrupted partial store is rejected, not auto-repaired.
    write_fsynced(destination / "library.json", raw)
    manifest = {"schema": "avoc-checked-library-store-v1", "certificate_sha256": sha(raw),
                "descriptors": DESCRIPTORS,
                "initial_validation": result,
                "claim": "global minimum tree-node witnesses for the fixed Bool3 grammar"}
    write_fsynced(destination / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    write_fsynced(destination / "READY", b"complete\n")
    fd = os.open(destination, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    result.update(published=True, certificate_sha256=sha(raw), store=str(destination))
    return result


def load_store(store: Path) -> bytes:
    if store.is_symlink() or not store.is_dir():
        raise ValueError("expected protected library directory")
    if read_snapshot(store / "READY") != b"complete\n":
        raise ValueError("incomplete library publication")
    m = decode(read_snapshot(store / "manifest.json"))
    required = {"schema", "certificate_sha256", "descriptors", "initial_validation", "claim"}
    if not isinstance(m, dict) or set(m) != required or m["schema"] != "avoc-checked-library-store-v1" or m["descriptors"] != DESCRIPTORS:
        raise ValueError("incompatible library store")
    raw = read_snapshot(store / "library.json")
    if sha(raw) != m["certificate_sha256"]:
        raise ValueError("library snapshot changed")
    # Crucially, initial_validation is not used to bypass current checking.
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ["validate", "publish", "query"]:
        p = sub.add_parser(name)
        p.add_argument("path", type=Path, help="certificate file or, for query, saved library directory")
        p.add_argument("--credit", type=int, default=1000000)
        p.add_argument("--timeout", type=int, default=60)
        if name == "publish":
            p.add_argument("--store", type=Path, required=True)
        if name == "query":
            p.add_argument("--queries", type=Path, required=True)
    args = ap.parse_args()
    if not 1 <= args.timeout <= 300:
        raise ValueError("timeout outside [1,300]")
    if args.command == "publish":
        result = publish(args.path, args.store, args.credit, args.timeout)
    elif args.command == "query":
        raw = load_store(args.path)
        queries = decode(read_snapshot(args.queries))
        result = invoke(decode(raw), args.credit, queries, args.timeout)
        result["certificate_sha256"] = sha(raw)
        result["regenerated_candidates"] = False
    else:
        raw = read_snapshot(args.path)
        result = invoke(decode(raw), args.credit, [], args.timeout)
        result["certificate_sha256"] = sha(raw)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in ("globally_certified", "unfunded") else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.TimeoutExpired, RecursionError) as exc:
        print("FAILED: " + str(exc), file=sys.stderr)
        sys.exit(2)
