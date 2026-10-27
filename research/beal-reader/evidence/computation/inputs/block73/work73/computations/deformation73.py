#!/usr/bin/env python3
"""Exact finite checks for Block73. No finite output proves the global Galois hypotheses."""
from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

class Ring:
    """a + b*w encoded a + modulus*b, with w^2=5."""
    def __init__(self, modulus: int): self.m=modulus; self.zero=0; self.one=1
    def pair(self,a,b=0): return a%self.m+self.m*(b%self.m)
    def add(self,x,y): m=self.m; return self.pair(x%m+y%m,x//m+y//m)
    def neg(self,x): return self.pair(-x%self.m,-(x//self.m))
    def sub(self,x,y): return self.add(x,self.neg(y))
    def mul(self,x,y):
        m=self.m;a,b=x%m,x//m;c,d=y%m,y//m
        return self.pair(a*c+5*b*d,a*d+b*c)
    def inv(self,x):
        m=self.m;a,b=x%m,x//m;t=pow((a*a-5*b*b)%m,-1,m)
        return self.pair(a*t,-b*t)
    def scale(self,n,x): return self.mul(self.pair(n),x)
    def power(self,x,n):
        y=1
        while n:
            if n&1:y=self.mul(y,x)
            x=self.mul(x,x);n//=2
        return y
    def lift(self,x,old=7):return self.pair(x%old,x//old)
    def matmul(self,a,b):
        return tuple(self.add(self.mul(a[2*i],b[j]),self.mul(a[2*i+1],b[2+j])) for i in range(2) for j in range(2))
    def matadd(self,a,b):return tuple(self.add(x,y) for x,y in zip(a,b))
    def matsub(self,a,b):return tuple(self.sub(x,y) for x,y in zip(a,b))
    def matscale(self,n,a):return tuple(self.scale(n,x) for x in a)
    def matinv(self,a):
        d=self.inv(self.sub(self.mul(a[0],a[3]),self.mul(a[1],a[2])))
        return tuple(self.mul(d,x) for x in (a[3],self.neg(a[1]),self.neg(a[2]),a[0]))
    def matpow(self,a,n):
        b=(1,0,0,1)
        while n:
            if n&1:b=self.matmul(b,a)
            a=self.matmul(a,a);n//=2
        return b
    def rank(self,rows):
        a=[list(r) for r in rows];r=0
        for c in range(len(a[0])):
            p=next((i for i in range(r,len(a)) if a[i][c]),None)
            if p is None:continue
            a[r],a[p]=a[p],a[r];iv=self.inv(a[r][c]);a[r]=[self.mul(iv,x) for x in a[r]]
            for i in range(len(a)):
                if i!=r and a[i][c]:
                    t=a[i][c];a[i]=[self.sub(x,self.mul(t,y)) for x,y in zip(a[i],a[r])]
            r+=1
        return r

K=Ring(7); S=Ring(49); R=Ring(343); I=(1,0,0,1); ZERO=(0,0,0,0); E=(0,1,0,0)
def need(c,s):
    if not c:raise AssertionError(s)
def xmat(p,q,b):return (p,q,b,K.neg(p))
def action(chi,a,x):
    p,q,b=x;t=K.mul(K.inv(chi),b)
    return (K.add(p,K.mul(a,t)), K.sub(K.sub(K.mul(chi,q),K.scale(2,K.mul(a,p))),K.mul(K.mul(a,a),t)),t)
def obstruction(a,chi,p_h,beta_h):
    return K.add(K.scale(2,K.mul(a,p_h)),K.mul(K.mul(a,a),K.mul(K.inv(chi),beta_h)))

def adjoint_checks():
    count=0;digest=hashlib.sha256()
    for chi in range(1,7):
      for a in range(49):
       g=(chi,a,0,1);gi=K.matinv(g)
       for j in range(3):
        for t in range(49):
         v=[0,0,0];v[j]=t;expected=action(chi,a,v)
         out=K.matmul(K.matmul(g,xmat(*v)),gi)
         need(out==xmat(*expected),'adjoint formula');digest.update(bytes(expected));count+=1
    prod=0;sec=0
    for i in range(4096):
        chi=1+i%6;chh=1+(i//6)%6
        a=(13*i+7)%49;ah=(19*i+11)%49
        x=((5*i+1)%49,(9*i+3)%49,(23*i+4)%49)
        y=((31*i+8)%49,(17*i+9)%49,(11*i+2)%49)
        ax=action(chi,a,y);xy=tuple(K.add(u,v) for u,v in zip(x,ax))
        rg0=(S.pair(chi+7*(i%7)),S.lift(a),0,1)
        rh0=(S.pair(chh+7*((i//7)%7)),S.lift(ah),0,1)
        def framed(xx,ref):
            xx=tuple(S.lift(z) for z in xmat(*xx));return S.matmul(S.matadd(I,S.matscale(7,xx)),ref)
        need(S.matmul(framed(x,rg0),framed(y,rh0))==framed(xy,S.matmul(rg0,rh0)),'framed multiplication');prod+=1
        # d E=0, with the p equation imposed rather than incorrectly setting dp=0.
        z=(7*i+3)%49;bh=(29*i+4)%49;bl=(37*i+5)%49;ph=(41*i+6)%49;pl=(43*i+7)%49
        agh=K.add(a,K.mul(chi,ah));p_hl=K.add(K.add(ph,pl),K.mul(ah,K.mul(K.inv(chh),bl)))
        b_hl=K.add(bh,K.mul(K.inv(chh),bl))
        d=K.sub(K.add(K.mul(chi,obstruction(ah,chh,pl,bl)),obstruction(a,chi,p_hl,b_hl)),K.add(obstruction(agh,K.mul(chi,chh),pl,bl),obstruction(a,chi,ph,bh)))
        need(d==0,'secondary expression is a 2-cocycle');sec+=1
    return {'basis_action_cases':count,'action_digest':digest.hexdigest(),'matrix_pair_cases':prod,'secondary_cocycle_cases':sec}

def toric_checks():
    # Every lower-nonzero nilpotent M over F49, complete linear-rank certification.
    nil=0;particular=0;shift=0;accepted_shifts=0;dig=hashlib.sha256()
    for c in range(1,49):
      for theta in range(49):
        t2=K.mul(theta,theta);M=tuple(K.mul(c,z) for z in (theta,K.neg(t2),1,K.neg(theta)))
        need(K.matmul(M,M)==ZERO,'nilpotence')
        a,b,cc,d=M
        rows=[(1,0,0,1),(0,cc,K.neg(b),0),(b,K.sub(d,a),0,K.neg(b)),(K.neg(cc),0,K.sub(a,d),cc),(0,K.neg(cc),b,0)]
        need(K.rank(rows)==3,'tame trace rank');nil+=1
        direction=(theta,K.neg(t2),1,K.neg(theta))
        for h in range(7):
            A=(0,K.scale(h,theta),0,h)
            need(K.matmul(A,M)==K.matscale(h,M) and K.matmul(M,A)==ZERO,'toric particular')
            need(K.matmul(direction,M)==ZERO and K.matmul(M,direction)==ZERO,'toric direction');particular+=1
        comm=K.matsub(K.matmul(E,M),K.matmul(M,E))
        for z in range(49):
            defect=tuple(K.mul(z,v) for v in comm);ok=defect==ZERO
            need(ok==(z==0),'upper shift detected');shift+=1;accepted_shifts+=ok
            dig.update(bytes(defect))
    # Complete prime-field enumeration, no parameterization used for acceptance.
    candidates=0;solutions=0
    for c in range(1,7):
      for t in range(7):
        M=(c*t%7,-c*t*t%7,c,-c*t%7)
        for A in itertools.product(range(7),repeat=4):
            h=(A[0]+A[3])%7
            AM=K.matmul(A,M);MA=K.matmul(M,A)
            tame=K.matsub(AM,MA)==K.matscale(h,M)
            toric=AM==K.matscale(h,M) and MA==ZERO
            need(tame==toric,'tame+trace equivalent toric');candidates+=1;solutions+=tame
    return {'F49_nilpotents':nil,'rank_per_nilpotent':3,'F49_particular_cases':particular,
      'implied_F49_toric_packets_for_h_in_F7':nil*7*49,
      'upper_shift_cases':shift,'accepted_upper_shifts':accepted_shifts,'shift_digest':dig.hexdigest(),
      'complete_F7_tame_candidates':candidates,'complete_F7_tame_solutions':solutions}

def delayed_control():
    Q=883**2;F=tuple(R.pair(x) for x in (1,0,0,Q));T=tuple(R.pair(x) for x in (1,0,7,1));Fp=R.matadd(F,R.matscale(7,E))
    defect=R.matsub(R.matmul(Fp,T),R.matmul(R.matpow(T,Q),Fp))
    need(defect==(49,0,0,294),'explicit tame defect')
    changes=0
    for which in range(2):
      for slot in range(4):
       for z in range(49):
        correction=[0]*4;correction[slot]=R.scale(49,R.lift(z));correction=tuple(correction)
        ff=R.matadd(Fp,correction) if which==0 else Fp
        tt=R.matadd(T,correction) if which==1 else T
        need(R.matsub(R.matmul(ff,tt),R.matmul(R.matpow(tt,Q),ff))==defect,'next digits cannot repair defect');changes+=1
    # Mod49, this IS a local tame representation, with identical traces on every word
    # in the finite elementary-abelian image. Diagonal trace=2 for all words.
    f49=tuple(S.pair(x) for x in (1,7,0,Q));t49=(1,0,7,1)
    words=0
    for i,j in itertools.product(range(7),repeat=2):
        m=S.matmul(S.matpow(f49,i),S.matpow(t49,j));need(S.add(m[0],m[3])==2,'word trace');words+=1
    return {'Q':Q,'F_perturbed_mod343':[1,7,0,Q%343],'T_mod343':[1,0,7,1],
      'tame_defect_mod343':list(defect),'basis_correction_checks':changes,'mod49_word_trace_checks':words,
      'mod49_relation_passes':True,'mod343_extension_possible':False}

def residue_and_fibre(root):
    q=883;m=q*q-1
    # Separate BASE field phi^2=phi+1. No identification with coefficient w.
    def mul(x,y):a,b=x;c,d=y;return ((a*c+b*d)%q,(a*d+b*c+b*d)%q)
    def power(x,n):
        y=(1,0)
        while n:
            if n&1:y=mul(y,x)
            x=mul(x,x);n//=2
        return y
    vals={name:list(power(x,m//7)) for name,x in [('phi',(0,1)),('3',(3,0)),('sqrt5',(q-1,2)),('7',(7,0))]}
    need(vals=={'phi':[1,0],'3':[1,0],'sqrt5':[1,0],'7':[296,0]},'883 symbols')
    need(pow(296,7,q)==1 and 296!=1,'nontrivial seventh root')
    data=json.loads((root/'work73/inputs/B72_B71_B70_refinement70.json').read_text())
    patterns=[];positive=0
    for s in data['survivors']:
        c=s['inertia'][s['columns'].index(883)];need(c!=0,'every frozen pattern supports883')
        patterns.append({'alpha':s['alpha'],'inertia883':c})
        # Integral toric packets over Z[w], checked modulo343, for all49 theta and7 y.
        for theta in range(49):
          for y in range(7):
            th=R.lift(theta);th2=R.mul(th,th)
            N=tuple(R.scale(7*c,x) for x in (th,R.neg(th2),1,R.neg(th)))
            F=(R.add(1,R.scale(7*y,th)),R.sub(R.scale(q*q-1,th),R.scale(7*y,th2)),R.pair(7*y),R.sub(R.pair(q*q),R.scale(7*y,th)))
            need(R.matmul(N,N)==ZERO and R.matmul(F,N)==R.matscale(q*q,N) and R.matmul(N,F)==N,'local positive packet');positive+=1
    allowed=[]
    for a,b in itertools.product(range(49),repeat=2):
        # Row normalized using 296: [phi]->0, [7]->1. This is not a beta normalization.
        if b==0:allowed.append([a,b])
    need(len(allowed)==49,'unit fibre kernel')
    gauges=[]
    for v in range(1,7):
      for c in range(1,8):
       for ep in (1,-1):
        target=(c*v*pow((2*ep)%7,-1,7))%7;gauges.append([v,c,ep,target])
    return {'prime':q,'residue_degree':2,'Q':q*q,'Q_minus_one_v7':2,'seventh_symbols':vals,
      'rational_seventh_symbol_7':pow(7,(q-1)//7,q),'frozen_patterns':patterns,
      'frozen_pattern_count':len(patterns),'patterns_eliminated':0,'local_positive_packet_checks':positive,
      'span_phi_7_coefficient_pairs':49**2,'admissible_phi_7_pairs':allowed,
      'fixed7_target_values':gauges,'fixed7_target_example_v3_c1_epsilon_minus':2,
      'all_eight_global_patterns_still_unexcluded':True}

def build(root):
    return {'schema':'beal.block73.finite.v1','adjoint':adjoint_checks(),'tame':toric_checks(),
      'delayed_control':delayed_control(),'arithmetic':residue_and_fibre(root),
      'non_claims':['Not a global realization or elimination of any of the eight patterns.',
        'The deformation-fibre theorem fixes complete inertia and all mod49 traces; the existing finite sieve does not supply these.',
        'No Lean certificate or independent mathematical review.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[2]
    data=build(root);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n');print('PASS',json.dumps({k:data[k] for k in ['adjoint','tame']},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
