#!/usr/bin/env python3
import json, hashlib, itertools, sys
P=7

def inv(x): return pow(x%P,-1,P)

def s(x): return x%P

# F49 in basis 1,w with w^2=5.
def add(x,y): return ((x[0]+y[0])%P,(x[1]+y[1])%P)
def neg(x): return ((-x[0])%P,(-x[1])%P)
def sub(x,y): return add(x,neg(y))
def mul(x,y): return ((x[0]*y[0]+5*x[1]*y[1])%P,(x[0]*y[1]+x[1]*y[0])%P)
def smul(a,x): return ((a*x[0])%P,(a*x[1])%P)
def sq(x): return mul(x,x)
ZERO=(0,0)

# B77.1 scalar exhaustive check.
scalar_cases=0
for a,A,b,B,pg,ph in itertools.product(range(P), repeat=6):
    for x in range(1,P):
        xi=inv(x)
        agh=(a+x*A)%P
        bgh=(b+xi*B)%P
        pgh=(pg+ph+a*xi*B)%P # dp=-alpha cup beta
        sg=a*b%P; sh=A*B%P; sgh=agh*bgh%P
        ds=(sg+sh-sgh)%P
        cupab=a*xi*B%P
        cupba=b*x*A%P
        if (ds+cupab+cupba)%P:
            raise AssertionError(('ds',a,A,b,B,x))
        # symmetric Massey cocycle mu = alpha cup (p-s) - p cup alpha
        mu=(a*((ph-sh)%P)-pg*x*A)%P
        R=(2*a*ph+a*a*xi*B)%P
        # f=alpha*p in chi-module
        fg=a*pg%P; fh=A*ph%P; fgh=agh*pgh%P
        df=(fg+x*fh-fgh)%P
        if (R+df-mu)%P:
            raise AssertionError(('identity',a,A,b,B,pg,ph,x,R,df,mu))
        scalar_cases+=1

# B77.1 coefficient-field checks on a deterministic complete slice:
# alpha(g),alpha(h) run through all F49, beta(g),beta(h) through F7,
# while p(g),p(h) are generated deterministically from the tuple. This is
# a finite implementation check, not the universal proof.
field_cases=0
field_hash=hashlib.sha256()
F49=[(a,b) for a in range(P) for b in range(P)]
for ag in F49:
  for ah in F49:
    for bg in range(P):
      for bh in range(P):
        x=1+((ag[0]+2*ag[1]+ah[0]+3*ah[1]+bg+bh)%6)
        xi=inv(x)
        pg=((3*ag[0]+ah[1]+2*bg)%P,(ag[1]+4*ah[0]+bh)%P)
        ph=((2*ah[0]+ag[1]+bg)%P,(5*ah[1]+ag[0]+2*bh)%P)
        agh=add(ag,smul(x,ah))
        # beta is embedded as scalar in F49
        bgh=(bg+xi*bh)%P
        pgh=add(add(pg,ph), smul(xi*bh,ag))
        sh=smul(bh,ah)
        mu=sub(mul(ag, sub(ph,sh)), smul(x,mul(pg,ah)))
        R=add(smul(2,mul(ag,ph)), smul(xi*bh,sq(ag)))
        fg=mul(ag,pg); fh=mul(ah,ph); fgh=mul(agh,pgh)
        df=sub(add(fg,smul(x,fh)),fgh)
        if add(R,df)!=mu:
            raise AssertionError(('field identity',ag,ah,bg,bh,x,R,df,mu))
        field_hash.update(bytes([*ag,*ah,bg,bh,x,*mu]))
        field_cases+=1

# B77 negative control: Heisenberg U3(F7) has cup-zero alpha cup beta
# with p=c, but the symmetric secondary q-equation is inconsistent.
def hmul(g,h):
    a,b,c=g; A,B,C=h
    return ((a+A)%P,(b+B)%P,(c+C+a*B)%P)
def alpha(g): return g[0]
def beta(g): return g[1]
def pp(g): return g[2]
def RR(g,h):
    return (2*alpha(g)*pp(h)+alpha(g)*alpha(g)*beta(h))%P
H=[(a,b,c) for a in range(P) for b in range(P) for c in range(P)]
heis_pair_checks=0
for g in H:
  for h in H:
    # dp = - alpha cup beta, trivial action
    dp=(pp(g)+pp(h)-pp(hmul(g,h)))%P
    if dp != (-alpha(g)*beta(h))%P:
        raise AssertionError(('heisenberg cup',g,h,dp))
    heis_pair_checks+=1
x=(1,0,0); z=(0,0,1)
assert hmul(x,z)==hmul(z,x)
R_xz=RR(x,z); R_zx=RR(z,x)
assert R_xz==2 and R_zx==0
# Any q would have dq(x,z)=dq(z,x) because xz=zx, contradiction.

# Symmetrization check at the formal class level: if u is a 1-cocycle and
# D12,D23 are shifted by -u/2, their sum condition is corrected. The change
# in Massey cocycle is -1/2(alpha cup u + u cup alpha), which is cohomologically
# zero by graded commutativity. We record the coefficient identity 2^{-1}=4.
inv2=inv(2)
assert inv2==4

out={
  'status':'PASS',
  'scalar_exhaustive_cases':scalar_cases,
  'field_slice_cases':field_cases,
  'field_slice_sha256':field_hash.hexdigest(),
  'heisenberg_pair_checks':heis_pair_checks,
  'heisenberg_commuting_control':{
      'x':x,'z':z,'R_xz':R_xz,'R_zx':R_zx,
      'conclusion':'no q on U3(F7) can solve the symmetric secondary equation for p=c'
  },
  'inverse_of_2_mod7':inv2,
  'nonclaims':[
    'finite checks do not prove the universal cochain identities',
    'the Heisenberg control is not an absolute Galois group or a Frey representation',
    'no Block70 pattern is eliminated by this computation'
  ]
}
print(json.dumps(out,indent=2,sort_keys=True))
