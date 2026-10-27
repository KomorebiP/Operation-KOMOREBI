import AVOC.ApproximateStochastic

namespace Komorebi.AVOC

universe u v w x

/-- Deterministic pushforward composes exactly. -/
theorem pushforwardRow_comp
    {S : Type u} {M : Type w} {Z : Type x}
    [Fintype S] [Fintype M] [Fintype Z]
    [DecidableEq M] [DecidableEq Z]
    (φ : S → M) (ψ : M → Z) (p : S → ℚ) (z : Z) :
    pushforwardRow ψ (pushforwardRow φ p) z =
      pushforwardRow (ψ ∘ φ) p z := by
  unfold pushforwardRow
  have h := Finset.sum_fiberwise_eq_sum_filter
    (Finset.univ : Finset S)
    (Finset.univ.filter (fun m : M => ψ m = z)) φ p
  simpa [Function.comp_def, Finset.mem_filter] using h

/-- Deterministic postprocessing cannot increase finite L1 row distance. -/
theorem l1_pushforward_contract
    {S : Type u} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (p q : S → ℚ) :
    l1RowDistance (pushforwardRow φ p) (pushforwardRow φ q) ≤
      l1RowDistance p q := by
  unfold l1RowDistance
  have hpoint : ∀ z : Z,
      |pushforwardRow φ p z - pushforwardRow φ q z| ≤
        ∑ s ∈ Finset.univ.filter (fun s : S => φ s = z), |p s - q s| := by
    intro z
    unfold pushforwardRow
    rw [← Finset.sum_sub_distrib]
    simpa using Finset.abs_sum_le_sum_abs
      (fun s : S => p s - q s)
      (Finset.univ.filter (fun s : S => φ s = z))
  calc
    (∑ z : Z, |pushforwardRow φ p z - pushforwardRow φ q z|)
        ≤ ∑ z : Z, ∑ s ∈ Finset.univ.filter (fun s : S => φ s = z), |p s - q s| := by
          apply Finset.sum_le_sum
          intro z hz
          exact hpoint z
    _ = ∑ s : S, |p s - q s| := by
          simpa using Finset.sum_fiberwise (Finset.univ : Finset S) φ
            (fun s : S => |p s - q s|)

/-- L1 contraction followed by a second approximation gives an additive error. -/
theorem l1_pushforward_triangle
    {S : Type u} {M : Type w} {Z : Type x}
    [Fintype S] [Fintype M] [Fintype Z]
    [DecidableEq M] [DecidableEq Z]
    (φ : S → M) (ψ : M → Z)
    (p : S → ℚ) (q : M → ℚ) (r : Z → ℚ)
    (δ₁ δ₂ : ℚ)
    (h₁ : l1RowDistance (pushforwardRow φ p) q ≤ δ₁)
    (h₂ : l1RowDistance (pushforwardRow ψ q) r ≤ δ₂) :
    l1RowDistance (pushforwardRow (ψ ∘ φ) p) r ≤ δ₁ + δ₂ := by
  have hcomp : pushforwardRow (ψ ∘ φ) p = pushforwardRow ψ (pushforwardRow φ p) := by
    funext z
    exact (pushforwardRow_comp φ ψ p z).symm
  rw [hcomp]
  exact le_trans
    (l1RowDistance_triangle _ _ _)
    (add_le_add (le_trans (l1_pushforward_contract ψ _ _) h₁) h₂)

/-- Approximate stochastic abstractions compose with additive reward and L1
transition-error ledgers. -/
theorem approximate_abstraction_comp
    {S : Type u} {A : Type v} {M : Type w} {Z : Type x}
    [Fintype S] [Fintype M] [Fintype Z]
    [DecidableEq M] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (mid : FiniteStochasticControlSystem M A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → M) (ψ : M → Z)
    (ε₁ δ₁ R₁ ε₂ δ₂ R₂ : ℚ)
    (h₁ : ApproximateStochasticAbstraction raw mid φ ε₁ δ₁ R₁)
    (h₂ : ApproximateStochasticAbstraction mid absSys ψ ε₂ δ₂ R₂) :
    ApproximateStochasticAbstraction raw absSys (ψ ∘ φ)
      (ε₁ + ε₂) (δ₁ + δ₂) R₂ := by
  refine {
    eps_nonneg := add_nonneg h₁.eps_nonneg h₂.eps_nonneg
    delta_nonneg := add_nonneg h₁.delta_nonneg h₂.delta_nonneg
    reward_bound_nonneg := h₂.reward_bound_nonneg
    actions_eq := h₁.actions_eq.trans h₂.actions_eq
    reward_close := ?_
    transition_close := ?_
    abstract_reward_bounded := h₂.abstract_reward_bounded
  }
  · intro s a ha
    have ha_mid : a ∈ mid.actions := by simpa [← h₁.actions_eq] using ha
    have e1 := h₁.reward_close s a ha
    have e2 := h₂.reward_close (φ s) a ha_mid
    have hsplit : raw.reward s a - absSys.reward (ψ (φ s)) a =
        (raw.reward s a - mid.reward (φ s) a) +
        (mid.reward (φ s) a - absSys.reward (ψ (φ s)) a) := by ring
    rw [Function.comp_apply, hsplit]
    exact le_trans (abs_add_le _ _) (add_le_add e1 e2)
  · intro s a ha
    have ha_mid : a ∈ mid.actions := by simpa [← h₁.actions_eq] using ha
    exact l1_pushforward_triangle φ ψ (raw.transitionProb s a)
      (mid.transitionProb (φ s) a) (absSys.transitionProb (ψ (φ s)) a)
      δ₁ δ₂ (h₁.transition_close s a ha) (h₂.transition_close (φ s) a ha_mid)

/-- Composite closed-form value error is obtained by substituting the additive
ledger into the main approximation theorem. -/
theorem approximate_composite_horizon_bound
    {S : Type u} {A : Type v} {M : Type w} {Z : Type x}
    [Fintype S] [Fintype M] [Fintype Z]
    [DecidableEq M] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (mid : FiniteStochasticControlSystem M A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → M) (ψ : M → Z)
    (ε₁ δ₁ R₁ ε₂ δ₂ R₂ : ℚ)
    (h₁ : ApproximateStochasticAbstraction raw mid φ ε₁ δ₁ R₁)
    (h₂ : ApproximateStochasticAbstraction mid absSys ψ ε₂ δ₂ R₂)
    (n : ℕ) (s : S) :
    |stochasticHorizonValue raw n s -
      stochasticHorizonValue absSys n (ψ (φ s))| ≤
      (n : ℚ) * (ε₁ + ε₂) + (δ₁ + δ₂) * R₂ *
        ((n : ℚ) * ((n : ℚ) - 1) / 2) := by
  simpa [Function.comp_apply] using
    approximate_stochastic_horizon_value_bound_closed raw absSys (ψ ∘ φ)
      (ε₁ + ε₂) (δ₁ + δ₂) R₂
      (approximate_abstraction_comp raw mid absSys φ ψ ε₁ δ₁ R₁ ε₂ δ₂ R₂ h₁ h₂)
      n s

end Komorebi.AVOC
