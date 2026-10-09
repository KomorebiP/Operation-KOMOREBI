"""Prepare an isolated environment before the final sdist is available."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRATCH = Path("/workspace/scratch/b79c7ffc9c0a")
VENV = SCRATCH / "amspd_clean_sdist_release"
WORK = SCRATCH / "amspd_sdist_release_execution"
TOOLING = SCRATCH / "amspd_wheels" / "sdist_tooling"
NUMERICAL = SCRATCH / "amspd_wheels" / "linux312"
environment = os.environ.copy()
environment.pop("PYTHONPATH", None)
environment.pop("PYTHONHOME", None)
environment.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1",
                   MPLBACKEND="Agg", PYTHONHASHSEED="0")
commands = []


def run(name, arguments, *, network=False):
    completed = subprocess.run(arguments, cwd=WORK, env=environment, text=True, capture_output=True)
    (ROOT / f"{name}.stdout.log").write_text(completed.stdout)
    (ROOT / f"{name}.stderr.log").write_text(completed.stderr)
    record = {"name": name, "command": [str(value) for value in arguments], "cwd": str(WORK),
              "network_allowed": network, "exit_code": completed.returncode}
    commands.append(record)
    (ROOT / "preparation_commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    print(json.dumps(record), flush=True)
    if completed.returncode:
        raise SystemExit(completed.returncode)


if VENV.exists():
    raise SystemExit(f"Refusing to reuse the existing environment {VENV}")
ROOT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=False)
TOOLING.mkdir(parents=True, exist_ok=True)
run("create_venv", [sys.executable, "-m", "venv", str(VENV)])
PYTHON = VENV / "bin" / "python"
run("install_tooling", [str(PYTHON), "-m", "pip", "install", "--no-index", "--find-links", str(TOOLING),
                         "pytest", "setuptools>=77", "wheel", "build"])
run("install_numerical", [str(PYTHON), "-m", "pip", "install", "--no-index", "--find-links", str(NUMERICAL),
                           "numpy>=2.0", "scipy>=1.14", "matplotlib>=3.9", "scikit-image>=0.24",
                           "opencv-python-headless>=4.10", "pillow>=10.4"])
run("prepared_freeze", [str(PYTHON), "-m", "pip", "freeze", "--all"])
run("prepared_pip_check", [str(PYTHON), "-m", "pip", "check"])
summary = {"status": "prepared_waiting_for_final_sdist", "python": sys.version,
           "platform": platform.platform(), "venv": str(VENV), "working_directory": str(WORK),
           "numerical_install": "offline wheelhouse", "tooling_preparation": "offline preexisting tooling wheelhouse",
           "network_used_for_preparation": False,
           "thread_limits": {key: environment[key] for key in
                             ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
           "pythonpath_removed": "PYTHONPATH" not in environment,
           "source_package_installed": False}
(ROOT / "preparation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary), flush=True)
