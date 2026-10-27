#!/usr/bin/env python3
"""Exact finite regressions for v0.10.0. No finite test proves a limiting theorem."""
from __future__ import annotations
import argparse, hashlib, itertools, json, platform, time
from math import isqrt
from pathlib import Path

Mat = tuple[int, ...]

def eye(d: int) -> Mat:
    return tuple(int(i == j) for i in range(d) for j in range(d))

def add(a: Mat, b: Mat, q: int) -> Mat:
    return tuple((x+y) % q for x,y in zip(a,b))

def sub(a: Mat, b: Mat, q: int) -> Mat:
    return tuple((x-y) % q for x,y in zip(a,b))

def scale(a: Mat, t: int, q: int) -> Mat:
    return tuple((x*t) % q for x in a)

def mul(a: Mat, b: Mat, q: int) -> Mat:
    d = isqrt(len(a))
    if d == 2:
        x,y,z,w=a; r,s,t,u=b
        return ((x*r+y*t)%q,(x*s+y*u)%q,(z*r+w*t)%q,(z*s+w*u)%q)
    return tuple(sum(a[i*d+k]*b[k*d+j] for k in range(d))%q for i in range(d) for j in range(d))

def inv(a: Mat, q: int) -> Mat:
    if len(a)==1: return (pow(a[0],-1,q),)
    if len(a)!=4: raise ValueError('This regression implementation uses ranks one and two.')
    x,y,z,w=a; t=pow((x*w-y*z)%q,-1,q)
    return (w*t%q,-y*t%q,-z*t%q,x*t%q)

def power(a: Mat, n: int, q: int) -> Mat:
    out=eye(isqrt(len(a)))
    while n:
        if n&1: out=mul(out,a,q)
        a=mul(a,a,q); n//=2
    return out

def valuation(x: int, p: int, cap: int) -> int:
    if x==0: return cap
    r=0
    while x%p==0 and r<cap: x//=p; r+=1
    return r

def depth(a: Mat, p: int, cap: int) -> int:
    return min(valuation(x,p,cap) for x in a)

def cyclic(n: int):
    return [[(i+j)%n for j in range(n)] for i in range(n)]

def group_fixture(name: str):
    if name.startswith('C'):
        n=int(name[1:]); table=cyclic(n)
        generators={2:(1,0,0,-1),3:(0,-1,1,-1),4:(0,-1,1,0)}
        gen=generators[n]
        # Exact integer powers, no modulus.
        def prod(a,b):
            x,y,z,w=a; r,s,t,u=b
            return (x*r+y*t,x*s+y*u,z*r+w*t,z*s+w*u)
        acts=[eye(2)]
        for _ in range(1,n): acts.append(prod(acts[-1],gen))
        return table,acts
    if name=='V4':
        return [[i^j for j in range(4)] for i in range(4)],[(1 if not i&1 else -1,0,0,1 if not i&2 else -1) for i in range(4)]
    if name=='S3':
        perms=list(itertools.permutations(range(3))); ix={g:i for i,g in enumerate(perms)}
        table=[[ix[tuple(g[h[k]] for k in range(3))] for h in perms] for g in perms]
        acts=[]
        for g in perms:
            # A2 lattice with basis e0-e2, e1-e2.
            acts.append(tuple(int(g[j]==i)-int(g[2]==i) for i in range(2) for j in range(2)))
        return table,acts
    raise ValueError(name)

def defects(table, A, q):
    d=isqrt(len(A[0])); I=eye(d); inverses=[inv(a,q) for a in A]
    return [[sub(mul(mul(A[g],A[h],q),inverses[table[g][h]],q),I,q) for h in range(len(A))] for g in range(len(A))]

def delta(table, action, b, p):
    N=len(table); out=[]
    for g in range(N):
        row=[]
        for h in range(N):
            gb=mul(mul(action[g],b[h],p),inv(action[g],p),p)
            row.append(sub(add(b[g],gb,p),b[table[g][h]],p))
        out.append(row)
    return out

def flatten(c):
    return [x for row in c[1:] for a in row[1:] for x in a]

def linear_solve(A, rhs, p):
    """RREF with a left-nullspace certificate in the inconsistent case."""
    m=len(A); n=len(A[0]) if m else 0
    B=[[x%p for x in row]+[rhs[i]%p] for i,row in enumerate(A)]
    U=[[int(i==j) for j in range(m)] for i in range(m)]
    piv=[]; r=0
    for j in range(n):
        z=next((i for i in range(r,m) if B[i][j]),None)
        if z is None: continue
        B[r],B[z]=B[z],B[r]; U[r],U[z]=U[z],U[r]
        v=pow(B[r][j],-1,p); B[r]=[x*v%p for x in B[r]]; U[r]=[x*v%p for x in U[r]]
        for i in range(m):
            if i==r or B[i][j]==0: continue
            v=B[i][j]; B[i]=[(x-v*y)%p for x,y in zip(B[i],B[r])]; U[i]=[(x-v*y)%p for x,y in zip(U[i],U[r])]
        piv.append(j); r+=1
    for i in range(r,m):
        if B[i][-1]:
            lam=U[i]
            assert all(sum(lam[t]*A[t][j] for t in range(m))%p==0 for j in range(n))
            assert sum(lam[t]*rhs[t] for t in range(m))%p!=0
            return None, n-r, lam
    x=[0]*n
    for i,j in enumerate(piv): x[j]=B[i][-1]
    assert all((sum(u*v for u,v in zip(row,x))-b)%p==0 for row,b in zip(A,rhs))
    return x,n-r,None

def cochain(A, vec, p):
    d2=len(A[0]); return [(0,)*d2]+[tuple(vec[i*d2:(i+1)*d2]) for i in range(len(A)-1)]

def test_obstructions():
    fixtures=[]
    for name,p,n in [('C2',2,1),('C2',3,1),('C3',3,1),('C3',3,2),('V4',2,1),('S3',2,1),('S3',3,1)]:
        t,a=group_fixture(name); fixtures.append((name,p,n,t,[tuple(x%(p**n) for x in z) for z in a]))
    fixtures.append(('C3-bad',3,2,cyclic(3),[power((1,3,3,1),i,9) for i in range(3)]))
    triples=0; changes=0; rows=[]
    for name,p,n,t,A in fixtures:
        q=p**(n+1); pn=p**n; N=len(t); I=eye(2)
        raw=defects(t,A,q)
        assert all(all(x%pn==0 for x in a) for row in raw for a in row)
        c=[[tuple(x//pn%p for x in a) for a in row] for row in raw]
        action=[tuple(x%p for x in a) for a in A]
        for g,h,k in itertools.product(range(N),repeat=3):
            gc=mul(mul(action[g],c[h][k],p),inv(action[g],p),p)
            z=sub(add(sub(gc,c[t[g][h]][k],p),c[g][t[h][k]],p),c[g][h],p)
            assert z==(0,)*4; triples+=1
        dim=4*(N-1); cols=[]
        for j in range(dim):
            v=[0]*dim; v[j]=1; cols.append(flatten(delta(t,action,cochain(A,v,p),p)))
        mat=[list(z) for z in zip(*cols)]; rhs=[-x%p for x in flatten(c)]
        sol,nullity,lam=linear_solve(mat,rhs,p)
        if sol is not None:
            b=cochain(A,sol,p); new=[mul(add(I,scale(bg,pn,q),q),a,q) for bg,a in zip(b,A)]
            assert all(a==(0,)*4 for row in defects(t,new,q) for a in row)
        for seed in range(7):
            b=cochain(A,[(seed*(j+1)+j*j)%p for j in range(dim)],p)
            new=[mul(add(I,scale(bg,pn,q),q),a,q) for bg,a in zip(b,A)]
            cc=[[tuple(x//pn%p for x in a) for a in row] for row in defects(t,new,q)]
            db=delta(t,action,b,p)
            assert all(cc[g][h]==add(c[g][h],db[g][h],p) for g in range(N) for h in range(N)); changes+=1
        rows.append({'name':name,'p':p,'n':n,'variables':dim,'lift_exists':sol is not None,'nullity':nullity,'negative_certificate':lam})
    assert rows[-1]['lift_exists'] is False
    return {'fixtures':rows,'cocycle_triples':triples,'change_of_section_cases':changes}

def test_cyclic():
    counts=[]
    for p,n,order in [(2,1,2),(2,2,2),(2,1,4),(3,1,3),(3,2,3),(5,1,5)]:
        pn=p**n; q=pn*p; I=eye(2); acts=0; candidates=0; no_lift=0
        Bs=list(itertools.product(range(p),repeat=4))
        for A in itertools.product(range(pn),repeat=4):
            if (A[0]*A[3]-A[1]*A[2])%p==0 or power(A,order,pn)!=I: continue
            acts+=1; Ap=[power(A,i,p) for i in range(order)]
            r=sub(power(A,order,q),I,q); c=tuple(x//pn%p for x in r); accepted=0
            for B in Bs:
                L=(0,)*4
                for i in range(order): L=add(L,mul(mul(Ap[i],B,p),Ap[order-1-i],p),p)
                target=add(c,L,p); lift=add(A,scale(B,pn,q),q)
                actual=sub(power(lift,order,q),I,q)
                assert tuple(x//pn%p for x in actual)==target
                accepted+=int(actual==(0,)*4); candidates+=1
            no_lift+=int(accepted==0)
        counts.append({'p':p,'n':n,'order':order,'all_valid_rank_two_actions':acts,'all_next_matrix_lifts':candidates,'nonliftable_actions':no_lift})
    return counts

def average_correction(table,A,p,Q):
    """Input exact residues at Q digits. Division loses e digits, explicitly."""
    N=len(table); e=valuation(N,p,100); q=p**Q; outQ=Q-e; oq=p**outQ; I=eye(2)
    E=defects(table,A,q); b=[]
    for g in range(N):
        s=tuple(sum(E[g][h][j] for h in range(N))%q for j in range(4))
        assert all(x%(p**e)==0 for x in s)
        b.append(tuple((x//(p**e))*pow(N//(p**e),-1,oq)%oq for x in s))
    new=[mul(sub(I,x,oq),a,oq) for x,a in zip(b,A)]
    return new,b,outQ

def test_newton():
    rows=[]; I=eye(2); identities=0; steps=0
    family=[('C2',2),('C2',3),('C3',2),('C3',3),('C3',5),('C4',2),('V4',2),('V4',3),('S3',2),('S3',3),('S3',5)]
    for name,p in family:
        t,rho=group_fixture(name); N=len(t); e=valuation(N,p,100)
        for offset in (0,1):
            m=2*e+1+offset; predicted=[2*e+(2**j)*(m-2*e) for j in range(4)]
            Q=predicted[-1]+4*e+3; mod=p**Q
            for seed in range(5):
                # Canonical integral representatives of conjugated finite-level action.
                pn=p**m; gauge=(1,p*seed,seed,1+p*seed*seed)
                assert (gauge[0]*gauge[3]-gauge[1]*gauge[2])==1
                rr=[mul(mul(gauge,tuple(x%pn for x in a),pn),inv(gauge,pn),pn) for a in rho]
                A=[]
                for g,a in enumerate(rr):
                    B=tuple((seed+g*(j+1)+j*j)%p for j in range(4))
                    A.append(I if g==0 else add(a,scale(B,pn,mod),mod))
                initial=A[:]; precision=Q; actuals=[]
                for j in range(3):
                    q=p**precision; E=defects(t,A,q)
                    assert min(depth(x,p,precision) for row in E for x in row)>=predicted[j]
                    for g,h,k in itertools.product(range(N),repeat=3):
                        left=mul(add(I,E[g][h],q),add(I,E[t[g][h]][k],q),q)
                        alpha=mul(mul(A[g],E[h][k],q),inv(A[g],q),q)
                        right=mul(add(I,alpha,q),add(I,E[g][t[h][k]],q),q)
                        assert left==right; identities+=1
                    new,b,newQ=average_correction(t,A,p,precision)
                    assert min(depth(x,p,newQ) for x in b)>=predicted[j]-e
                    ne=defects(t,new,p**newQ); got=min(depth(x,p,newQ) for row in ne for x in row)
                    assert got>=predicted[j+1]
                    assert all(depth(sub(x,y,p**newQ),p,newQ)>=m-e for x,y in zip(new,initial))
                    A=new; precision=newQ; actuals.append(got); steps+=1
                rows.append({'group':name,'p':p,'e':e,'m':m,'fixture':seed,'certified_depths':predicted,'observed_capped_depths':actuals,'remaining_precision':precision})
    return {'runs':rows,'correction_steps':steps,'associativity_identities':identities}

def test_horizons():
    cases=[]
    for p in (2,3,5):
        for order in (2,3,4,6):
            e=valuation(order,p,100)
            for n in range(1,4):
                h=max(n+e,2*e+1); pn=p**n
                roots=[u for u in range(pn) if u%p and pow(u,order,pn)==1]
                images=[]
                for r in (h,h+1,h+2):
                    images.append({u%pn for u in range(p**r) if u%p and pow(u,order,p**r)==1})
                assert images[0]==images[1]==images[2]
                cases.append({'p':p,'order':order,'n':n,'h':h,'finite_level_roots':roots,'horizon_image':sorted(images[0])})
    return cases

def test_exploratory_witness():
    a=3; values=[]; depths=[]
    for _ in range(3):
        values.append(a); depths.append(valuation(a*a-1,2,100))
        assert a%4==3
        a=((3-a*a)//2)*a
    assert values==[3,-9,351] and depths==[3,4,6]
    assert all((b*b)%16==9 for b in (3,11))
    assert (-1)%4==3 and (-1)%8!=3
    return {'successive_generators':values,'defect_depths':depths,
            'witness_modulus':8,'preserved_modulus':4,
            'both_next_lifts_fail':True,'integral_solution':-1}

def test_conjugacy():
    count=0
    for name,p in [('C2',2),('C3',3),('C4',2),('V4',2),('S3',2),('S3',3),('S3',5)]:
        t,rho=group_fixture(name); N=len(t); e=valuation(N,p,100)
        for s in (e+1,e+2):
            L=2*s+e+5; q=p**L; oq=p**(L-e); I=eye(2)
            r=[tuple(x%q for x in a) for a in rho]
            for seed in range(7):
                B=(seed,1,seed+1,2*seed); Q=add(I,scale(B,p**s,q),q)
                sig=[mul(mul(Q,a,q),inv(Q,q),q) for a in r]
                E=[sub(mul(a,inv(b,q),q),I,q) for a,b in zip(sig,r)]
                total=tuple(sum(a[j] for a in E)%q for j in range(4))
                T=add(I,tuple((x//(p**e))*pow(N//(p**e),-1,oq)%oq for x in total),oq)
                assert depth(sub(T,I,oq),p,L-e)>=s-e
                assert all(mul(a,T,oq)==mul(T,b,oq) for a,b in zip(sig,r)); count+=1
    return count

def test_blind_and_profinite():
    count=0
    for p in (3,5,7):
        q=p**3; I=eye(2); J=(0,1,1,0); A=add(I,scale(J,p,q),q)
        assert sub(power(A,p,q),I,q)==scale(J,p*p,q)
        # Central sign: plus idempotent is zero on M, and adjoint sign is identity.
        sign=scale(I,-1,q)
        assert scale(add(I,sign,q),pow(2,-1,q),q)==(0,)*4
        for B in itertools.product(range(p),repeat=4):
            lift=add(A,scale(B,p*p,q),q)
            assert sub(power(lift,p,q),I,q)==scale(J,p*p,q)
            assert mul(mul(sign,B,q),inv(sign,q),q)==B
            count+=1
        # Exact integer-power checks for the continuity-based p-adic extension.
        for x,y in itertools.product(range(2*p),repeat=2):
            assert power(A,x+y,q)==mul(power(A,x,q),power(A,y,q),q)
            assert tuple(z%(p*p) for z in power(A,x,q))==add(I,scale(J,p*x,p*p),p*p)
    return {'all_next_lifts_of_bad_rank_two_actions':count,'profinite_scope':'Finite integer powers only; uniform convergence and extension to Z_p have a separate proof.'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    start=time.monotonic()
    results={'obstructions':test_obstructions(),'cyclic':test_cyclic(),'newton':test_newton(),'rank_one_horizons':test_horizons(),'exploratory_witness':test_exploratory_witness(),'conjugacy_cases':test_conjugacy(),'blind_and_profinite':test_blind_and_profinite()}
    out={'status':'PASS','schema':'komorebi-action-lifting-regression-v1','python':platform.python_version(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.monotonic()-start,'arithmetic':'exact integer arithmetic and modular arithmetic, no floats in mathematical checks','sampling':'deterministic fixture families; cyclic and listed next-lift families exhaustive within their declared bounds','nonclaims':['No infinite or p-adic convergence claim follows from finite tests.','No independent proof review or Lean certification.','No exhaustive enumeration of all finite groups, ranks, or actions.'],'results':results}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'PASS','seconds':out['seconds'],'cyclic_actions':sum(x['all_valid_rank_two_actions'] for x in results['cyclic']),'cyclic_lifts':sum(x['all_next_matrix_lifts'] for x in results['cyclic']),'newton_runs':len(results['newton']['runs']),'newton_steps':results['newton']['correction_steps'],'cocycle_triples':results['obstructions']['cocycle_triples'],'conjugacy_cases':results['conjugacy_cases']},indent=2))

if __name__=='__main__': main()
