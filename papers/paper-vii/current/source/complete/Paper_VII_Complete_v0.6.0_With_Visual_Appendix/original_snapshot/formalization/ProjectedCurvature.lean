module
public import Mathlib.Analysis.Calculus.VectorField
public import Mathlib.Analysis.Calculus.FDeriv.Mul
public import Mathlib.Analysis.Calculus.FDeriv.CompCLM
public import Mathlib.Analysis.Normed.Operator.Mul
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, fourth block.
Actual Frechet derivatives and actual vector fields, including the Lie bracket.
This is a parameter-space/chart formalization; it does not construct a global
smooth range bundle over an arbitrary manifold. -/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.Curvature
open scoped ContDiff

section Algebra
variable {R : Type*} [Ring R]
/-- Derived differentiated-idempotent consequence, not an assumed zero block. -/
theorem jet_sandwich_zero (P D : R) (hP : P*P=P)
    (hD : D*P+P*D=D) : P*D*P=0 := by
  have hh := congrArg (fun z => P*z) hD
  simp only [mul_add, ← mul_assoc, hP] at hh
  exact add_eq_right.mp hh
end Algebra

variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- Projected differentiation along a parameter-space vector field. -/
noncomputable def nabla (P : E → F →L[ℝ] F) (X : E → E) (s : E → F) (x : E) : F :=
  P x (fderiv ℝ s x (X x))

/-- The actual covariant commutator, including the vector-field bracket. -/
noncomputable def curvature (P : E → F →L[ℝ] F) (X Y : E → E)
    (s : E → F) (x : E) : F :=
  nabla P X (nabla P Y s) x - nabla P Y (nabla P X s) x -
    nabla P (VectorField.lieBracket ℝ X Y) s x

/-- The operator-valued two-form coefficient P[dP(v),dP(w)]P. -/
noncomputable def curvatureForm (P : E → F →L[ℝ] F) (x v w : E) : F →L[ℝ] F :=
  P x * (fderiv ℝ P x v * fderiv ℝ P x w -
    fderiv ℝ P x w * fderiv ℝ P x v) * P x

theorem nabla_in_range (P : E → F →L[ℝ] F)
    (hP : ∀ x, P x * P x = P x) (X : E → E) (s : E → F) (x : E) :
    P x (nabla P X s x) = nabla P X s x := by
  exact congrArg (fun L : F →L[ℝ] F => L (fderiv ℝ s x (X x))) (hP x)

theorem projector_jet (P : E → F →L[ℝ] F) (hP : Differentiable ℝ P)
    (hPP : ∀ x, P x * P x = P x) (x v : E) :
    fderiv ℝ P x v * P x + P x * fderiv ℝ P x v = fderiv ℝ P x v := by
  have heq : (fun y => P y * P y) = P := funext hPP
  have hh := congrArg (fun L => L v) (fderiv_fun_mul' (hP x) (hP x))
  rw [heq] at hh
  simpa [add_comm] using hh.symm

theorem projector_differential_sandwich (P : E → F →L[ℝ] F)
    (hP : Differentiable ℝ P) (hPP : ∀ x, P x * P x = P x) (x v : E) :
    P x * fderiv ℝ P x v * P x = 0 :=
  jet_sandwich_zero _ _ (hPP x) (projector_jet P hP hPP x v)

theorem section_jet (P : E → F →L[ℝ] F) (s : E → F)
    (hP : Differentiable ℝ P) (hs : Differentiable ℝ s)
    (hPs : ∀ x, P x (s x) = s x) (x v : E) :
    fderiv ℝ s x v = fderiv ℝ P x v (s x) + P x (fderiv ℝ s x v) := by
  have heq : (fun y => P y (s y)) = s := funext hPs
  have hh := congrArg (fun L => L v) (fderiv_clm_apply (hP x) (hs x))
  rw [heq] at hh
  simpa [add_comm] using hh

theorem nabla_derivative (P : E → F →L[ℝ] F) (Y : E → E) (s : E → F)
    (hP : Differentiable ℝ P) (hY : Differentiable ℝ Y)
    (hs : ContDiff ℝ 2 s) (x v : E) :
    fderiv ℝ (nabla P Y s) x v =
      P x (fderiv ℝ (fun y => fderiv ℝ s y (Y y)) x v) +
      fderiv ℝ P x v (fderiv ℝ s x (Y x)) := by
  have hs' : Differentiable ℝ (fderiv ℝ s) :=
    ((contDiff_succ_iff_fderiv (n := 1)).mp hs).2.2.differentiable_one
  have hh := congrArg (fun L => L v)
    (fderiv_clm_apply (hP x) ((hs' x).clm_apply (hY x)))
  change (fderiv ℝ (fun y => P y (fderiv ℝ s y (Y y))) x) v = _
  simpa using hh

theorem curvature_expansion (P : E → F →L[ℝ] F) (X Y : E → E) (s : E → F)
    (hP : Differentiable ℝ P) (hPP : ∀ x, P x * P x = P x)
    (hX : Differentiable ℝ X) (hY : Differentiable ℝ Y)
    (hs : ContDiff ℝ 2 s) (x : E) :
    curvature P X Y s x =
      P x (fderiv ℝ P x (X x) (fderiv ℝ s x (Y x))) -
      P x (fderiv ℝ P x (Y x) (fderiv ℝ s x (X x))) := by
  have hp (z : F) : P x (P x z) = P x z :=
    congrArg (fun L : F →L[ℝ] F => L z) (hPP x)
  have hb := VectorField.fderiv_apply_lieBracket (hs.contDiffAt (x := x))
    (by simp : minSmoothness ℝ 2 ≤ (2 : ℕ∞ω)) (hY x) (hX x)
  unfold curvature
  simp only [nabla]
  rw [nabla_derivative P Y s hP hY hs x (X x),
    nabla_derivative P X s hP hX hs x (Y x)]
  simp only [map_add, hp, hb, map_sub]
  abel

/-- Full chart-level curvature formula for actual vector-valued range sections. -/
theorem projected_connection_curvature (P : E → F →L[ℝ] F)
    (X Y : E → E) (s : E → F)
    (hP : Differentiable ℝ P) (hPP : ∀ x, P x * P x = P x)
    (hX : Differentiable ℝ X) (hY : Differentiable ℝ Y)
    (hs : ContDiff ℝ 2 s) (hPs : ∀ x, P x (s x)=s x) (x : E) :
    curvature P X Y s x = curvatureForm P x (X x) (Y x) (s x) := by
  have hs1 : Differentiable ℝ s := hs.differentiable (by norm_num)
  have hz (v : E) (z : F) : P x (fderiv ℝ P x v (P x z)) = 0 := by
    have hh := congrArg (fun L : F →L[ℝ] F => L z)
      (projector_differential_sandwich P hP hPP x v)
    simpa [mul_apply_eq_comp] using hh
  rw [curvature_expansion P X Y s hP hPP hX hY hs x]
  conv_lhs => rw [section_jet P s hP hs1 hPs x (Y x),
    section_jet P s hP hs1 hPs x (X x)]
  simp only [map_add, hz, add_zero]
  simp [curvatureForm, hPs, map_sub]

theorem curvatureForm_alternating (P : E → F →L[ℝ] F) (x v : E) :
    curvatureForm P x v v = 0 := by simp [curvatureForm]

theorem curvatureForm_antisymmetric (P : E → F →L[ℝ] F) (x v w : E) :
    curvatureForm P x v w = -curvatureForm P x w v := by
  unfold curvatureForm
  noncomm_ring

theorem curvatureForm_left_range (P : E → F →L[ℝ] F)
    (hPP : ∀ x, P x*P x=P x) (x v w : E) :
    P x * curvatureForm P x v w = curvatureForm P x v w := by
  simp only [curvatureForm, ← mul_assoc, hPP]

theorem curvatureForm_right_range (P : E → F →L[ℝ] F)
    (hPP : ∀ x, P x*P x=P x) (x v w : E) :
    curvatureForm P x v w * P x = curvatureForm P x v w := by
  simp only [curvatureForm, mul_assoc, hPP]

/-- The two-form coefficients transform by the actual chain rule. -/
theorem curvatureForm_pullback {D : Type*} [NormedAddCommGroup D] [NormedSpace ℝ D]
    (f : D → E) (P : E → F →L[ℝ] F) (x v w : D)
    (hf : DifferentiableAt ℝ f x) (hP : DifferentiableAt ℝ P (f x)) :
    curvatureForm (P ∘ f) x v w =
      curvatureForm P (f x) (fderiv ℝ f x v) (fderiv ℝ f x w) := by
  simp [curvatureForm, fderiv_comp x hP hf]
/-- Connection Leibniz rule on actual range sections. -/
theorem nabla_scalar_leibniz (P : E → F →L[ℝ] F) (X : E → E)
    (s : E → F) (c : E → ℝ) (x : E)
    (hs : DifferentiableAt ℝ s x) (hc : DifferentiableAt ℝ c x)
    (hPs : P x (s x)=s x) :
    nabla P X (fun y => c y • s y) x =
      (fderiv ℝ c x (X x)) • s x + c x • nabla P X s x := by
  simp [nabla, fderiv_fun_smul hc hs, hPs, add_comm]

theorem nabla_add_vectorfields (P : E → F →L[ℝ] F) (X Y : E → E)
    (s : E → F) (x : E) :
    nabla P (fun y => X y+Y y) s x = nabla P X s x+nabla P Y s x := by
  simp [nabla]

theorem nabla_smul_vectorfield (P : E → F →L[ℝ] F) (X : E → E)
    (s : E → F) (c : E → ℝ) (x : E) :
    nabla P (fun y => c y • X y) s x = c x • nabla P X s x := by
  simp [nabla]

theorem curvatureForm_add_left (P : E → F →L[ℝ] F) (x u v w : E) :
    curvatureForm P x (u+v) w = curvatureForm P x u w+curvatureForm P x v w := by
  simp only [curvatureForm, map_add]
  noncomm_ring

theorem curvatureForm_add_right (P : E → F →L[ℝ] F) (x u v w : E) :
    curvatureForm P x u (v+w) = curvatureForm P x u v+curvatureForm P x u w := by
  simp only [curvatureForm, map_add]
  noncomm_ring

theorem curvatureForm_smul_left (P : E → F →L[ℝ] F) (x u v : E) (c : ℝ) :
    curvatureForm P x (c • u) v = c • curvatureForm P x u v := by
  simp only [curvatureForm, map_smul, smul_mul_assoc, mul_smul_comm, ← smul_sub]

theorem curvatureForm_smul_right (P : E → F →L[ℝ] F) (x u v : E) (c : ℝ) :
    curvatureForm P x u (c • v) = c • curvatureForm P x u v := by
  simp only [curvatureForm, map_smul, smul_mul_assoc, mul_smul_comm, ← smul_sub]

end KomorebiPaperVII.Curvature

/-! Complete declaration-level trust audit. -/
#print axioms KomorebiPaperVII.Curvature.jet_sandwich_zero
#print axioms KomorebiPaperVII.Curvature.nabla_in_range
#print axioms KomorebiPaperVII.Curvature.projector_jet
#print axioms KomorebiPaperVII.Curvature.projector_differential_sandwich
#print axioms KomorebiPaperVII.Curvature.section_jet
#print axioms KomorebiPaperVII.Curvature.nabla_derivative
#print axioms KomorebiPaperVII.Curvature.curvature_expansion
#print axioms KomorebiPaperVII.Curvature.projected_connection_curvature
#print axioms KomorebiPaperVII.Curvature.curvatureForm_alternating
#print axioms KomorebiPaperVII.Curvature.curvatureForm_antisymmetric
#print axioms KomorebiPaperVII.Curvature.curvatureForm_left_range
#print axioms KomorebiPaperVII.Curvature.curvatureForm_right_range
#print axioms KomorebiPaperVII.Curvature.curvatureForm_pullback
#print axioms KomorebiPaperVII.Curvature.nabla_scalar_leibniz
#print axioms KomorebiPaperVII.Curvature.nabla_add_vectorfields
#print axioms KomorebiPaperVII.Curvature.nabla_smul_vectorfield
#print axioms KomorebiPaperVII.Curvature.curvatureForm_add_left
#print axioms KomorebiPaperVII.Curvature.curvatureForm_add_right
#print axioms KomorebiPaperVII.Curvature.curvatureForm_smul_left
#print axioms KomorebiPaperVII.Curvature.curvatureForm_smul_right
