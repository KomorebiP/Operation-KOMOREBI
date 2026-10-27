#!/usr/bin/env python3
"""Broader search: outgoing degree <=1, arbitrary incoming degree.

Unlike atomic chains/loops, these models may be singular off the torus.
A Fano weight test alone is not a certificate of a geometric transfer.
"""
import itertools,json,math,time
from fractions import Fraction as F
from pathlib import Path
from carrier_search import weights,weighted_model,fracstr

def run(m,a):
    start=time.time(); candidates=[]; best=None; compatible=0; evaluated=0
    allgraphs=list(itertools.product(*[(-1,)+tuple(j for j in range(6) if j!=i) for i in range(6)]))
    units=[t for t in range(1,m) if math.gcd(t,m)==1]
    for t in units:
        c=tuple(t*x%m for x in a)
        for nxt in allgraphs:
            incoming=[0]*6
            for i,j in enumerate(nxt):
                if j!=-1:incoming[j]+=c[i]
            ns=[]
            for i,ci in enumerate(c):
                g=math.gcd(ci,m);rhs=-incoming[i]
                if rhs%g:break
                period=m//g
                ni=((rhs//g)*pow(ci//g,-1,period))%period
                if ni<2:ni+=((2-ni+period-1)//period)*period
                ns.append(ni)
            if len(ns)!=6:continue
            compatible+=1
            upper=sum((F(1,ni) for ni in ns),F(0))
            if best and upper<=best[0] and upper<=1:continue
            ws=weights(tuple(ns),nxt);s=sum(ws,F(0));evaluated+=1
            e={'unit':t,'character':c,'next':nxt,'exponents':ns,
               'rational_weights':[fracstr(w) for w in ws],'weight_sum':fracstr(s),
               'model':weighted_model(ws),
               'residue_numerator_exponents':[(ns[i]*c[i]+incoming[i])//m-1 for i in range(6)]}
            if best is None or s>best[0]:best=(s,e)
            if s>1:candidates.append(e)
    candidates.sort(key=lambda e:(e['model']['degree'],e['model']['weights'],e['next']))
    result={'modulus':m,'input_character':a,'graphs':len(allgraphs),
            'graph_conjugate_pairs':len(allgraphs)*len(units),'compatible_pairs':compatible,
            'weight_systems_evaluated':evaluated,'max':best[1],
            'fano_candidates':candidates,'candidate_count':len(candidates),
            'well_formed_fano_count':sum(e['model']['ambient_well_formed'] and e['model']['hypersurface_well_formed_test'] for e in candidates),
            'runtime_seconds':time.time()-start,
            'status':'candidate weights only; singular compactification transfer unverified'}
    return result

if __name__=='__main__':
    result=run(70,(1,20,24,42,61,62))
    Path(__file__).with_name('branched70.json').write_text(json.dumps(result,indent=2)+'\n')
    summary={k:v for k,v in result.items() if k!='fano_candidates'}
    summary['first_candidates']=result['fano_candidates'][:5]
    print(json.dumps(summary,indent=2))
