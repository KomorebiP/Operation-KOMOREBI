import Komorebi.QuadraticTransportBounds

noncomputable section
set_option autoImplicit false
namespace Komorebi.QuadraticTransport
open MeasureTheory
open scoped ENNReal NNReal

section Marginals
variable {E : Type*} [MeasurableSpace E]

/-- For probability marginals the definition automatically ranges over probability plans.
No extra mass normalization has been omitted from the infimum. -/
theorem transportPlan_isProbabilityMeasure (μ ν : Measure E) [IsProbabilityMeasure μ]
    (γ : Measure (E × E)) (hγ : IsTransportPlan μ ν γ) : IsProbabilityMeasure γ := by
  constructor
  have h : (γ.map Prod.fst) Set.univ = 1 := by rw [hγ.1, measure_univ]
  simpa only [Measure.map_apply measurable_fst MeasurableSet.univ, Set.preimage_univ] using h
end Marginals

variable {E : Type*} [NormedAddCommGroup E] [MeasurableSpace E]
  [BorelSpace E] [SecondCountableTopology E]

/-- Diagonal coupling gives zero distance, including degenerate Gaussian cases. -/
theorem wasserstein2Sq_self (μ : Measure E) : wasserstein2Sq μ μ = 0 := by
  apply le_antisymm _ bot_le
  simpa using wasserstein2Sq_map_le μ id id measurable_id measurable_id

theorem wasserstein2_self (μ : Measure E) : wasserstein2 μ μ = 0 := by
  simp only [wasserstein2, wasserstein2Sq_self]
  norm_num

end Komorebi.QuadraticTransport
