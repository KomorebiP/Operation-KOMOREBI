#!/usr/bin/env python3
"""Direct exact witness for the full-scan maximum and precision branch audit."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def integer_T(max_k: int) -> list[int]:
    values = [1,28]
    for k in range(2,max_k+1):
        j=k-1
        pp=20*j*j-8*j+1
        pn=20*k*k-8*k+1
        mid=3520*j**6+5632*j**5+2064*j**4-384*j**3-156*j*j+16*j+7
        num=16*mid*values[-1]+256*(2*k-3)**2*(2*k-2)**2*pn*values[-2]
        den=(2*k-1)**2*(2*k)**2*pp
        value,rem=divmod(num,den)
        assert rem==0
        values.append(value)
    return values[:max_k+1]


def valuation(value: int) -> int:
    assert value>0
    return (value & -value).bit_length()-1


def direct_sum(n: int,m: int,values:list[int]) -> int:
    # Multiplicative binomial coefficients, independent of math.comb/Pascal rows.
    coefficient=1
    total=values[n]
    for i in range(1,m+1):
        coefficient=coefficient*(m-i+1)//i
        total+=coefficient*values[n+i]
    return total


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location("old",Path("computations/catalan_packet_audit.py"))
    old=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    pairs=[(1466,2113),(1465,2113),(1467,2113),(1466,2112),(1466,2114)]
    T=integer_T(max(n+m for n,m in pairs))
    assert T[:501]==old.t_sequence(500)
    witness=[]
    for n,m in pairs:
        value=direct_sum(n,m,T)
        hex_value=hex(value)
        record={"n":n,"m":m,"v2":valuation(value),"bit_length":value.bit_length(),"lowest_64_bits":value % (1 << 64),"sum_hex_sha256":hashlib.sha256(hex_value.encode()).hexdigest()}
        (args.output_dir/f"S_{n}_{m}.hex.txt").write_text(hex_value+"\n")
        witness.append(record)
    assert witness[0]["v2"]==31
    small=old.scan_binomial_v2(3,4)
    exact=[valuation(direct_sum(n,m,T)) for n in range(1,4) for m in range(4*n+1)]
    assert small["pairs_scanned"]==len(exact)==27
    assert small["unresolved_residues"]==sum(x>=4 for x in exact)==8
    assert small["exact_below_precision"] is False
    result={"scope":"five direct positive-integer witnesses; precision-ceiling diagnostic; no global maximum established by these five witnesses","integer_recurrence_max_index":len(T)-1,"division_remainders_zero":True,"witnesses":witness,"precision_ceiling":{"historical_scan":small,"direct_exact_maximum":max(exact),"direct_number_at_or_above_ceiling":sum(x>=4 for x in exact),"classification_passed":True,"interpretation":"reported maximum_v2=4 is the ceiling lower bound for unresolved residues; the flag correctly withholds exactness"}}
    (args.output_dir/"results.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
