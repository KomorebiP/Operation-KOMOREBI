import KomorebiPadic.CartierDegreeClosure
import Mathlib.Data.Nat.Digits.Defs

/-! # Actual finite-state representation of a rational-mask Mahler series
F and its equation remain explicit inputs. States and transitions depend only on
p,r,A,B. No minimality, effective polynomial runtime, or existence of F is asserted.
-/
namespace KomorebiPadic
open Polynomial

@[simp] theorem finiteMaskKernel_series (p r ell k : ℕ) (A B : ℤ[X]) :
    (finiteMaskKernel p r ell k A B : PowerSeries (ZMod (p^r))) =
      integerPolynomialSeriesHom (ZMod (p^r))
        (A*B^maskPadding p ell*cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B)) := rfl

/-- Extend the inherited transition to arbitrary residue-polynomial numerators. -/
theorem residuePolynomial_cartier_transition (p r ell d : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hd : d < p) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r)))
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F)
    (P : (ZMod (p^r))[X]) :
    cartierSection p d ((P : PowerSeries (ZMod (p^r))) * maskLayerSeries p r B hp hr hB F ell) =
      ∑ k ∈ Finset.range r,
        (polynomialCartier p d (P*finiteMaskKernel p r ell k A B) : PowerSeries (ZMod (p^r))) *
          maskLayerSeries p r B hp hr hB F (quotientOfLayer p ell+k) := by
  have hb := maskLayerSeries_preCartier_transition p r ell 1 A B hp hr hB F hM
  simp only [map_one, one_mul] at hb
  rw [hb, Finset.mul_sum, map_sum]
  apply Finset.sum_congr rfl
  intro k _
  rw [← mul_assoc, ← finiteMaskKernel_series,
    ← Polynomial.coe_mul, cartierSection_mul_expand hp.ne_zero hd,
    ← polynomialCartier_coe hp.pos]

/-- The finite target index represents denominator layer q_ell+k. -/
def finiteMaskTarget (p r : ℕ) (hp : 1 < p)
    (i : Fin (cartierLayerBound p r)) (k : Fin r) : Fin (cartierLayerBound p r) :=
  ⟨quotientOfLayer p (i.val+1)+k.val-1, by
    have hb := cartierLayerBound_closed hp (show i.val+1 ≤ cartierLayerBound p r by omega) k.isLt
    have hq : 0 < quotientOfLayer p (i.val+1) := Nat.succ_pos _
    omega⟩

@[simp] theorem finiteMaskTarget_layer (p r : ℕ) (hp : 1 < p)
    (i : Fin (cartierLayerBound p r)) (k : Fin r) :
    (finiteMaskTarget p r hp i k).val+1 = quotientOfLayer p (i.val+1)+k.val := by
  have hq : 0 < quotientOfLayer p (i.val+1) := Nat.succ_pos _
  simp only [finiteMaskTarget]
  omega

noncomputable def finiteMaskMachine (p r : ℕ) (A B : ℤ[X]) (hp : 1 < p) :
    PolynomialCartierMachine (ZMod (p^r)) p (cartierLayerBound p r) r (cartierNumeratorBound p r A B) where
  radix_pos := by omega
  target := finiteMaskTarget p r hp
  kernel i k := finiteMaskKernel p r (i.val+1) k.val A B
  kernel_degree i k := finiteMaskKernel_degree hp k.isLt A B

noncomputable def finiteMaskLayers (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) : Fin (cartierLayerBound p r) → PowerSeries (ZMod (p^r)) :=
  fun i => maskLayerSeries p r B hp hr hB F (i.val+1)

/-- The generic finite machine's branch law is discharged, not an extra assumption. -/
theorem finiteMaskMachine_branch_law (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r)))
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F)
    (d : ℕ) (hd : d < p) (i : Fin (cartierLayerBound p r)) (P : (ZMod (p^r))[X]) :
    cartierSection p d ((P : PowerSeries (ZMod (p^r))) * finiteMaskLayers p r B hp hr hB F i) =
      ∑ k : Fin r,
        (polynomialCartier p d (P*(finiteMaskMachine p r A B hp.one_lt).kernel i k) : PowerSeries (ZMod (p^r))) *
          finiteMaskLayers p r B hp hr hB F ((finiteMaskMachine p r A B hp.one_lt).target i k) := by
  simp only [finiteMaskMachine, finiteMaskLayers, finiteMaskTarget_layer]
  have ht := residuePolynomial_cartier_transition p r (i.val+1) d A B hp hr hd hB F hM P
  rw [Finset.sum_range] at ht
  exact ht

noncomputable def finiteMaskInitial (p r : ℕ) (A B : ℤ[X]) :
    CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r) (cartierNumeratorBound p r A B) :=
  fun i => if i.val = 0 then
    numeratorCoordinates (cartierNumeratorBound p r A B) (B.map (Int.castRingHom (ZMod (p^r)))) else 0

/-- The distinguished coefficient vector represents the supplied actual series F. -/
theorem finiteMaskInitial_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) :
    machineSeries (finiteMaskLayers p r B hp hr hB F) (finiteMaskInitial p r A B) = F := by
  classical
  let i0 : Fin (cartierLayerBound p r) := ⟨0, cartierLayerBound_pos hp.one_lt hr⟩
  unfold machineSeries
  rw [Finset.sum_eq_single i0]
  · simp only [finiteMaskInitial, i0, ↓reduceIte]
    rw [numeratorPolynomial_coordinates _ (Polynomial.natDegree_map_le.trans (cartierNumeratorBound_initial p r A B))]
    exact maskLayerSeries_initial p r B hp hr hB F
  · intro i _ hi
    have hi0 : i.val ≠ 0 := by intro hv; apply hi; exact Fin.ext hv
    simp [finiteMaskInitial, hi0, numeratorPolynomial]
  · simp

/-- Output depends only on coefficient zero and the denominator's constant inverse, not on F. -/
noncomputable def finiteMaskOutput (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (s : CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r) (cartierNumeratorBound p r A B)) :
    ZMod (p^r) :=
  ∑ i : Fin (cartierLayerBound p r),
    s i ⟨0, Nat.succ_pos _⟩ *
      (PowerSeries.constantCoeff (↑((maskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p^r))))^(i.val+1)

/-- Under normalized F the output is exactly the represented series' constant coefficient. -/
theorem finiteMaskOutput_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : PowerSeries.constantCoeff F = 1)
    (s : CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r) (cartierNumeratorBound p r A B)) :
    finiteMaskOutput p r A B hp hr hB s =
      PowerSeries.constantCoeff (machineSeries (finiteMaskLayers p r B hp hr hB F) s) := by
  classical
  unfold finiteMaskOutput machineSeries
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro i _
  simp [finiteMaskLayers, maskLayerSeries, hF, numeratorPolynomial]

/-- Exact output for any in-range least-significant-first digit word. -/
theorem finiteMask_output_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : PowerSeries.constantCoeff F = 1)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F)
    (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) ds (finiteMaskInitial p r A B)) =
        PowerSeries.coeff (cartierWordValue p ds) F := by
  rw [finiteMaskOutput_series p r A B hp hr hB F hF]
  rw [iterateMachine_output _ _ (finiteMaskMachine_branch_law p r A B hp hr hB F hM) ds hd,
    finiteMaskInitial_series p r A B hp hr hB F]

theorem cartierWordValue_eq_ofDigits (p : ℕ) (ds : List ℕ) :
    cartierWordValue p ds = Nat.ofDigits p ds := by
  induction ds with
  | nil => rfl
  | cons d ds ih => simp [cartierWordValue, Nat.ofDigits, ih]

/-- Every natural coefficient is recovered from its canonical base-p digit expansion. -/
theorem finiteMask_output_coefficient (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : PowerSeries.constantCoeff F = 1)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F)
    (n : ℕ) :
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) (Nat.digits p n) (finiteMaskInitial p r A B)) =
        PowerSeries.coeff n F := by
  rw [finiteMask_output_word p r A B hp hr hB F hF hM _
    (fun d hd => Nat.digits_lt_base hp.one_lt hd), cartierWordValue_eq_ofDigits, Nat.ofDigits_digits]

/-- Exact ambient state count. This need not be the number of reachable states. -/
theorem finiteMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r) (cartierNumeratorBound p r A B)) =
      p^(r*(cartierLayerBound p r)*(cartierNumeratorBound p r A B+1)) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  rw [Nat.card_eq_fintype_card, cartierCoefficientState_card, ZMod.card]
  simp only [← pow_mul, Nat.mul_assoc]

/-- The chosen series inverse has the ordinary unit inverse as its constant coefficient. -/
theorem maskSeriesUnit_inverse_constant (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    PowerSeries.constantCoeff (↑((maskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p^r))) =
      (B.coeff 0 : ZMod (p^r))⁻¹ := by
  symm
  apply ZMod.inv_eq_of_mul_eq_one
  have h := congrArg (PowerSeries.constantCoeff : PowerSeries (ZMod (p^r)) → ZMod (p^r))
    (maskSeriesUnit p r B hp hr hB).mul_inv
  have hc : PowerSeries.constantCoeff (integerPolynomialSeriesHom (ZMod (p^r)) B) =
      (B.coeff 0 : ZMod (p^r)) := by
    rw [← PowerSeries.coeff_zero_eq_constantCoeff, integerPolynomialSeriesHom_coeff]
  simpa only [map_mul, map_one, maskSeriesUnit_val, hc] using h

/-- The output formula is finite and uses no coefficient of F. -/
theorem finiteMaskOutput_eq_coefficients (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (s : CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r) (cartierNumeratorBound p r A B)) :
    finiteMaskOutput p r A B hp hr hB s =
      ∑ i : Fin (cartierLayerBound p r),
        s i ⟨0, Nat.succ_pos _⟩ * ((B.coeff 0 : ZMod (p^r))⁻¹)^(i.val+1) := by
  unfold finiteMaskOutput
  rw [maskSeriesUnit_inverse_constant]

noncomputable def finiteMaskOutputLinear (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r) (cartierNumeratorBound p r A B) →ₗ[ZMod (p^r)] ZMod (p^r) where
  toFun := finiteMaskOutput p r A B hp hr hB
  map_add' s t := by
    simp [finiteMaskOutput, Pi.add_apply, add_mul, Finset.sum_add_distrib]
  map_smul' a s := by
    simp [finiteMaskOutput, Pi.smul_apply, smul_eq_mul, Finset.mul_sum, mul_assoc]

end KomorebiPadic
