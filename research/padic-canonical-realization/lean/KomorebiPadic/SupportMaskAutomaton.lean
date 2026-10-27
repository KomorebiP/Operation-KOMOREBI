import KomorebiPadic.ProfileSupport

/-! # Canonical coefficients on the least coordinate-support invariant
This machine retains the predecessor's mathematical output, not a supplied series
oracle. Its coordinate support is least among invariant coordinate boxes. It does
not minimize reachable states or general invariant submodules.
-/
namespace KomorebiPadic
open Polynomial

noncomputable def maskSupportSystem (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    CoordinateSupport.System (ZMod (p^r)) (ProfilePosition (leastMaskDegreeProfile p r A B hp)) (Fin p) :=
  profileSupportSystem (degreePrunedMaskMachine p r A B hp) (degreePrunedMaskInitial p r A B)
    (leastMaskDegreeProfile p r A B hp) (leastMaskDegreeProfile_bound p r A B hp)
    (leastMaskDegreeProfile_closed p r A B hp)

noncomputable def leastMaskCoordinateSupport (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Finset (ProfilePosition (leastMaskDegreeProfile p r A B hp)) :=
  CoordinateSupport.least (maskSupportSystem p r A B hp)

abbrev SupportMaskState (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :=
  CoordinateSupport.State (R := ZMod (p^r)) (leastMaskCoordinateSupport p r A B hp)

theorem leastMaskCoordinateSupport_closed (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    CoordinateSupport.Closed (maskSupportSystem p r A B hp) (leastMaskCoordinateSupport p r A B hp) :=
  CoordinateSupport.least_closed _

theorem leastMaskCoordinateSupport_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (s : Finset (ProfilePosition (leastMaskDegreeProfile p r A B hp)))
    (hs : CoordinateSupport.Closed (maskSupportSystem p r A B hp) s) :
    leastMaskCoordinateSupport p r A B hp ⊆ s := CoordinateSupport.least_subset _ _ hs

noncomputable def supportMaskInitial (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    SupportMaskState p r A B hp :=
  CoordinateSupport.restrict (leastMaskCoordinateSupport p r A B hp) (maskSupportSystem p r A B hp).initial

noncomputable def supportMaskEmbedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (s : SupportMaskState p r A B hp) : LeastProfileMaskState p r A B hp :=
  unflattenProfile (leastMaskDegreeProfile p r A B hp)
    (CoordinateSupport.embed (leastMaskCoordinateSupport p r A B hp) s)

noncomputable def supportMaskTransition (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : Fin p) (s : SupportMaskState p r A B hp) : SupportMaskState p r A B hp :=
  CoordinateSupport.transition (maskSupportSystem p r A B hp)
    (leastMaskCoordinateSupport p r A B hp) d s

noncomputable def supportMaskIterate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (s : SupportMaskState p r A B hp) : SupportMaskState p r A B hp :=
  CoordinateSupport.runRestricted (maskSupportSystem p r A B hp)
    (leastMaskCoordinateSupport p r A B hp) ds s

theorem supportMaskEmbedding_injective (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Function.Injective (supportMaskEmbedding p r A B hp) := by
  intro s t h
  apply CoordinateSupport.embed_injective (leastMaskCoordinateSupport p r A B hp)
  have hh := congrArg (flattenProfile (leastMaskDegreeProfile p r A B hp)) h
  simpa only [supportMaskEmbedding, flatten_unflatten] using hh

theorem supportMask_initial_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    supportMaskEmbedding p r A B hp (supportMaskInitial p r A B hp) = leastProfileMaskInitial p r A B hp := by
  unfold supportMaskEmbedding supportMaskInitial
  rw [leastMaskCoordinateSupport, CoordinateSupport.initial_embedding]
  rfl

theorem supportMask_transition_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : Fin p) (s : SupportMaskState p r A B hp) :
    supportMaskEmbedding p r A B hp (supportMaskTransition p r A B hp d s) =
      profileMachineTransition (degreePrunedMaskMachine p r A B hp)
        (leastMaskDegreeProfile p r A B hp) d.val (supportMaskEmbedding p r A B hp s) := by
  unfold supportMaskEmbedding supportMaskTransition
  rw [CoordinateSupport.transition_embedding _ _ (leastMaskCoordinateSupport_closed p r A B hp)]
  rfl

theorem supportMask_iterate_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (s : SupportMaskState p r A B hp) :
    supportMaskEmbedding p r A B hp (supportMaskIterate p r A B hp ds s) =
      iterateProfileMachine (degreePrunedMaskMachine p r A B hp)
        (leastMaskDegreeProfile p r A B hp) (ds.map Fin.val) (supportMaskEmbedding p r A B hp s) := by
  unfold supportMaskEmbedding supportMaskIterate
  rw [CoordinateSupport.run_embedding _ _ (leastMaskCoordinateSupport_closed p r A B hp)]
  exact profileSupportSystem_run _ _ _ _ _ ds _

noncomputable def supportMaskOutput (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (s : SupportMaskState p r A B hp) : ZMod (p^r) :=
  leastProfileMaskOutput p r A B hp hr hB (supportMaskEmbedding p r A B hp s)

theorem supportMask_output_eq_profile (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (ds : List (Fin p)) :
    supportMaskOutput p r A B hp hr hB (supportMaskIterate p r A B hp ds (supportMaskInitial p r A B hp)) =
      leastProfileMaskOutput p r A B hp hr hB
        (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
          (ds.map Fin.val) (leastProfileMaskInitial p r A B hp)) := by
  unfold supportMaskOutput
  rw [supportMask_iterate_embedding, supportMask_initial_embedding]

theorem supportMask_output_canonical_word (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (ds : List (Fin p)) :
    supportMaskOutput p r A B hp hr hB (supportMaskIterate p r A B hp ds (supportMaskInitial p r A B hp)) =
      PowerSeries.coeff (cartierWordValue p (ds.map Fin.val)) (canonicalMaskSeries p r A B hp hr hB) := by
  rw [supportMask_output_eq_profile]
  apply leastProfileMask_output_canonical_word p r A B hp hr hB hAB
  intro d hd
  obtain ⟨e, _, rfl⟩ := List.mem_map.mp hd
  exact e.isLt

/-- Exact conversion of the ordinary digit list into an in-range alphabet. -/
def finiteMaskDigitWord (p n : ℕ) (hp : p.Prime) : List (Fin p) :=
  (Nat.digits p n).attach.map (fun d => ⟨d.val, Nat.digits_lt_base hp.one_lt d.property⟩)

@[simp] theorem finiteMaskDigitWord_values (p n : ℕ) (hp : p.Prime) :
    (finiteMaskDigitWord p n hp).map Fin.val = Nat.digits p n := by
  simp [finiteMaskDigitWord, List.map_map]

theorem supportMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    supportMaskOutput p r A B hp hr hB
      (supportMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (supportMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [supportMask_output_canonical_word p r A B hp hr hB hAB,
    finiteMaskDigitWord_values, cartierWordValue_eq_ofDigits, Nat.ofDigits_digits]

theorem leastMaskCoordinateSupport_slots_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    (leastMaskCoordinateSupport p r A B hp).card ≤ ∑ i, leastMaskDegreeProfile p r A B hp i :=
  profileSupportSystem_slots_le _ _ _ _ _

theorem supportMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (SupportMaskState p r A B hp) = p^(r * (leastMaskCoordinateSupport p r A B hp).card) := by
  classical
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  simp only [SupportMaskState, CoordinateSupport.State, Nat.card_eq_fintype_card,
    Fintype.card_fun, Fintype.card_coe, ZMod.card, ← pow_mul]

theorem supportMask_state_card_le_profile (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (SupportMaskState p r A B hp) ≤ Nat.card (LeastProfileMaskState p r A B hp) := by
  rw [supportMask_state_card p r A B hp, leastProfileMask_state_card p r A B hp]
  apply Nat.pow_le_pow_right hp.pos
  exact Nat.mul_le_mul_left r (leastMaskCoordinateSupport_slots_le p r A B hp)

/-- Every omitted coefficient position gives a strict slot reduction. -/
theorem leastMaskCoordinateSupport_slots_lt (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (h : leastMaskCoordinateSupport p r A B hp ≠ Finset.univ) :
    (leastMaskCoordinateSupport p r A B hp).card < ∑ i, leastMaskDegreeProfile p r A B hp i := by
  have hh := Finset.card_lt_card
    (Finset.ssubset_iff_subset_ne.mpr ⟨Finset.subset_univ _,h⟩)
  simpa only [Finset.card_univ, profilePosition_card] using hh

/-- Precision compatibility is at the output level, not an identification of supports. -/
theorem supportMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (supportMaskOutput p r A B hp hr hB
        (supportMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (supportMaskInitial p r A B hp))) =
      supportMaskOutput p s A B hp hs hB
        (supportMaskIterate p s A B hp (finiteMaskDigitWord p n hp) (supportMaskInitial p s A B hp)) := by
  rw [supportMask_output_canonical_coefficient p r A B hp hr hB hAB,
    supportMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

structure SupportCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  predecessor : LeastProfileCanonicalMaskCertificate p r A B hp hr hB
  closed : CoordinateSupport.Closed (maskSupportSystem p r A B hp) (leastMaskCoordinateSupport p r A B hp)
  least : ∀ s, CoordinateSupport.Closed (maskSupportSystem p r A B hp) s →
    leastMaskCoordinateSupport p r A B hp ⊆ s
  output : ∀ n, supportMaskOutput p r A B hp hr hB
    (supportMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (supportMaskInitial p r A B hp)) =
    PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)
  state_card : Nat.card (SupportMaskState p r A B hp) = p^(r*(leastMaskCoordinateSupport p r A B hp).card)

noncomputable def supportCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    SupportCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := leastProfileCanonicalMaskCertificate p r A B hp hr hB hAB
  closed := leastMaskCoordinateSupport_closed p r A B hp
  least := leastMaskCoordinateSupport_le p r A B hp
  output := supportMask_output_canonical_coefficient p r A B hp hr hB hAB
  state_card := supportMask_state_card p r A B hp

end KomorebiPadic
