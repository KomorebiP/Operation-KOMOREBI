from __future__ import annotations

import numpy as np
import pytest

from komorebi_arc3_offline.exact_atlas import (
    MultiAtlasAnalyzer,
    fourier_band_masks,
    fourier_project,
    polyphase_project,
    wavelet_project,
    wavelet_subband_slices,
)
from komorebi_arc3_offline.lasm_agent import UltimateAgentConfig, UltimateLargeSignalAgent
from komorebi_arc3_offline.lasm_graph import StateTransitionGraph
from komorebi_arc3_offline.lasm_mock_envs import benchmark_factories
from komorebi_arc3_offline.lasm_model import ProjectorResolvedLargeSignalModel
from komorebi_arc3_offline.lasm_packetizer import UltimateLASMPacketizer
from komorebi_arc3_offline.lasm_programs import LASMProgram
from komorebi_arc3_offline.lasm_refinement import PacketTree, best_basis, l1_packet_cost
from komorebi_arc3_offline.lasm_synthetic import generate_program_identification_scenario
from komorebi_arc3_offline.types import ActionCandidate

TOL = 5e-12


def test_every_exact_atlas_reconstructs() -> None:
    rng = np.random.default_rng(10)
    frame = rng.integers(0, 16, size=(64, 64), dtype=np.int16)
    analysis = MultiAtlasAnalyzer().analyze(frame)
    residuals = analysis.reconstruction_residuals()
    assert max(residuals.values()) < TOL


def test_redundant_multi_atlas_tight_frame_reconstructs() -> None:
    frame = np.arange(4096, dtype=np.int16).reshape(64, 64) % 16
    analysis = MultiAtlasAnalyzer().analyze(frame)
    weights = {
        "spatial": 0.7,
        "fourier": 1.2,
        "haar": 0.9,
        "polyphase2": 0.5,
        "polyphase4": 1.1,
    }
    assert np.max(np.abs(analysis.tight_frame_synthesis(weights) - frame)) < TOL


def test_fourier_band_packets_are_complete_and_annihilating() -> None:
    rng = np.random.default_rng(11)
    frame = rng.normal(size=(32, 32))
    maximum = np.sqrt(0.5**2 + 0.5**2)
    masks = fourier_band_masks(frame.shape, np.linspace(0.0, maximum + 1e-12, 6))
    packets = [fourier_project(frame, mask) for mask in masks]
    assert np.max(np.abs(sum(packets) - frame)) < TOL
    spectrum = np.fft.fft2(frame, norm="ortho")
    for left in range(len(masks)):
        for right in range(len(masks)):
            if left != right:
                assert np.max(np.abs(spectrum * masks[left] * masks[right])) == 0.0


def test_polyphase_packets_reconstruct() -> None:
    frame = np.arange(64 * 64, dtype=float).reshape(64, 64)
    packets = [polyphase_project(frame, 4, (row, column)) for row in range(4) for column in range(4)]
    assert np.array_equal(sum(packets), frame)


def test_wavelet_subband_packets_reconstruct() -> None:
    rng = np.random.default_rng(12)
    frame = rng.normal(size=(64, 64))
    labels = tuple(wavelet_subband_slices(frame.shape, 4))
    packets = [wavelet_project(frame, 4, [label]) for label in labels]
    assert np.max(np.abs(sum(packets) - frame)) < TOL


def test_ultimate_packetizer_is_deterministic_and_nested() -> None:
    frame = np.zeros((64, 64), dtype=np.int16)
    frame[10:25, 18:40] = 4
    packetizer = UltimateLASMPacketizer()
    first = packetizer.resolve(frame)
    second = packetizer.resolve(frame)
    assert first.raw.size > first.micro.size > first.meso.size > first.macro.size
    assert first.macro.shape == (48,)
    assert first.meso.shape == (96,)
    assert first.micro.shape == (192,)
    assert np.array_equal(first.raw, second.raw)
    assert first.signature == second.signature
    assert max(first.reconstruction_residuals.values()) < TOL


def test_best_basis_is_mixed_depth_and_exact() -> None:
    t = np.linspace(0, 1, 4096, endpoint=False)
    signal = np.where(t < 0.42, 1.0, -0.8) + 0.12 * np.sin(2 * np.pi * 11 * t)
    tree = PacketTree.analyze(signal, maximum_depth=6)
    selected = best_basis(tree, cost=l1_packet_cost, packet_penalty=1.0)
    assert 1 < len(selected.paths) < 64
    assert len({len(path) for path in selected.paths}) > 1
    assert np.max(np.abs(tree.synthesize(selected.paths) - signal)) < TOL


def test_transition_graph_finds_frontier_and_winning_edges() -> None:
    graph = StateTransitionGraph()
    a1 = ActionCandidate(1, role=("simple", 1))
    a2 = ActionCandidate(2, role=("simple", 2))
    graph.register_state("s0", [a1, a2])
    graph.record("s0", a1, "s1", reward=1, level_delta=0, terminal_win=False, terminal_loss=False)
    graph.record("s0", a2, "loss", reward=-1, level_delta=0, terminal_win=False, terminal_loss=True)
    graph.register_state("s1", [a1, a2])
    graph.record("s1", a2, "win", reward=100, level_delta=1, terminal_win=True, terminal_loss=False)
    assert graph.path_to_frontier("s0") == [a1.identity()]
    assert graph.winning_action("s1") == a2.identity()


def _programs_for_identification() -> tuple[LASMProgram, ...]:
    common = dict(resolution="macro", state_rank=12, atlas_rank=24, interaction_rank=6)
    return (
        LASMProgram("linear-fourier", "linear", atlas="fourier", **common),
        LASMProgram("linear-spatial", "linear", atlas="spatial", **common),
        LASMProgram("linear-color", "linear", atlas="color", **common),
        LASMProgram("linear-portfolio", "linear", atlas="portfolio", **common),
        LASMProgram("quadratic-spatial", "quadratic", atlas="spatial", **common),
        LASMProgram("delay-portfolio", "delay", atlas="portfolio", **common),
        LASMProgram("fractional-fourier", "fractional", atlas="fourier", **common),
        LASMProgram("volterra-portfolio", "volterra", atlas="portfolio", **common),
        LASMProgram("phase2-polyphase", "phase", atlas="polyphase2", phase_modulus=2, **common),
        LASMProgram("gated-color", "gated", atlas="color", **common),
    )


@pytest.mark.parametrize(
    "scenario_name,expected_family,expected_atlas",
    [
        ("linear-fourier", "linear", "fourier"),
        ("quadratic-spatial", "quadratic", "spatial"),
        ("delay-portfolio", "delay", "portfolio"),
        ("fractional-fourier", "fractional", "fourier"),
        ("volterra-portfolio", "volterra", "portfolio"),
        ("phase2-polyphase", "phase", "polyphase2"),
        ("gated-color", "gated", "color"),
    ],
)
def test_bayesian_model_identifies_typed_mechanism(
    scenario_name: str, expected_family: str, expected_atlas: str
) -> None:
    scenario = generate_program_identification_scenario(scenario_name, steps=100, seed=4)
    model = ProjectorResolvedLargeSignalModel(
        programs=_programs_for_identification(),
        minimum_records=12,
        complexity_penalty=0.0012,
        mechanism_penalty=0.35,
        resolution_penalty={"macro": 0.0},
    )
    model.fit(scenario.transitions[:75])
    summary = model.posterior_summary()
    family = max(summary["family_probabilities"], key=summary["family_probabilities"].get)
    atlas = max(summary["atlas_probabilities"], key=summary["atlas_probabilities"].get)
    assert family == expected_family
    assert atlas == expected_atlas


@pytest.mark.parametrize("factory", benchmark_factories(), ids=lambda item: item.game_id)
def test_ultimate_agent_solves_deterministic_interactive_system(factory, tmp_path) -> None:
    agent = UltimateLargeSignalAgent(
        UltimateAgentConfig(
            maximum_actions=90,
            initial_probe_budget=16,
            recurring_probe_budget=8,
            probe_interval=2,
            maximum_resets=20,
            stagnation_limit=18,
        )
    )
    result = agent.solve(factory, tmp_path / factory.game_id)
    assert result.solved
    assert agent.graph.summary()["edges"] > 0
