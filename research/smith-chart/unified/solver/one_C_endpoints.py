"""Exact endpoint controls for the written one-C bilinear inequality.
Author: Komorebi P. These resistor solves allow disconnected floating parts.
"""
from fractions import Fraction as F
from exact_phasor import C
from phasor_unit_voltage import response


def contracted(edges,short_kinds):
    nodes=sorted({0,1}|{u for _,u,v,x in edges}|{v for _,u,v,x in edges});parent={v:v for v in nodes}
    def find(v):
        while parent[v]!=v:v=parent[v]
        return v
    for k,u,v,x in edges:
        if k in short_kinds:parent[find(v)]=find(u)
    labels={find(0):0}
    if find(1)!=find(0):labels[find(1)]=1
    for v in nodes:labels.setdefault(find(v),max(labels.values())+1)
    mapping={v:labels[find(v)] for v in nodes}
    R=[('R',mapping[u],mapping[v],x) for k,u,v,x in edges if k=='R' and mapping[u]!=mapping[v]]
    return mapping,R


def unit_current_endpoint(edges,short_kinds):
    mapping,R=contracted(edges,short_kinds)
    if mapping[0]==mapping[1]:
        return {'Z':F(0),'voltage':{v:F(0) for v in mapping},'R_current':[F(0)]*len(edges),'mapping':mapping,'free':0}
    out=response(R,C(1),all_nodes=mapping.values());Y=out['Y']
    if not Y:raise ValueError('Open endpoint has no unit-current solution')
    assert not Y.im and Y.re>0
    V={v:out['voltage'][mapping[v]].re/Y.re for v in mapping}
    IR=[(V[u]-V[v])/x if k=='R' else F(0) for k,u,v,x in edges]
    return {'Z':1/Y.re,'voltage':V,'R_current':IR,'mapping':mapping,'free':out['free_internal_variables']}


def capacitor_current(edges,state,also_short_L=False):
    caps=[e for e in edges if e[0]=='C']
    if len(caps)!=1:raise ValueError('Exactly one capacitor required')
    _,u,v,x=caps[0]
    before,_=contracted(edges,{'L'} if also_short_L else set())
    a,b=before[u],before[v]
    if a==b:return F(0)
    source=int(before[1]==a)-int(before[0]==a)
    return source-sum(i*(int(before[r]==a)-int(before[t]==a)) for (k,r,t,x),i in zip(edges,state['R_current']) if k=='R')


def states(edges):
    if sum(k=='C' for k,u,v,x in edges)!=1:raise ValueError('Exactly one capacitor required')
    dc=unit_current_endpoint(edges,{'L'});inf=unit_current_endpoint(edges,{'C'});allshort=unit_current_endpoint(edges,{'L','C'})
    Ronly=response([e for e in edges if e[0]=='R'],C(1),all_nodes=dc['voltage'])
    return dc,inf,allshort,Ronly,capacitor_current(edges,inf),capacitor_current(edges,allshort,True)
