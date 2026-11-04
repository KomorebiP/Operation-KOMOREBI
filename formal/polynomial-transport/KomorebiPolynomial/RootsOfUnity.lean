import KomorebiPolynomial.PolynomialPackets
import Mathlib.RingTheory.RootsOfUnity.Complex
import Mathlib.Algebra.Field.GeomSum
import Mathlib.Algebra.Polynomial.Eval.Degree

/-!
# Exact roots-of-unity averaging on finite complex polynomials

For a positive modulus `N`, a canonical residue `r < N`, and a primitive
`N`-th complex root `ζ`, the finite character average equals the polynomial
coefficient mask. The inverse weight is the integer power `ζ ^ (-(r * ℓ))`
itself, so the statement uses the reading edition's negative-exponent
convention without replacing it by an untranslated natural exponent.

The proof first evaluates the character sum by a geometric series with ratio
`ζ ^ k / ζ ^ r`, then compares every polynomial coefficient. The canonical
root is `Complex.exp (2 * Real.pi * Complex.I / N)`. A coefficient-extension
corollary shows that a rational input has precisely the embedded rational
packet as output, despite its complex averaging formula.

These are exact identities for arbitrary finite polynomials, without a degree
cutoff or numerical approximation. No infinite-series convergence or
floating-point implementation is asserted. The character identity and the
primitive-root and polynomial-coefficient APIs used below are classical;
Mathlib supplies the cited geometric-series and primitive-root results.
-/

set_option autoImplicit false
open scoped BigOperators Polynomial
open Polynomial

namespace Komorebi.Polynomial.RootsOfUnity

/-- Primitive-root powers agree exactly when their degrees have the same
canonical residue. The right-hand degree is explicitly less than `N`. -/
theorem pow_eq_pow_iff_residue {ζ : ℂ} {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (hζ : IsPrimitiveRoot ζ N) (k : ℕ) :
    ζ ^ k = ζ ^ r ↔ k % N = r := by
  have hmod : ζ ^ (k % N) = ζ ^ k := by
    simpa only [← hζ.eq_orderOf] using pow_mod_orderOf ζ k
  constructor
  · intro h
    exact hζ.pow_inj (Nat.mod_lt k hN) hr (hmod.trans h)
  · intro h
    rw [← hmod, h]

/-- The exact inverse-power character filter retains precisely residue `r`.
Primitivity, positive modulus, and a canonical residue are explicit premises. -/
theorem character_sum {ζ : ℂ} {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (hζ : IsPrimitiveRoot ζ N) (k : ℕ) :
    (∑ ℓ ∈ Finset.range N, ζ ^ (-((r * ℓ : ℕ) : ℤ)) * (ζ ^ ℓ) ^ k) =
      if k % N = r then (N : ℂ) else 0 := by
  have hzero : ζ ≠ 0 := hζ.ne_zero hN.ne'
  have hratio : ζ ^ k / ζ ^ r = 1 ↔ k % N = r := by
    rw [div_eq_one_iff_eq (pow_ne_zero r hzero)]
    exact pow_eq_pow_iff_residue hN hr hζ k
  have hpow : (ζ ^ k / ζ ^ r) ^ N = 1 := by
    have hk : (ζ ^ k) ^ N = 1 := by
      rw [← pow_mul, Nat.mul_comm k N, pow_mul, hζ.pow_eq_one, one_pow]
    have hr' : (ζ ^ r) ^ N = 1 := by
      rw [← pow_mul, Nat.mul_comm r N, pow_mul, hζ.pow_eq_one, one_pow]
    rw [div_pow, hk, hr', div_self one_ne_zero]
  calc
    (∑ ℓ ∈ Finset.range N, ζ ^ (-((r * ℓ : ℕ) : ℤ)) * (ζ ^ ℓ) ^ k) =
        ∑ ℓ ∈ Finset.range N, (ζ ^ k / ζ ^ r) ^ ℓ := by
      apply Finset.sum_congr rfl
      intro ℓ _
      simp only [zpow_neg, zpow_natCast, div_eq_mul_inv, mul_pow, inv_pow, ← pow_mul]
      rw [Nat.mul_comm ℓ k, mul_comm]
    _ = if k % N = r then (N : ℂ) else 0 := by
      by_cases h : k % N = r
      · simp [hratio.mpr h, h]
      · rw [geom_sum_eq (mt hratio.mp h), hpow]
        simp [h]

/-- Dividing the character sum by the nonzero complex cast of `N` gives the
zero-or-one coefficient selector. -/
theorem normalized_character_sum {ζ : ℂ} {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (hζ : IsPrimitiveRoot ζ N) (k : ℕ) :
    (1 / (N : ℂ)) *
        (∑ ℓ ∈ Finset.range N, ζ ^ (-((r * ℓ : ℕ) : ℤ)) * (ζ ^ ℓ) ^ k) =
      if k % N = r then 1 else 0 := by
  rw [character_sum hN hr hζ]
  have hn : (N : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr hN.ne'
  by_cases h : k % N = r <;> simp [h, hn]

/-- The roots-of-unity average, formed inside the actual polynomial ring.
`p.comp (C (ζ ^ ℓ) * X)` is the polynomial substitution `p(ζ^ℓ X)`. -/
noncomputable def average (N r : ℕ) (ζ : ℂ) (p : ℂ[X]) : ℂ[X] :=
  (1 / (N : ℂ)) • ∑ ℓ ∈ Finset.range N,
    (ζ ^ (-((r * ℓ : ℕ) : ℤ))) • p.comp (C (ζ ^ ℓ) * X)

/-- Every coefficient of the cyclotomic average is the selected coefficient
of the original polynomial, or zero outside the requested residue. -/
theorem coeff_average {ζ : ℂ} {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (hζ : IsPrimitiveRoot ζ N)
    (p : ℂ[X]) (k : ℕ) :
    (average N r ζ p).coeff k = if k % N = r then p.coeff k else 0 := by
  simp only [average, coeff_smul, finsetSum_coeff, comp_C_mul_X_coeff, smul_eq_mul]
  calc
    (1 / (N : ℂ)) *
        (∑ ℓ ∈ Finset.range N,
          ζ ^ (-((r * ℓ : ℕ) : ℤ)) * (p.coeff k * (ζ ^ ℓ) ^ k)) =
        ((1 / (N : ℂ)) *
          (∑ ℓ ∈ Finset.range N,
            ζ ^ (-((r * ℓ : ℕ) : ℤ)) * (ζ ^ ℓ) ^ k)) * p.coeff k := by
      rw [mul_assoc, Finset.sum_mul]
      congr 1
      apply Finset.sum_congr rfl
      intro ℓ _
      ring
    _ = if k % N = r then p.coeff k else 0 := by
      rw [normalized_character_sum hN hr hζ]
      by_cases h : k % N = r <;> simp [h]

/-- The complex roots-of-unity averaging formula is exactly the polynomial
residue projector. This is a polynomial identity, not only an equality of
evaluations at a finite set of points. -/
theorem average_eq_packet {ζ : ℂ} {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (hζ : IsPrimitiveRoot ζ N) (p : ℂ[X]) :
    average N r ζ p = Komorebi.Polynomial.Packets.packet N r p := by
  ext k
  rw [coeff_average hN hr hζ, Komorebi.Polynomial.Packets.coeff_packet]

/-- The standard complex exponential supplies the required primitive root for
every positive modulus, including `N = 1`. -/
theorem canonical_average_eq_packet {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (p : ℂ[X]) :
    average N r (Complex.exp (2 * Real.pi * Complex.I / (N : ℂ))) p =
      Komorebi.Polynomial.Packets.packet N r p := by
  exact average_eq_packet hN hr (Complex.isPrimitiveRoot_exp N hN.ne') p

/-- On an embedded rational polynomial, the complex averaging expression is
exactly the embedding of the rational coefficient packet. In particular, its
output coefficients lie in the image of the rational coefficient map. -/
theorem average_rat_map_eq_packet {ζ : ℂ} {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (hζ : IsPrimitiveRoot ζ N) (p : ℚ[X]) :
    average N r ζ (p.map (algebraMap ℚ ℂ)) =
      (Komorebi.Polynomial.Packets.packet N r p).map (algebraMap ℚ ℂ) := by
  rw [average_eq_packet hN hr hζ]
  exact (Komorebi.Polynomial.Packets.packet_map (algebraMap ℚ ℂ) N r p).symm

end Komorebi.Polynomial.RootsOfUnity
