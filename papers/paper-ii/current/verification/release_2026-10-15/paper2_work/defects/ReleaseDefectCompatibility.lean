import ReleaseDefectTower
import ReleaseAnalyticExponential
import ReleaseAnalyticContour

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseDefectCompatibility
open TypedLinearDefects ReleaseDefectTower ReleaseAnalyticExponential ReleaseAnalyticContour
universe u v

/-- Exact arbitrary-depth exponential compatibility on a genuinely typed
Banach-space tower, derived from its local zero defects and Duhamel. -/
theorem multilevel_exponential_compatible
    {𝕜 : Type u} [RCLike 𝕜] {X : ℕ → Type v}
    [∀ n, NormedAddCommGroup (X n)] [∀ n, NormedSpace 𝕜 (X n)]
    [∀ n, NormedSpace ℝ (X n)] [∀ n, IsScalarTower ℝ 𝕜 (X n)]
    [∀ n, CompleteSpace (X n)]
    (C : ∀ n, X (n + 1) →L[𝕜] X n) (T : ∀ n, X n →L[𝕜] X n)
    (L : ℕ) (h : ∀ k : Fin L,
      continuousDefect (C k.val) (T (k.val + 1)) (T k.val) = 0) (t : 𝕜) :
    (continuousSegment C (Nat.zero_le L)).comp (NormedSpace.exp (t • T L)) =
      (NormedSpace.exp (t • T 0)).comp (continuousSegment C (Nat.zero_le L)) := by
  apply exponential_compatible_of_defect_eq_zero
  exact sub_eq_zero.mpr (continuous_multilevel_compatible C T L h)

/-- Exact arbitrary-depth compatibility of actual chosen-cycle integrals.
Canonical holomorphic-calculus identification remains a separate bridge. -/
theorem multilevel_dunfordIntegral_compatible
    {X : ℕ → Type v}
    [∀ n, NormedAddCommGroup (X n)] [∀ n, NormedSpace ℂ (X n)]
    [∀ n, NormedSpace ℝ (X n)] [∀ n, IsScalarTower ℝ ℂ (X n)]
    [∀ n, CompleteSpace (X n)]
    (C : ∀ n, X (n + 1) →L[ℂ] X n) (T : ∀ n, X n →L[ℂ] X n)
    (L : ℕ) (hd : ∀ k : Fin L,
      continuousDefect (C k.val) (T (k.val + 1)) (T k.val) = 0)
    (Γ : IntegralCycle) (h : ℂ → ℂ) (hh : ContinuousOn h Γ.trace)
    (hf : Γ.trace ⊆ resolventSet ℂ (T L)) (hc : Γ.trace ⊆ resolventSet ℂ (T 0)) :
    (continuousSegment C (Nat.zero_le L)).comp (dunfordIntegral Γ h (T L)) =
      (dunfordIntegral Γ h (T 0)).comp (continuousSegment C (Nat.zero_le L)) := by
  apply dunfordIntegral_compatible_of_defect_eq_zero Γ h hh _ _ _ hf hc
  exact sub_eq_zero.mpr (continuous_multilevel_compatible C T L hd)
end Komorebi.PaperII.ReleaseDefectCompatibility
