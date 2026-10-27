"""Regression and adversarial tests. A rejected certificate is UNRESOLVED."""
import unittest, copy, tempfile, json
from pathlib import Path
from fractions import Fraction as F
import rational_menu as M
from repair_certificates import Mat, InvalidData, read_json

class MenuTests(unittest.TestCase):
    def setUp(self):
        self.D=Mat.of([[1],[0],[0]])
        self.E=Mat.of([[0,0],[1,0],[1,1]])
        self.R=Mat.of([[0],[1],[0]])
        self.p=M.problem(self.D,self.E,self.R,[1,1])
        self.c=M.construct(self.p)
    def test_original_optimum(self):
        self.assertEqual((self.c['selection'],self.c['cost']),(3,2))
        self.assertEqual(M.check_certificate(self.p,self.c)['required_rejections'],3)
    def test_compressed_blocks(self):self.assertEqual(len(self.c['blocks']),2)
    def test_restricted_menu_no_repair(self):
        p=M.problem(self.D,self.E,self.R,[1,1],[0,1,2]);c=M.construct(p)
        self.assertEqual(c['kind'],'no_admissible_repair');M.check_certificate(p,c)
    def test_full_separator_covers_all(self):
        p=M.problem(Mat.of([[1],[0]]),Mat.of([[2,3,4,5],[0,0,0,0]]),Mat.of([[0],[1]]),[1]*4)
        c=M.construct(p);self.assertEqual(len(c['blocks']),1)
        self.assertEqual(M.check_certificate(p,c)['required_rejections'],16)
    def test_cheaper_pair_than_singleton(self):
        E=Mat.of([[0,0,0],[1,1,0],[0,1,1]])
        c=M.construct(M.problem(self.D,E,self.R,[5,1,1]))
        self.assertEqual((c['selection'],c['cost']),(6,2))
    def test_zero_cost_tie(self):
        p=M.problem(self.D,self.E,self.R,[0,0]);c=M.construct(p)
        self.assertEqual(c['cost'],0);self.assertEqual(c['blocks'],[])
    def test_fractional_coefficients(self):
        p=M.problem(Mat.of([[1],[0]]),Mat.of([[0],[F(2,3)]]),Mat.of([[F(1,2)],[F(5,6)]]),[7])
        c=M.construct(p);self.assertEqual(Mat.from_wire(c['W']).data[0][0],F(-5,4))
    def test_nonhereditary_admissibility(self):
        p=M.problem(self.D,self.E,self.R,[1,1],[3]);c=M.construct(p)
        self.assertEqual(c['selection'],3);self.assertEqual(c['blocks'],[])
    def test_no_admitted_menus(self):
        p=M.problem(self.D,self.E,self.R,[1,1],[]);c=M.construct(p)
        self.assertEqual(c['kind'],'no_admissible_repair');self.assertEqual(c['blocks'],[])
    def test_no_residuals(self):
        p=M.problem(self.D,self.E,Mat.zero(3,0),[1,1]);c=M.construct(p)
        self.assertEqual((c['selection'],c['cost']),(0,0))
    def test_zero_target(self):
        p=M.problem(Mat.zero(0,2),Mat.zero(0,2),Mat.zero(0,3),[1,2]);c=M.construct(p)
        self.assertEqual(c['selection'],0)
    def test_zero_original_domain(self):
        p=M.problem(Mat.zero(2,0),Mat.eye(2),Mat.of([[1],[2]]),[1,1]);c=M.construct(p)
        self.assertEqual(c['selection'],3)
    def test_no_candidates_correctable(self):
        p=M.problem(Mat.eye(2),Mat.zero(2,0),Mat.of([[1],[2]]),[]);c=M.construct(p)
        self.assertEqual(c['selection'],0)
    def test_no_candidates_blocked(self):
        p=M.problem(Mat.zero(2,0),Mat.zero(2,0),Mat.of([[1],[2]]),[]);c=M.construct(p)
        self.assertEqual(c['kind'],'no_admissible_repair')
    def test_zero_residual_matrix(self):
        p=M.problem(self.D,self.E,Mat.zero(3,2),[1,1]);self.assertEqual(M.construct(p)['selection'],0)
    def test_invalid_target(self):
        with self.assertRaises(InvalidData):M.problem(self.D,self.E,Mat.eye(2),[1,1])
    def test_negative_cost(self):
        p=copy.deepcopy(self.p);p['costs'][0]=-1
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_bool_cost(self):
        p=copy.deepcopy(self.p);p['costs'][0]=True
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_float_cost(self):
        p=copy.deepcopy(self.p);p['costs'][0]=1.0
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_huge_cost(self):
        p=copy.deepcopy(self.p);p['costs'][0]=M.MAX_COST+1
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_wrong_cost_count(self):
        p=copy.deepcopy(self.p);p['costs']=[]
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_duplicate_admissibility(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[0,0]
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_unsorted_admissibility(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[1,0]
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_out_of_range_mask(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[4]
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_bool_mask(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[False]
        with self.assertRaises(InvalidData):M.parse_problem(p)
    def test_trial_budget(self):
        with self.assertRaises(M.ResourceLimit):M.construct(self.p,max_trials=3)
    def test_candidate_limit(self):
        with self.assertRaises(M.ResourceLimit):M.problem(Mat.zero(1,0),Mat.zero(1,9),Mat.zero(1,1),[1]*9)
    def test_missing_cheaper_coverage(self):
        c=copy.deepcopy(self.c);c['blocks']=c['blocks'][:1]
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_wrong_coefficients(self):
        c=copy.deepcopy(self.c);c['W']['entries'][0][0]=['1','1']
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_zero_separator(self):
        c=copy.deepcopy(self.c);c['blocks'][0]['Y']=Mat.zero(1,3).to_wire()
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_overstated_block(self):
        c=copy.deepcopy(self.c);c['blocks'][0]['mask']=3
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_duplicate_block(self):
        c=copy.deepcopy(self.c);c['blocks'].append(c['blocks'][0])
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_wrong_claimed_cost(self):
        c=copy.deepcopy(self.c);c['cost']=0
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_input_binding_costs(self):
        p=copy.deepcopy(self.p);p['costs']=[2,1]
        with self.assertRaises(InvalidData):M.check_certificate(p,self.c)
    def test_input_binding_admissibility(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[0,1,2]
        with self.assertRaises(InvalidData):M.check_certificate(p,self.c)
    def test_input_binding_residuals(self):
        p=copy.deepcopy(self.p);p['R']['entries'][1][0]=['2','1']
        with self.assertRaises(InvalidData):M.check_certificate(p,self.c)
    def test_input_binding_candidates(self):
        p=copy.deepcopy(self.p);p['E']['entries'][1][0]=['2','1']
        with self.assertRaises(InvalidData):M.check_certificate(p,self.c)
    def test_zero_denominator(self):
        c=copy.deepcopy(self.c);c['W']['entries'][0][0]=['1','0']
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_unreduced_fraction(self):
        c=copy.deepcopy(self.c);c['W']['entries'][0][0]=['-2','2']
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_unknown_certificate_field(self):
        c=copy.deepcopy(self.c);c['new_D']=self.p['D']
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_unsafe_namespace(self):
        with self.assertRaises(InvalidData):M.emit_input(self.p,'A\naxiom bad : False')
    def test_unsafe_import(self):
        with self.assertRaises(InvalidData):M.emit_certificate(self.p,self.c,'Test','Input\naxiom bad : False')
    def test_numeric_code_injection(self):
        c=copy.deepcopy(self.c);c['W']['entries'][0][0]=['1; sorry','1']
        with self.assertRaises(InvalidData):M.check_certificate(self.p,c)
    def test_json_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(InvalidData):read_json(p)
    def test_json_float(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_text('{"a":1.5}', encoding="utf-8")
            with self.assertRaises(InvalidData):read_json(p)
    def test_echo_exact(self):
        e={'D':self.p['D']['entries'],'E':self.p['E']['entries'],'R':self.p['R']['entries'],
           'menus':[{'selected':M.members(x,2),'allowed':True,'cost':M.cost(x,[1,1])} for x in range(4)]}
        self.assertTrue(M.check_echo(self.p,e))
    def test_echo_changed_policy(self):
        e={'D':self.p['D']['entries'],'E':self.p['E']['entries'],'R':self.p['R']['entries'],
           'menus':[{'selected':M.members(x,2),'allowed':x!=3,'cost':M.cost(x,[1,1])} for x in range(4)]}
        with self.assertRaises(InvalidData):M.check_echo(self.p,e)
    def test_echo_omits_menu(self):
        e={'D':self.p['D']['entries'],'E':self.p['E']['entries'],'R':self.p['R']['entries'],'menus':[]}
        with self.assertRaises(InvalidData):M.check_echo(self.p,e)
    def test_masked_unused_coefficients(self):
        # An unselected column never changes the equation. The checker assesses
        # selection cost, not the support of nonzero coefficients.
        p=M.problem(Mat.eye(1),Mat.of([[1]]),Mat.of([[2]]),[1]);c=M.construct(p)
        c['W']=Mat.of([[99]]).to_wire();M.check_certificate(p,c)
    def test_no_admitted_nonzero_original(self):
        p=M.problem(Mat.eye(1),Mat.eye(1),Mat.eye(1),[0],[]);c=M.construct(p)
        self.assertEqual(M.check_certificate(p,c)['admissible_menus'],0)

if __name__=='__main__':unittest.main()
