#!/usr/bin/env python3
"""Verifier negative controls. No successful Lean execution is simulated or claimed.
Author: Komorebi P.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('paper_v_verify',ROOT/'verification/verify.py')
verify=importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class VerifierControls(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='paper_v_verifier_')
        self.root=Path(self.temp.name)/'bundle'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__','.lake','*.log'))

    def tearDown(self):
        self.temp.cleanup()

    def edit(self, rel, transform, *, reseal=False):
        p=self.root/rel;p.write_text(transform(p.read_text(encoding='utf-8')),encoding='utf-8')
        if reseal:
            cp=self.root/'verification/candidate_contract.json'
            contract=json.loads(cp.read_text(encoding='utf-8'))
            contract['source_sha256'][rel]=hashlib.sha256(p.read_bytes()).hexdigest()
            cp.write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')

    def rejected(self, reason):
        with self.assertRaisesRegex(verify.VerificationError,reason):
            verify.static_checks(self.root)

    def test_clean_static_contract(self):
        result=verify.static_checks(self.root)
        self.assertEqual(result['explicit_theorem_targets'],225)
        self.assertEqual(result['proof_modules'],23)

    def test_incomplete_scope_rejected(self):
        def change(text):
            d=json.loads(text);d['results'][0]['status']='incomplete';return json.dumps(d)
        self.edit('verification/scope_contract.json',change)
        self.rejected('Incomplete manuscript scope row')

    def test_unknown_scope_target_rejected(self):
        def change(text):
            d=json.loads(text);d['results'][0]['targets']=['KomorebiPaperV.does_not_exist'];return json.dumps(d)
        self.edit('verification/scope_contract.json',change)
        self.rejected('Unregistered scope target')

    def test_no_assert_validation_statements(self):
        tree=ast.parse((ROOT/'verification/verify.py').read_text(encoding='utf-8'))
        self.assertFalse(any(isinstance(node,ast.Assert) for node in ast.walk(tree)))

    def test_baseline_corruption(self):
        baseline=json.loads((self.root/'provenance/BASELINE.json').read_text())
        with (self.root/'manuscript'/baseline['baseline_file']).open('ab') as f:f.write(b'changed')
        self.rejected('Baseline PDF hash mismatch')

    def test_source_mutation(self):
        self.edit('formalization/lean/KomorebiPaperV/IntegerPolyphase.lean',lambda s:s+'\n-- changed\n')
        self.rejected('Source integrity mismatch')

    def test_source_missing_or_extra(self):
        p=self.root/'formalization/lean/KomorebiPaperV/Packets.lean'
        saved=p.read_bytes();p.unlink();self.rejected('Source file-set mismatch')
        p.write_bytes(saved)
        (p.parent/'Extra.lean').write_text('import Mathlib\n')
        self.rejected('Source file-set mismatch')

    def test_source_placeholder_after_reseal(self):
        self.edit('formalization/lean/KomorebiPaperV/Packets.lean',lambda s:s+'\nsorry\n',reseal=True)
        self.rejected('Forbidden active Lean tokens')

    def test_target_contract_completeness(self):
        rel='formalization/lean/KomorebiPaperV/IntegerPolyphase.lean'
        self.edit(rel,lambda s:s.replace('theorem phase_val','theorem phase_val_renamed'),reseal=True)
        self.rejected('Theorem target mismatch')

    def test_root_import_completeness(self):
        self.edit('formalization/lean/KomorebiPaperV.lean',
                  lambda s:s.replace('import KomorebiPaperV.FIRTransfer\n',''),reseal=True)
        self.rejected('Top-level library import coverage mismatch')

    def test_axiom_print_completeness(self):
        self.edit('formalization/lean/KernelAudit.lean',
                  lambda s:s.replace('#print axioms KomorebiPaperV.Binary.cutSum_eq_root\n',''),reseal=True)
        self.rejected('Axiom-print target coverage mismatch')

    def test_audit_array_completeness(self):
        self.edit('formalization/lean/KernelAudit.lean',
                  lambda s:s.replace('    `KomorebiPaperV.Binary.cutSum_eq_root,\n',''),reseal=True)
        self.rejected('Audit target-array coverage mismatch')

    def test_pins_fail_closed(self):
        self.edit('formalization/lean/lean-toolchain',lambda s:s.replace('4.34.0-rc2','4.33.0'))
        self.rejected('Unexpected Lean toolchain pin')
        self.edit('formalization/lean/lean-toolchain',lambda _:verify.TOOLCHAIN+'\n')
        self.edit('formalization/lean/lake-manifest.json',lambda s:s.replace(verify.MATHLIB_REV,'0'*40))
        self.rejected('Unexpected mathlib pin')

    def test_scanner_comment_string_boundaries(self):
        self.assertEqual(verify.lean_code_only('/- sorry /- admit -/ -/ theorem t : True := by trivial\n'),
                         '  theorem t : True := by trivial\n')
        self.assertNotIn('sorry',verify.lean_code_only('def s := "sorry" -- admit\n'))
        for source in ('/- unclosed','def s := "unclosed'):
            with self.assertRaises(verify.VerificationError):verify.lean_code_only(source)
        self.assertIn('sorry',verify.lean_code_only('/- fine -/ sorry'))

    def test_optimized_python_preserves_rejection(self):
        # Run the real static_checks under -O, not a mocked compiler or fake proof log.
        rel='formalization/lean/KomorebiPaperV/Packets.lean'
        self.edit(rel,lambda s:s+'\nsorry\n',reseal=True)
        command='''import importlib.util, pathlib, sys
root=pathlib.Path(sys.argv[1])
s=importlib.util.spec_from_file_location("v",root/"verification/verify.py")
v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
try:
 v.static_checks(root)
except v.VerificationError as error:
 print("REJECTED:",error)
 sys.exit(7)
sys.exit(0)
'''
        p=subprocess.run([sys.executable,'-O','-c',command,str(self.root)],text=True,
                         stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
        self.assertEqual(p.returncode,7,p.stdout)
        self.assertIn('Forbidden active Lean tokens',p.stdout)

    def test_subprocess_failures_and_timeout_logs(self):
        log=self.root/'verification/control_child.log'
        with self.assertRaisesRegex(verify.VerificationError,'exited 9'):
            verify.run([sys.executable,'-c','print("failed intentionally");raise SystemExit(9)'],
                       self.root,log,10)
        self.assertIn('failed intentionally',log.read_text())
        with self.assertRaisesRegex(verify.VerificationError,'timed out'):
            verify.run([sys.executable,'-c','import time; print("started",flush=True);time.sleep(3)'],
                       self.root,log,1,ready_token='started',startup_timeout=30)
        self.assertIn('TIMEOUT',log.read_text())
        self.assertIn('started',log.read_text())


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
    started=time.perf_counter()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(VerifierControls))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),
            'elapsed_seconds':time.perf_counter()-started,'lean_kernel_checked':False,
            'scope':'Static verifier positive/negative controls; no simulated successful Lean build.',
            'actual_lean_positive_path_tested':False}
    if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
