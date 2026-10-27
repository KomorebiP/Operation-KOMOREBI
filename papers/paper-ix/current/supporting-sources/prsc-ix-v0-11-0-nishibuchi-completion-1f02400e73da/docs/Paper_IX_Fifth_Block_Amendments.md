# Paper IX fifth-block manuscript amendments

**Author: Komorebi P. — Release v0.5.0**

The original status-corrected manuscript PDF remains unchanged. Read this note with the
cumulative supplements and earlier amendments. This block does not change the seven
previously resolved definitions or replace the checked coefficients by a modular surrogate.

## 1. Corollary 8.3: reduction must follow integrality

The assertion C_(mp,j)(n) mod p requires the rational coefficient to be p-integral.
There is no ring homomorphism from the whole rational field to F_p. A total division
operation in F_p would not make a vanishing denominator invertible.

The new proof constructs a unit-pivot triangular solution in Z_p, proves its image in Q_p
equals the original rational coefficient, and only then applies the actual residue map.
The integral lift satisfies the actual rational-coefficient recurrence at every row.
The reduced sequence is independently constructed from the Lucas-reduced rows and is
proved unique. For j,k<p, their integral lifts differ by an element of p Z_p.

The prime hypothesis and j<p are explicit. The construction also works for m=0; the
paper's arithmetic interpretation uses m>=1. No finite-difference hypothesis, period
hypothesis, or theorem 7.5 is assumed. The canonical outside-window example C_(6,3)(1)
has denominator divisible by 3 and is proved not integral in Q_3.

## 2. Proposition 6.2: explicit finite root construction

For precision ell>=1, a is an actual unit in Z/(p^ell)Z. Define

    omega_ell(a) = a^(p^(ell-1))
    principal_ell(a) = a * omega_ell(a)^(-1).

The source uses ell=L+1, avoiding subtraction at zero precision. Euler's unit-group
exponent proves omega^(p-1)=1; finite-field Frobenius proves its residue equals that
of a. The principal factor reduces to 1. Reconstruction and uniqueness of both factors
are proved. Raising congruent elements to p^(ell-1) identifies them modulo p^ell,
which supplies the root uniqueness proof. Multiplicativity and compatibility under
reduction to any lower positive precision are checked for these prime-power factors.

This is an alternative finite proof of the manuscript statement, not an assumed
Hensel lift. It does not construct the full infinite topological group decomposition
or an analytic logarithm. Imported Mathlib number-theoretic and ideal-power theorems
remain dependencies of the formal proof.

## 3. The dyadic sign is a separate finite decomposition

At precision ell>=2, define the sign from a modulo 4 and set principal_2(a)=sign(a)*a.
The source uses ell=L+2. It proves that the sign is +/-1, the principal factor is 1
modulo 4, reconstruction holds, and the factors are unique.

This is not obtained by interpreting the generic p=2 principal factor as already 1
modulo 4. For the generic construction the residue constraint is only modulo 2.
Modulo 2 the two signs coincide; they are distinct modulo 4. The new source checks
both facts. Precision-compatibility theorems in UnitRefinement concern the generic
prime-power root/principal decomposition, not a separately proved dyadic inverse-limit
construction.

## 4. Theorem 10.1: canonical addresses and coefficientwise scope

The address map is the actual CRT ring equivalence

    Z/(2^a M)Z  ~=  Z/(2^a)Z x Z/MZ,

for odd M, including M=1 and a=0. For the existing selector definition, the combined
label satisfies 0<=r<2^a M; the component labels are r modulo 2^a and M.
Both the sequence-selector identity and its formal power-series version are proved.

This result factors residue addresses, not arithmetic visibility weights or all
p-adic filtrations. No analytic series convergence is added. The counterexample
0 and 2 modulo 4, both reducing to the same pair modulo 2, shows why arbitrary
noncoprime factors cannot replace the coprime CRT factors.

## 5. Remaining obligations

Items 7.5 (global Euler finite differences), 8.5 (uniform period), 9.1 (companion jump)
and 9.2 (Fibonacci packets) remain pending. Three classical inputs and two conjectures
remain outside the count of 24 manuscript-proved items.
