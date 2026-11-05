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


if __name__ == '__main__':
    unittest.main()
