#!/usr/bin/env python3
"""Crash/recovery regression using real SQLite writes and Lean subprocesses.
Each case owns a fresh directory. SIGKILL is injected at exact write/ack phases.
No crash outcome is replaced by mocked Bayesian evidence.
"""
from pathlib import Path
import argparse,copy,fcntl,hashlib,json,os,signal,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import run_recoverable_workflow as live
import artifact_gate as gate
from recoverable_store import Database, RecoveryError

RD=ROOT/'results/v0.20.0/recovery_tests'
CASES=['normal_and_duplicate_resume','after_commit_register','after_commit_verify','after_commit_admit',
 'before_ack_admit','after_ack_register','after_ack_admit','after_intent_register','after_intent_verify',
 'after_evaluation_admit','after_store_write_admit','after_result_write_admit','after_commit_stop',
 'mutated_commit_sequence','mutated_poststate','changed_candidate','changed_config','concurrent_lock',
 'unknown_intent_never_report','duplicate_publication','incomplete_initialization','forbidden_reports']

def require(ok,msg):
    if not ok:raise AssertionError(msg)

def fixture(base,**changes):
    p=base/'input';p.mkdir(parents=True)
    (p/'target.json').write_text(json.dumps({'schema':'avoc-proposition-1','task':'root-proof',
      'statement':['imp',['atom',0],['atom',0]],'dependencies':[]}))
    (p/'good.json').write_text(json.dumps(['intro',['atom',0],['hyp',['atom',0]]]))
    (p/'bad.json').write_text('["true"]')
    c=dict(prior_true='1/2',success_if_false=1,success_if_true=1,register_fee=1,verify_fee=1,
      admit_fee=1,admission_value=8,research_budget=3,horizon=3,planning_work_per_decision=3000,
      planning_price_per_unit='1/1000',target_file='target.json',candidate_files=['bad.json','good.json'])
    c.update(changes);path=p/'config.json';path.write_text(json.dumps(c));return path

def cli(config,run_dir,command='start',recover_only=False):
    cmd=[sys.executable,str(ROOT/'tools/run_recoverable_workflow.py'),command]
    if command=='start':cmd.append(str(config))
    cmd+=['--run-dir',str(run_dir)]
    if recover_only:cmd+=['--recover-only']
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    try:out=json.loads(proc.stdout if proc.stdout.strip() else proc.stderr)
    except json.JSONDecodeError:raise AssertionError(proc.stdout+'\n'+proc.stderr)
    return proc.returncode,out

def crash(config,run_dir,point,stage):
    cmd=[sys.executable,str(ROOT/'checks/recovery_crash_worker.py'),str(config),str(run_dir),point,stage]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    require(proc.returncode==-signal.SIGKILL,f'not SIGKILL: {proc.returncode} {proc.stdout} {proc.stderr}')
    return {'signal':'SIGKILL','point':point,'stage':stage,'returncode':proc.returncode}

def snap(run_dir):
    db=Database(run_dir/'state.sqlite3')
    try:
        ops=db.operations();native,checked=db.snapshot()
        calls=[gate.strict_json(r[0]) for r in db.db.execute('SELECT record FROM invocations ORDER BY id')]
        return {'phases':[o['phase'] for o in ops],'sequence':[o['sequence'] for o in ops],
          'admissions':len(native['admitted']),'next':native['next'],'pending':native['pending'] is not None,
          'checked':checked is not None,'fees':db.get('attempt_debits'),
          'checker_calls':sum(c['kind']=='checker' for c in calls),
          'planner_calls':sum(c['kind']=='planner' for c in calls),
          'confirmed':sum(o['phase']=='acknowledged' for o in ops),
          'core_hash':hashlib.sha256(gate.encode([native,checked,ops]).encode()).hexdigest()}
    finally:db.close()

def run_case(name,base):
    run_dir=base/'run';changes={}
    if name=='after_commit_stop':changes['planning_work_per_decision']=0
    if name=='forbidden_reports':changes['reports']=[True]
    config=fixture(base,**changes)
    if name=='normal_and_duplicate_resume':
        code,out=cli(config,run_dir);require(code==0 and out['status']=='admitted',str(out))
        before=snap(run_dir)
        for _ in range(2):
            code,out=cli(config,run_dir,'resume')
            require(code==0 and out['last_recovery_disposition']=='already_acknowledged',str(out))
            after=snap(run_dir)
            for k in ['fees','checker_calls','planner_calls','confirmed','admissions','next','core_hash']:
                require(before[k]==after[k],'duplicate resume changed '+k)
        require(out['checker_invocations']==3 and out['confirmed_steps']==3,'bad normal counts')
        return {'normal':out,'before':before,'after':snap(run_dir)}
    if name.startswith(('after_','before_ack_')):
        point,stage=name.rsplit('_',1)
        injected=crash(config,run_dir,point,stage);before=snap(run_dir)
        code,out=cli(config,run_dir,'resume',recover_only=True);after=snap(run_dir)
        uncommitted=point in ('after_intent','after_evaluation','after_store_write','after_result_write')
        if uncommitted:
            require(code==2 and out['status']=='aborted_uncommitted',str(out))
            require(before==after,'unfinished recovery changed state, calls or debit')
            if stage=='admit':require(after['admissions']==0 and after['confirmed']==2,'uncommitted admission appeared')
        else:
            require(code==0,str(out))
            require(after['checker_calls']==before['checker_calls'],'recovery reran checker')
            require(after['planner_calls']==before['planner_calls'],'recovery reran planner')
            require(after['fees']==before['fees'],'recovery charged fee twice')
            require(after['next']==before['next'],'recovery re-registered')
            expected=before['confirmed']+(point!='after_ack')
            require(after['confirmed']==expected,'wrong acknowledgement count')
            if stage=='admit':require(before['admissions']==after['admissions']==1,'commit lost or repeated')
            # Resume normally after acknowledging the committed prefix.
            code,finished=cli(config,run_dir,'resume')
            require(code==0 and finished['status']==('stopped' if stage=='stop' else 'admitted'),str(finished))
            out['normal_continuation']=finished
        return {'crash':injected,'before':before,'recovery':out,'after_recovery':after}
    if name in ('mutated_commit_sequence','mutated_poststate','changed_candidate','changed_config',
                'concurrent_lock','unknown_intent_never_report','duplicate_publication'):
        point='after_intent' if name=='unknown_intent_never_report' else 'after_commit'
        crash(config,run_dir,point,'register');before=snap(run_dir)
        db=Database(run_dir/'state.sqlite3')
        try:
            op=db.operations()[-1]
            if name=='mutated_commit_sequence':
                r=op['receipt'];r[0][0]+=1
                db.db.execute('UPDATE operations SET receipt=? WHERE sequence=0',(gate.encode(r),))
            elif name=='mutated_poststate':
                s,ch=db.snapshot();s['next']+=1
                db.db.execute('UPDATE store SET native=? WHERE id=1',(gate.encode(s),))
            elif name=='duplicate_publication':
                try:db.commit(op,op['after_native'],op['after_checked'],False,'root-proof')
                except RecoveryError:pass
                else:raise AssertionError('published twice')
                require(snap(run_dir)==before,'duplicate publish changed store')
                return {'duplicate_publish_rejected':True,'state':before}
        finally:db.close()
        if name=='changed_candidate':
            p=config.parent/'good.json';p.write_text(p.read_text()+' ')
        if name=='changed_config':config.write_text(config.read_text()+' ')
        if name=='concurrent_lock':
            with live.exclusive_run(run_dir):code,out=cli(config,run_dir,'resume')
        else:code,out=cli(config,run_dir,'resume')
        require(code==2,'unexpected recovery success '+str(out))
        after=snap(run_dir)
        require(after['confirmed']==before['confirmed'] and after['checker_calls']==before['checker_calls'],
                'invalid recovery admitted or checked')
        return {'before':before,'after':after,'rejection':out}
    if name=='incomplete_initialization':
        run_dir.mkdir();db=Database(run_dir/'state.sqlite3',create=True);db.close()
        code,out=cli(config,run_dir,'resume');require(code==2,'incomplete run resumed')
        return out
    if name=='forbidden_reports':
        code,out=cli(config,run_dir);require(code==2,'reports accepted')
        return out
    raise AssertionError('unknown test '+name)

p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=1)
a=p.parse_args();RD.mkdir(parents=True,exist_ok=True)
for name in CASES[a.start:a.start+a.count]:
    stamp=str(time.time_ns());base=RD/(name+'_'+stamp);base.mkdir()
    start=time.monotonic()
    try:
        result=run_case(name,base)
        record={'case':name,'passed':True,'seconds':time.monotonic()-start,'directory':str(base.relative_to(ROOT)),
                'result':result,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_pins':live.pins()}
    except Exception as e:
        record={'case':name,'passed':False,'error':repr(e),'directory':str(base.relative_to(ROOT))}
        (RD/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n');print(record,flush=True);raise
    (RD/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    print('PASS',name,round(record['seconds'],2),flush=True)
