module
public import GlobalRangeBundle
public import LocalProjectedCurvature
import all ProjectedCurvature
public import Mathlib.Geometry.Manifold.VectorField.LieBracket
public import Mathlib.Geometry.Manifold.MFDeriv.NormedSpace
public import Mathlib.Geometry.Manifold.VectorBundle.CovariantDerivative.Basic
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, item 6.4.
Actual global manifold derivative, range sections and atlas compatibility.
-/
@[expose] public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
open scoped Manifold ContDiff Topology
open Set Filter
noncomputable section
namespace KomorebiPaperVII.GlobalConnection
open KomorebiPaperVII.RangeBundle

variable {E H M F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [TopologicalSpace H] (I : ModelWithCorners ℝ E H)
  [TopologicalSpace M] [ChartedSpace H M]
  [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- The global projected covariant derivative. -/
def nabla (P : M → F →L[ℝ] F) (X : ∀ x : M, TangentSpace I x) (s : M → F) (x : M) : F :=
  P x (mvfderiv I s x (X x))

/-- The global operator-valued two-form. -/
def curvatureForm (P : M → F →L[ℝ] F) (x : M) (v w : TangentSpace I x) : F →L[ℝ] F :=
  P x * (mvfderiv I P x v * mvfderiv I P x w -
    mvfderiv I P x w * mvfderiv I P x v) * P x

/-- Actual covariant commutator with the manifold Lie bracket. -/
def curvature (P : M → F →L[ℝ] F) (X Y : ∀ x : M, TangentSpace I x)
    (s : M → F) (x : M) : F :=
  nabla I P X (nabla I P Y s) x - nabla I P Y (nabla I P X s) x -
    nabla I P (VectorField.mlieBracket I X Y) s x

/-- A connection as a section of Hom(TM, range P), not merely an ambient formula. -/
def covariant (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (s : ∀ x, fiber (P x)) (x : M) : TangentSpace I x →L[ℝ] fiber (P x) :=
  (project (P x) (hPP x)).comp (mvfderiv I (fun y => (s y : F)) x)

theorem nabla_in_range (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (X : ∀ x : M, TangentSpace I x) (s : M → F) (x : M) :
    P x (nabla I P X s x)=nabla I P X s x :=
  congrArg (fun q : F →L[ℝ] F => q (mvfderiv I s x (X x))) (hPP x)

theorem nabla_add_sections (P : M → F →L[ℝ] F) (X : ∀ x : M, TangentSpace I x)
    (s t : M → F) (x : M) (hs : MDifferentiableAt I 𝓘(ℝ,F) s x)
    (ht : MDifferentiableAt I 𝓘(ℝ,F) t x) :
    nabla I P X (s+t) x=nabla I P X s x+nabla I P X t x := by
  simp [nabla,mvfderiv_add hs ht]

theorem nabla_leibniz (P : M → F →L[ℝ] F) (X : ∀ x : M, TangentSpace I x)
    (s : M → F) (c : M → ℝ) (x : M) (hs : MDifferentiableAt I 𝓘(ℝ,F) s x)
    (hc : MDifferentiableAt I 𝓘(ℝ,ℝ) c x) (hPs : P x (s x)=s x) :
    nabla I P X (c • s) x = (mvfderiv I c x (X x)) • s x + c x • nabla I P X s x := by
  simp [nabla,mvfderiv_smul hc hs,hPs,add_comm]

theorem nabla_add_vectors (P : M → F →L[ℝ] F) (X Y : ∀ x : M, TangentSpace I x)
    (s : M → F) (x : M) :
    nabla I P (X+Y) s x = nabla I P X s x+nabla I P Y s x := by simp [nabla]

theorem nabla_smul_vector (P : M → F →L[ℝ] F) (X : ∀ x : M, TangentSpace I x)
    (s : M → F) (c : M → ℝ) (x : M) :
    nabla I P (c • X) s x=c x • nabla I P X s x := by simp [nabla]

theorem nabla_germ (P : M → F →L[ℝ] F) (X : ∀ x : M, TangentSpace I x)
    (s t : M → F) (x : M) (h : s =ᶠ[𝓝 x] t) : nabla I P X s x=nabla I P X t x := by
  have hd : mvfderiv I s x=mvfderiv I t x := h.mfderiv_eq
  simp only [nabla,hd]

variable [IsManifold I ∞ M]

/-- Differentiating a smooth vector-valued function along a smooth vector field is smooth. -/
theorem smooth_directional (s : M → F) (X : ∀ x : M, TangentSpace I x)
    (hs : ContMDiff I 𝓘(ℝ,F) ∞ s)
    (hX : ContMDiff I I.tangent ∞ (fun x => (X x : TangentBundle I M))) :
    ContMDiff I 𝓘(ℝ,F) ∞ (fun x => mvfderiv I s x (X x)) := by
  exact (contMDiff_snd_tangentBundle_modelSpace F 𝓘(ℝ,F)).comp
    ((hs.contMDiff_tangentMap (m := ∞) (by simp)).comp hX)

theorem smooth_nabla (P : M → F →L[ℝ] F) (s : M → F)
    (X : ∀ x : M, TangentSpace I x)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (hs : ContMDiff I 𝓘(ℝ,F) ∞ s)
    (hX : ContMDiff I I.tangent ∞ (fun x => (X x : TangentBundle I M))) :
    ContMDiff I 𝓘(ℝ,F) ∞ (nabla I P X s) := hP.clm_apply (smooth_directional I s X hs hX)

variable [CompleteSpace F]

/-- The local connection in the derived range coordinates. -/
def localNabla (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x) (a : M)
    (X : ∀ x : M, TangentSpace I x) (u : M → fiber (P a)) (x : M) : fiber (P a) :=
  toCoord P hPP a x (nabla I P X (fun y => fromCoord P a y (u y)) x)

/-- Local reconstruction gives the same global connection on the whole open domain. -/
theorem localNabla_represents_global (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (a : M)
    (X : ∀ x : M, TangentSpace I x) (s : M → F) (hPs : ∀ x, P x (s x)=s x)
    (x : M) (hx : x ∈ domain P a) :
    localNabla I P hPP a X (fun y => toCoord P hPP a y (s y)) x =
      toCoord P hPP a x (nabla I P X s x) := by
  unfold localNabla
  congr 1
  apply nabla_germ
  filter_upwards [(isOpen_domain P hP.continuous a).mem_nhds hx] with y hy
  exact fromCoord_toCoord P hPP a y hy (s y) (hPs y)

/-- The constructed local connections agree on every overlap. -/
theorem local_connections_glue (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ,F →L[ℝ] F) ∞ P) (a b : M)
    (X : ∀ x : M, TangentSpace I x) (s : M → F) (hPs : ∀ x, P x (s x)=s x)
    (x : M) (hx : x ∈ domain P a ∩ domain P b) :
    transition P hPP a b x (localNabla I P hPP a X (fun y => toCoord P hPP a y (s y)) x) =
      localNabla I P hPP b X (fun y => toCoord P hPP b y (s y)) x := by
  rw [localNabla_represents_global I P hPP hP a X s hPs x hx.1,
    localNabla_represents_global I P hPP hP b X s hPs x hx.2]
  change toCoord P hPP b x (fromCoord P a x (toCoord P hPP a x (nabla I P X s x))) = _
  rw [fromCoord_toCoord P hPP a x hx.1 _ (nabla_in_range I P hPP X s x)]

end KomorebiPaperVII.GlobalConnection
