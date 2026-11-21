"""Regression checks for conserved proofs, corrected labels, and frozen artifacts."""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
import json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sequence_final_edition import assemble,paper_fragment,verify_artifacts,EDITION
from sequence_math_reading import mathematical_reading_fragment
ROOT=Path(__file__).resolve().parents[1]

class PaperTests(unittest.TestCase):
    def test_complete_edition_preserves_imported_mathematics_and_updates_scope(self):
        paper, report=assemble(ROOT)
        self.assertEqual(paper,(ROOT/EDITION/'PAPER.md').read_text(encoding='utf-8'))
        self.assertEqual(report,json.loads((ROOT/EDITION/'ASSEMBLY.json').read_text(encoding='utf-8')))
        self.assertEqual(report['imported_mathematical_token_changes'],0)
        self.assertEqual(sum(row['tex_expressions_preserved'] for row in report['imports']),589)
        self.assertEqual(sum(len(row['tex_layout_changes']) for row in report['imports']),2)
        self.assertNotIn('This does not classify minimal orders on the exceptional parameter locus',paper)
        self.assertIn('**Certificate lemma.**',paper)
        for name in ['K','L','M','N']:
            self.assertIn('**Theorem '+name+'.**',paper)

    def test_final_reader_internal_cross_references_resolve(self):
        class Links(HTMLParser):
            def __init__(self):super().__init__();self.ids=[];self.refs=[]
            def handle_starttag(self,tag,attrs):
                data=dict(attrs)
                if 'id' in data:self.ids.append(data['id'])
                if data.get('href','').startswith('#'):self.refs.append(data['href'][1:])
        parser=Links();parser.feed(paper_fragment(ROOT)[0])
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertFalse(set(parser.refs)-set(parser.ids))
        self.assertGreater(len(parser.refs),30)
        bad=mathematical_reading_fragment('[x](javascript:evil) [y](file:///private) [z](#valid)')
        self.assertNotIn('href="javascript:',bad);self.assertNotIn('href="file:',bad)
        self.assertIn('href="#valid"',bad)

    def test_legacy_k5_tag_is_hoisted_outside_aligned(self):
        source='\\[\n\\begin{aligned}\nx&=1. \\tag{K5}\n\\end{aligned}\n\\]'
        html=mathematical_reading_fragment(source)
        self.assertIn('x&amp;=1.',html)
        self.assertIn('\\end{aligned}\n\\tag{K5}',html)
        self.assertNotIn('\\tag{K5}\n\\end{aligned}',html)

    def test_artifacts_are_bound_to_the_manuscript_and_rendering_inputs(self):
        receipt=verify_artifacts(ROOT)
        self.assertEqual(receipt['edition'],'1.0')
        self.assertGreater(receipt['pages'],20)
        self.assertEqual(receipt['math_errors'],0)
        self.assertEqual(receipt['offline_automatic_requests'],0)
        self.assertEqual(receipt['localhost_links'],[])
        html=(ROOT/EDITION/'PAPER.html').read_text(encoding='utf-8')
        self.assertIn('href="#main"',html)
        self.assertIn('id="main"',html)

if __name__=='__main__':unittest.main()
