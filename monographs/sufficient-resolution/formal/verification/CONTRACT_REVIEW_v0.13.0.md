# Block 13 contract review

The new statements refer to the inherited constructed Tikhonov normal operator,
resolvent, and regularizer. They do not assume the candidate source solves the
normal equation. Normal residuals, fitting norms, and source norms are actual maps
and Hilbert norms, not replacement definitions with desired values.

The image tolerance uses the proved sharp 1/(2√λ) bound. Its proof applies the normal
energy identity and Cauchy–Schwarz, then completes a square. The source tolerance
uses 1/λ. These different roles must not be conflated.

A source is near-accepted only after a witness for the inherited discrepancy rule is
constructed. Measured fitting errors and normal-residual effects each consume a
margin at both ends of the interval. Window feasibility does not establish existence
of a full source certificate. The no-closed-range consistency theorem follows by
comparison with actual accepted exact witnesses, not from pointwise numeric tests.

The positive certificate's squared comparisons are connected to the original norm
via nonnegativity hypotheses. Approximate evaluations of the normal residual have
an additional envelope; this does not allow arbitrary unknown forward operators.

Strong limits are fixed-operator, fixed-source results. They do not imply uniform
convergence over all sources. The true noise allowance is assumed valid; the finite
checker cannot verify that relation for an unknown true source. Source-correction
budgets tend to zero; raw normal residuals alone need not suffice. A fixed zero-map
counterexample and two margin-omission examples establish these boundaries in Lean.

The inherited regularization and discrepancy ideas are classical. This release is
a checked integration and extension of this program, not a novelty or priority audit.
