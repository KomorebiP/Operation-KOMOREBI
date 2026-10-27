#!/usr/bin/env python3
"""Exact algebra controls for Block58. Finite tests accompany written proofs.
No curve point counts at 2549 are performed or needed.
"""
from __future__ import annotations
import argparse,itertools,json,math
from pathlib import Path

def check(b,msg):
    if not b:raise ValueError(msg)

def mul(x,y,m):
    a,b=x;c,d=y
    return ((a*c+b*d)%m,(a*d+b*c+b*d)%m)

def inv(x,m):
    a,b=x;norm=(a*a+a*b-b*b)%m
    k=pow(norm,-1,m)
    return ((a+b)*k%m,-b*k%m)

def quartic(Q,s,c):return [Q*Q,-Q*s,c,-s,1]
def target(Q):return quartic(Q,2*(Q+1),(Q+1)**2+2*Q)

def weil_exact(Q,s,D):
    if D<0:return False
    v=16*Q-s*s-D
    return v>=0 and v*v>=4*s*s*D

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    tests=0
    for r,Q,A,B in itertools.product(range(1,7),(11,19,31,41,59,97,197,491,1373,2549),range(-3,4),range(-3,4)):
        t=7**r;x=Q+1+t*A;y=t*B
        trace=2*x+y;norm=x*x+x*y-y*y;D=trace*trace-4*norm
        check(D==5*y*y and D%(t*t)==0,'Trace-discriminant identity')
        P=quartic(Q,trace,norm+2*Q)
        check(all((p-q)%t==0 for p,q in zip(P,target(Q))),'Restriction-of-scalars coefficient precision')
        tests+=1
    separated=0
    for n,q in itertools.product(range(1,4),(41,59)):
        M=7**n;size=7**(n-1);survivors=[]
        for aa,bb in itertools.product(range(size),repeat=2):
            e=(1+7*aa,7*bb);iv=inv(e,M)
            if ((q*e[0]+iv[0])%M,(q*e[1]+iv[1])%M)==((q+1)%M,0):survivors.append(e)
            separated+=1
        check(survivors==[(1,0)],'Separated local character control failed')
    q=2549;r=3;M=7**r
    divisors=[d for d in range(2,math.isqrt(q)+1) if q%d==0];check(not divisors,'2549 composite')
    roots5=[x for x in range(q) if x*x%q==5];check(len(roots5)==2,'2549 not split')
    check((q-1)%49==0 and (q-1)%343!=0,'Wrong h2549')
    bound=math.isqrt(4*q);allowed=[t for t in range(-bound,bound+1) if (t-q-1)%M==0]
    check(bound==100 and not allowed,'A rational rank-two trace survived')
    check(M*M>16*q,'Discriminant not forced to vanish')
    # Generic reciprocal Weil polynomials that pass only the rank-four congruence.
    candidates=[]
    for s in range(-math.isqrt(16*q),math.isqrt(16*q)+1):
        if (s-2*(q+1))%M:continue
        for c in range(-2*q,6*q+1):
            P=quartic(q,s,c)
            if any((x-y)%M for x,y in zip(P,target(q))):continue
            D=s*s-4*(c-2*q)
            if weil_exact(q,s,D):candidates.append({'trace':s,'middle_coefficient':c,'D':D})
    check(candidates and not any(x['D']%(M*M)==0 for x in candidates),'Discriminant distinction lost')
    s=-45;c=2603;D=12005;P=quartic(q,s,c)
    check(D==s*s-4*(c-2*q)==5*49**2,'Control discriminant wrong')
    check(weil_exact(q,s,D) and all((x-y)%M==0 for x,y in zip(P,target(q))),'Generic Weil control failed')
    # tau=-47+49phi lies in the prescribed unramified coefficient field,
    # but is only congruent to Q+1 modulo49, not modulo343.
    tau=(-47,49);norm=tau[0]**2+tau[0]*tau[1]-tau[1]**2
    check(2*tau[0]+tau[1]==s and norm+2*q==c,'Control does not factor over the coefficient field')
    check((tau[0]-q-1)%49==0 and tau[1]%49==0 and tau[1]%343!=0,'Control precision')
    e=(295,0);iv=inv(e,343)
    check(((29*e[0]+iv[0])%343,(29*e[1]+iv[1])%343)==(30,0) and e!=(1,0),'h=1 negative control failed')
    out={'schema':'komorebi.beal.block58.discriminant.v1','status':'PASS_DECLARED_EXACT_CHECKS',
      'trace_discriminant_identity_cases':tests,'separated_principal_root_cases':separated,
      'prime2549':{'q':q,'trial_divisors_checked':math.isqrt(q)-1,'sqrt5_roots':roots5,
        'h':2,'trace_precision':r,'modulus':M,'D_divisibility':M*M,'D_upper_bound':16*q,
        'trace_integer_bound':bound,'trace_residue':(q+1)%M,'allowed_integer_traces':allowed},
      'rank_four_only_candidates':candidates,'rank_four_only_candidate_count':len(candidates),
      'rank_four_not_rank_two_negative_control':{'polynomial_ascending':P,'trace':s,'c2':c,'D':D,'tau_phi_coefficients':list(tau)},
      'h_positive_negative_control':{'q':29,'n':3,'eta':295},
      'nonclaims':['Finite algebra tests are not a universal proof','No point counts at 2549','No Beal proof']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'identity_cases':tests,'separated_roots':separated,'generic_Weil_candidates':len(candidates)}))
if __name__=='__main__':main()
