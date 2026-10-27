"""Fail closed until the owner records a public license choice in the metadata.

This is an engineering interlock, not legal advice or a license compliance audit.
"""
from pathlib import Path
import json
import tomllib

root = Path(__file__).resolve().parents[1]
license_id = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["license"]
allowed = license_id != "LicenseRef-Proprietary"
print(json.dumps({"public_release_enabled": allowed, "license": license_id,
                  "reason": "owner license decision required" if not allowed else
                            "metadata gate passed; owner must review third-party notices"}, indent=2))
raise SystemExit(0 if allowed else 2)
