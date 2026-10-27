import KomorebiPadic.PolynomialBranchValuation
import KomorebiPadic.MaximumLayerCompiler
import KomorebiPadic.NilpotentReciprocal
import Mathlib.RingTheory.PowerSeries.Inverse

/-!
# Actual integer masks and finite formal-series reciprocals

This module transports the proved integral identity into formal power series over
Z/(p^r). A p-unit constant coefficient supplies a genuine denominator unit.
The finite sum has precisely the polynomial weights used in the valuation-edge
bridge. The remaining Cartier digit-product identity is not assumed or claimed.
-/
namespace KomorebiPadic
open Polynomial

/-- Canonical map from integer polynomials to formal series over any commutative ring. -/
noncomputable def integerPolynomialSeriesHom (R : Type*) [CommRing R] :
    ℤ[X] →+* PowerSeries R :=
  (Polynomial.coeToPowerSeries.ringHom).comp (Polynomial.mapRingHom (Int.castRingHom R))

/-- Prime Frobenius identity after mapping the actual integer mask to formal series. -/
theorem frobeniusDefect_series_identity {p : ℕ} (hp : p.Prime)
    (R : Type*) [CommRing R] (B : ℤ[X]) :
    (integerPolynomialSeriesHom R B) ^ p =
      integerPolynomialSeriesHom R (expand ℤ p B) +
        (p : PowerSeries R) * integerPolynomialSeriesHom R (frobeniusDefect p B) := by
  have h := congrArg (integerPolynomialSeriesHom R) (frobeniusDefect_identity hp B)
  simpa using h

/-- An integer not divisible by p is a unit modulo every positive power of p. -/
theorem intCast_isUnit_primePower {p r : ℕ} (hp : p.Prime) (hr : 0 < r)
    (a : ℤ) (ha : ¬ (p : ℤ) ∣ a) : IsUnit (a : ZMod (p ^ r)) := by
  have hn : ¬ p ∣ a.natAbs := by
    intro h
    apply ha
    exact Int.natCast_dvd.mpr h
  have hu : IsUnit (a.natAbs : ZMod (p ^ r)) :=
    (ZMod.isUnit_natCast_iff_not_dvd_pow hp hr).mpr hn
  rcases Int.natAbs_eq a with h | h
  · have he : (a : ZMod (p ^ r)) = (a.natAbs : ZMod (p ^ r)) := by
      simpa only [Int.cast_natCast] using congrArg (fun z : ℤ => (z : ZMod (p ^ r))) h
    rw [he]
    exact hu
  · have he : (a : ZMod (p ^ r)) = -(a.natAbs : ZMod (p ^ r)) := by
      simpa only [Int.cast_neg, Int.cast_natCast] using congrArg (fun z : ℤ => (z : ZMod (p ^ r))) h
    rw [he]
    exact hu.neg

/-- The expanded mask is a unit as a formal series, derived from its constant term. -/
theorem expandedMaskSeries_isUnit {p r : ℕ} (hp : p.Prime) (hr : 0 < r)
    (B : ℤ[X]) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    IsUnit (integerPolynomialSeriesHom (ZMod (p ^ r)) (expand ℤ p B)) := by
  apply PowerSeries.isUnit_iff_constantCoeff.mpr
  change IsUnit (PowerSeries.constantCoeff
    (((expand ℤ p B).map (Int.castRingHom (ZMod (p ^ r)))) : PowerSeries (ZMod (p ^ r))))
  rw [Polynomial.constantCoeff_coe, Polynomial.coeff_map]
  change IsUnit (((expand ℤ p B).coeff 0 : ℤ) : ZMod (p ^ r))
  rw [Polynomial.coeff_expand hp.pos]
  simp only [dvd_zero, ↓reduceIte, Nat.zero_div]
  exact intCast_isUnit_primePower hp hr (B.coeff 0) hB

/-- A denominator unit whose value is the actual expanded integer mask. -/
noncomputable def expandedMaskSeriesUnit (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (PowerSeries (ZMod (p ^ r)))ˣ :=
  (expandedMaskSeries_isUnit hp hr B hB).unit

@[simp] theorem expandedMaskSeriesUnit_val (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (expandedMaskSeriesUnit p r B hp hr hB : PowerSeries (ZMod (p ^ r))) =
      integerPolynomialSeriesHom (ZMod (p ^ r)) (expand ℤ p B) :=
  (expandedMaskSeries_isUnit hp hr B hB).unit_spec

/-- The explicit reciprocal sum for B^(p*q) in formal series over Z/(p^r). -/
noncomputable def maskReciprocalSum (p q r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    PowerSeries (ZMod (p ^ r)) :=
  ∑ k ∈ Finset.range r,
    integerPolynomialSeriesHom (ZMod (p ^ r)) (cartierBranchWeight p q k (frobeniusDefect p B)) *
      (↑((expandedMaskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p ^ r))) ^ (q + k)

/-- The transported polynomial branch weights equal the finite nilpotent expansion termwise. -/
theorem maskReciprocalSum_eq_finiteCorrectionInverse (p q r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    maskReciprocalSum p q r B hp hr hB =
      finiteCorrectionInverse q r (expandedMaskSeriesUnit p r B hp hr hB)
        ((p : PowerSeries (ZMod (p ^ r))) *
          integerPolynomialSeriesHom (ZMod (p ^ r)) (frobeniusDefect p B)) := by
  unfold maskReciprocalSum finiteCorrectionInverse
  apply Finset.sum_congr rfl
  intro k _
  simp [cartierBranchWeight, negativeBinomialCoeff, mul_pow]
  ring

/-- Exact finite reciprocal identity for the original mask, not an abstract assumed denominator. -/
theorem maskReciprocalSum_spec (p q r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (integerPolynomialSeriesHom (ZMod (p ^ r)) B) ^ (p * q) *
      maskReciprocalSum p q r B hp hr hB = 1 := by
  rw [pow_mul, frobeniusDefect_series_identity hp,
    maskReciprocalSum_eq_finiteCorrectionInverse]
  have hz : (p : ZMod (p ^ r)) ^ r = 0 := by
    rw [← Nat.cast_pow, CharP.cast_eq_zero (ZMod (p ^ r)) (p ^ r)]
  have hps : (p : PowerSeries (ZMod (p ^ r))) ^ r = 0 := by
    simpa only [map_pow, map_natCast, map_zero] using congrArg
      (PowerSeries.C : ZMod (p ^ r) →+* PowerSeries (ZMod (p ^ r))) hz
  have hnil : ((p : PowerSeries (ZMod (p ^ r))) *
      integerPolynomialSeriesHom (ZMod (p ^ r)) (frobeniusDefect p B)) ^ r = 0 := by
    rw [mul_pow, hps, zero_mul]
  have h := finiteCorrectionInverse_spec q r (expandedMaskSeriesUnit p r B hp hr hB)
    ((p : PowerSeries (ZMod (p ^ r))) *
      integerPolynomialSeriesHom (ZMod (p ^ r)) (frobeniusDefect p B)) hr hnil
  simpa using h


/-- Padding exponent for the actual denominator B^(ell+1). -/
def maskPadding (p ell : ℕ) : ℕ :=
  p * quotientOfLayer p ell - (ell + 1)

/-- The existing quotient index gives exactly the Euclidean padding in [0,p). -/
theorem maskPadding_spec {p ell : ℕ} (hp : 0 < p) :
    p * quotientOfLayer p ell = ell + 1 + maskPadding p ell ∧
      maskPadding p ell < p := by
  have hm := Nat.mod_add_div ell p
  have hl := Nat.mod_lt ell hp
  unfold maskPadding quotientOfLayer
  rw [Nat.mul_add, Nat.mul_one]
  omega

/-- The finite sum also inverts B^(ell+1) after multiplication by its padding power.
This is the denominator identity needed before the Cartier digit-product step. -/
theorem paddedMaskReciprocalSum_spec (p ell r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (integerPolynomialSeriesHom (ZMod (p ^ r)) B) ^ (ell + 1) *
      ((integerPolynomialSeriesHom (ZMod (p ^ r)) B) ^ maskPadding p ell *
        maskReciprocalSum p (quotientOfLayer p ell) r B hp hr hB) = 1 := by
  rw [← mul_assoc, ← pow_add, ← (maskPadding_spec (ell := ell) hp.pos).1]
  exact maskReciprocalSum_spec p (quotientOfLayer p ell) r B hp hr hB

end KomorebiPadic

