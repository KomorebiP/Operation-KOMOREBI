from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

COMMIT = "32f413d8d55239d9bc54bb6b6ec37b0630891ed4"
REPO = "https://github.com/connordilgren/are-lrms-easily-interpretable.git"
HF_REPO = "connordilgren/gpt2-prontoqa-multimode-coconut"
HF_FILE = "checkpoint_37"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="external")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    repo = root / "are-lrms-easily-interpretable"
    ckpt_dir = root / "checkpoint"
    root.mkdir(parents=True, exist_ok=True)
    if not repo.exists():
        subprocess.run(["git", "clone", REPO, str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "--detach", COMMIT], check=True)
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise SystemExit("Install huggingface-hub first: pip install huggingface-hub") from exc
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(repo_id=HF_REPO, filename=HF_FILE, local_dir=ckpt_dir)
    print(f"repo={repo}")
    print(f"checkpoint={path}")
    print(f"tasks={repo / 'data' / 'prontoqa_test.json'}")


if __name__ == "__main__":
    main()
