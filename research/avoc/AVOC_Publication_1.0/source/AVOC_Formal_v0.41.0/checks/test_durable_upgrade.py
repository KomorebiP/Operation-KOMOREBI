#!/usr/bin/env python3
"""Independent bounded oracle and actual-process tests for v0.24.
No user store is touched. Tests own new directories and use injected process exits.
"""
from __future__ import annotations
import argparse, copy, fcntl, hashlib, json, os
from pathlib import Path
import random, sqlite3, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import durable_upgrade_campaign as app

CORE='AVOC-upgrade-checker-v1'
OBJ='retry-action-NoRevival;visits-horizons-0-1-2-4-8-16-32;v1'
BAD={'parent':'dynamic','revision':0,'candidate':'always_retry'}
GOOD={'parent':'dynamic','revision':0,'candidate':'threshold'}


def initial(): return [['dynamic','dynamic',0,0,0,0,0],None,[]]
def proposal(name, parent='dynamic', rev=0): return [parent,rev,name,CORE,OBJ]
def err(message): raise ValueError(message)


def raw_step(credit,s,p):
    out=copy.deepcopy(s)
    if s[4]+3+s[5]>credit:return out,'unfunded',0,0
    out[3]+=1;out[4]+=3
    U={'dynamic':-70,'threshold':-7,'always_retry':-7}
    eligible=(p[0]==s[1] and p[1]==s[2] and p[3]==CORE and p[4]==OBJ
              and p[2]!='always_retry' and U[s[1]]+9<=U[p[2]]
              and out[4]+s[5]+1<=credit)
    if eligible:
        out[1]=p[2];out[2]+=1;out[5]+=1;out[6]+=8
    return out,('promoted' if eligible else 'rejected'),3,(1 if eligible else 0)


def oracle(credit,j,cmd):
    out=copy.deepcopy(j);s,pending,closed=out
    op=cmd[0];key=cmd[1][0] if op=='begin' else cmd[1]
    rec=next((r for r in closed if r[0][0]==key),None)
    if op=='begin':
        t=cmd[1]
        if rec:
            if rec[0]!=t:err('key/request conflict')
            return out,False,0,0
        if pending:
            if pending!=t:err('pending evaluation or key conflict')
            return out,False,0,0
        if t[1]!=s:err('stale complete parent state')
        if s[4]+3+s[5]>credit:err('evaluation credit exhausted')
        out[0][3]+=1;out[0][4]+=3;out[1]=copy.deepcopy(t)
        return out,True,3,0
    if op=='finish':
        if rec:return out,False,0,0
        if not pending:err('no pending evaluation')
        if pending[0]!=key:err('wrong pending key')
        expected=copy.deepcopy(pending[1]);expected[3]+=1;expected[4]+=3
        if s!=expected:err('reservation state mismatch')
        old=pending[1];p=pending[2]
        if old[4]+3+old[5]>credit:err('invalid reservation')
        ns,o,_,sw=raw_step(credit,old,p)
        out[0]=ns;out[1]=None;out[2].append([pending,['evaluated',o]])
        return out,True,0,sw
    if op=='abandon':
        if rec:
            if rec[1]!=['abandoned']:err('evaluated results cannot be abandoned')
            return out,False,0,0
        if not pending:err('no pending evaluation')
        if pending[0]!=key:err('wrong pending key')
        out[2].append([pending,['abandoned']]);out[1]=None
        return out,True,0,0
    err('invalid campaign command')


def differential(destination):
    rng=random.Random(240024)
    requests=[];expected=[]
    for budget in [0,2,3,4,6,7,10,20,100]:
        for seed in range(12):
            j=initial();history=[];known=[]
            for n in range(12):
                if rng.randrange(4)==0 and known:
                    cmd=['begin',copy.deepcopy(rng.choice(known))]
                    if rng.randrange(5)==0:cmd[1][2][2]='always_retry'
                elif j[1] and rng.randrange(4)!=0:
                    cmd=[rng.choice(['finish','finish','abandon']),j[1][0]]
                else:
                    before=copy.deepcopy(j[0])
                    if rng.randrange(7)==0:before[4]+=1
                    p=proposal(rng.choice(['dynamic','threshold','always_retry']),j[0][1],j[0][2])
                    if rng.randrange(8)==0:p[3]='wrong-core'
                    t=[f'k-{budget}-{seed}-{n}',before,p]
                    known.append(copy.deepcopy(t));cmd=['begin',t]
                requests.append(app.wire(budget,copy.deepcopy(history),copy.deepcopy(j),cmd,False))
                try:
                    new,change,ev,sw=oracle(budget,j,cmd)
                    expected.append({'status':'checked','journal':new,'changed':change,'evaluation_debit':ev,'switch_debit':sw})
                    j=new
                    if change:history.append(copy.deepcopy(cmd))
                except ValueError as e:expected.append({'status':'error','error':str(e)})
            # Forge the materialized checkpoint while retaining its canonical log.
            corrupted=copy.deepcopy(j);corrupted[0][4]+=1
            requests.append(app.wire(budget,history,corrupted,None,False))
            expected.append({'status':'error','error':'log/checkpoint mismatch'})
    lean,env,_=app.environment()
    destination.mkdir(parents=True,exist_ok=True)
    (destination/'oracle_requests.json').write_text(json.dumps(requests))
    start=time.monotonic()
    p=subprocess.run([str(lean),'--run',str(ROOT/'tools/DurableUpgradeBatch.lean')],
                     input=json.dumps(requests),capture_output=True,text=True,env=env,cwd=ROOT,timeout=90)
    (destination/'oracle_stdout.json').write_text(p.stdout)
    (destination/'oracle_stderr.log').write_text(p.stderr)
    assert p.returncode==0,p.stderr
    actual=json.loads(p.stdout);assert len(actual)==len(expected)
    for i,(a,e) in enumerate(zip(actual,expected)):
        for k,v in e.items(): assert a.get(k)==v,(i,k,a,e,requests[i])
    result={'passed':True,'cases':len(requests),'accepted':sum(e['status']=='checked' for e in expected),
            'rejected':sum(e['status']=='error' for e in expected),'seed':240024,
            'seconds':time.monotonic()-start,'scope':'finite independent Python state-transition oracle versus executed Lean'}
    (destination/'differential.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result,flush=True)


def db_view(p):
    with sqlite3.connect(p/'campaign.sqlite3') as db:
        meta=db.execute('select epoch,snapshot,active,revision from meta').fetchone()
        return {'epoch':meta[0],'snapshot':json.loads(meta[1]),'active':meta[2],'revision':meta[3],
                'events':db.execute('select seq,command from events order by seq').fetchall(),
                'requests':db.execute('select * from requests order by key').fetchall()}


def fail(fn, contains=None):
    try:fn()
    except (RuntimeError,ValueError,sqlite3.Error,subprocess.SubprocessError) as e:
        if contains:assert contains in str(e),(contains,str(e))
        return str(e)
    raise AssertionError('expected rejection')


def begin(p,key='good',epoch=0,prop=GOOD):return app.operate(p,'begin',key=key,expected_epoch=epoch,proposal=prop)
def finish(p,key='good'):return app.operate(p,'finish',key=key)
def inspect(p):return app.operate(p,'inspect')

def crash(p,op,point,key='good',epoch=0,prop=GOOD):
    payload={'key':key}
    if op=='begin':payload.update(expected_epoch=epoch,proposal=prop)
    code='''import json,os,sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nimport durable_upgrade_campaign as d\ndef hook(point):\n if point == sys.argv[4]: os._exit(97)\nd.operate(Path(sys.argv[2]),sys.argv[3],hook=hook,**json.loads(sys.argv[5]))\n'''
    proc=subprocess.run([sys.executable,'-c',code,str(ROOT/'tools'),str(p),op,point,json.dumps(payload)],
                        capture_output=True,text=True,timeout=70)
    assert proc.returncode==97,(point,proc.returncode,proc.stdout,proc.stderr)
    return {'point':point,'returncode':proc.returncode}


def live_case(name,p):
    if name=='normal_promotion':
        app.start(p,100);begin(p,'bad',0,BAD);finish(p,'bad')
        assert inspect(p)['summary']['evaluation_spent']==3
        begin(p,'good',2,GOOD);result=finish(p)
        deployed=app.operate(p,'invoke')
        assert result['summary']['net_endpoint_gain']==56
        assert sum(x['active_visits'] for x in deployed['active_component_execution'])==7
        before=db_view(p)
        assert not finish(p)['changed']
        assert not begin(p,'good',2,GOOD)['changed']
        assert db_view(p)==before
        return {'final':result,'executed':deployed}
    if name=='key_conflict':
        app.start(p,100);begin(p)
        before=db_view(p)
        fail(lambda:begin(p,prop=BAD),'different exact request')
        fail(lambda:begin(p,epoch=1),'different exact request')
        assert db_view(p)==before
        return inspect(p)
    if name=='stale_epoch_after_rejection':
        app.start(p,100);begin(p,'bad',0,BAD);finish(p,'bad')
        fail(lambda:begin(p,'good',0,GOOD),'stale expected')
        r=inspect(p);assert r['summary']['active']=='dynamic' and r['summary']['evaluation_spent']==3
        return r
    if name.startswith('crash_begin_'):
        app.start(p,100)
        point={'crash_begin_event':'begin_after_event_write','crash_begin_state':'begin_after_state_write',
               'crash_begin_commit':'begin_after_commit'}[name]
        c=crash(p,'begin',point)
        r=inspect(p)
        committed=name=='crash_begin_commit'
        assert r['summary']['evaluation_spent']==(3 if committed else 0)
        assert bool(r['journal'][1])==committed
        begin(p);assert inspect(p)['summary']['evaluation_spent']==3
        result=finish(p);assert result['summary']['active']=='threshold'
        return {'crash':c,'observed_after_restart':r,'final':result}
    if name.startswith('crash_finish_'):
        app.start(p,100);begin(p)
        point={'crash_finish_gate':'finish_after_gate','crash_finish_event':'finish_after_event_write',
               'crash_finish_state':'finish_after_state_write','crash_finish_commit':'finish_after_commit',
               'crash_finish_response':'finish_before_response'}[name]
        c=crash(p,'finish',point)
        r=inspect(p)
        committed=name in {'crash_finish_commit','crash_finish_response'}
        assert r['summary']['active']==('threshold' if committed else 'dynamic')
        assert r['summary']['evaluation_spent']==3
        result=finish(p)
        assert result['changed']==(not committed)
        assert result['summary']['switch_spent']==1 and result['summary']['evaluation_spent']==3
        assert not finish(p)['changed']
        return {'crash':c,'observed_after_restart':r,'final':result,'invocation':app.operate(p,'invoke')}
    if name=='abandonment_no_refund':
        app.start(p,7);begin(p)
        app.operate(p,'abandon',key='good');r=inspect(p)
        assert r['summary']['evaluation_spent']==3 and r['summary']['active']=='dynamic'
        assert not app.operate(p,'abandon',key='good')['changed']
        assert not finish(p)['changed']
        begin(p,'replacement',2,GOOD);out=finish(p,'replacement')
        assert out['summary']['evaluation_spent']==6 and out['summary']['switch_spent']==1
        return out
    if name=='abandon_after_commit_crash':
        app.start(p,100);begin(p);c=crash(p,'abandon','abandon_after_commit')
        out=app.operate(p,'abandon',key='good');assert not out['changed']
        assert out['summary']['evaluation_spent']==3
        return {'crash':c,'final':out}
    if name=='evaluated_not_abandonable':
        app.start(p,100);begin(p);finish(p)
        before=db_view(p);fail(lambda:app.operate(p,'abandon',key='good'),'cannot be abandoned')
        assert db_view(p)==before;return inspect(p)
    if name=='switch_credit_rejection':
        app.start(p,3);begin(p);out=finish(p)
        assert out['summary']['evaluation_spent']==3 and out['summary']['active']=='dynamic'
        assert out['journal'][2][0][1]==['evaluated','rejected']
        fail(lambda:begin(p,'next',2),'credit exhausted')
        return out
    if name=='unfunded_no_charge':
        app.start(p,2);before=db_view(p);fail(lambda:begin(p),'credit exhausted')
        assert db_view(p)==before;return inspect(p)
    if name=='deleted_failure_event':
        app.start(p,100);begin(p,'bad',0,BAD);finish(p,'bad');begin(p,'good',2,GOOD);finish(p)
        with sqlite3.connect(p/'campaign.sqlite3') as db:db.execute('delete from events where seq=0')
        return {'rejection':fail(lambda:inspect(p),'event history')}
    if name=='forged_active_pointer':
        app.start(p,100)
        with sqlite3.connect(p/'campaign.sqlite3') as db:db.execute("update meta set active='threshold'")
        return {'rejection':fail(lambda:app.operate(p,'invoke'),'dispatch pointer')}
    if name=='forged_checkpoint':
        app.start(p,100);v=db_view(p)['snapshot'];v[0][1]='threshold'
        with sqlite3.connect(p/'campaign.sqlite3') as db:db.execute('update meta set active=?,snapshot=?',('threshold',app.canonical(v)))
        return {'rejection':fail(lambda:app.operate(p,'invoke'),'log/checkpoint mismatch')}
    if name=='authority_drift':
        app.start(p,100);q=p/'authority.json';v=json.loads(q.read_text());v['credits']=9999;q.write_text(json.dumps(v))
        return {'rejection':fail(lambda:inspect(p),'authority record')}
    if name=='lock_exclusion':
        app.start(p,100)
        fd=os.open(p/'CAMPAIGN_LOCK',os.O_RDWR)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            return {'rejection':fail(lambda:inspect(p),'locked')}
        finally:os.close(fd)
    if name=='key_event_mismatch':
        app.start(p,100);begin(p)
        with sqlite3.connect(p/'campaign.sqlite3') as db:db.execute("update requests set epoch=5")
        return {'rejection':fail(lambda:inspect(p),'request/event identity')}
    if name=='wrong_objective_paid_rejection':
        app.start(p,100);wrong={**GOOD,'objective':'weakened-objective'}
        begin(p,'wrong',0,wrong);r=finish(p,'wrong')
        assert r['summary']['active']=='dynamic' and r['summary']['evaluation_spent']==3
        return r
    raise AssertionError(name)


NAMES=['normal_promotion','key_conflict','stale_epoch_after_rejection',
 'crash_begin_event','crash_begin_state','crash_begin_commit',
 'crash_finish_gate','crash_finish_event','crash_finish_state','crash_finish_commit','crash_finish_response',
 'abandonment_no_refund','abandon_after_commit_crash','evaluated_not_abandonable',
 'switch_credit_rejection','unfunded_no_charge','deleted_failure_event','forged_active_pointer',
 'forged_checkpoint','authority_drift','lock_exclusion','key_event_mismatch','wrong_objective_paid_rejection']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--differential',action='store_true');ap.add_argument('--start',type=int,default=0);ap.add_argument('--count',type=int,default=100)
    args=ap.parse_args();out=ROOT/'results/v0.24.0/tests';out.mkdir(parents=True,exist_ok=True)
    if args.differential:return differential(out)
    for name in NAMES[args.start:args.start+args.count]:
        p=out/name
        if p.exists():raise RuntimeError('test directory already exists: '+str(p))
        started=time.monotonic()
        result=live_case(name,p)
        record={'name':name,'passed':True,'seconds':time.monotonic()-started,'result':result,
                'test_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'implementation_sha256':hashlib.sha256((ROOT/'tools/durable_upgrade_campaign.py').read_bytes()).hexdigest()}
        (out/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
        print('PASS',name,flush=True)


if __name__=='__main__':main()
