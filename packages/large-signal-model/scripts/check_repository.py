"""Check the release source without importing the runtime or making network calls.

This is a packaging/consistency check, not a security audit or type checker.
Historical reference documents deliberately retain their original versions.
"""
from __future__ import annotations
import argparse
import ast
import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "2.3.0"
SKIP = {".git", "__pycache__", ".pytest_cache", "build", "dist", "results", ".venv"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distribution", action="store_true",
                        help="also reject build outputs, caches and optional local game fixtures")
    args = parser.parse_args()
    errors: list[str] = []
    checked_python = 0
    checked_links = 0
    required = [
        "README.md", "LICENSE", "CITATION.cff", "pyproject.toml", "RELEASE_AUDIT.md",
        "REPRODUCIBILITY.md", "docs/RELEASE_GUIDE.md", "docs/RELEASE_GUIDE.pdf",
        "src/komorebi_pr_lasm/__init__.py", "src/komorebi_arc3_offline/__init__.py",
        ".github/workflows/ci.yml", ".github/workflows/release.yml",
        "paper/Projector_Resolved_Large_Algebraic_Signal_Model.pdf",
        "verification/SOURCE_LINEAGE.json", "verification/current_stress/summary.json",
    ]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f"missing required path: {name}")
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if project["version"] != EXPECTED_VERSION:
        errors.append("pyproject version mismatch")
    for name in ("src/komorebi_pr_lasm/__init__.py", "src/komorebi_arc3_offline/__init__.py"):
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
        versions = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "__version__" for t in n.targets)]
        if versions != [EXPECTED_VERSION]:
            errors.append(f"version mismatch: {name}")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if not re.search(rf'^version:\s*["\']?{re.escape(EXPECTED_VERSION)}["\']?\s*$', citation, re.M):
        errors.append("CITATION.cff version mismatch")
    for area in ("src", "tests", "examples", "scripts"):
        for path in (ROOT / area).rglob("*.py"):
            if any(p in SKIP for p in path.relative_to(ROOT).parts):
                continue
            try:
                ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
                checked_python += 1
            except (SyntaxError, UnicodeError) as exc:
                errors.append(f"syntax: {path.relative_to(ROOT)}: {exc}")
    # Only current documentation links are checked. Archival paper/reference links
    # may intentionally refer to publications outside this repository.
    for path in list(ROOT.glob("*.md")) + list((ROOT / "docs").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            local = target.split("#", 1)[0]
            if not local:
                continue
            checked_links += 1
            if not (path.parent / local).exists():
                errors.append(f"broken local link in {path.name}: {target}")
    if (ROOT / ".env").exists():
        errors.append("sensitive .env file present")
    if args.distribution:
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if any(p in {"__pycache__", ".pytest_cache", "build", "dist", "results", ".git", ".venv"}
                   for p in relative.parts) or path.suffix in {".pyc", ".pyo"}:
                errors.append(f"generated path present: {relative}")
        env = ROOT / "environment_files"
        if any(p.is_file() and p.name != "README.md" for p in env.rglob("*")):
            errors.append("optional local game fixtures must not enter the source release")
    result = {"ok": not errors, "version": EXPECTED_VERSION, "python_files_parsed": checked_python,
              "current_documentation_links_checked": checked_links,
              "distribution_mode": args.distribution,
              "license": project.get("license"), "errors": errors}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
