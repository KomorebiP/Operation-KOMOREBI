"""Finite, independent controls for the coupled special-function browser example."""
import contextlib
import csv
from fractions import Fraction as Q
import importlib.util
import io
import json
from math import factorial
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from special_function_presets import SPECIAL_FUNCTION_PRESETS

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('komorebi_browser', ROOT/'website/python/komorebi_browser.py')
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)

def run(replacement=None):
    HELPER._reset()
    messages = []
    HELPER._sink = messages.append
    spec = SPECIAL_FUNCTION_PRESETS['special-functions-coupled']
    source = spec['code']
    if replacement:
        source = source.replace(*replacement)
    output, ns = io.StringIO(), {}
    with patch.dict(sys.modules, {'komorebi_browser': HELPER}), contextlib.redirect_stdout(output):
        exec(compile(source, 'coupled.py', 'exec'), ns)
    return output.getvalue(), [json.loads(m) for m in messages], ns

class SpecialFunctionPythonTests(unittest.TestCase):
    def test_published_output_exact_export_and_majorant(self):
        out, messages, ns = run()
        self.assertEqual(out, SPECIAL_FUNCTION_PRESETS['special-functions-coupled']['expected'])
        rows = list(csv.DictReader(io.StringIO(next(m['content'] for m in messages if m['kind']=='file'))))
        self.assertEqual(len(rows), 12)
        for n,row in enumerate(rows):
            self.assertEqual(int(row['degree']), 2*n+1)
            self.assertEqual(Q(row['u']), ns['u'][n])
            self.assertEqual(Q(row['v']), ns['v'][n])
            for c in (Q(row['u']), Q(row['v'])):
                self.assertGreater(c, 0)
                self.assertLessEqual(c, Q(1, 2)**n)
        self.assertEqual(ns['tail'], Q(1, 2048))
        plots = [m for m in messages if m['kind']=='plot']
        self.assertEqual(len(plots), 1)
        self.assertEqual(len(plots[0]['data'][0]['x']), 161)

    def test_coefficients_satisfy_polynomial_differential_equations(self):
        _, _, ns = run()
        # Ordinary full-degree polynomial convolution, independent of the compressed recurrence.
        for left,right,coefficients in ((ns['q'],ns['r'],ns['u']),(ns['a'],ns['b'],ns['v'])):
            product = [Q(0)]*47
            for i,ui in enumerate(ns['u']):
                for j,vj in enumerate(ns['v']):
                    product[2*i+2*j+2] += ui*left**(2*i+1)*vj*right**(2*j+1)
            product[0] += 1
            for degree in range(23):
                derivative = (degree+1)*coefficients[degree//2] if degree%2==0 else Q(0)
                self.assertEqual(derivative, product[degree])

    def test_diagonal_matches_closed_form_coefficients(self):
        _, _, ns = run(('Q(1, 3), Q(2, 3), Q(1, 2), Q(3, 4)', 'Q(1, 2), Q(1, 2), Q(1, 2), Q(1, 2)'))
        # sqrt(2) sinh(z/sqrt(2)) has coefficient 1/(2**n (2n+1)!).
        exact = [Q(1, 2**n*factorial(2*n+1)) for n in range(12)]
        self.assertEqual(ns['u'], exact)
        self.assertEqual(ns['v'], exact)

    def test_invalid_contractions_and_counts_are_rejected(self):
        for old,new in [('Q(1, 3), Q(2, 3), Q(1, 2), Q(3, 4)', 'Q(0), Q(2, 3), Q(1, 2), Q(3, 4)'),('count = 12','count = 25')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                run((old,new))

if __name__ == '__main__':
    unittest.main()
