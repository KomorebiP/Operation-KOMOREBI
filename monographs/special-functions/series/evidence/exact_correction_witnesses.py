"""Small exact witnesses for correction claims; not a test of universal theorems."""
from fractions import Fraction as F
from pathlib import Path
import json
from math import gcd
import sympy as s

checks=[]
def record(identifier, assertion, data):
    assert assertion, identifier
    checks.append({'correction':identifier,'passed':True,'exact_data':data})

chi2=int(gcd(2,4)==1)
indicator2=int(gcd(2,1)==1)
record('C02', chi2 != indicator2, {'object':'principal character modulo 4','chi_at_2':chi2,
                                  'conductor_1_coprimality_indicator_at_2':indicator2})
record('C04', F(5,48) < F(9,16), {'analytic_node_upper_bound':'5/48',
                                 'first_positive_spectral_point':'9/16',
                                 'scope':'Verifies the exact bound comparison; positivity and the bound itself are proved in the manuscript.'})
z=s.symbols('z')
res=s.residue(s.Rational(3,2)/(1-z*s.Rational(2,3)),z,s.Rational(3,2))
record('C05', res == -s.Rational(9,4), {'weight':'3/2','node':'2/3','z_residue':str(res)})
H=s.Matrix([[0,1],[1,0]])
moments=[s.Integer(0),s.Integer(1),s.Integer(0),s.Integer(0)]
q1,q2=s.symbols('q1 q2')
sol=s.solve([moments[2]+q1*moments[1]+q2*moments[0],
             moments[3]+q1*moments[2]+q2*moments[1]],(q1,q2))
Q=1+sol[q1]*z+sol[q2]*z*z
P=moments[0]+(moments[1]+sol[q1]*moments[0])*z
record('C08', H.det() == -1 and Q == 1 and P == z,
       {'generic_signed_moments':[0,1,0,0],'hankel_determinant':-1,'pade_function':'z',
        'scope':'Generic signed illustration, not an arithmetic Mobius-family counterexample.'})
R=s.Matrix([[s.Rational(1,2),s.sqrt(3)/2],[s.sqrt(3)/2,-s.Rational(1,2)]])
J=R*s.diag(0,2)*R.T
record('C09', s.simplify(J[0,1]+s.sqrt(3)/2)==0,
       {'matrix':'equal-half-shape N=1','opposing_offdiagonal':str(J[0,1])})
B=[s.eye(2),s.Matrix([[0,1],[1,0]]),s.diag(1,-1),R,s.diag(-1,1)]
loop=s.eye(2)
for i in range(5):loop=loop*(B[i].T*B[(i+1)%5])
record('C10', s.simplify(loop)==s.eye(2),
       {'frames':'five arbitrary complete orthogonal frames in R^2','pentagon':'identity',
        'scope':'Demonstrates telescoping without representation or Casimir hypotheses.'})
q=F(1,2);alpha=beta=F(1,2);gamma=F(4);delta=F(1)
def poch(a,k):
    value=F(1)
    for r in range(k):value*=1-a*q**r
    return value
def qr(n,y):
    total=F(0)
    for k in range(n+1):
        denominator=poch(alpha*q,k)*poch(beta*delta*q,k)*poch(gamma*q,k)*poch(q,k)
        assert denominator!=0
        numerator=poch(q**(-n),k)*poch(alpha*beta*q**(n+1),k)*poch(q**(-y),k)*poch(gamma*delta*q**(y+1),k)
        total+=numerator*q**k/denominator
    return total
table=[[qr(n,y) for y in range(2)] for n in range(2)]
lattice=[q**(-y)+gamma*delta*q**(y+1) for y in range(2)]
record('C11', table==[[F(1),F(1)],[F(1),F(1)]] and lattice==[F(3),F(3)],
       {'N':1,'q':'1/2','alpha':'1/2','beta':'1/2','gamma':'4','delta':'1',
        'scalar_table':[[str(x) for x in row] for row in table], 'lattice':[str(x) for x in lattice]})

output=Path('evidence/correction_witness_run/results.json')
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps({'checks':checks,'passed':len(checks),'non_claims':['Does not certify all source proofs.','Does not test unbounded parameter families.']},indent=2)+'\n')
print(json.dumps({'passed':len(checks),'output':str(output)}))
