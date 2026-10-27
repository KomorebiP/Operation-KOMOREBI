#!/usr/bin/env python3
"""Exact, finite data behind the Conjecture 66 visual atlas.

Only integers and rational numbers are used for certificates. Floating point is
used by the separate renderer for drawing, never to decide a mathematical claim.
The model data do not manufacture an arithmetic host, marking, or H5 witness.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
from itertools import product
from math import gcd
from typing import Iterable


def symplectic(v: int, w: int, planes: int) -> int:
    if planes < 1 or not (0 <= v < 4**planes and 0 <= w < 4**planes):
        raise ValueError('vectors must lie in the declared binary space')
    return sum(((v >> (2*i)) & 1)*((w >> (2*i+1)) & 1)
               + ((v >> (2*i+1)) & 1)*((w >> (2*i)) & 1)
               for i in range(planes)) % 2


def quadratic(v: int, planes: int, linear: int = 0) -> int:
    if planes < 1 or not (0 <= v < 4**planes and 0 <= linear < 4**planes):
        raise ValueError('invalid vector or linear term')
    return (sum(((v >> (2*i)) & 1)*((v >> (2*i+1)) & 1)
                for i in range(planes)) + (v & linear).bit_count()) % 2


def gauss(planes: int, linear: int = 0) -> int:
    return sum(1 - 2*quadratic(v, planes, linear) for v in range(4**planes))


def dual(linear: int, planes: int) -> int:
    if not 0 <= linear < 4**planes:
        raise ValueError('invalid linear term')
    return sum(((linear >> (2*i)) & 1) << (2*i+1) |
               ((linear >> (2*i+1)) & 1) << (2*i) for i in range(planes))


def transvection(v: int, a: int, planes: int) -> int:
    return v ^ (a if symplectic(a, v, planes) else 0)


def extension_cocycle(v: int, w: int, planes: int, linear: int = 0) -> int:
    """Normal ordering X1 Z1 ... Xs Zs, with the declared lift squares."""
    return (sum(((v >> (2*i+1)) & 1)*((w >> (2*i)) & 1)
                for i in range(planes)) + (v & w & linear).bit_count()) % 2


def group_product(g: tuple[int, int], h: tuple[int, int], planes: int, linear: int = 0):
    z,v = g; t,w = h
    return (z ^ t ^ extension_cocycle(v,w,planes,linear), v ^ w)


def element_orders(linear: int) -> dict[int,int]:
    counts: Counter[int] = Counter()
    for g in product(range(2), range(4)):
        h=(0,0)
        for k in range(1,9):
            h=group_product(h,g,1,linear)
            if h==(0,0):
                counts[k]+=1
                break
        else:
            raise AssertionError('element order exceeded group order')
    return dict(sorted(counts.items()))


def profile(dims: list[int], levels: list[int]) -> dict:
    if len(dims) != len(levels)+1 or not levels or dims[-1]!=1:
        raise ValueError('profile must have one more grade dimension and end at one')
    if any(a<=b for a,b in zip(dims,dims[1:])) or any(a<=b for a,b in zip(levels,levels[1:])):
        raise ValueError('dimensions and positive levels must strictly decrease')
    if min(levels)<=0:
        raise ValueError('levels must be positive')
    jumps=[a-b for a,b in zip(dims,dims[1:])]
    weighted=[j*l for j,l in zip(jumps,levels)]
    I=sum(j*((l+1)//2) for j,l in zip(jumps,levels))-(dims[0]-1)
    D=sum(j for j,l in zip(jumps,levels) if l%2==0)
    pair=dims[0]**2-1+sum(weighted)
    return dict(dims=dims,levels=levels,jumps=jumps,weighted=weighted,I=I,D=D,pair=pair)


def conductor(dim: int, invariant_dim: int, swan: int) -> dict:
    if not 0 <= invariant_dim <= dim or swan<0:
        raise ValueError('invalid conductor dimensions')
    ordinary=dim-invariant_dim+swan
    return dict(dim=dim,inertia_fixed=invariant_dim,swan=swan,ordinary=ordinary,
                psi0_exponent=ordinary,psi1_exponent=ordinary-dim)


def root_levels(base: int = 3, depth: int = 5) -> list[dict]:
    if base<2 or depth<1:
        raise ValueError('positive depth and base at least two required')
    return [dict(level=n,modulus=base**n,
                 roots=[x for x in range(base**n) if (x*x-1)%(base**n)==0])
            for n in range(1,depth+1)]


def corner_image(h_fixed: int | None = None) -> set[tuple[int,...]]:
    ans=set()
    hs=range(3) if h_fixed is None else [h_fixed]
    for a,b,c,d,h in product(range(3),range(3),range(3),range(3),hs):
        u,v,w=c*d%3,a*b%3,b*c%3
        if u*v*w:
            ans.add((u,v,w,c*(a-h)%3,b*(d-h)%3))
    return ans


def corner_criterion(t: tuple[int,...]) -> bool:
    u,v,w,p,q=t
    return u*v*w!=0 and (p+u-w*(q+v))%3==0


def c3_action(v: int, power: int) -> int:
    """Order-three map (x,y) -> (y,x+y) over F2."""
    if v not in range(4):
        raise ValueError('C3 module is F2^2')
    for _ in range(power%3):
        x=v&1;y=(v>>1)&1;v=y|((x^y)<<1)
    return v


def model_data() -> dict:
    corners=sorted(corner_image());roots=root_levels()
    full=profile([8,4,2,1],[60,18,3]);skip=profile([8,4,1],[60,13])
    qrows=[dict(v=v,q=quadratic(v,1),q0=quadratic(v,1,2),
                image=transvection(v,1,1),corrected=quadratic(transvection(v,1,1),1,2))
           for v in range(4)]
    u=1;deltas=[u^c3_action(u,g) for g in range(3)]
    section_change=[[int(v==3)^int(w==3)^int((v^w)==3)
                     for w in range(4)] for v in range(4)]
    return {
      'schema':'P11-ATLAS-1','scope':'Exact finite examples and recorded claim-map states, not arithmetic realization certificates',
      'candidate_counterexample':{'realizers':['pi_1'],'H5_candidates':['pi_2'],'intersection':[]},
      'balanced_product':{'p':3,'factor_order':27,'domain_order':729,'kernel_order':3,'image_order':243,'factor_degree':3,'tensor_degree':9},
      'binder_roots':roots,
      'corner':{'image':[list(t) for t in corners], 'four_coordinate_image':[list(t) for t in sorted(corner_image(0))],
                'allowed':24,'total':72,'repaired_target':[1,1,1,2,2],'excluded_target':[1,1,1,1,2]},
      'trace_grid':{'valuations':list(range(-4,3)),'depths':list(range(1,7)),
                    'all_invisible':[[int(t+r>=1) for r in range(1,7)] for t in range(-4,3)]},
      'levels':{'odd_p3_d2':[24,4],'dyadic_d3':[60,18,3]},
      'capacities':[{'d':d,'rank':2**d,'source':2*d,'host':2**d-2} for d in range(1,6)],
      'induction_toy':{'G':12,'M':6,'H':2,'G_over_M':2,'M_over_H':3,'G_over_H':6},
      'conductors':{'rho':conductor(9,0,24),'End rho':conductor(81,1,152),'Ad rho':conductor(80,0,152)},
      'periods':[{'e':e,'r':str(Fraction(24*e,9)),'integral':(24*e)%9==0} for e in [1,3,9]],
      'source_breaks':{'breaks':[0,1,2],'multiplicities':[1,8,72],'swan_contributions':[0,8,144]},
      'rank9_profiles':[dict(c=c,**profile([9,3,1],[24,c])) for c in [4,10]],
      'rank8_profiles':{'full':full,'skipped':skip},
      'descent_fibres':{'m4_n9':[9*x%4 for x in range(4)],'m3_n3':[3*x%3 for x in range(3)]},
      'clifford':{'abelian_order':8,'radical_order':2,'projective_degree':2,'S3_orbit':2,'S3_multiplicity':1,'S3_constituent_degree':1},
      'occurrence':{'correction_powers':[0,1,2],'remaining_scalar_exponents_mod3':[1,0,2],'corrected_occurrence':None},
      'native_action':{'p':3,'cyclic_order':4,'symplectic_matrix':[[0,2],[1,0]],'native_p_group_hom_images':[0]},
      'marked_groups':{'D8_orders':element_orders(0),'Q8_orders':element_orders(3),
                       'D8_q':[quadratic(v,1) for v in range(4)],'Q8_q':[quadratic(v,1,3) for v in range(4)]},
      'section_cocycle_difference':section_change,
      'gauss6':{'plus':{'values':[quadratic(v,3) for v in range(64)],'gauss':gauss(3),'zeros':36},
                'minus':{'values':[quadratic(v,3,3) for v in range(64)],'gauss':gauss(3,3),'zeros':28}},
      'quadratic_embedding_gate':[{'host_dim':D,'host_arf':a,'source_arf':s,
                        'allowed':D>6 or (D==6 and a==s)} for D in [4,6,8] for a in [0,1] for s in [0,1]],
      'transvection':qrows,
      'defect_gate':[{'a':a,'q_a':quadratic(a,1),'mismatches':sum(quadratic(transvection(v,a,1),1)^symplectic(a,transvection(v,a,1),1)!=quadratic(v,1) for v in range(4))} for a in range(4)],
      'odd_action':{'u':u,'deltas':deltas,'g_u':[c3_action(u,g) for g in range(3)],
                    'corrected':[u^deltas[g]^c3_action(u,g) for g in range(3)]},
      'even_action':{'delta_generator':1,'coboundaries':[0,0,0,0],'remaining':[1,1,1,1]},
      'projective_phase':{'modulus':9,'lift_exponents':[0,1,2],
                          'cocycle_exponents':[[3*((g+h)//3) for h in range(3)] for g in range(3)],
                          'honest_characters_mod9':[[k*3*g%9 for g in range(3)] for k in range(3)]},
      'native_certificate':{'candidate':None,'native_lifts':[None]*6,'square_bits':[None]*6,
                            'section_products':None,'honest_phases':None,'status':'not_computed'},
      'open_endpoints':{'general_realization':'open','same_candidate_H5':'open',
                         'corrected_character_occurrence':'open','independent_native_marking':'open_when_required'},
    }
