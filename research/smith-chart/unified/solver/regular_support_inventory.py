"""All small active-support multigraph candidates; not a parameter search."""
from collections import Counter
from itertools import combinations,combinations_with_replacement,permutations
import json

def canonical(es,n):
    return min(tuple(sorted(tuple(sorted((p[u],p[v]))) for u,v in es))
        for tail in permutations(range(2,n)) for p in ((0,1)+tail,))

def components(es,n):
    parent=list(range(n))
    def find(v):
        while parent[v]!=v:v=parent[v]
        return v
    cycle=False
    for u,v in es:
        u,v=find(u),find(v)
        if u==v:cycle=True
        else:parent[v]=u
    groups={}
    for v in range(n):groups.setdefault(find(v),[]).append(v)
    return sorted(groups.values()),cycle

def inventory():
    seen={};labeled=Counter();raw=Counter()
    for m in range(1,5):
        for n in range(2,m+2):
            for es in combinations_with_replacement(tuple(combinations(range(n),2)),m):
                raw['all_edge_multisets']+=1
                degree=Counter(v for e in es for v in e)
                if degree[0]<1 or degree[1]<1 or any(degree[v]<2 for v in range(2,n)):continue
                groups,cycle=components(es,n)
                if not any(0 in g and 1 in g for g in groups):continue
                raw['degree_and_port_component_candidates']+=1
                if (0,1) in es:
                    raw['direct_port_edge_excluded_by_positive_endpoints']+=1
                    continue
                key=(m,n,canonical(es,n));labeled[str(m)]+=1
                if key in seen:continue
                es=key[2];groups,cycle=components(es,n)
                pairings=[]
                if n==4:
                    for partner in (2,3):
                        other=5-partner;parts=((0,partner),(1,other))
                        if all(not any(u in pair and v in pair for pair in parts) for u,v in es):pairings.append(parts)
                if not cycle:
                    assert len(groups)==1 and n==m+1
                    assert degree[0]==degree[1]==1 and all(degree[v]==2 for v in range(2,n))
                    kind='forest_port_path'
                elif m<4:
                    assert m==3 and n==3 and len(groups)==1 and sorted(Counter(es).values())==[1,2]
                    kind='three_edge_parallel_pair_and_tail'
                elif n<4:kind='too_few_active_vertices_for_two_disjoint_R_pairs'
                elif n==4:
                    assert len(groups)==1
                    kind='four_vertex_pairing_candidate' if pairings else 'no_two_equal_level_pair_partition'
                    if pairings:
                        assert len(pairings)==1 and sorted(Counter(es).values())==[1,1,2]
                else:
                    assert n==5 and len(groups)==2 and sorted(map(len,groups))==[2,3]
                    port=next(g for g in groups if 0 in g);closed=next(g for g in groups if 0 not in g)
                    assert 1 in port and len(port)==3
                    assert sum(u in port and v in port for u,v in es)==2
                    assert sum(u in closed and v in closed for u,v in es)==2
                    kind='disconnected_two_edge_port_path_and_parallel_cycle'
                seen[key]={'active_edges':m,'active_vertices':n,'edges':es,'components':groups,'cycle':cycle,'kind':kind,'possible_R_level_pairs':pairings}
    rows=[seen[k] for k in sorted(seen)]
    return {'status':'PASS','finite_assertion':'All loopless multigraph supports with1..4 edges,2..m+1 incident vertices, ports0/1 in one component, internal active degree>=2; direct port edges excluded separately by the written endpoint argument. Quotient only by internal-vertex relabeling.',
      'raw_counts':dict(raw),'labeled_retained_by_edge_count':dict(labeled),'unlabelled_port_fixed_types':len(rows),
      'type_counts':dict(Counter(r['kind'] for r in rows)),'types':rows,
      'non_claims':['No physical component values searched','KCL constraints are a covering overapproximation, not sufficiency','No full balanced margin or new formal coverage']}

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(inventory(),indent=2))
