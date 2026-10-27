"""Release-contract tests. Each failure must stay distinct from infeasibility."""
from __future__ import annotations
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))

import komorebi_repair as K
from repair_certificates import Mat, InvalidData, MAX_BYTES, read_json

ROOT = Path(__file__).resolve().parents[1]

class ExactBoundaryTests(unittest.TestCase):
    def test_explicit_column_mismatch(self):
        with self.assertRaises(InvalidData): Mat.of([[1,2]], 99)
    def test_boolean_column_count(self):
        with self.assertRaises(InvalidData): Mat.of([[1]], True)
    def test_float_column_count(self):
        with self.assertRaises(InvalidData): Mat.of([[1]], 1.0)
    def test_negative_column_count(self):
        with self.assertRaises(InvalidData): Mat.of([], -1)
    def test_matching_column_count(self):
        self.assertEqual(Mat.of([[1,2]], 2).cols, 2)
    def test_zero_row_width_preserved(self):
        self.assertEqual((Mat.of([], 7).rows, Mat.of([], 7).cols), (0,7))
    def test_mutable_outer_storage_rejected(self):
        with self.assertRaises(InvalidData): Mat(1,1,[[F(1)]])
    def test_mutable_inner_storage_rejected(self):
        with self.assertRaises(InvalidData): Mat(1,1,([F(1)],))
    def test_boolean_column_index(self):
        with self.assertRaises(InvalidData): Mat.of([[1,2]]).columns([True])
    def test_boolean_row_index(self):
        with self.assertRaises(InvalidData): Mat.of([[1],[2]]).select_rows([False])
    def test_float_entries(self):
        with self.assertRaises(InvalidData): Mat.of([[0.5]])
    def test_frozen_value(self):
        a=Mat.of([[1]])
        with self.assertRaises((AttributeError, TypeError)): a.data[0][0]=F(2)
    def test_float_indices(self):
        with self.assertRaises(InvalidData): Mat.of([[1,2]]).columns([1.0])
    def test_ragged_data(self):
        with self.assertRaises(InvalidData): Mat.of([[1],[1,2]])

class JsonBoundaryTests(unittest.TestCase):
    def rejects(self, data):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_bytes(data)
            with self.assertRaises(InvalidData): read_json(p)
    def test_actual_read_size(self):
        self.rejects(b' '*MAX_BYTES+b'{}')
    def test_stale_stat_cannot_bypass_bound(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_bytes(b' '*MAX_BYTES+b'{}')
            with patch.object(Path,'stat',side_effect=AssertionError('must not trust stat')):
                with self.assertRaises(InvalidData): read_json(p)
    def test_nonfinite(self): self.rejects(b'{"x": NaN}')
    def test_float(self): self.rejects(b'{"x": 1.25}')
    def test_repeated_key(self): self.rejects(b'{"x":1,"x":2}')
    def test_large_integer_token(self): self.rejects(b'{"x":'+b'1'*513+b'}')
    def test_invalid_utf8(self): self.rejects(b'\xff')
    def test_deep_structure(self): self.rejects(b'['*1500+b'0'+b']'*1500)
    def test_malformed_syntax(self): self.rejects(b'{')
    def test_brackets_inside_string_are_not_nesting(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x';value='['*2000+'\\'+'"'
            p.write_text(json.dumps({'text':value}), encoding="utf-8")
            self.assertEqual(read_json(p)['text'],value)
    def test_exact_integer_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x';p.write_bytes(b'{"x":'+b'1'*512+b'}')
            self.assertEqual(len(str(read_json(p)['x'])),512)

class PublicApiTests(unittest.TestCase):
    def setUp(self):
        self.D=Mat.of([[1],[0],[0]])
        self.E=Mat.of([[0,0],[1,0],[1,1]])
        self.R=Mat.of([[0],[1],[0]])
        self.p=K.menu_problem(self.D,self.E,self.R,[1,1])
    def test_version(self): self.assertEqual(K.__version__,'1.0.0rc3')
    def test_public_surface(self):
        self.assertTrue({'solve','verify','ExactMatrix','Outcome'}<=set(K.__all__))
    def test_menu_repair(self):
        r=K.solve(self.p)
        self.assertEqual(r.status,'PYTHON_CERTIFICATE_VALID')
        self.assertEqual(r.certificate['cost'],2)
    def test_not_kernel_checked(self):
        r=K.solve(self.p)
        self.assertFalse(r.kernel_checked)
        self.assertFalse(r.to_dict()['kernel_checked'])
    def test_free_repair(self):
        r=K.solve(K.free_problem(self.D,self.R))
        self.assertEqual(r.status,'PYTHON_CERTIFICATE_VALID')
        self.assertEqual(r.certificate['t'],1)
    def test_input_unchanged(self):
        old=copy.deepcopy(self.p);K.solve(self.p);self.assertEqual(old,self.p)
    def test_verified_output_copy(self):
        c=K.solve(self.p).certificate;r=K.verify(self.p,c)
        c['cost']=99
        self.assertEqual(r.certificate['cost'],2)
    def test_oversized_certificate_is_unresolved(self):
        c=K.solve(self.p).certificate;c['oversized']=' '*MAX_BYTES
        r=K.verify(self.p,c)
        self.assertEqual((r.status,r.error_code),('UNRESOLVED','RESOURCE_LIMIT'))
    def test_changed_cost_rejected(self):
        c=K.solve(self.p).certificate;c['cost']=9
        self.assertEqual(K.verify(self.p,c).status,'UNRESOLVED')
    def test_changed_original_rejected(self):
        c=K.solve(self.p).certificate;p=copy.deepcopy(self.p);p['costs']=[2,2]
        self.assertEqual(K.verify(p,c).status,'UNRESOLVED')
    def test_no_repair_scoped(self):
        p=K.menu_problem(self.D,self.E,self.R,[1,1],[0,1,2]);r=K.solve(p)
        self.assertEqual(r.certificate['kind'],'no_admissible_repair')
        self.assertEqual(r.status,'PYTHON_CERTIFICATE_VALID')
    def test_all_vs_empty_admissibility(self):
        p=K.menu_problem(self.D,self.E,self.R,[1,1],[])
        self.assertEqual(K.solve(p).certificate['kind'],'no_admissible_repair')
        self.assertEqual(K.solve(self.p).certificate['kind'],'optimal_menu')
    def test_node_exhaustion(self):
        r=K.solve(self.p,max_nodes=0)
        self.assertEqual((r.status,r.error_code),('UNRESOLVED','RESOURCE_LIMIT'))
        self.assertIsNone(r.certificate)
    def test_linear_exhaustion(self):
        self.assertEqual(K.solve(self.p,max_linear_trials=0).status,'UNRESOLVED')
    def test_boolean_budget(self):
        self.assertEqual(K.solve(self.p,max_nodes=True).status,'UNRESOLVED')
    def test_negative_budget(self):
        self.assertEqual(K.solve(self.p,max_nodes=-1).status,'UNRESOLVED')
    def test_oversized_budget(self):
        self.assertEqual(K.solve(self.p,max_nodes=8192).status,'UNRESOLVED')
    def test_unknown_schema(self):
        p=copy.deepcopy(self.p);p['schema']='unknown'
        self.assertEqual(K.solve(p).status,'UNRESOLVED')
    def test_bad_certificate_type(self):
        self.assertEqual(K.verify(self.p,[]).status,'UNRESOLVED')
    def test_bad_schema_type(self):
        p=copy.deepcopy(self.p);p['schema']=[]
        self.assertEqual(K.solve(p).status,'UNRESOLVED')
    def test_nonjson_value(self):
        self.assertEqual(K.solve({'schema':set()}).status,'UNRESOLVED')
    def test_no_result_input_field(self):
        p=copy.deepcopy(self.p);p['status']='KERNEL_CHECKED'
        self.assertEqual(K.solve(p).status,'UNRESOLVED')
    def test_serializable_outcome(self):
        self.assertEqual(json.loads(json.dumps(K.solve(self.p).to_dict()))['status'],'PYTHON_CERTIFICATE_VALID')
    def test_zero_target(self):
        p=K.menu_problem(Mat.zero(0,2),Mat.zero(0,2),Mat.zero(0,4),[1,2])
        self.assertEqual(K.solve(p).certificate['selection'],0)
    def test_all_exported_inputs_and_certificates(self):
        count=0
        for folder in ('corpus','menu_corpus','branch_corpus'):
            for inp in sorted((ROOT/'examples'/folder).glob('*_input.json')):
                with self.subTest(input=inp.name):
                    p=K.load(inp);cert=read_json(inp.with_name(inp.name.replace('_input','_certificate')))
                    self.assertEqual(K.verify(p,cert).status,'PYTHON_CERTIFICATE_VALID')
                    self.assertEqual(K.solve(p).status,'PYTHON_CERTIFICATE_VALID')
                    count+=1
        self.assertEqual(count,72)

class CliTests(unittest.TestCase):
    def call(self,*args):
        env=dict(os.environ,PYTHONPATH=str(ROOT/'python'))
        p=subprocess.run([sys.executable,'-m','komorebi_repair',*map(str,args)],
                         env=env,capture_output=True,text=True,timeout=20, encoding="utf-8")
        return p,json.loads(p.stdout)
    def test_doctor(self):
        p,r=self.call('doctor');self.assertEqual(p.returncode,0);self.assertFalse(r['kernel_checked'])
    def test_new_output_and_recheck(self):
        with tempfile.TemporaryDirectory() as td:
            inp=ROOT/'examples/branch_corpus/Branch018_input.json';out=Path(td)/'new'
            p,r=self.call('solve',inp,'--output',out)
            self.assertEqual(p.returncode,0)
            p2,r2=self.call('check',inp,out/'certificate.json','--output',Path(td)/'check')
            self.assertEqual(p2.returncode,0);self.assertFalse(r2['kernel_checked'])
    def test_preserve_existing_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            mark=Path(td)/'marker';mark.write_text('keep', encoding="utf-8")
            p,r=self.call('solve',ROOT/'examples/branch_corpus/Branch018_input.json','--output',td)
            self.assertEqual(p.returncode,2);self.assertEqual(mark.read_text(encoding="utf-8"),'keep')
    def test_missing_input(self):
        with tempfile.TemporaryDirectory() as td:
            p,r=self.call('solve',Path(td)/'missing','--output',Path(td)/'out')
            self.assertEqual((p.returncode,r['status']),(2,'UNRESOLVED'))
    def test_budget_unresolved_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            p,r=self.call('solve',ROOT/'examples/branch_corpus/Branch018_input.json','--max-nodes',0,'--output',Path(td)/'out')
            self.assertEqual((p.returncode,r['error_code']),(2,'RESOURCE_LIMIT'))
            self.assertFalse((Path(td)/'out/certificate.json').exists())
    def test_no_repair_is_not_parse_failure(self):
        with tempfile.TemporaryDirectory() as td:
            p,r=self.call('solve',ROOT/'examples/branch_corpus/Branch019_input.json','--output',Path(td)/'out')
            self.assertEqual(p.returncode,0)
            c=json.loads((Path(td)/'out/certificate.json').read_text(encoding="utf-8"))
            self.assertEqual(c['kind'],'no_admissible_repair')

if __name__=='__main__': unittest.main()
