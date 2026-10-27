import PaperX.MatrixSpanBound
import PaperX.IntegralActionSpan

/-! A uniform determinant detector inferred from a fixed split irreducible template.
Irreducibility and the scalar-commutant property concern the actual fraction-field
representation. Full action span and a detecting depth are conclusions, not inputs. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SplitTemplateRigidity
open PaperX.RepresentationLimits PaperX.RepresentationClasses PaperX.IntegralActionSpan
open scoped MonoidAlgebra
variable {R K G n : Type*} [CommRing R] [IsDomain R]
  [IsDiscreteValuationRing R] [Field K] [Algebra R K] [IsFractionRing R K]
  [Group G] [Fintype n] [DecidableEq n]

/-- One determinant depth works for every integral member of the field-isomorphism
class of a fixed split irreducible template. The source group need not be finite. -/
theorem uniform_detector_of_split_irreducible (τ : MatrixRep R G n)
    [Representation.IsIrreducible
      (matrixRepresentation (changeCoefficients (algebraMap R K) τ))]
    (hscalar : Function.Surjective (algebraMap K (Module.End K[G]
      (matrixRepresentation (changeCoefficients (algebraMap R K) τ)).asModule)))
    (π : R) (hπ : Irreducible π) :
    ∃ c : ℕ, ∀ ρ : MatrixRep R G n,
      Conjugate (changeCoefficients (algebraMap R K) τ)
        (changeCoefficients (algebraMap R K) ρ) →
      ∃ P : Matrix n n R, (∀ g, ρ g * P = P * τ g) ∧
        (P.map (Ideal.Quotient.mk
          ((Ideal.span {π}) ^ (c * Fintype.card n + 1)))).det ≠ 0 := by
  have hs := matrix_span_eq_top_of_split_irreducible
    (changeCoefficients (algebraMap R K) τ) hscalar
  exact MatrixSpanBound.uniform_detector_for_conjugates τ π hπ hs

end PaperX.SplitTemplateRigidity
