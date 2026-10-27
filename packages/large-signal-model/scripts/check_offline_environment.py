from __future__ import annotations

import importlib
import json
import os
import platform
import sys
from pathlib import Path

from komorebi_arc3_offline.offline_guard import assert_offline_guard, install_offline_guard


def module_status(name: str) -> dict[str, object]:
    try:
        module = importlib.import_module(name)
        return {
            "module": name,
            "available": True,
            "version": getattr(module, "__version__", "available"),
            "error": None,
        }
    except Exception as exc:
        return {
            "module": name,
            "available": False,
            "version": None,
            "error": repr(exc),
        }


def main() -> int:
    install_offline_guard(strict=True)
    assert_offline_guard()
    root = Path(os.environ.get("ENVIRONMENTS_DIR", "environment_files")).expanduser().resolve()
    metadata_count = len(list(root.rglob("metadata.json"))) if root.exists() else 0
    report = {
        "offline_guard": True,
        "operation_mode": os.environ.get("OPERATION_MODE"),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "conda_prefix": os.environ.get("CONDA_PREFIX"),
        "environments_dir": str(root),
        "local_metadata_files": metadata_count,
        "modules": [
            module_status(name)
            for name in ("numpy", "scipy", "PIL", "arcengine", "arc_agi", "pytest", "torch")
        ],
    }
    print(json.dumps(report, indent=2))
    required = {row["module"]: row["available"] for row in report["modules"]}
    return 0 if all(required.get(name, False) for name in ("numpy", "scipy", "PIL", "arcengine", "arc_agi")) else 2


if __name__ == "__main__":
    raise SystemExit(main())
