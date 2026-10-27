from __future__ import annotations

import ast
import csv
import json
import math
import time
import traceback
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Sequence

from .agent import AgentConfig
from .offline_guard import assert_offline_guard, install_offline_guard
from .runner import run_game
from .types import RunResult

_ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "abc",
    "arcengine",
    "collections",
    "copy",
    "enum",
    "math",
    "numpy",
    "random",
    "typing",
    "typing_extensions",
}
_FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "ftplib",
    "http",
    "pathlib",  # official game files do not need filesystem access
    "requests",
    "shutil",
    "socket",
    "subprocess",
    "urllib",
    "webbrowser",
}
_FORBIDDEN_CALL_NAMES = {
    "eval",
    "exec",
    "open",
    "compile",
    "__import__",
    "os.system",
    "subprocess.run",
    "subprocess.Popen",
    "socket.socket",
    "requests.get",
    "requests.post",
    "urllib.request.urlopen",
}


@dataclass(frozen=True)
class SuiteGame:
    game_id: str
    title: str
    tags: tuple[str, ...]
    default_fps: int
    baseline_actions: tuple[int, ...]
    directory: str
    metadata_path: str
    source_path: str

    @property
    def level_count(self) -> int:
        return len(self.baseline_actions)

    @property
    def baseline_total(self) -> int:
        return int(sum(self.baseline_actions))

    @property
    def expected_class_name(self) -> str:
        base = self.game_id.split("-", 1)[0]
        return base[:1].upper() + base[1:]


@dataclass(frozen=True)
class SuiteProfile:
    name: str
    budget_multiplier: float
    minimum_actions: int
    maximum_actions: int
    maximum_seconds: float
    initial_probes: int
    recurring_probes: int
    probe_interval: int
    refit_interval: int
    stagnation_limit: int
    maximum_candidates: int
    maximum_resets: int

    def actions_for(self, game: SuiteGame) -> int:
        derived = int(math.ceil(self.budget_multiplier * max(1, game.baseline_total)))
        return max(self.minimum_actions, min(self.maximum_actions, derived))

    def agent_config(self, game: SuiteGame, *, seed: int) -> AgentConfig:
        return AgentConfig(
            maximum_actions=self.actions_for(game),
            maximum_resets=self.maximum_resets,
            initial_probe_budget=self.initial_probes,
            recurring_probe_budget=self.recurring_probes,
            probe_interval=self.probe_interval,
            refit_interval=self.refit_interval,
            stagnation_limit=self.stagnation_limit,
            maximum_candidates=self.maximum_candidates,
            maximum_records=768,
            random_seed=int(seed),
            strict_replay_check=True,
            maximum_seconds=self.maximum_seconds,
        )


SUITE_PROFILES: dict[str, SuiteProfile] = {
    "quick": SuiteProfile(
        name="quick",
        budget_multiplier=0.65,
        minimum_actions=160,
        maximum_actions=900,
        maximum_seconds=300.0,
        initial_probes=4,
        recurring_probes=1,
        probe_interval=6,
        refit_interval=4,
        stagnation_limit=20,
        maximum_candidates=32,
        maximum_resets=20,
    ),
    "balanced": SuiteProfile(
        name="balanced",
        budget_multiplier=1.35,
        minimum_actions=350,
        maximum_actions=2600,
        maximum_seconds=1200.0,
        initial_probes=8,
        recurring_probes=2,
        probe_interval=4,
        refit_interval=3,
        stagnation_limit=24,
        maximum_candidates=48,
        maximum_resets=32,
    ),
    "thorough": SuiteProfile(
        name="thorough",
        budget_multiplier=2.25,
        minimum_actions=600,
        maximum_actions=6000,
        maximum_seconds=3600.0,
        initial_probes=12,
        recurring_probes=4,
        probe_interval=3,
        refit_interval=2,
        stagnation_limit=32,
        maximum_candidates=64,
        maximum_resets=48,
    ),
}


def discover_suite(environments_dir: str | Path) -> list[SuiteGame]:
    root = Path(environments_dir).expanduser().resolve()
    rows: list[SuiteGame] = []
    for metadata_path in sorted(root.rglob("metadata.json")):
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        game_id = str(payload.get("game_id", "")).strip()
        if not game_id:
            continue
        base = game_id.split("-", 1)[0]
        candidates = [metadata_path.parent / f"{base}.py"]
        class_name = base[:1].upper() + base[1:]
        candidates.extend(
            [metadata_path.parent / f"{class_name}.py", metadata_path.parent / f"{class_name.lower()}.py"]
        )
        source_path = next((path for path in candidates if path.exists()), None)
        if source_path is None:
            python_files = sorted(metadata_path.parent.glob("*.py"))
            source_path = python_files[0] if python_files else metadata_path.parent / f"{base}.py"
        baseline = tuple(int(value) for value in payload.get("baseline_actions", []) or [])
        rows.append(
            SuiteGame(
                game_id=game_id,
                title=str(payload.get("title", "") or ""),
                tags=tuple(str(value) for value in payload.get("tags", []) or []),
                default_fps=int(payload.get("default_fps", 5) or 5),
                baseline_actions=baseline,
                directory=str(metadata_path.parent.relative_to(root)),
                metadata_path=str(metadata_path.relative_to(root)),
                source_path=str(source_path.relative_to(root)),
            )
        )
    return sorted(rows, key=lambda row: row.game_id)


def order_suite(games: Sequence[SuiteGame], order: str = "id") -> list[SuiteGame]:
    if order == "id":
        return sorted(games, key=lambda row: row.game_id)
    if order == "easy":
        return sorted(games, key=lambda row: (row.baseline_total, row.game_id))
    if order == "hard":
        return sorted(games, key=lambda row: (-row.baseline_total, row.game_id))
    raise ValueError("order must be one of: id, easy, hard")


def write_suite_plan(
    games: Sequence[SuiteGame],
    output_dir: str | Path,
    *,
    profile: str = "balanced",
) -> dict[str, Path]:
    if profile not in SUITE_PROFILES:
        raise KeyError(f"unknown suite profile {profile!r}; choose {sorted(SUITE_PROFILES)}")
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    profile_value = SUITE_PROFILES[profile]
    rows = [
        {
            **asdict(game),
            "level_count": game.level_count,
            "baseline_total": game.baseline_total,
            "action_budget": profile_value.actions_for(game),
            "time_budget_seconds": profile_value.maximum_seconds,
        }
        for game in games
    ]
    payload = {
        "offline_only": True,
        "profile": profile,
        "game_count": len(rows),
        "baseline_total_actions": sum(row["baseline_total"] for row in rows),
        "planned_action_budget": sum(row["action_budget"] for row in rows),
        "games": rows,
    }
    json_path = root / "suite_plan.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    csv_path = root / "suite_plan.csv"
    fields = [
        "game_id", "title", "level_count", "baseline_total",
        "action_budget", "time_budget_seconds", "directory",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fields})
    return {"json": json_path, "csv": csv_path}


def _dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _class_bases(tree: ast.AST) -> dict[str, tuple[str, ...]]:
    output: dict[str, tuple[str, ...]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            output[node.name] = tuple(_dotted_name(base) for base in node.bases)
    return output


def audit_suite(environments_dir: str | Path) -> dict[str, Any]:
    root = Path(environments_dir).expanduser().resolve()
    games = discover_suite(root)
    reports: list[dict[str, Any]] = []
    all_ok = True
    for game in games:
        source = root / game.source_path
        errors: list[str] = []
        warnings: list[str] = []
        imports: set[str] = set()
        classes: dict[str, tuple[str, ...]] = {}
        try:
            text = source.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(source))
            compile(tree, str(source), "exec")
            classes = _class_bases(tree)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".", 1)[0])
                elif isinstance(node, ast.ImportFrom):
                    imports.add((node.module or "").split(".", 1)[0])
                elif isinstance(node, ast.Call):
                    name = _dotted_name(node.func)
                    if name in _FORBIDDEN_CALL_NAMES:
                        errors.append(f"forbidden call: {name}")
            forbidden = sorted(imports.intersection(_FORBIDDEN_IMPORT_ROOTS))
            if forbidden:
                errors.append(f"forbidden imports: {forbidden}")
            unexpected = sorted(imports.difference(_ALLOWED_IMPORT_ROOTS))
            if unexpected:
                warnings.append(f"unexpected import roots: {unexpected}")
            if game.expected_class_name not in classes:
                errors.append(
                    f"expected class {game.expected_class_name!r} not found; "
                    f"classes={sorted(classes)}"
                )
            expected_bases = classes.get(game.expected_class_name, ())
            if expected_bases and not any(base.endswith("ARCBaseGame") for base in expected_bases):
                warnings.append(
                    f"main class bases do not explicitly name ARCBaseGame: {expected_bases}"
                )
        except Exception as exc:
            errors.append(f"source parse/compile failed: {exc!r}")
        metadata = root / game.metadata_path
        if not metadata.exists():
            errors.append("metadata file missing")
        if not source.exists():
            errors.append("source file missing")
        ok = not errors
        all_ok &= ok
        reports.append(
            {
                **asdict(game),
                "baseline_total": game.baseline_total,
                "level_count": game.level_count,
                "expected_class_name": game.expected_class_name,
                "source_bytes": source.stat().st_size if source.exists() else 0,
                "imports": sorted(imports),
                "classes": sorted(classes),
                "errors": errors,
                "warnings": warnings,
                "ok": ok,
            }
        )
    return {
        "offline_static_audit": True,
        "environment_root": str(root),
        "game_count": len(games),
        "all_ok": bool(all_ok and len(games) > 0),
        "allowed_import_roots": sorted(_ALLOWED_IMPORT_ROOTS),
        "games": reports,
    }


def write_suite_manifest(environments_dir: str | Path, output: str | Path) -> Path:
    games = discover_suite(environments_dir)
    path = Path(output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "game_count": len(games),
        "games": [
            {
                **asdict(game),
                "level_count": game.level_count,
                "baseline_total": game.baseline_total,
                "quick_budget": SUITE_PROFILES["quick"].actions_for(game),
                "balanced_budget": SUITE_PROFILES["balanced"].actions_for(game),
                "thorough_budget": SUITE_PROFILES["thorough"].actions_for(game),
            }
            for game in games
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _load_existing_result(path: Path) -> RunResult | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["notes"] = tuple(payload.get("notes", []))
        return RunResult(**payload)
    except Exception:
        return None


def _error_result(game: SuiteGame, output_dir: Path, elapsed: float, exc: BaseException) -> RunResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_text = traceback.format_exc()
    (output_dir / "failure_traceback.txt").write_text(trace_text, encoding="utf-8")
    failure_payload = {
        "game_id": game.game_id,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "elapsed_seconds": float(elapsed),
        "traceback_file": str(output_dir / "failure_traceback.txt"),
    }
    (output_dir / "failure.json").write_text(
        json.dumps(failure_payload, indent=2), encoding="utf-8"
    )
    payload = {
        "game_id": game.game_id,
        "solved": False,
        "final_state": "ERROR",
        "levels_completed": 0,
        "win_levels": game.level_count,
        "committed_actions": 0,
        "probe_actions": 0,
        "resets": 0,
        "elapsed_seconds": float(elapsed),
        "model_updates": 0,
        "output_dir": str(output_dir),
        "notes": (f"exception: {exc!r}",),
    }
    result = RunResult(**payload)
    (output_dir / "result.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return result


def run_suite(
    environments_dir: str | Path,
    output_dir: str | Path,
    *,
    profile: str = "balanced",
    seed: int = 0,
    game_ids: Sequence[str] | None = None,
    order: str = "id",
    limit: int = 0,
    resume: bool = True,
    rerun_unsolved: bool = False,
    verbose: bool = False,
) -> list[RunResult]:
    install_offline_guard(strict=True)
    assert_offline_guard()
    if profile not in SUITE_PROFILES:
        raise KeyError(f"unknown suite profile {profile!r}; choose {sorted(SUITE_PROFILES)}")
    selected_ids = set(game_ids or ())
    games = [
        game for game in discover_suite(environments_dir)
        if not selected_ids or game.game_id in selected_ids or game.game_id.split("-", 1)[0] in selected_ids
    ]
    games = order_suite(games, order)
    if limit > 0:
        games = games[:limit]
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    results: list[RunResult] = []
    profile_value = SUITE_PROFILES[profile]
    write_suite_plan(games, root, profile=profile)
    for index, game in enumerate(games, start=1):
        game_output = root / game.game_id
        previous = _load_existing_result(game_output / "result.json")
        if (
            resume
            and previous is not None
            and previous.final_state != "ERROR"
            and (previous.solved or not rerun_unsolved)
        ):
            results.append(previous)
            continue
        started = time.perf_counter()
        try:
            result = run_game(
                game.game_id,
                environments_dir=environments_dir,
                output_dir=game_output,
                seed=seed,
                config=profile_value.agent_config(game, seed=seed),
                verbose=verbose,
            )
        except BaseException as exc:  # batch mode must record and continue
            result = _error_result(game, game_output, time.perf_counter() - started, exc)
        results.append(result)
        write_suite_index(results, games, root, profile=profile)
        print(
            f"[{index:02d}/{len(games):02d}] {game.game_id}: "
            f"state={result.final_state} solved={result.solved} "
            f"levels={result.levels_completed}/{result.win_levels} "
            f"actions={result.committed_actions} time={result.elapsed_seconds:.1f}s",
            flush=True,
        )
    write_suite_index(results, games, root, profile=profile)
    return results


def write_suite_index(
    results: Sequence[RunResult],
    games: Sequence[SuiteGame],
    output_dir: str | Path,
    *,
    profile: str,
) -> dict[str, Path]:
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    metadata = {game.game_id: game for game in games}
    rows: list[dict[str, Any]] = []
    for result in results:
        game = metadata.get(result.game_id)
        baseline_total = 0 if game is None else game.baseline_total
        rows.append(
            {
                **asdict(result),
                "notes": list(result.notes),
                "baseline_total": baseline_total,
                "level_count": 0 if game is None else game.level_count,
                "action_ratio_to_baseline": (
                    None if baseline_total <= 0 else result.committed_actions / baseline_total
                ),
            }
        )
    solved = sum(bool(row["solved"]) for row in rows)
    completed_levels = sum(int(row["levels_completed"]) for row in rows)
    total_levels = sum(int(row["win_levels"]) for row in rows)
    summary = {
        "offline_only": True,
        "profile": profile,
        "games_discovered": len(games),
        "games_recorded": len(rows),
        "solved": solved,
        "solve_rate": solved / max(1, len(rows)),
        "levels_completed": completed_levels,
        "total_levels": total_levels,
        "level_completion_rate": completed_levels / max(1, total_levels),
        "committed_actions": sum(int(row["committed_actions"]) for row in rows),
        "probe_actions": sum(int(row["probe_actions"]) for row in rows),
        "elapsed_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
        "errors": sum(str(row["final_state"]) == "ERROR" for row in rows),
    }
    json_path = root / "suite_index.json"
    json_path.write_text(json.dumps({"summary": summary, "results": rows}, indent=2), encoding="utf-8")
    csv_path = root / "suite_index.csv"
    fieldnames = [
        "game_id", "solved", "final_state", "levels_completed", "win_levels",
        "committed_actions", "probe_actions", "resets", "elapsed_seconds",
        "model_updates", "baseline_total", "level_count", "action_ratio_to_baseline",
        "output_dir",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})
    return {"json": json_path, "csv": csv_path}


def summarize_suite(output_dir: str | Path) -> dict[str, Any]:
    path = Path(output_dir).expanduser().resolve() / "suite_index.json"
    if not path.exists():
        raise FileNotFoundError(f"suite index not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload


def official_suite_smoke(
    environments_dir: str | Path,
    output: str | Path,
    *,
    seed: int = 0,
) -> dict[str, Any]:
    install_offline_guard(strict=True)
    assert_offline_guard()
    root = Path(environments_dir).expanduser().resolve()
    try:
        from arc_agi import Arcade, OperationMode
        from arcengine import GameAction
    except Exception as exc:
        raise RuntimeError("arc-agi 0.9.9 and arcengine 0.9.3 are required") from exc

    arcade = Arcade(
        arc_api_key="",
        operation_mode=OperationMode.OFFLINE,
        environments_dir=str(root),
        recordings_dir=str(Path(output).expanduser().resolve().parent / "recordings"),
    )
    reports: list[dict[str, Any]] = []
    for info in sorted(arcade.get_environments(), key=lambda item: str(item.game_id)):
        game_id = str(info.game_id)
        started = time.perf_counter()
        row: dict[str, Any] = {"game_id": game_id, "ok": False}
        try:
            wrapper = arcade.make(
                game_id,
                seed=int(seed),
                save_recording=False,
                include_frame_data=True,
                render_mode=None,
            )
            if wrapper is None:
                raise RuntimeError("Arcade.make returned None")
            before = wrapper.reset()
            actions = tuple(wrapper.action_space)
            if not actions:
                raise RuntimeError("no public action was exposed")
            action = actions[0]
            data = {"x": 32, "y": 32} if action.is_complex() else {}
            after = wrapper.step(action, data=data, reasoning={"offline": True, "smoke": True})
            if after is None:
                raise RuntimeError("step returned None")
            frames = getattr(after, "frame", [])
            shape = list(getattr(frames[-1], "shape", ())) if frames else []
            row.update(
                {
                    "ok": True,
                    "action_id": int(action.value),
                    "action_data": data,
                    "before_state": str(getattr(getattr(before, "state", None), "value", getattr(before, "state", ""))),
                    "after_state": str(getattr(getattr(after, "state", None), "value", getattr(after, "state", ""))),
                    "levels_completed": int(getattr(after, "levels_completed", 0) or 0),
                    "win_levels": int(getattr(after, "win_levels", 0) or 0),
                    "frame_shape": shape,
                }
            )
        except BaseException as exc:
            row["error"] = repr(exc)
        row["elapsed_seconds"] = time.perf_counter() - started
        reports.append(row)
        print(f"{game_id}: {'ok' if row['ok'] else 'FAILED'}", flush=True)
    report = {
        "offline_only": True,
        "game_count": len(reports),
        "passed": sum(bool(row["ok"]) for row in reports),
        "failed": sum(not bool(row["ok"]) for row in reports),
        "games": reports,
    }
    path = Path(output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
