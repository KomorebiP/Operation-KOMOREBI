#!/usr/bin/env python3
"""Reproduce the chosen active source build and evidence checks with the pinned portable runtime."""
import argparse,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser(description=__doc__);a.add_argument('--runtime',required=True,type=Path);x=a.parse_args();rt=str(x.runtime.resolve())
for args in [['verify_blocks.py','--runtime',rt,'--timeout','120','--clean'],['checks/negative_controls.py','--runtime',rt],['checks/test_cached.py','results/reproduced_diagnostics.json'],['checks/seal.py','--runtime',rt],['checks/benchmark_report.py']]:
    subprocess.run([sys.executable,*args],cwd=r,check=True)
print('Clean build and evidence checks completed. Historical benchmark timings are retained; rerun benchmark_cached.py for new timings.')
