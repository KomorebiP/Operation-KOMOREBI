import AVOC.ProjectedStochasticSufficiency
import Mathlib.Algebra.BigOperators.Ring.Finset

namespace Komorebi.AVOC

universe u v w

/-- Choose a raw representative of each compressed state under a surjective
representation. -/
noncomputable def stochasticRepresentative
    {S : Type u} {Z : Type w} (φ : S → Z) (hsurj : Function.Surjective φ)
    (z : Z) : S :=
  Classical.choose (hsurj z)

/-- The chosen representative really lies in its declared compressed fiber. -/
theorem stochasticRepresentative_spec
    {S : Type u} {Z : Type w} (φ : S → Z) (hsurj : Function.Surjective φ)
    (z : Z) :
    φ (stochasticRepresentative φ hsurj z) = z :=
  Classical.choose_spec (hsurj z)

/-- Quotient/lumped stochastic control system induced by a surjective
representation. Transition probability to compressed state `z'` is the total
raw mass assigned to its fiber by a chosen representative of the current
compressed state. -/
noncomputable def quotientStochasticControlSystem
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (hsurj : Function.Surjective φ) :
    FiniteStochasticControlSystem Z A where
  actions := sys.actions
  actions_nonempty := sys.actions_nonempty
  transitionProb z a z' :=
    ∑ s' ∈ Finset.univ.filter (fun s : S => φ s = z'),
      sys.transitionProb (stochasticRepresentative φ hsurj z) a s'
  transition_nonneg := by
    intro z a z'
    apply Finset.sum_nonneg
    intro s' hs'
    exact sys.transition_nonneg _ _ _
  transition_sum_one := by
    intro z a
    let r := stochasticRepresentative φ hsurj z
    have hfiber :
        (∑ z' : Z,
          ∑ s' ∈ Finset.univ.filter (fun s : S => φ s = z'),
            sys.transitionProb r a s') =
          ∑ s' : S, sys.transitionProb r a s' := by
      simpa using Finset.sum_fiberwise (Finset.univ : Finset S) φ
        (fun s' => sys.transitionProb r a s')
    rw [hfiber]
    exact sys.transition_sum_one r a
  reward z a := sys.reward (stochasticRepresentative φ hsurj z) a

/-- Immediate reward in the quotient agrees with the raw reward at every state
when the representation is projected-stochastically sufficient. -/
theorem quotientStochastic_reward_eq
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (hsurj : Function.Surjective φ)
    (h : ProjectedStochasticControlSufficient sys φ)
    (s : S) {a : A} (ha : a ∈ sys.actions) :
    (quotientStochasticControlSystem sys φ hsurj).reward (φ s) a =
      sys.reward s a := by
  let r := stochasticRepresentative φ hsurj (φ s)
  have hφ : φ r = φ s := stochasticRepresentative_spec φ hsurj (φ s)
  exact (h hφ a ha).1

/-- A raw fiber-constant value function can be reconstructed from its values on
chosen representatives. -/
theorem fiberConstant_eq_representative
    {S : Type u} {Z : Type w}
    (φ : S → Z) (hsurj : Function.Surjective φ)
    {V : S → ℚ} (hV : FiberConstant φ V) (s : S) :
    V s = V (stochasticRepresentative φ hsurj (φ s)) := by
  apply hV
  exact (stochasticRepresentative_spec φ hsurj (φ s)).symm

/-- Grouping a raw expectation by compressed fibers and evaluating the
fiber-constant continuation value at chosen representatives preserves the
expectation exactly. -/
theorem grouped_expectation_eq_raw
    {S : Type u} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (hsurj : Function.Surjective φ)
    (p : S → ℚ) {V : S → ℚ} (hV : FiberConstant φ V) :
    (∑ z : Z,
      (∑ s ∈ Finset.univ.filter (fun s : S => φ s = z), p s) *
        V (stochasticRepresentative φ hsurj z)) =
      ∑ s : S, p s * V s := by
  have hfiber :
      (∑ z : Z,
        ∑ s ∈ Finset.univ.filter (fun s : S => φ s = z), p s * V s) =
        ∑ s : S, p s * V s := by
    simpa using Finset.sum_fiberwise (Finset.univ : Finset S) φ
      (fun s => p s * V s)
  rw [← hfiber]
  apply Finset.sum_congr rfl
  intro z hz
  have hrmem : stochasticRepresentative φ hsurj z ∈
      Finset.univ.filter (fun s : S => φ s = z) := by
    apply Finset.mem_filter.mpr
    exact ⟨Finset.mem_univ _, stochasticRepresentative_spec φ hsurj z⟩
  rw [← fiber_weighted_sum_eq_mass_mul hV p z hrmem]

/-- If quotient and raw continuation values agree through `φ`, then the quotient
expected continuation at `φ s` equals the raw expected continuation at `s`.
Projected stochastic sufficiency is exactly what allows changing the current
raw representative. -/
theorem quotient_expectedContinuation_eq_raw
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (hsurj : Function.Surjective φ)
    (h : ProjectedStochasticControlSufficient sys φ)
    (Vq : Z → ℚ) (Vr : S → ℚ)
    (hlink : ∀ s, Vq (φ s) = Vr s)
    (hVr : FiberConstant φ Vr)
    (s : S) {a : A} (ha : a ∈ sys.actions) :
    expectedContinuation (quotientStochasticControlSystem sys φ hsurj) Vq (φ s) a =
      expectedContinuation sys Vr s a := by
  let r := stochasticRepresentative φ hsurj (φ s)
  have hφr : φ r = φ s := stochasticRepresentative_spec φ hsurj (φ s)
  have hrep : ∀ z : Z, Vq z = Vr (stochasticRepresentative φ hsurj z) := by
    intro z
    have hz := hlink (stochasticRepresentative φ hsurj z)
    rw [stochasticRepresentative_spec φ hsurj z] at hz
    exact hz
  have hgroup :
      (∑ z : Z,
        (∑ s' ∈ Finset.univ.filter (fun s : S => φ s = z),
          sys.transitionProb r a s') * Vq z) =
        ∑ s' : S, sys.transitionProb r a s' * Vr s' := by
    apply Eq.trans ?_ (grouped_expectation_eq_raw φ hsurj (sys.transitionProb r a) hVr)
    apply Finset.sum_congr rfl
    intro z hz
    rw [hrep z]
  unfold expectedContinuation
  change (∑ z : Z,
      (∑ s' ∈ Finset.univ.filter (fun s : S => φ s = z),
        sys.transitionProb r a s') * Vq z) =
    ∑ s' : S, sys.transitionProb s a s' * Vr s'
  rw [hgroup]
  rcases h hφr a ha with ⟨hr, hp⟩
  exact hp Vr hVr

/-- Main stochastic quotient theorem: a surjective projected-stochastically
sufficient representation preserves optimal finite-horizon value exactly. -/
theorem quotientStochasticControlSystem_horizonValue_eq
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (hsurj : Function.Surjective φ)
    (h : ProjectedStochasticControlSufficient sys φ) :
    ∀ n s,
      stochasticHorizonValue (quotientStochasticControlSystem sys φ hsurj) n (φ s) =
        stochasticHorizonValue sys n s := by
  intro n
  induction n with
  | zero =>
      intro s
      rfl
  | succ n ih =>
      intro s
      rw [stochasticHorizonValue_succ_eq_max, stochasticHorizonValue_succ_eq_max]
      congr 1
      ext q
      simp only [Finset.mem_image]
      constructor
      · rintro ⟨a, ha, rfl⟩
        refine ⟨a, ha, ?_⟩
        unfold stochasticQValue
        rw [quotientStochastic_reward_eq sys φ hsurj h s ha]
        congr 1
        exact (quotient_expectedContinuation_eq_raw sys φ hsurj h
          (stochasticHorizonValue (quotientStochasticControlSystem sys φ hsurj) n)
          (stochasticHorizonValue sys n)
          ih
          (stochasticHorizonValue_eq_of_projectedSuff sys h n)
          s ha).symm
      · rintro ⟨a, ha, rfl⟩
        refine ⟨a, ha, ?_⟩
        unfold stochasticQValue
        rw [quotientStochastic_reward_eq sys φ hsurj h s ha]
        congr 1
        exact quotient_expectedContinuation_eq_raw sys φ hsurj h
          (stochasticHorizonValue (quotientStochasticControlSystem sys φ hsurj) n)
          (stochasticHorizonValue sys n)
          ih
          (stochasticHorizonValue_eq_of_projectedSuff sys h n)
          s ha


/-- Quotient and raw stochastic Bellman action values agree exactly for every
admissible action. -/
theorem quotientStochasticControlSystem_qValue_eq
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (hsurj : Function.Surjective φ)
    (h : ProjectedStochasticControlSufficient sys φ)
    (n : ℕ) (s : S) {a : A} (ha : a ∈ sys.actions) :
    stochasticQValue (quotientStochasticControlSystem sys φ hsurj) n (φ s) a =
      stochasticQValue sys n s a := by
  unfold stochasticQValue
  rw [quotientStochastic_reward_eq sys φ hsurj h s ha]
  congr 1
  exact quotient_expectedContinuation_eq_raw sys φ hsurj h
    (stochasticHorizonValue (quotientStochasticControlSystem sys φ hsurj) n)
    (stochasticHorizonValue sys n)
    (quotientStochasticControlSystem_horizonValue_eq sys φ hsurj h n)
    (stochasticHorizonValue_eq_of_projectedSuff sys h n)
    s ha

/-- An action is Bellman-optimal in the stochastic quotient exactly when it is
Bellman-optimal at any raw state represented by that quotient state. -/
theorem quotient_stochasticBellmanOptimalAt_iff
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (hsurj : Function.Surjective φ)
    (h : ProjectedStochasticControlSufficient sys φ)
    (n : ℕ) (s : S) (a : A) :
    StochasticBellmanOptimalAt (quotientStochasticControlSystem sys φ hsurj) n (φ s) a ↔
      StochasticBellmanOptimalAt sys n s a := by
  constructor
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [← quotientStochasticControlSystem_qValue_eq sys φ hsurj h n s hb]
    rw [← quotientStochasticControlSystem_qValue_eq sys φ hsurj h n s ha]
    exact hmax b hb
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [quotientStochasticControlSystem_qValue_eq sys φ hsurj h n s hb]
    rw [quotientStochasticControlSystem_qValue_eq sys φ hsurj h n s ha]
    exact hmax b hb

end Komorebi.AVOC
