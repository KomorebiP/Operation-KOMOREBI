#!/usr/bin/env python3
"""Separate Block80 checker: phi fields, cyclotomic norm products,
Hensel-computed local uniformizer units, and certified linear algebra.
Imports no primary or predecessor arithmetic. It does not compute p0.
"""
import itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def check(x,msg):
    if not x:raise ArithmeticError(msg)
class Phi:
    def __init__(self,q):self.q=q
    def sum(self,u,v):return ((u[0]+v[0])%self.q,(u[1]+v[1])%self.q)
    def product(self,u,v):
        a,b=u;c,d=v
        return ((a*c+b*d)%self.q,(a*d+b*c+b*d)%self.q)
    def exp(self,u,n):
        z=(1,0)
        for bit in bin(n)[2:]:
            z=self.product(z,z)
            if bit=='1':z=self.product(z,u)
        return z
    def poly(self,p,u):
        total=(0,0);power=(1,0)
        for c in p:
            total=self.sum(total,(c*power[0]%self.q,c*power[1]%self.q));power=self.product(power,u)
        return total
    def omega(self,u):
        h=pow(2,-1,self.q)
        return [(u[0]+h*u[1])%self.q,h*u[1]%self.q]
    def fieldnorm(self,u):a,b=u;return (a*a+a*b-b*b)%self.q

def divs(n):
    s=set();d=2
    while d*d<=n:
        while n%d==0:s.add(d);n//=d
        d+=1
    if n>1:s.add(n)
    return sorted(s)

def cyclic_product(u,v):
    z=[0]*7
    for i,x in enumerate(u):
        for j,y in enumerate(v):z[(i+j)%7]+=x*y
    return z

def norm_product(cs):
    prod=[1]+[0]*6
    for b in range(1,7):
        conjugate=[0]*7
        for j,c in enumerate(cs):conjugate[b*j%7]+=c
        prod=cyclic_product(prod,conjugate)
    reduced=[prod[i]-prod[6] for i in range(6)]
    check(reduced[1:]==[0]*5,'non-scalar norm product')
    return reduced[0]

def elim(M):
    a=[[t%7 for t in row] for row in M];rows=len(a);cols=len(a[0]);p=[]
    for j in range(cols):
        nr=len(p)
        if nr>=rows:break
        for k in range(nr,rows):
            if a[k][j]:break
        else:continue
        a[nr],a[k]=a[k],a[nr]
        v=a[nr][j]
        # Finite-field inverse by exhaustive search, not extended Euclid.
        u=next(u for u in range(1,7) if u*v%7==1)
        a[nr]=[(u*t)%7 for t in a[nr]]
        for k in range(rows):
            if k!=nr:
                v=a[k][j]
                a[k]=[(a[k][h]-v*a[nr][h])%7 for h in range(cols)]
        p.append(j)
    return a,p

def tr(M):return [list(r) for r in zip(*M)]
def rk(M):return len(elim(M)[1])
def mv(M,x):return [sum(a*b for a,b in zip(row,x))%7 for row in M]
def mm(M,N):return [mv(tr(N),row) for row in M]
def kernel(M):
    a,p=elim(M);out=[]
    for j in range(len(M[0])):
        if j not in p:
            v=[0]*len(M[0]);v[j]=1
            for i,col in enumerate(p):v[col]=-a[i][j]%7
            out.append(v)
    return out

def determinant_mod7(M):
    # Subset expansion: no determinant elimination shares the rank code.
    n=len(M);d={0:1}
    for i,row in enumerate(M):
        nxt={}
        for mask,v in d.items():
            for j,a in enumerate(row):
                if mask>>j&1:continue
                inversions=(mask>>(j+1)).bit_count()
                value=(-1 if inversions%2 else 1)*v*a
                nxt[mask|1<<j]=(nxt.get(mask|1<<j,0)+value)%7
        d=nxt
    return d.get((1<<n)-1,1)

def rank_certificate(M):
    _,pc=elim(M);r=len(pc)
    # independent pivot row selection on the transpose of selected columns
    sub=[[row[j] for j in pc] for row in M]
    _,pr=elim(tr(sub))
    minor=[[M[i][j] for j in pc] for i in pr]
    check(len(pr)==r and determinant_mod7(minor)!=0,'rank minor failed')
    N=kernel(M)
    check(len(N)==len(M[0])-r and rk(N)==len(N) if N else r==len(M[0]),'nullity failed')
    check(all(mv(M,x)==[0]*len(M) for x in N),'nullspace failed')
    return r

def local7(a):
    # Direct powers in O/49 determine the two unit coordinates.
    F=Phi(49);g=F.exp(a,48);v=[((g[0]-1)//7)%7,(g[1]//7)%7]
    phi=F.exp((0,1),48);three=F.exp((3,0),48)
    x=[((phi[0]-1)//7)%7,(phi[1]//7)%7];y=[((three[0]-1)//7)%7,(three[1]//7)%7]
    hits=[(r,s) for r in range(7) for s in range(7) if all((r*x[i]+s*y[i])%7==v[i] for i in range(2))]
    check(len(hits)==1,'local7 coordinate ambiguity')
    return hits[0]

def polyint(cs,a,m):
    return sum(c*pow(a,i,m) for i,c in enumerate(cs))%m

def main_data():
    inp=json.loads((ROOT/'work80/inputs/finite_inputs.json').read_text());qs=sorted(map(int,inp['normalizations']))
    contexts={};rd={};calls=0
    for q in qs:
        o=inp['normalizations'][str(q)];F=Phi(q);degree=o['degree'];N=q**degree-1
        g=tuple(o['beta_generator']);root=F.exp(g,N//7)
        check(all(F.exp(g,N//d)!=(1,0) for d in divs(N)),'beta generator order')
        powers=[F.exp(root,i) for i in range(7)];check(len(set(powers))==7,'root order')
        og=(o['ordinary_generator_offset'],1);on=q*q-1;orr=F.exp(og,on//7)
        opowers=[F.exp(orr,i) for i in range(7)];check(len(set(opowers))==7,'ordinary quotient generator')
        def olog(x):
            nonlocal calls
            calls+=1;return opowers.index(F.exp(x,on//7))
        vals=[(0,1),(2,0),(3,0),(q-1,2),(7,0)]
        fixed=[olog(x) for x in vals]
        cross={str(l):(0 if l==q else olog((l%q,0))) for l in qs}
        scale_arg=(F.fieldnorm(og),0) if degree==1 else og
        scale=powers.index(F.exp(scale_arg,N//7));check(scale!=0,'inertia scale')
        rd[str(q)]={'q':q,'degree':degree,'beta_generator_w':F.omega(g),'beta_zeta_w':F.omega(root),
                    'ordinary_generator_w':F.omega(og),'ordinary_zeta_w':F.omega(orr),
                    'fixed_logs':fixed,'cross_logs':cross,'beta_inertia_scale':scale}
        check(fixed[0]==0 and (6*fixed[2]+fixed[3])%7==0,'frozen natural local value')
        old=next(e for e in inp['old_fixed_and_minus_constraints']['residue_data'] if e['q']==q)
        check(old['unit_logs']==fixed,'old fixed rows')
        contexts[q]=(F,N,g,root,powers)
    def symbol(q,x):
        nonlocal calls
        calls+=1;F,N,g,root,powers=contexts[q]
        check(x!=(0,0),'unit required');return powers.index(F.exp(x,N//7))
    rows={};details={};norms={};unitcheck=[]
    for sq,cs in sorted(inp['conductor_generators'].items(),key=lambda kv:int(kv[0])):
        ell=int(sq);check(norm_product(cs)==ell,'norm does not equal q');norms[sq]=ell
        F,N,g,z,powers=contexts[ell];check(F.poly(cs,z)==(0,0),'wrong chosen prime')
        row=[];detail={}
        for q in qs:
            F,N,g,z,powers=contexts[q]
            if q==ell:
                logs=[symbol(q,F.poly(cs,F.exp(z,b))) for b in range(2,7)]
                # Determine pi(q)/q as a unit at the chosen local embedding using
                # a genuine root of Phi_7 modulo q^2, rather than its norm relation.
                r=z[0];check(z[1]==0,'split residue expected')
                phi=[1]*7;m=q*q
                val=polyint(phi,r,m);check(val%q==0,'root not mod q')
                deriv=sum(i*pow(r,i-1,q) for i in range(1,7))%q
                lift=r+q*(-(val//q)*pow(deriv,-1,q)%q)
                check(polyint(phi,lift,m)==0,'root Hensel lift failed')
                pi=polyint(cs,lift,m);check(pi%q==0 and pi!=0,'norm-q valuation failed')
                u=pi//q;ul=powers.index(F.exp((u,0),N//7))
                check((ul+sum(logs))%7==0,'self-unit norm relation')
                a=(-ul-sum(b*logs[b-2] for b in range(2,7)))%7
                detail[str(q)]={'other_prime_logs':logs,'self_uniformizer_row':a}
                unitcheck.append({'prime':q,'cyclotomic_root_mod_q2':lift,'local_unit':u,'local_unit_log':ul})
            else:
                f=inp['normalizations'][str(q)]['degree'];reps=range(1,7) if f==1 else range(1,4)
                logs=[symbol(q,F.poly(cs,F.exp(z,b))) for b in reps]
                # Weighted residue product checked independently of sum formula.
                prod=(1,0)
                for b in reps:prod=F.product(prod,F.exp(F.poly(cs,F.exp(z,b)),b))
                a=-powers.index(F.exp(prod,N//7))%7
                check(a==-sum(b*logs[i] for i,b in enumerate(reps))%7,'weighted product mismatch')
                detail[str(q)]={'orbit_logs':logs,'row':a}
            row.append(a)
        rows[sq]=row;details[sq]=detail
    earlier={}
    for sl,cs in inp['earlier_test_generators'].items():
        check(norm_product(cs)==int(sl),'older norm');row=[]
        for q in qs:
            F,N,g,z,powers=contexts[q];f=inp['normalizations'][str(q)]['degree'];reps=range(1,7) if f==1 else range(1,4)
            val=-sum(b*symbol(q,F.poly(cs,F.exp(z,b))) for b in reps)%7;row.append(val)
            if f==1:check(val==inp['earlier_twisted_rows'][str(q)][sl],'old twisted row changed')
        earlier[sl]=row
    pats={};shifts=0;synthetic=0;minorchecks=0
    for name,pat in inp['patterns'].items():
        S=pat['support'];s=dict(zip(S,pat['inertia']));labels=['2:F','3:F','5:F','7:phi','7:3','7:7']+[f'{q}:{x}' for q in S for x in ['I','F']]
        names=['phi','2','3','sqrt5','7']+list(map(str,S));L=[]
        for tag in names:
            row=[0]*24
            if tag=='phi':row[3]=1;i=0
            elif tag=='2':row[0]=1;row[3],row[4]=local7((2,0));i=1
            elif tag=='3':row[1]=1;row[3],row[4]=local7((3,0));i=2
            elif tag=='sqrt5':row[2]=1;row[3],row[4]=local7((-1,2));i=3
            elif tag=='7':row[5]=1;i=4
            else:
                q=int(tag);row[7+2*S.index(q)]=1;row[3],row[4]=local7((q%49,0));i=None
            for j,q in enumerate(S):
                row[6+2*j]=rd[str(q)]['fixed_logs'][i] if i is not None else rd[str(q)]['cross_logs'][tag]
            L.append(row)
        # Build the local image from prescribed unit characters, using principal ideles.
        J=[[0]*10 for _ in range(24)];J[4][0]=1
        for i,q in enumerate(S):J[6+2*i][1+i]=1
        pivotcols=[3,0,1,2,5]+[7+2*i for i in range(9)]
        for row,piv in zip(L,pivotcols):
            for j in range(10):J[piv][j]=-sum(row[k]*J[k][j] for k in range(24) if k!=piv)%7
        check(mm(L,J)==[[0]*10 for _ in range(14)],'annihilator failure')
        check(rank_certificate(L)==14 and rank_certificate(J)==10,'wrong localization ranks');minorchecks+=2
        E=[[int(i==j) for j in range(24)] for i in range(6)];local=[]
        for i,q in enumerate(S):
            c=rd[str(q)]['beta_inertia_scale']*s[q]%7
            b=0 if q%7==6 else 2*sum(rows[str(q)][j]*s.get(r,0) for j,r in enumerate(qs))%7
            h=((q*q-1)//7)%7
            e=[0]*24;e[7+2*i]=c;e[6+2*i]=-b%7;E.append(e)
            local.append({'q':q,'b':b,'c':c,'h':h,'toric_rhs':-h*c%7})
            for x,y,t in itertools.product(range(7),repeat=3):
                old=(c*y-b*x)%7;new=(c*(y+t*x)-(b+t*c)*x)%7
                check(old==new,'lift dependence');shifts+=1
        A=mm(E,J);r=rank_certificate(A);minorchecks+=1;ker=kernel(A);dual=kernel(tr(A))
        check(rank_certificate(tr(A))==r,'dual rank');minorchecks+=1
        minus=[q for q in S if q%7==6]
        expected=[]
        for q in minus:v=[0]*10;v[1+S.index(q)]=1;expected.append(v)
        check(ker==expected,'not exactly inert-minus characters')
        for k in range(140):
            z=[k//7**i%7 for i in range(10)];t=mv(A,z)
            check(mv(dual,t)==[0]*len(dual),'synthetic image error');synthetic+=1
        bad=next([int(i==j) for i in range(15)] for j in range(15) if any(mv(dual,[int(i==j) for i in range(15)])))
        pats[name]={'support':S,'inertia':pat['inertia'],'local_labels':labels,'global_unit_labels':names,
          'localization_relations':L,'localization_image_basis':J,'local_dimension':24,
          'global_H1_dimension_over_k':10,'global_H2_dimension_over_k':9,
          'dual_S_unit_dimension':14,'toric_values':local,'constraint_matrix':E,
          'global_to_constraint_matrix':A,'rank':r,'kernel_basis':ker,'dual_obstruction_basis':dual,
          'homogeneous_dimension_over_k':len(ker),'affine_obstruction_dimension_over_k':len(dual),
          'remaining_character_support':minus,'common_semilinear_bound_if_nonempty':7**len(ker),
          'general_bound_if_nonempty':49**len(ker),'synthetic_nonimage_target':bad,
          'actual_affine_target_computed':False,'particular_cochain_computed':False}
    F=Phi(49);p=F.exp((0,1),48);v=[((p[0]-1)//7)%7,p[1]//7%7]
    phi_log=Phi(7).omega(v);p=F.exp((3,0),48);v=[((p[0]-1)//7)%7,p[1]//7%7];three=Phi(7).omega(v)
    result={'version':'8.0.0','status':'PASS_FINITE_ASSERTIONS','local_phi_log_w':phi_log,
      'local_three_log_w':three,'phi_three_log_determinant_mod7':5,'prime_order':qs,
      'residue_data':rd,'conductor_generator_norms':norms,'beta_uniformizer_rows_over_Q':rows,
      'beta_row_details':details,'earlier_rows':earlier,'patterns':pats,
      'checks':{'residue_symbol_evaluations':calls,'frobenius_lift_identity_cases':shifts,'synthetic_affine_image_targets':synthetic},
      'nonclaims':['No numerical arithmetic p0 or affine target','No full Stage-P nonemptiness with geometric conditions','No pattern eliminated','No new Lean certificate','No independent mathematical reviewer']}
    extras={'status':'PASS_EXTRA_CHECKS','self_uniformizer_units':unitcheck,
            'nonzero_integer_minor_checks':minorchecks,'no_primary_arithmetic_imported':True}
    return result,extras

def main():
    result,extras=main_data();folder=ROOT/'work80/verification';folder.mkdir(parents=True,exist_ok=True)
    (folder/'independent80.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (folder/'independent80_extra.json').write_text(json.dumps(extras,indent=2,sort_keys=True)+'\n')
    print(result['status'])
    for name,p in result['patterns'].items():print(name,p['rank'],p['homogeneous_dimension_over_k'],p['affine_obstruction_dimension_over_k'])
if __name__=='__main__':main()
