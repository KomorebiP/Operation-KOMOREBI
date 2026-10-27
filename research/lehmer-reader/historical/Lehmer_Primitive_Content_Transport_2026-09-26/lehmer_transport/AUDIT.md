# Mathematical self-review

Checkpoint LEHMER-CONTENT-TRANSPORT-02.

Primary verdict on Lehmer: **incomplete, with prime nonvanishing unresolved**.

The content decomposition, content conservation, all-square primitive
nonvanishing and odd-power unit statements are **proved as written** by the
included mathematical arguments, subject to ordinary external review.
This was self-review, not independent-agent review or Lean verification.

## Main claim audit

| Claim or obligation | Result | Reason |
|---|---|---|
| Coordinate gcd is coprime to 5 | Passed | Coordinates occupy all five residues |
| Content g gives g^2 dividing n | Passed | Rescaled, permuted vector has squared norm divisible by 10 |
| Scaling sign is chi_5(g) | Passed | Direct four-unit permutation calculation |
| Primitive transform and inverse | Passed | Content partition and square-divisor Mobius inversion |
| Nullity in each content | Passed | Induction for every homogeneous Q, then linearity |
| Scope of conserved correction space | Restricted explicitly | Homogeneous universal nulls and their finite span |
| Transfer refinement exactness | Passed | Aggregation is surjective on zero-total spaces and transfer images |
| Detail transfer rank at 31 | Exact finite result | Rank 15 minus rank 5 equals 10, certificate stored |
| All-prime transfer completeness | Not established | Only the recorded finite ranks are claimed |
| Primitive multiplicativity | Passed | Square-supported multiplicative convolution |
| Modulo-5 primitive local formula | Passed | Hecke recurrence and chi^2=1 |
| Even blocks when t<=4 or t>=6 | Passed | Unique lowest-valued term with unit extremal coefficient |
| Case a=0 | Passed explicitly | Even primitive term is a nonzero signed prime power times p+chi |
| Exceptional t=5 case | Passed | Integer root divides p+1 and is 1 mod p, leaving two impossible squares |
| Prime 5 | Passed | 2v_5(a) cannot equal 11 in even terms, actual a gives valuation r |
| Odd quotient polynomial | Passed | Division by a is performed symbolically before evaluation |
| Odd quotient parity | Passed | Constant coefficient odd, other terms contain even a |
| Every square index | Passed | Multiplicativity, even local factors, R(1)=1 |
| Zero-set equivalence | Passed | Odd factors retain tau(p), even factors cannot vanish |
| Excluding tau(p)=0 | Not established | Hypothetical zero inputs satisfy all new structural theorems |

## Sources

Han's packet normalization is inherited from the checked parent result.
The Hecke recurrence, modulo-5 congruence and parity proof were verified in
arXiv:2005.10345v1, respectively Theorem 2.2, equation (1.2), and Section 3.
The harmonic-theta statement was verified in arXiv:2505.23497v1, Section 3.4.
The full-level sign-line deduction is supplied in the note. The valence bound
was checked in Stein's Theorem 2.11.

None of these sources is claimed to state the displayed new-to-this-project
primitive theorem or rank certificates. No novelty classification beyond
derivation in this continuation is asserted.

## Computational review

The polynomial constructor uses exact Fractions. Each generated polynomial
is checked by the symbolic harmonic operator and by direct second derivatives
at three exact points. Direct derivative checks are bounded controls, not a
replacement for the symbolic identity.

The universal null conclusion uses harmonic modularity and the valence bound,
not extrapolation from the tested shell range. All initial coefficients required
by that bound are checked.

The actual coefficient run uses all primes through 500 and exponents through
40. This is a recurrence test, not direct enumeration of shells at all those
large prime powers. Direct shell and content enumeration has its separate
bound of 128, with additional odd shells for coarse-rank analysis.

Synthetic tests deliberately include the p-adic valuation t=5, which the
chosen small actual tau values would not exercise, and include a=0. These
cases prevent a finite run from silently assuming the desired nonvanishing.

The provenance manifest passed validation with current input and result hashes.
The supplemental n=121 numbers are also checked by a saved exact calculation
and by the recurrence formula displayed in the note.

## Proofreading

Reviewed the newly written mathematical note, README and audit.
Routine corrections: wording and scope clarifications.
Mathematical extension during proof development: the even-block statement was
explicitly generalized to arbitrary congruence-compatible recurrence parameters.
This was a proved extension, not a silent typographical change.
Unresolved issue: the original prime-level nonvanishing theorem.
