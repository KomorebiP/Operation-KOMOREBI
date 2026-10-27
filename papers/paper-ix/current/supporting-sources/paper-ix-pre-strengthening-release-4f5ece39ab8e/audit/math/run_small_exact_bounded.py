#!/usr/bin/env python3
"""Run the unchanged small exact-check source from a fresh output directory.

The source writes beside __file__; copying it byte-for-byte preserves its
original direct result while allowing a v2 runner to own fresh result paths.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    original = Path(__file__).with_name("small_exact_checks.py")
    predecessor = original.with_suffix(".json")
    output = args.output_directory
    if not output.is_dir() or output.is_symlink():
        raise ValueError("The bounded runner must create a regular fresh directory.")
    code_copy = output / original.name
    scientific_result = code_copy.with_suffix(".json")
    provenance = output / "copy_provenance.json"
    if any(p.exists() for p in (code_copy, scientific_result, provenance)):
        raise ValueError("Fresh copy/result/provenance paths already exist.")
    original_bytes = original.read_bytes()
    predecessor_bytes = predecessor.read_bytes()
    code_copy.write_bytes(original_bytes)
    assert code_copy.read_bytes() == original_bytes
    command = [sys.executable, str(code_copy)]
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    result_bytes = scientific_result.read_bytes()
    result = json.loads(result_bytes)
    assert result["status"] == "PASS"
    assert result_bytes == predecessor_bytes
    assert original.read_bytes() == original_bytes
    assert predecessor.read_bytes() == predecessor_bytes
    record = {
        "status": "PASS",
        "original_source": str(original),
        "source_copy": str(code_copy),
        "source_sha256": digest(original_bytes),
        "source_copy_sha256": digest(code_copy.read_bytes()),
        "copy_is_byte_identical": True,
        "predecessor_result": str(predecessor),
        "predecessor_result_sha256": digest(predecessor_bytes),
        "fresh_result_sha256": digest(result_bytes),
        "fresh_result_matches_predecessor_bytes": True,
        "actual_child_argv": command,
        "interpretation": "Unchanged implementation and finite assertion reproduced in the literal scripted range.",
        "non_claims": ["Universal proof", "Fresh Lean/Lake compilation", "Infinite p-adic construction"]
    }
    provenance.write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps({"status":"PASS", "source_copy_is_byte_identical":True,
                      "fresh_result_matches_predecessor_bytes":True}))

if __name__ == "__main__":
    main()
