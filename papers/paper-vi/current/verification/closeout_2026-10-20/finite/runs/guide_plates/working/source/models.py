"""Exact finite models for Paper VI's visual appendix.
All arithmetic definitions use SymPy rationals/algebraic expressions. Plotting samples
are downstream numerical evaluations, never used as proof certificates.
"""
from __future__ import annotations
from itertools import product
import sympy as s
R=s.Rational; M=s.Matrix

def norm1(a):
    if a.cols==1:return sum(abs(v) for v in a)
    return max([sum(abs(a[i,j]) for i in range(a.rows)) for j in range(a.cols)],default=s.S.Zero)
def stochastic(a):return all(v>=0 for v in a) and s.ones(1,a.rows)*a==s.ones(1,a.cols)
def basis(n,i):return s.eye(n)[:,i]

def chain():
    Q=M([[-3,1,2,0],[1,-3,0,2],[2,0,-3,1],[0,2,1,-3]])
    C=M([[1,1,0,0],[0,0,1,1]])
    K=s.eye(4)+Q/8;Kc=M([[R(3,4),R(1,4)],[R(1,4),R(3,4)]])
    H=M([[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]])/2
    # Columns are constant, within-pair, between-pair and alternating contrasts.
    Ps=[H[:,i]*H[:,i].T for i in range(4)]
    eps=R(1,16);bad=K.copy();bad[0,0]-=eps;bad[2,0]+=eps
    return Q,K,C,Kc,H,Ps,bad

def transfer(q):
    *_,Ps,_bad=chain()
    return sum((q**j*Ps[j] for j in range(4)),s.zeros(4))

def expectation():
    weights=M([R(1,10),R(2,10),R(3,10),R(4,10)]);W=s.diag(*weights)
    E=M([[R(1,3),R(2,3),0,0],[R(1,3),R(2,3),0,0],[0,0,R(3,7),R(4,7)],[0,0,R(3,7),R(4,7)]])
    E0=s.ones(4,1)*weights.T;Ds=[E0,E-E0,s.eye(4)-E];f=M([0,3,2,5])
    energies=[s.factor((d*f).dot(W*d*f)) for d in Ds]
    return weights,W,E,E0,Ds,f,energies

def bayes(p,likelihood):
    if p.rows!=len(likelihood):raise ValueError('Likelihood and state dimension differ')
    if any(x<0 for x in p) or sum(p)!=1:raise ValueError('Prior must be a probability vector')
    if any(x<0 for x in likelihood):raise ValueError('Likelihood must be nonnegative')
    weighted=s.diag(*likelihood)*p;z=sum(weighted)
    if z<=0:raise ValueError('Evidence must be positive')
    return weighted/z,z

def coarse_effective(p,ell):
    C=chain()[2];P=C*p
    r=M([sum(ell[i]*p[i] for i in I)/P[j] if P[j]!=0 else 0 for j,I in enumerate([(0,1),(2,3)])])
    return P,r

def posterior_packets(p,ell):
    post,z=bayes(p,ell);m=[];shapes=[]
    for I in [(0,1),(2,3)]:
        e=sum(ell[i]*p[i] for i in I);m.append(e/z)
        shapes.append(M([ell[i]*p[i]/e if i in I and e!=0 else 0 for i in range(4)]))
    return post,M(m),shapes,z

def filter_model():
    Q,K,C,Kc,H,Ps,bad=chain();p=basis(4,0);coarse=C*p
    likelihoods=[M([R(3,4),R(3,4),R(1,4),R(1,4)]),M([R(1,2),R(1,2),1,1])]
    rows=[];joint=s.S.One
    for ell in likelihoods:
        pred=K*p;post,z=bayes(pred,ell);cpred=Kc*coarse;cp,cz=bayes(cpred,[ell[0],ell[2]])
        rows.append({'before':p,'prediction':pred,'likelihood':ell,'posterior':post,'z':z,'coarse':cp,'coarse_z':cz})
        p=post;coarse=cp;joint*=z
    return rows,joint

def green(n):
    if n<1:raise ValueError('At least one interior grid point is needed')
    h=R(1,n+1);T=s.diag(*([2]*n))
    for i in range(n-1):T[i,i+1]=T[i+1,i]=-1
    L=T/h**2;xs=[h*(i+1) for i in range(n)]
    G=M(n,n,lambda i,j:min(xs[i],xs[j])-xs[i]*xs[j])
    return h,T,L,xs,G

def fk_paths(n=3):
    K=M([[R(3,4),R(1,4)],[R(1,4),R(3,4)]])
    w=M([1,R(1,2)]);f=M([2,1]);rows=[]
    for tail in product(range(2),repeat=n):
        path=(0,)+tail;p=s.S.One;a=s.S.One
        for i,j in zip(path,path[1:]):p*=K[j,i];a*=w[i]
        rows.append({'path':path,'probability':p,'potential':a,'terminal':f[path[-1]],'contribution':p*a*f[path[-1]]})
    return K,w,f,rows

def rational_times():
    return [R(0),R(1,8),R(1,4),R(1,2),R(3,4),R(1)]
