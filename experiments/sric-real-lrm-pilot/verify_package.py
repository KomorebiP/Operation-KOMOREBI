from __future__ import annotations

import json
from pathlib import Path

from sric_real_lrm.hashing import sha256_file, sha256_object
from sric_real_lrm.receipts import load_and_verify_result
from sric_real_lrm.sealing import load_and_verify_seal

ROOT = Path(__file__).resolve().parent


def ignored(path: str) -> bool:
    parts = Path(path).parts
    return (
        path == "package_manifest.json"
        or ".pytest_cache" in parts
        or "__pycache__" in parts
        or path.endswith(".pyc")
        or path.endswith(".pyo")
    )


manifest_path = ROOT / "package_manifest.json"
if not manifest_path.is_file():
    raise SystemExit("package_manifest.json is missing")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
payload = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
if sha256_object(payload) != manifest["manifest_sha256"]:
    raise SystemExit("Manifest receipt mismatch")

manifested = {row["path"] for row in manifest["files"]}
actual = {
    path.relative_to(ROOT).as_posix()
    for path in ROOT.rglob("*")
    if path.is_file() and not ignored(path.relative_to(ROOT).as_posix())
}
if actual != manifested:
    missing = sorted(manifested - actual)
    unexpected = sorted(actual - manifested)
    raise SystemExit(f"Package closure mismatch; missing={missing}, unexpected={unexpected}")

for row in manifest["files"]:
    path = ROOT / row["path"]
    if path.stat().st_size != row["size"]:
        raise SystemExit(f"Size mismatch: {row['path']}")
    if sha256_file(path) != row["sha256"]:
        raise SystemExit(f"Hash mismatch: {row['path']}")

fake_result = ROOT / "results" / "fake_fixture_audit.json"
result = load_and_verify_result(fake_result)
if result.get("execution_boundary", {}).get("real_checkpoint_used") is not False:
    raise SystemExit("Fake fixture incorrectly marked as a real checkpoint")
if result["summary"]["status"] != "PROCEDURE_SPECIFIC":
    raise SystemExit("Fake fixture did not reach its engineered expected status")

load_and_verify_seal(ROOT / "frozen" / "fake_fixture_preaudit_seal.json")

print("SRIC_REAL_LRM_PILOT_PACKAGE_VALID")
print(f"manifest_files={manifest['file_count']}")
print(f"manifest_sha256={manifest['manifest_sha256']}")
