#!/usr/bin/env python3
"""Komorebi Hilbert 12, cubic gamma analytical resolvent / ambient C3 pencil.

Pure cubic case beta^3=7. Exact symbolic identities and numerical diagnostics.
IMPORTANT: This is NOT a proof that the elliptic-gamma special value is algebraic.
All work offline. Author: Komorebi P.
"""
import argparse
import time
import sympy as sp
import mpmath as mp

b, x, y, w, d, z = sp.symbols('b x y w d z')
fb = b**3-7
fw = w**2+w+1
f = x**3-b*x**2+1
J = 2+3*w
Jbar = -1-3*w
S1_poly = b**2*x**2-3*x-b
S2_poly = -b**2*x**2+2*x+2*b
D1=b**2*x-4
D2=b**2*x-5
p1=5*x-3*b
p2=4*x-3*b
Phi=p1/D1
Phi2=p2/D2
Den_orbit=D1*D2
Delta=f/Den_orbit
Qdelta=1-13*Delta+49*Delta**2
L=x+w*Phi+(-1-w)*Phi2
Lp=x+(-1-w)*Phi+w*Phi2

A=4*b*b+b-14
B=11*b-23
C=-b*b+3*b-3
NY=(y-C)*(B+b*A)-A*A
DY=A*(y-C)+B*B+b*A*B
c=3*(652*b*b-1230*b-33)
R=y**3+(6*b*b-14*b+2)*y*y+(4*b*b-6*b-1)*y+94*b*b-124*b-107


def rem_b(poly):
    return sp.rem(sp.expand(poly),fb,b)


def assert_num_zero(expr, label):
    num,_=sp.fraction(sp.together(expr))
    num=sp.rem(sp.expand(num),fw,w)
    num=rem_b(num)
    assert num==0, f'{label}: exact polynomial residual = {sp.factor(num)}'
    print('  PASS',label)


def audit_exact():
    print('Exact rational-polynomial audits:')
    G=sp.Matrix([[5,-3*b],[b*b,-4]])
    assert_num_zero(G.det()-1,'SL2 determinant 1')
    assert_num_zero(sp.trace(G)-1,'matrix trace 1')
    for i,j in zip((G*G-G+sp.eye(2)),range(4)):
        assert_num_zero(i,'matrix cubic order' if j==0 else 'matrix component')
    assert_num_zero(Phi.subs(x,Phi)-Phi2, 'projective Phi squared')
    assert_num_zero(Phi.subs(x,Phi2)-x, 'projective Phi cubed')
    assert_num_zero(Delta.subs(x,Phi)-Delta,'Delta invariant under Phi')
    assert_num_zero(x+Phi+Phi2-b*(1+7*Delta),'cubic orbit trace')
    assert_num_zero(x*Phi+x*Phi2+Phi*Phi2-9*b*b*Delta,'cubic orbit pair sum')
    assert_num_zero(x*Phi*Phi2-(-1+20*Delta),'cubic orbit product')
    p_d=z**3-b*(1+7*d)*z*z+9*b*b*d*z+1-20*d
    assert_num_zero(sp.discriminant(p_d,z)-(49*d*d-13*d+1)**2,'perfect-square discriminant')
    assert_num_zero(L*Lp-b*b*Qdelta,'generic Fourier norm')
    assert_num_zero(L**3-(J**2+49*Delta)*Qdelta,'generic primitive Fourier cube')
    assert_num_zero(Lp**3-(Jbar**2+49*Delta)*Qdelta,'generic complementary Fourier cube')

    assert_num_zero(NY**3-b*NY*NY*DY+DY**3-c*R,'Möbius inverse: cubic polynomial residual')
    assert_num_zero(sp.diff(NY,y)*DY-NY*sp.diff(DY,y)-c,'Möbius determinant / derivative')
    Y0=A*x*x+B*x+C
    expr=sp.expand((DY*x-NY).subs(y,Y0)-A*A*f)
    # This identity holds in the full polynomial ring, not merely at a root.
    assert_num_zero(expr,'polynomial Y(x) inverse modulo f (identity)')

    # The gamma obstruction is Delta composed with the rational inverse x(Y).
    DeltaY=c*R/(DY*(b*b*NY-4*DY)*(b*b*NY-5*DY))
    assert_num_zero(Delta.subs(x,NY/DY)-DeltaY,'explicit rational gamma obstruction')

    # Cyclic Möbius action transported to Y coordinate.
    M=sp.Matrix([[sp.diff(NY,y),NY.subs(y,0)],
                 [sp.diff(DY,y),DY.subs(y,0)]])
    assert_num_zero(M.det()-c,'transport determinant')
    Psi0=M.adjugate()*G*M
    invc=sp.invert(c,fb,b)
    Psi=Psi0.applyfunc(lambda q:rem_b(q*invc))
    assert_num_zero(Psi.det()-1,'transported C3 action determinant')
    assert_num_zero(sp.trace(Psi)-1,'transported C3 action trace')
    for val in list(Psi**2-Psi+sp.eye(2)):
        assert_num_zero(val,'transported C3 action cubic relation')

    # A gamma triple on a single Psi orbit is parametrized by just Delta.
    T=sp.Poly(sp.expand(DY*(-7*b*NY**2+9*b*b*NY*DY-20*DY**2)),y)
    t3=rem_b(T.nth(3));t2=rem_b(T.nth(2))
    r2=6*b*b-14*b+2
    kappa=-(1300*b*b-3486*b+2723)/41
    theta=-14*(2*b*b+7*b+45)/41
    assert_num_zero((r2*t3-t2)-c*kappa,'trace normalizer numerator')
    assert_num_zero(t3-c*theta,'trace normalizer denominator')

    assert_num_zero(f.subs(x,-2*b/7)-sp.Rational(13,49),'spurious quadratic orbit control')
    print('Exact audit complete. None of these checks establishes Delta_gamma(1/3)=0.')
    return M,Psi,kappa,theta


def gamma_log(zeta,t,s,N):
    """Standard absolutely convergent fifth-smoothed gamma log at real zeta."""
    P=mp.exp(2j*mp.pi*t); Q=mp.exp(2j*mp.pi*s)
    ez=mp.exp(2j*mp.pi*zeta)
    pn=qn=en=ein=mp.mpc(1)
    total=mp.mpc(0)
    for n in range(1,N+1):
        pn*=P; qn*=Q; en*=ez; ein/=ez
        if n%5:
            total+=(pn*en-qn*ein)/(n*(1-pn)*(1-qn))
    r=max(abs(P),abs(Q)); small=min(abs(P),abs(Q))
    # Safe absolute analytic tail for real zeta and r>=small.
    bound=10*r**(N+1)/((N+1)*(1-r)**2*(1-small))
    return -5*total,bound


def numeric_experiment(zeta_fraction=(1,3),Ns=(4000,19000,34000),dps=64):
    mp.mp.dps=dps
    zeta=mp.mpf(zeta_fraction[0])/mp.mpf(zeta_fraction[1])
    omega=mp.exp(2j*mp.pi/3)
    beta=mp.root(7,3)*omega**2
    tau=(beta**2+2*beta)/15
    sigma=-(beta+2)/15
    chart=[]
    AA=4*beta**2+beta-14
    BB=11*beta-23
    CC=-beta**2+3*beta-3
    print('\nNumerical diagnostic at z=',mp.nstr(zeta,20),'with',dps,'digits')
    for (n,a,bs),N in zip([(1,0,0),(10,1,3),(23,5,-2)],Ns):
        t=(-tau-a)/n
        s=(sigma+bs)/n
        tick=time.monotonic()
        logU,tail=gamma_log(zeta,t,s,N)
        U=mp.exp(logU)
        Y=U+1/U
        num=(Y-CC)*(BB+beta*AA)-AA*AA
        den=AA*(Y-CC)+BB*BB+beta*AA*BB
        v=num/den
        fval=v**3-beta*v*v+1
        delt=fval/((beta**2*v-4)*(beta**2*v-5))
        chart.append((n,U,Y,v,delt))
        print(' chart',n,'N',N,'time',round(time.monotonic()-tick,2),'s')
        print('   U =',mp.nstr(U,22))
        print('   delta_gamma =',mp.nstr(delt,15),'abs',mp.nstr(abs(delt),8))
        print('   rigorous truncation tail for log(U) <=',mp.nstr(tail,8))
    v0=chart[0][3]
    orbit1=(5*v0-3*beta)/(beta**2*v0-4)
    orbit2=(4*v0-3*beta)/(beta**2*v0-5)
    e1=abs(chart[2][3]-orbit1)
    e2=abs(chart[1][3]-orbit2)
    Ys=[p[2] for p in chart]
    target=-6*beta**2+14*beta-2
    trace_err=abs(sum(Ys)-target)
    print(' analytic orbit check |v_23 - Phi(v_1)| =',mp.nstr(e1,11))
    print(' analytic orbit check |v_10 - Phi²(v_1)| =',mp.nstr(e2,11))
    print(' analytic trace |Y_1+Y_10+Y_23-target| =',mp.nstr(trace_err,11))
    print(' No small residual is an equality certificate.')
    return chart


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--exact-only',action='store_true')
    parser.add_argument('--dps',type=int,default=64)
    parser.add_argument('--nbase',type=int,default=4000)
    parser.add_argument('--n10',type=int,default=19000)
    parser.add_argument('--n23',type=int,default=34000)
    parser.add_argument('--negative-control',action='store_true')
    args=parser.parse_args()
    audit_exact()
    if not args.exact_only:
        numeric_experiment((1,3), (args.nbase,args.n10,args.n23),args.dps)
        if args.negative_control:
            numeric_experiment((1,4), (args.nbase,args.n10,args.n23),args.dps)
