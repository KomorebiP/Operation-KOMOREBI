#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    build = json.loads((HERE / "results/BUILD_VERIFICATION.json").read_text())
    failures: list[str] = []

    for key in (
        "axiom_audit_status",
        "predecessor_replay_status",
    ):
        if build.get(key) != "PASS":
            failures.append(f"{key} is not PASS")
    for key in ("kernel_controls", "static_source_audit", "finite_audit"):
        if build.get(key, {}).get("status") != "PASS":
            failures.append(f"{key}.status is not PASS")

    for rel, expected in build["source_sha256"].items():
        path = HERE / rel
        if not path.exists():
            failures.append(f"missing source: {rel}")
        elif sha256(path) != expected:
            failures.append(f"source hash mismatch: {rel}")

    for item in build["compiled_artifacts"]:
        path = HERE / item["path"]
        if not path.exists():
            # Compiled evidence is also retained in compiled_rc2 after staging.
            alt = HERE / "compiled_rc2" / Path(item["path"]).relative_to(".lake/build/lib/lean")
            path = alt
        if not path.exists():
            failures.append(f"missing compiled artifact: {item['path']}")
        elif sha256(path) != item["sha256"]:
            failures.append(f"compiled artifact hash mismatch: {item['path']}")

    required_logs = {
        "logs/lake_build_fresh_warning_as_error.log": "Build completed successfully",
        "logs/verify_all.log": "Block 05 verification passed.",
    }
    for rel, token in required_logs.items():
        path = HERE / rel
        if not path.exists() or token not in path.read_text(errors="replace"):
            failures.append(f"missing success token in {rel}")

    result = {
        "schema_version": 1,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "checked_sources": len(build["source_sha256"]),
        "checked_compiled_artifacts": len(build["compiled_artifacts"]),
    }
    (HERE / "results/release_integrity.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
