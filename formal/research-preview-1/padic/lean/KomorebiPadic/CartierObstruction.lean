import KomorebiPadic.CartierMaskTransition

/-!
# Exact obstruction to the literal one-layer Cartier normal form

Joint digit injectivity turns section identities into a series identity. Unit
cancellation then identifies it with the Frobenius congruence from Block21.
F must be a unit: a zero series cannot detect a failed mask identity.
-/
namespace KomorebiPadic
open Polynomial

/-- The elementary unit calculation behind the one-layer criterion. -/
theorem oneLayer_unit_criterion {R : Type*} [CommRing R] (u v : Rˣ)
    (p : ℕ) (hp : 2 ≤ p) (A F G : R) (hF : IsUnit F)
    (hM : (u : R)*F = A*G) :
    (F * (↑u⁻¹ : R) = A*(u : R)^(p-2)*(G*(↑v⁻¹ : R))) ↔ (u : R)^p = (v : R) := by
  have hl : (F*(↑u⁻¹ : R))*((u : R)*v) = F*v := by
    calc
      _ = F * ((↑u⁻¹ : R)*u) * v := by ring
      _ = _ := by rw [u.inv_mul]; ring
  have hr : (A*(u : R)^(p-2)*(G*(↑v⁻¹ : R)))*((u : R)*v) = F*(u : R)^p := by
    calc
      _ = (A*G)*(u : R)^(p-2)*u*((↑v⁻¹ : R)*v) := by ring
      _ = ((u : R)*F)*(u : R)^(p-2)*u := by rw [v.inv_mul, mul_one, ← hM]
      _ = F*(u : R)^((p-2)+2) := by rw [pow_add, pow_two]; ring
      _ = _ := by rw [Nat.sub_add_cancel hp]
  have hc : (F*(↑u⁻¹ : R) = A*(u : R)^(p-2)*(G*(↑v⁻¹ : R))) ↔
      (F*(↑u⁻¹ : R))*((u : R)*v) = (A*(u : R)^(p-2)*(G*(↑v⁻¹ : R)))*((u : R)*v) :=
    ⟨fun h => congrArg (· * ((u : R)*v)) h,
      fun h => (u.isUnit.mul v.isUnit).mul_right_cancel h⟩
  rw [hc, hl, hr]
  constructor
  · intro h
    exact (hF.mul_left_cancel h).symm
  · intro h
    rw [h]

/-- Equality in the series inclusion is equality of the reduced polynomials. -/
theorem integerPolynomialSeriesHom_eq_iff (R : Type*) [CommRing R] (P Q : ℤ[X]) :
    integerPolynomialSeriesHom R P = integerPolynomialSeriesHom R Q ↔
      P.map (Int.castRingHom R) = Q.map (Int.castRingHom R) := by
  exact Polynomial.coe_inj

/-- Literal one-layer identities for every polynomial numerator and in-range digit. -/
def LiteralOneLayerCartier (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) : Prop :=
  ∀ (P : ℤ[X]) d, d < p →
    cartierSection p d (integerPolynomialSeriesHom (ZMod (p^r)) P *
      maskLayerSeries p r B hp hr hB F 1) =
    cartierSection p d (integerPolynomialSeriesHom (ZMod (p^r)) (P*A*B^(p-2))) *
      maskLayerSeries p r B hp hr hB F 1

/-- All numerator identities are equivalent to the unsectioned unit-layer identity. -/
theorem literalOneLayerCartier_iff_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) :
    LiteralOneLayerCartier p r A B hp hr hB F ↔
      maskLayerSeries p r B hp hr hB F 1 =
        integerPolynomialSeriesHom (ZMod (p^r)) (A*B^(p-2)) *
          PowerSeries.expand p hp.ne_zero (maskLayerSeries p r B hp hr hB F 1) := by
  constructor
  · intro hall
    apply cartierSection_joint_injective hp.pos
    intro d hd
    rw [cartierSection_mul_expand hp.ne_zero hd]
    simpa only [map_one, one_mul] using hall 1 d hd
  · intro he P d hd
    calc
      _ = cartierSection p d
          ((integerPolynomialSeriesHom (ZMod (p^r)) P *
            integerPolynomialSeriesHom (ZMod (p^r)) (A*B^(p-2))) *
            PowerSeries.expand p hp.ne_zero (maskLayerSeries p r B hp hr hB F 1)) := by
        conv_lhs => rw [he]
        rw [mul_assoc]
      _ = _ := by
        rw [cartierSection_mul_expand hp.ne_zero hd]
        simp only [map_mul, mul_assoc]

/-- Testing P=1 at every digit already detects the literal one-layer property. -/
theorem literalOneLayerCartier_iff_unit_numerator (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) :
    LiteralOneLayerCartier p r A B hp hr hB F ↔
      ∀ d, d < p → cartierSection p d (maskLayerSeries p r B hp hr hB F 1) =
        cartierSection p d (integerPolynomialSeriesHom (ZMod (p^r)) (A*B^(p-2))) *
          maskLayerSeries p r B hp hr hB F 1 := by
  constructor
  · intro h d hd
    simpa only [map_one, one_mul] using h 1 d hd
  · intro h
    apply (literalOneLayerCartier_iff_series p r A B hp hr hB F).mpr
    apply cartierSection_joint_injective hp.pos
    intro d hd
    rw [cartierSection_mul_expand hp.ne_zero hd]
    exact h d hd

/-- Necessary and sufficient Frobenius congruence for the actual Cartier identities. -/
theorem literalOneLayerCartier_iff_frobenius (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : IsUnit F)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    LiteralOneLayerCartier p r A B hp hr hB F ↔
      (B^p).map (Int.castRingHom (ZMod (p^r))) =
        (Polynomial.expand ℤ p B).map (Int.castRingHom (ZMod (p^r))) := by
  rw [literalOneLayerCartier_iff_series]
  simp only [maskLayerSeries, pow_one, map_mul, map_pow, expand_maskSeriesUnit_inv]
  have hm : (maskSeriesUnit p r B hp hr hB : PowerSeries (ZMod (p^r))) * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F := by
    simpa only [maskSeriesUnit_val] using hM
  have hu := oneLayer_unit_criterion (maskSeriesUnit p r B hp hr hB)
    (expandedMaskSeriesUnit p r B hp hr hB) p hp.two_le
    (integerPolynomialSeriesHom (ZMod (p^r)) A) F (PowerSeries.expand p hp.ne_zero F) hF hm
  simp only [maskSeriesUnit_val, expandedMaskSeriesUnit_val] at hu
  rw [hu, ← map_pow, integerPolynomialSeriesHom_eq_iff]

/-- The original exact defect obstruction, now at the level of all actual Cartier sections. -/
theorem literalOneLayerCartier_iff_defectVanishing (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : IsUnit F)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    LiteralOneLayerCartier p r A B hp hr hB F ↔
      PolynomialVanishing p (r-1) (frobeniusDefect p B) := by
  obtain ⟨s, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hr.ne'
  rw [literalOneLayerCartier_iff_frobenius p (s+1) A B hp hr hB F hF hM]
  simpa only [Nat.succ_eq_add_one, Nat.add_sub_cancel] using (frobeniusDefect_congruence_iff hp B s)

/-- For nonzero defect the unchanged normal form survives exactly through h+1. -/
theorem literalOneLayerCartier_iff_defectDepth (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : IsUnit F) (hE : frobeniusDefect p B ≠ 0)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    LiteralOneLayerCartier p r A B hp hr hB F ↔
      r ≤ polynomialPadicOrder p (frobeniusDefect p B) + 1 := by
  rw [literalOneLayerCartier_iff_defectVanishing p r A B hp hr hB F hF hM,
    polynomialVanishing_iff_le_order hp (r-1) _ hE]
  omega

/-- Normalization F(0)=1 supplies precisely the unit hypothesis used by the obstruction. -/
theorem normalizedSeries_isUnit {R : Type*} [CommRing R] (F : PowerSeries R)
    (hF : PowerSeries.constantCoeff F = 1) : IsUnit F := by
  apply PowerSeries.isUnit_iff_constantCoeff.mpr
  rw [hF]
  exact isUnit_one

/-- The unit hypothesis is essential: zero series satisfies every digit identity for any mask. -/
theorem literalOneLayerCartier_zero_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    LiteralOneLayerCartier p r A B hp hr hB 0 := by
  intro P d _
  simp [maskLayerSeries]

/-- A zero series hides a genuine defect at modulus four; it cannot detect this obstruction. -/
theorem zeroSeries_cannot_detect_frobenius_defect :
    LiteralOneLayerCartier 2 2 (1+X) (1+X) (by decide) (by decide)
      (by norm_num) 0 ∧ ¬ PolynomialVanishing 2 1 (frobeniusDefect 2 (1+X)) := by
  constructor
  · exact literalOneLayerCartier_zero_series _ _ _ _ _ _ _
  · have he : frobeniusDefect 2 (1+X) = (X : ℤ[X]) := by
      symm
      apply frobeniusDefect_unique (by decide)
      simp only [map_add, map_one, Polynomial.expand_X]
      norm_num
      ring
    intro hv
    have hc := hv 1
    norm_num [he] at hc

/-- The in-range restriction on the digit-product law cannot be removed. -/
theorem cartierSection_product_requires_digit_bound :
    cartierSection 2 2 ((1 : PowerSeries ℤ) * PowerSeries.expand 2 (by decide) PowerSeries.X) ≠
      cartierSection 2 2 (1 : PowerSeries ℤ) * PowerSeries.X := by
  intro h
  have hc := congrArg (PowerSeries.coeff 0) h
  norm_num [coeff_cartierSection, PowerSeries.expand_X] at hc

end KomorebiPadic
