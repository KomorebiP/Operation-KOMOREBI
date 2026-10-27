#!/usr/bin/env python3
"""Independent smoothed-gamma series and continuation checks.
These are floating regressions with recorded truncation bounds, NOT interval
certificates. No U_alg is used, recognized, or fitted.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,sys,json,time,platform
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'prior'))
from gamma_evaluator import Evaluator

class PositiveSmoothed:
    def __init__(self,digits,theta):
        self.digits=digits;self.theta=theta;self.cache={};self.cutoffs=[];self.tails=[];self.continuations=[]
    def S(self,z,a,b):
        z,a,b=map(mp.mpc,(z,a,b));key=(z._mpc_,a._mpc_,b._mpc_)
        if key in self.cache:return self.cache[key]
        if not (mp.im(a)>0 and mp.im(b)>0):raise ValueError('positive periods required')
        step,other=(a,b) if mp.im(a)>mp.im(b) else (b,a)
        k=int(mp.nint(((mp.im(a)+mp.im(b))/2-mp.im(z))/mp.im(step)))
        w=z+k*step
        if not 0<mp.im(w)<mp.im(a+b):raise ValueError('continuation failed to enter open convergence strip')
        A=mp.exp(2j*mp.pi*a);B=mp.exp(2j*mp.pi*b)
        C=mp.exp(2j*mp.pi*w);D=A*B/C;rad=max(abs(C),abs(D))
        nmax=max(100,int(mp.ceil((self.digits+20)*mp.log(10)/(-mp.log(rad)))))
        def tail(n):
            j=n+1
            return 5/(j*(1-abs(A)**j)*(1-abs(B)**j))*(abs(C)**j/(1-abs(C))+abs(D)**j/(1-abs(D)))
        while tail(nmax)>mp.mpf(10)**(-self.digits-12):nmax+=100
        if nmax>20000:raise RuntimeError('20000-term cap exceeded')
        an=bn=cn=dn=mp.mpc(1);acc=mp.mpc(0)
        for n in range(1,nmax+1):
            an*=A;bn*=B;cn*=C;dn*=D
            if n%5:acc+=5*(cn-dn)/(n*(1-an)*(1-bn))
        val=mp.exp(acc)
        if k>0:
            for j in range(k):val/=self.theta(z+j*step,other)
        elif k<0:
            for j in range(k,0):val*=self.theta(z+j*step,other)
        self.cache[key]=val;self.cutoffs.append(nmax);self.tails.append(tail(nmax))
        self.continuations.append(k)
        return val
    def F(self,z,t,s):return 1/self.S(z+t,t,s)

def run(digits):
    with mp.workdps(digits+25):
        e=Evaluator(digits);p=PositiveSmoothed(digits,e.theta);ok=[];negative=[];errors=[];illustrations=[]
        tol=mp.mpf(10)**(-digits+8)
        def near(name,x,y):
            err=abs(x-y)/max(mp.mpf(1),abs(x),abs(y))
            if err>=tol:raise AssertionError((name,mp.nstr(err,20)))
            ok.append(name);errors.append(err)
        z0=mp.mpf(1)/3;delta=(-e.t+2*e.s+4)/7
        near('actual beta delta carry',e.beta*delta,-8*e.s-1)
        near('actual principal third carry',e.beta/3,z0-5*e.s-1)
        for z in [z0,mp.mpc('.217','.001')]:
            vals=[e.F(z+k*delta) for k in range(7)]
            for k in range(7):near('independent gamma continuation '+str(k)+' '+mp.nstr(z,6),vals[k],p.F(z+k*delta,e.t,e.s))
            lhs=mp.fprod(vals)
            rhs=p.S(z,e.s,delta)/(p.S(z,e.t,delta)*p.S(z+e.s,e.t,delta))
            near('actual seven-point norm '+mp.nstr(z,6),lhs,rhs)
            wrong=e.F(e.beta*z)
            if abs(lhs/wrong-1)<mp.mpf('1e-4'):raise AssertionError('naive principal norm control')
            negative.append('naive equality to F(beta*z) fails at '+mp.nstr(z,6))
            illustrations.append({'z':mp.nstr(z,25),'product':mp.nstr(lhs,45),'naive_norm_ratio':mp.nstr(lhs/wrong,30)})
        # A nonempty common convergence chamber independently checks the analytic continuation seed.
        s=mp.mpc('.37','.4');d=mp.mpc('.11','.04');t=2*s+4-7*d
        for z in [mp.mpc('.217','.031'),mp.mpc('.319','.06')]:
            lhs=mp.fprod(p.F(z+k*d,t,s) for k in range(7))
            rhs=p.S(z,s,d)/(p.S(z,t,d)*p.S(z+s,t,d))
            near('generic convergence-chamber norm '+mp.nstr(z,6),lhs,rhs)
        # Actual unit permutation of the principal kernel: rho v/7 = 4v/7+(8,-1,0).
        for k in range(7):
            r=(4*k)%7;m=(4*k)//7
            A=5+8*k+m;B=-k+2*m;C=1+4*m
            w=z0+k*delta;wr=z0+r*delta
            near('rho seven-label carry '+str(k),e.rho*w,wr-A*e.t+B*e.s+C)
        try:p.S(z0,-e.t,e.s)
        except ValueError:negative.append('positive-period guard rejects negative input period')
        else:raise AssertionError('missing period guard')
        return {'digits':digits,'working_digits':digits+25,'equalities':ok,'negative_controls':negative,
            'max_normalized_error':mp.nstr(max(errors),18),'positive_gamma_max_cutoff':max(p.cutoffs),
            'positive_gamma_max_series_tail':mp.nstr(max(p.tails),18),'inherited_gamma_max_cutoff':max(e.cutoffs),
            'inherited_gamma_max_series_tail':mp.nstr(max(e.tails),18),'continuation_shift_range':[min(p.continuations),max(p.continuations)],
            'illustrations':illustrations,'interpretation':'Floating regression, not a directed-rounding enclosure. Series tails do not bound rounding. No algebraic candidate evaluated.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--digits',type=int,choices=[40,70],required=True);args=ap.parse_args()
    start=datetime.now(timezone.utc).isoformat();tic=time.monotonic();r=run(args.digits)
    r.update(started_at=start,runtime_seconds=time.monotonic()-tic,exit_status=0,mpmath=mp.__version__,python=sys.version.split()[0],platform=platform.platform())
    (ROOT/f'evidence/numerical_{args.digits}.json').write_text(json.dumps(r,indent=2)+'\n')
    print('PASS',args.digits,len(r['equalities']),'equalities',len(r['negative_controls']),'negative controls; max error',r['max_normalized_error'],'seconds',r['runtime_seconds'])
