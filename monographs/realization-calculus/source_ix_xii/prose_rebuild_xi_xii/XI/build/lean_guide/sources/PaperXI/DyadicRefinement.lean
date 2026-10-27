import PaperXI.DyadicCoordinates
import PaperXI.DyadicTranslation

/-! Translation and opposite phases for all refinements of the actual
coordinate symplectic form, with the Arf value evaluated on basis vectors. -/
noncomputable section
set_option autoImplicit false
namespace PaperXI.DyadicRefinement
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates
variable {ι : Type*} [Fintype ι]

def basisArf (q : Refinement (symplectic (ι := ι))) : F2 :=
  ∑ i, q.value (firstAxis i) * q.value (secondAxis i)

@[simp] theorem basisArf_coordinateRefinement (a : ι → F2 × F2) :
    basisArf (coordinateRefinement a) = arf a := by
  simp [basisArf, coordinateRefinement, arf]

theorem translation_refinement (q : Refinement (symplectic (ι := ι)))
    (v : ι → F2 × F2) :
    addLinear q (symplectic v) =
      coordinateRefinement (translate (refinementCoefficients q) v) := by
  ext x
  change q.value x + symplectic v x = quadratic _ x
  rw [refinement_coordinate_formula, quadratic_translate]
  rfl

theorem arf_translation (q : Refinement (symplectic (ι := ι)))
    (v : ι → F2 × F2) :
    basisArf (addLinear q (symplectic v)) = basisArf q + q.value v := by
  rw [translation_refinement, basisArf_coordinateRefinement, arf_translate,
    refinement_arf_basis_formula, ← refinement_coordinate_formula]
  rfl

theorem opposite_refinements (i : ι) :
    ∃ q r : Refinement (symplectic (ι := ι)),
      basisArf q = 0 ∧ basisArf r = 1 ∧
      (∑ x, sign (r.value x)) = -(∑ x, sign (q.value x)) := by
  refine ⟨coordinateRefinement 0, coordinateRefinement (anisotropic i), ?_, ?_, ?_⟩
  · simp
  · simp [arf_anisotropic]
  · exact opposite_gauss i

theorem sign_eq_neg_one_pow (t : F2) : sign t = (-1 : ℤ) ^ t.val := by
  fin_cases t <;> decide

end PaperXI.DyadicRefinement
