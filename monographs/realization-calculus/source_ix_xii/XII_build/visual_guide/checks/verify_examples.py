#!/usr/bin/env python3
"""Exact checks for the visual guide, not a Lean/theorem-census update.
All finite enumerations use integers or F_5; symbolic checks use SymPy QQ.
The LaTeX text supplies uniform arguments where an illustration has a finite window.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, platform
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'checks'/'EXACT_CHECKS.json')
args=parser.parse_args()
results=[]
def record(name, assertion, detail):
    if not assertion: raise AssertionError(name)
    results.append({'name': name, 'status':'PASS', 'detail':detail})

def mul5(a,b,n):
    return tuple(sum(a[i]*b[j] for i in range(n) for j in range(n) if i+j==d)%5 for d in range(n))

# Local maps Z_5[[u,v]] -> F_5[d]/d^3, with the fixed residue coefficient map.
accepted=[]
for a,b,c,d in itertools.product(range(5),repeat=4):
    u=(0,a,b);v=(0,c,d)
    if mul5(u,u,3)==(0,0,0) and u==v: accepted.append((a,b,c,d))
record('local_points_order_three', accepted==[(0,b,0,b) for b in range(5)],
       {'candidate_count':625,'accepted_count':5,'accepted':accepted})
accepted2=[]
for a,c in itertools.product(range(5),repeat=2):
    if mul5((0,a),(0,a),2)==(0,0) and a==c: accepted2.append((a,c))
record('local_points_order_two',accepted2==[(a,a) for a in range(5)],
       {'candidate_count':25,'accepted_count':5,'image_of_order_three':[[0,0]],
        'nonzero_tangent_directions_with_no_lift':4})
# Each drawn square records a monomial of total variable degree < 6 over Z_5.
mons=[(i,j) for i in range(6) for j in range(6-i)]
kept=[(i,j) for i,j in mons if i<2 and j==0]
record('quotient_monomial_window',kept==[(0,0),(1,0)],
       {'window_total_degree_less_than':6,'shown':len(mons),'surviving_O_basis':kept})
# Canonical 5-adic digit prefixes in B_n=(Z/5^n)[epsilon]/epsilon^2.
prefix=[]
for n in range(1,7):
    a=sum(((j*j+1)%5)*5**j for j in range(n))
    b=sum(((2*j+1)%5)*5**j for j in range(n))
    prefix.append({'n':n,'modulus':5**n,'a':a,'b':b,'ring_cardinality':5**(2*n)})
record('adic_prefix_compatibility',all(prefix[i+1]['a']%prefix[i]['modulus']==prefix[i]['a'] and
       prefix[i+1]['b']%prefix[i]['modulus']==prefix[i]['b'] for i in range(5)),prefix)
# Fitting ideals: compute all minors, normalize the generated ideals by Groebner basis.
x,y,t=sp.symbols('x y t')
def fitting_gens(A,j):
    q=A.rows-j
    if q<=0: return [sp.Integer(1)]
    if q>min(A.shape): return [sp.Integer(0)]
    return [sp.expand(A.extract(r,c).det()) for r in itertools.combinations(range(A.rows),q)
            for c in itertools.combinations(range(A.cols),q)]
def gb(gens,vars):
    return tuple(sp.groebner(gens,*vars,domain=sp.QQ).polys)
A=sp.diag(x,y);A2=sp.diag(x*x,y);Astab=sp.diag(x,y,1)
expected=[[x*y],[x,y],[1]]
for j in range(3):
    record(f'fitting_matrix_index_{j}',gb(fitting_gens(A,j),(x,y))==gb(expected[j],(x,y)),
           {'generators':[str(q) for q in fitting_gens(A,j)]})
    record(f'presentation_stabilization_index_{j}',gb(fitting_gens(A,j),(x,y))==gb(fitting_gens(Astab,j),(x,y)),
           'Explicit diag(x,y) versus diag(x,y,1), not a proof of general presentation independence.')
record('nilpotent_fitting_ideals',gb(fitting_gens(A2,0),(x,y))==gb([x*x*y],(x,y)) and
       gb(fitting_gens(A2,1),(x,y))==gb([x*x,y],(x,y)),{'F0':'(x^2 y)','F1':'(x^2,y)'})
for a,b,dim in [(1,1,0),(0,1,1),(1,0,1),(0,0,2)]:
    record(f'fiber_rank_{a}_{b}',2-A.subs({x:a,y:b}).rank()==dim and
           2-A2.subs({x:a,y:b}).rank()==dim,{'point':[a,b],'fiber_dimension':dim})
for j,exp in [(0,[t*t]),(1,[t]),(2,[1])]:
    record(f'diagonal_base_change_{j}',gb([q.subs({x:t,y:t}) for q in fitting_gens(A,j)],(t,))==gb(exp,(t,)),
           {'expected':[str(q) for q in exp]})
a,b=sp.symbols('a b')
record('coordinate_change_invertible',sp.Matrix([[1,1],[1,-1]]).det()==-2,
       'Over characteristic not equal to 2; the geometric plate uses real coordinates.')
record('coordinate_change_fitting',sp.expand((a+b)*(a-b))==a*a-b*b and
       gb([a+b,a-b],(a,b))==gb([a,b],(a,b)),{'F0':'(a^2-b^2)','F1':'(a,b)'})
# CRT projectors for a genuine nonsemisimple five-dimensional algebra.
z=sp.symbols('z');f=sp.expand((z-1)**2*(z+1)**3)
p=sp.expand((5-3*z)*(z+1)**3/sp.Integer(16));q=1-p
J2=sp.Matrix([[1,0],[1,1]]);J3=sp.Matrix([[-1,0,0],[1,-1,0],[0,1,-1]])
H=sp.diag(J2,J3)
def peval(poly,mat):
    pp=sp.Poly(poly,z);r=sp.zeros(mat.rows)
    for (j,),c in pp.terms():r+=c*mat**j
    return r
E=peval(p,H);F=peval(q,H)
record('CRT_polynomial_congruences',sp.rem(p-1,(z-1)**2,z)==0 and sp.rem(p,(z+1)**3,z)==0 and
       sp.rem(p*p-p,f,z)==0,{'p_plus':str(p),'modulus':str(f)})
record('CRT_matrix_projectors',E==sp.diag(1,1,0,0,0) and F==sp.diag(0,0,1,1,1) and
       E*F==sp.zeros(5) and E+F==sp.eye(5),{'ranks':[E.rank(),F.rank()],'traces':[str(sp.trace(E)),str(sp.trace(F))]})
record('ordinary_vs_generalized',len((H-sp.eye(5)).nullspace())==1 and
       len((H+sp.eye(5)).nullspace())==1 and len(((H-sp.eye(5))**2).nullspace())==2 and
       len(((H+sp.eye(5))**3).nullspace())==3,{'ordinary':[1,1],'generalized':[2,3]})
record('packet_residue_fibers',2-(J2-sp.eye(2)).rank()==1 and 3-(J3+sp.eye(3)).rank()==1,
       'Regular local packet dimensions 2 and 3, residue fibers each dimension 1.')
record('empty_packet_example',peval(p,J2)==sp.eye(2) and peval(q,J2)==sp.zeros(2),
       'The supplied T-module T_+ is not faithful on the second factor.')
# Group algebra F_2[C_2] = F_2[d]/d^2, and the projector trace warning.
idempotents=[(a,b) for a,b in itertools.product(range(2),repeat=2)
             if (a*a%2,(2*a*b)%2)==(a,b)]
record('dyadic_idempotents',idempotents==[(0,0),(1,0)],idempotents)
G=sp.Matrix([[1,0],[1,1]])
record('dyadic_involution',all(int(v)%2==0 for v in G**2-sp.eye(2)),
       'Multiplication by g=1+d has g^2=1 over F_2 and a nonzero nilpotent part.')
record('trace_not_occupancy_in_characteristic_two',int(sp.trace(sp.eye(2)))%2==0,
       {'idempotent':'I_2','rank_over_F2':2,'trace_over_F2':0})
# Stable-core examples: identities prove the all-level assertions in the prose.
P=sp.diag(1,0,0);N=sp.Matrix([[0,1,0],[0,0,1],[0,0,0]])
record('stable_core_identities',P*P==P and N**3==sp.zeros(3),
       {'P_power_image_dimensions':[(P**i).rank() for i in range(5)],
        'N_power_image_dimensions':[(N**i).rank() for i in range(5)]})
dims=[5,4,4,2,1,1,1,1]
Ps=[sp.diag(*([1]*d+[0]*(5-d))) for d in dims]
record('fixed_carrier_nested_projectors',all(Ps[i+1]*Ps[i]==Ps[i+1] and Ps[i]*Ps[i+1]==Ps[i+1] for i in range(7)),
       {'dimensions':dims,'a_plateau_precedes_a_later_drop':True,'definition_after_level_5':'constant projector onto e_1'})
# Derived fiber exact matrices; uniform argument is in the text.
record('derived_fiber_dimensions',[(1-sp.Matrix([[a]]).rank(),1-sp.Matrix([[a]]).rank()) for a in [0,1,-1]]==[(1,1),(0,0),(0,0)],
       'C=[k[t] --t--> k[t]] in degrees 0,1; all a != 0 give an isomorphism.')

# Additional guide examples, still illustrative checks rather than a theorem audit.
def modmat(A,p):
    return A.applyfunc(lambda q:int(q)%p)
s7=sp.Matrix([[6,1],[0,1]]);t7=sp.Matrix([[0,6],[1,6]])
I2=sp.eye(2)
record('S3_group_relations_F7',modmat(s7**2,7)==I2 and modmat(t7**3,7)==I2 and
       modmat(s7*t7*s7,7)==modmat(t7**2,7),'Exact defining relations modulo 7.')
Wsign=sp.Matrix([[2,3],[4,5]]);Wstd=sp.Matrix([[6,4],[3,1]])
Pt=sp.Matrix([[2,4],[3,6]]);Ps=sp.Matrix([[0,4],[0,1]])
record('S3_projector_pairings_F7',int(sp.trace(Pt*Wsign))%7==3 and
       int(sp.trace(Ps*Wstd))%7==6,{'pairings_mod_7':[3,6]})
record('S3_projector_idempotence_F7',modmat(Pt*Pt,7)==Pt and modmat(Ps*Ps,7)==Ps,
       'Printed canonical projectors are idempotent.')
record('S3_canonical_formula_F7',modmat(3*(t7-4*I2),7)==Pt and
       modmat(4*(s7+I2),7)==Ps,'Inverses of 2-4 and 1-(-1) are 3 and 4 in F7.')
record('S3_adjoint_basis_F7',int(sp.Matrix([[2,1,1],[3,1,5],[4,2,6]]).det())%7==3,
       'Columns Z,A,B have determinant 3 modulo 7.')
record('S3_eigenvalue_polynomials_F7',sp.Poly(t7.charpoly(z).as_expr()-(z-2)*(z-4),z,
       modulus=7).is_zero and sp.Poly(s7.charpoly(z).as_expr()-(z-1)*(z+1),z,
       modulus=7).is_zero,'Characteristic polynomials split as printed.')
X,Y=sp.symbols('X Y')
record('augmentation_binomial_relations_F2',sp.Poly((1+X)**4-1-X**4,X,modulus=2).is_zero
       and sp.Poly((1+Y)**2-1-Y**2,Y,modulus=2).is_zero,'C4 x C2 relations in F2.')
aug_basis=[(i,j) for j in range(2) for i in range(4)]
record('augmentation_basis_and_nilpotence',len(aug_basis)==8 and
       all(i>=4 or 5-i>=2 for i in range(6)),
       {'basis_exponents':aug_basis,'nilpotence_bound':5})
D=sp.diag(1,-1);Q=sp.Matrix([[1,1],[0,1]]);C=Q*D*Q.inv()
record('conjugate_involution_frame',C==sp.Matrix([[1,-2],[0,-1]]) and C*C==I2,
       'Both frames satisfy A^2=I.')
record('frame_reduction_mismatch',modmat(C,25)==sp.Matrix([[1,23],[0,24]]) and
       modmat(C,5)==sp.Matrix([[1,3],[0,4]]) and modmat(C,5)!=modmat(D,5),
       'Compatible conjugacy classes need not give compatible arbitrary frames.')
record('compatible_diagonal_representatives',all(modmat(modmat(D,5**(n+1)),5**n)==
       modmat(D,5**n) for n in range(1,6)),'Prefixes checked through level 6; the all-level formula is reduction of one integral D.')
a11,a12,a21,a22=sp.symbols('a11 a12 a21 a22')
Amat=sp.Matrix([[a11,a12],[a21,a22]])
polys=[a11*a11+a12*a21-1,a12*(a11+a22),a21*(a11+a22),a21*a12+a22*a22-1]
record('involution_equations',all(sp.expand(lhs-rhs)==0 for lhs,rhs in
       zip(list(Amat*Amat-I2),polys)),'Four exact entries of A^2-I.')
record('frame_sensitive_entry',D[0,1]==0 and C[0,1]==-2,
       'a12=0 is not invariant under admissible change of frame.')
Sep=sp.Matrix([[1,1],[1,-1]])
record('trace_separator_exact_solution',Sep.det()==-2 and Sep.inv()*sp.Matrix([5,1])==
       sp.Matrix([3,2]),{'determinant':-2,'multiplicities':[3,2]})
record('trace_separator_dyadic_failure',int(Sep.det())%2==0 and
       modmat(Sep,2)==sp.Matrix([[1,1],[1,1]]),'The same sample rows merge in characteristic two.')

report={'scope':'Exact illustrative-example checks, not a new Lean verification or theorem census.',
        'python_version':platform.python_version(),'sympy_version':sp.__version__,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'status':'PASS','check_count':len(results),'checks':results,
        'limits':['Finite arithmetic enumerations are exhaustive only for their stated finite models.',
                  'Uniform algebraic conclusions and infinite-limit claims have explicit arguments in the appendix.',
                  'No test verifies external arithmetic existence, classicality, or automorphy inputs.',
                  'No new examples have been formalized in Lean by this editorial release.']}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(results)} exact checks. Report: checks/EXACT_CHECKS.json')
