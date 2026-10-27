#!/usr/bin/env python3
"""Actual-process controls for the opt-in readiness protocol. No simulated Lean run."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("paper_v_readiness", ROOT/"verification/verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

class ReadinessControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="paper_v_readiness_test_")
        self.root = Path(self.temp.name)
        self.log = self.root/"child.log"
    def tearDown(self):
        self.temp.cleanup()
    def child(self, code, **kwargs):
        return verify.run([sys.executable, "-c", code], self.root, self.log, **kwargs)
    def test_delayed_start_has_own_budget(self):
        # A minimal successful child avoids timing unrelated interpreter finalizers.
        # Its deliberate startup delay still exceeds the entire execution budget.
        result = self.child('import time,os;time.sleep(1.25);print("READY",flush=True);print("done",flush=True);os._exit(0)',
                            timeout=1,ready_token="READY",startup_timeout=15)
        self.assertIn("done",result.stdout)
    def test_post_ready_timeout_keeps_output(self):
        with self.assertRaisesRegex(verify.VerificationError,"timed out after readiness"):
            self.child('import time;print("READY",flush=True);print("payload",flush=True);time.sleep(20)',
                       timeout=.1,ready_token="READY",startup_timeout=10)
        self.assertIn("payload",self.log.read_text())
        self.assertIn("TIMEOUT",self.log.read_text())
    def test_missing_readiness_times_out(self):
        with self.assertRaisesRegex(verify.VerificationError,"readiness timed out"):
            self.child('import time;time.sleep(20)',timeout=2,ready_token="READY",startup_timeout=.2)
        self.assertIn("STARTUP TIMEOUT",self.log.read_text())
    def test_exit_before_ready_is_not_success(self):
        with self.assertRaisesRegex(verify.VerificationError,"exited before readiness"):
            self.child('print("no readiness");raise SystemExit(0)',timeout=2,ready_token="READY",startup_timeout=10)
        self.assertIn("READINESS FAILURE",self.log.read_text())
    def test_nonzero_after_ready_stays_failure(self):
        with self.assertRaisesRegex(verify.VerificationError,"exited 9"):
            self.child('print("READY",flush=True);raise SystemExit(9)',timeout=2,ready_token="READY",startup_timeout=10)
    def test_marker_requires_whole_line(self):
        with self.assertRaisesRegex(verify.VerificationError,"exited before readiness"):
            self.child('print("NOT_READY_extra",flush=True)',timeout=2,ready_token="READY",startup_timeout=10)
    def test_large_pre_ready_output_does_not_block(self):
        result = self.child('print("x"*200000,flush=True);print("READY",flush=True)',
                            timeout=2,ready_token="READY",startup_timeout=10)
        self.assertGreater(len(result.stdout),200000)
    def test_invalid_timeouts_rejected(self):
        for value in (0,-1,float("inf"),float("nan")):
            with self.assertRaises(verify.VerificationError):
                self.child('print("READY")',timeout=value,ready_token="READY")
            with self.assertRaises(verify.VerificationError):
                self.child('print("READY")',timeout=1,ready_token="READY",startup_timeout=value)
    def test_invalid_marker_rejected(self):
        for marker in ("", "a\nb", "a\rb"):
            with self.assertRaises(verify.VerificationError):
                self.child('print("READY")',timeout=1,ready_token=marker)
    def test_launch_error_recorded(self):
        with self.assertRaisesRegex(verify.VerificationError,"could not start"):
            verify.run([str(self.root/"nonexistent")],self.root,self.log,timeout=1,ready_token="READY")
        self.assertIn("PROCESS NOT STARTED",self.log.read_text())

if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--report",type=Path);args=parser.parse_args()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReadinessControls))
    data={"status":"PASS" if result.wasSuccessful() else "FAIL", "tests_run":result.testsRun,
          "failures":len(result.failures),"errors":len(result.errors),"lean_kernel_checked":False}
    if args.report:args.report.write_text(json.dumps(data,indent=2)+"\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
