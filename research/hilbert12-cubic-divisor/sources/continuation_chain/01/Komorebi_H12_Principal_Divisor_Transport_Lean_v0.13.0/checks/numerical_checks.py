#!/usr/bin/env python3
"""Actual gamma-correction regressions. No intervals, equality recognition or U_alg."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,sys,json,time,platform
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'prior'))
from gamma_evaluator import Evaluator
from v012_numerical_checks import PositiveSmoothed

def run(digits,stage):
    with mp.workdps(digits+25):
        e=Evaluator(digits)
        def fasttheta(z,v):
            return e.theta_t(z) if v==e.t else e.theta(z,v)
        p=PositiveSmoothed(digits,fasttheta)
        t,s,beta=e.t,e.s,e.beta;tau=-t;d=(tau+2*s+4)/7
        cache={};ok=[];neg=[];errs=[];rate=[]
        def F(z):return p.F(z,t,s)
        def Q(z):return e.theta_t(z)
        def QS(z):return e.theta(z,s)
        def R(z):
            z=mp.mpc(z);key=z._mpc_
            if key not in cache:cache[key]=mp.fprod(F(z+k*d) for k in range(7))/F(beta*z)
            return cache[key]
        def near(name,x,y):
            if y==0:raise ValueError('relative-error denominator zero')
            er=abs(x/y-1)
            if er>=mp.mpf(10)**(-digits+8):raise AssertionError((name,mp.nstr(er,25)))
            ok.append(name);errs.append(er)
        anchor=mp.fprod(1/Q((t+d)/2+j*d) for j in range(3))
        if stage=="anchor":
            near('gamma-free zero anchor',R(0),anchor)
            near('midpoint gamma reflection anchor',p.S((t+d)/2,t,d),1)
            near('midpoint-to-s three theta shifts',p.S(s,t,d),1/anchor)
            # Inherited evaluator is separately guarded and chooses different continuation steps.
            Rzero_independent=mp.fprod(e.F(k*d) for k in range(7))/e.F(0)
            near('two gamma evaluator zero anchors',R(0),Rzero_independent)
        points={'first':[mp.mpc('.217','.017')], 'second':[mp.mpc('.341','-.002')]}
        for z in points.get(stage,[]):
            rz=R(z);b=beta*z;tag=mp.nstr(z,8)
            near('unit-period transition '+tag,R(z+1)/rz,1/mp.fprod(Q(b-j*s) for j in range(1,16)))
            near('s-period transition '+tag,R(z+s)/rz,QS(b-tau)/mp.fprod(Q(z+k*d) for k in range(7)))
            near('tau-period transition '+tag,R(z+tau)/rz,
                 mp.fprod(QS(z+k*d) for k in range(7))*mp.fprod(Q(b+j*s) for j in range(4))/(QS(b)*QS(b+tau)))
            near('seventh transition '+tag,R(z+d)/rz,
                 QS(z)/(Q(z)*Q(z+s)*mp.fprod(Q(b-j*s) for j in range(1,9))))
            rhs=p.S(z,s,d)/(p.S(z,t,d)*p.S(z+s,t,d)*F(b))
            near('direct versus three-factor correction '+tag,rz,rhs)
        if stage=="divisor":
            # Ratios at shrinking offsets independently diagnose signed divisor orders.
            off=mp.mpf('1e-8')
            for label,z0,order in [('tau',tau,4),('s',s,-4),('negative integer',-1,4)]:
                er=abs((R(z0+off)/R(z0+2*off))*mp.mpf(2)**order-1)
                if er>=mp.mpf('1e-3'):raise AssertionError(('divisor diagnostic',label,mp.nstr(er,20)))
                rate.append({'point':label,'order':order,'offset':'1e-8','error':mp.nstr(er,18)})
            # The conjugate ratio remains singular at tau. This is not an equality claim.
            def phaseR(z):return R(z)/mp.conj(R(mp.conj(z)))
            er=abs(16*phaseR(tau+off)/phaseR(tau+2*off)-1)
            if er>=mp.mpf('1e-3'):raise AssertionError(('phase divisor diagnostic',mp.nstr(er,20)))
            rate.append({'point':'tau in conjugate quotient','order':4,'offset':'1e-8','error':mp.nstr(er,18)})
        if stage=="first":
            z=mp.mpc('.217','.017')
            for name,err in [
                ('constant correction fails',abs(R(z)/R(0)-1)),
                ('period-one invariance fails',abs(R(z+1)/R(z)-1)),
                ('erasing zero-anchor phase fails',abs(anchor/abs(anchor)-1)),
                ('zero anchor cannot be silently set to one',abs(anchor-1))]:
                if err<=mp.mpf('1e-5'):raise AssertionError(name)
                neg.append(name)
        return {'stage':stage,'digits':digits,'working_digits':digits+25,'identities':ok,'negative_controls':neg,
          'divisor_diagnostics':rate,'max_relative_error':mp.nstr(max(errs,default=0),22),
          'anchor':mp.nstr(anchor,45),'max_positive_gamma_cutoff':max(p.cutoffs,default=0),
          'max_positive_log_tail':mp.nstr(max(p.tails,default=0),22),'positive_continuation_range':[min(p.continuations,default=0),max(p.continuations,default=0)],
          'max_independent_cutoff':max(e.cutoffs,default=0),'max_independent_log_tail':mp.nstr(max(e.tails,default=0),22),
          'scope':'Floating regression with separate truncation bounds, not directed-rounding certificates. The exact divisor statements have ordinary proofs and formal integer identities. No U_alg is evaluated.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--digits',type=int,choices=[40,70],required=True);ap.add_argument("--stage",choices=["anchor","first","second","divisor"],required=True);a=ap.parse_args()
    start=datetime.now(timezone.utc).isoformat();tic=time.monotonic();r=run(a.digits,a.stage)
    r.update(started_at=start,runtime_seconds=time.monotonic()-tic,exit_status=0,mpmath=mp.__version__,python=sys.version.split()[0],platform=platform.platform())
    (ROOT/f'evidence/numerical_{a.digits}_{a.stage}.json').write_text(json.dumps(r,indent=2)+'\n')
    print('PASS',a.digits,len(r['identities']),'identities,',len(r['divisor_diagnostics']),'divisor diagnostics,',len(r['negative_controls']),'negative controls. Max relative error',r['max_relative_error'],'seconds',round(r['runtime_seconds'],3))
