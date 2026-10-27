#!/usr/bin/env python3
"""Actual live Lean planner/checker/store tests in new temporary directories.

Fault injections are controlled test subclasses, not user-enabled actions. The
successful cases do not provide artificial Boolean reports to the planner.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import run_live_workflow as live
import artifact_gate as gate

RD=ROOT/'results/v0.19.0/live_tests';RD.mkdir(parents=True,exist_ok=True)

def fixture(base, **changes):
    p=base/'input';p.mkdir()
    (p/'target.json').write_text(json.dumps({'schema':'avoc-proposition-1','task':'root-proof',
        'statement':['imp',['atom',0],['atom',0]],'dependencies':[]}))
    (p/'good.json').write_text(json.dumps(['intro',['atom',0],['hyp',['atom',0]]]))
    (p/'bad.json').write_text('["true"]')
    c=dict(prior_true='1/2',success_if_false=1,success_if_true=1,register_fee=1,verify_fee=1,
           admit_fee=1,admission_value=8,research_budget=3,horizon=3,
           planning_work_per_decision=3000,planning_price_per_unit='1/1000',
           target_file='target.json',candidate_files=['bad.json','good.json'])
    c.update(changes); path=p/'config.json';path.write_text(json.dumps(c))
    return path

def require(x,msg):
    if not x:raise AssertionError(msg)

def checked_summary(r,expect):
    require(r['status']==expect,str(r['error']))
    require(all(c['mode']=='plan' or json.loads(c['stdout']).get('new_planning_work')==0
                for c in r['planner_monitor_processes'] if c['returncode']==0),'hidden search on replay')
    return {'status':r['status'],'error':r['error'],'confirmed_steps':r['confirmed_steps'],
            'confirmed_state':r['confirmed_state'],
            'debits':r['nominal_fees_debited_including_unconfirmed_attempts'],
            'planning_work':r['planning_tree_work_total'],
            'stages':[{'action':a['action'],'status':a['status']} for a in r['stage_attempts']],
            'checker_processes':r['checker_processes'],
            'monitor_processes':[dict(mode=c['mode'],returncode=c['returncode'],
                timed_out=c['timed_out'],seconds=c['seconds'],stderr=c['stderr'],
                stdout_sha256=hashlib.sha256(c['stdout'].encode()).hexdigest(),
                request_sha256=c['request_sha256']) for c in r['planner_monitor_processes']],
            'measured':r['measured'],'source_sha256':r['source_sha256']}

class Mutation(live.LiveRun):
    def before_stage(self,a):
        if a['kind']=='verify':
            assert self.target_path is not None
            self.target_path.write_text(self.target_raw+' ')

class CandidateMutation(live.LiveRun):
    def before_stage(self,a):
        if a['kind']=='verify':
            path=self.candidate_paths[1];path.write_text(path.read_text()+' ')

class GenerationDrift(live.LiveRun):
    def after_stage(self,a):
        if a['kind']=='register':
            s=self.store.load();s['next']+=1;self.store.save(s)

class CheckerTimeout(live.LiveRun):
    def before_stage(self,a):
        if a['kind']=='verify':self.checker.seconds=0.000001

class CommitUncertain(live.LiveRun):
    def after_stage(self,a):
        if a['kind']=='admit':raise live.OperationalFault('injected failure after real admission commit')

class WrongReceipt(live.LiveRun):
    def after_stage(self,a):
        if a['kind']=='verify':
            r=gate.strict_json(gate.read_raw(self.receipt_path))
            r['subject']['generation']+=1
            live.atomic_json(self.receipt_path,r)

class EnvironmentDrift(live.LiveRun):
    def before_stage(self,a):
        if a['kind']=='verify':
            original=self.checker.environment
            def changed():
                x=original();x['test_drift']=True;return x
            self.checker.environment=changed

CASES=['real_success','no_search_stop','short_horizon_stop','zero_budget_stop',
       'all_candidates_invalid','target_mutation','generation_mismatch','checker_timeout',
       'uncertain_commit','substituted_receipt','environment_drift','planner_timeout',
       'reports_forbidden','dependencies_forbidden','uncalibrated_channel_forbidden',
       'existing_directory_refused','zero_support_report_refused','fault_not_negative_evidence',
       'old_receipt_replay_refused','changed_candidate_bytes','root_formula_falsity',
       'incomplete_trace_no_admission']

def run_case(name,base):
    if name=='existing_directory_refused':
        cfg=fixture(base);out=base/'run';out.mkdir();sentinel=out/'keep';sentinel.write_text('unchanged')
        try:live.LiveRun(cfg,out)
        except ValueError:pass
        else:raise AssertionError('existing directory accepted')
        require(sentinel.read_text()=='unchanged','existing file changed')
        return {'expected_rejection':True}
    changes={}
    if name=='no_search_stop':changes['planning_work_per_decision']=0
    if name=='short_horizon_stop':changes['horizon']=2
    if name=='zero_budget_stop':changes['research_budget']=0
    if name=='all_candidates_invalid':changes['candidate_files']=['bad.json']
    if name=='reports_forbidden':changes['public_reports']=[True]
    if name=='uncalibrated_channel_forbidden':changes['success_if_true']='3/4'
    cfg=fixture(base,**changes)
    if name=='dependencies_forbidden':
        p=cfg.parent/'target.json';c=json.loads(p.read_text());c['dependencies']=['other'];p.write_text(json.dumps(c))
    if name=='root_formula_falsity':
        p=cfg.parent/'target.json';c=json.loads(p.read_text());c['statement']=['false'];p.write_text(json.dumps(c))
    cls={'target_mutation':Mutation,'changed_candidate_bytes':CandidateMutation,'generation_mismatch':GenerationDrift,
         'checker_timeout':CheckerTimeout,'uncertain_commit':CommitUncertain,
         'substituted_receipt':WrongReceipt,'environment_drift':EnvironmentDrift}.get(name,live.LiveRun)
    run=cls(cfg,base/'run',planner_timeout=0.000001 if name=='planner_timeout' else 60)
    if name in {'zero_support_report_refused','fault_not_negative_evidence','incomplete_trace_no_admission'}:
        run.initialize();a=run.ask_monitor('plan')['recommendation']['action']
        require(a['kind']=='register' and a['candidate']==1,'did not choose valid candidate')
        report=run.execute_stage(a)
        event=[['register',1],['report',report,run.actual_view()]]
        ack=run.ask_monitor('observe',[event]);run.events=[event];run.last_confirmed=ack['current']
        before=copy.deepcopy(run.last_confirmed)
        if name=='incomplete_trace_no_admission':
            require(not before['completed'] and before['pending'],'registration admitted')
            require(not run.store.load()['admitted'],'external admission at registration')
            return {'registration_only_no_admission':True,'actual_generation':run.store.load()['next']}
        extra=[['verify'],['fault','tool timeout']] if name=='fault_not_negative_evidence' else [
                ['verify'],['report',False,run.actual_view()]]
        try:run.ask_monitor('observe',run.events+[extra])
        except live.OperationalFault as e:
            expected='not Bayesian evidence' if name=='fault_not_negative_evidence' else 'outside declared model support'
            require(expected in str(e),str(e))
        else:raise AssertionError('unsupported report admitted')
        require(run.last_confirmed==before and len(run.events)==1,'failure advanced confirmed prefix')
        require(not run.store.load()['admitted'],'failed monitor admitted')
        return {'expected_rejection':True,'posterior_unchanged':True,'monitor_error':run.calls[-1]['stderr']}
    r=run.perform()
    successes={'real_success','old_receipt_replay_refused'}
    stops={'no_search_stop','short_horizon_stop','zero_budget_stop','all_candidates_invalid','root_formula_falsity'}
    expected='admitted' if name in successes else 'stopped' if name in stops else 'aborted_unconfirmed'
    out=checked_summary(r,expected)
    state=run.store.load() if run.store else None
    if name in successes:
        require(r['confirmed_steps']==3,'wrong completed trace length')
        require(r['stage_attempts'][0]['action']=={'kind':'register','candidate':1},'bad proof selected')
        require(len(state['admitted'])==1 and state['pending'] is None,'no actual protected-store admission')
        record=next(iter(state['admitted'].values()))
        require(record['ticket']['candidate_bytes']==run.candidate_raw[1],'wrong source admitted')
        require(r['confirmed_state']['posterior_true']=='1/2','fictitious evidence update')
        require([c['phase'] for c in r['checker_processes']]==['verify','admit','admit'],'actual check count wrong')
        require(r['nominal_fees_debited_including_unconfirmed_attempts']==3,'fee mismatch')
        if name=='old_receipt_replay_refused':
            receipt={'schema':'avoc-receipt-1','subject':record['ticket'],'approved':True}
            try:run.store.admit(receipt)
            except gate.GateError:pass
            else:raise AssertionError('old receipt consumed twice')
            out['replay_rejected']=True
    if name in stops:
        require(not state['admitted'] and r['nominal_fees_debited_including_unconfirmed_attempts']==0,'stop changed research store')
    if name in {'checker_timeout','target_mutation','changed_candidate_bytes','environment_drift'}:
        require(r['confirmed_steps']==1 and not state['admitted'] and state['pending'] is not None,'fault advanced state')
        require(r['confirmed_state']['posterior_true']=='1/2','fault used as Bayesian evidence')
        require(r['nominal_fees_debited_including_unconfirmed_attempts']==2,'attempted cost silently discarded')
    if name=='checker_timeout':require(any(c['timed_out'] for c in r['checker_processes']),'no real checker timeout')
    if name=='uncertain_commit':
        require(len(state['admitted'])==1,'not a real post-commit failure')
        require(r['confirmed_steps']==2 and not r['confirmed_state']['completed'],'uncertain commit reported as confirmed success')
        out['real_store_committed_but_unconfirmed']=True
    if name in {'substituted_receipt','generation_mismatch'}:
        require(not state['admitted'],'mismatch admitted')
    if name=='planner_timeout':
        require(r['confirmed_steps']==0 and not state['admitted'],'planner timeout caused external actions')
        require(r['planner_monitor_processes'][0]['timed_out'],'no real planner timeout')
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=100)
    a=p.parse_args()
    for name in CASES[a.start:a.start+a.count]:
        t=time.monotonic()
        with tempfile.TemporaryDirectory(prefix='avoc_live_regression_') as d:
            result=run_case(name,Path(d))
        row={'case':name,'passed':True,'seconds':time.monotonic()-t,'result':result,
             'test_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (RD/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n')
        print('PASS',name,round(row['seconds'],3),flush=True)

if __name__=='__main__':main()
