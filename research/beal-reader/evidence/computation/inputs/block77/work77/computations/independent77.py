#!/usr/bin/env python3
import json, hashlib, itertools
P=7
# Independent F49 basis 1,t with t^2=t+1. w=2t-1.
def add(x,y): return ((x[0]+y[0])%P,(x[1]+y[1])%P)
def neg(x): return ((-x[0])%P,(-x[1])%P)
def sub(x,y): return add(x,neg(y))
def mul(x,y):
    a,b=x; c,d=y
    # ac + bd*(t+1) + (ad+bc)t
    return ((a*c+b*d)%P,(a*d+b*c+b*d)%P)
def scale(a,x): return ((a*x[0])%P,(a*x[1])%P)
def invs(a): return pow(a%P,-1,P)
def sq(x): return mul(x,x)
F=[(a,b) for a in range(P) for b in range(P)]

# Independent deterministic slice with different p generation and loop ordering.
cases=0; dig=hashlib.sha256()
for bg,bh in itertools.product(range(P),repeat=2):
  for ag in F:
    for ah in F:
      x=1+((5*ag[0]+ag[1]+2*ah[0]+4*ah[1]+3*bg+bh)%6)
      xi=invs(x)
      pg=((ag[0]+2*ah[0]+3*bh)%P,(4*ag[1]+ah[1]+bg)%P)
      ph=((6*ah[0]+ag[1]+bh)%P,(2*ah[1]+5*ag[0]+bg)%P)
      agh=add(ag,scale(x,ah))
      pgh=add(add(pg,ph),scale(xi*bh,ag))
      sh=scale(bh,ah)
      mu=sub(mul(ag,sub(ph,sh)),scale(x,mul(pg,ah)))
      R=add(scale(2,mul(ag,ph)),scale(xi*bh,sq(ag)))
      df=sub(add(mul(ag,pg),scale(x,mul(ah,ph))),mul(agh,pgh))
      if add(R,df)!=mu:
          raise AssertionError((ag,ah,bg,bh,x,R,df,mu))
      dig.update(bytes([bg,bh,*ag,*ah,x,*mu]))
      cases+=1

# Independent Heisenberg check written with explicit matrices.
def mat(a,b,c):
    return ((1,a,c),(0,1,b),(0,0,1))
def mm(A,B):
    return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(3))%P for j in range(3)) for i in range(3))
def tup(M): return (M[0][1],M[1][2],M[0][2])
H=[(a,b,c) for a in range(P) for b in range(P) for c in range(P)]
checks=0
for g in H:
  Mg=mat(*g)
  for h in H:
    gh=tup(mm(Mg,mat(*h)))
    dp=(g[2]+h[2]-gh[2])%P
    if dp != (-g[0]*h[1])%P: raise AssertionError(('cup',g,h,gh,dp))
    checks+=1
x=(1,0,0); z=(0,0,1)
assert tup(mm(mat(*x),mat(*z)))==tup(mm(mat(*z),mat(*x)))
def R(g,h): return (2*g[0]*h[2]+g[0]*g[0]*h[1])%P
assert (R(x,z),R(z,x))==(2,0)

print(json.dumps({
 'status':'PASS','field_slice_cases':cases,'field_slice_sha256':dig.hexdigest(),
 'heisenberg_matrix_pair_checks':checks,
 'heisenberg_R_pair':[R(x,z),R(z,x)],
 'basis':'theta^2=theta+1; no arithmetic imported from primary'
},indent=2,sort_keys=True))
