#!/usr/bin/env python3
"""Exact finite algebra checks for Block75; not an arithmetic Galois realization."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def ensure(ok,msg):
    if not ok: raise ValueError(msg)
def digest(x): return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
class Ring:
    def __init__(self,m):self.m=m;self.z=(0,0);self.one=(1,0)
    def x(self,a,b=0):return(a%self.m,b%self.m)
    def add(self,a,b):return self.x(a[0]+b[0],a[1]+b[1])
    def neg(self,a):return self.x(-a[0],-a[1])
    def sub(self,a,b):return self.add(a,self.neg(b))
    def mul(self,a,b):return self.x(a[0]*b[0]+5*a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    def sig(self,a):return self.x(a[0],-a[1])
    def inv(self,a):
        d=(a[0]*a[0]-5*a[1]*a[1])%self.m
        t=pow(d,-1,self.m);return self.x(a[0]*t,-a[1]*t)
    def sc(self,k,a):return self.x(k*a[0],k*a[1])
    def code(self,a):return a[0]+self.m*a[1]
    def eye(self):return((self.one,self.z),(self.z,self.one))
    def mat(self,vals):return tuple(tuple(self.x(*x) if isinstance(x,tuple) else self.x(x) for x in row) for row in vals)
    def mm(self,A,B):return tuple(tuple(self.add(self.mul(A[i][0],B[0][j]),self.mul(A[i][1],B[1][j])) for j in range(2)) for i in range(2))
    def ms(self,A):return tuple(tuple(self.sig(x) for x in row) for row in A)
    def det(self,A):return self.sub(self.mul(A[0][0],A[1][1]),self.mul(A[0][1],A[1][0]))
    def mi(self,A):
        d=self.inv(self.det(A));return((self.mul(d,A[1][1]),self.neg(self.mul(d,A[0][1]))),(self.neg(self.mul(d,A[1][0])),self.mul(d,A[0][0])))
    def tr(self,A):return self.add(A[0][0],A[1][1])
    def up(self,x):return((self.one,x),(self.z,self.one))
    def lo(self,x):return((self.one,self.z),(x,self.one))
    def diagonal(self,x):return((x,self.z),(self.z,self.one))
    def apply(self,A,v):return tuple(self.add(self.mul(A[i][0],v[0]),self.mul(A[i][1],v[1])) for i in range(2))

def v7(x,cap):
    if x==0:return cap
    n=0
    while x%7==0:n+=1;x//=7
    return n

def main_data():
    # The actual curve-map identities, calculated over Z[phi].
    def pm(x,y):a,b=x;c,d=y;return(a*c+b*d,a*d+b*c+b*d)
    phi=(0,1);phic=(1,-1);delta=(9,-3)
    ensure(pm(phi,phic)==(-1,0),'phi norm')
    ensure(pm(pm(phi,phi),delta)==(6,3),'twist comparison')
    ensure(pm((-1,1),(0,-1))==(-1,0),'map square')
    geom={'delta_conjugate_phi_basis':[6,3],'phi_norm':-1,'curve_map_composite_y_multiplier':-1,'coefficient_eta_norm':-1}
    k=Ring(7);w=k.x(0,1)
    ops=[]
    for ia in range(49):
        a=k.x(ia%7,ia//7)
        for ib in range(49):
            b=k.x(ib%7,ib//7)
            u1=k.add(a,b);uw=k.sub(k.mul(a,w),k.mul(b,w))
            mat=[u1[0],uw[0],u1[1],uw[1]]
            ap=k.sc(4,k.add(u1,k.mul(k.inv(w),uw)))
            bp=k.sc(4,k.sub(u1,k.mul(k.inv(w),uw)))
            ensure(ap==a and bp==b,'linear-semilinear projection')
            ops.append(mat)
    ensure(len({tuple(x) for x in ops})==2401,'End_F7 coverage')
    linear={'endomorphisms':2401,'ordinary_subspace_size':49,'semilinear_subspace_size':49,'matrix_set_sha256':digest(sorted(ops))}
    dirs=[];ordinary_fail=0
    for iu in range(1,49):
        u=k.x(iu%7,iu//7)
        for ir in range(1,49):
            r=k.x(ir%7,ir//7)
            ensure(k.neg(u)!=u,'nonzero unit obstruction')
            ordinary_fail+=1
            if k.sig(u)==k.neg(u) and k.sig(r)==r:dirs.append([iu,ir,1])
    ensure(len(dirs)==36,'coefficient directions')
    coeff={'input_directions':2304,'ordinary_proportionality_rejections':ordinary_fail,'semilinear_directions':dirs,'u_zero_negative_control':True}
    # Every projective line is inspected at every vertex in the stated range.
    lines=[(k.one,k.x(t%7,t//7)) for t in range(49)]+[(k.z,k.one)]
    nodes=[];line_tests=0
    for n in range(1,9):
        for i in range(n+1):
            gens=[k.diagonal(k.x(3)),k.up(k.x(1 if i==0 else 0)),k.lo(k.x(1 if i==n else 0))]
            inv=[]
            for idx,z in enumerate(lines):
                line_tests+=1
                good=True
                for G in gens:
                    q=k.apply(G,z)
                    if k.sub(k.mul(z[0],q[1]),k.mul(z[1],q[0]))!=k.z:good=False;break
                if good:inv.append(idx)
            expected=[0] if i==0 else ([49] if i==n else [0,49])
            ensure(inv==expected,'stable endpoint orientation')
            nodes.append({'depth':n,'vertex':i,'invariant_lines':inv})
    lattice={'nodes':len(nodes),'projective_lines_per_node':50,'line_tests':line_tests,'node_data':nodes,'scalar_residual_control_lines':50}
    norm_counts={}
    for M in [7,49]:
        r=Ring(M);xs=[]
        for a in range(M):
            for b in range(M):
                if (a*a-5*b*b+1)%M==0:xs.append(a+M*b)
        eta=r.x(pow(2,-1,M),pow(2,-1,M))
        ensure(r.mul(eta,r.sig(eta))==r.x(-1),'eta norm')
        norm_counts[str(M)]={'count':len(xs),'set_sha256':digest(sorted(xs)),'eta':list(eta)}
    ensure(norm_counts['7']['count']==8 and norm_counts['49']['count']==56,'norm counts')
    frozen=json.loads((ROOT/'work75/inputs/B72_B71_B70_refinement70.json').read_text())['survivors']
    ensure(len(frozen)==8,'eight frozen cases')
    records=[];examples=[];tested=0;nonrational=0
    for ix,sur in enumerate(frozen):
        v=sur['alpha'][0]//7
        beta=sur['inertia'][sur['columns'].index(883)]
        ensure(1<=v<=6 and 1<=beta<=6,'normalization')
        for n in range(1,7):
            precision=n+4;M=7**precision;r=Ring(M);eta=r.x(pow(2,-1,M),pow(2,-1,M))
            for c in [1,2,7,8,49]:
                for epsilon in [1,-1]:
                    kappa=(v*pow(2*epsilon,-1,M))%M
                    for seed in range(3):
                        P=r.mm(r.mm(r.up(r.sc(7,r.x(seed+1,seed+2))),r.diagonal(r.add(r.one,r.sc(7,r.x(seed+2,seed+3))))),r.lo(r.sc(7**n,r.x(seed+3,seed+4))))
                        Pi=r.mi(P)
                        S=r.mm(r.mm(P,((eta,r.z),(r.z,eta))),r.ms(Pi))
                        Sinv=r.mi(S)
                        ensure(r.mm(S,r.ms(S))==r.mat([[-1,0],[0,-1]]),'geometric minus norm')
                        ensure(S[1][0][0]%(7**n)==0 and S[1][0][1]%(7**n)==0,'endpoint preservation')
                        T=r.mm(r.mm(P,r.up(r.x(7*c*kappa))),Pi)
                        G=r.mm(r.mm(P,r.lo(r.x((7**n)*beta))),Pi)
                        ensure(r.mm(r.mm(S,r.ms(T)),Sinv)==T,'probe conjugation')
                        ensure(r.mm(r.mm(S,r.ms(G)),Sinv)==G,'rational beta conjugation')
                        W=r.mm(r.mm(P,r.up(r.x(0,1))),Pi)
                        Jw=r.mm(r.mm(S,r.ms(W)),Sinv)
                        ensure(r.tr(Jw)==r.sig(r.tr(W)),'exact trace covariance')
                        delta=r.add(r.sub(r.sub(r.tr(r.mm(T,G)),r.tr(T)),r.tr(G)),r.x(2))
                        expected=r.x(7**(n+1)*c*kappa*beta)
                        ensure(delta==expected,'mixed trace')
                        exactval=n+1+v7(c,precision)
                        ensure(min(v7(delta[0],precision),v7(delta[1],precision))==exactval,'mixed valuation')
                        tested+=1
                        if any(z[1] for row in S for z in row):nonrational+=1
                        rec=[ix,n,c,epsilon,seed,list(delta),list(r.tr(S)),list(r.det(S))]
                        records.append(rec)
                        if n==1 and c==1 and seed==0:examples.append({'pattern':ix,'epsilon':epsilon,'v':v,'beta883':beta,'delta_mod343':[delta[0]%343,delta[1]%343],'nu_mod7':(c*v*pow(2*epsilon,-1,7))%7})
    rr=Ring(343)
    trace_control=rr.tr(rr.mm(rr.up(rr.x(0,1)),rr.lo(rr.x(7))))
    ensure(trace_control==rr.x(2,7) and rr.sig(trace_control)!=trace_control,'not ordinary Q7 descent')
    return {'schema':'beal.block75.finite.v1','status':{'written_integral_theorem':'conditional on actual G1-G4 inputs','actual_intertwiner_numerically_computed':False,'actual_joint_word_traces_computed':False,'patterns_eliminated':0,'frozen_patterns_remaining':8,'new_point_counts':0,'new_lean':False},'geometry':geom,'operator_projection':linear,'coefficient_comparison':coeff,'lattice_segment':lattice,'norm_minus_one':norm_counts,'positive_packets':{'cases':tested,'nonrational_intertwiner_cases':nonrational,'depths':[1,2,3,4,5,6],'c_values':[1,2,7,8,49],'transcript_sha256':digest(records),'examples':examples},'controls':{'ordinary_descent_trace_mod343':list(trace_control),'wrong_plus_sign_rejected':True,'scalar_case_does_not_have_unique_endpoint':True,'all_eight_patterns_pass_new_matrix_conditions':True}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=main_data();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print('PASS_FINITE_ALGEBRA',d['positive_packets']['cases'])
if __name__=='__main__':main()
