"""Package an already verified offline handoff without altering its inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def package(root, output):
    require(not output.exists() and not output.is_symlink(),
            "Output path already exists; choose a new archive path.")
    root, output = root.resolve(), output.resolve()
    require(not output.exists() and not output.is_relative_to(root),
            "Choose a new archive path outside the handoff inputs.")
    audit = output.with_name(output.stem + "_audit.json")
    require(not audit.exists() and not audit.is_symlink(), "Detached audit path already exists.")
    manifest_path = root / "INPUTS_SHA256SUMS.txt"
    hashes = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
                "Invalid SHA256 manifest digest.")
        require(name == Path(name).name and "\\" not in name and ":" not in name and
                name not in {".", "..", "INPUTS_SHA256SUMS.txt"} and name not in hashes,
                "Invalid or duplicate root manifest member.")
        hashes[name] = digest
    files = {p.name: p for p in root.iterdir() if p.is_file()}
    require(set(files) == set(hashes) | {manifest_path.name}, "Root input membership differs from manifest.")
    hashes[manifest_path.name] = sha(manifest_path)
    before = {name: (path.stat().st_ino, path.stat().st_size, path.stat().st_mtime_ns)
              for name, path in files.items()}
    for name, path in files.items():
        require(sha(path) == hashes[name], f"Input changed: {name}")
    checked = subprocess.run([sys.executable, str(root / "verify_release.py"), "--root", str(root)],
                             capture_output=True, text=True)
    require(checked.returncode == 0,
            "Offline verification failed: " + (checked.stderr.strip() or checked.stdout.strip()))
    verification = json.loads(checked.stdout)
    require(verification.get("integrity_pass") is True, "Offline verification did not pass.")
    partial = output.with_suffix(output.suffix + ".partial")
    require(not partial.exists(), "Existing partial package must be preserved or removed explicitly.")
    with zipfile.ZipFile(partial, "x", allowZip64=True) as archive:
        for name, path in sorted(files.items()):
            compression = zipfile.ZIP_STORED if name.endswith(".zip") else zipfile.ZIP_DEFLATED
            archive.write(path, arcname=name, compress_type=compression, compresslevel=6)
    with zipfile.ZipFile(partial) as archive:
        require(len(archive.namelist()) == len(files) and set(archive.namelist()) == set(files),
                "Packaged input membership differs.")
        for name, digest in hashes.items():
            with archive.open(name) as stream:
                require(hashlib.file_digest(stream, "sha256").hexdigest() == digest,
                        f"Packaged payload hash differs: {name}")
    for name, path in files.items():
        after = path.stat()
        require((after.st_ino, after.st_size, after.st_mtime_ns) == before[name] and sha(path) == hashes[name],
                f"Input changed during packaging: {name}")
    # Exclusive publication preserves any unrelated output created concurrently.
    os.link(partial, output)
    require(sha(output) == sha(partial), "Published package differs from verified partial.")
    partial.unlink()
    report = {
        "schema": "komorebi.arc-agi2.block17.complete-handoff-package-audit.v1",
        "integrity_pass": True, "archive": str(output), "archive_bytes": output.stat().st_size,
        "archive_sha256": sha(output), "root_payloads": len(files),
        "all_payload_sha256_and_crc_verified": True, "input_bytes_and_file_identities_unchanged": True,
        "solver_source_modified": False, "compiler_calls": 0,
        "saved_score_verification": verification,
        "payload_sha256": dict(sorted(hashes.items())),
    }
    with audit.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.root, args.output), indent=2, sort_keys=True))
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"Packaging failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
