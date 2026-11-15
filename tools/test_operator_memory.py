"""Independent trajectory, restart and coefficient controls for the memory study."""
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
import operator_memory as example


class MemoryStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = example.run_audit()['groups']

    def test_summary_collision_and_two_step_return(self):
        row = self.groups['closure-and-return']
        self.assertEqual(row['compressed_rule'], Q(1, 2))
        self.assertEqual(row['collision_next_value'], Q(1, 4))
        self.assertEqual(row['two_step_full'], Q(1, 2)**2+Q(1, 4)**2)
        self.assertEqual(row['return_path'], Q(1, 16))
        self.assertEqual(row['two_step_full']-row['two_step_compressed'], row['return_path'])

    def test_table_matches_hand_calculated_scalar_values(self):
        row = self.groups['full-trajectory']
        self.assertEqual(row['states'], ((1, 0), (Q(1, 2), Q(1, 4)),
            (Q(5, 16), Q(1, 4)), (Q(7, 32), Q(13, 64)),
            (Q(41, 256), Q(5, 32)), (Q(61, 512), Q(121, 1024))))
        self.assertEqual(row['repeated_compression'], tuple(Q(1, 2)**n for n in range(6)))
        self.assertEqual(row['times_checked'], [0, 16])
        self.assertEqual(len(row['initial_states']), 3)

    def test_memory_coefficients_and_initial_hidden_input(self):
        row = self.groups['exact-memory']
        self.assertEqual(row['kernel_coefficients'][:5], (Q(1, 16), Q(1, 32), Q(1, 64), Q(1, 128), Q(1, 256)))
        self.assertEqual(row['update_indices_checked'], [0, 15])
        self.assertEqual(row['initial_states'], 3)
        self.assertEqual(row['hidden_initial_example'], Q(1, 4))
        # Direct scalar values with a nonzero hidden initial coordinate.
        hidden = example.trajectory((0, 1))
        self.assertEqual(hidden[:3], ((0, 1), (Q(1, 4), Q(1, 2)), (Q(1, 4), Q(5, 16))))

    def test_checkpoint_carries_the_returning_contribution(self):
        row = self.groups['checkpoint']
        self.assertEqual(row['saved_state'], (Q(7, 32), Q(13, 256)))
        self.assertEqual(row['correct_next'], Q(41, 256))
        self.assertEqual(row['reset_next'], Q(7, 64))
        self.assertEqual(row['restart_error'], Q(13, 256))
        self.assertEqual(row['correct_next'], row['saved_state'][0]/2+row['saved_state'][1])

    def test_all_five_cutoffs_have_the_expected_first_missing_path(self):
        rows = self.groups['finite-memory']['cutoffs']
        self.assertEqual([r['cutoff'] for r in rows], list(range(5)))
        self.assertEqual([r['first_error_time'] for r in rows], [2, 3, 4, 5, 6])
        self.assertEqual([r['first_error'] for r in rows],
            [Q(1, 16), Q(1, 32), Q(1, 64), Q(1, 128), Q(1, 256)])
        self.assertTrue(all(len(r['approximation']) == 17 for r in rows))
        self.assertEqual(rows[1]['approximation'][:5], (1, Q(1, 2), Q(5, 16), Q(3, 16), Q(29, 256)))

    def test_tail_bound_is_propagated_into_a_distinct_uniform_bound(self):
        rows = self.groups['finite-memory']['cutoffs']
        self.assertEqual([r['tail_bound'] for r in rows],
            [Q(1, 8), Q(1, 16), Q(1, 32), Q(1, 64), Q(1, 128)])
        self.assertEqual([r['uniform_error_bound'] for r in rows],
            [Q(1, 4), Q(1, 7), Q(1, 13), Q(1, 25), Q(1, 49)])
        for row in rows:
            self.assertEqual(row['uniform_error_bound']*(1-row['retained_coefficient_sum']), row['tail_bound'])
            self.assertLess(row['maximum_tested_error'], row['uniform_error_bound'])

    def test_formal_coefficients_satisfy_a_separate_second_order_recurrence(self):
        row = self.groups['formal-series']
        coefficients = row['coefficients']
        self.assertEqual(row['coefficient_count'], 17)
        self.assertEqual(row['numerator'], (1, Q(-1, 2)))
        self.assertEqual(row['denominator'], (1, -1, Q(3, 16)))
        self.assertEqual(coefficients[:6], (1, Q(1, 2), Q(5, 16), Q(7, 32), Q(41, 256), Q(61, 512)))
        for previous, current, following in zip(coefficients, coefficients[1:], coefficients[2:]):
            self.assertEqual(following, current-Q(3, 16)*previous)

    def test_invariant_summaries_answer_the_exercises(self):
        row = self.groups['invariant-summaries-and-exercises']
        self.assertEqual(row['sum_decay'], Q(3, 4))
        self.assertEqual(row['difference_decay'], Q(1, 4))
        self.assertEqual(row['checkpoint_restart_error'], Q(13, 256))
        self.assertEqual(row['cutoff_two_bound'], Q(1, 13))
        self.assertEqual(row['cutoff_two_first_error'], Q(1, 64))
        for u, v in ((2, -1), (-3, 5)):
            u, v = Q(u), Q(v)
            next_u, next_v = u/2+v/4, u/4+v/2
            self.assertEqual(next_u+next_v, Q(3, 4)*(u+v))
            self.assertEqual(next_u-next_v, Q(1, 4)*(u-v))

    def test_displayed_values_and_matrix_match_the_examples(self):
        text = (ROOT / 'docs/operators/REDUCTION.md').read_text(encoding='utf-8')
        compact = lambda s: re.sub(r'\s+', '', s)
        self.assertIn(r'\begin{pmatrix}1/2&1/4\\1/4&1/2\end{pmatrix}', compact(text))
        for value in ('41/256', '121/1024', '(7/32,13/256)', '$7/64$', '$1/13$', '$1/64$', '1-t+3t^2/16'):
            self.assertIn(compact(value), compact(text))
        self.assertEqual(len(re.findall(r'^## [1-7]\. ', text, re.M)), 7)

    def test_cli_is_exact_json_and_writes_no_files(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run([sys.executable, '-B', str(ROOT / 'examples/operator_memory.py')],
                cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['finite_example_groups'], 7)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
