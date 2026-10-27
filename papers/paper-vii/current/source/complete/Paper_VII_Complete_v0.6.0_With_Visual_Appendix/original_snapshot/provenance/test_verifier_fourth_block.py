#!/usr/bin/env python3
"""Regression tests for Lean audit parsing. Author: Komorebi P."""
import unittest
from verify import parse_axiom_audits

class AxiomAuditTests(unittest.TestCase):
    def test_standard_axioms(self):
        self.assertEqual(parse_axiom_audits("'X.a' depends on axioms: [propext, Classical.choice, Quot.sound]\n"),
                         {'X.a': ['propext', 'Classical.choice', 'Quot.sound']})
    def test_axiom_free(self):
        self.assertEqual(parse_axiom_audits("'X.b' does not depend on any axioms\n"), {'X.b': []})
    def test_empty_list(self):
        self.assertEqual(parse_axiom_audits("'X.c' depends on axioms: []\n"), {'X.c': []})
    def test_mixed_reports(self):
        self.assertEqual(parse_axiom_audits("'X.a' depends on axioms: [propext]\n'X.b' does not depend on any axioms\n"),
                         {'X.a': ['propext'], 'X.b': []})
    def test_missing_not_fabricated(self):
        self.assertEqual(parse_axiom_audits('not an audit\n'), {})
    def test_unexpected_axiom_retained(self):
        self.assertEqual(parse_axiom_audits("'X.a' depends on axioms: [sorryAx]\n"), {'X.a': ['sorryAx']})
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            parse_axiom_audits("'X.a' depends on axioms: [propext]\n'X.a' does not depend on any axioms\n")

if __name__ == '__main__':
    unittest.main(verbosity=2)
