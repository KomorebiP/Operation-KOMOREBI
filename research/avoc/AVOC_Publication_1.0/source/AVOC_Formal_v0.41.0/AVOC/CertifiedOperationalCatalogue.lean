import AVOC.MultiLevelOperational

namespace Komorebi.AVOC.Affine.CertifiedOperational

open Komorebi.AVOC.MultiLevel
open Komorebi.AVOC.Affine.MultiLevelRank
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.MultiLevelEconomics

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

/-- One hidden workload world with proof-carrying warm and cold implementations.
The planner payoff is derived from these objects instead of supplied independently. -/
structure WorldPlan (n m : Nat) where
  source : DenseProgram F n m
  calls : Nat
  warm : Deployment n m
  cold : Deployment n m
  warm_source : warm.source = source
  cold_source : cold.source = source
  warm_kind : warm.kind = .warm
  cold_kind : cold.kind = .cold

namespace WorldPlan

variable {n m : Nat}

@[simp] theorem warm_correct (w : WorldPlan n m) (x : Fin n → F) :
    execute w.warm.selected x = execute w.source x := by
  rw [← w.warm_source]
  exact w.warm.correct x

@[simp] theorem cold_correct (w : WorldPlan n m) (x : Fin n → F) :
    execute w.cold.selected x = execute w.source x := by
  rw [← w.cold_source]
  exact w.cold.correct x

@[simp] theorem warm_cost_le (w : WorldPlan n m) :
    executionCost w.warm.selected ≤ executionCost w.source := by
  rw [← w.warm_source]
  exact w.warm.noWorse

@[simp] theorem cold_cost_le (w : WorldPlan n m) :
    executionCost w.cold.selected ≤ executionCost w.source := by
  rw [← w.cold_source]
  exact w.cold.noWorse

@[simp] theorem warm_payoff (w : WorldPlan n m) :
    w.warm.payoff w.calls =
      netGain w.calls (executionCost w.source) w.warm.setup
        (executionCost w.warm.selected) := by
  unfold Deployment.payoff
  rw [w.warm_source]

@[simp] theorem cold_payoff (w : WorldPlan n m) :
    w.cold.payoff w.calls =
      netGain w.calls (executionCost w.source) w.cold.setup
        (executionCost w.cold.selected) := by
  unfold Deployment.payoff
  rw [w.cold_source]

end WorldPlan

variable {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]

/-- A complete prechecked finite operational catalogue. Probe fees remain model data;
terminal implementation payoffs are derived from proof-carrying deployments. -/
structure Catalogue (Ω P : Type*) [Fintype Ω] [DecidableEq Ω]
    [Fintype P] [DecidableEq P] (n m : Nat) where
  world : Ω → WorldPlan n m
  probe : P → Probe m n
  fee : P → ℚ
  fee_nonneg : ∀ p, 0 ≤ fee p


def rankCatalogue (c : Catalogue Ω P n m) : MultiLevelRank.Catalogue F Ω P n m where
  matrix w := (coefficients (c.world w).source).linear
  probe := c.probe
  fee := c.fee
  fee_nonneg := c.fee_nonneg
  reuseAvailable := true
  reusePayoff w := (c.world w).warm.payoff (c.world w).calls
  coldPayoff w := (c.world w).cold.payoff (c.world w).calls


def model (c : Catalogue Ω P n m) : MultiLevel.Model Ω P :=
  MultiLevelRank.model (rankCatalogue c)

@[simp] theorem reuse_payoff_derived (c : Catalogue Ω P n m) (w : Ω) :
    (model c).reusePayoff w = (c.world w).warm.payoff (c.world w).calls := rfl

@[simp] theorem cold_payoff_derived (c : Catalogue Ω P n m) (w : Ω) :
    (model c).coldPayoff w = (c.world w).cold.payoff (c.world w).calls := rfl

/-- The model reward for reuse is exactly the current retained-world average of
checked warm-deployment payoffs. -/
theorem reuse_reward_exact (c : Catalogue Ω P n m) (s : MultiLevel.State (model c)) :
    MultiLevel.reward (model c) s .reuse =
      MultiLevel.average (model c) s (fun w => (c.world w).warm.payoff (c.world w).calls) := rfl

/-- The model reward for cold generation is exactly the retained-world average
of checked cold-deployment payoffs. -/
theorem cold_reward_exact (c : Catalogue Ω P n m) (s : MultiLevel.State (model c)) :
    MultiLevel.reward (model c) s .cold =
      MultiLevel.average (model c) s (fun w => (c.world w).cold.payoff (c.world w).calls) := rfl

/-- Every world-level terminal option has an implementation proof, independently
of its probability or economic attractiveness. -/
theorem world_deployments_sound (c : Catalogue Ω P n m) (w : Ω) :
    (∀ x, execute (c.world w).warm.selected x = execute (c.world w).source x) ∧
    (∀ x, execute (c.world w).cold.selected x = execute (c.world w).source x) ∧
    executionCost (c.world w).warm.selected ≤ executionCost (c.world w).source ∧
    executionCost (c.world w).cold.selected ≤ executionCost (c.world w).source :=
  ⟨WorldPlan.warm_correct _,WorldPlan.cold_correct _,WorldPlan.warm_cost_le _,WorldPlan.cold_cost_le _⟩

/-- At an actual retained world, the terminal model error is zero because the
payoff function is derived from the same checked deployment. -/
theorem actual_reuse_discrepancy_zero (c : Catalogue Ω P n m)
    (s : MultiLevel.State (model c)) (w : Ω)
    (hconst : ∀ u ∈ s.worlds,
      (c.world u).warm.payoff (c.world u).calls =
        (c.world w).warm.payoff (c.world w).calls) :
    MultiLevelOperational.terminalDiscrepancy (model c) s .reuse
      (c.world w).warm (c.world w).calls = 0 := by
  have havg : MultiLevel.reward (model c) s .reuse =
      (c.world w).warm.payoff (c.world w).calls := by
    rw [reuse_reward_exact]
    unfold MultiLevel.average
    have hs : (∑ u ∈ s.worlds,
        (c.world u).warm.payoff (c.world u).calls) =
        ∑ _u ∈ s.worlds, (c.world w).warm.payoff (c.world w).calls := by
      apply Finset.sum_congr rfl
      intro u hu
      exact hconst u hu
    rw [hs,Finset.sum_const]
    have hn : (s.worlds.card : ℚ) ≠ 0 := by
      exact_mod_cast Nat.ne_of_gt (MultiLevel.worlds_card_pos s)
    simp [hn]
  simp [MultiLevelOperational.terminalDiscrepancy,havg]

end Komorebi.AVOC.Affine.CertifiedOperational

namespace Komorebi.AVOC.Affine.CertifiedOperational

open Komorebi.AVOC.MultiLevel
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.MultiLevelOperational

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F2 := ZMod 5

variable {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
variable {n m : Nat}

/-- The same exact-model bridge for cold generation.  Constancy is explicit:
a catalogue-average prediction need not equal every individual world's payoff. -/
theorem actual_cold_discrepancy_zero (c : Catalogue Ω P n m)
    (s : MultiLevel.State (model c)) (w : Ω)
    (hconst : ∀ u ∈ s.worlds,
      (c.world u).cold.payoff (c.world u).calls =
        (c.world w).cold.payoff (c.world w).calls) :
    terminalDiscrepancy (model c) s .cold
      (c.world w).cold (c.world w).calls = 0 := by
  have havg : MultiLevel.reward (model c) s .cold =
      (c.world w).cold.payoff (c.world w).calls := by
    rw [cold_reward_exact]
    unfold MultiLevel.average
    have hs : (∑ u ∈ s.worlds,
        (c.world u).cold.payoff (c.world u).calls) =
        ∑ _u ∈ s.worlds, (c.world w).cold.payoff (c.world w).calls := by
      apply Finset.sum_congr rfl
      intro u hu
      exact hconst u hu
    rw [hs,Finset.sum_const]
    have hn : (s.worlds.card : ℚ) ≠ 0 := by
      exact_mod_cast Nat.ne_of_gt (MultiLevel.worlds_card_pos s)
    simp [hn]
  simp [terminalDiscrepancy,havg]

end Komorebi.AVOC.Affine.CertifiedOperational
