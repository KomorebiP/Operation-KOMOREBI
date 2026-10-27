import PaperX.IdealClassQuantitativeTransfer
import PaperX.LatticeCountingTransport
import PaperX.CountingBoundaryTransport

/-! Actual geometric hypotheses for counting the lattice of a nonzero integral ideal. -/
set_option autoImplicit false
noncomputable section

open Ideal MeasureTheory Module
open scoped nonZeroDivisors Real Classical
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.euclidean NumberField.mixedEmbedding.fundamentalCone

namespace PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- The actual Euclidean norm cone is bounded. -/
theorem coneRegion_one_bounded : Bornology.IsBounded (coneRegion K 1) := by
  rw [coneRegion_one]
  exact (toMixed K).antilipschitz.isBounded_preimage (isBounded_normLeOne K)

/-- The actual Euclidean norm cone is measurable. -/
theorem coneRegion_one_measurable : MeasurableSet (coneRegion K 1) := by
  rw [coneRegion_one]
  exact (toMixed K).continuous.measurable (measurableSet_normLeOne K)

/-- An integral ideal lattice has exactly the number-field degree many basis vectors. -/
theorem ideal_basis_card {J : (Ideal (𝓞 K))⁰} {ι : Type*} [Fintype ι]
    (b : Basis ι ℤ (idealEuclideanLattice K J)) :
    Fintype.card ι = Module.finrank ℚ K := by
  rw [← Module.finrank_eq_card_basis b, ZLattice.rank ℝ, euclidean.finrank]

/-- The actual cone admits a dimension-correct finite boundary atlas in coordinates
of any integral basis of the actual ideal lattice. -/
theorem ideal_cone_boundaryAtlas (J : (Ideal (𝓞 K))⁰) {ι : Type*} [Fintype ι]
    (b : Basis ι ℤ (idealEuclideanLattice K J)) :
    Nonempty (PaperX.LatticeCounting.LipschitzBoundaryAtlas ι
      (PaperX.LatticeCountingTransport.coordinates (idealEuclideanLattice K J) b ''
        coneRegion K 1)) := by
  let e := (toMixed K).symm.trans
    (PaperX.LatticeCountingTransport.coordinates (idealEuclideanLattice K J) b)
  have h := PaperX.CountingBoundaryPolar.nonempty_boundaryAtlas_image K e (ideal_basis_card K b)
  convert h using 1
  rw [coneRegion_one, ← (toMixed K).image_symm_eq_preimage, ← Set.image_comp]
  rfl

end PaperX.IdealClassQuantitative
