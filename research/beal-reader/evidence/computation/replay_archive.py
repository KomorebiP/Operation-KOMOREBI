#!/usr/bin/env python3
"""Replay one authorized historical block without altering its archived bytes.

Only the original archive's verified predecessor chain is traversed. Each run
extracts a private copy, invokes that block's documented default verifier, and
copies its report outside the private payload. Block80 may additionally request
the documented immediate Block79 default replay. No full-chain execution is
inferred from that option.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, subprocess, sys, tempfile, time, zipfile
from pathlib import Path, PurePosixPath

ARCHIVE = Path('evidence/recovered/Komorebi_Beal_Block80_Restricted_Primitive_Affine_Obstruction_v8.0.0.zip')
ARCHIVE_SHA = 'cd5ed533e11d5d7202afc38293bf47d8134f94b758738d3931a317e808cddc0e'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def safe_zip(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()
    if len(names) != len(set(names)):
        raise ValueError('duplicate member')
    for info in z.infolist():
        p = PurePosixPath(info.filename)
        if p.is_absolute() or '..' in p.parts or (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError('unsafe or symlink archive member')
    if z.testzip() is not None:
        raise ValueError('archive CRC failure')
    return z

def select(block):
    raw = ARCHIVE.read_bytes()
    if digest(raw) != ARCHIVE_SHA:
        raise ValueError('original Block80 archive changed')
    chain = []
    for current in range(80, block - 1, -1):
        z = safe_zip(raw)
        chain.append({'block': current, 'archive_sha256': digest(raw), 'bytes': len(raw)})
        if current == block:
            return raw, chain
        predecessors = [n for n in z.namelist() if '/predecessor/' in '/' + n and n.endswith('.zip')]
        if len(predecessors) != 1:
            raise ValueError('ambiguous predecessor chain at Block' + str(current))
        raw = z.read(predecessors[0])
    raise ValueError('selected block not found')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--block', type=int, required=True, choices=range(67, 81))
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--immediate-predecessor', action='store_true')
    ns = p.parse_args()
    if ns.immediate_predecessor and ns.block != 80:
        p.error('This wrapper authorizes the immediate-predecessor option only for Block80')
    out = ns.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    raw, chain = select(ns.block)
    with tempfile.TemporaryDirectory(prefix='komorebi_beal_replay_') as td:
        dest = Path(td) / 'payload'
        dest.mkdir()
        safe_zip(raw).extractall(dest)
        roots = list(dest.rglob('verify.py'))
        if len(roots) != 1:
            raise ValueError('extracted verifier ambiguity')
        source = roots[0]
        argv = [sys.executable, '-B', 'verify.py', '--report', str(out / 'report.json')]
        if ns.immediate_predecessor:
            argv.append('--replay-predecessor')
        if ns.block in (69, 70):
            argv.extend(['--workers', '1', '--job-timeout', '600'])
        elif ns.block in (67, 68):
            argv.extend(['--job-timeout', '600'])
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        start = time.monotonic()
        run = subprocess.run(argv, cwd=source.parent, env=env, capture_output=True, text=True, timeout=840)
        (out / 'verifier_stdout.txt').write_text(run.stdout)
        (out / 'verifier_stderr.txt').write_text(run.stderr)
        metadata = {'block': ns.block, 'argv': argv, 'extracted_working_directory': str(source.parent),
                    'selected_archive_chain': chain, 'runtime_seconds': time.monotonic() - start,
                    'exit_status': run.returncode, 'default_only': not ns.immediate_predecessor,
                    'full_historical_chain_replayed': False, 'archive_sha256_after': digest(ARCHIVE.read_bytes())}
        (out / 'extraction_and_invocation.json').write_text(json.dumps(metadata, indent=2) + '\n')
        if run.returncode:
            print(run.stdout[-3000:] + run.stderr[-3000:], file=sys.stderr)
            return run.returncode
        report = json.loads((out / 'report.json').read_text())
        if report.get('status') != 'PASS_DECLARED_CHECKS':
            raise ValueError('Verifier did not report PASS_DECLARED_CHECKS')
        if metadata['archive_sha256_after'] != ARCHIVE_SHA:
            raise ValueError('Original archive changed during run')
        print('Block', ns.block, report['status'], round(metadata['runtime_seconds'], 3))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
