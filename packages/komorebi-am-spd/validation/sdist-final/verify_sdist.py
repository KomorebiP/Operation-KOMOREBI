"""Install and independently test a supplied, immutable final source archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import tarfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("archive", type=Path)
arguments = parser.parse_args()
ARCHIVE = arguments.archive.resolve(strict=True)
RESULTS = Path(__file__).resolve().parent
SCRATCH = Path("/workspace/scratch/b79c7ffc9c0a")
VENV = SCRATCH / "amspd_clean_sdist"
WORK = SCRATCH / "amspd_sdist_execution"
PYTHON = VENV / "bin" / "python"
EXTRACTED = SCRATCH / "amspd_sdist_extracted"
environment = os.environ.copy()
environment.pop("PYTHONPATH", None)
environment.pop("PYTHONHOME", None)
environment.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1",
                   MPLBACKEND="Agg", PYTHONHASHSEED="0", PIP_NO_INDEX="1")
commands = []
summary = {
    "passed": False,
    "archive": str(ARCHIVE),
    "archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
    "started_utc": datetime.now(timezone.utc).isoformat(),
    "platform": platform.platform(),
    "clean_venv": str(VENV),
    "cwd": str(WORK),
    "outside_checkout": True,
    "pythonpath_removed": "PYTHONPATH" not in environment,
    "network_used_for_sdist_install_or_verification": False,
    "tooling_network_preparation_record": "preparation_commands.json",
    "commands": commands,
}


def save_summary():
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


def run(name, argv):
    started = time.perf_counter()
    completed = subprocess.run(argv, cwd=WORK, env=environment, text=True, capture_output=True)
    (RESULTS / f"{name}.stdout.log").write_text(completed.stdout)
    (RESULTS / f"{name}.stderr.log").write_text(completed.stderr)
    record = {"name": name, "argv": [str(value) for value in argv], "cwd": str(WORK),
              "exit_code": completed.returncode, "elapsed_seconds": time.perf_counter() - started}
    commands.append(record)
    save_summary()
    print(json.dumps(record), flush=True)
    return completed


if EXTRACTED.exists():
    raise SystemExit(f"Refusing to reuse extracted archive directory {EXTRACTED}")
EXTRACTED.mkdir()
with tarfile.open(ARCHIVE, "r:gz") as source:
    source.extractall(EXTRACTED, filter="data")
roots = list(EXTRACTED.iterdir())
if len(roots) != 1 or not roots[0].is_dir():
    raise SystemExit("The source archive must contain exactly one root directory")
SOURCE = roots[0]
summary["extracted_source"] = str(SOURCE)
save_summary()

installation = run("install", [str(PYTHON), "-m", "pip", "install", "--no-index", "--no-deps",
                                "--no-build-isolation", str(ARCHIVE)])
if installation.returncode:
    raise SystemExit(installation.returncode)

guard = """
import importlib.metadata as metadata
import json
import os
import platform
import sys
from pathlib import Path
import am_spd
location = Path(am_spd.__file__).resolve()
assert location.is_relative_to(Path(sys.prefix).resolve()), location
assert 'site-packages' in location.parts, location
assert os.environ.get('PYTHONPATH') is None
print(json.dumps({
    'package_import_path': str(location),
    'python': sys.version,
    'platform': platform.platform(),
    'sys_prefix': sys.prefix,
    'sys_path': sys.path,
    'pythonpath': os.environ.get('PYTHONPATH'),
    'packages': {distribution.metadata['Name']: distribution.version
                 for distribution in metadata.distributions()},
}, indent=2, sort_keys=True))
"""
import_guard = run("installed_environment", [str(PYTHON), "-c", guard])
if import_guard.returncode:
    raise SystemExit(import_guard.returncode)
summary["installed_environment"] = json.loads(import_guard.stdout)
run("freeze", [str(PYTHON), "-m", "pip", "freeze", "--all"])
run("pip_check", [str(PYTHON), "-m", "pip", "check"])
tests = run("pytest", [str(PYTHON), "-m", "pytest", "-q", "--import-mode=importlib",
                       "-c", str(SOURCE / "pyproject.toml"), str(SOURCE / "tests"),
                       "--junitxml", str(RESULTS / "pytest.xml")])
if (RESULTS / "pytest.xml").is_file():
    xml = ET.parse(RESULTS / "pytest.xml").getroot()
    summary["test_results"] = {
        "total": len(list(xml.iter("testcase"))),
        "failures": len(list(xml.iter("failure"))),
        "errors": len(list(xml.iter("error"))),
        "skipped": len(list(xml.iter("skipped"))),
    }
integration = run("integration", [str(PYTHON), "-m", "am_spd", "verify", "--full"])
if integration.returncode == 0:
    report = json.loads(integration.stdout)
    (RESULTS / "integration.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    summary["integration"] = {"passed": report["passed"], "total": len(report["checks"]),
                              "passed_checks": sum(report["checks"].values())}
run("info", [str(PYTHON), "-m", "am_spd", "info"])
summary["archive_sha256_after_verification"] = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
summary["archive_unchanged"] = summary["archive_sha256"] == summary["archive_sha256_after_verification"]
summary["finished_utc"] = datetime.now(timezone.utc).isoformat()
summary["passed"] = (all(command["exit_code"] == 0 for command in commands)
                     and summary["archive_unchanged"]
                     and summary.get("test_results", {}).get("total", 0) > 0
                     and summary.get("integration", {}).get("passed", False))
save_summary()
print(json.dumps(summary, indent=2), flush=True)
raise SystemExit(0 if summary["passed"] else 1)
