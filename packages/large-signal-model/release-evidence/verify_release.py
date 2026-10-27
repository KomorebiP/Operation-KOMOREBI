"""Verify the exact handoff files listed in MANIFEST.json. No network operations."""
from pathlib import Path
import argparse
import hashlib
import json

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--strict", action="store_true")
args = parser.parse_args()
data = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
errors = []
expected = set()
for row in data["files"]:
    relative = Path(row["path"])
    if relative.is_absolute() or ".." in relative.parts:
        errors.append("invalid manifest path")
        continue
    expected.add(relative.as_posix())
    path = root / relative
    if not path.is_file():
        errors.append("missing: " + relative.as_posix())
    elif path.stat().st_size != row["bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
        errors.append("changed: " + relative.as_posix())
actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
extras = sorted(actual - expected - {"MANIFEST.json"})
if args.strict and extras:
    errors.append("unlisted files present")
print(json.dumps({"ok": not errors, "verified_files": len(expected), "extra_files": extras, "errors": errors}, indent=2))
raise SystemExit(0 if not errors else 1)
