import KomorebiPadic.ObservableQuotient
import KomorebiPadic.PresentedReachableMask

/-! # Observable quotients of the actual correlated mask module
The output functional is bundled from the inherited finite coefficient formula.
The quotient is of Block31's actual reachable submodule; no supplied matrix or
coefficient oracle is used. Block32 supplies a chosen cyclic presentation.
-/
namespace KomorebiPadic
open Polynomial
noncomputable section

/-- Remove the support wrapper without changing any coordinate value. -/
theorem idealMaskOutput_eq_fullProfile (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x : IdealMaskState p r A B hp) :
    idealMaskOutput p r A B hp hr hB x =
      leastProfileMaskOutput p r A B hp hr hB
        (unflattenProfile (leastMaskDegreeProfile p r A B hp) x.val) := by
  unfold idealMaskOutput supportMaskOutput supportMaskEmbedding idealMaskEmbedding
    CoordinateIdeal.supportEmbedding
  rw [CoordinateSupport.embed_restrict _ _ (CoordinateIdeal.least_supported hp.pos _ x)]

theorem idealMaskOutput_add (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x y : IdealMaskState p r A B hp) :
    idealMaskOutput p r A B hp hr hB (x+y) =
      idealMaskOutput p r A B hp hr hB x + idealMaskOutput p r A B hp hr hB y := by
  simp only [idealMaskOutput_eq_fullProfile, leastProfileMaskOutput]
  change degreePrunedMaskOutput p r A B hp hr hB
    (embedProfileState _ _ (unflattenProfile _ x.val + unflattenProfile _ y.val)) = _
  rw [embedProfileState_add]
  simp [degreePrunedMaskOutput, Pi.add_apply, add_mul, Finset.sum_add_distrib]

theorem idealMaskOutput_smul (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (a : ZMod (p^r))
    (x : IdealMaskState p r A B hp) :
    idealMaskOutput p r A B hp hr hB (a • x) = a • idealMaskOutput p r A B hp hr hB x := by
  simp only [idealMaskOutput_eq_fullProfile, leastProfileMaskOutput]
  change degreePrunedMaskOutput p r A B hp hr hB
    (embedProfileState _ _ (a • unflattenProfile _ x.val)) = _
  rw [embedProfileState_smul]
  simp [degreePrunedMaskOutput, Pi.smul_apply, smul_eq_mul, Finset.mul_sum, mul_assoc]

def reachableMaskOutputLinear (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    ReachableMaskState p r A B hp →ₗ[ZMod (p^r)] ZMod (p^r) where
  toFun := reachableMaskOutput p r A B hp hr hB
  map_add' x y := idealMaskOutput_add p r A B hp hr hB x.val y.val
  map_smul' a x := idealMaskOutput_smul p r A B hp hr hB a x.val

def observableMaskSystem (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    LinearObservability.System (ZMod (p^r)) (ReachableMaskState p r A B hp) (Fin p) where
  dynamics := reachableStateSystem p r A B hp
  output := reachableMaskOutputLinear p r A B hp hr hB

def unobservableMaskSpan (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :=
  LinearObservability.unobservable (observableMaskSystem p r A B hp hr hB)

abbrev ObservableMaskState (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :=
  LinearObservability.State (observableMaskSystem p r A B hp hr hB)

def observableMaskProjection (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :=
  LinearObservability.projection (observableMaskSystem p r A B hp hr hB)

def observableMaskTransition (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (d : Fin p) :=
  LinearObservability.quotientTransition (observableMaskSystem p r A B hp hr hB) d

def observableMaskInitial (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :=
  observableMaskProjection p r A B hp hr hB (reachableMaskInitial p r A B hp)

def observableMaskIterate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :=
  LinearReachability.run (LinearObservability.quotientSystem
    (observableMaskSystem p r A B hp hr hB)).dynamics

def observableMaskOutput (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :=
  LinearObservability.quotientOutput (observableMaskSystem p r A B hp hr hB)

@[simp] theorem observableMask_transition_projection (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (d : Fin p) (x : ReachableMaskState p r A B hp) :
    observableMaskTransition p r A B hp hr hB d (observableMaskProjection p r A B hp hr hB x) =
      observableMaskProjection p r A B hp hr hB (reachableMaskTransition p r A B hp d x) := rfl

@[simp] theorem observableMask_output_projection (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x : ReachableMaskState p r A B hp) :
    observableMaskOutput p r A B hp hr hB (observableMaskProjection p r A B hp hr hB x) =
      reachableMaskOutput p r A B hp hr hB x := rfl

theorem observableMask_iterate_projection (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (ds : List (Fin p))
    (x : ReachableMaskState p r A B hp) :
    observableMaskIterate p r A B hp hr hB ds (observableMaskProjection p r A B hp hr hB x) =
      observableMaskProjection p r A B hp hr hB (reachableMaskIterate p r A B hp ds x) := by
  exact (LinearObservability.run_projection (observableMaskSystem p r A B hp hr hB) ds x).trans
    (congrArg (observableMaskProjection p r A B hp hr hB) (reachableStateSystem_run p r A B hp ds x))

theorem observableMask_output_canonical_word (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B)
    (ds : List (Fin p)) :
    observableMaskOutput p r A B hp hr hB
      (observableMaskIterate p r A B hp hr hB ds (observableMaskInitial p r A B hp hr hB)) =
      PowerSeries.coeff (cartierWordValue p (ds.map Fin.val)) (canonicalMaskSeries p r A B hp hr hB) := by
  rw [observableMaskInitial, observableMask_iterate_projection, observableMask_output_projection]
  exact reachableMask_output_canonical_word p r A B hp hr hB hAB ds

theorem observableMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    observableMaskOutput p r A B hp hr hB
      (observableMaskIterate p r A B hp hr hB (finiteMaskDigitWord p n hp)
        (observableMaskInitial p r A B hp hr hB)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [observableMaskInitial, observableMask_iterate_projection, observableMask_output_projection]
  exact reachableMask_output_canonical_coefficient p r A B hp hr hB hAB n

/-- Exact source-state equivalence, not just equality of one output coefficient. -/
theorem observableMask_projection_eq_iff (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x y : ReachableMaskState p r A B hp) :
    observableMaskProjection p r A B hp hr hB x = observableMaskProjection p r A B hp hr hB y ↔
      ∀ ds : List (Fin p), reachableMaskOutput p r A B hp hr hB (reachableMaskIterate p r A B hp ds x) =
        reachableMaskOutput p r A B hp hr hB (reachableMaskIterate p r A B hp ds y) := by
  have he := LinearObservability.projection_eq_iff (observableMaskSystem p r A B hp hr hB) x y
  simpa only [LinearObservability.observation, LinearMap.comp_apply, LinearObservability.wordMap_apply,
    observableMaskSystem, reachableMaskOutputLinear, reachableStateSystem_run] using he

/-- All future outputs separate states of the new quotient. -/
theorem observableMask_observable (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x y : ObservableMaskState p r A B hp hr hB)
    (he : ∀ ds : List (Fin p),
      observableMaskOutput p r A B hp hr hB (observableMaskIterate p r A B hp hr hB ds x) =
      observableMaskOutput p r A B hp hr hB (observableMaskIterate p r A B hp hr hB ds y)) : x = y := by
  apply LinearObservability.quotient_observable (observableMaskSystem p r A B hp hr hB) x y
  intro ds
  simpa only [LinearObservability.observation, LinearMap.comp_apply, LinearObservability.wordMap_apply] using he ds

def observableMaskRounds (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : ℕ :=
  Nat.log p (Nat.card (ReachableMaskState p r A B hp))

theorem unobservableMaskSpan_finite (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    LinearObservability.iterate (observableMaskSystem p r A B hp hr hB) (observableMaskRounds p r A B hp) =
      unobservableMaskSpan p r A B hp hr hB := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  exact LinearObservability.iterate_eq_unobservable _ hp (reachableMask_state_card_power p r A B hp).1

theorem observableMask_state_card_mul (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    Nat.card (ObservableMaskState p r A B hp hr hB) * Nat.card (unobservableMaskSpan p r A B hp hr hB) =
      Nat.card (ReachableMaskState p r A B hp) :=
  LinearObservability.quotient_card_mul _

theorem observableMask_state_card_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    Nat.card (ObservableMaskState p r A B hp hr hB) ≤ Nat.card (ReachableMaskState p r A B hp) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  exact LinearObservability.quotient_card_le _

/-- Block32's cyclic-factor existence now applies to the actual behavior quotient. -/
def observableMaskPresentation (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    FiniteModulePresentation.Presentation p r (ObservableMaskState p r A B hp hr hB) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  let : Fintype (ReachableMaskState p r A B hp) := Fintype.ofFinite _
  exact FiniteModulePresentation.choosePresentation hp

theorem observableMask_signature_unique (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (P : FiniteModulePresentation.Presentation p r (ObservableMaskState p r A B hp hr hB)) :
    FiniteModulePresentation.signature P =
      FiniteModulePresentation.signature (observableMaskPresentation p r A B hp hr hB) :=
  FiniteModulePresentation.signature_unique hp.one_lt P _

theorem observableMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (observableMaskOutput p r A B hp hr hB
        (observableMaskIterate p r A B hp hr hB (finiteMaskDigitWord p n hp) (observableMaskInitial p r A B hp hr hB))) =
    observableMaskOutput p s A B hp hs hB
      (observableMaskIterate p s A B hp hs hB (finiteMaskDigitWord p n hp) (observableMaskInitial p s A B hp hs hB)) := by
  rw [observableMask_output_canonical_coefficient p r A B hp hr hB hAB,
    observableMask_output_canonical_coefficient p s A B hp hs hB
      (hAB.map (ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))))]
  rw [← PowerSeries.coeff_map, canonicalMaskSeries_reduce p r s A B hp hr hs hsr hB hAB]

end
end KomorebiPadic
