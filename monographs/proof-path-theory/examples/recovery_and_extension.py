"""Four inspectable outcomes from the finite APIs. No model or network calls."""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from proof_path_theory import (ClaimNode, NodeKind, Justification, ProofField,
    ProofFieldViews, factor_task, verify_factorization, solve_extension,
    verify_extension_result, analyze_semantic_cover, verify_semantic_cover)


def view(rules):
    return ProofFieldViews(ProofField(
        [ClaimNode(n,n,NodeKind.CLAIM) for n in 'abc'],
        [Justification(f'r{i}',p,c,'declared') for i,(p,c) in enumerate(rules)],
        premises=(),targets=('c',)))


def main():
    encoding={'archive0':'same','archive1':'same'}
    task={'archive0':'0','archive1':'1'}
    collision=factor_task(encoding,task)
    assert verify_factorization(encoding,task,collision)
    fine={'archive0':'first','archive1':'second'}
    decoder=factor_task(fine,task)
    assert verify_factorization(fine,task,decoder)
    field=view([(('a','b'),'c')])
    ext=solve_extension(field,positive=('a','b'),negative=('c',))
    assert verify_extension_result(field,positive=('a','b'),negative=('c',),result=ext)
    richer=view([(('a',),'b'),(('b',),'c'),(('a',),'c')])
    patches=[{'a','b'},{'b','c'}]
    cover=analyze_semantic_cover(richer,patches)
    assert verify_semantic_cover(richer,patches,cover)
    print(json.dumps({'collision':asdict(collision),'decoder':asdict(decoder),
        'extension_obstruction':asdict(ext),'semantic_cover':asdict(cover)},
        indent=2,default=lambda x:sorted(x) if isinstance(x,(set,frozenset)) else str(x)))

if __name__=='__main__':main()
