import AVOC.RobustQuoteExamples
namespace Komorebi.AVOC.Affine.RobustQuoteNegative
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.StagedExamples
open Komorebi.AVOC.Affine.Factorization
open Komorebi.AVOC.Affine.FactorExamples
open Komorebi.AVOC.Affine.QuoteAuthority
open Komorebi.AVOC.Affine.RobustQuote
open Komorebi.AVOC.Affine.RobustQuoteExamples

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

def wrongFeeDeployment : Deployment 4 4 := { warmDeployment with setup := 132 }

/-- MUST fail in `setup_mem`: 132 is outside the authorized singleton [133,133]. -/
def impossibleArtifact : BoundedArtifact exactModel .warm where
  deployment := wrongFeeDeployment
  identity := quoteIdentity exactModel .warm
  identity_eq := rfl
  kind_eq := rfl
  source_eq := rfl
  setup_mem := by
    change (NatBand.singleton 133).Contains 132
    norm_num [NatBand.Contains,NatBand.singleton]
  gross_mem := by
    change (RatBand.singleton 15000).Contains
      (LazyStaged.deploymentGross wrongFeeDeployment 1000)
    rw [RatBand.singleton_contains_iff]
    change (1000 : ℚ) * ((36 : ℚ) - executionCost (choose rankOneProgram rankOneChecked)) = 15000
    rw [rankOne_execution_costs.2.2]
    norm_num
end Komorebi.AVOC.Affine.RobustQuoteNegative
