import KomorebiPadic.MahlerConstruction
import KomorebiPadic.FiniteMaskAutomaton

/-! # Canonical normalized mask solutions and unconditional finite-machine output
The only input assumptions are mask data, prime-power precision, unit denominator
constant, and equality of the mask constants in the coefficient ring. No supplied
series or Mahler-equation oracle remains in the coefficient-output theorem.
-/
namespace KomorebiPadic
open Polynomial

/-- Mask constant compatibility is required only after coefficient reduction. -/
def MaskConstantsAgree (p r : ℕ) (A B : ℤ[X]) : Prop :=
  (A.coeff 0 : ZMod (p^r)) = (B.coeff 0 : ZMod (p^r))

/-- The uniquely normalized series constructed from integer mask data alone. -/
noncomputable def canonicalMaskSeries (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    PowerSeries (ZMod (p^r)) :=
  normalizedMahlerMaskSeries p hp.one_lt
    (integerPolynomialSeriesHom (ZMod (p^r)) A)
    (integerPolynomialSeriesHom (ZMod (p^r)) B) (maskSeries_isUnit hp hr B hB)

@[simp] theorem canonicalMaskSeries_constant (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    PowerSeries.constantCoeff (canonicalMaskSeries p r A B hp hr hB) = 1 :=
  normalizedMahlerMaskSeries_constant p hp.one_lt _ _ _

theorem canonicalMaskSeries_equation (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) :
    integerPolynomialSeriesHom (ZMod (p^r)) B * canonicalMaskSeries p r A B hp hr hB =
      integerPolynomialSeriesHom (ZMod (p^r)) A *
        PowerSeries.expand p hp.ne_zero (canonicalMaskSeries p r A B hp hr hB) := by
  apply normalizedMahlerMaskSeries_equation
  simpa only [← PowerSeries.coeff_zero_eq_constantCoeff, integerPolynomialSeriesHom_coeff, MaskConstantsAgree] using hAB

theorem canonicalMaskSeries_unique (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B)
    (F : PowerSeries (ZMod (p^r))) (hF : PowerSeries.constantCoeff F = 1)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    F = canonicalMaskSeries p r A B hp hr hB := by
  apply normalizedMahlerMaskSeries_unique p hp.one_lt _ _ _ _ F hF hM
  simpa only [← PowerSeries.coeff_zero_eq_constantCoeff, integerPolynomialSeriesHom_coeff, MaskConstantsAgree] using hAB

theorem canonicalMaskSeries_isUnit (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    IsUnit (canonicalMaskSeries p r A B hp hr hB) := by
  apply PowerSeries.isUnit_iff_constantCoeff.mpr
  rw [canonicalMaskSeries_constant]
  exact isUnit_one

/-- Exact existence and uniqueness from mask conditions, without an external F. -/
theorem existsUnique_canonicalMaskSeries (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) :
    ∃! F : PowerSeries (ZMod (p^r)), PowerSeries.constantCoeff F = 1 ∧
      integerPolynomialSeriesHom (ZMod (p^r)) B * F =
        integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F := by
  refine ⟨canonicalMaskSeries p r A B hp hr hB,
    ⟨canonicalMaskSeries_constant p r A B hp hr hB,
      canonicalMaskSeries_equation p r A B hp hr hB hAB⟩, ?_⟩
  intro F hF
  exact canonicalMaskSeries_unique p r A B hp hr hB hAB F hF.1 hF.2

/-- Under a unit denominator, reduced constant compatibility is also necessary. -/
theorem exists_normalizedMaskSeries_iff (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (∃ F : PowerSeries (ZMod (p^r)), PowerSeries.constantCoeff F = 1 ∧
      integerPolynomialSeriesHom (ZMod (p^r)) B * F =
        integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) ↔
      MaskConstantsAgree p r A B := by
  have h := exists_normalizedMahlerMask_iff p hp.one_lt
    (integerPolynomialSeriesHom (ZMod (p^r)) A)
    (integerPolynomialSeriesHom (ZMod (p^r)) B) (maskSeries_isUnit hp hr B hB)
  simpa only [← PowerSeries.coeff_zero_eq_constantCoeff, integerPolynomialSeriesHom_coeff,
    MaskConstantsAgree] using h

/-- The existing finite machine computes the constructed solution for every digit word. -/
theorem finiteMask_output_canonical_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) ds (finiteMaskInitial p r A B)) =
        PowerSeries.coeff (cartierWordValue p ds) (canonicalMaskSeries p r A B hp hr hB) :=
  finiteMask_output_word p r A B hp hr hB _
    (canonicalMaskSeries_constant p r A B hp hr hB)
    (canonicalMaskSeries_equation p r A B hp hr hB hAB) ds hd

/-- No supplied series or equation assumption remains in the all-coefficient theorem. -/
theorem finiteMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) (Nat.digits p n)
        (finiteMaskInitial p r A B)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) :=
  finiteMask_output_coefficient p r A B hp hr hB _
    (canonicalMaskSeries_constant p r A B hp hr hB)
    (canonicalMaskSeries_equation p r A B hp hr hB hAB) n

/-- Integer polynomial inclusion commutes with every coefficient ring homomorphism. -/
theorem integerPolynomialSeriesHom_natural {R S : Type*} [CommRing R] [CommRing S]
    (f : R →+* S) (P : ℤ[X]) :
    PowerSeries.map f (integerPolynomialSeriesHom R P) = integerPolynomialSeriesHom S P := by
  ext n
  simp only [PowerSeries.coeff_map, integerPolynomialSeriesHom_coeff, map_intCast]

/-- Any coefficient map between two precisions transports the canonical solutions exactly. -/
theorem canonicalMaskSeries_map (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hABr : MaskConstantsAgree p r A B) (hABs : MaskConstantsAgree p s A B)
    (f : ZMod (p^r) →+* ZMod (p^s)) :
    PowerSeries.map f (canonicalMaskSeries p r A B hp hr hB) =
      canonicalMaskSeries p s A B hp hs hB := by
  apply canonicalMaskSeries_unique p s A B hp hs hB hABs
  · change f (PowerSeries.constantCoeff (canonicalMaskSeries p r A B hp hr hB)) = 1
    rw [canonicalMaskSeries_constant, map_one]
  · have he := congrArg (PowerSeries.map f) (canonicalMaskSeries_equation p r A B hp hr hB hABr)
    simpa only [map_mul, PowerSeries.map_expand, integerPolynomialSeriesHom_natural] using he

/-- Higher-precision constant compatibility descends along every coefficient map. -/
theorem MaskConstantsAgree.map {p r s : ℕ} {A B : ℤ[X]}
    (hAB : MaskConstantsAgree p r A B) (f : ZMod (p^r) →+* ZMod (p^s)) :
    MaskConstantsAgree p s A B := by
  have h := congrArg f hAB
  simpa only [MaskConstantsAgree, map_intCast] using h

/-- The canonical series are exactly compatible across prime-power precision reductions. -/
theorem canonicalMaskSeries_reduce (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    PowerSeries.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s)))
      (canonicalMaskSeries p r A B hp hr hB) =
      canonicalMaskSeries p s A B hp hs hB := by
  exact canonicalMaskSeries_map p r s A B hp hr hs hB hAB
    (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s)))) _

/-- Outputs of the finite machines at different precisions reduce to one another. -/
theorem finiteMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (finiteMaskOutput p r A B hp hr hB
        (iterateMachine (finiteMaskMachine p r A B hp.one_lt) (Nat.digits p n)
          (finiteMaskInitial p r A B))) =
      finiteMaskOutput p s A B hp hs hB
        (iterateMachine (finiteMaskMachine p s A B hp.one_lt) (Nat.digits p n)
          (finiteMaskInitial p s A B)) := by
  rw [finiteMask_output_canonical_coefficient p r A B hp hr hB hAB,
    finiteMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

/-- Equal numerator and denominator masks give the constant solution one. -/
@[simp] theorem canonicalMaskSeries_self (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    canonicalMaskSeries p r B B hp hr hB = 1 := by
  symm
  apply canonicalMaskSeries_unique p r B B hp hr hB rfl _ (by simp)
  simp

/-- A full certificate constructs the normalized series and closes the existing finite machine. -/
structure CanonicalFiniteMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  series : PowerSeries (ZMod (p^r))
  series_eq : series = canonicalMaskSeries p r A B hp hr hB
  normalized : PowerSeries.constantCoeff series = 1
  equation : integerPolynomialSeriesHom (ZMod (p^r)) B * series =
    integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero series
  unique : ∀ F : PowerSeries (ZMod (p^r)), PowerSeries.constantCoeff F = 1 →
    integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F → F = series
  unit : IsUnit series
  output : ∀ n, finiteMaskOutput p r A B hp hr hB
    (iterateMachine (finiteMaskMachine p r A B hp.one_lt) (Nat.digits p n)
      (finiteMaskInitial p r A B)) = PowerSeries.coeff n series
  state_card : Nat.card (CartierCoefficientState (ZMod (p^r))
    (cartierLayerBound p r) (cartierNumeratorBound p r A B)) =
    p^(r*(cartierLayerBound p r)*(cartierNumeratorBound p r A B+1))

noncomputable def canonicalFiniteMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) : CanonicalFiniteMaskCertificate p r A B hp hr hB where
  series := canonicalMaskSeries p r A B hp hr hB
  series_eq := rfl
  normalized := canonicalMaskSeries_constant p r A B hp hr hB
  equation := canonicalMaskSeries_equation p r A B hp hr hB hAB
  unique := fun F hF hM => canonicalMaskSeries_unique p r A B hp hr hB hAB F hF hM
  unit := canonicalMaskSeries_isUnit p r A B hp hr hB
  output := finiteMask_output_canonical_coefficient p r A B hp hr hB hAB
  state_card := finiteMask_state_card p r A B hp

end KomorebiPadic
