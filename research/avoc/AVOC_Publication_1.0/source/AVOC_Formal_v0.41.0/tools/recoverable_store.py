#!/usr/bin/env python3
"""Transactional staging adapter for the existing AVOC proof gate.

The authoritative native gate state, checked receipt, and per-operation commit
result are published in ONE SQLite transaction. Candidate checking is staged in
memory. SQLite/OS atomicity and a protected single-writer run remain trusted.
"""
from __future__ import annotations
import contextlib
import copy
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterator
import artifact_gate as gate

SCHEMA = 'avoc-recoverable-store-1'

class RecoveryError(RuntimeError):
    pass

class StagedGate(gate.ArtifactGate):
    """Uses the unchanged register/verify/admit proof checks, without writing
    filesystem state. A successful stage is published only by Database.commit.
    Checker subprocesses and temporary request logs may execute more than once
    across manual retries; no exactly-once computation claim is made.
    """
    def __init__(self, state: dict[str, Any], checker: gate.LeanChecker):
        self._state = copy.deepcopy(state)
        self.checker = checker

    @contextlib.contextmanager
    def lock(self) -> Iterator[None]:
        yield  # Outer coordinator holds the exclusive run lock.

    def load(self) -> dict[str, Any]:
        return copy.deepcopy(self._state)

    def save(self, obj: dict[str, Any]) -> None:
        if len(gate.encode(obj).encode()) > gate.MAX_BYTES:
            raise RecoveryError('staged store byte limit exceeded')
        self._state = copy.deepcopy(obj)


def empty_native() -> dict[str, Any]:
    return {'schema':'avoc-store-1','next':0,'pending':None,'admitted':{},'events':[]}


def project(native: dict[str, Any], checked: Any, task: str) -> list[Any]:
    gate.exact_keys(native, {'schema','next','pending','admitted','events'})
    gate.require(native['schema']=='avoc-store-1' and type(native['next']) is int
                 and native['next'] >= 0, 'invalid native store')
    gate.require(isinstance(native['admitted'],dict) and set(native['admitted']) <= {task},
                 'unexpected root admission')
    gate.require(isinstance(native['events'],list),'invalid native events')
    if checked is not None:
        gate.exact_keys(checked,{'schema','subject','approved'})
        gate.require(checked['schema']=='avoc-receipt-1' and checked['approved'] is True,
                     'invalid checked receipt')
    record = native['admitted'].get(task)
    if record is not None:
        gate.exact_keys(record,{'schema','ticket'})
        gate.require(record['schema']=='avoc-admission-1','invalid admission record')
    return [[native['next'], None if native['pending'] is None else gate.wire_ticket(native['pending'])],
            None if checked is None else [gate.wire_ticket(checked['subject']),True],
            None if record is None else gate.wire_ticket(record['ticket'])]


class Database:
    def __init__(self, path: Path, *, create: bool = False):
        if path.is_symlink() or (not create and not path.is_file()):
            raise RecoveryError('database must be an existing protected regular file')
        if create and path.exists():
            raise RecoveryError('refusing to replace database')
        self.path = path
        self.db = sqlite3.connect(str(path), timeout=2, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=DELETE')
        self.db.execute('PRAGMA synchronous=EXTRA')
        self.db.execute('PRAGMA foreign_keys=ON')
        if create:
            self.db.executescript('''
              CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
              CREATE TABLE store(id INTEGER PRIMARY KEY CHECK(id=1),
                                 native TEXT NOT NULL, checked TEXT NOT NULL);
              CREATE TABLE operations(sequence INTEGER PRIMARY KEY,
                phase TEXT NOT NULL CHECK(phase IN ('intent','committed','acknowledged')),
                action TEXT NOT NULL, intent TEXT NOT NULL,
                before_native TEXT NOT NULL, before_checked TEXT NOT NULL,
                fee INTEGER NOT NULL CHECK(fee>=0), recommendation TEXT NOT NULL,
                receipt TEXT, after_native TEXT, after_checked TEXT, acknowledgement TEXT);
              CREATE TABLE invocations(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      record TEXT NOT NULL);
            ''')
            self.put('schema', SCHEMA)
            self.put('attempt_debits',0)
            self.put('status','initializing')
            self.db.execute('INSERT INTO store VALUES(1,?,?)',(gate.encode(empty_native()),'null'))
        if self.get('schema') != SCHEMA:
            raise RecoveryError('unsupported recovery store schema')
        if self.db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise RecoveryError('SQLite integrity check failed')

    def close(self) -> None:
        self.db.close()

    @contextlib.contextmanager
    def transaction(self) -> Iterator[None]:
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def put(self,key:str,value:Any) -> None:
        self.db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',(key,gate.encode(value)))

    def get(self,key:str,default:Any=None) -> Any:
        r=self.db.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
        return default if r is None else gate.strict_json(r[0])

    def snapshot(self) -> tuple[dict[str,Any],Any]:
        r=self.db.execute('SELECT native,checked FROM store WHERE id=1').fetchone()
        if r is None:raise RecoveryError('missing authoritative store')
        return gate.strict_json(r[0]),gate.strict_json(r[1])

    def operations(self) -> list[dict[str,Any]]:
        rows=[]
        for r in self.db.execute('SELECT * FROM operations ORDER BY sequence'):
            o=dict(r)
            for k in ('action','intent','before_native','before_checked','recommendation',
                      'receipt','after_native','after_checked','acknowledgement'):
                if o[k] is not None:o[k]=gate.strict_json(o[k])
            rows.append(o)
        return rows

    def checked_history(self) -> list[Any]:
        return [o['receipt'] for o in self.operations() if o['phase']=='acknowledged']

    def invocation_start(self,record:dict[str,Any]) -> int:
        record=dict(record,status='started')
        c=self.db.execute('INSERT INTO invocations(record) VALUES(?)',(gate.encode(record),))
        return int(c.lastrowid)

    def invocation_finish(self,index:int,record:dict[str,Any]) -> None:
        self.db.execute('UPDATE invocations SET record=? WHERE id=?',(gate.encode(record),index))

    def prepare(self,action:dict[str,Any],wire_action:list[Any],fee:int,
                recommendation:dict[str,Any],task:str,budget:int) -> dict[str,Any]:
        with self.transaction():
            ops=self.operations()
            if any(o['phase']!='acknowledged' for o in ops):
                raise RecoveryError('unresolved operation: acknowledge or stop before another action')
            if [o['sequence'] for o in ops] != list(range(len(ops))):
                raise RecoveryError('noncontiguous operation sequence')
            native,checked=self.snapshot()
            debit=self.get('attempt_debits')
            if type(fee) is not int or fee<0 or debit+fee>budget:
                raise RecoveryError('conservative attempted-fee budget exceeded')
            seq=len(ops);intent=[seq,project(native,checked,task),wire_action]
            self.db.execute('INSERT INTO operations(sequence,phase,action,intent,before_native,'
                            'before_checked,fee,recommendation) VALUES(?,?,?,?,?,?,?,?)',
                (seq,'intent',gate.encode(action),gate.encode(intent),gate.encode(native),
                 gate.encode(checked),fee,gate.encode(recommendation)))
            self.put('attempt_debits',debit+fee)
            self.put('status','operation_in_flight')
        return self.operations()[-1]

    def commit_hook(self,point:str)->None:
        """Controlled crash-test seam, not a configuration action."""

    def commit(self,op:dict[str,Any],native:dict[str,Any],checked:Any,report:bool,
               task:str) -> Any:
        if type(report) is not bool:raise RecoveryError('a durable Boolean result is required')
        receipt=[op['intent'],report,project(native,checked,task)]
        with self.transaction():
            current=self.operations()[-1]
            if current != op or op['phase']!='intent':
                raise RecoveryError('commit intent changed or already published')
            if self.snapshot() != (op['before_native'],op['before_checked']):
                raise RecoveryError('store changed since preparation')
            self.db.execute('UPDATE store SET native=?, checked=? WHERE id=1',
                            (gate.encode(native),gate.encode(checked)))
            self.commit_hook('after_store_write')
            self.db.execute('UPDATE operations SET phase=?,receipt=?,after_native=?,after_checked=? '
                            'WHERE sequence=?',('committed',gate.encode(receipt),gate.encode(native),
                                               gate.encode(checked),op['sequence']))
            self.put('status','committed_unacknowledged')
            self.commit_hook('after_result_write')
        return receipt

    def acknowledge(self,seq:int,result:dict[str,Any]) -> None:
        with self.transaction():
            ops=self.operations()
            if not ops or ops[-1]['sequence']!=seq:raise RecoveryError('not the latest operation')
            op=ops[-1]
            if op['phase'] not in ('committed','acknowledged'):raise RecoveryError('no durable result')
            if self.snapshot() != (op['after_native'],op['after_checked']):
                raise RecoveryError('store/result changed during acknowledgement')
            if result.get('status')!='ok' or result.get('confirmed_steps')!=seq+1:
                raise RecoveryError('invalid monitor acknowledgement')
            if op['phase']=='acknowledged':return
            self.db.execute('UPDATE operations SET phase=?,acknowledgement=? WHERE sequence=?',
                            ('acknowledged',gate.encode(result),seq))
            self.put('confirmed_state',result['current'])
            self.put('status','running')

    def assert_consistent_chain(self,task:str) -> None:
        native,checked=empty_native(),None
        ops=self.operations()
        for seq,op in enumerate(ops):
            if op['sequence']!=seq or op['intent']!=[seq,project(native,checked,task),
                 (['register',op['action']['candidate']] if op['action']['kind']=='register' else [op['action']['kind']])]:
                raise RecoveryError('operation intent/sequence chain mismatch')
            if (op['before_native'],op['before_checked'])!=(native,checked):
                raise RecoveryError('native pre-state chain mismatch')
            if seq<len(ops)-1 and op['phase']!='acknowledged':
                raise RecoveryError('operation follows an unacknowledged predecessor')
            if op['phase']=='intent':
                if op['receipt'] is not None:raise RecoveryError('unfinished operation has result')
            else:
                native,checked=op['after_native'],op['after_checked']
                if op['receipt'] is None or len(op['receipt'])!=3 or op['receipt'][0]!=op['intent'] or \
                   type(op['receipt'][1]) is not bool or op['receipt'][2]!=project(native,checked,task):
                    raise RecoveryError('durable receipt does not match atomic post-state')
        if self.snapshot()!=(native,checked):raise RecoveryError('authoritative store is not the last transaction state')
        if self.get('attempt_debits') != sum(o['fee'] for o in ops):
            raise RecoveryError('attempted fee ledger mismatch')
