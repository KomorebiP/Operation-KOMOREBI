from __future__ import annotations

from komorebi_arc3_offline.agent import AgentConfig, OfflineBayesianOperatorAgent
from komorebi_arc3_offline.mock_env import OfflineMockFactory


def test_agent_solves_offline_mock_environment(tmp_path) -> None:
    config = AgentConfig(
        maximum_actions=20,
        initial_probe_budget=8,
        recurring_probe_budget=2,
        probe_interval=2,
        maximum_resets=6,
        stagnation_limit=8,
    )
    result = OfflineBayesianOperatorAgent(config).solve(OfflineMockFactory(), tmp_path)
    assert result.solved
    assert result.levels_completed == 2
    assert result.committed_actions <= 10
    assert (tmp_path / "result.json").exists()
