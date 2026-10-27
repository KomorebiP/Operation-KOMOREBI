#!/usr/bin/env python3
"""Regenerate Block80 scientific outputs from bundled exact code/input copies.

This does not assert the integrity of excluded nested archives. The fresh
archival replay is a separately recorded observation requiring the original ZIP.
No archived code or input is changed. No actual arithmetic target is evaluated.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

SNAPSHOT = Path('evidence/computation/inputs/block80')
RESULTS = ('primary80.json', 'independent80.json', 'independent80_extra.json', 'target_evaluator80.json')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    ns = p.parse_args()
    ns.output.mkdir(parents=True, exist_ok=True)
    inputs = sorted(x for x in SNAPSHOT.rglob('*') if x.is_file())
    before = {x.as_posix(): sha(x) for x in inputs}
    expected = {name: json.loads((SNAPSHOT/'work80/verification'/name).read_text()) for name in RESULTS}
    jobs = []
    with tempfile.TemporaryDirectory(prefix='beal80_portable_science_') as td:
        root = Path(td)/'project'
        shutil.copytree(SNAPSHOT, root)
        for name in RESULTS:
            (root/'work80/verification'/name).unlink()
        (root/'work80/inputs/finite_inputs.json').unlink()
        for script, args in [('build_inputs.py', []), ('primary80.py', []), ('independent80.py', []), ('evaluate_target.py', ['--self-test'])]:
            argv = [sys.executable, '-B', 'work80/computations/'+script, *args]
            start = time.monotonic()
            cp = subprocess.run(argv, cwd=root, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), capture_output=True, text=True, timeout=120)
            jobs.append({'argv': argv, 'runtime_seconds': time.monotonic()-start, 'exit_status': cp.returncode, 'stdout': cp.stdout, 'stderr': cp.stderr})
            if cp.returncode:
                raise RuntimeError(script+' failed: '+cp.stdout+cp.stderr)
        if (root/'work80/inputs/finite_inputs.json').read_bytes() != (SNAPSHOT/'work80/inputs/finite_inputs.json').read_bytes():
            raise ValueError('rebuilt fixture changed')
        for name in RESULTS:
            result = root/'work80/verification'/name
            if json.loads(result.read_text()) != expected[name]:
                raise ValueError('complete result mismatch: '+name)
            shutil.copyfile(result, ns.output/name)
        shutil.copyfile(root/'work80/inputs/finite_inputs.json', ns.output/'finite_inputs.json')
    if expected['primary80.json'] != expected['independent80.json']:
        raise ValueError('separate arithmetic implementations disagree')
    after = {x.as_posix(): sha(x) for x in inputs}
    if before != after:
        raise ValueError('bundled input changed')
    report = {'status': 'PASS_SCIENTIFIC_REPLAY', 'scientific_outputs_regenerated': list(RESULTS),
              'input_fixture_regenerated': True, 'entire_result_comparisons': 4, 'jobs': jobs,
              'input_hashes_before': before, 'input_hashes_after': after,
              'actual_arithmetic_target_computed': False, 'patterns_eliminated': 0,
              'nested_archive_integrity_reasserted': False,
              'nonclaims': ['No actual global primitive or arithmetic target is supplied.',
                            'Finite outputs do not prove the classical duality theorem or the inherited Frey geometry.',
                            'This portable scientific replay does not rerun the whole historical chain.']}
    (ns.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'])
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
