import json,subprocess,unittest
from fractions import Fraction as F
from pathlib import Path
from sequence_hankel_orders import classify,normalized_terms
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'verification/sequence-library/hankel-compression'
COEFFICIENTS=json.loads((AREA/'interior-coefficients.json').read_text())['first_eight_with_unit']

class InteriorOrderTests(unittest.TestCase):
    def test_saved_exact_gf_orders_and_defining_terms(self):
        for row in json.loads((AREA/'interior-replay.json').read_text())['samples']['cases']:
            result=classify(row['t'],row['q'],COEFFICIENTS)
            self.assertEqual(result['order'],row['order'],row['label'])
            self.assertEqual(result['root_type'],row['root_type'])
            self.assertEqual(list(map(str,normalized_terms(row['t'],row['q'],8))),row['first_eight'])

    def test_boundary_and_invalid_term_requests_are_explicit(self):
        for t,q in [(0,1),(1,0)]:
            with self.assertRaises(ValueError):classify(t,q,COEFFICIENTS)
        with self.assertRaises(ValueError):normalized_terms(1,0)
        for count in [-1,114]:
            with self.assertRaises(ValueError):normalized_terms(1,1,count)

    def test_browser_and_python_agree_across_signed_fractional_parameters(self):
        ts=['-2','-1','1/3','2/3','1','4/3','2','3/2','10/9','2/15']
        qs=['-144','-36','-400/9','-16/9','-1','1/54','1/4','1','8/3','4']
        cases=[{'t':t,'q':q} for t in ts for q in qs]
        cases += [{'t':'123456789012345678901/999999999999999999989','q':'987654321098765432101/888888888888888888887'}]
        result=subprocess.run(['node','tools/test_sequence_hankel_orders.mjs','--bridge'],
            input=json.dumps(cases),capture_output=True,text=True,cwd=ROOT,timeout=90)
        self.assertEqual(result.returncode,0,result.stderr)
        actual=json.loads(result.stdout);self.assertEqual(len(actual),len(cases))
        for case,browser in zip(cases,actual):
            expected=classify(case['t'],case['q'],COEFFICIENTS)
            for key,value in browser.items():
                if key!='terms':self.assertEqual(value,expected[key],(case,key))
            self.assertEqual(browser['terms'],list(map(str,normalized_terms(case['t'],case['q'],8))))

if __name__=='__main__':unittest.main()
