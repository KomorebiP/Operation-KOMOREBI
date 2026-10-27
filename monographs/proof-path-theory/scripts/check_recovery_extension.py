"""Exhaustive finite checks against independently enumerated models and partitions.

Not a proof of Python for arbitrary inputs. No random sampling or model training.
"""
from __future__ import annotations
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from proof_path_theory import (ClaimNode, Justification, NodeKind, ProofField, ProofFieldViews,
    solve_extension, verify_extension_result, factor_task, verify_factorization,
    joint_task_scheme, compose_decoders, analyze_semantic_cover, verify_semantic_cover)


def check_all() -> dict:
    counts = {k:0 for k in ['rule_fields','protected_problems','feasible','infeasible',
        'semantic_covers','sufficient_covers','failed_covers','staged_closures','factorizations','decoder_compositions','joint_task_comparisons']}
    digest = hashlib.sha256()
    names = ('a','b','c')
    rule_spec = [(tuple(names[i] for i in range(j) if bits[i]), names[j])
                 for j in range(3) for bits in product((0,1),repeat=j)]
    subsets = [frozenset(names[i] for i in range(3) if mask>>i&1) for mask in range(8)]
    for rule_mask in range(1 << len(rule_spec)):
        chosen = [r for i,r in enumerate(rule_spec) if rule_mask>>i&1]
        rules = [Justification(f'r{i}',p,c,'declared') for i,(p,c) in enumerate(chosen)]
        for leaves in subsets:
            field=ProofField([ClaimNode(v,v,NodeKind.PREMISE if v in leaves else NodeKind.CLAIM) for v in names],rules,premises=leaves,targets=('c',))
            view=ProofFieldViews(field)
            # Independent truth-table semantics, without calling the local-model evaluator.
            models=[t for t in subsets if leaves<=t and all(not set(p)<=t or c in t for p,c in chosen)]
            counts['rule_fields']+=1
            closures={s:solve_extension(view,positive=s).closure for s in subsets}
            for patchmask in range(256):
                patches=[u for i,u in enumerate(subsets) if patchmask>>i&1]
                if frozenset().union(*patches)!=view.nodes:continue
                result=analyze_semantic_cover(view,patches)
                local_unions=[t for t in subsets if all(view.is_local_model(u,t & u) for u in patches)]
                expected=all(t in models for t in local_unions)
                assert result.sufficient==expected and verify_semantic_cover(view,patches,result)
                if not expected:assert result.countermodel in local_unions and result.countermodel not in models
                counts['semantic_covers']+=1
                counts['sufficient_covers' if expected else 'failed_covers']+=1
            for s in subsets:
                for n in subsets:
                    r=solve_extension(view,positive=s,negative=n)
                    expected=[t for t in models if s<=t and not (t & n)]
                    assert r.feasible==bool(expected)
                    assert verify_extension_result(view,positive=s,negative=n,result=r)
                    assert r.closure==closures[s]
                    if expected:
                        assert r.closure==frozenset.intersection(*expected)
                    counts['protected_problems']+=1
                    counts['feasible' if r.feasible else 'infeasible']+=1
                    digest.update(json.dumps([rule_mask,sorted(leaves),sorted(s),sorted(n),r.feasible,
                        sorted(r.closure),list(r.rule_ids)],separators=(',',':')).encode())
                for t in subsets:
                    assert solve_extension(view,positive=closures[s]|t).closure==closures[s|t]
                    counts['staged_closures']+=1
    for n in range(5):
        domain=tuple(f'p{i}' for i in range(n))
        encodings=[dict(zip(domain,x)) for x in product(('x','y','z'),repeat=n)]
        tasks=[dict(zip(domain,x)) for x in product(('0','1'),repeat=n)]
        for enc in encodings:
            for task in tasks:
                result=factor_task(enc,task)
                brute=all(enc[a]!=enc[b] or task[a]==task[b] for a in domain for b in domain)
                assert result.sufficient==brute and verify_factorization(enc,task,result)
                counts['factorizations']+=1
                for second in tasks:
                    joint=joint_task_scheme(domain,(task,second))
                    assert factor_task(enc,joint).sufficient==(result.sufficient and factor_task(enc,second).sufficient)
                    counts['joint_task_comparisons']+=1
        binary_schemes=tasks
        for fine in binary_schemes:
            for coarse in binary_schemes:
                bridge=factor_task(fine,coarse)
                for task in tasks:
                    outer=factor_task(coarse,task)
                    if bridge.sufficient and outer.sufficient:
                        composed=compose_decoders(outer.decoder,bridge.decoder)
                        assert all(composed.decode(fine[x])==task[x] for x in domain)
                        assert factor_task(fine,task).sufficient
                    counts['decoder_compositions']+=1
    return {'publication':'1.8.0','status':'PASS','counts':counts,
        'protected_result_digest':digest.hexdigest(),
        'scope':'All 3-node forward DAG rule subsets, all leaf/positive/negative sets and all node-covering patch families; archive functions on at most four named archives. Not empirical data or universal Python correctness.'}


def main() -> None:
    result=check_all()
    (ROOT/'data/recovery_extension_checks_1.8.0.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
