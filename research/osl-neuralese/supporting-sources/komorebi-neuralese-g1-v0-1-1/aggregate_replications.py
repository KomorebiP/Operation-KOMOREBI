from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

from neuralese_g1.integrity import atomic_json
from neuralese_g1.results import verify_run_directory


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return value


def _seedless_config(config: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(config)
    value.pop("seed", None)
    value.pop("config_digest", None)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate registered G1 replications")
    parser.add_argument("--runs", nargs="+", required=True, help="Pilot run directories")
    parser.add_argument("--output", required=True, help="Aggregate JSON destination")
    args = parser.parse_args()

    package_root = Path(__file__).resolve().parent
    roots = [Path(value).resolve() for value in args.runs]
    if len(set(roots)) != len(roots):
        raise RuntimeError("replication run directories must be distinct")
    destination = Path(args.output).resolve()
    if destination == package_root or package_root in destination.parents:
        raise RuntimeError("aggregate output must be outside the package directory")
    for root in roots:
        if destination == root or root in destination.parents:
            raise RuntimeError(
                f"aggregate output must not overwrite an input run: {root}"
            )
    entries: list[dict[str, Any]] = []
    reference_config: dict[str, Any] | None = None
    reference_model_hash: str | None = None
    reference_package_hash: str | None = None
    registered_seeds: set[int] | None = None
    for root in roots:
        verification = verify_run_directory(root)
        config = _read(root / "resolved_config.json")
        preflight = _read(root / "preflight.json")
        gates = _read(root / "gates.json")
        if config.get("profile") != "pilot":
            raise RuntimeError(f"non-pilot run supplied: {root}")
        if preflight.get("canonical_claim_eligible") is not True:
            raise RuntimeError(f"noncanonical pilot supplied: {root}")
        local_registered = {int(seed) for seed in config.get("replication_seeds", [])}
        if registered_seeds is None:
            registered_seeds = local_registered
        elif local_registered != registered_seeds:
            raise RuntimeError("registered seed sets differ across runs")
        normalized = _seedless_config(config)
        if reference_config is None:
            reference_config = normalized
        elif normalized != reference_config:
            raise RuntimeError("experimental configurations differ across replications")
        model_hash = str(preflight["model"]["metadata_sha256"])
        if reference_model_hash is None:
            reference_model_hash = model_hash
        elif model_hash != reference_model_hash:
            raise RuntimeError("model fingerprints differ across replications")
        package_hash = str(verification["package_manifest_sha256"])
        if reference_package_hash is None:
            reference_package_hash = package_hash
        elif package_hash != reference_package_hash:
            raise RuntimeError("package manifests differ across replications")
        entries.append(
            {
                "run": str(root),
                "seed": int(config["seed"]),
                "claim": gates["claim"],
                "verification": verification["status"],
                "config_digest": config["config_digest"],
            }
        )
    observed_seeds = {entry["seed"] for entry in entries}
    if (
        registered_seeds is None
        or observed_seeds != registered_seeds
        or len(entries) != len(registered_seeds)
    ):
        raise RuntimeError(
            f"replication seed coverage mismatch: expected={sorted(registered_seeds or [])}, "
            f"observed={sorted(entry['seed'] for entry in entries)}"
        )
    replicated = all(entry["claim"] == "G1_SINGLE_SEED_PILOT_PASS" for entry in entries)
    report = {
        "schema": "komorebi.neuralese.g1.replication.v1",
        "status": "G1_REPLICATED_PASS" if replicated else "G1_REPLICATION_NOT_ESTABLISHED",
        "registered_seeds": sorted(registered_seeds),
        "model_metadata_sha256": reference_model_hash,
        "package_manifest_sha256": reference_package_hash,
        "runs": sorted(entries, key=lambda entry: entry["seed"]),
        "interpretation_boundary": (
            "Replication applies only to the registered small-model late-binding task and "
            "does not establish general Neuralese or Astra parity."
        ),
    }
    atomic_json(destination, report)
    print(f"G1_REPLICATION_STATUS={report['status']}")
    print(f"OUTPUT={destination}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"G1_REPLICATION_INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
