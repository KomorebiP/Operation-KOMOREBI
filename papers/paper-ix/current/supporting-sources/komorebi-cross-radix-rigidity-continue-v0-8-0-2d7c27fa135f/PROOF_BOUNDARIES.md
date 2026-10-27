# Proof Boundaries — v0.8.0

## Certified meaning
A v0.8 claim is certified only when its exact statement occurs in saved `src/` and the module passes the pinned strict Lean gate. Narrative does not promote theorem strength.

## Bell boundary
Bell's generalized Cobham theorem remains external. `BellDownstreamInterface` is a normalized downstream contract, not Bell's theorem. Bell Theorem 1.5 is used only in its checked integer-valued scope, and the root-of-unity rational-generating-function to eventual quasi-polynomial normalization remains external.

## Absolute orbit-hull boundary
`ProfileOrbitHull T d P` is absolutely minimal among complex-linear bounded-profile submodules containing `P` and invariant under all positive affine profile sections. This is a theorem inside the declared finite profile space; it is not a universal normal-form theorem for arbitrary mathematical objects.

## Shell–jet boundary
`ShellJetEnvelope hT H` is the smallest shell/jet zero-mask submodule containing `H`. It is **not** asserted to be section-invariant.

`InvariantShellJetEnvelope hT H` is the smallest shell/jet zero-mask submodule that both contains `H` and is invariant under all positive affine profile sections. Its support is currently defined abstractly as an intersection of all admissible invariant supports. v0.8 does not yet prove an explicit divisor-upward / jet-downward formula for that support.

Shell-level minimality and absolute linear minimality are distinct: a shell contains multiple Fourier frequencies, so shell saturation can be strictly larger than the absolute orbit hull.

## Sequence-hull boundary
`OrbitCommonHull N T d P` retains the entire `N`-dimensional transient prefix space. Its minimality theorem is absolute only **under this full-prefix-retention convention**. It does not claim that every particular sequence needs all `N` transient coordinates.

## Rank/nullity scope
v0.6's rank/nullity theorem remains restricted to the saved finite complex degree-bounded projector-factorized affine section normal form; it is not identified with an unsaved stronger root-aggregation operator.

## Integral boundary
The naive base-independent integral normal form remains false and rejected. Future integral work must retain localized Smith/Fitting/radix-local defects.

## Novelty boundary
Lean certification establishes the formal statements relative to imports and explicit hypotheses. It does not establish literature novelty, publication priority, or peer review.
