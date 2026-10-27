import PaperX.ResidueLatticeWeights

/-! Weighted residue counts for actual nonzero integral ideals, with no geometric hypotheses. -/
set_option autoImplicit false
noncomputable section
open Ideal Module
open scoped nonZeroDivisors Real Classical Pointwise BigOperators
open NumberField
namespace PaperX.ResidueLattice
open PaperX.IdealClassQuantitative
variable (K : Type*) [Field K] [NumberField K]
  (M J : (Ideal (𝓞 K))⁰) [Fintype (IdealResidues K M J)]

/-- Weight each actual ideal-lattice point by its additive residue class. -/
def idealWeightedCount (w : IdealResidues K M J → ℂ) (t : ℝ) : ℂ :=
  ∑ c : IdealResidues K M J, w c * (idealFiberCount K M J c t : ℂ)

/-- The residue-weighted count is exactly the finite sum over actual cone lattice points. -/
theorem idealWeightedCount_eq_pointSum (w : IdealResidues K M J → ℂ) (t : ℝ) :
    idealWeightedCount K M J w t = latticePointSum (idealEuclideanLattice K M)
      (idealEuclideanLattice K J) (coneRegion K 1) w t :=
  weightedFiberCount_eq_pointSum _ _ (coneRegion_one_bounded K) w t

/-- Uniform arithmetic residue weights have their exact finite average as main coefficient. -/
theorem exists_idealWeighted_bound (h : (M : Ideal (𝓞 K)) ≤ J) :
    WeightedEstimate (idealFiberCount K M J)
      (fun t => t ^ Module.finrank ℚ K * (latticeDensity K J / Nat.card (IdealResidues K M J)))
      (fun t => t ^ (Module.finrank ℚ K - 1) + 1) :=
  weightedEstimate_of_uniform_bound _ _ _ (exists_idealFiber_bound K h)

/-- A zero finite average gives surface-order cancellation in an actual ideal lattice. -/
theorem exists_zeroMean_idealWeighted_bound (h : (M : Ideal (𝓞 K)) ≤ J) :
    ZeroMeanEstimate (idealFiberCount K M J) (fun t => t ^ (Module.finrank ℚ K - 1) + 1) :=
  (exists_idealWeighted_bound K M J h).zeroMean

end PaperX.ResidueLattice
