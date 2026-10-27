import PaperXII.IntrinsicFitting
import Mathlib.LinearAlgebra.TensorProduct.Pi
import Mathlib.LinearAlgebra.TensorProduct.RightExactness

/-! Intrinsic Fitting ideals commute with arbitrary coefficient base change. -/
noncomputable section
namespace PaperXII
open Matrix TensorProduct DeterminantalIdeals
variable {R S : Type*} [CommRing R] [CommRing S] [Algebra R S]
variable {m n : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]

/-- The actual tensor base change of a relation map has the coefficient-mapped matrix. -/
theorem baseChange_matrix_coordinates (A : Matrix m n R) :
    (A.map (algebraMap R S)).mulVecLin.comp (piScalarRight R S S n).toLinearMap =
      (piScalarRight R S S m).toLinearMap.comp (A.mulVecLin.baseChange S) := by
  apply LinearMap.ext
  intro z
  induction z with
  | zero => simp
  | tmul s x =>
    ext i
    simp [LinearMap.comp_apply,piScalarRight_apply,piScalarRightHom_tmul,
      Matrix.mulVec,dotProduct,Algebra.smul_def,
      map_sum,map_mul]
    simp only [Finset.sum_mul,mul_assoc]
  | add x y hx hy => simp only [map_add,hx,hy]

variable {M : Type*} [AddCommGroup M] [Module R M]

/-- The actual quotient map after tensor base change and free-coordinate identification. -/
def baseChangeQuotient (π : (m → R) →ₗ[R] M) : (m → S) →ₗ[S] S ⊗[R] M :=
  (π.baseChange S).comp (piScalarRight R S S m).symm.toLinearMap

/-- Right exactness supplies a genuine presentation after arbitrary base change; no flatness. -/
theorem presents_baseChange (A : Matrix m n R) (π : (m → R) →ₗ[R] M)
    (h : Presents A π) : Presents (A.map (algebraMap R S)) (baseChangeQuotient (S := S) π) := by
  refine ⟨(π.baseChange_surjective S h.surjective).comp
    (piScalarRight R S S m).symm.surjective, ?_⟩
  have hex : Function.Exact (A.mulVecLin.baseChange S) (π.baseChange S) :=
    lTensor_exact S (LinearMap.exact_iff.mpr h.range_eq_ker.symm) h.surjective
  have hc := baseChange_matrix_coordinates (S := S) A
  have hq : (baseChangeQuotient (S := S) π).comp (piScalarRight R S S m).toLinearMap =
      (LinearEquiv.refl S (S ⊗[R] M)).toLinearMap.comp (π.baseChange S) := by
    apply LinearMap.ext
    intro x
    change (π.baseChange S) ((piScalarRight R S S m).symm ((piScalarRight R S S m) x)) =
      (π.baseChange S) x
    rw [LinearEquiv.symm_apply_apply]
  exact ((Function.Exact.iff_of_ladder_linearEquiv hc hq).mpr hex).linearMap_ker_eq.symm

/-- Paper XII, Claim 6.5: intrinsic Fitting ideals commute with arbitrary base change. -/
theorem fittingIdeal_baseChange [Module.FinitePresentation R M] (j : ℕ) :
    fittingIdeal S (S ⊗[R] M) j = Ideal.map (algebraMap R S) (fittingIdeal R M j) := by
  let P := chosenPresentation R M
  rw [fittingIdeal_eq_presentation (P.matrix.map (algebraMap R S))
    (baseChangeQuotient P.quotient) (presents_baseChange P.matrix P.quotient P.presents) j,
    fittingIdeal_eq_presentation P.matrix P.quotient P.presents j]
  exact minorIdeal_map (algebraMap R S) P.matrix _

end PaperXII
