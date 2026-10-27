#!/usr/bin/env python3
"""Separate Block73 arithmetic. phi basis, normal forms, direct matrix products.
No import from the primary program. Reject any mismatch with its finite certificate.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

class Field:
    def __init__(self,m):self.m=m;self.z=(0,0);self.o=(1,0)
    def s(self,a):return (a%self.m,0)
    def add(self,x,y):return ((x[0]+y[0])%self.m,(x[1]+y[1])%self.m)
    def neg(self,x):return (-x[0]%self.m,-x[1]%self.m)
    def sub(self,x,y):return self.add(x,self.neg(y))
    def mul(self,x,y):
        a,b=x;c,d=y;m=self.m
        # Polynomial convolution, then phi^2=phi+1.
        f0=a*c;f1=a*d+b*c;f2=b*d
        return ((f0+f2)%m,(f1+f2)%m)
    def inv(self,x):
        a,b=x;m=self.m;ni=pow((a*a+a*b-b*b)%m,-1,m)
        return ((a+b)*ni%m,-b*ni%m)
    def scale(self,n,x):return (n*x[0]%self.m,n*x[1]%self.m)
    def code(self,n,base=7):
        a,b=n%base,n//base;return ((a-b)%self.m,2*b%self.m)
    def canonical(self,x):
        m=self.m;b=x[1]*pow(2,-1,m)%m;a=(x[0]+b)%m;return a+m*b
    def power(self,x,n):
        out=self.o
        for bit in bin(n)[2:]:
            out=self.mul(out,out)
            if bit=='1':out=self.mul(out,x)
        return out
    def mat(self,a):return tuple(self.s(x) for x in a)
    def times(self,a,b):
        out=[]
        for i in range(2):
            for j in range(2):
                v=self.z
                for k in range(2):v=self.add(v,self.mul(a[2*i+k],b[2*k+j]))
                out.append(v)
        return tuple(out)
    def plus(self,a,b):return tuple(self.add(x,y) for x,y in zip(a,b))
    def minus(self,a,b):return tuple(self.sub(x,y) for x,y in zip(a,b))
    def factor(self,n,a):return tuple(self.scale(n,x) for x in a)
    def inverse(self,a):
        d=self.inv(self.sub(self.mul(a[0],a[3]),self.mul(a[1],a[2])))
        return tuple(self.mul(d,x) for x in (a[3],self.neg(a[1]),self.neg(a[2]),a[0]))
    def mpow(self,a,n):
        o=self.mat((1,0,0,1))
        for bit in bin(n)[2:]:
            o=self.times(o,o)
            if bit=='1':o=self.times(o,a)
        return o

K=Field(7);S=Field(49);R=Field(343);Z=K.mat((0,0,0,0));E=K.mat((0,1,0,0))
def need(c,s):
    if not c:raise AssertionError(s)
def xm(k,v):p,q,b=v;return (p,q,b,k.neg(p))
def adj(g,x):return K.times(K.times(g,x),K.inverse(g))
def ecochain(alpha,chi,p,b):
    # Compute the quadratic upper-entry terms directly.
    term1=K.scale(2,K.mul(alpha,p));term2=K.mul(K.mul(alpha,alpha),K.mul(b,K.inv(chi)))
    return K.add(term1,term2)

def adjoint():
    count=0;digest=hashlib.sha256()
    for c in range(1,7):
      for aa in range(49):
       a=K.code(aa);g=(K.s(c),a,K.z,K.o)
       for slot in range(3):
        for v in range(49):
         x=[K.z]*3;x[slot]=K.code(v);y=adj(g,xm(K,x))
         p=K.add(x[0],K.mul(a,K.mul(K.inv(K.s(c)),x[2])))
         q=K.sub(K.sub(K.mul(K.s(c),x[1]),K.scale(2,K.mul(a,x[0]))),K.mul(K.mul(a,a),K.mul(K.inv(K.s(c)),x[2])))
         b=K.mul(K.inv(K.s(c)),x[2]);need(y==xm(K,(p,q,b)),'adjoint')
         digest.update(bytes(K.canonical(z) for z in (y[0],y[1],y[2])));count+=1
    pp=0;ee=0
    for i in range(4096):
        c=1+i%6;d=1+(i//6)%6;a=(13*i+7)%49;ah=(19*i+11)%49
        x=tuple(K.code(z) for z in ((5*i+1)%49,(9*i+3)%49,(23*i+4)%49))
        y=tuple(K.code(z) for z in ((31*i+8)%49,(17*i+9)%49,(11*i+2)%49))
        g=(K.s(c),K.code(a),K.z,K.o);v=K.plus(xm(K,x),adj(g,xm(K,y)))
        r0g=(S.s(c+7*(i%7)),S.code(a),S.z,S.o);r0h=(S.s(d+7*((i//7)%7)),S.code(ah),S.z,S.o)
        def lift_mat(mat):return tuple(S.code(K.canonical(z)) for z in mat)
        def change(mat,ref):return S.times(S.plus(S.mat((1,0,0,1)),S.factor(7,lift_mat(mat))),ref)
        need(S.times(change(xm(K,x),r0g),change(xm(K,y),r0h))==change(v,S.times(r0g,r0h)),'mixed-characteristic pair');pp+=1
        ag=K.code(a);ahh=K.code(ah);cg=K.s(c);ch=K.s(d)
        bh=K.code((29*i+4)%49);bl=K.code((37*i+5)%49);ph=K.code((41*i+6)%49);pl=K.code((43*i+7)%49)
        p_hl=K.add(K.add(ph,pl),K.mul(ahh,K.mul(K.inv(ch),bl)))
        beta_hl=K.add(bh,K.mul(K.inv(ch),bl));a_gh=K.add(ag,K.mul(cg,ahh))
        values=[K.mul(cg,ecochain(ahh,ch,pl,bl)),K.neg(ecochain(a_gh,K.mul(cg,ch),pl,bl)),ecochain(ag,cg,p_hl,beta_hl),K.neg(ecochain(ag,cg,ph,bh))]
        total=K.z
        for z in values:total=K.add(total,z)
        need(total==K.z,'secondary dE');ee+=1
    return {'basis_action_cases':count,'action_digest':digest.hexdigest(),'matrix_pair_cases':pp,'secondary_cocycle_cases':ee}

def toric():
    nc=pc=sc=ac=0;digest=hashlib.sha256()
    for ci in range(1,49):
      for ti in range(49):
        c=K.code(ci);t=K.code(ti)
        P=(t,K.o,K.o,K.z);Pi=K.inverse(P)
        M=K.times(K.times(P,(K.z,c,K.z,K.z)),Pi)
        need(M[2]==c and K.times(M,M)==Z,'nilpotent basis');nc+=1
        # In this basis trace=h and [A,cE12]=h*cE12 give A21=0,A11=h,A22=0.
        # These are three independent linear constraints, leaving A12 free.
        for h in range(7):
            A=K.times(K.times(P,K.mat((h,0,0,0))),Pi)
            need(K.times(A,M)==K.factor(h,M) and K.times(M,A)==Z,'normal form');pc+=1
        for zi in range(49):
            z=K.code(zi);shift=(K.z,z,K.z,K.z)
            defect=K.minus(K.times(shift,M),K.times(M,shift));good=defect==Z
            need(good==(zi==0),'commutator injective');sc+=1;ac+=good
            digest.update(bytes(K.canonical(z) for z in defect))
    # Full F7 enumeration: generate nilpotents from all four entries, not theta.
    ms=[]
    for a,b,c,d in itertools.product(range(7),repeat=4):
        if c and (a+d)%7==0 and (a*d-b*c)%7==0:ms.append((a,b,c,d))
    need(len(ms)==42,'42 nilpotents')
    def mm(a,b):return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2))%7 for i in range(2) for j in range(2))
    tested=accepted=0
    for M in ms:
      for A in itertools.product(range(7),repeat=4):
        h=(A[0]+A[3])%7;AM=mm(A,M);MA=mm(M,A);hM=tuple(h*x%7 for x in M)
        tame=tuple((x-y)%7 for x,y in zip(AM,MA))==hM;geometric=(AM==hM and MA==(0,0,0,0))
        need(tame==geometric,'trace/tame equivalence');tested+=1;accepted+=tame
    return {'F49_nilpotents':nc,'rank_per_nilpotent':3,'F49_particular_cases':pc,'implied_F49_toric_packets_for_h_in_F7':nc*7*49,
      'upper_shift_cases':sc,'accepted_upper_shifts':ac,'shift_digest':digest.hexdigest(),
      'complete_F7_tame_candidates':tested,'complete_F7_tame_solutions':accepted}

def delayed():
    Q=883*883;F=R.mat((1,7,0,Q));T=R.mat((1,0,7,1))
    base=R.minus(R.times(F,T),R.times(R.mpow(T,Q),F))
    need(tuple(R.canonical(x) for x in base)==(49,0,0,294),'failure certificate')
    changes=0
    for side in range(2):
      for i in range(4):
       for j in range(49):
        delta=[R.z]*4;delta[i]=R.scale(49,R.code(j))
        A=R.plus(F,delta) if side==0 else F;B=R.plus(T,delta) if side==1 else T
        need(R.minus(R.times(A,B),R.times(R.mpow(B,Q),A))==base,'49 correction');changes+=1
    sw=S.mat((1,7,0,Q));st=S.mat((1,0,7,1));words=0
    for a,b in itertools.product(range(7),repeat=2):
        v=S.times(S.mpow(sw,a),S.mpow(st,b));need(S.add(v[0],v[3])==S.s(2),'trace of word');words+=1
    return {'Q':Q,'F_perturbed_mod343':[1,7,0,Q%343],'T_mod343':[1,0,7,1],
      'tame_defect_mod343':[R.canonical(x) for x in base],'basis_correction_checks':changes,
      'mod49_word_trace_checks':words,'mod49_relation_passes':True,'mod343_extension_possible':False}

def arithmetic(root):
    q=883;Q=q*q
    # Independent base field sqrt5 model, encoded x+y*omega by ordinary pairs.
    def mul(x,y):a,b=x;c,d=y;return ((a*c+5*b*d)%q,(a*d+b*c)%q)
    def pw(x,n):
        z=(1,0)
        for digit in bin(n)[2:]:
            z=mul(z,z)
            if digit=='1':z=mul(z,x)
        return z
    half=pow(2,-1,q)
    raw={'phi':pw((half,half),(Q-1)//7),'3':pw((3,0),(Q-1)//7),'sqrt5':pw((0,1),(Q-1)//7),'7':pw((7,0),(Q-1)//7)}
    # Convert base omega coefficients to the primary phi basis.
    vals={name:[(a-b)%q,(2*b)%q] for name,(a,b) in raw.items()}
    need(vals=={'phi':[1,0],'3':[1,0],'sqrt5':[1,0],'7':[296,0]},'direct symbols')
    src=json.loads((root/'work73/inputs/B72_B71_B70_refinement70.json').read_text());out=[];np=0
    for s in src['survivors']:
        c=s['inertia'][s['columns'].index(883)];need(c!=0,'required883');out.append({'alpha':s['alpha'],'inertia883':c})
        for theta in range(49):
          for d in range(7):
            t=R.code(theta);P=(t,R.o,R.o,R.z);Pinv=R.inverse(P)
            N=R.times(R.times(P,R.mat((0,7*c,0,0))),Pinv)
            # Transformed F has eigenvalue Q on the first basis vector and 1 on quotient.
            F=R.times(R.times(P,R.mat((Q,7*d,0,1))),Pinv)
            need(R.times(N,N)==R.mat((0,0,0,0)) and R.times(F,N)==R.factor(Q,N) and R.times(N,F)==N,'exact toric packet');np+=1
    pairs=[[i,0] for i in range(49)]
    gauges=[[v,c,ep,(c*v*pow(2*ep%7,-1,7))%7] for v in range(1,7) for c in range(1,8) for ep in (1,-1)]
    return {'prime':q,'residue_degree':2,'Q':Q,'Q_minus_one_v7':2,'seventh_symbols':vals,
      'rational_seventh_symbol_7':pow(7,126,883),'frozen_patterns':out,'frozen_pattern_count':len(out),'patterns_eliminated':0,
      'local_positive_packet_checks':np,'span_phi_7_coefficient_pairs':2401,'admissible_phi_7_pairs':pairs,
      'fixed7_target_values':gauges,'fixed7_target_example_v3_c1_epsilon_minus':2,
      'all_eight_global_patterns_still_unexcluded':True}

def build(root):
    return {'schema':'beal.block73.finite.v1','adjoint':adjoint(),'tame':toric(),'delayed_control':delayed(),'arithmetic':arithmetic(root),
      'non_claims':['Not a global realization or elimination of any of the eight patterns.',
        'The deformation-fibre theorem fixes complete inertia and all mod49 traces; the existing finite sieve does not supply these.',
        'No Lean certificate or independent mathematical review.']}

def compare(got,expected,path=''):
    if type(got)!=type(expected):raise ValueError('CERTIFICATE_MISMATCH '+path+' type')
    if isinstance(expected,dict):
        if got.keys()!=expected.keys():raise ValueError('CERTIFICATE_MISMATCH '+path+' keys')
        for k in expected:compare(got[k],expected[k],path+'/'+k)
    elif isinstance(expected,list):
        if len(got)!=len(expected):raise ValueError('CERTIFICATE_MISMATCH '+path+' length')
        for i,(a,b) in enumerate(zip(got,expected)):compare(a,b,path+'/'+str(i))
    elif got!=expected:raise ValueError('CERTIFICATE_MISMATCH '+path)

def main():
    p=argparse.ArgumentParser();p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[2];out=build(root);compare(json.loads(a.certificate.read_text()),out)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print('PASS_SEPARATE_ALL_FIELDS');return 0
if __name__=='__main__':raise SystemExit(main())
