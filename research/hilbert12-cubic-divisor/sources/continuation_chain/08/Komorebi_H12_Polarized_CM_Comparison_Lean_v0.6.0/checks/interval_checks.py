#!/usr/bin/env python3
"""Directed interval enclosure plus a proved infinite-series tail.

Trusted arithmetic: mpmath.iv elementary real/complex operations. This is not a
Lean certificate of mpmath. No equality with U_alg is inferred from a small ball.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse,json,time,sys,math
import mpmath as mp
from mpmath import iv
from sympy import integer_nthroot
ROOT=Path(__file__).resolve().parents[1]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--digits',type=int,choices=[90,120],required=True);args=ap.parse_args()
 iv.dps=args.digits;start=datetime.now(timezone.utc).isoformat();tic=time.perf_counter();checks=[];neg=[]
 def require(name,cond):
  if cond is not True: raise AssertionError((name,cond))
  checks.append(name)
 def zero_in(z):return bool(0 in z.real and 0 in z.imag)
 def close(name,z):require(name,zero_in(z))
 def real_interval_endpoints(x):
  # Preserve exact binary endpoints in machine-readable output.
  return {'display':str(x),'binary_endpoints':[list(v) for v in x._mpi_]}
 def complex_interval(z):return {'real':real_interval_endpoints(z.real),'imag':real_interval_endpoints(z.imag)}
 D=10**(args.digits+10)
 k=int(integer_nthroot(7*D**3,3)[0]);m=math.isqrt(3*D**2)
 require('cube root exact integer lower/upper proof',k**3<=7*D**3<(k+1)**3)
 require('square root exact integer lower/upper proof',m*m<=3*D**2<(m+1)**2)
 def enclosed_ratio(lo,hi):
  a=iv.mpf(lo)/D;b=iv.mpf(hi)/D
  return iv.mpf([a.a,b.b])
 root7=enclosed_ratio(k,k+1);root3=enclosed_ratio(m,m+1)
 j=iv.mpc(0,1);pi=iv.pi;omega=iv.mpc(-iv.mpf(1)/2,root3/2)
 beta=root7*omega**2;eps=2-beta;t=-(beta*beta+2*beta)/15;s=-(beta+2)/15
 p=iv.exp(2*pi*j*t);q=iv.exp(2*pi*j*s)
 rp=iv.mpf(19)/20;rq=iv.mpf(3)/5
 require('positive t height',t.imag>0);require('positive s height',s.imag>0)
 require('p radius below 19/20',abs(p)<rp);require('q radius below 3/5',abs(q)<rq)
 N=2500;pn=qn=iv.mpc(1);L0=Lc=reg=iv.mpc(0);retained=active=0
 for n in range(1,N+1):
  pn*=p;qn*=q
  if n%5:
   retained+=1;den=n*(1-pn)*(1-qn);w=omega**(n%3)
   L0 += -5*(pn-qn)/den
   Lc += -5*(pn*w-qn/w)/den
   if n%3:
    active+=1;reg += -15*(pn*(w-1)-qn*(1/w-1))/den
 tail=5/((N+1)*(1-rp**(N+1))*(1-rq**(N+1)))*(rp**(N+1)/(1-rp)+rq**(N+1)/(1-rq))
 require('tail below 8e-58',tail<iv.mpf('8e-58'))
 def widen(z,e):
  rad=iv.mpf([-1,1])*e
  return z+iv.mpc(rad,rad)
 L0=widen(L0,tail);Lc=widen(Lc,tail);reg=widen(reg,6*tail)
 close('Green integral and exact periodic logarithm',reg-3*(Lc-L0))
 gamma0=iv.exp(L0);gamma=iv.exp(Lc)
 close('eta anchor enclosure',gamma0-eps**2)
 k0=(L0-2*iv.log(eps))/(2*pi*j)
 require('anchor lift real above -3/2',k0.real>-iv.mpf(3)/2)
 require('anchor lift real below -1/2',k0.real<-iv.mpf(1)/2)
 require('actual gamma logarithm above minus pi',Lc.imag>-pi)
 require('actual gamma logarithm below pi',Lc.imag<pi)
 require('regulator imaginary above 3pi',reg.imag>3*pi)
 require('regulator imaginary below 4pi',reg.imag<4*pi)
 close('root-free cubic Green reconstruction',iv.exp(reg)*eps**6-gamma**3)
 close('winding-preserving direct reconstruction',eps**2*iv.exp(reg/3)-gamma)
 # The ray-field value is fixed by the inherited Gauss branch; no fit is made.
 chi=[0,1,omega,omega**2,omega**2,omega,1]
 X=sum(chi[a]*iv.exp(6*pi*j*a/7) for a in range(1,7))/beta
 close('independent Gauss branch satisfies X^3=J',X**3-(2+3*omega))
 nu=(X+beta/X-beta**2)/3;v=-beta**2*nu-2*nu**2
 close('independent cubic coordinate',v**3-beta*v**2+1)
 Y=(4*beta**2+beta-14)*v**2+(11*beta-23)*v-beta**2+3*beta-3
 Z=((-2*beta**2+7*beta-8)*v**2+(-10*beta**2+11*beta+17)*v)/3+7-beta-beta**2
 Ualg=(Y-(1+2*omega)*Z)/2
 Q=lambda u:u**6+(6*beta**2-14*beta+2)*u**5+(4*beta**2-6*beta+2)*u**4+(106*beta**2-152*beta-103)*u**3+(4*beta**2-6*beta+2)*u**2+(6*beta**2-14*beta+2)*u+1
 close('ray unit satisfies inherited sextic enclosure',Q(Ualg))
 ratio=gamma/Ualg;bound=abs(ratio-1)
 require('conditional branch enclosure below 1e-56',bound<iv.mpf('1e-56'))
 require('conditional branch enclosure below one half',bound<iv.mpf(1)/2)
 target=3*iv.log(Ualg)-6*iv.log(eps)+6*pi*j
 delta=reg-target
 require('remaining logarithmic discrepancy bounded',abs(delta)<iv.mpf('1e-55'))
 # A genuine winding twist leaves G and the zero anchor intact but rotates U.
 twisted=omega*gamma
 close('winding-one twist preserves the cube',twisted**3-gamma**3)
 require('wrong winding changes target',abs(twisted/gamma-1)>iv.mpf(3)/2)
 neg.append('winding-one phase changes U while preserving its cube')
 wrong=eps**2*iv.exp(iv.log(iv.exp(reg))/3)
 require('principal log before cube root changes result',abs(wrong/gamma-1)>iv.mpf(3)/2)
 close('principal-log error is exactly omega',wrong/gamma-omega)
 neg.append('principal logarithm before division by three selects wrong root')
 kappa=2*pi*j
 z=iv.mpc(iv.mpf(1)/7,iv.mpf(1)/100)
 norm_twist=iv.exp(kappa*(6*z+2*(1-t+s)))
 require('winding twist violates full doubling norm',abs(norm_twist-1)>iv.mpf('1e-3'))
 neg.append('linear winding twist is not a solution of all gamma norm laws')

 # New independent arithmetic factorization and positivity target.
 a0=(1+omega)*X**2-X+1
 a1=-X**2+(1+omega)*X+1
 a2=-omega*X**2-omega*X+1
 C=eps*a1*a2**3/omega
 Rpos=abs(eps)**4*abs(a1)**6*abs(a2)**4
 palg=C*Ualg**3
 pgamma=C*gamma**3
 close('polarized arithmetic identity enclosure',palg-Rpos)
 require('positive arithmetic normalization',palg.real>0)
 require('positive real part of normalized gamma',pgamma.real>0)
 require('normalized gamma real part above 3.6 million',pgamma.real>3600000)
 require('normalized gamma real part below 3.7 million',pgamma.real<3700000)
 require('normalized reality discrepancy bound',abs(pgamma/Rpos-1)<iv.mpf('1e-55'))
 arith_lift=3*iv.log(Ualg)+iv.log(eps)+iv.log(a1)+3*iv.log(a2)-2*pi*j/3
 require('arithmetic log lift above minus pi',arith_lift.imag>-pi)
 require('arithmetic log lift below pi',arith_lift.imag<pi)
 close('arithmetic positive log identity enclosure',arith_lift-iv.log(Rpos))
 polarized_reg=reg+7*iv.log(eps)+iv.log(a1)+3*iv.log(a2)-20*pi*j/3
 require('new regulator comparison bound',abs(polarized_reg-iv.log(Rpos))<iv.mpf('1e-54'))
 correction=Ualg**3/(eps**3*a2*a1**5)
 require('correction not sixth root numerically',abs(correction**6-1)>iv.mpf('0.1'))
 neg.append('naive holomorphic lift has non-mu6 phase correction; exact checker proves this')
 newdata={'C':C,'Rpos':iv.mpc(Rpos),'polarized_Ualg_cube':palg,'polarized_gamma_cube':pgamma,'normalized_reality_discrepancy':pgamma/Rpos-1,'arithmetic_log_lift':arith_lift,'polarized_regulator_difference':polarized_reg-iv.log(Rpos),'naive_lift_phase_correction':correction}
 rec={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'interval_digits':args.digits,'term_cap':N,'retained_log_terms':retained,'active_regulator_terms':active,'check_count':len(checks),'checks':checks,'negative_controls':neg,'inputs':{'root7_integer_lower':str(k),'sqrt3_integer_lower':str(m),'denominator':str(D),'branch_chi':[0,0,1,2,2,1,0],'zeta':'exp(6 pi i/7)'},'tail_bound':real_interval_endpoints(tail),'bounds':{'ratio_minus_one_norm':real_interval_endpoints(bound),'logarithmic_discrepancy_norm':real_interval_endpoints(abs(delta))},'enclosures':{name:complex_interval(value) for name,value in [('L0',L0),('Lthird',Lc),('regulator3',reg),('anchor_lift_integer',k0),('U_gamma',gamma),('U_alg',Ualg),('ratio',ratio),('phase_log_discrepancy',delta)]},'python':sys.version.split()[0],'mpmath':mp.__version__,'scope':'Directed interval arithmetic includes elementary rounding and explicit uniform infinite tails. Conditional branch separation and integer anchor lift; NOT an equality proof. mpmath.iv is a trusted experimental library, not Lean-certified.'}
 rec['polarization']={k:complex_interval(v) for k,v in newdata.items()}
 rec['scope']+=' New certified positivity of the real part; NOT proof that the normalized gamma expression is real. Arithmetic log lift uses a separately proved exponential identity.'
 (ROOT/f'evidence/interval_{args.digits}.json').write_text(json.dumps(rec,indent=2)+'\n')
 print('PASS',args.digits,'interval digits;',len(checks),'checks;',len(neg),'negative controls')
 print('ratio error enclosure:',bound)
 print('regulator enclosure:',reg)
 print('polarized gamma enclosure:',pgamma)
 print('naive phase correction:',correction)
if __name__=='__main__':main()
