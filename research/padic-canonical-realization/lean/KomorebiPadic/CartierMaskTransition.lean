import KomorebiPadic.MaskReciprocalBridge
import KomorebiPadic.CartierSection

/-!
# Exact Cartier transitions for actual rational masks

The Mahler equation is an explicit hypothesis on the actual series F. Denominator
units and their finite reciprocals are constructed from the integer mask. The
conclusion is an identity of complete formal series over ZMod(p^r).
-/
namespace KomorebiPadic
open Polynomial

@[simp] theorem integerPolynomialSeriesHom_coeff (R : Type*) [CommRing R]
    (P : ℤ[X]) (n : ℕ) :
    PowerSeries.coeff n (integerPolynomialSeriesHom R P) = (P.coeff n : R) := by
  simp [integerPolynomialSeriesHom]

/-- Polynomial exponent expansion agrees with actual formal-series substitution. -/
theorem integerPolynomialSeriesHom_expand (R : Type*) [CommRing R]
    (p : ℕ) (hp : p ≠ 0) (P : ℤ[X]) :
    integerPolynomialSeriesHom R (Polynomial.expand ℤ p P) =
      PowerSeries.expand p hp (integerPolynomialSeriesHom R P) := by
  ext n
  rw [integerPolynomialSeriesHom_coeff, PowerSeries.coeff_expand,
    Polynomial.coeff_expand (Nat.pos_of_ne_zero hp)]
  split_ifs <;> simp

/-- The unexpanded denominator is a unit, also derived from the constant term. -/
theorem maskSeries_isUnit {p r : ℕ} (hp : p.Prime) (hr : 0 < r)
    (B : ℤ[X]) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    IsUnit (integerPolynomialSeriesHom (ZMod (p^r)) B) := by
  apply PowerSeries.isUnit_iff_constantCoeff.mpr
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, integerPolynomialSeriesHom_coeff]
  exact intCast_isUnit_primePower hp hr (B.coeff 0) hB

noncomputable def maskSeriesUnit (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (PowerSeries (ZMod (p^r)))ˣ := (maskSeries_isUnit hp hr B hB).unit

@[simp] theorem maskSeriesUnit_val (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (maskSeriesUnit p r B hp hr hB : PowerSeries (ZMod (p^r))) =
      integerPolynomialSeriesHom (ZMod (p^r)) B :=
  (maskSeries_isUnit hp hr B hB).unit_spec

/-- Expansion commutes with the constructed reciprocal; choices of units do not matter. -/
theorem expand_maskSeriesUnit_inv (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    PowerSeries.expand p hp.ne_zero
        (↑((maskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p^r))) =
      ↑((expandedMaskSeriesUnit p r B hp hr hB)⁻¹) := by
  apply Units.eq_inv_of_mul_eq_one_left
  rw [expandedMaskSeriesUnit_val,
    integerPolynomialSeriesHom_expand (ZMod (p^r)) p hp.ne_zero]
  have hu : (maskSeriesUnit p r B hp hr hB : PowerSeries (ZMod (p^r))) *
      ↑((maskSeriesUnit p r B hp hr hB)⁻¹) = 1 :=
    (maskSeriesUnit p r B hp hr hB).mul_inv
  simpa only [map_mul, map_one, maskSeriesUnit_val] using
    congrArg (PowerSeries.expand p hp.ne_zero) hu

/-- Uniqueness of a reciprocal of a unit power, without a field structure. -/
theorem unit_power_reciprocal_unique {R : Type*} [CommRing R]
    (u : Rˣ) (n : ℕ) (x : R) (hx : (u : R)^n * x = 1) :
    x = (↑u⁻¹ : R)^n := by
  have h : (↑(u^n) : R) * x = 1 := by simpa using hx
  simpa using (Units.eq_inv_of_mul_eq_one_left h)

/-- The inherited padded sum is the actual inverse power of the unexpanded mask. -/
theorem paddedMaskReciprocalSum_eq_inverse (p ell r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    (integerPolynomialSeriesHom (ZMod (p^r)) B)^maskPadding p ell *
      maskReciprocalSum p (quotientOfLayer p ell) r B hp hr hB =
    (↑((maskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p^r)))^(ell+1) := by
  apply unit_power_reciprocal_unique
  simpa using paddedMaskReciprocalSum_spec p ell r B hp hr hB

/-- Unit cancellation in the Mahler equation increases the denominator layer by one. -/
theorem mahler_unit_layer_step {R : Type*} [CommRing R] (u : Rˣ)
    (P A F G : R) (ell : ℕ) (hM : (u : R)*F = A*G) :
    P*F*(↑u⁻¹ : R)^ell = P*A*G*(↑u⁻¹ : R)^(ell+1) := by
  have hF : F = A*G*(↑u⁻¹ : R) := by
    calc
      F = (↑u⁻¹ : R) * ((u : R)*F) := by simp
      _ = A*G*(↑u⁻¹ : R) := by rw [hM]; ring
  conv_lhs => rw [hF]
  rw [pow_succ]
  ring

/-- The actual denominator-layer series F/B^ell. -/
noncomputable def maskLayerSeries (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (ell : ℕ) : PowerSeries (ZMod (p^r)) :=
  F * (↑((maskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p^r)))^ell

/-- Exact pre-section expansion using the actual Mahler equation and actual branch weights. -/
theorem maskLayerSeries_preCartier_transition (p r ell : ℕ) (P A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r)))
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    integerPolynomialSeriesHom (ZMod (p^r)) P * maskLayerSeries p r B hp hr hB F ell =
      ∑ k ∈ Finset.range r,
        integerPolynomialSeriesHom (ZMod (p^r))
          (P*A*B^maskPadding p ell *
            cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B)) *
        PowerSeries.expand p hp.ne_zero
          (maskLayerSeries p r B hp hr hB F (quotientOfLayer p ell+k)) := by
  unfold maskLayerSeries
  rw [← mul_assoc]
  have hM' : (maskSeriesUnit p r B hp hr hB : PowerSeries (ZMod (p^r))) * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F := by
    simpa using hM
  rw [mahler_unit_layer_step _ _ _ _ _ ell hM',
    ← paddedMaskReciprocalSum_eq_inverse p ell r B hp hr hB]
  unfold maskReciprocalSum
  simp only [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro k _
  simp only [map_mul, map_pow, expand_maskSeriesUnit_inv]
  ring

/-- Original finite prime-power Cartier transition on complete formal series.
A(0)=B(0) and F(0)=1 are not required for this conditional identity: the actual
Mahler equation and the denominator unit are sufficient. -/
theorem maskLayerSeries_cartier_transition (p r ell d : ℕ) (P A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hd : d < p) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r)))
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    cartierSection p d
      (integerPolynomialSeriesHom (ZMod (p^r)) P * maskLayerSeries p r B hp hr hB F ell) =
      ∑ k ∈ Finset.range r,
        cartierSection p d (integerPolynomialSeriesHom (ZMod (p^r))
          (P*A*B^maskPadding p ell *
            cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B))) *
        maskLayerSeries p r B hp hr hB F (quotientOfLayer p ell+k) := by
  rw [maskLayerSeries_preCartier_transition p r ell P A B hp hr hB F hM, map_sum]
  apply Finset.sum_congr rfl
  intro k _
  exact cartierSection_mul_expand hp.ne_zero hd _ _

/-- The polynomial-to-series inclusion detects zero after coefficient reduction. -/
theorem integerPolynomialSeriesHom_eq_zero_iff (R : Type*) [CommRing R] (P : ℤ[X]) :
    integerPolynomialSeriesHom R P = 0 ↔ P.map (Int.castRingHom R) = 0 := by
  change ((P.map (Int.castRingHom R) : R[X]) : PowerSeries R) = 0 ↔ _
  exact Polynomial.coe_eq_zero_iff

/-- One summand in the exact Cartier transition, with the polynomial weight retained. -/
noncomputable def maskCartierBranch (p r ell d : ℕ) (P A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (k : ℕ) : PowerSeries (ZMod (p^r)) :=
  cartierSection p d (integerPolynomialSeriesHom (ZMod (p^r))
    (P*A*B^maskPadding p ell *
      cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B))) *
    maskLayerSeries p r B hp hr hB F (quotientOfLayer p ell+k)

/-- Inactive graph branches vanish in the actual sectioned transition, for every state numerator. -/
theorem maskCartierBranch_eq_zero_of_inactive (p r ell d : ℕ) (P A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (k : ℕ) (hE : frobeniusDefect p B ≠ 0)
    (hk : ¬ ActiveAt r (polynomialPadicOrder p (frobeniusDefect p B)) k
      (padicValNat p ((quotientOfLayer p ell+k-1).choose k))) :
    maskCartierBranch p r ell d P A B hp hr hB F k = 0 := by
  have hq : 0 < quotientOfLayer p ell := by exact Nat.succ_pos (ell / p)
  have hw : (cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B)).map
      (Int.castRingHom (ZMod (p^r))) = 0 := by
    by_contra hn
    exact hk ((cartierBranchWeight_survives_iff_activeAt hp hq r k _ hE).mp hn)
  have hz := (integerPolynomialSeriesHom_eq_zero_iff (ZMod (p^r)) _).mpr hw
  simp only [maskCartierBranch, map_mul, hz, mul_zero, map_zero, zero_mul]

/-- The inherited edge-pruning rule preserves the exact complete-series transition.
The converse, survival of every sectioned summand, is deliberately not asserted. -/
theorem maskLayerSeries_cartier_transition_pruned (p r ell d : ℕ) (P A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hd : d < p) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hE : frobeniusDefect p B ≠ 0)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    cartierSection p d
      (integerPolynomialSeriesHom (ZMod (p^r)) P * maskLayerSeries p r B hp hr hB F ell) =
      ∑ k ∈ (Finset.range r).filter (fun k =>
        branchCost (polynomialPadicOrder p (frobeniusDefect p B)) k
          (padicValNat p ((quotientOfLayer p ell+k-1).choose k)) < r),
        maskCartierBranch p r ell d P A B hp hr hB F k := by
  rw [maskLayerSeries_cartier_transition p r ell d P A B hp hr hd hB F hM]
  change (∑ k ∈ Finset.range r, maskCartierBranch p r ell d P A B hp hr hB F k) = _
  symm
  apply Finset.sum_subset (Finset.filter_subset _ _)
  intro k hk hnot
  have hi : ¬ ActiveAt r (polynomialPadicOrder p (frobeniusDefect p B)) k
      (padicValNat p ((quotientOfLayer p ell+k-1).choose k)) := by
    intro ha
    exact hnot (Finset.mem_filter.mpr ⟨hk,ha⟩)
  exact maskCartierBranch_eq_zero_of_inactive p r ell d P A B hp hr hB F k hE hi

/-- Zero defect eliminates every positive-order summand without a finite-order fiction. -/
theorem maskCartierBranch_eq_zero_of_zero_defect (p r ell d : ℕ) (P A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (k : ℕ) (hk : 0 < k)
    (hE : frobeniusDefect p B = 0) :
    maskCartierBranch p r ell d P A B hp hr hB F k = 0 := by
  simp [maskCartierBranch, hE, cartierBranchWeight_zero_defect p _ k hk]

/-- In the zero-defect case the transition reduces exactly to order zero. -/
theorem maskLayerSeries_cartier_transition_zero_defect (p r ell d : ℕ) (P A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hd : d < p) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hE : frobeniusDefect p B = 0)
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F) :
    cartierSection p d
      (integerPolynomialSeriesHom (ZMod (p^r)) P * maskLayerSeries p r B hp hr hB F ell) =
      maskCartierBranch p r ell d P A B hp hr hB F 0 := by
  rw [maskLayerSeries_cartier_transition p r ell d P A B hp hr hd hB F hM]
  change (∑ k ∈ Finset.range r, maskCartierBranch p r ell d P A B hp hr hB F k) = _
  apply Finset.sum_eq_single 0
  · intro k _ hk
    exact maskCartierBranch_eq_zero_of_zero_defect p r ell d P A B hp hr hB F k
      (Nat.pos_of_ne_zero hk) hE
  · simp [hr]

/-- The original initial layer with numerator B represents F exactly. -/
theorem maskLayerSeries_initial (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) :
    integerPolynomialSeriesHom (ZMod (p^r)) B * maskLayerSeries p r B hp hr hB F 1 = F := by
  rw [maskLayerSeries, pow_one, ← maskSeriesUnit_val p r B hp hr hB]
  rw [mul_comm F _]
  exact (maskSeriesUnit p r B hp hr hB).mul_inv_cancel_left F

end KomorebiPadic
