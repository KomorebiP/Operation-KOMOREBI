import KomorebiPadic.ProfiledCartierMachine
import KomorebiPadic.NumeratorDegreeEmbedding

/-! # Canonical masks on least layer-specific degree profiles
The leastness concerns the explicit zero-aware, all-digit degree inequalities,
not orbit minimization or linear independence of represented series. The variable
row transition is specified via the old padded machine; no runtime speed claim.
-/
namespace KomorebiPadic
open Polynomial

noncomputable def maskDegreeSystem (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :=
  machineDegreeSystem (degreePrunedMaskMachine p r A B hp) (degreePrunedMaskInitial p r A B)

noncomputable def leastMaskDegreeProfile (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Fin (prunedMaskLayerBound p r B) → ℕ := leastDegreeProfile (maskDegreeSystem p r A B hp)

theorem leastMaskDegreeProfile_closed (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    DegreeProfileClosed (maskDegreeSystem p r A B hp) (leastMaskDegreeProfile p r A B hp) :=
  leastDegreeProfile_closed _

theorem leastMaskDegreeProfile_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (w : Fin (prunedMaskLayerBound p r B) → ℕ)
    (hw : DegreeProfileClosed (maskDegreeSystem p r A B hp) w) :
    leastMaskDegreeProfile p r A B hp ≤ w := leastDegreeProfile_le _ w hw

theorem leastMaskDegreeProfile_bound (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    ∀ i, leastMaskDegreeProfile p r A B hp i ≤ degreePrunedNumeratorBound p r A B+1 :=
  leastDegreeProfile_bound _

theorem leastMaskDegreeProfile_slots_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    (∑ i, leastMaskDegreeProfile p r A B hp i) ≤
      prunedMaskLayerBound p r B * (degreePrunedNumeratorBound p r A B+1) :=
  degreeProfileMass_le _ (leastMaskDegreeProfile_bound p r A B hp)

/-- Any strictly reduced row strictly reduces the total coefficient slots. -/
theorem leastMaskDegreeProfile_slots_lt (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (h : ∃ i, leastMaskDegreeProfile p r A B hp i < degreePrunedNumeratorBound p r A B+1) :
    (∑ i, leastMaskDegreeProfile p r A B hp i) <
      prunedMaskLayerBound p r B * (degreePrunedNumeratorBound p r A B+1) := by
  obtain ⟨i, hi⟩ := h
  have hh := Finset.sum_lt_sum (fun j (_ : j ∈ Finset.univ) =>
    leastMaskDegreeProfile_bound p r A B hp j) ⟨i, Finset.mem_univ _, hi⟩
  simpa using hh

abbrev LeastProfileMaskState (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :=
  ProfileCoefficientState (ZMod (p^r)) (leastMaskDegreeProfile p r A B hp)

noncomputable def leastProfileMaskInitial (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    LeastProfileMaskState p r A B hp :=
  profileMachineInitial (degreePrunedMaskInitial p r A B) (leastMaskDegreeProfile p r A B hp)

noncomputable def leastProfileMaskOutput (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬(p : ℤ) ∣ B.coeff 0)
    (s : LeastProfileMaskState p r A B hp) : ZMod (p^r) :=
  degreePrunedMaskOutput p r A B hp hr hB
    (embedProfileState (degreePrunedNumeratorBound p r A B) (leastMaskDegreeProfile p r A B hp) s)

/-- Literal initial-coordinate equality, including zero-capacity rows. -/
theorem leastProfileMask_initial_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    embedProfileState _ (leastMaskDegreeProfile p r A B hp) (leastProfileMaskInitial p r A B hp) =
      degreePrunedMaskInitial p r A B :=
  profileMachineInitial_embedding _ _ _ (leastMaskDegreeProfile_closed p r A B hp)

theorem leastProfileMask_transition_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : ℕ) (s : LeastProfileMaskState p r A B hp) :
    embedProfileState _ (leastMaskDegreeProfile p r A B hp)
      (profileMachineTransition (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp) d s) =
      machineTransition (degreePrunedMaskMachine p r A B hp) d
        (embedProfileState _ (leastMaskDegreeProfile p r A B hp) s) :=
  profileMachineTransition_embedding _ (degreePrunedMaskInitial p r A B) _
    (leastMaskDegreeProfile_bound p r A B hp) (leastMaskDegreeProfile_closed p r A B hp) d s

theorem leastProfileMask_iterate_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (ds : List ℕ) :
    embedProfileState _ (leastMaskDegreeProfile p r A B hp)
      (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
        ds (leastProfileMaskInitial p r A B hp)) =
      iterateMachine (degreePrunedMaskMachine p r A B hp) ds (degreePrunedMaskInitial p r A B) := by
  rw [iterateProfileMachine_embedding _ (degreePrunedMaskInitial p r A B) _
    (leastMaskDegreeProfile_bound p r A B hp) (leastMaskDegreeProfile_closed p r A B hp),
    leastProfileMask_initial_embedding]

/-- Every in-range word has exactly the canonical series coefficient. -/
theorem leastProfileMask_output_canonical_word (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬(p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (ds : List ℕ) (hd : ∀ d ∈ ds, d < p) :
    leastProfileMaskOutput p r A B hp hr hB
      (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
        ds (leastProfileMaskInitial p r A B hp)) =
      PowerSeries.coeff (cartierWordValue p ds) (canonicalMaskSeries p r A B hp hr hB) := by
  unfold leastProfileMaskOutput
  rw [leastProfileMask_iterate_embedding]
  exact degreePrunedMask_output_canonical_word p r A B hp hr hB hAB ds hd

theorem leastProfileMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬(p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    leastProfileMaskOutput p r A B hp hr hB
      (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
        (Nat.digits p n) (leastProfileMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [leastProfileMask_output_canonical_word p r A B hp hr hB hAB _
    (fun d hd => Nat.digits_lt_base hp.one_lt hd), cartierWordValue_eq_ofDigits, Nat.ofDigits_digits]

theorem leastProfileMask_output_eq_degreePruned (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬(p : ℤ) ∣ B.coeff 0) (ds : List ℕ) :
    leastProfileMaskOutput p r A B hp hr hB
      (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
        ds (leastProfileMaskInitial p r A B hp)) =
      degreePrunedMaskOutput p r A B hp hr hB
        (iterateMachine (degreePrunedMaskMachine p r A B hp) ds (degreePrunedMaskInitial p r A B)) := by
  unfold leastProfileMaskOutput
  rw [leastProfileMask_iterate_embedding]

/-- Exact ambient cardinality, not the number of reachable states. -/
theorem leastProfileMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (LeastProfileMaskState p r A B hp) =
      p^(r * ∑ i, leastMaskDegreeProfile p r A B hp i) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  rw [Nat.card_eq_fintype_card, profileCoefficientState_card, ZMod.card, ← pow_mul]

theorem leastProfileMask_state_card_le_degreePruned (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (LeastProfileMaskState p r A B hp) ≤
      Nat.card (CartierCoefficientState (ZMod (p^r)) (prunedMaskLayerBound p r B)
        (degreePrunedNumeratorBound p r A B)) := by
  rw [leastProfileMask_state_card p r A B hp, degreePrunedMask_state_card p r A B hp]
  apply Nat.pow_le_pow_right hp.pos
  simpa only [Nat.mul_assoc] using Nat.mul_le_mul_left r (leastMaskDegreeProfile_slots_le p r A B hp)

/-- Outputs still reduce correctly when precision changes, without identifying state vectors. -/
theorem leastProfileMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (leastProfileMaskOutput p r A B hp hr hB
        (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
          (Nat.digits p n) (leastProfileMaskInitial p r A B hp))) =
      leastProfileMaskOutput p s A B hp hs hB
        (iterateProfileMachine (degreePrunedMaskMachine p s A B hp) (leastMaskDegreeProfile p s A B hp)
          (Nat.digits p n) (leastProfileMaskInitial p s A B hp)) := by
  rw [leastProfileMask_output_canonical_coefficient p r A B hp hr hB hAB,
    leastProfileMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

structure LeastProfileCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬(p : ℤ) ∣ B.coeff 0) where
  predecessor : DegreePrunedCanonicalMaskCertificate p r A B hp hr hB
  profile_closed : DegreeProfileClosed (maskDegreeSystem p r A B hp) (leastMaskDegreeProfile p r A B hp)
  profile_least : ∀ w, DegreeProfileClosed (maskDegreeSystem p r A B hp) w → leastMaskDegreeProfile p r A B hp ≤ w
  profile_bound : ∀ i, leastMaskDegreeProfile p r A B hp i ≤ degreePrunedNumeratorBound p r A B+1
  output : ∀ n, leastProfileMaskOutput p r A B hp hr hB
    (iterateProfileMachine (degreePrunedMaskMachine p r A B hp) (leastMaskDegreeProfile p r A B hp)
      (Nat.digits p n) (leastProfileMaskInitial p r A B hp)) =
    PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)
  state_card : Nat.card (LeastProfileMaskState p r A B hp) = p^(r * ∑ i, leastMaskDegreeProfile p r A B hp i)

noncomputable def leastProfileCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    LeastProfileCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := degreePrunedCanonicalMaskCertificate p r A B hp hr hB hAB
  profile_closed := leastMaskDegreeProfile_closed p r A B hp
  profile_least := leastMaskDegreeProfile_le p r A B hp
  profile_bound := leastMaskDegreeProfile_bound p r A B hp
  output := leastProfileMask_output_canonical_coefficient p r A B hp hr hB hAB
  state_card := leastProfileMask_state_card p r A B hp

end KomorebiPadic
