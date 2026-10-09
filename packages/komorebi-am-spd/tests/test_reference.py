from __future__ import annotations

from am_spd.reference import (
    PAPER_CASES,
    available_paper_cases,
    compare_paper_reference,
    load_paper_reference,
    load_reference_packet_history,
)


def test_reference_resources_are_packaged() -> None:
    reference = load_paper_reference()
    histories = load_reference_packet_history()
    assert available_paper_cases() == PAPER_CASES
    assert set(reference["cases"]) == set(PAPER_CASES)
    assert set(histories) == set(PAPER_CASES)
    assert all(histories[case] for case in PAPER_CASES)


def test_reference_comparison_accepts_canonical_record() -> None:
    record = load_paper_reference()["cases"]["synthetic_geometry"]
    comparison = compare_paper_reference(record, record)
    assert comparison["passed"] is True
