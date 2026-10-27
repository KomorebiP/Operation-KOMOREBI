from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from komorebi_arc2 import entry


def test_hard_runner_on_mini_data(tmp_path: Path):
    root = Path(entry.make_mini_dataset(tmp_path / "mini"))
    repo = Path(__file__).resolve().parents[1]
    out = tmp_path / "submission.json"
    report = tmp_path / "runtime.json"
    command = [
        sys.executable,
        str(repo / "kaggle/run_submission.py"),
        "--solver",
        str(repo / "kaggle/arc2_entry.py"),
        "--input",
        str(root / "arc-agi_test-challenges.json"),
        "--output",
        str(out),
        "--report",
        str(report),
        "--soft-time-limit",
        "2",
        "--hard-time-limit",
        "10",
        "--workers",
        "2",
    ]
    subprocess.run(command, check=True)
    tasks = entry.load_tasks_from_path(root / "arc-agi_test-challenges.json")
    submission = json.loads(out.read_text())
    assert entry.validate_submission(submission, tasks) == []
    runtime = json.loads(report.read_text())
    assert runtime["valid_submission"] is True
    assert runtime["hard_timeouts"] == 0
