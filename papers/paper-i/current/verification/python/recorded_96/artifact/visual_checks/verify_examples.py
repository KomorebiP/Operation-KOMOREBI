#!/usr/bin/env python3
"""Exact checks of the finite visual examples. Not a proof of new general theorems."""
from __future__ import annotations
import hashlib,json,platform,sys
from datetime import datetime,timezone
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'visual_model_sources'))
from models import data,unit,matrix_unit,orbit,krylov,poly_matrix,path,cycle,serial
D=data(); results=[]
def check(name,condition,scope='exact displayed finite model'):
    if not bool(condition):
        raise AssertionError(name)
    results.append({'name':name,'status':'PASS','scope':scope})
N,s,Q=D['N'],D['s'],D['Q']
check('Repeated chains: nilpotence index three',N**3==sp.zeros(6) and N**2!=sp.zeros(6))
check('One linked seed: rank profile 1,2,3,3,3,3',
      [krylov(N,[s],r).rank() for r in range(1,7)]==[1,2,3,3,3,3])
check('Two independent chain heads span six dimensions',krylov(N,[unit(6,0),unit(6,3)]).rank()==6)
check('Same mixed seed becomes cyclic when packet projections are admitted',orbit([N,D['Pe'],D['Pf']],[s],6)[0].cols==6)
check('Packet projectors satisfy the complete idempotent identities',
      D['Pe']**2==D['Pe'] and D['Pf']**2==D['Pf'] and D['Pe']*D['Pf']==sp.zeros(6) and D['Pe']+D['Pf']==sp.eye(6))
check('Scalar quotient is surjective and kills N',Q.rank()==2 and Q*N==sp.zeros(2,6))
for coeffs in [(1,),(0,1),(2,-3,5,7),(0,0,0,1)]:
    p=sum(c*D['t']**i for i,c in enumerate(coeffs))
    check('Scalar quotient polynomial sample '+str(coeffs),Q*poly_matrix(p,N,D['t'])==coeffs[0]*Q)
check('Scalar grammar orbit of nonzero seed has dimension one',orbit([sp.eye(6)],[s],6)[0].cols==1)
full=[matrix_unit(6,i,j) for i in range(6) for j in range(6)]
check('Full matrix grammar makes the same seed cyclic',orbit(full,[s],6)[0].cols==6)
check('Empty seed family produces zero subspace',orbit([N],[],6)[0].cols==0)
# The seed annihilator is a left ideal, not necessarily a two-sided ideal.
e1=unit(2,0); c=matrix_unit(2,0,1); b=matrix_unit(2,1,0)
check('Left annihilator example: c annihilates e1',c*e1==sp.zeros(2,1))
check('Right multiplication need not preserve that annihilator',(c*b)*e1==e1)
check('Every matrix-unit left multiple of c still annihilates e1',all(matrix_unit(2,i,j)*c*e1==sp.zeros(2,1) for i in range(2) for j in range(2)))
# Typed U/V model, with the vertex projectors included in its path algebra.
check('Typed relation BA is identity on U',D['B']*D['A']==sp.eye(2))
check('AB is projection onto the image, not identity on V',D['A']*D['B']==sp.diag(1,1,0))
check('A seed at U reaches four of five directions',orbit(D['typed_ops'],[unit(5,0)],5)[0].cols==4)
check('Two displayed pure seeds fill U direct sum V',orbit(D['typed_ops'],[unit(5,0),unit(5,4)],5)[0].cols==5)
check('One mixed seed is cyclic for this typed path algebra',orbit(D['typed_ops'],[unit(5,0)+unit(5,4)],5)[0].cols==5)
# Oblique packets and conjugacy.
p,q,x=D['P'],D['Qob'],D['x']
check('Oblique exact packet identities',p*p==p and q*q==q and p*q==q*p==sp.zeros(2) and p+q==sp.eye(2))
check('Oblique components reconstruct x',p*x==sp.Matrix([1,0]) and q*x==sp.Matrix([2,2]) and p*x+q*x==x)
check('Oblique splitting does not satisfy Parseval',(p*x).dot(p*x)+(q*x).dot(q*x)==9 and x.dot(x)==13)
check('Oblique projectors are not self-adjoint',p.T!=p and q.T!=q)
a=sp.diag(1,2);u=D['U'];moved=u*a*u.inv()
check('Transported diagonal operator has a raw off-diagonal entry',moved==sp.Matrix([[1,1],[0,2]]))
check('Transported packet off-diagonal blocks remain zero',p*moved*q==q*moved*p==sp.zeros(2))
check('All four conjugacy block identities',all(
    (u*sp.diag(*(int(k==i) for k in range(2)))*u.inv())*moved*(u*sp.diag(*(int(k==j) for k in range(2)))*u.inv())
    ==u*(sp.diag(*(int(k==i) for k in range(2)))*a*sp.diag(*(int(k==j) for k in range(2))))*u.inv()
    for i in range(2) for j in range(2)))
proj=sp.Matrix.hstack(sp.eye(3),sp.zeros(3))
check('Surjective intertwiner discarding the second chain',proj*N==D['J']*proj and proj.rank()==3)
# Transfer blocks, paths, cancellation, and support closure.
t=D['T']; ps=[sp.diag(*(int(j==i) for j in range(3))) for i in range(3)]
check('All transfer blocks reconstruct T',sum((b*t*a for a in ps for b in ps),sp.zeros(3))==t)
check('All nine block-composition identities',all(ps[i]*t*t*ps[j]==sum((ps[i]*t*ps[k]*t*ps[j] for k in range(3)),sp.zeros(3)) for i in range(3) for j in range(3)))
check('Displayed transfer square',t*t==sp.Matrix([[1,4,6],[12,1,6],[8,8,1]]))
check('Orthogonal coordinate packets obey adjoint reversal',all((ps[i]*t*ps[j]).T==ps[j]*t.T*ps[i] for i in range(3) for j in range(3)))
c=D['D']
check('Two nonzero packet routes cancel in D squared',c**2==sp.zeros(4) and c[3,1]*c[1,0]==1 and c[3,2]*c[2,0]==-1)
check('Reachable four-vertex example has a two-dimensional orbit',krylov(c,[unit(4,0)]).rank()==2)
check('Nontransitive support counterexample',matrix_unit(3,2,1)*matrix_unit(3,1,0)==matrix_unit(3,2,0))
lower=[matrix_unit(3,i,j) for i in range(3) for j in range(3) if i>=j]
check('Lower-triangular matrix-unit support is multiplicatively closed',all(all((a*b)[i,j]==0 for i in range(3) for j in range(i+1,3)) for a in lower for b in lower))
# Independent vs shared scalar action.
v=sp.Matrix([1,1])
check('Shared scalar action cannot separate (1,1)',orbit([sp.eye(2)],[v],2)[0].cols==1)
check('Independent diagonal action separates (1,1)',orbit([sp.diag(1,0),sp.diag(0,1)],[v],2)[0].cols==2)
check('Two distinct eigenvalue interpolation projectors',2*sp.eye(2)-sp.diag(1,2)==sp.diag(1,0) and sp.diag(1,2)-sp.eye(2)==sp.diag(0,1))
# Semisimple row-space budget.
vs=D['Vs'];w=D['W']; aa=D['As']
check('Three row-budget seeds reconstruct the displayed arbitrary test matrix',sum((a*v for a,v in zip(aa,vs)),sp.zeros(2,5))==w)
collected=[];dims=[]
for v in vs:
    collected.extend([sp.Matrix(list(matrix_unit(2,i,j)*v)) for i in range(2) for j in range(2)])
    dims.append(sp.Matrix.hstack(*collected).rank())
check('Semisimple orbit dimensions 4,8,10',dims==[4,8,10])
check('Combined seed rows have full multiplicity rank',sp.Matrix.vstack(*vs).rank()==5)
check('Displayed product-algebra maximum is three',max(sp.ceiling(sp.Rational(5,2)),sp.ceiling(sp.Rational(4,3)))==3)
# Actual CRT extractor and a one-seed certificate for distinct primary labels.
a=D['Tsep'];p2=D['p2'];p0=D['p0'];sym=D['t']
e=poly_matrix(p2,a,sym)
check('CRT projector polynomial at distinct primary blocks',e==D['Pf'] and poly_matrix(p0,a,sym)==D['Pe'])
check('Exact confluent congruences for CRT polynomial',sp.rem(p2,sym**3,sym)==0 and sp.rem(p2-1,(sym-2)**3,sym)==0)
check('Extractor recovers each chain head',e*s==unit(6,3) and (sp.eye(6)-e)*s==unit(6,0))
check('Distinct-primary mixed seed has full Krylov rank',krylov(a,[s]).det()!=0)
# All-size statements are proved in the paper; this checks named finite ranges only.
for n in range(1,13):
    k=krylov(path(n),[unit(n,0)])
    check(f'Path P{n}: unit upper triangular Krylov certificate',
          k.det()==1 and all(k[i,j]==0 for i in range(n) for j in range(i)) and all(k[i,i]==1 for i in range(n)),
          'exact finite case; all-size theorem remains the cited manuscript result')
a=D['cycle6']; cq=D['cycle_Q']
check('Cycle C6: displayed scalar quotient has rank two',cq.rank()==2 and cq*a==cq)
check('Cycle C6: one vertex spans four directions',krylov(a,[unit(6,0)]).rank()==4)
check('Cycle C6: adjacent vertices span six directions',krylov(a,[unit(6,0),unit(6,1)]).rank()==6)
check('Cycle C6: exact spectrum with multiplicities',a.charpoly().as_expr().factor()==sp.Symbol('lambda')**0*(sp.Symbol('lambda')-2)*(sp.Symbol('lambda')+2)*(sp.Symbol('lambda')-1)**2*(sp.Symbol('lambda')+1)**2)
for n in range(3,13):
    check(f'Cycle C{n}: two adjacent seeds generate',krylov(cycle(n),[unit(n,0),unit(n,1)]).rank()==n,'exact finite case n=3..12; not an all-size proof')
# Quotient-coordinate algebra.
x,y=sp.symbols('x y');r=x**3-x
f=x*x+y;g=x-y
check('Affine coordinate product reduces to x+(x-x squared)y',sp.rem(sp.expand(f*g),y*y-r,y)==x+(x-x*x)*y)
my=sp.Matrix([[0,r],[1,0]])
check('Coordinate multiplication matrix squares to its relation',my*my==r*sp.eye(2))
a0,a1,b0,b1=sp.symbols('a0 a1 b0 b1')
check('Symbolic two-packet product identity',sp.expand(sp.rem((a0+y*a1)*(b0+y*b1),y*y-r,y)-(a0*b0+r*a1*b1+y*(a0*b1+a1*b0)))==0)
for k in range(6):
    check(f'Monomial y^{k}: unique displayed degree-under-two remainder',sp.expand(sp.rem(y**k,y*y-r,y)-y**(k%2)*r**(k//2))==0)
# Shift truncations: rational identities, not floating approximations.
for n in [0,1,3,5,8]:
    mass=1+2*sum((sp.Rational(1,4)**k for k in range(1,n+1)),sp.S.Zero)
    tail=sp.Rational(2,3)*sp.Rational(1,4)**n
    check(f'Bilateral geometric sequence N={n}: retained norm plus exact tail',mass+tail==sp.Rational(5,3),'rational identity obtained from the geometric-series formula')
seq={n:sp.Rational(1,2)**abs(n) for n in range(-7,8)}
shift=lambda n:seq.get(n-1,0)
check('Three residue-packet carry formulas on complete displayed support',all(
    shift(3*k+j)==seq.get(3*k+(j-1),0) if j>0 else shift(3*k)==seq.get(3*(k-1)+2,0)
    for k in range(-4,5) for j in range(3)))
# Tensor expansion and exact hull algorithm.
x=sp.Matrix([2,3]);y=sp.Matrix([5,7]);ten=sp.kronecker_product(x,y)
check('Tensor example has four, not two, coefficient terms',ten==sp.Matrix([10,14,15,21]))
check('Diagonal-only tensor pairing misses the cross directions',sp.Matrix.hstack(sp.kronecker_product(unit(2,0),unit(2,0)),sp.kronecker_product(unit(2,1),unit(2,1))).rank()==2)
check('Four basis tensor seeds span the scalar tensor module',sp.Matrix.hstack(*(sp.kronecker_product(unit(2,i),unit(2,j)) for i in range(2) for j in range(2))).rank()==4)
for label,ops,seeds,n in [('linked',[N],[s],6),('split',[N,D['Pe']],[s],6),('typed',D['typed_ops'],[unit(5,0)],5),('cancel',[c],[unit(4,0)],4)]:
    b,h=orbit(ops,seeds,n)
    check(f'Exact hull algorithm: {label} stable basis is invariant',all(sp.Matrix.hstack(b,o*b).rank()==b.cols for o in ops))
report={'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Exact finite/symbolic appendix calculations only. Not new Lean certification.',
        'check_count':len(results),'checks':results,'python':platform.python_version(),
        'sympy':sp.__version__,'arithmetic':'integers, rational numbers, and symbolic polynomials',
        'randomness':'none','rank_tolerance':'none; exact rank',
        'models_sha256':hashlib.sha256((ROOT/'visual_model_sources/models.py').read_bytes()).hexdigest(),
        'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'data':{'linked_rank_profile':[krylov(N,[s],i).rank() for i in range(1,7)],
                'path5_krylov':serial(krylov(D['path5'],[unit(5,0)])),
                'distinct_primary_krylov_determinant':str(krylov(D['Tsep'],[s]).det()),
                'semisimple_hull_dimensions':dims,'crt_p2':str(D['p2'])}}
(ROOT/'visual_checks/EXACT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(results)} exact checks; no Lean build performed.')
