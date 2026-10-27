"""Domain-linked exact arithmetic extensions to the initial repair audit."""
from fractions import Fraction
from math import comb, factorial
from itertools import product as cartprod, combinations
import random
from repair_core import (Field, rank_of_columns, solve_columns,
                         min_menu_repair, product, inverse, scalar, eye)


def v_p_fraction(a, p):
    if not a:
        return None
    a=Fraction(a)
    def val(z):
        z=abs(z);v=0
        while z%p==0:
            z//=p;v+=1
        return v
    return val(a.numerator)-val(a.denominator)


def tangent_numbers(maxdegree):
    T={1:1}
    for d in range(2,maxdegree,2):
        T[d+1]=sum(comb(d,r)*T[r]*T[d-r] for r in range(1,d,2))
    return T


def euler_numbers(maxdegree):
    E={0:1}
    for n in range(1,maxdegree+1):
        E[n] = 0 if n%2 else -sum(comb(n,j)*E[n-j] for j in range(2,n+1,2))
    return E


def trace_cyclotomic(p, eta, max_j):
    """Compute trace of binomial(eta*ξ,j) via Z[X]/(X^p−1) exactly."""
    P=[0]*p;P[0]=1;fact=1
    coeff=[]
    for j in range(max_j+1):
        if j:
            P=[eta*P[(k-1)%p] - (j-1)*P[k] for k in range(p)]
            fact*=j
        coeff.append(Fraction(P[0],fact))
    return coeff


def independent_menu_brute(n, D, R, candidates, costs, p):
    """No rref or solve calls: enumerate every menu and every coefficient tuple."""
    best=None
    for k in range(len(candidates)+1):
        for subset in combinations(range(len(candidates)),k):
            cols=D+[candidates[i] for i in subset]
            feasible=True
            for r in R:
                rhs=[-x%p for x in r]
                found=False
                for coeff in cartprod(range(p),repeat=len(cols)):
                    if all(sum(coeff[j]*cols[j][v] for j in range(len(cols)))%p==rhs[v]
                           for v in range(n)):
                        found=True;break
                if not found:
                    feasible=False;break
            if feasible:
                key=(sum(costs[i] for i in subset),k,subset)
                if best is None or key<best:
                    best=key
    return best


def random_invertible_2x2(rng,F):
    p=F.p
    while True:
        A=[[rng.randrange(p),rng.randrange(p)],
           [rng.randrange(p),rng.randrange(p)]]
        if inverse(A,F) is not None:
            return A


def run_extra(log, check, ch, expected_failure, SUMMARY, record):
    ch("TEST J — actual classical Euler numbers and signed tangent inversion")
    E=euler_numbers(18)
    T=tangent_numbers(19)
    log("Signed Euler numbers (even): "+str({n:E[n] for n in range(0,19,2)}))
    log("Positive tangent numbers: "+str(T))
    check([E[n] for n in [0,2,4,6,8]]==[1,-1,5,-61,1385],
          "Classical Euler reference values reconstructed independently from cosh·sech=1")
    check([T[n] for n in [1,3,5,7,9]]==[1,2,16,272,7936],
          "Tangent numbers reconstructed independently from tan'=1+tan²")
    count=0
    for N in [3,5,7,9,11]:
        for n in range(0,19,2):
            def S(k): return sum((-1)**j*(2*j+1)**k for j in range(N))
            terms=[(-1)**m*T[2*m+1]*comb(n,2*m)*(N**(2*m))*S(n-2*m)
                   for m in range(n//2+1)]
            if sum(terms)!=E[n]:
                raise AssertionError((N,n,E[n],terms,sum(terms)))
            record("euler_inverse", N=N, n=n, exact_euler=E[n], terms=terms, result=sum(terms))
            count+=1
        log(f"  odd N={N}: 10/10 signed tangent inverse identities PASS")
    N=7;n=8
    terms=[(-1)**m*T[2*m+1]*comb(n,2*m)*N**(2*m)*sum((-1)**j*(2*j+1)**(n-2*m) for j in range(N))
           for m in range(n//2+1)]
    log(f"  detailed N=7, n=8: terms={terms}")
    log(f"  exact cancellation sum={sum(terms)} versus Euler E_8={E[n]}")
    for M in range(0,4):
        tail=sum(terms[M+1:])
        check(tail % N**(2*M+2)==0,
              f"Euler actual p=7,n=8 truncation M={M}: tail divisible by p^{2*M+2}")
    # A deliberately false p^3 claim from keeping only m=0 at n=2.
    N=7;n=2
    S2=sum((-1)**j*(2*j+1)**2 for j in range(N))
    delta=E[n]-S2
    log(f"  negative control: n=2,p=7, E2={E[n]}, S2(7)={S2}, tail={delta}, v_7={v_p_fraction(delta,7)}")
    expected_failure(v_p_fraction(delta,7)==2 and delta % 7**3 != 0,
                     "Claiming p^3 congruence after omitting a term of weight p^2 is invalid")
    SUMMARY['euler_exact_inversions']=count

    ch("TEST K — exact cyclotomic trace bound, including singular coefficients")
    checked=0;zeros=0;slacks=[]
    for p in [3,5,7,11]:
        for eta in [1,-1]:
            cs=trace_cyclotomic(p,eta,90)
            for j,c in enumerate(cs):
                q=j//p
                valuation=v_p_fraction(c,p)
                if c==0:
                    zeros+=1
                    record("cyclotomic_trace", p=p, eta=eta, degree=j, coefficient="0", valuation="infinity", bound=-q)
                    continue
                slack=valuation+q
                if slack<0:
                    raise AssertionError((p,eta,j,c,valuation,q))
                slacks.append(slack)
                checked+=1
                record("cyclotomic_trace", p=p, eta=eta, degree=j, coefficient=str(c), valuation=valuation, bound=-q)
            check(all(cs[j]==0 for j in range(1,p)),
                  f"p={p}, η={eta}: exact low-degree root-average cancellation for 1≤j<p")
            log(f"  p={p}, η={eta}: c_0={cs[0]}; c_p={cs[p]} (v_p={v_p_fraction(cs[p],p)}); c_(p+1)={cs[p+1]} (v_p={v_p_fraction(cs[p+1],p)})")
    check(checked+zeros==8*91,"All 728 rational cyclotomic trace coefficients pass the weighted bound")
    log(f"  Nonzero coefficients checked={checked}; exact zeros={zeros}; minimum valuation slack={min(slacks)}")
    SUMMARY['cyclotomic_trace_coefficients']=checked+zeros

    ch("TEST L — admissible minimum-cost menu checked by an independent coefficient enumeration")
    rng=random.Random(20261019)
    trials=0;none_count=0
    for p in [2,3]:
        F=Field(p)
        for case in range(100):
            n=rng.randint(1,3)
            cols=lambda j:[tuple(rng.randrange(p) for _ in range(n)) for _ in range(j)]
            D=cols(rng.randrange(0,3))
            R=cols(rng.randrange(1,3))
            C=cols(3)
            costs=[rng.randrange(0,5) for _ in C]
            solver=min_menu_repair(n,D,R,C,costs,F)
            brute=independent_menu_brute(n,D,R,C,costs,p)
            if brute is None:
                if solver['status']!='NO_REPAIR_IN_ADMISSIBLE_MENU':
                    raise AssertionError((p,n,D,R,C,costs,solver,brute))
                none_count+=1
            else:
                if (solver['cost'],len(solver['indices']),tuple(solver['indices']))!=brute:
                    raise AssertionError((p,n,D,R,C,costs,solver,brute))
            record("menu_crosscheck", prime=p, n=n, D=D, R=R, candidates=C, costs=costs,
                   selected=solver.get('indices'), cost=solver.get('cost'), independent_optimal_key=brute)
            trials+=1
        log(f"  F_{p}: 100/100 globally optimized menus cross-checked using independent brute enumeration")
    check(trials==200,"200 independent global menu optimization checks passed")
    log(f"  No admissible repair among the three menu items in {none_count}/200 scenarios")
    SUMMARY['independent_menu_optimality_cases']=trials

    ch("TEST M — many-cycle transport coherence under exact GF(5) matrices")
    rng=random.Random(82117)
    F=Field(5)
    test_edges=[(0,1),(1,2),(2,3),(3,4),(0,2),(1,3),(0,4),(2,4)]
    positives=0; negatives=0
    for repetition in range(130):
        U=[random_invertible_2x2(rng,F) for _ in range(5)]
        A=[random_invertible_2x2(rng,F) for _ in test_edges]
        B=[product(product(U[v],Ai,F), inverse(U[u],F),F)
           for (u,v),Ai in zip(test_edges,A)]
        # Reconstruct from spanning tree only.
        Ucalc=[U[0]]
        for j in range(4):
            Ucalc.append(product(product(B[j],Ucalc[-1],F),inverse(A[j],F),F))
        if Ucalc!=U:
            raise AssertionError("Tree reconstruction mismatch")
        bad_edges=[i for i,((u,v),Ai,Bi) in enumerate(zip(test_edges,A,B))
                   if product(Ucalc[v],Ai,F)!=product(Bi,Ucalc[u],F)]
        if bad_edges:
            raise AssertionError(("unexpected positive failures",bad_edges))
        positives+=1
        # Perturb only first chord (edge index4) by a nonzero scalar, still invertible.
        Bbad=B.copy(); Bbad[4]=scalar(Bbad[4],2,F)
        bad=[i for i,((u,v),Ai,Bi) in enumerate(zip(test_edges,A,Bbad))
             if product(Ucalc[v],Ai,F)!=product(Bi,Ucalc[u],F)]
        if bad!=[4]:
            raise AssertionError(("unexpected negative failures",bad))
        negatives+=1
        record("graph_gluing", field="F5", trial=repetition, edges=test_edges, source_edges=A,
               target_edges=B, vertex_intertwiners=U, corrupted_chord_edge=4,
               corrupted_target_edge=Bbad[4], positive_mismatches=bad_edges, negative_mismatches=bad)
        if repetition==0:
            log(f"  sample: vertices=5 edges=8 fundamental independent cycles=4")
            log(f"  input root U0={U[0]}; spanning-tree U_1={Ucalc[1]}; U_4={Ucalc[4]}")
            log(f"  positive cycle failures=[]; negative corrupted chord index={bad}, original B={B[4]}, changed B={Bbad[4]}")
    check(positives==130 and negatives==130,
          "130 random many-cycle positive gluings and 130 corrupted-chord negative tests passed")
    SUMMARY['graph_positive_cases']=positives
    SUMMARY['graph_negative_cases']=negatives
    ch("TEST N — finite Heisenberg phase relation from Paper XI rank-two carrier")
    Q=Field()
    a=Fraction(2)
    X=[[0,1],[a,0]]
    Z=[[1,0],[0,-1]]
    X2=product(X,X,Q)
    Z2=product(Z,Z,Q)
    conj=product(product(X,Z,Q),inverse(X,Q),Q)
    log(f"  X={X}, Z={Z}, scalar a={a}")
    log(f"  X²={X2}, Z²={Z2}, XZX^-1={conj}")
    check(X2==[[a,0],[0,a]] and Z2==eye(2,Q) and conj==scalar(Z,-1,Q),
          "Exact rank-two finite Heisenberg commutator/phase relations hold")
    wrong=eye(2,Q)
    expected_failure(product(product(X,wrong,Q),inverse(X,Q),Q)!=scalar(wrong,-1,Q),
                     "Trivial scalar marking does not reproduce the required nontrivial projective commutator")
    log("  Scope: finite matrix relation only; not a construction of the full p-adic inducing representation.")

    ch("TEST O — injectivity is required to transport *nonzero* obstruction certificates")
    rng=random.Random(192210)
    preserved=0; collapsed=0
    for p in [2,3,5]:
        F=Field(p)
        for iteration in range(110):
            n=3; target_dim=rng.randrange(1,4)
            D=[tuple(rng.randrange(p) for _ in range(n)) for _ in range(2)]
            R=[tuple(rng.randrange(p) for _ in range(n)) for _ in range(2)]
            B=[[rng.randrange(p) for _ in range(n)] for _ in range(target_dim)]
            apply=lambda v:tuple(sum(B[i][j]*v[j] for j in range(n))%p for i in range(target_dim))
            DD=[apply(d) for d in D]; RR=[apply(r) for r in R]
            source=rank_of_columns(n,D+R,F)-rank_of_columns(n,D,F)
            target=rank_of_columns(target_dim,DD+RR,F)-rank_of_columns(target_dim,DD,F)
            if target>source:
                raise AssertionError("Quotient naturality rank can never increase")
            record("naturality", p=p, case=iteration, D=D, R=R, map_B=B,
                   source_obstruction_dim=source, target_obstruction_dim=target, collapsed=target<source)
            if target==source:
                preserved+=1
            else:
                collapsed+=1
        log(f"  F_{p}: 110 random commuting quotient diagrams pass rank-nonincreasing test")
    check(preserved+collapsed==330 and collapsed>0,
          "330 naturality checks, including genuine quotient-information losses")
    log(f"  injective on tested obstruction spans={preserved}; collapsing maps={collapsed}")
    SUMMARY['obstruction_transport_naturality_cases']=330
    SUMMARY['obstruction_transport_collapse_cases']=collapsed

    ch("TEST P — nearby nonlinear solutions despite nonzero first-order obstruction")
    epsilon=Fraction(1,10000)
    f0=-epsilon;derivative0=0
    root=Fraction(1,100)
    log(f"  F(x)=x²−{epsilon}, start x=0, residual={f0}, linearized derivative={derivative0}")
    log(f"  Exact nearby root x={root}, squared={root*root} = epsilon; distance |x|={root}")
    expected_failure(f0!=0 and derivative0==0 and root*root==epsilon,
                     "Linearized cokernel is nonzero yet an exact nonlinear solution exists within distance 0.01")

