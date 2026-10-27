# Paper IX: singular Amice continuation

Author: Komorebi P.  Release v0.9.0.  7 September 2026.

## New theorem

For prime p, N dividing p(p-1), and a positive address c=ap<N, the actual ratio

    R_c(t) = A_(c-1)(t) / A_c(t),
    A_c(t) = sum_n t^(N*n)/(N*n+c)!,

satisfies the weighted coefficient bound after formal logarithmic substitution:

    p^floor(d/p) [T^d] R_c(log(1+T)) belongs to Z_p.

For the paper's N=mp, this covers every singular address 1<=a<m. The coefficientwise valuation version explicitly separates zero coefficients.

## Replaced proof route

Instead of requiring a ramified cyclotomic field and its trace estimate first, this proof uses the integral cyclic group ring Z[Z/NZ]. The ideal (p,z-1) with z^p=1 satisfies I^p <= (p) I and I^q <= (p^v_p(q!)). Prime blocks of falling factorials yield a coordinatewise factorial-denominator bound. Coupled differential recurrences connect those coordinates to the actual log-substituted sections.

This is a new proof route for the supporting weighted estimate, not a claim of historical priority.

## No assumed inverse or ratio statement

The series U=c! T^(-c) H_(N,c)(log(1+T)) is constructed by removing the forced zero, not by inverting T. Its constant coefficient is proved to be one. Weighted inverse closure is derived from the actual formal reciprocal recurrence. The independently constructed ratio has constant c, not one, and its cleared identity with the original sections is proved before deriving the logarithmic formula.

Ordinary differentiation, log multiplication and the transformed Euler field preserve the weighted ring by explicit coefficient proofs. No Dwork-flatness or weighted estimate is a premise of the final singular-ratio theorem.

## What remains

The full higher-difference estimate for singular ratios is NOT proved by this block. Remaining work includes the dual Mahler polynomial filtration and integral pairing, the transfer to actual singular flatness, nonsingular ratio propagation between singular indices, and assembly of all residues for Theorem 7.5. The full register remains 23/24; the weighted estimate is listed only as a partial target under 7.5.

All previous corrections concerning rational normalization, zero valuations, finite-data stencils, and recurrence order remain applicable. The original manuscript is preserved rather than silently edited.
