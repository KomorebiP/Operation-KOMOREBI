#!/usr/bin/env python3
"""Separate arithmetic count driver. Imports only the hash-pinned independent core."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import independent_count68 as core

def main():
 p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--counts',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 d=json.loads(a.counts.read_text());spec=json.loads(a.spec.read_text());q=d['primes'][0]['q']
 assert q in spec['test_order'] and len(d['primes'])==1,'Undeclared count input'
 assert d['status']=='PASS_FINITE_COUNTS'
 core.PRIMES=(q,);sets,stats=core.count_audit(d)
 out={'schema':'beal.block69.independent_count.v1','status':'PASS_INDEPENDENT_COUNTS','primary_arithmetic_imports':False,'statistics':stats}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS_SEPARATE_COUNTS',q,flush=True)
if __name__=='__main__':main()
