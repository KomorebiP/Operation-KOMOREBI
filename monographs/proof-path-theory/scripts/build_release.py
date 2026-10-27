from __future__ import annotations

from pathlib import Path
import importlib.util
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    for name in ("build", "dist"):
        path = ROOT / name
        if path.exists():
            shutil.rmtree(path)
    for path in (ROOT / "src").glob("*.egg-info"):
        shutil.rmtree(path)
    if importlib.util.find_spec("build") is not None:
        command = [sys.executable, "-m", "build", "--no-isolation"]
    else:
        command = [sys.executable, "setup.py", "sdist", "bdist_wheel"]
        print(
            "The 'build' package is unavailable; using the setuptools offline fallback.",
            file=sys.stderr,
        )
    subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
