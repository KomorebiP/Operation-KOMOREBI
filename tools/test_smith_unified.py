"""Canonical-book fidelity, legacy routing, source packaging and exact new checks."""
from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
import zipfile

from build_reader_site import Site
import smith_chart_unified as book
import smith_chart_research as research
import smith_chart_continuation as continuation

ROOT = Path(__file__).resolve().parents[1]


def fixture(output):
    site = Site.__new__(Site)
    site.root,site.output,site.revision = ROOT,Path(output),'a'*40
    site.search = []
    site.reader = SimpleNamespace(lean_works={},resolve=lambda *args:None,image_url=lambda *args:None,document_works=lambda *args:[])
    site.roots,site.repos,site.revisions = {'collection':ROOT},{'collection':'KomorebiP/Operation-KOMOREBI'},{'collection':site.revision}
    site.asset_count = 0
    site.documents = {('collection','docs/demonstrations/'+name+'.md'):
        (ROOT/'docs/demonstrations'/(name+'.md')).read_text(encoding='utf-8')
        for name in ('SMITH_CHART','SMITH_FIRST_ORDER_RL','SMITH_SINGULAR_COMPLETION')}
    return site


class Data(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.ids=[];self.links=[];self.math=[];self.depth=0;self.parts=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if values.get('id'):self.ids.append(values['id'])
        if values.get('href'):self.links.append(values['href'])
        if self.depth:self.depth+=1
        elif 'arithmatex' in values.get('class','').split():self.depth=1;self.parts=[]
    def handle_endtag(self,tag):
        if self.depth:
            self.depth-=1
            if self.depth==0:self.math.append(''.join(self.parts))
    def handle_data(self,value):
        if self.depth:self.parts.append(value)
    def handle_entityref(self,name):
        if self.depth:self.parts.append('&'+name+';')
    def handle_charref(self,name):
        if self.depth:self.parts.append('&#'+name+';')


class UnifiedSmithTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.site=fixture(cls.temp.name)
        continuation.publish(cls.site)
        research.publish(cls.site)
        cls.body=(cls.site.output/book.PAGE).read_text(encoding='utf-8')
        cls.parsed=Data();cls.parsed.feed(cls.body)
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def test_one_article_contents_and_all_current_sections(self):
        self.assertEqual(len(re.findall(r'<article\b',self.body)),1)
        self.assertEqual(len(re.findall(r'<h1\b',self.body)),1)
        self.assertEqual(self.parsed.ids.count('contents'),1)
        self.assertEqual(len(self.parsed.ids),len(set(self.parsed.ids)))
        for anchor in ('current-results','exact-six','composition','families','deterministic-family','obstruction',
                       'quantitative-transfer','effective-margin','compact-model-audit','singular-completion',
                       'one-inductor','companion-guide','historical-synthesis','source-ledger',
                       'low-order-synthesis','formal-graph-core','typed-margins','component-tolerances'):
            self.assertIn(anchor,self.parsed.ids)
        self.assertEqual(self.body.count('class="research-figure'),47)
        for link in self.parsed.links:
            if link.startswith('#'):
                from urllib.parse import unquote
                self.assertIn(unquote(link[1:]),self.parsed.ids,link)
    def test_all_archived_math_survives_even_when_reordered(self):
        old=Data();old.feed(research.historical_body(ROOT,'a'*40))
        missing=Counter(old.math)-Counter(self.parsed.math)
        self.assertFalse(missing,dict(missing))
        self.assertEqual(len(old.math),1668)
        self.assertEqual(len(self.parsed.math),2928)
    def test_imported_statement_math_survives_label_namespacing(self):
        manifest,files=continuation.load(ROOT)
        actual=Counter(self.parsed.math)
        for chapter in manifest['chapters']:
            source=Data();source.feed(continuation.render(files[chapter['archive']][chapter['member']].decode('utf-8')))
            expected=[re.sub(r'\\tag\{([^}]+)\}',lambda m:r'\tag{'+book.TAG_PREFIXES[chapter['slug']]+'.'+m[1]+'}',m) for m in source.math]
            self.assertFalse(Counter(expected)-actual,chapter['slug'])
    def test_old_urls_are_noindex_aliases_of_one_book(self):
        from site_metadata import canonical_url,indexable
        from side_reader import NON_DOCUMENT_PAGES,pair_link
        for path,anchor in book.ALIASES.items():
            source=(self.site.output/path).read_text(encoding='utf-8')
            self.assertIn('data-book-prefix="'+anchor+'"',source)
            self.assertIn('<noscript><meta http-equiv="refresh"',source)
            self.assertEqual(canonical_url(path),canonical_url(book.PAGE))
            self.assertFalse(indexable(path))
            self.assertIn(path,NON_DOCUMENT_PAGES)
        paired=pair_link('read/smith-chart/exact-six.html#result','read/smith-chart/families.html','index.html')
        self.assertIn('research.html%23exact-six--result',paired)
        with self.assertRaises(ValueError):
            pair_link('javascript:read/smith-chart/exact-six.html','read/a.html','index.html')
        self.assertTrue(all(row['url'].split('#')[0]==book.PAGE for row in self.site.search))
        self.assertEqual(self.site.resolve('collection','docs/a.md','read/x.html',
            'https://komorebip.github.io/Operation-KOMOREBI/playground.html?example=1#library'), '../playground.html?example=1#library')
    def test_current_source_bundle_and_kernel_bindings(self):
        archive=self.site.output/'downloads/smith-rlc-current-source.zip'
        first=hashlib.sha256(archive.read_bytes()).hexdigest()
        with zipfile.ZipFile(archive) as z:
            hashes=json.loads(z.read('SOURCE_HASHES.json'))
            for name,checksum in hashes.items():
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),checksum,name)
            self.assertIn('research/smith-chart/unified/replay_current.py',hashes)
            self.assertIn('research/smith-chart/formal/SmithFirstOrderRL.lean',hashes)
            self.assertIn('replay.py',hashes)
            self.assertFalse(any(name.lower().endswith('.pdf') for name in hashes))
        book.publish_sources(self.site)
        self.assertEqual(first,hashlib.sha256(archive.read_bytes()).hexdigest())
        bindings=json.loads((ROOT/book.BASE/'kernel-bindings.json').read_bytes())
        source=ROOT/'research/smith-chart/continuation/archives'/bindings['source_archive']
        with zipfile.ZipFile(source) as z:
            prefix=z.namelist()[0].split('/')[0]+'/src/'
            for name,checksum in bindings['files'].items():
                raw=(ROOT/book.BASE/'solver/kernel'/name).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),checksum)
                self.assertEqual(raw,z.read(prefix+name))
    def test_current_exact_suites(self):
        result=subprocess.run([sys.executable,'-B','-S',str(ROOT/book.BASE/'solver/check_all.py')],capture_output=True,check=True,text=True,timeout=180)
        record=json.loads(result.stdout)
        self.assertEqual(record['status'],'PASS')
        family,boundary=[row['report'] for row in record['suites']]
        self.assertEqual(len(family['frozen_exact_member_regressions']),38)
        self.assertEqual(len(family['controls']),15)
        self.assertEqual(boundary['exact_boundary_comparisons'],1458)


if __name__=='__main__':
    unittest.main()
