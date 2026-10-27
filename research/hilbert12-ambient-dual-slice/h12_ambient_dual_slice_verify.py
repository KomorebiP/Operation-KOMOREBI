#!/usr/bin/env python3
"""Exact Hilbert 12 cubic ambient-duality and character-packet checks.

Finite polynomial and matrix algebra only. Does NOT check elliptic gamma
algebraicity or prove the Hilbert 12 analytic comparison. Requires sympy.
"""
import sympy as s

M=s.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
H=s.Matrix([[4,-4,15],[-4,1,0],[15,0,0]])
I=s.eye(3); N=M-2*I
u=s.Matrix([1,2,4]); v=s.Matrix([0,1,2]); w=s.Matrix([0,0,1])
B=s.Matrix.hstack(u,v,w)
assert M.det()==1
assert N**3==-7*I
assert s.discriminant(M.charpoly().as_expr())==-1323
assert M.T*H==H*M and H.det()==-225
assert B.det()==1
assert (B.T*H*B).applyfunc(lambda x:x%7)==s.Matrix([[0,0,1],[0,1,0],[1,0,0]])
for a,b in [(N*u,s.zeros(3,1)),(N*v,u),(N*w,v)]:
    assert all(int(x)%7==0 for x in a-b)
assert all(int((u.T*H*x)[0])%7==0 for x in (u,v))
assert int((u.T*H*w)[0])%7==1

vectors=(s.Matrix([a,b,c]) for a in range(7) for b in range(7) for c in range(7))
kerN=[];kerN2=[]
for a in vectors:
    if all(int(x)%7==0 for x in N*a): kerN.append(a)
    if all(int(x)%7==0 for x in (N**2)*a): kerN2.append(a)
assert len(kerN)==7 and len(kerN2)==49
assert all(int((u.T*H*a)[0])%7==0 for a in kerN2)
assert M.T*H*M.inv()==H

# 1/J=(-1-3omega)/7; 1/Jbar=(2+3omega)/7.
# The oriented Weil exponent e_{7,H}(x/J,y/Jbar) is 3*x^T*H*y mod 7.
def phase(x,y):
    return int(3*(x.T*H*y)[0])%7
assert phase(u,w)==3 and phase(u,u)==0
for a in range(7):
    for b in range(7):
        assert phase(u,w+a*u+b*v)==3
for r in range(1,7): assert phase(u,r*w)==3*r%7

beta=s.symbols('beta')
tau=(beta**2+2*beta)/15
sigma=-(beta+2)/15
delta=(tau+2*sigma+4)/7
assert s.simplify(delta-(beta**2+56)/105)==0
for expr in [beta*delta+8*sigma+1, (2-beta)*delta-2*delta-8*sigma-1]:
    assert s.rem(s.together(expr).as_numer_denom()[0],beta**3-7,beta)==0

omega=s.symbols('omega')
def red(expr): return s.rem(s.expand(expr),omega**2+omega+1,omega).expand()
J=2+3*omega;Jbar=-1-3*omega
assert red(J+Jbar)==1 and red(J*Jbar)==7
chi={1:s.Integer(1),2:omega,3:omega**2,4:omega**2,5:omega,6:s.Integer(1)}
def mul(a,b):
    out=[s.Integer(0)]*7
    for i in range(7):
        for j in range(7):out[(i+j)%7]+=a[i]*b[j]
    return [red(t) for t in out]
g1=[s.Integer(0)]*7
for k in range(1,7):g1[k]=red(chi[k])
for r in range(1,7):
    g=[s.Integer(0)]*7
    for k in range(1,7):g[(r*k)%7]+=chi[k]
    g=[red(t) for t in g]
    assert mul(mul(g,g),g)==[red(6*J)]+[red(-J)]*6
    assert all(red(g[k]-red(chi[r]**2)*g1[k])==0 for k in range(7))

# Integral Eisenstein coordinates of the cubic character:
# chi(k)=a(k)+omega*b(k).
a={1:1,2:0,3:-1,4:-1,5:0,6:1}
b={1:0,2:1,3:-1,4:-1,5:1,6:0}
assert all(red(a[k]+omega*b[k]-chi[k])==0 for k in range(1,7))
# Upon index relabeling f'_k=f_{2k}, (A,B)->(B/A,1/A).
T=s.Matrix([[-1,1],[-1,0]])
assert T**3==s.eye(2) and T.det()==1
assert [a[(4*k)%7] for k in range(1,7)]==[b[k]-a[k] for k in range(1,7)]
assert [b[(4*k)%7] for k in range(1,7)]==[-a[k] for k in range(1,7)]

print('PASS matrix/codifferent algebra and nilpotent filtration')
print('PASS no-go for pairing opposite fixed vectors and nontrivial dual phase')
print('PASS six Gauss-cube identities, independent of nonzero character slice')
print('PASS principal-seven shift and exact epsilon carry identity')
print('PASS two integral character coordinates and order-three torus action')
print('LIMIT: No elliptic-gamma scalar equality or formal Lean check was proved')
