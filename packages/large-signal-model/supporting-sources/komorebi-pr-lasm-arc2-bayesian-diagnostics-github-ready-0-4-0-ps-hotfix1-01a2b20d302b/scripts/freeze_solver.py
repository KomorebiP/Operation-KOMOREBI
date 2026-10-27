from __future__ import annotations

"""Freeze every file required by the offline Bayesian ARC runtime."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = (
    "src/komorebi_arc2/entry.py",
    "src/komorebi_arc2/atlas.py",
    "src/komorebi_arc2/lasm_bayesian.py",
    "src/komorebi_arc2/data/bayesian_lasm_calibration.json",
    "kaggle/arc2_entry.py",
    "kaggle/atlas.py",
    "kaggle/lasm_bayesian.py",
    "kaggle/bayesian_lasm_calibration.json",
    "kaggle/run_submission.py",
    "kaggle/PR_LASM_ARC2_Kaggle_Entry.ipynb",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="0.4.0")
    parser.add_argument("--output", default=str(ROOT / "FROZEN_SOLVER.json"))
    parser.add_argument("--calibration-report", default=None)
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    relative_files = tuple(args.files) if args.files else DEFAULT_FILES
    missing = [name for name in relative_files if not (ROOT / name).exists()]
    if missing:
        raise FileNotFoundError(f"Cannot freeze missing files: {missing}")
    hashes = {name: sha256(ROOT / name) for name in relative_files}
    record: dict[str, Any] = {
        "solver_name": "PR-LASM ARC2 Bayesian Entry",
        "solver_version": args.version,
        "author": "Komorebi P.",
        "frozen_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "runtime_sha256": hashes,
        "default_soft_time_limit_seconds": 8.0,
        "default_hard_time_limit_seconds": 20.0,
        "calibration_source": "ARC-AGI-2 public training split only",
        "private_competition_score": None,
    }
    if args.calibration_report:
        report_path = Path(args.calibration_report)
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            record["bayesian_calibration"] = {
                "model_version": report.get("model_version"),
                "training_metadata": report.get("training_metadata"),
                "calibration_evaluation": report.get("calibration_evaluation"),
                "parameter_holdout_evaluation": report.get("locked_training_holdout_evaluation"),
            }
    output = Path(args.output)
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
