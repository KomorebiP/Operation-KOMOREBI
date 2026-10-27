import KomorebiPaperVI.MemoryLaplace
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Basic
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Instances
import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.ExpLog.Basic
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Isometric

/-! Author: Komorebi P. Literal complex Laplace inversion and memory/self-energy.
The general nonnormal spectral-abscissa-to-growth implication is not asserted here. -/
namespace KomorebiPaperVI.ComplexMemory
open Set Filter MeasureTheory NormedSpace
open KomorebiPaperVI.Semigroups
set_option backward.isDefEq.respectTransparency false
attribute [local instance] IsStarNormal.instContinuousFunctionalCalculus
variable {R : Type*} [CStarAlgebra R]

noncomputable def damped (A : R) (z : ℂ) (t : ℝ) : R := Complex.exp (-z*t) • transfer A t

theorem damped_eq_shifted (A : R) (z : ℂ) (t : ℝ) :
    damped A z t=transfer (A-algebraMap ℂ R z) t := by
  let : NormedAlgebra ℚ R := NormedAlgebra.restrictScalars ℚ ℝ R
  have he : t • (A-algebraMap ℂ R z)=algebraMap ℂ R (-z*t)+t • A := by
    simp only [smul_sub,Algebra.algebraMap_eq_smul_one,neg_mul,neg_smul]
    rw [← smul_assoc,Complex.real_smul,mul_comm (t:ℂ) z]
    abel
  simp only [damped,transfer]
  rw [he,exp_add_of_commute (Algebra.commutes _ _),← algebraMap_exp_comm,
    ← Complex.exp_eq_exp_ℂ,Algebra.algebraMap_eq_smul_one,smul_mul_assoc,one_mul]

theorem shifted_decay (A : R) (z : ℂ) (M w : ℝ) (_hz : w < z.re)
    (hA : ∀ t,0 ≤ t → ‖transfer A t‖ ≤ M*Real.exp (w*t)) :
    ∀ t,0 ≤ t → ‖transfer (A-algebraMap ℂ R z) t‖ ≤ M*Real.exp (-(z.re-w)*t) := by
  intro t ht
  rw [← damped_eq_shifted,damped,norm_smul,Complex.norm_exp]
  have hre : (-z*(t:ℂ)).re= -z.re*t := by simp
  rw [hre]
  calc
    _ ≤ Real.exp (-z.re*t)*(M*Real.exp (w*t)) := mul_le_mul_of_nonneg_left (hA t ht) (Real.exp_pos _).le
    _ = _ := by
      rw [mul_left_comm,← Real.exp_add]
      congr 2
      ring

theorem integral_transfer_right (B : R) (M d : ℝ) (hd : 0 < d)
    (hB : ∀ t,0 ≤ t → ‖transfer B t‖ ≤ M*Real.exp (-d*t)) :
    (∫ t in Ioi 0,transfer B t)*B= -1 := by
  have hi := MemoryLaplace.decay_integrable B M d hd hB
  have hprod : IntegrableOn (fun t => transfer B t*B) (Ioi 0) :=
    ((ContinuousLinearMap.mul ℝ R).flip B).integrable_comp hi
  have hf := integral_Ioi_of_hasDerivAt_of_tendsto'
    (fun t (_ : t∈Ici (0:ℝ)) => transfer_derivative_right B t)
    hprod (MemoryLaplace.decay_tendsto_zero B M d hd hB)
  rw [integral_mul_const_of_integrable hi,transfer_zero,zero_sub] at hf
  exact hf

theorem laplace_inverse (A : R) (z : ℂ) (M w : ℝ) (hz : w < z.re)
    (hA : ∀ t,0 ≤ t → ‖transfer A t‖ ≤ M*Real.exp (w*t)) :
    IntegrableOn (damped A z) (Ioi 0) ∧
    IsUnit (algebraMap ℂ R z-A) ∧
    (∫ t in Ioi 0,damped A z t)=Ring.inverse (algebraMap ℂ R z-A) := by
  have hd : 0 < z.re-w := sub_pos.mpr hz
  have hB := shifted_decay A z M w hz hA
  have hi := MemoryLaplace.decay_integrable (A-algebraMap ℂ R z) M (z.re-w) hd hB
  have he : damped A z=transfer (A-algebraMap ℂ R z) := funext (damped_eq_shifted A z)
  rw [he]
  have hl := MemoryLaplace.integral_generator_transfer (A-algebraMap ℂ R z) M (z.re-w) hd hB
  have hr := integral_transfer_right (A-algebraMap ℂ R z) M (z.re-w) hd hB
  have hn : algebraMap ℂ R z-A= -(A-algebraMap ℂ R z) := by abel
  have hl' : (algebraMap ℂ R z-A)*(∫ t in Ioi 0,transfer (A-algebraMap ℂ R z) t)=1 := by rw [hn,neg_mul,hl,neg_neg]
  have hr' : (∫ t in Ioi 0,transfer (A-algebraMap ℂ R z) t)*(algebraMap ℂ R z-A)=1 := by rw [hn,mul_neg,hr,neg_neg]
  have hu : IsUnit (algebraMap ℂ R z-A) := ⟨⟨_,_,hl',hr'⟩,rfl⟩
  refine ⟨hi,hu,?_⟩
  calc
    _ = Ring.inverse (algebraMap ℂ R z-A)*((algebraMap ℂ R z-A)*(∫ t in Ioi 0,transfer (A-algebraMap ℂ R z) t)) :=
      (Ring.inverse_mul_cancel_left _ _ hu).symm
    _ = _ := by rw [hl',mul_one]

theorem memory_self_energy (A U V : R) (z : ℂ) (M w : ℝ) (hz : w < z.re)
    (hA : ∀ t,0 ≤ t → ‖transfer A t‖ ≤ M*Real.exp (w*t)) :
    IntegrableOn (fun t : ℝ => Complex.exp (-z*t) • (U*transfer A t*V)) (Ioi 0) ∧
    (∫ t : ℝ in Ioi 0,Complex.exp (-z*t) • (U*transfer A t*V))=U*Ring.inverse (algebraMap ℂ R z-A)*V := by
  have h := laplace_inverse A z M w hz hA
  have he : (fun t : ℝ => Complex.exp (-z*t) • (U*transfer A t*V))=(fun t => U*damped A z t*V) := by
    ext t
    simp [damped,Algebra.mul_smul_comm,Algebra.smul_mul_assoc]
  rw [he]
  have hu : IntegrableOn (fun t => U*damped A z t) (Ioi 0) := (ContinuousLinearMap.mul ℝ R U).integrable_comp h.1
  refine ⟨((ContinuousLinearMap.mul ℝ R).flip V).integrable_comp hu,?_⟩
  rw [integral_mul_const_of_integrable hu,integral_const_mul_of_integrable h.1,h.2.2]


theorem normal_growth (A : R) [IsStarNormal A] (w : ℝ)
    (hw : ∀ z∈spectrum ℂ A,z.re ≤ w) (t : ℝ) (ht : 0 ≤ t) :
    ‖transfer A t‖ ≤ Real.exp (w*t) := by
  rw [transfer,← CFC.exp_eq_normedSpace_exp (𝕜 := ℂ) (a := t • A),
    ← cfc_comp_smul t (NormedSpace.exp : ℂ → ℂ) A]
  apply norm_cfc_le (Real.exp_pos _).le
  intro z hz
  rw [← Complex.exp_eq_exp_ℂ,Complex.norm_exp,Real.exp_le_exp]
  simpa only [Complex.smul_re,smul_eq_mul,mul_comm] using mul_le_mul_of_nonneg_left (hw z hz) ht

theorem normal_memory_self_energy (A U V : R) [IsStarNormal A] (z : ℂ) (w : ℝ)
    (hw : ∀ v∈spectrum ℂ A,v.re ≤ w) (hz : w < z.re) :
    IntegrableOn (fun t : ℝ => Complex.exp (-z*t) • (U*transfer A t*V)) (Ioi 0) ∧
    (∫ t : ℝ in Ioi 0,Complex.exp (-z*t) • (U*transfer A t*V))=U*Ring.inverse (algebraMap ℂ R z-A)*V :=
  memory_self_energy A U V z 1 w hz (fun t ht => by simpa using normal_growth A w hw t ht)

end KomorebiPaperVI.ComplexMemory
