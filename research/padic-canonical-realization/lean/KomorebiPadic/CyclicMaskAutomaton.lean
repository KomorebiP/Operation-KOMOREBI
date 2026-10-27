import KomorebiPadic.IdealMaskAutomaton
import KomorebiPadic.CyclicIdealCoordinates

namespace KomorebiPadic
open Polynomial

abbrev CyclicMaskState (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :=
  CoordinateIdeal.CyclicState p (leastMaskIdealCapacity p r A B hp)

noncomputable def cyclicMaskToIdeal (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    CyclicMaskState p r A B hp ≃+ IdealMaskState p r A B hp :=
  CoordinateIdeal.cyclicBoxEquiv hp.pos _ (leastMaskIdealCapacity_bound p r A B hp)

noncomputable def cyclicMaskInitial (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : CyclicMaskState p r A B hp :=
  CoordinateIdeal.cyclicInitial hp.pos (maskSupportSystem p r A B hp)
noncomputable def cyclicMaskTransition (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (d : Fin p) :=
  CoordinateIdeal.cyclicTransition hp.pos (maskSupportSystem p r A B hp) d
noncomputable def cyclicMaskIterate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : CyclicMaskState p r A B hp) :=
  CoordinateIdeal.cyclicRun hp.pos (maskSupportSystem p r A B hp) ds x

@[simp] theorem cyclicMask_initial_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    cyclicMaskToIdeal p r A B hp (cyclicMaskInitial p r A B hp) = idealMaskInitial p r A B hp :=
  (cyclicMaskToIdeal p r A B hp).apply_symm_apply _

theorem cyclicMask_transition_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : Fin p) (x : CyclicMaskState p r A B hp) :
    cyclicMaskToIdeal p r A B hp (cyclicMaskTransition p r A B hp d x) =
      idealMaskTransition p r A B hp d (cyclicMaskToIdeal p r A B hp x) :=
  CoordinateIdeal.cyclicTransition_embedding _ _ _ _

theorem cyclicMask_iterate_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : CyclicMaskState p r A B hp) :
    cyclicMaskToIdeal p r A B hp (cyclicMaskIterate p r A B hp ds x) =
      idealMaskIterate p r A B hp ds (cyclicMaskToIdeal p r A B hp x) :=
  CoordinateIdeal.cyclicRun_embedding _ _ _ _

noncomputable def cyclicMaskOutput (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x : CyclicMaskState p r A B hp) : ZMod (p^r) :=
  idealMaskOutput p r A B hp hr hB (cyclicMaskToIdeal p r A B hp x)

theorem cyclicMask_output_eq_ideal (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (ds : List (Fin p)) :
    cyclicMaskOutput p r A B hp hr hB (cyclicMaskIterate p r A B hp ds (cyclicMaskInitial p r A B hp)) =
      idealMaskOutput p r A B hp hr hB (idealMaskIterate p r A B hp ds (idealMaskInitial p r A B hp)) := by
  unfold cyclicMaskOutput
  rw [cyclicMask_iterate_embedding, cyclicMask_initial_embedding]

theorem cyclicMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    cyclicMaskOutput p r A B hp hr hB
      (cyclicMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (cyclicMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [cyclicMask_output_eq_ideal]
  exact idealMask_output_canonical_coefficient p r A B hp hr hB hAB n

theorem cyclicMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (CyclicMaskState p r A B hp) = p^(∑ i, leastMaskIdealCapacity p r A B hp i) :=
  CoordinateIdeal.cyclicState_card hp.pos _

theorem idealMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (IdealMaskState p r A B hp) = p^(∑ i, leastMaskIdealCapacity p r A B hp i) :=
  CoordinateIdeal.boxState_card hp.pos _ (leastMaskIdealCapacity_bound p r A B hp)

theorem idealMask_state_card_le_support (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (IdealMaskState p r A B hp) ≤ Nat.card (SupportMaskState p r A B hp) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  exact Nat.card_le_card_of_injective _ (idealMaskEmbedding_injective p r A B hp)

theorem cyclicMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (cyclicMaskOutput p r A B hp hr hB
        (cyclicMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (cyclicMaskInitial p r A B hp))) =
      cyclicMaskOutput p s A B hp hs hB
        (cyclicMaskIterate p s A B hp (finiteMaskDigitWord p n hp) (cyclicMaskInitial p s A B hp)) := by
  rw [cyclicMask_output_canonical_coefficient p r A B hp hr hB hAB,
    cyclicMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

structure CyclicCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  predecessor : IdealCanonicalMaskCertificate p r A B hp hr hB
  coordinates : CyclicMaskState p r A B hp ≃+ IdealMaskState p r A B hp
  output : ∀ n, cyclicMaskOutput p r A B hp hr hB
    (cyclicMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (cyclicMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)
  state_card : Nat.card (CyclicMaskState p r A B hp) = p^(∑ i, leastMaskIdealCapacity p r A B hp i)

noncomputable def cyclicCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    CyclicCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := idealCanonicalMaskCertificate p r A B hp hr hB hAB
  coordinates := cyclicMaskToIdeal p r A B hp
  output := cyclicMask_output_canonical_coefficient p r A B hp hr hB hAB
  state_card := cyclicMask_state_card p r A B hp

end KomorebiPadic
