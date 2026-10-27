import json
from pathlib import Path

import pytest

from seed_refinement.experiments import run_experiments
from seed_refinement.release_validation import (
    assert_records_close,
    assert_summary_matches_record,
)


RELEASE_ROOT = Path(__file__).resolve().parents[3]


def test_stored_numerical_record_matches_fresh_run() -> None:
    stored = json.loads((RELEASE_ROOT / "results" / "numerical_results.json").read_text(encoding="utf-8"))
    assert_records_close(run_experiments(), stored)


def test_csv_summary_matches_json() -> None:
    record = json.loads((RELEASE_ROOT / "results" / "numerical_results.json").read_text(encoding="utf-8"))
    assert_summary_matches_record(
        RELEASE_ROOT / "results" / "numerical_summary.csv", record
    )


def test_record_comparison_tolerates_only_floating_roundoff() -> None:
    assert_records_close(
        {"residual": 1.0, "count": 3, "match": True, "formula": "x+y"},
        {"residual": 1.0 + 5e-14, "count": 3, "match": True, "formula": "x+y"},
    )
    with pytest.raises(AssertionError, match="integral values differ"):
        assert_records_close({"count": 3}, {"count": 4})
    with pytest.raises(AssertionError, match="symbolic values differ"):
        assert_records_close({"formula": "x+y"}, {"formula": "x-y"})
    with pytest.raises(AssertionError, match="boolean values differ"):
        assert_records_close({"match": True}, {"match": False})
