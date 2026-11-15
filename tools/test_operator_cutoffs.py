"""Independent scalar witnesses and coverage controls for finite cutoffs."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
import operator_cutoffs as example


class CutoffStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = example.run_audit()['groups']

    def test_boundary_diagonals_and_zero_trace_include_cutoff_zero(self):
        row = self.groups['finite-commutators']
        self.assertEqual(row['cutoffs'], list(range(7)))
        self.assertEqual(row['diagonals'][0], (0,))
        self.assertEqual(row['diagonals'][3], (1, 1, 1, -3))
        for n, diagonal in enumerate(row['diagonals']):
            self.assertEqual(diagonal, (1,)*n+(-n,))
            self.assertEqual(sum(diagonal), 0)

    def test_cubic_commutator_witness_has_the_missing_return_term(self):
        row = self.groups['boundary-witness']
        self.assertEqual(row['DM_f'], (1, 4, 9, 0))
        self.assertEqual(row['MD_f'], (0, 2, 6, 12))
        self.assertEqual(row['commutator_f'], (1, 2, 3, -12))
        self.assertEqual(row['defect_f'], (0, 0, 0, -16))
        self.assertEqual(row['padded_DM_diagonal'], (1, 2, 3, 4))

    def test_all_words_and_basis_vectors_are_covered(self):
        row = self.groups['safe-padding']
        self.assertEqual(row['word_count'], sum(2**length for length in range(6)))
        self.assertEqual(row['word_cutoff_combinations'], 6*63)
        self.assertEqual(row['basis_controls'], 63*sum(range(1, 7)))
        self.assertEqual(row['example_padding'], {'DM': 1, 'MD': 0, 'DDMM': 2, 'MDMD': 0, 'DDDMM': 2})

    def test_padding_order_is_right_to_left(self):
        self.assertEqual(example.full_polynomial_word('DM', (0, 0, 0, 1)), (0, 0, 0, 4))
        self.assertEqual(example.full_polynomial_word('MD', (0, 0, 0, 1)), (0, 0, 0, 3))
        self.assertEqual(example.cropped(example.full_polynomial_word('DDMM', (0, 0, 0, 1)), 3), (0, 0, 0, 20))
        # Derivatives may annihilate an input before later multiplication.
        self.assertEqual(example.cropped(example.full_polynomial_word('MMD', (1,)), 0), (0,))

    def test_one_extra_degree_is_insufficient_for_two_raises(self):
        row = self.groups['longer-word']
        self.assertEqual(row['full_diagonal'], tuple((k+1)*(k+2) for k in range(4)))
        self.assertEqual(row['unpadded_diagonal'], (2, 6, 0, 0))
        self.assertEqual(row['one_extra_diagonal'], (2, 6, 12, 0))
        self.assertEqual(row['full_f'], (2, 12, 36, 80))
        self.assertEqual(row['unpadded_f'], (2, 12, 0, 0))
        self.assertEqual(row['error_norm'], 20)

    def test_transported_cutoff_and_ordinary_cutoff_are_distinct(self):
        row = self.groups['transported-cutoff']
        self.assertEqual(row['top_packet'], ((0, 0, 0, 0), (0, 0, 0, 2), (0, 0, 0, -3), (0, 0, 0, 1)))
        self.assertEqual(row['raised_cube'], (0, 5, -8, 3))
        self.assertEqual(row['ordinary_cutoff_raised_cube'], (0, -1, 3, -3))
        # Subtracting b4=(0,-6,11,-6,1) from x(x-1)^3 cancels degree four.
        self.assertEqual(row['raised_cube'], (0, -1-(-6), 3-11, -3-(-6)))
        self.assertEqual(row['forward_difference'], ((0, 1, 1, 1), (0, 0, 2, 3), (0, 0, 0, 3), (0, 0, 0, 0)))
        self.assertEqual(row['boundary_on_cube'], (0, -8, 12, -4))

    def test_defect_norm_and_eventual_interior_agreement_are_separate(self):
        row = self.groups['coefficient-norms']
        self.assertEqual(row['defect_norms'], list(range(1, 8)))
        self.assertEqual(row['transported_norm'], 12)
        self.assertEqual(row['fixed_cubic_interior_cutoffs'], [4, 5, 6])

    def test_field_controls_include_all_basis_products_and_a_negative_case(self):
        row = self.groups['finite-field-controls']
        self.assertEqual(row['primes'], (2, 3, 5, 7))
        self.assertEqual(row['quotient_basis_product_pairs'], sum(p*p for p in row['primes']))
        self.assertEqual(row['F3_cutoff3_commutator_diagonal'], (1, 1, 1, 0))
        self.assertEqual(row['rational_quotient_representative_derivatives'], (0, 4))
        # In F3[z]/(z^3), D(z^2*z)=0 and the two product-rule contributions cancel.
        a, b = (0, 0, 1), (0, 1, 0)
        self.assertEqual(example.quotient_derivative(example.quotient_product(a, b, 3), 3), (0, 0, 0))

    def test_displayed_matrices_and_values_are_bound_to_the_examples(self):
        text = (ROOT/'docs/operators/CUTOFFS.md').read_text(encoding='utf-8')
        compact = lambda s: re.sub(r'\s+', '', s)
        def matrix(a):
            return r'\begin{pmatrix}'+r'\\'.join('&'.join(map(str, row)) for row in a)+r'\end{pmatrix}'
        row = self.groups['boundary-witness']
        for a in (row['D3'], row['M3'], example.C, self.groups['transported-cutoff']['top_packet']):
            self.assertIn(compact(matrix(a)), compact(text))
        for value in ('(2,12,36,80)', '(2,12,0,0)', '-16z^3', '3x^3-8x^2+5x', '-3x^3+3x^2-x', '$12$'):
            self.assertIn(compact(value), compact(text))
        # A leading [commutator] after gathered can be consumed as its placement option.
        self.assertNotRegex(text, r'\\begin\{gathered\}\s*\[')
        self.assertIn(r'\left[\widehatD,\widehatM\right]', compact(text))
        self.assertEqual(len(re.findall(r'^## [1-7]\. ', text, re.M)), 7)

    def test_cli_is_exact_json_and_writes_no_files(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run([sys.executable, '-B', str(ROOT/'examples/operator_cutoffs.py')],
                cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['finite_example_groups'], 7)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
