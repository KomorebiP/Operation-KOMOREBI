#!/usr/bin/env python3
"""Exact point-count production driver. The copied Block68 primary core is hash-pinned."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import count68 as core

def main():
 p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--q',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 spec=json.loads(a.spec.read_text());assert a.q in spec['test_order'],'Test prime not declared'
 core.PRIMES=tuple(spec['test_order']);rec=core.run_prime(a.q)
 out={'schema':'beal.block69.count.v1','status':'PASS_FINITE_COUNTS','curve':'z^2=x^6+10Bx^3+12Ax+5B^2','coefficient_order':'ascending','primes':[rec]}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS_COUNTS',a.q,rec['admissible_pairs'],rec['degree_one_counts'],rec['degree_two_counts'],flush=True)
if __name__=='__main__':main()
