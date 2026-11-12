"""Source fidelity and failure checks for the archived Smith chart reading."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import smith_chart_research as research
import smith_chart_edition as edition

ROOT = Path(__file__).resolve().parents[1]
REVISION = 'a' * 40


def manuscript_text(source):
    class Extractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.inside = False
            self.parts = []
        def handle_starttag(self, tag, attrs):
            if tag == 'article' and dict(attrs).get('id') == 'manuscript':
                self.inside = True
        def handle_endtag(self, tag):
            if tag == 'article' and self.inside:
                self.inside = False
        def handle_data(self, data):
            if self.inside:
                self.parts.append(data)
    parser = Extractor()
    parser.feed(source)
    return ''.join(parser.parts)


class ResearchReadingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = research.archive_contents(ROOT)
        cls.original = cls.files[research.HTML_NAME].decode('utf-8').split('<main class="page">', 1)[1].split('</main>', 1)[0]
        _, cls.prose = edition.load(ROOT, cls.files, research.HTML_NAME)
        cls.edited = edition.edit_prose(cls.files[research.HTML_NAME].decode('utf-8'), cls.prose).split('<main class="page">', 1)[1].split('</main>', 1)[0]
        cls.rendered = research.reading_body(ROOT, REVISION)

    def test_mathematical_text_figures_and_tables_survive(self):
        plain = re.sub(r'<div class="figure-heading">.*?</div>', '', self.rendered, flags=re.S)
        plain = re.sub(r'<aside class="research-update".*?</aside>', '', plain, flags=re.S)
        self.assertEqual(manuscript_text(self.edited), manuscript_text(plain))
        original_math = re.findall(r'<span class="math (?:inline|display)">.*?</span>', self.original, re.S)
        rendered_math = re.findall(r'<span class="math (?:inline|display) arithmatex">.*?</span>', self.rendered, re.S)
        self.assertEqual(len(original_math), 1668)
        self.assertEqual(original_math, [item.replace(' arithmatex"', '"', 1) for item in rendered_math])
        for tag in ('h1', 'h2', 'h3', 'figcaption', 'table'):
            original = re.findall(r'<'+tag+r'\b[^>]*>.*?</'+tag+r'>', self.edited, re.S)
            rendered = re.findall(r'<'+tag+r'\b[^>]*>.*?</'+tag+r'>', self.rendered, re.S)
            # Tables and captions include math spans, whose only change is their renderer class.
            self.assertEqual(original, [x.replace(' arithmatex"', '"') for x in rendered], tag)
        self.assertEqual(self.rendered.count('class="research-figure"'), 42)
        self.assertEqual(len(re.findall(r'<table\b', self.rendered)), 23)
        self.assertNotIn('="data:', self.rendered)

    def test_every_internal_route_resolves(self):
        ids = set(re.findall(r'\bid="([^"]+)"', self.rendered))
        targets = re.findall(r'\bhref="#([^"]+)"', self.rendered)
        self.assertFalse(set(targets) - ids)
        self.assertIn('seven-reactive-exact', ids)
        self.assertIn('arbitrary-order-separation', ids)
        self.assertIn('verification-register-and-reproducible-records', ids)
        self.assertIn('class="research-contents-jump" href="#contents"', self.rendered)
        self.assertIn('aria-label="Expanded figure; scroll to explore at full resolution"', self.rendered)
        self.assertIn('SMITH_FIRST_ORDER_RL.html', self.rendered)

    def test_source_links_are_revision_bound_and_claim_scope_is_visible(self):
        links = re.findall(r'(?:src|href)="(https://raw\.githubusercontent\.com/[^"]+)"', self.rendered)
        self.assertEqual(len(links), 87)  # 42 vector figures, 42 original figures, three downloads
        self.assertTrue(all('/'+REVISION+'/' in link for link in links))
        self.assertIn(research.ARCHIVE_SHA256, self.rendered)
        self.assertIn('six-reactive realization using an ideal transformer', self.rendered)
        self.assertIn('The six-reactive gap is closed.', self.rendered)
        self.assertIn('Earlier open-status statements below are retained as history.', self.rendered)
        self.assertIn('href="continuation.html"', self.rendered)
        self.assertIn('not this entire draft', self.rendered)
        self.assertEqual(self.rendered.count('class="figure-heading"'),42)
        self.assertEqual(len(re.findall(r'src="[^"]+/edition/figures/[^"]+\.svg"',self.rendered)),42)
        with self.assertRaises(ValueError):
            research.reading_body(ROOT, 'main')

    def test_tampered_figure_and_archive_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT/'research/smith-chart', root/'research/smith-chart')
            figure = next((root/'research/smith-chart/figures').glob('*'))
            figure.write_bytes(figure.read_bytes()+b'tampered')
            with self.assertRaisesRegex(ValueError, 'Published source differs'):
                research.archive_contents(root)
            shutil.copy2(ROOT/'research/smith-chart'/figure.relative_to(root/'research/smith-chart'), figure)
            archive = root/research.ARCHIVE
            archive.write_bytes(archive.read_bytes()+b'tampered')
            with self.assertRaisesRegex(ValueError, 'archive checksum mismatch'):
                research.archive_contents(root)

    def test_vector_and_editorial_bindings_fail_closed(self):
        self.assertEqual(len(self.prose['edits']),54)
        self.assertEqual(sum(c['expected_count'] for c in self.prose['edits']),92)
        with self.assertRaisesRegex(ValueError,'Editorial fragment changed'):
            edition.edit_prose('unrelated source',self.prose)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            shutil.copytree(ROOT/'research/smith-chart',root/'research/smith-chart')
            extra=root/'docs/demonstrations/figures/smith-two-packet-feasibility.svg'
            extra.parent.mkdir(parents=True)
            shutil.copyfile(ROOT/'docs/demonstrations/figures/smith-two-packet-feasibility.svg',extra)
            target=next((root/'research/smith-chart/edition/figures').glob('*.svg'))
            target.write_bytes(target.read_bytes()+b'tampered')
            with self.assertRaisesRegex(ValueError,'Vector edition source or output checksum mismatch'):
                edition.load(root,self.files,research.HTML_NAME)
            shutil.copyfile(ROOT/'research/smith-chart/edition/figures'/target.name,target)
            helper=root/'research/smith-chart/edition/diagram_redesign.py'
            helper.write_bytes(helper.read_bytes()+b'\n# changed renderer\n')
            with self.assertRaisesRegex(ValueError,'Diagram generator differs'):
                edition.load(root,self.files,research.HTML_NAME)

    def test_new_completion_formal_receipt(self):
        base=ROOT/'research/smith-chart/completion-formal'
        evidence=base/'verification/run04'
        receipt=json.loads((evidence/'receipt.json').read_bytes())
        self.assertEqual(receipt['status'],'PASS')
        for name in ('SmithCompletion.lean','AxiomAudit.lean','replay.py'):
            self.assertEqual(hashlib.sha256((base/name).read_bytes()).hexdigest(),receipt['input_sha256'][name])
        self.assertEqual(hashlib.sha256((ROOT/'docs/demonstrations/SMITH_SINGULAR_COMPLETION.md').read_bytes()).hexdigest(),receipt['input_sha256']['SMITH_SINGULAR_COMPLETION.md'])
        self.assertEqual(len(receipt['audited_axioms']),6)
        self.assertEqual([s['exit_code'] for s in receipt['steps']],[0,0,1,1])
        for values in receipt['audited_axioms'].values():
            self.assertLessEqual(set(values),{'propext','Classical.choice','Quot.sound'})
        for step in receipt['steps']:
            for stream in ('stdout','stderr'):
                self.assertEqual(hashlib.sha256((evidence/(step['name']+'.'+stream+'.txt')).read_bytes()).hexdigest(),step[stream+'_sha256'])

    def test_new_exact_computation_manifests(self):
        base=ROOT/'research/smith-chart/computations/verification'
        for name in ('completion-boundary-003','candidate-142-system-001','diagram-labels-002'):
            record=json.loads((base/name/'manifest.json').read_bytes())
            self.assertEqual(record['run']['status'],'completed')
            for item in record['input_artifacts']:
                actual=hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()
                self.assertEqual(actual,item['sha256'])
                self.assertEqual(actual,item['sha256_after'])
            for item in record['outputs']:
                self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),item['sha256'])

    def test_formal_receipt_matches_the_recorded_inputs_and_logs(self):
        base = ROOT/'research/smith-chart/formal'
        evidence = base/'verification/run03'
        receipt = json.loads((evidence/'receipt.json').read_bytes())
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(receipt['source_binding']['archive_sha256'], research.ARCHIVE_SHA256)
        for name in ('SmithFirstOrderRL.lean', 'AxiomAudit.lean', 'replay.py'):
            self.assertEqual(hashlib.sha256((base/name).read_bytes()).hexdigest(), receipt['input_sha256'][name])
        lock = ROOT/'formal/smith-chart-v0.1.0/dependency-lock.json'
        self.assertEqual(hashlib.sha256(lock.read_bytes()).hexdigest(), receipt['input_sha256']['dependency-lock.json'])
        self.assertEqual(len(receipt['audited_axioms']), 9)
        for axioms in receipt['audited_axioms'].values():
            self.assertLessEqual(set(axioms), {'propext', 'Classical.choice', 'Quot.sound'})
        self.assertEqual([step['exit_code'] for step in receipt['steps']], [0, 0, 1, 1])
        for step in receipt['steps']:
            for stream in ('stdout', 'stderr'):
                data = (evidence/(step['name']+'.'+stream+'.txt')).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), step[stream+'_sha256'])
        exact = json.loads((base/'verification/rational-check.json').read_bytes())
        self.assertEqual(exact['status'], 'PASS')
        self.assertEqual(exact['operating_points'], 3924)
        self.assertEqual(exact['script_sha256'], hashlib.sha256((base/'check_exact.py').read_bytes()).hexdigest())

    def test_earlier_formal_receipt_still_matches_its_proof_files(self):
        base = ROOT/'formal/smith-chart-v0.1.0'
        receipt = json.loads((base/'verification/run15/receipt.json').read_bytes())
        for name, expected in receipt['input_sha256_before'].items():
            if name.endswith('.lean') or name in {'replay.py', 'dependency-lock.json', 'source-bindings.json', 'lean-toolchain'}:
                self.assertEqual(hashlib.sha256((base/name).read_bytes()).hexdigest(), expected, name)

    def test_finite_topology_and_exact_candidate_checks(self):
        base = ROOT/'research/smith-chart/computations'
        for script, check, receipt_name in [('check_five_node_orbits.py', 'orbit_classes', 'five-node-002.json'),
                                             ('check_saved_candidate.py', 'results', 'candidate-142-exact-001.json')]:
            result = subprocess.run([sys.executable, '-B', str(base/script)], capture_output=True, check=True)
            record = json.loads(result.stdout)
            receipt = json.loads((base/'verification'/receipt_name).read_bytes())
            self.assertEqual(record['status'], 'PASS')
            self.assertEqual(record['script_sha256'], hashlib.sha256((base/script).read_bytes()).hexdigest())
            self.assertEqual(record['script_sha256'], receipt['script_sha256'])
            self.assertEqual(record[check] if check == 'orbit_classes' else len(record[check]), 168 if check == 'orbit_classes' else 3)
            if check == 'orbit_classes':
                self.assertEqual(record['orbit_size_histogram'], receipt['orbit_size_histogram'])
                self.assertEqual(record['classes_without_terminal_exchange'], 336)
            else:
                self.assertEqual([(x['s'], x['difference_numerator'], x['difference_denominator']) for x in record['results']],
                                 [(x['s'], x['difference_numerator'], x['difference_denominator']) for x in receipt['results']])


if __name__ == '__main__':
    unittest.main()
