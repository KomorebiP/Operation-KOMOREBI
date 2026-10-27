#!/usr/bin/env python3
"""Protected, single-writer durable promotion of a fixed compiled catalogue.

The Lean gate is authoritative for state transitions. SQLite publishes the
canonical command, campaign snapshot and dispatch pointer in one transaction.
A prepaid pending evaluation may be finished or explicitly abandoned. Finishing
may repeat PURE validation after interruption; no untrusted code is installed.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Iterator
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_upgrade_campaign import make_wire, unique_object, natural

SCHEMA = 'avoc-durable-upgrade-1'
MAX_EVENTS = 512
MAX_BYTES = 4 * 1024 * 1024
Hook = Callable[[str], None]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def load_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=unique_object)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_key(key: Any) -> str:
    if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9._-]{1,96}', key):
        raise ValueError('operation key must be 1-96 ASCII letters, digits, dot, dash or underscore')
    return key


def environment() -> tuple[Path, dict[str, str], dict[str, Any]]:
    pins = load_json((ROOT / 'durable_upgrade_source_pins.json').read_text())
    kit = Path(os.environ.get('AVOC_LEAN_KIT', '/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
    lean = kit / 'toolchain/bin/lean'
    if not lean.is_file():
        raise RuntimeError('missing pinned Lean runtime; follow REPRODUCE.md')
    for relative, expected in pins['sources'].items():
        path = ROOT / relative
        if not path.is_file() or sha(path) != expected:
            raise RuntimeError('protected source drift: ' + relative)
    outputs: dict[str, str] = {}
    for relative in pins['compiled_targets']:
        path = ROOT / relative
        output = ROOT / '.lake/build/lib/lean' / Path(relative).with_suffix('.olean')
        recfile = ROOT / 'results/v0.24.0' / ('clean_' + path.stem + '.json')
        if not output.is_file() or not recfile.is_file():
            raise RuntimeError('missing checked build: ' + relative)
        rec = load_json(recfile.read_text())
        if (rec['returncode'] != 0 or rec['timed_out'] or
                rec['source_sha256'] != sha(path) or rec['output_sha256'] != sha(output)):
            raise RuntimeError('stale checked build: ' + relative)
        for mod, expected in rec.get('import_outputs', {}).items():
            dep = ROOT / '.lake/build/lib/lean' / Path(mod.replace('.', '/')).with_suffix('.olean')
            if not dep.exists() or sha(dep) != expected:
                raise RuntimeError('compiled dependency drift: ' + mod)
        outputs[relative] = sha(output)
    version = subprocess.check_output([str(lean), '--version'], text=True, timeout=10).strip()
    if version != pins['lean_version'] or sha(lean) != pins['lean_binary_sha256']:
        raise RuntimeError('Lean runtime fingerprint mismatch')
    env = os.environ.copy()
    env['LEAN_PATH'] = ':'.join(map(str, [ROOT / '.lake/build/lib/lean'] + [
        p / '.lake/build/lib/lean' for p in sorted((kit / 'workspace/.lake/packages').iterdir()) if p.is_dir()]))
    env['PATH'] = str(kit / 'toolchain/bin') + ':' + env.get('PATH', '')
    fingerprint = {'sources': pins['sources'], 'compiled': outputs,
                   'lean_version': version, 'lean_binary_sha256': sha(lean)}
    return lean, env, fingerprint


def call_gate(wire: Any, run_dir: Path | None = None, timeout: int = 40) -> dict[str, Any]:
    lean, env, before = environment()
    text = canonical(wire)
    if len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('wire size limit')
    started = time.monotonic()
    proc = subprocess.run([str(lean), '--run', str(ROOT / 'tools/DurableUpgradeMain.lean')],
                          input=text, text=True, capture_output=True, cwd=ROOT, env=env,
                          timeout=timeout)
    elapsed = time.monotonic() - started
    if environment()[2] != before:
        raise RuntimeError('environment changed while executing gate')
    if run_dir is not None:
        folder = run_dir / 'diagnostics'
        folder.mkdir(exist_ok=True)
        tag = str(uuid.uuid4())
        (folder / (tag + '.json')).write_text(canonical({
            'request_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'stdout': proc.stdout, 'stderr': proc.stderr,
            'returncode': proc.returncode, 'seconds': elapsed}) + '\n')
    try:
        result = load_json(proc.stdout)
    except (ValueError, TypeError) as e:
        raise RuntimeError('Lean process did not return a valid response: ' + proc.stderr) from e
    if proc.returncode != 0 or result.get('status') != 'checked':
        raise RuntimeError('Lean gate rejected: ' + str(result.get('error', proc.stderr)))
    return result


def sync_file(path: Path, content: str) -> None:
    with path.open('x', encoding='utf-8') as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextmanager
def locked(directory: Path) -> Iterator[None]:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('expected a protected existing run directory')
    path = directory / 'CAMPAIGN_LOCK'
    if path.is_symlink():
        raise ValueError('symlink lock refused')
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as e:
            raise RuntimeError('campaign is locked by another cooperative writer') from e
        yield
    finally:
        os.close(fd)


def connection(path: Path, create: bool = False) -> sqlite3.Connection:
    if path.is_symlink() or (not create and not path.is_file()):
        raise ValueError('missing or symlink database')
    db = sqlite3.connect(str(path), timeout=3, isolation_level=None)
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('PRAGMA foreign_keys=ON')
    return db


def wire(credits: int, commands: list[Any], snapshot: Any, command: Any = None,
         invoke: bool = False) -> list[Any]:
    return ['avoc-durable-upgrade-v1', credits, commands, snapshot, command, invoke]


def start(run_dir: Path, credits: int) -> dict[str, Any]:
    natural(credits, 'credits', 10000)
    _, _, fingerprint = environment()
    header = {'format': SCHEMA, 'campaign': str(uuid.uuid4()), 'credits': credits,
              'environment': fingerprint}
    snapshot = [['dynamic', 'dynamic', 0, 0, 0, 0, 0], None, []]
    checked = call_gate(wire(credits, [], snapshot))
    run_dir = run_dir.absolute()
    run_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
    with locked(run_dir):
        sync_file(run_dir / 'authority.json', canonical(header) + '\n')
        db = connection(run_dir / 'campaign.sqlite3', create=True)
        try:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE meta(id INTEGER PRIMARY KEY CHECK(id=1), header TEXT NOT NULL, epoch INTEGER NOT NULL, snapshot TEXT NOT NULL, active TEXT NOT NULL, revision INTEGER NOT NULL)')
            db.execute('CREATE TABLE events(seq INTEGER PRIMARY KEY, command TEXT NOT NULL)')
            db.execute('CREATE TABLE requests(key TEXT PRIMARY KEY, epoch INTEGER NOT NULL, proposal TEXT NOT NULL, ticket TEXT NOT NULL)')
            db.execute('INSERT INTO meta VALUES(1,?,?,?,?,?)',
                       (canonical(header), 0, canonical(snapshot), 'dynamic', 0))
            db.commit()
        finally:
            db.close()
    return {**checked, 'epoch': 0, 'campaign': header['campaign'], 'operation': 'start'}


def read_store(db: sqlite3.Connection, run_dir: Path) -> tuple[dict[str, Any], int, Any, list[Any], dict[str, Any]]:
    row = db.execute('SELECT header,epoch,snapshot,active,revision FROM meta WHERE id=1').fetchone()
    if row is None:
        raise RuntimeError('incomplete campaign initialization')
    header, epoch, snapshot, active, revision = load_json(row[0]), row[1], load_json(row[2]), row[3], row[4]
    authority_path = run_dir / 'authority.json'
    if authority_path.is_symlink() or load_json(authority_path.read_text()) != header:
        raise RuntimeError('frozen authority record mismatch')
    if header['format'] != SCHEMA or header['environment'] != environment()[2]:
        raise RuntimeError('campaign environment/configuration changed')
    records = db.execute('SELECT seq,command FROM events ORDER BY seq').fetchall()
    if epoch != len(records) or [r[0] for r in records] != list(range(epoch)):
        raise RuntimeError('incomplete or reordered canonical event history')
    if epoch > MAX_EVENTS:
        raise RuntimeError('event limit')
    commands = [load_json(r[1]) for r in records]
    expected_keys = {}
    for seq, cmd in enumerate(commands):
        if cmd[0] == 'begin':
            t = cmd[1]
            if t[0] in expected_keys:
                raise RuntimeError('duplicate canonical begin key')
            expected_keys[t[0]] = (seq, t[2], t)
    requests = {}
    for key, seq, proposal, ticket in db.execute('SELECT key,epoch,proposal,ticket FROM requests'):
        requests[key] = (seq, load_json(proposal), load_json(ticket))
    if requests != expected_keys:
        raise RuntimeError('request/event identity mismatch')
    if active != snapshot[0][1] or revision != snapshot[0][2]:
        raise RuntimeError('deployed dispatch pointer differs from campaign checkpoint')
    # Actual semantic replay and exact checkpoint matching are performed by Lean.
    return header, epoch, snapshot, commands, requests


def operate(run_dir: Path, operation: str, *, key: str | None = None,
            proposal: Any = None, expected_epoch: int | None = None,
            hook: Hook | None = None) -> dict[str, Any]:
    if operation not in {'inspect', 'invoke', 'begin', 'finish', 'abandon'}:
        raise ValueError('unsupported operation')
    run_dir = run_dir.absolute()
    point: Hook = hook or (lambda _: None)
    if operation in {'begin', 'finish', 'abandon'}:
        key = check_key(key)
    encoded = None
    if operation == 'begin':
        natural(expected_epoch, 'expected_epoch', MAX_EVENTS)
        encoded = make_wire({'credits': 0, 'proposals': [proposal]})[2][0]
    with locked(run_dir):
        db = connection(run_dir / 'campaign.sqlite3')
        try:
            header, epoch, snapshot, commands, requests = read_store(db, run_dir)
            command = None
            if operation == 'begin':
                if key in requests:
                    old_epoch, old_proposal, ticket = requests[key]
                    if old_epoch != expected_epoch or old_proposal != encoded:
                        raise RuntimeError('operation key reused with a different exact request')
                else:
                    if expected_epoch != epoch:
                        raise RuntimeError('stale expected campaign epoch')
                    ticket = [key, snapshot[0], encoded]
                command = ['begin', ticket]
            elif operation in {'finish', 'abandon'}:
                command = [operation, key]
            checked = call_gate(wire(header['credits'], commands, snapshot, command,
                                     operation == 'invoke'), run_dir)
            point(operation + '_after_gate')
            if checked['changed']:
                if epoch >= MAX_EVENTS:
                    raise RuntimeError('event capacity exhausted')
                next_snapshot = checked['journal']
                db.execute('BEGIN IMMEDIATE')
                now = db.execute('SELECT epoch,snapshot FROM meta WHERE id=1').fetchone()
                if now != (epoch, canonical(snapshot)):
                    raise RuntimeError('campaign changed before commit')
                db.execute('INSERT INTO events VALUES(?,?)', (epoch, canonical(command)))
                if operation == 'begin':
                    db.execute('INSERT INTO requests VALUES(?,?,?,?)',
                               (key, epoch, canonical(encoded), canonical(ticket)))
                point(operation + '_after_event_write')
                db.execute('UPDATE meta SET epoch=?,snapshot=?,active=?,revision=? WHERE id=1',
                           (epoch + 1, canonical(next_snapshot), next_snapshot[0][1], next_snapshot[0][2]))
                point(operation + '_after_state_write')
                db.commit()
                point(operation + '_after_commit')
                epoch += 1
            # A command may have committed even if an acknowledgement/output fails.
            # Subsequent inspection or repeated keyed command replays the canonical DB.
            result = {**checked, 'epoch': epoch, 'campaign': header['campaign'],
                      'operation': operation, 'key': key,
                      'persistence_scope': 'protected local single-writer SQLite; immutable compiled catalogue'}
            point(operation + '_before_response')
            return result
        finally:
            if db.in_transaction:
                db.rollback()
            db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('start'); p.add_argument('--run-dir', type=Path, required=True); p.add_argument('--credits', type=int, required=True)
    for op in ['inspect', 'invoke', 'begin', 'finish', 'abandon']:
        p = sub.add_parser(op); p.add_argument('--run-dir', type=Path, required=True)
        if op in {'begin', 'finish', 'abandon'}:
            p.add_argument('--key', required=True)
        if op == 'begin':
            p.add_argument('proposal', type=Path); p.add_argument('--expected-epoch', required=True, type=int)
    args = parser.parse_args()
    try:
        if args.operation == 'start':
            output = start(args.run_dir, args.credits)
        else:
            proposal = None
            if args.operation == 'begin':
                if args.proposal.stat().st_size > 16384:
                    raise ValueError('proposal size limit')
                proposal = load_json(args.proposal.read_text())
            output = operate(args.run_dir, args.operation, key=getattr(args, 'key', None),
                             proposal=proposal, expected_epoch=getattr(args, 'expected_epoch', None))
        print(json.dumps(output, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
