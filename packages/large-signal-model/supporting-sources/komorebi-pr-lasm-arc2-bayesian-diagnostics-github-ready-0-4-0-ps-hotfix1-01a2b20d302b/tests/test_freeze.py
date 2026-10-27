from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_record() -> dict:
    return json.loads((ROOT / "FROZEN_SOLVER.json").read_text(encoding="utf-8"))


def test_package_and_kaggle_runtime_sources_are_identical() -> None:
    pairs = (
        ("src/komorebi_arc2/entry.py", "kaggle/arc2_entry.py"),
        ("src/komorebi_arc2/atlas.py", "kaggle/atlas.py"),
        ("src/komorebi_arc2/lasm_bayesian.py", "kaggle/lasm_bayesian.py"),
        (
            "src/komorebi_arc2/data/bayesian_lasm_calibration.json",
            "kaggle/bayesian_lasm_calibration.json",
        ),
    )
    for package_name, kaggle_name in pairs:
        assert (ROOT / package_name).read_bytes() == (ROOT / kaggle_name).read_bytes()


def test_frozen_hash_record_matches_every_runtime_file() -> None:
    record = freeze_record()
    assert record["solver_version"] == "0.4.0"
    hashes = record["runtime_sha256"]
    assert len(hashes) >= 10
    for name, expected in hashes.items():
        path = ROOT / name
        assert path.exists(), name
        assert digest(path) == expected, name


def test_notebook_embeds_every_frozen_kaggle_payload() -> None:
    notebook_path = ROOT / "kaggle/PR_LASM_ARC2_Kaggle_Entry.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )
    match = re.search(r"RUNTIME_PAYLOADS = (\{.*?\})\nWORK_ROOT", source, flags=re.DOTALL)
    assert match
    payloads = json.loads(match.group(1))
    expected_names = {
        "arc2_entry.py",
        "atlas.py",
        "lasm_bayesian.py",
        "bayesian_lasm_calibration.json",
        "run_submission.py",
    }
    assert set(payloads) == expected_names
    for name, record in payloads.items():
        decoded = gzip.decompress(base64.b64decode(record["gzip_base64"]))
        assert hashlib.sha256(decoded).hexdigest() == record["sha256"]
        assert decoded == (ROOT / "kaggle" / name).read_bytes()
