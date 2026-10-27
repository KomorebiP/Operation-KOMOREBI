# Literature check

Question: which underlying geometric-sum identities are standard, and what is
actually newly established in this branch? No historical-priority claim is made.

Primary formal source checked: Mathlib.Algebra.Ring.GeomSum and
Mathlib.Algebra.Field.GeomSum, in the local pinned Mathlib repository at
 aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Used statements include geom_sum_mul and geom_sum_eq. The latter says
sum_(j<d) a^j=(a^d-1)/(a-1) for a!=1 over a division ring.
The characteristic-p specialization also uses the pinned sub_pow_char theorem.

Online official documentation inspected during this turn:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Ring/GeomSum.html
https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Field/GeomSum.html

The online pages may advance beyond the pinned version. Actual compilation uses
the pinned local sources/cache, not the changing documentation as an axiom.
The scalar geometric-sum and first-order matrix power-map mechanisms are known.
The release's evidence is the exact checked integration with the existing
square-zero kernel, norm-matching class, continuous criterion and examples.
This was not a comprehensive novelty search and supplies no universal arithmetic
vanishing or local-field comparison.
