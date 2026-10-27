import AVOC.StochasticBlackwell

namespace Komorebi.AVOC

universe u v w

/-- A strong stochastic control-sufficiency condition. States merged by `φ`
have identical immediate rewards and identical raw-state transition rows for
every admissible action. This is stronger than quotient lumpability, but gives a
clean first stochastic preservation theorem. -/
def StrongStochasticControlSufficient
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} (φ : S → Z) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t →
    ∀ a ∈ sys.actions,
      sys.reward s a = sys.reward t a ∧
      ∀ s', sys.transitionProb s a s' = sys.transitionProb t a s'

/-- Under strong stochastic control sufficiency, one-step expected continuation
values agree on every representation fiber for every admissible action. -/
theorem expectedContinuation_eq_of_strongSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : StrongStochasticControlSufficient sys φ)
    {s t : S} (hst : φ s = φ t)
    (V : S → ℚ) {a : A} (ha : a ∈ sys.actions) :
    expectedContinuation sys V s a = expectedContinuation sys V t a := by
  rcases h hst a ha with ⟨hr, hp⟩
  unfold expectedContinuation
  apply Finset.sum_congr rfl
  intro s' hs'
  rw [hp s']

/-- Bellman action values agree on fibers under strong stochastic control
sufficiency. -/
theorem stochasticQValue_eq_of_strongSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : StrongStochasticControlSufficient sys φ)
    (n : ℕ) {s t : S} (hst : φ s = φ t)
    {a : A} (ha : a ∈ sys.actions) :
    stochasticQValue sys n s a = stochasticQValue sys n t a := by
  unfold stochasticQValue
  rcases h hst a ha with ⟨hr, hp⟩
  rw [hr]
  congr 1
  unfold expectedContinuation
  apply Finset.sum_congr rfl
  intro s' hs'
  rw [hp s']

/-- Strong stochastic control sufficiency preserves optimal finite-horizon value
exactly on every representation fiber. -/
theorem stochasticHorizonValue_eq_of_strongSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : StrongStochasticControlSufficient sys φ) :
    ∀ n {s t : S}, φ s = φ t →
      stochasticHorizonValue sys n s = stochasticHorizonValue sys n t := by
  intro n
  induction n with
  | zero =>
      intro s t hst
      rfl
  | succ n ih =>
      intro s t hst
      rw [stochasticHorizonValue_succ_eq_max, stochasticHorizonValue_succ_eq_max]
      congr 1
      ext q
      simp only [Finset.mem_image]
      constructor
      · rintro ⟨a, ha, rfl⟩
        refine ⟨a, ha, ?_⟩
        exact (stochasticQValue_eq_of_strongSuff sys h n hst ha).symm
      · rintro ⟨a, ha, rfl⟩
        refine ⟨a, ha, ?_⟩
        exact stochasticQValue_eq_of_strongSuff sys h n hst ha

/-- Bellman optimality of an admissible action is invariant across a strong
stochastic-sufficiency fiber. -/
def StochasticBellmanOptimalAt
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (n : ℕ) (s : S) (a : A) : Prop :=
  a ∈ sys.actions ∧ ∀ b ∈ sys.actions,
    stochasticQValue sys n s b ≤ stochasticQValue sys n s a

/-- Exact preservation of optimal action status across a strongly sufficient
stochastic representation fiber. -/
theorem stochasticBellmanOptimalAt_iff_of_strongSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : StrongStochasticControlSufficient sys φ)
    (n : ℕ) {s t : S} (hst : φ s = φ t) (a : A) :
    StochasticBellmanOptimalAt sys n s a ↔
      StochasticBellmanOptimalAt sys n t a := by
  constructor
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [← stochasticQValue_eq_of_strongSuff sys h n hst hb]
    rw [← stochasticQValue_eq_of_strongSuff sys h n hst ha]
    exact hmax b hb
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [stochasticQValue_eq_of_strongSuff sys h n hst hb]
    rw [stochasticQValue_eq_of_strongSuff sys h n hst ha]
    exact hmax b hb

end Komorebi.AVOC
