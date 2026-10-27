import KomorebiSpace.SurjectiveKernelMotion
import KomorebiSpace.MovingDescent
import KomorebiSpace.EuclideanCertificateCoordinates
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# An exactly moving kernel, its projector, and the strict-radius boundary

The Euclidean two-dimensional defect is d_t(x,y)=x+t*y. Its kernel is the moving
line (-t*b,b), not the old vertical axis. The projection and its full operator
motion are computed exactly for every real t. The general split perturbation
and two-stage-descent interfaces are instantiated, not only a separate formula.
-/
noncomputable section
namespace KomorebiSpace
namespace MovingKernelExamples
open HilbertKernelProjection
abbrev H := ExactCoordinates.Space 2

def vec (a b : ℝ) : H := WithLp.toLp 2 ![a,b]

theorem norm_sq (x : H) : ‖x‖^2=(x 0)^2+(x 1)^2 := by
  simpa only [Fin.sum_univ_two] using ExactCoordinates.norm_squared 2 x

def defectLinear (t : ℝ) : H →ₗ[ℝ] ℝ where
  toFun x := x 0+t*x 1
  map_add' x y := by simp only [PiLp.add_apply]; ring
  map_smul' a x := by
    change a*x 0+t*(a*x 1)=a*(x 0+t*x 1)
    ring

def defect (t : ℝ) : H →L[ℝ] ℝ := (defectLinear t).toContinuousLinearMap
@[simp] theorem defect_apply (t : ℝ) (x : H) : defect t x=x 0+t*x 1 := rfl

def sectionLinear : ℝ →ₗ[ℝ] H where
  toFun r := vec r 0
  map_add' x y := by ext i; fin_cases i <;> simp [vec,PiLp.add_apply]
  map_smul' a x := by ext i; fin_cases i <;> simp [vec,PiLp.smul_apply]

def sectionMap : ℝ →L[ℝ] H := sectionLinear.toContinuousLinearMap
@[simp] theorem section_apply (r : ℝ) : sectionMap r=vec r 0 := rfl

theorem section_norm (r : ℝ) : ‖sectionMap r‖=‖r‖ := by
  apply (sq_eq_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  rw [norm_sq,Real.norm_eq_abs,sq_abs]
  simp [section_apply,vec]

@[simp] theorem section_right (t r : ℝ) : defect t (sectionMap r)=r := by
  simp [defect_apply,section_apply,vec]

def selfCertificate (t : ℝ) : SplitKernel.Certificate (defect t) (defect t) where
  sectionMap := sectionMap
  right_inverse := section_right t
  constant := 1
  nonneg := by norm_num
  section_bound r := by rw [section_norm,one_mul]
  epsilon := 0
  epsilon_nonneg := le_rfl
  operator_error := by simp
  small := by norm_num

/-- Both systems have gain at most one, uniformly over all real slopes. -/
def bound (t : ℝ) : ResidualRobustness.Bound (defect t) :=
  (selfCertificate t).referenceBound

@[simp] theorem bound_constant (t : ℝ) : (bound t).constant=1 := rfl

theorem defect_surjective (t : ℝ) : Function.Surjective (defect t) :=
  fun r => ⟨sectionMap r,section_right t r⟩

theorem kernel_parameter (t : ℝ) (x : H) :
    defect t x=0 ↔ x=vec (-t*x 1) (x 1) := by
  constructor
  · intro h
    have h0 : x 0 = -t*x 1 := by change x 0+t*x 1=0 at h; linarith
    ext i
    fin_cases i <;> simp [vec,h0]
  · intro h
    rw [h]
    simp [defect_apply,vec]

def projected (t : ℝ) (x : H) : H :=
  vec (-t*((x 1-t*x 0)/(1+t^2))) ((x 1-t*x 0)/(1+t^2))

theorem projected_exact (t : ℝ) (x : H) : defect t (projected t x)=0 := by
  simp [projected,defect_apply,vec]

theorem projection_formula (t : ℝ) (x : H) : projection (defect t) x=projected t x := by
  apply projection_unique
  · exact projected_exact t x
  · intro y hy
    have hy0 : y 0 = -t*y 1 := by change y 0+t*y 1=0 at hy; linarith
    rw [ExactCoordinates.inner_coordinates,Fin.sum_univ_two]
    simp only [PiLp.sub_apply,projected,vec,Matrix.cons_val_zero,
      Matrix.cons_val_one,hy0]
    have ht : (1+t^2:ℝ) ≠ 0 := by positivity
    field_simp
    ring

@[simp] theorem zero_projection (x : H) : projection (defect 0) x=vec 0 (x 1) := by
  rw [projection_formula]
  simp [projected]

/-- Norm closeness is a theorem about operators, not a list of test vectors. -/
theorem defect_distance (s t : ℝ) : ‖defect s-defect t‖ ≤ |s-t| := by
  apply ContinuousLinearMap.opNorm_le_bound _ (abs_nonneg _)
  intro x
  have hid : (defect s-defect t) x=(s-t)*x 1 := by simp only [sub_apply,defect_apply]; ring
  rw [hid,norm_mul,Real.norm_eq_abs,Real.norm_eq_abs]
  apply mul_le_mul_of_nonneg_left _ (abs_nonneg _)
  apply (sq_le_sq₀ (abs_nonneg _) (norm_nonneg _)).mp
  rw [sq_abs,norm_sq]
  nlinarith [sq_nonneg (x 0)]

/-- The generic two-sided theorem is instantiated for the actual moving line. -/
theorem generic_motion (s t : ℝ) :
    ‖projection (defect s)-projection (defect t)‖ ≤ |s-t| := by
  have h := MovingKernel.projection_opNorm _ _ (bound s) (bound t) (defect_distance s t)
  simpa only [bound_constant,max_self,one_mul] using h

/-- Exact squared pointwise motion relative to the vertical-axis reference. -/
theorem motion_squared (t : ℝ) (x : H) :
    ‖projection (defect t) x-projection (defect 0) x‖^2 =
      (t^2/(1+t^2))*‖x‖^2 := by
  rw [projection_formula,zero_projection,norm_sq,norm_sq]
  simp only [PiLp.sub_apply,projected,vec,Matrix.cons_val_zero,
    Matrix.cons_val_one]
  have ht : (1+t^2:ℝ) ≠ 0 := by positivity
  field_simp
  ring

theorem motion_formula (t : ℝ) (x : H) :
    ‖projection (defect t) x-projection (defect 0) x‖ =
      Real.sqrt (t^2/(1+t^2))*‖x‖ := by
  apply (sq_eq_sq₀ (norm_nonneg _) (mul_nonneg (Real.sqrt_nonneg _) (norm_nonneg _))).mp
  rw [motion_squared,mul_pow,Real.sq_sqrt (by positivity)]

/-- The complete operator norm is calculated, not just bounded. -/
theorem motion_opNorm_exact (t : ℝ) :
    ‖projection (defect t)-projection (defect 0)‖ = Real.sqrt (t^2/(1+t^2)) := by
  apply le_antisymm
  · apply ContinuousLinearMap.opNorm_le_bound _ (Real.sqrt_nonneg _)
    intro x
    exact (motion_formula t x).le
  · have h := (projection (defect t)-projection (defect 0)).le_opNorm (vec 1 0)
    have hn : ‖vec 1 0‖=1 := by
      have h := section_norm 1
      simpa only [section_apply,norm_one] using h
    change ‖projection (defect t) (vec 1 0)-projection (defect 0) (vec 1 0)‖ ≤ _ at h
    rw [motion_formula,hn,mul_one,mul_one] at h
    exact h

/-- The old nonzero exact vector generally stops being exact, while a new one exists. -/
theorem exact_space_really_moves (t : ℝ) (ht : t ≠ 0) :
    defect 0 (vec 0 7)=0 ∧ defect t (vec 0 7)≠0 ∧
      defect t (vec (-7*t) 7)=0 ∧ vec (-7*t) 7 ≠ 0 := by
  constructor
  · norm_num [defect_apply,vec]
  constructor
  · simpa [defect_apply,vec] using ht
  constructor
  · simp [defect_apply,vec]; ring
  · intro h
    have h1 := congrArg (fun x : H => x 1) h
    norm_num [vec] at h1

/-- The small-radius perturbation construction is fully discharged on an interval. -/
def intervalCertificate (t : ℝ) (ht : |t|<1) : SplitKernel.Certificate (defect 0) (defect t) where
  sectionMap := sectionMap
  right_inverse := section_right 0
  constant := 1
  nonneg := by norm_num
  section_bound r := by rw [section_norm,one_mul]
  epsilon := |t|
  epsilon_nonneg := abs_nonneg t
  operator_error := by simpa only [zero_sub,abs_neg] using defect_distance 0 t
  small := by simpa only [one_mul] using ht

theorem interval_residual_identity (t : ℝ) (ht : |t|<1) (r : ℝ) :
    (intervalCertificate t ht).residualEquiv r=r := by
  rw [SplitKernel.Certificate.residualEquiv_apply]
  exact section_right t r

theorem interval_inverse_identity (t : ℝ) (ht : |t|<1) (r : ℝ) :
    (intervalCertificate t ht).residualEquiv.symm r=r := by
  have h := (intervalCertificate t ht).residualEquiv.apply_symm_apply r
  rw [interval_residual_identity] at h
  exact h

theorem interval_section_identity (t : ℝ) (ht : |t|<1) (r : ℝ) :
    (intervalCertificate t ht).perturbedSection r=sectionMap r := by
  change sectionMap ((intervalCertificate t ht).residualEquiv.symm r)=_
  rw [interval_inverse_identity]

/-- The actual general kernel equivalence preserves the second coordinate. -/
theorem kernel_transport_formula (t : ℝ) (ht : |t|<1) (b : ℝ) :
    ((intervalCertificate t ht).kernelEquiv
      ⟨vec 0 b,by simp [defect_apply,vec]⟩).val=vec (-t*b) b := by
  change vec 0 b-(intervalCertificate t ht).perturbedSection (defect t (vec 0 b))=_
  rw [interval_section_identity,section_apply]
  ext i
  fin_cases i <;> simp [vec,defect_apply,PiLp.sub_apply]

/-- The unchanged two-stage descent repair specializes to this moving projector. -/
theorem descent_repair_agreement (t : ℝ) (x : H) :
    QuantitativeDescent.repair (0 : H →L[ℝ] ℝ) (defect t) x=projection (defect t) x := by
  rw [QuantitativeDescent.repair_eq_projection]
  apply projection_unique
  · exact (QuantitativeDescent.joint_zero_iff _ _ _).mpr
      ⟨by simp,projection_exact (defect t) x⟩
  · intro y hy
    exact error_orthogonal (defect t) x y
      ((QuantitativeDescent.joint_zero_iff _ _ y).mp hy).2

/-- The exact comparison formula now concerns an actual v0.30 descent output. -/
theorem descent_motion_squared (t : ℝ) (x : H) :
    ‖QuantitativeDescent.repair (0 : H →L[ℝ] ℝ) (defect t) x-
      QuantitativeDescent.repair (0 : H →L[ℝ] ℝ) (defect 0) x‖^2=
      (t^2/(1+t^2))*‖x‖^2 := by
  rw [descent_repair_agreement,descent_repair_agreement]
  exact motion_squared t x

/-- At radius one a surjective defect may become the zero map. Strictness matters. -/
theorem closed_radius_failure :
    ‖(ContinuousLinearMap.id ℝ ℝ)-(0 : ℝ →L[ℝ] ℝ)‖ ≤ 1 ∧
    ¬ Function.Surjective (0 : ℝ →L[ℝ] ℝ) := by
  constructor
  · simpa only [sub_zero] using ContinuousLinearMap.norm_id_le (𝕜 := ℝ) (E := ℝ)
  · intro h
    obtain ⟨x,hx⟩ := h 1
    norm_num at hx

end MovingKernelExamples
end KomorebiSpace
end
