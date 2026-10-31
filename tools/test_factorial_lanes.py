"""Exact arithmetic and publication tests for factorial lanes."""
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from math import comb, factorial, prod
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from factorial_case import publish, verify_site

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('factorial_lane_example',
                                              ROOT/'examples/factorial_lanes.py')
EXAMPLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXAMPLE)


class FactorialLaneArithmeticTests(unittest.TestCase):
    def test_all_finite_checks(self):
        result = EXAMPLE.check()
        self.assertEqual(result['refinement'], 100)
        self.assertEqual(sum(result.values()), 225)

    def test_partition_and_missing_factor(self):
        for n in range(6):
            lanes = EXAMPLE.lane_products(n)
            self.assertEqual(factorial(4)*prod(lanes.values()), factorial(10*n+4))
        self.assertEqual(EXAMPLE.lane_products(3)[10], 6000)
        self.assertNotEqual(factorial(4)*prod(
            value for r,value in EXAMPLE.lane_products(3).items() if r!=10),factorial(34))

    def test_hypergeometric_and_reciprocal_agreement(self):
        for n in range(7):
            self.assertEqual(EXAMPLE.hypergeometric_coefficient(n),Fraction(1,factorial(10*n+4)))
        c = EXAMPLE.reciprocal_coefficients(6)
        for n in range(7):
            self.assertEqual(sum(comb(10*n,10*k)*EXAMPLE.unit_tail(k)*c[n-k]
                                 for k in range(n+1)),int(n==0))

    def test_prime_adic_bounds_and_sharp_boundary(self):
        for n in range(30):
            self.assertEqual(EXAMPLE.valuation(EXAMPLE.unit_tail(n)),0)
        for n in range(6):
            for q in (1,2,5,10):
                self.assertGreaterEqual(EXAMPLE.valuation(
                    EXAMPLE.unit_tail(n+q)-EXAMPLE.unit_tail(n)),1+EXAMPLE.valuation(q))
        self.assertEqual(EXAMPLE.valuation(Fraction(1,comb(25,5))),-1)

    def test_exports_are_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            EXAMPLE.write_tables(folder,EXAMPLE.check())
            record=json.loads((folder/'results.json').read_text())
            self.assertEqual(record['total'],225)
            self.assertIn('3,34,1/46376', (folder/'coefficients.csv').read_text())
            self.assertIn('10,10 * 20 * 30,6000', (folder/'lane-products.csv').read_text())
            for name in ('coefficients.csv', 'lane-products.csv', 'results.json'):
                self.assertEqual((folder/name).read_bytes(),
                                 (ROOT/'verification/factorial-lanes'/name).read_bytes())


class FactorialLanePublicationTests(unittest.TestCase):
    def test_publish_and_detect_corrupted_download(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)
            pages={}
            def write(path,contents):
                target=output/path
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(contents,encoding='utf-8')
            def page(path,title,body,source):
                pages[path]=body
                write(path,body)
            site=SimpleNamespace(root=ROOT,output=output,revision='a'*40,
                                 write=write,page=page,search=[])
            record=publish(site)
            pages[record['manuscript_url']]='<h1>Factorial lanes</h1>'
            # The production site checker supplies parsed Page objects, not strings.
            from check_reader_site import Page
            parsed={name:Page(body) for name,body in pages.items()}
            self.assertEqual(verify_site(output,parsed),1)
            self.assertEqual(len(site.search),1)
            (output/record['download_url']).write_bytes(b'mutated program')
            with self.assertRaises(AssertionError):
                verify_site(output,parsed)


if __name__ == '__main__':
    unittest.main()
