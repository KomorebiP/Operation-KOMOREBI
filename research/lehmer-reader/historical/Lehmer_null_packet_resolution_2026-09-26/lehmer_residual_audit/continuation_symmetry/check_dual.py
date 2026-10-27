from pathlib import Path
import sys,json,math
from fractions import Fraction
import numpy as np
import sympy as s
from scipy.optimize import linprog
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent/'continuation_5core'))
from explore_shell import shell,weight
K=json.load(open(H/'KERNELS.json'))
def ev(k,v):
 pp=[sum(x**i for x in v) for i in range(2,6)]
 return sum(c*math.prod(x**a for x,a in zip(pp,ex)) for ex,c in k['terms'])
rows=[];seen=set()
for v in shell(31):
 Q=tuple(ev(k,v) for k in K);w=weight(v);sg=1 if w>0 else -1
 if (Q,sg) not in seen:rows.append((v,w,sg,Q));seen.add((Q,sg))
m=len(rows);B=[[x[2] for x in rows]]+[[x[2]*x[3][j] for x in rows] for j in range(len(K))]
AA=[[float(Fraction(v,max(map(abs,row)))) for v in row]+[0] for row in B]+[[1.0]*m+[0]]
rr=linprog([0]*m+[-1],A_ub=[[-int(i==j) for j in range(m)]+[1] for i in range(m)],b_ub=[0]*m,A_eq=AA,b_eq=[0]*len(B)+[1],bounds=[(0,None)]*m+[(0,None)],method='highs')
print('proposal',rr.success,rr.message,'margin',rr.x[-1] if rr.success else None)
assert rr.success and rr.x[-1]>1e-8
M=s.Matrix(B+[[1]*m]);target=s.Matrix([0]*len(B)+[1]);R,piv=M.row_join(target).rref();assert m not in piv
free=[i for i in range(m) if i not in piv]
y=[s.Rational(0)]*m
for i in free:y[i]=s.Rational(str(round(float(rr.x[i]),10)))
for row,col in enumerate(piv):y[col]=R[row,m]-sum(R[row,j]*y[j] for j in free)
assert M*s.Matrix(y)==target and all(q>0 for q in y)
out={'p':31,'status':'EXACT POSITIVE DUAL VERIFIED','max_invariant_degree':16,'kernel_count':len(K),'groups':m,'rank':M.rank(),'weights':[[int(a.p),int(a.q)] for a in y],'points':[list(a[0]) for a in rows],'signs':[a[2] for a in rows],'statement':'All weights positive, sum=1, sum y_i sign(W_i)=0, sum y_i sign(W_i) Q_j(v_i)=0 for all seven kernels. Hence no nontrivial all-one-sign reweighting 1+sum a_j Q_j at p31 in this span.'}
(H/'DUAL_31.json').write_text(json.dumps(out,indent=2));print('EXACT',m,'groups',len(K),'kernels',M.rank(),'rank','min',min(y))
