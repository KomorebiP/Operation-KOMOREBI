import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Tactic.Push

/-! P8, finite-dimensional closure. Iteration adds actual images under
operators. Finite stabilization and leastness are proved, not supplied
as hypotheses. The action index may even be infinite. -/
set_option autoImplicit false
namespace Komorebi.LSM
open Module
universe u v w
variable {K : Type u} [DivisionRing K]
variable {V : Type v} [AddCommGroup V] [Module K V]
variable {I : Type w}

/-- Invariance under the whole declared family. -/
def CommonInvariant (L : I → V →ₗ[K] V) (W : Submodule K V) : Prop :=
  ∀ i, W.map (L i) ≤ W

/-- One enrichment step. -/
def invariantStep (L : I → V →ₗ[K] V) (W : Submodule K V) : Submodule K V :=
  W ⊔ ⨆ i, W.map (L i)

/-- The actual finite sequence of enriched observable spaces. -/
def invariantSequence (L : I → V →ₗ[K] V) (W₀ : Submodule K V) : ℕ → Submodule K V
  | 0 => W₀
  | n+1 => invariantStep L (invariantSequence L W₀ n)

theorem invariantStep_le (L : I → V →ₗ[K] V) (W : Submodule K V) :
    W ≤ invariantStep L W := le_sup_left

theorem invariantStep_monotone (L : I → V →ₗ[K] V) : Monotone (invariantStep L) := by
  intro W U h
  exact sup_le_sup h (iSup_mono fun _ => Submodule.map_mono h)

theorem invariantStep_eq_iff (L : I → V →ₗ[K] V) (W : Submodule K V) :
    invariantStep L W = W ↔ CommonInvariant L W := by
  constructor
  · intro h i
    calc
      W.map (L i) ≤ ⨆ j, W.map (L j) := le_iSup (fun j => W.map (L j)) i
      _ ≤ invariantStep L W := le_sup_right
      _ = W := h
  · intro h
    exact le_antisymm (sup_le le_rfl (iSup_le h)) (invariantStep_le L W)

theorem invariantSequence_le_succ (L : I → V →ₗ[K] V) (W₀ : Submodule K V) (n : ℕ) :
    invariantSequence L W₀ n ≤ invariantSequence L W₀ (n+1) := invariantStep_le L _

theorem invariantSequence_monotone (L : I → V →ₗ[K] V) (W₀ : Submodule K V) :
    Monotone (invariantSequence L W₀) :=
  monotone_nat_of_le_succ (invariantSequence_le_succ L W₀)

theorem initial_le_invariantSequence (L : I → V →ₗ[K] V)
    (W₀ : Submodule K V) (n : ℕ) : W₀ ≤ invariantSequence L W₀ n :=
  invariantSequence_monotone L W₀ (Nat.zero_le n)

theorem invariantSequence_minimal (L : I → V →ₗ[K] V)
    (W₀ U : Submodule K V) (h₀ : W₀ ≤ U) (hU : CommonInvariant L U) (n : ℕ) :
    invariantSequence L W₀ n ≤ U := by
  induction n with
  | zero => exact h₀
  | succ n ih =>
      calc
        invariantSequence L W₀ (n+1) ≤ invariantStep L U := invariantStep_monotone L ih
        _ = U := (invariantStep_eq_iff L U).mpr hU

/-- Equality at one stage persists at all later stages. -/
theorem invariantSequence_stays (L : I → V →ₗ[K] V) (W₀ : Submodule K V)
    (n : ℕ) (h : invariantSequence L W₀ (n+1) = invariantSequence L W₀ n) (k : ℕ) :
    invariantSequence L W₀ (n+k) = invariantSequence L W₀ n := by
  induction k with
  | zero => simp
  | succ k ih =>
      rw [Nat.add_succ, invariantSequence, ih]
      exact h

variable [FiniteDimensional K V]

/-- Every strict enrichment increases dimension by at least one. -/
theorem invariantSequence_dimension_growth (L : I → V →ₗ[K] V) (W₀ : Submodule K V)
    (n : ℕ) (strict : ∀ k < n,
      invariantSequence L W₀ k ≠ invariantSequence L W₀ (k+1)) :
    finrank K W₀ + n ≤ finrank K (invariantSequence L W₀ n) := by
  induction n with
  | zero => simp [invariantSequence]
  | succ n ih =>
      have hn := ih (fun k hk => strict k (Nat.lt_succ_of_lt hk))
      have hs : invariantSequence L W₀ n < invariantSequence L W₀ (n+1) :=
        lt_of_le_of_ne (invariantSequence_le_succ L W₀ n) (Ne.symm (strict n (Nat.lt_succ_self n)))
      have hd := Submodule.finrank_lt_finrank_of_lt hs
      omega

/-- Stabilization occurs no later than the ambient dimension deficit. -/
theorem invariantSequence_exists_stable (L : I → V →ₗ[K] V) (W₀ : Submodule K V) :
    ∃ n ≤ finrank K V - finrank K W₀,
      invariantSequence L W₀ (n+1) = invariantSequence L W₀ n := by
  classical
  by_contra h
  push_neg at h
  let N := finrank K V - finrank K W₀
  have hg := invariantSequence_dimension_growth L W₀ (N+1) (by
    intro k hk
    exact Ne.symm (h k (by omega)))
  have hu := Submodule.finrank_le (invariantSequence L W₀ (N+1))
  have h₀ := Submodule.finrank_le W₀
  dsimp [N] at hg
  omega

/-- A bounded, explicitly indexed completion, not a supplied fixed point. -/
def invariantCompletion (L : I → V →ₗ[K] V) (W₀ : Submodule K V) : Submodule K V :=
  invariantSequence L W₀ (finrank K V - finrank K W₀)

theorem invariantCompletion_fixed (L : I → V →ₗ[K] V) (W₀ : Submodule K V) :
    invariantStep L (invariantCompletion L W₀) = invariantCompletion L W₀ := by
  obtain ⟨n, hn, hs⟩ := invariantSequence_exists_stable L W₀
  have he := invariantSequence_stays L W₀ n hs (finrank K V - finrank K W₀ - n)
  rw [Nat.add_sub_of_le hn] at he
  change invariantStep L (invariantSequence L W₀ _) = invariantSequence L W₀ _
  rw [he]
  exact hs

theorem invariantCompletion_invariant (L : I → V →ₗ[K] V) (W₀ : Submodule K V) :
    CommonInvariant L (invariantCompletion L W₀) :=
  (invariantStep_eq_iff L _).mp (invariantCompletion_fixed L W₀)

theorem initial_le_invariantCompletion (L : I → V →ₗ[K] V) (W₀ : Submodule K V) :
    W₀ ≤ invariantCompletion L W₀ := initial_le_invariantSequence L W₀ _

theorem invariantCompletion_minimal (L : I → V →ₗ[K] V)
    (W₀ U : Submodule K V) (h₀ : W₀ ≤ U) (hU : CommonInvariant L U) :
    invariantCompletion L W₀ ≤ U := invariantSequence_minimal L W₀ U h₀ hU _

/-- The bounded construction is the unique least common invariant extension. -/
theorem invariantCompletion_isLeast (L : I → V →ₗ[K] V) (W₀ : Submodule K V) :
    IsLeast {W : Submodule K V | W₀ ≤ W ∧ CommonInvariant L W} (invariantCompletion L W₀) := by
  refine ⟨⟨initial_le_invariantCompletion L W₀, invariantCompletion_invariant L W₀⟩, ?_⟩
  intro U hU
  exact invariantCompletion_minimal L W₀ U hU.1 hU.2

end Komorebi.LSM
