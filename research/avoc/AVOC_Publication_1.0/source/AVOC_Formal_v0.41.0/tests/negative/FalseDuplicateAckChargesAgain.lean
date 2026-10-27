import AVOC.RobustQuoteExamples
namespace Komorebi.AVOC.Affine.RobustQuoteNegative
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.StagedExamples
open Komorebi.AVOC.Affine.Factorization
open Komorebi.AVOC.Affine.FactorExamples
open Komorebi.AVOC.Affine.QuoteAuthority
open Komorebi.AVOC.Affine.RobustQuote
open Komorebi.AVOC.Affine.RobustQuoteRecovery
open Komorebi.AVOC.Affine.RobustQuoteExamples

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

private def validWarm : BoundedArtifact exactModel .warm where
  deployment := warmDeployment
  identity := quoteIdentity exactModel .warm
  identity_eq := rfl
  kind_eq := rfl
  source_eq := rfl
  setup_mem := by
    change (NatBand.singleton 133).Contains 133
    simp
  gross_mem := by
    change (RatBand.singleton 15000).Contains
      (LazyStaged.deploymentGross warmDeployment 1000)
    rw [RatBand.singleton_contains_iff]
    change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num

/-- MUST fail: duplicate acknowledgement returns the exact same checkpoint and sequence. -/
example :
    (match acknowledge exactModel checkpoint1 warmCommit (.warmSuccess validWarm)
      (view afterWarm) (evidence exactModel) with
      | .ok c => c.next
      | .error _ => 0) = 2 := by
  rfl
end Komorebi.AVOC.Affine.RobustQuoteNegative
