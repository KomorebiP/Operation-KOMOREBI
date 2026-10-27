#!/usr/bin/env python3
"""Regression of exact theta norm identities. Not an interval or algebraicity proof."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,time,mpmath as mp
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dps',type=int,default=50);a=ap.parse_args();mp.mp.dps=a.dps+20
 started=datetime.now(timezone.utc).isoformat();tic=time.perf_counter();tests=[];controls=[]
 def close(name,x,y):
  e=abs(x-y)/max(mp.mpf(1),abs(x),abs(y))
  if e>mp.mpf(10)**(-a.dps+8):raise AssertionError(name+': '+str(e))
  tests.append({'name':name,'relative_error':mp.nstr(e,12)})
 def different(name,x,y):
  e=abs(x-y)/max(mp.mpf(1),abs(x),abs(y))
  if e<mp.mpf('1e-8'):raise AssertionError('negative control failed '+name)
  controls.append({'name':name,'separation':mp.nstr(e,12)})
 om=mp.e**(2j*mp.pi/3);beta=mp.root(7,3)*om**2
 configs=[('generic',mp.mpc('0.23','1.1'),mp.mpc('0.17','0.13'),[1,2,3,4,5,6,7,10]),
          ('cubic',-(beta**2+2*beta)/15,-(beta+2)/15,[2,3,5])]
 for label,t,s,ns in configs:
  q=mp.e**(2j*mp.pi*t);q5=q**5
  @lru_cache(maxsize=None)
  def theta(z):
   # Exact periodicity of the smoothed quotient permits stable representatives.
   z=z-mp.floor(mp.im(z)/mp.im(t))*t;z=z-mp.floor(mp.re(z))
   x=mp.e**(2j*mp.pi*z)
   return (mp.qp(x,q)*mp.qp(q/x,q))**5/(mp.qp(x**5,q5)*mp.qp(q5/x**5,q5))
  def psi(z):return theta(z)**2/(theta(2*z)*theta(2*z+s))
  def factor(z):return theta(z)**4/theta(2*z)
  def norm(n,f,w):return mp.fprod(f((w+j+k*t)/n) for j in range(n) for k in range(n))
  w=mp.mpc('0.127','0.017')
  for n in ns:
   obs=norm(n,psi,w)
   if n%5==0:rhs=mp.mpf(1)
   elif n%2:rhs=theta(w)**2/(theta(2*w)*theta(2*w+n*s))
   else:rhs=1/(theta(w)**2*theta(w+(n//2)*s)**4)
   close(f'{label} kernel norm n={n}',obs,rhs)
   if n%5 and n%2==0:
    k=n//2
    B=lambda z:mp.fprod(theta(z+j*s)**4 for j in range(k))
    close(f'{label} even boundary n={n}',rhs,theta(w)**(-6)*B(w)/B(w+s))
   elif n%5 and n%2:
    k=(n-1)//2
    B=lambda z:mp.fprod(theta(2*z+(2*j+1)*s) for j in range(k))
    close(f'{label} odd boundary n={n}',rhs,psi(w)*B(w)/B(w+s))
  close(label+' rational norm-one factor',norm(2,factor,w),1)
  close(label+' factorization',psi(w),theta(w)**(-6)*factor(w)**2*theta(2*w)/theta(2*w+s))
  aa,bb,cc,dd=[theta(w+eta) for eta in (0,mp.mpf(1)/2,t/2,(1+t)/2)]
  channels=[aa*bb/(cc*dd),aa*cc/(bb*dd),aa*dd/(bb*cc)]
  close(label+' Walsh product reconstructs factor',mp.fprod(channels),factor(w))
  close(label+' Walsh fourth power',aa*bb*cc*dd*mp.fprod(channels),aa**4)
  for j in range(3):
   def ch(z,j=j):
    A,B,C,D=[theta(z+e) for e in (0,mp.mpf(1)/2,t/2,(1+t)/2)]
    return [A*B/(C*D),A*C/(B*D),A*D/(B*C)][j]
   close(f'{label} signed-channel norm {j}',norm(2,ch,w),1)
  different(label+' norm-one does not mean constant',factor(w),1)
  different(label+' smoothing norm is not unsmoothed dilation',norm(5,psi,w),psi(5*w))
 out={'started_at':started,'runtime_seconds':time.perf_counter()-tic,'requested_dps':a.dps,'working_dps':mp.mp.dps,'mpmath':mp.__version__,'equalities':tests,'negative_controls':controls,'scope':'Direct theta products only. No interval arithmetic, no gamma-algebraic comparison.'}
 (ROOT/f'evidence/numerical_{a.dps}.json').write_text(json.dumps(out,indent=2)+'\n')
 print(f'PASS: {len(tests)} theta equalities, {len(controls)} negative controls at {a.dps} digits; max error '+max((v['relative_error'] for v in tests),key=lambda x:mp.mpf(x)))
if __name__=='__main__':main()
