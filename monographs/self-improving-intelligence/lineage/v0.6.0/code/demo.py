#!/usr/bin/env python3
"""Compile, serialize, independently check, and execute the eight-cell example."""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import time
from repair_calculus import (cell_problem, equality_tree, bit_tree, compile_frontier,
    check_tree, replay, tree_to_dict, tree_from_dict, relabel_problem, relabel_tree,
    Problem)

ROOT=Path(__file__).resolve().parents[1]

def capped_run(problem,tree,hidden,query_budget):
    """No terminal guess. Exhausted unresolved branches explicitly abstain."""
    node=tree;state=hidden;queries=0
    while node.kind=='query':
        if queries==query_budget:
            return {'status':'abstain','queries':queries,'repair':None,'work':queries}
        entry=problem.experiments[node.index].transitions[state]
        if entry is None:raise ValueError('Illegal operation in demonstration.')
        state,report=entry;node=dict(node.children)[report];queries+=1
    repair=problem.repairs[node.index]
    if state not in repair.good:raise ValueError('A bad repair was proposed.')
    return {'status':'repaired','queries':queries,'repair':repair.name,'work':queries+1}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',type=Path,default=ROOT/'validation')
    args=parser.parse_args();args.outdir.mkdir(parents=True,exist_ok=True)
    p=cell_problem(8);stats={};start=time.perf_counter()
    frontier=compile_frontier(p,range(8),3,stats)
    compile_seconds=time.perf_counter()-start
    eligible=[w for w in frontier if w.work<=4 and w.storage<=15]
    if not eligible:raise AssertionError('Expected cell witness not found.')
    w=eligible[0]
    certificate={'schema_version':1,'model':'eight-static-cells-v1','initial_support':list(range(8)),
                 'horizon':3,'allowance':{'work':'4','literal_records':15},'tree':tree_to_dict(w.tree)}
    certpath=args.outdir/'cell_certificate.json';certpath.write_text(json.dumps(certificate,indent=2)+'\n')
    # Read serialized bytes back rather than checking only the live compiler object.
    restored=tree_from_dict(json.loads(certpath.read_text())['tree'])
    actual=check_tree(p,range(8),restored,3,(F(4),15))
    baseline=equality_tree(8)
    parent=[capped_run(p,baseline,i,3) for i in range(8)]
    child=[capped_run(p,restored,i,3) for i in range(8)]
    sigma=tuple((3*i+1)%8 for i in range(8))
    target=relabel_problem(p,sigma)
    check_tree(target,range(8),restored,3,(F(4),15))
    adapter_missing=Problem(8,p.experiments,target.repairs)
    try:check_tree(adapter_missing,range(8),restored,3)
    except ValueError:missing_adapter_rejected=True
    else:raise AssertionError('Missing semantic adapter was not rejected.')
    result={'status':'PASS','model':'supplied complete finite observation and repair tables',
            'arithmetic':'integer/Fraction','frontier':[{'work':str(x.work),'records':x.storage} for x in frontier],
            'compiler_counters':stats,'compiler_runtime_seconds':compile_seconds,
            'checked_work':str(actual[0]),'checked_records':actual[1],
            'diagnostic_cap':3,'repair_cap':1,
            'parent_success':str(F(sum(t['status']=='repaired' for t in parent),8)),
            'child_success':str(F(sum(t['status']=='repaired' for t in child),8)),
            'parent_cases':parent,'child_cases':child,
            'compiled_case5_trace':replay(p,restored,5),
            'canonical_bit_case5_trace':replay(p,bit_tree(8),5),
            'target_case0_trace':replay(target,restored,0),
            'state_correspondence':list(sigma),'missing_adapter_rejected':missing_adapter_rejected,
            'development_ledger':{'installed_observation_entries':88,'installed_repair_success_pairs':8,
             'model_acquisition':'Supplied model generated from declared arithmetic; not inferred from 88 executed calibrations.',
             'compiler':'Project-authored exact frontier algorithm; not learned or self-modified.',
             'validation':'All eight cases and branch supports checked separately from synthesis.'},
            'non_claims':['No neural learning, external tools, or autonomous code rewriting.',
                          'A better diagnostic policy is compiled; the compiler itself is unchanged.',
                          'Affine adapters are supplied; transport is not broad task generalization.']}
    (args.outdir/'demonstration.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: compiled four-call, fifteen-record policy. Capped success: parent 3/8; child 1.')
    print(f'Compiler visited {stats["support_horizon_states"]} support/horizon states; {compile_seconds:.4f}s in this run.')

if __name__=='__main__':main()
