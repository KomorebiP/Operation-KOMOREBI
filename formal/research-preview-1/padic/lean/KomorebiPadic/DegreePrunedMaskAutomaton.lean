import KomorebiPadic.DegreePrunedClosure

/-! # Canonical finite mask machine with both layer and numerator pruning
The targets and residue kernels are unchanged from Block25. Only the coefficient
capacity is smaller; the reduced kernel-degree theorem certifies lossless closure.
-/
namespace KomorebiPadic
open Polynomial

noncomputable def degreePrunedMaskMachine (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    PolynomialCartierMachine (ZMod (p^r)) p (prunedMaskLayerBound p r B) r
      (degreePrunedNumeratorBound p r A B) where
  radix_pos := hp.pos
  target := prunedMaskTarget p r B hp
  kernel i k := prunedMaskKernel p r (i.val+1) k.val A B
  kernel_degree i k := by
    rw [prunedMaskKernel_eq_original hp]
    exact finiteMaskKernel_degree_pruned hp A B

/-- The pruned branch law uses the old full transition and discards only zero terms. -/
theorem degreePrunedMaskMachine_branch_law (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r)))
    (hM : integerPolynomialSeriesHom (ZMod (p^r)) B * F =
      integerPolynomialSeriesHom (ZMod (p^r)) A * PowerSeries.expand p hp.ne_zero F)
    (d : ℕ) (hd : d < p) (i : Fin (prunedMaskLayerBound p r B)) (P : (ZMod (p^r))[X]) :
    cartierSection p d ((P : PowerSeries (ZMod (p^r))) * prunedMaskLayers p r B hp hr hB F i) =
      ∑ k : Fin r,
        (polynomialCartier p d (P*(degreePrunedMaskMachine p r A B hp).kernel i k) : PowerSeries (ZMod (p^r))) *
          prunedMaskLayers p r B hp hr hB F ((degreePrunedMaskMachine p r A B hp).target i k) := by
  exact prunedMaskMachine_branch_law p r A B hp hr hB F hM d hd i P

noncomputable def degreePrunedMaskInitial (p r : ℕ) (A B : ℤ[X]) :
    CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (degreePrunedNumeratorBound p r A B) :=
  fun i => if i.val = 0 then
    numeratorCoordinates (degreePrunedNumeratorBound p r A B) (B.map (Int.castRingHom (ZMod (p^r)))) else 0

theorem degreePrunedMaskInitial_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) :
    machineSeries (prunedMaskLayers p r B hp hr hB F) (degreePrunedMaskInitial p r A B) = F := by
  classical
  let i0 : Fin (prunedMaskLayerBound p r B) := ⟨0, prunedMaskLayerBound_pos p r B⟩
  unfold machineSeries
  rw [Finset.sum_eq_single i0]
  · simp only [degreePrunedMaskInitial, i0, ↓reduceIte]
    rw [numeratorPolynomial_coordinates _ (Polynomial.natDegree_map_le.trans (degreePrunedNumeratorBound_initial p r A B))]
    exact maskLayerSeries_initial p r B hp hr hB F
  · intro i _ hi
    have hi0 : i.val ≠ 0 := by intro hv; apply hi; exact Fin.ext hv
    simp [degreePrunedMaskInitial, hi0, numeratorPolynomial]
  · simp

/-- Finite output uses the denominator constant and state coefficients, not F. -/
noncomputable def degreePrunedMaskOutput (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (degreePrunedNumeratorBound p r A B)) :
    ZMod (p^r) :=
  ∑ i : Fin (prunedMaskLayerBound p r B),
    s i ⟨0, Nat.succ_pos _⟩ *
      (PowerSeries.constantCoeff (↑((maskSeriesUnit p r B hp hr hB)⁻¹) : PowerSeries (ZMod (p^r))))^(i.val+1)

theorem degreePrunedMaskOutput_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (F : PowerSeries (ZMod (p^r))) (hF : PowerSeries.constantCoeff F = 1)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (degreePrunedNumeratorBound p r A B)) :
    degreePrunedMaskOutput p r A B hp hr hB s =
      PowerSeries.constantCoeff (machineSeries (prunedMaskLayers p r B hp hr hB F) s) := by
  classical
  unfold degreePrunedMaskOutput machineSeries
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro i _
  simp [prunedMaskLayers, maskLayerSeries, hF, numeratorPolynomial]

/-- Every coefficient of the constructed canonical solution is computed in the pruned space. -/
theorem degreePrunedMask_output_canonical_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    degreePrunedMaskOutput p r A B hp hr hB
      (iterateMachine (degreePrunedMaskMachine p r A B hp) ds (degreePrunedMaskInitial p r A B)) =
        PowerSeries.coeff (cartierWordValue p ds) (canonicalMaskSeries p r A B hp hr hB) := by
  rw [degreePrunedMaskOutput_series p r A B hp hr hB _ (canonicalMaskSeries_constant p r A B hp hr hB)]
  rw [iterateMachine_output _ _ (degreePrunedMaskMachine_branch_law p r A B hp hr hB _
    (canonicalMaskSeries_equation p r A B hp hr hB hAB)) ds hd,
    degreePrunedMaskInitial_series p r A B hp hr hB]

theorem degreePrunedMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    degreePrunedMaskOutput p r A B hp hr hB
      (iterateMachine (degreePrunedMaskMachine p r A B hp) (Nat.digits p n) (degreePrunedMaskInitial p r A B)) =
        PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [degreePrunedMask_output_canonical_word p r A B hp hr hB hAB _
    (fun d hd => Nat.digits_lt_base hp.one_lt hd), cartierWordValue_eq_ofDigits, Nat.ofDigits_digits]

/-- The new and old machines have exactly the same output at every word. -/
theorem degreePrunedMask_output_eq_unpruned_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    degreePrunedMaskOutput p r A B hp hr hB
      (iterateMachine (degreePrunedMaskMachine p r A B hp) ds (degreePrunedMaskInitial p r A B)) =
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) ds (finiteMaskInitial p r A B)) := by
  rw [degreePrunedMask_output_canonical_word p r A B hp hr hB hAB ds hd,
      finiteMask_output_canonical_word p r A B hp hr hB hAB ds hd]

/-- Exact ambient count; reachable states and minimal automata are separate questions. -/
theorem degreePrunedMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (degreePrunedNumeratorBound p r A B)) =
      p^(r*(prunedMaskLayerBound p r B)*(degreePrunedNumeratorBound p r A B+1)) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  rw [Nat.card_eq_fintype_card, cartierCoefficientState_card, ZMod.card]
  simp only [← pow_mul, Nat.mul_assoc]

/-- The finite output formula has no series coefficients as inputs. -/
theorem degreePrunedMaskOutput_eq_coefficients (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B) (degreePrunedNumeratorBound p r A B)) :
    degreePrunedMaskOutput p r A B hp hr hB s =
      ∑ i : Fin (prunedMaskLayerBound p r B),
        s i ⟨0, Nat.succ_pos _⟩ * ((B.coeff 0 : ZMod (p^r))⁻¹)^(i.val+1) := by
  unfold degreePrunedMaskOutput
  rw [maskSeriesUnit_inverse_constant]

end KomorebiPadic
