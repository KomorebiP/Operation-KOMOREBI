from __future__ import annotations

import sympy as sp

x, y = sp.symbols("x y")


def elliptic_reduce(expression: sp.Expr) -> sp.Expr:
    """Reduce modulo y^2 = x^3 - x to a(x) + y b(x)."""
    poly = sp.Poly(sp.expand(expression), y, domain=sp.QQ[x])
    relation = sp.Poly(y**2 - x**3 + x, y, domain=sp.QQ[x])
    return sp.expand(sp.rem(poly, relation).as_expr())


def elliptic_product(a0: sp.Expr, a1: sp.Expr, b0: sp.Expr, b1: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    """Multiply (a0 + y a1)(b0 + y b1) in the elliptic coordinate ring."""
    even = sp.expand(a0 * b0 + (x**3 - x) * a1 * b1)
    odd = sp.expand(a0 * b1 + a1 * b0)
    return even, odd


def elliptic_packet_matrix(operator: str) -> sp.Matrix:
    """Formal 2x2 packet matrix for multiplication by x or y."""
    if operator == "x":
        return sp.Matrix([[x, 0], [0, x]])
    if operator == "y":
        return sp.Matrix([[0, x**3 - x], [1, 0]])
    raise ValueError("operator must be 'x' or 'y'")
