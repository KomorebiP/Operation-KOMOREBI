"""Run the declared finite atlas checks and emit a machine-readable result."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import unittest

from sequence_atlas import ROOT, catalogue

if __name__ == '__main__':
    # Node's test reporter emits Unicode even when launched from legacy Windows pipes.
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tools'),pattern='test_sequence_atlas.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    import os
    env=dict(os.environ,PYTHON=sys.executable)
    browser_core=subprocess.run([args.node,'--test','tools/test_sequence_atlas.mjs','tools/test_sequence_atlas_search.mjs'],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
    print(browser_core.stdout)
    print(browser_core.stderr,file=sys.stderr)
    report=dict(status='passed' if result.wasSuccessful() and browser_core.returncode==0 else 'failed',
        python_tests=result.testsRun,python_errors=len(result.errors),python_failures=len(result.failures),
        browser_core_exit=browser_core.returncode,entries=len(catalogue()),
        assertion_tested='Exact catalogue terms and bounded transforms agree with the documented independent implementations and source definitions over the tested ranges.',
        bounds=dict(reciprocal_N=[2,8],reciprocal_powers=[1,3],rational_oracle_terms=16,python_browser_terms=64,partition_recurrence_terms=32,second_difference_terms=64,successive_modular_fixture_terms=3),
        non_claims=['No new sequence or formula novelty','No global period or asymptotic result','No new formal or independent mathematical review'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if report['status']=='passed' else 1)
