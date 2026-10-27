#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,random,subprocess,tempfile,time
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SEED=20260915
rng=random.Random(SEED)


def F(x):
    if isinstance(x,str): return Fraction(x)
    if type(x) is int: return Fraction(x)
    if isinstance(x,list) and len(x)==2: return Fraction(x[0],x[1])
    raise TypeError(x)

def wire(q:Fraction): return [q.numerator,q.denominator]

def runtime():
    kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
    lean=kit/'toolchain/bin/lean';build=ROOT/'.lake/build/lib/lean'
    paths=[build]+[p/'.lake/build/lib/lean' for p in (kit/'workspace/.lake/packages').iterdir() if p.is_dir()]
    env=os.environ.copy();env['LEAN_PATH']=':'.join(map(str,paths));env['PATH']=str(lean.parent)+':'+env.get('PATH','')
    return lean,env

def batch(reqs):
    lean,env=runtime();payload=(json.dumps(reqs,separators=(',',':'))+'\n').encode()
    with tempfile.TemporaryDirectory(prefix='staged_affine_test_') as td:
        p=Path(td)/'req.json';p.write_bytes(payload);t=time.monotonic()
        cp=subprocess.run([str(lean),'-j1','--run',str(ROOT/'tools/StagedAffineMain.lean'),'--batch',str(p)],
                          cwd=ROOT,env=env,text=True,capture_output=True,timeout=120)
    if cp.returncode: raise RuntimeError(cp.stderr+cp.stdout)
    outs=[json.loads(x) for x in cp.stdout.splitlines() if x.strip()]
    if len(outs)!=len(reqs): raise AssertionError((len(outs),len(reqs)))
    return outs,time.monotonic()-t,hashlib.sha256(payload).hexdigest(),hashlib.sha256(cp.stdout.encode()).hexdigest()

@dataclass(frozen=True)
class S:
    warm:str='untried';cold:str='untried';budget:int=0;spent:int=0;done:bool=False

def solve(req):
    calls=req[4];wp=F(req[6]);cp=F(req[7]);budget=req[8];horizon=req[9];history=req[10]
    # fixed proof-derived summaries for this test fixture
    wf,cf=133,196;gross=Fraction(15000)
    def actions(s):
        if s.done:return ['stop']
        xs=['stop']
        if s.warm=='untried' and wf<=s.budget:xs.append('inspect_warm')
        if s.cold=='untried' and cf<=s.budget:xs.append('generate_cold')
        if s.warm=='ready':xs.append('deploy_warm')
        if s.cold=='ready':xs.append('deploy_cold')
        return xs
    def prob(s,a,o):
        if a=='inspect_warm':return wp if o else 1-wp
        if a=='generate_cold':return cp if o else 1-cp
        return Fraction(0 if o else 1)
    def step(s,a,o):
        if a in ('stop','deploy_warm','deploy_cold'):return S(s.warm,s.cold,s.budget,s.spent,True)
        if a=='inspect_warm':return S('ready' if o else 'failed',s.cold,s.budget-wf,s.spent+wf,False)
        if a=='generate_cold':return S(s.warm,'ready' if o else 'failed',s.budget-cf,s.spent+cf,False)
        raise ValueError(a)
    def reward(s,a):
        return {'stop':Fraction(),'inspect_warm':-Fraction(wf),'generate_cold':-Fraction(cf),
                'deploy_warm':gross,'deploy_cold':gross}[a]
    s=S(budget=budget)
    for a,o in history:
        if a not in actions(s) or prob(s,a,bool(o))<=0: raise ValueError('invalid history')
        s=step(s,a,bool(o))
    @lru_cache(None)
    def V(h,s):
        if h==0:return Fraction(),None
        best=None
        for a in actions(s):
            v=reward(s,a)+sum(prob(s,a,o)*V(h-1,step(s,a,o))[0] for o in (False,True))
            if best is None or v>best[0]:best=(v,a)
        return best
    return s,V(horizon,s)

def main():
    base=json.load(open(ROOT/'examples/staged_affine/certain.json'))
    valid=[]
    # Fixed headline examples.
    for name in ['certain','risky_warm','one_step','after_warm_success','insufficient_budget','warm_failure']:
        valid.append(json.load(open(ROOT/f'examples/staged_affine/{name}.json')))
    probs=[Fraction(0),Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)]
    budgets=[0,100,132,133,150,195,196,250,400]
    for _ in range(90):
        q=list(base);q[6]=wire(rng.choice(probs));q[7]=wire(rng.choice(probs));q[8]=rng.choice(budgets);q[9]=rng.randrange(0,5);q[10]=[]
        valid.append(q)
    invalid=[]
    def bad(i,v):q=json.loads(json.dumps(base));q[i]=v;return q
    invalid += [bad(6,[-1,1]),bad(7,[2,1]),bad(6,[1,0]),bad(0,'wrong-tag'),bad(9,99),bad(8,100000001)]
    q=json.loads(json.dumps(base));q[10]=[['inspect_warm',False]];q[6]=[1,1];invalid.append(q)
    q=json.loads(json.dumps(base));q[3][0]=9;invalid.append(q)
    outs,sec,rh,oh=batch(valid+invalid)
    choices={};
    for req,out in zip(valid,outs[:len(valid)]):
        assert out['status']=='optimal_staged_affine_policy',out
        s,(v,a)=solve(req);a=a or 'stop'
        got=out['choice']['kind'];assert got==a,(got,a,req)
        assert F(out['expected_net_value'])==v,(out['expected_net_value'],v)
        st=out['state'];assert (st['warm_status'],st['cold_status'],st['budget'],st['spent'],st['done'])==(s.warm,s.cold,s.budget,s.spent,s.done)
        assert st['budget']+st['spent']==st['total']==req[8]
        assert out['warm']['setup']==133 and out['cold']['setup']==196
        assert F(out['warm']['gross_saving'])==15000 and F(out['cold']['gross_saving'])==15000
        choices[got]=choices.get(got,0)+1
    for out in outs[len(valid):]:assert out['status']=='error',out
    headline={}
    for name in ['certain','risky_warm','one_step','after_warm_success','insufficient_budget','warm_failure']:
        req=json.load(open(ROOT/f'examples/staged_affine/{name}.json'));s,(v,a)=solve(req);headline[name]={'choice':a or 'stop','value':str(v),'state':s.__dict__}
    summary={'status':'pass','seed':SEED,'valid_cases':len(valid),'invalid_cases':len(invalid),'choices':choices,
             'headline':headline,'seconds':round(sec,6),'request_sha256':rh,'stdout_sha256':oh}
    out=ROOT/'results/v0.35.0/staged_affine';out.mkdir(parents=True,exist_ok=True)
    (out/'regression.json').write_text(json.dumps(summary,indent=2,default=str)+'\n')
    print(json.dumps(summary,indent=2,default=str))
if __name__=='__main__':main()
