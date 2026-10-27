# First-release finish line

Author: Komorebi P. Release: Certified Inference Core 1.0.0.

The finished contract is finite-dimensional inference for one observation update,
with exact rational factor-coded model data, positive noise floor, fixed complete
self-adjoint rational packet families, positive rational posterior tolerance, and
positive rational output-radius tolerance. A supplied output-packet seed and scan
cover the finite label set. The mathematical program returns a represented gain,
a checked posterior Wasserstein tolerance, and parameter intervals of its Joseph
Gaussian. Singular priors and rectangular observation operators are supported.

The canonical entry point is Komorebi.CachedPosterior.runCached. Its iterative
updates and cached quantities are exact rational. Final verification and parameter
output use outward-rounded dyadic operations. The retained v11 solver is a separate
branch with genuinely rounded full-gain updates and its own termination theorem.

Completed release obligations:

1. An actual solver, sound successful returns, and guaranteed success for positive
   tolerances under the declared hypotheses.
2. Cached residual/energy invariants and equality with the original greedy gains.
3. Computable iteration fuel, verification precision, and output precision.
4. A narrow, inspectable input/output and arithmetic boundary.
5. Bounded full-cost reference measurements, including exported certificate checks.
6. A clean active-source rebuild and complete axiom audit, with preserved failures.
7. A bounded primary-source literature comparison and conservative attribution.

The Python producer and exporter are useful reference tools. Their parser and
implementation are not universally refined to the Lean program. An exported
instance certifies the explicit rational data in that Lean source. This is why
Python success is labeled provisional. Resource caps can return RESOURCE_LIMIT;
mathematical finite termination does not promise completion on bounded hardware.

Output intervals enclose the mean/covariance of the certified approximation. They
do not certify a separate Gaussian formed from the interval centers, and delta is
not an exact-posterior coordinate error bound. No sampler is part of this release.

Remaining capabilities belong to explicitly separate extensions: rounded selective
updates and approximate selection, hierarchy-changing refinement, large-scale
implementations, sequential filtering, uncertain inputs, parser refinement, hardware
floating point and sampling. Literature priority and practical superiority remain
unestablished. Their absence does not leave the declared theorem conditional.

The new rounded-selective route was assessed rather than silently claimed closed.
A checked counterexample shows independently rounding gain and cached residual
centers breaks the cache invariant. The independent final verifier still rejects
that false internal convergence signal. A future rounded cache must carry and
propagate error bounds, not reuse the exact-cache invariant without proof.
