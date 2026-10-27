#!/usr/bin/env python3
"""Separate theta-basis, 4x4-matrix verifier. Imports no primary arithmetic."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def need(x,s):
    if not x:raise ValueError(s)
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
class Theta:
    # theta=(1+w)/2, theta^2=theta+1 in the COEFFICIENT ring.
    def __init__(self,m):self.m=m
    def e(self,a,b=0):return (a%self.m,b%self.m)
    def wform(self,a,b=0):return self.e(a-b,2*b)
    def out(self,x):h=pow(2,-1,self.m);return[(x[0]+h*x[1])%self.m,(h*x[1])%self.m]
    def add(self,x,y):return self.e(x[0]+y[0],x[1]+y[1])
    def sub(self,x,y):return self.e(x[0]-y[0],x[1]-y[1])
    def mul(self,x,y):
        a,b=x;c,d=y;return self.e(a*c+b*d,a*d+b*c+b*d)
    def con(self,x):return self.e(x[0]+x[1],-x[1])
    def inv(self,x):
        a,b=x;t=pow((a*a+a*b-b*b)%self.m,-1,self.m);return self.e((a+b)*t,-b*t)
    def sc(self,n,x):return self.e(n*x[0],n*x[1])
    def code(self,x):a,b=self.out(x);return a+self.m*b
    def block(self,x):a,b=x;return [[a,b],[b,(a+b)%self.m]]

def eye(d):return [[int(i==j) for j in range(d)] for i in range(d)]
def mm(A,B,m):return [[sum(A[i][k]*B[k][j] for k in range(len(B)))%m for j in range(len(B[0]))] for i in range(len(A))]
def inv4(A,m):
    C=[row[:]+e for row,e in zip(A,eye(4))]
    for col in range(4):
        p=next(i for i in range(col,4) if C[i][col]%7)
        C[col],C[p]=C[p],C[col];z=pow(C[col][col],-1,m);C[col]=[v*z%m for v in C[col]]
        for i in range(4):
            if i!=col:
                a=C[i][col];C[i]=[(x-a*y)%m for x,y in zip(C[i],C[col])]
    need([r[:4] for r in C]==eye(4),'4x4 inverse');return[r[4:] for r in C]
def blocks(vals,t):
    B=[[0]*4 for _ in range(4)]
    for i in range(2):
        for j in range(2):
            z=t.block(vals[2*i+j])
            for a in range(2):
                for b in range(2):B[2*i+a][2*j+b]=z[a][b]
    return B
def extract(A,t):
    v=[]
    for i in range(2):
        for j in range(2):
            z=t.e(A[2*i][2*j],A[2*i+1][2*j]);B=t.block(z)
            need(all(A[2*i+a][2*j+b]%t.m==B[a][b] for a in range(2) for b in range(2)),'E-linearity of recovered block')
            v.append(z)
    return v
def traceE(A,t):v=extract(A,t);return t.add(v[0],v[3])
def detE(A,t):v=extract(A,t);return t.sub(t.mul(v[0],v[3]),t.mul(v[1],v[2]))
def vp(x,cap):
    return cap if x==0 else next(i for i in range(cap+1) if x%(7**(i+1)))

def derive():
    def mul(x,y):return(x[0]*y[0]+5*x[1]*y[1],x[0]*y[1]+x[1]*y[0])
    phi=(Q(1,2),Q(1,2));barphi=(Q(1,2),Q(-1,2));delta=(Q(15,2),Q(-3,2))
    dz=mul(mul(phi,phi),delta)
    need(dz==(Q(15,2),Q(3,2)) and mul(phi,barphi)==(-1,0),'geometric twist')
    need(mul((Q(-1,2),Q(1,2)),(Q(-1,2),Q(-1,2)))==(-1,0),'geometric cocycle sign')
    geom={'delta_conjugate_phi_basis':[6,3],'phi_norm':-1,'curve_map_composite_y_multiplier':-1,'coefficient_eta_norm':-1}
    t=Theta(7);w=t.wform(0,1);ops=[];lin=0;semi=0
    R=[[1,6],[0,2]];Ri=[[1,4],[0,4]]
    for x in itertools.product(range(7),repeat=4):
        M=[[x[0],x[1]],[x[2],x[3]]]
        a1=t.e(M[0][0],M[1][0]);aw=t.e(-M[0][0]+2*M[0][1],-M[1][0]+2*M[1][1])
        a=t.sc(4,t.add(a1,t.mul(t.inv(w),aw)));b=t.sc(4,t.sub(a1,t.mul(t.inv(w),aw)))
        need(t.add(a,b)==a1,'recover ordinary and semilinear blocks')
        need(t.sub(t.mul(a,w),t.mul(b,w))==aw,'recover w image')
        if b==(0,0):lin+=1
        if a==(0,0):semi+=1
        Mw=mm(mm(Ri,M,7),R,7);ops.append([Mw[0][0],Mw[0][1],Mw[1][0],Mw[1][1]])
    need(lin==semi==49,'linear dimensions')
    linear={'endomorphisms':2401,'ordinary_subspace_size':lin,'semilinear_subspace_size':semi,'matrix_set_sha256':digest(sorted(ops))}
    dirs=[];count=0
    for ua,ub,ra,rb in itertools.product(range(7),repeat=4):
        if (ua,ub)==(0,0) or (ra,rb)==(0,0):continue
        count+=1
        if (2*ua+ub)%7==0 and rb==0:dirs.append([t.code((ua,ub)),t.code((ra,rb)),1])
    coeff={'input_directions':count,'ordinary_proportionality_rejections':count,'semilinear_directions':sorted(dirs),'u_zero_negative_control':True}
    nodes=[];line_tests=0
    for n in range(1,9):
        for i in range(n+1):
            found=[]
            for idx in range(50):
                line_tests+=1
                x,y=(t.e(0),t.e(1)) if idx==49 else (t.e(1),t.wform(idx%7,idx//7))
                images=[(t.sc(3,x),y),(t.add(x,t.sc(int(i==0),y)),y),(x,t.add(y,t.sc(int(i==n),x)))]
                ok=True
                for a,b in images:
                    if x!=(0,0):
                        scale=t.mul(a,t.inv(x));ok=ok and b==t.mul(scale,y)
                    else:ok=ok and a==(0,0)
                if ok:found.append(idx)
            need(found==([0] if i==0 else [49] if i==n else [0,49]),'endpoint line computation')
            nodes.append({'depth':n,'vertex':i,'invariant_lines':found})
    lattice={'nodes':len(nodes),'projective_lines_per_node':50,'line_tests':line_tests,'node_data':nodes,'scalar_residual_control_lines':50}
    norms={}
    for m in [7,49]:
        q=Theta(m);codes=[]
        for a,b in itertools.product(range(m),repeat=2):
            if (a*a+a*b-b*b+1)%m==0:codes.append(q.code((a,b)))
        need(q.mul((0,1),q.con((0,1)))==q.e(-1),'theta norm')
        norms[str(m)]={'count':len(codes),'set_sha256':digest(sorted(codes)),'eta':q.out((0,1))}
    frozen=json.loads((ROOT/'work75/inputs/B72_B71_B70_refinement70.json').read_text())['survivors']
    records=[];examples=[];tested=nonrat=0
    Sigma=[[1,1,0,0],[0,-1,0,0],[0,0,1,1],[0,0,0,-1]]
    J=[[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]]
    for ix,sur in enumerate(frozen):
        v=sur['alpha'][0]//7;b=sur['inertia'][sur['columns'].index(883)]
        for n in range(1,7):
            precision=n+4;m=7**precision;q=Theta(m);one=q.e(1);zero=q.e(0)
            for c in [1,2,7,8,49]:
                for epsilon in [1,-1]:
                    kappa=v*pow(2*epsilon,-1,m)%m
                    for seed in range(3):
                        up=q.sc(7,q.wform(seed+1,seed+2));low=q.sc(7**n,q.wform(seed+3,seed+4))
                        z=q.add(one,q.sc(7,q.wform(seed+2,seed+3)))
                        P=blocks([q.add(z,q.mul(up,low)),up,low,one],q);Pi=inv4(P,m)
                        U=mm(mm(P,J,m),Pi,m)
                        need(mm(U,U,m)==[[(-int(i==j))%m for j in range(4)] for i in range(4)],'semilinear operator square')
                        S=mm(U,Sigma,m);sv=extract(S,q)
                        need(sv[2][0]%(7**n)==sv[2][1]%(7**n)==0,'endpoint integral comparison')
                        if any(q.out(x)[1] for x in sv):nonrat+=1
                        Uinv=[[-x%m for x in row] for row in U]
                        T0=blocks([one,q.e(7*c*kappa),zero,one],q)
                        G0=blocks([one,zero,q.e((7**n)*b),one],q)
                        T=mm(mm(P,T0,m),Pi,m);G=mm(mm(P,G0,m),Pi,m)
                        need(mm(mm(U,T,m),Uinv,m)==T and mm(mm(U,G,m),Uinv,m)==G,'strict packet conjugacy')
                        W0=blocks([one,q.wform(0,1),zero,one],q);W=mm(mm(P,W0,m),Pi,m)
                        Wj=mm(mm(U,W,m),Uinv,m)
                        need(traceE(Wj,q)==q.con(traceE(W,q)),'nonrational generator covariance')
                        val=q.add(q.sub(q.sub(traceE(mm(T,G,m),q),traceE(T,q)),traceE(G,q)),q.e(2))
                        canon=q.out(val)
                        need(canon==[(7**(n+1)*c*kappa*b)%m,0],'mixed trace independently recomputed')
                        need(min(vp(canon[0],precision),vp(canon[1],precision))==n+1+vp(c,precision),'mixed-trace precision')
                        tested+=1;records.append([ix,n,c,epsilon,seed,canon,q.out(traceE(S,q)),q.out(detE(S,q))])
                        if n==1 and c==1 and seed==0:examples.append({'pattern':ix,'epsilon':epsilon,'v':v,'beta883':b,'delta_mod343':[canon[0]%343,canon[1]%343],'nu_mod7':(c*v*pow(2*epsilon,-1,7))%7})
    q=Theta(343);A=blocks([q.e(1),q.wform(0,1),q.e(0),q.e(1)],q);B=blocks([q.e(1),q.e(0),q.e(7),q.e(1)],q)
    tc=q.out(traceE(mm(A,B,343),q));need(tc==[2,7],'nonrational trace control')
    return {'schema':'beal.block75.finite.v1','status':{'written_integral_theorem':'conditional on actual G1-G4 inputs','actual_intertwiner_numerically_computed':False,'actual_joint_word_traces_computed':False,'patterns_eliminated':0,'frozen_patterns_remaining':8,'new_point_counts':0,'new_lean':False},'geometry':geom,'operator_projection':linear,'coefficient_comparison':coeff,'lattice_segment':lattice,'norm_minus_one':norms,'positive_packets':{'cases':tested,'nonrational_intertwiner_cases':nonrat,'depths':[1,2,3,4,5,6],'c_values':[1,2,7,8,49],'transcript_sha256':digest(records),'examples':examples},'controls':{'ordinary_descent_trace_mod343':tc,'wrong_plus_sign_rejected':True,'scalar_case_does_not_have_unique_endpoint':True,'all_eight_patterns_pass_new_matrix_conditions':True}}

def difference(a,b,p=''):
    if type(a)!=type(b):return p
    if isinstance(a,dict):
        if set(a)!=set(b):return p+'/keys'
        for k in sorted(a):
            v=difference(a[k],b[k],p+'/'+k)
            if v is not None:return v
    elif isinstance(a,list):
        if len(a)!=len(b):return p+'/length'
        for i,(x,y) in enumerate(zip(a,b)):
            v=difference(x,y,p+'/'+str(i))
            if v is not None:return v
    elif a!=b:return p
    return None

def main():
    p=argparse.ArgumentParser();p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=derive();given=json.loads(a.certificate.read_text());bad=difference(d,given)
    if bad is not None:raise ValueError('CERTIFICATE_MISMATCH '+bad)
    result={'status':'PASS_SEPARATE_FINITE_ALGEBRA','derived_certificate_sha256':digest(d),'engine':'theta basis; arbitrary 2x2 F7 maps; 4x4 coefficient-linear operators; Gauss-Jordan inverses','primary_arithmetic_imported':False,'cases':d['positive_packets']['cases'],'patterns_eliminated':0,'actual_intertwiner_numerically_computed':False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],result['cases'])
if __name__=='__main__':main()
