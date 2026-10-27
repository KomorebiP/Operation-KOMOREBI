import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from rrct.causal_exclusion import _dct_directions, run_causal_exclusion
from rrct.cli import build_parser


class CausalExclusionTests(unittest.TestCase):
    def test_dct_probe_directions_are_orthonormal(self) -> None:
        directions = _dct_directions(12, 4)
        self.assertTrue(np.allclose(directions @ directions.T, np.eye(4), atol=1e-12))

    def test_nonconfirmatory_eight_seed_run_passes_all_gates(self) -> None:
        seeds = (1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367)
        with tempfile.TemporaryDirectory(prefix="rrct_v05_test_") as directory:
            result = run_causal_exclusion(
                Path(directory) / "run",
                seeds=seeds,
                train_episode_count=16,
                horizon=4,
                bootstrap_resamples=64,
                bootstrap_seed=99,
            )
            self.assertEqual(result["status"], "PASS")
            self.assertTrue(all(result["gates"].values()))
            self.assertEqual(result["row_count"], 64)
            saved = json.loads((Path(directory) / "run" / "summary.json").read_text())
            self.assertEqual(saved["status"], "PASS")

    def test_output_directory_must_be_empty(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rrct_v05_nonempty_") as directory:
            output = Path(directory) / "run"
            output.mkdir()
            (output / "existing.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_causal_exclusion(output, seeds=(1301,), train_episode_count=8, bootstrap_resamples=8)

    def test_cli_parses_fixed_parameters(self) -> None:
        parsed = build_parser().parse_args([
            "causal-exclusion", "--seeds", "1,2", "--magnitude", "0.2",
            "--horizon", "7", "--bootstrap-resamples", "40", "--bootstrap-seed", "99",
        ])
        self.assertEqual(parsed.command, "causal-exclusion")
        self.assertEqual(parsed.seeds, [(1, 2)])
        self.assertEqual(parsed.magnitude, 0.2)
        self.assertEqual(parsed.horizon, 7)
        self.assertEqual(parsed.bootstrap_resamples, 40)
        self.assertEqual(parsed.bootstrap_seed, 99)


if __name__ == "__main__":
    unittest.main()
