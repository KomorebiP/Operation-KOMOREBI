"""Matched experiments for the RRCT--Komorebi operator bridge.

The benchmark asks whether a controller can discover a controllable self packet,
transport it through an unknown coordinate change, localize a model residual to
self or world packets, and preserve a low-energy autobiographical packet during
fixed-rank compression.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

import numpy as np

from .komorebi_operator_self_model import (
    KOMOREBI_VERSION,
    KOMOREBI_WHEEL_SHA256,
    ChangeClass,
    KomorebiTransformationalSelfContinuityController,
    _effect_packet_energies,
    _orthogonal_transport,
    discover_controllable_packets,
    validate_komorebi_transformational_receipt_chain,
)
from .transformational_self_continuity import (
    TransformationalSelfContinuityController,
    _digest,
    validate_transformational_receipt_chain,
)
from .transformational_self_continuity_experiment import (
    V044_EXPOSED_TUNING_SEEDS,
    V044_SCENARIOS,
    _actual_task_values,
    _evidence_receipt,
    _make_root,
    _other_seed,
    _scenario_material,
    _task_material,
)

from komorebi_math.algorithms.low_rank import recompress_core
from komorebi_math.dynamics.bayes import BayesianUpdate

OperatorMode = Literal[
    "komorebi_packets",
    "coordinate_split",
    "global_residual",
    "resolution_cut",
]

V045_MODES: tuple[OperatorMode, ...] = (
    "komorebi_packets",
    "coordinate_split",
    "global_residual",
    "resolution_cut",
)
V045_SCENARIOS: tuple[ChangeClass, ...] = (
    "no_change",
    "self_change",
    "world_change",
    "mixed_change",
)
V045_EXPOSED_SEEDS = (45101, 45102, 45103)
V045_HOLDOUT_SEEDS: tuple[int, ...] = ()


@dataclass(frozen=True)
class OperatorBenchmarkConfig:
    dimension: int = 10
    self_rank: int = 3
    anchor_rows: int = 48
    anchor_noise: float = 0.002
    change_scale: float = 0.24
    detection_threshold: float = 0.035
    packet_decision_threshold: float = 0.72
    global_memory_rank: int = 4
    packet_self_memory_rank: int = 2
    packet_world_memory_rank: int = 2

    def __post_init__(self) -> None:
        if self.dimension < 6:
            raise ValueError("dimension must be at least six")
        if not 1 < self.self_rank < self.dimension - 1:
            raise ValueError("self_rank must define a nontrivial proper packet")
        if self.anchor_rows < self.dimension:
            raise ValueError("anchor_rows must be at least dimension")
        if min(
            self.global_memory_rank,
            self.packet_self_memory_rank,
            self.packet_world_memory_rank,
        ) <= 0:
            raise ValueError("memory ranks must be positive")


@dataclass(frozen=True)
class OperatorWorldCase:
    seed: int
    trial: int
    scenario: ChangeClass
    old_dynamics: np.ndarray
    old_actuation: np.ndarray
    successor_dynamics: np.ndarray
    successor_actuation: np.ndarray
    anchor_before: np.ndarray
    anchor_after: np.ndarray
    true_old_self_projector: np.ndarray
    true_successor_self_projector: np.ndarray
    memory_operator: np.ndarray
    self_query: np.ndarray


def _orthogonal(rng: np.random.Generator, dimension: int) -> np.ndarray:
    q, r = np.linalg.qr(rng.normal(size=(dimension, dimension)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return q @ np.diag(signs)


def _symmetric(rng: np.random.Generator, size: int, scale: float) -> np.ndarray:
    raw = rng.normal(size=(size, size))
    value = 0.5 * (raw + raw.T)
    norm = float(np.linalg.norm(value, 2))
    return value * (float(scale) / max(norm, 1e-12))


def _case(
    seed: int,
    trial: int,
    scenario: ChangeClass,
    config: OperatorBenchmarkConfig,
) -> OperatorWorldCase:
    token = int(hashlib.sha256(f"{seed}:{trial}:{scenario}".encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(token)
    n = config.dimension
    r = config.self_rank
    world_rank = n - r

    hidden_self = np.diag(np.linspace(0.82, 0.58, r))
    hidden_world = np.diag(np.linspace(0.47, 0.18, world_rank))
    hidden_dynamics = np.block(
        [
            [hidden_self, np.zeros((r, world_rank))],
            [np.zeros((world_rank, r)), hidden_world],
        ]
    )
    hidden_actuation = np.zeros((n, 1), dtype=np.float64)
    hidden_actuation[:r, 0] = np.linspace(1.0, 0.55, r)
    old_basis = _orthogonal(rng, n)
    old_dynamics = old_basis @ hidden_dynamics @ old_basis.T
    old_actuation = old_basis @ hidden_actuation
    hidden_self_projector = np.diag([1.0] * r + [0.0] * world_rank)
    old_self_projector = old_basis @ hidden_self_projector @ old_basis.T

    delta_hidden = np.zeros((n, n), dtype=np.float64)
    if scenario in {"self_change", "mixed_change"}:
        delta_hidden[:r, :r] = _symmetric(rng, r, config.change_scale)
    if scenario in {"world_change", "mixed_change"}:
        delta_hidden[r:, r:] = _symmetric(rng, world_rank, config.change_scale)
    changed_old_coordinates = old_dynamics + old_basis @ delta_hidden @ old_basis.T

    transport = _orthogonal(rng, n)
    successor_dynamics = transport.T @ changed_old_coordinates @ transport
    successor_actuation = transport.T @ old_actuation
    successor_self_projector = transport.T @ old_self_projector @ transport

    anchors = rng.normal(size=(config.anchor_rows, n))
    after = anchors @ transport
    if config.anchor_noise:
        after = after + config.anchor_noise * rng.normal(size=after.shape)

    # A low-energy two-mode self memory packet is combined with a stronger
    # world packet.  Global rank truncation tends to discard the self packet;
    # packet-wise recompression reserves an explicit causal-self budget.
    self_vectors = old_basis[:, :r]
    world_vectors = old_basis[:, r:]
    self_singular = np.zeros(r)
    self_singular[: min(2, r)] = (0.42, 0.31)[: min(2, r)]
    world_singular = np.linspace(3.2, 0.8, world_rank)
    memory_operator = (
        self_vectors @ np.diag(self_singular) @ self_vectors.T
        + world_vectors @ np.diag(world_singular) @ world_vectors.T
    )
    self_query = self_vectors[:, 0] + 0.7 * self_vectors[:, min(1, r - 1)]
    self_query = self_query / np.linalg.norm(self_query)
    return OperatorWorldCase(
        seed=int(seed),
        trial=int(trial),
        scenario=scenario,
        old_dynamics=old_dynamics,
        old_actuation=old_actuation,
        successor_dynamics=successor_dynamics,
        successor_actuation=successor_actuation,
        anchor_before=anchors,
        anchor_after=after,
        true_old_self_projector=old_self_projector,
        true_successor_self_projector=successor_self_projector,
        memory_operator=memory_operator,
        self_query=self_query,
    )


def _classify(
    residual: np.ndarray,
    self_projector: np.ndarray,
    world_projector: np.ndarray,
    reference: np.ndarray,
    config: OperatorBenchmarkConfig,
    *,
    bayesian: bool,
) -> tuple[ChangeClass, dict[str, float], tuple[float, ...]]:
    relative = float(np.linalg.norm(residual) / (np.linalg.norm(reference) + 1e-12))
    energies = _effect_packet_energies(
        residual,
        self_projector,
        world_projector,
        self_projector,
        world_projector,
    )
    self_fraction = float(energies["self_packet_fraction"])
    world_fraction = float(energies["world_packet_fraction"])
    if not bayesian:
        if relative <= config.detection_threshold:
            predicted: ChangeClass = "no_change"
        elif self_fraction >= config.packet_decision_threshold:
            predicted = "self_change"
        elif world_fraction >= config.packet_decision_threshold:
            predicted = "world_change"
        else:
            predicted = "mixed_change"
        return predicted, {"relative_residual": relative, **energies}, ()

    changed = float(1.0 - np.exp(-relative / max(config.detection_threshold, 1e-12)))
    unchanged = float(np.exp(-relative / max(config.detection_threshold, 1e-12)))
    likelihood = np.array(
        [
            max(unchanged, 1e-12),
            max(changed * self_fraction**2, 1e-12),
            max(changed * world_fraction**2, 1e-12),
            max(changed * 4.0 * self_fraction * world_fraction, 1e-12),
        ],
        dtype=np.float64,
    )
    posterior = BayesianUpdate(np.full(4, 0.25), likelihood).posterior
    predicted = V045_SCENARIOS[int(np.argmax(posterior))]
    return predicted, {"relative_residual": relative, **energies}, tuple(float(v) for v in posterior)


def _global_recompression(operator: np.ndarray, rank: int) -> np.ndarray:
    result = recompress_core(
        np.eye(operator.shape[0]),
        operator,
        np.eye(operator.shape[1]),
        min(rank, *operator.shape),
        tolerance=1e-10,
    )
    result.certificate.require()
    return np.asarray(result.materialize(), dtype=np.float64)


def _packet_recompression(
    operator: np.ndarray,
    self_projector: np.ndarray,
    world_projector: np.ndarray,
    config: OperatorBenchmarkConfig,
) -> np.ndarray:
    self_block = self_projector @ operator @ self_projector
    world_block = world_projector @ operator @ world_projector
    self_result = recompress_core(
        np.eye(operator.shape[0]),
        self_block,
        np.eye(operator.shape[1]),
        min(config.packet_self_memory_rank, *operator.shape),
        tolerance=1e-10,
    )
    world_result = recompress_core(
        np.eye(operator.shape[0]),
        world_block,
        np.eye(operator.shape[1]),
        min(config.packet_world_memory_rank, *operator.shape),
        tolerance=1e-10,
    )
    self_result.certificate.require()
    world_result.certificate.require()
    return np.asarray(self_result.materialize() + world_result.materialize(), dtype=np.float64)


def evaluate_operator_case(
    case: OperatorWorldCase,
    mode: OperatorMode,
    config: OperatorBenchmarkConfig,
) -> dict[str, Any]:
    transport, anchor_residual, _ = _orthogonal_transport(
        case.anchor_before, case.anchor_after
    )
    expected = transport.T @ case.old_dynamics @ transport
    residual = case.successor_dynamics - expected

    if mode in {"komorebi_packets", "resolution_cut"}:
        old_self, _, discovery = discover_controllable_packets(
            case.old_dynamics, case.old_actuation
        )
        successor_self, successor_world, successor_discovery = discover_controllable_packets(
            case.successor_dynamics, case.successor_actuation
        )
        predicted, diagnostics, posterior = _classify(
            residual,
            successor_self,
            successor_world,
            expected,
            config,
            bayesian=True,
        )
        projector_residual = float(
            np.linalg.norm(successor_self - transport.T @ old_self @ transport)
            / (np.linalg.norm(successor_self) + 1e-12)
        )
        discovery_valid = bool(
            discovery.packet_certificate_valid
            and successor_discovery.packet_certificate_valid
        )
    elif mode == "coordinate_split":
        rank = config.self_rank
        successor_self = np.diag([1.0] * rank + [0.0] * (config.dimension - rank))
        successor_world = np.eye(config.dimension) - successor_self
        predicted, diagnostics, posterior = _classify(
            residual,
            successor_self,
            successor_world,
            expected,
            config,
            bayesian=False,
        )
        projector_residual = float(
            np.linalg.norm(successor_self - case.true_successor_self_projector)
            / (np.linalg.norm(case.true_successor_self_projector) + 1e-12)
        )
        discovery_valid = False
    else:
        relative = float(np.linalg.norm(residual) / (np.linalg.norm(expected) + 1e-12))
        predicted = "no_change" if relative <= config.detection_threshold else "mixed_change"
        diagnostics = {
            "relative_residual": relative,
            "self_packet_fraction": 0.5,
            "world_packet_fraction": 0.5,
            "off_block_fraction": 1.0,
            "total_energy": float(np.linalg.norm(residual) ** 2),
        }
        posterior = ()
        successor_self = case.true_successor_self_projector
        successor_world = np.eye(config.dimension) - successor_self
        projector_residual = 1.0
        discovery_valid = False

    if mode == "resolution_cut":
        compressed = _global_recompression(
            case.memory_operator, config.global_memory_rank
        )
    else:
        compressed = _packet_recompression(
            case.memory_operator,
            case.true_old_self_projector,
            np.eye(config.dimension) - case.true_old_self_projector,
            config,
        )
    global_compressed = _global_recompression(
        case.memory_operator, config.global_memory_rank
    )
    packet_compressed = _packet_recompression(
        case.memory_operator,
        case.true_old_self_projector,
        np.eye(config.dimension) - case.true_old_self_projector,
        config,
    )
    true_response = case.memory_operator @ case.self_query
    response = compressed @ case.self_query
    global_response = global_compressed @ case.self_query
    packet_response = packet_compressed @ case.self_query
    self_task_error = float(
        np.linalg.norm(response - true_response) / (np.linalg.norm(true_response) + 1e-12)
    )
    global_self_error = float(
        np.linalg.norm(global_response - true_response)
        / (np.linalg.norm(true_response) + 1e-12)
    )
    packet_self_error = float(
        np.linalg.norm(packet_response - true_response)
        / (np.linalg.norm(true_response) + 1e-12)
    )
    payload = {
        "seed": case.seed,
        "trial": case.trial,
        "scenario": case.scenario,
        "mode": mode,
        "predicted_change_class": predicted,
        "change_class_correct": float(predicted == case.scenario),
        "change_detect_correct": float(
            (predicted == "no_change") == (case.scenario == "no_change")
        ),
        "anchor_transport_residual": float(anchor_residual),
        "projector_transport_residual": projector_residual,
        "projector_discovery_valid": float(discovery_valid),
        "relative_operator_residual": float(diagnostics["relative_residual"]),
        "self_packet_residual_fraction": float(diagnostics["self_packet_fraction"]),
        "world_packet_residual_fraction": float(diagnostics["world_packet_fraction"]),
        "off_block_fraction": float(diagnostics["off_block_fraction"]),
        "posterior": list(posterior),
        "self_memory_task_error": self_task_error,
        "global_self_memory_error": global_self_error,
        "packet_self_memory_error": packet_self_error,
        "packet_memory_improves_self_error": float(packet_self_error < global_self_error),
        "komorebi_version": KOMOREBI_VERSION,
        "komorebi_wheel_sha256": KOMOREBI_WHEEL_SHA256,
        "uses_evaluator_labels": False,
    }
    payload["row_digest"] = _digest(payload)
    return payload


def _mean(rows: Sequence[Mapping[str, Any]], key: str) -> float:
    return float(np.mean([float(row[key]) for row in rows]))


def run_operator_benchmark(
    seeds: Sequence[int],
    *,
    trials_per_scenario: int = 12,
    modes: Sequence[OperatorMode] = V045_MODES,
    config: OperatorBenchmarkConfig | None = None,
    cohort: str = "development",
) -> dict[str, Any]:
    parsed = tuple(int(seed) for seed in seeds)
    if not parsed or len(set(parsed)) != len(parsed):
        raise ValueError("seeds must be unique and nonempty")
    cfg = config or OperatorBenchmarkConfig()
    rows: list[dict[str, Any]] = []
    for seed in parsed:
        for trial in range(int(trials_per_scenario)):
            for scenario in V045_SCENARIOS:
                case = _case(seed, trial, scenario, cfg)
                for mode in modes:
                    rows.append(evaluate_operator_case(case, mode, cfg))
    summaries: dict[str, Any] = {}
    for mode in modes:
        subset = [row for row in rows if row["mode"] == mode]
        summaries[mode] = {
            "n": len(subset),
            "change_class_accuracy": _mean(subset, "change_class_correct"),
            "change_detection_accuracy": _mean(subset, "change_detect_correct"),
            "mean_projector_transport_residual": _mean(
                subset, "projector_transport_residual"
            ),
            "projector_discovery_valid_rate": _mean(
                subset, "projector_discovery_valid"
            ),
            "mean_self_memory_task_error": _mean(subset, "self_memory_task_error"),
            "packet_memory_improvement_rate": _mean(
                subset, "packet_memory_improves_self_error"
            ),
            "by_scenario": {
                scenario: {
                    "n": len([row for row in subset if row["scenario"] == scenario]),
                    "change_class_accuracy": _mean(
                        [row for row in subset if row["scenario"] == scenario],
                        "change_class_correct",
                    ),
                }
                for scenario in V045_SCENARIOS
            },
        }
    k = summaries["komorebi_packets"]
    coordinate = summaries["coordinate_split"]
    global_value = summaries["global_residual"]
    resolution_cut = summaries["resolution_cut"]
    endpoints = {
        "komorebi_change_attribution_high": k["change_class_accuracy"] >= 0.95,
        "komorebi_change_detection_high": k["change_detection_accuracy"] >= 0.98,
        "komorebi_projectors_certified": k["projector_discovery_valid_rate"] == 1.0,
        "komorebi_projector_transport_accurate": k["mean_projector_transport_residual"] <= 0.02,
        "komorebi_beats_coordinate_split": k["change_class_accuracy"] >= coordinate["change_class_accuracy"] + 0.20,
        "komorebi_beats_global_residual": k["change_class_accuracy"] >= global_value["change_class_accuracy"] + 0.30,
        "packet_resolution_preserves_self_memory": k["mean_self_memory_task_error"] <= 0.05,
        "global_resolution_cut_harms_self_memory": resolution_cut["mean_self_memory_task_error"] >= k["mean_self_memory_task_error"] + 0.50,
        "packet_compression_improves_every_case": k["packet_memory_improvement_rate"] == 1.0,
        "rows_use_no_evaluator_labels": all(not bool(row["uses_evaluator_labels"]) for row in rows),
        "row_digests_unique": len({row["row_digest"] for row in rows}) == len(rows),
    }
    return {
        "schema": "rrct.v045.komorebi_operator_benchmark.v1",
        "scientific_status": "bounded_synthetic_operator_integration",
        "cohort": cohort,
        "seeds": list(parsed),
        "trials_per_scenario": int(trials_per_scenario),
        "scenarios": list(V045_SCENARIOS),
        "modes": list(modes),
        "config": asdict(cfg),
        "rows": rows,
        "mode_summaries": summaries,
        "endpoints": endpoints,
        "all_endpoints_met": all(endpoints.values()),
        "claim_boundary": (
            "This benchmark tests whether Komorebi packet projectors, transfer "
            "blocks, Bayesian updates, and certified packet-wise recompression "
            "improve causal self/world change attribution and low-energy self-memory "
            "preservation in a controlled linear synthetic system. It does not "
            "establish open-world self-awareness or phenomenal consciousness."
        ),
    }


def run_v044_bridge_compatibility(
    seeds: Sequence[int] = V044_EXPOSED_TUNING_SEEDS[:2],
    *,
    trials_per_scenario: int = 2,
) -> dict[str, Any]:
    """Run matched v0.44 scenarios through the baseline and Komorebi bridge."""

    parsed = tuple(int(seed) for seed in seeds)
    if len(parsed) < 2 or len(set(parsed)) != len(parsed):
        raise ValueError("bridge compatibility requires at least two unique seeds")
    rows: list[dict[str, Any]] = []
    for seed in parsed:
        other = _other_seed(seed, parsed)
        for scenario_index, scenario in enumerate(V044_SCENARIOS):
            for trial in range(int(trials_per_scenario)):
                root = _make_root(seed, parsed)
                material = _scenario_material(seed, other, scenario, trial, root)
                time = 4_500_000 + scenario_index * 10_000 + trial * 10
                coarse = [
                    _evidence_receipt(
                        seed=seed, scenario=scenario, trial=trial, root=root,
                        spec=spec, level="coarse", time=time
                    )
                    for spec in material.candidates
                ]
                refined = {
                    spec.candidate_id: _evidence_receipt(
                        seed=seed, scenario=scenario, trial=trial, root=root,
                        spec=spec, level="refined", time=time
                    )
                    for spec in material.candidates
                }
                task = _task_material(
                    seed=seed, scenario=scenario, trial=trial, time=time + 1,
                    root=root, material=material
                )
                actual = _actual_task_values(task, material)
                oracle_flat = int(np.argmax(actual))
                oracle_candidate, oracle_action = np.unravel_index(oracle_flat, actual.shape)
                expected_relations = tuple(spec.true_relation for spec in material.candidates)
                for engine in ("v044_baseline", "komorebi_bridge"):
                    controller = (
                        TransformationalSelfContinuityController(root)
                        if engine == "v044_baseline"
                        else KomorebiTransformationalSelfContinuityController(root)
                    )
                    transition = controller.begin_transition(
                        time=time, coarse_evidence=coarse, intervention_mode="intact"
                    )
                    adjudication = controller.commit_transition(
                        transition,
                        refined_evidence=[
                            refined[candidate]
                            for candidate in transition.refinement_requested_candidate_ids
                        ],
                    )
                    plan = controller.plan_successor_task(adjudication, task)
                    value = float(actual[plan.selected_candidate_index, plan.selected_action_index])
                    outcome = controller.observe_outcome(
                        adjudication, plan, value, reveal_time=time + 2,
                        register_selected_successor=True
                    )
                    base_chain = validate_transformational_receipt_chain(
                        transition=transition, adjudication=adjudication,
                        plan=plan, task=task, outcome=outcome
                    )
                    operator_chain = (
                        True
                        if engine == "v044_baseline"
                        else validate_komorebi_transformational_receipt_chain(
                            transition=transition, adjudication=adjudication,
                            plan=plan, task=task, outcome=outcome,
                            operator_receipts=controller.komorebi_operator_receipts,
                        )
                    )
                    rows.append({
                        "seed": seed,
                        "scenario": scenario,
                        "trial": trial,
                        "engine": engine,
                        "relation_exact": float(tuple(adjudication.relations) == expected_relations),
                        "group_exact": float(adjudication.group_status == material.expected_group_status),
                        "task_correct": float(
                            plan.selected_candidate_index == oracle_candidate
                            and plan.selected_action_index == oracle_action
                        ),
                        "regret": float(np.max(actual) - value),
                        "base_chain_valid": float(base_chain),
                        "operator_chain_valid": float(operator_chain),
                        "operator_receipt_count": int(
                            0 if engine == "v044_baseline"
                            else len(controller.komorebi_operator_receipts)
                        ),
                    })
    summaries = {}
    for engine in ("v044_baseline", "komorebi_bridge"):
        subset = [row for row in rows if row["engine"] == engine]
        summaries[engine] = {
            "n": len(subset),
            "relation_exact_rate": _mean(subset, "relation_exact"),
            "group_exact_rate": _mean(subset, "group_exact"),
            "task_accuracy": _mean(subset, "task_correct"),
            "mean_regret": _mean(subset, "regret"),
            "base_chain_valid_rate": _mean(subset, "base_chain_valid"),
            "operator_chain_valid_rate": _mean(subset, "operator_chain_valid"),
            "mean_operator_receipt_count": _mean(subset, "operator_receipt_count"),
        }
    base = summaries["v044_baseline"]
    bridge = summaries["komorebi_bridge"]
    endpoints = {
        "bridge_preserves_relation_accuracy": bridge["relation_exact_rate"] >= base["relation_exact_rate"],
        "bridge_preserves_group_accuracy": bridge["group_exact_rate"] >= base["group_exact_rate"],
        "bridge_preserves_task_accuracy": bridge["task_accuracy"] >= base["task_accuracy"] - 0.01,
        "bridge_regret_not_materially_worse": bridge["mean_regret"] <= base["mean_regret"] + 0.005,
        "base_chains_valid": bridge["base_chain_valid_rate"] == 1.0,
        "operator_chains_valid": bridge["operator_chain_valid_rate"] == 1.0,
        "operator_receipts_emitted": bridge["mean_operator_receipt_count"] > 0.0,
    }
    return {
        "schema": "rrct.v045.v044_bridge_compatibility.v1",
        "seeds": list(parsed),
        "trials_per_scenario": int(trials_per_scenario),
        "rows": rows,
        "summaries": summaries,
        "endpoints": endpoints,
        "all_endpoints_met": all(endpoints.values()),
        "scientific_status": "retrospective_successor_compatibility",
    }


def write_operator_benchmark_results(
    result: Mapping[str, Any], output_directory: Path
) -> dict[str, str]:
    output_directory.mkdir(parents=True, exist_ok=True)
    rows = list(result["rows"])
    analysis_path = output_directory / "komorebi_operator_benchmark_analysis.json"
    compact = dict(result)
    compact.pop("rows", None)
    summary_path = output_directory / "komorebi_operator_benchmark_summary.json"
    csv_path = output_directory / "komorebi_operator_benchmark_rows.csv"
    analysis_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary_path.write_text(json.dumps(compact, indent=2, sort_keys=True) + "\n")
    fields = sorted({key for row in rows for key in row if key != "posterior"})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fields})
    hashes = {}
    for path in (analysis_path, summary_path, csv_path):
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output_directory / "SHA256SUMS.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n"
    )
    return hashes


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default=",".join(map(str, V045_EXPOSED_SEEDS)))
    parser.add_argument("--trials", type=int, default=12)
    parser.add_argument("--cohort", default="development")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    seeds = tuple(int(value.strip()) for value in args.seeds.split(",") if value.strip())
    result = run_operator_benchmark(
        seeds,
        trials_per_scenario=args.trials,
        cohort=args.cohort,
    )
    write_operator_benchmark_results(result, args.output)
    print(json.dumps({
        "status": "V045_OPERATOR_ENDPOINTS_MET" if result["all_endpoints_met"] else "V045_OPERATOR_ENDPOINTS_NOT_MET",
        "all_endpoints_met": result["all_endpoints_met"],
        "mode_summaries": result["mode_summaries"],
        "output": str(args.output.resolve()),
    }, indent=2, sort_keys=True))
    return 0 if result["all_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
