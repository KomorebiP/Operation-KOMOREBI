import Mathlib.LinearAlgebra.FreeModule.PID
import Mathlib.LinearAlgebra.Matrix.Basis
import Mathlib.LinearAlgebra.Matrix.Nondegenerate
import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Basic
import Mathlib.LinearAlgebra.Dimension.Finrank

/-! Integral left and right basis changes for an injective square matrix over
a PID. The changes of basis are retained as actual general linear matrices. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SmithMatrix106
open Matrix Module
variable {ι R : Type*} [Fintype ι] [DecidableEq ι]
  [CommRing R] [IsDomain R] [IsPrincipalIdealRing R]

def basisGL (b : Basis ι R (ι → R)) : GL ι R where
  val := (Pi.basisFun R ι).toMatrix b
  inv := b.toMatrix (Pi.basisFun R ι)
  val_inv := by rw [Basis.toMatrix_mul_toMatrix, Basis.toMatrix_self]
  inv_val := by rw [Basis.toMatrix_mul_toMatrix, Basis.toMatrix_self]

omit [IsDomain R] [IsPrincipalIdealRing R] in
@[simp] theorem basisGL_apply (b : Basis ι R (ι → R)) (i j : ι) :
    basisGL b i j = b j i := by
  simp [basisGL, Basis.toMatrix_apply]

theorem exists_diagonal (A : Matrix ι ι R) (hA : A.det ≠ 0) :
    ∃ P Q : GL ι R, ∃ d : ι → R,
      (∀ i, d i ≠ 0) ∧ A = P.val * diagonal d * Q.val := by
  let f := A.mulVecLin
  have hf : Function.Injective f := Matrix.mulVec_injective_of_det_ne_zero hA
  let e := LinearEquiv.ofInjective f hf
  have hr : Module.finrank R (LinearMap.range f) = Module.finrank R (ι → R) :=
    e.finrank_eq.symm
  let b := (LinearMap.range f).smithNormalFormTopBasis (Pi.basisFun R ι) hr
  let c := (LinearMap.range f).smithNormalFormBotBasis (Pi.basisFun R ι) hr
  let d := (LinearMap.range f).smithNormalFormCoeffs (Pi.basisFun R ι) hr
  let q := c.map e.symm
  have hd : ∀ i, d i ≠ 0 :=
    (LinearMap.range f).smithNormalFormCoeffs_ne_zero (Pi.basisFun R ι) hr
  have hcol : ∀ j, A *ᵥ q j = d j • b j := by
    intro j
    have h := (LinearMap.range f).smithNormalFormBotBasis_def (Pi.basisFun R ι) hr j
    change (c j : ι → R) = d j • b j at h
    change f (e.symm (c j)) = d j • b j
    rw [LinearEquiv.ofInjective_symm_apply]
    exact h
  have heq : A * (basisGL q).val = (basisGL b).val * diagonal d := by
    ext i j
    rw [Matrix.mul_diagonal]
    have h := congrFun (hcol j) i
    simpa [Matrix.mul_apply, Matrix.mulVec, dotProduct, mul_comm] using h
  refine ⟨basisGL b, (basisGL q)⁻¹, d, hd, ?_⟩
  have h := congrArg (fun X : Matrix ι ι R => X * ((basisGL q)⁻¹).val) heq
  simpa only [Matrix.mul_assoc, Units.mul_inv, Matrix.mul_one] using h

end PaperXI.SmithMatrix106
