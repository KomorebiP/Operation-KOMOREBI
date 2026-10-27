#!/usr/bin/env python3
"""Rerun the original CPU numerical/regression suite from the preserved source ZIP.

This checks numerical formulas and historical corpus metadata. It does NOT execute
new GPU benchmarks or verify the historical timing measurements. Author: Komorebi P.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import time
import traceback
import zipfile

for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
sys.dont_write_bytecode = True

def main() -> int:
    base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=base/'verification/numerical_rerun.json')
    args = parser.parse_args()
    archive = base/'manuscript/Original_Paper_VIII_Package.zip'
    report = {'started_utc': datetime.now(timezone.utc).isoformat(),
              'source_zip_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'python': platform.python_version(),
              'scope': 'Original CPU numerical/regression suite and historical corpus consistency only',
              'new_gpu_benchmarks': False, 'hardware_timings_independently_reproduced': False}
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix='prsc_viii_numerical_') as tmp:
            root = Path(tmp)
            with zipfile.ZipFile(archive) as z:
                for name in z.namelist():
                    p = Path(name)
                    if p.is_absolute() or '..' in p.parts:
                        raise ValueError('Unsafe archive member: '+name)
                z.extractall(root)
            candidates = list(root.rglob('verification/run_full_verification.py'))
            if len(candidates) != 1:
                raise ValueError(f'Expected one suite, found {len(candidates)}')
            source = candidates[0]
            sys.path.insert(0, str(source.parents[1]))
            spec = importlib.util.spec_from_file_location('paper_viii_original_suite', source)
            if spec is None or spec.loader is None:
                raise RuntimeError('Cannot load original suite')
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            import numpy
            report['numpy'] = numpy.__version__
            report['result'] = mod.run()
            report['pass'] = report['result'].get('status') == 'passed'
    except Exception:
        report['pass'] = False
        report['failure'] = traceback.format_exc()
    report['seconds'] = round(time.monotonic()-start,3)
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    return 0 if report['pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
