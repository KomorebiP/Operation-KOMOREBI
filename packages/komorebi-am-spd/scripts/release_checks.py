"""Run the finite source release checks and retain raw reports."""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from importlib.metadata import version
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    commands = [
        ("tests", [sys.executable, "-m", "pytest", "-q", "--junitxml", str(args.output / "pytest.xml")]),
        ("lint", [sys.executable, "-m", "ruff", "check", "src", "tests", "examples", "scripts/prepare_offline.py", "scripts/release_checks.py", "scripts/build_paper_fixtures.py"]),
        ("compile", [sys.executable, "-m", "compileall", "-q", "src", "examples"]),
        ("integration", [sys.executable, "-m", "am_spd", "verify", "--full"]),
    ]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(Path("src").resolve())
    for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        environment[variable] = "1"
    records = []
    for name, command in commands:
        started = time.perf_counter()
        result = subprocess.run(command, env=environment, text=True, capture_output=True, timeout=120, check=False)
        (args.output / f"{name}.stdout.log").write_text(result.stdout, encoding="utf-8")
        (args.output / f"{name}.stderr.log").write_text(result.stderr, encoding="utf-8")
        records.append({"name": name, "argv": command, "exit_code": result.returncode, "seconds": time.perf_counter() - started})
        if name == "integration" and result.returncode == 0:
            report = json.loads(result.stdout)
            (args.output / "integration.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"{name}: exit {result.returncode}", flush=True)
    summary = {
        "passed": all(record["exit_code"] == 0 for record in records),
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": {name: version(name) for name in ("numpy", "scipy", "matplotlib", "scikit-image", "opencv-python-headless", "pillow", "pytest", "ruff")},
        "commands": records,
        "scope": "finite float64 package checks; not a universal image approximation theorem",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
