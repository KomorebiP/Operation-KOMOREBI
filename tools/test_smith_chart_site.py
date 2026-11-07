"""Source and exact finite regression checks for the Smith chart laboratory."""
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == 'id':
                self.ids.append(value)

class SmithChartSiteTest(unittest.TestCase):
    def test_source_and_selectors(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        css = (ROOT/'website/assets/smith-chart.css').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        self.assertIn('id="smith-studio"', body)
        self.assertIn('id="smith-chart"', body)
        self.assertIn('id="grid-mode"', body)
        self.assertIn('id="panel-verify"', body)
        self.assertIn('id="run-tests"', body)
        self.assertIn('@scope (.smith-lab)', css)
        self.assertIn("$('smith-studio').classList.add('js-ready')", js)
        self.assertIn('runChecks()', js)
        self.assertNotIn('Not yet published', body)
        ids = Ids()
        ids.feed(body)
        self.assertEqual(len(ids.ids), len(set(ids.ids)))
        self.assertEqual(len(re.findall(r'<h1\b', body)), 1)
        self.assertNotRegex(body, r'<main\b|<script\b')

    def test_each_input_has_an_accessible_name(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        controls = re.findall(r'<(?:input|select|textarea)[ >][^>]*>', body)
        self.assertGreaterEqual(len(controls), 16)
        for control in controls:
            self.assertRegex(control, r'aria-label="[^"]+"')

    def test_cleanup_navigation_and_optional_controls(self):
        body = (ROOT/'website/smith-chart-body.html').read_text(encoding='utf-8')
        js = (ROOT/'website/assets/smith-chart.js').read_text(encoding='utf-8')
        self.assertEqual(body.count('<h1'), 1)
        nav = body.split('<nav class="smith-section-nav"', 1)[1].split('</nav>', 1)[0]
        targets = re.findall(r'href="#([^"]+)"', nav)
        ids = set(re.findall(r'\bid="([^"]+)"', body))
        self.assertEqual(len(targets), 4)
        self.assertTrue(set(targets).issubset(ids))
        self.assertIn('<details class="overlay-options">', body)
        self.assertIn('<details class="advanced-values">', body)
        for key in ('show-rays', 'show-orbit'):
            tag = re.search(r'<input[^>]*id="'+key+r'"[^>]*>', body)
            self.assertIsNotNone(tag)
            self.assertNotIn('checked', tag.group(0))
        self.assertIn("for(const id of ['show-rays','show-orbit'])$(id).checked=false;", js)

    def test_projector_impedance_identity_exactly(self):
        for t in (Fraction(0), Fraction(1,10), Fraction(-2,5), Fraction(3,4)):
            z = (1+t)/(1-t)
            for n in (2,3,4,5,6,8,12):
                packets = [(1+t**n)/(1-t**n)] + [
                    2*t**j/(1-t**n) for j in range(1,n)]
                self.assertEqual(sum(packets), z)
                K = 5
                for j in range(1,n):
                    finite = sum(2*t**(j+q*n) for q in range(K))
                    self.assertEqual(finite, 2*t**j*(1-t**(K*n))/(1-t**n))
                finite_zero = 1 + sum(2*t**(q*n) for q in range(1,K+1))
                self.assertEqual(finite_zero, 1+2*t**n*(1-t**(K*n))/(1-t**n))

    def test_admittance_parity_and_reconstruction(self):
        for t in (Fraction(1,2), Fraction(-1,3), Fraction(3,5)):
            z, y = (1+t)/(1-t), (1-t)/(1+t)
            for n in (2,3,4,5,6,8,12):
                zp = [(1+t**n)/(1-t**n)] + [
                    2*t**j/(1-t**n) for j in range(1,n)]
                if n % 2 == 0:
                    yp = [(-1)**j * zp[j] for j in range(n)]
                else:
                    yp = [(1-t**n)/(1+t**n)] + [
                        2*(-1)**j * t**j/(1+t**n) for j in range(1,n)]
                self.assertEqual(sum(zp), z)
                self.assertEqual(sum(yp), y)
                self.assertEqual(z*y, 1)

if __name__ == '__main__':
    unittest.main()
