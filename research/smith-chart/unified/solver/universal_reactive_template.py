"""Disjoint reactive edges plus open/wire resistor faces. Author: Komorebi P.

The graph lift is exact on a boundary face. Approximating opens/wires by finite
positive resistors is justified separately for positive-real Laplace samples.
"""
from itertools import combinations


def template(kinds):
    if any(k not in ('L','C') for k in kinds):raise ValueError('Reactive kind required')
    return tuple((k,2+2*j,3+2*j) for j,k in enumerate(kinds))


def lift(reactive):
    n=2+2*len(reactive);mapping=[0,1]
    for _,u,v in reactive:mapping.extend((u,v))
    anchors={}
    for copy,original in enumerate(mapping):anchors.setdefault(original,copy)
    wires=tuple((anchors[original],copy) for copy,original in enumerate(mapping) if anchors[original]!=copy)
    resistor_positions=tuple(tuple(sorted((anchors[u],anchors[v]))) for u,v in combinations(sorted(anchors),2))
    return {'reactive':template([k for k,_,_ in reactive]),'original_node_of_copy':tuple(mapping),
            'wires':wires,'resistor_positions':resistor_positions,
            'open_positions':tuple((u,v) for u,v in combinations(range(n),2)
                                  if (u,v) not in wires and (u,v) not in resistor_positions)}


def verify_lift(reactive):
    record=lift(reactive);mapping=record['original_node_of_copy'];parent=list(range(len(mapping)))
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for u,v in record['wires']:parent[find(v)]=find(u)
    assert all((find(i)==find(j))==(mapping[i]==mapping[j]) for i in range(len(mapping)) for j in range(len(mapping)))
    assert find(0)!=find(1)
    assert tuple((k,mapping[u],mapping[v]) for k,u,v in record['reactive'])==tuple(reactive)
    assert {tuple(sorted((mapping[u],mapping[v]))) for u,v in record['resistor_positions']}==set(combinations(sorted(set(mapping)),2))
    assert len(record['wires'])+len(record['resistor_positions'])+len(record['open_positions'])==len(mapping)*(len(mapping)-1)//2
    return record
