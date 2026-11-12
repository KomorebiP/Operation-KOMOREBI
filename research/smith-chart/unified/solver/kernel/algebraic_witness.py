"""Author: Komorebi P. Solver-independent algebraic RLC circuit checking.
Every component is a rational polynomial in one isolated real algebraic number.
All signs, nodal solves, gcds, and exact interpolation use standard-library code.
"""
from fractions import Fraction as F
from exact_polynomials import rational
from real_algebraic import RealField,linear_solve,trim,gcd,evaluate


def verify_algebraic_circuit(cert,expected_target=None,expected_budget=None):
    if cert.get('format')!='komorebi-algebraic-circuit-v1':raise ValueError('Unknown circuit format')
    target=cert['target'];P=trim(target['P']);Q=trim(target['Q'])
    if not any(P) or not any(Q):raise ValueError('Nonzero finite target required')
    if expected_target is not None:
        from real_algebraic import mul,sub,iszero
        if not iszero(sub(mul(P,trim(expected_target['Q'])),mul(Q,trim(expected_target['P'])))):
            raise ValueError('Target binding mismatch')
    q=cert['storage_budget']
    if not isinstance(q,int) or isinstance(q,bool) or q<0:raise ValueError('Invalid budget')
    if expected_budget is not None and q!=expected_budget:raise ValueError('Budget binding mismatch')
    f=RealField(cert['field']['polynomial'],cert['field']['interval'])
    edges=[];seen=set()
    for row in cert['branches']:
        typ=row['type'];a,b=row['nodes']
        if typ not in ('g','h','c') or not isinstance(a,int) or not isinstance(b,int) or a<0 or b<0 or a==b:raise ValueError('Bad branch')
        if a>b:a,b=b,a
        key=typ,a,b
        if key in seen:raise ValueError('Duplicate branches must be merged explicitly')
        seen.add(key);val=f.element(row['coefficient'])
        if val.sign()<=0:raise ValueError('Every listed component must be strictly positive')
        edges.append((typ,a,b,val))
    actual=sum(typ!='g' for typ,_,_,_ in edges)
    if actual>q:raise ValueError('Reactive budget exceeded')
    reached={0}
    while True:
        more=reached|{b for _,a,b,_ in edges if a in reached}|{a for _,a,b,_ in edges if b in reached}
        if more==reached:break
        reached=more
    if 1 not in reached:raise ValueError('Input is disconnected from ground')
    if any(a not in reached or b not in reached for _,a,b,_ in edges):raise ValueError('Remove disconnected material from witness')
    nodes=sorted(reached-{0});ix={a:j for j,a in enumerate(nodes)};N=len(nodes)
    degree_bound=max(len(P),len(Q))-1;reduced_degree=degree_bound-(len(gcd(P,Q))-1)
    K=degree_bound+q+1
    for k in range(1,K+1):
        A=[[f.element(0) for _ in range(N)] for _ in range(N)]
        bvec=[f.element(int(a==1)) for a in nodes]
        for typ,a,b,val in edges:
            y=val if typ=='g' else val/F(k) if typ=='h' else val*k
            if a:A[ix[a]][ix[a]]+=y
            if b:A[ix[b]][ix[b]]+=y
            if a and b:A[ix[a]][ix[b]]-=y;A[ix[b]][ix[a]]-=y
        vals=linear_solve(A,bvec,f);den=evaluate(Q,F(k))
        if not den:raise ValueError('Positive sample is a target pole')
        target_val=evaluate(P,F(k))/den
        if vals[ix[1]]!=target_val:raise ValueError(f'Exact target mismatch at argument {k}')
    return {'status':'PASS','arithmetic':'standard-library rational polynomial quotient arithmetic and Sturm isolation',
            'defining_degree':len(f.f)-1,'actual_storage':actual,'resistors':sum(t=='g' for t,_,_,_ in edges),
            'exact_sample_count':K,'reduced_target_degree':reduced_degree,
            'global_minimum_proved_by_degree':actual==reduced_degree,
            'root_interval_refinements':f.refinements}


def verify_minimality_bundle(bundle):
    """One witness at q and one COMPLETE refutation at q-1 suffice.
    A restricted refutation is never allowed to certify global minimality.
    """
    from polynomial_budget import check_circuit_refutation
    target=bundle['target'];q=bundle['q']
    upper=verify_algebraic_circuit(bundle['witness'],target,q)
    if upper['actual_storage']!=q:raise ValueError('Bundle q must be actual storage count')
    if q==upper['reduced_target_degree'] and bundle.get('lower_budget_refutation') is None:
        return {'status':'PASS','minimum_reactive_count':q,'lower_bound':'exact reduced degree','upper_bound':upper}
    lower=bundle.get('lower_budget_refutation')
    if lower is None:raise ValueError('Missing exact lower-budget refutation')
    spec=lower['problem']
    if spec.get('q')!=q-1:raise ValueError('Refutation is for wrong budget')
    from real_algebraic import iszero,sub,mul
    if not iszero(sub(mul(trim(spec['P']),trim(target['Q'])),mul(trim(spec['Q']),trim(target['P'])))):
        raise ValueError('Refutation targets a different impedance')
    checked=check_circuit_refutation(spec,lower['proof'])
    if not checked['full_topology_coverage']:raise ValueError('Restricted refutation cannot prove global minimum')
    return {'status':'PASS','minimum_reactive_count':q,'lower_bound':checked,'upper_bound':upper}
