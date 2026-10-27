from __future__ import annotations

import copy
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:\\[^\n\r\t\"]+"),
    re.compile(r"/home/[^/\s]+/[^\s\"]*"),
]


def _scrub_string(value: str) -> str:
    out = value
    for pattern in _PATH_PATTERNS:
        out = pattern.sub("<local-path-removed>", out)
    return out


def scrub_object(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key in {"filepath", "nvidia_smi", "nvcc_version", "timestamp_utc"}:
                continue
            result[key] = scrub_object(item)
        return result
    if isinstance(value, list):
        return [scrub_object(item) for item in value]
    if isinstance(value, str):
        return _scrub_string(value)
    return value


def load_benchmark(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "results" not in data or not isinstance(data["results"], list):
        raise ValueError("benchmark file must contain a results list")
    return data


def sanitized_benchmark(data: dict[str, Any]) -> dict[str, Any]:
    clean = scrub_object(copy.deepcopy(data))
    clean["author"] = "Komorebi P."
    clean["source_note"] = "Sanitized measured benchmark corpus used by Seed Calculus VIII. Local paths and machine timestamps were removed."
    return clean


def rows_frame(data: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(data["results"])


def fairness_violations(frame: pd.DataFrame) -> list[str]:
    violations: list[str] = []
    for (case_id, contract), group in frame.groupby(["case_id", "output_contract"], dropna=False):
        if group["case_id"].nunique() != 1 or group["output_contract"].nunique(dropna=False) != 1:
            violations.append(f"mixed contract in {case_id}/{contract}")
    for _, row in frame.iterrows():
        if pd.notna(row.get("speedup_vs_gpu_dense")) and row.get("output_contract") is None:
            violations.append(f"speedup without output contract for {row.get('method')}")
    return violations


def best_speedups(frame: pd.DataFrame, baseline: str, *, packet_only: bool = True) -> pd.DataFrame:
    column = f"speedup_vs_{baseline}"
    work = frame[pd.notna(frame[column])].copy()
    if packet_only:
        work = work[work["method"].astype(str).str.contains("packet")]
    if work.empty:
        return work
    idx = work.groupby("suite")[column].idxmax()
    return work.loc[idx].sort_values(column, ascending=False)


def dataset_summary(data: dict[str, Any]) -> dict[str, Any]:
    frame = rows_frame(data)
    gpu_name = data.get("environment", {}).get("gpu", {}).get("name")
    status_counts = Counter(frame["status"].fillna("missing"))
    device_counts = Counter(frame["device"].fillna("missing"))
    suite_counts = Counter(frame["suite"])
    max_error = float(frame["relative_error"].dropna().max()) if frame["relative_error"].notna().any() else None
    return {
        "author": "Komorebi P.",
        "rows": int(len(frame)),
        "suites": dict(sorted(suite_counts.items())),
        "status_counts": dict(status_counts),
        "device_counts": dict(device_counts),
        "gpu_name": gpu_name,
        "maximum_relative_error": max_error,
        "fairness_violations": fairness_violations(frame),
    }


def case_method(frame: pd.DataFrame, case_contains: str, method: str) -> pd.Series:
    rows = frame[frame["case_id"].astype(str).str.contains(case_contains, regex=False) & (frame["method"] == method)]
    if len(rows) != 1:
        raise KeyError(f"expected one row for {case_contains}/{method}, found {len(rows)}")
    return rows.iloc[0]


def write_analysis_tables(data: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frame = rows_frame(data)
    all_path = output / "all_benchmark_rows_sanitized.csv"
    frame.to_csv(all_path, index=False)
    gpu_path = output / "best_packet_speedups_vs_gpu_dense.csv"
    best_speedups(frame, "gpu_dense").to_csv(gpu_path, index=False)
    cpu_path = output / "best_packet_speedups_vs_cpu_dense.csv"
    best_speedups(frame, "cpu_dense").to_csv(cpu_path, index=False)
    negative = frame[
        (frame["method"].astype(str).str.contains("packet|strassen|iterative", regex=True))
        & (
            ((frame["speedup_vs_gpu_dense"].notna()) & (frame["speedup_vs_gpu_dense"] < 1))
            | ((frame["speedup_vs_cpu_dense"].notna()) & (frame["speedup_vs_cpu_dense"] < 1))
        )
    ]
    neg_path = output / "negative_controls.csv"
    negative.to_csv(neg_path, index=False)
    return {"all": all_path, "gpu": gpu_path, "cpu": cpu_path, "negative": neg_path}
