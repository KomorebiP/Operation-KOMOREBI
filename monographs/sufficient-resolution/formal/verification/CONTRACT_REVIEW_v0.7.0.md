# Contract review — block 07

**Komorebi P. · 13 September 2026**

The actual principal signatures are printed in PRINCIPAL_SIGNATURES_v0.7.0.log.
All new definitions are noncomputable classical mathematical constructions unless
otherwise stated. No new axiom, placeholder, or numerical tolerance enters them.

## Decomposition and the genuine quotient

For real inner-product local space V, R <= K, and actual orthogonal projections,
the three maps are P_R, P_K-P_R, and I-P_K. They have the stated ranges, are mutually
orthogonal, sum to the identity, and uniquely determine the components of each v.
Metric.infDist is Mathlib's actual metric infimum distance, not a newly defined
name for the norm of the residual. The proof identifies it with the projection
residual and proves the squared-distance identity.

For A:G->V and a continuous linear compatibility map delta:V->W, delta*A=0 gives
range(A)<=ker(delta). The obstruction quotient is the actual block-01
Globalization.ObstructionSpace, not a newly named copy of the harmonic space.
obstructionEquivHarmonic constructs maps in both directions and their inverse laws.
It is a linear equivalence. A norm or isometry theorem on the quotient is not claimed.

## Realizability and uniqueness

Every nearest realized vector is A(g) for some actual global g. Nearest IMAGE is
unique, but global preimages need not be. finite_unique_best_preimage separately
assumes injectivity of A. No source-space norm, bounded right inverse or canonical
minimum-norm preimage is constructed in this block.

In infinite-dimensional Hilbert V, closed_range_best_global states closedness of
range(A) explicitly. Distance zero is not silently equated with actual membership
for an arbitrary nonclosed range. The general projection contract and the
closed-range specialization do not automatically solve nonclosed-range problems.

## Conditioning and exactness

CoerciveOffKernel(delta,sigma) means a whole-map bound
sigma*||x|| <= ||delta x|| for EVERY x orthogonal to ker(delta).
The quantitative theorem separately requires sigma>0. It gives

dist(v,range(A))^2 <= ||obstruction(v)||^2 + (||delta v||/sigma)^2.

Finite local dimension supplies SOME sigma>0, including a zero-dimensional
complement. This does not calculate the smallest singular value, guarantee good
conditioning, or provide a constant uniform over varying maps. No finiteness of
G or W is needed for this existence result.

A residual-only bound at all vectors forces range(A)=ker(delta). In finite local
dimension, exactness also suffices for some positive bound, yielding the iff.
The pure-obstruction and degenerating-scalar examples prove the two independent
reasons that an unrestricted residual-only certificate can fail.

## Refinement and perturbations

The refinement hypotheses are R0 <= R1 <= K, with K and the inner product FIXED.
Squared error and squared obstruction drop by exactly ||(P_R1-P_R0)v||^2.
This is not a theorem about arbitrary moving atlases, altered compatibility tests,
or untracked changes of metric. Each fixed component map is nonexpansive in v.

## Rational executable contract

hilbert_certificate.py uses fractions.Fraction for known rational Euclidean A,
delta, v with delta*A=0. It computes projectors from exact bases, an actual global
preimage, and a PSD certificate for a SQUARED off-kernel coercivity constant.
Its default constant is conservative and derived from a finite inverse witness
and its Frobenius norm. It does not evaluate floating singular values.
The Schur-complement PSD checker is cross-checked against an independent all-
principal-minors test in the bounded suite. The parser, elimination algorithms,
and PSD checker are NOT themselves formally verified Lean programs.

check_hilbert_globalization.py is deterministic (seed 20260913), tests local
dimensions 0 through 6 over 42 systems and 336 vectors, and records 5729 exact
assertions, 37 rejected corrupted/invalid inputs and 100 PSD cross-comparisons.
These bounds are evidence for the tested implementation, not a source of the
universal Lean theorems.

## Non-claims

No positive/stochastic/integral/arithmetic admissible realization follows merely
from the unconstrained linear projection. No historical novelty, independent
proof-kernel implementation, verified JSON parser, or whole-program completion
percentage is claimed. Imported Lean/Mathlib compiled artifacts are reused.
