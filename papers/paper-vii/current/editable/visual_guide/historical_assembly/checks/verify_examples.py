#!/usr/bin/env python3
"""Check the displayed finite and symbolic assertions, with separate false controls.

No numerical sample is promoted into a universal mathematical or Lean proof.
The rational sine bounds use the alternating-series theorem on [0,1]; the checks
validate their stated input conditions, exact arithmetic and displayed bounds.
"""
from __future__ import annotations
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from models import *
records=[];controls=[]

def eq(a,b):
    if isinstance(a,s.MatrixBase) or isinstance(b,s.MatrixBase):
        a,b=M(a),M(b)
        return a.shape==b.shape and all(s.simplify(s.expand_complex(x))==0 for x in a-b)
    return s.simplify(a-b)==0

def check(name,condition,kind='exact finite algebra'):
    ok=bool(condition)
    records.append({'name':name,'kind':kind,'passed':ok})
    if not ok:raise AssertionError(name)

def same(name,a,b,kind='exact finite algebra'):check(name,eq(a,b),kind)
def reject(name,false_statement):
    check('negative control: '+name,not bool(false_statement),'deliberately false assertion rejected')
    controls.append(name)

def main():
    started=time.monotonic();X,Y,Z=paulis();h,cnot,middle,v,rhoBell=bell()
    for name,A in [('X',X),('Y',Y),('Z',Z),('Hadamard',h),('CNOT',cnot)]:
        same(name+' is unitary',A.conjugate().T*A,s.eye(A.rows))
    # Computational grammar and multiplicity orbits.
    addresses=[]
    for j in range(8):
        bits=[(j>>b)&1 for b in [2,1,0]]
        W=kron(*[X**a for a in bits]);addresses.append(W*basis(8,0))
        same('Pauli address '+format(j,'03b'),addresses[-1],basis(8,j))
    same('all addressed vectors are an orthonormal basis',M.hstack(*addresses).T*M.hstack(*addresses),s.eye(8))
    cs=[M([[1,0],[0,0]]),s.eye(2)/s.sqrt(2),M([[1,0,0],[0,1,0]])]
    for i,C in enumerate(cs):
        mats=[]
        for a in range(2):
            for b in range(2):
                E=s.zeros(2);E[a,b]=1;mats.append(M(2*C.cols,1,list(E*C)))
        check('orbit dimension from coefficient matrix '+str(i),M.hstack(*mats).rank()==2*C.rank())
    C1=M([[1,0,0],[0,1,0]]);C2=M([[0,0,1],[0,0,0]])
    check('two seeds span three multiplicity directions',C1.col_join(C2).rank()==3)
    check('minimum two for d=2 m=3',s.ceiling(R(3,2))==2)
    reject('Pauli words prepare a nonbasis plus state',any(eq(a,(basis(8,0)+basis(8,1))/s.sqrt(2)) for a in addresses))
    # Genuine witness: the plus state is not an addressed basis vector.
    plus3=(basis(8,0)+basis(8,1))/s.sqrt(2)
    check('linear span exceeds the finite Pauli word orbit',not any(eq(a,plus3) for a in addresses))
    S,Ps,vs,L=cyclic4();same('shift order four',S**4,s.eye(4));same('cyclic completeness',sum(Ps,s.zeros(4)),s.eye(4))
    for j in range(4):
        same('cyclic character projector '+str(j),Ps[j],outer(vs[j]))
        same('cyclic eigenpacket '+str(j),S*Ps[j],I**j*Ps[j])
        for k in range(4):same(f'cyclic orthogonality {j},{k}',Ps[j]*Ps[k],Ps[j] if j==k else s.zeros(4))
    fine,groups,coarse=parity(3)
    same('three-qubit even projector',coarse[0],(s.eye(8)+kron(Z,Z,Z))/2)
    same('three-qubit odd projector',coarse[1],(s.eye(8)-kron(Z,Z,Z))/2)
    check('parity child addresses',groups==[[0,3,5,6],[1,2,4,7]])
    same('Bell middle amplitude',middle,(basis(4,0)+basis(4,2))/s.sqrt(2))
    same('Bell final amplitude',v,(basis(4,0)+basis(4,3))/s.sqrt(2))
    p2=parity(2)[2]
    pieces=[p2[b]*cnot*p2[a]*kron(h,s.eye(2))*p2[c] for a in range(2) for b in range(2) for c in range(2)]
    same('Bell complete packet path reconstruction',sum(pieces,s.zeros(4)),cnot*kron(h,s.eye(2)))
    paths=[h[1,a]*h[a,0] for a in range(2)]
    same('Hadamard paths cancel',sum(paths),0);same('squares of path terms do not cancel',sum(abs(a)**2 for a in paths),R(1,2))
    reject('classical path probabilities equal coherent output',eq(sum(abs(a)**2 for a in paths),abs(sum(paths))**2))
    projectors=[s.diag(1,0),s.diag(0,1)]
    for a in range(2):
        for c in range(2):
            lhs=sum([(projectors[b]*h*projectors[a]).T*(projectors[b]*h*projectors[c]) for b in range(2)],s.zeros(2))
            same(f'packetwise unitarity {a},{c}',lhs,projectors[a] if a==c else s.zeros(2))
    H,B,HB=symmetry();same('parity Hamiltonian block form',HB,s.diag(M([[R(3,4),1],[1,-R(3,4)]]),X))
    same('parity commutator vanishes',H*kron(Z,Z)-kron(Z,Z)*H,s.zeros(4))
    check('parity Hamiltonian exact eigenvalues',set(H.eigenvals())=={R(5,4),-R(5,4),1,-1})
    for j,p in enumerate(p2):same('invariant symmetry packet '+str(j),H*p,p*H)
    t=s.symbols('t',real=True);U=s.cos(t)*s.eye(2)-I*s.sin(t)*X;P=s.diag(1,0);Q=s.eye(2)-P
    same('two-level unitary propagator',U.conjugate().T*U,s.eye(2),'symbolic trigonometric identity')
    same('leakage probability',((Q*U*P).conjugate().T*(Q*U*P)),s.sin(t)**2*P,'symbolic trigonometric identity')
    same('unit coupling commutator singular values',(X*P-P*X).T*(X*P-P*X),s.eye(2))
    same('pi/6 leakage amplitude squared',s.sin(s.pi/6)**2,R(1,4))
    # Frames, exact range atlas and actual derivative formulas.
    V,Pt,Qt=rotating_projector(t);J=M([[0,-1],[1,0]])
    Heff=-I*V.T*V.diff(t);same('moving-frame connection',Heff,-I*J,'symbolic derivative')
    y=V.T*basis(2,0);same('moving-frame Schroedinger identity',I*y.diff(t),Heff*y,'symbolic derivative')
    same('moving frame has unit omitted-term norm',y.diff(t).T*y.diff(t),M([[1]]),'symbolic derivative')
    C=s.simplify(Pt.diff(t)*Pt+Qt.diff(t)*Qt)
    same('canonical connection equals rotation generator',C,J,'symbolic derivative')
    same('connection is skew adjoint',C.T,-C)
    same('canonical derivative reconstruction',C*Pt-Pt*C,Pt.diff(t),'symbolic derivative')
    same('differentiated projector normal condition',Pt*Pt.diff(t)*Pt,s.zeros(2),'symbolic derivative')
    T=Pt*P+Qt*Q;same('range-atlas intertwiner',T,s.cos(t)*V,'symbolic trigonometric identity')
    same('range-atlas determinant',s.simplify(T.det()),s.cos(t)**2,'symbolic trigonometric identity')
    same('atlas degenerates at a chart boundary',T.subs(t,s.pi/2),s.zeros(2))
    same('projector remains regular at chart boundary',Pt.subs(t,s.pi/2),Q)
    th,ph=s.symbols('theta phi',real=True);PB=bloch(th,ph)
    same('Bloch projector idempotence',PB*PB,PB,'symbolic trigonometric identity')
    same('Bloch projector Hermitian',PB.conjugate().T,PB,'symbolic trigonometric identity')
    cur=s.simplify(-I*s.trace(PB*(PB.diff(th)*PB.diff(ph)-PB.diff(ph)*PB.diff(th))))
    same('Bloch scalar curvature',cur,s.sin(th)/2,'symbolic derivative')
    un=M([s.cos(th/2),s.exp(I*ph)*s.sin(th/2)])
    same('north frame represents the same projector',outer(un),PB,'symbolic trigonometric identity')
    An=s.simplify(-I*(un.conjugate().T*un.diff(ph))[0]);same('north scalar connection',An,(1-s.cos(th))/2,'symbolic derivative')
    same('cap flux at theta pi/3',s.integrate(s.sin(th)/2,(th,0,s.pi/3))*2*s.pi,s.pi/2,'symbolic integral')
    # States, dephasing and channels.
    dc=dephase(rhoBell,parity(2)[0]);dp=dephase(rhoBell,p2)
    same('parity does not dephase the Bell coherence',dp,rhoBell)
    same('computational dephasing loses cross-address coherence',dc,s.diag(R(1,2),0,0,R(1,2)))
    for j in range(4):same('diagonal measurement unchanged '+str(j),s.trace(parity(2)[0][j]*dc),s.trace(parity(2)[0][j]*rhoBell))
    same('Bell projector measurement before dephasing',s.trace(rhoBell*rhoBell),1)
    same('Bell projector measurement after dephasing',s.trace(rhoBell*dc),R(1,2))
    reject('every measurement is invariant under dephasing',eq(s.trace(rhoBell*rhoBell),s.trace(rhoBell*dc)))
    Ks,rho,out=damping();same('Kraus normalization',sum([k.T*k for k in Ks],s.zeros(2)),s.eye(2))
    same('amplitude damping exact output',out,M([[R(17,25),R(2,5)],[R(2,5),R(8,25)]]))
    same('amplitude damping trace',s.trace(out),1);same('amplitude damping determinant',out.det(),R(36,625))
    E=[M(2,2,lambda r,c:int((r,c)==(a,b))) for a in range(2) for b in range(2)]
    Super=M.hstack(*[M(4,1,list(channel(e,Ks))) for e in E]);same('channel superoperator',Super,M([[1,0,0,R(9,25)],[0,R(4,5),0,0],[0,0,R(4,5),0],[0,0,0,R(16,25)]]))
    choi=sum([kron(E[i],channel(E[i],Ks)) for i in range(4)],s.zeros(4));vecs=[M(4,1,[k[r,c] for c in range(2) for r in range(2)]) for k in Ks]
    same('Choi is a Kraus Gram sum',choi,sum([outer(vv) for vv in vecs],s.zeros(4)))
    check('damping Choi spectrum nonnegative',set(choi.eigenvals())=={0,R(9,25),R(41,25)})
    pt=partial_transpose_second(rhoBell);w=(basis(4,1)-basis(4,2))/s.sqrt(2)
    same('partial transpose negative witness',(w.T*pt*w)[0],-R(1,2));reject('positive maps are automatically completely positive',(w.T*pt*w)[0]>=0)
    # Error correction: every compression, syndrome and reconstruction.
    E,V,P,Qs,psi,rho,weights,corrupted,rec,recovered=code()
    same('code isometry',V.T*V,s.eye(2));same('syndrome completeness',sum(Qs,s.zeros(8)),s.eye(8))
    for a in range(4):
        for b in range(4):
            same(f'Knill-Laflamme compression {a},{b}',P*E[a].T*E[b]*P,P if a==b else s.zeros(8))
            same(f'syndrome orthogonality {a},{b}',Qs[a]*Qs[b],Qs[a] if a==b else s.zeros(8))
        same('syndrome probability '+str(a),s.trace(Qs[a]*corrupted),weights[a])
    same('recovery channel normalization',sum([r.T*r for r in rec],s.zeros(8)),s.eye(8))
    same('exact recovery of logical coherence',recovered,rho)
    bad=kron(Z,s.eye(2),s.eye(2));same('phase error compressed to logical Z',V.T*bad*V,Z)
    reject('zero trace compression implies scalar compression',eq(V.T*bad*V,s.zeros(2)))
    # Elimination, spectral domains and memory.
    z=s.symbols('z');H=M([[0,1],[1,2]]);G=(z*s.eye(2)-H).inv()
    same('Feshbach rational identity',G[0,0],(z-2)/(z*z-2*z-1),'rational function identity')
    same('Feshbach at z=3',G[0,0].subs(z,3),R(1,2));same('bare error at z=3',G[0,0].subs(z,3)-R(1,3),R(1,6))
    same('full resolvent remains defined at eliminated pole',(-2*s.eye(2)+H).det(),-1)
    same('continued projected resolvent at z=2',G[0,0].subs(z,2),0)
    reject('eliminated inverse ensures a full resolvent',s.diag(0,1).det()!=0)
    x=s.cos(t);same('quantum memory equation',s.diff(x,t),-s.integrate(s.cos(s.Symbol('u')),(s.Symbol('u'),0,t)),'symbolic integral')
    same('retained semigroup defect at pi/4',s.cos(s.pi/2)-s.cos(s.pi/4)**2,-R(1,2))
    reject('retained propagator is a semigroup',eq(s.cos(s.pi/2),s.cos(s.pi/4)**2))
    # Euclidean positivity, finite spectral diagnostic, dispersion.
    q,r=s.symbols('q r',real=True);T=lambda q:M([[1+q,1-q],[1-q,1+q]])/2
    same('Euclidean multiplicative spectral parameter',T(q)*T(r),T(q*r),'polynomial identity')
    same('Euclidean half-decay transfer',T(R(1,2)),M([[R(3,4),R(1,4)],[R(1,4),R(3,4)]]))
    Tg=Z*T(R(1,2))*Z;same('basis change preserves positive spectrum',Tg.charpoly().as_expr(),T(R(1,2)).charpoly().as_expr())
    reject('operator positivity implies entrywise nonnegativity',Tg[0,1]>=0)
    tau=s.symbols('tau',positive=True);K=(1+s.exp(-2*tau))**2/4;ds=-2*tau*s.diff(K,tau)/K
    same('C4 spectral dimension',s.simplify(ds),8*tau/(s.exp(2*tau)+1),'symbolic derivative')
    same('C4 times C4 doubles diagnostic',s.simplify(-2*tau*s.diff(K*K,tau)/(K*K)),2*ds,'symbolic derivative')
    same('C4 diagnostic at log2/2',s.simplify(ds.subs(tau,s.log(2)/2)),4*s.log(2)/3,'symbolic evaluation')
    for hh in [R(1,4),R(1,8),R(1,16)]:
        row=dispersion_row(hh)
        check('rational dispersion enclosure '+str(hh),0<row['error_lower']<=row['error_upper']<row['bound'],'rational Taylor enclosure')
    rows=[dispersion_row(hh) for hh in [R(1,4),R(1,8),R(1,16)]]
    for a,b in zip(rows,rows[1:]):
        check('second-order enclosure ratio '+str(a['h']),R(399,100)<a['error_lower']/b['error_upper'] and a['error_upper']/b['error_lower']<4,'rational Taylor enclosure')
    C1,C2,P,A=constraints();same('constraint 1 kills physical subspace',C1*P,s.zeros(3));same('constraint 2 kills physical subspace',C2*P,s.zeros(3))
    same('compressed commutator vanishes',P*A*P,s.zeros(3));check('full commutator is nonzero',A!=s.zeros(3))
    reject('compressed zero certifies unprojected closure',A==s.zeros(3))
    # End-to-end four-site transfer.
    S,Ps,vs,L=cyclic4();same('four-site Laplacian spectral reconstruction',sum([v*p for v,p in zip([0,2,4,2],Ps)],s.zeros(4)),L)
    Ut=sum([a*p for a,p in zip([1,-1,1,-1],Ps)],s.zeros(4));same('opposite-site perfect transfer',Ut,S**2)
    Uq=sum([a*p for a,p in zip([1,-I,-1,-I],Ps)],s.zeros(4));v=Uq*basis(4,0)
    same('quarter-time amplitudes',v,M([-I/2,R(1,2),I/2,R(1,2)]))
    same('quarter-time uniform probabilities',M([s.simplify(abs(a)**2) for a in v]),M([R(1,4)]*4))
    init=outer(basis(4,0));dm=dephase(init,Ps);same('complete momentum dephasing',dm,s.eye(4)/4)
    eta=s.symbols('eta',real=True);out=Ut*((1-eta)*init+eta*dm)*Ut.conjugate().T
    same('dephasing reduces perfect transfer',out[2,2],1-3*eta/4,'polynomial identity')
    check('Hamiltonian orbit has three independent directions',M.hstack(*[L**j*basis(4,0) for j in range(4)]).rank()==3)
    check('shift orbit has four independent directions',M.hstack(*[S**j*basis(4,0) for j in range(4)]).rank()==4)
    result={'status':'PASS','checks_passed':len(records),'invalid_controls_rejected':controls,'seconds':time.monotonic()-started,
     'scope':'Finite examples, symbolic identities, and rational Taylor enclosures. No Lean, no universal continuum claim.',
     'checks':records,'data':exact_data()}
    path=Path(__file__).resolve().parent/'EXACT_CHECKS.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(records)} checks; {len(controls)} invalid controls rejected.')
if __name__=='__main__':main()
