import KomorebiSpace.HolonomyProjection
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# Quadratic gap certificates with the correct residual-norm conversion

The existing edge-family norm is the maximum norm. A squared Euclidean
stacking estimate therefore contributes sqrt(card I), not a silent
identification of the maximum norm with a Hilbert norm.
The generic finite-dimensional gain is derived independently; this module
supplies one way to certify an explicit bound for it.
-/
universe u v w
noncomputable section
namespace KomorebiSpace
namespace KernelProjection
variable {E : Type u} {F : Type v} {I : Type w}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [FiniteDimensional ℝ E]
variable [NormedAddCommGroup F] [NormedSpace ℝ F] [Fintype I]
variable (d : E →L[ℝ] (I → F))

/-- A checkable lower bound on the squared loop defect in complementary directions. -/
def QuadraticGap (lam : ℝ) : Prop :=
  ∀ x : E, x ∈ d.kerᗮ → lam * ‖x‖^2 ≤ ∑ i : I, ‖d x i‖^2

omit [FiniteDimensional ℝ E] in
/-- Squared stacked residual is bounded by the number of components times the max norm squared. -/
theorem sum_squared_le_card (x : E) :
    (∑ i : I, ‖d x i‖^2) ≤ (Fintype.card I : ℝ) * ‖d x‖^2 := by
  calc
    _ ≤ ∑ _i : I, ‖d x‖^2 := by
      apply Finset.sum_le_sum
      intro i _hi
      have hn := norm_le_pi_norm (d x) i
      have h0 := norm_nonneg (d x i)
      nlinarith
    _ = _ := by simp [Finset.sum_const, nsmul_eq_mul]

/-- An explicit squared estimate for the constructed orthogonal correction. -/
theorem error_sq_of_quadratic_gap (lam : ℝ) (hg : QuadraticGap d lam) (x : E) :
    lam * ‖x-projection d x‖^2 ≤ (Fintype.card I : ℝ) * ‖d x‖^2 := by
  have hb := hg (x-projection d x) (error_orthogonal d x)
  have hn := sum_squared_le_card d (x-projection d x)
  rw [defect_error] at hn hb
  exact hb.trans hn

/-- Explicit max-residual bound; the sqrt(card I) conversion is retained. -/
theorem error_of_quadratic_gap (lam : ℝ) (hpos : 0 < lam)
    (hg : QuadraticGap d lam) (x : E) :
    ‖x-projection d x‖ ≤ Real.sqrt ((Fintype.card I : ℝ)/lam) * ‖d x‖ := by
  have hs := error_sq_of_quadratic_gap d lam hg x
  have hb : ‖x-projection d x‖^2 ≤ ((Fintype.card I : ℝ) * ‖d x‖^2)/lam := by
    apply (le_div_iff₀ hpos).mpr
    nlinarith
  have hn : 0 ≤ (Fintype.card I : ℝ)/lam := by positivity
  have he : ((Fintype.card I : ℝ) * ‖d x‖^2)/lam =
      (Real.sqrt ((Fintype.card I : ℝ)/lam) * ‖d x‖)^2 := by
    rw [mul_pow, Real.sq_sqrt hn]
    ring
  rw [he] at hb
  exact (sq_le_sq₀ (norm_nonneg _) (by positivity)).mp hb

theorem gain_le_of_quadratic_gap (lam : ℝ) (hpos : 0 < lam)
    (hg : QuadraticGap d lam) :
    gain d ≤ Real.sqrt ((Fintype.card I : ℝ)/lam) :=
  gain_le_of_bound d _ (Real.sqrt_nonneg _) (error_of_quadratic_gap d lam hpos hg)

end KernelProjection

namespace HolonomyTransport
namespace Rooted
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [FiniteDimensional ℝ H]
variable [Fintype V]
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

theorem holonomyGain_certificate (lam : ℝ) (hpos : 0 < lam)
    (hg : KernelProjection.QuadraticGap (rootResidualMap T p) lam) :
    holonomyGain T p ≤ Real.sqrt ((Fintype.card (OverlapTransport.Edges graph) : ℝ)/lam) :=
  KernelProjection.gain_le_of_quadratic_gap (rootResidualMap T p) lam hpos hg

/-- A certified squared spectral lower bound yields a numerical graph repair bound
without replacing the existing maximum residual norm by a Euclidean product norm. -/
theorem certified_orthogonalRepair_error (lam : ℝ) (hpos : 0 < lam)
    (hg : KernelProjection.QuadraticGap (rootResidualMap T p) lam) (x : V → H) :
    ‖x-orthogonalRepair T p x‖ ≤
      ((p.radius : ℝ) + Real.sqrt ((Fintype.card (OverlapTransport.Edges graph) : ℝ)/lam) *
        (2*(p.radius : ℝ)+1)) * ‖T.differential graph x‖ := by
  have hc := mul_le_mul_of_nonneg_right (holonomyGain_certificate T p lam hpos hg)
    (show 0 ≤ 2*(p.radius : ℝ)+1 by positivity)
  exact (orthogonalRepair_error T p x).trans
    (mul_le_mul_of_nonneg_right (add_le_add le_rfl hc) (norm_nonneg _))

end Rooted
end HolonomyTransport
end KomorebiSpace
end
