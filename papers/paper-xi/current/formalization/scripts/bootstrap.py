#!/usr/bin/env python3
"""Prepare the pinned portable Lean runtime and official mathlib dependencies.

The bundled bootstrap targets Linux x86_64, including Ubuntu under WSL. It
changes only this project directory and downloads from the official Lean,
leanprover-community and mathlib cache services. Use --offline to require an
already prepared runtime and dependency tree without downloading anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import urllib.request

from replay import ROOT, LEAN_VERSION, LEAN_COMMIT, MATHLIB_COMMIT, sha, stamp, write_json

ARCHIVE_NAME = "lean-4.34.0-rc2-linux.tar.zst"
ARCHIVE_URL = "https://github.com/leanprover/lean4/releases/download/v4.34.0-rc2/" + ARCHIVE_NAME
ARCHIVE_SHA256 = "3d011041203acacf300d343a39673f7d233743397993797c941346ae9e5df1a8"
BINARY_SHA256 = "e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if sys.platform != "linux" or platform.machine().lower() not in {"x86_64", "amd64"}:
        parser.error("This portable bootstrap requires Linux x86_64. On Windows use Ubuntu in WSL; the lakefile and lean-toolchain also support a separately installed matching Lean.")
    for tool in ["git", "tar", "zstd"]:
        if not shutil.which(tool):
            parser.error(f"Required system utility is missing: {tool}")
    runtime = ROOT / ".runtime"
    runtime.mkdir(exist_ok=True)
    toolchain = runtime / "lean-4.34.0-rc2-linux"
    bin_dir = toolchain / "bin"
    out = ROOT / "evidence" / ("bootstrap_" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    out.mkdir(parents=True, exist_ok=False)
    record = {"status": "RUNNING", "started_at": stamp(), "offline": args.offline,
              "commands": [], "official_archive_url": ARCHIVE_URL,
              "official_archive_sha256": ARCHIVE_SHA256}
    write_json(out / "RESULT.json", record)
    started = time.monotonic()
    try:
        if not (bin_dir / "lean").is_file():
            if args.offline:
                raise RuntimeError("Offline preparation requires the pinned portable runtime")
            archive = runtime / ARCHIVE_NAME
            if not archive.is_file() or sha(archive) != ARCHIVE_SHA256:
                temp = archive.with_suffix(archive.suffix + ".part")
                h = hashlib.sha256()
                request = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "PaperXI-Release-Validation"})
                with urllib.request.urlopen(request, timeout=60) as response, temp.open("wb") as f:
                    for chunk in iter(lambda: response.read(4 * 1024 * 1024), b""):
                        f.write(chunk); h.update(chunk)
                if h.hexdigest() != ARCHIVE_SHA256:
                    raise RuntimeError("Official Lean archive checksum mismatch")
                temp.replace(archive)
            command = ["tar", "--zstd", "--no-same-owner", "--no-same-permissions",
                       "-xf", str(archive), "-C", str(runtime)]
            record["commands"].append(command)
            subprocess.run(command, check=True)
        if sha(bin_dir / "lean") != BINARY_SHA256:
            raise RuntimeError("Pinned Linux Lean binary checksum mismatch")
        env = os.environ.copy()
        env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
        env["MATHLIB_NO_CACHE_ON_UPDATE"] = "1"
        env["MATHLIB_CACHE_DIR"] = str(runtime / "mathlib_cache")
        version = subprocess.check_output([str(bin_dir / "lean"), "--version"], env=env, text=True).strip()
        if LEAN_VERSION not in version or LEAN_COMMIT not in version:
            raise RuntimeError(f"Lean version mismatch: {version}")
        record["lean_version"] = version
        record["lean_binary_sha256"] = sha(bin_dir / "lean")
        manifest_path = ROOT / "lake-manifest.json"
        if not manifest_path.is_file():
            raise RuntimeError("The release's pinned lake-manifest.json is missing")
        manifest = json.loads(manifest_path.read_text())
        expected = {p["name"]: p["rev"] for p in manifest["packages"]}
        if expected.get("mathlib") != MATHLIB_COMMIT:
            raise RuntimeError("The release manifest has an unexpected mathlib revision")

        def installed_revisions() -> dict[str, str]:
            observed = {}
            for name in expected:
                package = ROOT / ".lake/packages" / name
                if not (package / ".git").exists():
                    continue
                p = subprocess.run(["git", "-C", str(package), "rev-parse", "HEAD"], capture_output=True, text=True)
                if p.returncode == 0:
                    observed[name] = p.stdout.strip()
            return observed

        observed = installed_revisions()
        if observed != expected:
            if args.offline:
                raise RuntimeError("Offline preparation requires all exact pinned dependencies")
            command = [str(bin_dir / "lake"), "--keep-toolchain", "update", "mathlib"]
            record["commands"].append(command)
            with (out / "DEPENDENCIES.log").open("w") as f:
                subprocess.run(command, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
            observed = installed_revisions()
            if observed != expected:
                raise RuntimeError("Installed dependency revisions do not match the release manifest")
        record["dependency_revisions"] = observed
        sources = json.loads((ROOT / "catalogues/SOURCE_CATALOG.json").read_text())["modules"]
        imports = sorted({imp for item in sources.values() for imp in item["imports"] if imp.startswith("Mathlib.")})
        if not args.offline:
            command = [str(bin_dir / "lake"), "exe", "cache", "get", *imports]
            record["commands"].append(command)
            with (out / "MATHLIB_CACHE.log").open("w") as f:
                subprocess.run(command, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
        mathlib_objects = ROOT / ".lake/packages/mathlib/.lake/build/lib/lean"
        missing = [name for name in imports if not (mathlib_objects / Path(*name.split(".")).with_suffix(".olean")).is_file()]
        if missing:
            raise RuntimeError(f"Required direct mathlib object roots are missing: {missing}")
        record.update(status="PASS", direct_mathlib_object_roots_present=len(imports))
    except Exception as exc:
        record.update(status="FAIL", error=repr(exc))
    finally:
        record.update(completed_at=stamp(), seconds=time.monotonic() - started)
        write_json(out / "RESULT.json", record)
    print(json.dumps(record, indent=2))
    return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
