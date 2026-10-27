#!/usr/bin/env python3
"""Exact finite regression. Not a substitute for the generic Lean proofs.
Enumerates every forward-edge DAG on 0..5 nodes, deduplicating their transitive
closures. Checker uses independent Floyd-Warshall closure and bitset predicates.
"""
from pathlib import Path
import hashlib,itertools,json,sys,time
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from scheduler import ProofDAG
start=time.monotonic();stats={'dag_inputs':0,'distinct_dependency_orders':0,'ideal_states':0,'batch_contracts':0,'complete_permutations':0,'plans':0,'invalid_inputs_rejected':0}
for n in range(6):
    edges=list(itertools.combinations(range(n),2));seen=set();allbits=(1<<n)-1
    for mask in range(1<<len(edges)):
        stats['dag_inputs']+=1
        rel=[[False]*n for _ in range(n)];deps={str(i):[] for i in range(n)}
        for j,(a,b) in enumerate(edges):
            if mask>>j&1:rel[a][b]=True;deps[str(b)].append(str(a))
        for k in range(n):
            for i in range(n):
                for j in range(n):rel[i][j]=rel[i][j] or (rel[i][k] and rel[k][j])
        pred=tuple(sum(1<<j for j in range(n) if rel[j][i]) for i in range(n))
        if pred in seen:continue
        seen.add(pred);stats['distinct_dependency_orders']+=1
        g=ProofDAG.create(map(str,range(n)),deps)
        assert all(g.prerequisites[str(i)]==frozenset(str(j) for j in range(n) if pred[i]>>j&1) for i in range(n))
        def ideal(k):return all(not(k>>i&1) or pred[i]&~k==0 for i in range(n))
        def anti(b):return all(not(b>>i&1) or pred[i]&b==0 for i in range(n))
        for k in range(1<<n):
            if not ideal(k):continue
            stats['ideal_states']+=1
            fr=sum(1<<i for i in range(n) if not(k>>i&1) and pred[i]&~k==0)
            names=[str(i) for i in range(n) if k>>i&1]
            assert set(g.frontier(names))=={str(i) for i in range(n) if fr>>i&1}
            assert anti(fr) and (bool(fr)==(k!=allbits))
            for b in range(1<<n):
                stats['batch_contracts']+=1
                assert (b&~fr==0)==(k&b==0 and anti(b) and ideal(k|b))
            for w in (1,2,5):
                done=set(names);plan=g.plan(done,w);stats['plans']+=1
                for batch in plan:
                    assert len(batch)<=w and g.validate_batch(done,batch)
                    done.update(batch)
                assert done==set(g.nodes)
                assert sum(map(len,plan))==n-len(names)
        for perm in itertools.permutations(range(n)):
            stats['complete_permutations']+=1
            pos={x:i for i,x in enumerate(perm)}
            topo=all(not rel[a][b] or pos[a]<pos[b] for a in range(n) for b in range(n))
            done=0;legal=True
            for x in perm:
                if pred[x]&~done:legal=False
                done|=1<<x
            assert legal==topo
for nodes,deps in [(['a'],{'a':['a']}),(['a','b'],{'a':['b'],'b':['a']}),(['a'],{'a':['z']}),(['a','a'],{})]:
    try:ProofDAG.create(nodes,deps)
    except ValueError:stats['invalid_inputs_rejected']+=1
    else:raise AssertionError('Invalid graph accepted')
g=ProofDAG.create(['a','b'],{'b':['a']})
try:g.frontier(['b'])
except ValueError:stats['invalid_inputs_rejected']+=1
else:raise AssertionError('Nonideal completed set accepted')
assert not g.validate_batch([],['a','a'])
result={'status':'PASS','tested_range':'All forward-edge DAGs with fixed natural topological order on 0..5 vertices; duplicate transitive closures skipped','counts':stats,'seconds':round(time.monotonic()-start,3),'python':sys.version,'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),root/'tools/scheduler.py']},'boundary':'Finite implementation regression only; Python is not formally extracted from Lean.'}
(root/'results/v0.13.0/python_regression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
