"""Guard the complete reading edition against silent scientific or routing loss."""
from collections import Counter
import copy,hashlib,json,re,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import smith_chart_reading as e
import smith_chart_unified as book
from test_smith_unified import ROOT,fixture

class ReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.site=fixture(cls.tmp.name)
        cls.raw=book.build_source_body(cls.site)
        cls.record=json.loads((ROOT/e.EDITION).read_bytes())
        cls.review=json.loads((ROOT/book.BASE/'READING_REVIEW.json').read_bytes())
        cls.final=e.finalize(ROOT,cls.raw)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_review_binds_entire_edition_and_complete_reading_pass(self):
        self.assertEqual(self.review['reviewed_parts'],list(range(1,26)))
        self.assertEqual(self.review['edition_sha256'],hashlib.sha256((ROOT/e.EDITION).read_bytes()).hexdigest())
        self.assertEqual(self.review['input_semantic_sha256'],e.digest(e.normalized(self.raw)))
    def test_every_removed_and_restored_expression_is_accounted_for(self):
        before=Counter(e.digest(m[0]) for m in e.MATH.finditer(self.raw))
        after=Counter(e.digest(m[0]) for m in e.MATH.finditer(self.final))
        audit=self.review['mathematics']
        self.assertEqual(dict(before-after),audit['removed_expression_hashes'])
        self.assertEqual(dict(after-before),audit['added_expression_hashes'])
        self.assertEqual(sum(after.values()),audit['output_expressions'])
        self.assertEqual(len(audit['source_forced_restorations']),2)
    def test_source_semantics_change_requires_another_review(self):
        with self.assertRaisesRegex(ValueError,'source changed'):
            e.apply_edits(self.raw.replace('Fejér','Changed',1),self.record)
    def test_deployment_url_changes_preserve_the_source_binding(self):
        changed=re.sub(r'\bhref="[^"]*"','href="https://example.invalid/source"',self.raw)
        self.assertEqual(e.normalized(changed),e.normalized(self.raw))
        e.apply_edits(changed,self.record)
    def test_prose_edit_cannot_change_a_retained_equation(self):
        record=copy.deepcopy(self.record)
        edit=next(x for x in record['edits'] if x['action']=='replace' and '{M0}' in x.get('text','') and not(x.get('retire_mathematics') or x.get('mathematical_repair')))
        edit['text']=edit['text'].replace('{M0}',r'\(0=1\)',1)
        with self.assertRaisesRegex(ValueError,'changed mathematics'):e.apply_edits(self.raw,record)
    def test_phrase_edits_fail_closed_on_ambiguous_or_missing_words(self):
        record=copy.deepcopy(self.record);edit=next(x for x in record['edits'] if x['action']=='sub')
        edit['changes'][0][0]='phrase absent from source'
        with self.assertRaisesRegex(ValueError,'Ambiguous editorial phrase'):e.apply_edits(self.raw,record)
    def test_forced_restoration_must_match_the_original_proof_source(self):
        record=copy.deepcopy(self.record)
        next(x for x in record['edits'] if x.get('mathematical_repair'))['mathematical_repair']['source_sha256']='0'*64
        original=Path.read_bytes
        def read(path):return json.dumps(record).encode() if path==ROOT/e.EDITION else original(path)
        with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(ValueError,'correction source changed'):
            e.finalize(ROOT,self.raw)
        self.assertIn(r'0&lt;Z(s)&lt;\infty',self.final)
        self.assertIn(r'R&lt;\mu/8',self.final)
        self.assertIn(r'R&gt;8/\mu',self.final)
    def test_all_old_fragments_and_scientific_figures_survive(self):
        old=e.Source(self.raw);new=e.Source(self.final)
        oldids={x['attrs']['id'] for x in old.nodes if 'id' in x['attrs']}
        newids=[x['attrs']['id'] for x in new.nodes if 'id' in x['attrs']]
        self.assertFalse(oldids-set(newids));self.assertEqual(len(newids),len(set(newids)))
        figures=[n for n in new.nodes if n['tag']=='figure']
        self.assertEqual(len(figures),51)
        for i,n in enumerate(figures,1):
            fragment=self.final[n['start']:n['end']]
            self.assertEqual(re.findall(r'<figcaption\b[^>]*><strong>Figure (\d+)\.</strong>',fragment),[str(i)])
            self.assertEqual(len(re.findall(r'Figure \d+\.',fragment)),1)
        for n in new.nodes:
            href=n['attrs'].get('href','')
            if href.startswith('#'):
                from urllib.parse import unquote
                self.assertIn(unquote(href[1:]),newids)
    def test_figures_have_only_the_declared_text_changes(self):
        self.assertEqual(len(self.record['figure_editions']),11)
        for fig in self.record['figure_editions']:
            old=(ROOT/fig['source']).read_bytes();new=(ROOT/fig['edition']).read_bytes()
            self.assertEqual(hashlib.sha256(old).hexdigest(),fig['source_sha256'])
            text=old.decode()
            for a,b in fig['text_changes']:
                self.assertEqual(text.count(a),1);text=text.replace(a,b,1)
            self.assertEqual(text.encode(),new)
    def test_visible_reading_contains_no_development_version_log(self):
        text=e.prose(self.final)
        self.assertNotRegex(text,re.compile(r'\bdraft\b|superseded|predecessor|checkpoint|outstanding|remains? open|remaining work|we have not proved',re.I))
        self.assertNotRegex(text,re.compile(r'\b(?:terminal|vertices|totals|below|minus|value|radius|baseline|all|step)\d',re.I))
    def test_reading_support_is_bound_to_its_reviewed_sources(self):
        path=ROOT/book.BASE/'reader-support.json'
        record=json.loads(path.read_bytes())
        self.assertEqual(self.review['reader_support']['support_sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(record['guide_sha256'],hashlib.sha256((ROOT/record['guide']).read_bytes()).hexdigest())
        self.assertIn('id="reading-guide"',self.final)
        with self.assertRaisesRegex(ValueError,'source changed'):
            e.reader_support(ROOT,'<article>Unreviewed input</article>')
    def test_each_figure_has_a_source_bound_text_alternative(self):
        source=e.Source(self.final)
        figures=[n for n in source.nodes if n['tag']=='figure']
        for index,node in enumerate(figures,1):
            fragment=self.final[node['start']:node['end']]
            self.assertIn('aria-details="smith-figure-description-'+str(index)+'"',fragment)
            self.assertIn('<summary>Text description of figure '+str(index)+'</summary>',fragment)
            self.assertEqual(fragment.count('class="figure-description"'),1)
            self.assertNotIn('alt="Python-generated',fragment)
    def test_tables_and_preformatted_examples_have_reading_semantics(self):
        source=e.Source(self.final)
        for node in source.nodes:
            if node['tag']=='table':
                fragment=self.final[node['start']:node['end']]
                self.assertEqual(len(re.findall('<caption\\b',fragment)),1)
                self.assertTrue(all('scope=' in tag for tag in re.findall('<th(?:\\s[^>]*)?>',fragment)))
                parent=source.nodes[node['parent']]
                self.assertEqual(parent['attrs'].get('tabindex'),'0')
                self.assertEqual(parent['attrs'].get('role'),'region')
                self.assertTrue(parent['attrs'].get('aria-label'))
            if node['tag']=='pre':
                self.assertEqual(node['attrs'].get('tabindex'),'0')
                self.assertTrue(node['attrs'].get('aria-label'))
    def test_source_notation_survives_markdown_rendering(self):
        self.assertIn('dP*Q-P*dQ',self.final)
        self.assertIn("k'_e differs relatively from k_e",self.final)
        self.assertIn('A_j*x=(Gamma_Z(s_j)-h_j)*(P(s_j)+Q(s_j))',self.final)
        self.assertIn(r'\[N:(12,51,95,111,81,33,6),\]',self.final)
        self.assertIn(r'\[D:(17,68,139,164,126,57,10).\]',self.final)
        for node in e.Source(self.final).blocks():
            if node['tag']=='p':self.assertNotIn('$',e.MATH.sub('',node['html']))
    def test_described_figure_accepts_only_its_two_bound_line_endings(self):
        record=json.loads((ROOT/book.BASE/'reader-support.json').read_bytes())
        entries=[x for x in record['figures'] if x.get('checkout_sha256')]
        self.assertEqual(len(entries),1)
        entry=entries[0];path=ROOT/entry['path'];raw=path.read_bytes();lf=raw.replace(b'\r\n',b'\n')
        self.assertEqual(hashlib.sha256(lf).hexdigest(),entry['source_sha256'])
        self.assertEqual(hashlib.sha256(lf.replace(b'\n',b'\r\n')).hexdigest(),entry['checkout_sha256'])
        original=Path.read_bytes
        for variant in (lf,lf.replace(b'\n',b'\r\n')):
            def read(candidate):return variant if candidate==path else original(candidate)
            with patch.object(Path,'read_bytes',read):self.assertEqual(e.finalize(ROOT,self.raw),self.final)
        def changed(candidate):return lf+b'<!-- changed -->' if candidate==path else original(candidate)
        with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(ValueError,'described figure source changed'):
            e.finalize(ROOT,self.raw)

if __name__=='__main__':unittest.main()
