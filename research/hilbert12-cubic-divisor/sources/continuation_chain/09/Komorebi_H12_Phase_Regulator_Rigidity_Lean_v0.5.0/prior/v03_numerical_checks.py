#!/usr/bin/env python3
"""Direct theta/Weierstrass/gamma regressions. No intervals or U_alg evaluation."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
from functools import lru_cache
from itertools import product
import argparse,importlib.util,json,time,sys,platform
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('inherited_evaluator',ROOT/'prior/gamma_evaluator.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
class Elliptic:
 def __init__(self,t,digits):
  self.t=mp.mpc(t);self.nome=mp.exp(mp.pi*1j*t);self.Q=self.nome**2
  self.j0=mp.jtheta(1,0,self.nome,derivative=3)/(3*mp.jtheta(1,0,self.nome,derivative=1))
  self.a=self.wp(mp.mpf(1)/5);self.b=self.wp(mp.mpf(2)/5);self.d=self.a-self.b
  self.ya=self.wpp(mp.mpf(1)/5);self.yb=self.wpp(mp.mpf(2)/5)
  self.eta_ratio=mp.qp(self.Q**5,self.Q**5)/mp.qp(self.Q,self.Q)**5
  self.c_eta=(2*mp.pi)**4/(5*self.eta_ratio**2)
  self.series_cutoff=max(100,int(mp.ceil((digits+40)*mp.log(10)/(-mp.log(abs(self.Q))))))
  z=mp.mpc(1);e4=e6=mp.mpc(0)
  for n in range(1,self.series_cutoff+1):
   z*=self.Q;v=z/(1-z);e4+=n**3*v;e6+=n**5*v
  self.g2=4*mp.pi**4/3*(1+240*e4);self.g3=8*mp.pi**6/27*(1-504*e6)
 def reduce(self,z):
  z=mp.mpc(z);z-=mp.floor(mp.im(z)/mp.im(self.t))*self.t;z-=mp.floor(mp.re(z));return z
 @lru_cache(None)
 def wp(self,z):
  z=mp.pi*self.reduce(z);j=[mp.jtheta(1,z,self.nome,derivative=k) for k in range(3)]
  return mp.pi**2*(self.j0-j[2]/j[0]+(j[1]/j[0])**2)
 @lru_cache(None)
 def wpp(self,z):
  z=mp.pi*self.reduce(z);j=[mp.jtheta(1,z,self.nome,derivative=k) for k in range(4)]
  return mp.pi**3*(-j[3]/j[0]+3*j[1]*j[2]/j[0]**2-2*(j[1]/j[0])**3)
 def curve(self,x):return 4*x**3-self.g2*x-self.g3
 def psi3(self,x):return 3*x**4-mp.mpf(3)/2*self.g2*x*x-3*self.g3*x-self.g2**2/16
 def X(self,z):return (self.wp(z)-self.a)/self.d
 def canonical(self,z):
  x=self.X(z);return 1/(x*(x+1))
 @lru_cache(None)
 def theta(self,z):
  z=self.reduce(z);x=mp.exp(2j*mp.pi*z);Q=self.Q
  return (mp.qp(x,Q)*mp.qp(Q/x,Q))**5/(mp.qp(x**5,Q**5)*mp.qp((Q/x)**5,Q**5))
 def Q5(self,x):return (x-self.a)*(x-self.b)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--digits',type=int,choices=[40,70],required=True);args=ap.parse_args()
 mp.mp.dps=args.digits+25;tic=time.perf_counter();start=datetime.now(timezone.utc).isoformat();e=prior.Evaluator(args.digits)
 checks=[];errors=[];neg=[];curves=[];tol=mp.mpf(10)**(-args.digits+8)
 def near(name,x,y):
  err=abs(x-y)/max(mp.mpf(1),abs(x),abs(y))
  if err>=tol:raise AssertionError((name,mp.nstr(err,20),mp.nstr(x,20),mp.nstr(y,20)))
  checks.append(name);errors.append(err)
 def different(name,x,y):
  err=abs(x-y)/max(mp.mpf(1),abs(x),abs(y))
  if err<=mp.mpf('1e-7'):raise AssertionError(('negative control',name,mp.nstr(err,18)))
  neg.append({'name':name,'normalized_difference':mp.nstr(err,18)})
 actual=None
 for label,t in [('generic1',mp.mpc('.23','.71')),('generic2',mp.mpc('-.31','1.13')),('cubic',e.t)]:
  E=Elliptic(t,args.digits)
  if label=='cubic':actual=E
  near(label+' ordinate product',E.ya*E.yb,E.d**3)
  near(label+' curve at P',E.ya**2,E.curve(E.a));near(label+' curve at 2P',E.yb**2,E.curve(E.b))
  near(label+' mutual doubling psi P',E.psi3(E.a),E.curve(E.a)*E.d)
  near(label+' mutual doubling psi 2P',E.psi3(E.b),-E.curve(E.b)*E.d)
  near(label+' f product',E.curve(E.a)*E.curve(E.b),E.d**6)
  near(label+' psi3 product',E.psi3(E.a)*E.psi3(E.b),-E.d**8)
  near(label+' cubed normalizer',E.c_eta**3,E.curve(E.a)*E.curve(E.b))
  near(label+' eighth normalizer',E.c_eta**8,(E.psi3(E.a)*E.psi3(E.b))**2)
  near(label+' canonical normalizer',E.c_eta,E.d**2)
  for n in [2,3]:
   torsion=[(mp.mpf(a)+b*t)/n for a,b in product(range(n),repeat=2) if (a,b)!=(0,0)]
   den=mp.fprod(E.Q5(E.wp(z)) for z in torsion)
   near(label+f' torsion norm at {n}',mp.fprod(E.theta(z) for z in torsion),mp.mpf(n)**4)
   near(label+f' normalizer from {n}',E.c_eta**(n*n-1),n**4*den)
  ss=E.a+E.b;pp=E.a*E.b;xx0=E.wp(mp.mpf(1)/3)
  near(label+' symmetric discriminant form',E.theta(mp.mpf(1)/3),(ss*ss-4*pp)/(xx0*xx0-ss*xx0+pp))
  u=-E.yb/E.ya;scale=E.ya/E.d
  for j,z in enumerate([mp.mpf(1)/3,mp.mpf('.127')+mp.mpf('.08')*t,mp.mpf('.312')+mp.mpf('.27')*t]):
   near(label+f' rational theta {j}',E.theta(z),E.canonical(z))
   X=E.X(z);swapped=(E.wp(z)-E.b)/(-E.d)
   near(label+f' unordered reflection {j}',swapped,-1-X)
   xx=(E.wp(z)-E.a)/scale**2
   yy=(E.wpp(z)-E.ya-(1-u)*scale*(E.wp(z)-E.a))/(2*scale**3)
   near(label+f' Tate equation {j}',yy**2+(1-u)*xx*yy-u*yy,xx**3-u*xx**2)
   near(label+f' Tate theta {j}',E.theta(z),u*u/(xx*(xx-u)))
  cube=mp.exp(2j*mp.pi/3)*E.c_eta
  near(label+' cuberoot rescaling retains cube',cube**3,E.c_eta**3)
  different(label+' cuberoot rescaling fails eighth',cube**8,E.c_eta**8)
  curves.append({'label':label,'t':mp.nstr(t,30),'c_t':mp.nstr(E.c_eta,30),'a_minus_b':mp.nstr(E.d,30),'Tate_parameter':mp.nstr(u,30),'Eisenstein_cutoff':E.series_cutoff})
 E=actual;Es=Elliptic(e.s,args.digits)
 near('source a scaling',Es.a,e.rho**2*E.a);near('source b scaling',Es.b,e.rho**2*E.b)
 near('source c scaling',Es.c_eta,e.rho**4*E.c_eta)
 near('source invariant Tate parameter',-Es.yb/Es.ya,-E.yb/E.ya)
 for j,z in enumerate([mp.mpf(1)/3,mp.mpc('.021','.003')]):
  near(f'normalized chart coordinate covariance {j}',E.X(e.rho*z),Es.X(z))
  near(f'canonical theta covariance {j}',E.canonical(e.rho*z),Es.canonical(z))
 V=list(product((0,1),repeat=3));T=lambda v:(v[2],v[0],v[1]);chi=lambda u,v:(-1)**sum(a*b for a,b in zip(u,v))
 w=lambda v:mp.mpf(1)/3+(-v[0]*e.t+v[1]*e.s+v[2])/2
 x={v:e.F(w(v)) for v in V};y={v:e.F(e.rho*w(v)) for v in V};can={};direct={}
 for v in V:
  A=5+4*v[0]-2*v[1]+7*v[2]
  points=[w(T(T(v)))+j*e.s for j in range(A)]
  can[v]=mp.fprod(E.canonical(z) for z in points)
  direct[v]=mp.fprod(E.theta(z) for z in points)
  near('canonical versus theta carry '+str(v),can[v],direct[v])
  near('canonical gamma carry '+str(v),y[v],x[T(v)]*can[v])
 walsh=lambda xx,u:mp.fprod(xx[v]**chi(u,v) for v in V)
 for u in V:
  near('all-channel canonical signed transport '+str(u),walsh(y,u),walsh(x,T(u))*walsh(can,u))
 first=[u for u in V if sum(u)==1]
 lhs=mp.fprod(walsh(y,u) for u in first)
 rhs=mp.fprod(walsh(x,u)*walsh(can,u) for u in first)
 near('first-order aggregate fully normalized',lhs,rhs)
 different('omitting c_t changes first-order aggregate',mp.fprod(walsh(can,u) for u in first),mp.fprod(walsh(can,u) for u in first)*E.c_eta**36)
 different('opposite normalization sign changes theta',E.canonical(mp.mpf(1)/3),-E.canonical(mp.mpf(1)/3))
 different('absolute value is not the complex normalizer',E.c_eta,abs(E.c_eta))
 out={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'requested_digits':args.digits,'working_digits':mp.mp.dps,'equality_count':len(checks),'equalities':checks,'negative_controls':neg,'max_normalized_error':mp.nstr(max(errors),25),'curves':curves,'max_gamma_cutoff':max(e.cutoffs),'max_gamma_series_truncation_bound':mp.nstr(max(e.tails),18),'python':sys.version.split()[0],'mpmath':mp.__version__,'platform':platform.platform(),'scope':'Three analytic lattices, direct theta and Weierstrass functions; actual cubic gamma carried signed packet. No U_alg is evaluated. Floating regression only, not interval arithmetic.'}
 (ROOT/f'evidence/numerical_{args.digits}.json').write_text(json.dumps(out,indent=2)+'\n')
 print(f'PASS {args.digits} digits: {len(checks)} equalities, {len(neg)} negative controls; max error {out["max_normalized_error"]}; {out["runtime_seconds"]:.2f}s')
if __name__=='__main__':main()
