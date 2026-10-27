import AVOC.LazyStagedRecovery
import AVOC.StagedAffineExamples

namespace Komorebi.AVOC.Affine.LazyStagedExamples

open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Action Status)
open Komorebi.AVOC.Affine.StagedExamples
open Komorebi.AVOC.Affine.Factorization
open Komorebi.AVOC.Affine.FactorExamples
open Komorebi.AVOC.Affine.LazyStaged
open Komorebi.AVOC.Affine.LazyRecovery

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩


def warmQuote : Quote .warm where
  fee := 133
  gross := 15000
  gross_nonneg := by norm_num
  successProb := 1
  prob_nonneg := by norm_num
  prob_le_one := by norm_num


def coldQuote : Quote .cold where
  fee := 196
  gross := 15000
  gross_nonneg := by norm_num
  successProb := 1
  prob_nonneg := by norm_num
  prob_le_one := by norm_num


def quoteModel : Model 4 4 where
  source := rankOneProgram
  calls := 1000
  warm := warmQuote
  cold := coldQuote


def warmArtifact : CheckedArtifact quoteModel .warm where
  deployment := warmDeployment
  kind_eq := rfl
  source_eq := rfl
  setup_eq := rfl
  gross_eq := by
    change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num


def coldArtifact : CheckedArtifact quoteModel .cold where
  deployment := coldDeployment
  kind_eq := rfl
  source_eq := rfl
  setup_eq := rfl
  gross_eq := by
    change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num


def start : RuntimeState quoteModel := initial quoteModel 196


theorem start_safe : LazyStaged.Safe 196 start := LazyStaged.initial_safe quoteModel 196


theorem artifact_payoffs_match_quotes :
    warmArtifact.deployment.payoff 1000 = 14867 ∧
    coldArtifact.deployment.payoff 1000 = 14804 := by
  constructor
  · have h := CheckedArtifact.fee_then_gross warmArtifact
    change -(133 : ℚ) + 15000 = warmArtifact.deployment.payoff 1000 at h
    norm_num at h ⊢
    exact h.symm
  · have h := CheckedArtifact.fee_then_gross coldArtifact
    change -(196 : ℚ) + 15000 = coldArtifact.deployment.payoff 1000 at h
    norm_num at h ⊢
    exact h.symm



def afterWarm : RuntimeState quoteModel :=
  install start .inspectWarm (.warmSuccess warmArtifact)
    (step quoteModel start.plan .inspectWarm true)


theorem warm_report_supported :
    Supported quoteModel start.plan .inspectWarm true := by
  constructor
  · exact (inspectWarm_mem_iff quoteModel start.plan).2 ⟨rfl,rfl,by norm_num [warmFee,quoteModel,warmQuote,start,LazyStaged.initial,initialPlan]⟩
  · norm_num [probability,quoteModel,warmQuote]


theorem warm_confirmation_exact :
    confirm quoteModel start .inspectWarm (.warmSuccess warmArtifact) = some afterWarm := by
  simp [confirm,reportOf,warm_report_supported,afterWarm]


theorem warm_confirmation_safe : Safe 196 afterWarm :=
  confirm_safe quoteModel 196 start afterWarm .inspectWarm (.warmSuccess warmArtifact)
    start_safe warm_confirmation_exact


theorem warm_confirmation_installs :
    afterWarm.plan.warmStatus = .ready ∧ afterWarm.warmArtifact = some warmArtifact := by
  exact warm_success_stores_exact quoteModel start afterWarm warmArtifact warm_confirmation_exact


theorem recommendation_does_not_require_artifacts :
    recommend quoteModel 1 start = recommend quoteModel 1
      { start with warmArtifact := some warmArtifact, coldArtifact := some coldArtifact } := by
  rfl


theorem unfinished_recovery_is_not_evidence :
    recover quoteModel (LazyRecovery.initial quoteModel 196)
      (.unfinished (prepare quoteModel 1 (LazyRecovery.initial quoteModel 196)))
      (view start) = .error "no durable result: do not infer a report or retry" := by
  rfl

end Komorebi.AVOC.Affine.LazyStagedExamples

namespace Komorebi.AVOC.Affine.LazyStagedExamples

open Komorebi.AVOC.Affine.Staged (Action)
open Komorebi.AVOC.Affine.LazyStaged
open Komorebi.AVOC.Affine.LazyRecovery


def checkpoint0 : Checkpoint quoteModel := LazyRecovery.initial quoteModel 196

def warmCommit : Commit quoteModel :=
  commitFor checkpoint0 .inspectWarm (.warmSuccess warmArtifact) afterWarm


def checkpoint1 : Checkpoint quoteModel :=
  ⟨1,afterWarm,some warmCommit⟩


theorem warm_commit_acknowledged :
    acknowledge quoteModel checkpoint0 warmCommit (.warmSuccess warmArtifact)
      (view afterWarm) = .ok checkpoint1 := by
  apply acknowledge_checked_transition
  · exact warm_confirmation_exact
  · simp [checkpoint0,commitFor,intentFor,LazyRecovery.initial]


theorem warm_commit_acknowledgement_idempotent :
    acknowledge quoteModel checkpoint1 warmCommit (.warmSuccess warmArtifact)
      (view afterWarm) = .ok checkpoint1 := by
  exact acknowledge_idempotent quoteModel checkpoint0 checkpoint1 warmCommit
    (.warmSuccess warmArtifact) (view afterWarm) warm_commit_acknowledged

end Komorebi.AVOC.Affine.LazyStagedExamples
