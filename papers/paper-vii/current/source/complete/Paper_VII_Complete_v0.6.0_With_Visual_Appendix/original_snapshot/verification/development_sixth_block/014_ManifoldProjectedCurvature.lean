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
  simpa [differentiableWithinAt_univ] using (hs.mdifferentiableWithinAt (s := Set.univ)).differentiableWithinAt_comp_extChartAt_symm

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
  simpa [Function.comp_def] using! hd

/-- The actual pullback of a vector field into a chart. -/
def chartField (a : M) (X : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) : E → E :=
  VectorField.mpullbackWithin 𝓘(ℝ,E) 𝓘(ℝ,E) (extChartAt 𝓘(ℝ,E) a).symm X
    (Set.range 𝓘(ℝ,E))

theorem chartField_self (a : M) (X : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) :
    chartField a X (extChartAt 𝓘(ℝ,E) a a)=X a := by
  dsimp only [chartField]
  rw [VectorField.mpullbackWithin_apply]
  have he : (X ((extChartAt 𝓘(ℝ,E) a).symm (extChartAt 𝓘(ℝ,E) a a)) : E) = X a := by
    exact congrArg (fun z : M => (show E from X z)) (extChartAt_to_inv (I := 𝓘(ℝ,E)) a)
  rw [he]
  exact mfderivWithin_extChartAt_symm_inverse_apply (I := 𝓘(ℝ,E)) (X a)

theorem chartField_differentiable (a : M) (X : ∀ x : M, TangentSpace 𝓘(ℝ,E) x)
    (hX : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,E).tangent
      (fun x => (X x : TangentBundle 𝓘(ℝ,E) M)) a) :
    DifferentiableAt ℝ (chartField a X) (extChartAt 𝓘(ℝ,E) a a) := by
  simpa [chartField, differentiableWithinAt_univ] using (hX.mdifferentiableWithinAt (s := Set.univ)).differentiableWithinAt_mpullbackWithin_vectorField

theorem bracket_in_chart (a : M) (X Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) :
    VectorField.mlieBracket 𝓘(ℝ,E) X Y a =
      VectorField.lieBracket ℝ (chartField a X) (chartField a Y) (extChartAt 𝓘(ℝ,E) a a) := by
  rw [VectorField.mlieBracket,VectorField.mlieBracketWithin_apply]
  rw [mfderiv_extChartAt_self, ContinuousLinearMap.inverse_id]
  change VectorField.lieBracketWithin ℝ (chartField a X) (chartField a Y)
    ((extChartAt 𝓘(ℝ,E) a).symm ⁻¹' Set.univ ∩ Set.range 𝓘(ℝ,E))
    (extChartAt 𝓘(ℝ,E) a a) = _
  simp

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
    convert! hc using 1
    exact (mfderiv_eq_fderiv : mfderiv 𝓘(ℝ,E) 𝓘(ℝ,F) (s ∘ (extChartAt 𝓘(ℝ,E) a).symm) u = _).symm
  rw [hd]
  simp only [ContinuousLinearMap.comp_apply,chartField,VectorField.mpullbackWithin_apply,
    modelWithCornersSelf_coe,Set.range_id,mfderivWithin_univ]
  exact congrArg (fun v => mvfderiv 𝓘(ℝ,E) s ((extChartAt 𝓘(ℝ,E) a).symm u) v)
    (hinv.self_apply_inverse (Y ((extChartAt 𝓘(ℝ,E) a).symm u)))

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


/-- The differentiated idempotence identity on the actual tangent space. -/
theorem projector_jet (P : M → F →L[ℝ] F) (x : M)
    (hP : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) P x)
    (hPP : ∀ x, P x*P x=P x) (v : TangentSpace 𝓘(ℝ,E) x) :
    mvfderiv 𝓘(ℝ,E) P x v * P x + P x * mvfderiv 𝓘(ℝ,E) P x v =
      mvfderiv 𝓘(ℝ,E) P x v := by
  rw [derivative_in_chart P x hP]
  have hh := LocalCurvature.projector_jet (P ∘ (extChartAt 𝓘(ℝ,E) x).symm)
    (extChartAt 𝓘(ℝ,E) x x) (differentiable_in_chart P x hP)
    (fun y => hPP _) (show E from v)
  simpa [Function.comp_def] using! hh

theorem projector_differential_sandwich (P : M → F →L[ℝ] F) (x : M)
    (hP : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) P x)
    (hPP : ∀ x, P x*P x=P x) (v : TangentSpace 𝓘(ℝ,E) x) :
    P x * mvfderiv 𝓘(ℝ,E) P x v * P x = 0 :=
  Curvature.jet_sandwich_zero _ _ (hPP x) (projector_jet P x hP hPP v)

theorem section_jet (P : M → F →L[ℝ] F) (s : M → F) (x : M)
    (hP : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) P x)
    (hs : MDifferentiableAt 𝓘(ℝ,E) 𝓘(ℝ,F) s x)
    (hPs : ∀ x, P x (s x)=s x) (v : TangentSpace 𝓘(ℝ,E) x) :
    mvfderiv 𝓘(ℝ,E) s x v =
      mvfderiv 𝓘(ℝ,E) P x v (s x) + P x (mvfderiv 𝓘(ℝ,E) s x v) := by
  have hh := derivative_clm_apply P s x hP hs v
  have heq : (fun y => P y (s y))=s := funext hPs
  rw [heq] at hh
  simpa only [add_comm] using hh

theorem nabla_derivative (P : M → F →L[ℝ] F)
    (Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) (s : M → F) (x : M)
    (hP : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) ∞ P)
    (hY : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (Y x : TangentBundle 𝓘(ℝ,E) M)))
    (hs : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ s) (v : TangentSpace 𝓘(ℝ,E) x) :
    mvfderiv 𝓘(ℝ,E) (nabla 𝓘(ℝ,E) P Y s) x v =
      P x (mvfderiv 𝓘(ℝ,E) (fun y => mvfderiv 𝓘(ℝ,E) s y (Y y)) x v) +
      mvfderiv 𝓘(ℝ,E) P x v (mvfderiv 𝓘(ℝ,E) s x (Y x)) :=
  derivative_clm_apply P _ x (hP.mdifferentiableAt (by simp))
    ((smooth_directional 𝓘(ℝ,E) s Y hs hY).mdifferentiableAt (by simp)) v

/-- Cancellation of second derivatives uses the actual manifold Lie bracket. -/
theorem curvature_expansion (P : M → F →L[ℝ] F)
    (X Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) (s : M → F) (x : M)
    (hP : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) ∞ P) (hPP : ∀ x, P x*P x=P x)
    (hX : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (X x : TangentBundle 𝓘(ℝ,E) M)))
    (hY : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (Y x : TangentBundle 𝓘(ℝ,E) M)))
    (hs : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ s) :
    curvature 𝓘(ℝ,E) P X Y s x =
      P x (mvfderiv 𝓘(ℝ,E) P x (X x) (mvfderiv 𝓘(ℝ,E) s x (Y x))) -
      P x (mvfderiv 𝓘(ℝ,E) P x (Y x) (mvfderiv 𝓘(ℝ,E) s x (X x))) := by
  have hp (z : F) : P x (P x z)=P x z :=
    congrArg (fun L : F →L[ℝ] F => L z) (hPP x)
  have hb := derivative_lieBracket s hs X Y hX hY x
  unfold curvature
  simp only [nabla]
  rw [nabla_derivative P Y s x hP hY hs (X x),nabla_derivative P X s x hP hX hs (Y x)]
  simp only [map_add,hp,hb,map_sub]
  abel

/-- Item 6.4: the global projected connection has curvature P(dP wedge dP)P.
The ambient manifold may require arbitrarily many charts. All differential operators,
vector fields and the Lie bracket here are the actual Mathlib manifold constructions. -/
theorem projected_connection_curvature (P : M → F →L[ℝ] F)
    (X Y : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) (s : M → F) (x : M)
    (hP : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) ∞ P) (hPP : ∀ x, P x*P x=P x)
    (hX : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (X x : TangentBundle 𝓘(ℝ,E) M)))
    (hY : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞
      (fun x => (Y x : TangentBundle 𝓘(ℝ,E) M)))
    (hs : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ s) (hPs : ∀ x, P x (s x)=s x) :
    curvature 𝓘(ℝ,E) P X Y s x = curvatureForm 𝓘(ℝ,E) P x (X x) (Y x) (s x) := by
  have hP1 := hP.mdifferentiableAt (x := x) (by simp)
  have hs1 := hs.mdifferentiableAt (x := x) (by simp)
  have hz (v : TangentSpace 𝓘(ℝ,E) x) (z : F) : P x (mvfderiv 𝓘(ℝ,E) P x v (P x z))=0 := by
    have hh := congrArg (fun L : F →L[ℝ] F => L z)
      (projector_differential_sandwich P x hP1 hPP v)
    simpa [mul_apply_eq_comp] using hh
  rw [curvature_expansion P X Y s x hP hPP hX hY hs]
  conv_lhs => rw [section_jet P s x hP1 hs1 hPs (Y x),section_jet P s x hP1 hs1 hPs (X x)]
  simp only [map_add,hz,add_zero]
  simp [curvatureForm,hPs,map_sub]

/-- The global curvature is tensorial: its value depends only on the two tangent vectors
and the section value at the point, not on their extensions. -/
theorem curvature_is_tensorial (P : M → F →L[ℝ] F)
    (hP : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F →L[ℝ] F) ∞ P) (hPP : ∀ x, P x*P x=P x)
    (X Y X' Y' : ∀ x : M, TangentSpace 𝓘(ℝ,E) x) (s t : M → F) (x : M)
    (hX : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞ (fun x => (X x : TangentBundle 𝓘(ℝ,E) M)))
    (hY : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞ (fun x => (Y x : TangentBundle 𝓘(ℝ,E) M)))
    (hX' : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞ (fun x => (X' x : TangentBundle 𝓘(ℝ,E) M)))
    (hY' : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,E).tangent ∞ (fun x => (Y' x : TangentBundle 𝓘(ℝ,E) M)))
    (hs : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ s) (ht : ContMDiff 𝓘(ℝ,E) 𝓘(ℝ,F) ∞ t)
    (hPs : ∀ x, P x (s x)=s x) (hPt : ∀ x, P x (t x)=t x)
    (hXX : X x=X' x) (hYY : Y x=Y' x) (hst : s x=t x) :
    curvature 𝓘(ℝ,E) P X Y s x=curvature 𝓘(ℝ,E) P X' Y' t x := by
  rw [projected_connection_curvature P X Y s x hP hPP hX hY hs hPs,
    projected_connection_curvature P X' Y' t x hP hPP hX' hY' ht hPt,hXX,hYY,hst]

end KomorebiPaperVII.ManifoldCurvature

