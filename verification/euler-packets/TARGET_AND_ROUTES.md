# Euler packets: target and executed routes

**Checkpoint EULER-CASE-001 · 29 October 2026**

Base collection revision: `3a9b5f89883fbf24247410a56519045e809fbd1a`.
Owner and reviewer: Codex in this chat. No delegated or independent review.

## Target contract

Produce a substantial, readable worked example connecting classical Euler/secant
numbers, Paper IV reciprocal-power polynomials, residue packets, exact residual
repair, and the existing Euler/signal transfer. Supply full algebraic derivations,
explicit hand calculations, countercontrols, and executable exact verification.
Publish it as a companion to the machine-native mathematics essay.

The setting is formal power series over Q and polynomial coefficient extensions,
with declared finite jets for computations. Sequence indices, ordinary powers,
exponential normalization, signed Euler numbers, and positive secant numbers must
remain distinct. The difference-operator part acts on one-sided integer
sequences through the forward shift. It makes no convergent Fourier-transform
claim for the growing Euler sequence.

Success requires the written proofs to type correctly and close, the independent
coefficient routes to agree in recorded finite ranges, every printed calculation
to be reproduced, and the published downloads to match the accepted source.
It does not require or assert a new Euler identity, new OEIS entry, exclusive
method, universal Euler congruence, speedup, or Lean formalization.

## Route A: scalar reciprocal and polynomial coefficients

- Mechanism: invert the formal unit D_N and differentiate D_N^(-r).
- First uncertainty: agreement of compressed EGF indexing with ordinary products.
- Discriminator: rational Cauchy/binomial inversion versus the derivative recurrence,
  including negative, zero and fractional reciprocal parameters.
- Executed outcome: the first exploration passed; the accepted bounded run records
  the final ranges and hashes. The written recurrence and parameter-addition law
  have direct coefficient proofs.
- Disposition: complete for this example. Analytic growth and numerical error
  estimates are outside the target.

## Route B: packet determinant and failed coarsening

- Mechanism: identify Q[[t^2]] with Q[[u]]^2, u=t^4, and transfer multiplication
  by cos(t) to the two-by-two matrix with the required u carry.
- First uncertainty: determinant scaling and the 4^k factor in the quartic bridge.
- Discriminator: compute both packet equations, the determinant, and the ordinary
  inverse independently. Deliberately omit the second packet or its carry.
- Executed outcome: the correct matrix recovers both secant packets. The coarsened
  inverse already gives -1 instead of 5 in the degree-four EGF numerator. The
  witness (0,1) proves that the first packet alone is not closed under the operator.
- Disposition: complete as a worked algebraic construction and obstruction.
  The bridge is a corollary of classical generating functions, not a novelty claim.

## Route C: exact residual correction

- Mechanism: B -> B(2-DB), with residual 1-DB squaring in a commutative ring.
- First uncertainty: finite-precision truncation being mistaken for an analytic bound.
- Discriminator: calculate in Q[t]/(t^32), record residual orders 2,4,8,16 and
  at least 32, and compare every certified coefficient with direct inversion.
- Executed outcome: exact residual identity and coefficient agreement. The written
  valuation argument gives the uniform formal precision statement.
- Disposition: complete for formal jets. Runtime improvement and real-variable
  error estimates are not claimed.

## Route D: sequence refinement and prime residual

- Mechanism: S_q R_(M,s)=R_(M,s) S^M, then substitute S=I+Delta.
- First uncertainty: loss of the lower-order prime correction under finer precision.
- Discriminator: compare direct lane differences with polynomial kernels, check
  composed refinements, and reject replacing 2*Delta+Delta^2 by Delta^2.
- Executed outcome: the signed Euler example gives 4 rather than 8, and two
  spacing-two refinements give 1384 exactly. The discrepancy is visible modulo 8.
- Disposition: complete for the stated operator laws and bounded implementation.
  Whole-branch Euler divisibility remains outside this example.

## Review and evidence

The formal proof self-review is in `PROOF_REVIEW.md`. Source authentication and
conventions are in `SOURCES.md`. The computation contract and v2 run manifest bind
the exact script and observed results. Publication integration is navigation and
exposition, and does not promote other papers' mathematical status.
