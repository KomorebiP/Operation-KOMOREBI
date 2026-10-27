#!/usr/bin/env python3
"""Deterministic, seed-paired post-hoc summaries for a completed v0.3 run.

This program is deliberately outside the immutable code digest.  It does not
alter the primary run.  It verifies the run receipts, reads per-seed records,
and writes a descriptive (not confirmatory) paired-bootstrap analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable

import numpy as np


DEFAULT_REPLICATES = 100_000


@dataclass(frozen=True)
class MetricSpec:
    path: str
    label: str
    category: str


CURATED_METRICS = (
    MetricSpec("closure.deep_stability.by_depth.8.endpoint_accuracy", "D4 endpoint accuracy, depth 8", "behavior"),
    MetricSpec("closure.deep_stability.by_depth.64.endpoint_accuracy", "D4 endpoint accuracy, depth 64", "behavior"),
    MetricSpec("closure.deep_stability.by_depth.128.endpoint_accuracy", "D4 endpoint accuracy, depth 128", "behavior"),
    MetricSpec("c8_deep_stability.by_depth.64.endpoint_accuracy", "C8 endpoint accuracy, depth 64", "behavior"),
    MetricSpec("random_deep_stability.by_depth.64.endpoint_accuracy", "Random-family endpoint accuracy, depth 64", "behavior"),
    MetricSpec("extended_stability.d4.by_depth.2048.finite_trajectory_fraction", "D4 finite trajectories, depth 2048", "stability"),
    MetricSpec("extended_stability.d4.by_depth.2048.g_endpoint_ratio.median", "D4 G-norm endpoint ratio, depth 2048", "stability"),
    MetricSpec("extended_stability.d4.by_depth.2048.g_step_ratio.minimum", "D4 minimum G-norm step ratio, depth 2048", "stability"),
    MetricSpec("extended_stability.d4.by_depth.2048.g_transient_gain.p95", "D4 P95 G-transient gain, depth 2048", "stability"),
    MetricSpec("hard_operator_health.d4.intrinsic_orthogonality_defect.p95", "D4 hard-operator P95 orthogonality defect", "stability"),
    MetricSpec("hard_operator_health.d4.intrinsic_minimum_singular_value.minimum", "D4 hard-operator minimum singular value", "stability"),
    MetricSpec("closure.anonymous_composition.true_substitution_accuracy", "True composition substitution accuracy", "closure"),
    MetricSpec("closure.anonymous_composition.true_substitution_output_agreement", "Sequential/direct output agreement", "closure"),
    MetricSpec("closure.anonymous_composition.metric_operator_closure_residual.median", "Median operator closure residual", "closure"),
    MetricSpec("closure.anonymous_composition.native_two_step_accuracy", "Native two-step accuracy", "closure"),
    MetricSpec("closure.cross_context_patch.recipient_native_accuracy", "Recipient-native accuracy", "cross_context"),
    MetricSpec("closure.cross_context_patch.cross_context_state_patch_accuracy", "Cross-context state-patch accuracy", "cross_context"),
    MetricSpec("closure.cross_context_patch.on_manifold_wrong_state_control_accuracy", "On-manifold wrong-state control accuracy", "cross_context"),
    MetricSpec("closure.cross_context_patch.cross_context_patch_margin", "Cross-context patch margin", "cross_context"),
    MetricSpec("split_conditioned_final_action.endpoint_accuracy", "Split-conditioned final-action accuracy", "split_boundary"),
)


DEFAULT_CONTRASTS = (
    ("hard_correct", "hard_shuffled", "hard correct minus hard shuffled"),
    ("hard_correct", "soft_correct", "hard correct minus soft correct"),
    ("soft_correct", "soft_shuffled", "soft correct minus soft shuffled"),
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        raise RuntimeError(f"could not parse JSON file {path}: {error}") from error


def _metric(value: Any, dotted_path: str) -> float:
    current = value
    for component in dotted_path.split("."):
        if not isinstance(current, dict) or component not in current:
            raise KeyError(dotted_path)
        current = current[component]
    if isinstance(current, bool) or not isinstance(current, (int, float)):
        raise TypeError(f"metric {dotted_path!r} is not numeric")
    number = float(current)
    if not math.isfinite(number):
        raise ValueError(f"metric {dotted_path!r} is not finite")
    return number


def _protocol_metric_specs(protocol: dict[str, Any]) -> tuple[MetricSpec, ...]:
    specs = {item.path: item for item in CURATED_METRICS}
    for gate in protocol.get("gates", []):
        if gate.get("source", "arm") != "arm" or not isinstance(gate.get("metric"), str):
            continue
        path = gate["metric"]
        specs.setdefault(path, MetricSpec(path, f"Gate metric: {path}", "frozen_gate"))
    return tuple(specs[path] for path in sorted(specs))


def _load_primary(primary_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[int, dict[str, Any]]], dict[str, Any]]:
    primary_dir = primary_dir.resolve()
    required = [primary_dir / "PROTOCOL.json", primary_dir / "RECEIPT.json", primary_dir / "GRID_AUDIT.json"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"primary run is incomplete; missing required files: {missing}")
    protocol_path, receipt_path, grid_path = required
    protocol = _read_json(protocol_path)
    receipt = _read_json(receipt_path)
    grid = _read_json(grid_path)
    if receipt.get("status") != "complete":
        raise RuntimeError(f"primary receipt status is not complete: {receipt.get('status')!r}")
    if receipt.get("grid_complete") is not True or grid.get("complete") is not True:
        raise RuntimeError("primary grid receipt is not complete")
    protocol_sha = _file_sha256(protocol_path)
    if receipt.get("protocol_digest") != protocol_sha:
        raise RuntimeError("primary receipt protocol digest does not match PROTOCOL.json")
    expected_arms = list(protocol.get("arms", {}))
    expected_seeds = [int(seed) for seed in protocol.get("seeds", [])]
    if not expected_arms or not expected_seeds:
        raise RuntimeError("primary protocol has an empty arm or seed grid")
    if receipt.get("arms") != expected_arms or [int(seed) for seed in receipt.get("seeds", [])] != expected_seeds:
        raise RuntimeError("primary receipt arm/seed grid differs from PROTOCOL.json")

    records: dict[str, dict[int, dict[str, Any]]] = {}
    inventory: list[dict[str, Any]] = []
    receipt_code = receipt.get("code_digest")
    receipt_split = receipt.get("coordinate_split_digest")
    for arm in expected_arms:
        records[arm] = {}
        for seed in expected_seeds:
            path = primary_dir / "arms" / arm / f"seed_{seed}.json"
            if not path.is_file():
                raise RuntimeError(f"missing expected primary cell: {path}")
            record = _read_json(path)
            checks = {
                "arm": record.get("arm") == arm,
                "seed": record.get("seed") == seed,
                "protocol_digest": record.get("protocol_digest") == protocol_sha,
                "code_digest": record.get("code_digest") == receipt_code,
                "coordinate_split_digest": record.get("coordinate_split_digest") == receipt_split,
            }
            if not all(checks.values()):
                raise RuntimeError(f"primary cell receipt mismatch for {path}: {checks}")
            records[arm][seed] = record
            inventory.append({"arm": arm, "seed": seed, "path": path.relative_to(primary_dir).as_posix(), "sha256": _file_sha256(path)})
    observed = sorted((path.parent.name, path.stem) for path in (primary_dir / "arms").glob("*/seed_*.json"))
    if len(observed) != len(expected_arms) * len(expected_seeds):
        raise RuntimeError("unexpected extra or duplicate arm JSON records are present")
    content_receipt = {
        "protocol_sha256": protocol_sha,
        "receipt_sha256": _file_sha256(receipt_path),
        "grid_audit_sha256": _file_sha256(grid_path),
        "code_digest": receipt_code,
        "coordinate_split_digest": receipt_split,
        "inventory": inventory,
    }
    provenance = {
        "primary_directory": str(primary_dir),
        **content_receipt,
        # Exclude the absolute path from this digest so moving an identical
        # package does not alter the bootstrap stream.
        "analysis_input_sha256": _sha256_bytes(_canonical_bytes(content_receipt)),
    }
    return protocol, receipt, records, provenance


def _bootstrap_seed(input_sha: str, spec: dict[str, Any]) -> tuple[int, str]:
    material = bytes.fromhex(input_sha) + b"\0" + _canonical_bytes(spec)
    digest = hashlib.sha256(material).digest()
    # PCG64 accepts a Python integer seed.  Use all 256 SHA bits, with the
    # hexadecimal value recorded so implementations can reproduce it exactly.
    return int.from_bytes(digest, "big"), digest.hex()


def _paired_bootstrap(deltas: np.ndarray, replicates: int, rng: np.random.Generator) -> np.ndarray:
    if deltas.ndim != 1 or deltas.size == 0:
        raise ValueError("paired deltas must be a nonempty vector")
    output = np.empty(replicates, dtype=np.float64)
    chunk = min(10_000, replicates)
    for start in range(0, replicates, chunk):
        stop = min(start + chunk, replicates)
        indices = rng.integers(0, deltas.size, size=(stop - start, deltas.size), dtype=np.int64)
        output[start:stop] = deltas[indices].mean(axis=1)
    return output


def _number_summary(values: Iterable[float]) -> dict[str, Any]:
    data = [float(value) for value in values]
    return {
        "n": len(data),
        "mean": mean(data),
        "population_std": pstdev(data) if len(data) > 1 else 0.0,
        "minimum": min(data),
        "maximum": max(data),
        "values": data,
    }


def analyze(primary_dir: Path, output_dir: Path, replicates: int = DEFAULT_REPLICATES) -> dict[str, Any]:
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    protocol, receipt, records, provenance = _load_primary(primary_dir)
    expected_seeds = [int(seed) for seed in protocol["seeds"]]
    metrics = _protocol_metric_specs(protocol)
    arm_summaries: dict[str, Any] = {}
    unavailable: list[dict[str, Any]] = []
    for arm, by_seed in records.items():
        arm_summaries[arm] = {}
        for metric_spec in metrics:
            values: list[float] = []
            bad: list[dict[str, Any]] = []
            for seed in expected_seeds:
                try:
                    values.append(_metric(by_seed[seed]["metrics"], metric_spec.path))
                except (KeyError, TypeError, ValueError) as error:
                    bad.append({"seed": seed, "reason": str(error)})
            if bad:
                unavailable.append({"kind": "arm_summary", "arm": arm, "metric": metric_spec.path, "issues": bad})
            else:
                arm_summaries[arm][metric_spec.path] = {
                    "label": metric_spec.label,
                    "category": metric_spec.category,
                    **_number_summary(values),
                    "seed_order": expected_seeds,
                }

    contrast_specs: list[dict[str, Any]] = []
    for left, right, label in DEFAULT_CONTRASTS:
        contrast_specs.append({"left_arm": left, "right_arm": right, "label": label})
    # Every prospectively frozen paired-delta gate should be represented even if
    # it was not in the curated list above.
    for gate in protocol.get("gates", []):
        if gate.get("source", "arm") == "arm" and gate.get("operator") == "delta_ge":
            candidate = {"left_arm": str(gate["arm"]), "right_arm": str(gate["comparator_arm"]), "label": f"frozen gate {gate['id']}"}
            if not any(item["left_arm"] == candidate["left_arm"] and item["right_arm"] == candidate["right_arm"] for item in contrast_specs):
                contrast_specs.append(candidate)

    contrasts: list[dict[str, Any]] = []
    for contrast in contrast_specs:
        left = contrast["left_arm"]
        right = contrast["right_arm"]
        if left not in records or right not in records:
            unavailable.append({"kind": "contrast", **contrast, "reason": "arm absent from protocol"})
            continue
        for metric_spec in metrics:
            paired: list[dict[str, Any]] = []
            issues: list[dict[str, Any]] = []
            for seed in expected_seeds:
                try:
                    left_value = _metric(records[left][seed]["metrics"], metric_spec.path)
                    right_value = _metric(records[right][seed]["metrics"], metric_spec.path)
                    paired.append({"seed": seed, "left": left_value, "right": right_value, "delta": left_value - right_value})
                except (KeyError, TypeError, ValueError) as error:
                    issues.append({"seed": seed, "reason": str(error)})
            if issues:
                unavailable.append({"kind": "contrast_metric", **contrast, "metric": metric_spec.path, "issues": issues})
                continue
            spec = {
                "analysis": "paired_seed_bootstrap_mean_delta",
                "left_arm": left,
                "right_arm": right,
                "metric": metric_spec.path,
                "seed_order": expected_seeds,
                "replicates": replicates,
                "ci": {"method": "percentile", "probability": 0.95, "quantile_method": "linear"},
            }
            seed_value, seed_sha = _bootstrap_seed(provenance["analysis_input_sha256"], spec)
            delta_vector = np.asarray([item["delta"] for item in paired], dtype=np.float64)
            bootstrap = _paired_bootstrap(delta_vector, replicates, np.random.Generator(np.random.PCG64(seed_value)))
            low, high = np.quantile(bootstrap, [0.025, 0.975], method="linear")
            contrasts.append(
                {
                    "label": contrast["label"],
                    "category": metric_spec.category,
                    "metric": metric_spec.path,
                    "metric_label": metric_spec.label,
                    "left_arm": left,
                    "right_arm": right,
                    "n_pairs": len(paired),
                    "seed_order": expected_seeds,
                    "left_mean": float(np.mean([item["left"] for item in paired])),
                    "right_mean": float(np.mean([item["right"] for item in paired])),
                    "observed_mean_delta": float(delta_vector.mean()),
                    "paired_deltas": [float(value) for value in delta_vector],
                    "bootstrap": {
                        "generator": "numpy.random.Generator(numpy.random.PCG64)",
                        "seed_derivation": "uint256(big-endian, SHA256(analysis_input_sha256_bytes || NUL || canonical_contrast_spec_json))",
                        "seed_sha256": seed_sha,
                        "replicates": replicates,
                        "statistic": "mean of seed-paired deltas",
                        "ci_method": "95% percentile interval; numpy.quantile(method='linear')",
                        "ci_95": [float(low), float(high)],
                    },
                }
            )

    result: dict[str, Any] = {
        "schema_version": 1,
        "analysis_id": "komorebi-v0.3-posthoc-seed-paired-bootstrap",
        "analysis_status": "posthoc_descriptive_not_preregistered_not_a_frozen_gate",
        "interpretation_boundary": (
            "These intervals are exploratory summaries over the completed finite seed grid. "
            "They do not retroactively create confirmatory tests, p-values, population guarantees, "
            "or multiplicity-adjusted evidence. A paired unit is one shared training seed."
        ),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "primary_receipt_status": receipt.get("status"),
        "protocol_id": protocol.get("protocol_id"),
        "replicates_per_contrast_metric": replicates,
        "provenance": provenance,
        "arm_summaries": arm_summaries,
        "contrasts": contrasts,
        "unavailable_metrics": unavailable,
    }
    semantic_receipt = dict(result)
    semantic_receipt.pop("created_utc")
    result["analysis_payload_sha256"] = _sha256_bytes(_canonical_bytes(semantic_receipt))

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "POSTHOC_DESCRIPTIVE.json"
    md_path = output_dir / "POSTHOC_DESCRIPTIVE.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(result), encoding="utf-8")
    return result


def _render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Post-hoc seed-paired descriptive analysis",
        "",
        f"**Status:** `{result['analysis_status']}`  ",
        f"**Bootstrap replicates per metric and contrast:** `{result['replicates_per_contrast_metric']:,}`  ",
        f"**Primary protocol:** `{result['protocol_id']}`  ",
        f"**Analysis input SHA-256:** `{result['provenance']['analysis_input_sha256']}`",
        "",
        result["interpretation_boundary"],
        "",
        "Each interval resamples shared seed pairs and summarizes the mean of left-minus-right deltas. "
        "Every PCG64 seed is independently derived from the immutable analysis-input hash and the canonical contrast specification.",
        "",
        "## Paired contrasts",
        "",
        "| Category | Metric | Contrast | Left mean | Right mean | Mean delta | 95% percentile CI | n |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in result["contrasts"]:
        low, high = item["bootstrap"]["ci_95"]
        lines.append(
            f"| {item['category']} | {item['metric_label']} | {item['left_arm']} - {item['right_arm']} | "
            f"{item['left_mean']:.6g} | {item['right_mean']:.6g} | {item['observed_mean_delta']:.6g} | "
            f"[{low:.6g}, {high:.6g}] | {item['n_pairs']} |"
        )
    lines.extend(
        [
            "",
            "## Completeness",
            "",
            f"- Available paired metric/contrast analyses: `{len(result['contrasts'])}`",
            f"- Structurally unavailable arm or contrast metrics recorded: `{len(result['unavailable_metrics'])}`",
            "- Full seed-level values, paired deltas, hashes, and per-analysis RNG receipts are in `POSTHOC_DESCRIPTIVE.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_self_check_fixture(root: Path) -> tuple[Path, Path]:
    primary = root / "primary"
    output = root / "output"
    protocol = {
        "protocol_id": "synthetic-self-check",
        "seeds": [1, 2, 3, 4],
        "arms": {name: {"model_name": "synthetic"} for name in ("hard_correct", "hard_shuffled", "soft_correct", "soft_shuffled")},
        "gates": [],
    }
    protocol_bytes = json.dumps(protocol, indent=2, sort_keys=True).encode() + b"\n"
    primary.mkdir(parents=True)
    (primary / "PROTOCOL.json").write_bytes(protocol_bytes)
    protocol_sha = _sha256_bytes(protocol_bytes)
    receipt = {
        "status": "complete",
        "grid_complete": True,
        "protocol_digest": protocol_sha,
        "code_digest": "a" * 64,
        "coordinate_split_digest": "b" * 64,
        "arms": list(protocol["arms"]),
        "seeds": protocol["seeds"],
    }
    (primary / "RECEIPT.json").write_text(json.dumps(receipt), encoding="utf-8")
    (primary / "GRID_AUDIT.json").write_text(json.dumps({"complete": True}), encoding="utf-8")
    offsets = {"hard_correct": 0.8, "hard_shuffled": 0.4, "soft_correct": 0.6, "soft_shuffled": 0.3}
    for arm, offset in offsets.items():
        for seed in protocol["seeds"]:
            record = {
                "arm": arm,
                "seed": seed,
                "protocol_digest": protocol_sha,
                "code_digest": receipt["code_digest"],
                "coordinate_split_digest": receipt["coordinate_split_digest"],
                "metrics": {"closure": {"deep_stability": {"by_depth": {"8": {"endpoint_accuracy": offset + seed / 1000}}}}},
            }
            path = primary / "arms" / arm / f"seed_{seed}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(record), encoding="utf-8")
    return primary, output


def self_check() -> None:
    with tempfile.TemporaryDirectory(prefix="komorebi-bootstrap-self-check-") as temporary:
        primary, output = _write_self_check_fixture(Path(temporary))
        first = analyze(primary, output, replicates=2_000)
        second_output = Path(temporary) / "output_2"
        second = analyze(primary, second_output, replicates=2_000)
        if not first["contrasts"]:
            raise RuntimeError("self-check generated no paired contrasts")
        left = [(x["metric"], x["left_arm"], x["right_arm"], x["bootstrap"]) for x in first["contrasts"]]
        right = [(x["metric"], x["left_arm"], x["right_arm"], x["bootstrap"]) for x in second["contrasts"]]
        if left != right:
            raise RuntimeError("deterministic replay of bootstrap summaries differed")
        expected = next(x for x in first["contrasts"] if x["left_arm"] == "hard_correct" and x["right_arm"] == "hard_shuffled")
        if not math.isclose(expected["observed_mean_delta"], 0.4, abs_tol=1e-12):
            raise RuntimeError("paired delta arithmetic self-check failed")
    print("paired_bootstrap self-check: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-dir", type=Path, help="completed primary result directory")
    parser.add_argument("--output-dir", type=Path, help="directory for POSTHOC_DESCRIPTIVE outputs")
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        if args.primary_dir is not None or args.output_dir is not None:
            parser.error("--self-check cannot be combined with --primary-dir or --output-dir")
        self_check()
        return 0
    if args.primary_dir is None or args.output_dir is None:
        parser.error("--primary-dir and --output-dir are required unless --self-check is used")
    result = analyze(args.primary_dir, args.output_dir, args.replicates)
    print(json.dumps({
        "status": "complete",
        "analysis_input_sha256": result["provenance"]["analysis_input_sha256"],
        "contrasts": len(result["contrasts"]),
        "unavailable_metrics": len(result["unavailable_metrics"]),
        "replicates": result["replicates_per_contrast_metric"],
        "output_dir": str(args.output_dir.resolve()),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
