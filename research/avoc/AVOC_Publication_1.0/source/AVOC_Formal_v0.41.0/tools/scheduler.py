#!/usr/bin/env python3
"""Deterministic structural proof-DAG scheduler. A plan is NOT a proof certificate.
Input JSON: {"nodes": [...], "dependencies": {task: [prerequisite, ...]},
             "declared_completed": [...]}
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping
import argparse,json

@dataclass(frozen=True)
class ProofDAG:
    nodes: tuple[str,...]
    prerequisites: Mapping[str,frozenset[str]]

    @classmethod
    def create(cls,nodes: Iterable[str],dependencies: Mapping[str,Iterable[str]]) -> 'ProofDAG':
        ns=tuple(nodes)
        if any(not isinstance(n,str) or not n for n in ns):
            raise ValueError('Every task ID must be a nonempty string')
        if len(set(ns))!=len(ns):raise ValueError('Duplicate task IDs')
        if not set(dependencies).issubset(ns):raise ValueError('Unknown dependency-map task')
        direct={n:frozenset(dependencies.get(n,())) for n in ns}
        if any(not p.issubset(ns) for p in direct.values()):raise ValueError('Unknown prerequisite')
        visiting:set[str]=set();closure:dict[str,frozenset[str]]={}
        def visit(n:str)->frozenset[str]:
            if n in closure:return closure[n]
            if n in visiting:raise ValueError('Dependency cycle at '+n)
            visiting.add(n);deps:set[str]=set()
            for q in direct[n]:deps.add(q);deps.update(visit(q))
            visiting.remove(n);closure[n]=frozenset(deps);return closure[n]
        for n in ns:visit(n)
        return cls(tuple(sorted(ns)),closure)

    def validate_completed(self,completed: Iterable[str])->frozenset[str]:
        k=frozenset(completed)
        if not k.issubset(self.nodes):raise ValueError('Unknown completed task')
        if any(not self.prerequisites[n].issubset(k) for n in k):
            raise ValueError('Completed set is not dependency-closed')
        return k

    def frontier(self,completed: Iterable[str])->tuple[str,...]:
        k=self.validate_completed(completed)
        return tuple(n for n in self.nodes if n not in k and self.prerequisites[n].issubset(k))

    def plan(self,completed: Iterable[str]=(),workers:int=1)->tuple[tuple[str,...],...]:
        if isinstance(workers,bool) or not isinstance(workers,int) or workers<1:
            raise ValueError('workers must be a positive integer')
        k=set(self.validate_completed(completed));batches=[]
        while len(k)<len(self.nodes):
            batch=self.frontier(k)[:workers]
            if not batch:raise RuntimeError('No frontier in a validated finite DAG')
            batches.append(batch);k.update(batch)
        return tuple(batches)

    def validate_batch(self,completed: Iterable[str],batch:Iterable[str])->bool:
        items=tuple(batch)
        return len(items)==len(set(items)) and set(items).issubset(self.frontier(completed))

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('file',type=Path);p.add_argument('--workers',type=int,default=1)
    a=p.parse_args()
    try:
        d=json.loads(a.file.read_text());g=ProofDAG.create(d['nodes'],d.get('dependencies',{}))
        k=d.get('declared_completed',[])
        result={'frontier':g.frontier(k),'planned_batches':g.plan(k,a.workers),
                'scope':'Structural plan only. Actual admission requires independent proof certificates.',
                'optimality':'Deterministic lexical tie-break; no minimum-makespan claim.'}
        print(json.dumps(result,indent=2))
    except (ValueError,KeyError,TypeError,OSError) as e:p.exit(2,f'ERROR: {e}\n')
if __name__=='__main__':main()
