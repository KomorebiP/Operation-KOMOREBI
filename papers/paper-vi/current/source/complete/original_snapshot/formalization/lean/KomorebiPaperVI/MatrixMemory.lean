import KomorebiPaperVI.NonnormalMemory
import Mathlib.Analysis.CStarAlgebra.Matrix

/-! Author: Komorebi P. The literal rectangular matrix memory/self-energy identity. -/
namespace KomorebiPaperVI.MatrixMemory
open Set MeasureTheory
open KomorebiPaperVI.Semigroups KomorebiPaperVI.ComplexMemory
open scoped Matrix.Norms.L2Operator
set_option backward.isDefEq.respectTransparency false
variable {I J : Type*} [Fintype I] [Fintype J] [DecidableEq I] [DecidableEq J]

noncomputable def sandwich (U : Matrix I J ℂ) (V : Matrix J I ℂ) :
    Matrix J J ℂ →L[ℂ] Matrix I I ℂ :=
  ( { toFun := fun B => U*B*V
      map_add' := fun A B => by simp [Matrix.mul_add,Matrix.add_mul]
      map_smul' := fun c A => by simp [Matrix.mul_smul,Matrix.smul_mul] } :
    Matrix J J ℂ →ₗ[ℂ] Matrix I I ℂ).toContinuousLinearMap

theorem rectangular_memory_self_energy (A : Matrix J J ℂ)
    (U : Matrix I J ℂ) (V : Matrix J I ℂ) (z : ℂ)
    (hz : ∀ μ∈spectrum ℂ A,μ.re < z.re) :
    IntegrableOn (fun t : ℝ => Complex.exp (-z*t) • (U*transfer A t*V)) (Ioi 0) ∧
    (∫ t : ℝ in Ioi 0,Complex.exp (-z*t) • (U*transfer A t*V))=
      U*(Matrix.scalar J z-A)⁻¹*V := by
  have h := NonnormalMemory.spectral_laplace_inverse A z hz
  have he : (fun t : ℝ => Complex.exp (-z*t) • (U*transfer A t*V))=
      (fun t => sandwich U V (damped A z t)) := by
    ext t i j
    simp [sandwich,damped]
  rw [he]
  refine ⟨(sandwich U V).integrable_comp h.1,?_⟩
  rw [(sandwich U V).integral_comp_comm h.1,h.2.2]
  change U*Ring.inverse (algebraMap ℂ (Matrix J J ℂ) z-A)*V=_
  rw [Matrix.nonsing_inv_eq_ringInverse]
  rfl

end KomorebiPaperVI.MatrixMemory
