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

## Expansion checkpoint EULER-CASE-002

Requested proofreading and further worked examples begin at collection commit
`9987ef468dcbfa49a256ea6da2b249d577da0a88`. Preserve the accepted first-edition
runs as historical records. New runs must bind the revised script and page.

The added targets are the Paper IX odd-length and dyadic local Euler charts,
their forward and inverse coefficient laws, and a fully worked reconstruction
of E_8 in each chart. Supply explicit partial sums, exact rational errors and
local valuations. Prove the odd-length truncation bound from integer factors.
For the sharp dyadic bound, derive the Bernoulli kernel formula and verify the
precise external denominator-theorem input before using it. Retain its prime,
positive-index and coefficient-domain hypotheses.

Complementary examples will recover the quartic carrier from its Euler packet,
explain the first quartic permutation counts by inclusion-exclusion, telescope
finite alternating powers with Euler polynomials, and test higher prime
residuals. A bounded alternating signal will show what a single sampled lane
forgets. These additions must have written derivations and independent exact
coefficient or sample-space controls.

The routes have distinct discriminators: formal generating functions against
finite power sums for the odd chart, direct inverse coefficients against the
Bernoulli formula for the dyadic chart, and direct sampling or enumeration
against transferred coordinates for the complementary examples. Success is
closed written arguments under explicit hypotheses, a fresh completed primary
run and library comparison, and source-bound published downloads. No result is
declared new, and no Lean execution is part of this phase.

## Infinite-matrix checkpoint EULER-CASE-003

The requested coefficient-transform expansion starts at collection revision
`0a1d2c6265885f22011e6717c5ddf3f3a627f462`. Make the infinite local Euler
matrices, their inverse and composition, factorial normalization, packet block
operator, and Pascal conjugation of sampling explicit. Every matrix product
must be row-finite, or supplied with the finite-support argument it needs.

Distinguish stable leading blocks of lower-triangular coefficient transforms
from sampling transforms, whose row k can require input through Mk+s. Include
the concrete bad-cutoff output 32 versus the correct 1376. Supply exact finite
blocks and a downloadable matrix-entry table. Universal statements require
written algebra, with fresh bounded execution records and a focused self-review.
The mathematical library pin and the existing local-chart comparison ranges
remain unchanged. No analytic infinite sum, new theorem priority, performance
advantage or Lean execution is claimed.

The expanded request also includes explicit supercongruences, exact local
chart base changes and their prime-dependent precision, normalized congruential
families with their addresses, and coprime combination of modular information.
Distinguish a coordinate change of the same Euler vector from changing the
family itself or changing the working modulus. Include the degree-zero
counterexample to the stated Euler-index supercongruence, and the concrete
loss of a ternary digit through a dyadic coordinate coefficient. These extend
the same checkpoint and must be proved and checked within its final evidence.

## Fibonacci checkpoint EULER-CASE-004

Target fixed before execution against collection base
`0ba7d402231a341383a47332072ddb20575bdfe7`. Add the existing library's
Euler-polynomial to Fibonacci-polynomial connection and recurrence defect
coordinates, with explicit source and target orders. Derive an invertible
ordinary-series Toeplitz transfer to the shifted Fibonacci sequence. Keep the
polynomial direct sum separate from arbitrary sequence columns and keep the
full-index Euler stream separate from its even subsequence. The sequence map
is constructed from its known source and target; no discovery or speed claim.

Routes: closed connection formula versus monic elimination; companion state
iteration versus Green-kernel reconstruction; ordinary formal-unit inversion
versus target recurrence. Contracts 004 declare the finite ranges before runs.
Same-assistant proof review and mathematical proofreading are separate from
execution. Earlier contracts and captured evidence are retained historically.

## Literature extension EULER-CASE-005

Target fixed before execution at collection revision
`2dc495d16c5c76d2e55e04f73b9e9872193fd4c2`. Sources checked: Paper IX
companion-jump theorem, Fibonacci/Lucas specialization, corrected integral
matrix precision amplification and explicit C^12 and C^24 examples; pinned
Komorebi Math typed-expression example and polynomial calculus implementation.

Add the exact sampled recurrence and its parity control, finite integral
binomial packet expansions with depth-dependent congruences and a sharp
dyadic example, the simultaneous-prime jump, and a complete polynomial
antiderivative/change-of-basis/derivative round trip with integral covector.
Distinguish source statements from newly written formal corollaries (the
144 factor, sharpness and composition with the Euler transfer). No new global
literature/novelty claim or Lean execution. Source authentication, extraction,
application, proof self-review and finite execution are separate evidence.
