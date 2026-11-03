# Route and compiler corrections for SF-LEAN-B03

The selected route proves entire existence by propagating absolute convergence
through the coefficient recurrence. It replaces the planned primitive/gluing
construction with the same mathematical extension conclusion for the already
defined sums. The primitive/gluing route and a direct asymptotic coefficient
estimate remain deferred alternatives; neither is refuted or exhausted.

The first compile exposed two implementation issues: an arbitrary inequality
was sent to a positivity tactic that accepts only positivity goals, and an
unconstrained higher-order Cauchy-product application exhausted elaboration
heartbeats. The bound was written as an explicit multiplication inequality,
and the complex series arguments were supplied explicitly. No mathematical
hypothesis was added to resolve either issue.

Further compile corrections supplied the current type parameter name for
`Nat.cast_nonneg`, converted ball membership before applying an order lemma,
removed an unused cast-normalization tactic, and normalized the natural-number
cast in a shifted derivative term. These were API and type-coercion changes.
The final production source compiles with warnings treated as errors.

The proof contains no placeholder, new custom axiom, unsafe construction or
native decision procedure. Deliberately invalid fixtures are isolated under
`lean/entire_controls/` and required to fail. The clean full verification
receipt, rather than the scratch compiler runs, binds the final accepted source.
