#!/usr/bin/env python3
"""Protected single-root workflow with explicit paid retry and terminal abandonment.

Default resume never retries an unfinished attempt. The `retry` command requires
a fresh resolution key and exact expected attempt generation. Operational fees
are separate from confirmed-model fees. One protected cooperative writer, stable
inputs, and SQLite/OS/runtime correctness remain trusted. No legacy migration.
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
from retry_store import RetryDatabase as Database, StagedGate, RecoveryError, project

ROOT=Path(__file__).resolve().parents[1]
SOURCE_FILES=['tools/run_retry_workflow.py','tools/retry_store.py',
 'tools/artifact_gate.py','tools/run_planner.py','tools/RecoveryMain.lean','tools/LivePlannerMain.lean',
 'AVOC/CommitRecovery.lean','AVOC/AtomicCommitModel.lean','AVOC/RecoveryCodec.lean',
 'AVOC/AttemptAccounting.lean','AVOC/AttemptCodec.lean','AVOC/AttemptRecovery.lean','tools/AttemptMain.lean']

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

class RetryRun:
    def __init__(self,run_dir:Path,*,checker_timeout:float=30,planner_timeout:float=60,attempt_budget:int|None=None,max_attempts:int|None=None):
        self.run_dir=run_dir.resolve();self.db=Database(self.run_dir/'state.sqlite3')
        self.checker_timeout=checker_timeout;self.planner_timeout=planner_timeout
        self.header=self.db.get('header')
        if not isinstance(self.header,dict):raise RecoveryError('incomplete initialization; no recovery header')
        self.config=self.header['config'];self.job=self.header['job'];self.identity=self.header['identity']
        self.task=self.header['task']
        self.checker=LoggedChecker(self.db,checker_timeout)
        self.db.account_transition=self.account_check

    @classmethod
    def create(cls,config_path:Path,run_dir:Path,**kwargs:Any)->'RetryRun':
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
            ab=kwargs.get('attempt_budget')
            ab=c['research_budget'] if ab is None else ab
            ac=kwargs.get('max_attempts')
            ac=32 if ac is None else ac
            if type(ab) is not int or ab<0 or type(ac) is not int or not 0<=ac<=1024:
                raise RecoveryError('invalid attempt envelope')
            header['attempt_limits']=[ab,ac]
            with db.transaction():
                db.put('retry_limits',[ab,ac]);db.put('header',header);db.put('status','running');db.put('confirmed_state',None)
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
        if self.db.get('retry_limits')!=h['attempt_limits']:raise RecoveryError('attempt-limit drift')
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
        if self.db.book()[5]:
            self.db.put('status','abandoned_uncommitted')
            return False
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
        return {'schema':'avoc-costed-retry-run-1','status':self.db.get('status'),'error':self.db.get('error'),
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
          'attempt_ledger':self.db.book(), 'attempt_limits':self.db.get('retry_limits'),
          'attempts':self.db.attempt_rows(),
          'wasted_nominal_fees':sum(r['fee'] for r in self.db.attempt_rows() if r['phase'] in ('superseded','abandoned')),
          'held_nominal_fee':0 if self.db.book()[3] is None else self.db.book()[3][2],
          'scope':'Protected fixed-candidate, explicit keyed retries with fresh charged reservations. '
                  'No hostile rollback, distributed exactly-once, complete filesystem refinement, or physical-cost guarantee.'}


    def account_check(self,limits,before,event):
        ans=self.call_lean('tools/AttemptMain.lean',
            ['avoc-attempt-v1',limits,before,event],'attempt_gate')
        if ans.get('backend')!='AVOC-v0.21-attempt-gate':raise RecoveryError('wrong accounting endpoint')
        return ans['ledger']

    def resolve(self,kind:str,key:str,expected:int,*,continue_run:bool=True):
        try:
            self.assert_fixed()
            prior=self.db._resolution(key,kind,expected)
            if prior is not None:
                out=self.summary();out['resolution_disposition']='duplicate_authorization_no_execution'
                return out
            ops=self.db.operations()
            if ops and ops[-1]['phase'] in ('committed','acknowledged'):
                self.recover()
                self.finish_status()
                out=self.summary();out['resolution_disposition']='already_committed_reconciled_not_retried'
                return out
            # Exact replay checks the last confirmed prefix against the CURRENT
            # store. No pending intent is ever turned into a report.
            before=self.recovery_monitor()
            if before['current']['research_spent']!=self.db.book()[1]:
                raise RecoveryError('checkpoint/accounting mismatch')
            if kind=='abandon':
                self.db.abandon_attempt(key,expected,self.task)
                out=self.summary();out['resolution_disposition']='administrative_abandonment'
                return out
            op=self.db.authorize_retry(key,expected,self.task)
            if op is None:
                out=self.summary();out['resolution_disposition']='duplicate_authorization_no_execution'
                return out
            self.hook('after_retry_intent',op['action'])
            self.assert_fixed()
            native,checked,report=self.stage(op)
            self.hook('after_retry_evaluation',op['action'])
            self.assert_fixed()
            self.db.commit(op,native,checked,report,self.task)
            self.hook('after_commit',op['action'])
            if not self.recover():return self.summary()
            if continue_run:return self.run()
            self.finish_status()
            out=self.summary();out['resolution_disposition']='retry_committed_and_acknowledged'
            return out
        except Exception as e:
            # This diagnostic status does not mutate the confirmed prefix,
            # refund a reservation, or fabricate a negative observation.
            self.db.put('status','resolution_blocked')
            self.db.put('error',type(e).__name__+': '+str(e))
            return self.summary()


def main()->int:
    parser=argparse.ArgumentParser(description='Costed explicit retries for new protected AVOC runs.')
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ['start','resume','retry','abandon','inspect']:
        p=sub.add_parser(name)
        p.add_argument('--run-dir',type=Path,required=True)
        if name=='start':
            p.add_argument('config',type=Path)
            p.add_argument('--attempt-budget',type=int)
            p.add_argument('--max-attempts',type=int,default=32)
        if name in ('retry','abandon'):
            p.add_argument('--key',required=True)
            p.add_argument('--expected-attempt',required=True,type=int)
        if name!='inspect':
            p.add_argument('--planner-timeout',type=float,default=60)
            p.add_argument('--checker-timeout',type=float,default=30)
            p.add_argument('--recover-only',action='store_true')
    a=parser.parse_args()
    try:
        if a.run_dir.is_symlink():raise RecoveryError('run symlink forbidden')
        if a.command=='start':a.run_dir.mkdir(parents=True,exist_ok=False)
        elif not a.run_dir.is_dir():raise RecoveryError('missing run directory')
        with exclusive_run(a.run_dir):
            if a.command=='inspect':
                obj=RetryRun(a.run_dir)
                try:out=obj.summary()
                finally:obj.close()
            else:
                kw=dict(planner_timeout=a.planner_timeout,checker_timeout=a.checker_timeout)
                if a.command=='start':
                    obj=RetryRun.create(a.config,a.run_dir,**kw,attempt_budget=a.attempt_budget,max_attempts=a.max_attempts)
                else:obj=RetryRun(a.run_dir,**kw)
                try:
                    if a.command in ('retry','abandon'):
                        out=obj.resolve(a.command,a.key,a.expected_attempt,continue_run=not a.recover_only)
                    else:out=obj.run(recover_only=a.recover_only)
                finally:obj.close()
            print(json.dumps(out,indent=2))
            if a.command=='inspect':return 0
            if out.get('status') in ('admitted','stopped','ready','horizon_exhausted','abandoned_uncommitted'):return 0
            return 2
    except Exception as e:
        print(json.dumps({'status':'rejected','error':type(e).__name__+': '+str(e)}))
        return 2

if __name__=='__main__':raise SystemExit(main())
