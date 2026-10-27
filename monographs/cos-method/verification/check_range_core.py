#!/usr/bin/env python3
"""Exact symbolic controls for the range-core theorem and its zero-spectrum boundary."""
import sympy as s
U=s.Matrix([[1,0],[0,1/s.sqrt(2)],[0,1/s.sqrt(2)]])
B=s.Matrix([[1,0,1],[0,2,0]])
A=U*B
assert U.T*U==s.eye(2)
assert B*B.T==s.diag(2,4)
assert A*A.T==s.Matrix([[2,0,0],[0,2,2],[0,2,2]])
assert (A*A.T).eigenvals()=={s.Integer(4):1,s.Integer(2):1,s.Integer(0):1}
A0=s.Matrix([[1],[0]])
Q0=s.eye(2)
B0=Q0.T*A0
assert (B0*B0.T).eigenvals()=={s.Integer(1):1,s.Integer(0):1}
print('Exact worked example and oversized-range negative control passed.')
