"""Source coverage, equation identity and navigation for the methodology essay."""
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
from methodology_reading import WORK, BASE, MAIN, ESSAY, SOURCES, DATA, BOOK, CHAPTERS, source_specs, source_math, normalize
from build_reader_site import Site
from reader_documents import ReadingDocuments, source_lines
from check_reader_site import Page, check_readable_chapter

ROOT = Path(__file__).resolve().parents[1]


def reader_fixture(output):
    site = SimpleNamespace(root=ROOT, output=output, revision='methodology-conversion-test',
        search=[], cache=None, assessments={}, editorial_editions={})
    for name in ('rel', 'write', 'page', 'read_source'):
        setattr(site, name, lambda *args, _name=name, **kwargs: getattr(Site, _name)(site, *args, **kwargs))
    reader = ReadingDocuments.__new__(ReadingDocuments)
    reader.site = site
    reader.owned, reader.records, reader.images, reader.inclusions = {}, {}, {}, {}
    reader.learning = {'learning_topics': []}
    reader.claims_by_module, reader.claims_by_source = {}, {}
    reader.manuscript_roots = {WORK: MAIN}
    receipt = json.loads((ROOT / 'manifests/source-imports/komorebi-methodology.json').read_bytes())
    for entry in receipt['files']:
        path = BASE + entry['path']
        reader.owned[path] = dict(entry, repository_path=path, work=WORK)
    reader.add(BASE + 'Komorebi_Methodology.pdf', 'Read PDF')
    with patch.object(reading, 'BOOKS', {WORK: BOOK}):
        reading.prepare(reader)
    return reader


def publish_fixture(output):
    reader = reader_fixture(output)
    with patch.object(reading, 'BOOKS', {WORK: BOOK}):
        reading.render(reader)
    for record in reader.records.values():
        raw = reader.site.read_source(record)
        target = output / record['file_url']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        if record['format'] == 'source':
            reader.site.page(record['url'], record['title'], '<h1>' + record['title'] + '</h1>' + source_lines(raw.decode('utf-8-sig')))
    return reader


class MethodologyReadingTests(unittest.TestCase):
    def test_collection_report_order_matches_registered_books(self):
        works = list(dict.fromkeys(spec['work'] for spec in reading.CHAPTERS))
        expected = [work for work, config in reading.BOOKS.items()
                    if config.get('custom_reader') is not True]
        self.assertEqual(works, expected)

    def test_complete_sources_and_reject_changed_inputs(self):
        load = lambda path: (ROOT / path).read_text(encoding='utf-8-sig')
        self.assertEqual(source_specs(load), CHAPTERS)
        self.assertEqual(len(CHAPTERS), 12)
        self.assertEqual(len(re.findall(r'\\(?:section\*?|essaychapter)\{', load(ESSAY))), 10)
        for path in DATA['source_sha256']:
            with self.assertRaisesRegex(ValueError, 'changed methodology source'):
                source_specs(lambda p: load(p) + ('changed' if p == path else ''))
        for spec in CHAPTERS:
            text = reading.chapter_text(load(spec['source']), spec)
            self.assertEqual(normalize(text).count('\n'), text.count('\n'))
            self.assertEqual(reading.original_math(normalize(text)), source_math(load(spec['source']), spec))

    def test_full_publication_math_numbering_figures_and_links(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            reader = publish_fixture(output)
            pages = {path.relative_to(output).as_posix(): Page(path.read_text(encoding='utf-8'))
                     for path in output.rglob('*.html')}
            documents = dict(files=list(reader.records.values()), images=list(reader.images.values()))
            with patch.object(reading, 'BOOKS', {WORK: BOOK}), patch.object(reading, 'CHAPTERS', CHAPTERS):
                self.assertEqual(check_readable_chapter(output, documents, pages), 164)
            book = reader.readable_books[WORK]
            self.assertEqual(len(book['references']), 9)
            self.assertEqual(book['chapters'][0][2].equation_numbers,
                             {'eq:return': '1', 'eq:memory': '2', 'eq:composition': '3'})
            nodes = [node for _, _, chapter in book['chapters'] for node in chapter.nodes]
            self.assertEqual([n['number'] for n in nodes if n['kind'] == 'section' and n['number']], list(map(str, range(1, 10))))
            self.assertTrue(all(n['number'] == '' for n in nodes if n['kind'] == 'subsection'))
            self.assertEqual([n['number'] for n in nodes if n['kind'] == 'figure'], ['1', '2', '3'])
            self.assertEqual(len(reader.images), 3)
            for spec in CHAPTERS:
                page = pages[spec['url']]
                self.assertEqual((page.h1, page.main, page.images_without_alt), (1, 1, 0))
                self.assertEqual(len(page.ids), len(set(page.ids)))
                markup = (output / spec['url']).read_text(encoding='utf-8')
                self.assertIn('reading-text-size', markup)
                self.assertIn('Switch work', markup)
                self.assertNotRegex(markup, r'\\(?:essaychapter|sourceref|deck|begin\{equation|vfill)')
            preface = (output / CHAPTERS[0]['url']).read_text(encoding='utf-8')
            self.assertIn('The central proposal is to make mathematical inquiry', preface)
            self.assertIn('not a report of a new corpus-wide proof audit', preface)
            end = (output / CHAPTERS[-1]['url']).read_text(encoding='utf-8')
            self.assertIn('The comparison of research workflows remains a proposed study', end)
            refs = (output / BOOK['bib_page']).read_text(encoding='utf-8')
            self.assertIn('ref-leanvalidation', refs)
            self.assertIn('Original bibliography entry', refs)
            targets = set(pages) | {record['url'] for record in reader.records.values()}
            for name, page in pages.items():
                for link in page.links:
                    parts = urlsplit(link)
                    if parts.scheme or parts.netloc:
                        continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parts.path))) if parts.path else name
                    if target.startswith('read/' + WORK + '/'):
                        self.assertIn(target, targets, (name, link))
                    if target in pages and parts.fragment and not parts.query:
                        self.assertIn(unquote(parts.fragment), pages[target].ids, (name, link))
            for record in reader.images.values():
                source = ROOT / record['source'].replace('.pdf', '.png')
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), record['sha256'])


if __name__ == '__main__':
    unittest.main()
