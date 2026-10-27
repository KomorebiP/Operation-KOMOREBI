#!/usr/bin/env python3
"""Exact, staged Frobenius certificate at 197 and 491 (Python 3.10+, stdlib).

Every equation residue is filtered individually. Weighted isomorphism orbits
save counts, not equation checks. At split 491 a failed degree-one trace test
modulo 7 already excludes the residual target; only remaining orbits need N2.
No finite output alone certifies the inherited geometric hypotheses.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path

PRIMES=(197,491)

def need(x:bool,msg:str)->None:
    if not x:raise ValueError(msg)

def character(a:int,q:int)->int:
    r=pow(a%q,(q-1)//2,q)
    return -1 if r==q-1 else r

def v7(a:int)->int:
    need(a!=0,'Zero has no finite valuation in this interface')
    a=abs(a);v=0
    while a%7==0:a//=7;v+=1
    return v

def tables(q:int):
    d=next(d for d in range(2,q) if character(d,q)==-1)
    leg=[character(x,q) for x in range(q)]
    base=[(x,pow(x,3,q),pow(x,6,q)) for x in range(q)]
    # Powers in F_q[w]/(w^2-d); no floating point or probabilistic tests.
    rows=[]
    for x in range(q):
        for y in range(q):
            x2=(x*x+d*y*y)%q;y2=2*x*y%q
            a=(x2*x+d*y2*y)%q;b=(x2*y+y2*x)%q
            c=(a*a+d*b*b)%q;e=2*a*b%q
            rows.append((x,y,a,b,c,e))
    return d,leg,base,rows

def count1(A:int,B:int,q:int,tabs)->int:
    _,leg,base,_=tabs;a=12*A%q;b=10*B%q;c=5*B*B%q
    return q+2+sum(leg[(x6+b*x3+a*x+c)%q] for x,x3,x6 in base)

def count2(A:int,B:int,q:int,tabs)->int:
    d,leg,_,rows=tabs;a=12*A%q;b=10*B%q;c=5*B*B%q
    s=0
    for x,y,x3,y3,x6,y6 in rows:
        u=(x6+b*x3+a*x+c)%q;v=(y6+b*y3+a*y)%q
        s+=leg[(u*u-d*v*v)%q]
    return q*q+2+s

def polynomial(q:int,n1:int,n2:int)->list[int]:
    s1=q+1-n1;num=s1*s1-q*q-1+n2
    need(num%2==0,'Nonintegral second coefficient')
    return [q*q,-q*s1,num//2,-s1,1]

def twisted(q:int,p:list[int],nu:int,f:int)->list[int]:
    s1=-p[3];s2=p[2];Q=q**f
    if f==2:s1,s2=s1*s1-2*s2,s2*s2-2*q*s1*s1+2*q*q
    return [Q*Q,-nu*Q*s1,s2,-nu*s1,1]

def run(q:int)->dict:
    need(q in PRIMES,'This release certifies only the declared primes')
    need(all(q%d for d in range(2,math.isqrt(q)+1)),'Composite modulus')
    f=1 if q%5 in (1,4) else 2;Q=q**f
    nu=(1 if Q%5==1 else -1)*character(-3,q)**f
    tabs=tables(q)
    seventh={pow(c,7,q) for c in range(1,q)}
    smooth={(a,b) for a in range(q) for b in range(q) if (a**3+b**5)%q!=0}
    eligible={p for p in smooth if (p[0]**3+p[1]**5)%q in seventh}
    powers=[(pow(u,5,q),pow(u,3,q)) for u in range(1,q)]
    unseen=set(smooth);covered=set();wrong=set();rows=[];orbits=0;full=0
    target=[Q*Q,-2*Q*(Q+1),(Q+1)**2+2*Q,-2*(Q+1),1]
    while unseen:
        a,b=min(unseen)
        orbit={(a*u5%q,b*u3%q) for u5,u3 in powers}
        need(orbit<=unseen,'Weighted-orbit partition failure')
        unseen.difference_update(orbit);orbits+=1
        if (a**3+b**5)%q in seventh:wrong.update(orbit)
        pairs=sorted(orbit & eligible)
        if not pairs:continue
        need(not covered.intersection(pairs),'Repeated eligible pair');covered.update(pairs)
        n1=count1(a,b,q,tabs)
        stage_pass=(f==2 or (nu*(q+1-n1)-2*(Q+1))%7==0)
        row={'representative':[a,b],'orbit_size':len(orbit),'admissible_pairs':[list(p) for p in pairs],
             'N1':n1,'degree_one_trace_pass':stage_pass,'N2':None,'Pq_ascending':None,
             'twisted_polynomial':None,'matches':{'7':False,'49':False,'343':False}}
        if stage_pass:
            n2=count2(a,b,q,tabs);p=polynomial(q,n1,n2);pnu=twisted(q,p,nu,f);full+=1
            row.update(N2=n2,Pq_ascending=p,twisted_polynomial=pnu)
            row['matches']={str(mod):all((a-b)%mod==0 for a,b in zip(pnu,target)) for mod in (7,49,343)}
        rows.append(row)
    need(covered==eligible,'Incomplete memberwise equation coverage')
    counts={str(mod):{'orbits':sum(r['matches'][str(mod)] for r in rows),
                    'pairs':sum(len(r['admissible_pairs']) for r in rows if r['matches'][str(mod)])}
            for mod in (7,49,343)}
    # Check the known exploratory assertions only after completing the exact enumeration.
    expected={197:((30,840),(2,56),(0,0)),491:((7,490),(0,0),(0,0))}[q]
    need([(counts[str(m)]['orbits'],counts[str(m)]['pairs']) for m in (7,49,343)]==list(expected),'Unexpected finite conclusion')
    residual_trace=sorted({-r['Pq_ascending'][3] for r in rows if r['matches']['7']})
    valuations=Counter()
    for r in rows:
        if r['twisted_polynomial'] is not None:
            order=sum(r['twisted_polynomial']);need(order>0,'Nonpositive Jacobian order')
            valuations[v7(order)]+=len(r['admissible_pairs'])
    if q==197:
        need(all(r['N1']==q+1 for r in rows),'Unexpected inert rational trace')
        need({r['Pq_ascending'][2] for r in rows if r['matches']['49']}=={2,296},'Unexpected surviving 49 coefficients')
    if q==491:need(residual_trace==[-25,10,24],'Unexpected rational traces on residual locus')
    return {'q':q,'f':f,'Q':Q,'h':v7(Q-1),'nu':nu,'quadratic_nonresidue':tabs[0],
            'smooth_pairs':len(smooth),'admissible_pairs':len(eligible),'full_weighted_orbits':orbits,
            'degree_one_counts':len(rows),'degree_two_counts':full,'matches':counts,
            'rational_traces_on_residual_locus':residual_trace,'target_polynomial_ascending':target,
            'counted_order_valuation_histogram':dict(sorted(valuations.items())),
            'bad_reduction_control':{'A':q-1,'B':1,'seventh_sum':0,'excluded_from_good_locus':(q-1,1) not in eligible},
            'wrong_representative_filter':{'false_positive_pairs':len(wrong-eligible),'false_negative_pairs':len(eligible-wrong)},
            'rows':rows}

def main()->None:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    data={'schema':'beal.block56.frobenius.v1','status':'PASS_DECLARED_FINITE_ASSERTIONS',
          'arithmetic':'exact integer finite-field character sums',
          'method':'memberwise admissibility; weighted orbits; quadratic characters through norms; staged trace filtering',
          'nonclaims':['No Frey geometry verification','No global solution or universal prime-support bound'],
          'primes':[run(q) for q in PRIMES]}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':data['status'],'pairs':sum(x['admissible_pairs'] for x in data['primes']),
                      'N1_counts':sum(x['degree_one_counts'] for x in data['primes']),
                      'N2_counts':sum(x['degree_two_counts'] for x in data['primes'])}))
if __name__=='__main__':main()
