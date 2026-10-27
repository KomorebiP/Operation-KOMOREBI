from __future__ import annotations

from fractions import Fraction
from typing import Any, Hashable, Iterable, Mapping, Sequence

import sympy as sp

from .covers import dyadic_signed_directions, fraction_from_parameter
from .model import (
    DeformationSystem,
    Direction,
    InteractionRule,
    InteractionSystem,
    JSONValue,
    ValidationResult,
)


class IntegerWalkSystem(DeformationSystem):
    name = "integer-walk"

    def directions(self, state: int, depth: int) -> Iterable[Direction]:
        return [Direction("plus_one"), Direction("minus_one")]

    def apply(self, state: int, direction: Direction) -> int:
        if direction.name == "plus_one":
            return int(state) + 1
        if direction.name == "minus_one":
            return int(state) - 1
        raise KeyError(direction.name)

    def canonical_key(self, state: int) -> Hashable:
        return int(state)

    def invariants(self, state: int) -> Mapping[str, JSONValue]:
        value = int(state)
        return {"value": value, "parity": value % 2, "absolute_value": abs(value)}

    def serialize_state(self, state: int) -> JSONValue:
        return int(state)

    def distance(self, left: int, right: int) -> float:
        return float(abs(int(left) - int(right)))


class DyadicLimitSystem(DeformationSystem):
    name = "dyadic-limit"

    def directions(self, state: Fraction, depth: int) -> Iterable[Direction]:
        return dyadic_signed_directions(depth)

    def apply(self, state: Fraction, direction: Direction) -> Fraction:
        return Fraction(state) + fraction_from_parameter(direction.parameter)

    def canonical_key(self, state: Fraction) -> Hashable:
        value = Fraction(state)
        return value.numerator, value.denominator

    def invariants(self, state: Fraction) -> Mapping[str, JSONValue]:
        value = Fraction(state)
        return {
            "numerator": value.numerator,
            "denominator": value.denominator,
            "absolute_value": float(abs(value)),
        }

    def serialize_state(self, state: Fraction) -> JSONValue:
        value = Fraction(state)
        return {"numerator": value.numerator, "denominator": value.denominator}

    def distance(self, left: Fraction, right: Fraction) -> float:
        return float(abs(Fraction(left) - Fraction(right)))


class PolynomialDeformationSystem(DeformationSystem):
    name = "polynomial-deformation"

    def __init__(self, symbol: sp.Symbol | None = None, max_degree: int = 7) -> None:
        self.x = symbol or sp.Symbol("x")
        self.max_degree = max_degree

    def directions(self, state: sp.Expr, depth: int) -> Iterable[Direction]:
        return [
            Direction("differentiate"),
            Direction("multiply_x"),
            Direction("shift_plus_one"),
            Direction("reflect"),
            Direction("finite_difference"),
        ]

    def apply(self, state: sp.Expr, direction: Direction) -> sp.Expr:
        x = self.x
        expression = sp.expand(state)
        if direction.name == "differentiate":
            child = sp.diff(expression, x)
        elif direction.name == "multiply_x":
            child = x * expression
        elif direction.name == "shift_plus_one":
            child = expression.subs(x, x + 1)
        elif direction.name == "reflect":
            child = expression.subs(x, -x)
        elif direction.name == "finite_difference":
            child = expression.subs(x, x + 1) - expression
        else:
            raise KeyError(direction.name)
        return sp.expand(child)

    def validate(self, state: sp.Expr) -> ValidationResult:
        try:
            polynomial = sp.Poly(sp.expand(state), self.x)
        except sp.PolynomialError:
            return ValidationResult(False, "state is not polynomial")
        degree = polynomial.degree()
        if degree is sp.S.NegativeInfinity:
            degree = -1
        if int(degree) > self.max_degree:
            return ValidationResult(False, f"degree {degree} exceeds cap {self.max_degree}")
        return ValidationResult(True, "")

    def canonical_key(self, state: sp.Expr) -> Hashable:
        polynomial = sp.Poly(sp.expand(state), self.x)
        degree = polynomial.degree()
        degree_value = -1 if degree is sp.S.NegativeInfinity else int(degree)
        return tuple(sp.srepr(value) for value in polynomial.all_coeffs()), degree_value

    def invariants(self, state: sp.Expr) -> Mapping[str, JSONValue]:
        polynomial = sp.Poly(sp.expand(state), self.x)
        degree = polynomial.degree()
        if degree is sp.S.NegativeInfinity:
            degree_value = -1
        else:
            degree_value = int(degree)
        return {
            "degree": degree_value,
            "leading_coefficient": str(polynomial.LC()),
            "constant_coefficient": str(polynomial.TC()),
            "term_count": len(polynomial.terms()),
        }

    def serialize_state(self, state: sp.Expr) -> JSONValue:
        return str(sp.expand(state))


class AnalyticExpressionSystem(DeformationSystem):
    name = "analytic-expression"

    def __init__(self, symbol: sp.Symbol | None = None, operation_cap: int = 300) -> None:
        self.x = symbol or sp.Symbol("x")
        self.operation_cap = operation_cap

    def directions(self, state: sp.Expr, depth: int) -> Iterable[Direction]:
        directions = [
            Direction("differentiate"),
            Direction("reciprocal"),
            Direction("log_derivative"),
            Direction("square"),
            Direction("even_projection"),
            Direction("odd_projection"),
        ]
        if depth <= 1:
            directions.append(Direction("double_argument"))
        return directions

    def _canonical_expr(self, expression: sp.Expr) -> sp.Expr:
        expression = sp.trigsimp(sp.simplify(expression))
        return sp.factor(expression)

    def apply(self, state: sp.Expr, direction: Direction) -> sp.Expr:
        x = self.x
        expression = self._canonical_expr(state)
        if direction.name == "differentiate":
            child = sp.diff(expression, x)
        elif direction.name == "reciprocal":
            if expression == 0:
                raise ZeroDivisionError("zero has no reciprocal")
            child = 1 / expression
        elif direction.name == "log_derivative":
            if expression == 0:
                raise ZeroDivisionError("zero has no logarithmic derivative")
            child = sp.diff(expression, x) / expression
        elif direction.name == "square":
            child = expression**2
        elif direction.name == "even_projection":
            child = (expression + expression.subs(x, -x)) / 2
        elif direction.name == "odd_projection":
            child = (expression - expression.subs(x, -x)) / 2
        elif direction.name == "double_argument":
            child = expression.subs(x, 2 * x)
        else:
            raise KeyError(direction.name)
        return self._canonical_expr(child)

    def validate(self, state: sp.Expr) -> ValidationResult:
        try:
            operations = int(sp.count_ops(state))
        except Exception as exc:
            return ValidationResult(False, f"cannot count operations: {exc}")
        if operations > self.operation_cap:
            return ValidationResult(False, f"expression complexity {operations} exceeds cap")
        if state.has(sp.zoo, sp.nan):
            return ValidationResult(False, "expression contains an invalid symbolic value")
        return ValidationResult(True, "")

    def canonical_key(self, state: sp.Expr) -> Hashable:
        return sp.srepr(self._canonical_expr(state))

    def invariants(self, state: sp.Expr) -> Mapping[str, JSONValue]:
        x = self.x
        simplified = self._canonical_expr(state)
        even = sp.simplify(simplified.subs(x, -x) - simplified) == 0
        odd = sp.simplify(simplified.subs(x, -x) + simplified) == 0
        return {
            "operation_count": int(sp.count_ops(simplified)),
            "even": bool(even),
            "odd": bool(odd),
            "has_hyperbolic": any(simplified.has(function) for function in (sp.sinh, sp.cosh, sp.tanh)),
        }

    def serialize_state(self, state: sp.Expr) -> JSONValue:
        # States are canonicalized when they are created.  Re-running full
        # trigonometric factorization during export can be arbitrarily costly.
        return str(state)


class ScalarInteractionSystem(InteractionSystem):
    def admissible(self, rule: InteractionRule, states: Sequence[Any]) -> bool:
        return len(states) == rule.arity and rule.name in {"add", "multiply", "average"}

    def apply_interaction(self, rule: InteractionRule, states: Sequence[Any]) -> Any:
        if rule.name == "add":
            return sum(states)
        if rule.name == "multiply":
            result = 1
            for state in states:
                result *= state
            return result
        if rule.name == "average":
            return sum(states) / len(states)
        raise KeyError(rule.name)


def catalan_numbers(count: int) -> list[int]:
    if count < 0:
        raise ValueError("count must be nonnegative")
    values = [1]
    for n in range(count):
        values.append(sum(values[k] * values[n - k] for k in range(n + 1)))
    return values


def fibonacci_numbers(count: int) -> list[int]:
    if count < 0:
        raise ValueError("count must be nonnegative")
    values: list[int] = []
    a, b = 0, 1
    for _ in range(count):
        values.append(a)
        a, b = b, a + b
    return values
