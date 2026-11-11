"""Exact symbolic checks for singular prediction and real two-packet feasibility.

These identities verify the examples and boundary algebra in the accompanying
note. The quantified block-matrix argument is a written proof, not a finite test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform

import sympy as S


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    x,y=S.symbols('x y',real=True)
    P=S.Matrix([[S.Rational(4,3)*(1-(x+y)**2),S.Rational(4,5)*(1-x*x+y*y)],
                [S.Rational(4,5)*(1-x*x+y*y),S.Rational(4,3)*(1-(x-y)**2)]])
    expected=S.Rational(64,225)*(2*x*x-2*y*y-5*y-2)*(2*x*x-2*y*y+5*y-2)
    assert S.expand(P.det()-expected)==0
    assert S.factor(P.det().subs(y,S.Rational(1,2)))==S.Rational(128,225)*x*x*(2*x*x-5)
    bound=(5-S.sqrt(9+16*x*x))/4
    assert S.simplify((2*x*x-2*y*y+5*y-2).subs(y,bound))==0
    assert bound.subs(x,0)==S.Rational(1,2) and bound.subs(x,1)==0
    nodes=[S.Rational(1,2),-S.Rational(1,2)]
    values=nodes[:]
    old=S.Matrix([[(1-v*S.conjugate(w))/(1-t*S.conjugate(u))
                   for u,w in zip(nodes,values)] for t,v in zip(nodes,values)])
    assert old==S.ones(2)
    zeta=S.I/3
    wr,wi=S.symbols('wr wi',real=True);w=wr+S.I*wi
    b=S.Matrix([(1-v*S.conjugate(w))/(1-t*S.conjugate(zeta)) for t,v in zip(nodes,values)])
    n=S.Matrix([1,-1])
    residual=S.simplify((n.T*b)[0])
    assert S.simplify(residual+S.Rational(36,37)*(S.conjugate(w)+S.I/3))==0
    assert S.solve([S.re(residual),S.im(residual)],(wr,wi))=={wr:0,wi:S.Rational(1,3)}
    def augmented(value):
        nodes3=nodes+[zeta];values3=values+[value]
        return S.Matrix([[(1-v*S.conjugate(q))/(1-t*S.conjugate(u))
                          for u,q in zip(nodes3,values3)] for t,v in zip(nodes3,values3)])
    assert augmented(S.I/3).applyfunc(S.simplify)==S.ones(3)
    q=S.Matrix([1,-1,-S.I/4])
    negative=S.simplify((S.conjugate(q).T*augmented(0)*q)[0])
    assert negative==-S.Rational(435,4736)
    # Exact points on both sides of the real-packet boundary, including its
    # singular tip. These are examples, not a replacement for the inequalities.
    examples=[]
    for a,bvalue,feasible in [(0,S.Rational(1,2),True),(S.Rational(1,10),S.Rational(1,2),False),
                              (S.Rational(1,10),S.Rational(49,100),True),(1,0,True),
                              (S.Rational(3,4),S.Rational(1,4),False)]:
        m=P.subs({x:a,y:bvalue});minors=[m[0,0],m[1,1],S.factor(m.det())]
        assert all(v>=0 for v in minors)==feasible
        examples.append({'p0':str(a),'p1':str(bvalue),'feasible':feasible,'principal_minors':list(map(str,minors))})
    record={'status':'PASS','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python':platform.python_version(),'sympy':S.__version__,
            'singular_example':{'nodes':['1/2','-1/2'],'values':['1/2','-1/2'],'query':'i/3',
                                'forced_value':'i/3','wrong_value':'0','negative_quadratic_form':str(negative)},
            'real_two_packet_boundary':'|p0| <= 1 and |p1| <= (5-sqrt(9+16*p0^2))/4',
            'examples':examples,
            'scope':'Symbolic identities and exact examples for the written proof; no general noisy partial-data or physical circuit theorem.'}
    data=json.dumps(record,indent=2)+'\n'
    if args.output:
        with args.output.open('x',encoding='utf-8',newline='\n') as stream:stream.write(data)
    print(data,end='')


if __name__=='__main__':main()
