#!/usr/bin/env python3
"""Regression tests for Lean audit parsing. Author: Komorebi P."""
import unittest
from verify import (parse_axiom_audits, without_comments, local_dependencies,
                    dependency_sources, build_hashes, artifacts_match)
from pathlib import Path
from tempfile import TemporaryDirectory

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

class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.base=Path(self.tmp.name)
        (self.base/'formalization').mkdir()
        (self.base/'build').mkdir()
        self.source('SyndromeRecovery','module\n')
        self.source('KnillLaflammeSufficiency','public import SyndromeRecovery\nimport all SyndromeRecovery\n')
        self.source('KnillLaflammeNecessity','public import KnillLaflammeSufficiency\n')
    def tearDown(self):
        self.tmp.cleanup()
    def source(self,name,text):
        (self.base/'formalization'/(name+'.lean')).write_text(text)
    def seed_build(self):
        d=self.base/'build'
        (d/'SyndromeRecovery.olean').write_bytes(b'public')
        (d/'SyndromeRecovery.olean.private').write_bytes(b'private')
        return build_hashes(d,'SyndromeRecovery')
    def test_duplicate_imports_collapsed(self):
        self.assertEqual(local_dependencies(self.base,'KnillLaflammeSufficiency'),['SyndromeRecovery'])
    def test_transitive_source_invalidation(self):
        before=dependency_sources(self.base,'KnillLaflammeNecessity')
        self.assertEqual(set(before),{'SyndromeRecovery','KnillLaflammeSufficiency'})
        self.source('SyndromeRecovery','module\n-- updated\n')
        self.assertNotEqual(before,dependency_sources(self.base,'KnillLaflammeNecessity'))
    def test_cycle_rejected(self):
        self.source('SyndromeRecovery','import KnillLaflammeNecessity\n')
        with self.assertRaises(ValueError):
            dependency_sources(self.base,'KnillLaflammeNecessity')
    def test_build_cache_valid(self):
        saved=self.seed_build()
        self.assertTrue(artifacts_match(self.base/'build','SyndromeRecovery',saved))
    def test_changed_private_artifact_rejected(self):
        saved=self.seed_build()
        (self.base/'build/SyndromeRecovery.olean.private').write_bytes(b'changed')
        self.assertFalse(artifacts_match(self.base/'build','SyndromeRecovery',saved))
    def test_missing_private_artifact_rejected(self):
        saved=self.seed_build()
        (self.base/'build/SyndromeRecovery.olean.private').unlink()
        self.assertFalse(artifacts_match(self.base/'build','SyndromeRecovery',saved))
    def test_unrecorded_artifact_rejected(self):
        saved=self.seed_build()
        (self.base/'build/SyndromeRecovery.ir').write_bytes(b'extra')
        self.assertFalse(artifacts_match(self.base/'build','SyndromeRecovery',saved))
    def test_nested_comment_scanner(self):
        self.assertEqual(without_comments('theorem x /- sorry /- axiom -/ -/ := by trivial').split(),
                         ['theorem','x',':=','by','trivial'])
    def test_unterminated_comment_rejected(self):
        with self.assertRaises(ValueError):
            without_comments('/- unterminated')

if __name__ == '__main__':
    unittest.main(verbosity=2)
