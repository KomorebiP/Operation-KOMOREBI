module
public import Mathlib.Analysis.Calculus.FDeriv.Analytic
public import Mathlib.Analysis.Calculus.InverseFunctionTheorem.FDeriv

/-!
Analyticity of the generic local inverse over any nontrivially normed field.
The result applies to finite-dimensional p-adic spaces without restricting the
field to the real or complex numbers.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialAnalyticInverse

open Filter Set
open scoped Topology

variable {𝕜 : Type*} [NontriviallyNormedField 𝕜]
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
variable {F : Type*} [NormedAddCommGroup F] [NormedSpace 𝕜 F]
variable [CompleteSpace E]
variable {f : E → F} {a : E} {i : E ≃L[𝕜] F}

/-- An analytic function with an invertible strict derivative has an analytic
local inverse. The only completeness hypothesis is on the original domain. -/
theorem analyticAt_inverse (ha : AnalyticAt 𝕜 f a)
    (hd : HasStrictFDerivAt f (i : E →L[𝕜] F) a) :
    AnalyticAt 𝕜 (hd.localInverse f i a) (f a) := by
  exact (hd.toOpenPartialHomeomorph f).analyticAt_symm'
    hd.mem_toOpenPartialHomeomorph_source ha hd.hasFDerivAt.fderiv

/-- The same inverse is analytic throughout some open neighborhood of the
image point, where its right inverse identity holds exactly. -/
theorem exists_open_analytic_inverse (ha : AnalyticAt 𝕜 f a)
    (hd : HasStrictFDerivAt f (i : E →L[𝕜] F) a) :
    ∃ U : Set F, IsOpen U ∧ f a ∈ U ∧
      AnalyticOnNhd 𝕜 (hd.localInverse f i a) U ∧
      ∀ y ∈ U, f (hd.localInverse f i a y) = y := by
  let R := hd.toOpenPartialHomeomorph f
  let U := {y | AnalyticAt 𝕜 (hd.localInverse f i a) y} ∩ R.target
  refine ⟨U, (isOpen_analyticAt 𝕜 _).inter R.open_target, ?_, ?_, ?_⟩
  · exact ⟨analyticAt_inverse ha hd, hd.image_mem_toOpenPartialHomeomorph_target⟩
  · intro y hy
    exact hy.1
  · intro y hy
    exact R.right_inv hy.2

end Komorebi.PolynomialAnalyticInverse
