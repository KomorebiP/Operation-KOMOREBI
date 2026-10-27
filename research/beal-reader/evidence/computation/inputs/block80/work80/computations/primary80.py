#!/usr/bin/env python3
"""Exact finite certificates for Block 80. Standard library only.
This program does not construct a global inhomogeneous cochain p0.
"""
from __future__ import annotations
import itertools, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def require(ok: bool, message: str) -> None:
    if not ok: raise ValueError(message)

class Quad:
    """Z/m[w]/(w^2-5), also used for the quadratic residue fields."""
    def __init__(self,m:int): self.m=m
    def add(self,x,y): return ((x[0]+y[0])%self.m,(x[1]+y[1])%self.m)
    def mul(self,x,y):
        a,b=x;c,d=y;m=self.m
        return ((a*c+5*b*d)%m,(a*d+b*c)%m)
    def power(self,x,n:int):
        out=(1,0)
        while n:
            if n&1:out=self.mul(out,x)
            x=self.mul(x,x);n//=2
        return out
    def phi(self): return (pow(2,-1,self.m),pow(2,-1,self.m))
    def phi_pair(self,x):
        h=pow(2,-1,self.m);return ((x[0]+h*x[1])%self.m,h*x[1]%self.m)
    def ev(self,cs,z):
        out=(0,0)
        for c in reversed(cs):out=self.add(self.mul(out,z),(c%self.m,0))
        return out

def factors(n:int):
    out=[];d=2
    while d*d<=n:
        if n%d==0:
            out.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:out.append(n)
    return out

def determinant(A):
    A=[r[:] for r in A];n=len(A);sign=1;previous=1
    if not n:return 1
    for k in range(n-1):
        j=next((j for j in range(k,n) if A[j][k]),None)
        if j is None:return 0
        if j!=k:A[j],A[k]=A[k],A[j];sign=-sign
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=pivot*A[i][j]-A[i][k]*A[k][j]
                require(num%previous==0,'inexact Bareiss division')
                A[i][j]=num//previous
        for i in range(k+1,n):A[i][k]=0
        previous=pivot
    return sign*A[-1][-1]

def cyclo_norm(cs):
    cols=[]
    for j in range(6):
        a=[0]*j+list(cs)+[0]*(5-j)
        for i in range(10,5,-1):
            z=a[i]
            for k in range(i-6,i):a[k]-=z
        cols.append(a[:6])
    return determinant(list(map(list,zip(*cols))))

def rr(A):
    A=[[x%7 for x in r] for r in A];piv=[];i=0
    for j in range(len(A[0])):
        k=next((k for k in range(i,len(A)) if A[k][j]),None)
        if k is None:continue
        A[i],A[k]=A[k],A[i];iv=pow(A[i][j],-1,7);A[i]=[x*iv%7 for x in A[i]]
        for k in range(len(A)):
            if k!=i:
                v=A[k][j];A[k]=[(x-v*y)%7 for x,y in zip(A[k],A[i])]
        piv.append(j);i+=1
        if i==len(A):break
    return A,piv

def null(A):
    R,p=rr(A);n=len(A[0]);out=[]
    for j in range(n):
        if j in p:continue
        x=[0]*n;x[j]=1
        for i,k in enumerate(p):x[k]=-R[i][j]%7
        out.append(x)
    return out

def transpose(A):return list(map(list,zip(*A)))
def matmul(A,B):return [[sum(x*y for x,y in zip(row,col))%7 for col in zip(*B)] for row in A]
def matvec(A,v):return [sum(x*y for x,y in zip(r,v))%7 for r in A]
def rank(A):return len(rr(A)[1])
def ell7(a:int):
    require(a%7!=0,'unit needed');return (((pow(a,6,49)-1)//7)*6)%7

def residue_data(data):
    qs=sorted(map(int,data['normalizations']));out={};B={};ordinary={}
    symbols=0;norm_checks={}
    for q in qs:
        require(all(q%d for d in range(2,math.isqrt(q)+1)),'prime expected')
        F=Quad(q);o=data['normalizations'][str(q)];f=o['degree'];N=q**f-1
        g=F.phi_pair(o['beta_generator']);z=F.power(g,N//7)
        require(all(F.power(g,N//p)!=(1,0) for p in factors(N)),'bad beta primitive')
        tab={F.power(z,i):i for i in range(7)}
        B[q]=(F,N,g,z,tab)
        go=F.phi_pair((o['ordinary_generator_offset'],1));No=q*q-1
        require(F.power(go,No//7)!=(1,0),'ordinary seventh-quotient generator required')
        zo=F.power(go,No//7);to={F.power(zo,i):i for i in range(7)}
        def lo(x):
            nonlocal symbols
            symbols+=1;return to[F.power(x,No//7)]
        fixed=[lo(F.phi()),lo((2,0)),lo((3,0)),lo((0,1)),lo((7,0))]
        cross={str(l):(0 if l==q else lo((l%q,0))) for l in qs}
        scarg=F.power(go,q+1) if f==1 else go
        scale=tab[F.power(scarg,N//7)];require(scale!=0,'zero normalization scale')
        ordinary[q]=(F,go,zo,to)
        out[str(q)]={'q':q,'degree':f,'beta_generator_w':list(g),'beta_zeta_w':list(z),
                     'ordinary_generator_w':list(go),'ordinary_zeta_w':list(zo),
                     'fixed_logs':fixed,'cross_logs':cross,'beta_inertia_scale':scale}
        require(fixed[0]==0 and (6*fixed[2]+fixed[3])%7==0,'frozen natural class not locally zero')
        old=next(v for v in data['old_fixed_and_minus_constraints']['residue_data'] if v['q']==q)
        require(fixed==old['unit_logs'],'changed old ordinary normalization')
    def log(q,x):
        nonlocal symbols
        symbols+=1;F,N,g,z,tab=B[q];require(x!=(0,0),'nonunit');return tab[F.power(x,N//7)]
    full={};details={}
    for sq,cs in sorted(data['conductor_generators'].items(),key=lambda kv:int(kv[0])):
        ell=int(sq);require(cyclo_norm(cs)==ell,'norm mismatch');norm_checks[sq]=ell
        F,N,g,z,tab=B[ell];require(F.ev(cs,z)==(0,0),'generator not at chosen root')
        row=[];det={}
        for q in qs:
            F,N,g,z,tab=B[q]
            if q==ell:
                logs=[log(q,F.ev(cs,F.power(z,b))) for b in range(2,7)]
                a=sum((1-b)*logs[b-2] for b in range(2,7))%7
                det[str(q)]={'other_prime_logs':logs,'self_uniformizer_row':a}
            else:
                reps=range(1,7) if data['normalizations'][str(q)]['degree']==1 else range(1,4)
                logs=[log(q,F.ev(cs,F.power(z,b))) for b in reps]
                a=-sum(b*logs[i] for i,b in enumerate(reps))%7
                det[str(q)]={'orbit_logs':logs,'row':a}
            row.append(a)
        full[sq]=row;details[sq]=det
    # Recheck two pinned unramified rows in the declared normalization.
    earlier={}
    for sl,cs in data['earlier_test_generators'].items():
        require(cyclo_norm(cs)==int(sl),'earlier norm mismatch');row=[]
        for q in qs:
            F,N,g,z,tab=B[q];f=data['normalizations'][str(q)]['degree']
            reps=range(1,7) if f==1 else range(1,4)
            v=-sum(b*log(q,F.ev(cs,F.power(z,b))) for b in reps)%7;row.append(v)
            if f==1:require(v==data['earlier_twisted_rows'][str(q)][sl],'old twisted row changed')
        earlier[sl]=row
    return qs,out,full,details,earlier,norm_checks,symbols

def compute():
    data=json.loads((ROOT/'work80/inputs/finite_inputs.json').read_text())
    qs,rd,brows,bd,earlier,norms,symbols=residue_data(data)
    Q=Quad(49);pa=Q.power(Q.phi(),48);p3=Q.power((3,0),48)
    phi_log=[((pa[0]-1)//7)%7,(pa[1]//7)%7]
    three_log=[((p3[0]-1)//7)%7,(p3[1]//7)%7]
    require(phi_log==[0,5] and three_log==[6,0],'local independence failed')
    pats={};shiftchecks=0;synth=0
    for lab,p in data['patterns'].items():
        S=p['support'];s=dict(zip(S,p['inertia']));m=24
        labels=['2:F','3:F','5:F','7:phi','7:3','7:7']+[f'{q}:{x}' for q in S for x in ['I','F']]
        L=[];units=['phi','2','3','sqrt5','7']+list(map(str,S))
        for i in range(5):
            v=[0]*m;v[{0:3,1:0,2:1,3:2,4:5}[i]]=1
            if i in [1,2,3]:v[4]={1:ell7(2),2:1,3:4}[i]
            for j,q in enumerate(S):v[6+2*j]=rd[str(q)]['fixed_logs'][i]
            L.append(v)
        for i,q in enumerate(S):
            v=[0]*m;v[7+2*i]=1;v[4]=ell7(q)
            for j,r in enumerate(S):v[6+2*j]=rd[str(r)]['cross_logs'][str(q)]
            L.append(v)
        # Image basis of unrestricted-Sigma ordinary H1, indexed by 7:3 and S inertia.
        columns=[]
        for k in range(10):
            vec=[0]*24;vec[4]=int(k==0)
            if k:vec[6+2*(k-1)]=1
            for i in range(5):
                pivot={0:3,1:0,2:1,3:2,4:5}[i]
                vec[pivot]=-sum(a*b for a,b in zip(L[i],vec))%7
            for j in range(9):vec[7+2*j]=-sum(a*b for a,b in zip(L[5+j],vec))%7
            columns.append(vec)
        J=transpose(columns)
        require(rank(L)==14 and rank(J)==10 and not any(sum(r) for r in matmul(L,J)),'localization exactness failed')
        E=[]
        for j in range(6):v=[0]*24;v[j]=1;E.append(v)
        loc=[]
        for i,q in enumerate(S):
            c=rd[str(q)]['beta_inertia_scale']*s[q]%7
            b=0 if q%7==6 else 2*sum(brows[str(q)][j]*s.get(r,0) for j,r in enumerate(qs))%7
            h=((q*q-1)//7)%7
            v=[0]*24;v[6+2*i]=-b%7;v[7+2*i]=c;E.append(v)
            loc.append({'q':q,'c':c,'b':b,'h':h,'toric_rhs':-h*c%7})
            for a,d,t in itertools.product(range(7),repeat=3):
                require((c*(d+t*a)-(b+t*c)*a-c*d+b*a)%7==0,'Frobenius gauge invariance');shiftchecks+=1
        A=matmul(E,J);R,pivs=rr(A);ker=null(A);dual=null(transpose(A))
        expected=2 if lab=='C' else 3
        require(len(ker)==expected and len(dual)==5+expected,'unexpected full rank')
        require(all(matvec(A,v)==[0]*15 for v in ker),'wrong kernel')
        require(all(matvec(transpose(A),v)==[0]*10 for v in dual),'wrong cokernel')
        minus=[q for q in S if q%7==6]
        require(len(ker)==len(minus),'kernel does not match minus support')
        expectedker=[]
        for q in minus:
            v=[0]*10;v[1+S.index(q)]=1;expectedker.append(v)
        require(ker==expectedker,'unexpected remaining characters')
        # Synthetic solvable targets are not evaluations of an arithmetic primitive.
        for k in range(140):
            z=[(k//(7**i))%7 for i in range(10)];t=matvec(A,z)
            require(matvec(dual,t)==[0]*len(dual),'synthetic image rejected');synth+=1
        testbad=[0]*15
        for j in range(15):
            testbad=[int(i==j) for i in range(15)]
            if any(matvec(dual,testbad)):break
        require(any(matvec(dual,testbad)),'no nonimage control')
        pats[lab]={'support':S,'inertia':p['inertia'],'local_labels':labels,'global_unit_labels':units,
                   'localization_relations':L,'localization_image_basis':J,'local_dimension':24,
                   'global_H1_dimension_over_k':10,'global_H2_dimension_over_k':9,
                   'dual_S_unit_dimension':14,'toric_values':loc,'constraint_matrix':E,
                   'global_to_constraint_matrix':A,'rank':len(pivs),'kernel_basis':ker,
                   'dual_obstruction_basis':dual,'homogeneous_dimension_over_k':len(ker),
                   'affine_obstruction_dimension_over_k':len(dual),
                   'remaining_character_support':minus,'common_semilinear_bound_if_nonempty':7**len(ker),
                   'general_bound_if_nonempty':49**len(ker),'synthetic_nonimage_target':testbad,
                   'actual_affine_target_computed':False,'particular_cochain_computed':False}
    # Root lift cross-check will be performed using the separate method.
    return {'version':'8.0.0','status':'PASS_FINITE_ASSERTIONS','local_phi_log_w':phi_log,
            'local_three_log_w':three_log,'phi_three_log_determinant_mod7':5,
            'prime_order':qs,'residue_data':rd,'conductor_generator_norms':norms,
            'beta_uniformizer_rows_over_Q':brows,'beta_row_details':bd,'earlier_rows':earlier,
            'patterns':pats,'checks':{'residue_symbol_evaluations':symbols,
              'frobenius_lift_identity_cases':shiftchecks,'synthetic_affine_image_targets':synth},
            'nonclaims':['No numerical arithmetic p0 or affine target','No full Stage-P nonemptiness with geometric conditions','No pattern eliminated','No new Lean certificate','No independent mathematical reviewer']}

def main():
    d=compute();out=ROOT/'work80/verification/primary80.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(d['status'])
    for l,p in d['patterns'].items():print(l,p['rank'],p['homogeneous_dimension_over_k'],p['affine_obstruction_dimension_over_k'])
if __name__=='__main__':main()
