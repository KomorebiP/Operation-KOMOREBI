import PaperX.MatrixWitnessLimits
import PaperX.RepresentationClasses
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-! A nonzero determinant at one fixed finite precision certifies a genuinely
invertible comparison matrix over an injectively containing coefficient field.
The matrix is constructed before the conclusion of conjugacy is obtained. -/
set_option autoImplicit false

namespace PaperX.CertificateIsomorphisms
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.MatrixWitnessLimits

variable {R : Type*} [CommRing R] (I : Ideal R)
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- A single finite-depth nonvanishing certificate detects a nonzero integral
determinant.  The determinant need not be an integral unit. -/
theorem det_ne_zero_of_reduction (P : Matrix ι ι R) (d : ℕ)
    (h : (P.map (Ideal.Quotient.mk (I ^ d))).det ≠ 0) : P.det ≠ 0 := by
  intro hP
  apply h
  change ((Ideal.Quotient.mk (I ^ d)).mapMatrix P).det = 0
  rw [← RingHom.map_det, hP, map_zero]

/-- Applying the detector to the actual reconstructed witness. -/
theorem reconstructed_det_ne_zero [IsAdicComplete I R]
    (P : MatrixFamily R I ι) (d : ℕ) (h : (P.maps d).det ≠ 0) :
    (reconstructMatrix I P).det ≠ 0 := by
  apply det_ne_zero_of_reduction I (reconstructMatrix I P) d
  rw [reconstructMatrix_reduces]
  exact h

variable {K : Type*} [Field K]

/-- The field image is an actual matrix unit; this uses injectivity and the
determinant criterion, not a supplied inverse matrix. -/
theorem mapped_matrix_isUnit (inc : R →+* K) (hinj : Function.Injective inc)
    (P : Matrix ι ι R) (hP : P.det ≠ 0) : IsUnit (P.map inc) := by
  apply (Matrix.isUnit_iff_isUnit_det _).mpr
  apply isUnit_iff_ne_zero.mpr
  change (inc.mapMatrix P).det ≠ 0
  rw [← RingHom.map_det]
  intro h
  exact hP (hinj (h.trans (map_zero inc).symm))

variable {G : Type*} [Group G]

/-- A nonsingular integral intertwiner becomes an explicit conjugating unit
over the coefficient field.  Its value is exactly the image of the supplied
matrix. -/
theorem exists_conjugating_unit (inc : R →+* K) (hinj : Function.Injective inc)
    (ρ τ : MatrixRep R G ι) (P : Matrix ι ι R) (hP : P.det ≠ 0)
    (h : ∀ g, ρ g * P = P * τ g) :
    ∃ u : (Matrix ι ι K)ˣ, (u : Matrix ι ι K) = P.map inc ∧
      conjugate u (changeCoefficients inc τ) = changeCoefficients inc ρ := by
  obtain ⟨u, hu⟩ := mapped_matrix_isUnit inc hinj P hP
  refine ⟨u, hu, ?_⟩
  apply MonoidHom.ext
  intro g
  have heq : changeCoefficients inc ρ g * (u : Matrix ι ι K) =
      (u : Matrix ι ι K) * changeCoefficients inc τ g := by
    rw [hu]
    have hρ : changeCoefficients inc ρ g = (ρ g).map inc := by ext i j; rfl
    have hτ : changeCoefficients inc τ g = (τ g).map inc := by ext i j; rfl
    rw [hρ, hτ]
    simpa only [Matrix.map_mul] using congrArg (fun M => M.map inc) (h g)
  change (u : Matrix ι ι K) * changeCoefficients inc τ g *
    (↑(u⁻¹) : Matrix ι ι K) = _
  rw [← heq, mul_assoc]
  simp

/-- A finite-depth determinant certificate suffices for the full field-valued
representation conjugacy conclusion. -/
theorem conjugate_of_finite_certificate (inc : R →+* K)
    (hinj : Function.Injective inc) (ρ τ : MatrixRep R G ι)
    (P : Matrix ι ι R) (d : ℕ)
    (hP : (P.map (Ideal.Quotient.mk (I ^ d))).det ≠ 0)
    (h : ∀ g, ρ g * P = P * τ g) :
    Conjugate (changeCoefficients inc τ) (changeCoefficients inc ρ) := by
  obtain ⟨u, _, hu⟩ := exists_conjugating_unit inc hinj ρ τ P
    (det_ne_zero_of_reduction I P d hP) h
  exact ⟨u, hu⟩

end PaperX.CertificateIsomorphisms
