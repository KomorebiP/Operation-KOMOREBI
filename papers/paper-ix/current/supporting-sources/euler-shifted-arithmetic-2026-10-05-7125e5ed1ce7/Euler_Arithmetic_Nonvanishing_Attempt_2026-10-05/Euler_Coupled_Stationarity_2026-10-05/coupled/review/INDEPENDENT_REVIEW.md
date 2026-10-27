# Independent audit of the coupled Euler continuation

Date: 2026-10-05. Reviewer: isolated `coupled_review` agent. Author files were
read-only; the reviewer wrote only `coupled/review/`.

**Normalized claim.** With the inherited exact Euler definitions, true-terminal
161 hypothesis, and complete 629-bit multiplier certificate as declared inputs:
the actual deep chart admits an exact square coordinate; a fixed integral lift
of the finite affine model has the stated stationary and critical-value geometry;
the independent fixed-r undepletion family has the stated exact motion and
cancellation laws; and the three packet examples have the displayed finite
valuations and precision. These are three different objects and are not
identified at all precision.

**Primary verdict: proved as written for this normalized, narrowly scoped claim.**
The packet assertions are computationally verified in their stated range. This
audit does not establish universal Euler simplicity or eliminate the retained
arithmetic exceptional class. No exact singular actual Euler parameter is found.

## Objects and dependencies

| Object | Domain and equality available | Consequence audited |
| --- | --- | --- |
| Actual Euler `K_T=2^-178 G_r(10202+2^15 Z)` | Each ordinary integer T with positive B and true terminal161; exact in Z | `K_T=Phi_T+w_T^2`, pointwise for each such index |
| Stored model `H0+T H1` | One chosen integral polynomial lift; T,Z in Z2 | Exact analytic c(T), Psi(T), and quadratic fold for that lift |
| Model compared with actual Euler | `B K_T=H0+T H1 mod2^451` coefficientwise | Stationary positions agree450bits, critical values451bits |
| Fixed-r epsilon deformation | A separate independent parameter `epsilon=2^24 eta` | Exact restricted analytic family and all-disc eta motion laws |
| Three packet examples | Global320bits, stationary141bits | Critical values0/30/80 and movement errors14/74/14 |

The dependency chain is: exact G and true carry normalization -> inherited
Theorem VI.7 with the parity-tail cutoff -> complete oldfast629 records -> the
actual coefficient class modulo256 and the finite affine comparison. The
all-precision square coordinate then follows by an analytic construction from
that coefficient class, rather than by promoting the finite parameter template
to an exact identity. The epsilon route additionally uses the exact depleted
Bernoulli ratio and convergent rational undepletion formula. Packet rebuilding
is corroboration at three actual indices, not the source of a universal
parameter quantifier.

The oldfast629 coefficient generation and classical Bernoulli identities are
inherited inputs. I read their stated precision reduction and raw source
Theorem VI.7; I did not freshly reconstruct that entire certificate or claim a
new independent implementation of its high-index Bernoulli evaluator.

## Obligation matrix

| Obligation | Result | Decisive reason |
| --- | --- | --- |
| Exact G and parameter domain | Passed | Original packet definition retained; true terminal161 remains a hypothesis outside proved finite-height ranges |
| Remote packet tail | Passed | Parity cutoff uses integral normalized gammas for every omitted q; it is not a low-prefix assumption |
| Affine-template precision | Passed | Global629 minus content178 gives451; half differentiation loses one bit to450 |
| Actual low coefficient class | Passed | Complete records give `K=213+167T+88Z+81Z^2 mod256` |
| Stationary point and low critical value | Passed | `K'/2=44+81Z mod128`, hence c=20mod128 and Phi=69+167Tmod256 |
| Actual Morse coordinate | Passed | Translation preserves the256-divisible higher tail; square-root terms have valuation at least6m+s2(m); resulting coordinate is an analytic isometry |
| Stored-model stationary curve | Passed | Contraction in the complete restricted parameter algebra has unit linear coefficient and even nonlinear coefficients |
| Stored-model curvature | Passed | Derivative valuations a,b,d,e are1,8,9,26; exact chain rules give15 and30 for Psi'' and Psi''' |
| Transfer to actual pairs | Passed | c error450; critical-value substitution error at least900; strict separation thresholds e<443 and e<451 are correct |
| Exact eta source cancellation | Passed | Independently recomputed source derivative50 and q1 derivative94 modulo128; their sum16 has valuation4 |
| Eta Taylor tails and derivatives | Passed | q1 dominates; explicit q2, remaining lower, and upper bounds leave strict gaps after both derivatives |
| Eta chord laws coefficientwise | Passed | The stationary contraction preserves the ideal `2^18 h Z2<h>`; expansion then gives the39/26 quadratic coefficient scales and units3/1 |
| Actual-sheet cancellation filters | Passed | Direct substitution E=2r-25 gives units15mod32 and7mod8 and the stated exact next-order depths |
| Packet precision and units | Passed after clarification | Individual value units149bits, derivative units152bits; dependent cancellation safely preserves152 obstruction bits |
| Universal Euler nonintersection | Not addressed by these results | No proof that the actual eta=2^(2r-25) avoids eta_* |

At the critical point, the claim `v2(K_ZZZ)=9` is justified: the cubic contributes
valuation9, while c is even and every degree at least4 gains a further factor
from `c^(n-3)`. Only a lower bound9 is asserted at arbitrary Z. No missing
coefficientwise conclusion is inferred from sampled values.

## Critical independent deductions

For the actual Morse proof, `S=81(1+256R)` has a restricted square root
`9(1+128A)`. The map `z -> z sqrt(S)` therefore has odd divided differences
and a contracting inverse. This establishes the exact pointwise identity
`K_T=Phi_T+w_T^2` from the finite coefficient class. A nonzero critical value
has roots precisely under the stated even-valuation and square-unit criterion;
when it vanishes the multiplicity is exactly two.

For eta motion, the mixed derivative has valuation19 and the Hessian1, giving
velocity18. The three terms in the second stationary derivative numerator have
valuations41,44,45; its unit after division is3mod8. In the critical-value
Schur complement, direct curvature27 dominates the movement correction37.
These are strict valuation gaps and therefore exclude hidden cancellation in
the displayed leading terms. They do not exclude the separate actual critical
value cancellation.

The chord argument works in the restricted algebra, not merely pointwise:
`Q(c(theta),theta+h)` lies coefficientwise in the ideal `2^18 h`, and the
stationary inverse preserves that ideal. Subtracting the exact linear terms
leaves the unique leading pure-parameter quadratic term. This supplies the
all-h remainder units, including h=0, used in the actual-sheet filters.

In the finite T model, motion has scale7 and the critical value scale0.
For actual pairs these laws transfer only at the declared strict precision
thresholds. They are consistent with the separate eta motion scale18, since
eta deforms a fixed integer index and is not the integer multiplier T.

## Computation and provenance

`check_stored_coupling.py` is a fresh bounded checker using direct modular
evaluation and exact rational low-source calculations. It imports no Euler
packet engine and performs no new singular-parameter lift. Its validated
runner output is `certified_run/STORED_CHECKS.json` with status PASS.

It independently checked:

* The complete H0/H1 modulo256 reductions and their equality to the oldfast629
  records; actual c20mod128 and Phi69+167Tmod256.
* Exact rational Newton-source coefficients and the depleted q1 unit43mod64,
  using the actual giant integer r in the bounded Bernoulli polynomial.
* Every retained stored packet evaluation in all three channels, total sums,
  finite-model coefficient agreement, and critical values0,30,80.
* Slope/value unit determinant identities, obstruction valuations18,48,98,
  explicit precision labels, and the frozen-point error valuations14,74,14.

The authored packet replay additionally rebuilds the actual retained
coefficients through a separate localization and scalar/source route. Its
completed final run and manifest were inspected; the expensive rebuild was
not duplicated. The geometry seven-order Taylor table is a bounded
128-bit check only. Its code was reviewed; no all-order pattern was inferred.
The eta stored-jet checks are finite corroboration of the independent
all-disc proof, not a precision extension of the T template.

The reviewer runner used Python3.12.14, a30second cap,512MiB address-space cap,
one CPU core and conventional one-thread environment caps. The successful
command and actual hashes are in its version2 manifest. An initial runner
invocation omitted explicit `--input` pins and was rejected before a process
started; the corrected pinned invocation completed and validated. This is an
execution setup rejection, not a failed mathematical check.

`SOURCE_HASHES.json` freezes the reviewed proof, code, data and provenance
records. This review changes no author proof or status file.

## Exact remaining implication

The strongest safe conclusion is the local exact geometry, the fixed-r eta
motion/cancellation laws, and the stated finite actual-family transfer and
examples. On the actual sheet one still needs

`Phi_r(2^(2r-25)) != 0`, equivalently `eta_*(r) != 2^(2r-25)`.

The new unit filters are necessary for a hypothetical intersection. No
arithmetic argument has been supplied that forces one of them to fail for
every admissible ordinary integer r. Another finite residue lift alone would
not prove that statement. The cheapest meaningful next investigation is a
uniform arithmetic restriction on these actual depleted Bernoulli units,
or a new reduction that makes the remaining intersection decidable; further
sampling is not a substitute.
