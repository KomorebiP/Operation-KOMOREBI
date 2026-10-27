#!/usr/bin/env python3
"""Independent exact certificate (no imports from the primary implementation).

F_q[theta]/(theta^2+theta+1), square-root tables, B=1 normalization,
all equation pairs generated directly, polynomial gcds, Newton identities,
and twist symbols from the defining radicand. Python 3.10+, stdlib only.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path

def need(x,msg):
    if not x:raise ValueError(msg)

def trim(p):
    while len(p)>1 and p[-1]==0:p.pop()
    return p

def gcd_degree(p,r,q):
    p,r=trim(p[:]),trim(r[:])
    while r!=[0]:
        z=p[:];inv=pow(r[-1],-1,q)
        while len(z)>=len(r) and z!=[0]:
            shift=len(z)-len(r);c=z[-1]*inv%q
            for j,a in enumerate(r):z[j+shift]=(z[j+shift]-c*a)%q
            trim(z)
        p,r=r,z
    return len(p)-1

def tables(q):
    need(q%3==2,'theta^2+theta+1 must be irreducible')
    def mul(a,b,c,d):return ((a*c-b*d)%q,(a*d+b*c-b*d)%q)
    roots1=[0]*q
    for x in range(q):roots1[x*x%q]+=1
    roots2=[0]*(q*q);rows=[]
    for x in range(q):
        for y in range(q):
            a,b=mul(x,y,x,y);roots2[a*q+b]+=1
            c,d=mul(a,b,x,y);e,f=mul(c,d,c,d)
            rows.append((x,y,c,d,e,f))
    need(roots2[0]==1 and sum(roots2)==q*q,'Square table multiplicity')
    need(sum(x!=0 for x in roots2)==(q*q+1)//2,'Square table support')
    return roots1,roots2,rows

def counts(A,B,q,tabs,degree_two):
    roots1,roots2,rows=tabs
    n1=2+sum(roots1[(pow(x,6,q)+10*B*pow(x,3,q)+12*A*x+5*B*B)%q] for x in range(q))
    n2=None
    if degree_two:
        a=12*A%q;b=10*B%q;c=5*B*B%q
        n2=2+sum(roots2[((e+b*z+a*x+c)%q)*q+(f+b*w+a*y)%q] for x,y,z,w,e,f in rows)
    return n1,n2

def square_roots_polynomial(P):
    cs=list(reversed(P));sums=[4]
    for m in range(1,9):
        if m<=4:s=-sum(cs[j]*sums[m-j] for j in range(1,m))-m*cs[m]
        else:s=-sum(cs[j]*sums[m-j] for j in range(1,5))
        sums.append(s)
    out=[1]
    for m in range(1,5):
        num=-sum(out[m-i]*sums[2*i] for i in range(1,m+1))
        need(num%m==0,'Nonintegral Newton coefficient');out.append(num//m)
    return list(reversed(out))

def twist_data(q):
    sq={z*z%q for z in range(q)}
    roots=[z for z in range(q) if z*z%q==5]
    if roots:
        signs={1 if 3*(5-z)*pow(2,-1,q)%q in sq else -1 for z in roots}
        need(len(signs)==1 and len(roots)==2,'Split radicand signs')
        return 1,signs.pop()
    # Norm_{Fq2/Fq}(3(5-sqrt5)/2)=45, giving the quadratic symbol.
    return 2,1 if 45%q in sq else -1

def canonical_maps(q):
    # Cubing is bijective for q=197,491. Normalize B to 1, not A to a
    # fifth-power representative as in the primary orbit traversal.
    need(math.gcd(3,q-1)==1,'Nonbijective cube map')
    inv3=pow(3,-1,q-1)
    bs={b:pow(pow(b,-inv3,q),5,q) for b in range(1,q)}
    fifth={pow(x,5,q) for x in range(1,q)}
    a0={a:min(a*c%q for c in fifth) for a in range(1,q)}
    return bs,a0

def run(ref):
    q=ref['q'];need(q in (197,491),'Undeclared prime')
    f,nu=twist_data(q);Q=q**f
    need((f,nu)==(ref['f'],ref['nu']),'Independent restriction/twist mismatch')
    tabs=tables(q);bm,am=canonical_maps(q)
    seventh={pow(z,7,q) for z in range(1,q)}
    groups=defaultdict(list);expected={}
    for row in ref['rows']:
        for pair in row['admissible_pairs']:
            pair=tuple(pair);need(pair not in expected,'Duplicate primary pair');expected[pair]=row
    direct=[];gcds=0
    for a in range(q):
        for b in range(q):
            if (pow(a,3,q)+pow(b,5,q))%q not in seventh:continue
            poly=[5*b*b%q,12*a%q,0,10*b%q,0,0,1]
            der=[i*poly[i]%q for i in range(1,7)]
            need(gcd_degree(poly,der,q)==0,'Singular good equation residue');gcds+=1
            key=(a*bm[b]%q,1) if b else (am[a],0)
            direct.append((a,b));groups[key].append((a,b))
    need(set(direct)==set(expected),'Independent direct equation coverage')
    rows=[];matches={str(m):{'orbits':0,'pairs':0} for m in (7,49,343)};full=0
    residual_traces=set();digest=hashlib.sha256()
    target=[Q*Q,-2*Q*(Q+1),(Q+1)**2+2*Q,-2*(Q+1),1]
    for (a,b),pairs in sorted(groups.items()):
        n1,_=counts(a,b,q,tabs,False)
        test=f==2 or (nu*(q+1-n1)-2*(Q+1))%7==0
        n2=None;P=None;tw=None;ok={str(m):False for m in (7,49,343)}
        if test:
            _,n2=counts(a,b,q,tabs,True);full+=1
            s=q+1-n1;num=s*s-(q*q+1-n2);need(num%2==0,'Second coefficient integrality')
            P=[q*q,-q*s,num//2,-s,1]
            base=square_roots_polynomial(P) if f==2 else P
            tw=[c*(nu if i%2 else 1) for i,c in enumerate(base)]
            ok={str(m):all((c-d)%m==0 for c,d in zip(tw,target)) for m in (7,49,343)}
            need(sum(tw)>0,'Nonpositive Jacobian order')
        for pair in pairs:
            r=expected[pair]
            need(n1==r['N1'] and test==r['degree_one_trace_pass'],'Independent degree-one mismatch')
            need((n2,P,tw,ok)==(r['N2'],r['Pq_ascending'],r['twisted_polynomial'],r['matches']),f'Independent full mismatch {q,pair}')
            digest.update((json.dumps([pair,n1,n2,P,tw,ok],sort_keys=True)+'\n').encode())
        for m in (7,49,343):
            if ok[str(m)]:matches[str(m)]['orbits']+=1;matches[str(m)]['pairs']+=len(pairs)
        if ok['7']:residual_traces.add(-P[3])
        rows.append({'canonical_representative':[a,b],'admissible_pairs':len(pairs),'N1':n1,'N2':n2,
                     'Pq_ascending':P,'twisted_polynomial':tw,'matches':ok})
    need(matches==ref['matches'],'Independent complete modulus-locus mismatch')
    need(len(groups)==ref['degree_one_counts'] and full==ref['degree_two_counts'],'Orbit/count-coverage mismatch')
    return {'q':q,'field':'theta^2+theta+1','f':f,'nu_from_radicand':nu,
            'direct_pairs':len(direct),'smoothness_gcd_checks':gcds,'canonical_orbits':len(groups),
            'degree_two_counts':full,'matches':matches,'all_pair_comparison_sha256':digest.hexdigest(),
            'rational_traces_on_residual_locus':sorted(residual_traces),'rows':rows}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--primary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    ref=json.loads(a.primary.read_text());need([x['q'] for x in ref['primes']]==[197,491],'Primary prime scope')
    data={'schema':'beal.block56.independent.v1','status':'PASS_INDEPENDENT_FINITE_IMPLEMENTATION',
          'method':'different field basis; explicit square roots; B normalization; full direct pair set; Newton and radicand',
          'primary_sha256':hashlib.sha256(a.primary.read_bytes()).hexdigest(),'primes':[run(r) for r in ref['primes']],
          'nonclaims':['Not an independent mathematical reviewer','Does not verify inherited geometry']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':data['status'],'direct_pairs_compared':sum(x['direct_pairs'] for x in data['primes']),
                      'gcd_checks':sum(x['smoothness_gcd_checks'] for x in data['primes'])}))
if __name__=='__main__':main()
