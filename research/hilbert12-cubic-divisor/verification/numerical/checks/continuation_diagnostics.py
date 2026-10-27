"""Record exact finite guard triggers and validate the centered continuation on overlap."""
from pathlib import Path
import argparse,datetime,json,sys,time
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'dependencies'));sys.path.insert(0,str(root/'v014_copy/prior'))
import mpmath as mp
from gamma_evaluator import Evaluator
ap=argparse.ArgumentParser();ap.add_argument('--result',type=Path,required=True);a=ap.parse_args();tic=time.monotonic()
with mp.workdps(80):
 e=Evaluator(50);t,s=e.t,e.s;Q=lambda z:e.theta(z,t)
 def Gamma(z):
  ks=[k for k in range(-40,41) if -mp.im(t)<mp.im(z+k*s)<mp.im(s)]
  assert ks
  k=min(ks,key=lambda k:abs(mp.im(z+k*s)-(mp.im(s)-mp.im(t))/2))
  out=mp.exp(e.logF(z+k*s))
  if k>0:
   for j in range(k):out*=Q(z+j*s)
  else:
   for j in range(k,0):out/=Q(z+j*s)
  return out,k
 triggers=[]
 z=e.beta*(mp.mpc('.173','.013')+1)
 try:e.F(z)
 except ValueError as error:message=str(error)
 else:raise AssertionError('expected fixed-window failure')
 assert message=='No continuation in declared shift range'
 _,k=Gamma(z)
 triggers.append({'run':'independent','failed_argument_definition':'beta*(1 + (0.173 + 0.013*i))','failed_argument':mp.nstr(z,75),'exception':'ValueError','message':message,'old_shift_window':[-12,12],'centered_shift':k})
 z=mp.mpc('.307','-.009')
 C=mp.exp(2j*mp.pi*(z+t));D=mp.exp(2j*mp.pi*(s-z));rad=max(abs(C),abs(D))
 initial_N=max(100,int(mp.ceil(70*mp.log(10)/(-mp.log(rad)))))
 try:e.logF(z)
 except RuntimeError as error:message=str(error)
 else:raise AssertionError('expected series-cap failure')
 assert message=='Explicit 20000-term resource cap exceeded'
 _,k=Gamma(z)
 triggers.append({'run':'independent_final','failed_argument_definition':'0.307 - 0.009*i (second new test point, numerator k=0)','failed_argument':mp.nstr(z,75),'exception':'RuntimeError','message':message,'minimum_shift':0,'predicted_initial_series_cutoff':initial_N,'series_cap':20000,'centered_shift':k})
 rows=[]
 for z in [mp.mpc('.217','.017'),mp.mpc('.307','-.006'),mp.mpf(0)]:
  alternate,k=Gamma(z);original=e.F(z);error=abs(alternate/original-1)
  assert error<mp.mpf('1e-42'),mp.nstr(error,25)
  rows.append({'argument':mp.nstr(z,60),'centered_shift':k,'relative_error':mp.nstr(error,25)})
 out={'result':'PASS','failures':triggers,'overlap_checks':rows,'working_digits':80,'series_design_digits':50,'relative_tolerance':'1e-42','max_overlap_error':mp.nstr(max(mp.mpf(x['relative_error']) for x in rows),25),'max_gamma_cutoff':max(e.cutoffs),'runtime_seconds':time.monotonic()-tic,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'derivation':'From F(z+s)=F(z)/q_t(z): for k>0, F(z)=F(z+ks)*product_(j=0)^(k-1)q_t(z+js); for k<0, F(z)=F(z+ks)/product_(j=k)^(-1)q_t(z+js). The direct logarithmic series is used only in its original open strip. Changing the representative does not change the meromorphic definition; overlapping admitted evaluations agree in the stated floating tests.','scope':'Finite guard diagnosis and floating overlap regression, not a universal analytic or rounding certificate.'}
a.result.write_text(json.dumps(out,indent=2)+'\n');print('PASS two exact guard triggers and three overlap comparisons; max error',out['max_overlap_error'])
