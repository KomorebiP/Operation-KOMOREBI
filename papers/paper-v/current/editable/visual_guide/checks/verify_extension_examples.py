#!/usr/bin/env python3
"""Finite exact arithmetic for the new worked pages V28--V39; no universal-proof claim."""
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import json,hashlib,sys,argparse
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,condition,evidence=None):
 if not condition: raise AssertionError(name)
 checks.append({'name':name,'status':'PASS','evidence':evidence})
# Coset address example and finite signed address enumeration.
check('negative lattice address',(-1%2,7%3,-1//2,7//3)==(1,1,-1,2))
addresses=[(i,j)for i in range(-12,13)for j in range(-12,13)]
check('625 signed two-dimensional addresses reconstruct',all((i%2+2*(i//2),j%3+3*(j//3))==(i,j)for i,j in addresses))
children={(1,2),(3,2),(1,5),(3,5)}
check('four fine descendants partition selected coarse class',all(((i%2,j%3)==(1,2))==((i%4,j%6)in children)for i,j in addresses))
# Diagonal bank quantities are exact singular values.
check('frame squares',(F(3,4)**2,F(9,4)**2)==(F(9,16),F(81,16)))
check('canonical noise amplification',F(4,3)*F(3,4)==1)
check('old synthesis defect',(F(3,4)-1,F(1,2)*F(9,4)-1)==(-F(1,4),F(1,8)))
check('mixed tree lower bound',F(1,2)*min(1,F(3,4))==F(3,8))
check('mixed tree upper bound',2*max(1,F(5,4))==F(5,2))
# Piecewise trace arithmetic. f(t)=t^2 +2H_(1/3)-3(t-2/3)_+.
check('trace value jump at one third',(F(1,9)+2)-F(1,9)==2)
check('trace derivative jump at two thirds',(F(4,3)-3)-F(4,3)==-3)
check('trace remainder equality on finite rational mesh',all((F(k,60)**2+(2 if F(k,60)>=F(1,3)else 0)-3*max(0,F(k,60)-F(2,3)))-( (2 if F(k,60)>=F(1,3)else 0)-3*max(0,F(k,60)-F(2,3)))==F(k,60)**2 for k in range(61)))
def matmul(A,B):return [[sum(x*y for x,y in zip(row,col))for col in zip(*B)]for row in A]
Q=[[1,2],[0,0]]
check('oblique projection idempotence',matmul(Q,Q)==Q)
check('oblique projection residual',matmul(Q,[[1],[1]])==[[3],[0]])
check('amplified squared norm',(-2)**2+1**2==5)
M=[[3,1,0],[0,2,1],[1,0,4]];a=[0,2,5]
check('overlap marginals',[sum(r)for r in M]==[4,3,5]and[sum(c)for c in zip(*M)]==[4,3,5])
check('overlap L1',sum(abs(a[i]-a[j])*M[i][j]for i in range(3)for j in range(3))==10)
check('overlap squared L2',sum((a[i]-a[j])**2*M[i][j]for i in range(3)for j in range(3))==38)
check('overlap MSE',F(38,12)==F(19,6))
d=F(1,16);u=F(5,16)
check('step squared L2',d==F(1,4)**2)
check('ramp integral',d**3/3+(1-u)*d**2==F(17,6144))
check('ramp Lipschitz bound',F(17,6144)<d*d)
h=F(1,256);smooth=F(1,2);noise=F(1,500);amin=F(2,25);theta=F(1,25);b=smooth*h+2*noise
check('deterministic contrast budget',b==F(381,64000))
check('strict deterministic threshold',b<theta<amin-b)
check('deterministic midpoint error',h/2==F(1,512))
# Positive Taylor terms give a rigorous lower bound on exp(10).
partial=sum(F(10**k,factorial(k))for k in range(16))
check('Taylor lower bound exp10 greater than10240',partial>10240,str(partial))
check('square-root conservative bound',F(16,5)**2>10)
repbound=F(1,256)+F(1,50)*F(16,5)
check('R16 sufficient probability budget',repbound==F(2173,32000)and repbound<amin)
L=F(1,4);sqrtL=F(1,2);smoothhaar=L*sqrtL/4;noisehaar=F(1,100)*sqrtL
check('Haar smooth plus noise',smoothhaar+noisehaar==F(29,800))
check('Haar lower jump margin',F(1,4)*sqrtL-smoothhaar-noisehaar==F(71,800))
check('Haar threshold separates',F(29,800)<F(1,16)<F(71,800))
# Exact finite sampling checks the displayed geometry; source theorem proves all positions.
def distance(u,shift):
 v=(u-shift)%1
 return min(v,1-v)
check('401 rational positions satisfy two-grid guarantee',all(max(distance(F(k,400),0),distance(F(k,400),F(1,2)))>=F(1,4)for k in range(401)))
check('one eighth margins',(distance(F(1,8),0),distance(F(1,8),F(1,2)))==(F(1,8),F(3,8)))
check('quarter position sharp',(distance(F(1,4),0),distance(F(1,4),F(1,2)))==(F(1,4),F(1,4)))
check('two-grid analytic gap',F(1,4)>F(2,100)+F(1,2)*L==F(29,200))
x=lambda n:n+2*max(0,n-3)
check('piecewise linear values',[x(n)for n in range(7)]==[0,1,2,3,6,9,12])
check('second differences',[x(n+2)-2*x(n+1)+x(n)for n in range(5)]==[0,0,2,0,0])
check('second difference noise bound',4*F(1,16)==F(1,4))
check('second difference robust threshold',F(1,4)<1<2-F(1,4))
controls=[('delta1 preserves positive frame lower bound',1-1>0),('oblique projection never amplifies residual',5<=1),('mismatch count equals squared L2',3==38),('single grid always quarter separated',distance(F(1,8),0)>=F(1,4))]
for name,assertion in controls:
 if assertion:raise AssertionError('invalid control unexpectedly true: '+name)
report={'status':'PASS','scope':'Finite exact specializations on visual pages V28--V39. Grouped checks contain stated bounded meshes; no universal theorem or Lean compilation claimed.','checks_passed':len(checks),'checks':checks,'invalid_controls_rejected':[x[0]for x in controls],'python':sys.version,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'checks/EXTENSION_EXACT_CHECKS.json');args=ap.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','checks_passed','invalid_controls_rejected']}))
