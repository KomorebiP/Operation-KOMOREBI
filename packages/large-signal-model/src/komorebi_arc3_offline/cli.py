from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from .agent import AgentConfig, OfflineBayesianOperatorAgent
from .mock_env import OfflineMockFactory
from .offline_guard import assert_offline_guard, install_offline_guard
from .reports import write_run_index
from .runner import official_adapter_smoke, list_local_games, run_game, run_games
from .suite import (
    SUITE_PROFILES,
    audit_suite,
    discover_suite,
    official_suite_smoke,
    order_suite,
    run_suite,
    summarize_suite,
    write_suite_manifest,
    write_suite_plan,
)


def _config(args: argparse.Namespace) -> AgentConfig:
    return AgentConfig(
        maximum_actions=int(args.max_actions),
        maximum_resets=int(args.max_resets),
        initial_probe_budget=int(args.initial_probes),
        recurring_probe_budget=int(args.probes),
        probe_interval=int(args.probe_interval),
        refit_interval=int(args.refit_interval),
        stagnation_limit=int(args.stagnation_limit),
        maximum_candidates=int(args.max_candidates),
        random_seed=int(args.seed),
        maximum_seconds=float(getattr(args, "max_seconds", 0.0)),
    )


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-actions", type=int, default=500)
    parser.add_argument("--max-resets", type=int, default=24)
    parser.add_argument("--initial-probes", type=int, default=8)
    parser.add_argument("--probes", type=int, default=2)
    parser.add_argument("--probe-interval", type=int, default=4)
    parser.add_argument("--refit-interval", type=int, default=3)
    parser.add_argument("--stagnation-limit", type=int, default=18)
    parser.add_argument("--max-candidates", type=int, default=48)
    parser.add_argument("--max-seconds", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="komorebi-arc3-offline",
        description=(
            "Offline-only ARC-AGI-3 runner for Bayesian multiresolution "
            "operator programs."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="verify offline guard and local dependencies")
    check.add_argument("--environments-dir", default="environment_files")

    listing = sub.add_parser("list", help="list local ARC-AGI-3 games")
    listing.add_argument("--environments-dir", default="environment_files")
    listing.add_argument("--json", action="store_true")

    run = sub.add_parser("run", help="run one local game")
    run.add_argument("--game", required=True)
    run.add_argument("--environments-dir", default="environment_files")
    run.add_argument("--output", default="results/run")
    _add_common(run)

    run_all = sub.add_parser("run-all", help="run all local games with one fixed budget")
    run_all.add_argument("--environments-dir", default="environment_files")
    run_all.add_argument("--output", default="results/all")
    run_all.add_argument("--game-prefix", action="append", default=[])
    _add_common(run_all)

    smoke = sub.add_parser("smoke", help="run the bundled deterministic smoke environment")
    smoke.add_argument("--output", default="results/smoke")
    _add_common(smoke)

    official_smoke = sub.add_parser(
        "official-smoke",
        help="load one local official environment and take one public action",
    )
    official_smoke.add_argument("--environments-dir", default="test_environment_files")
    official_smoke.add_argument("--output", default="results/official-adapter-smoke")
    official_smoke.add_argument("--seed", type=int, default=0)

    suite_list = sub.add_parser("suite-list", help="list the bundled/local test suite")
    suite_list.add_argument("--environments-dir", default="environment_files")
    suite_list.add_argument("--json", action="store_true")

    suite_audit = sub.add_parser(
        "suite-audit",
        help="statically audit local game files without executing them",
    )
    suite_audit.add_argument("--environments-dir", default="environment_files")
    suite_audit.add_argument("--output", default="results/suite_static_audit.json")

    suite_smoke = sub.add_parser(
        "suite-smoke",
        help="load, reset, and take one public action in every local game",
    )
    suite_smoke.add_argument("--environments-dir", default="environment_files")
    suite_smoke.add_argument("--output", default="results/suite_adapter_smoke.json")
    suite_smoke.add_argument("--seed", type=int, default=0)

    suite_plan = sub.add_parser(
        "suite-plan",
        help="write a per-game budget plan without running the agent",
    )
    suite_plan.add_argument("--environments-dir", default="environment_files")
    suite_plan.add_argument("--output", default="results/suite")
    suite_plan.add_argument("--profile", choices=sorted(SUITE_PROFILES), default="balanced")
    suite_plan.add_argument("--order", choices=("easy", "hard", "id"), default="easy")
    suite_plan.add_argument("--limit", type=int, default=0)

    suite_run = sub.add_parser(
        "suite-run",
        help="run a checkpointed suite with metadata-derived per-game budgets",
    )
    suite_run.add_argument("--environments-dir", default="environment_files")
    suite_run.add_argument("--output", default="results/suite")
    suite_run.add_argument("--profile", choices=sorted(SUITE_PROFILES), default="balanced")
    suite_run.add_argument("--game", action="append", default=[])
    suite_run.add_argument("--order", choices=("easy", "hard", "id"), default="easy")
    suite_run.add_argument("--limit", type=int, default=0)
    suite_run.add_argument("--seed", type=int, default=0)
    suite_run.add_argument("--no-resume", action="store_true")
    suite_run.add_argument("--rerun-unsolved", action="store_true")
    suite_run.add_argument("--verbose", action="store_true")

    suite_summary = sub.add_parser("suite-summary", help="print the latest suite summary")
    suite_summary.add_argument("--output", default="results/suite")
    return parser


def command_check(args: argparse.Namespace) -> int:
    install_offline_guard(strict=True)
    assert_offline_guard()
    report: dict[str, object] = {
        "offline_guard": True,
        "operation_mode": os.environ.get("OPERATION_MODE"),
        "python": sys.executable,
        "environments_dir": str(Path(args.environments_dir).expanduser().resolve()),
    }
    for module in ("numpy", "scipy", "PIL", "arc_agi", "arcengine"):
        try:
            imported = __import__(module)
            report[module] = getattr(imported, "__version__", "available")
        except Exception as exc:
            report[module] = f"missing: {exc!r}"
    print(json.dumps(report, indent=2))
    return 0 if not any(str(value).startswith("missing") for value in report.values()) else 2


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    install_offline_guard(strict=True)
    assert_offline_guard()

    if args.command == "check":
        return command_check(args)

    if args.command == "list":
        rows = list_local_games(args.environments_dir)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            for row in rows:
                print(f"{row['game_id']:<28} {row['title']}")
        return 0

    if args.command == "run":
        result = run_game(
            args.game,
            environments_dir=args.environments_dir,
            output_dir=args.output,
            seed=args.seed,
            config=_config(args),
            verbose=args.verbose,
        )
        print(json.dumps(asdict(result), indent=2))
        return 0 if result.solved else 1

    if args.command == "run-all":
        rows = list_local_games(args.environments_dir)
        ids = [str(row["game_id"]) for row in rows]
        if args.game_prefix:
            ids = [
                game_id
                for game_id in ids
                if any(game_id.startswith(prefix) for prefix in args.game_prefix)
            ]
        results = run_games(
            ids,
            environments_dir=args.environments_dir,
            output_dir=args.output,
            seed=args.seed,
            config=_config(args),
            verbose=args.verbose,
        )
        print(
            json.dumps(
                {"games": len(results), "solved": sum(row.solved for row in results)},
                indent=2,
            )
        )
        return 0

    if args.command == "smoke":
        agent = OfflineBayesianOperatorAgent(_config(args))
        result = agent.solve(OfflineMockFactory(), args.output)
        write_run_index([result], args.output)
        print(json.dumps(asdict(result), indent=2))
        return 0 if result.solved else 1

    if args.command == "official-smoke":
        report = official_adapter_smoke(
            args.environments_dir,
            output_dir=args.output,
            seed=args.seed,
        )
        print(json.dumps(report, indent=2))
        return 0

    if args.command == "suite-list":
        games = discover_suite(args.environments_dir)
        if args.json:
            print(
                json.dumps(
                    [
                        {
                            **asdict(game),
                            "baseline_total": game.baseline_total,
                            "level_count": game.level_count,
                        }
                        for game in games
                    ],
                    indent=2,
                )
            )
        else:
            for game in games:
                print(
                    f"{game.game_id:<18} levels={game.level_count:<2} "
                    f"baseline_total={game.baseline_total:<5} tags={','.join(game.tags)}"
                )
        return 0

    if args.command == "suite-audit":
        report = audit_suite(args.environments_dir)
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        manifest = write_suite_manifest(
            args.environments_dir,
            output.with_name("suite_manifest.json"),
        )
        print(
            json.dumps(
                {
                    "game_count": report["game_count"],
                    "all_ok": report["all_ok"],
                    "output": str(output),
                    "manifest": str(manifest),
                },
                indent=2,
            )
        )
        return 0 if report["all_ok"] else 2

    if args.command == "suite-smoke":
        report = official_suite_smoke(
            args.environments_dir,
            args.output,
            seed=args.seed,
        )
        print(
            json.dumps(
                {
                    "game_count": report["game_count"],
                    "passed": report["passed"],
                    "failed": report["failed"],
                    "output": str(Path(args.output).resolve()),
                },
                indent=2,
            )
        )
        return 0 if report["failed"] == 0 else 2

    if args.command == "suite-plan":
        games = order_suite(discover_suite(args.environments_dir), args.order)
        if args.limit > 0:
            games = games[: args.limit]
        paths = write_suite_plan(games, args.output, profile=args.profile)
        print(json.dumps({"games": len(games), "profile": args.profile, "plan": {key: str(value) for key, value in paths.items()}}, indent=2))
        return 0

    if args.command == "suite-run":
        results = run_suite(
            args.environments_dir,
            args.output,
            profile=args.profile,
            seed=args.seed,
            game_ids=args.game,
            order=args.order,
            limit=args.limit,
            resume=not args.no_resume,
            rerun_unsolved=args.rerun_unsolved,
            verbose=args.verbose,
        )
        solved = sum(row.solved for row in results)
        print(
            json.dumps(
                {
                    "games": len(results),
                    "solved": solved,
                    "output": str(Path(args.output).resolve()),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "suite-summary":
        print(json.dumps(summarize_suite(args.output), indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
