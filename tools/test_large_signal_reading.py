"""Publication identity, complete coverage and usable proof routes for LSM."""
import hashlib
import json
from pathlib import Path
import posixpath
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import readable_chapters as reading
from large_signal_reading import WORK, MAIN, BOOK, CHAPTERS, DATA, SCOPE_PAGE, normalize, source_specs, source_math
from build_reader_site import Site
from reader_documents import ReadingDocuments, source_lines
from check_reader_site import Page, check_readable_chapter
from reading_navigation import verify as verify_reading_navigation

ROOT = Path(__file__).resolve().parents[1]


def publish_fixture(output):
    site = SimpleNamespace(root=ROOT, output=output, revision='large-signal-reading-test',
        search=[], cache=None, assessments={}, editorial_editions={})
    for name in ('rel','write','page','read_source'):
        setattr(site,name,lambda *args,_name=name,**kwargs:getattr(Site,_name)(site,*args,**kwargs))
    reader = ReadingDocuments.__new__(ReadingDocuments)
    reader.site = site
    reader.owned, reader.records, reader.images, reader.inclusions = {}, {}, {}, {}
    reader.learning = {'learning_topics':[]}
    reader.claims_by_module, reader.claims_by_source = {}, {}
    reader.manuscript_roots = {WORK:MAIN}
    receipt = json.loads((ROOT / ('manifests/source-imports/'+WORK+'.json')).read_bytes())
    for entry in receipt['files']:
        path = receipt['destination']+'/'+entry['path']
        reader.owned[path] = dict(entry,repository_path=path,work=WORK)
    reader.add('monographs/large-signal-model/Monograph/build/Realization_Calculus_Large_Signal_Model.pdf','Read PDF')
    with patch.object(reading,'BOOKS',{WORK:BOOK}):
        reading.prepare(reader)
        prepared = set(reader.records)
        reading.render(reader)
        if set(reader.records) != prepared:
            raise AssertionError('Reading resources must be registered before source pages are rendered')
    for record in reader.records.values():
        raw = site.read_source(record)
        target = output / record['file_url']
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw)
        if record['format'] != 'pdf':
            site.page(record.get('source_url',record['url']),record['title'],
                '<h1>'+record['title']+'</h1>'+source_lines(raw.decode('utf-8-sig')))
    return reader


class LargeSignalReadingTests(unittest.TestCase):
    def test_complete_body_and_changed_source_rejection(self):
        load = lambda path:(ROOT/path).read_text(encoding='utf-8')
        raw = load(MAIN)
        self.assertEqual(source_specs(load),CHAPTERS)
        self.assertEqual(len(CHAPTERS),109)
        self.assertEqual([int(m[1]) for m in re.finditer(r'^# (\d+)\.',raw,re.M)],list(range(1,101)))
        with self.assertRaisesRegex(ValueError,'Review changed Large Signal Model'):
            source_specs(lambda path:load(path)+'\nUnreviewed change.')
        for spec in CHAPTERS:
            text = reading.chapter_text(raw,spec)
            self.assertEqual(normalize(text).count('\n'),text.count('\n'))
        # Extract the source's math independently by alternating display delimiters
        # and then parsing only the intervening inline spans.
        expected=[]
        for i,span in enumerate(raw.split('$$')):
            expected.extend([span] if i%2 else re.findall(r'(?<!\\)\$([^$\n]*?)(?<!\\)\$',span))
        self.assertEqual([v for c in CHAPTERS for v in source_math(raw,c)],expected)
        self.assertEqual(len(expected),2123)
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),DATA['source_sha256'])

    def test_publication_math_numbers_proofs_sources_and_figures(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            reader = publish_fixture(output)
            pages = {p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            with patch.object(reading,'BOOKS',{WORK:BOOK}),patch.object(reading,'CHAPTERS',CHAPTERS):
                self.assertEqual(check_readable_chapter(output,dict(files=list(reader.records.values())),pages),2123)
                self.assertEqual(verify_reading_navigation(output,pages,dict(files=list(reader.records.values()))),
                    dict(editions=1,reading_pages=110,navigation_controls=220))
            nodes = [n for _,_,c in reader.readable_books[WORK]['chapters'] for n in c.nodes]
            propositions = [n for n in nodes if n['kind']=='proposition']
            proofs = [n for n in nodes if n['kind']=='proof']
            self.assertEqual([n['number'] for n in propositions],list(map(str,range(1,88))))
            raw = (ROOT/MAIN).read_text(encoding='utf-8')
            self.assertEqual([n['line'] for n in propositions],
                [raw.count('\n',0,m.start())+1 for m in re.finditer(r'^\*\*Proposition \d+\.',raw,re.M)])
            self.assertEqual([n['line'] for n in proofs],
                [raw.count('\n',0,m.start())+1 for m in re.finditer(r'^\*\*Proof\.\*\*',raw,re.M)])
            self.assertEqual(len(proofs),87)
            self.assertEqual(sum(len(c.proof_pairs) for _,_,c in reader.readable_books[WORK]['chapters']),87)
            self.assertEqual(len(reader.images),2)
            statements = (output/'read'/WORK/'statements.html').read_text(encoding='utf-8')
            self.assertEqual(statements.count('data-statement-entry='),87)
            self.assertEqual(statements.count('class="statement-proof-link"'),87)
            for spec in CHAPTERS:
                markup = (output/spec['url']).read_text(encoding='utf-8')
                page = pages[spec['url']]
                self.assertEqual((page.h1,page.main,page.images_without_alt),(1,1,0))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                self.assertNotRegex(markup,r'\*\*Proposition|\$\$|\\begin\{proposition\}')
            self.assertEqual(len(reader.readable_books[WORK]['references']),28)
            scope_page=pages[SCOPE_PAGE]
            self.assertTrue({'p'+str(n) for n in range(1,88)} <= set(scope_page.ids))
            # Every reading destination and all source/proof fragment links exist.
            for name,page in pages.items():
                for link in page.links:
                    parts=urlsplit(link)
                    if parts.scheme or parts.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(parts.path))) if parts.path else name
                    if target.startswith('read/'+WORK+'/'):
                        self.assertTrue(target in pages or target in {r['url'] for r in reader.records.values()},(name,link))
                    if target in pages and parts.fragment and not parts.query:
                        self.assertIn(unquote(parts.fragment),pages[target].ids,(name,link))
            index=(output/BOOK['index']).read_text(encoding='utf-8')
            self.assertIn('additional glossary and formal registers',index)
            self.assertIn('no proof audit, Lean execution, or empirical validation',index)
            start=(output/BOOK['reading_guide']).read_text(encoding='utf-8')
            self.assertIn('collection/works/large-signal-model.html',start)
            self.assertIn('Signal laboratory',start)
            self.assertIn('mathematical coverage count does not establish empirical model performance',start)


if __name__=='__main__':
    unittest.main()
