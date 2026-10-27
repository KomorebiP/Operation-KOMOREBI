module
public import ManifoldProjectedCurvature
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, item 6.4.
Intrinsic atlas, section and gauge compatibility for the constructed global range bundle.
The explicit atlas is used directly; no bundle, gluing or curvature hypothesis is supplied.
-/
@[expose] public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
open scoped Manifold ContDiff Topology
open Set Filter
noncomputable section
namespace KomorebiPaperVII.BundleCompletion
open KomorebiPaperVII.RangeBundle KomorebiPaperVII.GlobalConnection

variable {E H M F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [TopologicalSpace H] {I : ModelWithCorners ℝ E H}
  [TopologicalSpace M] [ChartedSpace H M] [IsManifold I ∞ M]
  [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

/-- The actual total-space trivialization domains are open. -/
theorem total_domain_open (P : M → F →L[ℝ] F)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (a : M) :
    IsOpen {z : Total P | z.val.1 ∈ domain P a} :=
  (isOpen_domain P hP.continuous a).preimage continuous_subtype_val.fst

/-- The transition formula applies to the actual local product homeomorphisms. -/
theorem localProduct_overlap (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (a b x : M)
    (hxa : x ∈ domain P a) (hxb : x ∈ domain P b) (v : fiber (P a)) :
    localProduct P hPP hP b
      ⟨((localProduct P hPP hP a).symm (⟨x,hxa⟩,v)).val,hxb⟩ =
      (⟨x,hxb⟩,transition P hPP a b x v) := rfl

/-- Smoothness in the actual bundle coordinates is equivalent to ambient smoothness.
Only a local range condition near the point is required. -/
theorem smooth_section_iff (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (a x : M) (hx : x ∈ domain P a)
    (s : M → F) (hPs : ∀ᶠ y in 𝓝 x, P y (s y)=s y) :
    ContMDiffAt I 𝓘(ℝ,F) ∞ s x ↔
      ContMDiffAt I 𝓘(ℝ,fiber (P a)) ∞ (fun y => toCoord P hPP a y (s y)) x := by
  constructor
  · intro hs
    exact ((smooth_toCoord P hPP hP a x hx).contMDiffAt
      ((isOpen_domain P hP.continuous a).mem_nhds hx)).clm_apply hs
  · intro hs
    have hr := (smooth_fromCoord P hP a x).clm_apply hs
    apply hr.congr_of_eventuallyEq
    filter_upwards [hPs,(isOpen_domain P hP.continuous a).mem_nhds hx] with y hy hya
    exact (fromCoord_toCoord P hPP a y hya (s y) hy).symm

/-- The local connection obeys the full change-of-coordinate law for arbitrary local
coordinate functions, without assuming a global section or its smooth extension. -/
theorem local_connections_gauge (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (a b x : M)
    (hx : x ∈ domain P a ∩ domain P b) (X : ∀ y : M, TangentSpace I y)
    (u : M → fiber (P a)) :
    localNabla I P hPP b X (fun y => transition P hPP a b y (u y)) x =
      transition P hPP a b x (localNabla I P hPP a X u x) := by
  have hs : ∀ y, P y (fromCoord P a y (u y))=fromCoord P a y (u y) :=
    fun y => fromCoord_range P hPP a y (u y)
  change localNabla I P hPP b X (fun y => toCoord P hPP b y (fromCoord P a y (u y))) x = _
  rw [localNabla_represents_global I P hPP hP b X (fun y => fromCoord P a y (u y)) hs x hx.2]
  change toCoord P hPP b x (nabla I P X (fun y => fromCoord P a y (u y)) x) =
    toCoord P hPP b x (fromCoord P a x
      (toCoord P hPP a x (nabla I P X (fun y => fromCoord P a y (u y)) x)))
  rw [fromCoord_toCoord P hPP a x hx.1 _ (nabla_in_range I P hPP X _ x)]

/-- Curvature is an alternating two-form, with values in the actual range endomorphisms. -/
theorem curvatureForm_self (P : M → F →L[ℝ] F) (x : M) (v : TangentSpace I x) :
    curvatureForm I P x v v=0 := by simp [curvatureForm]

theorem curvatureForm_swap (P : M → F →L[ℝ] F) (x : M) (v w : TangentSpace I x) :
    curvatureForm I P x v w = -curvatureForm I P x w v := by
  unfold curvatureForm
  noncomm_ring

theorem curvatureForm_add_left (P : M → F →L[ℝ] F) (x : M) (u v w : TangentSpace I x) :
    curvatureForm I P x (u+v) w=curvatureForm I P x u w+curvatureForm I P x v w := by
  simp only [curvatureForm,map_add]
  noncomm_ring

theorem curvatureForm_smul_left (P : M → F →L[ℝ] F) (x : M) (c : ℝ) (v w : TangentSpace I x) :
    curvatureForm I P x (c • v) w=c • curvatureForm I P x v w := by
  simp only [curvatureForm,map_smul,smul_mul_assoc,mul_smul_comm,← smul_sub]

theorem curvatureForm_in_range (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (x : M) (v w : TangentSpace I x) (z : F) :
    P x (curvatureForm I P x v w z)=curvatureForm I P x v w z := by
  have hh : P x*curvatureForm I P x v w=curvatureForm I P x v w := by
    simp only [curvatureForm,← mul_assoc,hPP]
  exact congrArg (fun L : F →L[ℝ] F => L z) hh

/-- Curvature as an endomorphism of the actual fiber, not just of the ambient space. -/
def fiberCurvature (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (x : M) (v w : TangentSpace I x) : fiber (P x) →L[ℝ] fiber (P x) :=
  ((curvatureForm I P x v w).codRestrict (fiber (P x))
    (curvatureForm_in_range P hPP x v w)).comp (fiber (P x)).subtypeL

@[simp] theorem fiberCurvature_coe (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (x : M) (v w : TangentSpace I x) (z : fiber (P x)) :
    (fiberCurvature P hPP x v w z : F)=curvatureForm I P x v w z := rfl

/-- Zero, identity and all constant projector bundles have vanishing curvature form. -/
theorem constant_projector_flat (p : F →L[ℝ] F) (x : M) (v w : TangentSpace I x) :
    curvatureForm I (fun _ : M => p) x v w=0 := by simp [curvatureForm,mvfderiv_const]

/-- Smoothness of range sections does not depend on the chosen bundle chart. -/
theorem smooth_section_chart_independent (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (a b x : M)
    (hx : x ∈ domain P a ∩ domain P b) (s : M → F)
    (hPs : ∀ᶠ y in 𝓝 x, P y (s y)=s y) :
    ContMDiffAt I 𝓘(ℝ,fiber (P a)) ∞ (fun y => toCoord P hPP a y (s y)) x ↔
    ContMDiffAt I 𝓘(ℝ,fiber (P b)) ∞ (fun y => toCoord P hPP b y (s y)) x :=
  (smooth_section_iff P hPP hP a x hx.1 s hPs).symm.trans
    (smooth_section_iff P hPP hP b x hx.2 s hPs)

end KomorebiPaperVII.BundleCompletion

/-! Declaration-level dependency audit. -/
#print axioms KomorebiPaperVII.BundleCompletion.total_domain_open
#print axioms KomorebiPaperVII.BundleCompletion.localProduct_overlap
#print axioms KomorebiPaperVII.BundleCompletion.smooth_section_iff
#print axioms KomorebiPaperVII.BundleCompletion.local_connections_gauge
#print axioms KomorebiPaperVII.BundleCompletion.curvatureForm_self
#print axioms KomorebiPaperVII.BundleCompletion.curvatureForm_swap
#print axioms KomorebiPaperVII.BundleCompletion.curvatureForm_add_left
#print axioms KomorebiPaperVII.BundleCompletion.curvatureForm_smul_left
#print axioms KomorebiPaperVII.BundleCompletion.curvatureForm_in_range
#print axioms KomorebiPaperVII.BundleCompletion.fiberCurvature_coe
#print axioms KomorebiPaperVII.BundleCompletion.constant_projector_flat
#print axioms KomorebiPaperVII.BundleCompletion.smooth_section_chart_independent
