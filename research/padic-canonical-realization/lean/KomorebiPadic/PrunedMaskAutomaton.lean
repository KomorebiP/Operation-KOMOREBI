import KomorebiPadic.PrunedLayerClosure

/-! # Exact finite mask machine on valuation-pruned denominator coordinates
The old numerator bound is retained. Every discarded branch is zero as a
polynomial over ZMod(p^r); only such zero branches use a dummy target.
-/
namespace KomorebiPadic
open Polynomial
attribute [local instance] Classical.propDecidable

/-- Explicit branch pruning; the value is equal to the old residue kernel. -/
noncomputable def prunedMaskKernel (p r ell k : ℕ) (A B : ℤ[X]) : (ZMod (p^r))[X] :=
  if prunedCorrectionActive p r ell k B then finiteMaskKernel p r ell k A B else 0

theorem prunedMaskKernel_eq_original {p r ell k : ℕ} (hp : p.Prime) (A B : ℤ[X]) :
    prunedMaskKernel p r ell k A B = finiteMaskKernel p r ell k A B := by
  classical
  unfold prunedMaskKernel
  split
  · rfl
  · rename_i ha
    exact (finiteMaskKernel_zero_of_pruned_inactive hp A B ha).symm

/-- Active branches retain their exact target; zero branches have the harmless target 1. -/
noncomputable def prunedMaskTarget (p r : ℕ) (B : ℤ[X]) (hp : p.Prime)
    (i : Fin (prunedMaskLayerBound p r B)) (k : Fin r) : Fin (prunedMaskLayerBound p r B) :=
  if ha : prunedCorrectionActive p r (i.val+1) k.val B then
    ⟨quotientOfLayer p (i.val+1)+k.val-1, by
      have hb := prunedMaskLayerBound_closed hp B
        (show i.val+1 ≤ prunedMaskLayerBound p r B by omega) ha
      have hq : 0 < quotientOfLayer p (i.val+1) := Nat.succ_pos _
      omega⟩
  else ⟨0, prunedMaskLayerBound_pos p r B⟩

theorem prunedMaskTarget_layer {p r : ℕ} (B : ℤ[X]) (hp : p.Prime)
    (i : Fin (prunedMaskLayerBound p r B)) (k : Fin r)
    (ha : prunedCorrectionActive p r (i.val+1) k.val B) :
    (prunedMaskTarget p r B hp i k).val+1 = quotientOfLayer p (i.val+1)+k.val := by
  simp only [prunedMaskTarget, ha, ↓reduceDIte]
  have hq : 0 < quotientOfLayer p (i.val+1) := Nat.succ_pos _
  omega

noncomputable def prunedMaskMachine (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    PolynomialCartierMachine (ZMod (p^r)) p (prunedMaskLayerBound p r B) r
      (cartierNumeratorBound p r A B) where
  radix_pos := hp.pos
  target := prunedMaskTarget p r B hp
  kernel i k := prunedMaskKernel p r (i.val+1) k.val A B
  kernel_degree i k := by
    rw [prunedMaskKernel_eq_original hp]
    exact finiteMaskKernel_degree hp.one_lt k.isLt A B

noncomputable def prunedMaskLayers (p r : ℕ) (B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) : Fin (prunedMaskLayerBound p r B) → PowerSeries (ZMod (p^r)) :=
  fun i => maskLayerSeries p r B hp hr hB F (i.val+1)

/-- The pruned branch law uses the old full transition and discards only zero terms. -/
theorem prunedMaskMachine_branch_law (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r)))
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F)
    (d : ℕ) (hd : d < p) (i : Fin (prunedMaskLayerBound p r B)) (P : (ZMod (p^r))[X]) :
    cartierSection p d ((P : PowerSeries (ZMod (p^r))) * prunedMaskLayers p r B hp hr hB F i) =
      ∑ k : Fin r,
        (polynomialCartier p d (P*(prunedMaskMachine p r A B hp).kernel i k) : PowerSeries (ZMod (p^r))) *
          prunedMaskLayers p r B hp hr hB F ((prunedMaskMachine p r A B hp).target i k) := by
  classical
  have ht := residuePolynomial_cartier_transition p r (i.val+1) d A B hp hr hd hB F hM P
  rw [Finset.sum_range] at ht
  change cartierSection p d ((P : PowerSeries (ZMod (p^r))) * maskLayerSeries p r B hp hr hB F (i.val+1)) = _
  rw [ht]
  apply Finset.sum_congr rfl
  intro k _
  change (polynomialCartier p d (P*finiteMaskKernel p r (i.val+1) k.val A B) : PowerSeries (ZMod (p^r))) *
      maskLayerSeries p r B hp hr hB F (quotientOfLayer p (i.val+1)+k.val) =
    (polynomialCartier p d (P*prunedMaskKernel p r (i.val+1) k.val A B) : PowerSeries (ZMod (p^r))) *
      maskLayerSeries p r B hp hr hB F ((prunedMaskTarget p r B hp i k).val+1)
  rw [prunedMaskKernel_eq_original hp]
  by_cases ha : prunedCorrectionActive p r (i.val+1) k.val B
  · rw [prunedMaskTarget_layer B hp i k ha]
  · rw [finiteMaskKernel_zero_of_pruned_inactive hp A B ha, mul_zero]
    have hz : polynomialCartier p d (0 : (ZMod (p^r))[X]) = 0 :=
      (polynomialCartierLinear p d hp.pos).map_zero
    rw [hz]
    simp

noncomputable def prunedMaskInitial (p r : ℕ) (A B : ℤ[X]) :
    CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (cartierNumeratorBound p r A B) :=
  fun i => if i.val = 0 then
    numeratorCoordinates (cartierNumeratorBound p r A B) (B.map (Int.castRingHom (ZMod (p^r)))) else 0

theorem prunedMaskInitial_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) :
    machineSeries (prunedMaskLayers p r B hp hr hB F) (prunedMaskInitial p r A B) = F := by
  classical
  let i0 : Fin (prunedMaskLayerBound p r B) := ⟨0, prunedMaskLayerBound_pos p r B⟩
  unfold machineSeries
  rw [Finset.sum_eq_single i0]
  · simp only [prunedMaskInitial, i0, ↓reduceIte]
    rw [numeratorPolynomial_coordinates _ (Polynomial.natDegree_map_le.trans (cartierNumeratorBound_initial p r A B))]
    exact maskLayerSeries_initial p r B hp hr hB F
  · intro i _ hi
    have hi0 : i.val ≠ 0 := by intro hv; apply hi; exact Fin.ext hv
    simp [prunedMaskInitial, hi0, numeratorPolynomial]
  · simp

/-- Finite output uses the denominator constant and state coefficients, not F. -/
noncomputable def prunedMaskOutput (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (cartierNumeratorBound p r A B)) :
    ZMod (p^r) :=
  ∑ i : Fin (prunedMaskLayerBound p r B),
    s i ⟨0, Nat.succ_pos _⟩ *
      (PowerSeries.constantCoeff (↑((maskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p^r))))^(i.val+1)

theorem prunedMaskOutput_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : PowerSeries.constantCoeff F = 1)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (cartierNumeratorBound p r A B)) :
    prunedMaskOutput p r A B hp hr hB s =
      PowerSeries.constantCoeff (machineSeries (prunedMaskLayers p r B hp hr hB F) s) := by
  classical
  unfold prunedMaskOutput machineSeries
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro i _
  simp [prunedMaskLayers, maskLayerSeries, hF, numeratorPolynomial]

/-- Every coefficient of the constructed canonical solution is computed in the pruned space. -/
theorem prunedMask_output_canonical_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) ds (prunedMaskInitial p r A B)) =
        PowerSeries.coeff (cartierWordValue p ds) (canonicalMaskSeries p r A B hp hr hB) := by
  rw [prunedMaskOutput_series p r A B hp hr hB _ (canonicalMaskSeries_constant p r A B hp hr hB)]
  rw [iterateMachine_output _ _ (prunedMaskMachine_branch_law p r A B hp hr hB _
    (canonicalMaskSeries_equation p r A B hp hr hB hAB)) ds hd,
    prunedMaskInitial_series p r A B hp hr hB]

theorem prunedMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) (Nat.digits p n) (prunedMaskInitial p r A B)) =
        PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [prunedMask_output_canonical_word p r A B hp hr hB hAB _
    (fun d hd => Nat.digits_lt_base hp.one_lt hd), cartierWordValue_eq_ofDigits, Nat.ofDigits_digits]

/-- The new and old machines have exactly the same output at every word. -/
theorem prunedMask_output_eq_unpruned_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) ds (prunedMaskInitial p r A B)) =
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) ds (finiteMaskInitial p r A B)) := by
  rw [prunedMask_output_canonical_word p r A B hp hr hB hAB ds hd,
      finiteMask_output_canonical_word p r A B hp hr hB hAB ds hd]

/-- Exact ambient count; reachable states and minimal automata are separate questions. -/
theorem prunedMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (cartierNumeratorBound p r A B)) =
      p^(r*(prunedMaskLayerBound p r B)*(cartierNumeratorBound p r A B+1)) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  rw [Nat.card_eq_fintype_card, cartierCoefficientState_card, ZMod.card]
  simp only [← pow_mul, Nat.mul_assoc]

/-- Keeping the degree cap fixed, pruning cannot enlarge the ambient state count. -/
theorem prunedMask_state_card_le_unpruned (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) :
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (cartierNumeratorBound p r A B)) ≤
    Nat.card (CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r) (cartierNumeratorBound p r A B)) := by
  rw [prunedMask_state_card p r A B hp, finiteMask_state_card p r A B hp]
  apply Nat.pow_le_pow_right hp.pos
  exact Nat.mul_le_mul_right _ (Nat.mul_le_mul_left r (prunedMaskLayerBound_le_unpruned hp hr B))

/-- The finite output formula has no series coefficients as inputs. -/
theorem prunedMaskOutput_eq_coefficients (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (cartierNumeratorBound p r A B)) :
    prunedMaskOutput p r A B hp hr hB s =
      ∑ i : Fin (prunedMaskLayerBound p r B),
        s i ⟨0, Nat.succ_pos _⟩ * ((B.coeff 0 : ZMod (p^r))⁻¹)^(i.val+1) := by
  unfold prunedMaskOutput
  rw [maskSeriesUnit_inverse_constant]

end KomorebiPadic
