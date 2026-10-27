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

SCHEMA = 'avoc-costed-retry-store-1'

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
        if self.get('attempt_debits') != sum(r['fee'] for r in self.attempt_rows()):
            raise RecoveryError('attempted fee ledger mismatch')

class RetryDatabase(Database):
    """New format only. Every accounting mutation is checked by the Lean gate.

    Pure checker work may run in a staging object; only this database publishes.
    A cooperative exclusive writer and protected store remain prerequisites.
    """
    def __init__(self, path: Path, *, create: bool = False):
        super().__init__(path, create=create)
        self.account_transition = None
        if create:
            self.db.executescript('''
                  CREATE TABLE attempts(generation INTEGER PRIMARY KEY, operation INTEGER NOT NULL,
                    fee INTEGER NOT NULL CHECK(fee>=0), phase TEXT NOT NULL,
                    authorization TEXT UNIQUE NOT NULL,
                    FOREIGN KEY(operation) REFERENCES operations(sequence));
                  CREATE TABLE resolutions(key TEXT PRIMARY KEY, kind TEXT NOT NULL,
                    operation INTEGER NOT NULL, expected INTEGER NOT NULL, result INTEGER);
                ''')
            with self.transaction():
                self.put('attempt_ledger',[0,0,0,None,False,False])
                self.put('retry_limits',None)

    def attempt_rows(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM attempts ORDER BY generation')]

    def book(self):
        b=self.get('attempt_ledger')
        if not isinstance(b,list) or len(b)!=6: raise RecoveryError('missing attempt ledger')
        return b

    def apply_accounting(self,event):
        if self.account_transition is None: raise RecoveryError('Lean accounting gate not attached')
        before=self.book(); limits=self.get('retry_limits')
        after=self.account_transition(limits,before,event)
        if self.book()!=before: raise RecoveryError('attempt ledger changed during checking')
        self.put('attempt_ledger',after); self.put('attempt_debits',after[0])
        return after

    def prepare(self,action,wire_action,fee,recommendation,task,budget):
        with self.transaction():
            self.assert_consistent_chain(task)
            ops=self.operations()
            if any(o['phase']!='acknowledged' for o in ops):
                raise RecoveryError('unfinished operation: explicit retry or abandonment required')
            if sum(o['fee'] for o in ops)+fee>budget: raise RecoveryError('logical research budget exceeded')
            if type(fee) is not int or fee<0: raise RecoveryError('invalid fee')
            native,checked=self.snapshot();seq=len(ops)
            intent=[seq,project(native,checked,task),wire_action]
            book=self.apply_accounting(['reserve',seq,fee])
            self.db.execute('INSERT INTO operations(sequence,phase,action,intent,before_native,'
                'before_checked,fee,recommendation) VALUES(?,?,?,?,?,?,?,?)',
                (seq,'intent',gate.encode(action),gate.encode(intent),gate.encode(native),
                 gate.encode(checked),fee,gate.encode(recommendation)))
            generation=book[3][1]
            self.db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)',
                (generation,seq,fee,'active','initial:'+str(seq)))
            self.put('status','operation_in_flight')
        op=self.operations()[-1];op['_attempt']=generation;return op

    def _unfinished(self,expected,task):
        self.assert_consistent_chain(task)
        ops=self.operations();b=self.book()
        if not ops or ops[-1]['phase']!='intent': raise RecoveryError('no unfinished operation; recover commit instead')
        op=ops[-1]
        if b[4] or b[5] or b[3]!=[op['sequence'],expected,op['fee']]:
            raise RecoveryError('stale attempt number, published outcome, or terminal run')
        if self.snapshot()!=(op['before_native'],op['before_checked']):
            raise RecoveryError('uncommitted before-state mismatch')
        return op

    def _resolution(self,key,kind,expected):
        if not isinstance(key,str) or not 1<=len(key)<=128 or key.startswith('initial:'):
            raise RecoveryError('invalid resolution key')
        row=self.db.execute('SELECT * FROM resolutions WHERE key=?',(key,)).fetchone()
        if row is not None:
            if row['kind']!=kind or row['expected']!=expected:
                raise RecoveryError('resolution key reused for a different request')
            return dict(row)
        return None

    def authorize_retry(self,key,expected,task):
        with self.transaction():
            prior=self._resolution(key,'retry',expected)
            if prior is not None:return None # Idempotent authorization, NEVER duplicate execution.
            op=self._unfinished(expected,task)
            b=self.apply_accounting(['renew',[op['sequence'],expected,op['fee']]])
            generation=b[3][1]
            self.db.execute('UPDATE attempts SET phase=? WHERE generation=?',('superseded',expected))
            self.db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)',
                (generation,op['sequence'],op['fee'],'active','retry:'+key))
            self.db.execute('INSERT INTO resolutions VALUES(?,?,?,?,?)',
                (key,'retry',op['sequence'],expected,generation))
            self.put('status','retry_in_flight');self.put('error',None)
        op['_attempt']=generation;return op

    def abandon_attempt(self,key,expected,task):
        with self.transaction():
            prior=self._resolution(key,'abandon',expected)
            if prior is not None:return False
            op=self._unfinished(expected,task)
            self.apply_accounting(['abandon',[op['sequence'],expected,op['fee']]])
            self.db.execute('UPDATE attempts SET phase=? WHERE generation=?',('abandoned',expected))
            self.db.execute('INSERT INTO resolutions VALUES(?,?,?,?,NULL)',
                (key,'abandon',op['sequence'],expected))
            self.put('status','abandoned_uncommitted');self.put('error',None)
        return True

    def commit(self,op,native,checked,report,task):
        if type(report) is not bool: raise RecoveryError('durable Boolean report required')
        generation=op.get('_attempt'); bare={k:v for k,v in op.items() if k!='_attempt'}
        receipt=[bare['intent'],report,project(native,checked,task)]
        with self.transaction():
            self.assert_consistent_chain(task)
            current=self.operations()[-1]
            if current!=bare or current['phase']!='intent':raise RecoveryError('intent changed or already committed')
            if self.book()[3]!=[op['sequence'],generation,op['fee']]:raise RecoveryError('stale attempt fenced')
            if self.snapshot()!=(op['before_native'],op['before_checked']):raise RecoveryError('store changed since intent')
            self.apply_accounting(['publish',[op['sequence'],generation,op['fee']]])
            self.db.execute('UPDATE store SET native=?,checked=? WHERE id=1',
                (gate.encode(native),gate.encode(checked)))
            self.commit_hook('after_store_write')
            self.db.execute('UPDATE operations SET phase=?,receipt=?,after_native=?,after_checked=? WHERE sequence=?',
                ('committed',gate.encode(receipt),gate.encode(native),gate.encode(checked),op['sequence']))
            self.db.execute('UPDATE attempts SET phase=? WHERE generation=?',('published',generation))
            self.put('status','committed_unacknowledged')
            self.commit_hook('after_result_write')
        return receipt

    def acknowledge(self,seq,result):
        with self.transaction():
            ops=self.operations()
            if not ops or ops[-1]['sequence']!=seq: raise RecoveryError('not current operation')
            op=ops[-1]
            if op['phase'] not in ('committed','acknowledged'):raise RecoveryError('no committed result')
            if self.snapshot()!=(op['after_native'],op['after_checked']):raise RecoveryError('store/result mismatch')
            if result.get('status')!='ok' or result.get('confirmed_steps')!=seq+1:
                raise RecoveryError('invalid semantic acknowledgement')
            if op['phase']=='acknowledged':return
            t=self.book()[3]
            if t is None or t[0]!=seq or t[2]!=op['fee']:raise RecoveryError('attempt/operation mismatch')
            b=self.apply_accounting(['settle',t])
            if b[1]!=result['current']['research_spent']:raise RecoveryError('logical/physical spending mismatch')
            self.db.execute('UPDATE operations SET phase=?,acknowledgement=? WHERE sequence=?',
                ('acknowledged',gate.encode(result),seq))
            self.db.execute('UPDATE attempts SET phase=? WHERE generation=?',('settled',t[1]))
            self.put('confirmed_state',result['current']);self.put('status','running')

    def assert_consistent_chain(self,task):
        super().assert_consistent_chain(task)
        b=self.book();rows=self.attempt_rows();ops=self.operations();limits=self.get('retry_limits')
        if limits is None: raise RecoveryError('retry envelope missing')
        if any(type(x) is not int or x<0 for x in b[:3]):raise RecoveryError('invalid accounting totals')
        if [r['generation'] for r in rows]!=list(range(len(rows))):raise RecoveryError('attempt counter mismatch')
        if b[2]!=len(rows) or b[0]!=sum(r['fee'] for r in rows):raise RecoveryError('attempt total mismatch')
        if b[1]!=sum(o['fee'] for o in ops if o['phase']=='acknowledged'):
            raise RecoveryError('confirmed fee mismatch')
        if b[0]>limits[0] or b[2]>limits[1] or b[1]>b[0]:raise RecoveryError('attempt envelope violated')
        for row in rows:
            if not 0<=row['operation']<len(ops) or row['fee']!=ops[row['operation']]['fee']:
                raise RecoveryError('attempt operation/fee mismatch')
        active=[r for r in rows if r['phase'] in ('active','published')]
        if b[3] is None:
            if active or b[4]:raise RecoveryError('unexpected active attempt')
        else:
            if len(active)!=1 or [active[0]['operation'],active[0]['generation'],active[0]['fee']]!=b[3]:
                raise RecoveryError('active ticket mismatch')
            if b[4]!=(active[0]['phase']=='published'):raise RecoveryError('publication flag mismatch')
            phase=ops[active[0]['operation']]['phase']
            if (phase=='committed')!=b[4] or phase=='acknowledged':raise RecoveryError('operation phase mismatch')
        if b[5] and (b[3] is not None or b[4]):raise RecoveryError('invalid terminal attempt state')
