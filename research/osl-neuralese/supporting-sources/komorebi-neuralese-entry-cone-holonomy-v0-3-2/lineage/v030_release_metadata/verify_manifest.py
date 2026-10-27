#!/usr/bin/env python3
"""Verify release integrity, registered bindings, gates, and structural tests."""

from __future__ import annotations

import hashlib
import io
import json
import math
import unittest
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parent
EXCLUDED_NAMES = {"MANIFEST.json", "SHA256SUMS.txt"}
EXPECTED_RESULTS_SHA256 = "3bddb9174ca7bb1bd217eeefa0421f43575a5838ac0b0ddb845de944fcd15553"
EXPECTED_FREEZE_SHA256 = "06adcc6767f53d0106890d99dd171e6e160eee1a5943e991f39913b6dce51a88"
EXPECTED_GATES = {
    "E0_execution_integrity": True,
    "H0_hard_rectangle": False,
    "H1_downset": True,
    "S0_soft_exact_collapse": False,
    "D0_diagonal_action": False,
    "W0_relator_hard_closure": False,
    "W1_relator_soft_flatness": False,
    "C0_nonidentity_control": False,
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def release_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in EXCLUDED_NAMES
        and "__pycache__" not in path.parts
        and not path.name.endswith(".pyc")
    )


def numeric_scalars(value: Any) -> Iterator[int | float]:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from numeric_scalars(child)
    elif isinstance(value, list):
        for child in value:
            yield from numeric_scalars(child)


def is_downset(mask: list[list[bool]]) -> bool:
    for L, row in enumerate(mask):
        for H, passed in enumerate(row):
            if passed and any(not mask[i][j] for i in range(L + 1) for j in range(H + 1)):
                return False
    return True


def main() -> int:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    require(
        manifest.get("schema") == "komorebi.neuralese.completion_surface.manifest.v1",
        "unexpected manifest schema",
    )
    rows = manifest["files"]
    require(manifest["file_count"] == len(rows), "manifest file count mismatch")
    listed = {row["path"] for row in rows}
    actual = {path.relative_to(ROOT).as_posix() for path in release_files()}
    require(listed == actual, f"manifest membership mismatch: listed-only={sorted(listed-actual)}, actual-only={sorted(actual-listed)}")
    for row in rows:
        path = ROOT / row["path"]
        require(path.stat().st_size == row["bytes"], f"size mismatch: {row['path']}")
        require(digest(path) == row["sha256"], f"digest mismatch: {row['path']}")
    expected_sums = "".join(f"{row['sha256']}  {row['path']}\n" for row in rows)
    require((ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8") == expected_sums, "SHA256SUMS mismatch")

    result_path = ROOT / "results" / "COMPLETION_SURFACE_RESULTS.json"
    require(digest(result_path) == EXPECTED_RESULTS_SHA256, "registered-result digest mismatch")
    require(digest(ROOT / "EXECUTION_FREEZE.json") == EXPECTED_FREEZE_SHA256, "execution-freeze digest mismatch")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    freeze = json.loads((ROOT / "EXECUTION_FREEZE.json").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "results" / "POSTHOC_SUMMARY.json").read_text(encoding="utf-8"))
    receipt = json.loads((ROOT / "RUN_COMPLETE.json").read_text(encoding="utf-8"))

    require(result["registered_execution_profile"] is True, "result is not from the registered profile")
    require(result["status"] == "adaptive_developmental_followup", "unexpected result status")
    require(result["registered_rectangle"] == {"Lmax": 8, "Hmax": 8}, "registered rectangle mismatch")
    require(result["checkpoint_seeds"] == [0, 1], "checkpoint seed mismatch")
    require(result["execution_freeze"]["passed"] is True, "embedded freeze validation failed")
    require(result["execution_freeze"]["freeze_sha256"] == EXPECTED_FREEZE_SHA256, "embedded freeze digest mismatch")

    for relative, expected in freeze["files"].items():
        require(digest(ROOT / relative) == expected, f"frozen digest mismatch: {relative}")
    require(set(freeze["files"]) == {
        "PREREGISTRATION.json", "RESEARCH_SPEC.md", "checkpoint_io.py",
        "checkpoints/projective_terminal_seed0.pt", "checkpoints/projective_terminal_seed1.pt",
        "core.py", "relator_witness.py", "results/LINEAGE_REGRESSION.json",
        "run_completion_surface.py", "run_lineage_regression.py", "soft_surface.py",
        "test_completion_surface.py",
    }, "frozen scientific file set mismatch")
    require(result["execution"]["runner_sha256"] == freeze["files"]["run_completion_surface.py"], "runner binding mismatch")
    require(result["execution"]["test_sha256"] == freeze["files"]["test_completion_surface.py"], "test binding mismatch")
    require(result["execution"]["preregistration_sha256"] == freeze["files"]["PREREGISTRATION.json"], "registration binding mismatch")
    require(result["checkpoint_digests"] == {
        "projective_terminal_seed0.pt": freeze["files"]["checkpoints/projective_terminal_seed0.pt"],
        "projective_terminal_seed1.pt": freeze["files"]["checkpoints/projective_terminal_seed1.pt"],
    }, "checkpoint binding mismatch")

    require(summary["source_results_sha256"] == EXPECTED_RESULTS_SHA256, "post-hoc summary source mismatch")
    require(receipt["results_sha256"] == EXPECTED_RESULTS_SHA256, "run receipt result mismatch")
    require(receipt["posthoc_summary_sha256"] == digest(ROOT / "results" / "POSTHOC_SUMMARY.json"), "run receipt summary mismatch")
    require(receipt["report_sha256"] == digest(ROOT / "RESULTS_SUMMARY.md"), "run receipt report mismatch")

    episodes = [episode for seed in result["records"].values() for episode in seed["episodes"]]
    relator_episodes = [episode for seed in result["records"].values() for episode in seed["relator_witness"]["episodes"]]
    recomputed = {
        "E0_execution_integrity": bool(result["registered_execution_profile"] and result["execution_freeze"]["passed"]),
        "H0_hard_rectangle": all(ep["hard_rectangle_passed"] and all(cell["hard_completion_pass"] for cell in ep["cumulative_cells"]) for ep in episodes),
        "H1_downset": all(ep["downset_passed"] and not ep["downset_violations"] and is_downset(ep["cumulative_pass_mask"]) for ep in episodes),
        "S0_soft_exact_collapse": all(ep["soft_interfaces"]["both_interfaces_exact_on_cumulative_rectangle"] for ep in episodes),
        "D0_diagonal_action": all(ep["diagonal_action"]["passed"] and all(cell["passed"] for cell in ep["diagonal_action"]["cells"]) for ep in episodes),
        "W0_relator_hard_closure": all(ep["gates"]["W0_relator_hard_closure"] for ep in relator_episodes),
        "W1_relator_soft_flatness": all(ep["gates"]["W1_relator_soft_flatness"] for ep in relator_episodes),
        "C0_nonidentity_control": all(ep["gates"]["C0_nonidentity_control"] for ep in relator_episodes),
    }
    require(recomputed == EXPECTED_GATES, f"independent gate recomputation mismatch: {recomputed}")
    require(result["gates"] == EXPECTED_GATES, "stored gate verdict mismatch")
    require(summary["registered_gates"] == EXPECTED_GATES, "summary gate verdict mismatch")

    full = summary["ordinary_surface"]["full_cumulative_L8_H8"]
    postburn = summary["ordinary_surface"]["post_burnin_exact_L1_to_L8_cumulative_H8"]
    relator = summary["relator_witness"]
    require((full["decision_count"], full["error_count"], full["episode_hard_pass_count"]) == (33_423_488, 8, 8), "full-surface headline mismatch")
    require((postburn["decision_count"], postburn["error_count"], postburn["all_128_episode_depth_cells_pass"]) == (33_358_080, 0, True), "post-transition headline mismatch")
    require((relator["configuration_episode_count"], relator["decision_count"], relator["identity_wrong_decision_count"], relator["identity_failing_case_count"], relator["delayed_failing_case_count"]) == (336, 87_908_352, 350_757, 2_193, 1_697), "relator headline mismatch")
    require(relator["earliest_observed_depth_failure"]["observed_history_depth"] == 38, "earliest relator depth mismatch")
    require(relator["earliest_observed_depth_failure"]["first_failure_horizon"] == 3, "earliest reveal horizon mismatch")

    finite_count = 0
    for number in numeric_scalars(result):
        finite_count += 1
        if isinstance(number, float):
            require(math.isfinite(number), "registered result contains NaN or infinity")

    suite = unittest.defaultTestLoader.loadTestsFromName("test_completion_surface")
    require(suite.countTestCases() == 19, "structural test count mismatch")
    stream = io.StringIO()
    test_result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    require(test_result.wasSuccessful(), "structural tests failed:\n" + stream.getvalue())

    print(json.dumps({
        "manifest_files_verified": manifest["file_count"],
        "frozen_scientific_files_verified": len(freeze["files"]),
        "registered_result_sha256": EXPECTED_RESULTS_SHA256,
        "numeric_scalars_checked": finite_count,
        "registered_gates_recomputed": recomputed,
        "structural_tests_passed": test_result.testsRun,
        "status": "verified",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
