#!/usr/bin/env python3
"""Evaluate a SUPPLIED affine target; this does not produce the arithmetic target.
Field entries use code a+7*b for a+b*w, w^2=5. Matrix entries are in F7.
Example: python -B evaluate_target.py --input target.json --output result.json
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASIS='a+7*b for a+b*w; w^2=5'

def require(ok:bool,message:str):
    if not ok:raise ValueError(message)

def apply(M,x):
    return [sum(a*(v%7) for a,v in zip(row,x))%7+7*(sum(a*(v//7) for a,v in zip(row,x))%7) for row in M]

def add(x,y):return [(a%7+b%7)%7+7*((a//7+b//7)%7) for a,b in zip(x,y)]

def solve(M,y):
    # Augment two rational-coordinate targets; all arithmetic is F7.
    rows=[list(row)+[v%7,v//7] for row,v in zip(M,y)]
    cols=len(M[0]);piv=[]
    for c in range(cols):
        i=len(piv);j=next((j for j in range(i,len(rows)) if rows[j][c]%7),None)
        if j is None:continue
        rows[i],rows[j]=rows[j],rows[i];s=pow(rows[i][c],-1,7);rows[i]=[v*s%7 for v in rows[i]]
        for j in range(len(rows)):
            if j!=i:
                s=rows[j][c];rows[j]=[(v-s*w)%7 for v,w in zip(rows[j],rows[i])]
        piv.append(c)
    if any(not any(row[:cols]) and any(row[cols:]) for row in rows):return None
    out=[0]*cols
    for i,c in enumerate(piv):out[c]=rows[i][cols]+7*rows[i][cols+1]
    require(apply(M,out)==y,'linear-solver reconstruction failed')
    return out

def evaluate(inp,cert):
    require(isinstance(inp,dict),'target object required')
    require(inp.get('kind') in ('synthetic','supplied'),'kind must be synthetic or supplied')
    require(isinstance(inp.get('provenance'),str) and inp['provenance'].strip(),'nonempty target provenance required')
    require(inp.get('basis')==BASIS,'unknown coefficient encoding')
    label=inp.get('pattern');require(label in cert['patterns'],'unknown pattern')
    y=inp.get('target');require(isinstance(y,list) and len(y)==15 and all(type(v)is int and 0<=v<49 for v in y),'15 encoded field entries required')
    p=cert['patterns'][label];A=p['global_to_constraint_matrix'];N=p['dual_obstruction_basis'];o=apply(N,y);x=solve(A,y)
    require((x is not None)==(not any(o)),'dual and direct solver disagree')
    return {'pattern':label,'kind':inp['kind'],'provenance':inp['provenance'],'basis':BASIS,
      'linear_target_in_image':x is not None,'obstruction_coordinates':o,
      'particular_character_correction':x,'homogeneous_kernel_basis':p['kernel_basis'],
      'arithmetic_target_authenticated':False,'actual_pattern_eliminated':False,
      'warning':'Only the supplied linear target was evaluated. Its origin from one global primitive and actual local data is not certified here.'}

def self_test(cert):
    tests=0;invariance=0;rejections=0;examples={}
    for label,p in cert['patterns'].items():
        A=p['global_to_constraint_matrix'];N=p['dual_obstruction_basis']
        base={'kind':'synthetic','provenance':'Block80 basis/self-test, not arithmetic','basis':BASIS,'pattern':label}
        for j in range(10):
            for scalar in (1,7):
                z=[0]*10;z[j]=scalar;y=apply(A,z);r=evaluate({**base,'target':y},cert)
                require(r['linear_target_in_image'],'synthetic image rejected');tests+=1
        bad=p['synthetic_nonimage_target'];r=evaluate({**base,'target':bad},cert)
        require(not r['linear_target_in_image'],'synthetic nonimage accepted');tests+=1
        for j in range(10):
            z=[0]*10;z[j]=1
            require(apply(N,add(bad,apply(A,z)))==apply(N,bad),'origin independence failed');invariance+=1
        examples[label]={'input':{**base,'target':bad},'output':r}
        for broken in ({**base,'target':[0]*14},{**base,'target':[0]*14+[49]},
                       {**base,'target':[0]*15,'provenance':''},{**base,'target':[0]*15,'basis':'unknown'}):
            try:evaluate(broken,cert)
            except ValueError:rejections+=1
            else:raise ValueError('invalid target accepted')
    # Fixed-local primitive p=lam*chi^-1*alpha: exhaustive prime-field identity.
    fixed=0
    for x,y in itertools.product(range(1,7),repeat=2):
        ix=pow(x,-1,7);iy=pow(y,-1,7)
        for a,b,lam in itertools.product(range(7),repeat=3):
            ag_h=(a+x*b)%7;beta_h=(iy-1)*lam%7
            pg=lam*ix*a%7;ph=lam*iy*b%7;pgh=lam*ix*iy*ag_h%7
            require((pg+ph-pgh+a*ix*beta_h)%7==0,'fixed primitive differential failed')
            require(((x-1)*pg+a*(ix-1)*lam)%7==0,'fixed local trace failed');fixed+=1
    return {'status':'PASS_FINITE_EVALUATOR_CHECKS','basis_image_and_nonimage_checks':tests,
        'affine_origin_invariance_checks':invariance,'malformed_targets_rejected':rejections,
        'fixed_local_primitive_prime_field_cases':fixed,'examples':examples,
        'actual_arithmetic_target_evaluated':False,'no_pattern_elimination':True}

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--input',type=Path);a.add_argument('--output',type=Path);a.add_argument('--self-test',action='store_true');ns=a.parse_args()
    cert=json.loads((ROOT/'work80/verification/primary80.json').read_text())
    try:
        if ns.self_test:
            out=self_test(cert);dest=ns.output or ROOT/'work80/verification/target_evaluator80.json'
        else:
            require(ns.input is not None and ns.output is not None,'--input and --output are required')
            out=evaluate(json.loads(ns.input.read_text()),cert);dest=ns.output
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        print(out.get('status','TARGET_EVALUATED_CONDITIONALLY'))
    except (ValueError,TypeError,OSError,json.JSONDecodeError) as ex:
        a.exit(2,f'Invalid evaluation: {ex}\n')
if __name__=='__main__':main()
