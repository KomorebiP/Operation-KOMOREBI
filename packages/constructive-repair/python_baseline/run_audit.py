"""Reproducible exact-arithmetic experiments and falsification controls."""
import json
import random
from fractions import Fraction
from itertools import product as cartprod
from math import comb
from pathlib import Path
from repair_core import (Field, rank_of_columns, free_obstruction_basis, feasibility_certificate,
                         min_menu_repair, admissible_under_conservation, product, inverse,
                         scalar, check_triangle_gluing, solve_columns)

OUT = Path(__file__).resolve().parent
LINES = []
CASE_RECORDS = []

def record(kind, **data):
    CASE_RECORDS.append(dict(kind=kind, **data))

SUMMARY = {"program":"Komorebi constructive repair prototype v0.1.0", "source":"standalone prototype, not the existing Komorebi library", "assertion_count":0,
           "negative_controls":[], "random_seed":20261019, "formal_kernel_compilation":"NOT_RUN (Lean and Lake absent)", "chapters":[]}

def log(s=""):
    s=str(s)
    print(s)
    LINES.append(s)

def check(condition, explanation, status="PASS"):
    if not condition:
        log("FAIL: "+explanation)
        raise AssertionError(explanation)
    SUMMARY["assertion_count"] += 1
    log(f"{status}: {explanation}")

def ch(title):
    log("\n"+"="*78+"\n"+title+"\n"+"="*78)
    SUMMARY["chapters"].append(title)

def expected_failure(condition, explanation):
    check(condition, explanation, "EXPECTED-FAILURE DETECTED")
    SUMMARY["negative_controls"].append(explanation)


def finite_membership_bruteforce(n, cols, rhs, p):
    """Independent enumeration (does not call Gaussian elimination)."""
    if len(cols) > 4 or p > 5:
        raise ValueError("Only tiny finite systems permitted")
    for x in cartprod(range(p), repeat=len(cols)):
        if all(sum(x[j]*cols[j][i] for j in range(len(cols)))%p==rhs[i]%p for i in range(n)):
            return tuple(x)
    return None


def test_linear():
    ch("TEST A — unrestricted exact linear repair (Q and finite fields)")
    F=Field()
    D=[(1,0,0,0),(0,1,0,0)]
    R=[(0,0,2,0),(0,0,0,3),(0,0,2,3),(2,3,0,0)]
    base=rank_of_columns(4,D,F)
    extended=rank_of_columns(4,D+R,F)
    basis=free_obstruction_basis(4,D,R,F)
    cert=feasibility_certificate(4,D,R,[R[i] for i in basis],F)
    log(f"D columns={D}")
    log(f"Residual columns={R}")
    log(f"rank(D)={base}; rank([D | R])={extended}; quotient span dimension={extended-base}")
    log(f"Selected free directions indexed={basis}: {[R[i] for i in basis]}")
    for k,w in enumerate(cert['witnesses']):
        log(f"  residual {k}: correction coefficients (D coordinates | added coordinates)={w}")
    check(basis==[0,1],"Independent residual basis modulo im(D) is exactly residuals 0 and 1")
    check(cert['status']=='EXACT_REPAIR_CERTIFIED',"All four residuals admit exact correction witnesses")
    check(len(basis)==extended-base==2,"Free minimal correction dimension is 2")

    log("\nRandomized rank/basis checks:")
    rng=random.Random(20261019)
    summary={}
    for field in (None,2,3,5,7):
        FF=Field(field)
        for idx in range(270):
            n=rng.randrange(1,6)
            d=rng.randrange(0,5)
            r=rng.randrange(0,5)
            pick=lambda: tuple(rng.randrange(-3,4) if field is None else rng.randrange(field) for _ in range(n))
            Ds=[pick() for _ in range(d)]
            Rs=[pick() for _ in range(r)]
            b=free_obstruction_basis(n,Ds,Rs,FF)
            cert=feasibility_certificate(n,Ds,Rs,[Rs[i] for i in b],FF)
            if cert['status']!='EXACT_REPAIR_CERTIFIED':
                raise AssertionError((field,Ds,Rs,b,cert))
            if len(b)!=rank_of_columns(n,Ds+Rs,FF)-rank_of_columns(n,Ds,FF):
                raise AssertionError("rank test")
            record("free_rank_case", field="Q" if field is None else field, trial=idx, n=n, D=Ds, R=Rs,
                   obstruction_rank=len(b), free_basis_indices=b,
                   witness_coefficients=cert['witnesses'])
        summary[str(field)]=270
        log(f"  field={'Q' if field is None else 'F_'+str(field)}: 270/270 random cases PASS")
    SUMMARY['linear_random_cases']=sum(summary.values())
    check(SUMMARY['linear_random_cases']==1350,"1,350 random finite/rational tests completed")


def test_constrained():
    ch("TEST B — constrained finite menus, repair cost, and invariants")
    F=Field()
    D=[(1,0,0)]
    R=[(0,1,0)]
    e1=(0,1,1)
    e2=(0,0,1)
    cert1=feasibility_certificate(3,D,R,[e1],F)
    cert2=feasibility_certificate(3,D,R,[e2],F)
    cert12=feasibility_certificate(3,D,R,[e1,e2],F)
    log(f"D={D}; target={R}; available e1={e1}, e2={e2}")
    log(f"Obstruction rank={rank_of_columns(3,D+R,F)-rank_of_columns(3,D,F)}")
    log(f"single e1: {cert1['status']} ranks={cert1['ranks']}")
    log(f"single e2: {cert2['status']} ranks={cert2['ranks']}")
    log(f"pair: {cert12['status']}; witness={cert12['witnesses']}")
    expected_failure(cert1['status']!='EXACT_REPAIR_CERTIFIED' and cert2['status']!='EXACT_REPAIR_CERTIFIED',
                     "Naive claim 'obstruction dimension always equals number of menu items needed' is false")
    check(cert12['status']=='EXACT_REPAIR_CERTIFIED',"The two candidate directions jointly span the obstruction")
    optimum=min_menu_repair(3,D,R,[e1,e2], [1,1], F)
    log(f"Optimal menu={optimum['indices']}; cost={optimum['cost']}; audited subsets={optimum['tested_subsets']}")
    check(optimum['indices']==[0,1],"Minimum-cardinality permitted menu requires 2 directions")
    option3=(0,1,0)
    weighted=min_menu_repair(3,D,R,[e1,e2,option3],[1,1,9],F)
    log(f"Weighted menu: candidates={[e1,e2,option3]} costs={[1,1,9]}; selected={weighted['indices']} cost={weighted['cost']}")
    check(weighted['indices']==[0,1] and weighted['cost']==2,
          "Minimum cost differs from the minimum number of directions")
    cheap=min_menu_repair(3,D,R,[e1,e2,option3],[5,5,2],F)
    log(f"Alternate costs={[5,5,2]} selected={cheap['indices']} cost={cheap['cost']}")
    check(cheap['indices']==[2],"Optimal choice switches when the cost model changes")
    no=min_menu_repair(3,D,R,[(0,0,1)], [1], F)
    log(f"Missing repair direction: status={no['status']}; subsets={no['tested_subsets']}")
    expected_failure(no['status']=='NO_REPAIR_IN_ADMISSIBLE_MENU',"Finite menu cannot always repair a nonzero obstruction")

    # The invariant L(v)=v_2 must be preserved by all changes, and D has image ker L.
    DD=[(1,0)]
    RR=[(0,1)]
    candidate_restricted=[(0,1),(1,0)]
    ell=[(0,1)]
    allowed=admissible_under_conservation(candidate_restricted,ell,F)
    log(f"Conserved functional L(v)=v[1]. Residual={RR[0]}; candidates={candidate_restricted}; allowed mask={allowed}")
    check(allowed==[False,True],"Invariance rejects the only candidate that could cancel the defect")
    bad=min_menu_repair(2,DD,RR,candidate_restricted,[1,1],F,allowed=allowed)
    log(f"Conservation-respecting solver={bad['status']}")
    expected_failure(bad['status']=='NO_REPAIR_IN_ADMISSIBLE_MENU',"No legal repair when a preserved functional detects the residual")
    unrestricted=min_menu_repair(2,DD,RR,candidate_restricted,[1,1],F)
    log(f"Unrestricted solver={unrestricted['status']}, selected={unrestricted['indices']}")
    check(unrestricted['indices']==[0],"Unrestricted repair exists, demonstrating why the preservation profile matters")


def test_independent_solver():
    ch("TEST C — independently brute-force-check Gaussian feasibility over finite fields")
    rng=random.Random(166)
    count=0
    for p in [2,3,5]:
        F=Field(p)
        for i in range(170):
            n=rng.randint(1,4)
            d=rng.randint(0,3)
            cols=[tuple(rng.randrange(p) for _ in range(n)) for _ in range(d)]
            rhs=tuple(rng.randrange(p) for _ in range(n))
            ans=solve_columns(n, cols, rhs, F)
            brute=finite_membership_bruteforce(n,cols,rhs,p)
            check_same=(ans is None)==(brute is None)
            if not check_same:
                raise AssertionError(f"Disagreement p={p} cols={cols} rhs={rhs}: algebra={ans}, enumeration={brute}")
            record("independent_solver", prime=p, n=n, columns=cols, rhs=rhs, exact_solution=ans, brute_solution=brute)
            count+=1
        log(f"  F_{p}: 170/170 random systems verified by independent exhaustive enumeration")
    SUMMARY['independent_solver_crosschecks']=count
    check(count==510,"510 exact solver-vs-enumeration feasibility cross-checks")


def test_obstruction_transport():
    ch("TEST D — obstruction-faithful versus information-destroying transport")
    F=Field()
    D=[]  # D: zero into Q^2
    residual=[(0,1)]
    source=rank_of_columns(2,residual,F)-rank_of_columns(2,D,F)
    # b projects Q^2 onto first coordinate: b(0,1)=0.
    transported=(residual[0][0],)
    target=rank_of_columns(1,[transported],F)
    log(f"Source obstruction [r]={residual[0]}, rank={source}")
    log(f"Coarse transport b(x,y)=x: b(r)={transported}, target obstruction rank={target}")
    expected_failure(source==1 and target==0,"Vanishing transported obstruction does NOT imply vanishing source obstruction without injectivity")
    # B is invertible and hence faithful on all classes with D=0.
    B=[[1,1],[0,1]]
    img=(B[0][0]*residual[0][0]+B[0][1]*residual[0][1],
         B[1][0]*residual[0][0]+B[1][1]*residual[0][1])
    log(f"Invertible transport B={B}: B(r)={img}")
    check(rank_of_columns(2,[img],F)==source,"Invertible transport preserves the obstruction dimension")


def test_nonlinear():
    ch("TEST E — nonlinear failure modes of the linearized obstruction")
    # F(x)=x^2 -1; x0=0; D=F'(0)=0; defect -1; linear correction impossible.
    log("F(x)=x^2-1 at x0=0: residual=-1, derivative D=0")
    log("  Linear equation D·u=1: unsolvable; exact nonlinear solution x=1 gives F(1)=0")
    expected_failure((0 != 1) and (1*1-1 == 0),"Nonzero first-order obstruction need not forbid a nonlinear solution")
    # G(x)=x^2+x+1, derivative at 0 =1; but >=3/4 for all real x.
    log("G(x)=x^2+x+1 at x0=0: residual=1, derivative=1, linear correction u=-1")
    log("  G(-1)=1, and G(x)=(x+1/2)^2+3/4>0 over real x")
    expected_failure((-1)**2+(-1)+1==1 and Fraction(3,4)>0,
                     "Zero linear obstruction does not guarantee a global nonlinear solution")
    log("These examples do not contradict properly scoped local nonlinear correction theorems; no global claim follows from linearization.")


def hensel_lifts(a, p, x0, digits):
    """Teichmüller-style digit-by-digit Hensel trace for f(x)=x^2-a."""
    assert (x0*x0-a)%p==0
    x=x0
    trace=[]
    for k in range(1,digits):
        pk=p**k
        f=x*x-a
        assert f % pk==0
        c=(f//pk)%p
        d=(2*x)%p
        if d==0:
            trace.append(dict(k=k,old=x,modulus=pk,derivative_mod_p=0, status="SINGULAR: linear digit method cannot certify"))
            break
        t=(-c*pow(d,-1,p))%p
        y=x+t*pk
        assert (y*y-a)%(p**(k+1))==0
        trace.append(dict(k=k,old=x,old_residual=f,old_modulus=pk,
                          reduced_residual=c,derivative_mod_p=d,correction_digit=t,
                          new=y,new_modulus=p**(k+1),new_residual=y*y-a,status="EXACT_DIGIT_LIFT"))
        x=y
    return trace


def test_hensel():
    ch("TEST F — filtered arithmetic repair, valid Hensel lifts and singular failures")
    tr=hensel_lifts(2,7,3,7)
    for v in tr:
        log("  "+json.dumps(v,sort_keys=True))
        record("hensel_digit", **v)
    check(len(tr)==6 and all(v['status']=='EXACT_DIGIT_LIFT' for v in tr),"Six consecutive exact 7-adic digit repairs were constructed")
    # a=2, p=2, root x=0 mod 2, no lift mod 4, derivative nonunit.
    possible=[x for x in (0,2) if (x*x-2)%4==0]
    log(f"p=2, f(x)=x²-2, root x0=0 mod 2; candidates modulo 4 are 0,2; valid lifts={possible}")
    expected_failure(not possible,"Singular mod-2 root does NOT lift mod 4 (genuine next-depth obstruction)")
    log("p=2, f(x)=x²-1, root x0=1; derivative=0 mod 2; x=1 lifts to all 2^k")
    check((2*1)%2==0 and all((1*1-1)%(2**k)==0 for k in range(1,10)),
          "Nonunit derivative does not by itself forbid lifting")
    SUMMARY['hensel_successive_lifts']=len(tr)


def test_projector():
    ch("TEST G — finite root-of-unity projector orthogonality")
    F=Field(13)
    m=3
    omega=3
    check(pow(omega,m,13)==1 and all(pow(omega,k,13)!=1 for k in range(1,m)),
          "ω=3 is a primitive cube root of unity in F_13")
    c=[(7*j*j+3*j+11)%13 for j in range(20)]
    def P(a,data):
        out=[]
        for k,coeff in enumerate(data):
            phase=sum(pow(omega, (ell*(k-a))%m,13) for ell in range(m))
            out.append(coeff*phase*pow(m,-1,13)%13)
        return out
    for a in range(m):
        proj=P(a,c)
        log(f"  Π_{m},{a}: support degrees={[i for i,x in enumerate(proj) if x != 0]}, coefficients={proj}")
        record("root_filter", prime=13, m=m, a=a, original=c, projected=proj)
        check(proj==[(v if i%m==a else 0) for i,v in enumerate(c)], f"P_{a} exact coefficient projection")
        check(P(a,proj)==proj,f"P_{a} idempotent")
        for b in range(m):
            if a!=b:
                check(P(a,P(b,c))==[0]*len(c),f"P_{a}P_{b}=0")
    check([sum(P(a,c)[i] for a in range(m))%13 for i in range(len(c))]==c,
          "Sum of all root projectors reconstructs original series")
    try:
        pow(3,-1,3)
        raise AssertionError("Unexpected unit for divisor of characteristic")
    except ValueError:
        log("  Negative control: 1/m does not exist over F_3 when m=3")
        SUMMARY['negative_controls'].append("Root-of-unity normalized averaging undefined if characteristic divides projector order")


def test_holonomy():
    ch("TEST H — graph gluing with a fundamental cycle")
    F=Field(5)
    A01=[[1,1],[0,1]]
    A12=[[2,0],[0,1]]
    A02=[[1,0],[1,1]]
    U0=[[1,1],[0,1]]
    U1=[[1,0],[1,1]]
    U2=[[2,1],[1,1]]
    B01=product(product(U1,A01,F),inverse(U0,F),F)
    B12=product(product(U2,A12,F),inverse(U1,F),F)
    B02=product(product(U2,A02,F),inverse(U0,F),F)
    log(f"A01={A01} A12={A12} A02={A02}")
    log(f"U0={U0} U1={U1} U2={U2}")
    log(f"B01={B01} B12={B12} B02={B02}")
    pos=check_triangle_gluing(A01,A12,A02,B01,B12,B02,U0,F)
    log(f"Positive: status={pos['status']}; reconstructed U1={pos['U1']}, U2={pos['U2']}")
    log(f"  fundamental holonomies A={pos['holonomy_A']} B={pos['holonomy_B']}")
    check(pos['status']=='GLUING_CERTIFIED' and pos['U1']==U1 and pos['U2']==U2,
          "Chosen fundamental cycle certifies all edge intertwining constraints")
    Bbad=scalar(B02,2,F)  # still invertible, but holonomy changes
    neg=check_triangle_gluing(A01,A12,A02,B01,B12,Bbad,U0,F)
    log(f"Negative: modified invertible B02={Bbad}, status={neg['status']}")
    log(f"  chord mismatch left={neg['chord_left']} right={neg['chord_right']}")
    log(f"  fundamental holonomies A={neg['holonomy_A']} B={neg['holonomy_B']}")
    expected_failure(neg['status']=='HOLONOMY_OBSTRUCTION',"All local edges invertible but global gluing fails")


def test_filtered_truncation():
    ch("TEST I — exact p-adic truncation and deliberately false weight control")
    p=7
    n=6
    c=[1,3,-2,5,1,-4,6]
    S=[-2,1,3,-1,4,2,7]
    total=sum(comb(n,j)*c[j]*p**(2*j)*S[n-j] for j in range(n+1))
    log(f"p={p}, n={n}, c={c}, S={S}")
    log(f"Full integer combination E={total}")
    for L in range(1,12):
        partial=sum(comb(n,j)*c[j]*p**(2*j)*S[n-j] for j in range(n+1) if 2*j<L)
        delta=total-partial
        check(delta % (p**L)==0, f"precision p^{L}: terms retained={sum(2*j<L for j in range(n+1))}, delta divisible by p^{L}")
    # intentionally remove j=1 when L=4, where its valuation is only 2
    L=4
    partial_wrong=sum(comb(n,j)*c[j]*p**(2*j)*S[n-j] for j in range(n+1) if j==0)
    diff=total-partial_wrong
    log(f"Incorrect weight model discards j=1 at L=4; actual delta={diff}, modulo 7^4 is {diff%7**4}")
    expected_failure(diff%7**4 != 0,"Overestimating a weight creates a false congruence certificate")


def main():
    log("Komorebi — Experimental Constructive Repair Audit v0.1.0")
    log("Computation: stdlib Fraction/rational and modular arithmetic. Deterministic seed.")
    log("STATUS: tests of a proposed refinement, NOT new kernel-certified general theorems.")
    test_linear();test_constrained();test_independent_solver();test_obstruction_transport()
    test_nonlinear();test_hensel();test_projector();test_holonomy();test_filtered_truncation()
    from extra_audit import run_extra
    run_extra(log, check, ch, expected_failure, SUMMARY, record)
    ch("SUMMARY / VERIFICATION BOUNDARY")
    SUMMARY['individual_case_records']=len(CASE_RECORDS)
    log(f"Exact assertions/expected failures checked: {SUMMARY['assertion_count']}")
    log(f"Individual, reproducible cases saved: {len(CASE_RECORDS)}")
    log(f"Random structural cases: {SUMMARY['linear_random_cases']}")
    log(f"Independent enumerated solver checks: {SUMMARY['independent_solver_crosschecks']}")
    log(f"Expected negative controls detected: {len(SUMMARY['negative_controls'])}")
    for s in SUMMARY['negative_controls']:
        log("  NEGATIVE CONTROL: "+s)
    log("Lean toolchain absent: no new Lean kernel certification claimed.")
    log("Known limits: exact finite/rational settings only; exhaustive cost solver exponential in number of candidates.")
    log("Verdict: restricted repair theorem and certificate algorithm PASS; unrestricted/universal repair thesis NOT ESTABLISHED.")
    (OUT/'case_records.jsonl').write_text(''.join(json.dumps(d,default=str,sort_keys=True)+'\n' for d in CASE_RECORDS),encoding='utf8')
    (OUT/'audit_trace.txt').write_text('\n'.join(LINES)+'\n',encoding='utf8')
    (OUT/'audit_summary.json').write_text(json.dumps(SUMMARY,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':
    main()
