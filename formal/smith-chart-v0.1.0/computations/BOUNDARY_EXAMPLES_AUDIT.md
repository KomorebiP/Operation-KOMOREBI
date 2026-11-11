# Smith chart boundary examples: self-review

This reviews the written arguments and finite witnesses added to the Smith
chart guide. It is not an independent review. The later Lean continuation
is reviewed separately in [BOUNDARY_FORMAL_AUDIT.md](../BOUNDARY_FORMAL_AUDIT.md). The
[bounded computation record](boundary-examples-004/manifest.json) hashes the
guide, workbench markup, checker, and contract as they stood during the run.
Its repository field records the base commit and a dirty working tree.

## Cyclic reachability

**Claim.** For an integer \(N\geq1\) and nonzero complex \(\Gamma_0\), a
target is \(e^{2\pi ik/N}\Gamma_0\) for some integer \(k\) if and only if
\((\Gamma_*/\Gamma_0)^N=1\). If \(\Gamma_0=0\), only zero is reachable.

**Self-review verdict: proved as written.** The forward direction follows by
raising the phase to the \(N\)th power. The complex roots of \(w^N=1\) are
exactly the \(N\) canonical phases. The zero case is immediate. The guide's
positive-real impedance action starts inside the disk, so its inverse Cayley
denominator is nonzero. The exact-order root used in the existing companion
is separately covered by SmithCanonicalRoot.lean; the reachability
equivalence and zero case are now proved in SmithBoundaries.lean.

For a uniform lossless line with characteristic impedance equal to the fixed
real reference, the phase factor has modulus one. Thus a nonzero reflection
coefficient cannot become zero by varying that line's length. This says
nothing about the feasibility of a different matching network.

## Finite-sample nonidentifiability

**Claim.** For any finite list of \(M\geq1\) sample points strictly inside the
unit disk, there are two distinct analytic functions with positive real part
on the disk that agree at every listed point.

**Self-review verdict: proved as written.** Let the first function be \(1\)
and the second be \(1+\varepsilon\prod(t-t_m)\), where
\(\varepsilon=2^{-(M+1)}\). The product is a nonzero monic polynomial of
degree \(M\), so the functions differ. It vanishes at every sample. On the
open unit disk, each \(|t-t_m|<2\), so the perturbation has modulus below
\(1/2\) and the second function has real part greater than \(1/2\).
Repeated sample points do not change the argument.

This concerns analytic functions of the reflection coordinate. It does not
assert realizability as a passive circuit over frequency or nonidentifiability
within a specified finite-dimensional model. The checker and
SmithBoundaries.lean verify the indicated parts of the two-point witness;
the arbitrary-finite-sample statement rests on the written argument above.

## Other boundaries and computation

- SmithExamples.lean checks the totalized pole, an order-one character used
  at order two, and failure of the odd-order admittance shortcut.
  SmithResults.lean checks the negative-real nonzero packet witness.
- The noncoprime 2/4 coefficient-level projector example is also a Lean
  counterexample. Its numerical value and cancellation at \(-99/100\)
  are exact rational checks in the companion script.
- The interpolation comparison uses 32 specified nodes and 65,536 test
  angles. Its maxima are finite binary64 scan results, not continuous-domain
  error bounds. Equal-mass boundary nodes used in the scan differ from the
  mass-midpoint nodes displayed by the overlay.
- Source-to-proof mapping and this audit are self-review. The record does not
  certify the browser's floating-point implementation, hardware performance,
  or claims that might appear only in the inaccessible later conversation.
