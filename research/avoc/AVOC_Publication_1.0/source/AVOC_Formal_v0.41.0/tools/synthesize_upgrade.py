#!/usr/bin/env python3
"""Bounded grammar search -> proved equivalence -> inherited paid promotion gate.

Fresh one-shot campaigns only. Program data is interpreted by Lean, never installed
as arbitrary source. SQLite/host and this adapter are tested trust boundaries.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Iterator

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'avoc-generated-program-store-v1'
MAX_FILE = 262144
KEYS = {'reference', 'deployment_calls', 'credits', 'grammar_depth', 'trial_limit', 'search_credit'}


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON key: ' + key)
        out[key] = value
    return out


def loads(text: str) -> Any:
    return json.loads(text, object_pairs_hook=unique)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def natural(value: Any, name: str, maximum: int = 100000000) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f'{name} must be an integer in [0,{maximum}]')
    return value


def program_size(p: Any, depth: int = 0) -> int:
    if depth >= 32 or not isinstance(p, list) or not p or type(p[0]) is not str:
        raise ValueError('invalid or excessively nested program data')
    op = p[0]
    if op == 'literal' and len(p) == 2 and type(p[1]) is bool:
        return 1
    if op == 'variable' and len(p) == 2:
        natural(p[1], 'variable index', 2)
        return 1
    if op == 'not' and len(p) == 2:
        return 1 + program_size(p[1], depth+1)
    if op in {'and', 'or', 'xor'} and len(p) == 3:
        return 1 + program_size(p[1], depth+1) + program_size(p[2], depth+1)
    raise ValueError('unknown or malformed pure program constructor')


def validate_config(config: Any) -> list[Any]:
    if not isinstance(config, dict) or set(config) != KEYS:
        raise ValueError('configuration must have exactly: ' + ', '.join(sorted(KEYS)))
    if program_size(config['reference']) > 127:
        raise ValueError('reference size exceeds 127 nodes')
    calls = natural(config['deployment_calls'], 'deployment_calls')
    total = natural(config['credits'], 'credits')
    depth = natural(config['grammar_depth'], 'grammar_depth', 2)
    limit = natural(config['trial_limit'], 'trial_limit', 21845)
    budget = natural(config['search_credit'], 'search_credit')
    if budget > total:
        raise ValueError('search_credit exceeds total credits')
    return [config['reference'], calls, total, depth, limit, budget]


def load_config(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE:
        raise ValueError('invalid configuration file')
    config = loads(path.read_text(encoding='utf-8'))
    validate_config(config)
    return config


def environment() -> tuple[Path, dict[str, str], dict[str, Any]]:
    kit = Path(os.environ.get('AVOC_LEAN_KIT', '/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
    lean = kit / 'toolchain/bin/lean'
    pins_path = ROOT / 'synthesis_source_pins.json'
    if not lean.is_file() or not pins_path.is_file():
        raise RuntimeError('missing runtime/pins; follow REPRODUCE.md')
    pins = loads(pins_path.read_text())
    for rel, expected in pins['sources'].items():
        p = ROOT / rel
        if not p.is_file() or sha(p) != expected:
            raise RuntimeError('protected source drift: ' + rel)
    version = subprocess.check_output([str(lean), '--version'], text=True, timeout=10).strip()
    if version != pins['lean_version'] or sha(lean) != pins['lean_sha256']:
        raise RuntimeError('pinned Lean runtime mismatch')
    build = ROOT / '.lake/build/lib/lean'
    outputs = {}
    for rel in pins['targets']:
        path = ROOT / rel
        out = build / Path(rel).with_suffix('.olean')
        record = ROOT / 'results/v0.25.0' / ('clean_' + path.stem + '.json')
        if not out.is_file() or not record.is_file():
            raise RuntimeError('missing checked compilation: ' + rel)
        r = loads(record.read_text())
        if r['returncode'] != 0 or r['timed_out'] or r['source_sha256'] != sha(path) or r['output_sha256'] != sha(out):
            raise RuntimeError('stale checked compilation: ' + rel)
        for name, expected in r.get('import_outputs', {}).items():
            dep = build / Path(name.replace('.', '/')).with_suffix('.olean')
            if not dep.is_file() or sha(dep) != expected:
                raise RuntimeError('compiled local import mismatch: ' + name)
        outputs[rel] = sha(out)
    env = os.environ.copy()
    env['LEAN_PATH'] = str(build)
    env['PATH'] = str(kit / 'toolchain/bin') + ':' + env.get('PATH', '')
    return lean, env, {'sources': pins['sources'], 'outputs': outputs, 'lean_version': version, 'lean_sha256': sha(lean)}


def call(wire: Any, timeout: int = 60) -> tuple[dict[str, Any], dict[str, Any]]:
    lean, env, before = environment()
    with tempfile.TemporaryDirectory(prefix='avoc-synthesis-request-') as td:
        path = Path(td) / 'request.json'
        text = canonical(wire)
        if len(text.encode()) > MAX_FILE:
            raise ValueError('wire size limit')
        path.write_text(text, encoding='utf-8')
        start = time.monotonic()
        p = subprocess.run([str(lean), '--run', str(ROOT / 'tools/SynthesisMain.lean'), str(path)],
                           cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
        elapsed = time.monotonic() - start
    if environment()[2] != before:
        raise RuntimeError('checker environment changed during invocation')
    try:
        out = loads(p.stdout)
    except ValueError as exc:
        raise RuntimeError('invalid Lean output: ' + p.stderr) from exc
    if p.returncode != 0 or out.get('status') != 'checked':
        raise RuntimeError('Lean rejected: ' + str(out.get('error', p.stderr)))
    record = {'elapsed_seconds': elapsed, 'returncode': p.returncode,
              'wire_sha256': hashlib.sha256(text.encode()).hexdigest(),
              'stdout_sha256': hashlib.sha256(p.stdout.encode()).hexdigest(), 'stderr': p.stderr}
    return out, record


def expected_search(config: dict[str, Any]) -> tuple[int, int, int]:
    count, generation, bound = 5, 5, 1
    for _ in range(config['grammar_depth']):
        count = 2*count + 3*count*count
        generation += count
        bound = 2*bound + 1
    budget = config['search_credit']
    if generation > budget:
        return 0, 0, 0
    fee = 8 * (program_size(config['reference']) + bound + 1)
    tested = min(count, config['trial_limit'], (budget-generation)//fee)
    return generation, tested*fee, tested


def validate_result(config: dict[str, Any], result: dict[str, Any]) -> None:
    if result.get('status') != 'checked' or result.get('job') != validate_config(config):
        raise ValueError('result/job mismatch')
    generation, checks, tested = expected_search(config)
    if (result['generation_charge'], result['candidate_evaluation_charge'], result['tested']) != (generation, checks, tested):
        raise ValueError('search accounting mismatch')
    journal = result['journal']
    if result['active'] != journal[0][1] or result['reference_nodes'] != program_size(config['reference']):
        raise ValueError('active pointer/reference mismatch')
    if result['candidate_nodes'] != program_size(result['candidate']) or result['active_nodes'] != program_size(result['active']):
        raise ValueError('program size mismatch')
    costs = generation + checks + journal[0][4] + journal[0][5]
    if costs != result['total_charge'] or costs > config['credits']:
        raise ValueError('total credit mismatch')
    gain = config['deployment_calls'] * (program_size(config['reference']) - program_size(result['active']))
    if result['net'] != gain-costs or result['credits_remaining'] != config['credits']-costs:
        raise ValueError('utility/accounting mismatch')


@contextmanager
def locked(directory: Path) -> Iterator[None]:
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError('expected protected run directory')
    fd = os.open(directory/'LOCK', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def connect(directory: Path, create: bool = False) -> sqlite3.Connection:
    path = directory/'campaign.sqlite3'
    if path.is_symlink() or (not create and not path.is_file()):
        raise ValueError('missing/symlink campaign database')
    db = sqlite3.connect(str(path), isolation_level=None, timeout=3)
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=FULL')
    return db


def start(config: dict[str, Any], directory: Path, *, timeout: int = 60,
          hook: Callable[[str], None] = lambda _: None) -> dict[str, Any]:
    jw = validate_config(config)
    _, _, fingerprint = environment()
    directory = directory.absolute()
    directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    with locked(directory):
        header = {'format': VERSION, 'job': config, 'environment': fingerprint}
        hp = directory/'authority.json'
        with hp.open('x', encoding='utf-8') as f:
            f.write(canonical(header)+'\n'); f.flush(); os.fsync(f.fileno())
        db = connect(directory, True)
        try:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE run(id INTEGER PRIMARY KEY CHECK(id=1), header TEXT NOT NULL, phase TEXT NOT NULL, reservation INTEGER NOT NULL, result TEXT, result_hash TEXT, invocation TEXT)')
            # Reserve the entire declared envelope BEFORE any candidate generation.
            # If execution is interrupted, it remains held. This one-shot adapter
            # does not authorize an uncharged retry or guess an outcome.
            db.execute('INSERT INTO run VALUES(1,?,?,?,?,?,?)',
                       (canonical(header), 'reserved', config['credits'], None, None, None))
            db.commit()
            hook('after_reservation')
            result, record = call(['avoc-synthesis-v1', jw], timeout)
            validate_result(config, result)
            hook('after_search')
            if environment()[2] != fingerprint:
                raise RuntimeError('environment drift before publication')
            data = canonical(result)
            db.execute('BEGIN IMMEDIATE')
            db.execute('UPDATE run SET phase=?, reservation=?, result=?, result_hash=?, invocation=? WHERE id=1',
                       ('completed', result['total_charge'], data, hashlib.sha256(data.encode()).hexdigest(), canonical(record)))
            hook('inside_commit')
            db.commit()
            hook('after_commit')
            return {**result, 'phase':'completed', 'reserved_or_charged':result['total_charge'],
                    'execution_record':record, 'run_dir':str(directory)}
        finally:
            db.close()


def inspect(directory: Path, invoke: bool = False) -> dict[str, Any]:
    directory = directory.absolute()
    with locked(directory):
        db = connect(directory)
        try:
            row = db.execute('SELECT header,phase,reservation,result,result_hash,invocation FROM run WHERE id=1').fetchone()
        finally:
            db.close()
        if row is None:
            raise RuntimeError('incomplete initialization')
        header = loads(row[0])
        hp = directory/'authority.json'
        if hp.is_symlink() or loads(hp.read_text()) != header or header['format'] != VERSION:
            raise RuntimeError('frozen authority mismatch')
        if header['environment'] != environment()[2]:
            raise RuntimeError('environment drift')
        config = header['job']; validate_config(config)
        if row[1] == 'reserved':
            if row[2] != config['credits'] or row[3] is not None:
                raise RuntimeError('malformed unresolved reservation')
            if invoke:
                raise RuntimeError('unconfirmed search cannot dispatch a generated replacement')
            return {'phase':'unconfirmed_search', 'reserved_or_charged':row[2], 'reexecuted_search':False,
                    'message':'The prepaid search has no committed result. No automatic retry or refund.'}
        if row[1] != 'completed' or row[3] is None or hashlib.sha256(row[3].encode()).hexdigest() != row[4]:
            raise RuntimeError('result checksum/phase mismatch')
        result = loads(row[3]); validate_result(config,result)
        if row[2] != result['total_charge']:
            raise RuntimeError('retained cost mismatch')
        charge = result['generation_charge'] + result['candidate_evaluation_charge']
        confirmed, record = call(['avoc-synthesis-inspect-v1',validate_config(config),charge,
                                  result['commands'],result['journal']])
        if confirmed['active'] != result['active'] or confirmed['journal'] != result['journal']:
            raise RuntimeError('replay/active mismatch')
        return {**result,'phase':'completed','reserved_or_charged':row[2],
                'reexecuted_search':False,'replay_record':record,
                'executions':confirmed['executions'] if invoke else None}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sp = p.add_subparsers(dest='action', required=True)
    a=sp.add_parser('run'); a.add_argument('config',type=Path); a.add_argument('--run-dir',type=Path,required=True);a.add_argument('--timeout',type=int,default=60)
    a=sp.add_parser('search');a.add_argument('config',type=Path);a.add_argument('--timeout',type=int,default=60)
    for name in ['inspect','invoke']:
        a=sp.add_parser(name);a.add_argument('--run-dir',type=Path,required=True)
    ns=p.parse_args()
    try:
        if ns.action == 'run': out=start(load_config(ns.config), ns.run_dir,timeout=ns.timeout)
        elif ns.action == 'search':
            config=load_config(ns.config);out,_=call(['avoc-synthesis-v1',validate_config(config)],ns.timeout);validate_result(config,out)
        else: out=inspect(ns.run_dir,ns.action=='invoke')
        print(json.dumps(out,indent=2));return 0
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError,sqlite3.Error) as e:
        print(json.dumps({'status':'error','error':str(e)}),file=sys.stderr);return 2


if __name__=='__main__':
    raise SystemExit(main())
