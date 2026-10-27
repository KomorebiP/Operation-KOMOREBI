#!/usr/bin/env python3
"""Regress exact reflection and its quadratic jet; no U_alg, no intervals."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,sys,json,time
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'prior'))
from gamma_evaluator import Evaluator
from v012_numerical_checks import PositiveSmoothed

def run(digits):
  with mp.workdps(digits+25):
    e=Evaluator(digits); t,s,beta,rho=e.t,e.s,e.beta,e.rho
    d=(-t+2*s+4)/7
    def theta(z,v):return e.theta_t(z) if v==t else e.theta(z,v)
    pg=PositiveSmoothed(digits,theta)
    def F(z):return pg.F(z,t,s)
    def R(z):return mp.fprod(F(z+k*d) for k in range(7))/F(beta*z)
    def q(z):return e.theta_t(z)
    def qs(z):return e.theta(z,s)
    def T(z):
      return q(z)*qs(beta*z)/(qs(z)*q(beta*z))*mp.fprod(1/q(z+k*d-s) for k in range(1,7))
    checks=[];errs=[];negative=[]
    def ck(name,lhs,rhs):
      er=abs(lhs/rhs-1)
      if er>=mp.mpf(10)**(-digits+8):raise AssertionError((name,mp.nstr(er,20)))
      checks.append(name);errs.append(er)
    points=[mp.mpc('.217','.017'),mp.mpc('.031','.004')]
    for i,z in enumerate(points):ck(f'exact correction reflection point {i}',R(z)*R(-z),T(z))
    R0=mp.fprod(1/q((t+d)/2+j*d) for j in range(3))
    ck('gamma-free anchor agrees with actual gamma product',R(0),R0)
    ck('reflection at zero has exactly the squared anchor',mp.fprod(1/q(k*d-s) for k in range(1,7)),R0**2)
    def thlog2(z,v):
      nome=mp.exp(mp.pi*1j*v); x=mp.pi*z
      th=mp.jtheta(1,x,nome)
      return mp.pi**2*(mp.jtheta(1,x,nome,2)/th-(mp.jtheta(1,x,nome,1)/th)**2)
    def wp(z,v):
      nome=mp.exp(mp.pi*1j*v)
      return mp.pi**2*mp.jtheta(1,0,nome,3)/(3*mp.jtheta(1,0,nome,1))-thlog2(z,v)
    def Lt(z):return 5*thlog2(z,t)-25*thlog2(5*z,5*t)
    S=wp(mp.mpf(1)/5,t)+wp(mp.mpf(2)/5,t)
    a2=((1-beta**2)*(1-rho**2)*S-mp.fsum(Lt((t+d)/2+j*d) for j in range(3)))/2
    h=mp.mpf('1e-7')
    fd=mp.log(R(h)*R(-h)/R0**2)/(2*h*h)
    er=abs(fd/a2-1)
    if er>=mp.mpf('1e-5'):raise AssertionError(('quadratic jet diagnostic',mp.nstr(er,22)))
    for name,val in [('omitting reflection theta factors',abs(T(points[0])-1)),('omitting the quadratic factor two',abs(fd/(2*a2)-1)),('replacing the complex zero anchor by its modulus',abs(R0/abs(R0)-1))]:
      if val<=mp.mpf('1e-4'):raise AssertionError('negative control failed '+name)
      negative.append(name)
    return {'digits':digits,'working_digits':digits+25,'identities':checks,'max_relative_error':mp.nstr(max(errs),22),'quadratic_jet':mp.nstr(a2,40),'finite_difference_jet':mp.nstr(fd,40),'jet_diagnostic_relative_error':mp.nstr(er,22),'jet_offset':'1e-7','jet_tolerance':'1e-5','negative_controls':negative,'max_gamma_cutoff':max(pg.cutoffs),'max_logarithmic_tail_bound':mp.nstr(max(pg.tails),22),'mpmath':mp.__version__,'scope':'Floating regression of the reflection identity and the separately proved quadratic coefficient. No directed intervals, no canonical infinite-product numerical equality, no U_alg evaluation.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--digits',type=int,choices=[40,70],required=True);args=ap.parse_args()
    start=datetime.now(timezone.utc).isoformat();tic=time.monotonic();out=run(args.digits)
    out.update(started_at=start,runtime_seconds=time.monotonic()-tic,exit_status=0,python=sys.version.split()[0])
    (ROOT/f'evidence/numerical_{args.digits}.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS',args.digits,len(out['identities']),'identities; quadratic jet diagnostic;',len(out['negative_controls']),'negative controls; max error',out['max_relative_error'],'seconds',round(out['runtime_seconds'],2))
