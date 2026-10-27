from pathlib import Path

import pandas as pd

from packet_gpu.benchmark_data import (
    best_speedups,
    dataset_summary,
    fairness_violations,
    load_benchmark,
    rows_frame,
    sanitized_benchmark,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "benchmark_results_sanitized.json"


def test_dataset_schema_and_counts() -> None:
    data = load_benchmark(DATA)
    summary = dataset_summary(data)
    assert summary["rows"] == 154
    assert summary["status_counts"] == {"measured": 154}
    assert summary["fairness_violations"] == []
    assert "RTX 3070 Ti" in summary["gpu_name"]


def test_sanitized_has_no_private_paths() -> None:
    text = DATA.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "downloads" not in lowered
    assert "timestamp_utc" not in text
    assert "filepath" not in text


def test_best_packet_speedups() -> None:
    frame = rows_frame(load_benchmark(DATA))
    gpu = best_speedups(frame, "gpu_dense")
    row = gpu[gpu["suite"] == "block_diagonal_matmat"].iloc[0]
    assert row["speedup_vs_gpu_dense"] > 14
    cpu = best_speedups(frame, "cpu_dense")
    row2 = cpu[cpu["suite"] == "block_diagonal_matmat"].iloc[0]
    assert row2["speedup_vs_cpu_dense"] > 200


def test_negative_controls_present() -> None:
    frame = rows_frame(load_benchmark(DATA))
    strassen = frame[(frame["suite"] == "strassen") & frame["method"].str.contains("strassen")]
    assert (strassen["speedup_vs_cpu_dense"] < 1).all()
    hodlr = frame[(frame["suite"] == "hodlr") & (frame["method"] == "gpu_packet_hodlr")]
    assert (hodlr["speedup_vs_gpu_dense"] < 1).all()


def test_fairness_groups_have_fixed_contract() -> None:
    frame = rows_frame(load_benchmark(DATA))
    assert fairness_violations(frame) == []
    for _, group in frame.groupby(["case_id", "output_contract"], dropna=False):
        assert group["case_id"].nunique() == 1
        assert group["output_contract"].nunique(dropna=False) == 1
