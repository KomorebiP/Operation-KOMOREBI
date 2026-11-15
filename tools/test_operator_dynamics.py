"""Independent scalar controls for the stable-update study's finite examples."""
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
import operator_dynamics as example


class DynamicsStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = example.run_audit()['groups']

    def test_transient_trajectory_and_squared_lengths(self):
        row = self.groups['trajectory']
        self.assertEqual(row['states'], ((0, 1), (2, Q(1, 2)), (2, Q(1, 4)),
            (Q(3, 2), Q(1, 8)), (1, Q(1, 16)), (Q(5, 8), Q(1, 32))))
        self.assertEqual(row['euclidean_squared'],
            (1, Q(17, 4), Q(65, 16), Q(145, 64), Q(257, 256), Q(401, 1024)))
        self.assertEqual(row['times_checked'], [0, 16])
        self.assertEqual(len(row['initial_states']), 3)

    def test_norm_peak_and_decline(self):
        row = self.groups['transient-gain']
        self.assertEqual(row['norms'][:5], [1, Q(5, 2), Q(9, 4), Q(13, 8), Q(17, 16)])
        self.assertEqual(row['maximum_on_tested_times'], Q(5, 2))
        self.assertEqual(row['attaining_time'], 1)
        self.assertTrue(all(a > b for a, b in zip(row['norms'][1:], row['norms'][2:])))

    def test_transformed_scalar_update_and_budget(self):
        row = self.groups['weighted-norm']
        # y=(u,8v); first transformed output is u/2+(8v)/4.
        u, v = Q(-2), Q(3)
        self.assertEqual(u/2+2*v, u/2+(8*v)/4)
        self.assertEqual(row['B'], ((Q(1, 2), Q(1, 4)), (0, Q(1, 2))))
        self.assertEqual(row['contraction'], Q(3, 4))
        self.assertEqual(row['one_step_converted_bound'], 8*Q(3, 4))

    def test_energy_decreases_while_euclidean_length_grows(self):
        row = self.groups['quadratic-energy']
        self.assertEqual(row['energies'], (Q(356, 27), Q(329, 27), Q(857, 108)))
        self.assertEqual(row['energies'][0]-row['energies'][1], 1)
        self.assertEqual(row['energies'][1]-row['energies'][2], Q(17, 4))
        self.assertEqual(row['completed_square_coefficients'], (Q(4, 3), Q(4, 3), Q(292, 27)))
        # Independent coefficients from (3/4)a=1, (3/4)b=a, (3/4)c=4a+2b+1.
        a = Q(4, 3)
        b = 4*a/3
        c = 4*(4*a+2*b+1)/3
        self.assertEqual(row['W'], ((a, b), (b, c)))
        self.assertNotEqual(row['forced_cross_term']+row['forced_disturbance_energy'], 0)

    def test_omitted_interaction_persists_for_two_steps(self):
        row = self.groups['discarded-transfer']
        self.assertEqual(row['discrepancy_norms'][:6], [0, 2, 2, Q(3, 2), 1, Q(5, 8)])
        self.assertEqual(row['D'], ((Q(1, 2), 0), (0, Q(1, 2))))

    def test_every_short_sign_sequence_is_covered_and_bound_attained(self):
        row = self.groups['persistent-disturbances']
        self.assertEqual(row['sign_sequences_per_length'], [4**n for n in range(5)])
        self.assertEqual(row['sign_sequences_total'], 341)
        self.assertEqual(row['maxima'], [0, Q(1, 100), Q(7, 200), Q(23, 400), Q(59, 800)])
        self.assertEqual(row['attaining_errors'][-1], (Q(59, 800), Q(3, 160)))
        self.assertEqual(row['weighted_norm_uniform_bound'], Q(8, 25))
        # The all-positive disturbance steady state solves two scalar equations.
        v = 2*row['delta']
        u = 4*v+2*row['delta']
        self.assertEqual((u, v), (Q(1, 10), Q(1, 50)))

    def test_residual_does_not_equal_solution_error(self):
        row = self.groups['fixed-point-residual']
        self.assertEqual(row['fixed_point'], (10, 2))
        u, v = row['estimate']
        self.assertEqual((1-u/2+2*v, 1-v/2), (0, Q(1, 100)))
        self.assertEqual(row['residual'], (0, Q(1, 100)))
        self.assertEqual(row['error'], (Q(2, 25), Q(1, 50)))
        self.assertEqual(row['inverse_norm'], 10)

    def test_exercises_and_affine_convergence_use_the_same_error_update(self):
        row = self.groups['exercises-and-affine-error']
        self.assertEqual(row['one_step'], (Q(5, 2), Q(1, 2)))
        self.assertEqual(row['time_two_disturbance_bound'], Q(7, 200))
        self.assertEqual(row['solution_error_bound'], 10*row['residual_budget'])
        self.assertEqual(row['affine_times_checked'], [0, 16])

    def test_displayed_matrices_and_results_match_the_finite_examples(self):
        text = (ROOT / 'docs/operators/DYNAMICS.md').read_text(encoding='utf-8')
        compact = lambda s: re.sub(r'\s+', '', s)
        def matrix(a):
            return r'\begin{pmatrix}'+r'\\'.join('&'.join(map(str, row)) for row in a)+r'\end{pmatrix}'
        for a in (example.A, example.B, example.W, example.RESOLVENT):
            self.assertIn(compact(matrix(a)), compact(text))
        for value in ('356/27', '329/27', '(59/800,3/160)', '(1/10,1/50)',
                      '(248/25,99/50)', '(2/25,1/50)', '$7/200$', '$1/1000$'):
            self.assertIn(compact(value), compact(text))
        self.assertEqual(len(re.findall(r'^## [1-7]\. ', text, re.M)), 7)

    def test_cli_outputs_exact_json_without_writing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run([sys.executable, '-B', str(ROOT / 'examples/operator_dynamics.py')],
                cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads(run.stdout)
            self.assertEqual(data['status'], 'PASS')
            self.assertEqual(data['finite_example_groups'], 8)
            self.assertEqual(data['groups']['persistent-disturbances']['sign_sequences_total'], 341)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
