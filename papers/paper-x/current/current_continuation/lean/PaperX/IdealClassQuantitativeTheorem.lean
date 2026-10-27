import PaperX.IdealClassQuantitativeGeometry
import PaperX.LatticeCountingFull

/-!
# Quantitative counting in every ordinary ideal class of a number field

The boundary atlas, lattice estimate, and arithmetic attachment are all
constructed for the actual objects. No quantitative counting assumption remains.
-/
set_option autoImplicit false
noncomputable section

open Ideal MeasureTheory Module Filter Asymptotics
open scoped nonZeroDivisors Real Classical Pointwise
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.euclidean NumberField.mixedEmbedding.fundamentalCone
open NumberField.Units

namespace PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- A surface-order estimate for the actual ideal lattice and unit fundamental cone. -/
theorem exists_ideal_lattice_bound (J : (Ideal (𝓞 K))⁰) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ t : ℝ, 1 ≤ t →
      |(Nat.card (t • coneRegion K 1 ∩ idealEuclideanLattice K J :
        Set (euclidean.mixedSpace K)) : ℝ) -
        latticeDensity K J * t ^ Module.finrank ℚ K| ≤
          B * (t ^ (Module.finrank ℚ K - 1) + 1) := by
  let b := Module.Free.chooseBasis ℤ (idealEuclideanLattice K J)
  obtain ⟨A⟩ := ideal_cone_boundaryAtlas K J b
  obtain ⟨B, hB0, hB⟩ := PaperX.LatticeCountingTransport.exists_lattice_discrepancy_bound
    (idealEuclideanLattice K J) b (coneRegion_one_measurable K) (coneRegion_one_bounded K) A
  refine ⟨B, hB0, fun t ht => ?_⟩
  have h := hB 0 t ht
  simpa only [zero_add, Set.image_smul, ideal_basis_card K b, latticeDensity, mul_comm] using h

/-- Every ordinary ideal class has the quantitative asymptotic with its explicit common residue. -/
theorem classCount_isBigO (C : ClassGroup (𝓞 K)) :
    (fun s : ℝ => (classCount K C s : ℝ) - classResidue K * s) =O[atTop]
      (fun s : ℝ => s ^ countExponent K) := by
  obtain ⟨J, hJ⟩ := ClassGroup.mk0_surjective C⁻¹
  obtain ⟨B, hB0, hB⟩ := exists_ideal_lattice_bound K J
  exact class_isBigO_of_dilation_bound K hJ hB0 hB

/-- The same result as a bound valid at every threshold at least one. -/
theorem exists_classCount_bound (C : ClassGroup (𝓞 K)) :
    ∃ M : ℝ, 0 ≤ M ∧ ∀ s : ℝ, 1 ≤ s →
      |(classCount K C s : ℝ) - classResidue K * s| ≤ M * s ^ countExponent K := by
  obtain ⟨J, hJ⟩ := ClassGroup.mk0_surjective C⁻¹
  obtain ⟨B, hB0, hB⟩ := exists_ideal_lattice_bound K J
  refine ⟨B / torsionOrder K *
    ((absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1), ?_, ?_⟩
  · exact mul_nonneg (div_nonneg hB0 (torsionOrder_cast_pos K).le)
      (add_nonneg (Real.rpow_nonneg (Nat.cast_nonneg _) _) zero_le_one)
  · exact class_bound_of_norm_bound K hJ hB0 (norm_bound_of_dilation_bound K J B hB)

end PaperX.IdealClassQuantitative
