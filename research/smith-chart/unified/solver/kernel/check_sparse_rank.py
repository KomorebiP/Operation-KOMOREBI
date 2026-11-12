"""Author: Komorebi P. Exact full-rank test for two q=3 seven-element graphs.
The genericity/implicit-function argument is prior-art in RLC synthesis.
"""
import sympy as S,json,time
from pathlib import Path
from sparse_q3_templates import TEMPLATES
s=S.Symbol('s')
POINTS={
 'bridgeA_2L1C_4R':['1/3','1/4','1','1/3','1/4','1/5','1'],
 'bridgeB_1L2C_4R':['1/4','1','4','1/5','1/2','1/4','1/2'],
}
EXPECTED={'bridgeA_2L1C_4R':S.Rational(801,134456),
 'bridgeB_1L2C_4R':-S.Rational(2299,2097152000)}

def check():
 result={}
 for name,spec in TEMPLATES.items():
  t=time.perf_counter();v=S.symbols('x0:'+str(len(spec)));M=S.zeros(3)
  nl=sum(t=='L' for t,_,_ in spec)
  for z,(typ,a,b) in zip(v,spec):
   y=z if typ=='R' else z*s if typ=='C' else z/s
   if a:M[a-1,a-1]+=y
   if b:M[b-1,b-1]+=y
   if a and b:M[a-1,b-1]-=y;M[b-1,a-1]-=y
  N=S.Poly(S.cancel(s**nl*M.minor_submatrix(0,0).det()),s)
  D=S.Poly(S.cancel(s**nl*M.det()),s)
  assert N.degree()==3 and D.degree()==3
  coords=S.Matrix([N.nth(i)/N.nth(3) for i in range(3)]+[D.nth(i)/N.nth(3) for i in range(4)])
  point={z:S.Rational(x) for z,x in zip(v,POINTS[name])}
  det=S.factor(coords.jacobian(v).subs(point).det())
  assert det==EXPECTED[name],(name,det,EXPECTED[name])
  result[name]={'jacobian_determinant':str(det),'nonzero':True,
                'reactive_elements':3,'total_elements':7,
                'proof':'exact symbolic derivative and rational determinant',
                'elapsed_seconds':time.perf_counter()-t}
 return {'status':'PASS','templates':result,
         'scope':'local full-dimensional coefficient images, not all degree-three impedances'}

if __name__=='__main__':
 r=check();print(json.dumps(r,indent=2))
 (Path(__file__).parents[1]/'results/sparse_rank.json').write_text(json.dumps(r,indent=2))
