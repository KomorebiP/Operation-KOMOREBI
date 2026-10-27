import KomorebiPadic.CyclicPresentationDynamics
import KomorebiPadic.ReachableMaskAutomaton

/-! # Actual reachable mask machines in cyclic invariant-factor coordinates
The coordinate equivalence is chosen, not a canonical basis. Its exponent
multiset is intrinsic. The underlying module and all coefficient outputs are
unchanged; observational minimization is a separate target.
-/
namespace KomorebiPadic
open Polynomial
noncomputable section

/-- Existence applies to the actual Block31 reachable module, not a supplied matrix surrogate. -/
def reachableMaskPresentation (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    FiniteModulePresentation.Presentation p r (ReachableMaskState p r A B hp) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  exact FiniteModulePresentation.choosePresentation (p := p) (r := r) hp

abbrev PresentedMaskState (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :=
  FiniteModulePresentation.Coordinates (reachableMaskPresentation p r A B hp)

/-- Block31's restricted system, with the same seed and restricted digit maps. -/
def reachableStateSystem (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    LinearReachability.System (ZMod (p^r)) (ReachableMaskState p r A B hp) (Fin p) where
  initial := reachableMaskInitial p r A B hp
  transition := reachableMaskTransition p r A B hp

theorem reachableStateSystem_run (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : ReachableMaskState p r A B hp) :
    LinearReachability.run (reachableStateSystem p r A B hp) ds x =
      reachableMaskIterate p r A B hp ds x := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (reachableMaskTransition p r A B hp d x)

def presentedMaskInitial (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : PresentedMaskState p r A B hp :=
  FiniteModulePresentation.initial (reachableMaskPresentation p r A B hp) (reachableStateSystem p r A B hp)

def presentedMaskTransition (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (d : Fin p) :
    PresentedMaskState p r A B hp →+ PresentedMaskState p r A B hp :=
  FiniteModulePresentation.transport (reachableMaskPresentation p r A B hp) (reachableMaskTransition p r A B hp d)

def presentedMaskIterate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    List (Fin p) → PresentedMaskState p r A B hp → PresentedMaskState p r A B hp :=
  FiniteModulePresentation.run (reachableMaskPresentation p r A B hp) (reachableStateSystem p r A B hp)

def presentedMaskDecode (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    PresentedMaskState p r A B hp ≃+ ReachableMaskState p r A B hp :=
  (reachableMaskPresentation p r A B hp).equiv.symm

@[simp] theorem presentedMask_initial_decode (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    presentedMaskDecode p r A B hp (presentedMaskInitial p r A B hp) = reachableMaskInitial p r A B hp :=
  (reachableMaskPresentation p r A B hp).equiv.symm_apply_apply _

theorem presentedMask_transition_decode (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : Fin p) (x : PresentedMaskState p r A B hp) :
    presentedMaskDecode p r A B hp (presentedMaskTransition p r A B hp d x) =
      reachableMaskTransition p r A B hp d (presentedMaskDecode p r A B hp x) :=
  FiniteModulePresentation.transport_decode _ _ _

theorem presentedMask_iterate_decode (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : PresentedMaskState p r A B hp) :
    presentedMaskDecode p r A B hp (presentedMaskIterate p r A B hp ds x) =
      reachableMaskIterate p r A B hp ds (presentedMaskDecode p r A B hp x) := by
  exact (FiniteModulePresentation.run_decode _ _ ds x).trans (reachableStateSystem_run p r A B hp ds _)

def presentedMaskOutput (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x : PresentedMaskState p r A B hp) : ZMod (p^r) :=
  reachableMaskOutput p r A B hp hr hB (presentedMaskDecode p r A B hp x)

theorem presentedMask_output_eq_reachable (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (ds : List (Fin p)) :
    presentedMaskOutput p r A B hp hr hB
      (presentedMaskIterate p r A B hp ds (presentedMaskInitial p r A B hp)) =
    reachableMaskOutput p r A B hp hr hB
      (reachableMaskIterate p r A B hp ds (reachableMaskInitial p r A B hp)) := by
  unfold presentedMaskOutput
  rw [presentedMask_iterate_decode, presentedMask_initial_decode]

theorem presentedMask_output_canonical_word (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (ds : List (Fin p)) :
    presentedMaskOutput p r A B hp hr hB
      (presentedMaskIterate p r A B hp ds (presentedMaskInitial p r A B hp)) =
      PowerSeries.coeff (cartierWordValue p (ds.map Fin.val)) (canonicalMaskSeries p r A B hp hr hB) := by
  rw [presentedMask_output_eq_reachable]
  exact reachableMask_output_canonical_word p r A B hp hr hB hAB ds

theorem presentedMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    presentedMaskOutput p r A B hp hr hB
      (presentedMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (presentedMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [presentedMask_output_eq_reachable]
  exact reachableMask_output_canonical_coefficient p r A B hp hr hB hAB n

/-- Presentation changes no number of states; it exposes independent cyclic factors. -/
theorem presentedMask_state_card_eq (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (PresentedMaskState p r A B hp) = Nat.card (ReachableMaskState p r A B hp) :=
  Nat.card_congr (presentedMaskDecode p r A B hp).toEquiv

theorem presentedMask_state_card (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Nat.card (PresentedMaskState p r A B hp) =
      p^(∑ i, (reachableMaskPresentation p r A B hp).exponent i) := by
  rw [presentedMask_state_card_eq]
  exact FiniteModulePresentation.card hp.pos _

theorem presentedMask_exponent_sum_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    (∑ i, (reachableMaskPresentation p r A B hp).exponent i) ≤ reachableMaskRounds p r A B hp := by
  have h := (reachableMask_state_card_power p r A B hp).2
  rw [FiniteModulePresentation.card hp.pos (reachableMaskPresentation p r A B hp), Nat.log_pow hp.one_lt] at h
  exact h

/-- Intrinsic invariant factors, despite the noncanonical chosen equivalence. -/
def reachableMaskSignature (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : Multiset ℕ :=
  FiniteModulePresentation.signature (reachableMaskPresentation p r A B hp)

theorem reachableMaskSignature_unique (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (P : FiniteModulePresentation.Presentation p r (ReachableMaskState p r A B hp)) :
    FiniteModulePresentation.signature P = reachableMaskSignature p r A B hp :=
  FiniteModulePresentation.signature_unique hp.one_lt P _

/-- Each factor multiplicity can be read without choosing any module basis. -/
theorem reachableMaskSignature_multiplicity (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (k : ℕ) (hk : 0 < k) :
    (reachableMaskSignature p r A B hp).count k =
      FiniteModulePresentation.intrinsicMultiplicity p k (ReachableMaskState p r A B hp) := by
  rw [reachableMaskSignature, FiniteModulePresentation.signature_count]
  exact (FiniteModulePresentation.multiplicity_eq_count hp.one_lt _ k hk).symm

theorem presentedMask_output_precision_compatible (p r s : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hs : 0 < s) (hsr : s ≤ r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    ZMod.castHom (pow_dvd_pow p hsr) (ZMod (p^s))
      (presentedMaskOutput p r A B hp hr hB
        (presentedMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (presentedMaskInitial p r A B hp))) =
    presentedMaskOutput p s A B hp hs hB
      (presentedMaskIterate p s A B hp (finiteMaskDigitWord p n hp) (presentedMaskInitial p s A B hp)) := by
  rw [presentedMask_output_eq_reachable, presentedMask_output_eq_reachable]
  exact reachableMask_output_precision_compatible p r s A B hp hr hs hsr hB hAB n

structure PresentedCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  predecessor : ReachableCanonicalMaskCertificate p r A B hp hr hB
  signature_unique : ∀ P : FiniteModulePresentation.Presentation p r (ReachableMaskState p r A B hp),
    FiniteModulePresentation.signature P = reachableMaskSignature p r A B hp
  coordinate_count : Nat.card (PresentedMaskState p r A B hp) = Nat.card (ReachableMaskState p r A B hp)
  output : ∀ n, presentedMaskOutput p r A B hp hr hB
    (presentedMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (presentedMaskInitial p r A B hp)) =
    PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)

def presentedCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    PresentedCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := reachableCanonicalMaskCertificate p r A B hp hr hB hAB
  signature_unique := reachableMaskSignature_unique p r A B hp
  coordinate_count := presentedMask_state_card_eq p r A B hp
  output := presentedMask_output_canonical_coefficient p r A B hp hr hB hAB

end
end KomorebiPadic
