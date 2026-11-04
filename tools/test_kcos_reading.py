"""Preserve the complete source-bound K-COS volume in its reading edition."""
from collections import Counter
import csv
from decimal import Decimal
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import tempfile
from types import SimpleNamespace
import unittest

import kcos_reading as kcos
from kcos_routes import REQUIRED_LABELS, WORKED_EXAMPLE, calculation_navigation, label_targets
from readable_chapters import expand_math, original_math, render_book
from reader_documents import ReadingDocuments
from check_reader_site import Page
from reader_proofreading import prepare as prepare_proofreading, publish as publish_proofreading

ROOT = Path(__file__).resolve().parents[1]


class MathText(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.depth, self.math = 0, []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.depth += 1
        elif 'arithmatex' in dict(attrs).get('class', '').split():
            self.depth = 1
            self.math.append('')

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.math[-1] += data


class CalculationControls(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, markup):
        super().__init__()
        self.stack, self.controls, self.active = [], [], None
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav' and 'data-kcos-calculation' in attrs:
            self.active = dict(attrs=attrs, parent=self.stack[-1],
                               depth=len(self.stack), links=[])
            self.controls.append(self.active)
        if tag == 'a' and self.active is not None:
            self.active['links'].append(attrs)
        if tag not in self.VOID:
            self.stack.append((tag, attrs.get('id')))

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        if tag == 'nav' and self.active is not None and len(self.stack) == self.active['depth']:
            self.active = None


class KcosReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        registry = json.loads((ROOT / 'manifests/browse-resources.json').read_bytes())
        registry['components'] = [c for c in registry['components'] if c['id'] == kcos.WORK]
        site = SimpleNamespace(root=ROOT, output=cls.output, registry=registry, revision='kcos-proofread-test',
                               claims={'works': [], 'records': [], 'sources': []}, search=[])
        def write(path, text):
            target = cls.output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
        def read_source(record):
            raw = (ROOT / record['repository_path']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != record['sha256']:
                raise ValueError('Test source differs from its receipt: ' + record['repository_path'])
            return raw
        site.write, site.read_source = write, read_source
        site.rel = lambda target, page: posixpath.relpath(target, posixpath.dirname(page))
        site.page = lambda path, title, body: write(path, '<!doctype html><html lang="en"><title>' + title + '</title><main>' + body + '</main></html>')
        cls.reader = ReadingDocuments(site)
        cls.book = kcos.prepare_book(cls.reader, dict(kcos.BOOK))
        cls.reader.readable_books = {kcos.WORK: cls.book}
        prepare_proofreading(cls.reader)
        cls.reports = render_book(cls.reader, cls.book)
        publish_proofreading(cls.reader)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_whole_book_assembly_and_source_provenance(self):
        load = lambda path: (ROOT / path).read_text(encoding='utf-8-sig')
        self.assertEqual(kcos.source_specs(load), kcos.CHAPTERS)
        self.assertEqual(len(self.reports), 24)
        self.assertEqual(Counter(s['kind'] for s in kcos.CHAPTERS),
                         {'frontmatter': 3, 'part': 4, 'chapter': 16, 'bibliography': 1})
        self.assertEqual([s['printed_chapter'] for s in kcos.CHAPTERS if s['kind'] == 'chapter'],
                         [str(i) for i in range(1, 13)] + list('ABCD'))
        self.assertEqual(len({s['url'] for s in kcos.CHAPTERS}), 24)
        self.assertEqual(sum(s['url'] == kcos.BIB_PAGE for s in kcos.CHAPTERS), 1)
        self.assertEqual(len(self.book['references']), 7)
        self.assertEqual(len(self.book['included_sources']), 3)
        for report in self.reports:
            self.assertEqual(report['source_sha256'], hashlib.sha256((ROOT / report['source']).read_bytes()).hexdigest())
            self.assertEqual(report['macro_source'], kcos.STYLE)
            for node in report['nodes']:
                for span in node['source_spans']:
                    self.assertIn(span['source'], self.reader.records)
                    self.assertLessEqual(1, span['line'])
                    self.assertLessEqual(span['line'], span['end_line'])
                    self.assertLessEqual(span['end_line'], len(load(span['source']).splitlines()))
        changed = load(kcos.MAIN).replace(r'\input{chapters/04_range}', '')
        with self.assertRaisesRegex(ValueError, 'input order'):
            kcos.source_specs(lambda path: changed if path == kcos.MAIN else load(path))

    def test_every_rendered_expression_matches_its_retained_source(self):
        self.assertEqual(sum(r['math_expressions'] for r in self.reports), 1443)
        for spec, raw, chapter in self.book['chapters']:
            expected = kcos.source_math(raw.decode('utf-8-sig'), spec, self.book['source_texts'])
            markup = (self.output / spec['url']).read_text(encoding='utf-8')
            self.assertEqual([m[2:-2] for m in MathText(markup).math],
                             [expand_math(m, chapter.macros) for m in expected], spec['title'])
            page = Page(markup)
            self.assertEqual(len(page.ids), len(set(page.ids)), spec['title'])
        # The included numerical result must participate in the source check.
        spec = next(s for s in kcos.CHAPTERS if s.get('printed_chapter') == '9')
        source = self.book['source_texts'][spec['source']]
        changed = dict(self.book['source_texts'])
        included = kcos.BASE + 'worked_enclosure_result.tex'
        changed[included] = changed[included].replace('16384', '16385')
        self.assertNotEqual(kcos.source_math(source, spec, changed),
                            kcos.source_math(source, spec, self.book['source_texts']))

    def test_all_authored_statements_proofs_and_printed_numbers_survive(self):
        expected = {'theorem': 35, 'corollary': 12, 'proposition': 6,
                    'lemma': 2, 'remark': 5, 'algorithm': 1, 'proof': 39}
        counts = Counter(node['kind'] for _, _, chapter in self.book['chapters'] for node in chapter.nodes)
        self.assertEqual({kind: counts[kind] for kind in expected}, expected)
        self.assertEqual(sum(len(c.proof_pairs) for _, _, c in self.book['chapters']), 39)
        environments = '|'.join(kind for kind in expected if kind != 'proof')
        for spec, raw, chapter in self.book['chapters']:
            printed = spec.get('printed_chapter')
            source_kinds = re.findall(r'\\begin\{(' + environments + r')\}', raw.decode('utf-8-sig'))
            rendered = [n for n in chapter.nodes if n['kind'] in expected and n['kind'] != 'proof']
            self.assertEqual([n['kind'] for n in rendered], source_kinds)
            self.assertEqual([n['number'] for n in rendered],
                             [str(printed) + '.' + str(i) for i in range(1, len(source_kinds) + 1)])
        labels = self.book['chapters'][0][2].labels
        self.assertEqual(len(labels), 191)
        for key, number in self.book['chapters'][0][2].equation_numbers.items():
            self.assertEqual(labels[key]['equation_number'], number)
        self.assertEqual(labels['sec:gaussian-core']['reference_label'], '1')
        self.assertEqual(labels['sec:packets']['reference_label'], '6')
        self.assertEqual(labels['sec:final-5']['reference_label'], '10')
        # Printed equation counters restart by chapter; eqref adds parentheses.
        self.assertEqual(labels['eq:worked-exact-tail']['equation_number'], '1.1')
        self.assertEqual(labels['eq:Q']['equation_number'], '6.1')
        self.assertEqual(labels['eq:cgf']['equation_number'], '6.2')
        self.assertEqual(labels['eq:packet-expansion']['equation_number'], '6.10')
        self.assertEqual(labels['eq:J-def']['equation_number'], '7.1')
        packets = next(s for s in kcos.CHAPTERS if s.get('printed_chapter') == '6')
        markup = (self.output / packets['url']).read_text()
        self.assertIn('>(6.2)</a>', markup)
        self.assertIn('>(6.10)</a>', markup)

    def test_all_original_figures_and_visual_study_captions_survive(self):
        self.assertEqual(len(self.reader.images), 50)
        source_figures, rendered_figures = [], []
        for spec, raw, chapter in self.book['chapters']:
            source_figures.extend(re.findall(r'\\includegraphics\[[^\]]*\]\{([^{}]+)\}', raw.decode('utf-8-sig')))
            figures = [n for n in chapter.nodes if n['kind'] == 'figure']
            rendered_figures.extend(re.findall(r'\\includegraphics\[[^\]]*\]\{([^{}]+)\}', '\n'.join(n['body'] for n in figures)))
            if spec.get('printed_chapter') == 'A':
                self.assertEqual(len(figures), 17)
                self.assertTrue(all(n['number'] == '' for n in figures))
                self.assertTrue(all(n['alt'] for n in figures))
                markup = (self.output / spec['url']).read_text()
                self.assertIn('Their matching points use distinct markers.', markup)
                self.assertIn('All block Gram contributions use the same color scale.', markup)
            elif figures:
                self.assertEqual([n['number'] for n in figures],
                                 [spec['printed_chapter'] + '.' + str(i) for i in range(1, len(figures) + 1)])
        self.assertEqual(len(source_figures), 50)
        self.assertEqual(rendered_figures, source_figures)

    def test_printed_table_numbers_appear_in_their_authored_captions(self):
        # These seven numbers are printed in the retained monograph PDF.
        expected = {'2': ['2.1'], '5': ['5.1'],
                    '11': ['11.1', '11.2', '11.3', '11.4', '11.5']}
        for spec, _, _ in self.book['chapters']:
            markup = (self.output / spec['url']).read_text()
            numbers = re.findall(r'<caption>Table ([0-9]+\.[0-9]+)\. ', markup)
            self.assertEqual(numbers, expected.get(spec.get('printed_chapter'), []), spec['title'])
            self.assertEqual(markup.count('<caption>'), len(numbers),
                             'Uncaptioned source tables must remain unnumbered')

    def test_calculation_routes_follow_source_labels_and_complete_section_boundaries(self):
        source_labels = self.book['chapters'][0][2].labels
        targets = {name: source_labels[name]['url']+'#'+source_labels[name]['id']
                   for name in REQUIRED_LABELS}
        self.assertEqual(label_targets(self.book), targets)
        # These boundaries bracket the complete retained examples, including
        # their figures, imported enclosure result, and closing qualifications.
        boundaries = [('L329', None), ('L421', None),
                      ('L200', 'L203'), ('L216', 'L218')]
        for position, ((label, _, _), (last, following)) in enumerate(zip(WORKED_EXAMPLE, boundaries)):
            page, _ = targets[label].split('#')
            markup = (self.output / page).read_text()
            controls = CalculationControls(markup).controls
            self.assertEqual(len(controls), 1)
            control = controls[0]
            self.assertEqual(control['parent'], ('article', 'chapter-text'))
            self.assertEqual(control['attrs']['data-kcos-calculation'], label)
            self.assertEqual(control['attrs']['aria-label'],
                             'Worked calculation, step '+str(position+1)+' of 4')
            expected = []
            if position:
                expected.append(targets[WORKED_EXAMPLE[position-1][0]])
            expected.append(kcos.INDEX+'#kcos-worked-example')
            if position+1 < len(WORKED_EXAMPLE):
                expected.append(targets[WORKED_EXAMPLE[position+1][0]])
            self.assertEqual([a['href'] for a in control['links']],
                             [self.reader.site.rel(url, page) for url in expected])
            marker = markup.index('data-kcos-calculation="'+label+'"')
            start = markup.rfind('<nav ', 0, marker)
            end = markup.index('</nav>', marker)+len('</nav>')
            self.assertGreater(start, markup.index('id="'+last+'"'))
            self.assertTrue(markup[:start].endswith('</section>'))
            if following:
                self.assertLess(end, markup.index('id="'+following+'"'))
            else:
                self.assertTrue(markup[end:].startswith('</article>'))
            self.assertEqual(markup.count('data-reading-placement="top"'), 1)
            self.assertEqual(markup.count('data-reading-placement="bottom"'), 1)
        self.assertEqual(sum(len(CalculationControls((self.output / spec['url']).read_text()).controls)
                             for spec, _, _ in self.book['chapters']), 4)

    def test_calculation_routes_fail_closed_on_missing_ambiguous_or_nonsection_labels(self):
        def copied_book():
            return {**self.book, 'chapters': [
                (dict(spec), raw, SimpleNamespace(nodes=[{**node, 'labels': list(node['labels'])}
                                                         for node in chapter.nodes]))
                for spec, raw, chapter in self.book['chapters']]}
        def owner(book, label):
            return next(node for _, _, chapter in book['chapters'] for node in chapter.nodes
                        if label in node['labels'])
        book = copied_book()
        owner(book, 'sec:worked-tilt')['labels'].remove('sec:worked-tilt')
        with self.assertRaisesRegex(ValueError, 'Missing K-COS reading-path labels'):
            calculation_navigation(self.reader, book)
        book = copied_book()
        owner(book, 'sec:worked-law')['labels'].append('sec:worked-stream')
        with self.assertRaisesRegex(ValueError, 'Duplicate K-COS reading-path label'):
            label_targets(book)
        book = copied_book()
        owner(book, 'sec:worked-tilt')['kind'] = 'text'
        with self.assertRaisesRegex(ValueError, 'section heading'):
            calculation_navigation(self.reader, book)

    def test_reading_notes_are_bound_to_the_reviewed_sources_and_evidence(self):
        from reader_guidance import reading_passage_url
        record = json.loads((ROOT / 'manifests/reader-proofreading-kcos-2026-11-03.json').read_bytes())
        self.assertEqual(len(record['notes']), 4)
        self.assertEqual(record['mathematical_token_changes'], [])
        for note in record['notes']:
            markup = (self.output / note['page']).read_text()
            self.assertEqual(markup.count('data-proofreading-note="' + note['id'] + '"'), 1)
            self.assertIn('id="' + note['placement'] + '"', markup)
            for reference in note['references']:
                self.assertEqual(reading_passage_url(self.reader, reference['path'], reference['line']),
                                 reference['target'])
                target_page, anchor = reference['target'].split('#')
                self.assertIn(anchor, Page((self.output / target_page).read_text()).ids)
        for evidence in record['retained_evidence']:
            raw = (ROOT / evidence['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), evidence['sha256'])
            lines = raw.decode().splitlines()
            for row in evidence['lines']:
                self.assertEqual(lines[row['line'] - 1], row['expected'])
            full_range = [row for row in csv.DictReader(lines) if row['variant_basis_dim'] == '50']
            self.assertEqual(len(full_range), 2)
            for row in full_range:
                self.assertLess(Decimal(row['lower_log10_p']), Decimal(row['upper_log10_p']))
                self.assertEqual(format(Decimal(row['bracket_width_decades']), '.3g'), '9.50e-14')

    def test_parent_and_included_source_lookups_do_not_share_line_numbers(self):
        from reader_guidance import reading_passage_url
        self.assertEqual(reading_passage_url(self.reader, kcos.BASE + 'chapters/C_reproduction.tex', 24),
                         'read/monographs-cos-method/c-reproduction.html#L11')
        checked = 0
        for spec, _, chapter in self.book['chapters']:
            for node in chapter.nodes:
                for span in node['source_spans']:
                    # A source line can sit on two adjacent passage boundaries.
                    # Whichever passage wins must actually contain that file/line.
                    for line in {span['line'], span['end_line']}:
                        target = reading_passage_url(self.reader, span['source'], line)
                        self.assertIsNotNone(target, (span, line))
                        page, anchor = target.split('#')
                        destination = next(n for s, _, c in self.book['chapters'] if s['url'] == page
                                           for n in c.nodes if n['id'] == anchor)
                        self.assertTrue(any(s['source'] == span['source'] and s['line'] <= line <= s['end_line']
                                            for s in destination['source_spans']), (span, line, target))
                        checked += 1
        self.assertGreater(checked, 500)

    def test_included_data_formal_limits_and_literal_code_are_readable(self):
        by_number = {s.get('printed_chapter'): (s, c) for s, _, c in self.book['chapters'] if s.get('printed_chapter')}
        for number, filename in [('6', 'worked_packet_table.tex'), ('9', 'worked_enclosure_result.tex'), ('C', 'replay_results.tex')]:
            spec, chapter = by_number[number]
            self.assertTrue(any(span['source'] == kcos.BASE + filename
                                for n in chapter.nodes for span in n['source_spans']))
            self.assertNotIn(r'\input{', chapter.text)
            self.assertIn(filename, (self.output / spec['url']).read_text())
        evidence = (self.output / by_number['11'][0]['url']).read_text()
        self.assertIn('<code>np.empty</code>', evidence)
        self.assertIn('<code>+=</code>', evidence)
        formal = (self.output / by_number['B'][0]['url']).read_text()
        self.assertIn('The source does not directly instantiate this rule with the real logarithm', formal)
        self.assertIn('enclosed_monotone', formal)
        for spec, raw, chapter in self.book['chapters']:
            source_listings = re.findall(r'\\begin\{(?:lstlisting|verbatim)\}(?:\[[^\]\n]*\])?(.*?)\\end\{(?:lstlisting|verbatim)\}', raw.decode(), re.S)
            output_listings = [n['body'] for n in chapter.nodes if n['kind'] in {'lstlisting', 'verbatim'}]
            self.assertEqual(output_listings, source_listings, spec['title'])


if __name__ == '__main__':
    unittest.main()
