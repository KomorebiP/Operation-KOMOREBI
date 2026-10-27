#!/usr/bin/env python3
"""Exact quotient/marking identities over Q(u,x), no arithmetic target fits."""
from pathlib import Path
from datetime import datetime, timezone
import time,json,platform,sys
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
def main():
 tic=time.perf_counter();start=datetime.now(timezone.utc).isoformat();checks=[];neg=[]
 def zero(name,expr):
  value=s.cancel(expr)
  if value!=0:raise AssertionError((name,value))
  checks.append(name)
 def yes(name,expr):
  if not expr:raise AssertionError(name)
  checks.append(name)
 def nonzero(name,expr):
  if s.cancel(expr)==0:raise AssertionError(('negative control',name))
  neg.append(name)
 u,x,y,z,r,lam,a,ya,yb=s.symbols('u x y z r lam a ya yb')
 b2=u*u-6*u+1;b4=u*u-u
 c4=b2*b2-24*b4;c6=-b2**3+36*b2*b4-216*u*u
 g2=c4/12;g3=c6/216
 aa=b2/12;bb=aa+u
 D=4*x**3+b2*x*x+2*b4*x+u*u
 A4=-5*u*(u*u+2*u-1);A6=-u*(u**4+10*u**3-5*u*u+15*u-1)
 Dt=lambda X:4*X**3+b2*X*X+(2*b4+4*A4)*X+u*u+4*A6
 den=x*x*(x-u)**2
 num=x**5-2*u*x**4+(u**3+3*u*u-u)*x**3+(-3*u**3+3*u*u)*x*x+(u**4-3*u**3)*x+u**4
 nd=5*x**4-8*u*x**3+3*(u**3+3*u*u-u)*x*x+2*(-3*u**3+3*u*u)*x+(u**4-3*u**3)
 dd=2*x*(x-u)**2+2*x*x*(x-u)
 H=nd*den-num*dd;phi=num/den;J=H/den**2
 zero('explicit numerator derivative',s.diff(num,x)-nd)
 zero('explicit denominator derivative',s.diff(den,x)-dd)
 zero('explicit rational derivative',s.diff(phi,x)-J)
 zero('map cleared target equation',H**2*D-(4*num**3*den+b2*num*num*den**2+(2*b4+4*A4)*num*den**3+(u*u+4*A6)*den**4))
 zero('map rational target equation',J**2*D-Dt(phi))
 zero('partial fraction form',phi-(x+u*(u-1)/x+u*u/x**2+u*u*(u+1)/(x-u)+u**4/(x-u)**2))
 zero('numerator at first kernel x',num.subs(x,0)-u**4)
 zero('numerator at second kernel x',num.subs(x,u)-u**6)
 zero('resultant no kernel cancellation',s.resultant(num,den,x)-u**20)
 yes('rational map degree',s.degree(num,x)==5 and s.degree(den,x)==4)
 q=u*u/(x*(x-u))
 L2=D*(1/x**2+1/(x-u)**2)-s.diff(D,x)/2*(1/x+1/(x-u))
 zero('logarithmic quotient identity',phi-(5*x-2*u+L2))
 # Independent Velu paired-addition derivation in normalized Weierstrass coordinates.
 X=x+aa;fw=lambda X:4*X**3-g2*X-g3
 velu=X
 for c in [aa,bb]:velu+=(fw(X)+fw(c))/(2*(X-c)**2)-2*X-4*c
 zero('paired Weierstrass sum derives map',velu-aa-phi)
 gp=120*(aa*aa+bb*bb)-19*g2
 gpp=280*(aa**3+bb**3)-42*g2*(aa+bb)-55*g3
 zero('quotient a4 coefficient',A4-(g2-gp)/4)
 zero('quotient a6 coefficient',A6-(g3-gpp+b2*A4/3)/4)
 C=lambda U,X,Y:Y*Y+(1-U)*X*Y-U*Y-X**3+U*X*X
 nx=(x-u)/u**2;ny=(y-u*x)/u**3;nu=-1/u
 zero('marking curve identity',u**6*C(nu,nx,ny)-C(u,x,y))
 zero('marking x twice',(nx-nu)/nu**2-x)
 zero('marking y twice',(ny-nu*nx)/nu**3-(-y-(1-u)*x+u))
 zero('negation preserves source',C(u,x,-y-(1-u)*x+u)-C(u,x,y))
 zero('marking theta invariant',nu**2/(nx*(nx-nu))-q)
 zero('quotient commutes with negation',J*(-z)+J*z)
 # Full group-invariance test, using reduction rather than the quotient equation alone.
 m=y/x;xp=m*m+(1-u)*m+u-x;yp=-(m+1-u)*xp+u
 remainder=s.rem(s.fraction(s.cancel(phi.subs(x,xp)-phi))[0],C(u,x,y),y)
 zero('quotient x invariant under addition by P',remainder)
 Z=2*y+(1-u)*x-u;Zp=2*yp+(1-u)*xp-u
 remainder=s.rem(s.fraction(s.cancel(J.subs(x,xp)*Zp-J*Z))[0],C(u,x,y),y)
 zero('quotient Z invariant under addition by P',remainder)
 disc=u**5*(u*u-11*u-1);discp=u*(u*u-11*u-1)**5
 cp=u**4+228*u**3+494*u*u-228*u+1
 c6p=-(u*u+1)*(u**4-522*u**3-10006*u*u+522*u+1)
 zero('source discriminant',c4**3-c6**2-1728*disc)
 zero('quotient discriminant',cp**3-c6p**2-1728*discp)
 zero('quotient c4',cp-12*gp);zero('quotient c6',c6p-216*gpp)
 h=lambda u:u-11-1/u
 js=lambda h:(h*h+10*h+5)**3/h
 jt=lambda h:(h*h+250*h+3125)**3/h**5
 zero('unmarked parameter invariant',h(-1/u)-h(u))
 zero('source j formula',c4**3/disc-js(h(u)))
 zero('quotient j formula',cp**3/discp-jt(h(u)))
 zero('discriminant ratio',discp/disc-h(u)**4)
 zero('dual exchanges source',js(125/z)-jt(z))
 zero('dual exchanges quotient',jt(125/z)-js(z))
 zero('dual is involution',125/(125/z)-z)
 # Homothetic marked chart transport, including the ordinate sign.
 tx=lambda A,L,X:(X-A)/L**2
 ty=lambda U,A,YA,L,X,Y:(Y-YA-(1-U)*L*(X-A))/(2*L**3)
 xt=tx(a,lam,x);yt=ty(u,a,-u*lam**3,lam,x,y)
 xs=tx(r*r*a,-r*lam,r*r*x)
 ys=ty(u,r*r*a,-r**3*(-u*lam**3),-r*lam,r*r*x,r**3*y)
 zero('cubic chart x fixed',xs-xt)
 zero('cubic chart y inverted',ys-(-yt-(1-u)*xt+u))
 zero('cubic chart parameter fixed',-(-r**3*yb)/(-r**3*ya)-(-yb/ya))
 nonzero('omitting constant from logarithmic identity',phi-(5*x+L2))
 nonzero('opposite quotient a4 rejected',J**2*D-(4*phi**3+b2*phi**2+(2*b4-4*A4)*phi+u*u+4*A6))
 nonzero('quotient target generally differs from source',Dt(x)-D)
 nonzero('wrong Fricke scale rejected',js(1/z)-jt(z))
 nonzero('marking change is not pointwise identity',nx-x)
 nonzero('cubic chart is not ordinate identity',ys-yt)
 # Bounded arithmetic regressions supplement the universal polynomial identities.
 for U in [s.Rational(-3),s.Rational(-1),s.Rational(1,2),s.Rational(1),s.Rational(2),s.Rational(3)]:
  for X0 in [s.Rational(7,3),s.Rational(-5,2)]:
   yes(f'nondegenerate regression u={U},x={X0}',disc.subs(u,U)!=0 and den.subs({u:U,x:X0})!=0)
   zero(f'curve regression u={U},x={X0}',(J**2*D-Dt(phi)).subs({u:U,x:X0}))
 result={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'check_count':len(checks),'checks':checks,'negative_controls':neg,'coefficient_domain':'Q[u,x,y] and Q(u,x,y), no floating arithmetic','python':sys.version.split()[0],'sympy':s.__version__,'platform':platform.platform(),'scope':'Explicit degree-five rational map identities, discriminants, parameter transformations, formal derivative numerator, and bounded exact regressions. Geometric degree/isogeny interpretation has a separate ordinary proof.'}
 (ROOT/'evidence/exact_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS',len(checks),'exact checks,',len(neg),'negative controls;',round(result['runtime_seconds'],2),'seconds')
if __name__=='__main__':main()
