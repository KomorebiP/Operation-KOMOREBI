# Contract review

The central parameter theorem uses the actual residual of block-10 regularized
recovery and Mathlib's actual infDist. It constructs the parameter via actual
continuity and intermediate value, not by assuming a root. No closed range is
used. Uniqueness uses strict monotonicity when A* v != 0; the target interval
excludes the constant-curve degeneracy.

The source consistency proof uses norm domination and the proved density of the
normal range in ker(A)^perp. It does NOT assume that the desired strong limit,
vanishing lambda, or noise/sqrt(lambda) behavior already holds. Exact root
selection is replaced by an allowed residual band in the broader theorem.

The small-data branch returns zero, not a parameter zero fed into an inverse.
Kernel ambiguity is retained by the projected limit and norm-error limit.

The source-rate theorem is only for g=A* w and has the bound
||x-g||^2 <= 2||w||(tau+1)eta. No uniform rate for all identifiable sources follows.

The bounded search uses exact known finite rational Euclidean models and a
positive allowance. Feasibility of some source within that allowance is checked;
the truth of a noise bound about an unknown physical source is not inferred.
The search, its cap, and JSON parser are not formally verified.

This is an integration/formalization of classical discrepancy-principle
mathematics, not a novelty certificate. No claim about arithmetic globalization,
nonlinear models, positivity or unknown-operator inference is included.
