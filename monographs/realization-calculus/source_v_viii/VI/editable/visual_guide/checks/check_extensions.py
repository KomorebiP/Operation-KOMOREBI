#!/usr/bin/env python3
"""Exact finite witnesses for new Paper VI visual pages, using the standard library.
Analytic theorems and previously saved symbolic records are not rerun here.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse,json,hashlib,sys

def mat(a): return [[F(x) for x in r] for r in a]
def mm(a,b): return [[sum((x*y for x,y in zip(r,c)),F()) for c in zip(*b)] for r in a]
def add(a,b): return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def sub(a,b): return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(q,a): return [[F(q)*x for x in r] for r in a]
def ident(n): return mat([[int(i==j) for j in range(n)] for i in range(n)])
def zero(m,n): return mat([[0]*n for _ in range(m)])
def inverse(a):
 n=len(a);b=[r[:]+e for r,e in zip(a,ident(n))]
 for c in range(n):
  k=next(k for k in range(c,n) if b[k][c]);b[c],b[k]=b[k],b[c]
  z=b[c][c];b[c]=[x/z for x in b[c]]
  for j in range(n):
   if j!=c:
    z=b[j][c];b[j]=[x-z*y for x,y in zip(b[j],b[c])]
 return [r[n:] for r in b]
def bayes(p,l):
 u=[x*y for x,y in zip(p,l)];z=sum(u)
 if z<=0:raise ValueError('positive evidence required')
 return [x/z for x in u],z

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path(__file__).with_name('EXTENSION_EXACT_CHECKS.json'));args=parser.parse_args()
 checks=[];controls=[]
 def check(page,name,actual,expected):
  assert actual==expected,(page,name,actual,expected)
  checks.append({'visual_page':page,'name':name,'passed':True})
 def reject(page,name,actual,false):
  assert actual!=false,(page,name,'false alternative was not rejected')
  controls.append({'visual_page':page,'name':name,'rejected':True})
 A=mat([[0,0,0],[2,0,0],[0,3,0]]);A2=mm(A,A)
 check(29,'two-transfer coefficient',A2,mat([[0,0,0],[0,0,0],[6,0,0]]));check(29,'acyclic nilpotence',mm(A2,A),zero(3,3))
 for t in (F(0),F(1,2),F(1),F(2)):
  E=add(add(ident(3),scale(t,A)),scale(t*t/2,A2))
  check(29,f'initial-column polynomial at {t}',mm(E,mat([[1],[0],[0]])),mat([[1],[2*t],[3*t*t]]))
  check(29,f'differential equation at {t}',mm(A,E),add(A,scale(t,A2)))
 reject(29,'positive transfer is not automatically stochastic',[sum(c) for c in zip(*A)],[F(0)]*3)
 C=mat([[1,0]]);R=mat([[1],[0]]);quarter=mat([[0,-1],[1,0]]);P=mm(R,C)
 check(30,'quarter-turn compression',mm(mm(C,quarter),R),mat([[0]]));check(30,'half-turn compression',mm(mm(C,mm(quarter,quarter)),R),mat([[-1]]))
 check(30,'range excursion recovers composition defect',mm(mm(mm(mm(C,quarter),sub(P,ident(2))),quarter),R),mat([[1]]))
 reject(30,'limit is not scalar semigroup',mat([[0]]),mat([[-1]]))
 for n in range(8):
  an=1-F(1,2**n);an1=1-F(1,2**(n+1))
  check(31,f'adjacent generator magnitude n={n}',an1-an,F(1,2**(n+1)))
  check(31,f'finite-tail plus exact geometric remainder n={n}',sum((F(1,2**(j+1)) for j in range(n,n+8)),F())+F(1,2**(n+8)),F(1,2**n))
 Q=mat([[-3,1,2,0],[1,-3,0,2],[2,0,-3,1],[0,2,1,-3]])
 K=add(ident(4),scale(F(1,8),Q));K[0][0]-=F(1,16);K[2][0]+=F(1,16)
 C=mat([[1,1,0,0],[0,0,1,1]]);w=mat([[1],[-1],[0],[0]])
 check(32,'forgotten direction',mm(C,w),mat([[0],[0]]));check(32,'nonzero canonical obstruction',mm(mm(C,K),w),mat([[-F(1,16)],[F(1,16)]]))
 check(32,'perturbed matrix remains column stochastic',[sum(c) for c in zip(*K)],[F(1)]*4)
 reject(32,'nonzero obstruction cannot descend',mm(mm(C,K),w),mat([[0],[0]]))
 H={1:[F(0),F(1)],2:[F(-1),F(0),F(1)],4:[F(3),F(0),F(-6),F(0),F(1)]}
 def generator(p):
  return [((i+2)*(i+1)*p[i+2] if i+2<len(p) else 0)-i*p[i] for i in range(len(p))]
 def moment(n):
  if n%2:return F(0)
  out=1
  for k in range(1,n,2):out*=k
  return F(out)
 def inner(p,q):return sum((a*b*moment(i+j) for i,a in enumerate(p) for j,b in enumerate(q)),F())
 for n,p in H.items():
  check(33,f'H{n} exact generator eigenfunction',generator(p),[-n*a for a in p]);fact=1
  for k in range(1,n+1):fact*=k
  check(33,f'H{n} Gaussian squared norm',inner(p,p),F(fact))
 for n,m in combinations(H,2):check(33,f'H{n},H{m} orthogonality',inner(H[n],H[m]),F(0))
 check(33,'OU energy at log2',F(1,4)+2*F(1,16),F(3,8));check(33,'gap bound at log2',3*F(1,4),F(3,4))
 check(33,'fractional H1+H4 energy at log2',F(1,4)+24*F(1,16),F(7,4));check(33,'ordinary H1+H4 energy at log2',F(1,4)+24*F(1,256),F(11,32))
 reject(33,'fractional rate is not ordinary rate',F(1,4),F(1,16))
 p=[F(1,4)]*4;l1=list(map(F,[2,2,1,1]));l2=list(map(F,[1,1,3,1]))
 profile=list(zip(l1,l2));check(34,'equal likelihood profiles',profile[0],profile[1]);reject(34,'joint profiles distinguish states2and3',profile[2],profile[3])
 p1,z1=bayes(p,l1);p2,z2=bayes(p1,l2);direct,z=bayes(p,[x*y for x,y in zip(l1,l2)])
 check(34,'two-stage fine posterior',p2,[F(1,4),F(1,4),F(3,8),F(1,8)]);check(34,'composition matches direct posterior',p2,direct)
 check(34,'first evidence',z1,F(3,2));check(34,'second evidence',z2,F(4,3));check(34,'evidence product',z1*z2,F(2));check(34,'direct evidence',z,F(2))
 cp=[F(1,2),F(1,4),F(1,4)];cp1,_=bayes(cp,list(map(F,[2,1,1])));cp2,_=bayes(cp1,list(map(F,[1,3,1])))
 check(34,'coarse first posterior',cp1,[F(2,3),F(1,6),F(1,6)]);check(34,'coarse second posterior',cp2,[F(1,2),F(3,8),F(1,8)])
 # Prime-log coefficients encode exact algebraic identities in log(2), log(3).
 def logcoeff(q):
  out=[]
  for prime in (2,3):
   n,d=q.numerator,q.denominator;k=0
   while n%prime==0:n//=prime;k+=1
   while d%prime==0:d//=prime;k-=1
   out.append(F(k))
  # All ratios in this fixed example are products of powers of 2 and 3.
  residue=q
  for prime,k in zip((2,3),out):residue/=F(prime)**int(k)
  assert residue==1
  return out
 def klcoeff(p,q):return [sum((x*logcoeff(x/y)[k] for x,y in zip(p,q)),F()) for k in (0,1)]
 p=list(map(F,[F(1,2),F(1,4),F(1,8),F(1,8)]));q=[F(1,4)]*4
 fine=klcoeff(p,q);coarse=klcoeff([F(3,4),F(1,4)],[F(1,2),F(1,2)])
 within=[F(3,4)*a for a in klcoeff([F(2,3),F(1,3)],[F(1,2),F(1,2)])]
 check(35,'fine entropy prime-log coefficients',fine,[F(1,4),F(0)]);check(35,'coarse entropy prime-log coefficients',coarse,[F(-1),F(3,4)]);check(35,'conditional entropy coefficients',within,[F(5,4),F(-3,4)])
 check(35,'exact entropy chain rule coefficients',[a+b for a,b in zip(coarse,within)],fine)
 reject(35,'wrong Q weight breaks chain rule',[a+F(2,3)*b for a,b in zip(coarse,within)],fine)
 for q in (F(1,2),F(1),F(2),F(3)):
  den=1+q+q*q;post=[1/den,q/den,q*q/den];mean=post[1]+2*post[2];second=post[1]+4*post[2];var=second-mean*mean
  # d/dt=q d/dq; differentiating (q+2q²)/(1+q+q²).
  deriv=q*((1+4*q)*den-(q+2*q*q)*(1+2*q))/(den*den)
  check(36,f'mean derivative equals variance at q={q}',deriv,var)
  check(36,f'replicator derivatives preserve mass q={q}',sum(((i-mean)*x for i,x in enumerate(post)),F()),F(0))
 q=F(2);post=[F(1,7),F(2,7),F(4,7)];mean=F(10,7)
 check(36,'mean at log2',post[1]+2*post[2],mean);check(36,'second moment at log2',post[1]+4*post[2],F(18,7));check(36,'variance at log2',F(18,7)-mean*mean,F(26,49))
 check(36,'replicator derivative vector at log2',[(i-mean)*x for i,x in enumerate(post)],[F(-10,49),F(-6,49),F(16,49)])
 weights=[F(1,4),F(3,2)+F(2,4),F(1,9)];check(37,'Jordan block integrated weight',weights[1],F(2));check(37,'total integrated weight',sum(weights),F(85,36))
 for k,expected in ((1,F(13,36)),(2,F(1,9))):
  tails=[sum(w for i,w in enumerate(weights) if i not in J) for J in combinations(range(3),k)]
  check(37,f'exhaustive best {k}-block certificate',min(tails),expected)
 check(37,'two blocks meet tolerance',F(1,9)<=F(1,8),True);check(37,'one block fails tolerance',F(13,36)>F(1,8),True)
 reject(37,'slowest-first does not optimize certificate',weights[1]+weights[2],F(13,36))
 N=mat([[0,1],[0,0]]);check(38,'nilpotent kernel square',mm(N,N),zero(2,2))
 for t in (F(0),F(1,4),F(1,2),F(1),F(2)):
  x=mat([[t*t/2],[1]])
  check(38,f'constant second derivative at t={t}',mm(N,x),mat([[1],[0]]))
  check(38,f'exact polynomial state difference at t={t}',sub(x,mat([[0],[1]])),mat([[t*t/2],[0]]))
 check(38,'half-time exact error',F(1,2)**2/2,F(1,8));check(38,'half-time certificate prefactor',F(1,2)**2,F(1,4))
 D=mat([[-2,1],[0,-2]]);B=mat([[1,0]]);C=mat([[0],[1]]);J=add(D,scale(2,ident(2)))
 check(39,'Jordan nilpotence',mm(J,J),zero(2,2));check(39,'zero direct hidden transfer',mm(B,C),mat([[0]]));check(39,'nonzero link transfer',mm(mm(B,J),C),mat([[1]]))
 for z in (F(0),F(1),F(3)):
  check(39,f'repeated-pole transfer at z={z}',mm(mm(B,inverse(sub(scale(z,ident(2)),D))),C),mat([[1/(z+2)**2]]))
 mass=[F(1,4),F(1,8)];S=sum(mass);check(40,'surviving mass',S,F(3,8));check(40,'conditional surviving mixture',[x/S for x in mass],[F(2,3),F(1,3)])
 check(40,'total absorbed plus surviving mass',F(1,4)+F(3,8)+S,F(1));check(40,'equal cause densities',mass[0],2*mass[1]);check(40,'total hazard',(mass[0]+2*mass[1])/S,F(4,3))
 check(40,'initial mean',F(1,2)+F(1,4),F(3,4));check(40,'residual mean',F(2,3)+F(1,6),F(5,6))
 for q in (F(1,4),F(1,2),F(1)):
  check(40,f'residual survival formula for exp(-s)={q}',(F(1,2)*F(1,2)*q+F(1,2)*F(1,4)*q*q)/S,F(2,3)*q+F(1,3)*q*q)
 A=mat([[2,1,0],[0,2,0],[0,0,9]]);B=mat([[2,1],[0,2]]);FA=inverse(add(ident(3),A));FB=inverse(add(ident(2),B))
 for eta in (F(-1),F(0),F(1,4),F(1),F(2)):
  C=mat([[1,0,eta],[0,1,0]]);delta=sub(mm(C,A),mm(B,C));defect=sub(mm(C,FA),mm(FB,C))
  check(41,f'generator defect eta={eta}',delta,mat([[0,0,7*eta],[0,0,0]]))
  check(41,f'rational defect eta={eta}',defect,mat([[0,0,-F(7,30)*eta],[0,0,0]]))
  check(41,f'two-inverse defect identity eta={eta}',defect,scale(-1,mm(mm(FB,delta),FA)))
 reject(41,'wrong inverse-identity sign',mat([[0,0,-F(7,30)],[0,0,0]]),mat([[0,0,F(7,30)],[0,0,0]]))
 report={'status':'PASS','edition_date':'2026-10-05','scope':'Exact finite witnesses for visual pages V29-V41. Independent of inherited symbolic and Lean records.','checks_passed':len(checks),'false_controls_rejected':len(controls),'checks':checks,'false_controls':controls,'python':sys.version.split()[0],'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'limits':['No fresh Lean invocation.','No replay of original 204 symbolic assertions.','Exponential integral, infinite geometric tail, OU completeness, logarithm positivity, and general analytic theorem proofs are not certified by this finite checker.','The entropy checks compare exact coefficients in log(2),log(3); no approximate logarithms enter.','Gaussian checks concern three named Hermite polynomials and their exact moments.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
 print(f'PASS: {len(checks)} exact assertions; {len(controls)} false controls rejected.')
if __name__=='__main__':main()
