from __future__ import annotations

import subprocess
from pathlib import Path

from sric_real_lrm.source_lock import verify_external_repository


def _run(*args: str, cwd: Path) -> str:
    return subprocess.check_output(list(args), cwd=cwd, text=True).strip()


def test_external_source_lock_verifies_commit_and_blobs(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run("git", "init", "-q", cwd=repo)
    _run("git", "config", "user.email", "fixture@example.invalid", cwd=repo)
    _run("git", "config", "user.name", "Fixture", cwd=repo)
    files = {
        "model_wrapper": "models/wrapper.py",
        "latent_runtime": "runtime/latent.py",
        "requirements": "requirements.txt",
        "prontoqa_test": "data/prontoqa_test.json",
    }
    for index, path in enumerate(files.values()):
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"fixture-{index}\n", encoding="utf-8")
    _run("git", "add", ".", cwd=repo)
    _run("git", "commit", "-qm", "fixture", cwd=repo)
    commit = _run("git", "rev-parse", "HEAD", cwd=repo)
    lock = {
        "external_repository": {
            "name": "fixture/repo",
            "commit": commit,
            "files": {
                name: {
                    "path": path,
                    "git_blob_sha": _run("git", "rev-parse", f"HEAD:{path}", cwd=repo),
                }
                for name, path in files.items()
            },
        }
    }
    receipt = verify_external_repository(repo, lock, dataset_key="prontoqa_test")
    assert receipt["commit"] == commit
    assert receipt["clean"] is True
    assert len(receipt["verified_objects"]) == 4
