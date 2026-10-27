import KomorebiPadic.ObservabilityExamples
open KomorebiPadic KomorebiPadic.LinearObservability
noncomputable section

example : Nat.card (unobservable twiceIdentity) = 2 := twiceIdentity_kernel_card
example : Nat.card (State twiceIdentity) = 2 := twiceIdentity_quotient_card
example : LinearReachability.reachable twiceIdentity.dynamics = ⊤ := twiceIdentity_reachable
example : unobservable swapObserver = ⊥ := swapObserver_unobservable_bot
example : unobservable emptyAlphabet = ⊥ := emptyAlphabet_unobservable_bot
example : projection twiceIdentity 0 = projection twiceIdentity 2 := twiceIdentity_distinct_states_merge.2.1
example : projection twiceIdentity 0 ≠ projection twiceIdentity 1 := twiceIdentity_distinct_states_merge.2.2
example : (0 : ZMod 4) ∈ unobservable twiceIdentity := (unobservable twiceIdentity).zero_mem
example : (2 : ZMod 4) ∈ unobservable twiceIdentity := by rw [twiceIdentity_unobservable_mem]; decide +kernel
example : (1 : ZMod 4) ∉ unobservable twiceIdentity := by rw [twiceIdentity_unobservable_mem]; decide +kernel
example : (3 : ZMod 4) ∉ unobservable twiceIdentity := by rw [twiceIdentity_unobservable_mem]; decide +kernel
example : swapObserver.output ![0,1] = swapObserver.output 0 := immediate_output_not_future_equivalence.1
example : projection swapObserver ![0,1] ≠ projection swapObserver 0 := immediate_output_not_future_equivalence.2
example : observation swapObserver [] ![0,1] = 0 := rfl
example : observation swapObserver [()] ![0,1] = 1 := rfl
example : iterate swapObserver 0 = ⊤ := rfl
example : iterate swapObserver 2 = unobservable swapObserver :=
  iterate_eq_unobservable _ (by decide : Nat.Prime 5) (by simp)
example : iterate twiceIdentity 2 = unobservable twiceIdentity :=
  iterate_eq_unobservable _ (by decide : Nat.Prime 2) (by simp)
example : (unobservable (quotientSystem twiceIdentity)) = ⊥ := quotient_unobservable_eq_bot _
example : LinearReachability.reachable (quotientSystem twiceIdentity).dynamics = ⊤ :=
  quotient_reachable _ twiceIdentity_reachable

variable {R V A : Type*} [CommRing R] [AddCommGroup V] [Module R V]
example (M : System R V A) (x y : V) :
    projection M x = projection M y ↔ ∀ w, observation M w x = observation M w y := projection_eq_iff M x y
example [Finite V] (M : System R V A) {p b : ℕ} (hp : p.Prime) (hV : Nat.card V = p^b) :
    iterate M b = unobservable M := iterate_eq_unobservable M hp hV
example (M : System R V A) (U : Submodule R V) (hU : SilentInvariant M U) :
    Function.Surjective (quotientFactor M U hU) := quotientFactor_surjective M U hU
example (M : System R V A) (x y : State M)
    (h : ∀ w, observation (quotientSystem M) w x = observation (quotientSystem M) w y) : x = y :=
  quotient_observable M x y h
example (M : System R V A) (n : ℕ) (x : V) :
    x ∈ iterate M n ↔ ∀ w, w.length < n → observation M w x = 0 := mem_iterate_iff M n x
example (p r : ℕ) (P Q : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hQ : ¬ (p : ℤ) ∣ Q.coeff 0) (hPQ : MaskConstantsAgree p r P Q) :
    ObservableCanonicalMaskCertificate p r P Q hp hr hQ :=
  observableCanonicalMaskCertificate p r P Q hp hr hQ hPQ
example (p r : ℕ) (P Q : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hQ : ¬ (p : ℤ) ∣ Q.coeff 0) (hPQ : MaskConstantsAgree p r P Q) (n : ℕ) :
    observableMaskOutput p r P Q hp hr hQ
      (observableMaskIterate p r P Q hp hr hQ (finiteMaskDigitWord p n hp) (observableMaskInitial p r P Q hp hr hQ)) =
      PowerSeries.coeff n (canonicalMaskSeries p r P Q hp hr hQ) :=
  observableMask_output_canonical_coefficient p r P Q hp hr hQ hPQ n
example (p r : ℕ) (P Q : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hQ : ¬ (p : ℤ) ∣ Q.coeff 0) :
    FiniteModulePresentation.Presentation p r (ObservableMaskState p r P Q hp hr hQ) :=
  observableMaskPresentation p r P Q hp hr hQ
end
