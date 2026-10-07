import KomorebiPadic.PrunedMaskAutomaton

/-! # End-to-end certificates for the valuation-pruned canonical mask machine
The old degree cap is retained; this is not a minimal reachable-automaton claim.
-/
namespace KomorebiPadic
open Polynomial

noncomputable def prunedMaskOutputLinear (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (cartierNumeratorBound p r A B) →ₗ[ZMod (p^r)] ZMod (p^r) where
  toFun := prunedMaskOutput p r A B hp hr hB
  map_add' s t := by
    simp [prunedMaskOutput, Pi.add_apply, add_mul, Finset.sum_add_distrib]
  map_smul' a s := by
    simp [prunedMaskOutput, Pi.smul_apply, smul_eq_mul, Finset.mul_sum, mul_assoc]

/-- Arbitrary pruned states, not just the initial orbit, retain exact series semantics. -/
theorem prunedMask_transition_canonical_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (d : ℕ) (hd : d < p)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (cartierNumeratorBound p r A B)) :
    machineSeries (prunedMaskLayers p r B hp hr hB (canonicalMaskSeries p r A B hp hr hB))
      (machineTransition (prunedMaskMachine p r A B hp) d s) =
    cartierSection p d
      (machineSeries (prunedMaskLayers p r B hp hr hB (canonicalMaskSeries p r A B hp hr hB)) s) :=
  machineTransition_series _ _ d (prunedMaskMachine_branch_law p r A B hp hr hB _
    (canonicalMaskSeries_equation p r A B hp hr hB hAB) d hd) s

/-- Output equivalence includes the canonical digit expansion of every natural number. -/
theorem prunedMask_output_eq_unpruned_coefficient (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) (Nat.digits p n) (prunedMaskInitial p r A B)) =
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) (Nat.digits p n) (finiteMaskInitial p r A B)) := by
  rw [prunedMask_output_canonical_coefficient p r A B hp hr hB hAB,
      finiteMask_output_canonical_coefficient p r A B hp hr hB hAB]

/-- Different-dimensional pruned machines agree after precision reduction at the output. -/
theorem prunedMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (prunedMaskOutput p r A B hp hr hB
        (iterateMachine (prunedMaskMachine p r A B hp) (Nat.digits p n) (prunedMaskInitial p r A B))) =
      prunedMaskOutput p s A B hp hs hB
        (iterateMachine (prunedMaskMachine p s A B hp) (Nat.digits p n) (prunedMaskInitial p s A B)) := by
  rw [prunedMask_output_canonical_coefficient p r A B hp hr hB hAB,
    prunedMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

/-- A strict layer reduction gives a strict reduction in scalar coordinate slots. -/
theorem prunedMask_coordinate_count_lt {p r : ℕ} (A B : ℤ[X])
    (hlt : prunedMaskLayerBound p r B < cartierLayerBound p r) :
    prunedMaskLayerBound p r B * (cartierNumeratorBound p r A B+1) <
      cartierLayerBound p r * (cartierNumeratorBound p r A B+1) := by
  exact Nat.mul_lt_mul_of_pos_right hlt (Nat.succ_pos _)

/-- Zero defect gives a genuine single-denominator-layer coordinate space. -/
theorem prunedMask_zero_defect_state_card (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hE : frobeniusDefect p B = 0) :
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (cartierNumeratorBound p r A B)) = p^(r*(cartierNumeratorBound p r A B+1)) := by
  rw [prunedMask_state_card p r A B hp, prunedMaskLayerBound_zero_defect p r B hE]
  simp

/-- Complete mask-to-pruned-output evidence, retaining the prior canonical certificate. -/
structure PrunedCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  canonical : CanonicalFiniteMaskCertificate p r A B hp hr hB
  layer_positive : 0 < prunedMaskLayerBound p r B
  layer_le_unpruned : prunedMaskLayerBound p r B ≤ cartierLayerBound p r
  active_closed : ∀ ell k, ell ≤ prunedMaskLayerBound p r B →
    prunedCorrectionActive p r ell k B → quotientOfLayer p ell+k ≤ prunedMaskLayerBound p r B
  discarded_zero : ∀ ell k, ¬ prunedCorrectionActive p r ell k B → finiteMaskKernel p r ell k A B = 0
  coefficient_output : ∀ n,
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) (Nat.digits p n) (prunedMaskInitial p r A B)) =
        PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)
  old_output_eq : ∀ ds, (∀ d ∈ ds, d < p) →
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) ds (prunedMaskInitial p r A B)) =
    finiteMaskOutput p r A B hp hr hB
      (iterateMachine (finiteMaskMachine p r A B hp.one_lt) ds (finiteMaskInitial p r A B))
  state_card : Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (cartierNumeratorBound p r A B)) = p^(r*(prunedMaskLayerBound p r B)*(cartierNumeratorBound p r A B+1))

noncomputable def prunedCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) : PrunedCanonicalMaskCertificate p r A B hp hr hB where
  canonical := canonicalFiniteMaskCertificate p r A B hp hr hB hAB
  layer_positive := prunedMaskLayerBound_pos p r B
  layer_le_unpruned := prunedMaskLayerBound_le_unpruned hp hr B
  active_closed := fun _ _ hell ha => prunedMaskLayerBound_closed hp B hell ha
  discarded_zero := fun _ _ ha => finiteMaskKernel_zero_of_pruned_inactive hp A B ha
  coefficient_output := prunedMask_output_canonical_coefficient p r A B hp hr hB hAB
  old_output_eq := prunedMask_output_eq_unpruned_word p r A B hp hr hB hAB
  state_card := prunedMask_state_card p r A B hp

end KomorebiPadic
