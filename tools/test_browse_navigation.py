"""Check usable direct links without inventing availability or formal coverage."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from browse_navigation import Browser, REGISTRY, link, validate_resources
from update_source_navigation import Renderer


class BrowseNavigationTests(unittest.TestCase):
    def fixture(self, root):
        paths = ['README.md', 'paper.pdf', 'paper.tex', 'lean-guide.pdf',
                 'formal/Main.lean', 'formal/lakefile.lean', 'code/example.py', 'text with spaces.tex']
        rows = []
        assets = [{'kind':k,'label':label,'path':p} for k,label,p in [
            ('guide','Edition README','README.md'), ('pdf','Read PDF','paper.pdf'),
            ('text','Manuscript text (TeX)','paper.tex'),
            ('formal_guide','Lean guide (PDF)','lean-guide.pdf'),
            ('lean','Lean sources','formal/'), ('code','Code','code/')]]
        registry = {'schema':1,'selection_revision':'a'*40,'components':[]}
        status = {'labels':{'stage':{'development':['Active development']},
                  'lean':{'source':['Source; no current pass']},
                  'confidence':{'unassessed':['Unassessed']}},'components':[]}
        tracked = set()
        (root/'manifests/source-imports').mkdir(parents=True)
        for identifier in ['open-work','held-work']:
            c={'id':identifier,'destination':'research/'+identifier,'group':'research',
               'role':'primary','available':True,'title':identifier.title(), 'summary':'Bounded development',
               'category':'research','boundary':'Open obligations',
               'receipt':'manifests/source-imports/'+identifier+'.json'}
            (root/c['receipt']).write_text(json.dumps({'component':identifier,'destination':c['destination'],
                'files':[{'path':p} for p in paths]}),encoding='utf-8')
            rows.append(c)
            registry['components'].append({'id':identifier,'destination':c['destination'],'resources':copy.deepcopy(assets)})
            s={'id':identifier,'stage':'development','lean':'source','confidence':'unassessed'}
            if identifier=='held-work':s['reader_listing']={'placement':'incubator'}
            status['components'].append(s)
            tracked.update(c['destination']+'/'+p for p in paths)
        (root/REGISTRY).write_text(json.dumps(registry),encoding='utf-8')
        (root/'manifests/project-status.json').write_text(json.dumps(status),encoding='utf-8')
        return registry, {'components':rows}, status, tracked

    def test_direct_files_survive_sparse_checkout_and_labels_keep_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); registry,state,status,tracked=self.fixture(root)
            before=copy.deepcopy(status)
            browser=Browser(root,state,status,tracked)
            pages=browser.render()
            text=pages['docs/browse/RESEARCH.md']
            self.assertIn('(../../research/open-work/paper.pdf)',text)
            self.assertIn('(../../research/open-work/paper.tex)',text)
            self.assertIn('Source; no current pass',pages['docs/browse/LEAN.md'])
            self.assertIn('**Confidence:** Unassessed',pages['docs/works/open-work.md'])
            self.assertEqual(status,before)
            self.assertFalse((root/'research').exists())
            renderer=Renderer(root,state,tracked)
            self.assertEqual(renderer.reader_path(state['components'][0]),'docs/works/open-work.md')
            self.assertIn('paper.pdf',browser.shortcuts(state['components'][0],'README.md'))

    def test_incubator_is_preserved_but_excluded_from_resource_reading_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); _,state,status,tracked=self.fixture(root)
            pages=Browser(root,state,status,tracked).render()
            self.assertIn('**Incubator:**',pages['docs/browse/RESEARCH.md'])
            self.assertIn('INCUBATOR.md#held-work',pages['docs/browse/RESEARCH.md'])
            for name in ['PROOFS','LEAN','CODE']:
                self.assertNotIn('Held-Work',pages['docs/browse/'+name+'.md'])
            self.assertEqual(Renderer(root,state,tracked).reader_path(state['components'][1]),'docs/INCUBATOR.md#held-work')

    def test_lean_guide_does_not_become_a_source_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); registry,state,status,tracked=self.fixture(root)
            pages=Browser(root,state,status,tracked).render()
            self.assertIn('lean-guide.pdf',pages['docs/works/open-work.md'])
            self.assertNotIn('lean-guide.pdf',pages['docs/browse/LEAN.md'])
            for path in ['lean-guide.pdf','formal/lakefile.lean']:
                bad=copy.deepcopy(registry)
                bad['components'][0]['resources']=[{'kind':'lean','label':'Lean','path':path}]
                with self.subTest(path=path),self.assertRaisesRegex(AssertionError,'no declarations'):
                    validate_resources(root,bad,state,tracked)

    def test_missing_foreign_or_escaping_resources_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); registry,state,_,tracked=self.fixture(root)
            for path in ['missing.pdf','../held-work/paper.pdf','/paper.pdf','formal\\Main.lean','paper.pdf#page=2']:
                bad=copy.deepcopy(registry)
                bad['components'][0]['resources']=[{'kind':'pdf','label':'Read PDF','path':path}]
                with self.subTest(path=path),self.assertRaises(AssertionError):
                    validate_resources(root,bad,state,tracked)
            tracked.remove('research/open-work/paper.pdf')
            with self.assertRaisesRegex(AssertionError,'Git tree'):
                validate_resources(root,registry,state,tracked)

    def test_component_and_resource_duplicates_and_missing_work_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); registry,state,_,tracked=self.fixture(root)
            duplicate=copy.deepcopy(registry);duplicate['components'].append(duplicate['components'][0])
            missing=copy.deepcopy(registry);missing['components'].pop()
            repeated=copy.deepcopy(registry);repeated['components'][0]['resources'].append(repeated['components'][0]['resources'][0])
            for bad in [duplicate,missing,repeated]:
                with self.assertRaises(AssertionError):validate_resources(root,bad,state,tracked)

    def test_navigation_has_unique_explicit_targets_and_return_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); _,state,status,tracked=self.fixture(root)
            text=Browser(root,state,status,tracked).render()['docs/browse/RESEARCH.md']
            for c in state['components']:
                self.assertEqual(text.count('<a id="'+c['id']+'"></a>'),1)
                self.assertIn('(../works/'+c['id']+'.md)',text)
            self.assertEqual(text.count('[Back to contents](#contents)'),2)

    def test_work_page_sections_returns_and_separate_lean_guide(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); _,state,status,tracked=self.fixture(root)
            pages=Browser(root,state,status,tracked).render()
            text=pages['docs/works/open-work.md']
            for title,anchor in [('Read','read'),('Written proofs','written-proofs'),
                                 ('Lean','lean'),('Code','code'),('Evidence','evidence')]:
                self.assertIn('## '+title+'\n',text)
                self.assertIn('](#'+anchor+')',text)
            self.assertEqual(text.count('[Back to work navigation](#work-navigation)'),5)
            self.assertIn('(../STATUS_CATALOG.md#open-work)',text)
            self.assertIn('(../browse/RESEARCH.md#contents)',text)
            lean=text.split('## Lean\n')[1].split('## Code\n')[0]
            self.assertIn('lean-guide.pdf',lean)
            self.assertIn('formal/)',lean)
            self.assertNotIn('|',text)  # single-column reading route

    def test_previous_next_are_reciprocal_and_skip_incubator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); _,state,status,tracked=self.fixture(root)
            browser=Browser(root,state,status,tracked)
            first=state['components'][0]
            second={**first,'id':'next-work','title':'Next work'}
            third={**first,'id':'last-work','title':'Last work'}
            browser.components.extend([second,third])
            browser.assessments.update({c['id']:status['components'][0] for c in [second,third]})
            self.assertEqual(browser.neighbours(first,'docs/works/open-work.md'),
                             '- [Next: Next work](next-work.md)')
            self.assertEqual(browser.neighbours(second,'docs/works/next-work.md'),
                             '- [Previous: Open-Work](open-work.md)\n- [Next: Last work](last-work.md)')
            self.assertEqual(browser.neighbours(third,'docs/works/last-work.md'),
                             '- [Previous: Next work](next-work.md)')
            self.assertEqual(browser.neighbours(state['components'][1],'docs/works/held-work.md'),'')

    def test_special_functions_online_link_survives_page_regeneration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);registry,state,status,tracked=self.fixture(root)
            for data in (registry,state,status):
                for component in data['components']:
                    if component['id']=='open-work':component['id']='monographs-special-functions'
            receipt=root/'manifests/source-imports/open-work.json'
            contents=json.loads(receipt.read_bytes());contents['component']='monographs-special-functions'
            receipt.write_text(json.dumps(contents),encoding='utf-8')
            (root/REGISTRY).write_text(json.dumps(registry),encoding='utf-8')
            text=Browser(root,state,status,tracked).render()['docs/works/monographs-special-functions.md']
            self.assertIn('[Read online: chapters, proof appendices, figures and glossary](https://KomorebiP.github.io/Operation-KOMOREBI/read/monographs-special-functions/index.html)',text)

    def test_no_resource_selection_does_not_claim_proofs_or_sources_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); registry,state,status,tracked=self.fixture(root)
            registry['components'][0]['resources']=[]
            (root/REGISTRY).write_text(json.dumps(registry),encoding='utf-8')
            text=Browser(root,state,status,tracked).render()['docs/works/open-work.md']
            self.assertIn('Written proofs may be in the [reading files](#read)',text)
            self.assertIn('No Lean source or guide is linked here',text)
            self.assertIn('(../../research/open-work/)',text)

    def test_repaired_runtime_is_first_and_preserved_code_is_labeled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); _,state,status,tracked=self.fixture(root)
            browser=Browser(root,state,status,tracked)
            c={**state['components'][0],'id':'research-sric-external-admission'}
            browser.rows[c['id']]=browser.rows['open-work']
            links=browser.resources(c,{'code'},'docs/works/test.md')
            self.assertIn('sric-admission-v0.3.3/',links[0])
            self.assertIn('SRIC_REPAIR_2026-10-27.md',links[1])
            self.assertIn('Preserved original edition',links[2])
            shortcuts=browser.shortcuts(c,'README.md')
            self.assertIn('[Code](packages/sric-admission-v0.3.3/)',shortcuts)
            self.assertNotIn('research/open-work/code/',shortcuts)

    def test_finders_and_work_sections_have_reciprocal_exact_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); _,state,status,tracked=self.fixture(root)
            pages=Browser(root,state,status,tracked).render()
            work=pages['docs/works/open-work.md']
            for finder,section in [('PROOFS','written-proofs'),('LEAN','lean'),('CODE','code')]:
                text=pages['docs/browse/'+finder+'.md']
                self.assertIn('(../browse/'+finder+'.md#open-work)',work)
                self.assertEqual(text.count('<a id="open-work"></a>'),1)
                self.assertIn('[Open-Work](#open-work)',text)
                self.assertIn('(../works/open-work.md#'+section+')',text)
                self.assertNotIn('<a id="held-work"></a>',text)
            self.assertIn('Read the [edition guide](../../research/open-work/README.md)',work)

    def test_lean_setup_does_not_create_a_formal_source_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); registry,state,status,tracked=self.fixture(root)
            row=registry['components'][0]
            row['resources']=[a for a in row['resources'] if a['kind'] not in ('lean','guide')]
            row['resources'].append({'kind':'lean_setup','label':'Setup and limits','path':'README.md'})
            (root/REGISTRY).write_text(json.dumps(registry),encoding='utf-8')
            pages=Browser(root,state,status,tracked).render()
            self.assertNotIn('Open-Work',pages['docs/browse/LEAN.md'])
            lean=pages['docs/works/open-work.md'].split('## Lean\n')[1].split('## Code\n')[0]
            self.assertIn('No Lean source is linked here',lean)
            self.assertIn('[Setup and limits]',lean)
            self.assertLess(lean.index('[Setup and limits]'),lean.index('[Lean guide (PDF)]'))
            row['resources'][-1]['path']='paper.pdf'
            row['resources']=[row['resources'][-1]]
            with self.assertRaisesRegex(AssertionError,'instructions must be a text document'):
                validate_resources(root,registry,state,tracked)

    def test_absent_resources_offer_clickable_fallbacks_without_dead_finder_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); registry,state,status,tracked=self.fixture(root)
            registry['components'][0]['resources']=[]
            (root/REGISTRY).write_text(json.dumps(registry),encoding='utf-8')
            text=Browser(root,state,status,tracked).render()['docs/works/open-work.md']
            self.assertIn('[reading files](#read)',text)
            self.assertIn('[evidence record](#evidence)',text)
            self.assertIn('[complete file listing under Evidence](#evidence)',text)
            for finder in ['PROOFS','LEAN','CODE']:
                self.assertNotIn(finder+'.md#open-work',text)

    def test_resource_links_encode_spaces_and_parentheses_and_keep_fragments(self):
        self.assertEqual(link('Text','papers/a file (draft).tex','docs/BROWSE.md'),
                         '[Text](../papers/a%20file%20%28draft%29.tex)')
        self.assertEqual(link('Work','docs/browse/PAPERS.md#paper-i','README.md'),
                         '[Work](docs/browse/PAPERS.md#paper-i)')


if __name__=='__main__':unittest.main()
