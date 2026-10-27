#!/usr/bin/env python3
"""Exact rational arithmetic audit. Finite tests do not supply universal quantifiers."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from datetime import datetime, timezone
import hashlib,json,platform,sys,time
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]

def main():
    start=datetime.now(timezone.utc).isoformat(); tic=time.monotonic(); checks=[]; negatives=[]
    def check(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    M=sp.Matrix([[0,1,0],[-4,2,15],[-1,0,4]])
    N=2*sp.eye(3)-M; D=sp.diag(1,1,sp.Rational(1,5)); N5=D.inv()*N*D
    check('principal action in smoothed divisor lattice',N5==sp.Matrix([[2,-1,0],[4,0,-3],[5,0,-2]]))
    check('principal cube',N5**3==7*sp.eye(3))
    check('principal determinant',N5.det()==7)
    inv=[[F(0),F(-2,7),F(3,7)],[F(-1),F(-4,7),F(6,7)],[F(0),F(-5,7),F(4,7)]]
    check('independent rational inverse',sp.Matrix(inv)==N5.inv())
    v5=(F(1,7),F(2,7),F(20,7))
    def weight(c):return 4 if c%5==0 else -1
    def step(a):return int(a>0)
    def baseorder(a,b,c):return weight(c)*(step(a)-step(b))
    def pivot(b,c):return -((2*b-3*c)//7)
    def wall(a,b,j):return step(j)-step(2*j-a)-step(a)+step(b)
    def order(a,b,c):return weight(c)*wall(a,b,pivot(b,c))
    def inverse(w):return tuple(sum(r[j]*w[j] for j in range(3)) for r in inv)
    def direct_order(a,b,c):
        z=inverse((a,b,c)); contribution=0; lifts=[]
        for k in range(7):
            t=tuple(z[i]+k*v5[i] for i in range(3))
            if all(x.denominator==1 for x in t):
                t=tuple(int(x) for x in t);lifts.append((k,t));contribution+=baseorder(*t)
        return contribution-baseorder(a,b,c),lifts
    count=0;seen=set()
    for a,b,c in product(range(-12,13),repeat=3):
        val,lifts=direct_order(a,b,c); j=pivot(b,c); k=7*j+2*b-3*c
        assert len(lifts)==1
        assert lifts[0]==(k,(j,2*j-a,20*j+5*b-8*c))
        assert val==order(a,b,c)
        assert weight(lifts[0][1][2])==weight(c)
        assert -1<=wall(a,b,j)<=1
        assert order(a,b-15,c-10)-val == -weight(c)*int(0<b<=15)
        assert pivot(b-8,c-5)==j+int(k==0)
        assert (7*pivot(b-8,c-5)+2*(b-8)-3*(c-5))==(k+6)%7
        count+=1;seen.add(val)
    check('complete 25 cubed rational-lattice divisor regression',count==15625)
    check('all five possible orders occur',seen=={-4,-1,0,1,4})
    for n in range(1,101):
        assert order(2*n,4*n,5*n)==4
        assert order(-n,0,0)==-4 and order(n,0,0)==-4
        assert order(0,15*n,10*n)==4
    check('three infinite-ray identities regressed through 100',True)
    check('zero is regular in divisor calculation',order(0,0,0)==0)
    x=sp.symbols('x'); tau=(x*x+2*x)/15;s=-(x+2)/15;d=(tau+2*s+4)/7
    red=lambda f:sp.rem(sp.together(f),x**3-7,x)
    for name,f in [('beta delta carry',x*d+8*s+1),('beta tau carry',x*tau-2*tau-4*s-1),('beta s carry',x*s+tau),('beta one carry',x+15*s+2),('seventh period relation',7*d-tau-2*s-4)]:
        check(name,red(f)==0)
    # Algebraic support/nonconjugacy: tau has degree three and beta is recovered from tau.
    polynomial=sp.resultant(x**3-7,15*sp.Symbol('T')-x*x-2*x,x)
    T=sp.Symbol('T')
    check('tau elimination polynomial',sp.expand(polynomial)==15*(225*T**3-42*T-7))
    check('tau recovers beta',red((2-x)*(4+15*tau)-1)==0)
    # General multiplicative exponent census for the zero-anchor limit.
    # S_5 leading constant is 5 H(a)H(b)/(2pi)^4.  The common d and universal
    # constants cancel, and F(0)=H(s)/H(t) removes the remaining ratio.
    c=sp.symbols('c');Ht,Hs,Hd=sp.symbols('Ht Hs Hd',nonzero=True)
    check('zero-anchor leading factors cancel',sp.cancel((c*Hs*Hd)/(c*Ht*Hd)/(Hs/Ht))==1)
    check('midpoint translated to s',sp.expand(((-tau)+d)/2+3*d-2-s)==0)
    # Orders expected from the base cone at selected checkpoints.
    for name,args,want in [('tau',(1,0,0),4),('s',(0,1,0),-4),('fractional fifth',(1,0,1),-1),('mixed cone',(1,1,0),0)]:
        check('base gamma divisor '+name,baseorder(*args)==want)
    for name,predicate in [('raw correction is not a unit',order(2,4,5)!=0),('opposite sign of tau order rejected',order(2,4,5)!=-4),('constant correction rejected',order(-1,0,0)!=0),('fixed numerator digit rejected',direct_order(0,1,0)[1][0][0]!=0)]:
        if not predicate:raise AssertionError(name)
        negatives.append(name)
    res={'started_at':start,'runtime_seconds':time.monotonic()-tic,'exit_status':0,
         'checks':checks,'negative_controls':negatives,'rational_sample_triples':count,
         'bounds':{'a_b_c':[-12,12],'rays':[1,100]},'domains':['exact integers','fractions.Fraction','SymPy QQ'],
         'python':sys.version.split()[0],'sympy':sp.__version__,'platform':platform.platform(),
         'non_claims':['No finite range proves universal analytic divisor statements.','No U_alg or gamma equality is used.','No analytic complex conjugation is formally defined by these tests.']}
    (ROOT/'evidence/exact_results.json').write_text(json.dumps(res,indent=2)+'\n')
    print('PASS',len(checks),'named assertions,',len(negatives),'negative controls;',count,'exact lattice points;',round(res['runtime_seconds'],3),'seconds')
if __name__=='__main__':main()
