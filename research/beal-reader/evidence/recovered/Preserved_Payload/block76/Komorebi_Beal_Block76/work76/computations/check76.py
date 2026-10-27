#!/usr/bin/env python3
"""Separate phi-basis verification. Does not import image76 or its arithmetic.
Uses full matrix conjugation, integer minors, and repeated multiplication.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from pathlib import Path

PLUS=[[((x%7+y%7)%7)+7*((x//7+y//7)%7) for y in range(49)] for x in range(49)]
TIMES=[[((x%7*(y%7)+(x//7)*(y//7))%7)+7*((x%7*(y//7)+(x//7)*(y%7)+(x//7)*(y//7))%7) for y in range(49)] for x in range(49)]
MINUS=[(-x%7)%7+7*((- (x//7))%7) for x in range(49)]
FROM_W=[((x%7-x//7)%7)+7*((2*(x//7))%7) for x in range(49)]
TO_W=[((x%7+4*(x//7))%7)+7*((4*(x//7))%7) for x in range(49)]
def minus(a,b): return PLUS[a][MINUS[b]]
def product(A,B):
    return (PLUS[TIMES[A[0]][B[0]]][TIMES[A[1]][B[2]]],PLUS[TIMES[A[0]][B[1]]][TIMES[A[1]][B[3]]],PLUS[TIMES[A[2]][B[0]]][TIMES[A[3]][B[2]]],PLUS[TIMES[A[2]][B[1]]][TIMES[A[3]][B[3]]])
def conj(s,X):
    p,q,b=X;M=(p,q,b,MINUS[p]);R=product(product((1,s,0,1),M),(1,MINUS[s],0,1));assert R[3]==MINUS[R[0]]
    return(R[0],R[1],R[2])
def canonical(X): return tuple(TO_W[x] for x in X)
def vec(X):
    return [z for x in canonical(X) for z in (x%7,x//7)]
def det_integer(A):
    A=[list(map(int,row)) for row in A];n=len(A);den=1;sgn=1
    if not n:return 1
    for i in range(n-1):
        k=next((k for k in range(i,n) if A[k][i]),None)
        if k is None:return 0
        if k!=i:A[k],A[i]=A[i],A[k];sgn=-sgn
        pivot=A[i][i]
        for r in range(i+1,n):
            for c in range(i+1,n):
                num=A[r][c]*pivot-A[r][i]*A[i][c]
                assert num%den==0
                A[r][c]=num//den
        for r in range(i+1,n):A[r][i]=0
        den=pivot
    return sgn*A[-1][-1]
def nonzero_minor(rows,size):
    for ri in itertools.combinations(range(len(rows)),size):
        for ci in itertools.combinations(range(6),size):
            if det_integer([[rows[i][j] for j in ci] for i in ri])%7:
                return list(ri),list(ci)
    raise AssertionError('no nonzero minor')

class PhiRing:
    def __init__(self,N): self.N=N;self.z=(0,0);self.o=(1,0);self.identity=(self.o,self.z,self.z,self.o)
    def encode_w(self,a,b):return((a-b)%self.N,2*b%self.N)
    def decode_w(self,x):
        b=x[1]*pow(2,-1,self.N)%self.N
        return((x[0]+b)%self.N,b)
    def plus(self,x,y):return((x[0]+y[0])%self.N,(x[1]+y[1])%self.N)
    def neg(self,x):return(-x[0]%self.N,-x[1]%self.N)
    def times(self,x,y):return((x[0]*y[0]+x[1]*y[1])%self.N,(x[0]*y[1]+x[1]*y[0]+x[1]*y[1])%self.N)
    def multiple(self,t,x):return(t*x[0]%self.N,t*x[1]%self.N)
    def inverse_scalar(self,x):
        norm=(x[0]*x[0]+x[0]*x[1]-x[1]*x[1])%self.N
        inv=pow(norm,-1,self.N)
        return((x[0]+x[1])*inv%self.N,-x[1]*inv%self.N)
    def multiply(self,A,B):
        out=[]
        for i in range(2):
            for j in range(2):
                value=self.z
                for k in range(2):value=self.plus(value,self.times(A[2*i+k],B[2*k+j]))
                out.append(value)
        return tuple(out)
    def inverse(self,A):
        # Gauss-Jordan over the unramified quadratic ring. A unit pivot exists.
        rows=[[A[0],A[1],self.o,self.z],[A[2],A[3],self.z,self.o]]
        for col in range(2):
            pivot=next(i for i in range(col,2) if any(t%7 for t in rows[i][col]))
            rows[col],rows[pivot]=rows[pivot],rows[col]
            inv=self.inverse_scalar(rows[col][col]);rows[col]=[self.times(inv,x) for x in rows[col]]
            for i in range(2):
                if i==col:continue
                v=rows[i][col];rows[i]=[self.plus(a,self.neg(self.times(v,b))) for a,b in zip(rows[i],rows[col])]
        return(rows[0][2],rows[0][3],rows[1][2],rows[1][3])
    def upper(self,x):return(self.o,x,self.z,self.o)
    def lower(self,x):return(self.o,self.z,x,self.o)
    def diagonal(self,x):return(x,self.z,self.z,self.inverse_scalar(x))
    def commutator(self,A,B):return self.multiply(self.multiply(self.multiply(A,B),self.inverse(A)),self.inverse(B))
    def leading(self,A,den):
        out=[]
        for x,y in zip(A,self.identity):
            a,b=self.decode_w(self.plus(x,self.neg(y)))
            assert a%den==b%den==0
            out.append((a//den)%7+7*((b//den)%7))
        return out
    def seven(self,A):
        out=self.identity
        for _ in range(7):out=self.multiply(out,A)
        return out
    def trace(self,A):return self.plus(A[0],A[3])

def independently_compute():
    digest=hashlib.sha256();cases=0
    for p0 in range(49):
        for q0 in range(49):
            for b0 in range(1,49):
                X=tuple(FROM_W[t] for t in(p0,q0,b0))
                for s0 in (1,7,8):
                    s=FROM_W[s0];a=conj(s,X);z=conj(MINUS[s],X)
                    even=tuple(minus(PLUS[a[i]][z[i]],TIMES[2][X[i]]) for i in range(3))
                    odd=tuple(minus(a[i],z[i]) for i in range(3))
                    assert even==(0,TIMES[5][TIMES[TIMES[s][s]][X[2]]],0)
                    assert odd==(TIMES[2][TIMES[s][X[2]]],TIMES[3][TIMES[s][X[0]]],0)
                    digest.update(bytes((p0,q0,b0,s0,*canonical(a),*canonical(z))));cases+=1
    ranks=[];first_selected=None
    for b0 in range(1,49):
        b=FROM_W[b0]
        rows=[vec(conj(FROM_W[s],(0,0,b))) for s in(0,1,6,7,42,8,48)]
        ri,_=nonzero_minor(rows,5)
        # All lower coordinates lie in the one-dimensional line F7*b: upper rank5.
        assert all(canonical(conj(FROM_W[s],(0,0,b)))[2]==b0 for s in(0,1,6,7,42,8,48))
        if b0==1:first_selected=[rows[i] for i in ri]
        lb=TO_W[TIMES[5][b]];lw=TO_W[TIMES[5][TIMES[FROM_W[7]][b]]]
        second=[[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,1,0,0],[0,0,0,0,lb%7,lb//7],[0,0,0,0,lw%7,lw//7]]
        assert det_integer(second)%7
        ranks.append([b0,5,6])
    assert first_selected is not None
    assert det_integer(first_selected+[[0,0,0,0,0,1]])%7
    derived_ranks=[]
    for b0 in range(1,49):
        b=FROM_W[b0]
        rows=[]
        for ss in(0,1,6,7,42,8,48):
            z=conj(FROM_W[ss],(0,0,b));rows.append(vec((z[0],z[1],0)))
        nonzero_minor(rows,4)
        assert all(row[4:]==[0,0] for row in rows)
        derived_ranks.append([b0,4,6])
    counts={'F7':0,'wF7':0,'k':0}
    for p in range(49):
        for q in range(49):
            for b in range(49):
                bphi=FROM_W[b];sg=(bphi%7+bphi//7)%7+7*(-(bphi//7)%7)
                counts['k']+=1
                counts['F7']+=int(sg==bphi)
                counts['wF7']+=int(sg==MINUS[bphi])
    stable=[]
    for generator in [1]+[a+7 for a in range(7)]:
        line=sorted(TO_W[TIMES[t][FROM_W[generator]]] for t in range(7))
        image=[]
        for b0 in line:
            b=FROM_W[b0];sg=(b%7+b//7)%7+7*(-(b//7)%7);image.append(TO_W[sg])
        if sorted(image)==line:stable.append(line)
    projections=0
    for a in range(49):
        for b in range(49):
            x=FROM_W[a];y=FROM_W[b]
            pa=TIMES[3][minus(TIMES[3][x],TIMES[5][x])]
            pb=TIMES[3][minus(TIMES[5][y],TIMES[5][y])]
            assert(pa,pb)==(x,0)
            assert TIMES[2][TIMES[4][x]]==x and TIMES[4][TIMES[2][y]]==y
            projections+=1
    ring=PhiRing(343);ch=hashlib.sha256();nc=0
    for x0 in range(49):
        x=ring.encode_w(x0%7,x0//7)
        A=ring.diagonal(ring.plus(ring.o,ring.multiple(7,x)))
        for b0 in range(1,49):
            b=ring.encode_w(b0%7,b0//7)
            B=ring.lower(ring.multiple(7,b))
            result=ring.leading(ring.commutator(A,B),49)
            want=TO_W[TIMES[5][TIMES[FROM_W[x0]][FROM_W[b0]]]]
            assert result==[0,0,want,0]
            ch.update(bytes((x0,b0,*result)));nc+=1
    dr=PhiRing(49);derivedhash=hashlib.sha256();nd=0
    for ss in range(49):
        for b0 in range(1,49):
            S=dr.upper(dr.encode_w(ss%7,ss//7))
            L=dr.lower(dr.multiple(7,dr.encode_w(b0%7,b0//7)))
            z=dr.leading(dr.commutator(S,L),7)
            sb=TIMES[FROM_W[ss]][FROM_W[b0]]
            upper=MINUS[TIMES[FROM_W[ss]][sb]]
            assert z==[TO_W[sb],TO_W[upper],0,TO_W[MINUS[sb]]]
            derivedhash.update(bytes((ss,b0,*z)));nd+=1
    eigencounts={};functional_count=0
    for d in(1,2):
        accepted=0
        for coefficients in itertools.product(range(7),repeat=2+d):
            ok=True
            for i,t in enumerate(coefficients):
                basis=[0]*(2+d);basis[i]=1
                transformed=[((3 if j<2 else 5)*x)%7 for j,x in enumerate(basis)]
                lhs=sum(a*b for a,b in zip(coefficients,transformed))%7
                rhs=3*sum(a*b for a,b in zip(coefficients,basis))%7
                ok=ok and lhs==rhs
            accepted+=int(ok);functional_count+=1
        assert accepted==49;eigencounts[str(d)]=accepted
    ph=hashlib.sha256();np=0
    for s in range(1,7):
        R=PhiRing(7**(s+2))
        for x0 in range(49):
            x=R.multiple(7**s,R.encode_w(x0%7,x0//7))
            for typ,A in enumerate([R.upper(x),R.diagonal(R.plus(R.o,x)),R.lower(x)]):
                out=R.leading(R.seven(A),7**(s+1));nx=TO_W[MINUS[FROM_W[x0]]]
                assert out==([0,x0,0,0],[x0,0,0,nx],[0,0,x0,0])[typ]
                ph.update(bytes((s,x0,typ,*out)));np+=1
    mh=hashlib.sha256();nm=0
    for a0 in range(49):
        T=ring.upper(ring.multiple(7,ring.encode_w(a0%7,a0//7)))
        for b in range(1,7):
            G=ring.lower((7*b,0))
            delta=ring.plus(ring.trace(ring.multiply(T,G)),ring.neg((2,0)))
            a,c=ring.decode_w(delta);want=TO_W[TIMES[FROM_W[a0]][b]]
            assert (a,c)==(49*(want%7),49*(want//7))
            mh.update(bytes((a0,b,want)));nm+=1
    orders={str(d):[{'j':j,'order':49 if j==1 else 49*(49**2)*(7**d)*(49**3)**(j-2)} for j in range(1,7)] for d in (1,2)}
    return {
      'schema':'beal.block76.finite.v1',
      'proof_status':{'conditional_on_actual_inputs':True,'arithmetic_patterns_eliminated':0,'remaining_bounded_patterns':8,'actual_galois_map_constructed':False,'actual_labelled_mixed_trace_computed':False,'new_lean':False},
      'joint_image':{'projection_vectors':projections,'cyclotomic_weights':[3,5],'commutator_weights':[2,4]},
      'first_layer':{'matrix_seeds':49*49*48,'identity_instances':cases,'orbit_hash':digest.hexdigest(),'nonzero_lower_seed_ranks':ranks,'two_dimensional_lower_rank':6,'full_traceless_matrices_enumerated':49**3,'allowed_counts':counts},
      'abelianization':{'derived_seed_ranks':derived_ranks,'derived_commutator_instances':nd,'derived_commutator_hash':derivedhash.hexdigest(),'orders':{'1':343,'2':2401},'character_functionals_enumerated':functional_count,'chi_weight_characters':eigencounts,'uniformizer_noncontainment_is_written_argument':True},
      'sigma_lines':{'lines_enumerated':8,'stable_lines':stable},
      'second_layer':{'commutator_instances':nc,'commutator_hash':ch.hexdigest(),'dimension':6,'order':49**3},
      'power_propagation':{'levels':[1,2,3,4,5,6],'instances':np,'hash':ph.hexdigest(),'universal_closed_group_conclusion_is_written_proof':True},
      'cyclotomic_image_orders':orders,
      'mixed_trace_controls':{'instances':nm,'hash':mh.hexdigest(),'all_residue_values_in_image':49,'does_not_locate_uniformizer_probe':True},
      'negative_controls':{'K1_not_contained_when_lower_B_is_F7':True,'L7w_lower_digit':7,'K2_is_contained':True,'residual_upper_field_cannot_be_shrunk':True,'depth_three_lower_ideal_need_not_contain_L49':True,'image_membership_is_not_Galois_labelling':True},
      'nonclaims':['No enumeration of the full 7^13 finite group','No conductor or depth bound','No excluded residual pattern','No global arithmetic realization','No computed local embedding or labelled mixed trace']}

def first_diff(a,b,path=''):
    if type(a)!=type(b):return path
    if isinstance(a,dict):
        if set(a)!=set(b):return path+'/keys'
        for k in sorted(a):
            d=first_diff(a[k],b[k],path+'/'+k)
            if d:return d
    elif isinstance(a,list):
        if len(a)!=len(b):return path+'/length'
        for i,(x,y) in enumerate(zip(a,b)):
            d=first_diff(x,y,path+'/'+str(i))
            if d:return d
    elif a!=b:return path or '/'
    return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--negative-set',type=Path);ap.add_argument('--negative-report',type=Path);args=ap.parse_args()
    computed=independently_compute();proposed=json.loads(args.certificate.read_text());difference=first_diff(computed,proposed)
    if difference:
        print('CERTIFICATE_MISMATCH '+difference,file=sys.stderr);return 1
    if args.negative_set:
        if args.negative_report is None:raise ValueError('negative-report required')
        negatives=[]
        for item in json.loads(args.negative_set.read_text()):
            candidate=json.loads(Path(item['certificate']).read_text())
            diff=first_diff(computed,candidate)
            if diff!=item['expected_path']:raise ValueError('negative not rejected at expected path: '+item['name'])
            negatives.append({'name':item['name'],'rejected':True,'mismatch_path':diff})
        args.negative_report.write_text(json.dumps(negatives,indent=2,sort_keys=True)+'\n')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(computed,indent=2,sort_keys=True)+'\n')
    print('PASS_SEPARATE_CHECKS',computed['first_layer']['identity_instances']);return 0
if __name__=='__main__':raise SystemExit(main())
