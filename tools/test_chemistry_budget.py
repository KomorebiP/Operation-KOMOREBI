import hashlib,io,json,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest import mock
from chemistry_budget_data import DATA,AREA,payload,replay
from chemistry_responses import build
from test_computational_chemistry import fixture_site
ROOT=Path(__file__).resolve().parents[1]
class BudgetTests(unittest.TestCase):
    def test_frontiers_reproduce_from_the_recorded_endpoint_data(self):
        self.assertEqual((ROOT/DATA).read_bytes(),payload())
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'fresh'
            subprocess.run([sys.executable,'-B',str(ROOT/AREA/'budget_study.py'),'--output',str(out)],cwd=ROOT,check=True,capture_output=True)
            self.assertEqual((out/'frontiers.json').read_bytes(),payload())
    def test_complete_replay_is_portable_and_hash_bound(self):
        raw=replay()
        with mock.patch('zipfile.sys.platform','linux'):self.assertEqual(replay(),raw)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            self.assertEqual(len(z.namelist()),len(set(z.namelist())))
            for x in json.loads(z.read('PACKAGE.json'))['files']:self.assertEqual(hashlib.sha256(z.read(x['path'])).hexdigest(),x['sha256'])
            self.assertIn('website/assets/chemistry/continuous-v1.json',z.namelist())
            self.assertIn((AREA/'PRECISION_PLANNER.md').as_posix(),z.namelist())
    def test_static_plans_and_proof_preserve_the_predecessor_experiments(self):
        with tempfile.TemporaryDirectory() as temp:
            site=fixture_site(Path(temp));result=build(site);self.assertEqual(result['planner']['frontier_rows'],717)
            text=(site.output/'chemistry-responses.html').read_text(encoding='utf-8')
            for item in ['id="cr-plan"','id="cr-continuous"','id="cr-explorer"','32 actions and 14 energies','zero new Hamiltonian actions','Download this scan plan','not measured runtime optima']:self.assertIn(item,text)
            self.assertEqual((site.output/'assets/chemistry/planner-v1.json').read_bytes(),payload())
            note=(site.output/'read/computational-chemistry/precision-planning.html').read_text(encoding='utf-8');self.assertIn('unique penultimate node',note);self.assertIn('project self-review',note)
            core=(site.output/'assets/chemistry-budget-core.mjs').read_text();self.assertIn('chemistry-lab-core.mjs?v=',core);self.assertIn('chemistry-continuous-core.mjs?v=',core)
if __name__=='__main__':unittest.main()
