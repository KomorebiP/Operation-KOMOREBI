#!/usr/bin/env python3
"""Exact differential and real-file regressions for the affine cache/guard.

Oracle: homogeneous matrix multiplication, direct syntax evaluation, explicit
image enumeration for small dimensions. It does not invoke the Lean equations
or the RREF algorithm to decide validity/rank. The RREF is only a candidate source.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import affine_cache as app
import factor_affine as proposer
RD=ROOT/'results/v0.30.0/cache_tests'


def mm(a,b,m,k,n):return [[sum(a[i][t]*b[t][j] for t in range(k))%5 for j in range(n)]for i in range(m)]
def eye(n):return [[int(i==j) for j in range(n)]for i in range(n)]
def hom(p):
    tag=p[0]
    if tag=='map':
        _,n,m,a,b=p
        return n,m,[a[i]+[b[i]] for i in range(m)]+[[0]*n+[1]]
    if tag=='id':return p[1],p[1],eye(p[1]+1)
    n,k,a=hom(p[1]);j,m,b=hom(p[2])
    if tag=='seq':
        assert k==j
        return n,m,mm(b,a,m+1,k+1,n+1)
    assert(n,k)==(j,m)
    return n,m,[[(a[i][j]+b[i][j])%5 for j in range(n+1)]for i in range(m)]+[[0]*n+[1]]

def nf(p):
    n,m,h=hom(p);return n,m,[r[:n]for r in h[:m]],[r[n]for r in h[:m]]
def run(p,x):
    if p[0]=='map':return [(sum(a*y for a,y in zip(row,x))+off)%5 for row,off in zip(p[3],p[4])]
    if p[0]=='id':return x[:]
    a=run(p[1],x)
    if p[0]=='seq':return run(p[2],a)
    return[(y+z)%5 for y,z in zip(a,run(p[2],x))]
def tariff(p):
    if p[0]=='map':return p[2]*(2*p[1]+1)
    if p[0]=='id':return 0
    v=tariff(p[1])+tariff(p[2]);n,m,_,_=nf(p)
    return v+(m if p[0]=='sum' else 0)

def norm_cost(p):
    if p[0]in('map','id'):return 0
    n,k,_,_=nf(p[1]);_,m,_,_=nf(p[2]);base=norm_cost(p[1])+norm_cost(p[2])
    return base+(2*m*n*k+m*(2*k+1) if p[0]=='seq' else m*(n+1))
def dense(n,m):return m*(2*n+1)
def factor_cost(n,m,r):return dense(n,r)+dense(r,m)
def check_cost(n,m,r):return 2*m*n*r+dense(r,m)+2*r*m*n+2*r*n*r+m*(n+1)+r*r
def reuse_cost(n,m,r):return check_cost(n,m,r)+m*n+dense(r,m)
def emission(n,m,r):return r*n+r+m*r+m+r*m+n*r

def valid(rec):
    _,n,m,a,b,c=rec;r,d,da,cm,cb,u,v=c
    return(mm(cm,d,m,r,n)==a and
           [(sum(cm[i][j]*da[j]for j in range(r))+cb[i])%5 for i in range(m)]==b and
           mm(mm(u,a,r,m,n),v,r,n,r)==eye(r))

def exact_rank(n,m,a):
    image={tuple(sum(a[i][j]*x[j]for j in range(n))%5 for i in range(m))
           for x in itertools.product(range(5),repeat=n)}
    q=len(image);r=0
    while q>1:assert q%5==0;q//=5;r+=1
    return r

def candidate(p):
    n,m,a,b=nf(p);meter=proposer.Meter(10**8)
    c=proposer.certificate(n,m,a,b,meter)
    return [app.SCHEMA,n,m,a,b,c],meter.spent

def check_preflight(p,calls,credit,out):
    n,m,a,b=nf(p);old=tariff(p);fee=norm_cost(p)+n*m
    if old==0 or calls==0:
        assert out['status']=='no_deployment_opportunity' and out['spent']==0;return
    if fee>credit:
        assert out['status']=='unfunded_preflight' and out['spent']==0;return
    assert out['status']=='preflight';lo=int(any(t for row in a for t in row))
    base=min(old,dense(n,m));floor=min(base,dense(n,m),factor_cost(n,m,lo))
    cold=norm_cost(p)+reuse_cost(n,m,lo)+emission(n,m,lo)
    warm=norm_cost(p)+reuse_cost(n,m,lo)
    assert out['normal']==dict(input_dim=n,output_dim=m,matrix=a,offset=b)
    assert out['minimum_width_floor']==lo and out['menu_cost_floor']==floor
    assert out['prospective_savings_ceiling']==calls*(base-floor)
    assert out['search_may_pay']==(cold<calls*(base-floor))
    assert out['cache_may_pay']==(warm<calls*(base-floor))
    assert out['spent']==fee and out['spent']+out['remaining']==credit
    assert nf(out['selected'])==nf(p)

def check_reuse(p,rec,calls,paid,credit,inputs,out):
    n,m,a,b=nf(p);r=rec[5][0];required=paid+norm_cost(p)+reuse_cost(n,m,r)
    if required>credit:
        assert out['status']=='unfunded_cache_validation' and not out['certificate_executed']
        assert out['spent']==paid;return 0
    ok=valid(rec) and a==rec[3]
    assert out['spent']==required and out['remaining']+required==credit
    assert out['certificate_executed']
    if not ok:
        assert out['status']=='rejected_cache_certificate';return 0
    assert out['status']=='certified_reuse'
    best=min(tariff(p),dense(n,m),factor_cost(n,m,r))
    assert out['per_call_selected']==best and tariff(out['selected'])==best
    assert nf(out['selected'])==nf(p)
    assert out['rank']==r
    if n<=3:assert r==exact_rank(n,m,a)
    expected=[run(p,x)for x in inputs]
    assert out['outputs']==expected
    assert [run(out['selected'],x)for x in inputs]==expected
    assert out['net_gain']==calls*tariff(p)-(required+calls*best)
    return len(inputs)

def differential():
    RD.mkdir(parents=True,exist_ok=True)
    requests=[];expect=[];seed=20260913;rng=random.Random(seed)
    for z,entries in enumerate(itertools.product(range(5),repeat=4)):
        a=[list(entries[:2]),list(entries[2:])];b=[z%5,(z//5)%5]
        orig=['map',2,2,a,b];rec,_=candidate(orig)
        # Half of the saved certificates have a nonzero first affine offset.
        if z%2:
            r,d,da,cm,cb,u,v=rec[5];da=[(i+1)%5 for i in range(r)]
            cb=[(b[i]-sum(cm[i][j]*da[j]for j in range(r)))%5 for i in range(2)]
            rec[5]=[r,d,da,cm,cb,u,v]
        p=['map',2,2,a,[(b[0]+1)%5,(b[1]+2)%5]]
        ins=[list(x)for x in itertools.product(range(5),repeat=2)]
        req=['affine-reuse-f5-v1',p,rec,20,7,100000,ins]
        requests.append(req);expect.append(('reuse',(p,rec,20,7,100000,ins)))
        calls=z%21;credit=100000 if z%11 else 1
        requests.append(['affine-preflight-f5-v1',p,calls,credit]);expect.append(('pre',(p,calls,credit)))
        if z%25==0:
            bad=copy.deepcopy(rec);bad[4][0]=(bad[4][0]+1)%5
            requests.append(['affine-reuse-f5-v1',p,bad,20,7,100000,[]])
            expect.append(('reuse',(p,bad,20,7,100000,[])))
    # All dimensions including zero; modest bounded rank families and general random rows.
    for n in range(5):
      for m in range(5):
        a=[[rng.randrange(5)for _ in range(n)]for _ in range(m)]
        b=[rng.randrange(5)for _ in range(m)];orig=['map',n,m,a,b];rec,_=candidate(orig)
        p=['seq',['id',n],['map',n,m,a,[(x+3)%5 for x in b]]]
        ins=[[rng.randrange(5)for _ in range(n)]for _ in range(12)]
        for credit in [0,1,100000]:
          requests.append(['affine-reuse-f5-v1',p,rec,17,0,credit,ins])
          expect.append(('reuse',(p,rec,17,0,credit,ins)))
    # Changed semantic keys, descriptor/shape failures, and exact zero-cost incumbent.
    eye2=['map',2,2,eye(2),[0,0]];rec,_=candidate(eye2)
    for p in [['id',2],['sum',['map',2,2,eye(2),[0,0]],['map',2,2,[[0,0],[0,0]],[3,4]]]]:
        requests.append(['affine-reuse-f5-v1',p,rec,100,0,100000,[[0,0],[1,2]]])
        expect.append(('reuse',(p,rec,100,0,100000,[[0,0],[1,2]])))
    wrong=['map',2,2,[[2,0],[0,1]],[0,0]]
    requests.append(['affine-reuse-f5-v1',wrong,rec,100,0,100000,[]]);expect.append(('reuse',(wrong,rec,100,0,100000,[])))
    malformed=[]
    q=['affine-reuse-f5-v1',eye2,rec,10,0,100000,[]]
    for mode in range(8):
        z=copy.deepcopy(q)
        if mode==0:z[0]='wrong-tag'
        elif mode==1:z[2][0]='wrong-field'
        elif mode==2:z[2][1]=3
        elif mode==3:z[2][3][0][0]=5
        elif mode==4:z[2][5][0]=9
        elif mode==5:z[2][5][2]=[]
        elif mode==6:z[3]=-1
        else:z[2].append('untrusted-approval')
        malformed.append(z)
    requests+=malformed;expect+=[('error',())for _ in malformed]
    (RD/'requests.json').write_bytes(app.canonical(requests))
    replies=[];logs=[];vector_count=0
    for start in range(0,len(requests),120):
        got=app.invoke(requests[start:start+120],timeout=90,records=logs,batch=True)
        for out,(typ,args)in zip(got,expect[start:start+120]):
            if typ=='reuse':vector_count+=check_reuse(*args,out)
            elif typ=='pre':check_preflight(*args,out)
            else:assert out['status']=='error'
        replies+=got
    (RD/'responses.json').write_bytes(app.canonical(replies))
    summary={'passed':True,'seed':seed,'requests':len(requests),'exhaustive_2x2_linear_maps':625,
      'reuse_requests':sum(k=='reuse'for k,_ in expect),'preflight_requests':sum(k=='pre'for k,_ in expect),
      'malformed_requests':len(malformed),'individual_vector_comparisons':vector_count,'invocations':logs}
    (RD/'differential_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='invocations'}))


def live(group='basic'):
    RD.mkdir(parents=True,exist_ok=True);records=[]
    cfg={'program':['map',4,4,[[1]*4 for _ in range(4)],[1,2,3,4]],
         'calls':1000,'credit':100000,'inputs':[[0,0,0,0],[1,2,3,4]]}
    def no_generation(phase,*_):
        if phase=='before_generate':raise AssertionError('unexpected factor generation')
    def case(name,fn):
        t=time.monotonic();value=fn();records.append({'name':name,'passed':True,'seconds':round(time.monotonic()-t,4),'result':value})
        print('PASS',name,flush=True);return value
    with tempfile.TemporaryDirectory(prefix='avoc_affine_store_tests_') as td:
        base=Path(td);store=base/'bank'
        # A fresh checked fixture in each bounded group. No old run is resumed.
        cold=app.run(copy.deepcopy(cfg),store)
        assert cold['route']=='cold_generation_and_validation' and cold['spent']==240
        leaf=Path(cold['saved_certificate']);before=leaf.read_bytes()
        if group=='basic':
            records.append({'name':'cold_publish','passed':True,'result':cold})
            warm=case('fresh_revalidated_warm',lambda:app.run(copy.deepcopy(cfg),store,hook=no_generation))
            assert warm['cache_hit'] and not warm['generator_executed'] and warm['spent']==149 and leaf.read_bytes()==before
            changed=copy.deepcopy(cfg);changed['program'][4]=[4,3,2,1]
            shifted=case('new_offset_same_certificate',lambda:app.run(changed,store,hook=no_generation))
            assert shifted['outputs'][0]==[4,3,2,1] and leaf.read_bytes()==before
            syntax=copy.deepcopy(changed);syntax['program']=['seq',['id',4],syntax['program']]
            got=case('different_program_same_linear_key',lambda:app.run(syntax,store,hook=no_generation));assert got['cache_hit']
            low=copy.deepcopy(cfg);low['calls']=1
            out=case('cold_preflight_skips_generator',lambda:app.run(low,base/'not_created',hook=no_generation))
            assert out['status']=='skip_search_bound' and not(base/'not_created').exists()
            out=case('warm_preflight_skips_revalidation',lambda:app.run(low,store,hook=no_generation))
            assert out['status']=='skip_cache_bound' and len(out['invocations'])==1
            (RD/'demo_cold.json').write_text(json.dumps(cold,indent=2)+'\n')
            (RD/'demo_warm.json').write_text(json.dumps(warm,indent=2)+'\n')
            (RD/'demo_shifted.json').write_text(json.dumps(shifted,indent=2)+'\n')
        elif group=='economics':
            ten=copy.deepcopy(cfg);ten['calls']=10
            cold10=case('ten_calls_cold_denied',lambda:app.run(ten,base/'ten_absent',hook=no_generation));assert cold10['status']=='skip_search_bound'
            warm10=case('ten_calls_warm_pays',lambda:app.run(ten,store,hook=no_generation));assert warm10['net_gain']==1
            eleven=copy.deepcopy(cfg);eleven['calls']=11
            ex=case('optimistic_pass_can_lose',lambda:app.run(eleven,base/'eleven'));assert ex['net_gain']==-75
            ident=copy.deepcopy(cfg);ident['program']=['id',4];ident['inputs']=[]
            out=case('identity_no_search_no_validation',lambda:app.run(ident,store,hook=no_generation));assert out['spent']==0
            poor=copy.deepcopy(cfg);poor['credit']=1
            out=case('unfunded_preflight',lambda:app.run(poor,base/'poor',hook=no_generation));assert out['status']=='unfunded_preflight'
            limited=copy.deepcopy(cfg);limited['credit']=175
            out=case('metered_generation_exhaustion',lambda:app.run(limited,base/'limited'));assert out['spent']<=175
            (RD/'demo_warm_ten_calls.json').write_text(json.dumps(warm10,indent=2)+'\n')
            (RD/'demo_optimistic_loss.json').write_text(json.dumps(ex,indent=2)+'\n')
        elif group=='integrity':
            data=app.decode(before.decode());bad=copy.deepcopy(data);bad['record'][4][0]=2
            leaf.write_bytes(app.canonical(bad))
            out=case('tampered_offset_rechecked',lambda:app.run(copy.deepcopy(cfg),store));assert out['status']=='rejected_cache_certificate'
            leaf.write_bytes(before)
            bad=copy.deepcopy(data);bad['record'][3][0][0]=2;leaf.write_bytes(app.canonical(bad))
            try:app.run(copy.deepcopy(cfg),store)
            except ValueError:records.append({'name':'changed_linear_key_rejected','passed':True})
            else:raise AssertionError('bad linear key admitted')
            leaf.write_bytes(before)
            bad=copy.deepcopy(data);bad['checker_fingerprint']='0'*64;leaf.write_bytes(app.canonical(bad))
            try:app.run(copy.deepcopy(cfg),store)
            except ValueError:records.append({'name':'changed_checker_descriptor_rejected','passed':True})
            else:raise AssertionError('bad descriptor admitted')
            leaf.write_bytes(before)
            target=base/'target';target.write_bytes(before);leaf.unlink();leaf.symlink_to(target)
            try:app.run(copy.deepcopy(cfg),store)
            except ValueError:records.append({'name':'certificate_symlink_rejected','passed':True})
            else:raise AssertionError('symlink accepted')
            leaf.unlink();leaf.write_bytes(before)
            def interrupt(phase,*_):
                if phase=='before_certificate_publication':raise RuntimeError('controlled publication interruption')
            try:app.run(copy.deepcopy(cfg),base/'interrupted',hook=interrupt)
            except RuntimeError:records.append({'name':'publication_interruption_no_certificate','passed':True})
            else:raise AssertionError('hook failed')
            assert not list((base/'interrupted').glob('[0-9a-f]'*64+'.json'))
            assert leaf.read_bytes()==before
        else:raise ValueError(group)
    summary={'passed':True,'group':group,'cases':len(records),'records':records,
      'interruption_kind':'controlled Python exception, not SIGKILL/power loss',
      'trust_boundary':'protected single-writer store and tested Python/IO projection; actual Lean checker executed'}
    (RD/('live_'+group+'.json')).write_text(json.dumps(summary,indent=2)+'\n');print('LIVE',group,len(records),'PASS')

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['differential','live']);p.add_argument('--group',choices=['basic','economics','integrity'],default='basic');args=p.parse_args()
    pins={str(x.relative_to(ROOT)):app.sha(x) for x in [Path(__file__),ROOT/'tools/affine_cache.py',ROOT/'tools/factor_affine.py']}
    t=time.monotonic()
    if args.mode=='live':live(args.group)
    else:differential()
    assert all(app.sha(ROOT/n)==v for n,v in pins.items())
    (RD/(args.mode+('_'+args.group if args.mode=='live' else '')+'_provenance.json')).write_text(json.dumps({'source_pins':pins,'unchanged':True,
      'seconds':round(time.monotonic()-t,6),'mode':args.mode,'python':sys.version},indent=2)+'\n')
if __name__=='__main__':main()
