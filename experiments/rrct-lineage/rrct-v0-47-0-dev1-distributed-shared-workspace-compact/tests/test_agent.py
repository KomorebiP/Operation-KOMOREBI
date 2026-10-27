import unittest

import numpy as np

from rrct import DelayedBindingEnvironment, RRCTAgent


class AgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.episode = DelayedBindingEnvironment(delay=3, noise=0.0, seed=7).sample()

    def test_seeded_agents_are_exactly_replayable(self) -> None:
        first = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=11)
        second = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=11)
        first_trace = [first.step(x).feature_vector() for x in self.episode.observations]
        second_trace = [second.step(x).feature_vector() for x in self.episode.observations]
        np.testing.assert_array_equal(first_trace, second_trace)

    def test_broadcast_ablation_blocks_workspace_intervention(self) -> None:
        agent = RRCTAgent(
            12,
            projector_ranks=(3, 6, 9, 12),
            seed=12,
            ablations=("broadcast",),
        )
        result = agent.step(np.zeros(12), perturb_workspace=np.ones(16) * 0.2)
        np.testing.assert_array_equal(result.workspace, np.zeros(16))

    def test_self_state_is_causally_fed_back(self) -> None:
        baseline = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=13)
        changed = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=13)
        for x in self.episode.observations:
            baseline.step(x)
            changed.step(x)
        changed.self_model.state[0] += 0.4
        zero = np.zeros(12)
        base_result = baseline.step(zero)
        changed_result = changed.step(zero)
        self.assertGreater(
            float(np.linalg.norm(changed_result.workspace - base_result.workspace)),
            1e-6,
        )

    def test_adaptive_resolution_uses_valid_levels(self) -> None:
        agent = RRCTAgent(12, projector_ranks=(3, 6, 9, 12), seed=14)
        levels = [agent.step(x).next_resolution_level for x in self.episode.observations]
        self.assertTrue(all(0 <= level < 4 for level in levels))
        self.assertGreater(len(set(levels)), 1)


if __name__ == "__main__":
    unittest.main()
