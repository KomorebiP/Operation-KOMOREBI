from __future__ import annotations

import csv
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rrct_lab.config import DEFAULT_CONFIG  # noqa: E402
from rrct_lab.features import feature_rows  # noqa: E402
from rrct_lab.registry import EXPERIMENTS, list_experiments  # noqa: E402
from rrct_lab.utils import scalarize  # noqa: E402
from rrct_lab.version import __version__  # noqa: E402


def write_json(path: pathlib.Path, value: Any) -> None:
    path.write_text(
        json.dumps(scalarize(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: pathlib.Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: scalarize(row.get(key)) for key in fields})


def main() -> None:
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    rows = feature_rows()
    families = list(EXPERIMENTS)

    write_json(docs / "DEFAULT_CONFIG.json", DEFAULT_CONFIG)
    schema = {
        "schema": "rrct.lab.configuration_schema.v1",
        "version": __version__,
        "key_count": len(rows),
        "defaults": DEFAULT_CONFIG,
        "keys": [
            {"key": row["key"], "type": row["type"], "default": row["default"]}
            for row in rows
        ],
    }
    write_json(docs / "CONFIGURATION_SCHEMA.json", schema)

    registry_rows: list[dict[str, Any]] = []
    for row in rows:
        registry_rows.append(
            {
                "key": row["key"],
                "type": row["type"],
                "default": json.dumps(scalarize(row["default"]), sort_keys=True),
                "implemented_experiments": row["implemented_experiments"],
                "partial_experiments": row["partial_experiments"],
                "unsupported_experiments": row["unsupported_experiments"],
            }
        )
    write_csv(docs / "FEATURE_REGISTRY.csv", registry_rows)

    matrix_rows: list[dict[str, Any]] = []
    for row in rows:
        matrix = {"key": row["key"], "default": json.dumps(scalarize(row["default"]), sort_keys=True)}
        for family in families:
            matrix[family] = row["family_status"][family]
        matrix_rows.append(matrix)
    write_csv(docs / "EXPERIMENT_FEATURE_MATRIX.csv", matrix_rows)

    reference = [
        f"# RRCT {__version__} Feature Reference",
        "",
        f"This file is generated from the live configuration schema. It contains **{len(rows)} keys**.",
        "",
        "Contract status is family-specific: `implemented`, `partial`, or `unsupported`.",
        "",
        "| Key | Type | Default | Implemented families | Partial families |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        default = json.dumps(scalarize(row["default"]), sort_keys=True)
        reference.append(
            f"| `{row['key']}` | {row['type']} | `{default}` | "
            f"{row['implemented_experiments'] or '—'} | {row['partial_experiments'] or '—'} |"
        )
    (docs / "FEATURE_REFERENCE.md").write_text("\n".join(reference) + "\n", encoding="utf-8")

    experiments = list_experiments()
    write_json(
        docs / "EXPERIMENT_REGISTRY.json",
        {
            "schema": "rrct.lab.experiment_registry.v1",
            "version": __version__,
            "experiment_count": len(experiments),
            "experiments": experiments,
        },
    )
    catalog = [
        "# Experiment Catalog",
        "",
        f"RRCT {__version__} provides **{len(experiments) - 1} scientific/engineering families** plus the all-family smoke matrix.",
        "",
    ]
    for experiment in experiments:
        catalog.extend(
            [
                f"## `{experiment['key']}` — {experiment['title']}",
                "",
                experiment["description"],
                "",
                "Optional dependencies: "
                + (", ".join(experiment["optional_dependencies"]) or "none"),
                "",
                "Declared feature surface: "
                + (", ".join(experiment["supported_feature_keys"]) or "none"),
                "",
            ]
        )
    (docs / "EXPERIMENT_CATALOG.md").write_text("\n".join(catalog), encoding="utf-8")

    print(
        json.dumps(
            {
                "version": __version__,
                "configuration_keys": len(rows),
                "families": len(experiments),
                "feature_switches": len(DEFAULT_CONFIG["features"]),
                "interventions": len(DEFAULT_CONFIG["interventions"]),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
