"""Exact terminal-carry reductions and uniform odd-multiplier certificates.

The paired polynomials represent F(x,z)=f0(x)+z*f1(x).  A leaf certificate
is coefficientwise for ALL z in Z_2, not a grid of parameter samples.
The wall template applies only when the specified label is the terminal
carry label of the actual first omitted index. See CONTINUATION_06.md.
"""
from __future__ import annotations
from fractions import Fraction
from typing import Any
import dyadic_modular as d


def terminal_descriptor(r: int) -> dict[str, Any]:
    if not isinstance(r, int) or isinstance(r, bool) or r < 1:
        raise ValueError('r must be a positive integer')
    mu, minima = d.minimum(r)
    j = max(minima)
    ans = {'r': r, 'mu': mu, 'minima': minima, 'j': j}
    if j == 0:
        return {**ans, 'kind': 'unit', 'regular': True}
    L = int(d.v2(r+j)); b = (r+j) >> L
    e = [3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
    E = min(e); L0 = 3*j+1+(j-1).bit_count()-E
    assert j < (1<<L) and b % 2 == 1
    assert mu == 3*j+1+(j-1).bit_count()-L and L >= L0
    expected = [j] if L>L0 else [q for q,z in enumerate(e) if z==E]+[j]
    assert minima == expected
    return {**ans, 'kind': 'terminal_wall', 'L': L, 'odd_multiplier': b,
            'wall_threshold': L0, 'delta': L-L0, 'lower_weights': e,
            'regular': all(z>0 for z in e[1:])}


def separating_scales(j: int) -> list[dict[str,int]]:
    if j < 1:
        raise ValueError('Positive label required')
    return [{'s':i, 'k':0 if j==1 else max(i,j-1-i).bit_length(),
             'derivative':j-1-i.bit_count()-(j-1-i).bit_count(),
             'threshold':j-1-i.bit_count()-(j-1-i).bit_count()
                 +(0 if j==1 else max(i,j-1-i).bit_length())}
            for i in range(j)]


def regular_root_count(desc: dict) -> int:
    if desc['j']==0:return 0
    if not desc['regular']:raise ValueError('Irregular terminal label')
    return sum(a['threshold']<=desc['delta'] for a in separating_scales(desc['j']))


def wall_template(j: int, L: int, precision: int) -> dict:
    """b*G_(b*2^L-j), as low*b+high on each parity ball modulo 2^P.

    Valid for positive odd b whose actual terminal label is j. This is a
    branchwise congruence on x=e+2y. Do NOT treat it as a global Gauss
    congruence: remote terms are discarded using the content of P_q(e+2y).
    """
    if j<1 or precision<1 or L<1:raise ValueError('Positive inputs required')
    r=(1<<L)-j
    base=terminal_descriptor(r)
    if base['j']!=j or base['L']!=L:
        raise ValueError('Base member not on specified terminal wall')
    qcut=2*precision
    if (1<<L) <= 2*(j+qcut):raise ValueError('Scale insufficient for one crossing')
    stability=L+1-(2*(j+qcut)).bit_length()
    if stability<precision:raise ValueError('Insufficient parameter-stability margin')
    if 2*r-1<precision:raise ValueError('Nonunit Bernoulli depletion not negligible')
    modulus=1<<precision;low=[0];high=[0];p=[1]
    source=d.source_polynomial(precision)
    for q in range(qcut):
        if q:
            h=q-1;p=d.mul(d.mul(p,[-h,1],modulus),[-(2*h+1),2],modulus)
        gamma=d.gamma_mod(r,q,base['mu'],precision)
        if not gamma:continue
        term=[gamma*z%modulus for z in d.mul(p,d.affine(source,-q,1,modulus),modulus)]
        if q<j:low=d.add(low,term,modulus)
        else:high=d.add(high,term,modulus)
    return {'j':j,'L':L,'mu':base['mu'],'precision':precision,'qcut':qcut,
            'stability_margin':stability,'low':low,'high':high,
            'scope':'coefficientwise after any integral parity-ball substitution; terminal-label hypothesis required'}


def paired_atlas(f0: list[int], f1: list[int], precision: int,
                 max_depth: int=16) -> list[dict]:
    """Partition x for f0(x)+z*f1(x), uniformly in z in Z_2.

    Root leaves give exactly one x-root for EACH z. No claim that its
    coordinate is independent of z. Parameter sampling is not used.
    The initial split into parity balls is mandatory for wall templates.
    """
    leaves=[];modulus=1<<precision
    def visit(p0,p1,bits,s,k,content):
        if k>max_depth:
            leaves.append({'kind':'unresolved_depth','s':s,'k':k});return
        nu=min((d.v2(c) for p in (p0,p1) for c in p if c),default=bits)
        if nu>=bits:
            leaves.append({'kind':'unresolved_precision','s':s,'k':k,'content_lower':content+bits});return
        nu=int(nu)
        if nu:
            p0=d.trim([c>>nu for c in p0]);p1=d.trim([c>>nu for c in p1])
            bits-=nu;content+=nu
        a=d.trim([c%2 for c in p0]);b=d.trim([c%2 for c in p1])
        if a==[1] and b==[0]:
            leaves.append({'kind':'constant','s':s,'k':k,'value':content,'red0':a,'red1':b});return
        if len(a)==2 and a[1]==1 and len(b)==1:
            leaves.append({'kind':'simple_root','s':s,'k':k,'content':content,
                           'offset':content-k,'red0':a,'red1':b});return
        mod=1<<bits
        for e in (0,1):
            visit(d.affine(p0,e,2,mod),d.affine(p1,e,2,mod),bits,s+(1<<k)*e,k+1,content)
    for e in (0,1):
        visit(d.affine(f0,e,2,modulus),d.affine(f1,e,2,modulus),precision,e,1,0)
    return leaves


def validate_paired_atlas(f0,f1,precision,atlas) -> int:
    if any(a['kind'].startswith('unresolved') for a in atlas):
        raise ValueError('Incomplete paired atlas')
    assert sum((Fraction(1,1<<a['k']) for a in atlas),Fraction())==1
    for i,a in enumerate(atlas):
        for b in atlas[:i]:
            assert (a['s']-b['s'])%(1<<min(a['k'],b['k'])) != 0
        c=a['value'] if a['kind']=='constant' else a['content']
        assert 0<=c<precision
        m=1<<(c+1)
        polys=[d.affine(f,a['s'],1<<a['k'],m) for f in (f0,f1)]
        assert all(z%(1<<c)==0 for p in polys for z in p)
        red=[d.trim([(z>>c)&1 for z in p]) for p in polys]
        assert red==[a['red0'],a['red1']]
        if a['kind']=='constant':assert red==[[1],[0]]
        else:assert len(red[0])==2 and red[0][1]==1 and len(red[1])==1
    return len(atlas)


def parameter_certificate(template: dict, residue: int, exponent: int,
                          max_depth: int=16) -> dict:
    if exponent<1 or residue%2!=1 or not 0<=residue<1<<exponent:
        raise ValueError('Odd residue in declared range required')
    P=template['precision'];mod=1<<P
    f0=d.add([residue*z%mod for z in template['low']],template['high'],mod)
    f1=[(z<<exponent)%mod for z in template['low']]
    atlas=paired_atlas(f0,f1,P,max_depth)
    complete=not any(a['kind'].startswith('unresolved') for a in atlas)
    if complete:validate_paired_atlas(f0,f1,P,atlas)
    return {'parameter_residue':residue,'parameter_exponent':exponent,
            'complete':complete,'root_count':sum(a['kind']=='simple_root' for a in atlas) if complete else None,
            'atlas':atlas}
