module
public import ProjectedCurvature
import all ProjectedCurvature
public import Mathlib.Analysis.Calculus.VectorField
public import Mathlib.Analysis.Calculus.FDeriv.Mul
public import Mathlib.Analysis.Calculus.FDeriv.CompCLM
public import Mathlib.Analysis.Normed.Operator.Mul
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, sixth block.
Actual Frechet derivatives and actual vector fields, including the Lie bracket.
Point-local hypotheses allow application inside arbitrary open chart domains.
The manifold construction imports these results. -/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.LocalCurvature
open KomorebiPaperVII.Curvature
open scoped ContDiff

variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [NormedAddCommGroup F] [NormedSpace ℝ F]

theorem projector_jet (P : E → F →L[ℝ] F) (x : E) (hP : DifferentiableAt ℝ P x)
    (hPP : ∀ x, P x * P x = P x) (v : E) :
    fderiv ℝ P x v * P x + P x * fderiv ℝ P x v = fderiv ℝ P x v := by
  have heq : (fun y => P y * P y) = P := funext hPP
  have hh := congrArg (fun L => L v) (fderiv_fun_mul' hP hP)
  rw [heq] at hh
  simpa [add_comm] using hh.symm

theorem projector_differential_sandwich (P : E → F →L[ℝ] F)
    (x : E) (hP : DifferentiableAt ℝ P x) (hPP : ∀ x, P x * P x = P x) (v : E) :
    P x * fderiv ℝ P x v * P x = 0 :=
  jet_sandwich_zero _ _ (hPP x) (projector_jet P x hP hPP v)

theorem section_jet (P : E → F →L[ℝ] F) (s : E → F) (x : E)
    (hP : DifferentiableAt ℝ P x) (hs : DifferentiableAt ℝ s x)
    (hPs : ∀ x, P x (s x) = s x) (v : E) :
    fderiv ℝ s x v = fderiv ℝ P x v (s x) + P x (fderiv ℝ s x v) := by
  have heq : (fun y => P y (s y)) = s := funext hPs
  have hh := congrArg (fun L => L v) (fderiv_clm_apply hP hs)
  rw [heq] at hh
  simpa [add_comm] using hh

theorem nabla_derivative (P : E → F →L[ℝ] F) (Y : E → E) (s : E → F) (x : E)
    (hP : DifferentiableAt ℝ P x) (hY : DifferentiableAt ℝ Y x)
    (hs : ContDiffAt ℝ 2 s x) (v : E) :
    fderiv ℝ (nabla P Y s) x v =
      P x (fderiv ℝ (fun y => fderiv ℝ s y (Y y)) x v) +
      fderiv ℝ P x v (fderiv ℝ s x (Y x)) := by
  have hs' : DifferentiableAt ℝ (fderiv ℝ s) x :=
    (hs.fderiv_right (m := 1) (by norm_num)).differentiableAt one_ne_zero
  have hh := congrArg (fun L => L v)
    (fderiv_clm_apply hP (hs'.clm_apply hY))
  change (fderiv ℝ (fun y => P y (fderiv ℝ s y (Y y))) x) v = _
  simpa using hh

theorem curvature_expansion (P : E → F →L[ℝ] F) (X Y : E → E) (s : E → F) (x : E)
    (hP : DifferentiableAt ℝ P x) (hPP : ∀ x, P x * P x = P x)
    (hX : DifferentiableAt ℝ X x) (hY : DifferentiableAt ℝ Y x)
    (hs : ContDiffAt ℝ 2 s x) :
    curvature P X Y s x =
      P x (fderiv ℝ P x (X x) (fderiv ℝ s x (Y x))) -
      P x (fderiv ℝ P x (Y x) (fderiv ℝ s x (X x))) := by
  have hp (z : F) : P x (P x z) = P x z :=
    congrArg (fun L : F →L[ℝ] F => L z) (hPP x)
  have hb := VectorField.fderiv_apply_lieBracket hs
    (by simp : minSmoothness ℝ 2 ≤ (2 : ℕ∞ω)) hY hX
  unfold curvature
  simp only [nabla]
  rw [nabla_derivative P Y s x hP hY hs (X x),
    nabla_derivative P X s x hP hX hs (Y x)]
  simp only [map_add, hp, hb, map_sub]
  abel

/-- Full chart-level curvature formula for actual vector-valued range sections. -/
theorem projected_connection_curvature (P : E → F →L[ℝ] F)
    (X Y : E → E) (s : E → F) (x : E)
    (hP : DifferentiableAt ℝ P x) (hPP : ∀ x, P x * P x = P x)
    (hX : DifferentiableAt ℝ X x) (hY : DifferentiableAt ℝ Y x)
    (hs : ContDiffAt ℝ 2 s x) (hPs : ∀ x, P x (s x)=s x) :
    curvature P X Y s x = curvatureForm P x (X x) (Y x) (s x) := by
  have hs1 : DifferentiableAt ℝ s x := hs.differentiableAt (by norm_num)
  have hz (v : E) (z : F) : P x (fderiv ℝ P x v (P x z)) = 0 := by
    have hh := congrArg (fun L : F →L[ℝ] F => L z)
      (projector_differential_sandwich P x hP hPP v)
    simpa [mul_apply_eq_comp] using hh
  rw [curvature_expansion P X Y s x hP hPP hX hY hs]
  conv_lhs => rw [section_jet P s x hP hs1 hPs (Y x),
    section_jet P s x hP hs1 hPs (X x)]
  simp only [map_add, hz, add_zero]
  simp [curvatureForm, hPs, map_sub]


end KomorebiPaperVII.LocalCurvature

/-! Declaration-level dependency audit. -/
#print axioms KomorebiPaperVII.LocalCurvature.projector_jet
#print axioms KomorebiPaperVII.LocalCurvature.projector_differential_sandwich
#print axioms KomorebiPaperVII.LocalCurvature.section_jet
#print axioms KomorebiPaperVII.LocalCurvature.nabla_derivative
#print axioms KomorebiPaperVII.LocalCurvature.curvature_expansion
#print axioms KomorebiPaperVII.LocalCurvature.projected_connection_curvature
