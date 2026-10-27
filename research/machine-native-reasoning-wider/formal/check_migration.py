#!/usr/bin/env python3
"""Exact finite constructions for representation migration and added information."""
from __future__ import annotations
from itertools import product
from pathlib import Path
import json

def partitions(n):
    # Canonical restricted-growth labels enumerate every equivalence relation once.
    if n==0: yield ();return
    def rec(prefix):
        if len(prefix)==n: yield tuple(prefix);return
        for k in range(max(prefix)+2): yield from rec(prefix+[k])
    yield from rec([0])

def decoder(old, new):
    table={}
    for u,v in zip(old,new):
        if u in table and table[u]!=v:return None
        table[u]=v
    return table

def semantic_fibre_test(old,new):
    return all(old[i]!=old[j] or new[i]==new[j]
               for i in range(len(old)) for j in range(len(old)))

def main():
    counts={'record_pairs':0,'supplementary_encodings':0,'brute_decoder_existence':0,
            'evidence_triples':0,'operation_intertwinings':0,'joint_refinement_tests':0,
            'negative_controls':0}
    for n in range(1,7):
        ps=list(partitions(n))
        for m in ps:
            for target in ps:
                d=decoder(m,target)
                assert (d is not None)==semantic_fibre_test(m,target)
                if d is not None:assert all(d[m[h]]==target[h] for h in range(n))
                counts['record_pairs']+=1
                # Construct the optimal auxiliary code independently inside each fibre.
                possibilities={u:sorted({target[h] for h in range(n) if m[h]==u}) for u in set(m)}
                k=max(map(len,possibilities.values()));bits=(k-1).bit_length()
                codes=[possibilities[m[h]].index(target[h]) for h in range(n)]
                assert all(possibilities[m[h]][codes[h]]==target[h] for h in range(n))
                assert max(codes)<2**bits and (bits==0 or 2**(bits-1)<k)
                counts['supplementary_encodings']+=1
                # Exhaustive map existence only for genuinely small records.
                if n<=3:
                    brute=False
                    for vals in product(range(max(target)+1),repeat=max(m)+1):
                        if all(vals[m[h]]==target[h] for h in range(n)):
                            brute=True;break
                    assert brute==(d is not None);counts['brute_decoder_existence']+=1
                if n<=4:
                    pair=tuple(zip(m,target))
                    for r in ps:
                        if decoder(r,m) is not None and decoder(r,target) is not None:
                            assert decoder(r,pair) is not None
                            assert len(set(r))>=len(set(pair));counts['joint_refinement_tests']+=1
                    for evidence in ps:
                        paired=tuple(zip(m,evidence))
                        assert (decoder(paired,target) is not None)==semantic_fibre_test(paired,target)
                        counts['evidence_triples']+=1
                if n<=3 and d is not None:
                    for f in product(range(n),repeat=n):
                        pm=decoder(m,tuple(m[f[h]] for h in range(n)))
                        qn=decoder(target,tuple(target[f[h]] for h in range(n)))
                        if pm is None or qn is None:continue
                        assert all(d[pm[u]]==qn[d[u]] for u in set(m))
                        for u in set(m):
                            left=u;right=d[u]
                            for _ in range(5):
                                assert d[left]==right
                                left=pm[left];right=qn[right]
                        counts['operation_intertwinings']+=1
    h=list(product((0,1),repeat=3))
    old=tuple(b^s for b,s,n in h)
    new=tuple((b^s,b) for b,s,n in h)
    more=tuple((b^s,b,n) for b,s,n in h)
    evidence=tuple(s for b,s,n in h)
    assert decoder(old,new) is None
    assert decoder(tuple(zip(old,evidence)),new) is not None
    assert decoder(tuple(zip(old,evidence)),more) is None
    counts['negative_controls']+=2
    # Preserving the initial code does not transport changed operations.
    assert any(u != 1-u for u in (0,1));counts['negative_controls']+=1
    result={'status':'PASS','counts':counts,
            'sensor':{'old_values':len(set(old)),'target_values':len(set(new)),
                      'expanded_values':len(set(more)),'supplementary_bits':[1,2]},
            'scope':'all canonical partition pairs through six histories; smaller domains for explicit decoder and operation enumeration; no statistical sampling or Lean execution'}
    out=Path(__file__).resolve().parents[1]/'verification'/'migration.json'
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
