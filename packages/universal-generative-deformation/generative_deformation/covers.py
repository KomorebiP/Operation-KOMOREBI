from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .model import Direction


@dataclass(frozen=True, slots=True)
class IntervalDirectionFamily:
    """A compact continuous direction family represented by certified nets."""

    name: str
    low: Fraction
    high: Fraction
    base_cost: float = 1.0

    def net(self, level: int) -> tuple[list[Direction], Fraction]:
        if level < 0:
            raise ValueError("level must be nonnegative")
        cells = 2**level
        width = (self.high - self.low) / cells
        directions: list[Direction] = []
        for index in range(cells + 1):
            value = self.low + index * width
            directions.append(
                Direction(
                    self.name,
                    parameter={"numerator": value.numerator, "denominator": value.denominator},
                    cost=self.base_cost,
                    family=self.name,
                    resolution=float(width / 2),
                )
            )
        return directions, abs(width) / 2


def dyadic_signed_directions(depth: int, name: str = "dyadic_step") -> list[Direction]:
    step = Fraction(1, 2 ** (depth + 1))
    return [
        Direction(name, {"numerator": step.numerator, "denominator": step.denominator}),
        Direction(name, {"numerator": -step.numerator, "denominator": step.denominator}),
    ]


def fraction_from_parameter(parameter: object) -> Fraction:
    if not isinstance(parameter, dict):
        raise TypeError("fraction parameter must be a dictionary")
    return Fraction(int(parameter["numerator"]), int(parameter["denominator"]))
