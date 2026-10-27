#!/usr/bin/env python3
"""Finite direct-product check of the KR 2008 half-binomial formula."""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
from fractions import Fraction as F
from pathlib import Path


def choose_half(top:F,j:int)->F:
    value=F(1)
    for i in range(j):
        value*=F(top-i,i+1)
    return value


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location("independent",Path("computations/independent_audit_final.py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    u,_=module.recurrence(50)
    rows=[]
    terms=0
    for n in range(51):
        value=F(0)
        for j in range(n+1):
            left=choose_half(F(2*n-1,2),j)
            right=choose_half(F(2*n+2*j-1,2),j)
            assert (4**j*left).denominator==1
            assert (4**j*right).denominator==1
            term=math.comb(n,j)*left*right
            assert (16**n*term).denominator==1
            value+=term
            terms+=1
        assert value==u[n]
        assert (16**n*value).denominator==1
        rows.append({"n":n,"u_direct":str(value),"T_direct":str(16**n*value),"recurrence_equal":True})
    result={"scope":"finite normalization translation check, n=0..50; direct computation does not prove the identity for all n","source_formula_label":"Krattenthaler-Rivoal 2008, arXiv:0810.1927, Lemma 3, equation (3.1), authenticated by the separate literature audit","formula":"u_n=sum_(j=0)^n binom(n,j)binom(n-1/2,j)binom(n+j-1/2,j)","arithmetic":"exact fractions.Fraction products and integers","n_min":0,"n_max":50,"number_of_summands":terms,"half_binomial_4_power_denominator_checks":True,"scaled_term_16_power_integrality_checks":True,"all_recurrence_matches":True,"rows":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},indent=2))


if __name__=="__main__":
    main()
