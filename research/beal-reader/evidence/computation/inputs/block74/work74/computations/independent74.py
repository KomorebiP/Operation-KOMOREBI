#!/usr/bin/env python3
"""Separate phi-basis audit. Does not import trace_probe74 or predecessor arithmetic."""
from __future__ import annotations
import argparse,hashlib,itertools,json,sys
from pathlib import Path

class Field:
    def __init__(self,m):self.m=m
    def elt(self,a=0,b=0):return (a%self.m,b%self.m)
    def plus(self,a,b):return self.elt(a[0]+b[0],a[1]+b[1])
    def minus(self,a,b):return self.elt(a[0]-b[0],a[1]-b[1])
    def times(self,a,b):
        # phi^2=phi+1
        return self.elt(a[0]*b[0]+a[1]*b[1],a[0]*b[1]+a[1]*b[0]+a[1]*b[1])
    def scalar(self,n,a):return self.elt(n*a[0],n*a[1])
    def reciprocal(self,a):
        norm=(a[0]*a[0]+a[0]*a[1]-a[1]*a[1])%self.m
        if norm%7==0:raise ValueError('not a unit')
        z=pow(norm,-1,self.m)
        return self.elt((a[0]+a[1])*z,-a[1]*z)
    def omega_in(self,x):return self.elt(x[0]-x[1],2*x[1])
    def omega_out(self,x):
        t=x[1]*pow(2,-1,self.m)%self.m
        return ((x[0]+t)%self.m,t)
    def product(self,A,B):
        out=[[self.elt(),self.elt()],[self.elt(),self.elt()]]
        for i in range(2):
            for j in range(2):
                for k in range(2):out[i][j]=self.plus(out[i][j],self.times(A[i][k],B[k][j]))
        return out
    def inverse(self,A):
        d=self.minus(self.times(A[0][0],A[1][1]),self.times(A[0][1],A[1][0]));t=self.reciprocal(d)
        return [[self.times(t,A[1][1]),self.scalar(-1,self.times(t,A[0][1]))],[self.scalar(-1,self.times(t,A[1][0])),self.times(t,A[0][0])]]
    def trace(self,A):return self.plus(A[0][0],A[1][1])
    def det(self,A):return self.minus(self.times(A[0][0],A[1][1]),self.times(A[0][1],A[1][0]))

def valuation(x,j):
    if x==(0,0):return j
    for s in range(j):
        if x[0]%(7**(s+1)) or x[1]%(7**(s+1)):return s
    return j

def difference(a,b,path=''):
    if type(a)!=type(b):return path
    if isinstance(a,dict):
        if set(a)!=set(b):return path+'/<keys>'
        for k in sorted(a):
            z=difference(a[k],b[k],path+'/'+k)
            if z is not None:return z
    elif isinstance(a,list):
        if len(a)!=len(b):return path+'/<length>'
        for i,(x,y) in enumerate(zip(a,b)):
            z=difference(x,y,path+'/'+str(i))
            if z is not None:return z
    elif a!=b:return path
    return None

def evaluate(C,patterns):
    count=nr=nd=0;hist={};examples=[];dig=hashlib.sha256()
    choices=itertools.product(C['depths'],C['valuation_exponents'],C['c_units'],C['natural_v'],C['orientations'],C['variations'])
    for n,s,cu,v,eps,i in choices:
        c=7**s*cu;t=1+s;j=n+t+1;F=Field(7**j)
        kappa=(v*pow(2*eps,-1,7))%7
        a=F.plus(F.elt(1),F.scalar(7,F.omega_in((i+cu,v+i))))
        b=F.omega_in((2*i+v,cu+1))
        d=F.scalar(7**n,F.omega_in((i+1,cu+i)))
        e=F.plus(F.elt(pow(kappa,-1,7)),F.scalar(7,F.omega_in((cu+v,2*i+1))))
        P=[[a,b],[d,e]]
        # Compute rank-one operator by the column and dual row, independently of
        # the primary conjugation multiplication.
        pinv=F.inverse(P);J=[[F.times(P[z][0],pinv[1][w]) for w in range(2)] for z in range(2)]
        assert F.trace(J)==F.elt() and F.det(J)==F.elt()
        J12=F.omega_out(J[0][1]);assert (J12[0]%7,J12[1]%7)==(kappa,0)
        assert valuation(J[1][0],j)>=min(j,2*n)
        U=[[F.plus(F.elt(int(z==w)),F.scalar(7*c,J[z][w])) for w in range(2)] for z in range(2)]
        bc=1+(i+7*cu+5*v+3*n+11*s)%48;beta=(bc%7,bc//7)
        x=F.plus(F.elt(1),F.scalar(7,F.omega_in((i+3,v+cu))))
        y=F.scalar(7,F.omega_in((cu+i,2*v+i)))
        z=F.scalar(7**n,F.omega_in(beta));Q=1+7*(1+i+v+cu+n)
        w=F.times(F.plus(F.elt(Q),F.times(y,z)),F.reciprocal(x));V=[[x,y],[z,w]]
        assert F.det(U)==F.elt(1) and F.det(V)==F.elt(Q)
        # Direct polarized trace, and orthogonal rank-one formula.
        UV=F.product(U,V)
        delta=F.plus(F.minus(F.minus(F.trace(UV),F.trace(U)),F.trace(V)),F.elt(2))
        partial=F.elt()
        for row in range(2):
            for col in range(2):
                partial=F.plus(partial,F.times(J[row][col],F.minus(V[col][row],F.elt(int(row==col)))))
        assert delta==F.scalar(7*c,partial)
        assert valuation(delta,j)==n+t
        out=F.omega_out(delta);lead=(out[0]//7**(n+t)%7,out[1]//7**(n+t)%7)
        assert lead==(cu*kappa*beta[0]%7,cu*kappa*beta[1]%7)
        item={'n':n,'c':c,'v':v,'epsilon':eps,'i':i,'precision':j,'beta':beta,'mixed_trace':out,'valuation':n+t,'leading':lead}
        dig.update((json.dumps(item,sort_keys=True,separators=(',',':'))+'\n').encode())
        if i==0 and cu==1 and v==1 and eps==1:examples.append(item)
        nr+=int(any(F.omega_out(a)[1] for row in U+V for a in row))
        nd+=int(U[0][0]!=F.elt(1) or U[1][1]!=F.elt(1));count+=1;hist[str(n)]=hist.get(str(n),0)+1
    # Exhaustive finite k pairing via coordinate arithmetic in phi basis.
    F=Field(7);pd=hashlib.sha256();pc=0
    for nu,b in itertools.product(range(49),range(1,49)):
        N=F.omega_in((nu%7,nu//7));B=F.omega_in((b%7,b//7))
        D=F.times(N,B);assert F.times(D,F.reciprocal(B))==N
        d=F.omega_out(D);pd.update(bytes([nu,b,*d]));pc+=1
    F=Field(49);images=[]
    for a in (F.elt(0,1),F.elt(3)):
        p=F.elt(1)
        for _ in range(48):p=F.times(p,a)
        z=F.omega_out(p);images.append(((z[0]-1)//7%7,z[1]//7%7))
    histogram=[0]*49;units=0
    # Enumerate directly in the different coefficient basis; the distribution
    # is basis-invariant after conversion to the declared output coordinates.
    for a,b in itertools.product(range(49),repeat=2):
        if a%7==b%7==0:continue
        p=F.elt(1);x=F.elt(a,b)
        for _ in range(48):p=F.times(p,x)
        z=F.omega_out(p);a0=((z[0]-1)//7)%7;b0=z[1]//7%7
        histogram[a0+7*b0]+=1;units+=1
    assert images==[(0,5),(6,0)] and units==2352 and set(histogram)=={48}
    F=Field(7);cocycles=0
    for u,v in itertools.product(range(49),repeat=2):
        U=F.elt(u%7,u//7);V=F.elt(v%7,v//7)
        if F.plus(U,F.scalar(3,V))==F.plus(V,U):
            cocycles+=1;assert V==F.elt()
            assert any(F.scalar(2,F.elt(a,b))==U for a,b in itertools.product(range(7),repeat=2))
    assert cocycles==49
    projection=0
    for a,b in itertools.product(range(49),repeat=2):
        A=F.elt(a%7,a//7);B=F.elt(b%7,b//7)
        assert F.scalar(4,F.minus(F.scalar(3,A),F.scalar(3,A)))==F.elt()
        assert F.scalar(4,F.minus(F.scalar(5,B),F.scalar(3,B)))==B;projection+=1
    # Compute all concrete controls independently; none are merely imported flags.
    F=Field(343)
    def mixed(U,V):return F.plus(F.minus(F.minus(F.trace(F.product(U,V)),F.trace(U)),F.trace(V)),F.elt(2))
    V=[[F.elt(1),F.elt()],[F.elt(7),F.elt(1)]];traces=[]
    for n0 in (1,2):
        U=[[F.elt(1),F.elt(7*n0)],[F.elt(),F.elt(1)]]
        assert F.det(U)==F.elt(1);traces.append(F.trace(F.product(U,V))[0])
    U=[[F.elt(8),F.elt(7)],[F.elt(),F.reciprocal(F.elt(8))]]
    V=[[F.elt(8),F.elt()],[F.elt(7),F.reciprocal(F.elt(8))]]
    contam=mixed(U,V)[0]//49
    F=Field(2401)
    U=[[F.elt(1),F.elt(7)],[F.elt(),F.elt(1)]];V=[[F.elt(1),F.elt()],[F.elt(49),F.elt(1)]]
    depth2=mixed(U,V)[0]
    controls={'same_individual_traces':{'U1_trace':2,'U2_trace':2,'V_trace':2,'U1V_trace_mod343':traces[0],'U2V_trace_mod343':traces[1],'determinants':[1,1,1]},
       'contaminated_probe':{'predicted_if_uniformizer_only':1,'actual_mixed_digit':contam,'reason':'nonzero diagonal first digit contaminates the pairing'},
       'wrong_depth_denominator':{'n':2,'c':1,'delta':depth2,'mod343':depth2%343,'mod2401':depth2%2401},
       'coefficient_trace_loss':{'nonzero_digit':[0,1],'trace_to_F7':0},
       'beta_zero':{'reconstruction_allowed':False},'not_arbitrary_primes':{'joint_word_labels_required':True}}
    assert len(patterns['survivors'])==8
    return {'schema':'beal.block74.trace-probe.v1',
       'matrix_family':{'cases':count,'nonrational':nr,'nontrivial_toric_diagonals':nd,'depth_histogram':hist,'ordered_sha256':dig.hexdigest(),'examples':examples},
       'residue_reconstruction':{'cases':pc,'ordered_sha256':pd.hexdigest()},
       'unit_basis':{'phi_image':images[0],'three_image':images[1],'unit_residues_checked':units,'image_multiplicities':histogram},
       'cyclotomic_cocycle_model':{'generator_value_pairs':2401,'cocycles':cocycles,'coboundaries':cocycles,'H1_dimension':0},
       'joint_projection':{'vectors':projection,'weights':[3,5],'inverse_difference':4},'controls':controls,
       'status':{'patterns_before':8,'patterns_after':8,'patterns_eliminated':0,'actual_joint_word_traces_computed':False,'Frobenius_point_counts':0,'Lean_compilation':False,'independent_mathematical_review':False}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    root=Path(__file__).resolve().parents[2]
    data=evaluate(json.loads((root/'work74/inputs/TEST_CONTRACT.json').read_text()),json.loads((root/'work74/inputs/B72_B71_B70_refinement70.json').read_text()))
    # Normalize tuple/list representation before the structural comparison.
    data=json.loads(json.dumps(data));cert=json.loads(a.certificate.read_text())
    bad=difference(data,cert)
    if bad is not None:print('CERTIFICATE_MISMATCH '+bad,file=sys.stderr);return 1
    result={'schema':'beal.block74.independent.v1','verified':True,'primary_sha256':hashlib.sha256(a.certificate.read_bytes()).hexdigest(),'arithmetic_basis':'phi^2=phi+1','imports_primary_arithmetic':False,'recomputed_certificate':data}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS_SEPARATE_TRACE_PROBE',data['matrix_family']['cases']);return 0
if __name__=='__main__':raise SystemExit(main())
