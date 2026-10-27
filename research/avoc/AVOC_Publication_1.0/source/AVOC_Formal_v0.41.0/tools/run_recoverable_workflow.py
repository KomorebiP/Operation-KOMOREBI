#!/usr/bin/env python3
"""Recoverable protected single-root AVOC workflow.

Only start creates work. Resume acknowledges durably committed operations and
then continues. An intent without a durable result is NOT retried: checking may
have run and its cost/output may be unknown. `inspect` is read-only except for
SQLite's own recovery. Host/store, SQLite durability, and cooperative flock
exclusion remain trusted. Not a migration tool for pre-v0.20 stores.
"""
from __future__ import annotations
import argparse
import contextlib
import copy
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Iterator
from fractions import Fraction

import artifact_gate as gate
import run_planner as planner
from recoverable_store import Database, StagedGate, RecoveryError, project

ROOT=Path(__file__).resolve().parents[1]
SOURCE_FILES=['tools/run_recoverable_workflow.py','tools/recoverable_store.py',
 'tools/artifact_gate.py','tools/run_planner.py','tools/RecoveryMain.lean','tools/LivePlannerMain.lean',
 'AVOC/CommitRecovery.lean','AVOC/AtomicCommitModel.lean','AVOC/RecoveryCodec.lean']

class CheckedRejection(Exception):
    pass

@contextlib.contextmanager
def exclusive_run(path:Path) -> Iterator[None]:
    lock=path/'COORDINATOR_LOCK'
    if lock.is_symlink():raise RecoveryError('lock symlink forbidden')
    fd=os.open(lock,os.O_CREAT|os.O_RDWR,0o600)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as e:raise RecoveryError('run is in use') from e
        yield
    finally:
        os.close(fd)

def pins()->dict[str,str]:
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_FILES}

class LoggedChecker(gate.LeanChecker):
    def __init__(self,db:Database,seconds:float):
        self.db=db;self.phase='initialization'
        super().__init__(ROOT,seconds=seconds)

    def request(self,payload:Any)->bool:
        row={'kind':'checker','phase':self.phase,'request_sha256':hashlib.sha256(gate.encode(payload).encode()).hexdigest()}
        index=self.db.invocation_start(row)
        start=len(self.records)
        try:
            result=super().request(payload)
        except BaseException as e:
            row.update(status='fault',error=type(e).__name__+': '+str(e))
            if len(self.records)>start:row.update(self.records[-1])
            self.db.invocation_finish(index,row)
            raise
        row.update(self.records[-1],status='completed',accepted=result)
        self.db.invocation_finish(index,row)
        return result

    def check(self,target:Any,context:list[Any],proof:Any)->bool:
        if not super().check(target,context,proof):raise CheckedRejection('actual Lean checker returned false')
        return True

class RecoverableRun:
    def __init__(self,run_dir:Path,*,checker_timeout:float=30,planner_timeout:float=60):
        self.run_dir=run_dir.resolve();self.db=Database(self.run_dir/'state.sqlite3')
        self.checker_timeout=checker_timeout;self.planner_timeout=planner_timeout
        self.header=self.db.get('header')
        if not isinstance(self.header,dict):raise RecoveryError('incomplete initialization; no recovery header')
        self.config=self.header['config'];self.job=self.header['job'];self.identity=self.header['identity']
        self.task=self.header['task']
        self.checker=LoggedChecker(self.db,checker_timeout)

    @classmethod
    def create(cls,config_path:Path,run_dir:Path,**kwargs:Any)->'RecoverableRun':
        # Caller creates and locks a new directory before entering this method.
        db=Database(run_dir/'state.sqlite3',create=True)
        checker=LoggedChecker(db,kwargs.get('checker_timeout',30))
        try:
            raw=gate.read_raw(config_path)
            c=gate.strict_json(raw)
            allowed={'prior_true','success_if_false','success_if_true','register_fee','verify_fee',
              'admit_fee','admission_value','research_budget','horizon','planning_work_per_decision',
              'planning_price_per_unit','target_file','candidate_files'}
            if not isinstance(c,dict) or set(c)-allowed or not allowed-{'planning_price_per_unit'}<=set(c):
                raise RecoveryError('invalid configuration fields; supplied reports/fault hooks are forbidden')
            if planner.fraction(c['success_if_false'])!=[1,1] or planner.fraction(c['success_if_true'])!=[1,1]:
                raise RecoveryError('live backend requires deterministic availability')
            if not isinstance(c['target_file'],str) or not isinstance(c['candidate_files'],list) or not 1<=len(c['candidate_files'])<=8:
                raise RecoveryError('one root target and one to eight candidates required')
            base=config_path.resolve().parent
            target=base/c['target_file'];target_raw=gate.read_raw(target);spec=gate.parse_target(target_raw)
            if spec['dependencies']:raise RecoveryError('root-only recovery adapter')
            paths=[base/x for x in c['candidate_files']]
            texts=[gate.read_raw(x) for x in paths]
            for text in texts:gate.validate_proof(gate.strict_json(text))
            env=checker.environment()
            identity=[spec['task'],spec['statement'],target_raw,[],[[k,gate.encode(v)] for k,v in sorted(env.items())]]
            model={k:v for k,v in c.items() if k not in {'target_file','candidate_files'}}
            model.update(target_text=gate.encode(spec['statement']),candidate_texts=texts)
            job=planner.wire_request(model,base)
            header={'config_path':str(config_path.resolve()),'config_bytes':raw,'config':c,
                    'target_path':str(target.resolve()),'target_bytes':target_raw,
                    'candidate_paths':[str(x.resolve()) for x in paths],'candidate_bytes':texts,
                    'task':spec['task'],'environment':env,'identity':identity,'job':job,
                    'source_pins':pins(),'run_id':uuid.uuid4().hex}
            with db.transaction():
                db.put('header',header);db.put('status','running');db.put('confirmed_state',None)
        finally:db.close()
        return cls(run_dir,**kwargs)

    def close(self)->None:self.db.close()

    def hook(self,name:str,action:dict[str,Any])->None:
        """Test subclass seam; deliberately unavailable in user config/CLI."""

    def assert_fixed(self)->None:
        h=self.header
        if pins()!=h['source_pins']:raise RecoveryError('coordinator/monitor source drift')
        if gate.read_raw(Path(h['config_path']))!=h['config_bytes']:raise RecoveryError('configuration drift')
        if gate.read_raw(Path(h['target_path']))!=h['target_bytes']:raise RecoveryError('target drift')
        for path,text in zip(h['candidate_paths'],h['candidate_bytes']):
            if gate.read_raw(Path(path))!=text:raise RecoveryError('candidate drift')
        if self.checker.environment()!=h['environment']:raise RecoveryError('checker environment drift')
        self.db.assert_consistent_chain(self.task)

    def view(self)->list[Any]:
        return project(*self.db.snapshot(),self.task)

    def call_lean(self,entry:str,wire:Any,kind:str)->dict[str,Any]:
        record={'kind':kind,'entrypoint':entry,'status':'started'}
        idx=self.db.invocation_start(record)
        requests=self.run_dir/'requests';requests.mkdir(exist_ok=True)
        req=requests/f'{idx:05d}_{kind}.json';req.write_text(gate.encode(wire),encoding='utf-8')
        if req.stat().st_size>4194304:raise RecoveryError('request byte limit')
        lean,env=planner.runtime()
        cmd=[str(lean),'-j1','-DwarningAsError=true','--run',str(ROOT/entry),str(req)]
        record.update(command=cmd,request_sha256=hashlib.sha256(req.read_bytes()).hexdigest())
        t=time.monotonic();before=self.db.snapshot()
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              text=True,start_new_session=True)
        timed_out=False
        try:out,err=proc.communicate(timeout=self.planner_timeout)
        except subprocess.TimeoutExpired:
            timed_out=True;os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate()
        record.update(returncode=proc.returncode,timed_out=timed_out,stdout=out,stderr=err,
                      seconds=time.monotonic()-t,status='completed' if proc.returncode==0 else 'fault')
        self.db.invocation_finish(idx,record)
        if timed_out or proc.returncode or err.strip():raise RecoveryError('Lean monitor failed: '+err[:400])
        if self.db.snapshot()!=before:raise RecoveryError('store changed during monitor')
        ans=gate.strict_json(out)
        if not isinstance(ans,dict) or ans.get('status')!='ok':raise RecoveryError('invalid Lean response')
        return ans

    def recovery_monitor(self,incoming:Any=None)->dict[str,Any]:
        ans=self.call_lean('tools/RecoveryMain.lean',['avoc-recovery-v1',self.job,self.identity,
                          self.db.checked_history(),incoming,self.view()],'recovery')
        if ans.get('backend')!='AVOC-v0.20-recovery-monitor' or ans.get('new_planning_work')!=0:
            raise RecoveryError('wrong recovery endpoint or hidden planning')
        return ans

    def recommend(self)->dict[str,Any]:
        records=self.db.checked_history()
        events=[[r[0][2],['report',r[1],r[2]]] for r in records]
        ans=self.call_lean('tools/LivePlannerMain.lean',['avoc-live-v1',self.job,self.identity,events,
                          self.view(),'plan'],'planner')
        if ans.get('backend')!='AVOC-v0.19-live-monitor' or ans.get('confirmed_steps')!=len(records):
            raise RecoveryError('invalid planner checkpoint')
        rec=ans.get('recommendation')
        if rec is not None and not 0<=rec['work_used']<=rec['work_reserved']<=self.config['planning_work_per_decision']:
            raise RecoveryError('invalid planning work reservation')
        return ans

    def stage(self,op:dict[str,Any])->tuple[dict[str,Any],Any,bool]:
        action=op['action'];kind=action['kind'];self.checker.phase=kind
        staged=StagedGate(op['before_native'],self.checker)
        checked=copy.deepcopy(op['before_checked'])
        if kind=='register':
            c=action['candidate']
            if type(c) is not int or not 0<=c<len(self.header['candidate_paths']):raise RecoveryError('bad candidate index')
            staged.register(Path(self.header['target_path']),Path(self.header['candidate_paths'][c]))
            checked=None;report=False
        elif kind=='verify':
            try:checked=staged.verify();report=True
            except CheckedRejection:checked=None;report=False
        elif kind=='admit':
            if checked is None:raise RecoveryError('no checked receipt')
            staged.admit(checked);checked=None;report=False
        elif kind=='stop':report=False
        else:raise RecoveryError('unknown stage')
        return staged.load(),checked,report

    def recover(self)->bool:
        self.assert_fixed()
        ops=self.db.operations()
        if ops and ops[-1]['phase']=='intent':
            # It is known that no atomic database effect/result committed, but
            # the checker may have run. Do not fabricate a report or retry it.
            self.db.put('status','aborted_uncommitted')
            self.db.put('error','unfinished intent: no durable result; automatic retry forbidden')
            return False
        incoming=ops[-1]['receipt'] if ops else None
        ans=self.recovery_monitor(incoming)
        if ops:
            op=ops[-1]
            if ans['confirmed_steps']!=op['sequence']+1:raise RecoveryError('wrong recovered sequence')
            self.hook('before_ack',op['action'])
            self.assert_fixed()
            self.db.acknowledge(op['sequence'],ans)
            self.hook('after_ack',op['action'])
        self.db.put('confirmed_state',ans['current'])
        self.db.put('last_recovery_disposition',ans['disposition'])
        self.db.put('error',None)
        return True

    def run(self,*,recover_only:bool=False)->dict[str,Any]:
        try:
            if not self.recover():return self.summary()
            if recover_only:
                self.finish_status()
                return self.summary()
            while len(self.db.checked_history())<self.config['horizon']:
                self.assert_fixed()
                state=self.db.get('confirmed_state')
                if state and (state['completed'] or state['halted']):break
                ans=self.recommend();rec=ans.get('recommendation')
                if rec is None:break
                a=rec['action'];kind=a['kind'];fee=0 if kind=='stop' else self.config[kind+'_fee']
                wa=['register',a['candidate']] if kind=='register' else [kind]
                op=self.db.prepare(a,wa,fee,rec,self.task,self.config['research_budget'])
                self.hook('after_intent',a)
                self.assert_fixed()
                native,checked,report=self.stage(op)
                self.hook('after_evaluation',a)
                self.assert_fixed()
                self.db.commit(op,native,checked,report,self.task)
                self.hook('after_commit',a)
                # Same path for normal acknowledgement and crash recovery.
                if not self.recover():break
            self.finish_status()
        except Exception as e:
            self.db.put('status','aborted_unconfirmed')
            self.db.put('error',type(e).__name__+': '+str(e))
        return self.summary()

    def finish_status(self)->None:
        s=self.db.get('confirmed_state')
        status='admitted' if s and s['completed'] else 'stopped' if s and s['halted'] else 'ready'
        if len(self.db.checked_history())>=self.config['horizon'] and status=='ready':status='horizon_exhausted'
        self.db.put('status',status)

    def summary(self)->dict[str,Any]:
        ops=self.db.operations();native,checked=self.db.snapshot()
        inv=[gate.strict_json(r[0]) for r in self.db.db.execute('SELECT record FROM invocations ORDER BY id')]
        return {'schema':'avoc-recoverable-run-1','status':self.db.get('status'),'error':self.db.get('error'),
          'confirmed_steps':sum(o['phase']=='acknowledged' for o in ops),'confirmed_state':self.db.get('confirmed_state'),
          'committed_steps':sum(o['phase'] in ('committed','acknowledged') for o in ops),
          'operations':[{'sequence':o['sequence'],'action':o['action'],'phase':o['phase'],'fee':o['fee']} for o in ops],
          'physical_admissions':len(native['admitted']),'physical_pending':native['pending'] is not None,
          'physical_checked':checked is not None,'physical_generation':native['next'],
          'nominal_attempt_debits':self.db.get('attempt_debits'),
          'last_recovery_disposition':self.db.get('last_recovery_disposition'),
          'checker_invocations':sum(i['kind']=='checker' for i in inv),
          'unfinished_invocations':sum(i['status']=='started' for i in inv),
          'planner_invocations':sum(i['kind']=='planner' for i in inv),
          'recovery_monitor_invocations':sum(i['kind']=='recovery' for i in inv),
          'sqlite_version':__import__('sqlite3').sqlite_version,
          'sqlite_journal_mode':self.db.db.execute('PRAGMA journal_mode').fetchone()[0],
          'sqlite_synchronous':self.db.db.execute('PRAGMA synchronous').fetchone()[0],
          'scope':'Protected single-writer atomic store/result commits. Unfinished intents are not retried. '
                  'No hostile rollback, distributed exactly-once, complete filesystem refinement, or physical-cost guarantee.'}


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ['start','resume','inspect']:
        q=sub.add_parser(name)
        if name=='start':q.add_argument('config',type=Path)
        q.add_argument('--run-dir',type=Path,required=True)
        if name!='inspect':
            q.add_argument('--planner-timeout',type=float,default=60)
            q.add_argument('--checker-timeout',type=float,default=30)
            q.add_argument('--recover-only',action='store_true')
    a=p.parse_args()
    try:
        if a.run_dir.is_symlink():raise RecoveryError('run symlink forbidden')
        if a.command=='start':a.run_dir.mkdir(parents=True,exist_ok=False)
        elif not a.run_dir.is_dir():raise RecoveryError('run directory missing')
        with exclusive_run(a.run_dir):
            if a.command=='inspect':
                # Inspect does not invoke a checker or execute a research action.
                db=Database(a.run_dir/'state.sqlite3');h=db.get('header')
                try:
                    db.assert_consistent_chain(h['task'])
                    out={'status':db.get('status'),'confirmed_state':db.get('confirmed_state'),
                         'operations':[{'sequence':o['sequence'],'phase':o['phase'],'action':o['action']} for o in db.operations()],
                         'native_store':db.snapshot()[0],'nominal_attempt_debits':db.get('attempt_debits')}
                finally:db.close()
            else:
                if not 0<a.planner_timeout<=300 or not 0<a.checker_timeout<=300:raise RecoveryError('invalid timeouts')
                kw=dict(planner_timeout=a.planner_timeout,checker_timeout=a.checker_timeout)
                run=RecoverableRun.create(a.config,a.run_dir,**kw) if a.command=='start' else RecoverableRun(a.run_dir,**kw)
                try:out=run.run(recover_only=a.recover_only)
                finally:run.close()
        print(json.dumps(out,indent=2))
        return 2 if out.get('status','').startswith('aborted') else 0
    except Exception as e:
        print(json.dumps({'status':'rejected','error':type(e).__name__+': '+str(e)}),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
