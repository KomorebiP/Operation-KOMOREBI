from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .manifest import verify_manifest
from .utils import environment_report, save_json


VERIFICATION_EXCLUDES = {".venv", ".git", ".pytest_cache", "__pycache__", "dist", "results", "runs"}


def _portable_environment() -> dict[str, Any]:
    report = environment_report()
    executable = report.pop("executable", None)
    report.pop("cwd", None)
    if executable:
        report["python_executable_name"] = Path(str(executable)).name
    return report


def verify_python_sources(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root)
    failures = []
    checked = 0
    for path in sorted((root / "osl_lab").glob("*.py")):
        checked += 1
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failures.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return {"status": "PASS" if not failures else "FAIL", "checked": checked, "failures": failures}


def verify_json_artifacts(root: str | Path) -> dict[str, Any]:
    base = Path(root)
    failures = []
    checked = 0
    for path in sorted(base.rglob("*.json")):
        relative = path.relative_to(base)
        if any(part in VERIFICATION_EXCLUDES for part in relative.parts):
            continue
        checked += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(
                {
                    "path": relative.as_posix(),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return {"status": "PASS" if not failures else "FAIL", "checked": checked, "failures": failures}


def verify_project(
    project_root: str | Path,
    output_path: str | Path | None = None,
    check_manifest: bool = True,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    checks: dict[str, Any] = {
        "python_sources": verify_python_sources(root),
        "json_artifacts": verify_json_artifacts(root),
    }
    manifest = root / "MANIFEST.json"
    if check_manifest and manifest.is_file():
        checks["manifest"] = verify_manifest(root, manifest)
    status = "PASS" if all(value.get("status") == "PASS" for value in checks.values()) else "FAIL"
    report = {
        "schema": "osl.micro-emergence.project-verification.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_root": ".",
        "status": status,
        "checks": checks,
        "environment": _portable_environment(),
    }
    if output_path:
        save_json(output_path, report)
    return report
