"""The exact runnable example printed in Chapter 11."""
from fractions import Fraction
from src.dense_lift_groups import DenseLiftGroup, Element

G = DenseLiftGroup(lambda n: False)
u = Element.make(1)
half = Element.make(Fraction(1, 2))

assert G.scale(2, half) == Element.make(1, {2: 1})
assert G.root(u, 2).obstructing_prime == 2
third = G.root(u, 3).root
assert third is not None and G.scale(3, third) == u

x = Element.make(1, {2: 1})
sixth = G.root(x, 6).root
assert sixth is not None and G.scale(6, sixth) == x

print("PASS: printed Chapter 11 example")
