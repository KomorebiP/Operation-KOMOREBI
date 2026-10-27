from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .adjudication import build_evidence_adjudication
from .utils import ensure_dir, load_json, save_json, sha256_file


def _find_json(root: Path, names: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    for name in names:
        found.extend(sorted(root.rglob(name)))
    return found


def _safe_load(path: Path) -> dict[str, Any]:
    try:
        return load_json(path)
    except Exception as exc:
        return {"load_error": f"{type(exc).__name__}: {exc}"}


def _metric_rows(payload: Any, prefix: str = "") -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_metric_rows(value, child))
    elif isinstance(payload, (int, float)) and not isinstance(payload, bool):
        rows.append((prefix, float(payload)))
    return rows


def _accuracy_rows(artifacts: list[dict[str, Any]]) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for artifact in artifacts:
        path = str(artifact["path"])
        content = artifact["content"]
        models = content.get("models", {}) if isinstance(content, dict) else {}
        if isinstance(models, dict):
            for name, model in sorted(models.items()):
                try:
                    rows.append((f"baseline:{name}", float(model["overall"]["accuracy"])))
                except (KeyError, TypeError, ValueError):
                    pass
        try:
            accuracy = float(content["behavior"]["overall"]["accuracy"])
        except (KeyError, TypeError, ValueError):
            continue
        experiment = Path(path).parent.name
        rows.append((experiment if experiment != "." else "neural", accuracy))
    return rows


def _make_accuracy_figure(
    rows: list[tuple[str, float]], output: Path
) -> str | None:
    if not rows:
        return None
    try:
        matplotlib_cache = Path(tempfile.gettempdir()) / "osl-matplotlib-cache"
        matplotlib_cache.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_cache))
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None
    figure_dir = ensure_dir(output / "figures")
    labels = [label for label, _ in rows]
    values = [value for _, value in rows]
    height = max(3.2, 0.42 * len(rows) + 1.4)
    figure, axis = plt.subplots(figsize=(9.5, height))
    positions = list(range(len(rows)))
    axis.barh(positions, values, color="#3a6ea5")
    axis.set_yticks(positions, labels=labels)
    axis.set_xlim(0.0, 1.0)
    axis.set_xlabel("Exact answer accuracy")
    axis.set_title("Implemented controls and neural experiments")
    axis.grid(axis="x", alpha=0.25)
    for position, value in zip(positions, values):
        axis.text(min(value + 0.015, 0.96), position, f"{value:.3f}", va="center")
    figure.tight_layout()
    destination = figure_dir / "accuracy_overview.png"
    figure.savefig(destination, dpi=160)
    plt.close(figure)
    return str(destination)


def build_report(
    run_dir: str | Path,
    output_dir: str | Path | None = None,
    *,
    make_figures: bool = True,
) -> dict[str, Any]:
    root = Path(run_dir)
    out = ensure_dir(output_dir or root / "reports")
    adjudication = build_evidence_adjudication(root)
    source_files = _find_json(
        root,
        (
            "manifest.json",
            "dataset_manifest.json",
            "validation_report.json",
            "baseline_results.json",
            "training_summary.json",
            "evaluation_results.json",
            "soft_quotient_results.json",
            "verification_report.json",
            "EVIDENCE_ADJUDICATION.json",
        ),
    )
    artifacts = [
        {
            "path": path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name,
            "content": _safe_load(path),
        }
        for path in source_files
    ]
    summarized_sources = []
    for item in artifacts:
        path = root / item["path"]
        metrics = _metric_rows(item["content"])
        summarized_sources.append(
            {
                "path": item["path"],
                "size_bytes": path.stat().st_size if path.is_file() else None,
                "sha256": sha256_file(path) if path.is_file() else None,
                "scalar_metrics": {key: value for key, value in metrics[:250]},
            }
        )
    summary = {
        "schema": "osl.micro-emergence.report.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": ".",
        "sources": summarized_sources,
    }
    save_json(out / "SUMMARY.json", summary)

    lines = [
        "# Micro OSL Offline Lab Report",
        "",
        "## Claim boundary",
        "",
        "This report distinguishes task learning, operator abstraction, held out composition, behavioral input intervention, and independently certified symbolic structure. Accuracy or latent decodability alone is not treated as evidence of spontaneous operator language emergence.",
        "",
        "Quotient outputs in this release are benchmark-only structural references unless an analysis is explicitly fitted to learned representations.",
        "",
        "## Behavioral gate adjudication",
        "",
        f"Overall behavioral status: **{adjudication['status']}**",
        "",
        "See `EVIDENCE_ADJUDICATION.json` and `EVIDENCE_ADJUDICATION.md` at the run root. A PASS means only that the answer-only arm met the configured behavioral gates for this run.",
        "",
        "## Collected artifacts",
        "",
    ]
    if not artifacts:
        lines.append("No result artifacts were found yet.")
    for item in artifacts:
        content = item["content"]
        lines.extend([f"### `{item['path']}`", ""])
        metrics = _metric_rows(content)
        if metrics:
            lines.extend(["| Metric | Value |", "|---|---:|"])
            for key, value in metrics[:80]:
                lines.append(f"| `{key}` | {value:.6g} |")
        else:
            lines.append("```json")
            lines.append(json.dumps(content, indent=2, sort_keys=True)[:8000])
            lines.append("```")
        lines.append("")
    figure_path = _make_accuracy_figure(_accuracy_rows(artifacts), out) if make_figures else None
    if figure_path:
        lines.extend(
            [
                "## Accuracy overview",
                "",
                "![Accuracy overview](figures/accuracy_overview.png)",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation order",
            "",
            "1. Confirm dataset integrity and leakage controls.",
            "2. Compare against the implemented majority and TF-IDF leakage controls.",
            "3. Evaluate lexically disjoint and held out composition splits.",
            "4. Evaluate episodic operator renaming.",
            "5. Evaluate counterfactual completeness and specificity.",
            "6. Treat latent algebra metrics as secondary unless behavioral counterfactuals agree.",
            "",
        ]
    )
    report_path = out / "FINAL_REPORT.md"
    report_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return {
        "summary": str(out / "SUMMARY.json"),
        "report": str(report_path),
        "source_count": len(artifacts),
        "figures": [figure_path] if figure_path else [],
        "adjudication": {
            "status": adjudication["status"],
            "json": adjudication["json"],
            "markdown": adjudication["markdown"],
        },
    }
