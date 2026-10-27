#!/usr/bin/env python3
"""Exact projective wild-image data for the explicit induced cubic character.

The finite-to-Weil reduction uses local reciprocity and monomial induction,
as explained in reports/WILD_IMAGE113.md. Scalar values of a lift of sigma
cubed are deliberately not inferred from these projective data.
"""
import argparse
import contextlib
import importlib.util
import io
import json
from fractions import Fraction
from math import lcm
from pathlib import Path

root=Path(__file__).resolve().parents[1]
source=root/'evidence/arithmetic/self_twist113.py'
spec=importlib.util.spec_from_file_location('source113',source)
st=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(st)
c=st.c

def apply_sigma(a):
    # sigma(pi)=(1+pi)^4-1, evaluated in the exact cyclotomic quotient.
    xp=c.sub(c.power(c.add(c.one,c.x),4),c.one)
    total=c.zero
    for v in reversed(a):
        total=c.add(c.mul(total,xp),c.scale(c.one,v))
    return total

def closure(gens,modulus):
    values={(0,0)};pending=[(0,0)]
    while pending:
        a=pending.pop()
        for g in gens:
            b=tuple((a[i]+g[i])%modulus for i in range(2))
            if b not in values:
                values.add(b);pending.append(b)
    return values

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    rows=[];denominator=1
    for r in range(1,7):
        u=c.add(c.one,c.power(c.x,r));vals=[]
        for j in range(3):
            vals.append(c.fractional_part_3(c.trace(c.mul(c.beta,st.padic_log_mod7(u)))/3))
            u=apply_sigma(u)
        assert u==c.add(c.one,c.power(c.x,r))
        diffs=[c.fractional_part_3(vals[j]-vals[0]) for j in (1,2)]
        for x in diffs:denominator=lcm(denominator,x.denominator)
        rows.append({'unit_level':r,'character_exponents':[str(x) for x in vals],
                     'relative_exponents':[str(x) for x in diffs]})
    gens=[tuple(int(Fraction(v)*denominator)%denominator for v in row['relative_exponents']) for row in rows]
    D=closure(gens,denominator)
    beta=lambda a:(-a[1]%denominator,(a[0]-a[1])%denominator)
    assert {beta(a) for a in D}==D
    assert all(beta(beta(beta(a)))==a for a in D)
    comm=closure([tuple((beta(a)[i]-a[i])%denominator for i in range(2)) for a in D],denominator)
    fixed={a for a in D if beta(a)==a}
    result={'status':'PASS','unit_character_table':rows,'root_denominator':denominator,
        'projective_diagonal_generators':gens,'projective_diagonal_order':len(D),
        'projective_wild_image_order':3*len(D),'diagonal_commutator_subgroup_order':len(comm),
        'fixed_diagonal_order':len(fixed),'projective_image_is_abelian':len(comm)==1,
        'source_generating_reduction':'The six units generate U_L1/U_L7; all three conjugate characters have conductor7. Wild inertia modulo P_L is C3. Its lift has scalar cube, so the projective permutation generator has order3.',
        'non_claims':['No exact scalar cube or full Weil/Frobenius lift is determined.',
                      'No complete intrinsic Clifford filtration, type attachment or H5 is proved.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
