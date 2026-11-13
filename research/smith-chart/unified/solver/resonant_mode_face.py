"""Exact mode certificates for the separately written balanced-face theorem.
Author: Komorebi P. Rational consumer; the written theorem allows real values.
"""
from fractions import Fraction as F
from collections import Counter,defaultdict
import hashlib,json
from pure_type_margins import gamma


def rational(x):
    if isinstance(x,bool) or not isinstance(x,(int,str,F)):raise ValueError('Exact rational data required')
    return F(x)


def checked_edges(edges):
    out=[]
    if not edges or len(edges)>4096:raise ValueError('Consumer edge cap is1..4096')
    for row in edges:
        if len(row)!=4:raise ValueError('Four entries per branch required')
        k,u,v,x=row
        if k not in ('R','L','C') or type(u)!=int or type(v)!=int or min(u,v)<0:raise ValueError('Ordinary labelled RLC branches required')
        x=rational(x)
        if x<=0:raise ValueError('Positive values required')
        if u==v:raise ValueError('Remove self-loops before supplying certificate indices')
        out.append((k,u,v,x))
    if len({u for k,u,v,x in out}|{v for k,u,v,x in out}|{0,1})>256:raise ValueError('Consumer vertex cap exceeded')
    if sum(k=='L' for k,u,v,x in out)>2 or sum(k=='C' for k,u,v,x in out)>2:raise ValueError('At most two L and two C required')
    return out


def port_component(edges):
    reached={1}
    while True:
        more=reached|{v for k,u,v,x in edges if u in reached}|{u for k,u,v,x in edges if v in reached}
        if more==reached:break
        reached=more
    return [e for e in edges if e[1] in reached and e[2] in reached],reached


def normalized_mode(edges,mode):
    nodes={0,1}|{u for k,u,v,x in edges}|{v for k,u,v,x in edges}
    if not isinstance(mode,dict) or any(type(k)!=int and (not isinstance(k,str) or not k.isdigit() or str(int(k))!=k) for k in mode):raise ValueError('Canonical integer node labels required')
    if len({int(k) for k in mode})!=len(mode):raise ValueError('Duplicate mode node label')
    mode={int(k):rational(v) for k,v in mode.items()}
    if set(mode)!=nodes or mode[0] or mode[1] or not any(mode.values()):raise ValueError('Nonzero mode on all nodes, zero at both ports, required')
    scale=next(mode[v] for v in sorted(nodes) if mode[v]);w={v:mode[v]/scale for v in nodes}
    div={v:F(0) for v in nodes}
    for k,u,v,x in edges:
        d=w[u]-w[v]
        if k=='R':
            if d:raise ValueError('Resistor drop is nonzero in proposed mode')
        else:
            flow=(x if k=='C' else -1/x)*d;div[u]+=flow;div[v]-=flow
    if any(div.values()):raise ValueError('Reactive mode fails KCL, including a port')
    return w


def nullspace(A,n):
    rows=[list(row) for row in A];pivots=[];r=0
    for col in range(n):
        pivot=next((j for j in range(r,len(rows)) if rows[j][col]),None)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r];z=rows[r][col];rows[r]=[x/z for x in rows[r]]
        for j in range(len(rows)):
            if j!=r:
                z=rows[j][col];rows[j]=[x-z*y for x,y in zip(rows[j],rows[r])]
        pivots.append(col);r+=1
    out=[]
    for free in (j for j in range(n) if j not in pivots):
        v=[F(0)]*n;v[free]=1
        for row,pivot in zip(rows,pivots):v[pivot]=-row[free]
        assert all(sum(x*y for x,y in zip(row,v))==0 for row in A);out.append(v)
    return out


def find_modes(edges):
    edges=checked_edges(edges);kept,reached=port_component(edges)
    if 0 not in reached or len(kept)!=len(edges):raise ValueError('Connected port graph required')
    nodes=sorted(reached);internal=[v for v in nodes if v not in (0,1)];index={v:j for j,v in enumerate(internal)};A=[]
    for k,u,v,x in edges:
        if k=='R':
            row=[F(0)]*len(internal)
            for node,sign in ((u,1),(v,-1)):
                if node in index:row[index[node]]+=sign
            A.append(row)
    for node in nodes:
        row=[F(0)]*len(internal)
        for k,u,v,x in edges:
            if k=='R':continue
            sign=int(u==node)-int(v==node);b=x if k=='C' else -1/x
            for endpoint,d in ((u,1),(v,-1)):
                if endpoint in index:row[index[endpoint]]+=sign*b*d
        A.append(row)
    return [{0:F(0),1:F(0),**{v:z for v,z in zip(internal,vec)}} for vec in nullspace(A,len(internal))]


def fold_parallel(edges):
    groups=defaultdict(list)
    for k,u,v,x in edges:groups[(k,min(u,v),max(u,v))].append(x)
    out=[]
    for (k,u,v),xs in sorted(groups.items()):
        x=sum(xs) if k=='C' else 1/sum(1/x for x in xs)
        out.append((k,u,v,x))
    return out


def serialized(edges):return [[k,u,v,str(x)] for k,u,v,x in edges]


def certificate(edges,mode):
    edges=checked_edges(edges);kept,reached=port_component(edges)
    if 0 not in reached or len(kept)!=len(edges):raise ValueError('Discard disconnected components first')
    w=normalized_mode(edges,mode);folded=fold_parallel(edges)
    base={'format':'komorebi-balanced-mode-face-v1','input_sha256':hashlib.sha256(json.dumps(serialized(edges),separators=(',',':')).encode()).hexdigest(),
      'mode':{str(v):str(w[v]) for v in sorted(w)},'strict_margin':'1/10000000000000',
      'scope':'Connected positive ordinary graph, <=2L/2C, explicit nonzero port-zero internal mode at i. Written classification, not a complete balanced-region separator.'}
    if sum(k!='R' for k,u,v,x in folded)<=3:
        return {**base,'kind':'lower-budget','mechanism':'parallel same-kind reduction','reduced_edges':serialized(folded)}
    active=[e for e in edges if e[0]!='R' and w[e[1]]!=w[e[2]]]
    degree=Counter(v for k,u,v,x in active for v in (u,v));pairs=defaultdict(list)
    for e in active:pairs[tuple(sorted(e[1:3]))].append(e)
    if not active or min(degree.values())<2:raise ValueError('Invalid cyclic active support')
    if len(active)==4 and len(pairs)==2 and all(len(es)==2 for es in pairs.values()):
        for es in pairs.values():
            if {e[0] for e in es}!={'L','C'} or es[0][3]*es[1][3]!=1:raise ValueError('Parallel active pairs are not tuned')
        return {**base,'kind':'inversion-symmetric','mechanism':'two tuned parallel LC pairs',
          'two_sample_weak_margin':str(abs(gamma(F(2))-gamma(F(1,2)))/2)}
    zero=[v for v in degree if not w[v]]
    if len(zero)==1:
        # Every active vertex outside level zero is in a one-anchor appendage.
        reduced=[e for e in edges if w[e[1]]==w[e[2]]==0]
        if sum(k!='R' for k,u,v,x in reduced)>3:raise ValueError('Single-anchor reduction did not lower budget')
        return {**base,'kind':'lower-budget','mechanism':'one zero-level attachment to the active support',
          'active_edges':len(active),'active_vertices':len(degree),'reduced_edges':serialized(reduced)}
    if len(active)==4 and len(degree)==4 and all(d==2 for d in degree.values()) and len(zero)==2:
        # A four-cycle splits into two length-two series-LC arcs.
        a,b=zero;middle=[v for v in degree if w[v]];arcs=[]
        for v in middle:
            es=[e for e in active if v in e[1:3]]
            if {e[0] for e in es}!={'L','C'} or es[0][3]*es[1][3]!=1:raise ValueError('Opposite-zero cycle arcs are not tuned LC')
            if {a,b}!={x for e in es for x in e[1:3] if x!=v}:raise ValueError('Not two parallel two-edge arcs')
            arcs.append({'middle':v,'L':str(next(e[3] for e in es if e[0]=='L'))})
        if w[middle[0]]==w[middle[1]] and arcs[0]['L']!=arcs[1]['L']:raise ValueError('Equal mode levels require equal L values')
        return {**base,'kind':'inversion-symmetric','mechanism':'tuned four-cycle with two zero-level attachments',
          'zero_vertices':sorted(zero),'arcs':arcs,'internal_mode_levels_equal':w[middle[0]]==w[middle[1]],
          'two_sample_weak_margin':str(abs(gamma(F(2))-gamma(F(1,2)))/2)}
    raise ValueError('Unsupported active mode pattern; do not infer a theorem from rejection')


def verify(edges,mode,record):
    if record!=certificate(edges,mode):raise ValueError('Mode-face certificate binding differs')
    return {'status':'PASS','kind':record['kind'],'strict_margin':record['strict_margin']}
