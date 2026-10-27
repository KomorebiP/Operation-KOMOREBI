import AVOC.StagedAffineOperational
import AVOC.AffineFactorExamples
import AVOC.AffineReuseExamples

namespace Komorebi.AVOC.Affine.StagedExamples

open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Staged
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Factorization
open Komorebi.AVOC.Affine.FactorExamples

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

/-- The same checked width-one implementation is available from a cache or by a
cold generation stage, but with different setup costs. -/
def warmDeployment : Deployment 4 4 where
  kind := .warm
  source := rankOneProgram
  selected := choose rankOneProgram rankOneChecked
  setup := 133
  correct := choose_correct rankOneProgram rankOneChecked
  noWorse := choose_le_original rankOneProgram rankOneChecked


def coldDeployment : Deployment 4 4 where
  kind := .cold
  source := rankOneProgram
  selected := choose rankOneProgram rankOneChecked
  setup := 196
  correct := choose_correct rankOneProgram rankOneChecked
  noWorse := choose_le_original rankOneProgram rankOneChecked


def warmCertain : OptionPlan .warm rankOneProgram where
  deployment := warmDeployment
  source_eq := rfl
  kind_eq := rfl
  successProb := 1
  prob_nonneg := by norm_num
  prob_le_one := by norm_num


def warmHalf : OptionPlan .warm rankOneProgram where
  deployment := warmDeployment
  source_eq := rfl
  kind_eq := rfl
  successProb := 1/2
  prob_nonneg := by norm_num
  prob_le_one := by norm_num


def coldCertain : OptionPlan .cold rankOneProgram where
  deployment := coldDeployment
  source_eq := rfl
  kind_eq := rfl
  successProb := 1
  prob_nonneg := by norm_num
  prob_le_one := by norm_num


def certainModel : Model 4 4 where
  source := rankOneProgram
  calls := 1000
  warm := warmCertain
  cold := coldCertain


def riskyWarmModel : Model 4 4 where
  source := rankOneProgram
  calls := 1000
  warm := warmHalf
  cold := coldCertain


def startCertain : State certainModel := initial certainModel 196
def startRisky : State riskyWarmModel := initial riskyWarmModel 196


def warmReady : State certainModel := step certainModel startCertain .inspectWarm true

def coldReady : State certainModel := step certainModel startCertain .generateCold true


theorem source_and_selected_costs :
    executionCost rankOneProgram = 36 ∧
    executionCost warmDeployment.selected = 21 ∧
    executionCost coldDeployment.selected = 21 := by decide


theorem gross_saving :
    warmCertain.grossSaving 1000 = 15000 ∧ coldCertain.grossSaving 1000 = 15000 := by
  constructor
  · change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num
  · change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num


theorem staged_net_values :
    warmDeployment.payoff 1000 = 14867 ∧ coldDeployment.payoff 1000 = 14804 := by
  constructor
  · change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) - 133 = 14867
    rw [rankOne_execution_costs.2.2]
    norm_num
  · change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) - 196 = 14804
    rw [rankOne_execution_costs.2.2]
    norm_num


theorem successful_stages_ready :
    warmReady.warmStatus = .ready ∧ coldReady.coldStatus = .ready := by
  constructor <;> rfl


theorem warm_deploy_unavailable_initial :
    .deployWarm ∉ actions certainModel startCertain := by
  simp [actions,actionList,startCertain,initial]


theorem warm_deploy_available_after_success :
    .deployWarm ∈ actions certainModel warmReady := by
  simp [warmReady,step,actions,actionList,startCertain,initial,spend,warmFee,
    certainModel,warmCertain,warmDeployment]


theorem initial_budget_safe : BudgetSafe 196 startCertain := by rfl


theorem staged_budget_after_warm :
    warmReady.budget = 63 ∧ warmReady.spent = 133 ∧ BudgetSafe 196 warmReady := by
  change 196 - 133 = 63 ∧ 0 + 133 = 133 ∧ (196 - 133) + (0 + 133) = 196
  norm_num


theorem staged_budget_after_cold :
    coldReady.budget = 0 ∧ coldReady.spent = 196 ∧ BudgetSafe 196 coldReady := by
  change 196 - 196 = 0 ∧ 0 + 196 = 196 ∧ (196 - 196) + (0 + 196) = 196
  norm_num


theorem staged_path_values :
    reward certainModel startCertain .inspectWarm + reward certainModel warmReady .deployWarm = 14867 ∧
    reward certainModel startCertain .generateCold + reward certainModel coldReady .deployCold = 14804 := by
  constructor
  · change -(133 : ℚ) + warmCertain.grossSaving 1000 = 14867
    rw [gross_saving.1]
    norm_num
  · change -(196 : ℚ) + coldCertain.grossSaving 1000 = 14804
    rw [gross_saving.2]
    norm_num


theorem warm_net_strictly_better : (14804 : ℚ) < 14867 := by norm_num

/-- The generic theorem gives exact finite-horizon adaptive optimality and budget
safety. The executable runtime regression checks the concrete choices below. -/
theorem certain_model_safe_optimal_plan (h : Nat) :
    ∃ p : Guarded.Plan Action Bool h,
      Guarded.Legal (system certainModel) startCertain p ∧
      Guarded.TreeSafe (system certainModel) (BudgetSafe 196) startCertain p ∧
      Guarded.planValue (system certainModel) startCertain p =
        Guarded.value (system certainModel) h startCertain ∧
      ∀ q : Guarded.Plan Action Bool h,
        Guarded.Legal (system certainModel) startCertain q →
        Guarded.planValue (system certainModel) startCertain q ≤
          Guarded.planValue (system certainModel) startCertain p :=
  safe_optimal_plan_exists certainModel 196 h startCertain initial_budget_safe


theorem risky_model_choice_is_feasible (h : Nat) :
    ∃ a, (ExecutablePlanner.evaluate (executable riskyWarmModel) (h+1) startRisky).choice = some a ∧
      a ∈ (system riskyWarmModel).actions startRisky ∧
      ∀ b ∈ (system riskyWarmModel).actions startRisky,
        Guarded.qValue (system riskyWarmModel) h startRisky b ≤
          Guarded.qValue (system riskyWarmModel) h startRisky a :=
  evaluated_choice_optimal riskyWarmModel h startRisky

end Komorebi.AVOC.Affine.StagedExamples
