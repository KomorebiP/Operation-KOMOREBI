"""Independent finite checks for the algebraic-kernel worked examples.

Author: Komorebi P. These tests do not establish identities for all n.
"""
from fractions import Fraction
from math import comb
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sequence_algebraic_kernel_examples import (
    block_generating_polynomials, block_values, example_values,
    expanded_example_generating_values, kernel_coefficients,
    kernel_generating_coefficients, quadratic_evaluate, rational_at_auxiliary,
)


class AlgebraicKernelExamplesTests(unittest.TestCase):
    def test_classical_and_multistep_kernels_by_independent_expansions(self):
        for phi, numerator, denominator in [
            ([1, 2, 1], [1], [1]),
            ([1, 3, 3, 1], [1], [1]),
            ([1, 1, 1], [1], [1]),
            ([1, 0, 1, 1], [1], [1]),
            ([1, 1, 1], [1], [1, -1]),
            ([2, 1, -1], [3, -2], [2, 1]),
        ]:
            with self.subTest(phi=phi, numerator=numerator, denominator=denominator):
                self.assertEqual(
                    kernel_coefficients(phi, numerator, denominator, 24),
                    kernel_generating_coefficients(phi, numerator, denominator, 24))

    def test_arbitrary_block_formula_including_degenerate_parameters(self):
        cases = [
            (1, 1, 3, [1]),
            (1, 0, 0, [2]),
            (2, 0, 1, [1, -1]),
            (2, -1, 1, [1, 1]),
            (2, 1, 1, [1, 1]),
            (2, 2, 1, [1, 1]),
            (2, 4, 1, [1, 1]),
            (2, 0, 2, [1, 1]),
            (3, 1, 1, [1, 1, 1]),
            (3, 2, 1, [1, 0, -1]),
            (3, 1, 2, [1, 2, 3]),
            (4, 0, 1, [1, 0, 0, 0]),
            (5, 0, 2, [1] * 5),
            (4, 3, 0, [2, -1, 0, 5]),
            (3, Fraction(2, 3), Fraction(-1, 2),
             [Fraction(1, 2), 0, Fraction(-3, 4)]),
        ]
        for d, r, q, weights in cases:
            phi = [1] + [0] * (d-1) + [q]
            with self.subTest(d=d, r=r, q=q, weights=weights):
                self.assertEqual(
                    block_values(d, r, q, weights, 20),
                    kernel_generating_coefficients(phi, weights, [1, r], 20))

    def test_polynomial_weight_m_plus_one_ternary_closed_form(self):
        # (1+t^3)*(1+t+t^2-t^3+t^5+4t^6+2t^7).
        p = [1, 1, 1, -1, 0, 1, 4, 2]
        numerator = p + [0] * 3
        for i, value in enumerate(p):
            numerator[i+3] += value
        denominator = [1, 0, 0, -6, 0, 0, 12, 0, 0, -8]
        expected = [(n//3+1)*comb(n, n//3) for n in range(24)]
        self.assertEqual(expected, rational_at_auxiliary(
            [1, 0, 0, 1], numerator, denominator, 24))

    def test_polynomial_weight_m_dyadic_closed_form(self):
        numerator = [0, 0, 2, 3, 2, 2, 0, -1]
        denominator = [1, 0, -3, 0, 3, 0, -1]
        expected = [(n//2)*comb(n, n//2) for n in range(24)]
        self.assertEqual(expected, rational_at_auxiliary(
            [1, 0, 1], numerator, denominator, 24))

    def test_named_worked_values(self):
        examples = example_values(13)
        self.assertEqual(examples[4][:7], [1, 1, 3, 7, 19, 51, 141])
        self.assertEqual(examples[5][8], 238)
        self.assertEqual(examples[6][3], 17)
        self.assertEqual(examples[10][4], 22)
        self.assertEqual(examples[11][4], 246)
        self.assertEqual(examples[16][5], -9)
        self.assertEqual(examples[19][10], 180)
        self.assertEqual(examples[20][4], 10)
        self.assertEqual(examples[21][9], 336)
        self.assertEqual(examples[22][8], 280)
        self.assertEqual(examples[23][12], 1485)

    def test_nine_recurrence_weight_examples_by_independent_expansions(self):
        # Exactly n=0,...,23 for each of the nine displayed specializations.
        direct = example_values(24)
        generating = expanded_example_generating_values(24)
        self.assertEqual(set(generating), set(range(24, 33)))
        for number, coefficients in generating.items():
            with self.subTest(example=number):
                self.assertEqual(len(coefficients), 24)
                self.assertEqual(direct[number], coefficients)

    def test_q_interpolation_at_an_unused_rational_parameter(self):
        count, d, r, q = 24, 3, 1, Fraction(-2, 3)
        polynomials = block_generating_polynomials(d, r, count=count)
        reconstructed = [sum(c*q**m for m, c in enumerate(p))
                         for p in polynomials]
        expected = kernel_generating_coefficients(
            [1, 0, 0, q], [1, 1, 1], [1, r], count)
        self.assertEqual(reconstructed, expected)
        for n, polynomial in enumerate(polynomials):
            self.assertTrue(all(c == 0 for c in polynomial[n//d+1:]))

    def test_exact_characteristic_root_arithmetic(self):
        cases = [
            ([-1, -1, 1], Fraction(1, 2), Fraction(1, 2), 5),
            ([-1, -2, 1], 1, 1, 2),
            ([1, 1, 1], Fraction(-1, 2), Fraction(1, 2), -3),
        ]
        for polynomial, a, b, square in cases:
            with self.subTest(polynomial=polynomial):
                self.assertEqual(quadratic_evaluate(polynomial, a, b, square),
                                 (0, 0))

    def test_expanded_example_lists_and_worked_values(self):
        source = (Path(__file__).resolve().parents[1]
                  / 'research/sequence-closed-forms/ALGEBRAIC_KERNEL_EXAMPLES.md')
        manuscript = source.read_text(encoding='utf-8')
        values = example_values(13)
        for number in range(24, 33):
            with self.subTest(example=number):
                section = manuscript.split(f'## Example {number}.', 1)[1]
                section = section.split('\n## Example ', 1)[0]
                terms = section.split('The first terms are', 1)[1]
                terms = re.search(r'\\begin\{gathered\}(.*?)\\end\{gathered\}',
                                  terms, re.S).group(1)
                displayed = list(map(int, re.findall(r'-?\d+', terms)))
                self.assertEqual(displayed, values[number][:12])
        for number, index, value in [
            (24, 8, 1120), (25, 12, 5940), (26, 8, 490),
            (27, 9, 420), (28, 12, 924), (29, 7, 13),
            (30, 6, 40), (30, 7, 140), (31, 5, 14), (32, 4, 72),
        ]:
            with self.subTest(example=number, index=index):
                self.assertEqual(values[number][index], value)


if __name__ == '__main__':
    unittest.main()
