from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath


EXPECTED_SPLITS = {"id", "length_ood", "motif_ood", "syntax_ood", "joint_ood", "codebook_id", "codebook_ood"}
CAUSAL_FAMILIES = {"OBSERVE_UPGRADE", "TELL_WRITE", "IMAGINE_WRITE", "INFER_WRITE", "AUTHORIZE_WRITE"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def safe_relative(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def parse_manifest(text: str) -> dict[str, str]:
    entries = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        check(len(expected) == 64 and all(char in "0123456789abcdef" for char in expected), f"invalid digest: {relative}")
        check(safe_relative(relative), f"unsafe manifest path: {relative}")
        check(relative not in entries, f"duplicate manifest path: {relative}")
        entries[relative] = expected
    return entries


def check_finite(value, path: str = "summary") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            check_finite(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            check_finite(child, f"{path}[{index}]")
    elif isinstance(value, float):
        check(math.isfinite(value), f"non-finite numeric value at {path}")


def recompute_means(metric_rows: list[dict]) -> dict:
    grouped = defaultdict(list)
    for row in metric_rows:
        grouped[(row["arm"], row["split"])].append(row)
    result = defaultdict(dict)
    for (arm, split), rows in grouped.items():
        numeric_keys = [key for key in rows[0] if key not in ("arm", "seed", "split")]
        result[arm][split] = {key: sum(float(row[key]) for row in rows) / len(rows) for key in numeric_keys}
        values = [float(row["mode_balanced_accuracy"]) for row in rows]
        if len(values) > 1:
            mean = sum(values) / len(values)
            variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
            result[arm][split]["seed_sd_mode_balanced"] = math.sqrt(variance)
        else:
            result[arm][split]["seed_sd_mode_balanced"] = 0.0
    return result


def compare_nested_numbers(actual: dict, expected: dict, path: str = "trained_mean") -> None:
    check(set(actual) == set(expected), f"key mismatch at {path}")
    for key in actual:
        left = actual[key]
        right = expected[key]
        if isinstance(left, dict):
            check(isinstance(right, dict), f"type mismatch at {path}.{key}")
            compare_nested_numbers(left, right, f"{path}.{key}")
        else:
            check(math.isclose(float(left), float(right), rel_tol=1e-10, abs_tol=1e-12), f"mean mismatch at {path}.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a complete OSL v0.3 results directory")
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    root = args.results.resolve()
    required = {
        "summary.json",
        "FINAL_ADJUDICATION.json",
        "FINAL_REPORT.md",
        "metrics.csv",
        "DATASET_AUDIT.json",
        "PREOUTCOME_FREEZE.json",
        "training_history.json",
        "model_config.json",
        "vocab.json",
        "sample_examples.jsonl",
        "CAUSAL_CASES.jsonl",
        "CHECKPOINT_SHA256SUMS.txt",
        "RETURN_RESULTS_INSTRUCTIONS.txt",
        "SHA256SUMS.txt",
        "RETURN_THIS_OSL_HF_RESULTS.zip",
        "RETURN_THIS_OSL_HF_RESULTS.zip.sha256",
    }
    for name in required:
        check((root / name).is_file(), f"missing {name}")

    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    adjudication = json.loads((root / "FINAL_ADJUDICATION.json").read_text(encoding="utf-8"))
    check(summary.get("adjudication") == adjudication, "summary and final adjudication differ")
    check_finite(summary)
    arms = summary["config"]["arms"]
    seeds = summary["config"]["seeds"]
    check(len(arms) == len(set(arms)), "duplicate arms in configuration")
    check(len(seeds) == len(set(seeds)), "duplicate seeds in configuration")
    for arm in arms:
        check(EXPECTED_SPLITS == set(summary["trained_mean"][arm]), f"incomplete trained_mean for {arm}")

    audit = summary["dataset"]
    for overlap in audit["pairwise_overlap"].values():
        check(overlap["structural_overlap"] == 0, "structural overlap detected")
        check(overlap["alpha_overlap"] == 0, "alpha-renamed overlap detected")
    check(all(value == 0 for value in audit["causal_case_overlap"].values()), "causal case overlap detected")
    check(all(value == 0 for value in audit["causal_structural_overlap"].values()), "causal structural overlap detected")
    check(all(value == 0 for value in audit["causal_vs_ordinary_structural_overlap"].values()), "causal/ordinary structural overlap detected")
    for bank in audit["causal_banks"].values():
        check(bank["size"] == bank["unique_case_ids"], "duplicate causal case ids")
        check(set(bank["family_counts"]) == CAUSAL_FAMILIES, "incomplete causal family coverage")
        check(len(set(bank["family_counts"].values())) == 1, "unbalanced causal families")

    with (root / "metrics.csv").open(newline="", encoding="utf-8") as stream:
        metric_rows = list(csv.DictReader(stream))
    expected_identities = {(arm, str(seed), split) for arm in arms for seed in seeds for split in EXPECTED_SPLITS}
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
    compare_nested_numbers(summary["trained_mean"], recompute_means(metric_rows))

    histories = json.loads((root / "training_history.json").read_text(encoding="utf-8"))
    for arm in arms:
        check(set(histories[arm]) == {str(seed) for seed in seeds}, f"incomplete histories for {arm}")
        for seed in seeds:
            history = histories[arm][str(seed)]
            check(isinstance(history, list), f"invalid history type for {arm} seed {seed}")
            if history:
                check(sum(bool(row.get("selected")) for row in history) == 1, f"checkpoint selection is ambiguous for {arm} seed {seed}")

    expected_checkpoints = {f"checkpoints/{arm}_seed{seed}.pt" for arm in arms for seed in seeds}
    checkpoint_manifest = parse_manifest((root / "CHECKPOINT_SHA256SUMS.txt").read_text(encoding="utf-8"))
    if summary["config"].get("save_checkpoints", False):
        check(set(checkpoint_manifest) == expected_checkpoints, "checkpoint hash index has wrong coverage")
        check(len(set(checkpoint_manifest.values())) == len(checkpoint_manifest), "duplicate checkpoint hashes")
        for relative, expected in checkpoint_manifest.items():
            path = root / relative
            check(path.is_file(), f"missing checkpoint: {relative}")
            check(sha256(path) == expected, f"checkpoint checksum mismatch: {relative}")
    else:
        check(not checkpoint_manifest, "checkpoint index is nonempty when checkpoints were disabled")

    recovery = summary.get("recovery", {})
    completed = set(recovery.get("loaded_checkpoints", [])) | set(recovery.get("trained_checkpoints", []))
    expected_names = {f"{arm}_seed{seed}" for arm in arms for seed in seeds}
    check(completed == expected_names, "recovery coverage does not equal configured arm-seed grid")
    check(not (set(recovery.get("loaded_checkpoints", [])) & set(recovery.get("trained_checkpoints", []))), "checkpoint marked both loaded and trained")

    full_manifest = parse_manifest((root / "SHA256SUMS.txt").read_text(encoding="utf-8"))
    excluded = {"SHA256SUMS.txt", "RETURN_THIS_OSL_HF_RESULTS.zip", "RETURN_THIS_OSL_HF_RESULTS.zip.sha256"}
    actual_files = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root).as_posix() not in excluded
    }
    check(set(full_manifest) == actual_files, "full manifest does not exactly cover output files")
    for relative, expected in full_manifest.items():
        check(sha256(root / relative) == expected, f"checksum mismatch: {relative}")

    zip_path = root / "RETURN_THIS_OSL_HF_RESULTS.zip"
    with zipfile.ZipFile(zip_path) as archive:
        check(archive.testzip() is None, "corrupt compact ZIP member")
        names_list = archive.namelist()
        check(len(names_list) == len(set(names_list)), "duplicate compact ZIP member")
        check(all(safe_relative(name) for name in names_list), "unsafe compact ZIP member")
        names = set(names_list)
        check("summary.json" in names and "FINAL_REPORT.md" in names, "compact ZIP lacks core reports")
        check("COMPACT_SHA256SUMS.txt" in names, "compact ZIP lacks its manifest")
        check(not any(name.startswith("checkpoints/") for name in names), "compact ZIP unexpectedly contains checkpoints")
        check("SHA256SUMS.txt" not in names, "compact ZIP contains the full-output manifest")
        compact_manifest = parse_manifest(archive.read("COMPACT_SHA256SUMS.txt").decode("utf-8"))
        check(names == set(compact_manifest) | {"COMPACT_SHA256SUMS.txt"}, "unmanifested compact ZIP member")
        for relative, expected in compact_manifest.items():
            check(hashlib.sha256(archive.read(relative)).hexdigest() == expected, f"compact checksum mismatch: {relative}")

    expected_zip_hash = (root / "RETURN_THIS_OSL_HF_RESULTS.zip.sha256").read_text(encoding="utf-8").split()[0]
    check(sha256(zip_path) == expected_zip_hash, "compact ZIP checksum mismatch")

    from run_experiment import adjudicate

    check(adjudicate(summary) == adjudication, "frozen adjudication does not replay exactly")
    print(f"verified results: {root}")


if __name__ == "__main__":
    main()
