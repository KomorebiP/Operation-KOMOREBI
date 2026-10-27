#!/usr/bin/env python3
"""Reproduce exact worked examples. Finite assertions, not a Lean verification."""
from pathlib import Path
import json,sys,platform
from datetime import datetime,timezone
from itertools import product
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import models as M
import sympy as s
Q=M.Q
checks=[];controls=[]
def check(name,condition):
    if not bool(condition):raise RuntimeError('Exact check failed: '+name)
    checks.append(name)
def reject(name,condition):
    if bool(condition):raise RuntimeError('False control unexpectedly accepted: '+name)
    controls.append(name)
def main():
    x=M.SIGNAL
    check('signal decomposition',M.eq(x,M.SMOOTH+M.JUMP))
    check('finite signal length',len(x)==16)
    for N in [1,2,3,4,6,8]:
        sample={n:Q((n*n+2*n)%11-5,4) for n in range(-17,18)}
        ch=M.analyze_dict(sample,N)
        check(f'signed Euclidean addresses N={N}',all(N*(n//N)+n%N==n and 0<=n%N<N for n in range(-40,41)))
        check(f'analysis synthesis N={N}',M.synthesize_dict(ch)=={n:a for n,a in sample.items() if a!=0})
        check(f'energy reindexing N={N}',M.eq(M.energy(sample.values()),sum(M.energy(c.values()) for c in ch)))
        check(f'FIR signed taps N={N}',M.polyphase_convolve({-2:Q(1,2),0:Q(2),3:-1},sample,N)==M.convolve({-2:Q(1,2),0:Q(2),3:-1},sample))
    for N,K in [(1,4),(2,4),(2,6),(3,6),(4,12)]:
        check(f'refinement {N}|{K}',all(int(n%N==r)==sum(int(n%K==j) for j in range(K) if j%N==r) for n in range(-24,25) for r in range(N)))
    check('two-phase FIR matrix',M.eq(M.fir_polyphase_matrix(M.FIR,2),M.H))
    check('FIR polynomial in sample shift',M.eq(M.H,s.Matrix([[1-M.D,2*M.D+M.D**2],[2+M.D,1-M.D]])))
    check('sample delay squared equals channel delay',M.eq(M.J**2,M.D*s.eye(2)))
    for delay in [-5,-1,0,1,2,5]:
        check(f'original-sample delay routes {delay}',all(2*(n+(k-delay)//2)+(k-delay)%2==2*n+k-delay for n in range(-8,9) for k in range(2)))
    E=s.Matrix([[1,M.D],[0,1]]);R=s.Matrix([[1,-M.D],[0,1]])
    check('lifting polynomial bank left inverse',M.eq(R*E,s.eye(2)))
    check('lifting polynomial bank right inverse',M.eq(E*R,s.eye(2)))
    reject('one transform value proves perfect reconstruction',M.eq(s.diag(M.D,1),s.eye(2)))
    check('misleading one-frequency test really passes',M.eq(s.diag(M.D,1).subs(M.D,1),s.eye(2)))
    check('normalized Haar inverse',M.eq(M.H2.T*M.H2,s.eye(2)))
    a=M.one_level(16,0)*x;d=M.one_level(16,1)*x
    check('Haar energy',M.eq(M.energy(a)+M.energy(d),M.energy(x)))
    check('Haar synthesis',M.eq(M.one_level(16,0).T*a+M.one_level(16,1).T*d,x))
    check('complex Haar energy',M.eq(M.energy(M.H2*s.Matrix([1+2*s.I,3-s.I])),M.energy([1+2*s.I,3-s.I])))
    check('predict update determinant',M.LIFT.det()==1)
    check('predict update inverse',M.eq(M.LIFT.inv(),s.Matrix([[1,-Q(1,2)],[1,Q(1,2)]])))
    check('predict update worked pair',M.eq(M.LIFT*s.Matrix([2,6]),s.Matrix([4,4])))
    reject('determinant one implies energy preservation',M.eq(M.LIFT.T*M.LIFT,s.eye(2)))
    for depth in range(4):
        W=s.Matrix.vstack(*(M.packet(16,a) for a in M.addresses(depth)))
        check(f'packet depth {depth} unitary',M.eq(W.T*W,s.eye(16)))
        check(f'packet depth {depth} energy',M.eq(M.energy(W*x),M.energy(x)))
    for k in [0,1,2,4,8,12,16]:
        _,y,tail=M.best_coefficients(k)
        check(f'sparse squared error equals coefficient tail k={k}',M.eq(M.energy(x-y),tail))
    cuts=M.prunings();check('depth-three pruning census',len(cuts)==26)
    for index,cut in enumerate(cuts):
        check(f'complete pruning {index:02}',M.complete(cut))
        P=sum((M.packet_projector(16,a) for a in cut),s.zeros(16))
        check(f'actual mixed-depth synthesis {index:02}',M.eq(P,s.eye(16)))
    reject('overlapping nodes form a complete pruning',M.complete(('0','00','1')))
    reject('missing terminal branch forms a complete pruning',M.complete(('00','01','10')))
    val,cut=M.optimum();ranked=M.ranked_prunings()
    check('DP equals exhaustive minimum',val==ranked[0][0]==9)
    check('unique mixed-depth optimum',cut==('00','01','100','101','11') and ranked[1][0]==10)
    check('attained positive gap',ranked[1][0]-ranked[0][0]==1)
    check('exact perturbation envelope',M.envelope()==max(sum(Q(1,32) for a in c) for c in cuts)==Q(1,4))
    check('strict margin certificate',2*M.envelope()<1)
    for offset in range(5):
        costs={a:Q(c)+Q((-1)**(i+offset),32) for i,(a,c) in enumerate(M.COSTS.items())}
        check(f'bounded node perturbation preserves selector {offset}',M.optimum(costs=costs)[1]==cut)
    tie={a:1 for a in ['','0','1']};tie['']=2
    check('stop on ties convention',M.optimum(depth=1,costs=tie)==(2,('',)))
    check('singleton tree selector',M.optimum(depth=0,costs={'':7})==(7,('',)))
    reject('nonstrict gap universally ensures a unique selector',9+Q(1,2)<10-Q(1,2))
    q=M.smooth_periodic
    check('known packet residual identity',M.eq(x-(q(M.SMOOTH)+M.JUMP),M.SMOOTH-q(M.SMOOTH)))
    check('global smoothing adds jump leakage',M.eq(x-q(x),(M.SMOOTH-q(M.SMOOTH))+(M.JUMP-q(M.JUMP))))
    check('jump leakage is nonzero',M.energy(M.JUMP-q(M.JUMP))>0)
    # Fourier pulse endpoints use exact trigonometric expressions, not plot samples.
    for cutoff in [3,5,15]:
        coeff=[s.sin(s.pi*n/2)/n for n in range(1,cutoff+1)]
        check(f'Fourier pulse midpoint at jump cutoff={cutoff}',s.simplify(Q(1,2)+2/s.pi*sum(coeff[n-1]*s.cos(s.pi*n/2) for n in range(1,cutoff+1)))==Q(1,2))
    delta=Q(1,16)
    check('shifted-interval symmetric difference',2*delta==Q(1,8))
    check('shifted-interval L1',3*2*delta==Q(3,8))
    check('shifted-interval squared L2',9*2*delta==Q(9,8))
    A=set(range(6,12));B=set(range(7,13));j=s.Matrix([3*int(i in A) for i in range(16)]);jh=s.Matrix([Q(5,2)*int(i in B) for i in range(16)])
    check('mask census',(len(A),len(A&B),len(A^B))==(6,5,2))
    check('jump error L1 attains bound',sum(abs(v) for v in j-jh)==abs(3-Q(5,2))*len(A)+Q(5,2)*len(A^B)==8)
    check('jump error squared L2',M.energy(j-jh)==Q(33,2))
    check('jump error L2 bound',s.sqrt(Q(33,2))<=s.sqrt(6)/2+5*s.sqrt(2)/2)
    check('jump error supremum',max(abs(v) for v in j-jh)==3)
    ca,cb=M.circle_masks()
    check('2D exact mask census',(len(ca),len(cb),len(ca^cb))==(21,21,10))
    check('2D mask translated inside display',all(0<=i<8 and 0<=j<8 for i,j in cb))
    check('2D indicator squared norm',sum((int((i,j) in ca)-int((i,j) in cb))**2 for i in range(8) for j in range(8))==len(ca^cb))
    # Two exact noisy explanations of one boundary observation.
    u=s.Matrix([0,0,3,3]);v=s.Matrix([0,3,3,3]);obs=(u+v)/2
    check('two different masks have same permitted observation',u!=v and max(abs(z) for z in obs-u)==max(abs(z) for z in obs-v)==Q(3,2))
    reject('bounded noise always permits unique boundary recovery',u==v)
    f=1+2*M.t+3*M.t**2;g=2+M.t**2
    for k in range(3):
        check(f'Cauchy residue convolution k={k}',M.eq(M.masked_polynomial(f*g,3,k),sum(M.masked_polynomial(f,3,i)*M.masked_polynomial(g,3,j) for i in range(3) for j in range(3) if (i+j)%3==k)))
    for k in range(3):check(f'zero power convention k={k}',M.masked_polynomial(1,3,k)==int(k==0))
    check('pointwise masks do not mix phases',all((x[n] if n%2==0 else 0)*(x[n] if n%2==1 else 0)==0 for n in range(16)))
    F=s.Matrix([x[n]+x[n]*x[(n-1)%16]/2 for n in range(16)]);e=x[0::2];o=x[1::2]
    check('nonlinear even output',all(M.eq(F[2*n],e[n]+e[n]*o[(n-1)%8]/2) for n in range(8)))
    check('nonlinear odd output',all(M.eq(F[2*n+1],o[n]+o[n]*e[n]/2) for n in range(8)))
    check('nonlinear printed example',F[2]==Q(9,16) and F[3]==Q(5,16))
    for phase in [1,s.I,-1,-s.I]:
        ga=s.sympify(phase)/2;z=M.impedance(ga)
        check(f'Cayley exact inverse {phase}',M.eq(M.gamma(z),ga))
        check(f'projective action determinant {phase}',M.eq(M.action(phase).det(),phase))
    check('Cayley quarter orbit coordinates',all(M.eq(M.impedance(g),z) for g,z in zip([Q(1,2),s.I/2,-Q(1,2),-s.I/2],[3,Q(3,5)+Q(4,5)*s.I,Q(1,3),Q(3,5)-Q(4,5)*s.I])))
    r0,y0=s.symbols('r0 y0',real=True)
    check('Cayley constant mismatch circle equation',M.eq(4*((r0-1)**2+y0**2)-((r0+1)**2+y0**2),3*((r0-Q(5,3))**2+y0**2-Q(16,9))))
    check('projective composition symbolic',M.eq(M.action(M.w)*M.action(M.v),M.action(M.w*M.v)))
    pairs=[s.Matrix([0,1]),s.Matrix([-s.I,1]),s.Matrix([1,0]),s.Matrix([s.I,1])]
    for k in range(4):check(f'pole-safe quarter step {k}',M.homogeneous_equal(M.action(s.I)*pairs[k],pairs[(k+1)%4]))
    check('half-turn swaps zero and infinity',M.homogeneous_equal(M.action(-1)*pairs[0],pairs[2]))
    check('CRT 4 by 3 labels',len({(i%4,i%3) for i in range(12)})==12)
    check('CRT projector identity',all(int(n%12==k)==int(n%4==k%4)*int(n%3==k%3) for n in range(-30,31) for k in range(12)))
    for g,expected in [(Q(1,2),8),(Q(9,10),200),(Q(99,100),20000)]:
        check(f'Cayley derivative at {g}',2/(1-g)**2==expected)
    check('finite Cayley error differs from linear estimate',M.impedance(Q(91,100))-M.impedance(Q(9,10))==Q(20,9))
    reject('derivative is exact finite increment',Q(20,9)==2)
    z,h=s.symbols('z h')
    check('Cayley finite increment identity',M.eq(M.impedance(z+h)-M.impedance(z),2*h/((1-z-h)*(1-z))))
    report={'status':'PASS','created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Exact finite illustrative examples; no new Lean proofs or universal recovery claim.','checks_passed':len(checks),'checks':checks,'invalid_controls_rejected':controls,'depth_three_prunings':26,'optimal_pruning':list(cut),'optimal_cost':9,'gap':1,'envelope':'1/4','signal_energy':str(M.energy(x)),'haar_energies':[str(M.energy(a)),str(M.energy(d))],'two_dimensional_mask_sizes':[len(ca),len(cb),len(ca^cb)],'python':platform.python_version(),'sympy':s.__version__}
    p=Path(__file__).resolve().parent/'EXACT_CHECKS.json';p.write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(checks)} exact checks; {len(controls)} false controls rejected')
if __name__=='__main__':main()
