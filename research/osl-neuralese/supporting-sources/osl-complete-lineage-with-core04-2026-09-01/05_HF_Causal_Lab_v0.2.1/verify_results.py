from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    root = args.results.resolve()
    required = [
        "summary.json",
        "FINAL_ADJUDICATION.json",
        "FINAL_REPORT.md",
        "metrics.csv",
        "DATASET_AUDIT.json",
        "PREOUTCOME_FREEZE.json",
        "SHA256SUMS.txt",
        "RETURN_THIS_OSL_HF_RESULTS.zip",
        "RETURN_THIS_OSL_HF_RESULTS.zip.sha256",
    ]
    for name in required:
        check((root / name).is_file(), f"missing {name}")

    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    expected_splits = {"id", "length_ood", "motif_ood", "syntax_ood", "joint_ood", "codebook_id", "codebook_ood"}
    arms = summary["config"]["arms"]
    seeds = summary["config"]["seeds"]
    for arm in arms:
        check(expected_splits == set(summary["trained_mean"][arm]), f"incomplete trained_mean for {arm}")
    for overlap in summary["dataset"]["pairwise_overlap"].values():
        check(overlap["structural_overlap"] == 0, "structural overlap detected")
        check(overlap["alpha_overlap"] == 0, "alpha-renamed overlap detected")

    with (root / "metrics.csv").open(newline="", encoding="utf-8") as stream:
        metric_rows = list(csv.DictReader(stream))
    expected_identities = {(arm, str(seed), split) for arm in arms for seed in seeds for split in expected_splits}
    actual_identities = {(row["arm"], row["seed"], row["split"]) for row in metric_rows}
    check(len(metric_rows) == len(expected_identities), "unexpected metrics row count or duplicate rows")
    check(actual_identities == expected_identities, "missing arm, seed, or split metrics")
    for row in metric_rows:
        for key, raw_value in row.items():
            if key in ("arm", "seed", "split"):
                continue
            value = float(raw_value)
            check(math.isfinite(value), f"non-finite metric {key}")
            check(0.0 <= value <= 1.0, f"out-of-range metric {key}")

    histories = json.loads((root / "training_history.json").read_text(encoding="utf-8"))
    for arm in arms:
        check(set(histories[arm]) == {str(seed) for seed in seeds}, f"incomplete histories for {arm}")
        check(all(isinstance(histories[arm][str(seed)], list) for seed in seeds), f"invalid history type for {arm}")
    if summary["config"].get("save_checkpoints", False):
        for arm in arms:
            for seed in seeds:
                check((root / "checkpoints" / f"{arm}_seed{seed}.pt").is_file(), f"missing checkpoint {arm} seed {seed}")

    for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = root / relative
        check(path.is_file(), f"manifest file missing: {relative}")
        check(sha256(path) == expected, f"checksum mismatch: {relative}")

    zip_path = root / "RETURN_THIS_OSL_HF_RESULTS.zip"
    with zipfile.ZipFile(zip_path) as archive:
        check(archive.testzip() is None, "corrupt compact ZIP member")
        names = set(archive.namelist())
        check("summary.json" in names and "FINAL_REPORT.md" in names, "compact ZIP lacks core reports")
        check("COMPACT_SHA256SUMS.txt" in names, "compact ZIP lacks its manifest")
        check(not any(name.startswith("checkpoints/") for name in names), "compact ZIP unexpectedly contains checkpoints")
        check("SHA256SUMS.txt" not in names, "compact ZIP contains the full-output manifest")
        compact_lines = archive.read("COMPACT_SHA256SUMS.txt").decode("utf-8").splitlines()
        compact_names = set()
        for line in compact_lines:
            expected, relative = line.split("  ", 1)
            check(relative in names, f"compact manifest file missing: {relative}")
            check(hashlib.sha256(archive.read(relative)).hexdigest() == expected, f"compact checksum mismatch: {relative}")
            compact_names.add(relative)
        check(names == compact_names | {"COMPACT_SHA256SUMS.txt"}, "unmanifested compact ZIP member")

    expected_zip_hash = (root / "RETURN_THIS_OSL_HF_RESULTS.zip.sha256").read_text(encoding="utf-8").split()[0]
    check(sha256(zip_path) == expected_zip_hash, "compact ZIP checksum mismatch")
    print(f"verified results: {root}")


if __name__ == "__main__":
    main()
