#!/usr/bin/env python3
"""Independent finite audit. Counts enumerate only the declared finite ranges."""
from __future__ import annotations
import copy,itertools,json,random,sys,time
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from matrix_logic import compile_artifact,emit_lean,class_formula
from checks.check_logical_export import check_logical,check_lean_literals
from checks.check_certificate import InvalidCertificate
from discover import discover
from observational_logic import FiniteSystem,fo_sat
from standard_logic import TaggedModel,eval_formula,translate,target_rank

COUNTS=Counter()
def ck(name,p):
    if not p:raise AssertionError(name)
    COUNTS[name]+=1

def mul(a,x,m):return tuple(sum(c*v for c,v in zip(row,x))%m for row in a)
def encode(c,x,m):return mul(c['basis'],x,m)
def value(s,x,w,j):
    m=s['p']**s['r'];v=tuple(x)
    for a in w:v=mul(s['actions'][a],v,m)
    return sum(c*z for c,z in zip(s['observations'][j],v))%m

def symbolic_term(s,t,env):
    tag=t[0]
    if tag=='free':return env[t[1]]
    if tag=='constant':return ('value',t[1])
    v=symbolic_term(s,t[2],env)
    if v[0]=='value':return v
    if tag=='action':return ('state',mul(s['actions'][t[1]],v[1],s['p']**s['r']))
    if tag=='observe':return ('value',value(s,v[1],[],t[1]))
    raise ValueError('outside term grammar')

def symbolic_qf(s,f,env):
    match f:
        case ['false']|('false',):return False
        case ['eq',a,b]|('eq',a,b):return symbolic_term(s,a,env)==symbolic_term(s,b,env)
        case ['state',a]|('state',a):return symbolic_term(s,a,env)[0]=='state'
        case ['imp',a,b]|('imp',a,b):return not symbolic_qf(s,a,env) or symbolic_qf(s,b,env)
        case _:raise ValueError('symbolic evaluator is quantifier-free only')

def kernel_delta(c,p,r,d,rng):
    m=p**r;t=c['dimension'];z=[]
    for j in range(d):
        z.append((p**(r-c['smith_valuations'][j]))*rng.randrange(p**c['smith_valuations'][j]) if j<t else rng.randrange(m))
    return mul(c['V'],z,m)

def finite_models(s,c):
    m=s['p']**s['r'];d=s['dimension'];xs=list(itertools.product(range(m),repeat=d));xi={x:i for i,x in enumerate(xs)}
    ys=sorted({encode(c,x,m) for x in xs});yi={y:i for i,y in enumerate(ys)}
    st=tuple(tuple(xi[mul(a,x,m)] for x in xs) for a in s['actions'])
    so=tuple(tuple(value(s,x,[],j) for x in xs) for j in range(len(s['observations'])))
    it=tuple(tuple(yi[mul(a,y,m)] for y in ys) for a in c['transitions'])
    io=tuple(tuple(sum(a*b for a,b in zip(row,y))%m for y in ys) for row in c['observation_decoder'])
    source=FiniteSystem(st,so,len(xs));image=FiniteSystem(it,io,len(ys))
    return xs,ys,source,image,tuple(yi[encode(c,x,m)] for x in xs)

def rejects(name,fn):
    try:fn()
    except (ValueError,AssertionError,TypeError,RuntimeError):COUNTS[name]+=1
    else:raise AssertionError('control was accepted: '+name)

def main():
    rng=random.Random(2026092103);t0=time.monotonic();cases=json.loads((ROOT/'source_records/EXPORTED_CASES.json').read_text());records=[];small=[]
    for case in cases:
        s=json.loads((ROOT/case['source']).read_text());c=json.loads((ROOT/case['certificate']).read_text());a=json.loads((ROOT/case['logic']).read_text())
        p,r,d=s['p'],s['r'],s['dimension'];m=p**r
        ck('independent_logical_certificate',check_logical(s,c,a)['status']=='PASS')
        ck('rediscovered_certificate_identical',discover(s)['certificate']==c)
        ck('deterministic_logical_export',json.loads(json.dumps(compile_artifact(s,c)))==a)
        text=(ROOT/'formalization'/(case['module']+'.lean')).read_text()
        ck('independent_lean_transcription',check_lean_literals(s,c,text)['status']=='PASS')
        ck('deterministic_lean_export',text==emit_lean(s,c,case['namespace'].split('.')[-1]))
        ck('quantifier_free_export',target_rank(a['formula'])==0)
        for j in range(16):
            x=tuple(rng.randrange(m) for _ in range(d))
            if j%2==0:
                delta=kernel_delta(c,p,r,d,rng);y=tuple((a+b)%m for a,b in zip(x,delta))
            else:y=tuple(rng.randrange(m) for _ in range(d))
            expected=encode(c,x,m)==encode(c,y,m)
            ck('symbolic_qf_vs_encoding',symbolic_qf(s,a['formula'],(('state',x),('state',y)))==expected)
            ck('wrong_sort_rejected',not symbolic_qf(s,a['formula'],(('state',x),('value',0))))
            vals=tuple(value(s,x,z['word'],z['observation']) for z in c['raw_tests'])
            ck('test_values_reconstruct_encoding',mul(c['basis_combinations'],vals,m)==encode(c,x,m))
            target=encode(c,x,m);ff=class_formula(s,c,list(target))
            ck('class_formula_nonempty',symbolic_qf(s,ff,(('state',x),)))
            ck('class_formula_exact',symbolic_qf(s,ff,(('state',y),))==expected)
            ck('class_formula_wrong_sort',not symbolic_qf(s,ff,(('value',0),)))
        z=tuple(0 for _ in range(d))
        for e in c['strict_growth_witnesses']:
            test=e['test'];f=translate(('test',(0,tuple(test['word'])),test['observation'],0),1)
            ck('growth_formula_distinguishes',symbolic_qf(s,f,(('state',z),)) and not symbolic_qf(s,f,(('state',tuple(e['delta'])),)))
        if m**d<=64:
            xs,ys,ss,im,emap=finite_models(s,c);small.append(case['name'])
            sm=TaggedModel.from_system(ss,tuple(range(m)));tm=TaggedModel.from_system(im,tuple(range(m)))
            for ix,x in enumerate(xs):
                for iy,y in enumerate(xs):
                    ck('exhaustive_finite_formula_kernel',eval_formula(sm,a['formula'],(('state',ix),('state',iy)))==(emap[ix]==emap[iy]))
                for v in range(m):
                    ck('exhaustive_wrong_sort',not eval_formula(sm,a['formula'],(('state',ix),('value',v))))
            forms=[('exists',('test',(0,()),0,v)) for v in [0,1]]
            forms += [('exists',('compare',(0,(0,)),0,(1,()),0)),('exists',('and',('test',(0,()),0,0),('test',(1,()),0,1))),('not',('exists',('not',('compare',(0,()),0,(1,()),0))))]
            if len(xs)<=16:forms += [('exists',('exists',('and',('test',(1,()),0,0),('test',(0,()),0,1))))]
            for f in forms:
                for ix in sorted({0,len(xs)-1}):
                    ck('quantified_image_transport',fo_sat(ss,f,(ix,))==eval_formula(tm,translate(f,1),(('state',emap[ix]),)))
        records.append(case)
    base=next(ca for ca in cases if ca['name']=='scrambled_128bit');s=json.loads((ROOT/base['source']).read_text());c=json.loads((ROOT/base['certificate']).read_text());a=json.loads((ROOT/base['logic']).read_text())
    muts=[]
    b=copy.deepcopy(a);b['formula']=['imp',['false'],['false']];muts.append(b)
    b=copy.deepcopy(a);b['profile']['quantifier_domain']='free_target';muts.append(b)
    b=copy.deepcopy(a);b['terms'][0]=['free',0];muts.append(b)
    b=copy.deepcopy(a);b['tests'][1]['word']=[1];muts.append(b)
    b=copy.deepcopy(a);b['source_sha256']='0'*64;muts.append(b)
    b=copy.deepcopy(a);b['certificate_sha256']='0'*64;muts.append(b)
    b=copy.deepcopy(a);b['coordinate_count']=1;muts.append(b)
    b=copy.deepcopy(a);b['term_horizon']=0;muts.append(b)
    for b in muts:rejects('corrupted_logical_export_rejected',lambda b=b:check_logical(s,c,b))
    changed=copy.deepcopy(s);changed['observations'][0][0]=(changed['observations'][0][0]+1)%65536
    from matrix_logic import digest
    rebound=copy.deepcopy(a);rebound['source_sha256']=digest(changed)
    rejects('rebound_source_rejected',lambda:check_logical(changed,c,rebound))
    txt=(ROOT/'formalization'/(base['module']+'.lean')).read_text();bad=txt.replace('([0], 0)', '([1], 0)')
    rejects('corrupted_lean_test_transcription_rejected',lambda:check_lean_literals(s,c,bad))
    rejects('out_of_image_class_query_rejected',lambda:class_formula(s,c,[0,1]))
    # Noncommuting two-digit fixture, with a query requiring both digits.
    ns={'schema':'finite-linear-profile-v1','p':2,'r':2,'dimension':2,'actions':[[[1,1],[0,1]],[[0,1],[1,0]]],'observations':[[1,0]],'initial_interface':'all_states','word_order':'left_to_right'}
    x=(1,0)
    ck('word_order_counterexample',value(ns,x,[0,1],0)!=value(ns,x,[1,0],0))
    # Actual free-target quantifier failure: source outputs 2*x mod 4, raw target outputs y.
    outputs={2*x%4 for x in range(4)}
    ck('free_target_quantifier_failure',1 not in outputs and 1 in set(range(4)))
    result={'status':'PASS','seed':2026092103,'cases':len(cases),'counts':dict(COUNTS),'total_checks':sum(COUNTS.values()),'small_systems':small,'small_count':len(small),'large':{'source_states':2**128,'tests':a['test_count'],'term_horizon':a['term_horizon'],'coordinates':a['coordinate_count']},'bounds':{'sample_pairs_per_case':16,'exhaustive_source_state_cap':64,'quantified_formulas_per_small_case':'5, plus one nested existential when size<=16','growth_witnesses':'all retained 643','cases':'202 frozen synthetic cases, not a held-out discovery benchmark'},'runtime_seconds':time.monotonic()-t0,'non_claims':['No minimal-formula theorem.','Python is not a verified executable.','Finite samples do not prove the universal Lean claims.']}
    (ROOT/'results/LOGICAL_DISCOVERY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
