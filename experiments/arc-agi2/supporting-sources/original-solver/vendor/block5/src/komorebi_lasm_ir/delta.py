"""Bidirectional demonstration deltas for Program IR v2.

This module analyzes *training* input-output pairs.  It is intentionally kept
separate from runtime execution so an evaluation input cannot acquire answer
information.  The output is a conservative, content-addressed graph of object
correspondences, raster edits, and output-shape relations that can seed a later
program-sketch search.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np

from .arc_scene import ArcObject, Edit, Scene, analyze_grid, derive_edits, freeze_grid


def _normalized_points(obj: ArcObject) -> frozenset[tuple[int, int]]:
    return frozenset((cell.row, cell.column) for cell in obj.normalized_cells)


def _normalize_points(points: Iterable[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    values = tuple(points)
    if not values:
        return frozenset()
    minimum_row = min(row for row, _ in values)
    minimum_column = min(column for _, column in values)
    return frozenset((row - minimum_row, column - minimum_column) for row, column in values)


def _shape_variants(obj: ArcObject) -> tuple[tuple[str, frozenset[tuple[int, int]]], ...]:
    points = _normalized_points(obj)

    def rotate90(values: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
        if not values:
            return values
        height = max(row for row, _ in values) + 1
        return _normalize_points((column, height - 1 - row) for row, column in values)

    def reflect_h(values: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
        if not values:
            return values
        width = max(column for _, column in values) + 1
        return _normalize_points((row, width - 1 - column) for row, column in values)

    candidates: list[tuple[str, frozenset[tuple[int, int]]]] = []
    current = points
    for index, name in enumerate(("identity", "rotate90", "rotate180", "rotate270")):
        if index:
            current = rotate90(current)
        candidates.append((name, current))
    reflected = reflect_h(points)
    current = reflected
    for index, name in enumerate(("reflect_horizontal", "reflect_diagonal", "reflect_vertical", "reflect_antidiagonal")):
        if index:
            current = rotate90(current)
        candidates.append((name, current))
    output: list[tuple[str, frozenset[tuple[int, int]]]] = []
    seen: set[frozenset[tuple[int, int]]] = set()
    for name, value in candidates:
        if value not in seen:
            seen.add(value)
            output.append((name, value))
    return tuple(output)


@dataclass(frozen=True)
class ObjectCorrespondence:
    source_id: str
    target_id: str
    kind: str
    shape_transform: str
    delta_row: int
    delta_column: int
    source_color: int
    target_color: int
    area: int

    def to_record(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AmbiguousCorrespondence:
    source_id: str
    target_ids: tuple[str, ...]
    best_score: tuple[int, int, int, int]

    def to_record(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "target_ids": list(self.target_ids),
            "best_score": list(self.best_score),
        }


@dataclass(frozen=True)
class DeltaGraph:
    source_shape: tuple[int, int]
    target_shape: tuple[int, int]
    shape_relation: str
    correspondences: tuple[ObjectCorrespondence, ...]
    ambiguous: tuple[AmbiguousCorrespondence, ...]
    deleted_source_ids: tuple[str, ...]
    constructed_target_ids: tuple[str, ...]
    edits: tuple[Edit, ...]

    @property
    def fully_corresponded(self) -> bool:
        return not self.ambiguous and not self.deleted_source_ids and not self.constructed_target_ids

    def signature_record(self) -> dict[str, object]:
        return {
            "shape_relation": self.shape_relation,
            "correspondence_kinds": dict(sorted(Counter(item.kind for item in self.correspondences).items())),
            "shape_transforms": dict(sorted(Counter(item.shape_transform for item in self.correspondences).items())),
            "edit_kinds": dict(sorted(Counter(item.kind for item in self.edits).items())),
            "deleted_count": len(self.deleted_source_ids),
            "constructed_count": len(self.constructed_target_ids),
            "ambiguous_count": len(self.ambiguous),
            "fully_corresponded": self.fully_corresponded,
        }

    def to_record(self) -> dict[str, object]:
        return {
            "schema": "komorebi.lasm_delta_graph",
            "schema_version": 1,
            "source_shape": list(self.source_shape),
            "target_shape": list(self.target_shape),
            "shape_relation": self.shape_relation,
            "correspondences": [item.to_record() for item in self.correspondences],
            "ambiguous": [item.to_record() for item in self.ambiguous],
            "deleted_source_ids": list(self.deleted_source_ids),
            "constructed_target_ids": list(self.constructed_target_ids),
            "edits": [
                {
                    "edit_id": item.edit_id,
                    "kind": item.kind,
                    "cells": [[cell.row, cell.column] for cell in item.cells],
                    "source_color": item.source_color,
                    "target_color": item.target_color,
                    "source_shape": list(item.source_shape),
                    "target_shape": list(item.target_shape),
                }
                for item in self.edits
            ],
            "signature": self.signature_record(),
        }

    def content_hash(self) -> str:
        payload = json.dumps(self.to_record(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DeltaPattern:
    source_count: int
    common_shape_relation: str | None
    required_correspondence_kinds: tuple[tuple[str, int], ...]
    required_edit_kinds: tuple[tuple[str, int], ...]
    maximum_ambiguity: int
    source_hashes: tuple[str, ...]

    def to_record(self) -> dict[str, object]:
        return {
            "schema": "komorebi.lasm_delta_pattern",
            "schema_version": 1,
            "source_count": self.source_count,
            "common_shape_relation": self.common_shape_relation,
            "required_correspondence_kinds": dict(self.required_correspondence_kinds),
            "required_edit_kinds": dict(self.required_edit_kinds),
            "maximum_ambiguity": self.maximum_ambiguity,
            "source_hashes": list(self.source_hashes),
        }

    def content_hash(self) -> str:
        payload = json.dumps(self.to_record(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _shape_relation(source: tuple[int, int], target: tuple[int, int]) -> str:
    if source == target:
        return "preserve"
    source_height, source_width = source
    target_height, target_width = target
    if target_height % source_height == 0 and target_width % source_width == 0:
        row_factor = target_height // source_height
        column_factor = target_width // source_width
        if row_factor == column_factor:
            return f"uniform_upscale:{row_factor}"
        return f"anisotropic_upscale:{row_factor}x{column_factor}"
    if source_height % target_height == 0 and source_width % target_width == 0:
        row_factor = source_height // target_height
        column_factor = source_width // target_width
        if row_factor == column_factor:
            return f"uniform_downscale:{row_factor}"
        return f"anisotropic_downscale:{row_factor}x{column_factor}"
    if target_height == source_height and target_width != source_width:
        return "width_constructor"
    if target_width == source_width and target_height != source_height:
        return "height_constructor"
    return "general_constructor"


def _candidate_score(source: ArcObject, target: ArcObject) -> tuple[tuple[int, int, int, int], str] | None:
    target_points = _normalized_points(target)
    transform = None
    transform_rank = 99
    for rank, (name, points) in enumerate(_shape_variants(source)):
        if points == target_points:
            transform = name
            transform_rank = rank
            break
    if transform is None:
        return None
    same_cells = source.cells == target.cells
    same_color = source.color == target.color
    distance = abs(target.box.top - source.box.top) + abs(target.box.left - source.box.left)
    # Lexicographic score: exact support, color change, geometric transform, displacement.
    score = (
        0 if same_cells else 1,
        0 if same_color else 1,
        transform_rank,
        int(distance),
    )
    return score, transform


def _kind(source: ArcObject, target: ArcObject, transform: str) -> str:
    same_cells = source.cells == target.cells
    same_color = source.color == target.color
    moved = source.box.top != target.box.top or source.box.left != target.box.left
    transformed = transform != "identity"
    parts: list[str] = []
    if same_cells and same_color:
        return "preserved"
    if moved:
        parts.append("translated")
    if transformed:
        parts.append("transformed")
    if not same_color:
        parts.append("recolored")
    return "_and_".join(parts) if parts else "support_changed"


def derive_delta_graph(source: object, target: object) -> DeltaGraph:
    source_grid = freeze_grid(source)
    target_grid = freeze_grid(target)
    source_scene = analyze_grid(source_grid)
    target_scene = analyze_grid(target_grid)

    unmatched_sources = {item.object_id: item for item in source_scene.objects}
    unmatched_targets = {item.object_id: item for item in target_scene.objects}
    correspondences: list[ObjectCorrespondence] = []
    ambiguous: list[AmbiguousCorrespondence] = []

    # Repeatedly commit only mutual, unique best matches.  Repetition permits a
    # forced match to become visible after an easier object is removed.
    while unmatched_sources and unmatched_targets:
        source_best: dict[str, tuple[tuple[int, int, int, int], list[tuple[str, str]]]] = {}
        target_best: dict[str, tuple[tuple[int, int, int, int], list[tuple[str, str]]]] = {}
        for source_id, source_object in unmatched_sources.items():
            for target_id, target_object in unmatched_targets.items():
                candidate = _candidate_score(source_object, target_object)
                if candidate is None:
                    continue
                score, transform = candidate
                current = source_best.get(source_id)
                if current is None or score < current[0]:
                    source_best[source_id] = (score, [(target_id, transform)])
                elif score == current[0]:
                    current[1].append((target_id, transform))
                current_target = target_best.get(target_id)
                if current_target is None or score < current_target[0]:
                    target_best[target_id] = (score, [(source_id, transform)])
                elif score == current_target[0]:
                    current_target[1].append((source_id, transform))

        forced: list[tuple[str, str, str, tuple[int, int, int, int]]] = []
        for source_id, (score, targets) in source_best.items():
            if len(targets) != 1:
                continue
            target_id, transform = targets[0]
            target_choice = target_best.get(target_id)
            if target_choice is None or len(target_choice[1]) != 1:
                continue
            if target_choice[1][0][0] == source_id:
                forced.append((source_id, target_id, transform, score))
        if not forced:
            break
        for source_id, target_id, transform, _ in sorted(forced):
            if source_id not in unmatched_sources or target_id not in unmatched_targets:
                continue
            source_object = unmatched_sources.pop(source_id)
            target_object = unmatched_targets.pop(target_id)
            correspondences.append(
                ObjectCorrespondence(
                    source_id=source_id,
                    target_id=target_id,
                    kind=_kind(source_object, target_object, transform),
                    shape_transform=transform,
                    delta_row=int(target_object.box.top - source_object.box.top),
                    delta_column=int(target_object.box.left - source_object.box.left),
                    source_color=int(source_object.color),
                    target_color=int(target_object.color),
                    area=int(source_object.area),
                )
            )

    # Record unresolved equal-cost alternatives rather than choosing an
    # arbitrary repeated object.  This is compiler evidence, not a guess.
    for source_id, source_object in sorted(unmatched_sources.items()):
        options: list[tuple[tuple[int, int, int, int], str]] = []
        for target_id, target_object in unmatched_targets.items():
            candidate = _candidate_score(source_object, target_object)
            if candidate is not None:
                options.append((candidate[0], target_id))
        if options:
            best_score = min(score for score, _ in options)
            winners = tuple(sorted(target_id for score, target_id in options if score == best_score))
            if winners:
                ambiguous.append(AmbiguousCorrespondence(source_id, winners, best_score))

    shape_relation = _shape_relation(source_scene.shape, target_scene.shape)
    edits = derive_edits(source_grid, target_grid)
    return DeltaGraph(
        source_shape=source_scene.shape,
        target_shape=target_scene.shape,
        shape_relation=shape_relation,
        correspondences=tuple(sorted(correspondences, key=lambda item: (item.source_id, item.target_id))),
        ambiguous=tuple(sorted(ambiguous, key=lambda item: item.source_id)),
        deleted_source_ids=tuple(sorted(unmatched_sources)),
        constructed_target_ids=tuple(sorted(unmatched_targets)),
        edits=edits,
    )


def anti_unify_delta_graphs(graphs: Sequence[DeltaGraph]) -> DeltaPattern:
    if len(graphs) < 2:
        raise ValueError("delta anti-unification requires at least two demonstrations")
    shape_relations = {graph.shape_relation for graph in graphs}

    def minimum_histogram(histograms: Sequence[Counter[str]]) -> tuple[tuple[str, int], ...]:
        keys = set.intersection(*(set(histogram) for histogram in histograms)) if histograms else set()
        return tuple(sorted((key, min(histogram[key] for histogram in histograms)) for key in keys))

    correspondence_histograms = [Counter(item.kind for item in graph.correspondences) for graph in graphs]
    edit_histograms = [Counter(item.kind for item in graph.edits) for graph in graphs]
    return DeltaPattern(
        source_count=len(graphs),
        common_shape_relation=next(iter(shape_relations)) if len(shape_relations) == 1 else None,
        required_correspondence_kinds=minimum_histogram(correspondence_histograms),
        required_edit_kinds=minimum_histogram(edit_histograms),
        maximum_ambiguity=max(len(graph.ambiguous) for graph in graphs),
        source_hashes=tuple(sorted(graph.content_hash() for graph in graphs)),
    )


def derive_task_delta_pattern(task: Mapping[str, object]) -> DeltaPattern:
    raw_train = task.get("train")
    if not isinstance(raw_train, Sequence) or len(raw_train) < 2:
        raise ValueError("task requires at least two training demonstrations")
    graphs = []
    for example in raw_train:
        if not isinstance(example, Mapping) or "input" not in example or "output" not in example:
            raise TypeError("training demonstrations require input and output grids")
        graphs.append(derive_delta_graph(example["input"], example["output"]))
    return anti_unify_delta_graphs(graphs)


__all__ = [
    "AmbiguousCorrespondence",
    "DeltaGraph",
    "DeltaPattern",
    "ObjectCorrespondence",
    "anti_unify_delta_graphs",
    "derive_delta_graph",
    "derive_task_delta_pattern",
]
