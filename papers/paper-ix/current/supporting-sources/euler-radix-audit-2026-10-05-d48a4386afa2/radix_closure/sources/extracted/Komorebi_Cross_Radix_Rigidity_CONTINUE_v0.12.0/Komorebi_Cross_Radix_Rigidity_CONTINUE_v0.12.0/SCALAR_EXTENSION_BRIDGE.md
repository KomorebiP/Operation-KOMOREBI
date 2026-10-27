# Scalar-Extension Bridge — v0.12.0

Let `T>0`, let `c | T` be a primitive divisor-shell label, and let `D_c` be the exact
least common denominator certified in v0.11. Let `N_c` denote the cleared integral
Möbius/Reynolds shell numerator and `P_c` the certified primitive DFT shell projector.

The v0.12 theorem chain proves:

1. Each unnormalized integer subgroup Reynolds sum scalar-extends to
   `width × subgroupReynoldsAverage`.
2. The active Möbius shell mask is the exact nonzero-support Möbius sum of the certified
   Reynolds width masks.
3. Since every active width divides `D_c`, its denominator share cancels exactly after
   scalar extension.
4. Therefore, as complex linear endomorphisms of residue profiles,

   `N_c ⊗ ℂ = D_c P_c`.

5. On every integer packet `x`, with coordinatewise embedding `iota`,

   `iota(N_c x) = D_c P_c(iota x)`.

6. Since `D_c ≠ 0`,

   `P_c(iota x) = D_c^{-1} iota(N_c x)`.

7. Consequently the v0.11 good lattice has the intrinsic characterization

   `x ∈ L_c` iff there exists an integer packet `y` with `P_c(iota x)=iota(y)`.

Thus the complex spectral shell and the integral denominator-defect shell are no longer
parallel constructions: they are the same operator before and after denominator clearing.
