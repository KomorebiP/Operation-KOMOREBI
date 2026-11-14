"""Check public source identity, response evidence and reader integration."""
from fractions import Fraction
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import tempfile
from types import SimpleNamespace
import unittest
import zipfile

import computational_chemistry as chemistry
from build_reader_site import Site

ROOT=Path(__file__).resolve().parents[1]


def fixture_site(output,revision='a'*40):
    site=object.__new__(Site);site.root=ROOT;site.output=output;site.revision=revision;site.search=[]
    site.documents={('collection','docs/'+name):(ROOT/'docs'/name).read_text(encoding='utf-8') for name in ['COMPUTATIONAL_CHEMISTRY.md','PHYSICS_COLLECTION.md']}
    site.roots={'collection':ROOT};site.repos={'collection':'KomorebiP/Operation-KOMOREBI','math':'KomorebiP/komorebi-math','polyphase':'KomorebiP/polyphase-float'}
    site.revisions={key:revision for key in site.repos}
    site.reader=SimpleNamespace(resolve=lambda *args:None,image_url=lambda *args:None,document_works=lambda *args:[],lean_works={})
    return site


class ChemistryCheckpointTests(unittest.TestCase):
    def test_export_covers_exactly_the_bound_members_and_retains_proof_scope(self):
        record,files=chemistry.load(ROOT)
        self.assertEqual(len(files),28)
        for name in ['NORMAL_FORM.md','RECOVERY_THEOREM.md','ROBUST_SPIN_COMPARISON.md']:
            self.assertIn('Komorebi P.',files['chemistry_stage14/'+name].decode())
        self.assertIn('not asserted sharp',files['chemistry_stage14/RECOVERY_THEOREM.md'].decode())
        self.assertIn('Originality, priority and publication significance remain',files['chemistry_stage14/LITERATURE.md'].decode())
        self.assertEqual(record['fixture_view']['original_container_sha256'],'e6a3540d254b54a77902bd13049f302eb6dec647088b086d3948a887d0da9166')

    def test_minimal_fixture_is_declared_as_a_different_container(self):
        record,files=chemistry.load(ROOT);view=record['fixture_view']
        self.assertNotEqual(view['view_container_sha256'],view['original_container_sha256'])
        with zipfile.ZipFile(BytesIO(files['chemistry_checkpoint/molecular_fixtures/h10_1.4.npz'])) as archive:
            self.assertEqual(set(archive.namelist()),{'h1.npy','eri.npy','ground_energy.npy'})
        self.assertEqual({x['name'] for x in view['retained_arrays']},{'h1','eri','ground_energy'})
        self.assertIn('source-container hash',files['README.md'].decode())
        self.assertFalse(any(b'C:\\Users\\' in raw or b'C:/Users/' in raw for raw in files.values()))

    def test_changed_archive_is_rejected_instead_of_relabelled(self):
        record,_=chemistry.load(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'manifests').mkdir();shutil.copyfile(ROOT/chemistry.MANIFEST,root/chemistry.MANIFEST)
            target=root/record['archive'];target.parent.mkdir(parents=True);raw=bytearray((ROOT/record['archive']).read_bytes());raw[100]^=1;target.write_bytes(raw)
            with self.assertRaisesRegex(ValueError,'identity mismatch'):chemistry.load(root)

    def test_reader_and_overview_have_shared_chrome_math_and_download_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            site=fixture_site(Path(directory));report=chemistry.publish(site);site.markdown_pages()
            self.assertEqual(report['reading_pages'],9);self.assertFalse(report['new_scientific_execution'])
            self.assertEqual(len(site.search),11)
            self.assertTrue(all(row['group']=='Collection' for row in site.search))
            proof_rows=[row for row in site.search if row.get('kind')=='Written proofs']
            self.assertEqual({Path(row['url']).name for row in proof_rows},{'normal-form.html','three-queries.html','spin-comparison.html','model-error.html'})
            overview=(site.output/chemistry.OVERVIEW).read_text(encoding='utf-8')
            self.assertIn('<title>Computational chemistry:',overview)
            self.assertIn('21 independent parameters',overview)
            self.assertIn('exactly three complete action',overview)
            self.assertIn('aria-label="Main navigation"',overview)
            self.assertIn('class="arithmatex"',overview)
            self.assertNotIn('language-math',overview)
            self.assertIn('../assets/chemistry/stage14/Stage14_Fixed_Spin_Recovery.zip',overview)
            self.assertIn('world-priority', (site.output/'read/computational-chemistry/reproduce.html').read_text(encoding='utf-8'))
            self.assertIn('../assets/chemistry/validation-v1/Stage14_Validated_Replay.zip',overview)
            physics=(site.output/'collection/PHYSICS_COLLECTION.html').read_text(encoding='utf-8')
            self.assertIn('href="COMPUTATIONAL_CHEMISTRY.html"',physics)
            for _,(name,_) in chemistry.PAGES.items():
                body=(site.output/'read/computational-chemistry'/name).read_text(encoding='utf-8')
                self.assertIn('../../collection/COMPUTATIONAL_CHEMISTRY.html',body)
                self.assertIn('Source identity and download',body)
                self.assertIn('Explore the chemistry notes',body)
                self.assertIn('chemistry-reading.css',body)
                self.assertEqual(body.count('aria-current="page"'),1)
                self.assertEqual(len(re.findall(r'<table\b',body)),body.count('<caption>'))
                self.assertEqual(len(re.findall(r'<th\b',body)),body.count('<th scope="col">'))
                self.assertEqual(len(re.findall(r'<h1\b',body)),1)
                self.assertIn('/blob/'+'a'*40+'/',body)
                ids=set(re.findall(r'\bid="([^"]+)"',body))
                self.assertFalse(set(re.findall(r'href="#([^"]+)"',body))-ids)

    def test_reading_edition_is_bound_to_both_current_and_original_sources(self):
        original,_=chemistry.load(ROOT);edition=chemistry.load_edition(ROOT,original)
        self.assertEqual(len(edition['pages']),9)
        self.assertEqual(sum(bool(x['original_member']) for x in edition['pages']),7)
        for page in edition['pages']:
            if page['original_member']:self.assertEqual(page['original_sha256'],original['files'][page['original_member']]['sha256'])
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'manifests').mkdir();shutil.copyfile(ROOT/chemistry.EDITION,root/chemistry.EDITION)
            for page in edition['pages']:
                target=root/page['source'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/page['source'],target)
            page=edition['pages'][0];(root/page['source']).write_text('Changed source')
            with self.assertRaisesRegex(ValueError,'source changed'):chemistry.load_edition(root,original)

    def test_new_validation_binds_actual_view_and_fresh_run_dependencies(self):
        record,files=chemistry.load_validation(ROOT)
        self.assertEqual(len(record['validation_runs']),3)
        self.assertIn('verify_public_replay.py',files)
        self.assertIn('reading-edition/model-error.md',files)
        self.assertEqual(json.loads(files['BUNDLE_CONTENTS.json'])['files'],sorted(files))
        for run in record['validation_runs']:
            manifest=json.loads(files[run+'/manifest.json'])
            self.assertEqual(manifest['command'][0],'python')
            self.assertEqual(manifest['run']['status'],'completed')
        extensions=json.loads(files['validation/extensions-001/checks.json'])
        self.assertEqual(extensions['aggregated_cases'],174)
        self.assertFalse(any(b'C:\\Users\\' in value or b'C:/Users/' in value for value in files.values()))
        current=(ROOT/'research/computational-chemistry/reading-edition/three-queries.md').read_text(encoding='utf-8')
        self.assertIn('the estimate itself is compatible',current)
        self.assertIn('not positive semidefinite',current)
        self.assertIn('finite\nconvex feasibility problem',current)

    def test_caption_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'caption coverage'):chemistry.caption_tables('<table></table>',[])

    def test_saved_rational_certificates_support_the_displayed_numerical_bounds(self):
        _,files=chemistry.load(ROOT)
        certificate=json.loads(files['chemistry_stage14/molecular-audit-001/molecular_certificate.json'])
        radius=Fraction(certificate['response_radius_rational_upper'])
        self.assertEqual(radius,Fraction(879641391875,9444732965739290427392))
        toy=json.loads(files['chemistry_stage14/exact-audit-001/example_certificate.json'])
        self.assertEqual(Fraction(toy['response_center']['real']),Fraction(-107,1157))
        self.assertEqual(Fraction(toy['response_center']['imaginary']),Fraction(-1146,1157))
        self.assertFalse(toy['operator_bound_is_sharp'])


if __name__=='__main__':unittest.main()
