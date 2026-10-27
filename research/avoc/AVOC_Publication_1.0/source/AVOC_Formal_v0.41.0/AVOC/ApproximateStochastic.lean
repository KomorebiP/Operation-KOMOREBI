import AVOC.StochasticQuotient
import Mathlib.Algebra.Order.Ring.Abs
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC

universe u v w

/-- Deterministic pushforward of a finite signed/rational row through `φ`. -/
def pushforwardRow
    {S : Type u} {Z : Type w} [Fintype S] [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (p : S → ℚ) (z : Z) : ℚ :=
  ∑ s ∈ Finset.univ.filter (fun s : S => φ s = z), p s

/-- L1 distance between two finite rational rows. -/
def l1RowDistance
    {Z : Type w} [Fintype Z] (p q : Z → ℚ) : ℚ :=
  ∑ z, |p z - q z|

theorem l1RowDistance_nonneg
    {Z : Type w} [Fintype Z] (p q : Z → ℚ) :
    0 ≤ l1RowDistance p q := by
  unfold l1RowDistance
  exact Finset.sum_nonneg (fun _ _ => abs_nonneg _)

theorem l1RowDistance_self
    {Z : Type w} [Fintype Z] (p : Z → ℚ) :
    l1RowDistance p p = 0 := by
  simp [l1RowDistance]

theorem l1RowDistance_symm
    {Z : Type w} [Fintype Z] (p q : Z → ℚ) :
    l1RowDistance p q = l1RowDistance q p := by
  unfold l1RowDistance
  apply Finset.sum_congr rfl
  intro z hz
  rw [abs_sub_comm]

theorem l1RowDistance_triangle
    {Z : Type w} [Fintype Z] (p q r : Z → ℚ) :
    l1RowDistance p r ≤ l1RowDistance p q + l1RowDistance q r := by
  unfold l1RowDistance
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro z hz
  have hident : p z - r z = (p z - q z) + (q z - r z) := by ring
  rw [hident]
  exact abs_add_le _ _

/-- Grouping a weighted raw sum by representation fibers. -/
theorem sum_pushforward_mul
    {S : Type u} {Z : Type w} [Fintype S] [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (p : S → ℚ) (V : Z → ℚ) :
    (∑ z : Z, pushforwardRow φ p z * V z) =
      ∑ s : S, p s * V (φ s) := by
  unfold pushforwardRow
  have hfiber := Finset.sum_fiberwise (Finset.univ : Finset S) φ
    (fun s => p s * V (φ s))
  rw [← hfiber]
  apply Finset.sum_congr rfl
  intro z hz
  rw [Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro s hs
  have hφ : φ s = z := (Finset.mem_filter.mp hs).2
  rw [hφ]

/-- Absolute expectation is bounded by a uniform bound on the value function. -/
theorem expectedContinuation_abs_le
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (V : S → ℚ) (B : ℚ)
    (hV : ∀ s, |V s| ≤ B) (s : S) (a : A) :
    |expectedContinuation sys V s a| ≤ B := by
  unfold expectedContinuation
  calc
    |∑ s' : S, sys.transitionProb s a s' * V s'|
        ≤ ∑ s' : S, |sys.transitionProb s a s' * V s'| := by
            simpa using Finset.abs_sum_le_sum_abs
              (fun s' : S => sys.transitionProb s a s' * V s') Finset.univ
    _ = ∑ s' : S, sys.transitionProb s a s' * |V s'| := by
          apply Finset.sum_congr rfl
          intro s' hs'
          rw [abs_mul, abs_of_nonneg (sys.transition_nonneg s a s')]
    _ ≤ ∑ s' : S, sys.transitionProb s a s' * B := by
          apply Finset.sum_le_sum
          intro s' hs'
          exact mul_le_mul_of_nonneg_left (hV s') (sys.transition_nonneg s a s')
    _ = B := by
          rw [← Finset.sum_mul, sys.transition_sum_one]
          simp

/-- L1 row error controls expectation error against a uniformly bounded test. -/
theorem weighted_sum_difference_le_l1
    {Z : Type w} [Fintype Z]
    (p q V : Z → ℚ) (B : ℚ)
    (hV : ∀ z, |V z| ≤ B) :
    |(∑ z, p z * V z) - ∑ z, q z * V z| ≤
      l1RowDistance p q * B := by
  have hident : (∑ x : Z, p x * V x) - (∑ x : Z, q x * V x) =
      ∑ x : Z, (p x - q x) * V x := by
    rw [← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro x hx
    ring
  rw [hident]
  calc
    |∑ z : Z, (p z - q z) * V z|
        ≤ ∑ z : Z, |(p z - q z) * V z| := by
            simpa using Finset.abs_sum_le_sum_abs
              (fun z : Z => (p z - q z) * V z) Finset.univ
    _ = ∑ z : Z, |p z - q z| * |V z| := by
          apply Finset.sum_congr rfl
          intro z hz
          rw [abs_mul]
    _ ≤ ∑ z : Z, |p z - q z| * B := by
          apply Finset.sum_le_sum
          intro z hz
          exact mul_le_mul_of_nonneg_left (hV z) (abs_nonneg _)
    _ = l1RowDistance p q * B := by
          rw [← Finset.sum_mul]
          rfl

/-- Approximate stochastic abstraction with explicit reward and projected-row
L1 distortion and a uniform abstract reward envelope. -/
structure ApproximateStochasticAbstraction
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ) : Prop where
  eps_nonneg : 0 ≤ ε
  delta_nonneg : 0 ≤ δ
  reward_bound_nonneg : 0 ≤ R
  actions_eq : raw.actions = absSys.actions
  reward_close : ∀ s a, a ∈ raw.actions →
    |raw.reward s a - absSys.reward (φ s) a| ≤ ε
  transition_close : ∀ s a, a ∈ raw.actions →
    l1RowDistance (pushforwardRow φ (raw.transitionProb s a))
      (absSys.transitionProb (φ s) a) ≤ δ
  abstract_reward_bounded : ∀ z a, a ∈ absSys.actions →
    |absSys.reward z a| ≤ R

/-- Abstract finite-horizon values grow by at most `n * R`. -/
theorem abstract_horizon_value_abs_le
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R) :
    ∀ n z, |stochasticHorizonValue absSys n z| ≤ (n : ℚ) * R := by
  intro n
  induction n with
  | zero =>
      intro z
      simp [stochasticHorizonValue]
  | succ n ih =>
      intro z
      obtain ⟨a, ha, hval⟩ := stochastic_finite_horizon_optimal_action_exists absSys n z
      rw [hval]
      unfold stochasticQValue
      have hr := h.abstract_reward_bounded z a ha
      have he := expectedContinuation_abs_le absSys
        (stochasticHorizonValue absSys n) ((n : ℚ) * R) ih z a
      calc
        |absSys.reward z a + expectedContinuation absSys (stochasticHorizonValue absSys n) z a|
            ≤ |absSys.reward z a| +
              |expectedContinuation absSys (stochasticHorizonValue absSys n) z a| := abs_add_le _ _
        _ ≤ R + (n : ℚ) * R := add_le_add hr he
        _ = ((n + 1 : ℕ) : ℚ) * R := by
              push_cast
              ring

/-- Raw expectation of an abstract continuation, grouped by `φ`, differs from
abstract expectation by at most `δ * B`. -/
theorem projected_expectation_error_le
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (V : Z → ℚ) (B : ℚ) (hB : 0 ≤ B)
    (hV : ∀ z, |V z| ≤ B)
    (s : S) {a : A} (ha : a ∈ raw.actions) :
    |(∑ s' : S, raw.transitionProb s a s' * V (φ s')) -
      expectedContinuation absSys V (φ s) a| ≤ δ * B := by
  rw [← sum_pushforward_mul φ (raw.transitionProb s a) V]
  unfold expectedContinuation
  exact le_trans
    (weighted_sum_difference_le_l1
      (pushforwardRow φ (raw.transitionProb s a))
      (absSys.transitionProb (φ s) a) V B hV)
    (mul_le_mul_of_nonneg_right (h.transition_close s a ha) hB)

/-- If linked raw/abstract continuations differ uniformly by `D`, then their
one-step expectations differ by at most `D + δ*B`. -/
theorem linked_expectation_error_le
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R D B : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (Vr : S → ℚ) (Va : Z → ℚ)
    (hB : 0 ≤ B)
    (hlink : ∀ s, |Vr s - Va (φ s)| ≤ D)
    (hVa : ∀ z, |Va z| ≤ B)
    (s : S) {a : A} (ha : a ∈ raw.actions) :
    |expectedContinuation raw Vr s a -
      expectedContinuation absSys Va (φ s) a| ≤ D + δ * B := by
  let diff : S → ℚ := fun x => Vr x - Va (φ x)
  have hdiff : ∀ x, |diff x| ≤ D := hlink
  have hraw :
      |expectedContinuation raw diff s a| ≤ D :=
    expectedContinuation_abs_le raw diff D hdiff s a
  have hproj := projected_expectation_error_le raw absSys φ ε δ R h
    Va B hB hVa s ha
  have hdecomp :
      expectedContinuation raw Vr s a - expectedContinuation absSys Va (φ s) a =
        expectedContinuation raw diff s a +
          ((∑ x : S, raw.transitionProb s a x * Va (φ x)) -
            expectedContinuation absSys Va (φ s) a) := by
    unfold expectedContinuation diff
    simp only [mul_sub]
    rw [Finset.sum_sub_distrib]
    ring
  rw [hdecomp]
  exact le_trans (abs_add_le _ _) (add_le_add hraw hproj)

/-- Recursive approximation budget. -/
def approxBudget (ε δ R : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => approxBudget ε δ R n + ε + δ * (n : ℚ) * R

theorem approxBudget_nonneg
    {ε δ R : ℚ} (hε : 0 ≤ ε) (hδ : 0 ≤ δ) (hR : 0 ≤ R) :
    ∀ n, 0 ≤ approxBudget ε δ R n := by
  intro n
  induction n with
  | zero => simp [approxBudget]
  | succ n ih =>
      simp only [approxBudget]
      positivity

/-- The intermediate horizon-sum identity used by the closed form. -/
theorem sum_range_cast_eq_triangular (n : ℕ) :
    (∑ k ∈ Finset.range n, (k : ℚ)) =
      (n : ℚ) * ((n : ℚ) - 1) / 2 := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Finset.sum_range_succ]
      rw [ih]
      push_cast
      ring

/-- Closed form of the recursive approximation budget. -/
theorem approxBudget_closed_form (ε δ R : ℚ) (n : ℕ) :
    approxBudget ε δ R n =
      (n : ℚ) * ε + δ * R * ((n : ℚ) * ((n : ℚ) - 1) / 2) := by
  induction n with
  | zero => simp [approxBudget]
  | succ n ih =>
      simp only [approxBudget, ih]
      push_cast
      ring

/-- Per-action Q-value distortion recurrence. -/
theorem stochastic_qValue_error_le
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (n : ℕ)
    (hprev : ∀ s, |stochasticHorizonValue raw n s -
      stochasticHorizonValue absSys n (φ s)| ≤ approxBudget ε δ R n)
    (s : S) {a : A} (ha : a ∈ raw.actions) :
    |stochasticQValue raw n s a - stochasticQValue absSys n (φ s) a| ≤
      approxBudget ε δ R (n + 1) := by
  have hE := linked_expectation_error_le raw absSys φ ε δ R
    (approxBudget ε δ R n) ((n : ℚ) * R) h
    (stochasticHorizonValue raw n)
    (stochasticHorizonValue absSys n)
    (mul_nonneg (Nat.cast_nonneg n) h.reward_bound_nonneg)
    hprev (abstract_horizon_value_abs_le raw absSys φ ε δ R h n) s ha
  have hr := h.reward_close s a ha
  have hdecomp :
      stochasticQValue raw n s a - stochasticQValue absSys n (φ s) a =
        (raw.reward s a - absSys.reward (φ s) a) +
        (expectedContinuation raw (stochasticHorizonValue raw n) s a -
          expectedContinuation absSys (stochasticHorizonValue absSys n) (φ s) a) := by
    unfold stochasticQValue
    ring
  rw [hdecomp]
  calc
    |(raw.reward s a - absSys.reward (φ s) a) +
      (expectedContinuation raw (stochasticHorizonValue raw n) s a -
        expectedContinuation absSys (stochasticHorizonValue absSys n) (φ s) a)|
      ≤ |raw.reward s a - absSys.reward (φ s) a| +
        |expectedContinuation raw (stochasticHorizonValue raw n) s a -
          expectedContinuation absSys (stochasticHorizonValue absSys n) (φ s) a| := abs_add_le _ _
    _ ≤ ε + (approxBudget ε δ R n + δ * (n : ℚ) * R) := by
          apply add_le_add hr
          simpa [mul_assoc] using hE
    _ = approxBudget ε δ R (n + 1) := by
          simp only [approxBudget]
          ring

/-- Uniform Q-value closeness implies closeness of the corresponding maxima
when both systems optimize over the same action set. -/
theorem stochastic_value_error_of_q_error
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z)
    (n : ℕ) (s : S) (D : ℚ)
    (hactions : raw.actions = absSys.actions)
    (hq : ∀ a ∈ raw.actions,
      |stochasticQValue raw n s a - stochasticQValue absSys n (φ s) a| ≤ D) :
    |stochasticHorizonValue raw (n + 1) s -
      stochasticHorizonValue absSys (n + 1) (φ s)| ≤ D := by
  obtain ⟨ar, har, hrval⟩ := stochastic_finite_horizon_optimal_action_exists raw n s
  obtain ⟨aa, haa_abs, haval⟩ := stochastic_finite_horizon_optimal_action_exists absSys n (φ s)
  have haa : aa ∈ raw.actions := by simpa [hactions] using haa_abs
  have har_abs : ar ∈ absSys.actions := by simpa [← hactions] using har
  have hq_r := hq ar har
  have hq_a := hq aa haa
  have habs_ge_r : stochasticQValue absSys n (φ s) ar ≤
      stochasticHorizonValue absSys (n + 1) (φ s) := by
    rw [stochasticHorizonValue_succ_eq_max]
    apply Finset.le_max'
    exact Finset.mem_image.mpr ⟨ar, har_abs, rfl⟩
  have hraw_ge_a : stochasticQValue raw n s aa ≤
      stochasticHorizonValue raw (n + 1) s := by
    rw [stochasticHorizonValue_succ_eq_max]
    apply Finset.le_max'
    exact Finset.mem_image.mpr ⟨aa, haa, rfl⟩
  have hup : stochasticHorizonValue raw (n + 1) s -
      stochasticHorizonValue absSys (n + 1) (φ s) ≤ D := by
    rw [hrval]
    have hqr_upper : stochasticQValue raw n s ar -
        stochasticQValue absSys n (φ s) ar ≤ D := (abs_le.mp hq_r).2
    linarith
  have hdown : -(D) ≤ stochasticHorizonValue raw (n + 1) s -
      stochasticHorizonValue absSys (n + 1) (φ s) := by
    rw [haval]
    have hqa_lower : -D ≤ stochasticQValue raw n s aa -
        stochasticQValue absSys n (φ s) aa := (abs_le.mp hq_a).1
    linarith
  exact abs_le.mpr ⟨hdown, hup⟩

/-- Main approximate stochastic control theorem. -/
theorem approximate_stochastic_horizon_value_bound
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R) :
    ∀ n s,
      |stochasticHorizonValue raw n s -
        stochasticHorizonValue absSys n (φ s)| ≤ approxBudget ε δ R n := by
  intro n
  induction n with
  | zero =>
      intro s
      simp [stochasticHorizonValue, approxBudget]
  | succ n ih =>
      intro s
      apply stochastic_value_error_of_q_error raw absSys φ n s
        (approxBudget ε δ R (n + 1))
        h.actions_eq
      intro a ha
      exact stochastic_qValue_error_le raw absSys φ ε δ R h n ih s ha

/-- Closed-form finite-horizon approximation theorem. -/
theorem approximate_stochastic_horizon_value_bound_closed
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (n : ℕ) (s : S) :
    |stochasticHorizonValue raw n s - stochasticHorizonValue absSys n (φ s)| ≤
      (n : ℚ) * ε + δ * R * ((n : ℚ) * ((n : ℚ) - 1) / 2) := by
  rw [← approxBudget_closed_form ε δ R n]
  exact approximate_stochastic_horizon_value_bound raw absSys φ ε δ R h n s

/-- A closed-form certificate for `η`-value-sufficiency through horizon `n`. -/
theorem approximate_value_sufficient_of_budget
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R η : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (n : ℕ)
    (hη : (n : ℚ) * ε + δ * R * ((n : ℚ) * ((n : ℚ) - 1) / 2) ≤ η) :
    ∀ s, |stochasticHorizonValue raw n s -
      stochasticHorizonValue absSys n (φ s)| ≤ η := by
  intro s
  exact le_trans
    (approximate_stochastic_horizon_value_bound_closed raw absSys φ ε δ R h n s) hη

/-- An action optimal in the abstract controller is `2D`-optimal in the raw
controller, where `D` is the next-horizon approximation budget. -/
theorem abstract_optimal_action_raw_regret_le
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (n : ℕ) (s : S) (a : A)
    (haopt : StochasticBellmanOptimalAt absSys n (φ s) a) :
    stochasticHorizonValue raw (n + 1) s - stochasticQValue raw n s a ≤
      2 * approxBudget ε δ R (n + 1) := by
  rcases haopt with ⟨ha_abs, hmax⟩
  have ha_raw : a ∈ raw.actions := by simpa [h.actions_eq] using ha_abs
  have hV := approximate_stochastic_horizon_value_bound raw absSys φ ε δ R h (n + 1) s
  have hQ := stochastic_qValue_error_le raw absSys φ ε δ R h n
    (approximate_stochastic_horizon_value_bound raw absSys φ ε δ R h n) s ha_raw
  have habsval := stochasticHorizonValue_eq_qValue_of_optimal absSys n (φ s) a ha_abs hmax
  have hVupper : stochasticHorizonValue raw (n + 1) s -
      stochasticHorizonValue absSys (n + 1) (φ s) ≤ approxBudget ε δ R (n + 1) :=
    (abs_le.mp hV).2
  have hQlower : -approxBudget ε δ R (n + 1) ≤
      stochasticQValue raw n s a - stochasticQValue absSys n (φ s) a :=
    (abs_le.mp hQ).1
  rw [habsval] at hVupper
  linarith

end Komorebi.AVOC
