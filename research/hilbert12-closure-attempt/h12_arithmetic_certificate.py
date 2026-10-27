#!/usr/bin/env python3
"""Exact polynomial certificate for the independently specified H12 target.
Author: Komorebi P. No gamma algebraicity conclusion.
"""
import sympy as s
b,w,x,z=s.symbols('b w x z')
J=2+3*w;Jb=-1-3*w

def red(e):
    e=s.rem(s.expand(e),x**3-J,x)
    e=s.rem(s.expand(e),w*w+w+1,w)
    return s.rem(s.expand(e),b**3-7,b)

def mul(a,c):return red(a*c)
def power(a,n):
    result=s.Integer(1)
    for _ in range(n):result=mul(result,a)
    return result

def check(e,label):
    r=red(e)
    assert r==0,(label,r)
    print('PASS',label)

check(J*Jb-7,'Jacobi norm seven')
check(J+Jb-1,'complementary Jacobi sum')
xinv=red(x*x*Jb/7)
check(x*xinv-1,'Kummer coordinate inverse')
nu=red((x+b*xinv-b*b)/3)
v=red(-b*b*nu-2*nu*nu)
check(power(v,3)-mul(b,power(v,2))+1,'explicit cubic generator')
Y=red((4*b*b+b-14)*power(v,2)+(11*b-23)*v-b*b+3*b-3)
Z=red(((-2*b*b+7*b-8)*power(v,2)+(-10*b*b+11*b+17)*v)/3+7-b-b*b)
check(power(Y,2)-4+3*power(Z,2),'reciprocal quadratic discriminant')
check(power(Y,3)+(6*b*b-14*b+2)*power(Y,2)+(4*b*b-6*b-1)*Y+94*b*b-124*b-107,'cubic membership of Y')
U=red((Y-(1+2*w)*Z)/2)
Ui=red((Y+(1+2*w)*Z)/2)
check(mul(U,Ui)-1,'unit reciprocal')
check(U+Ui-Y,'U plus inverse equals Y')
Q=power(U,6)+(6*b*b-14*b+2)*power(U,5)+(4*b*b-6*b+2)*power(U,4)+(106*b*b-152*b-103)*power(U,3)+(4*b*b-6*b+2)*power(U,2)+(6*b*b-14*b+2)*U+1
check(Q,'original reciprocal sextic Q(U_alg) = 0')

# The selected embedding uses the primitive seventh root exp(6 pi i/7).
chi={1:1,2:w,3:-1-w,4:-1-w,5:w,6:1}
G=sum(chi[a]*z**((3*a)%7) for a in range(1,7))
res=s.rem(s.expand(G**3),z**7-1,z)
res=s.rem(s.expand(res-7*J+J*sum(z**k for k in range(7))),w*w+w+1,w)
assert s.expand(res)==0
print('PASS exact Gauss cubic in the group algebra')

# Check the contraction endpoint in the ambient Möbius invariant.
y=s.symbols('y')
fb=b**3-7
rb=lambda e:s.rem(s.expand(e),fb,b)
def rat(e):
    n,d=s.fraction(s.cancel(e));n=rb(n);d=rb(d)
    return rb(n*s.invert(d,fb,b))
A=4*b*b+b-14;B=11*b-23;C=-b*b+3*b-3
eps=2-b;rho=b*b+2*b+4
Y0=rb(eps**2+rho**2)
NY=(Y0-C)*(B+b*A)-A*A
DY=A*(Y0-C)+B*B+b*A*B
v0=rat(NY/DY)
d0=rat((v0**3-b*v0*v0+1)/((b*b*v0-4)*(b*b*v0-5)))
assert d0!=0
assert s.degree(d0,b)<3
print('PASS contraction endpoint is not the arithmetic fiber d = 0')
print('d_gamma(0) =',s.factor(d0))
print('All arithmetic assertions passed. No analytic phase equality asserted.')
