#!/usr/bin/env python3
"""Independent exact Python probe; NOT a Lean proof or release validation.

Grammar: false, true, x0,x1,x2, unary not and eager binary and/or/xor.
Cost: tree AST nodes; truth signatures use bit i for the i-th lexicographic input.
The source release remains unchanged. This proposes a finite certificate for a
future Lean structural-induction theorem about unrestricted-height optimality.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import operator
import platform
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROGRAM = tuple[Any, ...]
OPS = [('and', operator.and_), ('or', operator.or_), ('xor', operator.xor)]
SEEDS = [(0, ('lit', False)), (255, ('lit', True)), (240, ('var', 0)),
         (204, ('var', 1)), (170, ('var', 2))]

def size(p: PROGRAM | list) -> int:
    if p[0] in ('lit','var'): return 1
    if p[0] == 'not': return 1 + size(p[1])
    if p[0] in ('and','or','xor'): return 1 + size(p[1]) + size(p[2])
    raise ValueError('Unknown constructor')

def run(p: PROGRAM | list, x: tuple[bool,bool,bool]) -> bool:
    tag=p[0]
    if tag=='lit': return bool(p[1])
    if tag=='var': return x[p[1]]
    if tag=='not': return not run(p[1],x)
    a,b=run(p[1],x),run(p[2],x)
    if tag=='and': return a and b
    if tag=='or': return a or b
    if tag=='xor': return a!=b
    raise ValueError('Unknown constructor')

def expand(old: dict[int,tuple[int,PROGRAM]]) -> dict[int,tuple[int,PROGRAM]]:
    new=dict(old)
    def insert(mask:int,cost:int,p:PROGRAM)->None:
        if mask not in new or cost < new[mask][0]: new[mask]=(cost,p)
    for m,(c,p) in old.items(): insert(255^m,c+1,('not',p))
    for tag,op in OPS:
        for a,(ca,pa) in old.items():
            for b,(cb,pb) in old.items(): insert(op(a,b),ca+cb+1,(tag,pa,pb))
    return new

def costs(bank): return {m:c for m,(c,_) in bank.items()}

def validate(cert: dict[str,Any]) -> dict[str,int]:
    """No generator calls. Check realizability, all masks, and all cost inequalities."""
    entries=cert['entries']
    if len(entries)!=256: raise ValueError('Certificate must contain exactly 256 entries')
    table={e['signature']:e for e in entries}
    if set(table)!=set(range(256)): raise ValueError('Missing or duplicated signature')
    c={m:e['node_count'] for m,e in table.items()}
    if any(type(v) is not int or v<1 for v in c.values()): raise ValueError('Invalid node cost')
    truth_checks=0
    for m,e in table.items():
        if size(e['program'])!=c[m]: raise ValueError('Incorrect AST node count')
        for i,x in enumerate(itertools.product([False,True],repeat=3)):
            if run(e['program'],x)!=bool(m & (1<<i)): raise ValueError('Incorrect signature')
            truth_checks+=1
    inequality_checks=0
    for m,_ in SEEDS:
        if c[m]>1: raise ValueError('Primitive lower-bound condition failed')
        inequality_checks+=1
    for a in range(256):
        if c[255^a]>1+c[a]: raise ValueError('Negation closure failed')
        inequality_checks+=1
    for tag,op in OPS:
        for a in range(256):
            for b in range(256):
                if c[op(a,b)]>1+c[a]+c[b]: raise ValueError(f'{tag} cost closure failed')
                inequality_checks+=1
    return {'ast_node_checks':256,'truth_value_checks':truth_checks,
            'primitive_and_constructor_inequalities':inequality_checks}

def size_ordered_oracle(max_nodes:int) -> dict[int,int]:
    """Independent cost-layer enumeration rather than height-layer relaxation."""
    seen={m:1 for m,_ in SEEDS}; levels={1:set(seen)}
    for n in range(2,max_nodes+1):
        generated={255^a for a in levels.get(n-1,set())}
        for left_size in range(1,n-1):
            right_size=n-1-left_size
            for a in levels.get(left_size,set()):
                for b in levels.get(right_size,set()):
                    generated.update((a & b,a | b,a ^ b))
        levels[n]=generated-set(seen)
        for m in levels[n]: seen[m]=n
    return seen

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',type=Path,default=Path('probe_output'))
    ap.add_argument('--max-depth',type=int,default=8)
    args=ap.parse_args()
    if not 1<=args.max_depth<=12: ap.error('max-depth must be between 1 and 12')
    out=args.output_dir; out.mkdir(parents=True,exist_ok=True)
    source=Path(__file__).resolve(); before=hashlib.sha256(source.read_bytes()).hexdigest()
    started=datetime.now(timezone.utc).isoformat(); t=time.perf_counter()
    bank={m:(1,p) for m,p in SEEDS}; rows=[]; stable_depth=None
    for depth in range(args.max_depth+1):
        previous=bank
        if depth: bank=expand(previous)
        same=bool(depth and costs(previous)==costs(bank))
        rows.append({'depth':depth,'behaviors':len(bank),'sum_retained_costs':sum(costs(bank).values()),
                     'max_retained_cost':max(costs(bank).values()),
                     'old_behaviors_improved':sum(m in previous and c<previous[m][0] for m,(c,_) in bank.items()) if depth else 0,
                     'same_cost_map_as_previous':same})
        if same: stable_depth=depth-1; break
    if stable_depth is None or len(bank)!=256:
        raise RuntimeError('No complete cost-stable table within the declared resource cap')
    cert={'grammar':'Bool3-not-and-or-xor-tree-nodes','input_order':'lexicographic false-first; signature bit i is input i',
          'status':'PYTHON_CHECKED_CANDIDATE_CERTIFICATE_NOT_LEAN_VERIFIED',
          'entries':[{'signature':m,'node_count':c,'program':p} for m,(c,p) in sorted(bank.items())]}
    checks=validate(cert)
    oracle=size_ordered_oracle(max(costs(bank).values()))
    if oracle!=costs(bank): raise RuntimeError('Independent size-order oracle disagrees')
    # Positive obstruction tests: recompute content, do not rely on a failing proof script.
    negatives=[]
    for name in ['missing_entry','false_signature','worse_valid_representative']:
        bad=json.loads(json.dumps(cert))
        if name=='missing_entry': bad['entries'].pop()
        elif name=='false_signature': bad['entries'][0]['program']=['lit',True]
        else:
            e=bad['entries'][1]; e['program']=['not',['not',e['program']]]; e['node_count']+=2
        try: validate(bad)
        except ValueError as exc: negatives.append({'case':name,'rejected':True,'reason':str(exc)})
        else: raise RuntimeError('Bad certificate unexpectedly accepted: '+name)
    after=hashlib.sha256(source.read_bytes()).hexdigest(); assert before==after
    cert_path=out/'candidate_global_cost_certificate.json'
    cert_path.write_text(json.dumps(cert,indent=2)+'\n')
    summary={'status':'INDEPENDENT_EXACT_PYTHON_PROBE_PASS_NOT_LEAN_CHECKED',
             'layers':rows,'candidate_cost_fixed_point_depth':stable_depth,
             'certificate_checks':checks,'oracle':'independent exact node-size layering',
             'oracle_complete':len(oracle)==256,'oracle_equal_costs':True,
             'cost_histogram':dict(sorted(Counter(costs(bank).values()).items())),
             'negative_certificate_cases':negatives,
             'source_sha256_before':before,'source_sha256_after':after,
             'started_at_utc':started,'runtime_seconds':time.perf_counter()-t,
             'python':sys.version,'platform':platform.platform(),'randomness':False,
             'not_claimed':['No Lean theorem was compiled in this task.',
               'This script is not formally refined to the AVOC Lean implementation.',
               'No speedup, empirical LLM result, grammar-independent optimum or general recursive improvement.'],
             'interpretation':'The finite table has realized witnesses and passes all constructor-cost closure inequalities. A separate structural-induction soundness theorem can promote these checks into a grammar-wide optimality certificate; that Lean theorem is proposed in FOLLOW_UP_ROADMAP.md.'}
    (out/'closure_probe_results.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
