import PaperX.NormSignGeometry
import PaperX.ResidueLatticeIdeal
import PaperX.ResidueLatticeWeights

/-! Actual additive residue counts in each sign portion of the number-field cone. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NormSignGeometry
open Set MeasureTheory Module Ideal
open NumberField NumberField.mixedEmbedding NumberField.mixedEmbedding.euclidean
open PaperX.IdealClassQuantitative PaperX.ResidueLattice
open scoped nonZeroDivisors Classical Pointwise

variable (K : Type*) [Field K] [NumberField K]

/-- The actual sign portion, in the Euclidean mixed coordinates used for ideal lattices. -/
def signRegion (positive : Bool) : Set (euclidean.mixedSpace K) :=
  toMixed K ⁻¹' signCone K positive

theorem signRegion_measurable (positive : Bool) : MeasurableSet (signRegion K positive) :=
  (toMixed K).continuous.measurable (signCone_measurable K positive)

theorem signRegion_bounded (positive : Bool) : Bornology.IsBounded (signRegion K positive) :=
  (toMixed K).antilipschitz.isBounded_preimage (signCone_bounded K positive)

/-- The sign-region boundary atlas in any basis of an actual ideal lattice. -/
theorem nonempty_signRegionAtlas (M : (Ideal (𝓞 K))⁰) {ι : Type*} [Fintype ι]
    (b : Basis ι ℤ (idealEuclideanLattice K M)) (positive : Bool) :
    Nonempty (LatticeCounting.LipschitzBoundaryAtlas ι
      (LatticeCountingTransport.coordinates (idealEuclideanLattice K M) b ''
        signRegion K positive)) := by
  let e := (toMixed K).symm.trans
    (LatticeCountingTransport.coordinates (idealEuclideanLattice K M) b)
  have h := signConeAtlas K e (ideal_basis_card K b) positive
  apply Nonempty.intro
  convert h using 1
  rw [signRegion, ← (toMixed K).image_symm_eq_preimage, ← Set.image_comp]
  rfl

/-- Actual additive residue points with a prescribed real norm sign. -/
def signFiberCount (M J : (Ideal (𝓞 K))⁰) (positive : Bool)
    (c : IdealResidues K M J) (t : ℝ) : ℕ :=
  fiberCount (idealEuclideanLattice K M) (idealEuclideanLattice K J)
    (signRegion K positive) c t

/-- Every residue has the same sign-region density; the constant is uniform in the residue. -/
theorem exists_signFiber_bound {M J : (Ideal (𝓞 K))⁰}
    (h : (M : Ideal (𝓞 K)) ≤ J) (positive : Bool) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ (c : IdealResidues K M J) (t : ℝ), 1 ≤ t →
      |(signFiberCount K M J positive c t : ℝ) -
        t ^ Module.finrank ℚ K *
          ((volume.real (signRegion K positive) / ZLattice.covolume (idealEuclideanLattice K J)) /
            Nat.card (IdealResidues K M J))| ≤
        B * (t ^ (Module.finrank ℚ K - 1) + 1) := by
  let b := Module.Free.chooseBasis ℤ (idealEuclideanLattice K M)
  obtain ⟨A⟩ := nonempty_signRegionAtlas K M b positive
  obtain ⟨B, hB0, hB⟩ := exists_fiber_discrepancy_bound
    (idealEuclideanLattice K M) (idealEuclideanLattice K J) (idealLattice_mono K h) b
    (signRegion_measurable K positive) (signRegion_bounded K positive) A
  refine ⟨B, hB0, fun c t ht => ?_⟩
  simpa only [ideal_basis_card K b, signFiberCount] using hB c t ht

/-- Zero-mean finite residue weights have a surface-order bound separately on each sign region. -/
theorem exists_sign_zeroMean_bound {M J : (Ideal (𝓞 K))⁰}
    (h : (M : Ideal (𝓞 K)) ≤ J) [Fintype (IdealResidues K M J)] (positive : Bool) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ (w : IdealResidues K M J → ℂ), (∑ c : IdealResidues K M J, w c) = 0 →
      ∀ t : ℝ, 1 ≤ t →
        ‖weightedFiberCount (idealEuclideanLattice K M) (idealEuclideanLattice K J)
          (signRegion K positive) w t‖ ≤
          (∑ c : IdealResidues K M J, ‖w c‖) * B * (t ^ (Module.finrank ℚ K - 1) + 1) := by
  let b := Module.Free.chooseBasis ℤ (idealEuclideanLattice K M)
  obtain ⟨A⟩ := nonempty_signRegionAtlas K M b positive
  obtain ⟨B, hB0, hB⟩ := exists_zeroMean_weightedFiber_bound
    (idealEuclideanLattice K M) (idealEuclideanLattice K J) (idealLattice_mono K h) b
    (signRegion_measurable K positive) (signRegion_bounded K positive) A
  refine ⟨B, hB0, fun w hw t ht => ?_⟩
  simpa only [ideal_basis_card K b, weightedFiberCount] using hB w hw t ht

end PaperX.NormSignGeometry
