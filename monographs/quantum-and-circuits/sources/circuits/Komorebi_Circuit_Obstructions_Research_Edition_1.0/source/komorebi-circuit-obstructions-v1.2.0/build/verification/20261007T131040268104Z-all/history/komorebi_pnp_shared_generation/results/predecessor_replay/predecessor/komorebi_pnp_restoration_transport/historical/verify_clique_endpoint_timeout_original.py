#!/usr/bin/env python3
"""Exact controls for the binary-tree symmetry and majority-clique endpoint."""
from itertools import combinations
from math import comb
from pathlib import Path
import json
from verify_restoration_transport import degree

def graph(m,mask):
    a=[0]*m
    for k,(i,j) in enumerate(combinations(range(m),2)):
        if mask>>k&1:a[i]|=1<<j;a[j]|=1<<i
    return a

def omega(a):
    best=0
    def rec(cand,size):
        nonlocal best
        if size+cand.bit_count()<=best:return
        if not cand:best=max(best,size);return
        while cand:
            if size+cand.bit_count()<=best:return
            v=(cand&-cand).bit_length()-1;cand^=1<<v
            rec(cand&a[v],size+1)
        best=max(best,size)
    rec((1<<len(a))-1,0)
    return best

def generators(m):
    r=m.bit_length()-1
    for j in range(1,r+1):
        for b in range(0,m,1<<j):
            yield tuple((v^(1<<(j-1))) if b<=v<b+(1<<j) else v for v in range(m))

def level_graph(r,J):
    m=1<<r;a=[0]*m
    for i,j in combinations(range(m),2):
        level=(i^j).bit_length()-1
        if J>>level&1:a[i]|=1<<j;a[j]|=1<<i
    return a

def map_graph(a,p):
    b=[0]*len(a)
    for i in range(len(a)):
        for j in range(i+1,len(a)):
            if a[i]>>j&1:b[p[i]]|=1<<p[j];b[p[j]]|=1<<p[i]
    return b

def pad_clique(a,k):
    v=len(a);M=1
    while M<2*v:M*=2
    K=M//2+1;s=K-k;t=M-v-s
    assert s>=0 and t>=0
    out=[z for z in a]+[0]*(M-v)
    for i in range(v,v+s):
        for j in range(v+s):
            if i!=j:out[i]|=1<<j;out[j]|=1<<i
    return out,K,{'source_vertices':v,'target_vertices':M,'joined':s,'isolated':t}

def main():
    report={'status':'PASS','domain':'integer adjacency bitsets and GF(2) truth-table transform'}
    table=[];checks=0
    for m in (2,4):
        n=comb(m,2)
        all_omega=[omega(graph(m,x)) for x in range(1<<n)]
        for k in range(2,m+1):
            f=sum(int(w>=k)<<x for x,w in enumerate(all_omega))
            parity=f.bit_count()%2;d=degree(f,n)
            assert parity==1
            assert d==n
            table.append({'vertices':m,'k':k,'input_bits':n,'degree':d,'top_coefficient':parity})
            checks+=1<<n
    report['complete_small_truth_tables']={'cases':table,'graph_threshold_checks':checks}
    fixed=0;invariance=0;formula=0
    rows=[]
    for r in range(1,7):
        m=1<<r;gs=list(generators(m));maxcl=[]
        # Edge orbit characterization is checked by union-find under the generators.
        edges=list(combinations(range(m),2));index={e:i for i,e in enumerate(edges)}
        par=list(range(len(edges)))
        def root(x):
            while par[x]!=x:par[x]=par[par[x]];x=par[x]
            return x
        for p in gs:
            for idx,(u,v) in enumerate(edges):
                j=index[tuple(sorted((p[u],p[v])))];aa=root(idx);bb=root(j)
                if aa!=bb:par[bb]=aa
        groups={}
        for idx,(u,v) in enumerate(edges):groups.setdefault(root(idx),set()).add((u^v).bit_length()-1)
        assert len(groups)==r and all(len(v)==1 for v in groups.values())
        for J in range(1<<r):
            a=level_graph(r,J);w=omega(a);assert w==1<<J.bit_count();fixed+=1;maxcl.append(w)
            for p in gs:
                assert map_graph(a,p)==a;invariance+=1
        for k in range(2,m+1):
            q=(k-1).bit_length();parity=sum(w>=k for w in maxcl)%2
            assert parity==comb(r-1,q-1)%2;formula+=1
            if k>m//2: assert sum(w>=k for w in maxcl)==1
        rows.append({'vertices':m,'edge_orbits':r,'fixed_graphs':1<<r,
                     'majority_threshold':m//2+1,'input_bits':comb(m,2),
                     'passive_Toffoli_lower_bound':max(0,2*comb(m,2)-3),
                     'unrestricted_Toffoli_degree_lower_bound':comb(m,2)-1})
    report['tree_symmetry']={'fixed_graphs_tested':fixed,'generator_invariance_checks':invariance,
        'threshold_parity_checks':formula,'rows':rows}
    pads=0;largest=0
    for v in range(2,6):
        for x in range(1<<comb(v,2)):
            a=graph(v,x);w=omega(a)
            for k in range(2,v+1):
                out,K,meta=pad_clique(a,k)
                assert (omega(out)>=K)==(w>=k)
                pads+=1;largest=max(largest,len(out))
    report['padding_reduction']={'all_source_graphs_vertices':list(range(2,6)),
                                 'source_graph_threshold_pairs':pads,'largest_target_vertices':largest}
    out=Path(__file__).resolve().parents[1]/'results/clique_endpoint.json'
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
