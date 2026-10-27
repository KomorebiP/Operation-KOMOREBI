module
public import SmallCoreNorms
import all SmallCoreNorms
public import Mathlib.Analysis.InnerProductSpace.PiL2
public import Mathlib.Analysis.InnerProductSpace.Subspace
public import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
public import Mathlib.Tactic
/-! Author: Komorebi P. Orthonormal kernel coordinates and diagonal projection weights. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {n r : Type*} [Fintype n] [Fintype r] [DecidableEq n] [DecidableEq r]
noncomputable def subspaceFrame (S : Submodule ℂ (EuclideanSpace ℂ n)) :
    Matrix n (Fin (Module.finrank ℂ S)) ℂ :=
  LinearMap.toMatrix (stdOrthonormalBasis ℂ S).toBasis
    (EuclideanSpace.basisFun n ℂ).toBasis S.subtype

omit [DecidableEq n] in
theorem subspaceFrame_apply (S : Submodule ℂ (EuclideanSpace ℂ n))
    (i : n) (j : Fin (Module.finrank ℂ S)) :
    subspaceFrame S i j = (stdOrthonormalBasis ℂ S j : EuclideanSpace ℂ n) i := by
  simp [subspaceFrame,LinearMap.toMatrix_apply]

omit [DecidableEq n] in
theorem subspaceFrame_isometry (S : Submodule ℂ (EuclideanSpace ℂ n)) :
    (subspaceFrame S)ᴴ * subspaceFrame S = 1 := by
  ext i j
  have h := orthonormal_iff_ite.mp (stdOrthonormalBasis ℂ S).orthonormal i j
  simpa only [Submodule.coe_inner,PiLp.inner_apply,RCLike.inner_apply,
    Matrix.mul_apply,Matrix.conjTranspose_apply,subspaceFrame_apply,Matrix.one_apply,
    Complex.star_def,mul_comm] using h

noncomputable def kernelSpace (B : Matrix n n ℂ) : Submodule ℂ (EuclideanSpace ℂ n) :=
  LinearMap.ker (Matrix.toEuclideanLin B)
noncomputable def kernelDim (B : Matrix n n ℂ) := Module.finrank ℂ (kernelSpace B)
noncomputable def kernelFrame (B : Matrix n n ℂ) : Matrix n (Fin (kernelDim B)) ℂ :=
  subspaceFrame (kernelSpace B)

theorem kernelFrame_isometry (B : Matrix n n ℂ) : (kernelFrame B)ᴴ*kernelFrame B=1 :=
  subspaceFrame_isometry _

set_option backward.isDefEq.respectTransparency false in
theorem mul_kernelFrame (B : Matrix n n ℂ) : B*kernelFrame B=0 := by
  unfold kernelFrame subspaceFrame
  conv_lhs => lhs; rw [←LinearMap.toMatrix_toLin (EuclideanSpace.basisFun n ℂ).toBasis
    (EuclideanSpace.basisFun n ℂ).toBasis B]
  rw [←LinearMap.toMatrix_comp]
  have he : Matrix.toLin (EuclideanSpace.basisFun n ℂ).toBasis
      (EuclideanSpace.basisFun n ℂ).toBasis B ∘ₗ (kernelSpace B).subtype = 0 := by
    ext x i
    exact congrArg (fun z : EuclideanSpace ℂ n => z i) x.property
  rw [he,map_zero]

theorem kernel_rank_nullity (B : Matrix n n ℂ) : B.rank+kernelDim B=Fintype.card n := by
  have h := LinearMap.finrank_range_add_finrank_ker (Matrix.toEuclideanLin B)
  have hr := Matrix.rank_eq_finrank_range_toLin B
    (EuclideanSpace.basisFun n ℂ).toBasis (EuclideanSpace.basisFun n ℂ).toBasis
  rw [←Matrix.toEuclideanLin_eq_toLin_orthonormal] at hr
  simpa only [←hr,kernelSpace,kernelDim,finrank_euclideanSpace] using h

noncomputable def rowWeight (Q : Matrix n r ℂ) (i : n) : ℝ := ∑ j, ‖Q i j‖^2

omit [Fintype n] [DecidableEq n] [DecidableEq r] in
theorem rowWeight_nonneg (Q : Matrix n r ℂ) (i : n) : 0 ≤ rowWeight Q i :=
  Finset.sum_nonneg (fun _ _ => sq_nonneg _)

omit [DecidableEq n] in
theorem rowWeight_sum (Q : Matrix n r ℂ) (hQ : Qᴴ*Q=1) :
    ∑ i, rowWeight Q i = Fintype.card r := by
  have h : (Matrix.trace (Qᴴ*Q)).re = Fintype.card r := by simp [hQ]
  have he : (Matrix.trace (Qᴴ*Q)).re = ∑ i, rowWeight Q i := by
    simp only [rowWeight,Matrix.trace,Matrix.diag,Matrix.mul_apply,Matrix.conjTranspose_apply,
      Complex.re_sum,Complex.star_def,Complex.conj_mul',←Complex.ofReal_pow,Complex.ofReal_re]
    exact Finset.sum_comm
  rw [he] at h
  exact h

section Operator
open scoped Matrix.Norms.L2Operator
/-- The diagonal weights of an orthogonal projection lie in [0,1]. -/
theorem rowWeight_le_one (Q : Matrix n r ℂ) (hQ : Qᴴ*Q=1) (i : n) : rowWeight Q i ≤ 1 := by
  let x : EuclideanSpace ℂ n := WithLp.toLp 2 (Pi.single i (1:ℂ))
  let y : EuclideanSpace ℂ r := (EuclideanSpace.equiv r ℂ).symm (Qᴴ *ᵥ x)
  have hb : ‖Qᴴ‖ ≤ 1 := by rw [Matrix.l2_opNorm_conjTranspose]; exact spectral_isometry_bound Q hQ
  have hn : ‖y‖ ≤ ‖Qᴴ‖ := by simpa [x,y] using Matrix.l2_opNorm_mulVec Qᴴ x
  have he : ‖y‖^2 = rowWeight Q i := by
    rw [EuclideanSpace.norm_sq_eq]
    simp [y,x,rowWeight,Matrix.mulVec_single_one,Matrix.conjTranspose_apply]
  nlinarith [norm_nonneg y]

end Operator
end KomorebiPaperVIII.SmallCore
