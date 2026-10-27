"""Adversarial tests of the actual manifest validator, in isolated temporary copies.

Every rejection must have a nonzero exit code and the expected diagnostic.
No mathematical proof or signature verification is claimed.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent
VALIDATOR = ROOT / "verify_manifest.py"


def main() -> int:
    records: list[dict] = []
    def scenario(name: str, mutate: Callable[[Path], None], expected: int, diagnostic: str,
                 *, optimized: bool = False) -> None:
        with tempfile.TemporaryDirectory(prefix="komorebi-integrity-") as tmp:
            root = Path(tmp)
            (root / "payload").mkdir()
            (root / "README.txt").write_text("A complete test archive.\n", encoding="utf-8")
            (root / "payload/data.txt").write_text("exact witness: 14, 17\n", encoding="utf-8")
            paths = ["README.txt", "payload/data.txt"]
            (root / "MANIFEST_SHA256.txt").write_text("".join(
                f"{hashlib.sha256((root/p).read_bytes()).hexdigest()}  {p}\n" for p in paths
            ), encoding="utf-8")
            mutate(root)
            args = [sys.executable] + (["-O"] if optimized else [])
            args += [str(VALIDATOR), "--root", str(root)]
            try:
                result = subprocess.run(args, capture_output=True, text=True, timeout=15)
                output = (result.stdout + result.stderr).replace(str(root), "<fixture>")
                passed = result.returncode == expected and diagnostic in output
                records.append({"name": name, "passed": passed,
                                "exit_code": result.returncode, "expected_exit_code": expected,
                                "expected_diagnostic": diagnostic, "output": output.strip(),
                                "optimized_python": optimized})
            except subprocess.TimeoutExpired:
                records.append({"name": name, "passed": False, "failure": "timeout is not a rejection"})

    def alter_manifest(root: Path, transform: Callable[[str], str]) -> None:
        p = root / "MANIFEST_SHA256.txt"
        p.write_text(transform(p.read_text()), encoding="utf-8")

    scenario("complete_inventory_accepted", lambda p: None, 0, "complete inventory of 2 files")
    scenario("altered_payload_rejected", lambda p: (p/"payload/data.txt").write_text("tampered\n"), 1, "Digest mismatch")
    scenario("missing_payload_rejected", lambda p: (p/"payload/data.txt").unlink(), 1, "Missing inventory file")
    scenario("empty_manifest_rejected", lambda p: (p/"MANIFEST_SHA256.txt").write_text(""), 1, "no file records")
    scenario("comments_only_manifest_rejected", lambda p: (p/"MANIFEST_SHA256.txt").write_text("# no records\n"), 1, "no file records")
    scenario("omitted_inventory_entry_rejected", lambda p: alter_manifest(p, lambda s: s.splitlines()[0]+"\n"), 1, "Unlisted file")
    scenario("unlisted_payload_rejected", lambda p: (p/"extra.txt").write_text("unexpected"), 1, "Unlisted file")
    scenario("duplicate_entry_rejected", lambda p: alter_manifest(p, lambda s: s+s.splitlines()[0]+"\n"), 1, "duplicate inventory entry")
    scenario("invalid_digest_rejected", lambda p: alter_manifest(p, lambda s: "Z"+s[1:]), 1, "invalid SHA-256")
    scenario("parent_traversal_rejected", lambda p: alter_manifest(p, lambda s: s+("0"*64)+"  ../outside.txt\n"), 1, "unsafe or noncanonical")
    scenario("absolute_path_rejected", lambda p: alter_manifest(p, lambda s: s+("0"*64)+"  /outside.txt\n"), 1, "unsafe or noncanonical")
    scenario("windows_path_rejected", lambda p: alter_manifest(p, lambda s: s+("0"*64)+"  C:\\outside.txt\n"), 1, "unsafe or noncanonical")
    scenario("noncanonical_path_rejected", lambda p: alter_manifest(p, lambda s: s.replace("payload/data", "payload/./data")), 1, "unsafe or noncanonical")
    scenario("self_listing_rejected", lambda p: alter_manifest(p, lambda s: s+("0"*64)+"  MANIFEST_SHA256.txt\n"), 1, "must not list itself")
    scenario("missing_manifest_diagnosed", lambda p: (p/"MANIFEST_SHA256.txt").unlink(), 2, "Cannot read manifest")
    scenario("non_utf8_manifest_diagnosed", lambda p: (p/"MANIFEST_SHA256.txt").write_bytes(b"\xff\xfe"), 2, "Cannot read manifest")
    scenario("optimized_python_empty_manifest_rejected", lambda p: (p/"MANIFEST_SHA256.txt").write_text(""), 1, "no file records", optimized=True)

    failed = [r["name"] for r in records if not r["passed"]]
    summary = {"suite": "manifest integrity controls", "cases": len(records),
               "passed": len(records)-len(failed), "failed": failed, "checks": records,
               "scope": "Actual CLI executions in isolated fixtures. Not a Lean audit or authentication test."}
    (ROOT/"audit").mkdir(exist_ok=True)
    (ROOT/"audit/integrity_checks.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(f"Integrity validator: {summary['passed']}/{summary['cases']} controls passed.")
    if failed:
        print("Failed: "+", ".join(failed), file=sys.stderr)
    return int(bool(failed))

if __name__ == "__main__":
    raise SystemExit(main())
