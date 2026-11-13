"""Independent exact unit-voltage solver, permitting nonunique solutions.
Author: Komorebi P. No synthesis/certificate kernel algebra is used.
Free variables in compatible singular systems are set to zero.
"""
from fractions import Fraction as F
from exact_phasor import C


def solve_compatible(A,b):
    n=len(A)
    if not n:return [],0
    rows=[list(a)+[v] for a,v in zip(A,b)];pivots=[];r=0
    for col in range(n):
        pivot=next((k for k in range(r,n) if rows[k][col]),None)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r]
        value=rows[r][col];rows[r]=[x/value for x in rows[r]]
        for k in range(n):
            if k!=r:
                value=rows[k][col];rows[k]=[x-value*y for x,y in zip(rows[k],rows[r])]
        pivots.append(col);r+=1
    for row in rows:
        if not any(row[:n]) and row[n]:raise ValueError('No finite unit-voltage phasor solution')
    out=[C() for _ in range(n)]
    for k,col in enumerate(pivots):out[col]=rows[k][n]
    assert all(sum((x*y for x,y in zip(row,out)),C())==v for row,v in zip(A,b))
    return out,n-r


def response(edges,s,all_nodes=()):
    s=C.make(s)
    if not s:raise ValueError('Use contracted resistor solution at DC')
    nodes=sorted(set(all_nodes)|{0,1}|{u for _,u,_,_ in edges}|{v for _,_,v,_ in edges})
    internal=[v for v in nodes if v not in (0,1)];index={v:j for j,v in enumerate(internal)}
    A=[[C() for _ in internal] for _ in internal];rhs=[C() for _ in internal]
    adm=[]
    for kind,u,v,value in edges:
        value=F(value)
        if value<=0 or kind not in ('R','L','C'):raise ValueError('Positive ordinary physical branch required')
        y=C(1/value) if kind=='R' else 1/(s*value) if kind=='L' else s*value
        adm.append(y)
        if u==v:continue
        for a,b in ((u,v),(v,u)):
            if a in index:
                A[index[a]][index[a]]+=y
                if b in index:A[index[a]][index[b]]-=y
                elif b==1:rhs[index[a]]+=y
    solution,free=solve_compatible(A,rhs)
    voltage={0:C(),1:C(1),**{v:solution[j] for j,v in enumerate(internal)}}
    current=[y*(voltage[u]-voltage[v]) for y,(_,u,v,_) in zip(adm,edges)]
    Y=sum((i if u==1 else -i if v==1 else C() for (_,u,v,_),i in zip(edges,current)),C())
    for v in internal:
        assert sum((i if u==v else -i if w==v else C() for (_,u,w,_),i in zip(edges,current)),C())==C()
    return {'Y':Y,'voltage':voltage,'current':current,'free_internal_variables':free}


def dc_one_L(edges):
    inductors=[e for e in edges if e[0]=='L']
    if len(inductors)!=1:raise ValueError('Exactly one inductor required')
    _,u,v,L=inductors[0]
    nodes=sorted({0,1}|{a for _,a,_,_ in edges}|{b for _,_,b,_ in edges})
    parent={a:a for a in nodes}
    def find(a):
        while parent[a]!=a:a=parent[a]
        return a
    parent[find(v)]=find(u)
    if find(0)==find(1):raise ValueError('DC input short: finite Y0 hypothesis excluded')
    labels={find(0):0,find(1):1}
    for a in nodes:labels.setdefault(find(a),len(labels))
    mapping={a:labels[find(a)] for a in nodes}
    R=[('R',mapping[a],mapping[b],value) for k,a,b,value in edges if k=='R' and mapping[a]!=mapping[b]]
    dc=response(R,C(1),all_nodes=mapping.values())
    V={a:dc['voltage'][mapping[a]] for a in nodes};Y0=dc['Y']
    Rcurr=[(V[a]-V[b])/value if k=='R' else C() for k,a,b,value in edges]
    IL0=(Y0 if u==1 else -Y0 if u==0 else C())-sum((i if a==u else -i if b==u else C() for (_,a,b,_),i in zip(edges,Rcurr)),C())
    assert not Y0.im and not IL0.im and all(not z.im for z in V.values())
    return {'Y0':Y0.re,'voltage':V,'R_current':Rcurr,'IL0':IL0.re,'free_internal_variables':dc['free_internal_variables']}
