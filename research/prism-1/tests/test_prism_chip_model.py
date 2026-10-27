from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from prism_chip_model import (
    OUTPUT_CONTRACTS,
    REPRESENTATION_FORMS,
    PlanChoice,
    PrismConfig,
    bdlr_apply,
    bdlr_estimate,
    bdlr_sensitivity_tables,
    certificate_commit_allowed,
    dense_apply_estimate,
    gain_decomposition,
    haar_analyze,
    haar_synthesize,
    local_refinement_descriptor_bound,
    materialize_bdlr,
    measured_cuda_baselines,
    output_contract_allows,
    pmr_plan,
    polyphase_analyze,
    polyphase_synthesize,
    precision_allocation,
    route_workload,
    run_self_tests,
)

ROOT = Path(__file__).resolve().parents[1]


def test_configuration() -> None:
    cfg = PrismConfig()
    assert cfg.psms == 64
    assert cfg.execution_groups == 256
    assert cfg.tiles == 256
    assert cfg.total_hbm_gib == 144
    assert abs(cfg.total_hbm_tbps - 11.2) < 1e-12
    assert abs(cfg.total_sram_mib - 192.0) < 1e-12


def test_polyphase_roundtrip() -> None:
    x = np.arange(64, dtype=float)
    assert np.array_equal(polyphase_synthesize(polyphase_analyze(x, 4), length=64), x)


def test_haar_roundtrip() -> None:
    x = np.linspace(-1, 1, 64)
    low, high = haar_analyze(x)
    assert np.max(np.abs(haar_synthesize(low, high) - x)) < 1e-12


def test_bdlr_contract() -> None:
    rng = np.random.default_rng(3)
    blocks = [rng.normal(size=(4, 4)) for _ in range(4)]
    u = rng.normal(size=(16, 3))
    v = rng.normal(size=(16, 3))
    x = rng.normal(size=16)
    assert np.max(np.abs(bdlr_apply(blocks, u, v, x) - materialize_bdlr(blocks, u, v) @ x)) < 1e-11


def test_modeled_bdlr_route_reduction() -> None:
    cfg = PrismConfig()
    dense = dense_apply_estimate(cfg, 8192, 32)
    packet = bdlr_estimate(cfg, 8192, 64, 8, 32)
    assert dense.flops / packet.flops == 102.4
    assert dense.total_time_us > packet.total_time_us


def test_self_tests() -> None:
    result = run_self_tests()
    assert result["tests_passed"] == result["tests_total"] == 18


def test_precision_allocation_uses_full_budget() -> None:
    sensitivity = np.array([0.2, 0.5, 1.0, 2.0])
    cost = np.array([1.0, 2.0, 1.0, 3.0])
    tau = 0.025
    epsilon = precision_allocation(sensitivity, cost, tau)
    assert abs(float(np.dot(sensitivity, epsilon)) - tau) < 1e-14


def test_commit_protocol_blocks_failed_certificate() -> None:
    assert certificate_commit_allowed(True, True, 8e-6, 1e-5)
    assert not certificate_commit_allowed(True, True, 2e-5, 1e-5)
    assert not certificate_commit_allowed(False, True, 0.0, 1e-5)


def test_local_refinement_descriptor_bound() -> None:
    assert local_refinement_descriptor_bound(3, 2, 1, 1, 1, 1) == 7


def test_reference_routing_policy() -> None:
    assert route_workload("bdlr", 12.0, 8, 32) == "prism"
    assert route_workload("dense", 1.0, 1, 1) == "dense_path"
    assert route_workload("transform", 1.1, 1, 2) == "host_or_general_device"


def test_bdlr_sensitivity_tables_are_well_formed() -> None:
    table = bdlr_sensitivity_tables(PrismConfig())
    speedups = np.asarray(table["modeled_speedups"])
    storage = np.asarray(table["storage_reduction"])
    assert speedups.shape == storage.shape == (5, 5)
    assert np.all(speedups > 1.0)
    assert np.all(storage > 1.0)


def test_bandwidth_hierarchy() -> None:
    cfg = PrismConfig()
    assert cfg.package_network_tbps > cfg.total_hbm_tbps
    assert cfg.total_hbm_tbps > cfg.host_bidirectional_gbps / 1000.0


def test_output_contracts_do_not_require_dense_state() -> None:
    assert output_contract_allows("bdlr", "apply")
    assert output_contract_allows("bdlr", "factor_graph")
    assert not output_contract_allows("bdlr", "explicit_array")
    assert output_contract_allows("explicit_dense", "explicit_array")


def test_pmr_planner_uses_output_contract() -> None:
    options = {
        "root": (
            PlanChoice("dense", "explicit_dense", 100.0),
            PlanChoice("transform", "transform_domain", 8.0),
            PlanChoice("split", "packet_graph", 1.0, children=("left", "right")),
        ),
        "left": (
            PlanChoice("block", "block_diagonal", 2.0),
            PlanChoice("dense", "explicit_dense", 20.0),
        ),
        "right": (
            PlanChoice("rank", "low_rank", 2.5, local_error=0.01),
            PlanChoice("dense", "explicit_dense", 18.0),
        ),
    }
    factor_plan = pmr_plan("root", options, 10.0, "factor_graph")
    array_plan = pmr_plan("root", options, 10.0, "explicit_array")
    assert factor_plan.choice == "split"
    assert array_plan.choice == "dense"


def test_measured_cuda_registry() -> None:
    data = measured_cuda_baselines()
    assert data["hardware"] == "NVIDIA GeForce RTX 3070 Ti Laptop GPU"
    assert abs(float(data["bdlr_graph_replay_gain"]) - 0.097280 / 0.079872) < 1e-12
    assert float(data["bdlr_speedup_vs_gpu_dense"]) > 10.0
    assert float(data["compressed_output_gain"]) > 3.0


def test_gain_decomposition_is_typed() -> None:
    data = gain_decomposition()
    assert data["representation_reduction_bdlr"] == 102.4
    assert float(data["measured_packet_gpu_gain_vs_dense_gpu"]) > 1.0
    assert "not multiplied" in str(data["note"])


def test_representation_and_contract_registries() -> None:
    assert len(REPRESENTATION_FORMS) == 9
    assert "explicit_dense" in REPRESENTATION_FORMS
    assert "packet_graph" in REPRESENTATION_FORMS
    assert len(OUTPUT_CONTRACTS) == 5


def test_generated_results() -> None:
    data = json.loads((ROOT / "results" / "prism_chip_results.json").read_text())
    assert data["figure_pairs"] == 43
    assert data["derived"]["packet_streaming_multiprocessors"] == 64
    assert data["derived"]["execution_groups"] == 256
    assert data["self_tests"]["tests_passed"] == 18
    assert data["measured_cuda_baselines"]["bdlr_graph_packet_ms"] == 0.079872
