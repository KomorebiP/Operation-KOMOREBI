"""Keep editorial routes tied to each paper's recorded sources and examples."""
import copy
import json
from pathlib import Path
import posixpath
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from reader_guidance import load_introductions, prepare_introductions, paper_introduction, notation_help, reading_passage_url
from check_reader_site import Page


class ReaderGuidanceTests(unittest.TestCase):
    def reader(self):
        root=Path(__file__).resolve().parents[1]
        claims=json.loads((root/'manifests/claim-navigation.json').read_bytes())
        learning=json.loads((root/'manifests/reader-experience.json').read_bytes())
        owned={}
        for work in claims['works']:
            receipt=json.loads((root/('manifests/source-imports/'+work['id']+'.json')).read_bytes())
            for entry in receipt['files']:
                owned[receipt['destination']+'/'+entry['path']]={**entry, 'work':work['id']}
        site=SimpleNamespace(root=root,claims=claims,revision='test-revision',
                             rel=lambda target,page:posixpath.relpath(target,posixpath.dirname(page)),
                             read_source=lambda record:(root/record['repository_path']).read_bytes())
        reader=SimpleNamespace(site=site,learning=learning,owned=owned,records={})
        def add(path):reader.records[path]={'repository_path':path};return reader.records[path]
        reader.add=add
        reader.resolve=lambda path,page,fragment:'source.html#'+fragment
        return reader

    def test_all_twelve_reading_paths_keep_their_own_example_statement_and_proof(self):
        reader=self.reader();reader.paper_introductions=load_introductions(reader)
        self.assertEqual(len(reader.paper_introductions),12)
        prepare_introductions(reader)
        for work,guide in reader.paper_introductions.items():
            with self.subTest(work=work):
                markup=paper_introduction(reader,work,'collection/works/'+work+'.html')
                parsed=Page(markup)
                self.assertIn('reading-path',parsed.ids)
                self.assertEqual(markup.count('<li>'),4)
                self.assertIn(guide['question'],markup)
                self.assertIn('Assumptions and limits.',markup)
                self.assertNotIn('None',parsed.links)
        self.assertIn('Conjecture 66',paper_introduction(reader,'paper-xi','collection/works/paper-xi.html'))
        self.assertIn('GPU execution was not performed',paper_introduction(reader,'paper-viii','collection/works/paper-viii.html'))

    def test_cross_work_examples_and_claims_are_rejected(self):
        reader=self.reader()
        reader.learning=copy.deepcopy(reader.learning)
        next(t for t in reader.learning['learning_topics'] if t['id']=='seeds')['works']=[]
        with self.assertRaisesRegex(ValueError,'Example does not belong'):load_introductions(reader)
        reader=self.reader()
        next(r for r in reader.site.claims['records'] if r['id']=='PSC-I-T-SINGLE-OPERATOR')['work_id']='paper-ii'
        with self.assertRaisesRegex(ValueError,'statement and proof'):load_introductions(reader)

    def test_partial_book_build_only_loads_selected_paper_introductions(self):
        reader=self.reader()
        reader.site.registry={'components':[{'id':'proof-path-theory'}]}
        reader.site.claims={'records':[]}
        self.assertEqual(load_introductions(reader),{})
        self.assertEqual(reader.records,{})
        reader=self.reader()
        reader.site.registry={'components':[{'id':'paper-i'}]}
        reader.site.claims['records']=[row for row in reader.site.claims['records'] if row['work_id']=='paper-i']
        self.assertEqual(set(load_introductions(reader)),{'paper-i'})
        self.assertEqual(len(reader.records),1)

    def test_moved_setup_requires_review_and_introduction_text_is_inert(self):
        reader=self.reader();reader.paper_introductions=load_introductions(reader)
        reader.paper_introductions['paper-i']['setup']['expected']='A changed definition'
        with self.assertRaisesRegex(ValueError,'setup for paper-i'):prepare_introductions(reader)
        reader.paper_introductions['paper-i']['question']='<script>bad</script>'
        markup=paper_introduction(reader,'paper-i','collection/works/paper-i.html')
        self.assertIn('&lt;script&gt;bad&lt;/script&gt;',markup)
        self.assertNotIn('<script>',markup)

    def test_notation_is_optional_and_scoped_to_the_chapter_work(self):
        reader=self.reader()
        controls,dialog=notation_help(reader.site,'read/paper-i/one.html','paper-i')
        self.assertIn('hidden>Notation help</button>',controls)
        self.assertIn('href="../../notation/paper-i.html"',controls)
        self.assertIn('data-work="paper-i"',dialog)
        self.assertIn('data-source="../../notation/reader/paper-i.json?v=test-revision"',dialog)
        self.assertNotIn('<script',dialog)

    def test_interior_source_lines_link_to_the_containing_rendered_passage(self):
        first=SimpleNamespace(nodes=[dict(line=10,end_line=25,id='L10')])
        second=SimpleNamespace(nodes=[dict(line=30,end_line=50,id='L30')])
        reader=SimpleNamespace(readable_books={'test':{'chapters':[
            (dict(source='main.tex',url='read/test/first.html'),b'',first),
            (dict(source='main.tex',url='read/test/second.html'),b'',second)]}})
        self.assertEqual(reading_passage_url(reader,'main.tex',17),'read/test/first.html#L10')
        self.assertEqual(reading_passage_url(reader,'main.tex',38),'read/test/second.html#L30')
        self.assertIsNone(reading_passage_url(reader,'other.tex',17))
        self.assertIsNone(reading_passage_url(reader,'main.tex',28))


if __name__=='__main__':unittest.main()
