#!/usr/bin/env python3
"""Independent finite exact checks of the rounded enclosure implementation."""
from __future__ import annotations
import json, itertools, hashlib, platform, time
from fractions import Fraction as Q
from pathlib import Path
import sympy as sp
from exact_certificate import Model, matrix, eye, zero, mul, trans, sub, vec_energy
from rounded_certificate import Ball, down, up, rexact, radd, rsub, rmul, produce

ROOT=Path(__file__).resolve().parents[1]
def sym(a):return sp.Matrix([[sp.Rational(x.numerator,x.denominator) for x in row] for row in a])
def fq(x):return Q(int(x.p),int(x.q))
def run():
    started=time.time();checks=0;cases=0;negative=0
    def check(p):
        nonlocal checks
        assert p;checks+=1
    vals=list(map(Q,['-7/3','-1/5','0','1/7','5/2']))
    for p,x,y in itertools.product([0,1,4,12],vals,vals):
        a=Ball(x,Q(1,10));b=Ball(y,Q(1,7))
        for z in [x-a.radius,x,x+a.radius]:
            for w in [y-b.radius,y,y+b.radius]:
                check(radd(p,a,b).encloses(z+w));check(rsub(p,a,b).encloses(z-w));check(rmul(p,a,b).encloses(z*w))
        for z in (x,y):
            check(down(p,z)<=z<=up(p,z));check(rexact(p,z).encloses(z))
    for n,k in itertools.product(range(1,4),range(1,4)):
        h=tuple(tuple(Q((i+2*j)%5-2,3) for j in range(n)) for i in range(k))
        l=tuple(tuple(Q((i+j)%3-1,5) for j in range(n)) for i in range(n))
        z=tuple(tuple(Q((i+2*j)%3-1,7) for j in range(k)) for i in range(k))
        mean=tuple(Q(i-1,3) for i in range(n));obs=tuple(Q(i+1,5) for i in range(k))
        m=Model(h,l,z,Q(2,3),mean,obs,(eye(n),),(eye(k),))
        gain=tuple(tuple(Q((2*i+j)%5-1,11) for j in range(k)) for i in range(n))
        H,L,N,B=sym(h),sym(l),sym(z),sym(gain)
        P=L*L.T;R=N*N.T+sp.Rational(2,3)*sp.eye(k);S=H*P*H.T+R;F=P*H.T-B*S
        v=sp.Matrix([sp.Rational(x.numerator,x.denominator) for x in obs])-H*sp.Matrix([sp.Rational(x.numerator,x.denominator) for x in mean])
        true={'prior':P,'noise':R,'innovation':S,'residual':F,'innovation_vector':v,'packet_0_0':F}
        for p in [0,4,12]:
            c,t=produce(m,gain,p);cases+=1
            for key,mat in true.items():
                ballmat=t[key]
                for i in range(mat.rows):
                    for j in range(mat.cols):
                        a=ballmat[i][j];x=fq(mat[i,j]);check(a.encloses(x));check(x*x<=a.upper())
                        check((a.center*(1<<p)).denominator==1);check((a.radius*(1<<p)).denominator==1)
            check(c.valid(m));check(fq(sp.trace(F*F.T))<=c.total());check(fq((v.T*v)[0])<=c.innovation_upper)
    for name in ['scalar','rotated']:
        d=json.loads((ROOT/f'examples/rounded_{name}.json').read_text());m=Model.parse(d['model']);g=matrix(d['gain'],'gain');e=Q(d['epsilon'])
        low,lt=produce(m,g,4);high,ht=produce(m,g,12)
        check(not low.tolerance(m,e));check(high.tolerance(m,e));check(low.valid(m));check(high.valid(m))
        if name=='scalar':
            check(lt['residual'][0][0].center==0);check(m.residual(g)[0][0]==Q(-1,1024));check(lt['residual'][0][0].radius==Q(1,8))
            check(not Ball(Q(0),Q(0)).encloses(m.residual(g)[0][0]))
    badprec=[-1,True,1.5,513,'12']
    for p in badprec:
        try:produce(m,g,p)
        except ValueError:negative+=1
        else:raise AssertionError('Bad precision accepted')
    for x in [0.1,True,None]:
        from exact_certificate import rational
        try:rational(x)
        except ValueError:negative+=1
        else:raise AssertionError('Bad rational accepted')
    result={'status':'PASS','matrix_cases':cases,'dimension_pairs':9,'precisions':[0,4,12],
      'assertions':checks,'negative_inputs_rejected':negative,'arithmetic':'Exact Fraction plus independent SymPy matrix expressions',
      'sympy':sp.__version__,'python':platform.python_version(),'seconds':round(time.time()-started,4),
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'implementation_sha256':{n:hashlib.sha256((ROOT/'checks'/n).read_bytes()).hexdigest() for n in ['rounded_certificate.py','exact_certificate.py']},
      'non_claims':['Finite diagnostics, not a universal proof','No hardware floating-point or uncertainty guarantee']}
    (ROOT/'results/exact_rounding_tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run()
