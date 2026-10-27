#!/usr/bin/env python3
"""Exhaust all compatible residual (3,5,unipotent) trace pairs over F49.

For A=[[0,-1],[1,-1]], trace B=beta, beta²+beta−1=0, and
trace AB=2, enumerate every determinant-one B. Partition by the exact
centralizer of A and verify each orbit representative generates PSL2(F49).
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from lastform_normalizer import ADD, NEG, MUL, INV, ID, norm, mult, inverse, power, digest


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    G=set()
    for a in range(1,49):
        for b in range(49):
            for c in range(49):
                d=MUL[INV[a]][ADD[1][MUL[b][c]]]
                G.add(norm((a,b,c,d)))
    for b in range(1,49):
        for d in range(49):G.add(norm((0,b,NEG[INV[b]],d)))
    assert len(G)==58800
    a=norm((0,NEG[1],1,NEG[1]))
    Z={g for g in G if mult(g,a)==mult(a,g)}
    assert len(Z)==24
    roots=[x for x in range(49) if ADD[MUL[x][x]][x]==1]
    assert roots==[24,31]
    records=[]
    for beta in roots:
        candidates=set(); lifted=[]
        # With actual trace(A)=-1, tr(AB)=x+y-z-beta=2.
        for x in range(49):
            for z in range(49):
                y=ADD[ADD[z][beta]][ADD[2][NEG[x]]]
                d=ADD[beta][NEG[x]]
                if ADD[MUL[x][d]][NEG[MUL[y][z]]]!=1:continue
                raw=(x,y,z,d); b=norm(raw)
                assert ADD[x][d]==beta
                assert ADD[ADD[x][y]][NEG[ADD[z][beta]]]==2
                assert power(b,5)==ID and b!=ID
                assert power(mult(a,b),7)==ID and mult(a,b)!=ID
                candidates.add(b); lifted.append(raw)
        assert len(candidates)==48 and len(lifted)==48
        remaining=set(candidates); orbits=[]
        while remaining:
            b=min(remaining)
            orbit={mult(mult(g,b),inverse(g)) for g in Z}
            assert len(orbit)==24 and orbit <= remaining
            remaining-=orbit
            subgroup={ID};queue=deque([ID])
            while queue:
                g=queue.popleft()
                for h in (a,b):
                    x=mult(g,h)
                    if x not in subgroup:subgroup.add(x);queue.append(x)
            assert subgroup==G
            orbits.append({'representative':b,'orbit_size':len(orbit),
                           'orbit':sorted(orbit),'generated_group_order':len(subgroup)})
        assert len(orbits)==2
        records.append({'beta':beta,'lifted_candidate_matrices':lifted,
                        'candidate_count':len(candidates),'centralizer_orbits':orbits})
    out={'status':'all_compatible_trace_pairs_generate_PSL2_F49',
         'field':'F7[s]/(s²−5), encoding a+7b for a+bs',
         'actual_order3_matrix':[0,6,1,6],
         'normalised_projective_order3_matrix':a,
         'centralizer_order':len(Z),'group_order':len(G),
         'group_sha256':digest(sorted(G)),'records':records,
         'total_compatible_pairs':sum(r['candidate_count'] for r in records),
         'generated_orbit_representatives':4,
         'non_claims':['Arithmetic cover equation and descent not computed',
                       'No rational-point or K-rational-point conclusion'],
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','total_compatible_pairs','generated_orbit_representatives','group_order')}))


if __name__=='__main__':main()
