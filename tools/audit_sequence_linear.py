"""Independent finite constructions for ordinary k-step coefficient formulas."""
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from math import comb
from pathlib import Path


def convolution(a,b,count):
    return [sum(a[j]*b[n-j] for j in range(n+1)) for n in range(count)]


@lru_cache(maxsize=None)
def binomial_h(k,r,c,m):
    if m<0:return 0
    return sum((-c)**j*comb(r+m-k*j-1,m-k*j)*comb(m-k*j,j)*(c+1)**(m-(k+1)*j) for j in range(m//(k+1)+1))


def verify_linear(entries):
    from sequence_linear_research import coefficients,finite_hypergeometric
    from sequence_library import source_degree
    extra=[entry for entry in entries if entry.get('linear_addition')];assert len(extra)==130
    seen=Counter();count=96;oracles={}
    for k in range(2,17):
        for c in (1,2):
            base=[1]
            for n in range(1,count):base.append(c*sum(base[max(0,n-k):n]))
            powered=[1]+[0]*(count-1)
            for r in range(1,5):
                powered=convolution(powered,base,count);assert coefficients(k,r,c,count)==powered
                for n,value in enumerate(powered):
                    finite=sum((-1)**ell*comb(r,ell)*binomial_h(k,r,c,n-ell) for ell in range(min(r,n)+1))
                    hyper=sum((-1)**ell*comb(r,ell)*finite_hypergeometric(k,r,c,n-ell) for ell in range(min(r,n)+1))
                    assert finite==value and hyper==value,(k,r,c,n)
                    seen['linear_extended_coefficients']+=1;seen['finite_hypergeometric_values']+=1
                oracles[k,r,c]=powered
    snapshot=Path(__file__).resolve().parents[1]/'research/sequence-connections/sources/komorebi-math-families.py'
    tree=ast.parse(snapshot.read_text(encoding='utf-8'));function=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='kbonacci_closed_form')
    namespace={'comb':comb,'require_integer':lambda value,**kw:value,'_nonnegative':lambda value,name:value,'ValidationError':ValueError}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),str(snapshot),'exec'),namespace)
    source=namespace['kbonacci_closed_form']
    for k in range(2,17):
        for n in range(count):
            expected=0 if n<k-1 else oracles[k,1,1][n-k+1]
            assert source(k,n)==expected,(k,n);seen['pinned_source_kbonacci_values']+=1
    for entry in extra:
        k,r,c=entry['recurrence_order'],entry['power'],entry['weight']
        expected=oracles[k,r,c]
        if entry['kind']=='k-bonacci':expected=[0]*(k-1)+expected
        assert list(map(int,entry['terms']))==expected[:len(entry['terms'])],entry['id']
        for i in range(len(entry['terms'])):assert source_degree(entry,i)==i;seen['source_index_maps']+=1
        seen['linear_stored_terms']+=len(entry['terms'])
    # At m=0 a zero upper/lower pair may not be cancelled before truncation.
    assert finite_hypergeometric(2,1,1,0)==1
    assert Q(1,3)*Q(2,3)/Q(1,2)==Q(4,9) # cancelled infinite series has a nonzero linear term
    seen['termination_boundary_controls']=1
    assert seen['linear_extended_coefficients']==120*96
    assert seen['linear_stored_terms']==3360
    return seen
