import unittest

import numpy as np

from rrct.environment import DelayedBindingEnvironment, task_names


class EnvironmentTests(unittest.TestCase):
    def test_cues_are_temporally_separated(self) -> None:
        env = DelayedBindingEnvironment(delay=4, noise=0.0, seed=2)
        episode = env.sample()
        x = episode.observations
        self.assertEqual(x.shape, (7, 12))
        self.assertEqual(int(np.count_nonzero(x[:, 3])), 1)
        self.assertEqual(int(np.count_nonzero(x[:, 4])), 1)
        self.assertEqual(int(np.count_nonzero(x[:, 5])), 1)
        self.assertEqual(x[0, 0], episode.context)
        self.assertEqual(x[1, 1], episode.object_cue)
        self.assertEqual(x[-1, 2], episode.actuator_map)

    def test_all_latent_combinations_are_balanced(self) -> None:
        env = DelayedBindingEnvironment(noise=0.0, seed=3)
        episodes = list(env.enumerate_latents(repeats=2))
        combinations = {
            (e.context, e.object_cue, e.actuator_map) for e in episodes
        }
        self.assertEqual(len(episodes), 16)
        self.assertEqual(len(combinations), 8)
        for task in task_names():
            labels = [e.label(task) for e in episodes]
            self.assertEqual(sum(labels), len(labels) // 2)


if __name__ == "__main__":
    unittest.main()
