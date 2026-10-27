"""Check the declared MIT publication metadata and retained third-party notice."""
from pathlib import Path
import json
import tomllib

root = Path(__file__).resolve().parents[1]
license_id = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["license"]
license_text = (root / "LICENSE").read_text(encoding="utf-8")
notices_present = (root / "THIRD_PARTY_NOTICES.md").is_file()
allowed = license_id == "MIT" and "MIT License" in license_text and "Komorebi P." in license_text and notices_present
print(json.dumps({"public_release_enabled": allowed, "license": license_id,
                  "third_party_notices_present": notices_present,
                  "reason": "MIT source metadata and third-party notice present" if allowed else
                            "publication metadata does not match the declared MIT release"}, indent=2))
raise SystemExit(0 if allowed else 2)
