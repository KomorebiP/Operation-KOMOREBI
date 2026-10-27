#!/usr/bin/env python3
"""Adversarial tests of verification plumbing, not additional mathematical proofs."""
from dataclasses import replace
from pathlib import Path
import contextlib, io, json, os, sys, tempfile, time, unittest
import replay_lean as replay
import validate_source_contract as source
from process_controls import execute_ready

class SourceContractTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with contextlib.redirect_stdout(io.StringIO()):cls.gate,cls.rows,cls.records,cls.targets,cls.report=source.collect()
 def check(self,rows=None,records=None,targets=None):return self.gate.crosscheck_map_contract(self.rows if rows is None else rows,self.records if records is None else records,self.targets if targets is None else targets)
 def test_real_typed_api(self):
  self.assertIsInstance(self.rows[0],self.gate.MapRow);self.assertIsInstance(self.targets[0],self.gate.LeanTarget);self.assertIsInstance(next(iter(self.records.values())),self.gate.RegisterRecord)
 def test_full_scope(self):self.assertEqual(self.report['full_scoped_results'],68);self.assertEqual(self.report['mapped_targets'],1164)
 def test_valid_map(self):self.assertEqual(len(self.check()[0]),1164)
 def test_missing_row(self):
  with self.assertRaises(self.gate.GateFailure):self.check(rows=self.rows[:-1])
 def test_reordered_rows(self):
  with self.assertRaises(self.gate.GateFailure):self.check(rows=list(reversed(self.rows)))
 def test_missing_target(self):
  with self.assertRaises(self.gate.GateFailure):self.check(targets=self.targets[1:])
 def test_duplicate_target(self):
  with self.assertRaises(self.gate.GateFailure):self.check(targets=self.targets+[self.targets[-1]])
 def test_changed_target_name(self):
  targets=self.targets.copy();targets[0]=replace(targets[0],declaration='Komorebi.PaperIV.NONEXISTENT')
  with self.assertRaises(self.gate.GateFailure):self.check(targets=targets)
 def test_wrong_record_label(self):
  targets=self.targets.copy();targets[0]=replace(targets[0],record_labels=('thm:NONEXISTENT',))
  with self.assertRaises(self.gate.GateFailure):self.check(targets=targets)
 def test_unknown_record_number(self):
  rows=self.rows.copy();rows[0]=replace(rows[0],record_numbers=('999.999',))
  with self.assertRaises(self.gate.GateFailure):self.check(rows=rows)
 def test_downgraded_evidence(self):
  records=self.records.copy();key=next(k for k,r in records.items() if r.kind in self.gate.RESULT_KINDS and r.evidence=='P + L(full)');records[key]=replace(records[key],evidence='P + L(partial)')
  with self.assertRaises(self.gate.GateFailure):self.check(records=records)
 def test_missing_manuscript_record(self):
  records=self.records.copy();del records[self.rows[0].record_numbers[0]]
  with self.assertRaises(self.gate.GateFailure):self.check(records=records)

class AxiomParserTests(unittest.TestCase):
 def parse(self,text):return replay.check_axiom_reports(text,{'A.x','A.y'})
 def test_valid(self):self.assertEqual(self.parse("'A.x' depends on axioms: [propext, Quot.sound]\n'A.y' does not depend on any axioms\n")['names'],2)
 def test_multiline(self):self.assertEqual(self.parse("'A.x' depends on axioms: [propext,\n Classical.choice]\n'A.y' does not depend on any axioms\n")['names'],2)
 def test_missing(self):
  with self.assertRaises(ValueError):self.parse("'A.x' does not depend on any axioms\n")
 def test_extra(self):
  with self.assertRaises(ValueError):self.parse("'A.x' does not depend on any axioms\n'A.y' does not depend on any axioms\n'A.z' does not depend on any axioms\n")
 def test_duplicate(self):
  with self.assertRaises(ValueError):self.parse("'A.x' does not depend on any axioms\n'A.y' does not depend on any axioms\n'A.x' does not depend on any axioms\n")
 def test_custom_axiom(self):
  with self.assertRaises(ValueError):self.parse("'A.x' depends on axioms: [evil]\n'A.y' does not depend on any axioms\n")
 def test_sorry(self):
  with self.assertRaises(ValueError):self.parse("'A.x' depends on axioms: [sorryAx]\n'A.y' does not depend on any axioms\n")
 def test_empty(self):
  with self.assertRaises(ValueError):self.parse('')
 def test_malformed(self):
  with self.assertRaises(ValueError):self.parse("'A.x' depends on axioms: [propext\n'A.y' does not depend on any axioms\n")
 def test_sentinel_only_not_proof(self):
  with self.assertRaises(ValueError):self.parse('FAIL-CLOSED PAPER IV v1.0.0 KERNEL AUDIT PASS')

class DiagnosticTests(unittest.TestCase):
 def test_positive(self):self.assertTrue(replay.diagnostic_accept({'returncode':0,'timed_out':False},'PAPER_IV_POSITIVE_CONTROL_PASS','positive'))
 def test_positive_error_code(self):self.assertFalse(replay.diagnostic_accept({'returncode':1,'timed_out':False},'PAPER_IV_POSITIVE_CONTROL_PASS','positive'))
 def test_positive_missing_marker(self):self.assertFalse(replay.diagnostic_accept({'returncode':0,'timed_out':False},'','positive'))
 def test_false_rejected(self):self.assertTrue(replay.diagnostic_accept({'returncode':1,'timed_out':False},'error: decide proposition false','false'))
 def test_unrelated_failure(self):self.assertFalse(replay.diagnostic_accept({'returncode':1,'timed_out':False},'error: missing object file','false'))
 def test_zero_exit_negative(self):self.assertFalse(replay.diagnostic_accept({'returncode':0,'timed_out':False},'error: decide proposition false','false'))
 def test_timeout_is_not_rejection(self):self.assertFalse(replay.diagnostic_accept({'returncode':1,'timed_out':True},'error: decide proposition false','false'))
 def test_signal_is_not_rejection(self):self.assertFalse(replay.diagnostic_accept({'returncode':-9,'timed_out':False},'error: decide proposition false','false'))
 def test_sorry_marker_required(self):self.assertFalse(replay.diagnostic_accept({'returncode':1,'timed_out':False},'error: malformed input','sorry'))
 def test_axiom_marker_required(self):self.assertFalse(replay.diagnostic_accept({'returncode':1,'timed_out':False},'error: unknown collectAxioms','custom-axiom'))
 def test_kind_marker_required(self):self.assertFalse(replay.diagnostic_accept({'returncode':1,'timed_out':False},'error: invalid environment API','wrong-kind'))
 def test_missing_premise_marker_required(self):self.assertFalse(replay.diagnostic_accept({'returncode':1,'timed_out':False},'error: missing import','missing-premise'))

class ProcessTests(unittest.TestCase):
 def test_success(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);r=replay.execute([sys.executable,'-c','print("ok")'],p,os.environ.copy(),5,p/'out.log');self.assertEqual(r['returncode'],0);self.assertFalse(r['timed_out'])
 def test_nonzero(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);r=replay.execute([sys.executable,'-c','raise SystemExit(7)'],p,os.environ.copy(),5,p/'out.log');self.assertEqual(r['returncode'],7)
 def test_timeout(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);r=replay.execute([sys.executable,'-c','import time;time.sleep(20)'],p,os.environ.copy(),0.15,p/'out.log');self.assertTrue(r['timed_out']);self.assertNotEqual(r['returncode'],0)
 @unittest.skipUnless(os.name=='posix','POSIX process groups only')
 def test_timeout_kills_descendant(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);marker=p/'child_survived';ready=p/'ready'
   child=f'from pathlib import Path;import time;Path({str(ready)!r}).write_text("READY");time.sleep(1.0);Path({str(marker)!r}).write_text("survived")'
   parent=f'import subprocess,sys,time;subprocess.Popen([sys.executable,"-c",{child!r}]);time.sleep(20)'
   r=execute_ready([sys.executable,'-c',parent],p,ready,p/'out.log',startup_timeout=5,execution_timeout=0.2)
   self.assertTrue(r['ready']);self.assertEqual(r['timeout_stage'],'execution');time.sleep(1.1);self.assertFalse(marker.exists())
 @unittest.skipUnless(os.name=='posix','POSIX process groups only')
 def test_readiness_delayed_start(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);ready=p/'ready';cmd=f'import time;from pathlib import Path;time.sleep(0.4);Path({str(ready)!r}).write_text("READY");time.sleep(0.05)'
   r=execute_ready([sys.executable,'-c',cmd],p,ready,p/'out.log',startup_timeout=5,execution_timeout=1)
   self.assertTrue(r['ready']);self.assertFalse(r['timed_out']);self.assertEqual(r['returncode'],0)
 @unittest.skipUnless(os.name=='posix','POSIX process groups only')
 def test_readiness_startup_hang(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);r=execute_ready([sys.executable,'-c','import time;time.sleep(20)'],p,p/'ready',p/'out.log',startup_timeout=0.2,execution_timeout=1)
   self.assertFalse(r['ready']);self.assertEqual(r['timeout_stage'],'startup')
 @unittest.skipUnless(os.name=='posix','POSIX process groups only')
 def test_readiness_early_failure(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);r=execute_ready([sys.executable,'-c','raise SystemExit(7)'],p,p/'ready',p/'out.log')
   self.assertFalse(r['ready']);self.assertFalse(r['timed_out']);self.assertEqual(r['returncode'],7)
 @unittest.skipUnless(os.name=='posix','POSIX process groups only')
 def test_readiness_stale_file_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);ready=p/'ready';ready.write_text('READY')
   with self.assertRaises(ValueError):execute_ready([sys.executable,'-c','print("ok")'],p,ready,p/'out.log')


if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]);result=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'schema':'paper_iv.verifier_tests.v1','status':'PASS' if result.wasSuccessful() else 'FAILED','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'scope':'Python verifier/API/diagnostic/process controls, not Lean theorem counts.'}
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n')
 sys.exit(0 if result.wasSuccessful() else 1)
