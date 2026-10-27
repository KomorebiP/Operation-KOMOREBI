import AVOC.Core
import Mathlib.Algebra.Order.Field.Rat
import Mathlib.Data.Fintype.Pi
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Finset.Max
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

universe u v w z

/-- Value of a deterministic observation experiment followed by a deterministic
policy. `prior` need not be normalized for the structural theorems below. -/
def deterministicDecisionValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} {A : Type w}
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (obs : Ω → O) (policy : O → A) : ℚ :=
  ∑ ω, prior ω * utility ω (policy (obs ω))

/-- A policy on a garbled/coarser experiment lifts along the decoder of a
refining experiment with exactly the same decision value. -/
theorem deterministic_policy_lift_value_eq
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} {Coarse : Type w} {A : Type z}
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    {fine : Ω → Fine} {coarse : Ω → Coarse}
    (h : Refines fine coarse) (policy : Coarse → A) :
    ∃ lifted : Fine → A,
      deterministicDecisionValue prior utility fine lifted =
        deterministicDecisionValue prior utility coarse policy := by
  rcases h with ⟨decode, hdecode⟩
  refine ⟨policy ∘ decode, ?_⟩
  unfold deterministicDecisionValue
  apply Finset.sum_congr rfl
  intro ω hω
  simp only [Function.comp_apply, hdecode]

/-- Best deterministic decision value available from an observation map over a
finite nonempty action space. -/
noncomputable def bestDeterministicDecisionValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ) (obs : Ω → O) : ℚ := by
  classical
  let vals : Finset ℚ := (Finset.univ : Finset (O → A)).image
    (deterministicDecisionValue prior utility obs)
  have hne : vals.Nonempty := by
    let a0 : A := Classical.choice (inferInstance : Nonempty A)
    let p0 : O → A := fun _ => a0
    refine ⟨deterministicDecisionValue prior utility obs p0, ?_⟩
    exact Finset.mem_image.mpr ⟨p0, Finset.mem_univ _, rfl⟩
  exact vals.max' hne

/-- Every concrete policy is bounded by the best deterministic value. -/
theorem deterministicDecisionValue_le_best
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ) (obs : Ω → O)
    (policy : O → A) :
    deterministicDecisionValue prior utility obs policy ≤
      bestDeterministicDecisionValue prior utility obs := by
  classical
  unfold bestDeterministicDecisionValue
  let vals : Finset ℚ := (Finset.univ : Finset (O → A)).image
    (deterministicDecisionValue prior utility obs)
  have hne : vals.Nonempty := by
    let a0 : A := Classical.choice (inferInstance : Nonempty A)
    let p0 : O → A := fun _ => a0
    refine ⟨deterministicDecisionValue prior utility obs p0, ?_⟩
    exact Finset.mem_image.mpr ⟨p0, Finset.mem_univ _, rfl⟩
  exact Finset.le_max' vals _ (Finset.mem_image.mpr ⟨policy, Finset.mem_univ _, rfl⟩)

/-- A best deterministic policy exists for every finite observation and action
space with at least one action. -/
theorem best_deterministic_policy_exists
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ) (obs : Ω → O) :
    ∃ policy : O → A,
      deterministicDecisionValue prior utility obs policy =
        bestDeterministicDecisionValue prior utility obs := by
  classical
  let vals : Finset ℚ := (Finset.univ : Finset (O → A)).image
    (deterministicDecisionValue prior utility obs)
  have hne : vals.Nonempty := by
    let a0 : A := Classical.choice (inferInstance : Nonempty A)
    let p0 : O → A := fun _ => a0
    refine ⟨deterministicDecisionValue prior utility obs p0, ?_⟩
    exact Finset.mem_image.mpr ⟨p0, Finset.mem_univ _, rfl⟩
  have hmaxmem : vals.max' hne ∈ vals := Finset.max'_mem vals hne
  rcases Finset.mem_image.mp hmaxmem with ⟨policy, hpu, hpval⟩
  refine ⟨policy, ?_⟩
  unfold bestDeterministicDecisionValue
  change deterministicDecisionValue prior utility obs policy = vals.max' hne
  exact hpval

/-- Deterministic Blackwell/data-processing theorem. If `fine` deterministically
refines `coarse`, then no finite decision problem can have a larger optimal
value from the coarse observation than from the fine observation. -/
theorem deterministic_blackwell_monotonicity
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    {fine : Ω → Fine} {coarse : Ω → Coarse}
    (h : Refines fine coarse) :
    bestDeterministicDecisionValue prior utility coarse ≤
      bestDeterministicDecisionValue prior utility fine := by
  obtain ⟨policy, hpolicy⟩ :=
    best_deterministic_policy_exists prior utility coarse
  obtain ⟨lifted, hlift⟩ :=
    deterministic_policy_lift_value_eq prior utility h policy
  rw [← hpolicy, ← hlift]
  exact deterministicDecisionValue_le_best prior utility fine lifted

/-- Net value of an experiment after charging an explicit acquisition cost. -/
def netExperimentValue (decisionValue cost : ℚ) : ℚ := decisionValue - cost

/-- If one deterministic experiment refines another and costs no more, the
coarser experiment is weakly dominated in every finite decision problem. -/
theorem deterministic_blackwell_cost_dominance
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    {fine : Ω → Fine} {coarse : Ω → Coarse}
    (h : Refines fine coarse) {fineCost coarseCost : ℚ}
    (hcost : fineCost ≤ coarseCost) :
    netExperimentValue (bestDeterministicDecisionValue prior utility coarse) coarseCost ≤
      netExperimentValue (bestDeterministicDecisionValue prior utility fine) fineCost := by
  unfold netExperimentValue
  have hv := deterministic_blackwell_monotonicity prior utility h
  linarith

end Komorebi.AVOC
