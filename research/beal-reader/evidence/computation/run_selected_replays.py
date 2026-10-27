#!/usr/bin/env python3
"""Run the documented selected historical defaults under version-2 provenance.

Run from the released project root. Completed run directories are never reused.
The archive wrapper extracts each predecessor privately. Existing evidence is
kept, so a repeat must use --suffix with a new value.
"""
from __future__ import annotations
import argparse, concurrent.futures, json, subprocess, sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--blocks', nargs='+', type=int, choices=range(67, 81), default=list(range(67, 79)))
    p.add_argument('--suffix', default='run')
    p.add_argument('--workers', type=int, choices=(1, 2), default=2)
    ns = p.parse_args()
    root = Path('.').resolve()
    archive = 'evidence/recovered/Komorebi_Beal_Block80_Restricted_Primitive_Affine_Obstruction_v8.0.0.zip'
    def one(n):
        output = f'evidence/computation/block{n}-{ns.suffix}'
        contract = f'evidence/computation/contracts/block{n}.json'
        argv = [sys.executable, 'evidence/computation/tools/run_experiment.py', '--root', str(root),
                '--contract', contract, '--input', 'evidence/computation/replay_archive.py',
                '--input', archive, '--input', contract, '--output', output,
                '--timeout', '900', '--max-output-bytes', '2097152', '--max-memory-bytes', '2147483648',
                '--max-cpu-seconds', '800', '--max-cores', '1', '--max-threads', '1']
        for result in ('report.json', 'extraction_and_invocation.json', 'verifier_stdout.txt', 'verifier_stderr.txt'):
            argv.extend(['--result', output + '/' + result])
        argv.extend(['--', sys.executable, '-B', 'evidence/computation/replay_archive.py',
                     '--block', str(n), '--output', output])
        if n == 80:
            argv.append('--immediate-predecessor')
        result = subprocess.run(argv, capture_output=True, text=True)
        print(json.dumps({'block': n, 'exit_status': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}), flush=True)
        return result.returncode
    with concurrent.futures.ThreadPoolExecutor(max_workers=ns.workers) as pool:
        statuses = list(pool.map(one, ns.blocks))
    return int(any(statuses))

if __name__ == '__main__':
    raise SystemExit(main())
