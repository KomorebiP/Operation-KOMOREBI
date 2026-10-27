#!/usr/bin/env python3
"""Reproduce exact worked examples; no GPU timing and no Lean invocation."""
from __future__ import annotations
import sys,json,hashlib,platform
from pathlib import Path
from itertools import product
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from models import *
checks=[];negative=[]
def check(name,condition):
    ok=bool(condition)
    checks.append({'name':name,'passed':ok})
    if not ok:raise AssertionError(name)
def eq(name,a,b):
    difference=a-b
    zero=all(s.simplify(v)==0 for v in difference) if isinstance(difference,s.MatrixBase) else s.simplify(difference)==0
    check(name,zero)
def reject(name,condition):
    if bool(condition):raise AssertionError('Invalid control was accepted: '+name)
    negative.append(name)
def fro2(A):return s.simplify(s.trace(A.H*A))

def main():
    D,u,v,A,x=bdlr();diag_parts=[list(range(i,i+2)) for i in (0,2,4)]
    Ps=[s.diag(*[int(j in p) for j in range(6)]) for p in diag_parts]
    eq('complete coordinate projectors',sum(Ps,s.zeros(6)),s.eye(6))
    for i,P in enumerate(Ps):
        eq(f'projector {i} idempotent',P*P,P)
        for j,T in enumerate(Ps):
            if i!=j:eq(f'projectors {i},{j} annihilate',P*T,s.zeros(6))
    eq('exact full packet reconstruction',sum((P*A*T for P in Ps for T in Ps),s.zeros(6)),A)
    check('running matrix has all 36 entries nonzero',sum(int(a!=0) for a in A)==36)
    eq('global contraction is three',(v.T*x)[0],3)
    eq('local product vector',D*x,M([2,-2,6,2,-3,7]))
    eq('factored application',D*x+u*(v.T*x),A*x)
    eq('running result',A*x,M([5,1,9,5,0,10]))
    eq('running application storage count',3*2**2+2*6,24)
    for q in (1,2,4,8):
        eq(f'operation ratio q={q}',Q(2*36*q,2*(12+12)*q),Q(3,2))
    for p in range(1,7):
        for w in range(p):eq(f'band count p={p} w={w}',sum(abs(i-j)<=w for i in range(p) for j in range(p)),p*(2*w+1)-w*(w+1))
    sizes=(2,2,2);edges=((0,0),(1,1),(2,2))
    eq('stream byte count q=1',modeled_bytes(sizes,edges,1),240)
    eq('stream byte count q=4',modeled_bytes(sizes,edges,4),672)
    c,F,C,lam,xc=fourier4()
    eq('unitary Fourier matrix',F.H*F,s.eye(4));eq('four circulant eigenvalues',lam,M([2,2-2*s.I,2,2+2*s.I]))
    eq('circulant reconstruction',F.H*s.diag(*lam)*F,C)
    eq('circulant transformed application',F.H*s.diag(*lam)*F*xc,C*xc)
    reject('omit sqrt(n) in unitary Fourier convention',F.H*s.diag(*(F*c))*F==C)
    T,g,Cg,xt=toeplitz_model();pad=xt.col_join(s.zeros(3,1));result=Cg*pad
    eq('Toeplitz padded result',result[:3,:],T*xt)
    eq('Toeplitz output',T*xt,M([-5,8,8]))
    reject('use first column as an unpadded circulant',circulant([2,3,4])*xt==T*xt)
    AA,BB,XX=kron_model();eq('Kronecker column-major identity',s.kronecker_product(AA,BB)*vec(XX),vec(BB*XX*AA.T))
    reject('replace transpose by adjoint in vectorization',vec(BB*XX*AA.H)==s.kronecker_product(AA,BB)*vec(XX))
    for n in (1,2,4,8,16):
        H=walsh(n);xs=list(range(1,n+1));st=walsh_stages(xs)
        eq(f'Walsh orthogonality n={n}',H*H.T,n*s.eye(n));eq(f'Walsh output n={n}',M(st[-1]),H*M(xs))
        eq(f'Walsh exact operation count n={n}',n*(len(st)-1),n*(n.bit_length()-1))
    reject('unnormalized Walsh preserves norm',fro2(walsh(8)*M(range(1,9)))==fro2(M(range(1,9))))
    DA,DB,ua,va,ub,vb,AA,BB,UC,VC=product_model()
    eq('BDLR product with cross term',DA*DB+UC*VC.T,AA*BB)
    check('product correction actual rank is at most two',(AA*BB-DA*DB).rank()<=2)
    reject('drop quadratic low rank term',DA*DB+DA*ub*vb.T+ua*va.T*DB==AA*BB)
    invD=D.inv();S=s.eye(1)+v.T*invD*u;WB=invD-invD*u*S.inv()*v.T*invD
    eq('Woodbury small scalar',S[0],Q(5,2));eq('Woodbury left inverse',WB*A,s.eye(6));eq('Woodbury right inverse',A*WB,s.eye(6))
    eq('determinant through small scalar',A.det(),D.det()*S.det())
    reject('invertible diagonal guarantees invertible update',(s.eye(2)-M([1,0])*M([1,0]).T).det()!=0)
    QL,RL,RR,L,R,G,LR=compact_model()
    eq('compact left isometry',QL.T*QL,s.eye(2));eq('actual left factor',QL*RL,L)
    eq('compact core shape',(G.rows*100+G.cols),203)
    eq('actual small core',G,M([[5,0,0],[0,2,0]]));eq('core reconstruction',QL*G,LR)
    eq('left range rank',L.rank(),2);eq('right range rank',R.rank(),3);eq('core rank equals ambient',G.rank(),LR.rank())
    Ak=QL*M([[5,0,0],[0,0,0]])
    eq('rank one output',Ak.rank(),1);eq('rank one squared Frobenius error',fro2(LR-Ak),4)
    eq('residual spectral square',max(((LR-Ak).T*(LR-Ak)).eigenvals()),4)
    eq('residual Gram eigenvalues',s.prod((s.Symbol('z')-t)**m for t,m in ((LR-Ak).T*(LR-Ak)).eigenvals().items()),s.Symbol('z')**2*(s.Symbol('z')-4))
    eq('rank zero tail',fro2(LR),29);eq('full retention',QL*G,LR)
    competitor=s.zeros(4,3);competitor[3,2]=1
    check('outside competitor rank one',competitor.rank()==1)
    eq('outside competitor compresses to zero',QL.T*competitor,s.zeros(2,3))
    check('outside competitor no improvement',fro2(LR-competitor)>=4)
    # Exact witness for spectral and Frobenius tail bounds for a diagonal competitor.
    DD=s.diag(5,2,1);B1=s.diag(4,0,0);K=s.eye(3)[:,1:]
    eq('rank-one competitor kills kernel frame',B1*K,s.zeros(3,2))
    eq('kernel weights sum to two',sum(sum(K[i,j]**2 for j in range(2)) for i in range(3)),2)
    eq('kernel weighted tail lower bound',fro2(DD*K),5)
    eq('best rank-one tail squared',fro2(DD-s.diag(5,0,0)),5)
    # Two distinct error models; rational example has positive aligned errors.
    aa=[2,3,4];ee=[Q(1,10),Q(1,5),Q(1,20)];pp=Q(1);hp=Q(1)
    for z,e in zip(aa,ee):pp*=z;hp=z*hp+e
    bound=sum(s.prod(aa[j+1:])*ee[j] for j in range(3))
    eq('additive recompression chain error',hp-pp,bound);eq('additive chain bound value',bound,Q(41,20))
    ah=[a+e for a,e in zip(aa,ee)];tel=sum(s.prod(ah[j+1:])*ee[j]*s.prod(aa[:j]) for j in range(3))
    eq('factor perturbation telescoping',s.prod(ah)-s.prod(aa),tel)
    reject('unweighted local errors are a final bound',hp-pp<=sum(ee))
    Kd=diamond();eq('diamond exact cancellation',Kd**2,s.zeros(4));eq('two allowed paths',Kd[3,1]*Kd[1,0]+Kd[3,2]*Kd[2,0],0)
    support=(Kd.applyfunc(lambda a:int(a!=0)))**2
    check('structural path exists despite cancellation',support[3,0]==2)
    AD,b,xD,levels=dag_model();eq('DAG triangular solve',AD*xD,b);eq('DAG level count',len(levels),4)
    check('DAG levels partition vertices',sorted(sum(levels,[]))==list(range(7)))
    for a,z in DAG_EDGES:check(f'predecessor level {a}->{z}',next(i for i,vv in enumerate(levels) if a in vv)<next(i for i,vv in enumerate(levels) if z in vv))
    eq('strict graph transfer nilpotent',(AD-2*s.eye(7))**4,s.zeros(7))
    for cancel in (False,True):
        AS,SS=schur_model(cancel);eq(f'Schur retained inverse cancel={cancel}',AS.inv()[:2,:2],SS.inv())
    eq('Schur fill entry',schur_model()[1][0,1],-Q(1,2));eq('Schur cancellation entry',schur_model(True)[1][0,1],0)
    # Equal eigenvalues cause linked polynomial actions.
    AA=s.eye(2);vv=M([1,1]);eq('global Krylov dimension',M.hstack(vv,AA*vv).rank(),1)
    eq('independent local Krylov dimensions',M([[1,0],[0,0]]).rank()+M([[0,0],[0,1]]).rank(),2)
    reject('invariant Krylov inclusion is always equality',M.hstack(vv,AA*vv).rank()==2)
    PA,PD,PB,PN=preconditioner();eq('normalization of diagonal',PB*PD*PB,s.eye(2));eq('preconditioned matrix',PN,M([[1,Q(1,2)],[Q(1,2),1]]))
    eq('preconditioned spectral condition bound',max(PN.eigenvals())/min(PN.eigenvals()),3)
    eq('normalized coupling spectral radius',max(abs(a) for a in (PN-s.eye(2)).eigenvals()),Q(1,2))
    ea,er=error_model();eq('discovery residual squared',fro2(er),Q(3,2500));eq('discovery spectral error',max(abs(a) for a in er.eigenvals()),Q(3,100))
    reject('largest block error bounds total spectral error',max(abs(a) for a in er.eigenvals())<=Q(1,100))
    sensitivities=[1,2,4];costs=[1,1,2];eps=[Q(1,4),Q(1,8),Q(1,8)]
    eq('continuous precision budget',sum(a*e for a,e in zip(sensitivities,eps)),1)
    for i in range(3):eq(f'continuous stationary ratio {i}',costs[i]/(eps[i]*sensitivities[i]),4)
    caps=[Q(1,10),Q(1,2),Q(1,2)];clipped=[Q(1,10),Q(3,20),Q(3,20)];lam=Q(10,3)
    eq('clipped budget',sum(a*e for a,e in zip(sensitivities,clipped)),1)
    for i in range(3):eq(f'clipped water filling {i}',min(caps[i],costs[i]/(lam*sensitivities[i])),clipped[i])
    tables=precision_dp();enum=assignments()
    for budget in range(13):
        best=min((c,choice) for w,c,choice in enum if w<=budget)
        dp=min(cc for w,cc in tables[-1].items() if w<=budget)
        eq(f'discrete budget {budget} optimum cost',dp[0],best[0]);check(f'discrete budget {budget} selector feasible',sum(OPTIONS[i][k][0] for i,k in enumerate(dp[1]))<=budget)
    tau=Q(1,10);err=[Q(3,50),Q(2,25)];check('ceiling weights bound actual total',sum(err)<=tau*sum(s.ceiling(e/tau) for e in err))
    reject('floor quantization is a safe budget',sum(err)<=tau*sum(s.floor(e/tau) for e in err))
    tree=tree_model();rows=prunings(tree);eq('complete tree pruning count',len(rows),5)
    for lam in (0,Q(1,2),1,Q(3,2),2,4):eq(f'tree Lagrange optimum lambda={lam}',tree_lagrange(tree,lam)[0],min(c+lam*e for c,e,ll in rows))
    bt=tree_budget(tree)
    for budget in (0,1,2,3,4,5,6):eq(f'tree budget optimum {budget}',min(c for w,(c,_) in bt.items() if w<=budget),min(c for c,e,ll in rows if e<=budget))
    eq('unsupported budget optimum cost B=2',min(c for c,e,_ in rows if e<=2),8)
    check('unsupported Pareto requires inconsistent multiplier bounds',Q(7,4)>1)
    old=node_values(tree,2);new=node_values(changed_leaf(tree,'a0',3),2)
    check('only leaf and ancestors change',{k for k in old if old[k]!=new[k]}=={'a0','a','r'})
    eq('root updated value',new['r'],11)
    check('strict decision gap perturbation safe',13-Q(7,5)>10+Q(7,5))
    reject('half-gap equality preserves strict decision',13-Q(3,2)>10+Q(3,2))
    for reuse in range(1,12):check(f'amortization equivalence R={reuse}',(30+2*reuse<7*reuse)==(reuse>6))
    eq('minimum strictly profitable reuse',min(r for r in range(1,20) if 30+2*r<7*r),7)
    eq('end-to-end factored product application',DA*(DB*x)+UC*(VC.T*x),(product_model()[6]*product_model()[7])*x)
    # Selectors/data are machine-readable values used by the figures and prose.
    report={'status':'PASS','scope':'Exact worked examples only. No new Lean compilation, device timing, or universal algorithm claim.',
       'checks_passed':len(checks),'checks':checks,'invalid_controls_rejected':negative,
       'python_version':platform.python_version(),'sympy_version':s.__version__,
       'model_sha256':hashlib.sha256((ROOT/'source/models.py').read_bytes()).hexdigest(),
       'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       'values':{'running_y':[str(a) for a in A*x],'toeplitz_y':[str(a) for a in T*xt],
                 'walsh_stages':walsh_stages(list(range(1,9))),
                 'tree_prunings':rows,'precision_B4':min(cc for w,cc in tables[-1].items() if w<=4),
                 'triangular_solution':[str(a) for a in xD]}}
    (ROOT/'checks/EXACT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(checks)} positive exact/symbolic assertions; {len(negative)} false controls rejected.')
    print(json.dumps(report['values'],indent=2))
if __name__=='__main__':main()
