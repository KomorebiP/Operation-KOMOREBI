import copy, json, tempfile, unittest
from pathlib import Path
from repair_certificates import *

class ExactCertificateTests(unittest.TestCase):
    def setUp(self):
        self.p=problem(Mat.of([[1],[0],[0]]),Mat.of([[2,4],[1,2],[1,2]]))
        self.c=construct(self.p)
    def test_worked(self): self.assertEqual(self.c['t'],1)
    def test_original_equation(self): self.assertTrue(check_certificate(self.p,self.c)['original_equations'])
    def test_fractional(self):
        c=construct(problem(Mat.of([[F(2,3)],[F(4,3)]]),Mat.of([[F(1,2)],[F(5,6)]])))
        self.assertEqual(c['t'],1)
    def test_zero_target(self): self.assertEqual(construct(problem(Mat.zero(0,2),Mat.zero(0,3)))['t'],0)
    def test_zero_original(self): self.assertEqual(construct(problem(Mat.zero(2,0),Mat.eye(2)))['t'],2)
    def test_empty_residual_family(self): self.assertEqual(construct(problem(Mat.of([[1],[2]]),Mat.zero(2,0)))['t'],0)
    def test_zero_residual(self): self.assertEqual(construct(problem(Mat.of([[1],[2]]),Mat.zero(2,1)))['t'],0)
    def test_surjective(self): self.assertEqual(construct(problem(Mat.eye(2),Mat.of([[2],[3]])))['t'],0)
    def test_two_obstructions(self): self.assertEqual(construct(problem(Mat.zero(3,1),Mat.of([[1,0],[0,1],[0,0]])))['t'],2)
    def test_singular_inverse(self):
        with self.assertRaises(InvalidData): inverse(Mat.of([[1,2],[2,4]]))
    def test_matrix_roundtrip(self): self.assertEqual(Mat.from_wire(self.p['R']),parse_problem(self.p)[1])
    def test_digest_binding(self):
        c=copy.deepcopy(self.c);c['problem_sha256']='0'*64
        with self.assertRaises(InvalidData): check_certificate(self.p,c)
    def test_substituted_problem(self):
        p=copy.deepcopy(self.p);p['R']['entries'][0][0]=['3','1']
        with self.assertRaises(InvalidData): check_certificate(p,self.c)
    def test_corrupt_split(self):
        c=copy.deepcopy(self.c);c['matrices']['P']['entries'][0][0]=['2','1']
        with self.assertRaisesRegex(InvalidData,'complete_split'):check_certificate(self.p,c)
    def test_corrupt_factor(self):
        c=copy.deepcopy(self.c);c['matrices']['G']['entries'][0][0]=['2','1']
        with self.assertRaisesRegex(InvalidData,'residual_factorization'):check_certificate(self.p,c)
    def test_corrupt_lower(self):
        c=copy.deepcopy(self.c);c['matrices']['J']['entries'][0][0]=['2','1']
        with self.assertRaisesRegex(InvalidData,'rank_lower'):check_certificate(self.p,c)
    def test_corrupt_output(self):
        c=copy.deepcopy(self.c);c['matrices']['U']['entries'][0][0]=['0','1']
        with self.assertRaisesRegex(InvalidData,'returned_U'):check_certificate(self.p,c)
    def test_zero_denominator(self):
        with self.assertRaises(InvalidData): rational_pair(['1','0'])
    def test_negative_denominator(self):
        with self.assertRaises(InvalidData): rational_pair(['1','-2'])
    def test_unreduced(self):
        with self.assertRaises(InvalidData): rational_pair(['2','4'])
    def test_noncanonical_zero(self):
        with self.assertRaises(InvalidData): rational_pair(['-0','1'])
    def test_leading_zero(self):
        with self.assertRaises(InvalidData): rational_pair(['01','1'])
    def test_code_injection(self):
        with self.assertRaises(InvalidData): rational_pair(['0); axiom X:False','1'])
    def test_unsafe_namespace(self):
        with self.assertRaises(InvalidData):emit_input(self.p,'X\naxiom fake : False')
    def test_float(self):
        with self.assertRaises(InvalidData): Mat.of([[0.5]])
    def test_bool_dimension(self):
        with self.assertRaises(InvalidData):Mat.from_wire({'rows':True,'cols':0,'entries':[[]]})
    def test_shape(self):
        with self.assertRaises(InvalidData):Mat.from_wire({'rows':1,'cols':2,'entries':[[['1','1']]]})
    def test_extra_keys(self):
        c=copy.deepcopy(self.c);c['D']=self.p['D']
        with self.assertRaises(InvalidData):check_certificate(self.p,c)
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.json';p.write_text('{"x":1,"x":2}', encoding="utf-8")
            with self.assertRaises(InvalidData):read_json(p)
    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.json';p.write_text('{"x":NaN}', encoding="utf-8")
            with self.assertRaises(InvalidData):read_json(p)
    def test_float_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.json';p.write_text('{"x":1.0}', encoding="utf-8")
            with self.assertRaises(InvalidData):read_json(p)
    def test_invariants_actual_input(self):
        text=emit_certificate(self.p,self.c,'Test','FixedInput')
        self.assertNotIn('def D :',text);self.assertNotIn('def R :',text)
        self.assertIn('import FixedInput',text)
    def test_no_native_proof(self):
        text=emit_certificate(self.p,self.c,'Test','FixedInput')
        self.assertNotIn('native_decide',text);self.assertIn('decide +kernel',text)
    def test_zero_denom_decoder_scope(self):
        c=copy.deepcopy(self.c);c['matrices']['H']['entries'][0][0]=['0','0']
        with self.assertRaises(InvalidData):decode_certificate(self.p,c)

if __name__=='__main__':unittest.main(verbosity=2)
