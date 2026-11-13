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
            self.assertEqual(report['reading_pages'],7);self.assertFalse(report['new_scientific_execution'])
            self.assertEqual(len(site.search),9)
            overview=(site.output/chemistry.OVERVIEW).read_text(encoding='utf-8')
            self.assertIn('<title>Computational chemistry:',overview)
            self.assertIn('21 independent parameters',overview)
            self.assertIn('exactly three complete action',overview)
            self.assertIn('aria-label="Main navigation"',overview)
            self.assertIn('class="arithmatex"',overview)
            self.assertNotIn('language-math',overview)
            self.assertIn('../assets/chemistry/stage14/Stage14_Fixed_Spin_Recovery.zip',overview)
            self.assertIn('world priority', (site.output/'read/computational-chemistry/reproduce.html').read_text(encoding='utf-8'))
            physics=(site.output/'collection/PHYSICS_COLLECTION.html').read_text(encoding='utf-8')
            self.assertIn('href="COMPUTATIONAL_CHEMISTRY.html"',physics)
            for _,(name,_) in chemistry.PAGES.items():
                body=(site.output/'read/computational-chemistry'/name).read_text(encoding='utf-8')
                self.assertIn('../../collection/COMPUTATIONAL_CHEMISTRY.html',body)
                self.assertIn('Source identity and download',body)
                self.assertIn('/blob/'+'a'*40+'/',body)
                ids=set(re.findall(r'\bid="([^"]+)"',body))
                self.assertFalse(set(re.findall(r'href="#([^"]+)"',body))-ids)

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
