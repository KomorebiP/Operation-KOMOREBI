"""Exact physical-state repair and finite support for the written global bound.
Author: Komorebi P. The universal transfer theorem is a written proof; finite
checks and producer/consumer acceptance have their explicitly declared scopes.
"""
from fractions import Fraction as F
from itertools import combinations,product
import json
from exact_phasor import C,response as phasor
from natural_graph_polynomials import pair,value
from regular_balanced import CORES,endpoint
from pure_type_margins import SAMPLES,gamma
from real_root_constraints import derivative
import hashlib
import regular_balanced as rb

MAX_BYTES=524288
FEATURE_RADIUS=F(1,1000)

def rational(x,bits=8192):
    if type(x) not in (str,int) and not isinstance(x,F):raise ValueError('Rational strings or integers required')
    if isinstance(x,str) and len(x)>5000:raise ValueError('Rational text cap exceeded')
    try:z=F(x)
    except (ValueError,ZeroDivisionError,OverflowError) as exc:raise ValueError('Invalid rational') from exc
    if max(abs(z.numerator).bit_length(),z.denominator.bit_length())>bits:raise ValueError('Rational bit cap exceeded')
    return z

def checked_graph(rows,bits=8192):
    if not isinstance(rows,(list,tuple)) or not rows or len(rows)>49:raise ValueError('Graph edge cap exceeded')
    out=[]
    for row in rows:
        if not isinstance(row,(list,tuple)) or len(row)!=4:raise ValueError('Branch requires kind,u,v,value')
        k,u,v,x=row
        if k not in ('R','L','C') or type(u)!=int or type(v)!=int or min(u,v)<0 or max(u,v)>9:
            raise ValueError('Ordinary graph on node labels0..9 required')
        x=rational(x,bits)
        if x<=0:raise ValueError('Strictly positive components required')
        out.append((k,u,v,x))
    if any(sum(k==kind for k,u,v,x in out)>cap for kind,cap in (('R',45),('L',2),('C',2))):
        raise ValueError('This consumer supports at most45 R,two L,two C')
    present={0,1}|{v for k,u,v,x in out for v in (u,v)}
    labels=groups(max(present)+1,[(u,v) for k,u,v,x in out if u!=v])
    if any(labels[v]!=labels[0] for v in present):raise ValueError('Connected physical port graph required by this consumer')
    return out

def prepared(spec):
    allowed={'actual','opened_R_indices','shorted_R_indices','mode','large','small','potential','requested_margin'}
    if not isinstance(spec,dict) or set(spec)-allowed or not {'actual','large','small','requested_margin'}<=set(spec):
        raise ValueError('Invalid specification fields')
    if type(spec.get('mode',False))!=bool:raise ValueError('Mode must be Boolean')
    if 'potential' in spec:
        if not isinstance(spec['potential'],list) or len(spec['potential'])>10:raise ValueError('Bounded potential vector required')
        for x in spec['potential']:rational(x)
    actual=checked_graph(spec['actual'],bits=256)
    opened=rb.indices(spec.get('opened_R_indices',[]),actual);shorted=rb.indices(spec.get('shorted_R_indices',[]),actual)
    if set(opened)&set(shorted):raise ValueError('Opened and shorted indices overlap')
    transformed,mapping=rb.surgery_graph(actual,opened,shorted);transformed=checked_graph(transformed,bits=256)
    large,small,requested=(rational(spec[k],256) for k in ('large','small','requested_margin'))
    if not large>small>=0 or requested<=0:raise ValueError('Positive ordered thresholds and requested margin required')
    return actual,transformed,opened,shorted,large,small,requested,mapping

def evaluate_witness(spec,witness):
    actual,transformed,opened,shorted,large,small,requested,mapping=prepared(spec)
    if not isinstance(witness,dict) or set(witness)!={'corrected','potential'}:raise ValueError('Invalid state witness')
    corrected=checked_graph(witness['corrected'])
    if len(corrected)!=len(transformed):raise ValueError('Corrected topology differs')
    eps=F(0)
    for (k,u,v,z),(h,a,b,t) in zip(corrected,transformed):
        if (k,u,v)!=(h,a,b):raise ValueError('Corrected branch topology differs')
        if k=='R' and z!=t:raise ValueError('State repair must retain every R value')
        if k!='R':eps=max(eps,abs(z/t-1))
    if not isinstance(witness['potential'],list) or len(witness['potential'])>10:raise ValueError('Bounded state vector required')
    phi=[rational(x) for x in witness['potential']]
    nodes={0,1}|{v for k,u,v,z in corrected for v in (u,v)};n=max(nodes)+1
    if len(phi)!=n or phi[0] or any(phi[v] for v in range(n) if v not in nodes):raise ValueError('Invalid physical potential coordinates')
    div=[F(0)]*n;jet=F(0)
    for k,u,v,z in corrected:
        drop=phi[u]-phi[v]
        if k=='R':
            if drop:raise ValueError('Nonzero resistor voltage in exact loss-free witness')
            continue
        flow=(1/z if k=='L' else -z)*drop
        div[u]+=flow;div[v]-=flow;jet+=(z if k=='L' else 1/z)*flow*flow
    mode=spec.get('mode',False);target=[F(0)]*n
    if mode:
        if phi[1] or not any(phi[v] for v in nodes):raise ValueError('Nonzero port-zero mode required')
    else:target[1]=F(1);target[0]=F(-1)
    if div!=target:raise ValueError('Original-node KCL fails')
    features=None;baseline=None;reason=None
    if mode:baseline=F(1,10**13);reason='exact internal mode'
    else:
        p=pair(corrected)
        if not value(p['Q'],C(0,1)):
            baseline=F(1,10**13);reason='compatible driven state with an internal port-zero kernel'
        else:
            r0=endpoint(p['P'],p['Q']);r1=endpoint(p['P'],p['Q'],True)
            features={'Im_Zi':str(phi[1]),'Zprime_i':str(jet),'Z0':str(r0),'Zinf':str(r1)}
            if isinstance(r0,F) and isinstance(r1,F) and all(abs(x-y)<=FEATURE_RADIUS for x,y in zip((phi[1],jet,r0,r1),(F(1),F(5),F(4,9),F(1)))):
                baseline=F(1,300);reason='zero-loss global feature chart'
            else:reason='Exact state is outside the certified feature chart'
    surgery=sum((1/actual[j][3] for j in opened),F(0))+sum((actual[j][3] for j in shorted),F(0))
    relative=eps/(2*(1-eps)) if eps<1 else None
    floor=baseline-relative-2*surgery if baseline is not None and relative is not None else None
    slack=floor-requested if floor is not None else None
    normalized={'actual':rb.serialized(actual),'opened_R_indices':opened,'shorted_R_indices':shorted,
      'mode':mode,'large':str(large),'small':str(small),'requested_margin':str(requested),
      'potential':[str(rational(z)) for z in spec['potential']] if 'potential' in spec else None}
    return {'format':'komorebi-physical-state-transfer-v1','status':'PASS' if slack is not None and slack>0 else 'INCONCLUSIVE',
      'input_sha256':hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
      'reason':reason,'base_strict_margin':str(baseline) if baseline is not None else None,
      'features':features,'relative_LC_error':str(eps),'relative_response_bound':str(relative) if relative is not None else None,
      'combined_R_surgery_budget':str(surgery),'remaining_strict_error_floor':str(floor) if floor is not None else None,
      'requested_margin':str(requested),'strict_slack':str(slack) if slack is not None else None,
      'strict_margin':str(requested) if slack is not None and slack>0 else None,
      'witness':{'corrected':rb.serialized(corrected),'potential':list(map(str,phi))},
      'scope':'Exact supplied physical state and checked relative-LC/R-surgery budgets on positive-real Laplace samples. Universal transfer has a written proof; this consumer is resource bounded and has no imaginary-frequency, hardware or formal assurance.'}

def certificate(spec):
    actual,transformed,opened,shorted,large,small,requested,mapping=prepared(spec)
    n=max(v for k,u,v,z in transformed for v in (u,v))+1
    if 'potential' in spec:
        if not isinstance(spec['potential'],list) or len(spec['potential'])!=n:raise ValueError('Potential length differs from transformed graph')
        x=[rational(v) for v in spec['potential']]
    elif spec.get('mode',False):raise ValueError('Supply the approximate real mode potential')
    else:
        try:state=unit_current(transformed)
        except (ValueError,ZeroDivisionError) as exc:
            return {'format':'komorebi-physical-state-transfer-v1','status':'INCONCLUSIVE','reason':str(exc)}
        x=[state['potentials'].get(v,C()).im for v in range(n)]
    try:corrected,phi,details=repair(transformed,x,large,small,mode=spec.get('mode',False))
    except (ValueError,AssertionError) as exc:
        return {'format':'komorebi-physical-state-transfer-v1','status':'INCONCLUSIVE','reason':str(exc) or 'No safe LC voltage gap for supplied thresholds'}
    return evaluate_witness(spec,{'corrected':rb.serialized(corrected),'potential':list(map(str,phi))})

def verify(spec,record):
    if not isinstance(record,dict) or 'witness' not in record:raise ValueError('No physical-state witness to verify')
    expected=evaluate_witness(spec,record['witness'])
    if record!=expected:raise ValueError('State certificate input or bound binding differs')
    return {'status':expected['status'],'strict_margin':expected['strict_margin']}

def global_arithmetic_certificate():
    B=10000;K=B+1;needed=16*B*K**9;chosen=10**45
    assert needed+1<chosen and 200*F(1,10**16)<F(1,4)
    assert F(2000-18,9)>220
    assert F(B-2003,2)-2040>70
    assert 16*F(1,10**(16*137))<1
    assert 8*F(1,10**(16*31))<1 and 8*F(1,10**16)<1
    assert 34*F(1,10**16)+12*F(1,10**(16*11))<1
    assert 4*chosen<2**803
    return {'status':'PASS','margin_notation':'10^(-10^45)',
      'negative_decimal_exponent':str(chosen),'needed_decimal_exponent':str(needed),
      'bounded_backbone_exponent':B,'scale_multiplier':K,'R_forest_edges_max':9,
      'scope':'Integer/exponent arithmetic supporting the separate written universal proof. No claim that code alone proves the graph reductions.'}

def main():
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser(description='Physical zero-loss state certificate producer/consumer')
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.source.stat().st_size>MAX_BYTES:raise ValueError('JSON byte cap exceeded')
    def unique(rows):
        out={}
        for k,v in rows:
            if k in out:raise ValueError('Duplicate JSON field')
            out[k]=v
        return out
    data=json.loads(args.source.read_bytes(),object_pairs_hook=unique)
    if args.verify:
        if not isinstance(data,dict) or set(data)!={'input','certificate'}:raise ValueError('Expected producer wrapper')
        result=verify(data['input'],data['certificate'])
    else:result={'input':data,'certificate':certificate(data)}
    raw=json.dumps(result,indent=2)+'\n'
    if args.output:
        if args.output.resolve()==args.source.resolve():raise ValueError('Output must differ from input')
        args.output.write_text(raw,encoding='utf-8')
    else:print(raw,end='')


def unit_current(graph):
    source=phasor(graph,C(0,1));current=1-source['voltages'][1]
    return {'Z':source['voltages'][1]/current,
      'potentials':{v:z/current for v,z in source['voltages'].items()}}

def groups(n,edges):
    parent=list(range(n))
    def find(v):
        while parent[v]!=v:v=parent[v]
        return v
    for u,v in edges:
        a,b=find(u),find(v)
        if a!=b:parent[b]=a
    return [find(v) for v in range(n)]

def maximum_forest(n,edges):
    out=[]
    for g,u,v in sorted(edges,reverse=True):
        labels=groups(n,[(a,b) for _,a,b in out])
        if labels[u]!=labels[v]:out.append((g,u,v))
    return out

def scale_surgery(graph,a,c):
    n=max(v for _,u,v,_ in graph for v in (u,v))+1
    R=[(1/x,u,v) for k,u,v,x in graph if k=='R' and u!=v]
    T=maximum_forest(n,R)
    assert not any(c<min(g,1/g)<=a for g,u,v in T)
    short=[(g,u,v) for g,u,v in T if g>=1/c]
    contracted=groups(n,[(u,v) for g,u,v in short])
    moderate=groups(n,[(u,v) for g,u,v in T if g>=a])
    opened=[(g,u,v) for g,u,v in R if moderate[u]!=moderate[v]]
    assert all(g<=c for g,u,v in opened)
    assert all(g<=1/a for g,u,v in R if contracted[u]!=contracted[v] and moderate[u]==moderate[v])
    cost=sum(1/g for g,u,v in short)+sum(g for g,u,v in opened)
    assert cost<=(n-1+len(R))*c
    assert contracted[0]!=contracted[1]
    labels={contracted[0]:0,contracted[1]:1}
    for v in range(n):labels.setdefault(contracted[v],len(labels))
    out=[]
    for k,u,v,x in graph:
        if k=='R' and moderate[u]!=moderate[v]:continue
        u,v=labels[contracted[u]],labels[contracted[v]]
        if u!=v:out.append((k,u,v,x))
    # New R components are spanned using edges with conductance >=a.
    nn=max(v for _,u,v,_ in out for v in (u,v))+1
    all_g=groups(nn,[(u,v) for k,u,v,x in out if k=='R'])
    good=groups(nn,[(u,v) for k,u,v,x in out if k=='R' and 1/x>=a])
    assert all((all_g[u]==all_g[v])==(good[u]==good[v]) for u,v in combinations(range(nn),2))
    return out,cost

def repair(graph,x,large,small,mode=False):
    n=len(x);assert x[0]==0 and large>small>=0
    active=[j for j,(k,u,v,z) in enumerate(graph) if k!='R' and abs(x[u]-x[v])>large]
    assert all(abs(x[u]-x[v])<=small for j,(k,u,v,z) in enumerate(graph) if k!='R' and j not in active)
    eq=[(u,v) for j,(k,u,v,z) in enumerate(graph) if k=='R' or j not in active]
    label=groups(n,eq);phi=list(x)
    for key in set(label):
        vs=[v for v in range(n) if label[v]==key]
        if 0 in vs or (mode and 1 in vs):val=F(0)
        elif 1 in vs:val=x[1]
        else:val=x[min(vs)]
        if not mode and 0 in vs and 1 in vs:raise ValueError('Incompatible port cluster')
        for v in vs:phi[v]=val
    f=[F(0)]*len(graph);div=[F(0)]*n
    for j in active:
        k,u,v,z=graph[j];coef=1/z if k=='L' else z
        f[j]=(1 if k=='L' else -1)*coef*(phi[u]-phi[v])
        div[u]+=f[j];div[v]-=f[j]
    target=[F(0)]*n
    if not mode:target[1]=F(1);target[0]=F(-1)
    residual=[b-d for b,d in zip(target,div)];before=list(residual)
    adj=[[] for _ in range(n)]
    for j in active:
        _,u,v,_=graph[j];adj[u].append((v,j));adj[v].append((u,j))
    seen=set();correction=[F(0)]*len(graph)
    for root in range(n):
        if root in seen:continue
        seen.add(root);order=[root];parent={root:None}
        for v in order:
            for w,j in adj[v]:
                if w not in seen:seen.add(w);parent[w]=(v,j);order.append(w)
        for v in reversed(order[1:]):
            p,j=parent[v];_,u,w,_=graph[j]
            correction[j]=residual[v] if u==v else -residual[v]
            f[j]+=correction[j];residual[p]+=residual[v];residual[v]=0
        if residual[root]:raise ValueError('Active component cannot carry the port injection')
    out=list(graph)
    for j in active:
        k,u,v,z=graph[j];d=phi[u]-phi[v]
        if not d:raise ValueError('Active voltage collapsed')
        coef=(1 if k=='L' else -1)*f[j]/d
        if coef<=0:raise ValueError('Positive element correction failed')
        out[j]=(k,u,v,1/coef if k=='L' else coef)
    final=[F(0)]*n
    for k,u,v,z in out:
        d=phi[u]-phi[v]
        if k=='R':assert d==0;continue
        flow=(1/z if k=='L' else -z)*d
        final[u]+=flow;final[v]-=flow
    assert final==target and (not mode or any(phi))
    err=max((abs(z/t-1) for (_,u,v,z),(_,a,b,t) in zip(out,graph)),default=F(0))
    return out,phi,{'relative_physical_change':str(err),'maximum_original_node_residual':str(max(map(abs,before))),
      'maximum_tree_flow_correction':str(max(map(abs,correction))),
      'active_LC':len(active),'inactive_LC':sum(k!='R' for k,u,v,z in graph)-len(active)}

def chart_graph(kind,a,b,r0,r1):
    if kind=='forest':
        vals=[a,1/a,(b-a)/2,2/(b-3*a),r1-r0,r0]
    else:vals=[2*a*a/(b-a),(b-3*a)/(2*a*a),1/a,a,r0*r1/(r1-r0),r1]
    return [(k,u,v,x) for (k,u,v,z),x in zip(CORES[kind],vals)]

def tree_completion_check(graph):
    if len(graph)>12:raise ValueError('This finite tree-control enumerator is capped at12 edges')
    n=max(v for k,u,v,x in graph for v in (u,v))+1
    r=[(1/x,u,v) for k,u,v,x in graph if k=='R']
    T=maximum_forest(n,r);backbone={(min(u,v),max(u,v)) for g,u,v in T}
    lc=[j for j,e in enumerate(graph) if e[0]!='R'];lpos={j:k for k,j in enumerate(lc)}
    available=[j for j,(k,u,v,x) in enumerate(graph) if k!='R' or (min(u,v),max(u,v)) in backbone]
    coverage=[set(),set()];backbone_coverage=[set(),set()]
    polys=[[F(0)]*5 for _ in range(2)];tested=0
    for which,size in ((0,n-2),(1,n-1)):
        for indices in combinations(range(len(graph)),size):
            labels=groups(n,[(graph[j][1],graph[j][2]) for j in indices])
            if len(set(labels))!=(2 if which==0 else 1):continue
            if which==0 and labels[0]==labels[1]:continue
            mask=sum(1<<lpos[j] for j in indices if j in lpos);coverage[which].add(mask)
            if all(j in available for j in indices):backbone_coverage[which].add(mask)
            exponent=sum(k=='L' for k,u,v,x in graph);coefficient=F(1)
            for j in indices:
                k,u,v,x=graph[j]
                coefficient*=x if k=='C' else 1/x
                exponent+=1 if k=='C' else -1 if k=='L' else 0
            polys[which][exponent]+=coefficient;tested+=1
    assert coverage==backbone_coverage
    natural=pair(graph)
    assert all(tuple(polys[j])==tuple(x*natural['scale'] for x in natural[k]) for j,k in enumerate(('P','Q')))
    return {'trees_and_separating_forests':tested,'LC_subset_populations':list(map(len,coverage))}

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
