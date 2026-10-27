#!/usr/bin/env python3
"""Independent finite exact checks of the reusable family and phase API.

Run from any directory. The theorem proofs are in sequence_polyphase.md;
success here checks these implementations on the explicitly reported ranges.
"""
from fractions import Fraction as Q
from math import factorial
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import family_lab as lab


def picard_taylor(channels,degree):
    p=[Q(0)]*(degree+1)
    for _ in range(degree+1):
        rhs=[Q(0)]*degree;rhs[0]=Q(1)
        for h,q,r in channels:
            for i,a in enumerate(p):
                for j,b in enumerate(p[:max(0,degree-i)]):
                    rhs[i+j] += h*a*b*q**i*r**j
        p=[Q(0)]+[a/Q(j+1) for j,a in enumerate(rhs)]
    return p


def tan_series(degree):
    # Independent sin/cos division; no nonlinear recurrence.
    sin=[Q(0)]*(degree+1);cos=[Q(0)]*(degree+1)
    for i in range(degree+1):
        if i%2:sin[i]=Q((-1)**((i-1)//2),factorial(i))
        else:cos[i]=Q((-1)**(i//2),factorial(i))
    p=[]
    for n in range(degree+1):
        p.append(sin[n]-sum((cos[j]*p[n-j] for j in range(1,n+1)),Q(0)))
    return p


PHI={1:[-1,1],2:[1,1],3:[1,1,1],4:[1,0,1],5:[1,1,1,1,1],
     6:[1,-1,1],7:[1,1,1,1,1,1,1]}


def root_filter_multiplier(base,m,residue):
    # Sum omega^(k*(m-residue)) in Q[omega]/(Phi_base), using exact division.
    p=[Q(0)]*base
    for k in range(base):p[(k*(m-residue))%base]+=1
    f=PHI[base]
    while len(p)>=len(f):
        c=p[-1]
        degree=len(p)-len(f)
        for j,x in enumerate(f):p[degree+j]-=c*x
        p.pop()
    return [x/Q(base) for x in p]


def run():
    started=time.monotonic();counts={}
    def check(category,ok):
        if not ok:raise AssertionError(category)
        counts[category]=counts.get(category,0)+1
    data=lab.catalog(12)
    check("catalog_structure",data["catalog_count"]==18)
    polynomials=lab.asymmetric_polynomials(8)
    check("hand_polynomials",polynomials[0]=={(0,0):1})
    check("hand_polynomials",polynomials[1]=={(1,1):2})
    check("hand_polynomials",polynomials[2]=={(2,4):8,(4,2):8})
    for n,p in enumerate(polynomials):
        check("polynomial_symmetry",p=={(v,u):x for (u,v),x in p.items()})
        for (u,v),a in p.items():
            check("integer_positive_polynomial",isinstance(a,int) and a>0)
            check("polynomial_degree_bound",u+v<=n*(n+1))
            check("polynomial_parity",u%2==n%2 and v%2==n%2)
    degree=25
    independent_tan=tan_series(degree)
    samples=[]
    for row in data["rows"]:
        channels=[tuple(Q(x) for x in channel) for channel in row["channels"]]
        a=lab.feedback_odd_derivatives(channels,12)
        ordinary=lab.ordinary_taylor_coefficients(a)
        independent=picard_taylor(channels,degree)
        full=lab.full_egf_coefficients(a)
        for m,x in enumerate(independent):
            check("independent_picard",x==full[m]/factorial(m))
        for n,x in enumerate(a):
            check("serialization",Q(row["A_n"][n])==x)
            check("normalization",x==ordinary[n]*factorial(2*n+1))
            check("denominator_clearing",Q(row["cleared_A_n"][n]).denominator==1)
        swapped=lab.feedback_odd_derivatives([(h,r,q) for h,q,r in channels],12)
        for x,y in zip(a,swapped):check("channel_symmetry",x==y)
        if len(channels)==1:
            _,q,r=channels[0]
            for n,p in enumerate(polynomials):
                check("polynomial_evaluation",lab.evaluate_polynomial(p,q,r)==a[n])
        if row["id"]=="tangent":
            for n,x in enumerate(ordinary):
                check("independent_tangent",x==independent_tan[2*n+1])
            check("known_tangent_anchor",a[:8]==[1,2,16,272,7936,353792,22368256,1903757312])
        if row["id"]=="hyperbolic_tangent":
            for n,x in enumerate(ordinary):
                check("known_tanh_anchor",x==(-1)**n*independent_tan[2*n+1])
        if row["id"]=="scaled_sinh":
            for n,x in enumerate(a):check("known_sinh_anchor",x==Q(1,2**n))
        if row["id"]=="linear":check("known_linear_anchor",a==[1]+[0]*12)
        if row["id"]=="entire_infinite_order_boundary":
            # The exact coefficient identity for the boundary linear equation.
            for n in range(1,13):
                coefficient=sum((Q(1,2)**(2*i+1)*ordinary[i]*ordinary[n-1-i]
                                 for i in range(n)),Q(0))
                check("boundary_linear_equation",(2*n+1)*ordinary[n]==coefficient)
        samples.append({"id":row["id"],"first_five_A":[str(x) for x in a[:5]]})
    for base in range(1,8):
        for m in range(32):
            for j in range(base):
                expected=[Q(int(m%base==j))]+[Q(0)]*(len(PHI[base])-2)
                check("independent_cyclotomic_filter",root_filter_multiplier(base,m,j)==expected)
    # Sequences with positive, zero and signed entries exercise carries and cancellation.
    taps_cases=[[1],[1,1],[Q(1,2),-1,Q(3,2)], [0,1,0,-2,3,0,1]]
    for length in range(1,27):
        a=[Q((m*m+3*m)%11-5,m%4+1) for m in range(length)]
        for base in range(1,8):
            lanes=lab.phase_lanes(a,base)
            check("phase_reconstruction",lab.merge_lanes(lanes)==a)
            sections=[lab.section(a,base,j) for j in range(base)]
            for m in range(length):
                check("section_reconstruction",sum(s[m] for s in sections)==a[m])
            for h in taps_cases:
                expected=lab.ordinary_taps(a,h)
                matrix=lab.polyphase_tap_matrix(h,base)
                actual=lab.merge_lanes(lab.apply_polyphase_matrix(lanes,matrix,len(expected)),len(expected))
                check("polyphase_fir_matrix",actual==expected)
        for order in range(6):
            check("derivative_integral_inverse",lab.derivative_shift(lab.integral_shift(a,order),order)==a)
        for h in taps_cases:
            expected=lab.ordinary_taps(a,h)
            actual=[Q(0)]*len(expected)
            for t,x in enumerate(h):
                for m,y in enumerate(lab.integral_shift(a,t)):
                    actual[m]+=x*y
            check("egf_taps_antiderivatives",expected==actual)
    # Exact EGF product verification against ordinary Taylor multiplication.
    for length in range(1,18):
        a=[Q(m+2,m%3+1) for m in range(length)]
        b=[Q((-1)**m,m+1) for m in range(8)]
        out=lab.hurwitz_product(a,b)
        ordinary=lab.ordinary_taps([x/factorial(m) for m,x in enumerate(a)],
                                   [x/factorial(m) for m,x in enumerate(b)])
        for m,x in enumerate(out):check("hurwitz_independent_cauchy",x/factorial(m)==ordinary[m])
    a=[Q(1)]*8;h=[Q(1),Q(1)]
    check("negative_control_hurwitz_not_fir",lab.hurwitz_product(a,h)[2]==3 and lab.ordinary_taps(a,h)[2]==2)
    a=[Q(m*m+1) for m in range(13)]
    check("negative_control_derivative_not_delay",lab.derivative_shift(a)!=lab.integral_shift(a))
    lanes=lab.phase_lanes(a,3)
    check("negative_control_phase_carry",lab.polyphase_tap_matrix([0,1],3)[0][2]=={1:Q(1)})
    check("negative_control_no_lane_alias",lab.merge_lanes(lanes)!=sum(lanes,[]))
    try:lab.merge_lanes(lanes,12)
    except ValueError:check("negative_control_no_silent_truncation",True)
    else:check("negative_control_no_silent_truncation",False)
    check("empty_taps",lab.ordinary_taps([],h)==[] and lab.ordinary_taps(a,[])==[])
    check("empty_lanes",lab.merge_lanes(lab.phase_lanes([],3))==[])
    try:lab.section(a,3,Q(3,2))
    except ValueError:check("reject_fractional_residue",True)
    else:check("reject_fractional_residue",False)
    try:lab.apply_polyphase_matrix([],[],0)
    except ValueError:check("reject_zero_phase_base",True)
    else:check("reject_zero_phase_base",False)
    code=Path(lab.__file__).read_bytes()
    result={"contract":"SF-DISCOVERY-100","status":"passed","python":platform.python_version(),
            "coefficient_domain":"Q exactly; sparse Z[q,r] for factorial-normalized asymmetric coefficients",
            "exact_assertions":sum(counts.values()),"assertion_categories":counts,
            "bounds":{"last_odd_index":12,"degree_z":25,"bivariate_last_index":8,
                      "catalog_rows":18,"root_filter_bases":"1..7","root_filter_indices":"0..31",
                      "fir_input_lengths":"1..26","fir_bases":"1..7","tap_vectors":4},
            "independence":"Dense formal Picard iteration; sin/cos division; cyclotomic reduction; ordinary Taylor Cauchy product; direct FIR vs phase matrix",
            "samples":samples,"input_sha256":{"family_lab.py":hashlib.sha256(code).hexdigest(),
                "checks/family_lab_checks.py":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            "runtime_seconds":time.monotonic()-started,
            "non_claims":["Finite checks do not prove entire extension, growth order or historical novelty.",
                          "No OEIS accession was verified by this script.","The positive integer asymmetric rows have radius zero; the one-unit-scale boundary has a separately proved entire extension."],
            "failures":[{"kind":"input-validation defect","finding":"Fractional projector residue returned an all-zero section instead of raising; an empty phase matrix accepted base zero.",
                         "resolution":"Require integer residue and positive phase count; both invalid-input regression checks now pass."}]}
    evidence=ROOT/"evidence"/"family_lab_checks.json"
    evidence.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    return result


if __name__=="__main__":run()
