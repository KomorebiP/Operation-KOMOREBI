#!/usr/bin/env python3
"""Print exact finite data for the monograph's approximation models.

Example: python3 examples/approximation_models.py --depth 16 --steps 10
This computes rational values and analytic bounds, not an infinite-limit test.
"""
from __future__ import annotations
import argparse,json
from fractions import Fraction as F

def fraction_text(x: F | int) -> str:
    x=F(x)
    return str(x.numerator) if x.denominator==1 else f'{x.numerator}/{x.denominator}'

def positive_int(text: str) -> int:
    value=int(text)
    if not 1<=value<=4096:
        raise argparse.ArgumentTypeError('Use an integer between 1 and 4096.')
    return value

def models(depth: int, steps: int) -> dict:
    if not 1<=depth<=4096 or not 1<=steps<=4096:
        raise ValueError('depth and steps must lie between 1 and 4096')
    polynomial=[];bursts=[]
    for n in range(steps):
        polynomial.append({'n':n,'residual':fraction_text(F(1,n+1)),
                           'step':fraction_text(F(1,(n+1)*(n+2))),
                           'remaining_movement':fraction_text(F(1,n+1))})
        Q=F(1,4**(n//2))*(1 if n%2==0 else 2)
        c=F(1) if n%2==0 else F(7,8)
        tail=(F(11,3) if n%2==0 else F(8,3))*F(1,4**(n//2))
        bursts.append({'n':n,'residual':fraction_text(Q),'step':fraction_text(c*Q),
                       'remaining_movement_bound':fraction_text(tail)})
    diagonal={'N':depth,'exact_prefix':[-1]*depth,'protected_value':1,
              'next_residual':fraction_text(F(1,depth+1)),
              'squared_correction_norm':depth,'squared_candidate_norm':depth+1,
              'infinite_residual_square_lower':fraction_text(F(1,depth+1)),
              'infinite_residual_square_upper':fraction_text(F(1,depth)),
              'finite_diagonal_inverse_gain':depth,
              'interpretation':'Tail endpoints are proved bounds. The all-minus-one infinite sequence is not square summable.'}
    G=[(0,0),(1,0),(0,1),(1,1)]
    return {'polynomial_path':polynomial,'burst_path':bursts,'diagonal_model':diagonal,
            'phase_labels':G,'phase_table':[[x[1]*y[0]%2 for y in G] for x in G],
            'scope':'Exact finite formulas and proved tail bounds. This is not a Lean proof, an infinite numerical experiment, or a general reconstruction solver.'}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--depth',type=positive_int,default=8)
    parser.add_argument('--steps',type=positive_int,default=8)
    args=parser.parse_args()
    print(json.dumps(models(args.depth,args.steps),indent=2))

if __name__=='__main__':main()
