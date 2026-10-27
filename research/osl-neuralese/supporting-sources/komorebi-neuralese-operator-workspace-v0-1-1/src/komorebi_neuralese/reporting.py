from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tree_digest(root: Path, relative_paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(relative_paths, key=lambda value: value.as_posix()):
        path = root / relative
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def source_files(root: Path) -> list[Path]:
    selected: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts[0] in {"results", ".git", "__pycache__"}:
            continue
        if path.suffix.lower() in {".py", ".md", ".txt", ".toml", ".ps1", ".json"}:
            selected.append(relative)
    return selected


def flatten_metrics(prefix: str, value: Any, output: dict[str, Any]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            flatten_metrics(f"{prefix}.{key}" if prefix else str(key), child, output)
    elif isinstance(value, (str, int, float, bool)) or value is None:
        output[prefix] = value


def arm_summary(record: dict[str, Any]) -> dict[str, float]:
    evaluation = record["evaluation"]
    d4 = evaluation["accuracy"]["d4"]
    c8 = evaluation["accuracy"]["c8"]
    random_family = evaluation["accuracy"]["random"]
    relations = evaluation["relations"]
    paths = evaluation["equivalent_paths"]
    interventions = evaluation["interventions"]
    output: dict[str, float] = {
        "d4_id_mean": mean(d4[str(length)] for length in (1, 2, 3, 4)),
        "d4_long_mean": mean(d4[str(length)] for length in (8, 10, 12)),
        "d4_length_12": d4["12"],
        "c8_id_mean": mean(c8[str(length)] for length in (1, 2, 3, 4)),
        "c8_length_12": c8["12"],
        "random_id_mean": mean(random_family[str(length)] for length in (1, 2, 3, 4)),
        "relation_endpoint_mean": mean(item["endpoint_accuracy"] for item in relations.values()),
        "equivalent_path_exact_mean": mean(item["both_paths_exact"] for item in paths.values()),
    }
    hidden_residuals = [
        item["hidden_return_normalized_l2_mean"]
        for item in relations.values()
        if item["hidden_return_normalized_l2_mean"] is not None
    ]
    if hidden_residuals:
        output["relation_hidden_residual_mean"] = mean(hidden_residuals)
    if interventions.get("available"):
        output.update(
            {
                "state_patch_accuracy": interventions["state_patch_accuracy"],
                "random_state_patch_accuracy": interventions["random_state_patch_accuracy"],
                "random_absolute_state_accuracy": interventions["random_absolute_state_accuracy"],
                "operator_patch_accuracy": interventions["operator_patch_accuracy"],
                "random_operator_patch_accuracy": interventions["random_operator_patch_accuracy"],
                "zero_state_lesion_original_accuracy": interventions["zero_state_lesion_original_accuracy"],
                "native_original_accuracy": interventions["native_original_accuracy"],
                "state_patch_margin": interventions["state_patch_accuracy"] - interventions["random_state_patch_accuracy"],
                "operator_patch_margin": interventions["operator_patch_accuracy"] - interventions["random_operator_patch_accuracy"],
            }
        )
    return output


def aggregate_arms(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {}
    for arm_name, arm_records in records.items():
        summaries = [arm_summary(record) for record in arm_records]
        keys = sorted(set.intersection(*(set(summary) for summary in summaries)))
        aggregate[arm_name] = {
            key: {
                "mean": mean(float(summary[key]) for summary in summaries),
                "std": pstdev(float(summary[key]) for summary in summaries) if len(summaries) > 1 else 0.0,
                "n": len(summaries),
            }
            for key in keys
        }
    return aggregate


def write_summary_csv(path: Path, records: dict[str, list[dict[str, Any]]]) -> None:
    rows: list[dict[str, Any]] = []
    for arm_name, arm_records in records.items():
        for record in arm_records:
            row: dict[str, Any] = {
                "arm": arm_name,
                "seed": record["config"]["seed"],
                "model": record["config"]["model_name"],
                "regime": record["config"]["regime"],
                "parameters": record["training"]["parameter_count"],
                "elapsed_seconds": record["training"]["elapsed_seconds"],
            }
            row.update(arm_summary(record))
            rows.append(row)
    fieldnames = sorted(set().union(*(row.keys() for row in rows)))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown_report(
    profile: str,
    source_digest: str,
    aggregate: dict[str, Any],
    gates: dict[str, Any],
    transport: dict[str, Any] | None,
) -> str:
    lines = [
        "# Neuralese Operator Workspace: Initial Test Report",
        "",
        f"**Profile:** `{profile}`  ",
        f"**Frozen source digest:** `{source_digest}`",
        "",
        "## Behavioral and causal summary",
        "",
        "| Arm | D4 ID | D4 long | C8 ID | Random-family ID | Relation endpoint | State patch | Matched state control | Operator patch | Random operator control |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm, metrics in aggregate.items():
        def get(name: str) -> str:
            item = metrics.get(name)
            return "—" if item is None else f"{item['mean']:.4f}"
        lines.append(
            f"| {arm} | {get('d4_id_mean')} | {get('d4_long_mean')} | {get('c8_id_mean')} | "
            f"{get('random_id_mean')} | {get('relation_endpoint_mean')} | {get('state_patch_accuracy')} | "
            f"{get('random_state_patch_accuracy')} | {get('operator_patch_accuracy')} | "
            f"{get('random_operator_patch_accuracy')} |"
        )
    lines.extend(["", "## Frozen development gates", ""])
    for name, gate in gates.items():
        status = "PASS" if gate["passed"] else "FAIL"
        lines.append(f"- **{status}** `{name}`: observed `{gate['observed']:.6f}`, criterion `{gate['criterion']}`")
    if transport is not None:
        lines.extend(["", "## Cross-seed coordinate transport", ""])
        by_family = transport.get("by_family")
        if by_family:
            lines.extend(
                [
                    "The affine map was fitted only on D4 trajectories of lengths 1 through 4, then tested on new episodes.",
                    "",
                    "| Test family | Native continuation | Aligned source patch | Random-map control | Hidden R² | Intertwining cosine |",
                    "|---|---:|---:|---:|---:|---:|",
                ]
            )
            for family, metrics in by_family.items():
                lines.append(
                    f"| {family} | {metrics['target_native_accuracy']:.4f} | "
                    f"{metrics['aligned_state_patch_accuracy']:.4f} | "
                    f"{metrics['random_map_state_patch_accuracy']:.4f} | "
                    f"{metrics['heldout_hidden_r2']:.4f} | "
                    f"{metrics['empirical_intertwining_cosine_mean']:.4f} |"
                )
        else:
            lines.extend(
                [
                    f"- Held-out hidden-state R²: `{transport['heldout_hidden_r2']:.6f}`",
                    f"- Aligned state-patch accuracy: `{transport['aligned_state_patch_accuracy']:.6f}`",
                    f"- Random-map state-patch accuracy: `{transport['random_map_state_patch_accuracy']:.6f}`",
                    f"- Empirical intertwining cosine: `{transport['empirical_intertwining_cosine_mean']:.6f}`",
                    f"- Empirical intertwining normalized L2: `{transport['empirical_intertwining_normalized_l2_mean']:.6f}`",
                ]
            )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "This is a controlled finite-state development assay. The linear-hypernetwork arm is intentionally biased toward a latent operator representation. Success demonstrates learned coordinate alignment, recurrent composition, causal state/operator use, and transportability under the tested distribution. It does not establish spontaneous Neuralese, natural-language-model internals, consciousness, or unrestricted operator discovery.",
            "",
        ]
    )
    return "\n".join(lines)
