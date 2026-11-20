"""Finite exact checks for the uniform central binomial recurrence.

Author: Komorebi P.
These tests corroborate finite ranges. The source derivation supplies the
universal proof; computation alone does not establish the all-index identity.
"""
import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sequence_central_binomial import (
    COUNT, FAMILY_ID, SOURCE, central_binomial_sum,
    central_binomial_coefficients, central_binomial_polynomial,
    central_binomial_catalogue, central_binomial_families,
)


def polynomial_product(left, right):
    result = [0] * (len(left)+len(right)-1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            result[i+j] += x*y
    return result


def polynomial_sum(*polynomials):
    result = [0] * max(map(len, polynomials))
    for polynomial in polynomials:
        for i, coefficient in enumerate(polynomial):
            result[i] += coefficient
    return result


def definition_polynomials(last):
    """Build binomial rows by Pascal addition, independently of math.comb."""
    row = [1]
    result = []
    for n in range(last+1):
        result.append([(-1)**j * row[(n-j)//2] for j in range(n+1)])
        row = [1] + [row[j-1]+row[j] for j in range(1, len(row))] + [1]
    return result


def gaussian_add(left, right):
    return left[0]+right[0], left[1]+right[1]


def gaussian_multiply(left, right):
    return (left[0]*right[0]-left[1]*right[1],
            left[0]*right[1]+left[1]*right[0])


def gaussian_scale(value, factor):
    return value[0]*factor, value[1]*factor


def gaussian_polynomial(coefficients, point):
    value = (0, 0)
    for coefficient in reversed(coefficients):
        value = gaussian_add(gaussian_multiply(value, point), (coefficient, 0))
    return value


def gaussian_definition(n, point):
    value = (0, 0)
    power = (1, 0)
    minus_point = (-point[0], -point[1])
    for k in range(n, -1, -1):
        value = gaussian_add(value, gaussian_scale(power, comb(n, k//2)))
        power = gaussian_multiply(power, minus_point)
    return value


def four_term_residual(n, r, values):
    return (r*n*values[n] + ((r*r+1)*n-2*r)*values[n-1]
            - (4*r*(n-2)+2*(r*r+1))*values[n-2]
            - 4*(r*r+1)*(n-2)*values[n-3])


class CentralBinomialTests(unittest.TestCase):
    def test_integer_definition_and_first_order_recurrence(self):
        # 25*161=4,025 coefficient comparisons and 25*158=3,950 residuals.
        for r in range(-12, 13):
            values = central_binomial_coefficients(r, 160)
            self.assertEqual(len(values), 161)
            for n, value in enumerate(values):
                self.assertIsInstance(value, int)
                self.assertEqual(value, central_binomial_sum(n, r), (n, r))
                if n >= 3:
                    self.assertEqual(four_term_residual(n, r, values), 0, (n, r))

    def test_rational_definition_and_first_order_recurrence(self):
        # 3*41=123 coefficient comparisons and 3*38=114 residuals.
        for r in (Fraction(-3, 2), Fraction(1, 2), Fraction(7, 3)):
            values = central_binomial_coefficients(r, 40)
            for n, value in enumerate(values):
                self.assertIsInstance(value, (int, Fraction))
                self.assertEqual(value, central_binomial_sum(n, r), (n, r))
                if n >= 3:
                    self.assertEqual(four_term_residual(n, r, values), 0, (n, r))
        self.assertEqual(central_binomial_coefficients(Fraction(0), 3), [1, 1, 2, 3])

    def test_exact_polynomial_four_term_identity(self):
        # Thirty polynomial identities, n=3..32, with 585 coefficient slots.
        rows = definition_polynomials(32)
        for n, row in enumerate(rows):
            self.assertEqual(central_binomial_polynomial(n), tuple(row), n)
            self.assertEqual(len(row), n+1)
            self.assertEqual(row[-1], (-1)**n)
        for n in range(3, 33):
            residual = polynomial_sum(
                polynomial_product([0, n], rows[n]),
                polynomial_product([n, -2, n], rows[n-1]),
                polynomial_product([-2, -4*(n-2), -2], rows[n-2]),
                polynomial_product([-4*(n-2), 0, -4*(n-2)], rows[n-3]),
            )
            self.assertEqual(residual, [0]*(n+2), n)

    def test_initial_polynomials_and_worked_specialization(self):
        self.assertEqual([central_binomial_polynomial(n) for n in range(4)],
                         [(1,), (1, -1), (2, -1, 1), (3, -3, 1, -1)])
        for r in (-4, -1, 0, 1, 4, Fraction(2, 3)):
            expected = [1, 1-r, r*r-r+2, -r**3+r*r-3*r+3]
            self.assertEqual([central_binomial_sum(n, r) for n in range(4)], expected)
            self.assertEqual(central_binomial_coefficients(r, 3), expected)
        self.assertEqual(central_binomial_coefficients(4, 11),
                         [1, -3, 14, -57, 246, -1038, 4424, -18777,
                          79846, -339258, 1442004, -6128202])

    def test_real_boundary_specializations(self):
        for r in (-1, 0, 1):
            values = central_binomial_coefficients(r, 64)
            for n, value in enumerate(values):
                expected = (2**n if r == -1 else comb(n, n//2) if r == 0
                            else 0 if n % 2 else comb(n, n//2))
                self.assertEqual(value, expected, (n, r))
        for r in (0, -1, 1, Fraction(1, 2)):
            self.assertEqual(central_binomial_coefficients(r, 0), [1])
            self.assertEqual(central_binomial_sum(0, r), 1)

    def test_imaginary_boundary_parameters_without_floating_point(self):
        # Exact Gaussian-integer arithmetic at +i and -i through index40.
        for r in ((0, 1), (0, -1)):
            values = []
            for n in range(41):
                value = gaussian_polynomial(central_binomial_polynomial(n), r)
                self.assertEqual(value, gaussian_definition(n, r), (n, r))
                values.append(value)
                if n >= 3:
                    # Since r*r+1=0 and r!=0, cancel r in the four-term identity.
                    residual = gaussian_add(
                        gaussian_scale(values[n], n),
                        gaussian_add(gaussian_scale(values[n-1], -2),
                                     gaussian_scale(values[n-2], -4*(n-2))))
                    self.assertEqual(residual, (0, 0), (n, r))

    def test_invalid_indices_are_not_rounded_or_reinterpreted(self):
        for bad in (-1, -20):
            with self.assertRaises(ValueError):
                central_binomial_sum(bad, 1)
            with self.assertRaises(ValueError):
                central_binomial_polynomial(bad)
            with self.assertRaises(ValueError):
                central_binomial_coefficients(1, bad)
        for bad in (True, False, 2.0, 1.5, Fraction(2), '2', None):
            with self.assertRaises(TypeError):
                central_binomial_sum(bad, 1)
            with self.assertRaises(TypeError):
                central_binomial_polynomial(bad)
            with self.assertRaises(TypeError):
                central_binomial_coefficients(1, bad)

    def test_inexact_and_unsupported_parameters_are_rejected(self):
        for bad in (True, False, 1.0, 0.5, float('nan'), float('inf'),
                    1j, '1/2', Decimal('0.5'), None):
            with self.assertRaises(TypeError):
                central_binomial_sum(0, bad)
            with self.assertRaises(TypeError):
                central_binomial_coefficients(bad, 0)

    def test_catalogue_and_family_define_the_exact_specializations(self):
        records = central_binomial_catalogue()
        self.assertEqual([row['id'] for row in records],
                         ['KFOR-CF-CB-m1']+[f'KFOR-CF-CB-{r}' for r in range(5)])
        self.assertEqual([row['oeis'] for row in records],
                         ['A000079', 'A001405', 'A126869',
                          'A127361', 'A127362', 'A127363'])
        for row in records:
            r = row['r']
            self.assertEqual(row['source'], SOURCE)
            self.assertEqual(row['closed_form_family'], FAMILY_ID)
            self.assertEqual((row['offset'], row['N'], row['degree']), (0, 1, 'n'))
            self.assertEqual(len(row['terms']), COUNT)
            self.assertEqual(row['terms'], [str(central_binomial_sum(n, r))
                                            for n in range(COUNT)])
            self.assertEqual(row['calculator'], {'mode': 'central_binomial', 'r': r})
            self.assertEqual(len(row['formulas']), 3)
            self.assertEqual([f['kind'] for f in row['formulas']],
                             ['finite sum', 'generating function', 'recurrence'])
            self.assertTrue(all(f['source'] == SOURCE for f in row['formulas']))
            self.assertIn('a(0)=1, a(1)=1-r, a(2)=r^2-r+2', row['recurrence'])
            self.assertIn('Known sequence specialization', row['status'])
            if r == 0:
                self.assertIn('a(n)=binom(n,floor(n/2)) for all n>=0', row['recurrence'])
        families = central_binomial_families()
        self.assertEqual(len(families), 1)
        family = families[0]
        self.assertEqual(family['id'], FAMILY_ID)
        self.assertEqual(family['domain'], 'r in C; n>=0')
        self.assertEqual(family['paper'], 'CLOSED-FORMS-II-III')
        self.assertEqual(family['paper_refs'], [])
        self.assertEqual(family['derivation'], SOURCE)
        self.assertEqual(len(family['formulas']), 3)


if __name__ == '__main__':
    unittest.main()
