"""Declared fixture generator, separate from geometry proposal."""
from pathlib import Path
import json
import sympy as sp
from robust_reference import U,poly_matrices
ROOT=Path(__file__).resolve().parents[1]

def noisy_fixture():
    source=json.loads((ROOT/'certificates/discovered_quadratic_certificate.json').read_text())
    original={name:poly_matrices(row['operator_coefficients']) for name,row in source['actions'].items()}
    delta=sp.Rational(1,2000)
    E0=sp.Matrix([[0,0,0],[-1,2,0],[0,1,-1]])
    E1=sp.Matrix([[0,1,-1],[1,0,1],[1,-1,0]])
    E2=sp.Matrix([[0,0,0],[0,-1,1],[1,0,1]])
    noise=E0+U*E1+U**2*E2
    fitted={name:(B+delta*(1 if j==0 else -1)*noise).applyfunc(sp.expand) for j,(name,B) in enumerate(sorted(original.items()))}
    return original,fitted,sp.Matrix([1,sp.Rational(1,2),sp.Rational(1,2)]),delta

