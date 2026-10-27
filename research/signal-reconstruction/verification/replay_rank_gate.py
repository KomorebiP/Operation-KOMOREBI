#!/usr/bin/env python3
"""A bounded witness separating largest-ratio selection from a threshold gate."""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from replay_scoped import G, Checks, clean, load


def multiply(a,b):
    return [[sum((a[r][k]*b[k][s] for k in range(len(b))),G(F(0)))
             for s in range(len(b[0]))] for r in range(len(a))]


def transpose(a,conjugate=False):
    return [[a[r][s].conjugate() if conjugate else a[r][s]
             for r in range(len(a))] for s in range(len(a[0]))]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--result",type=Path,required=True)
    args=parser.parse_args()
    c=Checks()
    try:
        import numpy as np
        roots=[G(F(1)),G(F(0),F(1)),G(F(-1)),G(F(0),F(-1))]
        weights=[F(100),F(-99),F(-1),F(0)]
        noise=F(1,10)
        n0=4
        true=[sum((a*z**n for a,z in zip(weights,roots)),G(F(0))) for n in range(n0,n0+16)]
        noisy=[value+noise*roots[-1]**n for n,value in zip(range(n0,n0+16),true)]
        H=[[true[r+s] for s in range(4)] for r in range(4)]
        Hn=[[noisy[r+s] for s in range(4)] for r in range(4)]
        V=[[z**r for z in roots] for r in range(4)]
        U=[[v/F(2) for v in row] for row in V]
        c.check("exact Q(i) unitary Fourier basis",multiply(transpose(U,True),U)==
                [[G(F(int(r==s))) for s in range(4)] for r in range(4)])
        diagonal=[[G(F(4)*a if r==s else F(0)) for s,a in enumerate(weights)] for r in range(4)]
        converted=multiply(multiply(transpose(U,True),H),[[v.conjugate() for v in row] for row in U])
        c.check("exact Q(i) Hankel diagonal factorization",converted==diagonal)
        c.check("exact true smallest active singular value",abs(diagonal[2][2].re)==4)
        expected_noisy=[F(400),F(-396),F(-4),F(2,5)]
        diagonal_noisy=[[G(value if r==s else F(0)) for s,value in enumerate(expected_noisy)] for r in range(4)]
        converted_noisy=multiply(multiply(transpose(U,True),Hn),[[v.conjugate() for v in row] for row in U])
        c.check("exact Q(i) noisy Hankel diagonal factorization",converted_noisy==diagonal_noisy)
        c.check("noise below half smallest active singular value",F(2,5)<F(4,2))
        ratios=[F(400,396),F(396,4),F(4)/F(2,5)]
        c.check("exact largest ratio selects rank two",max(range(3),key=lambda k:ratios[k])+1==2,ratios)
        threshold=F(2)
        c.check("exact supplied threshold lies in Weyl gap",F(2,5)<threshold<F(4)-F(2,5))
        c.check("exact supplied threshold selects rank three",sum(abs(s)>threshold for s in expected_noisy)==3)
        numerical=np.array([[complex(v) for v in row] for row in Hn])
        singular=np.linalg.svd(numerical,compute_uv=False)
        c.check("independent numerical SVD matches exact singular spectrum",
                np.max(np.abs(singular-np.array([400.,396.,4.,.4])))<1e-10,singular)
        c.check("numerical H4 largest ratio selects rank two",int(np.argmax(singular[:-1]/singular[1:])+1)==2)
        c.check("numerical supplied threshold selects rank three",int(np.sum(singular>2))==3)
        native=load("signal_native_rank_heuristic","sources/self_calibration/polyphase_gibbs_breakthrough.py")
        order,native_singular,native_ratios=native.estimate_model_order(np.array([complex(v) for v in noisy]),3)
        c.check("native rectangular largest-ratio heuristic selects rank two",order==2,
                {"order":order,"singular":native_singular,"ratios":native_ratios})
        record={"status":"PASS","suite":"rank_ratio_boundary","fresh_explicit_check_count":len(c.rows),"checks":c.rows,
                "scientific_details":{"true_order":3,"native_inferred_order":order,"square_H4_threshold_inferred_order":3,
                "n0":n0,"nodes":roots,"amplitudes":weights[:3],"noise_amplitude":noise,
                "exact_singular_true":[400,396,4,0],"exact_singular_noisy":[400,396,4,"2/5"],
                "exact_noise_operator_norm":"2/5","supplied_threshold":threshold,
                "threshold_scope":"Known error and true active singular-value bounds; not recovered automatically from the largest-ratio heuristic"},
                "interpretation":"source order heuristic fails on this bounded valid perturbation despite threshold theorem hypotheses; no heuristic repair is claimed"}
    except Exception as error:
        record={"status":"FAIL","checks":c.rows,"failure":{"type":type(error).__name__,"message":str(error)}}
        args.result.write_text(json.dumps(clean(record),indent=2,allow_nan=False)+"\n")
        raise
    args.result.write_text(json.dumps(clean(record),indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":record["status"],"checks":len(c.rows)}))

if __name__=="__main__":main()
