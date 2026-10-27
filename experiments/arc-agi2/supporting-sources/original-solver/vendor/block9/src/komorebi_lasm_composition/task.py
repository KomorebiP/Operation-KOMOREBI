"""Sanitized training-task boundary for recursive composition.

Compilation receives a :class:`TrainingTask`, never the caller's raw task
mapping.  Test examples are copied by reading only their ``input`` member, so
an attached public-training ``output`` cannot influence compilation, hashes,
candidate ordering, or diagnostics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .model import Grid, SCHEMA_VERSION, canonical_value, sha256_record, validate_grid


def _finite_sequence(value: object, label: str) -> list[Any]:
    if isinstance(value, (str, bytes, bytearray, Mapping)):
        raise TypeError(f"{label} must be a finite sequence")
    try:
        count = len(value)  # type: ignore[arg-type]
        return [value[index] for index in range(count)]  # type: ignore[index]
    except (TypeError, AttributeError, KeyError, IndexError) as error:
        raise TypeError(f"{label} must be a finite indexable sequence") from error


@dataclass(frozen=True, slots=True)
class TrainingExample:
    """One labeled demonstration, stored as immutable validated grids."""

    input_grid: Grid
    output_grid: Grid
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "input_grid", validate_grid(self.input_grid))
        object.__setattr__(self, "output_grid", validate_grid(self.output_grid))
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @classmethod
    def from_mapping(cls, example: Mapping[str, Any]) -> "TrainingExample":
        if not isinstance(example, Mapping):
            raise TypeError("training example must be a mapping")
        if "input" not in example or "output" not in example:
            raise ValueError("training example requires input and output grids")
        return cls(
            input_grid=validate_grid(example["input"]),
            output_grid=validate_grid(example["output"]),
        )

    @property
    def input(self) -> Grid:
        return self.input_grid

    @property
    def output(self) -> Grid:
        return self.output_grid

    @property
    def source(self) -> Grid:
        return self.input_grid

    @property
    def target(self) -> Grid:
        return self.output_grid

    @property
    def pair_hash(self) -> str:
        return sha256_record(
            {"input": self.input_grid, "output": self.output_grid}
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composition.training_example",
            "schema_version": self.schema_version,
            "input": canonical_value(self.input_grid),
            "output": canonical_value(self.output_grid),
            "pair_hash": self.pair_hash,
        }

    def to_mapping(self) -> dict[str, list[list[int]]]:
        return {
            "input": canonical_value(self.input_grid),
            "output": canonical_value(self.output_grid),
        }


TrainingPair = TrainingExample


@dataclass(frozen=True, slots=True)
class TrainingTask:
    """A compiler-safe task containing labels only for demonstrations."""

    train: tuple[TrainingExample, ...]
    test_inputs: tuple[Grid, ...]
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "train", tuple(self.train))
        object.__setattr__(self, "test_inputs", tuple(self.test_inputs))
        if not self.train:
            raise ValueError("task must contain at least one training demonstration")
        if not self.test_inputs:
            raise ValueError("task must contain at least one test input")
        if not all(isinstance(example, TrainingExample) for example in self.train):
            raise TypeError("train must contain TrainingExample records")
        object.__setattr__(
            self,
            "test_inputs",
            tuple(validate_grid(grid) for grid in self.test_inputs),
        )
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @classmethod
    def from_mapping(cls, task: Mapping[str, Any]) -> "TrainingTask":
        """Copy a raw ARC task while structurally discarding all test labels."""

        if not isinstance(task, Mapping):
            raise TypeError("task must be a mapping")
        if "train" not in task or "test" not in task:
            raise ValueError("task requires train and test sequences")

        raw_train = _finite_sequence(task["train"], "task train")
        raw_test = _finite_sequence(task["test"], "task test")
        train = tuple(TrainingExample.from_mapping(example) for example in raw_train)

        # Deliberately access exactly one key of every test record.  In
        # particular, never call dict(example), iterate its items, or serialize
        # the raw task: each would copy an attached test output into compiler
        # memory even if it were not later used.
        test_inputs: list[Grid] = []
        for example in raw_test:
            if not isinstance(example, Mapping):
                raise TypeError("test example must be a mapping")
            if "input" not in example:
                raise ValueError("test example requires an input grid")
            test_inputs.append(validate_grid(example["input"]))
        return cls(train=train, test_inputs=tuple(test_inputs))

    @property
    def demonstrations(self) -> tuple[TrainingExample, ...]:
        return self.train

    @property
    def training_pairs(self) -> tuple[tuple[Grid, Grid], ...]:
        return tuple((example.input_grid, example.output_grid) for example in self.train)

    @property
    def training_inputs(self) -> tuple[Grid, ...]:
        return tuple(example.input_grid for example in self.train)

    @property
    def training_outputs(self) -> tuple[Grid, ...]:
        return tuple(example.output_grid for example in self.train)

    @property
    def tests(self) -> tuple[Grid, ...]:
        return self.test_inputs

    @property
    def training_hashes(self) -> tuple[str, ...]:
        return tuple(example.pair_hash for example in self.train)

    @property
    def source_record(self) -> dict[str, Any]:
        """Compiler-visible content; by construction this has no test labels."""

        return {
            "schema": "komorebi.lasm_composition.sanitized_training_task",
            "schema_version": self.schema_version,
            "train": [example.to_mapping() for example in self.train],
            "test": [
                {"input": canonical_value(grid)} for grid in self.test_inputs
            ],
        }

    @property
    def source_hash(self) -> str:
        return sha256_record(self.source_record)

    @property
    def task_hash(self) -> str:
        return self.source_hash

    def to_compile_mapping(self) -> dict[str, Any]:
        """Return a fresh legacy-compatible mapping with sanitized test records."""

        return {
            "train": [example.to_mapping() for example in self.train],
            "test": [
                {"input": canonical_value(grid)} for grid in self.test_inputs
            ],
        }

    def to_record(self) -> dict[str, Any]:
        return {**self.source_record, "source_hash": self.source_hash}


SanitizedTrainingTask = TrainingTask


def sanitize_training_task(task: Mapping[str, Any] | TrainingTask) -> TrainingTask:
    """Return an immutable compiler-safe view of ``task``."""

    if isinstance(task, TrainingTask):
        return task
    return TrainingTask.from_mapping(task)


def sanitize_task(task: Mapping[str, Any] | TrainingTask) -> TrainingTask:
    return sanitize_training_task(task)


def sanitized_task_mapping(task: Mapping[str, Any] | TrainingTask) -> dict[str, Any]:
    return sanitize_training_task(task).to_compile_mapping()


def scrub_test_outputs(task: Mapping[str, Any] | TrainingTask) -> dict[str, Any]:
    """Legacy-friendly spelling for a mapping with input-only test records."""

    return sanitized_task_mapping(task)


__all__ = [
    "Grid",
    "SanitizedTrainingTask",
    "TrainingExample",
    "TrainingPair",
    "TrainingTask",
    "sanitize_task",
    "sanitize_training_task",
    "sanitized_task_mapping",
    "scrub_test_outputs",
    "validate_grid",
]
