"""Adversarial proof-tree and exact input tests. No failed check means no repair."""
import unittest,copy,json,tempfile
from pathlib import Path
from fractions import Fraction as F
import branch_menu as B
from repair_certificates import Mat,InvalidData,read_json

class BranchTests(unittest.TestCase):
    def setUp(self):
        self.D=Mat.of([[1],[0],[0]]);self.E=Mat.of([[0,0],[1,0],[1,1]]);self.R=Mat.of([[0],[1],[0]])
        self.p=B.problem(self.D,self.E,self.R,[1,1]);self.c=B.construct(self.p)
    def bad(self,c,p=None):
        with self.assertRaises(InvalidData):B.check_certificate(self.p if p is None else p,c)
    def first(self,node,typ):
        if node['type']==typ:return node
        if node['type']=='split':return self.first(node['exclude'],typ) or self.first(node['include'],typ)
        return None
    def test_success(self):self.assertEqual((self.c['selection'],self.c['cost']),(3,2));B.check_certificate(self.p,self.c)
    def test_table_rejection(self):
        p=B.problem(self.D,self.E,self.R,[1,1],[0,1,2]);c=B.construct(p);self.assertEqual(c['kind'],'no_admissible_repair');B.check_certificate(p,c)
    def test_empty_table(self):
        p=B.problem(self.D,self.E,self.R,[1,1],[]);c=B.construct(p);self.assertEqual(c['tree'],{'type':'inadmissible'})
        p=B.problem(Mat.zero(1,0),Mat.zero(1,24),Mat.of([[1]]),[0]*24,[]);c=B.construct(p);self.assertEqual(c['tree'],{'type':'inadmissible'})
    def test_zero_cost(self):
        c=B.construct(B.problem(self.D,self.E,self.R,[0,0]));self.assertEqual(c['cost'],0)
    def test_fractional(self):
        p=B.problem(Mat.of([[1],[0]]),Mat.of([[0],[F(2,3)]]),Mat.of([[F(1,2)],[F(5,6)]]),[7]);c=B.construct(p)
        self.assertEqual(Mat.from_wire(c['W']).data[0][0],F(-5,4))
    def test_nonhereditary(self):
        p=B.problem(self.D,self.E,self.R,[1,1],[3]);self.assertEqual(B.construct(p)['selection'],3)
    def test_cheaper_pair(self):
        E=Mat.of([[0,0,0],[1,1,0],[0,1,1]]);c=B.construct(B.problem(self.D,E,self.R,[5,1,1]));self.assertEqual(c['cost'],2)
    def test_incumbent_improves(self):
        E=Mat.of([[0,0,0],[1,0,1],[1,1,0]]);s={};c=B.construct(B.problem(self.D,E,self.R,[1,9,4]),stats=s)
        self.assertEqual(c['cost'],4);self.assertGreater(s['incumbent_updates'],1)
    def test_large_single_separator(self):
        p=B.problem(Mat.of([[1],[0]]),Mat.of([[1]*24,[0]*24]),Mat.of([[0],[1]]),[1]*24);s={};c=B.construct(p,stats=s)
        self.assertEqual(s['visited_nodes'],1);self.assertEqual(B.check_certificate(p,c)['nodes'],1)
    def test_zero_target(self):
        p=B.problem(Mat.zero(0,2),Mat.zero(0,2),Mat.zero(0,3),[1,2]);self.assertEqual(B.construct(p)['selection'],0)
    def test_empty_residuals(self):
        p=B.problem(self.D,self.E,Mat.zero(3,0),[1,1]);self.assertEqual(B.construct(p)['selection'],0)
    def test_zero_candidates(self):
        p=B.problem(Mat.eye(2),Mat.zero(2,0),Mat.of([[1],[2]]),[]);self.assertEqual(B.construct(p)['selection'],0)
    def test_zero_candidates_impossible(self):
        p=B.problem(Mat.zero(2,0),Mat.zero(2,0),Mat.of([[1],[2]]),[]);self.assertEqual(B.construct(p)['kind'],'no_admissible_repair')
    def test_budget_nodes(self):
        with self.assertRaises(B.ResourceLimit):B.construct(self.p,max_nodes=0)
    def test_budget_linear(self):
        with self.assertRaises(B.ResourceLimit):B.construct(self.p,max_linear_trials=0)
    def test_partial_search_budget(self):
        with self.assertRaises(B.ResourceLimit):B.construct(self.p,max_nodes=2)
    def test_budget_type(self):
        with self.assertRaises(InvalidData):B.construct(self.p,max_nodes=True)
    def test_candidate_guard(self):
        with self.assertRaises(B.ResourceLimit):B.problem(Mat.zero(1,0),Mat.zero(1,25),Mat.zero(1,1),[1]*25)
    def test_wrong_W(self):
        c=copy.deepcopy(self.c);c['W']=(-Mat.from_wire(c['W'])).to_wire();self.bad(c)
    def test_false_cost_bound(self):
        c=copy.deepcopy(self.c);c['tree']={'type':'bound'};self.bad(c)
    def test_false_inadmissibility(self):
        c=copy.deepcopy(self.c);c['tree']={'type':'inadmissible'};self.bad(c)
    def test_zero_detector(self):
        c=copy.deepcopy(self.c);self.first(c['tree'],'separator')['Y']=Mat.zero(1,3).to_wire();self.bad(c)
    def test_separator_overstates_scope(self):
        c=copy.deepcopy(self.c);c['tree']=copy.deepcopy(self.first(c['tree'],'separator'));self.bad(c)
    def test_missing_child(self):
        c=copy.deepcopy(self.c);del c['tree']['include'];self.bad(c)
    def test_extra_leaf_field(self):
        c=copy.deepcopy(self.c);self.first(c['tree'],'bound')['trusted']=True;self.bad(c)
    def test_repeated_split(self):
        c=copy.deepcopy(self.c);c['tree']['include']['j']=c['tree']['j'];self.bad(c)
    def test_split_out_of_range(self):
        c=copy.deepcopy(self.c);c['tree']['j']=2;self.bad(c)
    def test_split_bool(self):
        c=copy.deepcopy(self.c);c['tree']['j']=False;self.bad(c)
    def test_swap_children(self):
        c=copy.deepcopy(self.c);c['tree']['include'],c['tree']['exclude']=c['tree']['exclude'],c['tree']['include'];self.bad(c)
    def test_no_repair_with_bound(self):
        c={k:copy.deepcopy(self.c[k]) for k in ('schema','problem_sha256','tree')};c['kind']='no_admissible_repair';self.bad(c)
    def test_unselected_direction(self):
        c=copy.deepcopy(self.c);c['selection']=1;c['cost']=1;self.bad(c)
    def test_wrong_declared_cost(self):
        c=copy.deepcopy(self.c);c['cost']=1;self.bad(c)
    def test_input_binding_weights(self):
        p=copy.deepcopy(self.p);p['costs']=[2,1];self.bad(self.c,p)
    def test_input_binding_table(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[0,1,2];self.bad(self.c,p)
    def test_input_binding_D(self):
        p=copy.deepcopy(self.p);p['D']['entries'][0][0]=['2','1'];self.bad(self.c,p)
    def test_input_binding_R(self):
        p=copy.deepcopy(self.p);p['R']['entries'][1][0]=['2','1'];self.bad(self.c,p)
    def test_negative_weights(self):
        p=copy.deepcopy(self.p);p['costs'][0]=-1
        with self.assertRaises(InvalidData):B.parse_problem(p)
    def test_float_weights(self):
        p=copy.deepcopy(self.p);p['costs'][0]=1.0
        with self.assertRaises(InvalidData):B.parse_problem(p)
    def test_duplicate_table(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[0,0]
        with self.assertRaises(InvalidData):B.parse_problem(p)
    def test_bad_table_mask(self):
        p=copy.deepcopy(self.p);p['admissible_masks']=[4]
        with self.assertRaises(InvalidData):B.parse_problem(p)
    def test_zero_denominator(self):
        c=copy.deepcopy(self.c);c['W']['entries'][0][0]=['1','0'];self.bad(c)
    def test_unreduced_fraction(self):
        c=copy.deepcopy(self.c);c['W']['entries'][0][0]=['-2','2'];self.bad(c)
    def test_injected_numerator(self):
        c=copy.deepcopy(self.c);c['W']['entries'][0][0]=['1; sorry','1'];self.bad(c)
    def test_injected_namespace(self):
        with self.assertRaises(InvalidData):B.emit_input(self.p,'X\naxiom bad : False')
    def test_injected_import(self):
        with self.assertRaises(InvalidData):B.emit_certificate(self.p,self.c,'X','Y\naxiom bad : False')
        with self.assertRaises(InvalidData):B.emit_echo(self.p,'X','Y\naxiom bad : False')
    def test_echo_all(self):
        e={k:self.p[k]['entries'] for k in ('D','E','R')};e.update(costs=[1,1],admissible_masks=None);self.assertTrue(B.check_echo(self.p,e))
        p=copy.deepcopy(self.p);p['admissible_masks']=[3];e['admissible_masks']=[[0,1]]
        self.assertTrue(B.check_echo(p,e))
        e['admissible_masks']=[[False,True]]
        with self.assertRaises(InvalidData):B.check_echo(p,e)
    def test_echo_all_vs_empty(self):
        e={k:self.p[k]['entries'] for k in ('D','E','R')};e.update(costs=[1,1],admissible_masks=[])
        with self.assertRaises(InvalidData):B.check_echo(self.p,e)
    def test_reject_replacement_input_field(self):
        c=copy.deepcopy(self.c);c['D']=self.p['D'];self.bad(c)
    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_text('{"tree":{},"tree":{}}', encoding="utf-8")
            with self.assertRaises(InvalidData):read_json(p)
    def test_float_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_text('{"cost":1.0}', encoding="utf-8")
            with self.assertRaises(InvalidData):read_json(p)

if __name__=='__main__':unittest.main()
