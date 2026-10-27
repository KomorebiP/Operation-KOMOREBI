from __future__ import annotations
import json
from pathlib import Path

from komorebi_arc2 import entry


def test_synthetic_suite_exact():
    report = entry.run_synthetic_benchmark(6, time_limit=2.0)
    assert report["valid_submission"] is True
    assert report["ok"] == report["total"] == 6


def test_mini_file_pipeline(tmp_path: Path):
    root = Path(entry.make_mini_dataset(tmp_path / "mini"))
    challenge = root / "arc-agi_evaluation-challenges.json"
    solutions = root / "arc-agi_evaluation-solutions.json"
    output = root / "submission.json"
    report = entry.evaluate_split(str(challenge), str(solutions), str(output), None, 2.0, True)
    assert report["valid_submission"] is True
    assert report["ok"] == report["total"] == 6
    submission = json.loads(output.read_text())
    assert entry.validate_submission(submission, entry.load_tasks_from_path(challenge)) == []


def test_validator_rejects_wrong_attempt_count():
    tasks, _ = entry.make_synthetic_challenge_solution(1)
    task_id = next(iter(tasks))
    bad = {task_id: [{"attempt_1": [[0]]}]}
    errors = entry.validate_submission(bad, tasks)
    assert errors



def _candidate_prediction(candidates):
    assert candidates
    return candidates[0].grids[0]


def test_cell_level_comparison_distinguishes_shape_from_exactness():
    expected = entry.as_array([[0, 1], [2, 3]])
    prediction = entry.as_array([[0, 1], [2, 4]])
    comparison = entry.compare_prediction(expected, prediction)
    assert comparison["shape_match"] is True
    assert comparison["exact"] is False
    assert comparison["wrong_cells"] == 1
    assert comparison["cell_accuracy"] == 0.75
    assert comparison["first_mismatches"] == [
        {"row": 1, "column": 1, "expected": 3, "predicted": 4}
    ]
    assert comparison["color_confusion"][0] == {"expected": 3, "predicted": 4, "count": 1}


def test_diagnostic_bundle_contains_problem_solution_and_html(tmp_path: Path):
    tasks, solutions = entry.make_synthetic_challenge_solution(2)
    submission = entry.build_submission(tasks, time_limit_per_task=1.0, verbose=False)
    task_id = next(iter(submission))
    # Force one exact-shape miss so the atlas must explain a cell error.
    submission[task_id][0]["attempt_1"][0][0] = (submission[task_id][0]["attempt_1"][0][0] + 1) % 10
    submission[task_id][0]["attempt_2"][0][0] = (submission[task_id][0]["attempt_2"][0][0] + 2) % 10
    summary = entry.write_diagnostic_bundle(
        tasks,
        solutions,
        submission,
        tmp_path / "atlas",
        include_solved=False,
    )
    assert summary["records_written"] >= 1
    assert (tmp_path / "atlas" / "index.html").exists()
    assert (tmp_path / "atlas" / "summary.json").exists()
    assert (tmp_path / "atlas" / "output_ledger.csv").exists()
    assert (tmp_path / "atlas" / "near_misses.json").exists()
    assert list((tmp_path / "atlas" / "tasks").glob("*.svg"))
    jsonl = (tmp_path / "atlas" / "problems_and_solutions.jsonl").read_text(encoding="utf-8")
    assert '"training_examples"' in jsonl
    assert '"expected"' in jsonl
    assert '"attempt_1_comparison"' in jsonl


def test_marker_conditioned_recolor_rule_generalizes():
    source = entry.as_array([
        [9, 0, 0, 0, 0],
        [0, 2, 2, 2, 0],
        [0, 2, 2, 2, 0],
        [0, 0, 0, 0, 0],
    ])
    target = entry.as_array([
        [0, 0, 0, 0, 0],
        [0, 7, 7, 7, 0],
        [0, 7, 7, 7, 0],
        [0, 0, 0, 0, 0],
    ])
    test = entry.as_array([
        [0, 0, 0, 0, 9],
        [0, 2, 2, 0, 0],
        [0, 2, 2, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    expected = entry.as_array([
        [0, 0, 0, 0, 0],
        [0, 7, 7, 0, 0],
        [0, 7, 7, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    prediction = _candidate_prediction(entry.marker_shape_recolor_rules([(source, target)], [test]))
    assert entry.exact(prediction, expected)


def test_enclosed_region_fill_rule_generalizes():
    source = entry.as_array([
        [0, 0, 0, 0, 0],
        [0, 2, 2, 2, 0],
        [0, 2, 0, 2, 0],
        [0, 2, 2, 2, 0],
        [0, 0, 0, 0, 0],
    ])
    target = source.copy(); target[2, 2] = 4
    test = entry.as_array([
        [3, 3, 3, 3, 3],
        [3, 0, 0, 0, 3],
        [3, 0, 0, 0, 3],
        [3, 3, 3, 3, 3],
    ])
    expected = test.copy(); expected[1:3, 1:4] = 4
    predictions = [candidate.grids[0] for candidate in entry.enclosed_region_rules([(source, target)], [test])]
    assert any(entry.exact(prediction, expected) for prediction in predictions)


def test_periodic_resize_rule_generalizes():
    source = entry.as_array([[1], [2], [1]])
    target = entry.as_array([[1], [2], [1], [2], [1]])
    test = entry.as_array([[3], [4], [3]])
    expected = entry.as_array([[3], [4], [3], [4], [3]])
    predictions = [candidate.grids[0] for candidate in entry.periodic_resize_rules([(source, target)], [test])]
    assert any(entry.exact(prediction, expected) for prediction in predictions)


def test_kronecker_complement_rule_generalizes():
    source = entry.as_array([[2, 0], [0, 2]])
    target = entry.kronecker_mask_motif_exact(source, "complement")
    test = entry.as_array([[3, 3], [0, 0]])
    expected = entry.kronecker_mask_motif_exact(test, "complement")
    predictions = [candidate.grids[0] for candidate in entry.kronecker_variant_rules([(source, target)], [test])]
    assert any(entry.exact(prediction, expected) for prediction in predictions)


def test_object_hole_recolor_rule_generalizes():
    source = entry.as_array([
        [2, 2, 2, 0, 5, 5],
        [2, 0, 2, 0, 5, 5],
        [2, 2, 2, 0, 0, 0],
    ])
    target = entry.as_array([
        [7, 7, 7, 0, 3, 3],
        [7, 0, 7, 0, 3, 3],
        [7, 7, 7, 0, 0, 0],
    ])
    test = entry.as_array([
        [6, 6, 0, 8, 8, 8],
        [6, 6, 0, 8, 0, 8],
        [0, 0, 0, 8, 8, 8],
    ])
    expected = entry.as_array([
        [3, 3, 0, 7, 7, 7],
        [3, 3, 0, 7, 0, 7],
        [0, 0, 0, 7, 7, 7],
    ])
    predictions = [candidate.grids[0] for candidate in entry.object_shape_recolor_rules([(source, target)], [test])]
    # The shape map and the hole-count map are both legal here; either may carry the abstraction.
    predictions += [candidate.grids[0] for candidate in entry.structural_exact_rules([(source, target)], [test])]
    assert any(entry.exact(prediction, expected) for prediction in predictions)
