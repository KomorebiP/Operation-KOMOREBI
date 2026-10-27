"""Exact finite audit of the actual Euler factor in stable Jacobi models."""
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import json,sys

PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'bernoulli_closure/nonintersection'))
from check_hankel_separation import bernoulli,val,v_int,add,mul,scale

def main(path):
    B=bernoulli(64)
    D=[(2-4**n)*B[2*n] for n in range(33)]
    identities=errors=first=0
    records=[]
    for r in range(1,7):
        def moment(p):return sum(z*D[r+j] for j,z in enumerate(p))
        polys=[];norms=[]
        for n in range(5):
            p=[F(0)]*n+[F(1)]
            for old,h in zip(polys,norms):p=add(p,scale(old,-moment(mul(p,old))/h))
            polys.append(p);norms.append(moment(mul(p,p)))
        diagonal=[moment([F(0)]+mul(p,p))/h for p,h in zip(polys,norms)]
        sub=[F(0)]+[norms[n]/norms[n-1] for n in range(1,5)]
        for m in range(1,5):
            h=4*m+4*v_int(factorial(m));vector=[F(1)]+[F(0)]*(m-1)
            for q in range(21):
                delta=F(2**(2*r-1))
                e=(1-delta)/(1-delta*4**q)
                assert val(e)==0
                depleted=D[r+q]/D[r]
                actual=B[2*(r+q)]/B[2*r]
                assert actual==depleted*e
                identities+=1
                model=vector[0]*e;error=actual-model
                assert val(model)==0
                if q<2*m:assert error==0
                else:assert error==0 or val(error)>=h
                if q==2*m:
                    assert val(error)==h;first+=1
                errors+=1
                if q in (0,2*m,20):
                    records.append({'r':r,'m':m,'q':q,'bound':h,'error_valuation':val(error)})
                nxt=[F(0)]*m
                for n,z in enumerate(vector):
                    nxt[n]+=diagonal[n]*z
                    if n+1<m:nxt[n+1]+=z
                    if n:nxt[n-1]+=sub[n]*z
                vector=nxt
    payload={'status':'passed','factor_identity_checks':identities,
             'actual_error_checks':errors,'exact_first_exit_checks':first,
             'records':records,'nonclaims':['No stationary scalar or new T tested',
               'All-depth chart theorem uses explicitly named parent inputs',
               'No proof of Euler nonvanishing']}
    out=Path(path);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({k:payload[k] for k in ['status','factor_identity_checks','actual_error_checks','exact_first_exit_checks']}))

if __name__=='__main__':main(sys.argv[1])
