#!/usr/bin/env python3
"""Exact clique padding, monotone-ideal, and parity-packet controls."""
from pathlib import Path
from itertools import combinations,product
from math import comb,isqrt
import json,argparse
from verify_cut_comparison import immunity,degree

def adjacency(m,g):
    a=[0]*m
    for j,(u,v) in enumerate(combinations(range(m),2)):
        if g>>j&1:a[u]|=1<<v;a[v]|=1<<u
    return a

def clique_number(a):
    # Exact maximum clique via a branch-and-bound recurrence; no numeric relaxation.
    best=0
    def walk(cands,size):
        nonlocal best
        if size+cands.bit_count()<=best:return
        if not cands:best=max(best,size);return
        while cands:
            if size+cands.bit_count()<=best:return
            bit=cands&-cands;cands^=bit;v=bit.bit_length()-1
            walk(cands&a[v],size+1)
        best=max(best,size)
    walk((1<<len(a))-1,0)
    return best

def pad(a,k):
    v=len(a);s=4
    while s<v:s*=2
    M=s*s;K=M-s;added=K-k;b=s-v+k
    assert added>=0 and b>=0 and v+added+b==M
    ans=[0]*M
    core=(1<<(v+added))-1;new=core^((1<<v)-1)
    for i in range(v):ans[i]=a[i]|new
    for i in range(v,v+added):ans[i]=core^(1<<i)
    return ans,M,K,added,b

def parity(a):return a.bit_count()&1

def main(out):
    out.mkdir(exist_ok=True,parents=True)
    result={'status':'PASS','domain':'exact graph bitsets, F2 integers'}
    padding=0; structural=0; sizes={}
    for v in range(2,6):
        n=comb(v,2)
        for g in range(1<<n):
            src=adjacency(v,g);om=clique_number(src)
            for k in range(2,v+1):
                dst,M,K,a,b=pad(src,k)
                assert M>=16 and K>M//2
                target=clique_number(dst)
                assert (target>=K)==(om>=k)
                padding+=1;sizes[M]=sizes.get(M,0)+1
                assert target==max(a+om,1 if b else 0)
                assert all(not(dst[i]>>i&1) for i in range(M))
                structural+=1
    result['padding']={'source_graph_threshold_pairs':padding,'target_vertex_counts':sizes,'independent_target_maximum_clique_evaluations':padding,'source_vertices':'2 through 5; thresholds 2 through v','structural_checks':structural}
    rows=[]
    for r in range(2,8):
        M=4**r;s=isqrt(M);K=M-s;N=comb(M,2);q=comb(K,2)
        bound=2*q-3
        assert bound==2*N-2*M*s+M+s-3
        rows.append({'M':M,'K':K,'N':N,'alpha_1':q,'restored_Toffoli_lower_bound':bound,'degree_only_lower_bound':N-1,'ratio_numerator':bound,'ratio_denominator':N})
    result['all_size_formula_evaluations']=rows
    # Exact annihilator computations for every nontrivial threshold through four vertices.
    small=[]
    for m in range(2,5):
        N=comb(m,2);omegas=[clique_number(adjacency(m,g)) for g in range(1<<N)]
        for k in range(2,m+1):
            f=sum((z>=k)<<g for g,z in enumerate(omegas))
            a,h=immunity(f,N);assert a==comb(k,2)
            small.append({'m':m,'k':k,'N':N,'alpha_1':a,'degree':degree(f,N)})
    result['clique_ideal_small']=small
    # All 4-vertex triangle-incidence vectors, and an optimal three-parity cover.
    m=4;edges=list(combinations(range(m),2));triples=list(combinations(range(m),3));patterns=[]
    for g in range(1<<len(edges)):
        z=0
        for i,K in enumerate(triples):
            mask=sum(1<<edges.index(e) for e in combinations(K,2))
            if g&mask==mask:z|=1<<i
        patterns.append(z)
    seen=sorted(set(patterns));positive=[z for z in seen if z]
    assert len(seen)==12 and all(z.bit_count()!=3 for z in seen)
    rowsH=[0b0101,0b0110,0b1000]
    assert all(any(parity(z&r) for r in rowsH) for z in positive)
    two=0
    for a,b in product(range(16),repeat=2):
        assert any(parity(z&a)==parity(z&b)==0 for z in positive)
        two+=1
    result['parity_packets']={'graph_instances':64,'distinct_clique_incidence_vectors':len(seen),'three_row_cover':rowsH,'all_two_row_candidates_refuted':two,'conclusion':'minimum number of degree-three parity-of-triangle packets is three, for this finite function only'}
    # Independently check polynomial support property: no negative point receives a 1.
    packet_tables=[]
    for h in rowsH:
        table=sum(parity(h&z)<<g for g,z in enumerate(patterns))
        assert degree(table,6)==3
        packet_tables.append(table)
    target=sum(bool(z)<<g for g,z in enumerate(patterns))
    assert packet_tables[0]|packet_tables[1]|packet_tables[2]==target
    result['parity_packets']['full_truth_tables']=packet_tables
    (out/'clique_packets.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results');main(p.parse_args().out)
