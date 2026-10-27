# Continue here — 2026-10-02

## Exact state

Test case is beta^3=7, not the other BCG cubic. Keep beta=7^(1/3) omega^2, omega=exp(2*pi*i/3), X the negative-imaginary cube root of J=2+3omega fixed by the previous Gauss/CM branch proof.

### Newly proved in ordinary mathematics

1. The three paired ray zeta derivatives for F=Q(omega), modulus 3J, are
   ell_m=-(2/3)log|a_m|, where

       a0=(1+omega)X^2-X+1,
       a1=-X^2+(1+omega)X+1,
       a2=-omega X^2-omega X+1.

   They are roots of T^3-3T^2+6omega T-1.

2. With R=-log(2-cuberoot(7)), and sigma the arithmetic norm-two Frobenius,

       zeta_f'(sigma^h,0)=(-1)^h [R/6+(2/3)log|a_(h-1)|].

3. The previously constructed W has

       log|sigma^h W|=-3 zeta_f'(sigma^(h+5),0).

   Therefore W_St=sigma(W) satisfies the exact Stark logarithmic formula for all six classes. Combined with the already proved unit/other-place/abelian-radical facts, this verifies the stated rank-one Stark conditions for this ray extension.

4. The original gamma value is at geometric ray index five, not index zero. BCG Theorem 3.2 and W^(5-sigma)=U_alg^6 now give

       |U_gamma|=|U_alg|,
       |U_gamma|^3=|(2-beta)^3 a2 a1^5|.

5. More generally the admissible geometric gamma packet has the exact moduli described by PROOF.md (7.4).

### What did not close

The phase d=U_gamma/U_alg satisfies |d|=1. We do NOT know from this proof that d is algebraic, a root of unity, or one. Do not use numerical closeness, or the two-smoothing lemma requiring complex identities, to claim any of those conclusions.

### Corrected former route

The finite orbit counts 529=1+528 and 100=1+3+8*12 are correct. But adjacent ratios around an orbit leave one arbitrary scalar. An orbit-closing product of ratios does not evaluate the product of the values. The old proposed normalization inference is not available.

### Conventions that must not be lost

- Arithmetic sigma fixes beta and sends omega to omega^2, X to omega*beta/X.
- Actual complex conjugation kappa sends beta to omega^2*beta; it is NOT sigma^3.
- For the CM ray calculation the conductor is 3J, NOT 21=3J*Jbar. Removing the additional Euler factor kills the first derivative.
- L(0,chi_-3)=1/3 uses conductor 3, not the imprimitive modulus21 version.
- The shifted Epstein derivative is -2log|g|. Complex-place valuations are squared absolute values.
- The exact positive product identity is V_m^3=|a_m|, not an unproved phase identity between V_m and a chosen cubic root.

## Best next target

Seek a phase-sensitive comparison of the actual elliptic-gamma construction with the algebraic unit: an exact complex regulator identity, a sixth-power equality, or an independent arithmetic characterization of its phase. The Stark logarithmic formula is now an available theorem of this checkpoint, not a premise to be conjectured again.

A failure to recover phase from moduli is structural: multiplying a candidate by exp(i*delta) preserves its modulus for every real delta. That obstruction persists even at arbitrarily high numerical precision.

## Verification state

Two exact arithmetic implementations agree on the six new W norm identities. The full exact run has 140 assertions. The numerical runs have 27 equality assertions at each of 70 and 110 digits plus negative controls. No Lean verification and no independent human/second-agent review. See PROOF.md for the whole argument and evidence manifests for actual executions.
