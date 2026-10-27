from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict
from pathlib import Path
from ._validation import integer

import numpy as np

from .bayes import BayesianRegression
from .exact_atlas import MultiAtlasAnalyzer
from .lasm_agent import UltimateAgentConfig, UltimateLargeSignalAgent
from .lasm_mock_envs import benchmark_factories
from .lasm_model import ProjectorResolvedLargeSignalModel
from .lasm_packetizer import UltimateLASMPacketizer
from .lasm_programs import LASMProgram
from .lasm_refinement import PacketTree, best_basis, l1_packet_cost
from .lasm_synthetic import generate_program_identification_scenarios


def _benchmark_programs() -> tuple[LASMProgram, ...]:
    common = dict(resolution="macro", state_rank=12, atlas_rank=24, interaction_rank=6)
    programs = [
        LASMProgram(f"linear-{atlas}", "linear", atlas=atlas, **common)
        for atlas in ("spatial", "color", "fourier", "haar", "polyphase2", "polyphase4", "portfolio")
    ]
    programs.extend(
        [
            LASMProgram("quadratic-spatial", "quadratic", atlas="spatial", complexity_weight=1.02, **common),
            LASMProgram("delay-portfolio", "delay", atlas="portfolio", complexity_weight=1.01, **common),
            LASMProgram("fractional-fourier", "fractional", atlas="fourier", complexity_weight=1.01, **common),
            LASMProgram("volterra-portfolio", "volterra", atlas="portfolio", complexity_weight=1.01, **common),
            LASMProgram("phase2-polyphase", "phase", atlas="polyphase2", phase_modulus=2, **common),
            LASMProgram("phase4-polyphase", "phase", atlas="polyphase4", phase_modulus=4, **common),
            LASMProgram("gated-color", "gated", atlas="color", complexity_weight=1.03, **common),
        ]
    )
    return tuple(programs)


def _ensemble_prediction(model: ProjectorResolvedLargeSignalModel, transition) -> np.ndarray:
    means = []
    weights = []
    for item in model.fitted:
        row = item.program.design_transition(transition)
        mean, _ = item.regression.predict(row)
        means.append(mean[0])
        weights.append(item.posterior_probability)
    probability = np.asarray(weights, dtype=float)
    probability /= probability.sum()
    return probability @ np.vstack(means)


def run_operator_benchmark(output_dir: Path, *, steps: int = 84, seed: int = 11) -> list[dict[str, object]]:
    steps = integer(steps, "training steps", minimum=16)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scenarios = generate_program_identification_scenarios(steps=(10 * steps + 6) // 7, seed=seed)
    rows: list[dict[str, object]] = []
    for scenario in scenarios:
        train = scenario.transitions[:steps]
        test = scenario.transitions[steps:]
        programs = _benchmark_programs()
        model = ProjectorResolvedLargeSignalModel(
            programs=programs,
            minimum_records=12,
            complexity_penalty=0.0012,
            mechanism_penalty=0.35,
            resolution_penalty={"macro": 0.0},
        )
        started = time.perf_counter()
        model.fit(train)
        fit_seconds = time.perf_counter() - started
        if not model.fitted:
            raise RuntimeError(f"no PR-LASM programs fitted for {scenario.name}")

        baseline_program = next(program for program in programs if program.name == "linear-portfolio")
        baseline_x = np.vstack([baseline_program.design_transition(record) for record in train])
        baseline_y = np.vstack([baseline_program.targets(record) for record in train])
        baseline = BayesianRegression(prior_precision=1.5, shape=2.5, scale=0.05).fit(
            baseline_x, baseline_y
        )

        truth = np.vstack([baseline_program.targets(record) for record in test])
        baseline_prediction = np.vstack(
            [baseline.predict(baseline_program.design_transition(record))[0][0] for record in test]
        )
        lasm_prediction = np.vstack([_ensemble_prediction(model, record) for record in test])
        state_slice = slice(0, 12)
        scalar_slice = slice(12, 17)
        baseline_state_rmse = float(
            np.sqrt(np.mean((truth[:, state_slice] - baseline_prediction[:, state_slice]) ** 2))
        )
        lasm_state_rmse = float(
            np.sqrt(np.mean((truth[:, state_slice] - lasm_prediction[:, state_slice]) ** 2))
        )
        baseline_scalar_rmse = float(
            np.sqrt(np.mean((truth[:, scalar_slice] - baseline_prediction[:, scalar_slice]) ** 2))
        )
        lasm_scalar_rmse = float(
            np.sqrt(np.mean((truth[:, scalar_slice] - lasm_prediction[:, scalar_slice]) ** 2))
        )
        summary = model.posterior_summary()
        best_family = max(summary["family_probabilities"], key=summary["family_probabilities"].get)
        best_atlas = max(summary["atlas_probabilities"], key=summary["atlas_probabilities"].get)
        rows.append(
            {
                "scenario": scenario.name,
                "expected_family": scenario.expected_family,
                "best_family": best_family,
                "family_match": best_family == scenario.expected_family,
                "expected_atlas": scenario.expected_atlas,
                "best_atlas": best_atlas,
                "atlas_match": best_atlas == scenario.expected_atlas,
                "best_program": summary["best_program"],
                "best_probability": summary["best_probability"],
                "baseline_state_rmse": baseline_state_rmse,
                "lasm_state_rmse": lasm_state_rmse,
                "state_rmse_ratio": lasm_state_rmse / max(baseline_state_rmse, 1e-12),
                "baseline_scalar_rmse": baseline_scalar_rmse,
                "lasm_scalar_rmse": lasm_scalar_rmse,
                "fit_seconds": fit_seconds,
                "train_rows": len(train),
                "test_rows": len(test),
            }
        )
    (output_dir / "operator_benchmark.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    with (output_dir / "operator_benchmark.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def run_exactness_benchmark(output_dir: Path, *, seed: int = 17) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    analyzer = MultiAtlasAnalyzer()
    residuals: dict[str, list[float]] = {
        name: [] for name in ("spatial", "fourier", "haar", "polyphase2", "polyphase4", "color", "tight_frame")
    }
    basis_sizes: list[int] = []
    basis_residuals: list[float] = []
    yy, xx = np.mgrid[0:64, 0:64]
    for index in range(24):
        frame_float = (
            4.0
            + 2.5 * np.sin(2 * np.pi * (index % 7 + 1) * xx / 64.0)
            + 1.5 * np.cos(2 * np.pi * (index % 5 + 1) * yy / 64.0)
        )
        frame_float[8 + index % 9 : 25 + index % 9, 15:38] += 5.0
        frame_float[40:47, 4 + (3 * index) % 28 : 18 + (3 * index) % 28] += 3.0
        frame = np.clip(np.rint(frame_float), 0, 15).astype(np.int16)
        analysis = analyzer.analyze(frame)
        for name, residual in analysis.reconstruction_residuals().items():
            residuals[name].append(residual)
        residuals["tight_frame"].append(
            float(np.max(np.abs(analysis.tight_frame_synthesis() - frame)))
        )
        vector = frame.astype(float).ravel()
        tree = PacketTree.analyze(vector, maximum_depth=6)
        selected = best_basis(tree, cost=l1_packet_cost, packet_penalty=1.0)
        rebuilt = tree.synthesize(selected.paths)
        basis_sizes.append(len(selected.paths))
        basis_residuals.append(float(np.max(np.abs(rebuilt - vector))))
    report = {
        "maximum_residuals": {key: max(values) for key, values in residuals.items()},
        "maximum_best_basis_residual": max(basis_residuals),
        "minimum_selected_packets": min(basis_sizes),
        "maximum_selected_packets": max(basis_sizes),
        "mean_selected_packets": float(np.mean(basis_sizes)),
        "frames_tested": 24,
    }
    (output_dir / "exactness_benchmark.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def run_agent_benchmark(output_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for factory in benchmark_factories():
        game_output = output_dir / "agents" / factory.game_id
        agent = UltimateLargeSignalAgent(
            UltimateAgentConfig(
                maximum_actions=90,
                maximum_resets=20,
                initial_probe_budget=16,
                recurring_probe_budget=8,
                probe_interval=2,
                refit_interval=2,
                stagnation_limit=18,
            )
        )
        result = agent.solve(factory, game_output)
        rows.append(
            {
                "game_id": result.game_id,
                "solved": result.solved,
                "committed_actions": result.committed_actions,
                "probe_actions": result.probe_actions,
                "resets": result.resets,
                "elapsed_seconds": result.elapsed_seconds,
                "model_updates": result.model_updates,
                "graph_nodes": agent.graph.summary()["nodes"],
                "graph_edges": agent.graph.summary()["edges"],
            }
        )
    (output_dir / "agent_benchmark.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with (output_dir / "agent_benchmark.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def run_all_benchmarks(output_dir: str | Path) -> dict[str, object]:
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    exactness = run_exactness_benchmark(output)
    operators = run_operator_benchmark(output)
    agents = run_agent_benchmark(output)
    summary = {
        "exactness": exactness,
        "operator_scenarios": len(operators),
        "operator_family_matches": sum(bool(row["family_match"]) for row in operators),
        "operator_atlas_matches": sum(bool(row["atlas_match"]) for row in operators),
        "median_state_rmse_ratio": float(np.median([row["state_rmse_ratio"] for row in operators])),
        "agent_games": len(agents),
        "agent_solved": sum(bool(row["solved"]) for row in agents),
    }
    (output / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run_all_benchmarks(Path("results/pr_lasm_benchmark")), indent=2))
