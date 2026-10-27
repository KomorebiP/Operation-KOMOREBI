import KomorebiPadic.LinearReachability
import KomorebiPadic.CyclicMaskAutomaton

/-! # Canonical coefficients on the least correlated reachable submodule
No field hypothesis, orbit enumeration, or supplied-series oracle is introduced.
The module is least among all invariant submodules in the original profile space.
It is not yet quotiented by future-output equivalence.
-/
namespace KomorebiPadic
open Polynomial
noncomputable section

/-- The existing ideal-state linear system, with no changed transition rule. -/
def idealMaskLinearSystem (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    LinearReachability.System (ZMod (p^r)) (IdealMaskState p r A B hp) (Fin p) where
  initial := idealMaskInitial p r A B hp
  transition := idealMaskTransition p r A B hp

theorem idealMaskLinearSystem_run (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : IdealMaskState p r A B hp) :
    LinearReachability.run (idealMaskLinearSystem p r A B hp) ds x =
      idealMaskIterate p r A B hp ds x := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (idealMaskTransition p r A B hp d x)

def reachableMaskSpan (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :=
  LinearReachability.reachable (idealMaskLinearSystem p r A B hp)

abbrev ReachableMaskState (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) := reachableMaskSpan p r A B hp

def reachableMaskRounds (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : ℕ :=
  ∑ i, leastMaskIdealCapacity p r A B hp i

theorem reachableMaskSpan_closed (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    LinearReachability.Closed (idealMaskLinearSystem p r A B hp) (reachableMaskSpan p r A B hp) :=
  LinearReachability.reachable_closed _

theorem reachableMaskSpan_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (U : Submodule (ZMod (p^r)) (IdealMaskState p r A B hp))
    (hU : LinearReachability.Closed (idealMaskLinearSystem p r A B hp) U) :
    reachableMaskSpan p r A B hp ≤ U := LinearReachability.reachable_le _ U hU

/-- Finite construction: no more rounds than the predecessor's p-adic digit capacity. -/
theorem reachableMaskSpan_eq_finiteClosure (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    LinearReachability.iterate (idealMaskLinearSystem p r A B hp)
      (reachableMaskRounds p r A B hp) = reachableMaskSpan p r A B hp := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  exact LinearReachability.iterate_eq_reachable _ hp (idealMask_state_card p r A B hp)

theorem reachableMaskClosure_stable (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    LinearReachability.step (idealMaskLinearSystem p r A B hp)
      (LinearReachability.iterate (idealMaskLinearSystem p r A B hp) (reachableMaskRounds p r A B hp)) =
    LinearReachability.iterate (idealMaskLinearSystem p r A B hp) (reachableMaskRounds p r A B hp) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  exact LinearReachability.iterate_stabilizes _ hp (idealMask_state_card p r A B hp)

def reachableMaskInitial (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : ReachableMaskState p r A B hp :=
  LinearReachability.initial (idealMaskLinearSystem p r A B hp)

def reachableMaskTransition (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (d : Fin p) :
    ReachableMaskState p r A B hp →ₗ[ZMod (p^r)] ReachableMaskState p r A B hp :=
  LinearReachability.transition (idealMaskLinearSystem p r A B hp) d

def reachableMaskIterate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : ReachableMaskState p r A B hp) : ReachableMaskState p r A B hp :=
  LinearReachability.runRestricted (idealMaskLinearSystem p r A B hp) ds x

theorem reachableMask_iterate_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : ReachableMaskState p r A B hp) :
    (reachableMaskIterate p r A B hp ds x).val = idealMaskIterate p r A B hp ds x.val := by
  exact (LinearReachability.runRestricted_embedding (idealMaskLinearSystem p r A B hp) ds x).trans
    (idealMaskLinearSystem_run p r A B hp ds x.val)

def reachableMaskToCyclic (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (x : ReachableMaskState p r A B hp) : CyclicMaskState p r A B hp :=
  (cyclicMaskToIdeal p r A B hp).symm x.val

theorem reachableMaskToCyclic_injective (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Function.Injective (reachableMaskToCyclic p r A B hp) :=
  (cyclicMaskToIdeal p r A B hp).symm.injective.comp Subtype.val_injective

theorem reachableMask_initial_cyclic (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    reachableMaskToCyclic p r A B hp (reachableMaskInitial p r A B hp) = cyclicMaskInitial p r A B hp := by
  apply (cyclicMaskToIdeal p r A B hp).injective
  rw [reachableMaskToCyclic, AddEquiv.apply_symm_apply, cyclicMask_initial_embedding]
  rfl

theorem reachableMask_transition_cyclic (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : Fin p) (x : ReachableMaskState p r A B hp) :
    reachableMaskToCyclic p r A B hp (reachableMaskTransition p r A B hp d x) =
      cyclicMaskTransition p r A B hp d (reachableMaskToCyclic p r A B hp x) := by
  apply (cyclicMaskToIdeal p r A B hp).injective
  rw [reachableMaskToCyclic, AddEquiv.apply_symm_apply, cyclicMask_transition_embedding,
    reachableMaskToCyclic, AddEquiv.apply_symm_apply]
  rfl

theorem reachableMask_iterate_cyclic (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : ReachableMaskState p r A B hp) :
    reachableMaskToCyclic p r A B hp (reachableMaskIterate p r A B hp ds x) =
      cyclicMaskIterate p r A B hp ds (reachableMaskToCyclic p r A B hp x) := by
  apply (cyclicMaskToIdeal p r A B hp).injective
  rw [reachableMaskToCyclic, AddEquiv.apply_symm_apply, cyclicMask_iterate_embedding,
    reachableMaskToCyclic, AddEquiv.apply_symm_apply, reachableMask_iterate_embedding]

def reachableMaskOutput (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (x : ReachableMaskState p r A B hp) : ZMod (p^r) :=
  idealMaskOutput p r A B hp hr hB x.val

theorem reachableMask_output_eq_cyclic (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (x : ReachableMaskState p r A B hp) :
    reachableMaskOutput p r A B hp hr hB x =
      cyclicMaskOutput p r A B hp hr hB (reachableMaskToCyclic p r A B hp x) := by
  simp only [reachableMaskOutput, cyclicMaskOutput, reachableMaskToCyclic, AddEquiv.apply_symm_apply]

theorem reachableMask_output_canonical_word (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (ds : List (Fin p)) :
    reachableMaskOutput p r A B hp hr hB
      (reachableMaskIterate p r A B hp ds (reachableMaskInitial p r A B hp)) =
      PowerSeries.coeff (cartierWordValue p (ds.map Fin.val)) (canonicalMaskSeries p r A B hp hr hB) := by
  unfold reachableMaskOutput
  rw [reachableMask_iterate_embedding]
  exact idealMask_output_canonical_word p r A B hp hr hB hAB ds

theorem reachableMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    reachableMaskOutput p r A B hp hr hB
      (reachableMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (reachableMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  unfold reachableMaskOutput
  rw [reachableMask_iterate_embedding]
  exact idealMask_output_canonical_coefficient p r A B hp hr hB hAB n

theorem reachableMask_state_card_le_cyclic (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (ReachableMaskState p r A B hp) ≤ Nat.card (CyclicMaskState p r A B hp) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  rw [cyclicMask_state_card, ← idealMask_state_card p r A B hp]
  exact LinearReachability.state_card_le _

theorem reachableMask_state_card_power (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (ReachableMaskState p r A B hp) =
      p ^ Nat.log p (Nat.card (ReachableMaskState p r A B hp)) ∧
    Nat.log p (Nat.card (ReachableMaskState p r A B hp)) ≤ reachableMaskRounds p r A B hp :=
  LinearReachability.submodule_card_power hp (idealMask_state_card p r A B hp) _

/-- Original full profile coordinate module and its actual summed digit maps. -/
def profileMaskLinearSystem (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    LinearReachability.System (ZMod (p^r))
      (ProfilePosition (leastMaskDegreeProfile p r A B hp) → ZMod (p^r)) (Fin p) where
  initial := (maskSupportSystem p r A B hp).initial
  transition := (maskSupportSystem p r A B hp).transition

/-- The image is globally least in the entire profile module, not only within ideal products. -/
theorem reachableMask_image_eq_profileReachable (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    (reachableMaskSpan p r A B hp).map
      (CoordinateIdeal.boxModule (p := p) (r := r) (leastMaskIdealCapacity p r A B hp)).subtype =
      LinearReachability.reachable (profileMaskLinearSystem p r A B hp) := by
  apply LinearReachability.map_reachable
  · rfl
  · intro d x; rfl

theorem reachableMask_global_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (U : Submodule (ZMod (p^r)) (ProfilePosition (leastMaskDegreeProfile p r A B hp) → ZMod (p^r)))
    (hU : LinearReachability.Closed (profileMaskLinearSystem p r A B hp) U) :
    (reachableMaskSpan p r A B hp).map
      (CoordinateIdeal.boxModule (p := p) (r := r) (leastMaskIdealCapacity p r A B hp)).subtype ≤ U := by
  rw [reachableMask_image_eq_profileReachable]
  exact LinearReachability.reachable_le _ U hU

theorem reachableMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (reachableMaskOutput p r A B hp hr hB
        (reachableMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (reachableMaskInitial p r A B hp))) =
    reachableMaskOutput p s A B hp hs hB
      (reachableMaskIterate p s A B hp (finiteMaskDigitWord p n hp) (reachableMaskInitial p s A B hp)) := by
  rw [reachableMask_output_canonical_coefficient p r A B hp hr hB hAB,
    reachableMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

structure ReachableCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬(p : ℤ) ∣ B.coeff 0) where
  predecessor : CyclicCanonicalMaskCertificate p r A B hp hr hB
  closed : LinearReachability.Closed (idealMaskLinearSystem p r A B hp) (reachableMaskSpan p r A B hp)
  least : ∀ U, LinearReachability.Closed (idealMaskLinearSystem p r A B hp) U → reachableMaskSpan p r A B hp ≤ U
  finite_closure : LinearReachability.iterate (idealMaskLinearSystem p r A B hp)
    (reachableMaskRounds p r A B hp) = reachableMaskSpan p r A B hp
  output : ∀ n, reachableMaskOutput p r A B hp hr hB
    (reachableMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (reachableMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)
  state_card_bound : Nat.card (ReachableMaskState p r A B hp) ≤ Nat.card (CyclicMaskState p r A B hp)

def reachableCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    ReachableCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := cyclicCanonicalMaskCertificate p r A B hp hr hB hAB
  closed := reachableMaskSpan_closed p r A B hp
  least := reachableMaskSpan_le p r A B hp
  finite_closure := reachableMaskSpan_eq_finiteClosure p r A B hp
  output := reachableMask_output_canonical_coefficient p r A B hp hr hB hAB
  state_card_bound := reachableMask_state_card_le_cyclic p r A B hp
end
end KomorebiPadic
