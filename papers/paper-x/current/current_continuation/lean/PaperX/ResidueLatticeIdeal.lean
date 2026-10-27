import PaperX.ResidueLatticeFibers
import PaperX.IdealClassQuantitativeGeometry

/-! Uniform actual additive-residue counts inside integral ideal lattices. -/
set_option autoImplicit false
noncomputable section
open Ideal MeasureTheory Module
open scoped nonZeroDivisors Real Classical Pointwise
open NumberField NumberField.mixedEmbedding NumberField.mixedEmbedding.euclidean
namespace PaperX.ResidueLattice
open PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- Inclusion of integral ideals gives the same inclusion of their actual Euclidean lattices. -/
theorem idealLattice_mono {M J : (Ideal (𝓞 K))⁰} (h : (M : Ideal (𝓞 K)) ≤ J) :
    idealEuclideanLattice K M ≤ idealEuclideanLattice K J := by
  intro x hx
  change toMixed K x ∈ idealLattice K (FractionalIdeal.mk0 K J)
  change toMixed K x ∈ idealLattice K (FractionalIdeal.mk0 K M) at hx
  rw [mem_idealLattice] at hx ⊢
  obtain ⟨a, ha, he⟩ := hx
  refine ⟨a, ?_, he⟩
  rw [FractionalIdeal.coe_mk0] at ha ⊢
  obtain ⟨y, hy, rfl⟩ := (FractionalIdeal.mem_coeIdeal _).mp ha
  exact FractionalIdeal.mem_coeIdeal_of_mem _ (h hy)

/-- The actual finite additive quotient for two integral ideal lattices. -/
abbrev IdealResidues (M J : (Ideal (𝓞 K))⁰) :=
  Residues (idealEuclideanLattice K M) (idealEuclideanLattice K J)

/-- The exact count of lattice points in one additive residue of the unit fundamental cone. -/
def idealFiberCount (M J : (Ideal (𝓞 K))⁰) (c : IdealResidues K M J) (t : ℝ) : ℕ :=
  fiberCount (idealEuclideanLattice K M) (idealEuclideanLattice K J) (coneRegion K 1) c t

/-- The residue space for an inclusion of nonzero integral ideals is finite. -/
theorem finite_idealResidues {M J : (Ideal (𝓞 K))⁰} (h : (M : Ideal (𝓞 K)) ≤ J) :
    Finite (IdealResidues K M J) :=
  finite_residues _ _ (idealLattice_mono K h)

/-- Every actual residue of one nonzero ideal modulo another has a common surface-order estimate.
All geometric and lattice hypotheses are supplied internally for the actual number field. -/
theorem exists_idealFiber_bound {M J : (Ideal (𝓞 K))⁰} (h : (M : Ideal (𝓞 K)) ≤ J) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ (c : IdealResidues K M J) (t : ℝ), 1 ≤ t →
      |(idealFiberCount K M J c t : ℝ) -
        t ^ Module.finrank ℚ K * (latticeDensity K J / Nat.card (IdealResidues K M J))| ≤
        B * (t ^ (Module.finrank ℚ K - 1) + 1) := by
  let b := Module.Free.chooseBasis ℤ (idealEuclideanLattice K M)
  obtain ⟨A⟩ := ideal_cone_boundaryAtlas K M b
  obtain ⟨B, hB0, hB⟩ := exists_fiber_discrepancy_bound
    (idealEuclideanLattice K M) (idealEuclideanLattice K J) (idealLattice_mono K h) b
    (coneRegion_one_measurable K) (coneRegion_one_bounded K) A
  refine ⟨B, hB0, fun c t ht => ?_⟩
  simpa only [ideal_basis_card K b, idealFiberCount, latticeDensity] using hB c t ht

end PaperX.ResidueLattice
