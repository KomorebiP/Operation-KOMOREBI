# Block 10 — Bounded spectral operators and topology-specific truncation

Komorebi Physics Lean v0.10.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF page 31 of 550, printed page 18, Section 6.3, equations (6.15)–(6.25). The original page image was inspected. The actual source PDF is preserved unchanged. The authoritative current verification result is `verification/final/report.json`, not this prose alone.

## Inventory and scope

| Module | Theorems | Definitions | Abbreviations |
|---|---:|---:|---:|
| BoundedSpectral | 17 | 3 | 2 |
| SpectralTruncation | 19 | 3 | 0 |
| HarmonicSurrogates | 31 | 5 | 0 |
| AnchoredSurrogates | 26 | 6 | 0 |
| SpectralErrorBounds | 20 | 0 | 0 |
| **Block 10** | **113** | **17** | **2** |

The cumulative inventory contains **896 theorem declarations, 1,084 named declarations and 52 mathematical modules**. Of the theorems, 39 are recovered Paper VII declarations and 857 were authored across the ten full-edition blocks. All 47 prior mathematical files are preserved byte-for-byte. Counts include supporting lemmas, formulas and exact tests. They are not independent physical discoveries or a full-edition completion percentage.

The generic construction acts on the genuine infinite-dimensional Hilbert space `lp (fun _ : Nat => Complex) 2`. Its symbol is an actual bounded complex sequence (`lp ... top`). The five physical multipliers are realized spectrally, using the previously constructed self-adjoint harmonic multiplier with eigenvalues lambda_n = n + 1/2. The phase-family algebra works for arbitrary real eigenvalues. No differential-oscillator equivalence or general spectral functional calculus is assumed to have been formalized here.

## 1. Bounded multiplication is constructed, and its norm is proved

For a bounded complex sequence a, define

    (D_a x)_n = a_n x_n.

`multiply` proves that the product belongs to l2, using domination by ||a|| times the original square-summable sequence. `diagonal` then constructs an actual continuous complex-linear operator. Its boundedness is not an assumption field attached to an otherwise undefined multiplication.

The proof first derives ||D_a x|| <= ||a||_infty ||x||_2. Applying D_a to actual norm-one coordinate vectors gives the reverse bound. Consequently,

    ||D_a|| = sup_n |a_n|.

Addition, subtraction, scalar multiplication and products of symbols agree with the corresponding actual operator operations. The adjoint is D_(conjugate a), and

    ||D_a - D_b|| = ||a-b||_infty.

Both proof-bearing constructors and the two type abbreviations are included in the named-declaration axiom audit.

## 2. Actual cutoffs, not formal truncated notation

Let S_M retain coordinates n<M. `cutoff` is a bounded linear operator, and its idempotence is proved. `cutoff_eq_old_partial` proves it agrees with the previous block's actual finite sum of coordinate projectors.

The zero-padded symbol retains a_n for n<M and is zero otherwise. `truncate_sandwich` proves its operator is S_M D_a S_M.

For a fixed complex anchor c, `anchored` retains a_n below M and equals c for n>=M. The full operator identity is

    D_(anchored a c M) = S_M D_a S_M + c (I-S_M).

This is a derived identity between actual operators. The tail term is not erased or replaced by a finite-dimensional identity matrix.

### Exact tail norm

For every bounded a and every cutoff,

    ||D_a - D_(anchored a c M)|| = sup_{k>=0} |a_(k+M)-c|.

The supremum is a genuine conditionally complete real supremum; its boundedness is established. Each tail coordinate supplies a lower bound, and a uniform tail bound supplies the upper bound.

### Strong versus operator-norm convergence

For every fixed l2 state x and every bounded symbol,

    S_M D_a S_M x -> D_a x.

The proof identifies the truncated vector with the actual finite coordinate sum of D_a x and uses its l2 convergence. It does not assume the operator norms tend to zero. Every fixed scalar anchored version also converges strongly on each x.

The exact characterization is

    ||D_a - D_(anchored a c M)|| -> 0  iff  a_n -> c.

Sufficiency uses a uniform tail epsilon bound. Necessity tests the first omitted coordinate at each M. Thus the anchor is mathematically necessary, not an aesthetic padding choice. For modulus-one symbols the zero-padded operator error is exactly one at every finite cutoff.

## 3. Harmonic resolvent: actual inverse with actual domain range

Set lambda_n=n+1/2 and

    d_eta(n) = lambda_n - i eta,
    r_eta(n) = 1/d_eta(n).

For every real eta, the positive spectral gap proves d_eta(n) != 0. In particular eta=0 is valid for THIS harmonic realization. That conclusion is not asserted for an arbitrary self-adjoint operator whose spectrum might contain zero.

The estimates and literal coefficient formula are proved:

    |r_eta(n)| = 1/sqrt(lambda_n^2+eta^2) <= 1/lambda_n <= 2.

The symbol is bounded, so R_eta = D_(r_eta) is an actual bounded operator on all l2. The new proof additionally establishes

    R_eta x belongs to D(H)

for every l2 x. It does so by proving the weighted sequence lambda_n (R_eta x)_n is square summable, using |lambda_n r_eta(n)|<=1.

`resolventDomain` packages this range membership. The two inverse identities are then proved:

    (H-i eta) R_eta x = x              for every x in l2,
    R_eta (H-i eta) x = x              for every x in D(H).

The unbounded H is evaluated only on actual domain elements. This is stronger than naming a coefficient sequence a resolvent without proving that it is the inverse of the source operator.

Both the literal source supremum and the attained endpoint error are proved:

    ||R_eta - S_M R_eta S_M||
      = sup_{n>=M} 1/sqrt(lambda_n^2+eta^2)
      = 1/sqrt(lambda_M^2+eta^2)
      <= 1/lambda_M -> 0.

## 4. Heat and phase operators have different truncation topologies

For t>=0, define the actual heat coefficients exp(-t lambda_n). They are bounded by one. The source's exact error is proved:

    ||E_t - S_M E_t S_M|| = exp(-t lambda_M).

It tends to zero for fixed t>0. At t=0 the operator is the identity, and its error is exactly one for every finite M. For t<0, the coefficient sequence is proved unbounded. Thus neither the constructor's t>=0 condition nor the convergence theorem's stronger t>0 condition is silently discarded.

The actual heat operators have the proved composition law E_(s+t)=E_s E_t for nonnegative s,t. This release does not claim a separately checked time-continuity or generator-domain differentiability theorem for this semigroup.

For arbitrary real eigenvalues, define

    u_t(n) = exp(-i t lambda_n),
    U_t = D_(u_t).

The actual coefficients have modulus one. Lean proves U_0=I, U_(s+t)=U_s U_t, U_(-t)U_t=I, and ||U_t x||=||x||. These are constructed norm-preserving phase operators with algebraic group law, not an unspecified evolution family assumed as data.

For every fixed state, their zero-padded cutoffs converge strongly. Nevertheless,

    ||U_t - S_M U_t S_M|| = 1

for every real t and every finite M. `phase_tail_eigenvector` proves the literal source action on every omitted coordinate vector. The failure of norm convergence is separately formalized, not merely inferred from a finite experiment.

The remaining link to (6.26) is explicit: strong continuity IN TIME, domain invariance and the actual derivative U_t' x=-i H U_t x on D(H) are not yet proved. The current block proves strong convergence IN CUTOFF M. Those are different assertions.

## 5. Bounded and Cayley transforms require the nonzero tail

Define

    f_n = lambda_n / sqrt(1+lambda_n^2),
    c_n = (lambda_n-i)/(lambda_n+i).

The functions are actual bounded symbols, with f_n -> 1 and c_n -> 1. The bounded-transform limit is proved through a valid positive-eigenvalue normalization. The Cayley limit uses the exact identity

    c_n - 1 = -2i/(lambda_n+i).

The square-root regularizer has coefficients 1/sqrt(1+lambda_n^2), maps every l2 vector into D(H), and satisfies

    H (regularizer x) = D_f x.

Likewise the Cayley map satisfies the actual domain-correct formula

    D_c x = (H-i) R_(-1) x,

where R_(-1)=(H+i)^(-1) was already proved to have domain range. Cayley norm preservation is proved independently. This is a spectral realization of the displayed transforms; a general unbounded Borel functional calculus or a theorem identifying a fractional operator power is not claimed.

The correct approximants are

    F_M = S_M D_f S_M + (I-S_M),
    C_M = S_M D_c S_M + (I-S_M).

The source supremum formulas and their exact harmonic endpoints are proved:

    ||D_f-F_M|| = 1-lambda_M/sqrt(1+lambda_M^2),
    ||D_c-C_M|| = 2/sqrt(1+lambda_M^2).

Both tend to zero. In contrast, the ZERO-PADDED error of either transform is exactly one for every finite M.

A further exact rationalization is

    1-lambda_M/sqrt(1+lambda_M^2)
      = 1/[sqrt(1+lambda_M^2)(sqrt(1+lambda_M^2)+lambda_M)].

The resulting quantified bounds are <=lambda_M^(-2) for the bounded transform and <=2/lambda_M for Cayley. No floating-point execution or numerical cancellation stability is inferred from these real-number identities.

`wrong_anchor_not_norm` rejects EVERY constant anchor different from the actual scalar tail limit. This applies to both transforms, not only to the special mistaken choice zero.

## 6. Exact witnesses and rejection tests

At eta=0 and M=10 the resolvent error is proved exactly 2/21. The identity cutoff is proved strongly convergent on every l2 state while its norm error is exactly one at every M. Tail eigenvectors, positive-time versus zero-time heat, backward-heat unboundedness, and the incorrect zero anchors are genuine infinite-dimensional or universal statements.

Eight new invalid compilation controls separately test: strong implies norm, zero-time heat decay, zero-padding the bounded transform, zero-padding Cayley, a wrong resolvent endpoint, the missing factor two in the Cayley error, an incorrect constant tail, and bounded backward heat. The positive library contains the opposing identities or refutations. Each negative control must fail with its own intended proof diagnostic in its source range. A timeout, import failure, or nonzero batch exit alone never passes the control contract.

## 7. Verification and explicit boundaries

The cumulative verifier removes local build outputs, freshly recompiles all 52 mathematical modules plus the aggregate with one worker and warnings as errors, audits all 1,084 inventoried names, and checks all 73 deliberately invalid controls. It preserves all 47 prior mathematical modules and earlier preservation layers. The completed final report and separate fresh-extraction receipt determine pass status.

The v0.9.0 baseline was freshly recompiled and audited before extension. Lean is 4.34.0-rc2, Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06, and all nine tracked dependency trees must be clean at their pinned revisions. Imported compiled dependency caches are reused, not independently rebuilt wholesale. Only propext, Classical.choice and Quot.sound are allowed in audited axiom dependencies. No admissions, custom axioms, native evaluation or disabled kernel checks occur in active mathematics.

This block covers Section 6.3 in the constructed spectral model and a more general bounded-diagonal truncation theorem. It does not prove a general functional calculus for every self-adjoint operator, identify the differential oscillator on L2(R), prove the full form-domain hierarchy, establish a time-differentiable evolution on the unbounded domain, justify infinite coarse-cell current rearrangement, or validate gravity/cosmology empirically. Fixed-t cutoff convergence does not imply a uniform-in-t cutoff statement. In particular heat convergence is not uniform through t=0.

Next: prove strong time continuity, domain preservation and the actual Schrödinger derivative for the constructed phase family. Then the prior countable continuity results can consume a proved spectral solution rather than a supplied flow hypothesis. The general Stone theorem remains a separate target.
