"""Exact examples and selected source bindings for the Operator guide."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('operator_guide_examples', ROOT/'examples/operator_guide.py')
examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)


class OperatorGuideTests(unittest.TestCase):
    def check_chapter(self, name):
        cases = examples.CHECKS[name]()
        text = (ROOT/('docs/operators/'+name+'.md')).read_text(encoding='utf8')
        entries = re.findall(r'^## [1-9][0-9]*\. ', text, re.M)
        self.assertEqual(len(cases), len(entries))
        compact = lambda value: re.sub(r'\s+', '', value)
        self.assertIn(compact(examples.SOURCE_BINDINGS[name]), compact(text))

    def test_basics_examples(self): self.check_chapter('BASICS')
    def test_algebra_examples(self): self.check_chapter('ALGEBRA')
    def test_packet_examples(self): self.check_chapter('PACKETS')
    def test_transfer_examples(self): self.check_chapter('TRANSFER')
    def test_recovery_examples(self): self.check_chapter('RECOVERY')
    def test_stability_examples(self): self.check_chapter('STABILITY')
    def test_polynomial_examples(self): self.check_chapter('POLYNOMIAL')


class SupplementaryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = examples.supplementary_audits()

    def test_coordinate_metric_preserves_the_original_length(self):
        row = self.rows['coordinate-metric']
        self.assertEqual(row['coordinate'], ((2,), (1,)))
        self.assertEqual(row['weighted_squared_length'], 2)
        self.assertEqual(row['unweighted_squared_length'], 5)

    def test_cutoff_commutator_has_the_top_degree_boundary_term(self):
        row = self.rows['cutoff-commutator']
        self.assertEqual(row['commutator'], ((1, 0, 0), (0, 1, 0), (0, 0, -2)))
        self.assertEqual(row['trace'], 0)

    def test_inconsistent_redundant_coordinates_have_a_synthesis_kernel_residual(self):
        Q = examples.F
        row = self.rows['redundant-coordinates']
        self.assertEqual(row['synthesized'], ((Q(1, 3),), (Q(1, 3),)))
        self.assertEqual(row['corrected'], ((Q(1, 3),), (Q(1, 3),), (Q(2, 3),)))
        self.assertEqual(row['residual'], ((Q(-1, 3),), (Q(-1, 3),), (Q(1, 3),)))

    def test_two_steps_include_the_indirect_path(self):
        row = self.rows['two-step-return']
        # From e1, direct updates give (1,3), then (1+2*3,3+4*3).
        self.assertEqual(row['first_state'], ((1,), (3,)))
        self.assertEqual(row['second_state'], ((7,), (15,)))
        self.assertEqual(row['full'], ((7, 0), (0, 0)))
        self.assertEqual(row['repeated'], ((1, 0), (0, 0)))
        self.assertEqual(row['excursion'], ((6, 0), (0, 0)))

    def test_nearly_parallel_measurements_amplify_opposite_noise(self):
        Q = examples.F
        row = self.rows['noisy-repair']
        self.assertEqual(row['clean'], ((2,), (Q(2003, 1000),)))
        self.assertEqual(row['noisy'], ((Q(1999, 1000),), (Q(2004, 1000),)))
        self.assertEqual(row['recovered'], 5)
        self.assertEqual(row['error'], 2)
        self.assertEqual(row['noise_gain'], 2000)

    def test_two_observations_recover_the_shear_state(self):
        row = self.rows['observation-history']
        self.assertEqual(row['observations'], ((1, 0), (1, 1)))
        self.assertEqual(row['inverse'], ((1, 0), (-1, 1)))

    def test_repeated_error_agrees_with_independent_scalar_powers(self):
        Q = examples.F
        row = self.rows['repeated-error']
        error = Q(1, 2) ** 3 - Q(2, 5) ** 3
        self.assertEqual(error, Q(61, 1000))
        self.assertEqual(row['difference'], ((0, 0), (0, error)))
        self.assertEqual(row['norm'], error)
        self.assertLessEqual(error, row['bound'])

    def test_observation_uses_values_of_the_transported_basis(self):
        row = self.rows['polynomial-observation']
        self.assertEqual(row['transported'], 4 + 3 * (4 * 3) + (4 * 3 * 2))
        self.assertEqual(row['transported'], 64)
        self.assertEqual(row['unchanged'], 116)

    def test_supplementary_results_are_displayed_in_the_guide(self):
        bindings = {
            'BASICS': [r"W'=\operatorname{diag}(1/4,1)", 'squared lengths are $2$'],
            'ALGEBRA': [r'D_2M_2-M_2D_2&=\operatorname{diag}(1,1,-2)'],
            'PACKETS': [r'ASz=(1/3,1/3,2/3)^{\mathsf T}',
                        r'z-ASz=(-1/3,-1/3,1/3)^{\mathsf T}'],
            'TRANSFER': [r'PT^2P&=\begin{pmatrix}7&0\\0&0\end{pmatrix}',
                         r'PT(I-P)TP&=\begin{pmatrix}6&0\\0&0\end{pmatrix}'],
            'RECOVERY': ['values $1999/1000$ and $2004/1000$',
                         r'\mathcal O_2=\begin{pmatrix}1&0\\1&1\end{pmatrix}'],
            'STABILITY': [r'T^3-\widetilde T^3=\operatorname{diag}(0,61/1000)'],
            'POLYNOMIAL': ['$0+4+36+24=64$', 'row $(1,4,16,64)$ instead gives $116$'],
        }
        for chapter, snippets in bindings.items():
            text = (ROOT / 'docs/operators' / (chapter + '.md')).read_text(encoding='utf-8')
            compact = lambda s: re.sub(r'\s+', '', s)
            for snippet in snippets:
                with self.subTest(chapter=chapter, snippet=snippet):
                    self.assertIn(compact(snippet), compact(text))


if __name__ == '__main__':
    unittest.main()
