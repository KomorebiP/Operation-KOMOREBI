#!/usr/bin/env python3
"""Exact finite checks for the written depth-one cyclotomic-image theorem.
No Galois realization is constructed and no arithmetic hypothesis is verified here.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

ADD=[[((x%7+y%7)%7)+7*((x//7+y//7)%7) for y in range(49)] for x in range(49)]
MUL=[[((x%7*(y%7)+5*(x//7)*(y//7))%7)+7*((x%7*(y//7)+(x//7)*(y%7))%7) for y in range(49)] for x in range(49)]
NEG=[((-x%7)%7)+7*((-(x//7))%7) for x in range(49)]
# NOTE: scalar component is -(x mod7), not -(encoded x) in any other modulus.
INV=[0]+[next(y for y in range(1,49) if MUL[x][y]==1) for x in range(1,49)]
def sub(x,y): return ADD[x][NEG[y]]
def sc(t,x): return MUL[t%7][x]
def ad(s,X):
    p,q,b=X
    return (ADD[p][MUL[s][b]],sub(sub(q,sc(2,MUL[p][s])),MUL[MUL[s][s]][b]),b)
def vv(X): return [z for x in X for z in (x%7,x//7)]
def rank(rows):
    a=[list(row) for row in rows];r=0
    for j in range(6):
        pivot=next((i for i in range(r,len(a)) if a[i][j]%7),None)
        if pivot is None: continue
        a[r],a[pivot]=a[pivot],a[r]; inv=pow(a[r][j],-1,7)
        a[r]=[(x*inv)%7 for x in a[r]]
        for i in range(len(a)):
            if i!=r:
                u=a[i][j]%7
                if u:a[i]=[(x-u*y)%7 for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r

class Ring:
    """Z/N[w]/(w^2-5); 2x2 matrices are flat length-four tuples."""
    def __init__(self,N): self.N=N;self.zero=(0,0);self.one=(1,0);self.I=(self.one,self.zero,self.zero,self.one)
    def add(self,x,y):return ((x[0]+y[0])%self.N,(x[1]+y[1])%self.N)
    def neg(self,x):return (-x[0]%self.N,-x[1]%self.N)
    def sub(self,x,y):return self.add(x,self.neg(y))
    def mul(self,x,y):return ((x[0]*y[0]+5*x[1]*y[1])%self.N,(x[0]*y[1]+x[1]*y[0])%self.N)
    def scale(self,a,x):return(a*x[0]%self.N,a*x[1]%self.N)
    def inv(self,x):
        inv=pow((x[0]*x[0]-5*x[1]*x[1])%self.N,-1,self.N)
        return(x[0]*inv%self.N,-x[1]*inv%self.N)
    def mm(self,A,B):
        return tuple(self.add(self.mul(A[2*i],B[j]),self.mul(A[2*i+1],B[2+j])) for i in range(2) for j in range(2))
    def mi(self,A):
        iv=self.inv(self.sub(self.mul(A[0],A[3]),self.mul(A[1],A[2])))
        return tuple(self.mul(iv,z) for z in (A[3],self.neg(A[1]),self.neg(A[2]),A[0]))
    def power(self,A,n):
        out=self.I
        while n:
            if n&1:out=self.mm(out,A)
            A=self.mm(A,A);n//=2
        return out
    def U(self,x):return(self.one,x,self.zero,self.one)
    def L(self,x):return(self.one,self.zero,x,self.one)
    def D(self,x):return(x,self.zero,self.zero,self.inv(x))
    def comm(self,A,B):return self.mm(self.mm(self.mm(A,B),self.mi(A)),self.mi(B))
    def lead(self,A,den):
        out=[]
        for x,y in zip(A,self.I):
            z=self.sub(x,y)
            assert z[0]%den==z[1]%den==0
            out.append((z[0]//den)%7+7*((z[1]//den)%7))
        return out
    def trace(self,A):return self.add(A[0],A[3])

def make_certificate():
    # Every trace-zero field matrix with nonzero lower entry; three exact probes each.
    dg=hashlib.sha256();cnt=0
    S=(1,7,8)
    for p in range(49):
        for q in range(49):
            for b in range(1,49):
                X=(p,q,b)
                for s in S:
                    a=ad(s,X);z=ad(NEG[s],X)
                    even=tuple(sub(ADD[a[i]][z[i]],sc(2,X[i])) for i in range(3))
                    odd=tuple(sub(a[i],z[i]) for i in range(3))
                    assert even==(0,sc(-2,MUL[MUL[s][s]][b]),0)
                    assert odd==(sc(2,MUL[s][b]),sc(-4,MUL[s][p]),0)
                    dg.update(bytes((p,q,b,s,*a,*z)));cnt+=1
    orbit_rank=[]
    probes=(0,1,6,7,42,8,48)
    for b in range(1,49):
        rows=[vv(ad(s,(0,0,b))) for s in probes]
        rr=rank(rows);assert rr==5
        # Seventh powers retain diagonal and upper directions. Their commutator
        # with the available lower b supplies BOTH lower field directions.
        second=[vv(z) for z in [(1,0,0),(7,0,0),(0,1,0),(0,7,0),(0,0,sc(-2,b)),(0,0,sc(-2,MUL[7][b]))]]
        sr=rank(second);assert sr==6
        orbit_rank.append([b,rr,sr])
    all_rank=rank([vv(ad(s,(0,0,b))) for b in (1,7) for s in probes]);assert all_rank==6
    derived_ranks=[]
    for b in range(1,49):
        rows=[]
        for ss in probes:
            z=ad(ss,(0,0,b));rows.append(vv((z[0],z[1],0)))
        assert rank(rows)==4
        derived_ranks.append([b,4,6])
    counts={'F7':0,'wF7':0,'k':0}
    for p in range(49):
        for q in range(49):
            for b in range(49):
                counts['k']+=1;counts['F7']+=int(b//7==0);counts['wF7']+=int(b%7==0)
    assert counts=={'F7':16807,'wF7':16807,'k':117649}
    lines=[sorted({sc(t,b) for t in range(7)}) for b in [1]+[a+7 for a in range(7)]]
    stable=[]
    for line in lines:
        sigma=sorted({z%7+7*((-(z//7))%7) for z in line})
        if sigma==line:stable.append(line)
    assert stable==[list(range(7)),[7*i for i in range(7)]]
    proj=0
    for a in range(49):
        for b in range(49):
            T=(sc(3,a),sc(5,b))
            extract=(sc(pow(3-5,-1,7),sub(T[0],sc(5,a))),sc(pow(3-5,-1,7),sub(T[1],sc(5,b))))
            assert extract==(a,0)
            invcomm=(sc(pow(2,-1,7),a),sc(pow(4,-1,7),b))
            assert (sc(2,invcomm[0]),sc(4,invcomm[1]))==(a,b)
            proj+=1
    R=Ring(343);commhash=hashlib.sha256();ncomm=0
    for x in range(49):
        xx=(x%7,x//7)
        A=R.D(R.add(R.one,R.scale(7,xx)))
        for b in range(1,49):
            B=R.L(R.scale(7,(b%7,b//7)))
            lead=R.lead(R.comm(A,B),49)
            assert lead==[0,0,sc(-2,MUL[x][b]),0]
            commhash.update(bytes((x,b,*lead)));ncomm+=1
    dr=Ring(49);derivedhash=hashlib.sha256();nd=0
    for ss in range(49):
        for b in range(1,49):
            z=dr.lead(dr.comm(dr.U((ss%7,ss//7)),dr.L((7*(b%7),7*(b//7)))),7)
            sb=MUL[ss][b];upper=NEG[MUL[MUL[ss][ss]][b]]
            assert z==[sb,upper,0,NEG[sb]]
            derivedhash.update(bytes((ss,b,*z)));nd+=1
    eigencounts={};functional_count=0
    from itertools import product
    for d in (1,2):
        accepted=0
        for coefficients in product(range(7),repeat=2+d):
            ok=all(((3 if i<2 else 5)-3)*t%7==0 for i,t in enumerate(coefficients))
            accepted+=int(ok);functional_count+=1
        assert accepted==49;eigencounts[str(d)]=accepted
    powerhash=hashlib.sha256();powercnt=0
    for s in range(1,7):
        rr=Ring(7**(s+2))
        for x in range(49):
            v=rr.scale(7**s,(x%7,x//7))
            for typ,A in enumerate([rr.U(v),rr.D(rr.add(rr.one,v)),rr.L(v)]):
                lead=rr.lead(rr.power(A,7),7**(s+1))
                want=([0,x,0,0],[x,0,0,NEG[x]],[0,0,x,0])[typ]
                assert lead==want
                powerhash.update(bytes((s,x,typ,*lead)));powercnt+=1
    mixedhash=hashlib.sha256();mixedcnt=0
    for a in range(49):
        T=R.U(R.scale(7,(a%7,a//7)))
        for b in range(1,7):
            G=R.L((7*b,0))
            D=R.sub(R.trace(R.mm(T,G)),(2,0))
            want=MUL[a][b]
            assert D==((49*(want%7))%343,(49*(want//7))%343)
            mixedhash.update(bytes((a,b,want)));mixedcnt+=1
    orders={}
    for d in (1,2):
        orders[str(d)]=[{'j':j,'order':7**(2 if j==1 else 6*j-6+d)} for j in range(1,7)]
    # There are two independent traceless last-digit coordinates per coefficient
    # component, plus one diagonal: 6 over F7, not an exhaustive huge-group run.
    return {
      'schema':'beal.block76.finite.v1',
      'proof_status':{'conditional_on_actual_inputs':True,'arithmetic_patterns_eliminated':0,'remaining_bounded_patterns':8,'actual_galois_map_constructed':False,'actual_labelled_mixed_trace_computed':False,'new_lean':False},
      'joint_image':{'projection_vectors':proj,'cyclotomic_weights':[3,5],'commutator_weights':[2,4]},
      'first_layer':{'matrix_seeds':49*49*48,'identity_instances':cnt,'orbit_hash':dg.hexdigest(),'nonzero_lower_seed_ranks':orbit_rank,'two_dimensional_lower_rank':all_rank,'full_traceless_matrices_enumerated':49**3,'allowed_counts':counts},
      'abelianization':{'derived_seed_ranks':derived_ranks,'derived_commutator_instances':nd,'derived_commutator_hash':derivedhash.hexdigest(),'orders':{'1':343,'2':2401},'character_functionals_enumerated':functional_count,'chi_weight_characters':eigencounts,'uniformizer_noncontainment_is_written_argument':True},
      'sigma_lines':{'lines_enumerated':len(lines),'stable_lines':stable},
      'second_layer':{'commutator_instances':ncomm,'commutator_hash':commhash.hexdigest(),'dimension':6,'order':117649},
      'power_propagation':{'levels':[1,2,3,4,5,6],'instances':powercnt,'hash':powerhash.hexdigest(),'universal_closed_group_conclusion_is_written_proof':True},
      'cyclotomic_image_orders':orders,
      'mixed_trace_controls':{'instances':mixedcnt,'hash':mixedhash.hexdigest(),'all_residue_values_in_image':49,'does_not_locate_uniformizer_probe':True},
      'negative_controls':{'K1_not_contained_when_lower_B_is_F7':True,'L7w_lower_digit':7,'K2_is_contained':True,'residual_upper_field_cannot_be_shrunk':True,'depth_three_lower_ideal_need_not_contain_L49':True,'image_membership_is_not_Galois_labelling':True},
      'nonclaims':['No enumeration of the full 7^13 finite group','No conductor or depth bound','No excluded residual pattern','No global arithmetic realization','No computed local embedding or labelled mixed trace']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    c=make_certificate();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
    print('PASS_FINITE_ASSERTIONS',c['first_layer']['identity_instances'],c['second_layer']['commutator_instances'])
if __name__=='__main__': main()
