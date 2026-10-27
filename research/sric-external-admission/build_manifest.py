from __future__ import annotations

import json
from pathlib import Path

from sric_real_lrm.hashing import file_manifest, sha256_object

ROOT = Path(__file__).resolve().parent


def ignored(path: str) -> bool:
    parts = Path(path).parts
    return (
        path == "package_manifest.json"
        or ".pytest_cache" in parts
        or "__pycache__" in parts
        or "capture_cache" in parts
        or path.endswith(".pyc")
        or path.endswith(".pyo")
    )


rows = [row for row in file_manifest(ROOT, exclude={"package_manifest.json"}) if not ignored(row["path"])]
manifest = {
    "schema": "sric.block24.package-manifest.v1",
    "files": rows,
    "file_count": len(rows),
}
manifest["manifest_sha256"] = sha256_object({k: v for k, v in manifest.items() if k != "manifest_sha256"})
(ROOT / "package_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"MANIFEST_FILES={len(rows)}")
print(f"MANIFEST_SHA256={manifest['manifest_sha256']}")
