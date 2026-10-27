# Komorebi Derived Residual Reflection

For a sized residual system `S` and cardinal `κ`, define

    KRR_κ(S) :=
      not Exact(S) -> exists q : Nat, exists J,
        size(J) < κ and Obstruct(S,q,J).

Its depth-zero restriction is

    KRR0_κ(S) :=
      not Exact(S) -> exists J,
        size(J) < κ and Obstruct(S,0,J).

The formal development proves:

    KRR0_κ(S) -> KRR_κ(S).

If every higher-depth obstruction on a `< κ` piece can be replaced by a depth-zero
obstruction on another `< κ` piece, then

    KRR_κ(S) <-> KRR0_κ(S).

Thus any strict separation forces both:

    exists q > 0, exists J, size(J) < κ and Obstruct(S,q,J),

and failure of flattenability.

For an abstract logic `L`, let residual pieces be subtheories and let a depth-zero
obstruction mean "this subtheory is unsatisfiable."  Lean proves the generic theorem

    KRR0Schema(L, κ) <-> KappaCompact(L, κ).

Hence the depth-zero part of the program is ordinary logical compactness in a residual
presentation.  The foundational question is now precise:

> Does there exist a mathematically natural admissible class of residual systems for
> which finite positive-depth residual reflection cannot be flattened to depth zero,
> and what is the consistency strength of that principle over ZFC?

The next natural comparison target is `L_{κ,κ}`.  The current Mathlib snapshot does not
supply a ready-made strongly compact cardinal API, so that comparison requires a new
formal block rather than an invocation of an existing theorem.
