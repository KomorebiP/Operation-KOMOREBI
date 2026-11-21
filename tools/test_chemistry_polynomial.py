import hashlib,io,json,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock
from chemistry_polynomial_data import AREA,DATA,payload,replay
from chemistry_responses import build
from test_computational_chemistry import fixture_site
ROOT=Path(__file__).resolve().parents[1]
class PolynomialTests(unittest.TestCase):
    def test_fresh_study_reproduces_saved_bytes(self):
        self.assertEqual((ROOT/DATA).read_bytes(),payload())
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'fresh';subprocess.run([sys.executable,'-B',str(ROOT/AREA/'polynomial_study.py'),'--output',str(out)],cwd=ROOT,check=True,capture_output=True)
            self.assertEqual((out/'polynomial.json').read_bytes(),payload())
    def test_replay_is_portable_and_complete(self):
        raw=replay()
        with mock.patch('zipfile.sys.platform','linux'):self.assertEqual(replay(),raw)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for x in json.loads(z.read('PACKAGE.json'))['files']:
                b=z.read(x['path']);self.assertEqual(len(b),x['bytes']);self.assertEqual(hashlib.sha256(b).hexdigest(),x['sha256'])
            for name in ['stage16/verify_stage16.py','stage17/verify_stage17.py','stage18/verify_stage18.py']:
                self.assertIn('research/computational-chemistry/'+name,z.namelist())
    def test_reader_keeps_linear_planning_and_adds_qualified_polynomial_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            site=fixture_site(Path(temp));result=build(site);self.assertEqual(result['polynomial']['cells'],1005)
            text=(site.output/'chemistry-responses.html').read_text(encoding='utf-8')
            for s in ['id="cc-method"','id="bp-poly-alternative"','using linear cell bounds','not a minimum-node polynomial plan','zero new endpoint evaluations','cr-polynomial']:self.assertIn(s,text)
            self.assertEqual((site.output/'assets/chemistry/polynomial-v1.json').read_bytes(),payload())
            note=(site.output/'read/computational-chemistry/polynomial-responses.html').read_text(encoding='utf-8');self.assertIn('Negative Lagrange weights',note);self.assertIn('project self-review',note)
            for boot in ['chemistry-continuous.js','chemistry-budget.js']:self.assertIn('chemistry-polynomial-core.mjs?v=',(site.output/'assets'/boot).read_text())
            expected={'stage16':'9af873a8d9b409720279a0e2a792e616d8cdaeb3fde98c58022ab4bc80fcae14','stage17':'4cf026fffd7fe15a55b42115655dca472261daca7c4bbcfab05abe1c52f054c8'}
            for stage,digest in expected.items():self.assertEqual(hashlib.sha256((site.output/'assets/chemistry'/f'{stage}-replay.zip').read_bytes()).hexdigest(),digest)
if __name__=='__main__':unittest.main()
