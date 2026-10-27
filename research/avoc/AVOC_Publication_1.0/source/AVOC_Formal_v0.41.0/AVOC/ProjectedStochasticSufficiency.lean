import AVOC.StochasticSufficiency
import Mathlib.Algebra.Order.BigOperators.Group.Finset

namespace Komorebi.AVOC

universe u v w

/-- A value function is fiber-constant when it depends only on the compressed
representation `φ`. -/
def FiberConstant
    {S : Type u} {Z : Type w} (φ : S → Z) (V : S → ℚ) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t → V s = V t

/-- Two transition rows have the same projected law through `φ` exactly for the
purposes of dynamic programming when they give equal expectation to every
fiber-constant continuation value. -/
def ProjectedTransitionEquivalent
    {S : Type u} [Fintype S] {Z : Type w}
    (φ : S → Z) (p q : S → ℚ) : Prop :=
  ∀ V : S → ℚ, FiberConstant φ V →
    (∑ s, p s * V s) = ∑ s, q s * V s

/-- Reflexivity of projected transition equivalence. -/
theorem projectedTransitionEquivalent_refl
    {S : Type u} [Fintype S] {Z : Type w}
    (φ : S → Z) (p : S → ℚ) :
    ProjectedTransitionEquivalent φ p p := by
  intro V hV
  rfl

/-- Symmetry of projected transition equivalence. -/
theorem projectedTransitionEquivalent_symm
    {S : Type u} [Fintype S] {Z : Type w}
    {φ : S → Z} {p q : S → ℚ}
    (h : ProjectedTransitionEquivalent φ p q) :
    ProjectedTransitionEquivalent φ q p := by
  intro V hV
  exact (h V hV).symm

/-- Transitivity of projected transition equivalence. -/
theorem projectedTransitionEquivalent_trans
    {S : Type u} [Fintype S] {Z : Type w}
    {φ : S → Z} {p q r : S → ℚ}
    (hpq : ProjectedTransitionEquivalent φ p q)
    (hqr : ProjectedTransitionEquivalent φ q r) :
    ProjectedTransitionEquivalent φ p r := by
  intro V hV
  exact (hpq V hV).trans (hqr V hV)

/-- Proper stochastic control sufficiency: merged current states have equal
immediate rewards and transition laws that agree after projection through `φ`.
Unlike `StrongStochasticControlSufficient`, raw next-state probabilities need
not agree pointwise. -/
def ProjectedStochasticControlSufficient
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} (φ : S → Z) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t →
    ∀ a ∈ sys.actions,
      sys.reward s a = sys.reward t a ∧
      ProjectedTransitionEquivalent φ
        (sys.transitionProb s a) (sys.transitionProb t a)

/-- The strong raw-row condition implies the proper projected stochastic
condition. -/
theorem projectedSuff_of_strongSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : StrongStochasticControlSufficient sys φ) :
    ProjectedStochasticControlSufficient sys φ := by
  intro s t hst a ha
  rcases h hst a ha with ⟨hr, hp⟩
  refine ⟨hr, ?_⟩
  intro V hV
  apply Finset.sum_congr rfl
  intro s' hs'
  rw [hp s']

/-- Under projected stochastic control sufficiency, expectations of every
fiber-constant continuation value agree across merged current states. -/
theorem expectedContinuation_eq_of_projectedSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : ProjectedStochasticControlSufficient sys φ)
    {s t : S} (hst : φ s = φ t)
    (V : S → ℚ) (hV : FiberConstant φ V)
    {a : A} (ha : a ∈ sys.actions) :
    expectedContinuation sys V s a = expectedContinuation sys V t a := by
  rcases h hst a ha with ⟨hr, hp⟩
  exact hp V hV

/-- Projected stochastic control sufficiency preserves every finite-horizon
Bellman value exactly on representation fibers. -/
theorem stochasticHorizonValue_eq_of_projectedSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : ProjectedStochasticControlSufficient sys φ) :
    ∀ n, FiberConstant φ (stochasticHorizonValue sys n) := by
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
        unfold stochasticQValue
        rcases h hst a ha with ⟨hr, hp⟩
        rw [hr]
        congr 1
        exact (hp (stochasticHorizonValue sys n) ih).symm
      · rintro ⟨a, ha, rfl⟩
        refine ⟨a, ha, ?_⟩
        unfold stochasticQValue
        rcases h hst a ha with ⟨hr, hp⟩
        rw [hr]
        congr 1
        exact hp (stochasticHorizonValue sys n) ih

/-- Projected sufficiency therefore preserves Bellman action values on fibers. -/
theorem stochasticQValue_eq_of_projectedSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : ProjectedStochasticControlSufficient sys φ)
    (n : ℕ) {s t : S} (hst : φ s = φ t)
    {a : A} (ha : a ∈ sys.actions) :
    stochasticQValue sys n s a = stochasticQValue sys n t a := by
  unfold stochasticQValue
  rcases h hst a ha with ⟨hr, hp⟩
  rw [hr]
  congr 1
  exact hp (stochasticHorizonValue sys n)
    (stochasticHorizonValue_eq_of_projectedSuff sys h n)

/-- Exact optimal-action status is preserved by projected stochastic control
sufficiency. -/
theorem stochasticBellmanOptimalAt_iff_of_projectedSuff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {Z : Type w} {φ : S → Z}
    (h : ProjectedStochasticControlSufficient sys φ)
    (n : ℕ) {s t : S} (hst : φ s = φ t) (a : A) :
    StochasticBellmanOptimalAt sys n s a ↔
      StochasticBellmanOptimalAt sys n t a := by
  constructor
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [← stochasticQValue_eq_of_projectedSuff sys h n hst hb]
    rw [← stochasticQValue_eq_of_projectedSuff sys h n hst ha]
    exact hmax b hb
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [stochasticQValue_eq_of_projectedSuff sys h n hst hb]
    rw [stochasticQValue_eq_of_projectedSuff sys h n hst ha]
    exact hmax b hb

/-- Indicator of one representation fiber. -/
def fiberIndicator
    {S : Type u} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (z : Z) : S → ℚ :=
  fun s => if φ s = z then 1 else 0

/-- Fiber indicators are fiber-constant. -/
theorem fiberIndicator_fiberConstant
    {S : Type u} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (z : Z) : FiberConstant φ (fiberIndicator φ z) := by
  intro s t hst
  unfold fiberIndicator
  rw [hst]

/-- Equality of projected transition laws implies equality of probability mass
assigned to every representation fiber. Thus the expectation-based definition
really does imply the familiar finite pushforward-law condition. -/
theorem projectedTransitionEquivalent_implies_fiber_mass_eq
    {S : Type u} [Fintype S]
    {Z : Type w} [DecidableEq Z]
    {φ : S → Z} {p q : S → ℚ}
    (h : ProjectedTransitionEquivalent φ p q) (z : Z) :
    (∑ s ∈ (Finset.univ.filter (fun s => φ s = z)), p s) =
      ∑ s ∈ (Finset.univ.filter (fun s => φ s = z)), q s := by
  have hi := h (fiberIndicator φ z) (fiberIndicator_fiberConstant φ z)
  unfold fiberIndicator at hi
  simpa [Finset.sum_filter] using hi


/-- Familiar finite pushforward-law formulation: two raw transition rows assign
the same total mass to every representation fiber. -/
def FiberMassEqual
    {S : Type u} [Fintype S]
    {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (p q : S → ℚ) : Prop :=
  ∀ z : Z,
    (∑ s ∈ (Finset.univ.filter (fun s => φ s = z)), p s) =
      ∑ s ∈ (Finset.univ.filter (fun s => φ s = z)), q s

/-- A fiber-constant continuation value can be factored out of a nonempty
fiber-weighted sum. -/
theorem fiber_weighted_sum_eq_mass_mul
    {S : Type u} [Fintype S]
    {Z : Type w} [DecidableEq Z]
    {φ : S → Z} {V : S → ℚ} (hV : FiberConstant φ V)
    (p : S → ℚ) (z : Z) {s0 : S}
    (hs0 : s0 ∈ Finset.univ.filter (fun s => φ s = z)) :
    (∑ s ∈ Finset.univ.filter (fun s => φ s = z), p s * V s) =
      (∑ s ∈ Finset.univ.filter (fun s => φ s = z), p s) * V s0 := by
  rw [Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro s hs
  have hφs : φ s = z := (Finset.mem_filter.mp hs).2
  have hφ0 : φ s0 = z := (Finset.mem_filter.mp hs0).2
  have hVs : V s = V s0 := hV (hφs.trans hφ0.symm)
  rw [hVs]

/-- Equality of all fiber masses implies equality of expectations for every
fiber-constant continuation value. This is the converse to the indicator test
above, so in finite spaces the two notions of projected transition equality are
equivalent. -/
theorem fiber_mass_eq_implies_projectedTransitionEquivalent
    {S : Type u} [Fintype S]
    {Z : Type w} [Fintype Z] [DecidableEq Z]
    {φ : S → Z} {p q : S → ℚ}
    (hmass : FiberMassEqual φ p q) :
    ProjectedTransitionEquivalent φ p q := by
  intro V hV
  have hpFiber :
      (∑ z : Z, ∑ s ∈ Finset.univ.filter (fun s => φ s = z), p s * V s) =
        ∑ s : S, p s * V s := by
    simpa using Finset.sum_fiberwise (Finset.univ : Finset S) φ (fun s => p s * V s)
  have hqFiber :
      (∑ z : Z, ∑ s ∈ Finset.univ.filter (fun s => φ s = z), q s * V s) =
        ∑ s : S, q s * V s := by
    simpa using Finset.sum_fiberwise (Finset.univ : Finset S) φ (fun s => q s * V s)
  rw [← hpFiber, ← hqFiber]
  apply Finset.sum_congr rfl
  intro z hz
  let fiber := Finset.univ.filter (fun s : S => φ s = z)
  by_cases hf : fiber.Nonempty
  · obtain ⟨s0, hs0⟩ := hf
    change (∑ s ∈ fiber, p s * V s) = ∑ s ∈ fiber, q s * V s
    rw [fiber_weighted_sum_eq_mass_mul hV p z hs0]
    rw [fiber_weighted_sum_eq_mass_mul hV q z hs0]
    have hm := hmass z
    change (∑ s ∈ fiber, p s) = ∑ s ∈ fiber, q s at hm
    rw [hm]
  · have he : fiber = ∅ := Finset.not_nonempty_iff_eq_empty.mp hf
    change (∑ s ∈ fiber, p s * V s) = ∑ s ∈ fiber, q s * V s
    rw [he]
    simp

/-- Exact finite characterization of projected transition equality by equality
of pushforward mass on every representation fiber. -/
theorem projectedTransitionEquivalent_iff_fiberMassEqual
    {S : Type u} [Fintype S]
    {Z : Type w} [Fintype Z] [DecidableEq Z]
    {φ : S → Z} {p q : S → ℚ} :
    ProjectedTransitionEquivalent φ p q ↔ FiberMassEqual φ p q := by
  constructor
  · intro h z
    exact projectedTransitionEquivalent_implies_fiber_mass_eq h z
  · exact fiber_mass_eq_implies_projectedTransitionEquivalent

end Komorebi.AVOC
