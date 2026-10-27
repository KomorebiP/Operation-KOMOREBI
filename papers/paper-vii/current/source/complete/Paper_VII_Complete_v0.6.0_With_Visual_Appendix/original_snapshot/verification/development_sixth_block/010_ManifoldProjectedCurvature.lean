module
public import GlobalProjectedConnection
import all ProjectedCurvature
import all Mathlib.Geometry.Manifold.IsManifold.Basic
import all Mathlib.Geometry.Manifold.VectorField.LieBracket
import all Mathlib.Geometry.Manifold.MFDeriv.NormedSpace
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, sixth block.
Curvature of the actual global connection on arbitrary smooth real manifolds
without boundary, modelled on a complete normed space. No global chart is assumed.
-/
@[expose] public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
open scoped Manifold ContDiff Topology
open Set Filter
noncomputable section
namespace KomorebiPaperVII.ManifoldCurvature
open KomorebiPaperVII.GlobalConnection

variable {E M F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
  [TopologicalSpace M] [ChartedSpace E M] [IsManifold 𝓘(ℝ,E) ∞ M]
  [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- Derivative in the chart centred at the point being differentiated. -/
theorem derivative_in_chart (s : M → F) (x : M)
    (hs : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F) s x) :
    mvfderiv 𝓘(ℝ,E) s x =
      fderiv ℝ (s ∘ (extChartAt 𝓘(ℝ,E) x).symm) (extChartAt 𝓘(ℝ,E) x x) := by
  simpa [writtenInExtChartAt, mfld_simps] using hs.mvfderiv

theorem differentiable_in_chart (s : M → F) (x : M)
    (hs : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F) s x) :
    DifferentiableAt ℝ (s ∘ (extChartAt 𝓘(ℝ,E) x).symm) (extChartAt 𝓘(ℝ,E) x x) := by
  simpa using hs.mdifferentiableWithinAt.differentiableWithinAt_comp_extChartAt_symm

theorem smooth_in_chart (s : M → F) (a : M)
    (hs : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ s) :
    ContDiffAt ℝ ∞ (s ∘ (extChartAt 𝓘(ℝ,E) a).symm) (extChartAt 𝓘(ℝ,E) a a) := by
  have hi : ContMDiffAt 𝓘(ℝ,E) 𝓘(ℝ,E) ∞ (extChartAt 𝓘(ℝ,E) a).symm
      (extChartAt 𝓘(ℝ,E) a a) := by
    simpa [contMDiffWithinAt_univ] using (contMDiffWithinAt_extChartAt_symm_range (I := 𝓘(ℝ,E)) (n := ∞)
      a (mem_extChartAt_target a))
  exact ((hs _).comp _ hi).contDiffAt

/-- Manifold product rule for operator evaluation, proved from actual derivatives. -/
theorem derivative_clm_apply (P : M → F →L[ℝ] F) (s : M → F) (x : M)
    (hP : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) P x)
    (hs : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F) s x) (v : TangentSpace 𝓘(ℝ,E) x) :
    mvfderiv 𝓘(ℝ,E) (fun y => P y (s y)) x v =
      P x (mvfderiv 𝓘(ℝ,E) s x v)+mvfderiv 𝓘(ℝ,E) P x v (s x) := by
  rw [derivative_in_chart _ x (hP.clm_apply hs),derivative_in_chart P x hP,
    derivative_in_chart s x hs]
  have hd := congrArg (fun q : E →L[ℝ] F => q v)
    (fderiv_clm_apply (differentiable_in_chart P x hP) (differentiable_in_chart s x hs))
  simpa [Function.comp_def] using hd

/-- The actual pullback of a vector field into a chart. -/
def chartField (a : M) (X : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) : E → E :=
  VectorField.mpullbackWithin 𝓘(ℝ,E) 𝓘(ℝ,E) (extChartAt 𝓘(ℝ,E) a).symm X
    (Set.range 𝓘(ℝ,E))

theorem chartField_self (a : M) (X : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) :
    chartField a X (extChartAt 𝓘(ℝ,E) a a)=X a := by
  simp only [chartField,VectorField.mpullbackWithin_apply,mfderivWithin_range_extChartAt_symm,
    ContinuousLinearMap.inverse_id,ContinuousLinearMap.id_apply,extChartAt_to_inv]

theorem chartField_differentiable (a : M) (X : ∀ x : M, TangentSpace 𝓘(ℝ,E) x)
    (hX : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,E).tangent
      (fun x => (X x : TangentBundle 𝓘(ℝ,E) M)) a) :
    DifferentiableAt ℝ (chartField a X) (extChartAt 𝓘(ℝ,E) a a) := by
  simpa [chartField] using hX.mdifferentiableWithinAt.differentiableWithinAt_mpullbackWithin_vectorField

theorem bracket_in_chart (a : M) (X Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) :
    VectorField.mlieBracket 𝓘(ℝ,E) X Y a =
      VectorField.lieBracket ℝ (chartField a X) (chartField a Y) (extChartAt 𝓘(ℝ,E) a a) := by
  simp [VectorField.mlieBracket,VectorField.mlieBracketWithin,VectorField.mpullback,
    chartField,mfderiv_extChartAt_self]

/-- The chain rule identifies directional derivatives on every point of a chart domain. -/
theorem directional_chart_pullback (s : M → F)
    (hs : MDifferentiable 𝓘(ℝ,E) 𝓘(ℝ,F) s)
    (Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) (a : M) (u : E)
    (hu : u ∈ (extChartAt 𝓘(ℝ,E) a).target) :
    fderiv ℝ (s ∘ (extChartAt 𝓘(ℝ,E) a).symm) u (chartField a Y u) =
      mvfderiv 𝓘(ℝ,E) s ((extChartAt 𝓘(ℝ,E) a).symm u)
        (Y ((extChartAt 𝓘(ℝ,E) a).symm u)) := by
  have hi : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,E) (extChartAt 𝓘(ℝ,E) a).symm u := by
    simpa [mdifferentiableWithinAt_univ] using (mdifferentiableWithinAt_extChartAt_symm (I := 𝓘(ℝ,E)) hu)
  have hc := mvfderiv_comp u (hs _) hi
  have hinv : (mfderiv 𝓘(ℝ,E) 𝓘(ℝ,E) (extChartAt 𝓘(ℝ,E) a).symm u).IsInvertible := by
    simpa using (isInvertible_mfderivWithin_extChartAt_symm (I := 𝓘(ℝ,E)) hu)
  have hd : fderiv ℝ (s ∘ (extChartAt 𝓘(ℝ,E) a).symm) u =
      (mvfderiv 𝓘(ℝ,E) s ((extChartAt 𝓘(ℝ,E) a).symm u)).comp
        (mfderiv 𝓘(ℝ,E) 𝓘(ℝ,E) (extChartAt 𝓘(ℝ,E) a).symm u) := by
    simpa [mvfderiv,mfderiv_eq_fderiv, NormedSpace.fromTangentSpace, tangentSpaceCastModel] using hc
  rw [hd]
  simp only [ContinuousLinearMap.comp_apply,chartField,VectorField.mpullbackWithin_apply,
    modelWithCornersSelf_range,mfderivWithin_univ]
  rw [hinv.self_apply_inverse]

/-- The outer derivative also agrees after localization to an open chart. -/
theorem second_directional_in_chart (s : M → F)
    (hs : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ s)
    (X Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x)
    (hY : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (Y x : TangentBundle 𝓘(ℝ,E) M))) (a : M) :
    mvfderiv 𝓘(ℝ,E) (fun x => mvfderiv 𝓘(ℝ,E) s x (Y x)) a (X a) =
      fderiv ℝ (fun u => fderiv ℝ (s ∘ (extChartAt 𝓘(ℝ,E) a).symm) u (chartField a Y u))
        (extChartAt 𝓘(ℝ,E) a a) (chartField a X (extChartAt 𝓘(ℝ,E) a a)) := by
  rw [chartField_self,derivative_in_chart _ a
    ((smooth_directional 𝓘(ℝ,E) s Y hs hY).mdifferentiableAt (by simp))]
  congr 1
  apply Filter.EventuallyEq.fderiv_eq
  filter_upwards [(isOpen_extChartAt_target (I := 𝓘(ℝ,E)) a).mem_nhds (mem_extChartAt_target a)]
    with u hu
  exact (directional_chart_pullback s (hs.mdifferentiable (by simp)) Y a u hu).symm

/-- Flat ambient differentiation obeys the actual manifold Lie-bracket identity. -/
theorem derivative_lieBracket (s : M → F)
    (hs : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ s)
    (X Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x)
    (hX : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (X x : TangentBundle 𝓘(ℝ,E) M)))
    (hY : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (Y x : TangentBundle 𝓘(ℝ,E) M))) (a : M) :
    mvfderiv 𝓘(ℝ,E) s a (VectorField.mlieBracket 𝓘(ℝ,E) X Y a) =
      mvfderiv 𝓘(ℝ,E) (fun x => mvfderiv 𝓘(ℝ,E) s x (Y x)) a (X a) -
      mvfderiv 𝓘(ℝ,E) (fun x => mvfderiv 𝓘(ℝ,E) s x (X x)) a (Y a) := by
  rw [second_directional_in_chart s hs X Y hY a,second_directional_in_chart s hs Y X hX a,
    bracket_in_chart,derivative_in_chart s a (hs.mdifferentiableAt (by simp))]
  exact VectorField.fderiv_apply_lieBracket (E := E) (F := F) (smooth_in_chart s a hs) (by simp)
    (chartField_differentiable a Y (hY.mdifferentiableAt (by simp)))
    (chartField_differentiable a X (hX.mdifferentiableAt (by simp)))

end KomorebiPaperVII.ManifoldCurvature
