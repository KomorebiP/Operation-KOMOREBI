#!/usr/bin/env python3
"""Complete exact Frey residue locus at 83, with an order-only 7-torsion filter.
The primary orbit counter adapts Block62's documented count mechanism.
No class-group, Galois, or analytical geometry theorem is certified by this code.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
Q=83

def require(ok:bool,msg:str)->None:
    if not ok:raise AssertionError(msg)

def legendre(x:int)->int:
    a=pow(x%Q,41,Q)
    return -1 if a==82 else a

def tables():
    d=2
    require(legendre(d)==-1,'Count basis is not a quadratic field')
    chars=[legendre(i) for i in range(Q)]
    base=[(x,x**3%Q,x**6%Q) for x in range(Q)]
    ext=[]
    for x in range(Q):
        for y in range(Q):
            a=(x*x+d*y*y)%Q;b=2*x*y%Q
            c=(a*x+d*b*y)%Q;e=(a*y+b*x)%Q
            ext.append((x,y,c,e,(c*c+d*e*e)%Q,2*c*e%Q))
    return chars,base,ext

def run()->dict:
    chars,base,ext=tables();p=Q
    seventh={pow(c,7,p) for c in range(1,p)}
    require(seventh==set(range(1,p)),'Equation admissibility shortcut not justified')
    eligible={(a,b) for a in range(p) for b in range(p) if (a**3+b**5)%p in seventh}
    todo=set(eligible);covered=set();rows=[];pair_records={}
    scalings=[(pow(t,5,p),pow(t,3,p)) for t in range(1,p)]
    target=[]
    while todo:
        a,b=min(todo)
        orbit={(a*x%p,b*y%p) for x,y in scalings}
        pairs=sorted(orbit&eligible);covered.update(pairs);todo.difference_update(orbit)
        AA=12*a%p;BB=10*b%p;CC=5*b*b%p
        N1=p+2+sum(chars[(x6+BB*x3+AA*x+CC)%p] for x,x3,x6 in base)
        n=0
        for x,y,x3,y3,x6,y6 in ext:
            re=(x6+BB*x3+AA*x+CC)%p;im=(y6+BB*y3+AA*y)%p
            n+=chars[(re*re-2*im*im)%p]
        N2=p*p+2+n
        s=p+1-N1;num=s*s-p*p-1+N2
        require(num%2==0,'Nonintegral Frobenius coefficient');b2=num//2
        # Rational roots squared, then the actual nonsquare F_(83^2) twist.
        S0=s*s-2*b2;B0=b2*b2-2*p*s*s+2*p*p
        S=-S0;Qv=p*p
        P=[Qv*Qv,-Qv*S,B0,-S,1];order=sum(P)
        require(order>0,'Nonpositive group order')
        row={'representative':[a,b],'pairs':[list(x) for x in pairs],
             'N1':N1,'N2':N2,'rational_polynomial':[p*p,-p*s,b2,-s,1],
             'twisted_polynomial':P,'jacobian_order':order,'order_divisible_2401':order%2401==0}
        rows.append(row)
        for x in pairs:pair_records[x]=[N1,N2,order]
        if row['order_divisible_2401']:target.extend(pairs)
    require(covered==eligible,'Incomplete admissible pair coverage')
    require(len(eligible)==6806 and len(rows)==83,'Unexpected exact count range')
    surviving=[r for r in rows if r['order_divisible_2401']]
    require(len(surviving)==1 and surviving[0]['representative']==[1,30],'Order filter changed')
    require(len(target)==82 and surviving[0]['jacobian_order']==45724644,'Exceptional orbit changed')
    digest=hashlib.sha256()
    for (a,b),rec in sorted(pair_records.items()):digest.update(f'{a},{b},{rec[0]},{rec[1]},{rec[2]}\n'.encode())
    return {'schema':'beal.block63.count83.v1','status':'PASS_FINITE_ORDER_FILTER',
        'q':83,'base_count_field':'Fp','degree_two_count_field':'Fp[t]/(t^2-2)',
        'f':2,'twist_sign':-1,'curve':'z^2=x^6+10 B x^3+12 A x+5 B^2',
        'all_admissible_pairs':6806,'orbits':83,'degree_one_counts':83,'degree_two_counts':83,
        'full_pair_count_hash':digest.hexdigest(),'surviving_pairs':len(target),'rows':rows,
        'nonclaim':'Divisibility of the group order by 7^4 does NOT certify full rational 7-torsion.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=run();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(d['status'])
if __name__=='__main__':main()
