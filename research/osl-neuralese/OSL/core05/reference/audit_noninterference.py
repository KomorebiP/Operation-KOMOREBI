#!/usr/bin/env python3
"""Paired-trace noninterference audit for OSL-Core 0.5.

Two executions must differ in at least one registered secret.  The audit then
compares their declared public projections.  Equality is evidence for the
specific paired runs, not a universal proof over all possible executions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

try:  # pragma: no cover
    from .osl_core import run_program
    from .osl_model import digest
except ImportError:  # pragma: no cover
    from osl_core import run_program  # type: ignore
    from osl_model import digest  # type: ignore


def _diff(left: Any, right: Any, path: str = "$") -> list[dict[str, Any]]:
    if type(left) is not type(right):
        return [{"path": path, "left": left, "right": right, "reason": "type"}]
    if isinstance(left, dict):
        differences: list[dict[str, Any]] = []
        for key in sorted(set(left) | set(right)):
            if key not in left:
                differences.append(
                    {"path": f"{path}.{key}", "left": None, "right": right[key], "reason": "missing-left"}
                )
            elif key not in right:
                differences.append(
                    {"path": f"{path}.{key}", "left": left[key], "right": None, "reason": "missing-right"}
                )
            else:
                differences.extend(_diff(left[key], right[key], f"{path}.{key}"))
        return differences
    if isinstance(left, list):
        differences: list[dict[str, Any]] = []
        if len(left) != len(right):
            differences.append(
                {"path": path, "left": len(left), "right": len(right), "reason": "length"}
            )
        for index, (l_item, r_item) in enumerate(zip(left, right)):
            differences.extend(_diff(l_item, r_item, f"{path}[{index}]"))
        return differences
    if left != right:
        return [{"path": path, "left": left, "right": right, "reason": "value"}]
    return []


def audit(left_path: Path, right_path: Path) -> dict[str, Any]:
    left = run_program(left_path)
    right = run_program(right_path)
    if not left["ok"] or not right["ok"]:
        return {
            "schema": "osl.core.noninterference-audit.v1",
            "language_version": "OSL-Core 0.5",
            "ok": False,
            "noninterference": False,
            "reason": "one or both programs rejected",
            "left_error": left["error"],
            "right_error": right["error"],
        }

    left_secrets = left["state"]["secret_digests"]
    right_secrets = right["state"]["secret_digests"]
    changed_secrets = sorted(
        key
        for key in set(left_secrets) | set(right_secrets)
        if left_secrets.get(key) != right_secrets.get(key)
    )
    if not changed_secrets:
        return {
            "schema": "osl.core.noninterference-audit.v1",
            "language_version": "OSL-Core 0.5",
            "ok": False,
            "noninterference": False,
            "reason": "paired traces do not differ in any registered secret",
        }

    # public_digest itself is derived from the projection and would duplicate
    # the same difference.  Remove it before producing path-level diagnostics.
    left_public = dict(left["public"])
    right_public = dict(right["public"])
    left_public.pop("public_digest", None)
    right_public.pop("public_digest", None)
    differences = _diff(left_public, right_public)
    payload = {
        "schema": "osl.core.noninterference-audit.v1",
        "language_version": "OSL-Core 0.5",
        "ok": True,
        "left": str(left_path),
        "right": str(right_path),
        "changed_secret_names": changed_secrets,
        "noninterference": not differences,
        "difference_count": len(differences),
        "differences": differences,
        "left_public_digest": digest(left_public),
        "right_public_digest": digest(right_public),
        "claim_boundary": (
            "This is a paired-run audit over the declared public projection. "
            "It is not a universal noninterference proof over all programs."
        ),
    }
    payload["audit_digest"] = digest(payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit two OSL traces for public noninterference")
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = audit(args.left, args.right)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        status = "PASS" if result.get("noninterference") else "FAIL"
        print(
            f"OSL_NONINTERFERENCE_{status} changed_secrets="
            f"{','.join(result.get('changed_secret_names', []))} "
            f"differences={result.get('difference_count', 'n/a')}"
        )
    return 0 if result.get("ok") and result.get("noninterference") else 1


if __name__ == "__main__":
    raise SystemExit(main())
