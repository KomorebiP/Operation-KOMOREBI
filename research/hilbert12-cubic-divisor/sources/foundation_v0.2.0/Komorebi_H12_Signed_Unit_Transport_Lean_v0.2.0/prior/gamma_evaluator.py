#!/usr/bin/env python3
"""Gamma-series/theta-product regression. Not directed-rounding certificates.
Run with --digits 60 or --digits 100; no comparison to U_alg is made.
"""
from __future__ import annotations
import argparse,json,platform,sys,time
from datetime import datetime,timezone
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]

class Evaluator:
    def __init__(self,digits):
        self.digits=digits; w=mp.exp(2j*mp.pi/3)
        self.beta=mp.root(7,3)*w*w; self.eps=2-self.beta;self.rho=1/self.eps
        self.t=-(self.beta**2+2*self.beta)/15;self.s=-(self.beta+2)/15
        self.p=mp.exp(2j*mp.pi*self.t);self.q=mp.exp(2j*mp.pi*self.s)
        self.pn=[mp.mpc(1)];self.qn=[mp.mpc(1)];self.weights=[mp.mpc(0)]
        self.logs={};self.values={};self.cutoffs=[];self.tails=[];self.shifts=[]
    def ensure(self,N):
        for n in range(len(self.pn),N+1):
            P=self.pn[-1]*self.p;Q=self.qn[-1]*self.q
            self.pn.append(P);self.qn.append(Q)
            self.weights.append(-5/(n*(1-P)*(1-Q)) if n%5 else mp.mpc(0))
    def logF(self,z):
        z=mp.mpc(z)
        if not -mp.im(self.t)<mp.im(z)<mp.im(self.s):
            raise ValueError('Direct logarithmic series is outside its convergence strip')
        key=z._mpc_
        if key in self.logs:return self.logs[key]
        a=mp.exp(2j*mp.pi*(z+self.t));b=mp.exp(2j*mp.pi*(self.s-z))
        rad=max(abs(a),abs(b))
        N=max(100,int(mp.ceil((self.digits+20)*mp.log(10)/(-mp.log(rad)))))
        def tail(n):
            k=n+1
            return 5/(k*(1-abs(self.p)**k)*(1-abs(self.q)**k))*(abs(a)**k/(1-abs(a))+abs(b)**k/(1-abs(b)))
        while tail(N)>mp.mpf(10)**(-self.digits-12):N+=100
        if N>20000:raise RuntimeError('Explicit 20000-term resource cap exceeded')
        self.ensure(N);an=bn=mp.mpc(1);acc=mp.mpc(0)
        for n in range(1,N+1):
            an*=a;bn*=b
            if n%5:acc+=self.weights[n]*(an-bn)
        self.cutoffs.append(N);self.tails.append(tail(N));self.logs[key]=acc
        return acc
    def theta(self,z,v):
        z=mp.mpc(z);v=mp.mpc(v)
        # Reduce the elliptic quotient Theta_5, not theta0 separately.
        z-=mp.floor(mp.im(z)/mp.im(v))*v;z-=mp.floor(mp.re(z))
        x=mp.exp(2j*mp.pi*z);Q=mp.exp(2j*mp.pi*v)
        return (mp.qp(x,Q)*mp.qp(Q/x,Q))**5/(mp.qp(x**5,Q**5)*mp.qp((Q/x)**5,Q**5))
    def theta_t(self,z):return self.theta(self.eps*z,self.s)
    def F(self,z):
        z=mp.mpc(z);key=z._mpc_
        if key in self.values:return self.values[key]
        if -mp.im(self.t)<mp.im(z)<mp.im(self.s):out=mp.exp(self.logF(z))
        else:
            ks=[k for k in range(-12,13) if -mp.im(self.t)<mp.im(z+k*self.s)<mp.im(self.s)]
            if not ks:raise ValueError('No continuation in declared shift range')
            k=min(ks,key=abs);out=mp.exp(self.logF(z+k*self.s))
            if k>0:
                for j in range(k):out*=self.theta_t(z+j*self.s)
            else:
                for j in range(k,0):out/=self.theta_t(z+j*self.s)
            self.shifts.append({'z':mp.nstr(z,18),'sigma_steps':k})
        self.values[key]=out;return out
    def reflection(self,z):return self.theta_t(z)/self.theta_t(self.rho*z)
    def window(self,k,m):
        a=[0,5,60]
        while len(a)<=m:a.append(12*a[-1]-6*a[-2]+a[-3])
        out=mp.mpc(1)
        for j in range(k*a[m-1],k*a[m]):out*=self.theta_t(mp.mpf(k)/3+j*self.s)
        return out
    def c3(self):
        N=int(mp.ceil((self.digits+30)*mp.log(10)/(-mp.log(abs(self.p)))))
        self.ensure(N)
        return -5*(2j*mp.pi)**3/6*mp.fsum(n*n*(self.pn[n]+self.qn[n])/((1-self.pn[n])*(1-self.qn[n])) for n in range(1,N+1) if n%5)

def run(digits):
    with mp.workdps(digits+25):
        e=Evaluator(digits);ok=[];neg=[];errlist=[];table=[]
        tol=mp.mpf(10)**(-digits+8)
        def near(name,x,y):
            er=abs(x-y)/max(mp.mpf(1),abs(x),abs(y))
            if er>=tol:raise AssertionError((name,mp.nstr(er,20)))
            ok.append(name);errlist.append(er)
        z0=mp.mpf(1)/3;U=e.F(z0);F0=e.eps**2
        near('zero anchor',e.F(0),F0)
        near('negative-third inversion',e.F(-z0)*U,1)
        near('two-thirds inversion',e.F(2*z0)*U,1)
        for z in [z0,mp.mpc('.015','.002'),e.rho/3,e.rho**2/3]:
            near('reflection-dilation '+mp.nstr(z,7),e.F(z)*e.F(-z),e.reflection(z))
        for z in [z0,mp.mpc('.01','.003')]:
            near('direct versus covariance theta '+mp.nstr(z,7),e.theta_t(z),e.theta(z,e.t))
        for m in [1,2]:
            z=e.rho**m/3;P={k:e.window(k,m) for k in [1,2]}
            for k in [1,2]:near(f'theta window k={k},m={m}',P[k],e.F(k*z)/e.F(k*z0))
            near(f'new cubic normal form m={m}',e.reflection(z)*P[1]**2/P[2],e.F(z)**3*e.F(-z)/e.F(2*z)/U**3)
        paired=mp.mpc(1)
        for j in range(5):
            x=z0+j*e.s;paired*=e.theta_t(x)**2/(e.theta_t(2*x)*e.theta_t(2*x+e.s))
        near('doubling kernel regrouping m=1',paired,e.window(1,1)**2/e.window(2,1))
        L0=e.logF(0);c3=e.c3();R=mp.mpf('.008');P=abs(e.p);Q=abs(e.q)
        M=5/((1-P)*(1-Q))*(mp.log((1-P)/(1-P*mp.exp(2*mp.pi*R)))+mp.log((1-Q)/(1-Q*mp.exp(2*mp.pi*R))))
        for m in [4,5,6,7,8,9,10,12,14]:
            z=e.rho**m/3
            delta=3*e.logF(z)+e.logF(-z)-e.logF(2*z)-3*L0
            new=mp.expm1(delta)
            old=mp.expm1(mp.fsum(h*(e.logF(e.rho**(m+j)/3)-L0) for j,h in enumerate([1,-6,12,-1])))
            table.append({'m':m,'old_sixth_relative_error':mp.nstr(abs(old),20),'new_cube_relative_error':mp.nstr(abs(new),20),
                          'scaled_cubic_coefficient':mp.nstr(new/z**3,24)})
            if m in [4,8,12]:
                D=e.reflection(z)*(e.F(z)/U)**2/(e.F(2*z)*U)
                near(f'cubic finite relative error m={m}',D/(F0**3/U**3),mp.exp(delta))
            u=abs(z)/R;eb=M*(4*u**3/(1-u)+(2*u)**3/(1-2*u))
            if not abs(new)<=mp.expm1(eb):raise AssertionError('Cauchy bound regression')
        z=e.rho**14/3;delta=3*e.logF(z)+e.logF(-z)-e.logF(2*z)-3*L0
        if not abs(mp.expm1(delta)/z**3/(-6*c3)-1)<mp.mpf('1e-6'):raise AssertionError('leading cubic coefficient')
        try:e.logF(e.rho/3)
        except ValueError:neg.append('out-of-strip direct series is rejected')
        else:raise AssertionError('missing strip guard')
        z=e.rho/3
        if abs(mp.exp(e.logF(z+e.s))/e.F(z)-1)<mp.mpf('1e-4'):raise AssertionError('continuation factor control')
        neg.append('omitting continuation theta factor fails')
        if abs(e.F(2*z0)/U-1)<mp.mpf('1e-4'):raise AssertionError('wrong conductor class')
        neg.append('two-thirds value is not U')
        z=e.rho**4/3
        if abs(e.reflection(z)/F0**2-1)<mp.mpf('1e-5'):raise AssertionError('premature endpoint limit')
        neg.append('finite reflection endpoint cannot be replaced by its limit')
        return {'digits':digits,'working_digits':digits+25,'equalities':ok,'negative_controls':neg,'cauchy_bound_tests':len(table),
                'max_normalized_equality_error':mp.nstr(max(errlist),15),'max_series_cutoff':max(e.cutoffs),
                'max_reported_analytic_series_tail':mp.nstr(max(e.tails),15),'continuations':e.shifts,
                'rho_abs_cubed':mp.nstr(abs(e.rho)**3,25),'minus_six_c3':mp.nstr(-6*c3,30),'convergence':table,
                'interpretation':'Floating arithmetic regression; analytic tail bounds exclude rounding error. No U_alg equality is tested.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--digits',type=int,choices=[60,100],required=True);args=ap.parse_args()
    start=datetime.now(timezone.utc).isoformat();tic=time.perf_counter();row=run(args.digits)
    out={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'python':sys.version.split()[0],
         'mpmath':mp.__version__,'platform':platform.platform(),'run':row}
    (ROOT/f'evidence/numerical_{args.digits}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(f'PASS {args.digits} digits: {len(row["equalities"])} equalities, {len(row["negative_controls"])} negative controls; max error {row["max_normalized_equality_error"]}; {out["runtime_seconds"]:.2f}s')
if __name__=='__main__':main()
