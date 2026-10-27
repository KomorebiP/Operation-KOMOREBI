"""Independent finite recalculation from displayed definitions, stdlib only.

Does not import either author's model/checker and does not invoke Lean.
"""
from fractions import Fraction as Q
from math import factorial, comb
from pathlib import Path
import argparse, json

checks=[]
def check(name,ok,scope):
    assert ok,name
    checks.append({'name':name,'passed':True,'scope':scope})
def valuation(x,p):
    x=Q(x)
    if x==0:return None
    result=0
    for number,sign in [(abs(x.numerator),1),(x.denominator,-1)]:
        while number%p==0:
            number//=p;result+=sign
    return result
def reciprocal(a):
    # Direct identity a*b=1 in ordinary polynomial coefficient coordinates.
    b=[1/a[0]]
    for n in range(1,len(a)):
        b.append(-sum(a[n-k]*b[k] for k in range(n))/a[0])
    return b
def matmul(A,B):
    return [[sum(Q(A[i][k])*B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]
def eye(d,c=1):return [[Q(c if i==j else 0) for j in range(d)] for i in range(d)]

u=reciprocal([Q(1,factorial(6*n+3)) for n in range(3)])
u=[factorial(6*n)*u[n] for n in range(3)]
c=[v/6 for v in u]
check('actual_6_3_reciprocal',c==[Q(1),Q(-1,84),Q(703,5460)],'degrees 0,6,12 of the displayed reciprocal')
check('normalization_loss',valuation(c[2]-c[1],3)==0 and valuation(u[2]-u[1],3)==1,'visual p.7 two displayed differences')

e=reciprocal([Q(1,factorial(2*n)) for n in range(8)])
e=[factorial(2*n)*e[n] for n in range(8)]
beta=reciprocal([Q(2**(2*n+1),factorial(2*n+2)) for n in range(8)])
def source(n):return Q(3**(2*n+2)-1,4*(2*n+1)*(2*n+2))
def term(n,m):return beta[m]*2**(2*m)*Q(factorial(2*n),factorial(2*n-2*m))*source(n-m)
check('dyadic_reconstruction_from_series',all(sum(term(n,m) for m in range(n+1))==e[n] for n in range(8)),'rows 0 through 7, rational formal-series inversion')
check('row6_weights', [valuation(term(6,m),2) for m in range(1,7)]==[4,7,13,15,20,23], 'visual p.18 all six nonconstant terms')
check('row6_tail_weights',[valuation(e[6]-sum(term(6,m) for m in range(M+1)),2) for M in range(6)]==[4,7,13,15,20,23],'visual p.18 depths 0 through 5')
t=sum(term(4,m) for m in range(2))
check('synthesis_coefficients',e[4]==1385 and t==Q(-91019,45) and e[4]-t==Q(153344,45) and valuation(e[4]-t,2)==8,'visual p.29 exact coefficient/truncation/error')
target=(2*t.numerator*pow(t.denominator,-1,256))%256
roots=[y for y in range(256) if (y+y*y-2*e[4])%256==0]
check('synthesis_residue_roots',target==210 and roots==[14,241],'complete 256-candidate enumeration')

check('weighted_finite_roots',[x for x in range(1,256,4) if (x*x-17)%256==0]==[105,233],'visual p.25 complete residue ball at depth eight')
check('weighted_branch_transition',[x for x in [105,361] if (x*x-17)%512==0]==[] and [x for x in [233,489] if (x*x-17)%512==0]==[233,489],'visual p.25 all two children of each shown residue')
check('strict_weighted_threshold_failure',all((x*x+3)%8!=0 for x in range(8)),'visual p.25 complete depth-three exclusion')
check('joint_motion_sign',(-8)+4+4==0 and (-8+4)%16!=0 and (-8)%16!=0,'visual p.26 linear parameter and coefficient motion')
unit_candidates=[y for y in range(0,256,2) if (y+y*y+2)%256==0]
weighted_candidates=[y for y in range(0,512,4) if (y*y+2*y+8)%512==0]
check('motion_error_sharp_unit',len(unit_candidates)==1 and all(valuation(y+2,2)==2 for y in unit_candidates),'all even residues at depth eight; finite evidence only')
check('motion_error_weight_one',len(weighted_candidates)==2 and all(valuation(y+4,2)==3 for y in weighted_candidates),'independent weighted s=1,M=3 example; finite evidence only')
B=[[2,0,1],[0,8,3],[0,0,1]];C=[[4,0,-4],[0,1,-3],[0,0,8]]
check('augmented_inverse_both_orders',matmul(B,C)==eye(3,8) and matmul(C,B)==eye(3,8),'visual p.27 two actual 3-by-3 products')

psi=[Q(0)]
for n in range(1,9):psi.append(-Q(n==1)-sum(psi[k]*psi[n-k] for k in range(1,n)))
check('analytic_formal_coefficients',psi[1:7]==[-1,-1,-2,-5,-14,-42],'visual p.24 formal algebra through degree eight; no convergence claim')
path=[]
for L in range(1,9):
    candidates=[y for y in range(0,2**L,2) if (y+y*y+2)%2**L==0]
    assert len(candidates)==1
    path.append(candidates[0])
check('fixed_parameter_path',path==[0,2,2,10,26,26,90,90] and all(path[L]%2**L==path[L-1] for L in range(1,8)),'visual p.34 complete even-residue enumeration at each depth')
check('finite_representative_not_exact',90+90**2+2==8192,'visual p.34 integer evaluation')

T=[[1,0,0,0],[1,1,0,0],[0,2,1,0],[0,0,3,1]]
V=[[1,0,0,0],[-1,1,0,0],[2,-2,1,0],[-6,6,-3,1]]
P=eye(4);P[1][1]=P[3][3]=0
Ph=matmul(matmul(T,P),V)
check('coordinate_conjugation',matmul(T,V)==eye(4) and matmul(V,T)==eye(4) and matmul(Ph,Ph)==Ph,'visual p.31 exact closed leading triangular block')
fib=[0,1]
for n in range(2,16):fib.append(fib[-1]+fib[-2])
check('recurrence_packets',all(fib[n+4]==3*fib[n+2]-fib[n] for n in range(12)),'visual p.32 first twelve two-step recurrence evaluations')
result={'primary_verdict':'computationally verified only in a stated range','fresh_lean_run':False,'checks':checks,'checks_passed':len(checks),'method':'Independent Python integer/Fraction derivations; no imports from author models or checkers','limits':['Bounded computations do not prove the manuscript universal statements.','Formal series coefficient calculations do not certify analytic convergence.','Finite roots are tested at stated moduli, not exact p-adic roots.']}
parser=argparse.ArgumentParser()
parser.add_argument('--result',type=Path,default=Path(__file__).with_name('INDEPENDENT_EXAMPLE_CHECKS.json'))
args=parser.parse_args()
args.result.write_text(json.dumps(result,indent=2)+'\n')
print({'checks_passed':len(checks),'primary_verdict':result['primary_verdict']})
