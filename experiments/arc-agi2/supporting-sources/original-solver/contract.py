"""Block 14 deterministic, label-separated tournament infrastructure.

Canonical runs load entrants from an explicit name-to-SHA-256 allowlist that
is completely verified before any module executes.  Entrants receive only
demonstrations and test inputs.  A module may additionally expose
``replay_program(program, grid)``; when present, every cached candidate output
is recomputed from the serialized program.  Replay hooks may return either a
grid or ``{"output": grid, "stages": [...]}``, where each stage contains
``name``, ``input``, and ``output``.  Detailed traces are checked as exact
chains and reduced to hash-sealed stage receipts.

Freezing, retrospective scoring, and promotion are deliberately separate.
Promotion starts from the baseline and commits only output positions whose
authenticated score proves a new exact pass@2 gain.  Attempt 1 is immutable.

Only the Python standard library is required.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence


SCHEMA_PREFIX = "komorebi.pr_lasm.block14"
AUTHOR = "Komorebi P."
DEFAULT_LIMITS: dict[str, int] = {
    "max_candidates": 256,
    "candidate_cap": 256,
    "max_total_candidates": 2048,
    "max_replay_calls": 4096,
    "max_replay_stages": 64,
    "max_trace_bytes": 1_000_000,
}
_REQUIRED_CANDIDATE_KEYS = frozenset(
    {"family", "program", "train_outputs", "test_outputs", "complexity", "evidence"}
)
_TRACE_KEYS = frozenset({"output", "stages"})
_STAGE_KEYS = frozenset({"name", "input", "output"})
_VOLATILE_SEMANTIC_KEYS = frozenset({"runtime_seconds"})


class TournamentError(RuntimeError):
    """Base class for fail-closed tournament errors."""


class CandidateContractError(TournamentError):
    """An entrant returned a value outside the candidate contract."""


def canonical_json(value: Any) -> str:
    """Return the canonical JSON representation used by every digest."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path: str | Path, value: Any) -> None:
    """Atomically write finite, deterministic JSON."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".partial")
    temporary.unlink(missing_ok=True)
    try:
        temporary.write_text(
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _json_copy(value: Any, *, what: str) -> Any:
    try:
        return json.loads(canonical_json(value))
    except (TypeError, ValueError) as error:
        raise CandidateContractError(f"{what} is not finite JSON: {error}") from error


def validate_grid(value: Any, *, what: str = "grid") -> list[list[int]]:
    if not isinstance(value, list) or not value or len(value) > 30:
        raise ValueError(f"{what} must have between 1 and 30 rows")
    if not all(isinstance(row, list) and row for row in value):
        raise ValueError(f"{what} rows must be nonempty lists")
    width = len(value[0])
    if width > 30 or any(len(row) != width for row in value):
        raise ValueError(f"{what} must be rectangular with width at most 30")
    result: list[list[int]] = []
    for row in value:
        normalized: list[int] = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError(f"{what} cells must be integer colors in [0, 9]")
            normalized.append(cell)
        result.append(normalized)
    return result


def sanitize_task(task: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Strip task identity, metadata, and attached test outputs."""

    if not isinstance(task, Mapping):
        raise ValueError("task must be a mapping")
    train = task.get("train")
    test = task.get("test")
    if not isinstance(train, list) or not train:
        raise ValueError("task.train must be a nonempty list")
    if not isinstance(test, list) or not test:
        raise ValueError("task.test must be a nonempty list")
    if len(train) > 10 or len(test) > 10:
        raise ValueError("task arity exceeds the finite tournament contract")
    clean_train: list[dict[str, Any]] = []
    clean_test: list[dict[str, Any]] = []
    for index, example in enumerate(train):
        if not isinstance(example, Mapping) or "input" not in example or "output" not in example:
            raise ValueError(f"train[{index}] must contain input and output")
        clean_train.append(
            {
                "input": validate_grid(example["input"], what=f"train[{index}].input"),
                "output": validate_grid(example["output"], what=f"train[{index}].output"),
            }
        )
    for index, example in enumerate(test):
        if not isinstance(example, Mapping) or "input" not in example:
            raise ValueError(f"test[{index}] must contain input")
        clean_test.append(
            {"input": validate_grid(example["input"], what=f"test[{index}].input")}
        )
    return {"train": clean_train, "test": clean_test}


def task_semantic_hash(task: Mapping[str, Any]) -> str:
    return digest(sanitize_task(task))


def _semantic_body(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in _VOLATILE_SEMANTIC_KEYS | {"semantic_hash", "content_hash"}
    }


def seal_record(body: Mapping[str, Any]) -> dict[str, Any]:
    result = _json_copy(dict(body), what="record")
    result.pop("semantic_hash", None)
    result.pop("content_hash", None)
    result["semantic_hash"] = digest(_semantic_body(result))
    result["content_hash"] = digest(
        {key: value for key, value in result.items() if key != "content_hash"}
    )
    return result


def verify_seal(record: Mapping[str, Any], *, schema: str | None = None) -> None:
    if not isinstance(record, Mapping):
        raise TournamentError("sealed record must be a mapping")
    if schema is not None and record.get("schema") != schema:
        raise TournamentError(f"expected {schema!r} record")
    if record.get("semantic_hash") != digest(_semantic_body(record)):
        raise TournamentError("semantic hash mismatch")
    if record.get("content_hash") != digest(
        {key: value for key, value in record.items() if key != "content_hash"}
    ):
        raise TournamentError("content hash mismatch")


def _normalize_limits(limits: Mapping[str, Any] | None) -> dict[str, int]:
    result: dict[str, Any] = dict(DEFAULT_LIMITS)
    if limits is not None:
        if not isinstance(limits, Mapping):
            raise ValueError("limits must be a mapping")
        result.update(_json_copy(dict(limits), what="limits"))
    for key in DEFAULT_LIMITS:
        value = result.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"limits.{key} must be a positive integer")
    if result["max_candidates"] != result["candidate_cap"]:
        raise ValueError("max_candidates and candidate_cap must agree")
    return {key: int(result[key]) for key in sorted(result)}


def _normalize_allowlist(
    allowlist: Mapping[str, str] | None,
) -> dict[str, str]:
    if allowlist is None:
        raise TournamentError("canonical runs require a hash-pinned entrant allowlist")
    if not isinstance(allowlist, Mapping) or not allowlist:
        raise TournamentError("entrant allowlist must be a nonempty name-to-SHA-256 mapping")
    result: dict[str, str] = {}
    for name, expected_hash in allowlist.items():
        if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
            raise TournamentError("entrant names must be public Python identifiers")
        if (
            not isinstance(expected_hash, str)
            or len(expected_hash) != 64
            or expected_hash != expected_hash.lower()
            or any(character not in "0123456789abcdef" for character in expected_hash)
        ):
            raise TournamentError(
                f"entrant allowlist hash for {name} must be lowercase SHA-256"
            )
        result[name] = expected_hash
    return dict(sorted(result.items()))


@dataclass(frozen=True, slots=True)
class Entrant:
    name: str
    path: Path
    source_hash: str
    module: ModuleType
    compile_task: Callable[..., Any]
    replay_program: Callable[..., Any] | None


def load_entrants(
    entrants_dir: str | Path,
    entrant_allowlist: Mapping[str, str] | None,
) -> tuple[Entrant, ...]:
    """Hash-check every allowlisted source before executing any entrant module."""

    root = Path(entrants_dir).resolve()
    if not root.is_dir():
        raise TournamentError(f"entrant directory does not exist: {root}")
    allowlist = _normalize_allowlist(entrant_allowlist)
    # Complete preflight is intentionally separate from imports.  One missing,
    # redirected, or changed source prevents *all* entrant code from executing.
    sources: list[tuple[str, Path, str]] = []
    for name, expected_hash in allowlist.items():
        unresolved = root / f"{name}.py"
        if unresolved.is_symlink():
            raise TournamentError(f"entrant {name} must not be a symlink")
        if not unresolved.is_file():
            raise TournamentError(f"allowlisted entrant is missing: {name}")
        path = unresolved.resolve()
        if path.parent != root:
            raise TournamentError(f"entrant {name} resolves outside the entrant directory")
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise TournamentError(f"entrant source hash mismatch for {name}")
        sources.append((name, path, actual_hash))

    loaded: list[Entrant] = []
    for name, path, source_hash in sources:
        module_name = f"_komorebi_block14_entrant_{name}_{source_hash[:16]}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise TournamentError(f"cannot create import specification for entrant {name}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException as error:
            sys.modules.pop(module_name, None)
            raise TournamentError(
                f"entrant {name} failed to import: {type(error).__name__}: {error}"
            ) from error
        compiler = getattr(module, "compile_task", None)
        if not callable(compiler):
            raise TournamentError(f"entrant {name} does not expose callable compile_task")
        hook = getattr(module, "replay_program", None)
        if hook is not None and not callable(hook):
            raise TournamentError(f"entrant {name}.replay_program is not callable")
        loaded.append(Entrant(name, path, source_hash, module, compiler, hook))
    return tuple(loaded)


def _bounded_state(value: Any, *, what: str, remaining_bytes: list[int]) -> Any:
    detached = _json_copy(value, what=what)
    size = len(canonical_json(detached).encode("utf-8"))
    remaining_bytes[0] -= size
    if remaining_bytes[0] < 0:
        raise CandidateContractError("replay trace exceeded max_trace_bytes")
    return detached


def _seal_stage(
    *, index: int, name: str, source: Any, successor: Any, program_hash: str
) -> dict[str, Any]:
    body = {
        "index": index,
        "name": name,
        "program_hash": program_hash,
        "source_hash": digest(source),
        "successor_hash": digest(successor),
    }
    body["receipt_hash"] = digest(body)
    return body


def _replay_one(
    hook: Callable[..., Any],
    *,
    program: Mapping[str, Any],
    grid: list[list[int]],
    limits: Mapping[str, int],
    what: str,
) -> tuple[list[list[int]], dict[str, Any]]:
    program_arg = copy.deepcopy(dict(program))
    grid_arg = copy.deepcopy(grid)
    program_before = canonical_json(program_arg)
    grid_before = canonical_json(grid_arg)
    try:
        raw = hook(program_arg, grid_arg)
    except BaseException as error:
        raise CandidateContractError(
            f"{what} replay_program failed: {type(error).__name__}: {error}"
        ) from error
    try:
        if canonical_json(program_arg) != program_before or canonical_json(grid_arg) != grid_before:
            raise CandidateContractError(f"{what} replay_program mutated an argument")
    except (TypeError, ValueError) as error:
        raise CandidateContractError(
            f"{what} replay_program made an argument non-JSON: {error}"
        ) from error

    program_hash = digest(program)
    remaining_bytes = [int(limits["max_trace_bytes"])]
    detailed = isinstance(raw, Mapping)
    if detailed:
        if frozenset(raw) != _TRACE_KEYS:
            raise CandidateContractError(
                f"{what} detailed replay must contain exactly output and stages"
            )
        try:
            output = validate_grid(raw["output"], what=f"{what}.output")
        except ValueError as error:
            raise CandidateContractError(str(error)) from error
        raw_stages = raw["stages"]
        if not isinstance(raw_stages, list) or not raw_stages:
            raise CandidateContractError(f"{what}.stages must be a nonempty list")
        if len(raw_stages) > int(limits["max_replay_stages"]):
            raise CandidateContractError(f"{what} exceeded max_replay_stages")
        previous: Any = copy.deepcopy(grid)
        stages: list[dict[str, Any]] = []
        for index, raw_stage in enumerate(raw_stages):
            if not isinstance(raw_stage, Mapping) or frozenset(raw_stage) != _STAGE_KEYS:
                raise CandidateContractError(
                    f"{what}.stages[{index}] must contain exactly name, input, and output"
                )
            name = raw_stage["name"]
            if not isinstance(name, str) or not name.strip() or len(name) > 128:
                raise CandidateContractError(
                    f"{what}.stages[{index}].name must be a short nonempty string"
                )
            source = _bounded_state(
                raw_stage["input"],
                what=f"{what}.stages[{index}].input",
                remaining_bytes=remaining_bytes,
            )
            successor = _bounded_state(
                raw_stage["output"],
                what=f"{what}.stages[{index}].output",
                remaining_bytes=remaining_bytes,
            )
            if source != previous:
                raise CandidateContractError(f"{what}.stages[{index}] breaks the state chain")
            stages.append(
                _seal_stage(
                    index=index,
                    name=name.strip(),
                    source=source,
                    successor=successor,
                    program_hash=program_hash,
                )
            )
            previous = successor
        if previous != output:
            raise CandidateContractError(f"{what} final stage does not equal replay output")
        trace_mode = "detailed"
    else:
        try:
            output = validate_grid(raw, what=f"{what}.output")
        except ValueError as error:
            raise CandidateContractError(str(error)) from error
        stages = [
            _seal_stage(
                index=0,
                name="program",
                source=grid,
                successor=output,
                program_hash=program_hash,
            )
        ]
        trace_mode = "single_stage"

    body = {
        "trace_mode": trace_mode,
        "program_hash": program_hash,
        "input_hash": digest(grid),
        "output_hash": digest(output),
        "stage_count": len(stages),
        "stages": stages,
    }
    body["receipt_hash"] = digest(body)
    return output, body


def verify_replay_receipt(bundle: Mapping[str, Any], *, program_hash: str) -> None:
    """Verify the compact stage chain embedded in a frozen candidate."""

    if not isinstance(bundle, Mapping):
        raise TournamentError("replay receipt must be a mapping")
    required = {
        "trace_mode",
        "program_hash",
        "input_hash",
        "output_hash",
        "stage_count",
        "stages",
        "example_index",
        "receipt_hash",
    }
    if set(bundle) != required:
        raise TournamentError("replay receipt fields are malformed")
    if bundle.get("program_hash") != program_hash:
        raise TournamentError("replay receipt is bound to another program")
    if bundle.get("receipt_hash") != digest(
        {key: value for key, value in bundle.items() if key != "receipt_hash"}
    ):
        raise TournamentError("replay receipt hash mismatch")
    stages = bundle.get("stages")
    if not isinstance(stages, list) or not stages:
        raise TournamentError("replay receipt has no stages")
    if bundle.get("stage_count") != len(stages):
        raise TournamentError("replay stage count mismatch")
    previous = bundle.get("input_hash")
    for index, stage in enumerate(stages):
        if not isinstance(stage, Mapping):
            raise TournamentError("stage receipt must be a mapping")
        required_stage = {
            "index", "name", "program_hash", "source_hash", "successor_hash", "receipt_hash"
        }
        if set(stage) != required_stage:
            raise TournamentError("stage receipt fields are malformed")
        if stage.get("index") != index:
            raise TournamentError("stage receipt indices are not contiguous")
        if stage.get("program_hash") != program_hash:
            raise TournamentError("stage receipt is bound to another program")
        if stage.get("source_hash") != previous:
            raise TournamentError("stage receipt hash chain is broken")
        if stage.get("receipt_hash") != digest(
            {key: value for key, value in stage.items() if key != "receipt_hash"}
        ):
            raise TournamentError("stage receipt hash mismatch")
        previous = stage.get("successor_hash")
    if previous != bundle.get("output_hash"):
        raise TournamentError("stage receipts do not reach the replay output")


def _replay_candidate(
    entrant: Entrant,
    *,
    program: Mapping[str, Any],
    task: Mapping[str, Any],
    expected_train: Sequence[list[list[int]]],
    expected_test: Sequence[list[list[int]]],
    limits: Mapping[str, int],
) -> dict[str, Any]:
    program_hash = digest(program)
    if entrant.replay_program is None:
        return {
            "status": "not_supplied",
            "hook": None,
            "program_hash": program_hash,
            "train": [],
            "test": [],
        }

    arity = len(task["train"]) + len(task["test"])
    if arity > int(limits["max_replay_calls"]):
        raise CandidateContractError("candidate replay exceeded max_replay_calls")
    train_receipts: list[dict[str, Any]] = []
    test_receipts: list[dict[str, Any]] = []
    for split, examples, expected, destination in (
        ("train", task["train"], expected_train, train_receipts),
        ("test", task["test"], expected_test, test_receipts),
    ):
        for index, (example, cached_output) in enumerate(zip(examples, expected)):
            output, receipt = _replay_one(
                entrant.replay_program,
                program=program,
                grid=example["input"],
                limits=limits,
                what=f"{split}[{index}]",
            )
            if output != cached_output:
                raise CandidateContractError(
                    f"serialized program replay disagrees with cached {split}[{index}] output"
                )
            receipt["example_index"] = index
            receipt["receipt_hash"] = digest(
                {key: value for key, value in receipt.items() if key != "receipt_hash"}
            )
            destination.append(receipt)
    body = {
        "status": "verified",
        "hook": "replay_program(program, grid)",
        "program_hash": program_hash,
        "train": train_receipts,
        "test": test_receipts,
    }
    body["content_hash"] = digest(body)
    return body


def _normalize_candidate(
    raw: Any,
    *,
    entrant: Entrant,
    task: Mapping[str, Any],
    limits: Mapping[str, int],
) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise CandidateContractError("candidate must be a mapping")
    if any(not isinstance(key, str) for key in raw):
        raise CandidateContractError("candidate keys must be strings")
    keys = frozenset(raw)
    missing = sorted(_REQUIRED_CANDIDATE_KEYS - keys)
    extra = sorted(keys - _REQUIRED_CANDIDATE_KEYS)
    if missing or extra:
        raise CandidateContractError(
            f"candidate keys violate contract: missing={missing}, extra={extra}"
        )
    detached = _json_copy(dict(raw), what="candidate")
    family = detached["family"]
    if not isinstance(family, str) or not family.strip():
        raise CandidateContractError("candidate.family must be a nonempty string")
    if not isinstance(detached["program"], dict):
        raise CandidateContractError("candidate.program must be a JSON object")
    if not isinstance(detached["evidence"], dict):
        raise CandidateContractError("candidate.evidence must be a JSON object")
    complexity = detached["complexity"]
    if isinstance(complexity, bool) or not isinstance(complexity, int) or complexity < 0:
        raise CandidateContractError("candidate.complexity must be a nonnegative integer")
    train_outputs = detached["train_outputs"]
    test_outputs = detached["test_outputs"]
    if not isinstance(train_outputs, list) or len(train_outputs) != len(task["train"]):
        raise CandidateContractError("candidate train output arity mismatch")
    if not isinstance(test_outputs, list) or len(test_outputs) != len(task["test"]):
        raise CandidateContractError("candidate test output arity mismatch")
    try:
        normalized_train = [
            validate_grid(grid, what=f"candidate.train_outputs[{index}]")
            for index, grid in enumerate(train_outputs)
        ]
        normalized_test = [
            validate_grid(grid, what=f"candidate.test_outputs[{index}]")
            for index, grid in enumerate(test_outputs)
        ]
    except ValueError as error:
        raise CandidateContractError(str(error)) from error
    expected_demonstrations = [example["output"] for example in task["train"]]
    if normalized_train != expected_demonstrations:
        raise CandidateContractError("candidate does not exactly replay every demonstration")
    for key in ("all_demos_exact", "all_demonstrations_exact", "exact_replay"):
        if key in detached["evidence"] and detached["evidence"][key] is not True:
            raise CandidateContractError(f"candidate evidence falsely reports {key}")

    execution_replay = _replay_candidate(
        entrant,
        program=detached["program"],
        task=task,
        expected_train=normalized_train,
        expected_test=normalized_test,
        limits=limits,
    )
    body = {
        "entrant": entrant.name,
        "family": family.strip(),
        "program": detached["program"],
        "train_outputs": normalized_train,
        "test_outputs": normalized_test,
        "complexity": complexity,
        "evidence": detached["evidence"],
        "execution_replay": execution_replay,
        "behavior_hash": digest(normalized_test),
    }
    body["candidate_hash"] = digest(body)
    return body


def _compile_one(
    entrant: Entrant,
    task: Mapping[str, Any],
    limits: Mapping[str, int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = copy.deepcopy(task)
    before = canonical_json(payload)
    try:
        raw = entrant.compile_task(payload, limits=copy.deepcopy(dict(limits)))
    except BaseException as error:
        return [], {
            "status": "compiler_error",
            "proposals": 0,
            "error": f"{type(error).__name__}: {error}",
        }
    try:
        after = canonical_json(payload)
    except (TypeError, ValueError) as error:
        return [], {
            "status": "input_mutation_error",
            "proposals": 0,
            "error": f"entrant made its task non-JSON: {error}",
        }
    if after != before:
        return [], {
            "status": "input_mutation_error",
            "proposals": 0,
            "error": "entrant mutated its sanitized task argument",
        }
    if not isinstance(raw, list):
        return [], {
            "status": "contract_error",
            "proposals": 0,
            "error": "compile_task must return a list",
        }
    if len(raw) > int(limits["max_candidates"]):
        return [], {
            "status": "limit_error",
            "proposals": len(raw),
            "error": "entrant exceeded max_candidates",
        }
    replay_calls = len(raw) * (len(task["train"]) + len(task["test"]))
    if entrant.replay_program is not None and replay_calls > int(limits["max_replay_calls"]):
        return [], {
            "status": "limit_error",
            "proposals": len(raw),
            "error": "entrant candidate set exceeded max_replay_calls",
        }
    try:
        normalized = [
            _normalize_candidate(candidate, entrant=entrant, task=task, limits=limits)
            for candidate in raw
        ]
    except (CandidateContractError, ValueError) as error:
        return [], {
            "status": "contract_error",
            "proposals": len(raw),
            "error": f"{type(error).__name__}: {error}",
        }
    by_hash = {candidate["candidate_hash"]: candidate for candidate in normalized}
    retained = sorted(
        by_hash.values(),
        key=lambda item: (
            item["behavior_hash"],
            item["complexity"],
            item["family"],
            item["candidate_hash"],
        ),
    )
    return retained, {
        "status": "ok",
        "proposals": len(raw),
        "retained_candidates": len(retained),
        "behavior_count": len({item["behavior_hash"] for item in retained}),
        "program_replay": "verified" if entrant.replay_program is not None else "not_supplied",
        "replay_calls": replay_calls if entrant.replay_program is not None else 0,
        "error": None,
    }


def _behavior_records(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for candidate in candidates:
        groups.setdefault(str(candidate["behavior_hash"]), []).append(candidate)
    result: list[dict[str, Any]] = []
    for behavior_hash in sorted(groups):
        members = sorted(groups[behavior_hash], key=lambda item: item["candidate_hash"])
        outputs = members[0]["test_outputs"]
        if any(member["test_outputs"] != outputs for member in members[1:]):
            raise TournamentError("SHA-256 collision across unequal raster behaviors")
        body = {
            "behavior_hash": behavior_hash,
            "test_outputs": copy.deepcopy(outputs),
            "candidate_hashes": [member["candidate_hash"] for member in members],
            "entrants": sorted({str(member["entrant"]) for member in members}),
            "families": sorted(
                {f"{member['entrant']}:{member['family']}" for member in members}
            ),
            "minimum_complexity": min(int(member["complexity"]) for member in members),
        }
        body["content_hash"] = digest(body)
        result.append(body)
    return result


def _validate_submission_task(
    submission: Mapping[str, Any], task_id: str, count: int
) -> list[dict[str, list[list[int]]]]:
    if task_id not in submission:
        raise ValueError(f"submission is missing task {task_id}")
    items = submission[task_id]
    if not isinstance(items, list) or len(items) != count:
        raise ValueError(f"submission output arity mismatch for task {task_id}")
    result: list[dict[str, list[list[int]]]] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping) or set(item) != {"attempt_1", "attempt_2"}:
            raise ValueError(
                f"submission[{task_id}][{index}] must contain exactly attempt_1 and attempt_2"
            )
        result.append(
            {
                "attempt_1": validate_grid(
                    item["attempt_1"], what=f"submission[{task_id}][{index}].attempt_1"
                ),
                "attempt_2": validate_grid(
                    item["attempt_2"], what=f"submission[{task_id}][{index}].attempt_2"
                ),
            }
        )
    return result


def _attempt_1_hash(submission: Mapping[str, Any]) -> str:
    return digest(
        {
            str(task_id): [copy.deepcopy(item["attempt_1"]) for item in items]
            for task_id, items in sorted(submission.items(), key=lambda pair: str(pair[0]))
        }
    )


def _replace_attempt_2(
    submission: dict[str, Any], task_id: str, outputs: Sequence[Any]
) -> None:
    if task_id not in submission or len(submission[task_id]) != len(outputs):
        raise TournamentError("selected output arity does not match baseline")
    for index, output in enumerate(outputs):
        submission[task_id][index]["attempt_2"] = copy.deepcopy(output)


def freeze_tournament(
    challenges: Mapping[str, Mapping[str, Any]],
    baseline: Mapping[str, Any],
    *,
    entrants_dir: str | Path,
    entrant_allowlist: Mapping[str, str] | None,
    limits: Mapping[str, Any] | None = None,
    require_replay: bool = False,
    source_hashes: Mapping[str, str] | None = None,
    run_name: str | None = None,
) -> dict[str, Any]:
    """Freeze an explicitly allowlisted tournament without accepting solutions."""

    if not isinstance(challenges, Mapping) or not challenges:
        raise ValueError("challenges must be a nonempty mapping")
    if not isinstance(baseline, Mapping) or not baseline:
        raise ValueError("baseline must be a nonempty mapping")
    if not isinstance(require_replay, bool):
        raise ValueError("require_replay must be Boolean")
    normalized_limits = _normalize_limits(limits)
    normalized_allowlist = _normalize_allowlist(entrant_allowlist)
    entrants = load_entrants(entrants_dir, normalized_allowlist)
    missing_hooks = [entrant.name for entrant in entrants if entrant.replay_program is None]
    if require_replay and missing_hooks:
        raise TournamentError(
            "required replay_program hook missing from: " + ", ".join(missing_hooks)
        )

    baseline_copy = _json_copy(dict(baseline), what="baseline submission")
    submission = copy.deepcopy(baseline_copy)
    before_attempt_1 = _attempt_1_hash(baseline_copy)
    records: dict[str, Any] = {}
    totals = {
        "tasks": 0,
        "proposed_candidates": 0,
        "retained_candidates": 0,
        "behaviors": 0,
        "selected_tasks": 0,
        "ambiguous_tasks": 0,
        "error_tasks": 0,
        "limit_error_tasks": 0,
        "replay_verified_candidates": 0,
    }

    for raw_task_id, raw_task in sorted(challenges.items(), key=lambda pair: str(pair[0])):
        task_id = str(raw_task_id)
        totals["tasks"] += 1
        errors: list[str] = []
        entrant_receipts: dict[str, Any] = {}
        candidates: list[dict[str, Any]] = []
        try:
            safe_task = sanitize_task(raw_task)
            _validate_submission_task(baseline_copy, task_id, len(safe_task["test"]))
        except (KeyError, ValueError) as error:
            safe_task = {"train": [], "test": []}
            errors.append(f"input_contract: {type(error).__name__}: {error}")

        if not errors:
            for entrant in entrants:
                retained, receipt = _compile_one(entrant, safe_task, normalized_limits)
                entrant_receipts[entrant.name] = receipt
                totals["proposed_candidates"] += int(receipt.get("proposals", 0))
                if receipt["status"] != "ok":
                    errors.append(f"{entrant.name}: {receipt['error']}")
                    if receipt["status"] == "limit_error":
                        totals["limit_error_tasks"] += 1
                candidates.extend(retained)

        candidates = sorted(
            {item["candidate_hash"]: item for item in candidates}.values(),
            key=lambda item: (
                item["behavior_hash"],
                item["complexity"],
                item["entrant"],
                item["family"],
                item["candidate_hash"],
            ),
        )
        if len(candidates) > int(normalized_limits["max_total_candidates"]):
            errors.append("tournament: aggregate max_total_candidates exceeded")
            totals["limit_error_tasks"] += 1
        behaviors = _behavior_records(candidates)
        totals["retained_candidates"] += len(candidates)
        totals["behaviors"] += len(behaviors)
        totals["replay_verified_candidates"] += sum(
            candidate["execution_replay"]["status"] == "verified"
            for candidate in candidates
        )
        selected_behavior_hash = ""
        if errors:
            status = "error_abstention"
            totals["error_tasks"] += 1
        elif len(behaviors) > 1:
            status = "ambiguous_abstention"
            totals["ambiguous_tasks"] += 1
        elif len(behaviors) == 1:
            status = "selected_unique_behavior"
            selected_behavior_hash = behaviors[0]["behavior_hash"]
            _replace_attempt_2(submission, task_id, behaviors[0]["test_outputs"])
            totals["selected_tasks"] += 1
        else:
            status = "no_candidate"

        record = {
            "task_semantic_hash": task_semantic_hash(raw_task),
            "status": status,
            "selection_complete": not errors,
            "retained_candidate_count": len(candidates),
            "behavior_count": len(behaviors),
            "selected_behavior_hash": selected_behavior_hash,
            "entrants": entrant_receipts,
            "candidates": candidates,
            "behaviors": behaviors,
            "errors": errors,
        }
        record["content_hash"] = digest(record)
        records[task_id] = record

    if _attempt_1_hash(submission) != before_attempt_1:
        raise TournamentError("Attempt 1 changed while applying the challenger overlay")
    hashes = dict(sorted((source_hashes or {}).items()))
    hashes.setdefault(
        "challenges_semantic",
        digest({str(key): sanitize_task(value) for key, value in challenges.items()}),
    )
    hashes.setdefault("baseline_semantic", digest(baseline_copy))
    body = {
        "schema": f"{SCHEMA_PREFIX}.frozen_tournament",
        "schema_version": 1,
        "author": AUTHOR,
        "run_name": run_name or "block14-frozen-challenger",
        "phase": "prediction_freeze_before_solution_open",
        "label_access": "none",
        "task_identity_visible_to_entrants": False,
        "entrant_loading_policy": "explicit_allowlist_only",
        "program_replay_policy": "required" if require_replay else "verify_if_supplied",
        "stage_receipt_policy": "exact_chain_then_hash_seal",
        "selected_task_ids": sorted(str(key) for key in challenges),
        "selected_entrants": [entrant.name for entrant in entrants],
        "entrant_allowlist": normalized_allowlist,
        "entrant_allowlist_hash": digest(normalized_allowlist),
        "entrant_source_hashes": {entrant.name: entrant.source_hash for entrant in entrants},
        "limits": normalized_limits,
        "source_hashes": hashes,
        "baseline_attempt_1_hash": before_attempt_1,
        "baseline_semantic_hash": digest(baseline_copy),
        "records": records,
        "totals": totals,
        "submission": submission,
        "claim_boundary": (
            "Entrants received labelled demonstrations and sanitized test inputs. "
            "No solution file was accepted or opened during this freeze."
        ),
    }
    return seal_record(body)


def rebuild_submission(
    baseline: Mapping[str, Any], frozen: Mapping[str, Any]
) -> dict[str, Any]:
    submission = _json_copy(dict(baseline), what="baseline submission")
    before = _attempt_1_hash(submission)
    records = frozen.get("records")
    if not isinstance(records, Mapping):
        raise TournamentError("freeze records are malformed")
    for task_id, record in sorted(records.items()):
        if record.get("status") != "selected_unique_behavior":
            continue
        if record.get("errors") or not record.get("selection_complete"):
            raise TournamentError("errored or incomplete record claims a selection")
        behaviors = record.get("behaviors")
        if not isinstance(behaviors, list) or len(behaviors) != 1:
            raise TournamentError("selected record does not contain one behavior")
        behavior = behaviors[0]
        if record.get("selected_behavior_hash") != behavior.get("behavior_hash"):
            raise TournamentError("selected behavior hash mismatch")
        _replace_attempt_2(submission, str(task_id), behavior["test_outputs"])
    if _attempt_1_hash(submission) != before:
        raise TournamentError("Attempt 1 changed during overlay rebuild")
    return submission


def verify_freeze(
    frozen: Mapping[str, Any], baseline: Mapping[str, Any] | None = None
) -> None:
    verify_seal(frozen, schema=f"{SCHEMA_PREFIX}.frozen_tournament")
    if frozen.get("phase") != "prediction_freeze_before_solution_open":
        raise TournamentError("record is not a pre-solution prediction freeze")
    if frozen.get("label_access") != "none":
        raise TournamentError("freeze crossed the label boundary")
    if frozen.get("entrant_loading_policy") != "explicit_allowlist_only":
        raise TournamentError("freeze did not use an explicit entrant allowlist")
    selected = frozen.get("selected_entrants")
    if not isinstance(selected, list) or not selected or selected != sorted(set(selected)):
        raise TournamentError("freeze entrant allowlist is malformed")
    allowlist = frozen.get("entrant_allowlist")
    if not isinstance(allowlist, Mapping):
        raise TournamentError("freeze hash-pinned entrant allowlist is malformed")
    try:
        normalized_allowlist = _normalize_allowlist(allowlist)
    except TournamentError as error:
        raise TournamentError("freeze hash-pinned entrant allowlist is malformed") from error
    if list(normalized_allowlist) != selected:
        raise TournamentError("selected entrant set differs from the hash-pinned allowlist")
    if frozen.get("entrant_allowlist_hash") != digest(normalized_allowlist):
        raise TournamentError("freeze entrant allowlist hash mismatch")
    source_hashes = frozen.get("entrant_source_hashes")
    if source_hashes != normalized_allowlist:
        raise TournamentError("freeze entrant source hashes differ from the allowlist")
    records = frozen.get("records")
    if not isinstance(records, Mapping):
        raise TournamentError("freeze records are malformed")
    if frozen.get("selected_task_ids") != sorted(str(key) for key in records):
        raise TournamentError("freeze selected task set differs from its records")
    submission = frozen.get("submission")
    if not isinstance(submission, Mapping) or any(key not in submission for key in records):
        raise TournamentError("freeze submission does not cover every selected task")
    for task_id, record in records.items():
        if record.get("content_hash") != digest(
            {key: value for key, value in record.items() if key != "content_hash"}
        ):
            raise TournamentError(f"task record hash mismatch for {task_id}")
        candidates = record.get("candidates")
        if not isinstance(candidates, list):
            raise TournamentError(f"candidate list is malformed for {task_id}")
        for candidate in candidates:
            if not isinstance(candidate, Mapping):
                raise TournamentError("candidate record must be a mapping")
            if candidate.get("candidate_hash") != digest(
                {key: value for key, value in candidate.items() if key != "candidate_hash"}
            ):
                raise TournamentError("candidate hash mismatch")
            if candidate.get("behavior_hash") != digest(candidate.get("test_outputs")):
                raise TournamentError("candidate behavior hash mismatch")
            replay = candidate.get("execution_replay")
            if not isinstance(replay, Mapping):
                raise TournamentError("candidate execution replay is malformed")
            program_hash = digest(candidate.get("program"))
            if replay.get("program_hash") != program_hash:
                raise TournamentError("candidate replay/program hash mismatch")
            if replay.get("status") == "verified":
                if replay.get("content_hash") != digest(
                    {key: value for key, value in replay.items() if key != "content_hash"}
                ):
                    raise TournamentError("candidate replay content hash mismatch")
                train_receipts = replay.get("train")
                test_receipts = replay.get("test")
                if not isinstance(train_receipts, list) or not isinstance(test_receipts, list):
                    raise TournamentError("candidate replay split receipts are malformed")
                for split, bundles, outputs in (
                    ("train", train_receipts, candidate.get("train_outputs")),
                    ("test", test_receipts, candidate.get("test_outputs")),
                ):
                    if not isinstance(outputs, list) or len(bundles) != len(outputs):
                        raise TournamentError(f"candidate {split} replay arity mismatch")
                    for index, (bundle, output) in enumerate(zip(bundles, outputs)):
                        if bundle.get("example_index") != index:
                            raise TournamentError("replay example indices are not contiguous")
                        verify_replay_receipt(bundle, program_hash=program_hash)
                        if bundle.get("output_hash") != digest(output):
                            raise TournamentError("replay receipt output hash mismatch")
            elif replay.get("status") == "not_supplied":
                if frozen.get("program_replay_policy") == "required":
                    raise TournamentError("required executable replay is absent")
            else:
                raise TournamentError("candidate execution replay status is invalid")
        candidate_hashes = {candidate["candidate_hash"] for candidate in candidates}
        behaviors = record.get("behaviors")
        if not isinstance(behaviors, list):
            raise TournamentError("behavior list is malformed")
        referenced_hashes: set[str] = set()
        for behavior in behaviors:
            if not isinstance(behavior, Mapping):
                raise TournamentError("behavior record must be a mapping")
            if behavior.get("content_hash") != digest(
                {key: value for key, value in behavior.items() if key != "content_hash"}
            ):
                raise TournamentError("behavior content hash mismatch")
            if behavior.get("behavior_hash") != digest(behavior.get("test_outputs")):
                raise TournamentError("behavior raster hash mismatch")
            hashes = behavior.get("candidate_hashes")
            if not isinstance(hashes, list) or hashes != sorted(set(hashes)):
                raise TournamentError("behavior candidate hashes are malformed")
            if not set(hashes) <= candidate_hashes:
                raise TournamentError("behavior references an unknown candidate")
            referenced_hashes.update(hashes)
        if referenced_hashes != candidate_hashes:
            raise TournamentError("candidate/behavior partition is incomplete")
        if record.get("retained_candidate_count") != len(candidates):
            raise TournamentError("retained candidate count mismatch")
        if record.get("behavior_count") != len(behaviors):
            raise TournamentError("behavior count mismatch")
    if baseline is not None:
        baseline_copy = _json_copy(dict(baseline), what="baseline submission")
        if frozen.get("baseline_semantic_hash") != digest(baseline_copy):
            raise TournamentError("baseline semantic hash differs from freeze")
        if frozen.get("baseline_attempt_1_hash") != _attempt_1_hash(baseline_copy):
            raise TournamentError("baseline Attempt 1 hash mismatch")
        if rebuild_submission(baseline_copy, frozen) != frozen.get("submission"):
            raise TournamentError("stored submission is not the selected-only overlay")


def _solution_task(
    solutions: Mapping[str, Any], task_id: str, count: int
) -> list[list[list[int]]]:
    if task_id not in solutions:
        raise TournamentError(f"solutions are missing task {task_id}")
    outputs = solutions[task_id]
    if not isinstance(outputs, list) or len(outputs) != count:
        raise TournamentError(f"solution arity mismatch for task {task_id}")
    return [
        validate_grid(value, what=f"solutions[{task_id}][{index}]")
        for index, value in enumerate(outputs)
    ]


def _normalized_solutions(solutions: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for raw_task_id, outputs in sorted(solutions.items(), key=lambda pair: str(pair[0])):
        task_id = str(raw_task_id)
        if task_id in result:
            raise TournamentError("solution task identities collide after string normalization")
        if not isinstance(outputs, list):
            raise TournamentError(f"solutions[{task_id}] must be a list")
        result[task_id] = [
            validate_grid(value, what=f"solutions[{task_id}][{index}]")
            for index, value in enumerate(outputs)
        ]
    return result


def score_tournament(
    frozen: Mapping[str, Any],
    solutions: Mapping[str, Any],
    baseline: Mapping[str, Any],
    *,
    source_hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Score an authenticated freeze after the solution boundary opens."""

    if not isinstance(solutions, Mapping) or not isinstance(baseline, Mapping):
        raise ValueError("solutions and baseline must be mappings")
    verify_freeze(frozen, baseline)
    normalized_solutions = _normalized_solutions(solutions)
    if set(normalized_solutions) != {str(key) for key in baseline}:
        raise TournamentError("solutions and baseline task sets differ")
    overlay = rebuild_submission(baseline, frozen)
    if overlay != frozen.get("submission"):
        raise TournamentError("freeze submission failed deterministic rebuild")
    if _attempt_1_hash(overlay) != _attempt_1_hash(baseline):
        raise TournamentError("Attempt 1 is not byte-identical to baseline")

    gain_records: list[dict[str, Any]] = []
    loss_keys: list[str] = []
    changed_wrong_keys: list[str] = []
    redundant_correct_keys: list[str] = []
    baseline_exact_outputs = 0
    overlay_exact_outputs = 0
    baseline_exact_tasks = 0
    overlay_exact_tasks = 0
    total_outputs = 0
    for task_id, expected in normalized_solutions.items():
        base_items = _validate_submission_task(baseline, task_id, len(expected))
        new_items = _validate_submission_task(overlay, task_id, len(expected))
        base_flags: list[bool] = []
        new_flags: list[bool] = []
        for index, (base, new, target) in enumerate(zip(base_items, new_items, expected)):
            if new["attempt_1"] != base["attempt_1"]:
                raise TournamentError("Attempt 1 changed before scoring")
            prior = base["attempt_1"] == target or base["attempt_2"] == target
            after = new["attempt_1"] == target or new["attempt_2"] == target
            base_flags.append(prior)
            new_flags.append(after)
            key = f"{task_id}:{index}"
            changed = new["attempt_2"] != base["attempt_2"]
            if after and not prior:
                record = {
                    "key": key,
                    "task_id": task_id,
                    "output_index": index,
                    "baseline_attempt_1_hash": digest(base["attempt_1"]),
                    "baseline_attempt_2_hash": digest(base["attempt_2"]),
                    "winner_attempt_2_hash": digest(new["attempt_2"]),
                    "expected_output_hash": digest(target),
                    "exact": True,
                }
                record["receipt_hash"] = digest(record)
                gain_records.append(record)
            elif prior and not after:
                loss_keys.append(key)
            elif changed and after:
                redundant_correct_keys.append(key)
            elif changed:
                changed_wrong_keys.append(key)
        total_outputs += len(expected)
        baseline_exact_outputs += sum(base_flags)
        overlay_exact_outputs += sum(new_flags)
        baseline_exact_tasks += int(all(base_flags))
        overlay_exact_tasks += int(all(new_flags))

    body = {
        "schema": f"{SCHEMA_PREFIX}.tournament_score",
        "schema_version": 1,
        "author": AUTHOR,
        "phase": "separate_retrospective_score",
        "label_access": "solutions_opened_after_verified_freeze",
        "frozen_semantic_hash": frozen["semantic_hash"],
        "frozen_content_hash": frozen["content_hash"],
        "baseline_semantic_hash": digest(baseline),
        "solutions_semantic_hash": digest(normalized_solutions),
        "attempt_1_preserved": True,
        "verified_exact_gain_records": gain_records,
        "verified_exact_gain_keys": [record["key"] for record in gain_records],
        "loss_keys": loss_keys,
        "changed_wrong_keys": changed_wrong_keys,
        "redundant_correct_change_keys": redundant_correct_keys,
        "metrics": {
            "total_outputs": total_outputs,
            "total_tasks": len(solutions),
            "baseline_exact_outputs": baseline_exact_outputs,
            "frozen_exact_outputs": overlay_exact_outputs,
            "baseline_exact_tasks": baseline_exact_tasks,
            "frozen_exact_tasks": overlay_exact_tasks,
            "verified_exact_gains": len(gain_records),
            "losses": len(loss_keys),
        },
        "source_hashes": dict(sorted((source_hashes or {}).items())),
        "claim_boundary": (
            "Retrospective score of a content-addressed pre-solution freeze; "
            "promotion may consume only the sealed exact-gain receipts."
        ),
    }
    return seal_record(body)


def verify_score(
    score: Mapping[str, Any],
    frozen: Mapping[str, Any],
    baseline: Mapping[str, Any],
    solutions: Mapping[str, Any] | None = None,
) -> None:
    verify_seal(score, schema=f"{SCHEMA_PREFIX}.tournament_score")
    verify_freeze(frozen, baseline)
    if score.get("phase") != "separate_retrospective_score":
        raise TournamentError("record is not a separate score")
    if score.get("label_access") != "solutions_opened_after_verified_freeze":
        raise TournamentError("score label boundary is malformed")
    if score.get("frozen_semantic_hash") != frozen.get("semantic_hash"):
        raise TournamentError("score does not authenticate the freeze semantic hash")
    if score.get("frozen_content_hash") != frozen.get("content_hash"):
        raise TournamentError("score does not authenticate the freeze content hash")
    if score.get("baseline_semantic_hash") != digest(baseline):
        raise TournamentError("score does not authenticate the baseline")
    if score.get("attempt_1_preserved") is not True:
        raise TournamentError("score does not certify Attempt 1 preservation")
    records = score.get("verified_exact_gain_records")
    keys = score.get("verified_exact_gain_keys")
    if not isinstance(records, list) or not isinstance(keys, list):
        raise TournamentError("score exact-gain receipts are malformed")
    if keys != [record.get("key") for record in records] or keys != sorted(set(keys)):
        raise TournamentError("score exact-gain keys are malformed")
    overlay = frozen.get("submission")
    if not isinstance(overlay, Mapping):
        raise TournamentError("freeze submission is malformed")
    for record in records:
        if not isinstance(record, Mapping):
            raise TournamentError("exact-gain receipt must be a mapping")
        if record.get("receipt_hash") != digest(
            {key: value for key, value in record.items() if key != "receipt_hash"}
        ):
            raise TournamentError("exact-gain receipt hash mismatch")
        task_id = record.get("task_id")
        index = record.get("output_index")
        if not isinstance(task_id, str) or isinstance(index, bool) or not isinstance(index, int):
            raise TournamentError("exact-gain coordinate is malformed")
        if record.get("key") != f"{task_id}:{index}":
            raise TournamentError("exact-gain key disagrees with its coordinate")
        if task_id not in baseline or task_id not in overlay:
            raise TournamentError("exact-gain coordinate is outside the submission")
        if not 0 <= index < len(baseline[task_id]) or index >= len(overlay[task_id]):
            raise TournamentError("exact-gain output index is outside the submission")
        base = baseline[task_id][index]
        winner = overlay[task_id][index]
        if record.get("baseline_attempt_1_hash") != digest(base["attempt_1"]):
            raise TournamentError("exact-gain baseline Attempt 1 hash mismatch")
        if record.get("baseline_attempt_2_hash") != digest(base["attempt_2"]):
            raise TournamentError("exact-gain baseline Attempt 2 hash mismatch")
        if record.get("winner_attempt_2_hash") != digest(winner["attempt_2"]):
            raise TournamentError("exact-gain winner output hash mismatch")
        expected_hash = record.get("expected_output_hash")
        if record.get("exact") is not True or record.get("winner_attempt_2_hash") != expected_hash:
            raise TournamentError("exact-gain receipt does not prove winner exactness")
        if expected_hash in {
            record.get("baseline_attempt_1_hash"), record.get("baseline_attempt_2_hash")
        }:
            raise TournamentError("exact-gain receipt does not prove a new gain")
    metrics = score.get("metrics")
    if not isinstance(metrics, Mapping) or metrics.get("verified_exact_gains") != len(records):
        raise TournamentError("score exact-gain metric mismatch")
    if solutions is not None:
        normalized_solutions = _normalized_solutions(solutions)
        if score.get("solutions_semantic_hash") != digest(normalized_solutions):
            raise TournamentError("score does not authenticate the solution set")
        recomputed = score_tournament(
            frozen,
            normalized_solutions,
            baseline,
            source_hashes=score.get("source_hashes", {}),
        )
        if recomputed != score:
            raise TournamentError("score does not match independent exactness recomputation")


def promote_verified_gains(
    baseline: Mapping[str, Any],
    frozen: Mapping[str, Any],
    score: Mapping[str, Any],
    *,
    solutions: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Commit only separately scored exact gains to a baseline copy."""

    verify_score(score, frozen, baseline, solutions)
    promoted = _json_copy(dict(baseline), what="baseline submission")
    before_attempt_1 = _attempt_1_hash(promoted)
    frozen_submission = frozen["submission"]
    committed_keys: list[str] = []
    for receipt in score["verified_exact_gain_records"]:
        task_id = receipt["task_id"]
        index = receipt["output_index"]
        promoted[task_id][index]["attempt_2"] = copy.deepcopy(
            frozen_submission[task_id][index]["attempt_2"]
        )
        committed_keys.append(receipt["key"])
    if _attempt_1_hash(promoted) != before_attempt_1:
        raise TournamentError("Attempt 1 changed during score-gated promotion")
    actual_changed = sorted(
        f"{task_id}:{index}"
        for task_id, items in sorted(promoted.items())
        for index, item in enumerate(items)
        if item["attempt_2"] != baseline[task_id][index]["attempt_2"]
    )
    if actual_changed != committed_keys:
        raise TournamentError("promotion changed outputs outside verified exact gains")
    audit_body = {
        "schema": f"{SCHEMA_PREFIX}.score_gated_promotion",
        "schema_version": 1,
        "author": AUTHOR,
        "phase": "post_score_exact_gain_promotion",
        "policy": "preserve_attempt_1_commit_only_separately_verified_exact_gains",
        "baseline_semantic_hash": digest(baseline),
        "freeze_semantic_hash": frozen["semantic_hash"],
        "freeze_content_hash": frozen["content_hash"],
        "score_semantic_hash": score["semantic_hash"],
        "score_content_hash": score["content_hash"],
        "solutions_semantic_hash": digest(_normalized_solutions(solutions)),
        "attempt_1_preserved": True,
        "committed_output_keys": committed_keys,
        "committed_output_count": len(committed_keys),
        "rejected_changed_wrong_count": len(score.get("changed_wrong_keys", [])),
        "rejected_loss_count": len(score.get("loss_keys", [])),
        "promoted_submission_hash": digest(promoted),
        "claim_boundary": (
            "Winner outputs were admitted only from a separate authenticated score. "
            "All non-gain outputs remain byte-equivalent to the baseline."
        ),
    }
    return promoted, seal_record(audit_body)


# Clear singular-name alias for release scripts.
promote_scored_winner = promote_verified_gains


def _limits_from_path(path: Path | None) -> Mapping[str, Any] | None:
    if path is None:
        return None
    value = load_json(path)
    if not isinstance(value, Mapping):
        raise ValueError("limits JSON must contain an object")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("--challenges", type=Path, required=True)
    freeze_parser.add_argument("--baseline", type=Path, required=True)
    freeze_parser.add_argument("--entrants-dir", type=Path, required=True)
    freeze_parser.add_argument(
        "--entrant-allowlist",
        type=Path,
        required=True,
        help="JSON object mapping each permitted entrant name to its SHA-256",
    )
    freeze_parser.add_argument("--limits-json", type=Path)
    freeze_parser.add_argument("--require-replay", action="store_true")
    freeze_parser.add_argument("--run-name")
    freeze_parser.add_argument("--output", type=Path, required=True)

    score_parser = subparsers.add_parser("score")
    score_parser.add_argument("--freeze", type=Path, required=True)
    score_parser.add_argument("--solutions", type=Path, required=True)
    score_parser.add_argument("--baseline", type=Path, required=True)
    score_parser.add_argument("--output", type=Path, required=True)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--freeze", type=Path, required=True)
    promote_parser.add_argument("--score", type=Path, required=True)
    promote_parser.add_argument("--baseline", type=Path, required=True)
    promote_parser.add_argument("--solutions", type=Path, required=True)
    promote_parser.add_argument("--output-submission", type=Path, required=True)
    promote_parser.add_argument("--output-audit", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "freeze":
        allowlist = load_json(args.entrant_allowlist)
        if not isinstance(allowlist, Mapping):
            raise ValueError("entrant allowlist JSON must contain an object")
        frozen = freeze_tournament(
            load_json(args.challenges),
            load_json(args.baseline),
            entrants_dir=args.entrants_dir,
            entrant_allowlist=allowlist,
            limits=_limits_from_path(args.limits_json),
            require_replay=args.require_replay,
            source_hashes={
                "challenges": sha256_file(args.challenges),
                "baseline": sha256_file(args.baseline),
                "entrant_allowlist": sha256_file(args.entrant_allowlist),
            },
            run_name=args.run_name,
        )
        write_json(args.output, frozen)
        return 0
    if args.command == "score":
        scored = score_tournament(
            load_json(args.freeze),
            load_json(args.solutions),
            load_json(args.baseline),
            source_hashes={"solutions": sha256_file(args.solutions)},
        )
        write_json(args.output, scored)
        return 0
    if args.command == "promote":
        submission, audit = promote_verified_gains(
            load_json(args.baseline),
            load_json(args.freeze),
            load_json(args.score),
            solutions=load_json(args.solutions),
        )
        write_json(args.output_submission, submission)
        write_json(args.output_audit, audit)
        return 0
    raise AssertionError("unreachable command")


__all__ = [
    "AUTHOR",
    "CandidateContractError",
    "DEFAULT_LIMITS",
    "Entrant",
    "SCHEMA_PREFIX",
    "TournamentError",
    "canonical_json",
    "digest",
    "freeze_tournament",
    "load_entrants",
    "promote_scored_winner",
    "promote_verified_gains",
    "rebuild_submission",
    "sanitize_task",
    "score_tournament",
    "seal_record",
    "verify_freeze",
    "verify_replay_receipt",
    "verify_score",
]


if __name__ == "__main__":
    raise SystemExit(main())
