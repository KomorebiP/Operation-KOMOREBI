#!/usr/bin/env python3
"""Untrusted deterministic candidate producer. The separate Lean importer decides validity."""
from __future__ import annotations
import argparse
import json
import operator
from pathlib import Path


def produce(depth: int = 3) -> tuple[list, list]:
    bank = {0:(1,["literal",False]),255:(1,["literal",True]),
            240:(1,["variable",0]),204:(1,["variable",1]),170:(1,["variable",2])}
    layers = []
    for d in range(depth + 1):
        if d:
            old = bank
            bank = dict(old)
            def insert(mask, cost, expr):
                if mask not in bank or cost < bank[mask][0]:
                    bank[mask] = (cost, expr)
            for a,(ca,pa) in old.items():
                insert(255 ^ a, ca+1, ["not",pa])
            for name,op in [("and",operator.and_),("or",operator.or_),("xor",operator.xor)]:
                for a,(ca,pa) in old.items():
                    for b,(cb,pb) in old.items():
                        insert(op(a,b),ca+cb+1,[name,pa,pb])
        layers.append({"depth":d,"behaviors":len(bank),"sum_cost":sum(c for c,_ in bank.values())})
    if set(bank) != set(range(256)):
        raise ValueError("incomplete bank at requested production depth")
    rows = [[[bool(mask & (1<<i)) for i in range(8)],cost,p] for mask,(cost,p) in sorted(bank.items())]
    cert = ["avoc-global-cost-library-v1","bool3-not-and-or-xor-v1",
            "lexicographic-false-first-bit0","eager-tree-nodes-v1",rows]
    return cert,layers


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output",type=Path)
    ap.add_argument("--depth",type=int,default=3)
    args=ap.parse_args()
    if not 3 <= args.depth <= 4: ap.error("production depth must be 3 or 4")
    cert,layers=produce(args.depth)
    with args.output.open("x",encoding="utf-8") as f:
        json.dump(cert,f,separators=(",",":"));f.write("\n")
    print(json.dumps({"status":"UNTRUSTED_CANDIDATE_REQUIRES_LEAN_IMPORT","layers":layers},indent=2))

if __name__=="__main__": main()
