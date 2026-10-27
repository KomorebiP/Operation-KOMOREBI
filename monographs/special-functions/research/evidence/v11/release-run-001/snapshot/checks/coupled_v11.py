#!/usr/bin/env python3
"""Independent finite checks for coupled_lab.py, SF-DISCOVERY-110.

Run: python3 checks/coupled_v11.py
The finite output verifies implementation, not the universal growth theorem.
"""
from fractions import Fraction as Q
from math import factorial, log
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import coupled_lab as lab
import family_lab as scalar


def dense_picard(p,degree):
    """Independent ordinary Taylor Picard integration, including all parities."""
    q,r,a,b=map(Q,p)
    u=v=[Q(0)]*(degree+1)
    for _ in range(degree+1):
        rhs_u=[Q(0)]*degree;rhs_v=[Q(0)]*degree
        rhs_u[0]=rhs_v[0]=Q(1)
        for i,x in enumerate(u[:degree]):
            for j,y in enumerate(v[:degree-i]):
                rhs_u[i+j]+=x*q**i*y*r**j
                rhs_v[i+j]+=x*a**i*y*b**j
        u=[Q(0)]+[x/(i+1) for i,x in enumerate(rhs_u)]
        v=[Q(0)]+[x/(i+1) for i,x in enumerate(rhs_v)]
    return u,v


def independent_tangent(degree):
    sin=[Q(0)]*(degree+1);cos=[Q(0)]*(degree+1)
    for j in range(degree+1):
        if j%2:sin[j]=Q((-1)**((j-1)//2),factorial(j))
        else:cos[j]=Q((-1)**(j//2),factorial(j))
    out=[]
    for n in range(degree+1):
        out.append(sin[n]-sum((cos[j]*out[n-j] for j in range(1,n+1)),Q(0)))
    return out


def run():
    start=time.monotonic();exact={};numeric={};guards={}
    def check(category,condition,bucket=exact):
        if not condition:raise AssertionError(category)
        bucket[category]=bucket.get(category,0)+1
    def rejects(name,fn):
        try:fn()
        except ValueError:check(name,True,guards)
        else:raise AssertionError(name+" did not reject")
    data=lab.catalog(10)
    samples=[]
    for row in data["rows"]:
        p=tuple(map(Q,row["scales"]))
        u,v=lab.coupled_odd_derivatives(*p,last=10)
        dense=dense_picard(p,21)
        swapped=lab.coupled_odd_derivatives(p[3],p[2],p[1],p[0],last=10)
        for actual,full,other in zip((u,v),dense,swapped[::-1]):
            egf=lab.full_egf_coefficients(actual)
            for m,x in enumerate(full):check("independent_dense_picard",x==egf[m]/factorial(m))
            for x,y in zip(actual,other):check("component_swap",x==y)
        check("hand_cubic_U",u[1]==2*p[0]*p[1])
        check("hand_cubic_V",v[1]==2*p[2]*p[3])
        check("hand_quintic_U",u[2]==8*p[0]*p[1]**3*p[2]*p[3]+8*p[0]**4*p[1]**2)
        check("hand_quintic_V",v[2]==8*p[2]**2*p[3]**4+8*p[2]**3*p[3]*p[0]*p[1])
        d,m,(cu,cv)=lab.cleared_derivatives(*p,last=10)
        for name,arr,cleared in (("U",u,cu),("V",v,cv)):
            for n,(value,integer) in enumerate(zip(arr,cleared)):
                check("rational_denominator_clearing",integer.denominator==1)
                check("catalog_roundtrip",Q(row[name+"_derivatives"][n])==value)
                check("catalog_cleared_roundtrip",Q(row["cleared_"+name][n])==integer)
                if all(0<x<1 for x in p):check("positive_contraction_coefficients",value>0)
        for arr in (u,v):
            full=lab.full_egf_coefficients(arr)
            for base in range(2,7):
                phases=lab.phase_lanes(full,base)
                check("phase_reconstruction",lab.merge_lanes(phases)==full)
                for h in ([1,-2,1],[0,1,0,Q(1,2),-1]):
                    direct=lab.ordinary_taps(full,h)
                    matrix=lab.polyphase_tap_matrix(h,base)
                    output=lab.apply_polyphase_matrix(phases,matrix,len(direct))
                    check("coupled_polyphase_fir",lab.merge_lanes(output,len(direct))==direct)
        samples.append({"id":row["id"],"first_U":[str(x) for x in u[:4]],
                        "first_V":[str(x) for x in v[:4]]})
    for q,r in [(Q(1,2),Q(1,2)),(Q(1,3),Q(2,3)),(Q(1,4),Q(3,4)),(Q(1),Q(2))]:
        expected=scalar.asymmetric_odd_derivatives(q,r,12)
        for p in ((q,r,q,r),(q,r,r,q)):
            for arr in lab.coupled_odd_derivatives(*p,last=12):
                for x,y in zip(arr,expected):check("scalar_reduction",x==y)
    for arr in lab.coupled_odd_derivatives(*([Q(1,2)]*4),last=20):
        for n,x in enumerate(arr):check("known_sinh_derivatives",x==Q(1,2**n))
    tan=independent_tangent(25)
    for arr in lab.coupled_odd_derivatives(1,1,1,1,12):
        for n,x in enumerate(arr):check("independent_tangent_division",x/factorial(2*n+1)==tan[2*n+1])
    # A wrong row-swapping convention and scalar replacement must be detectable.
    p=tuple(map(Q,("1/5","2/5","3/5","7/10")))
    u,v=lab.coupled_odd_derivatives(*p,last=10)
    wrong=lab.coupled_odd_derivatives(p[2],p[3],p[0],p[1],last=10)
    check("negative_control_wrong_swap",(v,u)!=wrong)
    check("negative_control_not_scalar",u[1]!=v[1])
    q,r,a,b=p
    check("exact_PF_anchor_first_row",q*Q(1,2)+r==Q(1,2))
    check("exact_PF_anchor_second_row",a*Q(1,2)+b==1)
    check("exact_PF_determinant",(1-q)*(1-b)-r*a==0)
    certificates=[]
    for x in [Q(0),Q(1,4),Q(1,2),Q(1),Q(3,2)]:
        certificate=lab.certified_evaluation(*p,x,last=18,outer_radius=max(1,2*x))
        more=lab.coupled_odd_derivatives(*p,last=36)
        for name,row in zip(("U","V"),more):
            refined=sum((c*x**(2*n+1) for n,c in enumerate(lab.ordinary_taylor_coefficients(row))),Q(0))
            lo,hi=certificate[name]
            check("certified_interval_contains_longer_partial",lo<=refined<=hi)
            check("positive_interval_width",hi-lo==certificate["tail_bound"])
        check("majorant_base_formula",lab.disk_majorant(*p,Q(1,2))==Q(2,3))
        certificates.append({key:([str(x) for x in value] if isinstance(value,tuple) else str(value))
                             for key,value in certificate.items()})
    # Independent sinh evaluation uses summation to a rational residual bound.
    for x in [Q(1,4),Q(1),Q(3,2)]:
        cert=lab.certified_evaluation(*([Q(1,2)]*4),x,last=20,outer_radius=2*x+1)
        terms=[x**(2*n+1)/Q(2**n*factorial(2*n+1)) for n in range(41)]
        remainder=terms[-1]*(x*x/Q(2*82*83))/(1-x*x/Q(2*82*83))
        independent=sum(terms,Q(0))
        check("independent_sinh_interval",cert["U"][0]<=independent and independent+remainder<=cert["U"][1])
    root=lab.pf_order(*p)
    check("numeric_PF_anchor",abs(root["rho"]-1)<1e-11,numeric)
    for c in [.2,.4,.5,.75,.9]:
        root=lab.pf_order(c,c,c,c)
        check("numeric_PF_scalar_root",abs(root["rho"]-log(2)/log(1/c))<1e-10,numeric)
    for p in [(Q(1,3),Q(2,3),Q(1,2),Q(3,4)),(Q(1,8),Q(1,4),Q(3,8),Q(1,2))]:
        root=lab.pf_order(*p)
        check("numeric_PF_residual",abs(root["spectral_residual"])<1e-11,numeric)
        check("numeric_PF_swap",abs(root["rho"]-lab.pf_order(p[3],p[2],p[1],p[0])["rho"])<1e-11,numeric)
    for bad in (-1,1.5,True):rejects("reject_bad_index",lambda:lab.coupled_odd_derivatives(1,1,1,1,bad))
    for bad in (0,1,-1,2):rejects("reject_noncontraction_certificate",lambda:lab.certified_evaluation(bad,.5,.5,.5,1))
    rejects("reject_bad_outer_radius",lambda:lab.certified_evaluation(.5,.5,.5,.5,1,outer_radius=1))
    rejects("reject_negative_evaluation",lambda:lab.certified_evaluation(.5,.5,.5,.5,-1))
    rejects("reject_majorant_resource_depth",lambda:lab.disk_majorant(.9,.9,.9,.9,10,max_steps=1))
    rejects("reject_majorant_resource_bits",lambda:lab.disk_majorant(.5,.5,.5,.5,2,max_bits=1))
    rejects("reject_nan_PF",lambda:lab.pf_order(float("nan"),.5,.5,.5))
    rejects("reject_zero_tolerance",lambda:lab.pf_order(.5,.5,.5,.5,tolerance=0))
    output={"checkpoint":"SF-DISCOVERY-110","status":"passed","python":platform.python_version(),
            "exact_assertions":sum(exact.values()),"numeric_assertions":sum(numeric.values()),
            "operational_guards":sum(guards.values()),"exact_categories":exact,
            "numeric_categories":numeric,"guard_categories":guards,
            "arithmetic":"fractions.Fraction except explicitly labelled PF root comparisons",
            "bounds":{"catalog_cases":7,"Picard_degree":21,"catalog_last_index":10,
                      "scalar_reduction_last_index":12,"sinh_last_index":20,
                      "phase_bases":[2,3,4,5,6],"tap_cases":2,
                      "certified_evaluation_last_index":18,"longer_partial_last_index":36},
            "independence":["dense ordinary Taylor Picard iteration", "sin/cos formal division",
                            "closed sinh derivative identity","direct convolution versus phase matrix",
                            "exact rational PF eigenvector at order one"],
            "nonclaims":["Finite computation does not prove the order/type theorem.",
                         "PF floating point brackets are not rigorous interval arithmetic.",
                         "The analytic tail certificate needs positive strict contractions.",
                         "No convergence claim for generic integer or signed catalog rows."],
            "samples":samples,"certificates":certificates,
            "input_sha256":{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                for name in ["coupled_lab.py","family_lab.py","checks/coupled_v11.py"]},
            "elapsed_seconds":time.monotonic()-start}
    target=ROOT/"evidence/v11";target.mkdir(parents=True,exist_ok=True)
    (target/"coupled_checks.json").write_text(json.dumps(output,indent=2)+"\n")
    lab.export_catalog(ROOT/"examples",10)
    print(json.dumps({k:output[k] for k in ["status","exact_assertions","numeric_assertions","operational_guards","elapsed_seconds"]}))


if __name__=="__main__":run()
