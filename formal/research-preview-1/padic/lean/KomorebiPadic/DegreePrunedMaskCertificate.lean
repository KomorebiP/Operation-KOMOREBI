import KomorebiPadic.DegreePrunedMaskAutomaton

/-! # Certificates and size comparisons for numerator-degree pruning
The canonical solution, targets and branch weights remain unchanged. This is a
sufficient global degree envelope, not a least layer-specific degree profile.
-/
namespace KomorebiPadic
open Polynomial

noncomputable def degreePrunedMaskOutputLinear (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (degreePrunedNumeratorBound p r A B) →ₗ[ZMod (p^r)] ZMod (p^r) where
  toFun := degreePrunedMaskOutput p r A B hp hr hB
  map_add' s t := by
    simp [degreePrunedMaskOutput, Pi.add_apply, add_mul, Finset.sum_add_distrib]
  map_smul' a s := by
    simp [degreePrunedMaskOutput, Pi.smul_apply, smul_eq_mul, Finset.mul_sum, mul_assoc]

/-- Arbitrary states retain the exact full-series Cartier semantics. -/
theorem degreePrunedMask_transition_canonical_series (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (d : ℕ) (hd : d < p)
    (s : CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (degreePrunedNumeratorBound p r A B)) :
    machineSeries (prunedMaskLayers p r B hp hr hB (canonicalMaskSeries p r A B hp hr hB))
      (machineTransition (degreePrunedMaskMachine p r A B hp) d s) =
    cartierSection p d
      (machineSeries (prunedMaskLayers p r B hp hr hB (canonicalMaskSeries p r A B hp hr hB)) s) :=
  machineTransition_series _ _ d (degreePrunedMaskMachine_branch_law p r A B hp hr hB _
    (canonicalMaskSeries_equation p r A B hp hr hB hAB) d hd) s

/-- Both numerator capacities recover the identical output at every in-range word. -/
theorem degreePrunedMask_output_eq_pruned_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    degreePrunedMaskOutput p r A B hp hr hB
      (iterateMachine (degreePrunedMaskMachine p r A B hp) ds (degreePrunedMaskInitial p r A B)) =
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) ds (prunedMaskInitial p r A B)) := by
  rw [degreePrunedMask_output_canonical_word p r A B hp hr hB hAB ds hd,
      prunedMask_output_canonical_word p r A B hp hr hB hAB ds hd]

theorem degreePrunedMask_output_eq_pruned_coefficient (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    degreePrunedMaskOutput p r A B hp hr hB
      (iterateMachine (degreePrunedMaskMachine p r A B hp) (Nat.digits p n) (degreePrunedMaskInitial p r A B)) =
    prunedMaskOutput p r A B hp hr hB
      (iterateMachine (prunedMaskMachine p r A B hp) (Nat.digits p n) (prunedMaskInitial p r A B)) := by
  rw [degreePrunedMask_output_canonical_coefficient p r A B hp hr hB hAB,
      prunedMask_output_canonical_coefficient p r A B hp hr hB hAB]

/-- Exact outputs remain natural under positive precision reduction. -/
theorem degreePrunedMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (degreePrunedMaskOutput p r A B hp hr hB
        (iterateMachine (degreePrunedMaskMachine p r A B hp) (Nat.digits p n) (degreePrunedMaskInitial p r A B))) =
      degreePrunedMaskOutput p s A B hp hs hB
        (iterateMachine (degreePrunedMaskMachine p s A B hp) (Nat.digits p n) (degreePrunedMaskInitial p s A B)) := by
  rw [degreePrunedMask_output_canonical_coefficient p r A B hp hr hB hAB,
    degreePrunedMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

/-- At the same pruned layer count, the smaller degree cap cannot enlarge the state space. -/
theorem degreePrunedMask_state_card_le_pruned (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (degreePrunedNumeratorBound p r A B)) ≤
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (cartierNumeratorBound p r A B)) := by
  rw [degreePrunedMask_state_card p r A B hp, prunedMask_state_card p r A B hp]
  apply Nat.pow_le_pow_right hp.pos
  exact Nat.mul_le_mul_left _ (Nat.add_le_add_right (degreePrunedNumeratorBound_le_original p r A B) 1)

theorem degreePrunedMask_state_card_le_unpruned (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) :
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (degreePrunedNumeratorBound p r A B)) ≤
    Nat.card (CartierCoefficientState (ZMod (p^r)) (cartierLayerBound p r)
      (cartierNumeratorBound p r A B)) :=
  (degreePrunedMask_state_card_le_pruned p r A B hp).trans
    (prunedMask_state_card_le_unpruned p r A B hp hr)

/-- Strict degree improvement removes scalar slots even with the denominator count fixed. -/
theorem degreePrunedMask_coordinate_count_lt {p r : ℕ} (A B : ℤ[X])
    (hlt : degreePrunedNumeratorBound p r A B < cartierNumeratorBound p r A B) :
    prunedMaskLayerBound p r B * (degreePrunedNumeratorBound p r A B+1) <
      prunedMaskLayerBound p r B * (cartierNumeratorBound p r A B+1) := by
  exact Nat.mul_lt_mul_of_pos_left (Nat.add_lt_add_right hlt 1) (prunedMaskLayerBound_pos p r B)

structure DegreePrunedCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  predecessor : PrunedCanonicalMaskCertificate p r A B hp hr hB
  cap_le_precision : prunedMaskOrderCap p r B ≤ r-1
  active_order_bound : ∀ ell k, prunedCorrectionActive p r ell k B → k ≤ prunedMaskOrderCap p r B
  initial_degree : B.natDegree ≤ degreePrunedNumeratorBound p r A B
  degree_le_original : degreePrunedNumeratorBound p r A B ≤ cartierNumeratorBound p r A B
  kernel_degree : ∀ ell k, (finiteMaskKernel p r ell k A B).natDegree ≤
    (p-1)*degreePrunedNumeratorBound p r A B
  output : ∀ n, degreePrunedMaskOutput p r A B hp hr hB
    (iterateMachine (degreePrunedMaskMachine p r A B hp) (Nat.digits p n) (degreePrunedMaskInitial p r A B)) =
    PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)
  state_card : Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
    (degreePrunedNumeratorBound p r A B)) =
    p^(r*(prunedMaskLayerBound p r B)*(degreePrunedNumeratorBound p r A B+1))
  cardinality_le_previous : Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (degreePrunedNumeratorBound p r A B)) ≤
    Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
      (cartierNumeratorBound p r A B))

noncomputable def degreePrunedCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) : DegreePrunedCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := prunedCanonicalMaskCertificate p r A B hp hr hB hAB
  cap_le_precision := prunedMaskOrderCap_le_precision p r B
  active_order_bound := fun _ _ ha => prunedCorrectionActive_le_orderCap B ha
  initial_degree := degreePrunedNumeratorBound_initial p r A B
  degree_le_original := degreePrunedNumeratorBound_le_original p r A B
  kernel_degree := fun _ _ => finiteMaskKernel_degree_pruned hp A B
  output := degreePrunedMask_output_canonical_coefficient p r A B hp hr hB hAB
  state_card := degreePrunedMask_state_card p r A B hp
  cardinality_le_previous := degreePrunedMask_state_card_le_pruned p r A B hp

end KomorebiPadic
