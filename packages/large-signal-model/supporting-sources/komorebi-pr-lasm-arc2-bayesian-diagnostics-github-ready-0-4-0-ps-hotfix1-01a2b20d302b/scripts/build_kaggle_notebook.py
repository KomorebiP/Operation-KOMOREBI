from __future__ import annotations

"""Build the self-contained offline Kaggle notebook from frozen runtime files."""

import base64
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KAGGLE = ROOT / "kaggle"
OUTPUT = KAGGLE / "PR_LASM_ARC2_Kaggle_Entry.ipynb"
RUNTIME_FILES = (
    "arc2_entry.py",
    "atlas.py",
    "lasm_bayesian.py",
    "bayesian_lasm_calibration.json",
    "run_submission.py",
)


def encode(path: Path) -> tuple[str, str]:
    content = path.read_bytes()
    return base64.b64encode(gzip.compress(content, compresslevel=9)).decode("ascii"), hashlib.sha256(content).hexdigest()


def source_lines(text: str) -> list[str]:
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return lines


def code_cell(source: str, cell_id: str) -> dict[str, Any]:
    return {
        "id": cell_id,
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines(source),
    }


def markdown_cell(source: str, cell_id: str) -> dict[str, Any]:
    return {"id": cell_id, "cell_type": "markdown", "metadata": {}, "source": source_lines(source)}


def main() -> int:
    missing = [name for name in RUNTIME_FILES if not (KAGGLE / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing Kaggle runtime files: {missing}")

    payloads: dict[str, dict[str, str]] = {}
    for name in RUNTIME_FILES:
        encoded, digest = encode(KAGGLE / name)
        payloads[name] = {"gzip_base64": encoded, "sha256": digest}

    writer = f'''from pathlib import Path
import base64, gzip, hashlib, json, os, sys

RUNTIME_PAYLOADS = {json.dumps(payloads, sort_keys=True)}
WORK_ROOT = Path("/kaggle/working/pr_lasm_arc2")
WORK_ROOT.mkdir(parents=True, exist_ok=True)
for name, record in RUNTIME_PAYLOADS.items():
    content = gzip.decompress(base64.b64decode(record["gzip_base64"]))
    digest = hashlib.sha256(content).hexdigest()
    assert digest == record["sha256"], (name, digest, record["sha256"])
    (WORK_ROOT / name).write_bytes(content)

solver_path = WORK_ROOT / "arc2_entry.py"
runner_path = WORK_ROOT / "run_submission.py"
calibration_path = WORK_ROOT / "bayesian_lasm_calibration.json"
os.environ["PR_LASM_ARC2_CALIBRATION"] = str(calibration_path)
if str(WORK_ROOT) not in sys.path:
    sys.path.insert(0, str(WORK_ROOT))
print(json.dumps({{"runtime_root": str(WORK_ROOT), "verified_files": len(RUNTIME_PAYLOADS), "hashes": {{k: v["sha256"] for k, v in RUNTIME_PAYLOADS.items()}}}}, indent=2))
'''

    run = '''import os, subprocess, sys
DATA_DIR = os.environ.get("ARC2_DATA_DIR", "/kaggle/input")
OUTPUT = os.environ.get("ARC2_OUTPUT", "/kaggle/working/submission.json")
REPORT = os.environ.get("ARC2_REPORT", "/kaggle/working/pr_lasm_arc2_runtime_report.json")
SOFT_LIMIT = os.environ.get("ARC2_SOFT_LIMIT", "8")
HARD_LIMIT = os.environ.get("ARC2_HARD_LIMIT", "20")
WORKERS = os.environ.get("ARC2_WORKERS", str(max(1, min(4, os.cpu_count() or 1))))
command = [
    sys.executable, str(runner_path),
    "--solver", str(solver_path),
    "--data-dir", DATA_DIR,
    "--output", OUTPUT,
    "--report", REPORT,
    "--soft-time-limit", SOFT_LIMIT,
    "--hard-time-limit", HARD_LIMIT,
    "--workers", WORKERS,
]
print(" ".join(command))
subprocess.run(command, check=True, env=os.environ.copy())
'''

    validate = '''import importlib.util, json, os, sys
spec = importlib.util.spec_from_file_location("pr_lasm_arc2_notebook_check", solver_path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
challenge = module.find_challenge_json(DATA_DIR, "test") or module.find_input_json(DATA_DIR, "test")
tasks = module.load_tasks_from_path(challenge)
submission = json.load(open(OUTPUT, encoding="utf-8"))
errors = module.validate_submission(submission, tasks)
assert not errors, errors[:10]
runtime = json.load(open(REPORT, encoding="utf-8"))
calibration = json.load(open(calibration_path, encoding="utf-8"))
print(json.dumps({
    "submission": OUTPUT,
    "task_count": len(tasks),
    "valid": True,
    "solver_version": module.SOLVER_VERSION,
    "calibration_version": calibration.get("model_version"),
    "runtime": {k: v for k, v in runtime.items() if k != "per_task"},
}, indent=2))
'''

    notebook = {
        "cells": [
            markdown_cell(
                "# PR-LASM ARC2 Bayesian Entry\n\n"
                "Version **0.4.0**. This notebook contains the complete offline runtime, "
                "the fitted public-training Bayesian calibration, and the hard-isolated task runner. "
                "Attach the ARC Prize ARC-AGI-2 competition data, keep internet disabled, and run all cells.\n",
                "intro",
            ),
            code_cell(writer, "write-runtime"),
            code_cell(run, "run-submission"),
            code_cell(validate, "validate-submission"),
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
