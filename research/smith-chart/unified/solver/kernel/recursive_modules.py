"""Author: Komorebi P. Certified passive factor stripping for mixed RLC synthesis.

This is an INCOMPLETE constructive chart, not a global minimum realization solver.
Proposes exact rational-pole RC/RL sections and full irreducible-quadratic
2-reactive RLC sections. Every result must pass the separately implemented
algebraic nodal verifier against the original target.

The quadratic section is a genuine mixed RLC branch and can handle complex
poles, not just real negative Foster poles. Recursive use preserves rigorous
minimal reactive order if the resulting circuit count equals target degree.
"""
from __future__ import annotations
from fractions import Fraction as F
from copy import deepcopy
from pathlib import Path
import json

from real_algebraic import trim,gcd,iszero,derivative,evaluate,divmod_poly,sub,mul
from exact_biquadratic_templates import R,L,C,parallel,series,graph,dual
from exact_biquadratic_templates import find_exact
from exact_three_node import find_exact_three_node
from cauer_ladders import find_cauer
from endpoint_extract import (find_endpoint_cauer, extract_shunt_L, extract_series_R_C)
from algebraic_witness import verify_algebraic_circuit
from bridge_three_reactive import synthesize_bridge_q3
from sparse_q3_templates import find_sparse_q3


def degree(p):return len(trim(p))-1

def toF(c):
    if hasattr(c,'p') and hasattr(c,'q'):return F(int(c.p),int(c.q))
    return F(c)

def polys(P,Q):
    import sympy as S
    x=S.Symbol('s')
    f=lambda a:S.Poly(sum(S.Rational(t.numerator,t.denominator)*x**j for j,t in enumerate(trim(a))),x,domain=S.QQ)
    return f(P),f(Q)

def as_list(p):
    return trim([toF(p.nth(i)) for i in range(p.degree()+1)]) if p.degree()>=0 else [F(0)]

def normalized(P,Q):
    P,Q=trim(P),trim(Q)
    if not any(P) or not any(Q):raise ValueError('Zero/nonfinite driving-point target')
    g=gcd(P,Q)
    if degree(g)>0:
        P=divmod_poly(P,g)[0];Q=divmod_poly(Q,g)[0]
    if Q[-1]<0:P=[-c for c in P];Q=[-c for c in Q]
    return P,Q


def parallel_second_order(P,Q):
    """Exact Foster-compatible mixed parallel one-port for strictly proper q=2.

    Z=(A*s+B)/(s**2+a*s+b) = 1/(s/A+(a-c)/A+k/(s+c)),
    c=B/A, k=(b-a*c+c*c)/A. Accept only nonnegative admittance
    parameters, with k>0, so every component is ordinary positive RLC.
    """
    P,Q=normalized(P,Q)
    if degree(P)!=1 or degree(Q)!=2: return {'status':'UNKNOWN'}
    A=P[1]/Q[2];B=P[0]/Q[2];a=Q[1]/Q[2];b=Q[0]/Q[2]
    if A<=0:return {'status':'UNKNOWN'}
    c=B/A;g=(a-c)/A;k=(b-a*c+c*c)/A
    if c<0 or g<0 or k<=0:return {'status':'UNKNOWN'}
    branches=[C(1/A)]
    if g>0:branches.append(R(1/g))
    branches.append(series(*([R(c/k)] if c>0 else [])+[L(1/k)]))
    tree=parallel(*branches)
    from exact_biquadratic_templates import circuit_certificate
    cert=circuit_certificate(P,Q,tree)
    try:check=verify_algebraic_circuit(cert,{'P':P,'Q':Q},2)
    except (ValueError,ZeroDivisionError):return {'status':'UNKNOWN'}
    if check['actual_storage']!=2 or check['reduced_target_degree']!=2:return {'status':'UNKNOWN'}
    return {'status':'CERTIFIED_MINIMUM','route':'exact parallel RLC 2-reactive rational inverse',
            'certificate':cert,'verification':check,'minimum_reactive_count':2}


def base_case(P,Q):
    n=max(degree(P),degree(Q))
    r=find_cauer(P,Q)
    if r['status']=='CERTIFIED_MINIMUM':return r
    if n>=2:
        ep=find_endpoint_cauer(P,Q)
        if ep['status']=='CERTIFIED_MINIMUM':return ep
    if n==3:
        bridge=synthesize_bridge_q3(P,Q)
        if bridge['status']=='CERTIFIED_MINIMUM':return bridge
        sparse=find_sparse_q3(P,Q,max_starts=5,max_nfev=250)
        if sparse['status']=='CERTIFIED_MINIMUM':return sparse
    if n==2:
        rr=parallel_second_order(P,Q)
        if rr['status']=='CERTIFIED_MINIMUM':return rr
        for fn in (find_exact,find_exact_three_node):
            try: rr=fn(P,Q)
            except (ValueError,ZeroDivisionError):continue
            if rr['status']=='CERTIFIED_MINIMUM':return rr
    return {'status':'UNKNOWN','reason':f'No certified base template for degree {n}'}


def module_from_pole(a,rho):
    """Returns graph and the exact (numerator,denominator) for an RC or RL section.
    a positive and rho the signed residue at s=-a.
    """
    if a<=0 or rho==0:raise ValueError('Missing stable simple pole/residue')
    if rho>0:
        u=rho
        return parallel(R(u/a),C(1/u)),[u],[a,F(1)],{'type':'RC','a':str(a),'u':str(u)}
    u=-rho/a
    return parallel(R(u),L(u/a)),[F(0),u],[a,F(1)],{'type':'RL','a':str(a),'u':str(u)}


def module_from_quadratic(D,N):
    """Rational quadratic factor D=s²+a*s+b, partial fraction N=A*s+B.

    Sufficient, exact 2-reactive realization with shunt C, optional R, and
    a series RL branch; permits conjugate complex poles.
    """
    if degree(D)!=2 or degree(N)>1:raise ValueError('Invalid quadratic factor')
    s=D[-1];a=D[1]/s;b=D[0]/s
    A=(N[1] if len(N)>1 else F(0))/s;B=N[0]/s
    if min(a,b,A)<=0:raise ValueError('Nonpassive quadratic factor coefficients')
    c=B/A;g=(a-c)/A;k=(b-a*c+c*c)/A
    if c<0 or g<0 or k<=0:raise ValueError('Quadratic partial fraction not in positive mixed-RLC template')
    branches=[C(1/A)]
    if g>0:branches.append(R(1/g))
    branches.append(series(*([R(c/k)] if c>0 else [])+[L(1/k)]))
    return parallel(*branches),[B,A],[b,a,F(1)],{'type':'quadratic_RLC','a':str(a),'b':str(b),'A':str(A),'B':str(B),'conductance':str(g),'rl_rate':str(c),'rl_admittance_scale':str(k)}


def factor_sections(P,Q):
    """List candidate (module tree, lower-degree P/Q, record) exactly.
    Refuse factors repeated in Q; these cannot be peeled by simple residues.
    """
    import sympy as S
    p,q=polys(P,Q);x=p.gens[0]
    factors=S.factor_list(q)[1]
    choices=[]
    for f,e in factors:
        if e!=1:continue
        d=f.monic()
        if d.degree() not in (1,2):continue
        h=q.exquo(d)
        if d.degree()==1:
            a=toF(d.nth(0));
            if a<=0:continue
            residue=evaluate(P,-a)/evaluate(derivative(Q),-a)
            if residue==0:continue
            try:tree,mm,dd,record=module_from_pole(a,residue)
            except ValueError:continue
            numerator=p-S.Poly(sum(S.Rational(z.numerator,z.denominator)*x**i for i,z in enumerate(mm)),x)*h
        else:
            try:inv=S.invert(h,d)
            except Exception:continue
            n=(p*inv).rem(d)
            try:tree,mm,dd,record=module_from_quadratic(as_list(d),as_list(n))
            except ValueError:continue
            numerator=p-n*h
        quotient,remainder=S.div(numerator,d)
        if not remainder.is_zero:raise AssertionError('Exact partial fraction extraction failed')
        coreP=as_list(quotient);coreQ=as_list(h)
        if max(degree(coreP),degree(coreQ))!=max(degree(P),degree(Q))-d.degree():
            continue
        choices.append((tree,coreP,coreQ,record))
    # Higher-order sections first, since they reach different template classes.
    choices.sort(key=lambda row: (0 if row[3]['type']=='quadratic_RLC' else 1,str(row[3])))
    return choices


def append_series_cert(core_cert,module_tree,P,Q):
    """Series composition by relabeling graph ports, preserving the algebraic field.

    Input core has nodes 0 ground and 1 port. Move its port to a new internal
    node; attach module between new external port 1 and that internal node.
    """
    from copy import deepcopy
    c=deepcopy(core_cert)
    mx=max(max(row['nodes']) for row in c['branches'])
    middle=mx+1
    for row in c['branches']:
        row['nodes']=[middle if z==1 else z for z in row['nodes']]
    nxt=middle+1
    for typ,a,b,value in graph(module_tree):
        def translate(j):
            return 1 if j==1 else middle if j==0 else j+middle-1
        aa,bb=sorted((translate(a),translate(b)))
        typ={'R':'g','L':'h','C':'c'}[typ]
        v=value if typ=='c' else 1/value
        c['branches'].append({'type':typ,'nodes':[aa,bb],'coefficient':[str(v)]})
    keys=[(row['type'],tuple(row['nodes'])) for row in c['branches']]
    if len(keys)!=len(set(keys)):raise ValueError('Duplicated branch after series graft')
    c['target']={'P':list(map(str,P)),'Q':list(map(str,Q))}
    c['storage_budget']=sum(row['type']!='g' for row in c['branches'])
    return c


def append_parallel_cert(core_cert,module_tree,P,Q):
    """Attach module directly across the input port (admittances add)."""
    from real_algebraic import RealField
    c=deepcopy(core_cert)
    mx=max(max(row['nodes']) for row in c['branches'])
    rows=c['branches']
    f=RealField(c['field']['polynomial'],c['field']['interval'])
    keys={(row['type'],tuple(sorted(row['nodes']))):i for i,row in enumerate(rows)}
    for typ,a,b,value in graph(module_tree):
        aa=a if a<2 else mx+a-1
        bb=b if b<2 else mx+b-1
        aa,bb=sorted((aa,bb))
        typ={'R':'g','L':'h','C':'c'}[typ]
        v=value if typ=='c' else 1/value
        key=(typ,(aa,bb))
        if key in keys:
            row=rows[keys[key]]
            row['coefficient']=(f.element(row['coefficient'])+f.element(v)).serialize()
        else:
            keys[key]=len(rows)
            rows.append({'type':typ,'nodes':[aa,bb],'coefficient':[str(v)]})
    c['target']={'P':list(map(str,P)),'Q':list(map(str,Q))}
    c['storage_budget']=sum(row['type']!='g' for row in rows)
    return c


def both_orientation_sections(P,Q):
    for tree,cp,cq,rec in factor_sections(P,Q):
        yield 'series',tree,cp,cq,dict(rec,orientation='series impedance')
    # If Y = 1/Z is passively decomposable in series, Z is realizable by
    # placing the corresponding reciprocal-impedance modules in parallel.
    for tree,yp,yq,rec in factor_sections(Q,P):
        yield 'parallel',dual(tree),yq,yp,dict(rec,orientation='parallel admittance')


def one_reactive_endpoint_candidates(P,Q):
    """Exactly peel one physically exposed L or C if rational order drops.

    No optimizers or topology guessing; all four scalar endpoint operations
    are classical and are later checked against the original rational target.
    """
    from real_algebraic import divmod_poly,derivative
    n=max(degree(P),degree(Q))
    if n<2:return
    if degree(P)==degree(Q)+1:
        l=P[-1]/Q[-1]
        if l>0:
            cp=sub(P,mul([F(0),l],Q));cq=Q
            if max(degree(cp),degree(cq))==n-1:
                yield ('series-L',l,cp,cq)
    if degree(Q)==degree(P)+1:
        c=Q[-1]/P[-1]
        if c>0:
            cp=P;cq=sub(Q,mul([F(0),c],P))
            if not iszero(cq) and max(degree(cp),degree(cq))==n-1:
                yield ('shunt-C',c,cp,cq)
    if Q[0]==0 and P[0]!=0 and len(Q)>=2 and Q[1]!=0:
        z=P[0]/Q[1]
        if z>0:
            H=Q[1:];temp=sub(P,[z*c for c in H])
            if temp[0]==0:
                cp=trim(temp[1:]);cq=H
                if max(degree(cp),degree(cq))==n-1 and not iszero(cp):
                    yield ('series-C',1/z,cp,cq)
    if P[0]==0 and Q[0]!=0 and len(P)>=2 and P[1]!=0:
        h=Q[0]/P[1]
        if h>0:
            H=P[1:];temp=sub(Q,[h*c for c in H])
            if temp[0]==0:
                cp=H;cq=trim(temp[1:])
                if max(degree(cp),degree(cq))==n-1 and not iszero(cq):
                    yield ('shunt-L',1/h,cp,cq)


def attach_one_reactive(corecert,mode,val,P,Q):
    leaf=L(val) if mode.endswith('L') else C(val)
    composer=append_series_cert if mode.startswith('series') else append_parallel_cert
    return composer(corecert,leaf,P,Q)


def invert_frequency_certificate(cert,P,Q):
    """Z(s)->Z(1/s) on the SAME circuit graph by L/C element exchange."""
    c=deepcopy(cert)
    for row in c['branches']:
        if row['type']=='h':row['type']='c'
        elif row['type']=='c':row['type']='h'
        # In admittance convention 1/(sL)=h/s -> h*s, and c*s -> c/s.
    c['target']={'P':list(map(str,P)),'Q':list(map(str,Q))}
    return c


def endpoint_candidates(P,Q):
    """Generate q->q-1 rational extraction paths with no pole factorization.
    Both endcaps yield a lower-degree target, unlike arbitrary resistor removal.
    """
    for freq in (False,True):
        pp,qq=(list(reversed(P)),list(reversed(Q))) if freq else (P,Q)
        try:
            g,l,cp,cq=extract_shunt_L(pp,qq)
            yield {'kind':'shunt-R series-L','freq':freq,'g':g,'reactive':l,'coreP':cp,'coreQ':cq}
        except (ValueError,ZeroDivisionError):pass
        try:
            r,c,cp,cq=extract_series_R_C(pp,qq)
            yield {'kind':'series-R shunt-C','freq':freq,'r':r,'reactive':c,'coreP':cp,'coreQ':cq}
        except (ValueError,ZeroDivisionError):pass


def attach_endpoint(corecert,item,P,Q):
    """Compose verified core and physically positive two-element endcap."""
    cp,cq=item['coreP'],item['coreQ']
    if item['kind']=='shunt-R series-L':
        l=item['reactive'];g=item['g']
        p_inter=__poly_add(cp,__poly_mul([F(0),l],cq));q_inter=cq
        cert=append_series_cert(corecert,L(l),p_inter,q_inter)
        p_target,q_target=normalized(P,Q)
        p_t,q_t=(list(reversed(p_target)),list(reversed(q_target))) if item['freq'] else (p_target,q_target)
        cert=append_parallel_cert(cert,R(1/g),p_t,q_t)
    else:
        r=item['r'];c=item['reactive']
        p_inter=cp;q_inter=__poly_add(cq,__poly_mul([F(0),c],cp))
        cert=append_parallel_cert(corecert,C(c),p_inter,q_inter)
        p_target,q_target=normalized(P,Q)
        p_t,q_t=(list(reversed(p_target)),list(reversed(q_target))) if item['freq'] else (p_target,q_target)
        cert=append_series_cert(cert,R(r),p_t,q_t)
    if item['freq']:cert=invert_frequency_certificate(cert,P,Q)
    return cert

from real_algebraic import add as __poly_add
from real_algebraic import mul as __poly_mul


def synthesize(P,Q,max_degree=12,max_states=250):
    P,Q=normalized(P,Q)
    n=max(degree(P),degree(Q))
    if n>max_degree:return {'status':'UNKNOWN','reason':f'Conservative max_degree={max_degree} search cutoff'}
    states=[0];tried=[]
    def recurse(pp,qq):
        d=max(degree(pp),degree(qq));states[0]+=1
        if states[0]>max_states:return None
        bas=base_case(pp,qq)
        if bas['status']=='CERTIFIED_MINIMUM':return {'certificate':bas['certificate'],'route':[bas['route']],'stages':[]}
        # A degree-two core may still expose an L/C endpoint and leave a
        # degree-one Cauer function. Stopping at degree two skipped that valid
        # route (see the archived fresh holdout's origin-pole boundary case).
        if d<=1:return None
        for mode,val,cp,cq in one_reactive_endpoint_candidates(pp,qq):
            result=recurse(cp,cq)
            if result is None:continue
            try:
                cert=attach_one_reactive(result['certificate'],mode,val,pp,qq)
                check=verify_algebraic_circuit(cert,{'P':pp,'Q':qq},d)
                if check['actual_storage']!=d or check['reduced_target_degree']!=d:continue
            except (ValueError,ZeroDivisionError) as e:
                tried.append({'one_endpoint':mode,'rejection':str(e)});continue
            return {'certificate':cert,'route':result['route'],
                    'stages':[{'type':'one_reactive_endpoint','kind':mode,'value':str(val)}]+result['stages']}
        for item in endpoint_candidates(pp,qq):
            result=recurse(item['coreP'],item['coreQ'])
            if result is None:continue
            try:
                cert=attach_endpoint(result['certificate'],item,pp,qq)
                check=verify_algebraic_circuit(cert,{'P':pp,'Q':qq},d)
                if check['actual_storage']!=d or check['reduced_target_degree']!=d:continue
            except (ValueError,ZeroDivisionError) as e:
                tried.append({'endpoint_kind':item['kind'],'rejection':str(e)})
                continue
            record={'type':'endpoint','mode':item['kind'],'frequency_inverted':item['freq'],
                'reactive':str(item['reactive']),
                'resistor_parameter':str(item.get('g',item.get('r')))}
            return {'certificate':cert,'route':result['route'],'stages':[record]+result['stages']}
        candidates=both_orientation_sections(pp,qq)
        for orientation,tree,rp,rq,rec in candidates:
            result=recurse(rp,rq)
            if result is None:continue
            try:
                cert=(append_series_cert if orientation=='series' else append_parallel_cert)(result['certificate'],tree,pp,qq)
                check=verify_algebraic_circuit(cert,{'P':pp,'Q':qq},d)
                if check['actual_storage']!=d or check['reduced_target_degree']!=d:continue
            except (ValueError,ZeroDivisionError) as e:
                tried.append({'stage':rec,'rejection':str(e)});continue
            return {'certificate':cert,'route':result['route'],'stages':[rec]+result['stages']}
        return None
    z=recurse(P,Q)
    if z is None:
        return {'status':'UNKNOWN','reason':'No complete positive branch decomposition into supported q<=2 base; no all-topology impossibility conclusion',
                'visited_states':states[0],'rejected_candidates':tried[:8]}
    c=z['certificate'];v=verify_algebraic_circuit(c,{'P':P,'Q':Q},n)
    if v['actual_storage']!=n or v['reduced_target_degree']!=n:raise AssertionError('Minimum-reactive claim unsupported')
    return {'status':'CERTIFIED_MINIMUM','route':'exact passive module decomposition + verified low-order core',
            'minimum_reactive_count':n,'certificate':c,'verification':v,'modules':z['stages'],
            'core_route':z['route'],'visited_states':states[0]}

if __name__=='__main__':
    import sys
    d=json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(synthesize(d['P'],d['Q']),indent=2))
