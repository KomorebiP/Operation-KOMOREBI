# Contract review — v0.8.0

The 82 added theorems were checked against the intended mathematical statements.
The core inverse is constructed, not supplied. `restricted_surjective` takes a
preimage in the ACTUAL range and projects it to ker(A)^perp. Banach's open mapping
theorem makes its inverse continuous. The public constructor takes IsClosed of
range(A), not density or closure(range(A)).

The closed-range equivalence quantifies over bounded recovery operators. It does
not exclude unbounded inverses in a weaker setting. The backward direction from
coercivity uses a complete source complement and an anti-Lipschitz image.

`unique_minimum_norm_least_squares` selects among all best-fit sources. It is not
full source uniqueness. `noisy_source_error_sq` explicitly retains P_ker(A)g.
The alpha lower bound is for A, while sigma is for delta. Fixed-map continuity
is proved; continuity of the inverse AS A CHANGES RANK is not asserted.

The scalar inverse example is proved for every nonzero real c. The zero-map
example is separate. No float test or sampled residual is used in a theorem.
Source norms are Euclidean/Hilbert norms, not arbitrary arbitrary user weights.

Projection symmetry is stated in inner-product form, not as an extra equality of
Mathlib adjoint objects. The four Penrose conditions hold in this form.

No new axiom, excluded edge case, or weakened conclusion was added to repair a
compiler error. Probe failures involved API names and warning-fatal syntax only.
