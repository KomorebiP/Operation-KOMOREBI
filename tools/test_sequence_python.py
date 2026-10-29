"""Finite exact controls for the source-linked sequence plotting presets."""
import contextlib
import csv
from fractions import Fraction as Q
import importlib.util
import io
import json
from math import comb, factorial
from pathlib import Path
import sys
import unittest

from komorebi_math.sequences import reciprocal_coefficients
from sequence_presets import SEQUENCE_PRESETS

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('komorebi_browser', ROOT/'website/python/komorebi_browser.py')
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def multiply(a, b, count):
    return [sum(a[k]*b[n-k] for k in range(n+1)) for n in range(count)]


class SequencePythonTests(unittest.TestCase):
    def test_reciprocal_coefficients_against_ordinary_rational_inversion(self):
        # This uses ordinary series in w, with rational coefficients, rather
        # than the library's compressed integer binomial recurrence.
        count = 16
        for N in range(2, 9):
            denominator = [Q((-1)**n, factorial(N*n)) for n in range(count)]
            inverse = [Q(1)]
            for n in range(1, count):
                inverse.append(-sum(denominator[k]*inverse[n-k] for k in range(1, n+1)))
            power = [Q(1)]+[Q(0)]*(count-1)
            for r in range(4):
                with self.subTest(N=N, r=r):
                    values = reciprocal_coefficients(N, count, power=r)
                    self.assertEqual(tuple(power[n]*factorial(N*n) for n in range(count)), values)
                power = multiply(power, inverse, count)
        self.assertEqual(Q(reciprocal_coefficients(2, 3)[2], factorial(4)), Q(5, 24))
        self.assertNotEqual(Q(5, factorial(2)), Q(5, 24))

    def test_presets_outputs_and_exact_exports(self):
        from unittest.mock import patch
        with patch.dict(sys.modules, {'komorebi_browser': HELPER}):
            for name, spec in SEQUENCE_PRESETS.items():
                with self.subTest(preset=name):
                    HELPER._reset()
                    messages = []
                    HELPER._sink = messages.append
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        exec(compile(spec['code'], name+'.py', 'exec'), {'__name__': '__main__'})
                    self.assertEqual(output.getvalue(), spec['expected'])
                    records = [json.loads(m) for m in messages]
                    exported = [m for m in records if m['kind'] == 'file']
                    self.assertEqual(len(exported), 1)
                    rows = list(csv.DictReader(io.StringIO(exported[0]['content'])))
                    if name.startswith('sequence-'):
                        self.assertEqual(len(rows), 112 if name.endswith('landscape') else 16)
                        for row in rows:
                            self.assertEqual(Q(row['normalized_fraction']), Q(int(row['A']), factorial(int(row['degree']))))
                    else:
                        self.assertEqual(len(rows), 190)
                        for row in rows:
                            n, k = int(row['n']), int(row['k'])
                            # Inclusion-exclusion for labelled surjections,
                            # independent of the displayed Stirling recurrence.
                            expected = sum((-1)**(k-j)*comb(k,j)*j**n for j in range(k+1))
                            self.assertEqual(int(row['weighted_contribution']), expected)
                            self.assertEqual(int(row['stirling'])*factorial(k), expected)
                    self.assertTrue(any(m['kind'] == 'plot' for m in records))


if __name__ == '__main__':
    unittest.main()
