from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

from .agent import AgentConfig, OfflineBayesianOperatorAgent
from .offline_guard import assert_offline_guard, install_offline_guard
from .official_adapter import OfficialOfflineFactory
from .reports import write_run_index
from .types import RunResult


def _logger(verbose: bool) -> logging.Logger:
    logger = logging.getLogger("komorebi_arc3_offline")
    logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger


def list_local_games(environments_dir: str | Path) -> list[dict[str, object]]:
    install_offline_guard(strict=True)
    assert_offline_guard()
    root = Path(environments_dir).expanduser().resolve()
    try:
        from arc_agi import Arcade, OperationMode
    except Exception as exc:
        raise RuntimeError("arc-agi 0.9.9 is required to list official local games") from exc
    arcade = Arcade(
        arc_api_key="",
        operation_mode=OperationMode.OFFLINE,
        environments_dir=str(root),
        recordings_dir=str(root.parent / "recordings"),
    )
    rows = []
    for item in arcade.get_environments():
        rows.append(
            {
                "game_id": str(getattr(item, "game_id", "")),
                "title": str(getattr(item, "title", "") or ""),
                "baseline_actions": list(getattr(item, "baseline_actions", []) or []),
                "local_dir": str(getattr(item, "local_dir", "") or ""),
            }
        )
    return sorted(rows, key=lambda row: str(row["game_id"]))



def official_adapter_smoke(
    environments_dir: str | Path,
    *,
    output_dir: str | Path,
    seed: int = 0,
) -> dict[str, object]:
    """Load one local official environment, reset it, and take one public action.

    This validates the pinned ARC toolkit contract without running the full
    solver.  It never downloads an environment and remains behind the strict
    network guard.
    """
    install_offline_guard(strict=True)
    assert_offline_guard()
    games = list_local_games(environments_dir)
    if not games:
        raise RuntimeError("no local ARC-AGI-3 environments were found")
    game_id = str(games[0]["game_id"])
    factory = OfficialOfflineFactory(
        game_id=game_id,
        environments_dir=Path(environments_dir),
        seed=int(seed),
        recordings_dir=Path(output_dir) / "recordings",
        save_recording=True,
        logger=_logger(False),
    )
    environment = factory.create()
    before = environment.reset()
    action_space = tuple(environment.action_space)
    if not action_space:
        raise RuntimeError(f"local game {game_id!r} exposed no public actions")
    action = action_space[0]
    action_id = int(getattr(action, "value", action))
    if bool(getattr(action, "is_complex", lambda: False)()):
        candidate_data = {"x": 32, "y": 32}
    else:
        candidate_data = {}
    from .types import ActionCandidate

    after = environment.step(
        ActionCandidate(
            action_id=action_id,
            data=candidate_data,
            role=("official-contract-smoke", action_id),
            source="official-contract-smoke",
        )
    )
    report = {
        "offline_only": True,
        "game_id": game_id,
        "action_id": action_id,
        "action_data": candidate_data,
        "before_state": before.state.value,
        "after_state": after.state.value,
        "before_levels": before.levels_completed,
        "after_levels": after.levels_completed,
        "frame_shape": list(after.frame.shape),
    }
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "official_adapter_smoke.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report

def run_game(
    game_id: str,
    *,
    environments_dir: str | Path,
    output_dir: str | Path,
    seed: int = 0,
    config: AgentConfig | None = None,
    verbose: bool = False,
) -> RunResult:
    install_offline_guard(strict=True)
    assert_offline_guard()
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    factory = OfficialOfflineFactory(
        game_id=game_id,
        environments_dir=Path(environments_dir),
        seed=int(seed),
        recordings_dir=output / "recordings",
        save_recording=True,
        logger=_logger(verbose),
    )
    agent = OfflineBayesianOperatorAgent(config)
    result = agent.solve(factory, output)
    return result


def run_games(
    game_ids: Iterable[str],
    *,
    environments_dir: str | Path,
    output_dir: str | Path,
    seed: int = 0,
    config: AgentConfig | None = None,
    verbose: bool = False,
) -> list[RunResult]:
    root = Path(output_dir).expanduser().resolve()
    results = []
    for game_id in game_ids:
        game_output = root / game_id.replace("/", "_")
        results.append(
            run_game(
                game_id,
                environments_dir=environments_dir,
                output_dir=game_output,
                seed=seed,
                config=config,
                verbose=verbose,
            )
        )
    write_run_index(results, root)
    return results
