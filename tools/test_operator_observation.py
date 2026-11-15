"""Independent values, fitting controls and source bindings for the observation study."""
from fractions import Fraction as Q
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import operator_observation as example


class ObservationStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = example.run_audit()['groups']

    def test_states_and_readings_match_scalar_updates(self):
        row = self.groups['dynamics']
        self.assertEqual(row['states'], ((2, 3, 1), (5, 4, 1), (9, 5, 1), (14, 6, 1), (20, 7, 1)))
        self.assertEqual(row['readings'], (2, 5, 9, 14, 20))
        self.assertEqual(row['times_checked'], [0, 12])
        self.assertEqual(len(row['initial_states']), 3)

    def test_finite_differences_recover_and_expose_the_two_reading_collision(self):
        row = self.groups['exact-recovery']
        self.assertEqual(row['O3'], ((1, 0, 0), (1, 1, 0), (1, 2, 1)))
        self.assertEqual(row['B3'], ((1, 0, 0), (-1, 1, 0), (1, -2, 1)))
        self.assertEqual(row['recovered'], (2, 5 - 2, 9 - 2 * 5 + 2))
        self.assertEqual(row['two-reading-witness'], (0, 0, 1))

    def test_history_update_uses_all_three_values(self):
        row = self.groups['history-update']
        self.assertEqual(row['K'], ((0, 1, 0), (0, 0, 1), (1, -3, 3)))
        self.assertEqual(row['next_reading'], 2 - 3 * 5 + 3 * 9)
        self.assertEqual(row['following_reading'], 5 - 3 * 9 + 3 * 14)

    def test_alternating_noise_attains_the_difference_and_prediction_bounds(self):
        row = self.groups['noisy-recovery']
        self.assertEqual(row['noise_corners_checked'], 8)
        self.assertEqual(row['measured'], (Q(201, 100), Q(499, 100), Q(901, 100)))
        self.assertEqual(row['reconstructed'], (Q(201, 100), Q(149, 50), Q(26, 25)))
        self.assertEqual(row['predicted_next'], Q(1407, 100))
        self.assertEqual(row['gains'], (1, 2, 4))

    def test_fourth_reading_residual_and_exercise_rejection(self):
        row = self.groups['consistency']
        z = row['measured']
        self.assertEqual(z, (Q(201, 100), Q(499, 100), Q(901, 100), Q(1399, 100)))
        self.assertEqual(row['rho'], z[3] - 3 * z[2] + 3 * z[1] - z[0])
        self.assertEqual(row['rho'], Q(-2, 25))
        self.assertEqual(row['bound'], Q(2, 25))
        self.assertEqual(row['exercise_residual'], -1)
        self.assertEqual(row['noise_corners_checked'], 16)

    def test_squared_error_estimate_and_residual_are_independent_scalar_values(self):
        row = self.groups['squared-error-fit']
        self.assertEqual(row['estimate'], (Q(1003, 500), Q(749, 250), 1))
        self.assertEqual(row['residual'], (Q(1, 250), Q(-3, 250), Q(3, 250), Q(-1, 250)))
        self.assertEqual(row['residual_squared'], sum(r * r for r in row['residual']))
        self.assertEqual(row['residual_squared'], Q(1, 3125))
        # Check the objective with scalar trajectory formulas, independently of matrix multiplication.
        z = self.groups['consistency']['measured']
        def objective(state):
            u, v, w = state
            return sum((reading - u - n * v - Q(n * (n - 1), 2) * w) ** 2
                       for n, reading in enumerate(z))
        self.assertEqual(objective(row['estimate']), Q(1, 3125))
        self.assertEqual(objective((2, 3, 1)), Q(1, 2500))
        self.assertGreater(objective((0, 0, 0)), objective(row['estimate']))

    def test_squared_error_fit_and_bounded_residual_feasibility_are_distinct(self):
        row = self.groups['fitting-criteria']
        self.assertEqual(row['coordinate_gains'], (Q(13, 10), 2, 2))
        self.assertEqual(row['squared_error_fit_max_residual'], Q(3, 250))
        self.assertEqual(row['feasible_original_state_max_residual'], Q(1, 100))
        self.assertGreater(row['squared_error_fit_max_residual'], Q(1, 100))

    def test_later_sample_times_change_both_inverse_and_noise_gains(self):
        row = self.groups['sample-times']
        self.assertEqual(row['times'], [0, 2, 4])
        self.assertEqual(row['observation'], ((1, 0, 0), (1, 2, 1), (1, 4, 6)))
        self.assertEqual(row['readings'], (2, 9, 20))
        self.assertEqual(row['coordinate_gains'], (1, Q(3, 2), 1))
        a, b, d = row['readings']
        w = (d - 2 * b + a) / 4
        self.assertEqual((a, (b - a) / 2 - w / 2, w), (2, 3, 1))

    def test_displayed_matrices_and_values_are_bound_to_the_computation(self):
        text = (ROOT / 'docs/operators/OBSERVATION.md').read_text(encoding='utf-8')
        compact = lambda s: re.sub(r'\s+', '', s)
        def matrix(a):
            return r'\begin{pmatrix}' + r'\\'.join('&'.join(map(str, row)) for row in a) + r'\end{pmatrix}'
        for a in (example.T, example.R, example.O3, example.B3, example.K, example.O4, example.C, example.L,
                  self.groups['sample-times']['observation'], self.groups['sample-times']['reconstruction']):
            with self.subTest(matrix=a):
                self.assertIn(compact(matrix(a)), compact(text))
        for value in ('(201/100,149/50,26/25)', '(1003/500,749/250,1)',
                      '(1/250,-3/250,3/250,-1/250)', '$1/3125$', '$1407/100=14+7\\delta$'):
            self.assertIn(compact(value), compact(text))
        self.assertEqual(len(re.findall(r'^## [1-7]\. ', text, re.M)), 7)

    def test_cli_is_exact_json_and_does_not_write_into_the_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run([sys.executable, '-B', str(ROOT / 'examples/operator_observation.py')],
                                 cwd=directory, capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, 0, run.stderr)
            receipt = json.loads(run.stdout)
            self.assertEqual(receipt['result'], 'PASS')
            self.assertEqual(receipt['finite_example_groups'], 8)
            self.assertEqual(receipt['groups']['squared-error-fit']['estimate'], ['1003/500', '749/250', '1'])
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
