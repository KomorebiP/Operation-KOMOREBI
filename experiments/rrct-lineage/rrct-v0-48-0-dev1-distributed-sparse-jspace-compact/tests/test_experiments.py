import json
import tempfile
import unittest
from pathlib import Path

from rrct.experiments import intervention_diagnostics, run_experiment


class ExperimentTests(unittest.TestCase):
    def test_workspace_intervention_is_blocked_by_broadcast_ablation(self) -> None:
        full = intervention_diagnostics(seed=41, horizon=5)
        blocked = intervention_diagnostics(
            seed=41, ablations=("broadcast",), horizon=5
        )
        self.assertGreater(full.broadcast, blocked.broadcast)
        self.assertEqual(blocked.broadcast, 0.0)

    def test_smoke_experiment_writes_machine_readable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            summary = run_experiment(
                directory,
                seed=43,
                train_episode_count=16,
                test_episode_count=8,
                make_figures=False,
            )
            self.assertEqual(len(summary["results"]), 8)
            self.assertTrue((Path(directory) / "summary.json").is_file())
            self.assertTrue((Path(directory) / "ablations.csv").is_file())
            loaded = json.loads((Path(directory) / "summary.json").read_text())
            self.assertIn("interpretation_boundary", loaded)
            self.assertIn(loaded["status"], {
                "implemented_architectural_hypothesis_supported",
                "implemented_architectural_hypothesis_not_supported",
            })


if __name__ == "__main__":
    unittest.main()
