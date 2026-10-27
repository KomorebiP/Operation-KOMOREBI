"""Exact finite checks of generic inverse and both scalar-reduction surfaces."""
from fractions import Fraction as F
from itertools import product
from math import factorial
from pathlib import Path
import argparse,hashlib,json,platform,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coupled_lab import coupled_odd_derivatives
from coupled_inverse import recover_rational_scales
from family_lab import asymmetric_odd_derivatives

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'evidence/v11/coupled_inverse_checks.json')
    args=parser.parse_args()
    start=time.monotonic(); counts={}; generic=0;reduced=0
    def check(label,condition):
        if not condition:raise AssertionError(label)
        counts[label]=counts.get(label,0)+1
    for q,r,a,b in product([F(1,5),F(2,5),F(3,5),F(4,5)],repeat=4):
        U,V=coupled_odd_derivatives(q,r,a,b,last=3)
        u1,u2,u3=[U[n]/factorial(2*n+1) for n in range(1,4)]
        v1,v2,v3=[V[n]/factorial(2*n+1) for n in range(1,4)]
        p,k=q*r,a*b
        D=k*k*u2-p*p*v2
        check('D_factorization',D==p*k*a*r*(q*q-b*b)*(q*b-a*r)/15)
        for x,y in [(u1,p/3),(v1,k/3),(u2,p*(p*q*q+k*r*r)/15),
                    (v2,k*(p*a*a+k*b*b)/15),
                    (u3,p*(q**4*u2+p*p*u1*v1+r**4*v2)/7),
                    (v3,k*(a**4*u2+k*k*u1*v1+b**4*v2)/7)]:
            check('coefficient_formulas',x==y)
        check('reduction_locus',bool(D==0)==bool(q==b or q*b==a*r))
        if D:
            generic+=1
            check('exact_parameter_recovery',recover_rational_scales(u1,v1,u2,v2,u3,v3)==(q,r,a,b))
            x,x2=q*q,k*p/(q*q)
            u3_other=p*(x2*x2*u2+p*p*u1*v1+(p*p/x2)**2*v2)/7
            check('U_candidate_separation',u3-u3_other==p*D*(x*x-x2*x2)/(7*k*k))
            y,y2=a*a,k**3/(p*a*a)
            v3_other=k*(y2*y2*u2+k*k*u1*v1+(k*k/y2)**2*v2)/7
            check('V_candidate_separation',v3-v3_other==D*(y*y-y2*y2)/(7*k))
        else:
            reduced+=1
            try:recover_rational_scales(u1,v1,u2,v2,u3,v3)
            except ValueError:check('reduced_domain_rejection',True)
            else:raise AssertionError('D=0 inverse silently accepted')
    reduction_cases=[(F(1,2),F(1,9),F(4,9),F(1,2),F(2)),
                     (F(1,5),F(1,4),F(2,5),F(1,2),F(2)),
                     (F(2,5),F(1,2),F(1,5),F(1,4),F(1,2))]
    for q,r,a,b,s in reduction_cases:
        U,V=coupled_odd_derivatives(q,r,a,b,last=14)
        T=asymmetric_odd_derivatives(q,s*r,14)
        for n in range(15):
            check('scalar_reduction_U',U[n]==s**(-n)*T[n])
            check('scalar_reduction_V',V[n]==s**n*T[n])
    p=(F(1,5),F(2,5),F(3,5),F(7,10))
    U,V=coupled_odd_derivatives(*p,last=3)
    jet=[U[1]/6,V[1]/6,U[2]/120,V[2]/120,U[3]/5040,V[3]/5040]
    check('worked_example',recover_rational_scales(*jet)==p)
    bad=jet.copy();bad[-1]+=F(1,10**8)
    try:recover_rational_scales(*bad)
    except ValueError:check('inconsistent_jet_rejection',True)
    else:raise AssertionError('inconsistent jet accepted')
    sources=['coupled_inverse.py','coupled_lab.py','family_lab.py','checks/coupled_inverse_v11.py',
             'research_v11/coupled_identifiability.md','research_v11/TARGET_CONTRACT.json']
    report={'checkpoint':'SF-DISCOVERY-110','status':'passed','python':platform.python_version(),
            'exact_assertions':sum(counts.values()),'numerical_assertions':0,'counts':counts,
            'bounds':{'rational_grid_points':256,'generic_points':generic,'reduced_points':reduced,
                      'grid_jet_degree':7,'reduction_cases':3,'reduction_max_degree':29},
            'worked_parameters':list(map(str,p)),'worked_jet':list(map(str,jet)),
            'elapsed_seconds':time.monotonic()-start,
            'inputs':[{'path':x,'sha256':hashlib.sha256((ROOT/x).read_bytes()).hexdigest()} for x in sources],
            'non_claims':['Finite checks are not a proof of the universal classification.',
                          'No stability guarantee is inferred from exact reconstruction.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','exact_assertions','bounds','elapsed_seconds']}))
if __name__=='__main__':main()
