import KomorebiPadic.CanonicalLinearRealization

/-! # A finite certificate for equality of two complete word behaviors
The observation horizon is the sum of cardinality exponents, not dimensions.
Both initial and future empty words are included by the strict length convention.
-/
namespace KomorebiPadic
namespace ResidualRealization
variable {R V W A : Type*} [CommRing R]
variable [AddCommGroup V] [Module R V] [AddCommGroup W] [Module R W]
noncomputable section

def differenceSystem (M : LinearObservability.System R V A) (N : LinearObservability.System R W A) :
    LinearObservability.System R (V × W) A where
  dynamics := ⟨(M.dynamics.initial,N.dynamics.initial),
    fun d => (M.dynamics.transition d).prodMap (N.dynamics.transition d)⟩
  output := M.output.comp (LinearMap.fst R V W) - N.output.comp (LinearMap.snd R V W)

theorem differenceSystem_run (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (u : List A) (x : V × W) :
    LinearReachability.run (differenceSystem M N).dynamics u x =
      (LinearReachability.run M.dynamics u x.1, LinearReachability.run N.dynamics u x.2) := by
  induction u generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih ((M.dynamics.transition d x.1), (N.dynamics.transition d x.2))

theorem differenceSystem_observation (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (u : List A) (x : V × W) :
    LinearObservability.observation (differenceSystem M N) u x =
      LinearObservability.observation M u x.1 - LinearObservability.observation N u x.2 := by
  simp only [LinearObservability.observation, LinearMap.comp_apply, LinearObservability.wordMap_apply]
  rw [differenceSystem_run]
  rfl

/-- Equality on words shorter than b+c certifies equality on every word. -/
theorem behavior_eq_iff_finite_words [Finite V] [Finite W]
    (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    {p b c : ℕ} (hp : p.Prime) (hV : Nat.card V = p^b) (hW : Nat.card W = p^c) :
    behavior M = behavior N ↔ ∀ u : List A, u.length < b+c → behavior M u = behavior N u := by
  have hprod : Nat.card (V × W) = p^(b+c) := by rw [Nat.card_prod, hV, hW, pow_add]
  constructor
  · intro h u _
    exact congrFun h u
  · intro ht
    have hzero : (M.dynamics.initial,N.dynamics.initial) ∈
        LinearObservability.unobservable (differenceSystem M N) := by
      apply (LinearObservability.unobservable_iff_finite_words _ hp hprod _).mpr
      intro u hu
      rw [differenceSystem_observation]
      exact sub_eq_zero.mpr (ht u hu)
    funext u
    have hz := (LinearObservability.mem_unobservable _ _).mp hzero u
    rw [differenceSystem_observation] at hz
    exact sub_eq_zero.mp hz

theorem exists_short_behavior_difference [Finite V] [Finite W]
    (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    {p b c : ℕ} (hp : p.Prime) (hV : Nat.card V = p^b) (hW : Nat.card W = p^c)
    (hne : behavior M ≠ behavior N) :
    ∃ u : List A, u.length < b+c ∧ behavior M u ≠ behavior N u := by
  classical
  by_contra hn
  push Not at hn
  exact hne ((behavior_eq_iff_finite_words M N hp hV hW).mpr hn)

end
end ResidualRealization
end KomorebiPadic
