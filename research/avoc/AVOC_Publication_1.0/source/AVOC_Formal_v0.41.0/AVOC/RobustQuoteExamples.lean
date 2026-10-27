import AVOC.RobustQuoteRecovery
import AVOC.LazyStagedExamples

namespace Komorebi.AVOC.Affine.RobustQuoteExamples

open Komorebi.AVOC
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Action Status)
open Komorebi.AVOC.Affine.Factorization
open Komorebi.AVOC.Affine.FactorExamples
open Komorebi.AVOC.Affine.StagedExamples
open Komorebi.AVOC.Affine.LazyStagedExamples
open Komorebi.AVOC.Affine.LazyStaged
open Komorebi.AVOC.Affine.QuoteAuthority
open Komorebi.AVOC.Affine.RobustQuote
open Komorebi.AVOC.Affine.RobustQuoteRecovery

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

private def identity (k : Kind) (calls : Nat) (provider : String) : Identity 4 4 :=
  { kind := k, source := coefficients rankOneProgram, calls := calls,
    costModel := "dense-v1", provider := provider, checker := "affine-factor-v1",
    environment := "lean-4.34.0-rc2", schema := "robust-quote-v1" }

private def exactRaw (k : Kind) (fee : Nat) (gross probability : ℚ)
    (_hg : 0 ≤ gross) (hp0 : 0 ≤ probability) (hp1 : probability ≤ 1) : RawQuote 4 4 :=
  { identity := identity k 1000 (match k with | .warm => "cache" | .cold => "generator"),
    setup := NatBand.singleton fee,
    gross := RatBand.singleton gross,
    probability := ProbabilityBand.singleton probability hp0 hp1 }

private def exactWarmAuthority : Authority 4 4 .warm where
  approved := exactRaw .warm 133 15000 1 (by norm_num) (by norm_num) (by norm_num)
  kind_eq := rfl
  gross_nonneg := by norm_num [exactRaw,RatBand.singleton]

private def exactColdAuthority : Authority 4 4 .cold where
  approved := exactRaw .cold 196 15000 1 (by norm_num) (by norm_num) (by norm_num)
  kind_eq := rfl
  gross_nonneg := by norm_num [exactRaw,RatBand.singleton]

/-- Singleton evidence reproduces the inherited v0.37 rank-one quote model. -/
def exactModel : QModel 4 4 where
  source := rankOneProgram
  calls := 1000
  warm := exactWarmAuthority
  cold := exactColdAuthority
  warm_source := rfl
  cold_source := rfl
  warm_calls := rfl
  cold_calls := rfl

theorem exact_nominal_is_v037 : nominal exactModel = quoteModel := by rfl

theorem exact_bands : ExactBands exactModel := by
  norm_num [ExactBands,setupBand,grossBand,probBand,rawQuote,exactModel,
    exactWarmAuthority,exactColdAuthority,exactRaw,NatBand.width,NatBand.singleton,
    RatBand.width,RatBand.singleton,ProbabilityBand.width,ProbabilityBand.singleton]

def exactRealization : Realization exactModel where
  warm := ⟨133,15000,1,
    by simp [setupBand,rawQuote,exactModel,exactWarmAuthority,exactRaw,NatBand.Contains,NatBand.singleton],
    by simp [grossBand,rawQuote,exactModel,exactWarmAuthority,exactRaw,RatBand.Contains,RatBand.singleton],
    by simp [probBand,rawQuote,exactModel,exactWarmAuthority,exactRaw,
      ProbabilityBand.Contains,ProbabilityBand.singleton,RatBand.Contains]⟩
  cold := ⟨196,15000,1,
    by simp [setupBand,rawQuote,exactModel,exactColdAuthority,exactRaw,NatBand.Contains,NatBand.singleton],
    by simp [grossBand,rawQuote,exactModel,exactColdAuthority,exactRaw,RatBand.Contains,RatBand.singleton],
    by simp [probBand,rawQuote,exactModel,exactColdAuthority,exactRaw,
      ProbabilityBand.Contains,ProbabilityBand.singleton,RatBand.Contains]⟩

noncomputable def exactStart : RobustQuote.RuntimeState exactModel := RobustQuote.initial exactModel 196

noncomputable def exactLazyStart : LazyStaged.RuntimeState (nominal exactModel) :=
  ⟨LazyStaged.initialPlan (nominal exactModel) 196,none,none⟩

theorem exact_recovers_v037 :
    robustChoice exactModel 1 exactLazyStart.plan =
      LazyStaged.recommend (nominal exactModel) 1 exactLazyStart :=
  robustChoice_recovers_v037 exactModel exact_bands 1 exactLazyStart

/-- Warm uncertainty is large enough that the nominal lower-end model prefers warm,
while robust lower-Q planning prefers the exact cold alternative. -/
private def uncertainWarmRaw : RawQuote 4 4 :=
  { identity := identity .warm 1 "uncertain-cache",
    setup := NatBand.singleton 0,
    gross := RatBand.singleton 200,
    probability := ⟨⟨3/5,1,by norm_num⟩,by norm_num,by norm_num⟩ }

private def uncertainColdRaw : RawQuote 4 4 :=
  { identity := identity .cold 1 "exact-generator",
    setup := NatBand.singleton 0,
    gross := RatBand.singleton 60,
    probability := ProbabilityBand.singleton 1 (by norm_num) (by norm_num) }

private def uncertainModel : QModel 4 4 where
  source := rankOneProgram
  calls := 1
  warm := ⟨uncertainWarmRaw,rfl,by norm_num [uncertainWarmRaw,RatBand.singleton]⟩
  cold := ⟨uncertainColdRaw,rfl,by norm_num [uncertainColdRaw,RatBand.singleton]⟩
  warm_source := rfl
  cold_source := rfl
  warm_calls := rfl
  cold_calls := rfl

private def uncertainPlan : State uncertainModel := LazyStaged.initialPlan (nominal uncertainModel) 0

/-- The interval data expose the mechanism used by the executable uncertainty example. -/
theorem uncertain_probability_width : (probBand uncertainModel .warm).width = 2/5 := by
  norm_num [probBand,rawQuote,uncertainModel,uncertainWarmRaw,ProbabilityBand.width]

theorem uncertain_cold_exact_probability : (probBand uncertainModel .cold).width = 0 := by
  norm_num [probBand,rawQuote,uncertainModel,uncertainColdRaw,
    ProbabilityBand.width,ProbabilityBand.singleton]


private def warmBounded : BoundedArtifact exactModel .warm where
  deployment := warmDeployment
  identity := quoteIdentity exactModel .warm
  identity_eq := rfl
  kind_eq := rfl
  source_eq := rfl
  setup_mem := by
    change (NatBand.singleton 133).Contains warmDeployment.setup
    rw [NatBand.singleton_contains_iff]
    rfl
  gross_mem := by
    change (RatBand.singleton 15000).Contains
      (LazyStaged.deploymentGross warmDeployment 1000)
    rw [RatBand.singleton_contains_iff]
    change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num

private def coldBounded : BoundedArtifact exactModel .cold where
  deployment := coldDeployment
  identity := quoteIdentity exactModel .cold
  identity_eq := rfl
  kind_eq := rfl
  source_eq := rfl
  setup_mem := by
    change (NatBand.singleton 196).Contains coldDeployment.setup
    rw [NatBand.singleton_contains_iff]
    rfl
  gross_mem := by
    change (RatBand.singleton 15000).Contains
      (LazyStaged.deploymentGross coldDeployment 1000)
    rw [RatBand.singleton_contains_iff]
    change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num

noncomputable def afterWarm : RobustQuote.RuntimeState exactModel :=
  install exactStart .inspectWarm (.warmSuccess warmBounded)
    (LazyStaged.step (nominal exactModel) exactStart.plan .inspectWarm true)

private theorem warm_supported : Supported exactModel exactStart.plan .inspectWarm true := by
  constructor
  · exact (LazyStaged.inspectWarm_mem_iff (nominal exactModel) exactStart.plan).2
      ⟨rfl,rfl,by
        norm_num [exactStart,RobustQuote.initial,LazyStaged.initialPlan,
          nominal,nominalQuote,exactModel,exactWarmAuthority,exactRaw,
          NatBand.singleton,LazyStaged.warmFee]⟩
  · norm_num [reportPossible,probBand,rawQuote,exactModel,exactWarmAuthority,exactRaw,
      ProbabilityBand.singleton]

private theorem warm_confirmed :
    confirm exactModel exactStart .inspectWarm (.warmSuccess warmBounded) = some afterWarm := by
  simp [RobustQuote.confirm,RobustQuote.reportOf,warm_supported,afterWarm]

theorem artifact_refines_deterministic_fields :
    afterWarm.warmEvidence = some warmBounded.refined ∧
    warmBounded.refined.setup = 133 ∧
    warmBounded.refined.gross = 15000 ∧
    warmBounded.refined.probabilityBand = probBand exactModel .warm := by
  obtain h := warm_success_stores_refinement exactModel exactStart afterWarm warmBounded warm_confirmed
  refine ⟨h.2.2,?_,?_,rfl⟩
  · rfl
  · change LazyStaged.deploymentGross warmDeployment 1000 = 15000
    change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num

theorem warm_install_preserves_unselected :
    afterWarm.coldArtifact = exactStart.coldArtifact ∧
    afterWarm.coldEvidence = exactStart.coldEvidence :=
  warm_success_preserves_cold exactModel exactStart afterWarm warmBounded warm_confirmed

noncomputable def checkpoint0 : Checkpoint exactModel := RobustQuoteRecovery.initial exactModel 196
noncomputable def warmCommit : Commit exactModel := commitFor exactModel checkpoint0
  .inspectWarm (.warmSuccess warmBounded) afterWarm
noncomputable def checkpoint1 : Checkpoint exactModel := ⟨checkpoint0.next+1,afterWarm,some warmCommit⟩

theorem committed_result_recovers_without_rerun :
    acknowledge exactModel checkpoint0 warmCommit (.warmSuccess warmBounded)
      (view afterWarm) (evidence exactModel) = .ok checkpoint1 := by
  simpa [checkpoint1,warmCommit] using
    acknowledge_checked_transition exactModel checkpoint0 .inspectWarm
      (.warmSuccess warmBounded) afterWarm warm_confirmed (by
        simp [checkpoint0,RobustQuoteRecovery.initial,commitFor,intentFor])

theorem duplicate_acknowledgement_is_exactly_idempotent :
    acknowledge exactModel checkpoint1 warmCommit (.warmSuccess warmBounded)
      (view afterWarm) (evidence exactModel) = .ok checkpoint1 :=
  acknowledge_idempotent exactModel checkpoint0 checkpoint1 warmCommit
    (.warmSuccess warmBounded) (view afterWarm) (evidence exactModel)
    committed_result_recovers_without_rerun


/-- Exact local uncertainty attached to warm inspection in the concrete example. -/
theorem uncertain_warm_local_radius :
    localQRadius uncertainModel 1 .inspectWarm = 208 := by
  norm_num [localQRadius,valueRadius,Guarded.modelValueBudget,transportBudget,
    residualBudget,rewardError,probabilityError,rewardEnvelope,rewardRadius,
    probabilityRadius,uncertainModel,uncertainWarmRaw,uncertainColdRaw,
    setupBand,grossBand,probBand,rawQuote,NatBand.width,NatBand.singleton,
    RatBand.width,RatBand.singleton,ProbabilityBand.width,ProbabilityBand.singleton]

/-- The exact cold alternative carries no quote uncertainty in this example. -/
theorem uncertain_cold_local_radius :
    localQRadius uncertainModel 1 .generateCold = 0 := by
  norm_num [localQRadius,valueRadius,Guarded.modelValueBudget,transportBudget,
    residualBudget,rewardError,probabilityError,rewardEnvelope,rewardRadius,
    probabilityRadius,uncertainModel,uncertainWarmRaw,uncertainColdRaw,
    setupBand,grossBand,probBand,rawQuote,NatBand.width,NatBand.singleton,
    RatBand.width,RatBand.singleton,ProbabilityBand.width,ProbabilityBand.singleton]

/-- The point estimate prefers warm (120 > 60), but its certified lower value (-88)
falls below the exact cold value.  The executable example connects these numbers
to the actual nominal and robust selectors. -/
theorem uncertainty_changes_numerical_order :
    (60 : ℚ) < 120 ∧ (120 : ℚ) - 208 < 60 := by norm_num

/-- Singleton quote evidence makes all action-specific Q radii vanish. -/
theorem exact_all_local_radii_zero (h : Nat) (a : Action) :
    localQRadius exactModel h a = 0 :=
  exact_localQRadius exactModel exact_bands h a

end Komorebi.AVOC.Affine.RobustQuoteExamples
