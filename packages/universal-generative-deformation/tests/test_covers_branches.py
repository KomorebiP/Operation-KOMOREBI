from fractions import Fraction

from generative_deformation import DyadicLimitSystem, IntervalDirectionFamily, follow_branch
from generative_deformation.covers import fraction_from_parameter


def test_interval_net_radius_halves() -> None:
    family = IntervalDirectionFamily("shift", Fraction(-1), Fraction(1))
    _, radius_2 = family.net(2)
    _, radius_3 = family.net(3)
    assert radius_3 == radius_2 / 2


def test_interval_net_covers_endpoints() -> None:
    family = IntervalDirectionFamily("shift", Fraction(-1), Fraction(1))
    directions, radius = family.net(3)
    values = [fraction_from_parameter(direction.parameter) for direction in directions]
    assert values[0] == -1
    assert values[-1] == 1
    assert radius == Fraction(1, 8)


def test_dyadic_positive_branch_converges_to_one() -> None:
    system = DyadicLimitSystem()

    def select_positive(state, depth, directions):
        return directions[0]

    states, _ = follow_branch(system, Fraction(0), select_positive, 20)
    assert abs(float(states[-1]) - 1.0) <= 2 ** -20


def test_dyadic_alternating_branch_is_cauchy() -> None:
    system = DyadicLimitSystem()

    def select_alternating(state, depth, directions):
        return directions[depth % 2]

    states, _ = follow_branch(system, Fraction(0), select_alternating, 20)
    assert abs(float(states[-1] - states[-2])) <= 2 ** -20
