from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import numpy as np

from .lasm_agent import UltimateAgentConfig, UltimateLargeSignalAgent
from .lasm_benchmark import run_all_benchmarks
from .lasm_mock_envs import benchmark_factories
from .official_adapter import OfficialOfflineFactory
from .offline_guard import assert_offline_guard, install_offline_guard
from .suite import discover_suite, order_suite


def _agent_config(args: argparse.Namespace) -> UltimateAgentConfig:
    return UltimateAgentConfig(
        maximum_actions=args.max_actions,
        maximum_seconds=args.max_seconds,
        maximum_resets=args.max_resets,
        initial_probe_budget=args.initial_probes,
        recurring_probe_budget=args.recurring_probes,
        probe_interval=args.probe_interval,
        refit_interval=args.refit_interval,
        stagnation_limit=args.stagnation_limit,
    )


def _add_agent_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-actions", type=int, default=1200)
    parser.add_argument("--max-seconds", type=float, default=0.0)
    parser.add_argument("--max-resets", type=int, default=160)
    parser.add_argument("--initial-probes", type=int, default=14)
    parser.add_argument("--recurring-probes", type=int, default=6)
    parser.add_argument("--probe-interval", type=int, default=3)
    parser.add_argument("--refit-interval", type=int, default=3)
    parser.add_argument("--stagnation-limit", type=int, default=24)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="komorebi-pr-lasm",
        description="Projector-Resolved Large Algebraic Signal Model",
    )
    from . import __version__
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("self-check", help="verify the installed core without external runtimes")
    analyze = sub.add_parser("analyze", help="analyze a finite 1-D/2-D .npy or .csv signal without resizing")
    analyze.add_argument("input", type=Path)
    analyze.add_argument("--output", type=Path)
    analyze.add_argument("--modulus", type=int, default=4)
    analyze.add_argument("--maximum-depth", type=int, default=6)

    benchmark = sub.add_parser("benchmark", help="run exactness, operator, and synthetic-agent benchmarks")
    benchmark.add_argument("--output", default="results/pr_lasm_benchmark")

    smoke = sub.add_parser("smoke", help="solve the four bundled deterministic interactive systems")
    smoke.add_argument("--output", default="results/pr_lasm_smoke")
    _add_agent_options(smoke)

    run = sub.add_parser("run", help="run one local ARC-AGI-3 environment with PR-LASM")
    run.add_argument("--game", required=True)
    run.add_argument("--environments-dir", default="environment_files")
    run.add_argument("--output", default="results/pr_lasm_run")
    run.add_argument("--seed", type=int, default=0)
    _add_agent_options(run)

    suite = sub.add_parser("suite-run", help="run a checkpointed local suite with PR-LASM")
    suite.add_argument("--environments-dir", default="environment_files")
    suite.add_argument("--output", default="results/pr_lasm_suite")
    suite.add_argument("--seed", type=int, default=0)
    suite.add_argument("--limit", type=int, default=0)
    suite.add_argument("--order", choices=("easy", "hard", "id"), default="easy")
    _add_agent_options(suite)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    install_offline_guard(strict=True)
    assert_offline_guard()

    if args.command == "self-check":
        from komorebi_pr_lasm.diagnostics import self_check
        summary = self_check()
        print(json.dumps(summary, indent=2, allow_nan=False))
        return 0 if summary["status"] == "PASS" else 1

    if args.command == "analyze":
        from komorebi_pr_lasm.signal import analyze_signal
        from .exact_atlas import MultiAtlasAnalyzer, MultiAtlasConfig
        try:
            if args.input.suffix.lower() == ".npy":
                values = np.load(args.input, allow_pickle=False)
            elif args.input.suffix.lower() == ".csv":
                values = np.loadtxt(args.input, delimiter=",")
            else:
                raise ValueError("input must be a .npy or .csv file")
            if values.ndim == 1:
                analysis = analyze_signal(values, modulus=args.modulus, maximum_depth=args.maximum_depth)
                detail = {"effective_packet_depth": analysis.effective_depth, "modulus": analysis.modulus}
            elif values.ndim == 2:
                analysis = MultiAtlasAnalyzer(MultiAtlasConfig(haar_levels=args.maximum_depth)).analyze(values)
                detail = {"effective_haar_depth": analysis.haar_levels, "color_available": analysis.color is not None,
                          "polyphase_moduli": [2, 4]}
            else:
                raise ValueError("input must be a 1-D signal or a 2-D image")
            summary = {"shape": list(values.shape), "residuals": analysis.reconstruction_residuals(), **detail,
                       "scope": "finite real float64 coordinate reconstruction, not model prediction"}
            text = json.dumps(summary, indent=2, allow_nan=False)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(text + "\n", encoding="utf-8")
            print(text)
            return 0
        except (ValueError, OSError, FloatingPointError) as exc:
            print(json.dumps({"status": "ERROR", "message": str(exc)}))
            return 2

    if args.command == "benchmark":
        summary = run_all_benchmarks(args.output)
        print(json.dumps(summary, indent=2, allow_nan=False))
        exact = summary["exactness"]
        passed = (max(exact["maximum_residuals"].values()) < 5e-10
                  and exact["maximum_best_basis_residual"] < 5e-10
                  and summary["operator_family_matches"] == summary["operator_scenarios"]
                  and summary["operator_atlas_matches"] == summary["operator_scenarios"]
                  and summary["agent_solved"] == summary["agent_games"])
        return 0 if passed else 1

    if args.command == "smoke":
        output = Path(args.output).expanduser().resolve()
        rows = []
        for factory in benchmark_factories():
            result = UltimateLargeSignalAgent(_agent_config(args)).solve(
                factory, output / factory.game_id
            )
            rows.append(asdict(result))
        summary = {"games": len(rows), "solved": sum(bool(row["solved"]) for row in rows), "results": rows}
        output.mkdir(parents=True, exist_ok=True)
        (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return 0 if summary["solved"] == summary["games"] else 1

    if args.command == "run":
        factory = OfficialOfflineFactory(
            args.game,
            Path(args.environments_dir),
            seed=args.seed,
            recordings_dir=Path(args.output) / "recordings",
            save_recording=True,
        )
        result = UltimateLargeSignalAgent(_agent_config(args)).solve(factory, args.output)
        print(json.dumps(asdict(result), indent=2))
        return 0 if result.solved else 1

    if args.command == "suite-run":
        root = Path(args.environments_dir).expanduser().resolve()
        games = order_suite(discover_suite(root), args.order)
        if args.limit > 0:
            games = games[: args.limit]
        output = Path(args.output).expanduser().resolve()
        output.mkdir(parents=True, exist_ok=True)
        rows = []
        for game in games:
            factory = OfficialOfflineFactory(
                game.game_id,
                root,
                seed=args.seed,
                recordings_dir=output / game.game_id / "recordings",
                save_recording=True,
            )
            result = UltimateLargeSignalAgent(_agent_config(args)).solve(
                factory, output / game.game_id
            )
            rows.append(asdict(result))
            (output / "suite_index.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
        summary = {"games": len(rows), "solved": sum(bool(row["solved"]) for row in rows)}
        print(json.dumps(summary, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
