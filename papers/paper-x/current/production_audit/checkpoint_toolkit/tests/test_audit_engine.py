"""Bounded tests of evidence handling. These are not Paper X theorem checks."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_engine import (AuditError, PREFIX, audit_source, execute, parse_audit,
    parse_json, require_rejection, require_success, safe_relative, sha256, verify_files)

OK={'returncode':0,'timed_out':False,'spawn_error':None}
OWNERS=['Fixture']
TARGETS=[{'name':'Fixture.ok','kind':'theorem','owner':'Fixture'}]
def rows():
    return [dict(event='target',**TARGETS[0]),
        dict(event='declaration',name='Fixture.ok',kind='theorem',owner='Fixture',axioms=[],forbidden=[]),
        dict(event='complete',owners=OWNERS,declarations=1,theorems=1,targets=1)]
def text(rs):return '\n'.join(PREFIX+json.dumps(r) for r in rs)+'\n'
def parse(rs=None,result=None,owners=None,targets=None):
    return parse_audit(OK if result is None else result,text(rows() if rs is None else rs),
        OWNERS if owners is None else owners,TARGETS if targets is None else targets)

class AuditLogTests(unittest.TestCase):
    def test_valid_minimal_audit(self):self.assertEqual(parse()['declarations'],1)
    def test_foundational_axioms(self):
        r=rows();r[1]['axioms']=['propext','Classical.choice','Quot.sound']
        self.assertEqual(len(parse(r)['axiom_union']),3)
    def test_failure_overrides_complete(self):
        with self.assertRaises(AuditError):parse(result=dict(OK,returncode=1))
    def test_timeout_overrides_complete(self):
        with self.assertRaises(AuditError):parse(result=dict(OK,timed_out=True))
    def test_spawn_failure_overrides_complete(self):
        with self.assertRaises(AuditError):parse(result=dict(OK,spawn_error='missing executable'))
    def test_missing_completion(self):
        with self.assertRaises(AuditError):parse(rows()[:-1])
    def test_empty_census(self):
        r=rows();del r[1];r[-1]['declarations']=0;r[-1]['theorems']=0
        with self.assertRaises(AuditError):parse(r)
    def test_duplicate_declaration(self):
        r=rows();r.insert(2,r[1])
        with self.assertRaises(AuditError):parse(r)
    def test_duplicate_target(self):
        r=rows();r.insert(1,r[0])
        with self.assertRaises(AuditError):parse(r)
    def test_duplicate_completion(self):
        r=rows();r.append(r[-1])
        with self.assertRaises(AuditError):parse(r)
    def test_post_completion_record(self):
        r=rows();r.append(r[1])
        with self.assertRaises(AuditError):parse(r)
    def test_missing_target(self):
        r=rows();del r[0]
        with self.assertRaises(AuditError):parse(r)
    def test_wrong_target_kind(self):
        r=rows();r[0]['kind']='definition'
        with self.assertRaises(AuditError):parse(r)
    def test_wrong_target_owner(self):
        r=rows();r[0]['owner']='Other'
        with self.assertRaises(AuditError):parse(r)
    def test_unowned_declaration(self):
        r=rows();r[1]['owner']='Other'
        with self.assertRaises(AuditError):parse(r)
    def test_wrong_count(self):
        r=rows();r[-1]['declarations']=2
        with self.assertRaises(AuditError):parse(r)
    def test_boolean_count(self):
        r=rows();r[-1]['declarations']=True
        with self.assertRaises(AuditError):parse(r)
    def test_forbidden_axiom(self):
        r=rows();r[1]['axioms']=['bad'];r[1]['forbidden']=['bad']
        with self.assertRaises(AuditError):parse(r)
    def test_false_clean_axiom_list(self):
        r=rows();r[1]['axioms']=['bad']
        with self.assertRaises(AuditError):parse(r)
    def test_duplicate_axiom(self):
        r=rows();r[1]['axioms']=['propext','propext']
        with self.assertRaises(AuditError):parse(r)
    def test_unknown_event(self):
        r=rows();r[1]['event']='success'
        with self.assertRaises(AuditError):parse(r)
    def test_unknown_declaration_kind(self):
        r=rows();r[1]['kind']='theoremish'
        with self.assertRaises(AuditError):parse(r)
    def test_unexpected_record_field(self):
        r=rows();r[1]['skip']=True
        with self.assertRaises(AuditError):parse(r)
    def test_duplicate_expected_owners(self):
        with self.assertRaises(AuditError):parse(owners=['Fixture','Fixture'])
    def test_empty_expected_owners(self):
        with self.assertRaises(AuditError):parse(owners=[])
    def test_duplicate_expected_targets(self):
        with self.assertRaises(AuditError):parse(targets=TARGETS*2)
    def test_target_missing_from_census(self):
        r=rows();r[1]['name']='Fixture.other'
        with self.assertRaises(AuditError):parse(r)
    def test_nonobject_record(self):
        with self.assertRaises(AuditError):parse([[],*rows()])
    def test_duplicate_json_key(self):
        with self.assertRaises(AuditError):parse_json('{"a":0,"a":1}')
    def test_nonfinite_json_constant(self):
        with self.assertRaises(AuditError):parse_json('{"a":NaN}')
    def test_boolean_success_code(self):
        with self.assertRaises(AuditError):require_success(dict(OK,returncode=False))
    def test_boolean_rejection_code(self):
        with self.assertRaises(AuditError):require_rejection(dict(OK,returncode=True),'error: rejected','rejected')
    def test_negative_signal_not_rejection(self):
        with self.assertRaises(AuditError):require_rejection(dict(OK,returncode=-9),'error: rejected','rejected')
    def test_rejection_requires_diagnostic(self):
        with self.assertRaises(AuditError):require_rejection(dict(OK,returncode=1),'error: wrong failure','expected')
    def test_rejection_requires_error(self):
        with self.assertRaises(AuditError):require_rejection(dict(OK,returncode=1),'expected','expected')
    def test_expected_rejection(self):require_rejection(dict(OK,returncode=1),'error: expected','expected')
    def test_module_source_injection(self):
        with self.assertRaises(AuditError):audit_source(['Fixture\naxiom forged : False'],[])
    def test_module_source_duplicate(self):
        with self.assertRaises(AuditError):audit_source(['Fixture','Fixture'],[])

class FilesAndProcessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def fixture(self):
        (self.root/'a.txt').write_text('source',encoding='utf-8')
        return {'a.txt':sha256(self.root/'a.txt')}
    def test_exact_files_pass(self):self.assertEqual(verify_files(self.root,self.fixture(),strict=True)['files'],1)
    def test_modified_source_rejected(self):
        m=self.fixture();(self.root/'a.txt').write_text('changed')
        with self.assertRaises(AuditError):verify_files(self.root,m)
    def test_missing_file_rejected(self):
        m=self.fixture();(self.root/'a.txt').unlink()
        with self.assertRaises(AuditError):verify_files(self.root,m)
    def test_extra_file_rejected(self):
        m=self.fixture();(self.root/'extra').write_text('x')
        with self.assertRaises(AuditError):verify_files(self.root,m,strict=True)
    def test_empty_manifest_rejected(self):
        with self.assertRaises(AuditError):verify_files(self.root,{})
    def test_symlink_rejected(self):
        m=self.fixture();(self.root/'link').symlink_to(self.root/'a.txt')
        with self.assertRaises(AuditError):verify_files(self.root,{'link':m['a.txt']})
    def test_traversal_rejected(self):
        with self.assertRaises(AuditError):safe_relative('../a')
    def test_absolute_path_rejected(self):
        with self.assertRaises(AuditError):safe_relative('/tmp/a')
    def test_windows_drive_rejected(self):
        with self.assertRaises(AuditError):safe_relative('C:/a')
    def test_empty_path_component_rejected(self):
        with self.assertRaises(AuditError):safe_relative('a//b')
    def test_execute_success(self):
        r=execute([sys.executable,'-c','print("ok")'],self.root,dict(os.environ),10,self.root/'ok.log')
        require_success(r);self.assertEqual((self.root/'ok.log').read_text().strip(),'ok')
    def test_execute_nonzero(self):
        r=execute([sys.executable,'-c','raise SystemExit(3)'],self.root,dict(os.environ),10,self.root/'bad.log')
        with self.assertRaises(AuditError):require_success(r)
    def test_spawn_error(self):
        r=execute([str(self.root/'missing')],self.root,dict(os.environ),10,self.root/'spawn.log')
        self.assertIsNotNone(r['spawn_error'])
        with self.assertRaises(AuditError):require_rejection(r,'error: expected','expected')
    def test_timeout_not_rejection(self):
        r=execute([sys.executable,'-c','import time; time.sleep(10)'],self.root,dict(os.environ),0.2,self.root/'timeout.log')
        self.assertTrue(r['timed_out'])
        with self.assertRaises(AuditError):require_rejection(r,'error: expected','expected')
    def test_no_log_overwrite(self):
        p=self.root/'existing.log';p.write_text('previous')
        with self.assertRaises(AuditError):execute([sys.executable,'-c','pass'],self.root,dict(os.environ),1,p)
        self.assertEqual(p.read_text(),'previous')
    def test_nonfinite_timeout(self):
        with self.assertRaises(AuditError):execute([sys.executable,'-c','pass'],self.root,dict(os.environ),float('inf'),self.root/'t.log')
    def test_boolean_timeout(self):
        with self.assertRaises(AuditError):execute([sys.executable,'-c','pass'],self.root,dict(os.environ),True,self.root/'t.log')


class ReceiptTests(unittest.TestCase):
    """Mutation controls for the preserved compiler-fixture evidence."""
    def setUp(self):
        import shutil
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for name in ('scripts','lean','evidence/controls'):
            shutil.copytree(ROOT/name,self.root/name)
        from verify_control_evidence import check
        self.check=lambda:check(self.root)
    def tearDown(self):self.temp.cleanup()
    def test_saved_receipts_pass(self):self.assertEqual(self.check()['cases'],18)
    def test_missing_chunk_rejected(self):
        import shutil
        shutil.rmtree(self.root/'evidence/controls/c01_03')
        with self.assertRaises(AuditError):self.check()
    def test_duplicate_chunk_rejected(self):
        import shutil
        shutil.copytree(self.root/'evidence/controls/c01_03',self.root/'evidence/controls/duplicate')
        with self.assertRaises(AuditError):self.check()
    def test_changed_fixture_rejected(self):
        p=next((self.root/'evidence/controls').rglob('Fixture.lean'));p.write_text('theorem altered : True := True.intro')
        with self.assertRaises(AuditError):self.check()
    def test_changed_log_rejected(self):
        p=next((self.root/'evidence/controls').rglob('compiler_version.log'));p.write_text('forged')
        with self.assertRaises(AuditError):self.check()
    def test_changed_auditor_rejected(self):
        (self.root/'lean/AuditCore.lean').write_text('-- changed')
        with self.assertRaises(AuditError):self.check()
    def test_changed_engine_rejected(self):
        (self.root/'scripts/audit_engine.py').write_text('# changed')
        with self.assertRaises(AuditError):self.check()
    def test_wrong_receipt_count_rejected(self):
        p=next((self.root/'evidence/controls').glob('*/CONTROLS.json'));r=json.loads(p.read_text());r['case_count']=999;p.write_text(json.dumps(r))
        with self.assertRaises(AuditError):self.check()
    def test_wrong_compiler_pin_rejected(self):
        p=next((self.root/'evidence/controls').glob('*/CONTROLS.json'));r=json.loads(p.read_text());r['compiler_sha256']='0'*64;p.write_text(json.dumps(r))
        with self.assertRaises(AuditError):self.check()

if __name__=='__main__':unittest.main(verbosity=2)
