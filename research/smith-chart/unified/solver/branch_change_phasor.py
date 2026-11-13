"""Exact physical edge changes for finite positive-real controls.
Author: Komorebi P. The universal sensitivity argument is written separately.
"""
from fractions import Fraction as F
from exact_phasor import C
from phasor_unit_voltage import response


def thevenin(edges,s,all_nodes=()):
    nodes=set(all_nodes)|{0,1}|{a for _,a,_,_ in edges}|{b for _,_,b,_ in edges}
    port=max(nodes)+1;mapping={v:port if v==1 else v for v in nodes}
    moved=[(k,mapping[u],mapping[v],value) for k,u,v,value in edges]
    out=response(moved+[('R',1,port,F(1))],s,all_nodes=[mapping[v] for v in nodes])
    V={v:out['voltage'][mapping[v]] for v in nodes}
    return {'gamma':2*V[1]-1,'voltage':V,'current':out['current'][:-1],
            'input_current':1-V[1],'free_internal_variables':out['free_internal_variables']}


def open_branch(edges,j,s):
    nodes={0,1}|{a for _,a,_,_ in edges}|{b for _,_,b,_ in edges}
    return thevenin(edges[:j]+edges[j+1:],s,nodes)


def short_branch(edges,j,s):
    _,u,v,_=edges[j];nodes={0,1}|{a for _,a,_,_ in edges}|{b for _,_,b,_ in edges}
    parent={a:a for a in nodes}
    def find(a):
        while parent[a]!=a:a=parent[a]
        return a
    parent[find(v)]=find(u)
    if find(0)==find(1):
        return {'gamma':C(-1),'voltage':{a:C() for a in nodes},'input_current':C(1),
                'wire_current':C(1 if u==1 else -1 if u==0 else 0)}
    labels={find(0):0,find(1):1}
    for a in sorted(nodes):labels.setdefault(find(a),len(labels))
    mapping={a:labels[find(a)] for a in nodes}
    moved=[(k,mapping[a],mapping[b],value) for k0,(k,a,b,value) in enumerate(edges) if k0!=j]
    out=thevenin(moved,s,mapping.values());V={a:out['voltage'][mapping[a]] for a in nodes}
    other=[]
    for k0,(k,a,b,value) in enumerate(edges):
        if k0==j:continue
        y=1/F(value) if k=='R' else C.make(s)*value if k=='C' else 1/(C.make(s)*value)
        other.append((a,b,y*(V[a]-V[b])))
    injected=out['input_current'] if u==1 else -out['input_current'] if u==0 else C()
    wire=C() if u==v else injected-sum((i if a==u else -i if b==u else C() for a,b,i in other),C())
    return {'gamma':out['gamma'],'voltage':V,'input_current':out['input_current'],'wire_current':wire}
