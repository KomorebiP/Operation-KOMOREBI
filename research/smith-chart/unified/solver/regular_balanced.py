"""Exact regular balanced cores and a positive-real surgery certificate.
Author: Komorebi P. Universal classification is a written proof, not this API.
The consumer independently checks the nominal rational response and budgets.
"""
from fractions import Fraction as F
from itertools import combinations
import hashlib,json
from exact_phasor import C
from phasor_unit_voltage import response
from natural_graph_polynomials import pair,value
from real_root_constraints import derivative
from coefficient_fiber import multiply
from pure_type_margins import SAMPLES,gamma
from positive_real_comparison import relative_bound

MAX_NODES=64
MAX_EDGES=256
MAX_BITS=256
MAX_BYTES=524288
FOREST_P=tuple(map(F,(36,121,198,222,162)))
FOREST_Q=tuple(map(F,(81,126,344,126,162)))
CYCLIC_P=tuple(map(F,(8,14,21,14,4)))
CYCLIC_Q=tuple(map(F,(18,23,22,14,4)))
CORES={
 'forest':(('L',1,2,F(1)),('C',2,3,F(1)),('L',3,4,F(2)),('C',4,0,F(1)),('R',1,3,F(5,9)),('R',2,0,F(4,9))),
 'cyclic':(('L',1,2,F(1,2)),('C',1,2,F(1)),('C',2,3,F(1)),('L',3,0,F(1)),('R',1,3,F(4,5)),('R',2,0,F(1)))}
BASE_ERRORS={'forest':F(5175,65083),'cyclic':F(25,2769)}

def rational(x):
    if not (type(x) in (str,int) or isinstance(x,F)) or (isinstance(x,str) and len(x)>180):
        raise ValueError('Bounded rational strings or integers required')
    try:v=F(x)
    except (ValueError,ZeroDivisionError,OverflowError) as exc:raise ValueError('Invalid rational value') from exc
    if max(abs(v.numerator).bit_length(),v.denominator.bit_length())>MAX_BITS:raise ValueError('Rational input exceeds bit cap')
    return v

def checked_edges(edges):
    if not isinstance(edges,(list,tuple)) or len(edges)>MAX_EDGES:raise ValueError('Invalid edge list or edge cap exceeded')
    out=[];nodes={0,1}
    for row in edges:
        if not isinstance(row,(list,tuple)) or len(row)!=4:raise ValueError('Each edge requires kind,u,v,value')
        k,u,v,x=row
        if k not in ('R','L','C') or type(u)!=int or type(v)!=int or min(u,v)<0 or max(u,v)>10**9:
            raise ValueError('Ordinary branch and bounded nonnegative integer nodes required')
        x=rational(x)
        if x<=0:raise ValueError('Physical values must be positive')
        out.append((k,u,v,x));nodes.update((u,v))
    if len(nodes)>MAX_NODES:raise ValueError('Node cap exceeded')
    return out

def serialized(edges):return [[k,u,v,str(x)] for k,u,v,x in edges]

def port_component(edges):
    reach={1}
    while True:
        more=reach|{v for k,u,v,x in edges if u in reach}|{u for k,u,v,x in edges if v in reach}
        if more==reach:break
        reach=more
    if 0 not in reach:raise ValueError('Nominal port must be connected')
    return [e for e in edges if e[1] in reach and e[2] in reach and e[1]!=e[2]]

def kron_resistors(edges):
    """Eliminate only vertices incident to R, keeping all reactive endpoints."""
    edges=port_component(checked_edges(edges))
    reactive=[e for e in edges if e[0]!='R'];keep={0,1}|{v for k,u,v,x in reactive for v in (u,v)}
    nodes={v for k,u,v,x in edges for v in (u,v)};conductance={}
    for k,u,v,x in edges:
        if k=='R':
            edge=tuple(sorted((u,v)));conductance[edge]=conductance.get(edge,F(0))+1/x
    for w in sorted(nodes-keep):
        incident={v if u==w else u:g for (u,v),g in conductance.items() if w in (u,v)}
        total=sum(incident.values(),F(0))
        if total:
            for u,v in combinations(sorted(incident),2):
                key=(u,v);conductance[key]=conductance.get(key,F(0))+incident[u]*incident[v]/total
        conductance={e:g for e,g in conductance.items() if w not in e}
    return reactive+[('R',u,v,1/g) for (u,v),g in sorted(conductance.items()) if g]

def same_response(P,Q,U,V):
    left,right=multiply(P,V),multiply(U,Q)
    return len(left)==len(right) and all(a==b for a,b in zip(left,right))

def endpoint(P,Q,infinity=False):
    p=[(j,x) for j,x in enumerate(P) if x];q=[(j,x) for j,x in enumerate(Q) if x]
    if not p or not q:raise ValueError('Degenerate natural pair')
    a,x=(p[-1] if infinity else p[0]);b,y=(q[-1] if infinity else q[0])
    if a==b:return x/y
    return 'infinity' if (a>b if infinity else a<b) else F(0)

def analyze_nominal(edges):
    edges=checked_edges(edges)
    if any(sum(k==kind for k,u,v,x in edges)>2 for kind in ('L','C')):raise ValueError('At most two L and two C required')
    reduced=kron_resistors(edges);p=pair(reduced);P,Q=p['P'],p['Q'];ti=C(0,1)
    qi=value(Q,ti);pi=value(P,ti)
    if not qi:raise ValueError('Natural Q(i) is zero: regular hypothesis fails')
    zi=pi/qi;jet=(value(derivative(P),ti)*qi-pi*value(derivative(Q),ti))/(qi*qi)
    if zi!=ti or jet!=C(5) or endpoint(P,Q)!=F(4,9) or endpoint(P,Q,True)!=1:
        raise ValueError('Nominal graph does not satisfy all five exact target conditions')
    if same_response(P,Q,FOREST_P,FOREST_Q):kind='forest'
    elif same_response(P,Q,CYCLIC_P,CYCLIC_Q):kind='cyclic'
    else:raise RuntimeError('Exact-data graph has an unrecognized response: classification requires review')
    phasor=response(reduced,ti);unit_current=[ti*i for i in phasor['current']]
    if any(i for (k,u,v,x),i in zip(reduced,unit_current) if k=='R'):
        raise RuntimeError('Zero-loss consistency failure')
    active=[j for j,((k,u,v,x),i) in enumerate(zip(reduced,unit_current)) if k!='R' and i]
    energy=sum((x*i*i if k=='L' else i*i/x for (k,u,v,x),i in zip(reduced,unit_current) if k!='R'),C())
    if len(active)!=4 or energy!=C(5) or any(i.im for i in unit_current):
        raise RuntimeError('Active-support/derivative consistency failure')
    error=max(abs((value(P,s)-value(Q,s))/(value(P,s)+value(Q,s))-gamma(s)) for s in SAMPLES)
    if error!=BASE_ERRORS[kind]:raise RuntimeError('Canonical error mismatch')
    return {'kind':kind,'Z0':'4/9','Zinf':'1','Zi':'i','Zprime_i':'5',
      'natural_P':list(map(str,P)),'natural_Q':list(map(str,Q)),
      'active_LC_edges':4,'effective_R_edges':sum(k=='R' for k,u,v,x in reduced),
      'nominal_seven_sample_error':str(error),'scope':'Exact supplied nominal graph; classification theorem is a separate written argument.'}

def indices(ids,edges):
    if not isinstance(ids,(list,tuple)) or any(type(j)!=int for j in ids) or len(ids)!=len(set(ids)):
        raise ValueError('Distinct resistor index lists required')
    if any(j<0 or j>=len(edges) or edges[j][0]!='R' for j in ids):raise ValueError('Only actual resistor indices may be opened or shorted')
    return sorted(ids)

def surgery_graph(edges,opened,shorted):
    nodes={0,1}|{v for k,u,v,x in edges for v in (u,v)};parent={v:v for v in nodes}
    def find(v):
        while parent[v]!=v:v=parent[v]
        return v
    for j in shorted:
        k,u,v,x=edges[j];u,v=find(u),find(v)
        if u!=v:parent[v]=u
    if find(0)==find(1):raise ValueError('Surgery identifies the two ports')
    groups={}
    for v in sorted(nodes):groups.setdefault(find(v),[]).append(v)
    labels={r:(0 if 0 in vs else 1 if 1 in vs else min(vs)) for r,vs in groups.items()}
    mapping={v:labels[find(v)] for v in nodes}
    deleted=set(opened)|set(shorted)
    return [(k,mapping[u],mapping[v],x) for j,(k,u,v,x) in enumerate(edges) if j not in deleted],mapping

def certificate(spec):
    allowed={'nominal','actual','opened_R_indices','shorted_R_indices','relative_error','requested_margin'}
    if not isinstance(spec,dict) or set(spec)-allowed:raise ValueError('Unexpected specification fields')
    if not {'nominal','actual','relative_error','requested_margin'}<=set(spec):raise ValueError('Required specification field missing')
    nominal=checked_edges(spec['nominal']);actual=checked_edges(spec['actual'])
    epsilon=rational(spec['relative_error']);margin=rational(spec['requested_margin'])
    if not 0<=epsilon<1 or margin<=0:raise ValueError('Relative error must be in[0,1) and requested margin positive')
    opened=indices(spec.get('opened_R_indices',[]),actual);shorted=indices(spec.get('shorted_R_indices',[]),actual)
    if set(opened)&set(shorted):raise ValueError('Opened and shorted sets overlap')
    transformed,mapping=surgery_graph(actual,opened,shorted)
    if len(transformed)!=len(nominal):raise ValueError('Retained branch counts differ')
    for (k,u,v,x),(h,a,b,target) in zip(transformed,nominal):
        if k!=h or sorted((u,v))!=sorted((a,b)):raise ValueError('Retained branch topology differs after surgery')
        if not (1-epsilon)*target<=x<=(1+epsilon)*target:raise ValueError('Retained value outside declared relative box')
    baseline=analyze_nominal(nominal)
    opening=sum((1/actual[j][3] for j in opened),F(0));shorting=sum((actual[j][3] for j in shorted),F(0))
    relative=relative_bound(epsilon);cost=relative+2*(opening+shorting)
    floor=F(baseline['nominal_seven_sample_error'])-cost;slack=floor-margin
    normalized={'nominal':serialized(nominal),'actual':serialized(actual),
      'opened_R_indices':opened,'shorted_R_indices':shorted,'relative_error':str(epsilon),'requested_margin':str(margin)}
    return {'format':'komorebi-regular-core-v1','status':'PASS' if slack>0 else 'INCONCLUSIVE',
      'input_sha256':hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
      'nominal_analysis':baseline,'relative_response_bound':str(relative),
      'opened_conductance_sum':str(opening),'shorted_resistance_sum':str(shorting),'surgery_response_bound':str(2*(opening+shorting)),
      'contraction_map':{str(v):mapping[v] for v in sorted(mapping)},'remaining_error_floor':str(floor),
      'requested_margin':str(margin),'strict_margin':str(margin) if slack>0 else None,'strict_slack':str(slack),
      'scope':'Supplied nominal graph and physical relative/open/short budgets, positive-real Laplace samples only. No whole balanced margin, imaginary-frequency/hardware or new formal assurance.'}

def verify(spec,record):
    expected=certificate(spec)
    if record!=expected:raise ValueError('Certificate input or bound binding differs')
    return {'status':record['status'],'strict_margin':record['strict_margin']}

def main():
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser(description='Positive-real regular-core certificate producer/consumer.')
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.source.stat().st_size>MAX_BYTES:raise ValueError('Input exceeds byte cap')
    def unique(pairs):
        out={}
        for key,val in pairs:
            if key in out:raise ValueError('Duplicate JSON field')
            out[key]=val
        return out
    data=json.loads(args.source.read_bytes(),object_pairs_hook=unique)
    if args.verify:
        if not isinstance(data,dict) or set(data)!={'input','certificate'}:raise ValueError('Producer result must contain input and certificate')
        result=verify(data['input'],data['certificate'])
    else:result={'input':data,'certificate':certificate(data)}
    raw=json.dumps(result,indent=2)+'\n'
    if args.output:
        if args.output.resolve()==args.source.resolve():raise ValueError('Choose an output different from the input')
        args.output.write_text(raw,encoding='utf-8')
    else:print(raw,end='')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
