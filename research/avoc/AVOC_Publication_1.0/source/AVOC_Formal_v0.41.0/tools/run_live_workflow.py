#!/usr/bin/env python3
"""Drive the proved Lean planner against the real, protected root-artifact store.

Fresh single-root runs only. Real checker Boolean results are evidence; process
errors are not. Every confirmed operation is replayed through the Lean monitor
and checked against a freshly read exact store projection. The filesystem,
serialization and process adapter is tested, not a universally proved refinement.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import artifact_gate as gate
import run_planner as planner

ROOT = Path(__file__).resolve().parents[1]

class OperationalFault(RuntimeError):
    """No supported report/transition is confirmed by this exception."""

class CheckedRejection(Exception):
    """Only an actual well-formed negative answer from the Lean checker."""

def atomic_json(path: Path, data: Any) -> None:
    raw = gate.encode(data)
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w', encoding='utf-8') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

class MeasuredChecker(gate.LeanChecker):
    def __init__(self, run_dir: Path, seconds: float = 30):
        self.run_dir = run_dir
        self.phase = 'initialization'
        self.environment_calls = 0
        self.environment_seconds = 0.0
        super().__init__(ROOT, seconds=seconds)

    def environment(self) -> dict[str, Any]:
        t = time.monotonic()
        try:
            return super().environment()
        finally:
            self.environment_calls += 1
            self.environment_seconds += time.monotonic() - t

    def request(self, payload: Any) -> bool:
        index = len(self.records)
        request = self.run_dir / 'requests' / f'checker_{index:03d}.json'
        atomic_json(request, payload)
        try:
            return super().request(payload)
        finally:
            if len(self.records) > index:
                self.records[index].update(phase=self.phase,
                    request_file=str(request.relative_to(self.run_dir)),
                    request_file_sha256=sha(request))

    def check(self, target: Any, context: list[Any], proof: Any) -> bool:
        if not super().check(target, context, proof):
            raise CheckedRejection('actual Lean proof check returned false')
        return True

class LiveRun:
    """Single invocation, no auto-resume after faults or uncertain commits.

    Never uses a planner-predicted ticket to populate an external store view.
    Views are read from the protected store and actual receipt file.
    """
    def __init__(self, config_path: Path, run_dir: Path, *, planner_timeout: float = 60,
                 checker_timeout: float = 30):
        self.started = time.monotonic()
        self.config_path = config_path.resolve()
        # Do not turn a symlink destination into a different existing store.
        if run_dir.exists() or run_dir.is_symlink():
            raise ValueError('run directory must be new; existing stores are never resumed or overwritten')
        run_dir.mkdir(parents=True, exist_ok=False)
        self.run_dir = run_dir.resolve()
        (self.run_dir/'requests').mkdir()
        self.events: list[Any] = []
        self.calls: list[dict[str, Any]] = []
        self.attempts: list[dict[str, Any]] = []
        self.planning_work = 0
        self.planning_charge = Fraction(0)
        self.fee_debits = 0
        self.last_confirmed: dict[str, Any] | None = None
        self.status = 'initializing'
        self.error: dict[str, Any] | None = None
        self.planner_timeout = planner_timeout
        self.checker_timeout = checker_timeout
        self.checker: MeasuredChecker | None = None
        self.store: gate.ArtifactGate | None = None
        self.receipt_path = self.run_dir/'checked_receipt.json'
        self.target_path: Path | None = None
        self.candidate_paths: list[Path] = []
        self.target_raw = ''
        self.candidate_raw: list[str] = []
        self.config: dict[str, Any] = {}
        self.spec: dict[str, Any] = {}
        self.environment: dict[str, Any] = {}
        self.identity: list[Any] = []
        self.job: list[Any] = []
        self.initialization_seconds = 0.0

    def initialize(self) -> None:
        raw = gate.read_raw(self.config_path)
        c = gate.strict_json(raw)
        allowed = {'prior_true','success_if_false','success_if_true','register_fee','verify_fee',
          'admit_fee','admission_value','research_budget','horizon','planning_work_per_decision',
          'planning_price_per_unit','target_file','candidate_files'}
        if not isinstance(c, dict) or set(c) - allowed:
            raise ValueError('unknown configuration fields; externally supplied reports are forbidden')
        required = allowed - {'planning_price_per_unit'}
        if not required <= set(c):
            raise ValueError('missing live configuration fields')
        if not isinstance(c['target_file'],str) or not isinstance(c['candidate_files'],list):
            raise ValueError('target_file and candidate_files are required path values')
        if not 1 <= len(c['candidate_files']) <= 8 or not all(isinstance(x,str) for x in c['candidate_files']):
            raise ValueError('one to eight candidate file paths required')
        # The real backend is a deterministic data checker, not a sampled
        # availability service. Do not claim a fictitious calibrated channel.
        if planner.fraction(c['success_if_false']) != [1,1] or planner.fraction(c['success_if_true']) != [1,1]:
            raise ValueError('this live backend requires deterministic availability: both success_if fields must be 1')
        self.config = c
        base = self.config_path.parent
        self.target_path = base / c['target_file']
        self.candidate_paths = [base / p for p in c['candidate_files']]
        self.target_raw = gate.read_raw(self.target_path)
        self.spec = gate.parse_target(self.target_raw)
        if self.spec['dependencies']:
            raise ValueError('single-root live adapter does not support dependencies')
        self.candidate_raw = [gate.read_raw(p) for p in self.candidate_paths]
        for text in self.candidate_raw:
            gate.validate_proof(gate.strict_json(text))
        self.checker = MeasuredChecker(self.run_dir, self.checker_timeout)
        self.store = gate.ArtifactGate(self.run_dir/'store', self.checker)
        self.environment = self.checker.environment()
        self.identity = [self.spec['task'], self.spec['statement'], self.target_raw, [],
                         [[k,gate.encode(v)] for k,v in sorted(self.environment.items())]]
        model = {k:v for k,v in c.items() if k not in {'target_file','candidate_files'}}
        model.update(target_text=gate.encode(self.spec['statement']), candidate_texts=self.candidate_raw)
        self.job = planner.wire_request(model,base)
        self.status='running'
        self.initialization_seconds = time.monotonic()-self.started
        self.persist()

    def assert_fixed_catalogue(self) -> None:
        assert self.checker is not None and self.target_path is not None
        if gate.read_raw(self.target_path) != self.target_raw:
            raise OperationalFault('target changed since initialization')
        for path, original in zip(self.candidate_paths,self.candidate_raw):
            if gate.read_raw(path) != original:
                raise OperationalFault('candidate changed since initialization')
        if self.checker.environment() != self.environment:
            raise OperationalFault('checker environment changed since initialization')

    def actual_view(self) -> list[Any]:
        assert self.store is not None
        s=self.store.load()
        if not set(s['admitted']) <= {self.spec['task']}:
            raise OperationalFault('unexpected admitted task in root store')
        pending = s['pending']
        checked = None
        if self.receipt_path.exists():
            receipt=gate.strict_json(gate.read_raw(self.receipt_path))
            gate.exact_keys(receipt,{'schema','subject','approved'})
            if receipt['schema'] != 'avoc-receipt-1' or receipt['approved'] is not True:
                raise OperationalFault('malformed checked receipt')
            checked=[gate.wire_ticket(receipt['subject']),True]
        record=s['admitted'].get(self.spec['task'])
        if record is not None:
            gate.exact_keys(record,{'schema','ticket'})
            if record['schema']!='avoc-admission-1':raise OperationalFault('malformed admission record')
        return [[s['next'],None if pending is None else gate.wire_ticket(pending)],
                checked,None if record is None else gate.wire_ticket(record['ticket'])]

    def ask_monitor(self, mode: str, events: list[Any] | None = None) -> dict[str, Any]:
        events = self.events if events is None else events
        actual_before = self.actual_view()
        wire=['avoc-live-v1',self.job,self.identity,events,actual_before,mode]
        request=self.run_dir/'requests'/f'planner_{len(self.calls):03d}_{mode}.json'
        atomic_json(request,wire)
        if request.stat().st_size>2097152:raise OperationalFault('live request size limit')
        lean,env=planner.runtime()
        cmd=[str(lean),'-j1','-DwarningAsError=true','--run',str(ROOT/'tools/LivePlannerMain.lean'),str(request)]
        start=time.monotonic()
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              text=True,start_new_session=True)
        timed_out=False
        try:out,err=proc.communicate(timeout=self.planner_timeout)
        except subprocess.TimeoutExpired:
            timed_out=True;os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate()
        record={'mode':mode,'command':cmd,'seconds':time.monotonic()-start,
                'returncode':proc.returncode,'timed_out':timed_out,'request':str(request.relative_to(self.run_dir)),
                'request_sha256':sha(request),'stdout':out,'stderr':err,
                'entrypoint_sha256':sha(ROOT/'tools/LivePlannerMain.lean')}
        self.calls.append(record)
        if timed_out:raise OperationalFault('planner/monitor timed out; no decision/evidence certificate issued')
        if proc.returncode or err.strip():raise OperationalFault('planner/monitor rejected: '+err.strip()[:350])
        if self.actual_view() != actual_before:
            raise OperationalFault('store changed during planner/monitor execution')
        result=gate.strict_json(out)
        if not isinstance(result,dict) or result.get('status')!='ok' or result.get('backend')!='AVOC-v0.19-live-monitor':
            raise OperationalFault('unexpected planner/monitor response')
        if result.get('matched_external') is not True or result.get('confirmed_steps')!=len(events):
            raise OperationalFault('incomplete external match')
        work=result['new_planning_work']
        if type(work) is not int or work<0:raise OperationalFault('invalid work counter')
        rec=result.get('recommendation')
        if mode=='observe' and (work!=0 or rec is not None):raise OperationalFault('observation mode performed hidden search')
        if rec is not None:
            if rec['work_used']!=work or work>rec['work_reserved'] or rec['work_reserved']>self.config['planning_work_per_decision']:
                raise OperationalFault('planning credit violation')
            self.planning_charge += Fraction(rec['declared_planning_charge'])
        self.planning_work += work
        return result

    def before_stage(self, action: dict[str, Any]) -> None:
        """Subclass seam for controlled fault-injection tests; not a config action."""

    def after_stage(self, action: dict[str, Any]) -> None:
        """Subclass seam for testing uncertain commits and concurrent drift."""

    def execute_stage(self, action: dict[str, Any]) -> bool:
        assert self.store is not None and self.checker is not None and self.target_path is not None
        kind=action['kind'];self.checker.phase=kind
        if kind=='register':
            c=action['candidate']
            if type(c) is not int or not 0<=c<len(self.candidate_paths):raise OperationalFault('invalid selected candidate')
            self.store.register(self.target_path,self.candidate_paths[c])
            self.receipt_path.unlink(missing_ok=True)
            return False
        if kind=='verify':
            # Only CheckedRejection represents normal negative proof evidence.
            # GateError, timeout, malformed output, and environment mismatch do not.
            try:receipt=self.store.verify()
            except CheckedRejection:
                self.receipt_path.unlink(missing_ok=True)
                return False
            atomic_json(self.receipt_path,receipt)
            return True
        if kind=='admit':
            receipt=gate.strict_json(gate.read_raw(self.receipt_path))
            self.store.admit(receipt)
            self.receipt_path.unlink(missing_ok=True)
            return False
        if kind=='stop':return False
        raise OperationalFault('unknown planner action')

    def perform(self) -> dict[str, Any]:
        try:
            self.initialize()
            while len(self.events)<self.config['horizon']:
                self.assert_fixed_catalogue()
                answer=self.ask_monitor('plan')
                self.last_confirmed=answer['current']
                rec=answer['recommendation']
                if rec is None:break
                action=rec['action'];kind=action['kind']
                stage_fee=0 if kind=='stop' else self.config[kind+'_fee']
                if type(stage_fee) is not int or stage_fee<0 or self.fee_debits+stage_fee>self.config['research_budget']:
                    raise OperationalFault('attempted nominal debit exceeds original research budget')
                self.fee_debits+=stage_fee  # conservative reservation before the external operation
                row={'action':copy.deepcopy(action),'nominal_debit':stage_fee,'status':'intent',
                     'confirmed_before':copy.deepcopy(self.last_confirmed),'recommendation':rec}
                self.attempts.append(row);self.persist()  # write-ahead intent; no crash auto-resume
                start=time.monotonic()
                try:
                    self.before_stage(action)
                    self.assert_fixed_catalogue()
                    report=self.execute_stage(action)
                    self.after_stage(action)
                    self.assert_fixed_catalogue()
                    aw=['register',action['candidate']] if kind=='register' else [kind]
                    event=[aw,['report',report,self.actual_view()]]
                    candidate_history=self.events+[copy.deepcopy(event)]
                    ack=self.ask_monitor('observe',candidate_history)
                    # Only now adopt the transition as confirmed.
                    self.events=candidate_history
                    self.last_confirmed=ack['current']
                    row.update(status='confirmed',report=report,after=ack['current'])
                finally:
                    row['seconds_including_monitor_and_snapshot_checks']=time.monotonic()-start
                    self.persist()
                if kind=='stop' or self.last_confirmed['completed']:break
            self.status='admitted' if self.last_confirmed and self.last_confirmed['completed'] else 'stopped'
        except (Exception,) as exc:
            self.status='aborted_unconfirmed'
            self.error={'type':type(exc).__name__,'message':str(exc),
                'interpretation':'No exception is a negative Bayesian report. Retain the last confirmed prefix; do not auto-resume.'}
            if self.attempts and self.attempts[-1]['status']=='intent':self.attempts[-1]['status']='unconfirmed'
        self.persist()
        return self.summary()

    def summary(self) -> dict[str, Any]:
        checker_records=[] if self.checker is None else self.checker.records
        return {'schema':'avoc-live-run-1','status':self.status,'error':self.error,
            'config_path':str(self.config_path),'config_sha256':sha(self.config_path) if self.config_path.is_file() else None,
            'confirmed_steps':len(self.events),'confirmed_state':self.last_confirmed,
            'events':self.events,'stage_attempts':self.attempts,
            'nominal_fees_debited_including_unconfirmed_attempts':self.fee_debits,
            'planning_tree_work_total':self.planning_work,'declared_planning_charge':str(self.planning_charge),
            'planner_monitor_processes':self.calls,'checker_processes':checker_records,
            'measured':{'elapsed_seconds_including_setup':time.monotonic()-self.started,
              'initialization_seconds':self.initialization_seconds,
              'planner_monitor_process_seconds':sum(r['seconds'] for r in self.calls),
              'checker_process_seconds':sum(r['seconds'] for r in checker_records),
              'environment_capture_calls':0 if self.checker is None else self.checker.environment_calls,
              'environment_capture_seconds':0 if self.checker is None else self.checker.environment_seconds},
            'scope':'Actual protected root-store operations and executed Lean planning/monitoring. Measured elapsed categories overlap; do not sum them. No empirically calibrated LLM or optimal charged utility.',
            'failure_boundary':'A process may commit before an acknowledgement fails. Inspect actual store and intent journal; no rollback/automatic recovery claimed.',
            'source_sha256':{p:sha(ROOT/p) for p in ['tools/run_live_workflow.py','tools/artifact_gate.py',
                'tools/LivePlannerMain.lean','AVOC/LiveExecution.lean','AVOC/LiveExecutionCodec.lean']}}

    def persist(self) -> None:
        atomic_json(self.run_dir/'run.json',self.summary())

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('config',type=Path);p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--planner-timeout',type=float,default=60);p.add_argument('--checker-timeout',type=float,default=30)
    a=p.parse_args()
    try:
        if not 0<a.planner_timeout<=300 or not 0<a.checker_timeout<=300:raise ValueError('timeouts must be in (0,300] seconds')
        run=LiveRun(a.config,a.run_dir,planner_timeout=a.planner_timeout,checker_timeout=a.checker_timeout)
        result=run.perform()
        small={k:result[k] for k in ['status','error','confirmed_steps','confirmed_state',
            'nominal_fees_debited_including_unconfirmed_attempts','planning_tree_work_total','declared_planning_charge','measured']}
        small['record']=str(run.run_dir/'run.json');print(json.dumps(small,indent=2))
        return 2 if result['status']=='aborted_unconfirmed' else 0
    except (ValueError,OSError) as e:
        print('ERROR: '+str(e),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
