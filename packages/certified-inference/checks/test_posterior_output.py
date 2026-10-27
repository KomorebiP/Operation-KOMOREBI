#!/usr/bin/env python3
"""Bounded exact tests against an independent scalar-sum reference implementation."""
import json,sys
from pathlib import Path
from fractions import Fraction as Q
from exact_certificate import Model,encode,eye,matrix,rational
import posterior_output as out
import rounded_certificate as rb
checks=0

def check(b,msg):
    global checks
    checks+=1
    if not b:raise AssertionError(msg)

def reference(m,B):
    # Independent closed scalar sums: no evaluator or producer matrix routines.
    n,k=len(B),len(B[0]);u,w=len(m.L[0]),len(m.N[0])
    v=[m.observation[j]-sum((m.H[j][i]*m.mean[i] for i in range(n)),Q(0)) for j in range(k)]
    mean=[m.mean[i]+sum((B[i][j]*v[j] for j in range(k)),Q(0)) for i in range(n)]
    # Form Joseph factors directly, instead of the evaluator's (I-BH) P (I-BH)^T graph.
    A=[[m.L[i][a]-sum((B[i][j]*m.H[j][l]*m.L[l][a] for j in range(k) for l in range(n)),Q(0)) for a in range(u)] for i in range(n)]
    C=[[sum((B[i][j]*m.N[j][a] for j in range(k)),Q(0)) for a in range(w)] for i in range(n)]
    cov=[[sum((A[i][a]*A[j][a] for a in range(u)),Q(0))+sum((C[i][a]*C[j][a] for a in range(w)),Q(0))+m.sigma*sum((B[i][a]*B[j][a] for a in range(k)),Q(0)) for j in range(n)] for i in range(n)]
    return mean,cov

def main():
    cases=[]
    for cid,(n,k,u,w) in enumerate([(1,1,1,1),(2,1,1,1),(1,2,1,2),(2,2,1,1),(3,2,2,1),(2,3,1,2)]):
        H=tuple(tuple(Q((-1)**(i+j)*(i+j+1),3) for j in range(n)) for i in range(k))
        L=tuple(tuple(Q(i+j+1,4) for j in range(u)) for i in range(n))
        N=tuple(tuple(Q(i-j,7) for j in range(w)) for i in range(k))
        B=tuple(tuple(Q(i-j-1,9) for j in range(k)) for i in range(n))
        m=Model.parse(encode(dict(H=H,L=L,N=N,sigma=Q(1,1000) if cid==5 else Q(2,3),mean=tuple(Q(i-1,5) for i in range(n)),observation=tuple(Q(j+1,7) for j in range(k)),output_packets=(eye(n),),input_packets=(eye(k),))))
        mean,cov=reference(m,B);bm,bc=out.graph(m,B,budget=True)
        for prec in [0,1,4,12,32]:
            om,oc=out.graph(m,B,precision=prec)
            for i in range(n):
                check(om[i].encloses(mean[i]),'mean enclosure')
                check(om[i].radius<=bm[i].coeff*Q(1,1<<prec),'mean budget')
                for j in range(n):
                    check(oc[i][j].encloses(cov[i][j]),'covariance enclosure')
                    check(oc[i][j].radius<=bc[i][j].coeff*Q(1,1<<prec),'covariance budget')
        selected=[]
        for delta in [Q(1,10),Q(1,1000),Q(1,10**9)]:
            rep=out.represent(m,B,delta);check(Q(rep['maximum_radius'])<=delta,'precision sufficiency')
            om,oc=out.graph(m,B,precision=rep['precision'])
            check(all(om[i].encloses(mean[i]) for i in range(n)),'selected mean')
            check(all(oc[i][j].encloses(cov[i][j]) for i in range(n) for j in range(n)),'selected covariance')
            selected.append(rep['precision'])
        cases.append(dict(n=n,k=k,prior_factor_columns=u,noise_factor_columns=w,noise_floor=str(m.sigma),selected_bits=selected))
    L=[Q(1,2),Q(3,2)];c=[[x*y for y in L] for x in L]
    rounded=[[rb.down(1,x) for x in row] for row in c];v=[-3,1]
    check(c[0][0]*c[1][1]-c[0][1]*c[1][0]==0,'singular Gram')
    check(rounded[0][0]*rounded[1][1]-rounded[0][1]*rounded[1][0]==Q(-1,4),'negative determinant')
    check(sum(v[i]*rounded[i][j]*v[j] for i in range(2) for j in range(2))==-1,'negative quadratic witness')
    raw=json.loads(Path('examples/solver_scalar.json').read_text());m=Model.parse(raw['model']);b=matrix(raw['initial_gain'],'B');eps=rational(raw['epsilon']);rejected=0
    for delta in [Q(0),Q(-1)]:
        try:out.represent(m,b,delta)
        except ValueError:rejected+=1
        else:raise AssertionError('nonpositive delta accepted')
    limited=out.solve(m,b,eps,Q(1,2**1000),[12]);check(limited['status']=='RESOURCE_LIMIT','output precision cap')
    try:out.export_lean(m,b,eps,Q(1,2**1000),limited,'MustFail')
    except ValueError:rejected+=1
    else:raise AssertionError('capped output exported proof')
    report=dict(status='PASS',assertions=checks,expected_rejections=rejected,cases=cases,precisions=[0,1,4,12,32],radius_tolerances=['1/10','1/1000','1/1000000000'],arithmetic='Exact Fraction ball graph against independent direct Joseph-factor scalar sums',covariance_rounding_counterexample={'input':encode(c),'rounded':encode(rounded),'vector':v,'quadratic_form':'-1'},non_claims=['Finite constructed tests, not universal proof or performance evidence.','No center-defined Gaussian or sample executable certified.'])
    path=Path(sys.argv[1]);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','assertions','expected_rejections']}))
if __name__=='__main__':main()
