# Independent audit of projective reconstruction

**Normalized claim.** On each of the 14 frozen prepared-quadratic inputs,
the stated congruence lattice parametrizes the common-denominator models.
Exact LLL and the declared coefficient box produce the reported candidates.
The dual-basis certificate globally excludes the sufficient coefficient-height
test at those finite precisions. Reduced rational numerators can nevertheless
give valid certificates, as they do for the two named T=0 records. No claim
of globally minimum discriminant, a uniform exponent, or Euler closure follows.

**Primary verdict: proved as written in the corrected frozen revision.**
The lattice parity, precision, exact LLL verification, primitive reduction,
rational discriminant reduction, dual lower bound, and sufficient numerator
certificate all pass. The bounded replay is byte-identical. One terminology
correction was requested and made by the author: “square-discriminant model”
was changed to “zero-discriminant model.” The checker counts discriminant
zero, not nonzero discriminants that happen to be rational squares.

Reviewer: `/root/cross_cartier_review`. Author files were read-only for the
reviewer; the author made the terminology correction. No new search range,
ordinary parameter, or precision was introduced. No Lean compilation was run.

Current proof SHA256:
`6d8b6531ade1609d3c38aa3ed9d3c4523264caf8d2255592d8c8b7a6738552c5`.
Current checker SHA256:
`9ad6e07dfd2b9683531d7c1522555465baf45955f6a9b1c9e0887395b1bc074e`.
All inputs, author/replay evidence, and the additional finite certificate
cross-check are pinned in `PROJECTIVE_RECONSTRUCTION_REVIEW_HASHES.json`.

## Dependency graph and obligations

The already reviewed quadratic preparation supplies alpha and 2 beta modulo
2^P, and equality of reduced-discriminant and actual stationary valuations.
The linear congruences then define an explicit integer lattice. Unimodular
integer row operations give another basis of that lattice. Candidate
congruences, gcd reduction, and a dual inverse bound are elementary exact
integer and rational calculations. No new external theorem beyond the
explicitly checked LLL inequalities is needed for the conclusions.

| Obligation | Status | Decisive reason |
|---|---|---|
| Linear coefficient precision P-1 | Passed | Agreement of 2B with 2 beta A modulo 2^P is exactly the stated B congruence |
| Lattice basis and determinant | Passed | Every solution is uniquely an integer row combination; determinant is 2^(2P-1) |
| Lattice preservation through LLL | Passed | Every operation is an integer row subtraction or swap; independent membership and determinant checks also certify equality |
| Exact LLL certificate | Passed | Fraction Gram--Schmidt verifies every size-reduction and Lovasz inequality with delta=3/4 |
| Primitive gcd removal | Passed | A odd makes the full common gcd odd, so division preserves both congruences |
| Rational reduced-discriminant invariant | Passed | Odd A and P>=2 give full-P square congruence; the additional gcd is also odd |
| Strict reduced-numerator criterion | Passed | A nonzero integer numerator smaller than 2^P has valuation below P; its odd denominator changes no valuation |
| Dual global height lower bound | Passed | The inverse-transpose identity bounds a nonzero integer coordinate of the lattice vector |
| Global failure of the coefficient-height test at the 14 inputs | Passed | Every recorded lower bound satisfies 2L^2>=2^P |
| Stated bounded minima and successful examples | Passed in the declared box | Replayed all combinations in [-8,8]^3, followed by primitive reduction and deduplication |
| Uniform stationary nonvanishing | Not established | The finite certificates give no uniform successful reduced-numerator precision |

## Lattice and projective normalization

Let N=2^(P-1) and M=2^P. For an integer vector (A,B,C), the two congruences
are equivalent to

    (A,B,C)=A(1,beta,alpha)+j(0,N,0)+k(0,0,M)

for integers j,k. This proves both inclusions in the lattice description,
not merely that the proposed rows satisfy its constraints. Its determinant
is NM. Restricting A to be odd makes A nonzero and invertible dyadically.

If g is the common gcd of the coordinates, then g divides the odd A and
is itself odd. Dividing by g is therefore legitimate modulo both N and M.
Normalizing the sign of A is likewise harmless. These normalized vectors
remain members of the same lattice, so the later global bound applies to
them even if the division changes their coordinates in the displayed basis.

The B congruence determines B/A modulo 2^(P-1). Squaring gives its square
modulo 2^P for P>=2. Combining with C/A=alpha modulo 2^P proves

    (B^2-AC)/A^2 = beta^2-alpha modulo 2^P.

Reducing this fraction is distinct from making (A,B,C) primitive. Its
numerator/denominator gcd divides the odd A^2, so both this gcd and the
reduced denominator are odd. Consequently reduction preserves the dyadic
valuation. Condition 0<|n|<2^P on the reduced integer numerator is sufficient
for actual nonvanishing through the inherited prepared-quadratic theorem.
The rational denominator may be large; oddness, not a real-size bound on
that denominator, is what makes this numerator test valid.

## LLL, bounded enumeration, and dual certificate

The implementation uses exact Fraction arithmetic, including nearest-integer
size reduction. The rounding rule chooses a nearest integer at ties and is
valid for negative coefficients. Integer row subtractions and swaps preserve
the lattice throughout. At termination it checks the absolute determinant,
all Gram--Schmidt coefficients of absolute value at most 1/2, and all
Lovasz inequalities with parameter 3/4. The finite step limit would abort on
failure and is not used to certify an unfinished reduction.

Independently of that execution, the stored reduced bases were checked for
membership in the original congruence lattice and determinant absolute value
NM. These two facts imply equality of the full integer lattices. An
independent exact Gram--Schmidt reconstruction confirms all recorded LLL
conditions. The declared enumeration consists of all 17^3 coefficient
triples for each basis, then the documented odd-A filter, primitive/sign
normalization, and deduplication. The reported minima are only minima among
those resulting representatives, as the note explicitly states.

For a row basis B_0, vector coordinates are v=B_0^T z. The cofactor matrix
C_0, without transposing it again, satisfies

    C_0 B_0^T=det(B_0)I.

Thus each |z_i| is at most H times its absolute cofactor row sum divided by
|det(B_0)|. For nonzero v some integer z_i has absolute value at least 1.
Replacing that row sum by the largest one weakens the estimate in the correct
direction and gives the ceiling bound (4). It is valid for every lattice
vector, without an odd-A or bounded-enumeration assumption.

The reviewer also reconstructed (B_0^T)^(-1) by exact Gauss--Jordan
elimination, independently of the cofactor calculation. The reciprocal of
its maximum absolute row sum gives the same lower bound for all 14 bases.
Each satisfies 2L^2>=M. Hence no vector, including a primitive odd-A model
outside the search box, can satisfy 2H^2<M at these particular inputs.
This conclusion is global over vectors at fixed precision; it is not global
over all precisions or all Euler indices.

## Replayed results and scope

The bounded checker was replayed into `review/projective_replay`, with only
the two declared inputs pinned. Results are byte-identical to the author
results. Both author and replay manifests validate against the project root.
The independent stored-certificate cross-check is summarized in
`PROJECTIVE_CERTIFICATE_CROSSCHECK.json`; it uses the same 14 inputs and no
new enumeration range.

The two reduced numerator certificates reconstruct exactly as

    T=0, P=16:  34297/1248075,
    T=0, P=32: -3878929729/121356655581.

Both numerators are odd and have absolute value below 2^P. Their congruences
therefore certify the already known valuation 0. At P=93 the checked
coefficient heights are 62 bits, the smallest integer discriminants in the
declared candidate sets are 116 and 119 bits, and the smallest reduced
numerators are 114 and 112 bits. The two recorded dual lower bounds match
the note. No zero-discriminant candidate occurs in the declared search.

For the second control at P=16 and P=24, the prepared discriminant is zero
modulo 2^P. Every congruent rational number with odd denominator has either
zero numerator or a nonzero numerator divisible by 2^P. Thus no valid
strict numerator certificate can occur there, regardless of the search
algorithm. This observation does not decide whether the exact limit is zero;
the inherited higher precision record already has valuation 30.

## Remaining implication

The addendum correctly separates three claims: a bounded reconstruction
search, a global coefficient-height obstruction at those fixed inputs, and
a sufficient reduced-numerator certificate. The dual lower bound does not
exclude cancellation in B^2-AC or in its rational gcd reduction. The two
successful examples demonstrate that distinction. Conversely, the LLL
reconstruction gives no uniform bound forcing a successful reduced-numerator
certificate for every admitted ordinary index. That remains the exact
arithmetic separation gap.

Self-review: the complete report was conservatively proofread. The sole
author correction was the zero-discriminant terminology noted above; no
mathematical formula was changed and no unresolved local issue remains.
