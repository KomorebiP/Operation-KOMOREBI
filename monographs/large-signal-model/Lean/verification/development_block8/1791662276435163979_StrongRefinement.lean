import KomorebiLSM.Normed
import Mathlib.Analysis.InnerProductSpace.Projection.Basic

/-! P13: strong convergence of compressed bounded operators at each fixed horizon.
Uniform operator bounds are used, not operator-norm convergence. -/
set_option autoImplicit false
open Filter
open scoped Topology
namespace Komorebi.LSM.Stability
universe u v w
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {X : Type v} [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable {Y : Type w} [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]

/-- A uniform operator bound permits a strongly convergent family to act on
convergent varying vectors. -/
theorem strong_apply_varying (A : ℕ → X →L[𝕜] Y) (L : X →L[𝕜] Y)
    {C : ℝ} (bound : ∀ n, ‖A n‖ ≤ C)
    (strong : ∀ x, Tendsto (fun n => A n x) atTop (𝓝 (L x)))
    (x : ℕ → X) (v : X) (hx : Tendsto x atTop (𝓝 v)) :
    Tendsto (fun n => A n (x n)) atTop (𝓝 (L v)) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  have hbound : ∀ n, ‖A n (x n)-L v‖ ≤
      C*‖x n-v‖ + ‖A n v-L v‖ := by
    intro n
    calc
      ‖A n (x n)-L v‖ = ‖A n (x n-v)+(A n v-L v)‖ := by
        rw [map_sub]; congr 1; abel
      _ ≤ ‖A n (x n-v)‖+‖A n v-L v‖ := norm_add_le _ _
      _ ≤ C*‖x n-v‖+‖A n v-L v‖ := by
        apply add_le_add _ le_rfl
        exact ((A n).le_opNorm _).trans
          (mul_le_mul_of_nonneg_right (bound n) (norm_nonneg _))
  have hz : Tendsto (fun n => C*‖x n-v‖+‖A n v-L v‖) atTop (𝓝 0) := by
    convert (tendsto_const_nhds.mul (tendsto_iff_norm_sub_tendsto_zero.mp hx)).add
      (tendsto_iff_norm_sub_tendsto_zero.mp (strong v)) using 1; simp
  exact squeeze_zero (fun n => norm_nonneg _) hbound hz

/-- Powers are taken at a fixed finite horizon. -/
theorem strong_fixed_powers (A : ℕ → X →L[𝕜] X) (L : X →L[𝕜] X)
    {C : ℝ} (bound : ∀ n, ‖A n‖ ≤ C)
    (strong : ∀ x, Tendsto (fun n => A n x) atTop (𝓝 (L x)))
    (x : X) (k : ℕ) : Tendsto (fun n => ((A n)^k) x) atTop (𝓝 ((L^k) x)) := by
  induction k with
  | zero => simp
  | succ k ih =>
    have h := strong_apply_varying A L bound strong (fun n => ((A n)^k) x)
      ((L^k) x) ih
    simpa only [pow_succ', mul_apply_eq_comp] using h

/-- The local consistency estimate for compression. -/
theorem compression_error_bound (L P : X →L[𝕜] X) (hP : ‖P‖ ≤ 1) (x : X) :
    ‖P (L (P x))-L x‖ ≤ ‖L‖*‖P x-x‖+‖P (L x)-L x‖ := by
  calc
    ‖P (L (P x))-L x‖ = ‖P (L (P x-x))+(P (L x)-L x)‖ := by
      simp only [map_sub]; congr 1; abel
    _ ≤ ‖P (L (P x-x))‖+‖P (L x)-L x‖ := norm_add_le _ _
    _ ≤ ‖L‖*‖P x-x‖+‖P (L x)-L x‖ := by
      apply add_le_add _ le_rfl
      calc
        ‖P (L (P x-x))‖ ≤ ‖P‖*‖L (P x-x)‖ := P.le_opNorm _
        _ ≤ 1*‖L (P x-x)‖ := mul_le_mul_of_nonneg_right hP (norm_nonneg _)
        _ ≤ ‖L‖*‖P x-x‖ := by simpa only [one_mul] using L.le_opNorm (P x-x)

theorem compression_uniform_bound (L P : X →L[𝕜] X) (hP : ‖P‖ ≤ 1) :
    ‖P.comp (L.comp P)‖ ≤ ‖L‖ := by
  apply ContinuousLinearMap.opNorm_le_bound _ (norm_nonneg L)
  intro x
  calc
    ‖P (L (P x))‖ ≤ ‖P‖*‖L (P x)‖ := P.le_opNorm _
    _ ≤ 1*‖L (P x)‖ := mul_le_mul_of_nonneg_right hP (norm_nonneg _)
    _ ≤ ‖L‖*‖x‖ := by
      simp only [one_mul]
      apply (L.le_opNorm _).trans
      apply mul_le_mul_of_nonneg_left _ (norm_nonneg L)
      exact (P.le_opNorm _).trans (by simpa using mul_le_mul_of_nonneg_right hP (norm_nonneg x))

theorem compression_strong (L : X →L[𝕜] X) (P : ℕ → X →L[𝕜] X)
    (hP : ∀ n, ‖P n‖ ≤ 1)
    (hstrong : ∀ x, Tendsto (fun n => P n x) atTop (𝓝 x)) (x : X) :
    Tendsto (fun n => P n (L (P n x))) atTop (𝓝 (L x)) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  have hz : Tendsto (fun n => ‖L‖*‖P n x-x‖+‖P n (L x)-L x‖) atTop (𝓝 0) := by
    convert (tendsto_const_nhds.mul (tendsto_iff_norm_sub_tendsto_zero.mp (hstrong x))).add
      (tendsto_iff_norm_sub_tendsto_zero.mp (hstrong (L x))) using 1; simp
  exact squeeze_zero (fun _ => norm_nonneg _) (fun n => compression_error_bound L (P n) (hP n) x) hz

/-- The generalized contraction-family statement includes orthogonal projections. -/
theorem contractive_refinement_fixed_horizon (L : X →L[𝕜] X) (P : ℕ → X →L[𝕜] X)
    (hP : ∀ n, ‖P n‖ ≤ 1)
    (hstrong : ∀ x, Tendsto (fun n => P n x) atTop (𝓝 x)) (x : X) (k : ℕ) :
    Tendsto (fun n => (((P n).comp (L.comp (P n)))^k) x) atTop (𝓝 ((L^k) x)) := by
  exact strong_fixed_powers (fun n => (P n).comp (L.comp (P n))) L
    (fun n => compression_uniform_bound L (P n) (hP n))
    (compression_strong L P hP hstrong) x k

/-- Additional fitted-operator errors may vanish strongly, provided their own
uniform bound is supplied. This is not inferred from a fitting procedure. -/
theorem estimated_refinement_fixed_horizon (L : X →L[𝕜] X)
    (A Ahat : ℕ → X →L[𝕜] X) {C : ℝ}
    (bound : ∀ n, ‖Ahat n‖ ≤ C)
    (strong : ∀ x, Tendsto (fun n => A n x) atTop (𝓝 (L x)))
    (error : ∀ x, Tendsto (fun n => (Ahat n-A n) x) atTop (𝓝 0)) (x : X) (k : ℕ) :
    Tendsto (fun n => ((Ahat n)^k) x) atTop (𝓝 ((L^k) x)) := by
  apply strong_fixed_powers Ahat L bound
  intro y
  have h := (error y).add (strong y)
  simpa only [sub_apply, sub_add_cancel, zero_add] using h

section Orthogonal
variable {𝕜' E : Type*} [RCLike 𝕜'] [NormedAddCommGroup E] [InnerProductSpace 𝕜' E]

/-- Actual orthogonal projection maps supply the contraction hypothesis. -/
theorem strong_fixed_horizon_refinement (L : E →L[𝕜'] E) (S : ℕ → Submodule 𝕜' E)
    [∀ n, (S n).HasOrthogonalProjection]
    (hstrong : ∀ x, Tendsto (fun n => (S n).starProjection x) atTop (𝓝 x))
    (x : E) (k : ℕ) :
    Tendsto (fun n => (((S n).starProjection.comp (L.comp (S n).starProjection))^k) x)
      atTop (𝓝 ((L^k) x)) := by
  exact contractive_refinement_fixed_horizon L (fun n => (S n).starProjection)
    (fun n => (S n).starProjection_norm_le) hstrong x k

end Orthogonal
end Komorebi.LSM.Stability
