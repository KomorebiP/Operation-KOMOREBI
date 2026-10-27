"""Semantic comparison helpers for frozen Paper II release artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from pathlib import Path
from typing import NoReturn
from zipfile import ZipFile

from .experiments import SUMMARY_CERTIFICATES, numerical_summary_rows


DEFAULT_RELATIVE_TOLERANCE = 1e-12
DEFAULT_ABSOLUTE_TOLERANCE = 1e-14


def _fail(path: str, message: str) -> NoReturn:
    raise AssertionError(f"{path}: {message}")


def assert_records_close(
    fresh: object,
    frozen: object,
    *,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
    absolute_tolerance: float = DEFAULT_ABSOLUTE_TOLERANCE,
    path: str = "$",
) -> None:
    """Compare nested records, tolerating only floating-point roundoff.

    Mapping keys, sequence lengths, strings, booleans, integral counts, and all
    other symbolic values must match exactly.  A tolerance is used only when
    both corresponding values are non-integral real numbers.
    """
    if isinstance(fresh, Mapping) and isinstance(frozen, Mapping):
        if set(fresh) != set(frozen):
            _fail(path, f"mapping keys differ: {set(fresh) ^ set(frozen)}")
        for key in fresh:
            assert_records_close(
                fresh[key],
                frozen[key],
                relative_tolerance=relative_tolerance,
                absolute_tolerance=absolute_tolerance,
                path=f"{path}.{key}",
            )
        return

    sequence_types = (list, tuple)
    if isinstance(fresh, sequence_types) and isinstance(frozen, sequence_types):
        if len(fresh) != len(frozen):
            _fail(path, f"sequence lengths differ: {len(fresh)} != {len(frozen)}")
        for index, (fresh_item, frozen_item) in enumerate(zip(fresh, frozen, strict=True)):
            assert_records_close(
                fresh_item,
                frozen_item,
                relative_tolerance=relative_tolerance,
                absolute_tolerance=absolute_tolerance,
                path=f"{path}[{index}]",
            )
        return

    if isinstance(fresh, bool) or isinstance(frozen, bool):
        if type(fresh) is not bool or type(frozen) is not bool or fresh != frozen:
            _fail(path, f"boolean values differ: {fresh!r} != {frozen!r}")
        return

    if isinstance(fresh, Integral) or isinstance(frozen, Integral):
        if not isinstance(fresh, Integral) or not isinstance(frozen, Integral) or fresh != frozen:
            _fail(path, f"integral values differ: {fresh!r} != {frozen!r}")
        return

    if isinstance(fresh, Real) and isinstance(frozen, Real):
        if not math.isclose(
            float(fresh),
            float(frozen),
            rel_tol=relative_tolerance,
            abs_tol=absolute_tolerance,
        ):
            _fail(path, f"floating values differ: {fresh!r} != {frozen!r}")
        return

    if type(fresh) is not type(frozen) or fresh != frozen:
        _fail(path, f"symbolic values differ: {fresh!r} != {frozen!r}")


def _read_summary(path: Path) -> list[tuple[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if not rows or rows[0] != ["certificate", "value"]:
        raise AssertionError(f"{path}: expected the header certificate,value")
    data = rows[1:]
    if any(len(row) != 2 for row in data):
        raise AssertionError(f"{path}: every summary row must have exactly two columns")
    names = [row[0] for row in data]
    if names != list(SUMMARY_CERTIFICATES):
        raise AssertionError(
            f"{path}: expected exactly nine canonical rows in order; found {names}"
        )
    return [(name, value) for name, value in data]


def assert_summary_matches_record(
    summary_path: str | Path,
    record: dict[str, object],
    *,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
    absolute_tolerance: float = DEFAULT_ABSOLUTE_TOLERANCE,
) -> None:
    """Validate every CSV row against its source JSON record."""
    rows = _read_summary(Path(summary_path))
    expected_rows = numerical_summary_rows(record)
    for (name, raw_value), (expected_name, expected_value) in zip(
        rows, expected_rows, strict=True
    ):
        if name != expected_name:
            raise AssertionError(f"summary certificate mismatch: {name} != {expected_name}")
        if isinstance(expected_value, Integral):
            try:
                actual_value = int(raw_value)
            except ValueError as error:
                raise AssertionError(f"{name}: expected an integral value") from error
            if str(actual_value) != raw_value or actual_value != expected_value:
                raise AssertionError(f"{name}: {raw_value!r} != {expected_value!r}")
        else:
            try:
                actual_value = float(raw_value)
            except ValueError as error:
                raise AssertionError(f"{name}: expected a floating-point value") from error
            if not math.isclose(
                actual_value,
                float(expected_value),
                rel_tol=relative_tolerance,
                abs_tol=absolute_tolerance,
            ):
                raise AssertionError(f"{name}: {actual_value!r} != {expected_value!r}")


def compare_generated_records(
    fresh_root: str | Path,
    frozen_root: str | Path,
) -> None:
    """Compare regenerated JSON/CSV outputs with the frozen release records."""
    fresh_root = Path(fresh_root)
    frozen_root = Path(frozen_root)
    fresh_json = fresh_root / "results" / "numerical_results.json"
    frozen_json = frozen_root / "results" / "numerical_results.json"
    fresh_record = json.loads(fresh_json.read_text(encoding="utf-8"))
    frozen_record = json.loads(frozen_json.read_text(encoding="utf-8"))
    assert_records_close(fresh_record, frozen_record)
    assert_summary_matches_record(
        fresh_root / "results" / "numerical_summary.csv", fresh_record
    )
    assert_summary_matches_record(
        frozen_root / "results" / "numerical_summary.csv", frozen_record
    )


def compare_wheel_contents(fresh_wheel: str | Path, frozen_wheel: str | Path) -> None:
    """Compare wheel payloads exactly while ignoring ZIP container timestamps."""
    with ZipFile(fresh_wheel) as fresh, ZipFile(frozen_wheel) as frozen:
        fresh_names = set(fresh.namelist())
        frozen_names = set(frozen.namelist())
        if fresh_names != frozen_names:
            raise AssertionError(
                f"wheel member sets differ: {fresh_names ^ frozen_names}"
            )
        for name in sorted(fresh_names):
            if fresh.read(name) != frozen.read(name):
                raise AssertionError(f"wheel payload differs: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    records = subparsers.add_parser("compare-records")
    records.add_argument("fresh_root", type=Path)
    records.add_argument("frozen_root", type=Path)
    wheels = subparsers.add_parser("compare-wheels")
    wheels.add_argument("fresh_wheel", type=Path)
    wheels.add_argument("frozen_wheel", type=Path)
    arguments = parser.parse_args()

    if arguments.command == "compare-records":
        compare_generated_records(arguments.fresh_root, arguments.frozen_root)
        print("RELEASE_RECORD_COMPARISON_PASS rows=9")
    else:
        compare_wheel_contents(arguments.fresh_wheel, arguments.frozen_wheel)
        print("WHEEL_PAYLOAD_COMPARISON_PASS")


if __name__ == "__main__":
    main()
