import KomorebiLSM.Normed
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Algebra.Field.GeomSum
import Mathlib.Topology.MetricSpace.Lipschitz
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-! P18: actual time-dependent trajectory defects and their propagated bounds. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Stability

/-- The exact scalar envelope, written with the manuscript's suffix products. -/
def errorEnvelope (l d : ℕ → ℝ) (e0 : ℝ) (T : ℕ) : ℝ :=
  (∏ j ∈ Finset.range T, l j) * e0 +
    ∑ k ∈ Finset.range T, (∏ j ∈ Finset.Ico (k+1) T, l j) * d k

@[simp] theorem errorEnvelope_zero (l d : ℕ → ℝ) (e0 : ℝ) :
    errorEnvelope l d e0 0 = e0 := by simp [errorEnvelope]

theorem errorEnvelope_succ (l d : ℕ → ℝ) (e0 : ℝ) (T : ℕ) :
    errorEnvelope l d e0 (T+1) = l T * errorEnvelope l d e0 T + d T := by
  rw [errorEnvelope, Finset.prod_range_succ, Finset.sum_range_succ]
  have hsum :
      (∑ k ∈ Finset.range T, (∏ j ∈ Finset.Ico (k+1) (T+1), l j) * d k) =
      l T * (∑ k ∈ Finset.range T, (∏ j ∈ Finset.Ico (k+1) T, l j) * d k) := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k hk
    rw [Finset.prod_Ico_succ_top (by simpa using Finset.mem_range.mp hk)]
    ring
  rw [hsum]
  simp only [Finset.Ico_self, Finset.prod_empty, one_mul]
  unfold errorEnvelope
  ring

theorem recurrence_product_sum (e l d : ℕ → ℝ) (hl : ∀ t, 0 ≤ l t)
    (step : ∀ t, e (t+1) ≤ l t * e t + d t) (T : ℕ) :
    e T ≤ errorEnvelope l d (e 0) T := by
  induction T with
  | zero => simp
  | succ T ih =>
    rw [errorEnvelope_succ]
    exact (step T).trans (add_le_add (mul_le_mul_of_nonneg_left ih (hl T)) le_rfl)

/-- The one-step inequality follows from a true local residual and the two
actual inputs to the approximate step. -/
theorem local_error_step {E F : Type*} [NormedAddCommGroup E] [NormedAddCommGroup F]
    (f : E → F) (x y : E) (next : F) {l d : ℝ}
    (defect : ‖next - f x‖ ≤ d) (lip : ‖f x - f y‖ ≤ l * ‖x-y‖) :
    ‖next - f y‖ ≤ l * ‖x-y‖ + d := by
  have ht := norm_add_le (next-f x) (f x-f y)
  have hid : (next-f x)+(f x-f y)=next-f y := by abel
  rw [hid] at ht
  linarith

universe u v
/-- State spaces may change at every time. The domain membership and Lipschitz
assumptions are not inferred from a small initial error. -/
theorem compositional_defect_propagation {X : Type u} {Z : ℕ → Type v}
    [∀ t, NormedAddCommGroup (Z t)]
    (gamma : (t : ℕ) → X → Z t) (F : ℕ → X → X)
    (f : (t : ℕ) → Z t → Z (t+1)) (x : ℕ → X) (zhat : (t : ℕ) → Z t)
    (domain : (t : ℕ) → Set (Z t)) (l : ℕ → NNReal) (d : ℕ → ℝ)
    (true_step : ∀ t, x (t+1)=F t (x t))
    (pred_step : ∀ t, zhat (t+1)=f t (zhat t))
    (true_mem : ∀ t, gamma t (x t) ∈ domain t)
    (pred_mem : ∀ t, zhat t ∈ domain t)
    (lip : ∀ t, LipschitzOnWith (l t) (f t) (domain t))
    (defect : ∀ t, ‖gamma (t+1) (F t (x t))-f t (gamma t (x t))‖ ≤ d t)
    (T : ℕ) :
    ‖gamma T (x T)-zhat T‖ ≤
      errorEnvelope (fun t => (l t : ℝ)) d ‖gamma 0 (x 0)-zhat 0‖ T := by
  apply recurrence_product_sum (fun t => ‖gamma t (x t)-zhat t‖)
    (fun t => (l t : ℝ)) d (fun t => (l t).coe_nonneg)
  intro t
  rw [true_step, pred_step]
  apply local_error_step _ _ _ _ (defect t)
  simpa only [dist_eq_norm] using (lip t).dist_le_mul (true_mem t) (pred_mem t)

theorem decoder_error_bound {E F : Type*} [NormedAddCommGroup E] [NormedAddCommGroup F]
    (H : E → F) (x y : E) (output : F) {k eta : ℝ}
    (residual : ‖output-H x‖ ≤ eta) (lip : ‖H x-H y‖ ≤ k*‖x-y‖) :
    ‖output-H y‖ ≤ eta+k*‖x-y‖ := by
  simpa only [add_comm] using local_error_step H x y output residual lip

theorem constant_gain_bound (e : ℕ → ℝ) {rho delta : ℝ}
    (hrho : 0 ≤ rho) (hsmall : rho < 1)
    (step : ∀ t, e (t+1) ≤ rho*e t+delta) (T : ℕ) :
    e T ≤ rho^T*e 0 + delta*((1-rho^T)/(1-rho)) := by
  have hden : 1-rho ≠ 0 := ne_of_gt (sub_pos.mpr hsmall)
  induction T with
  | zero => simp
  | succ T ih =>
    calc
      e (T+1) ≤ rho*e T+delta := step T
      _ ≤ rho*(rho^T*e 0+delta*((1-rho^T)/(1-rho)))+delta :=
        add_le_add (mul_le_mul_of_nonneg_left ih hrho) le_rfl
      _ = _ := by rw [pow_succ']; field_simp; ring

/-- The separation of representational and fitted-operator defects is literal
linear-map algebra. -/
theorem linear_defect_split {𝕜 E G : Type*} [CommRing 𝕜]
    [AddCommGroup E] [Module 𝕜 E] [AddCommGroup G] [Module 𝕜 G]
    (R : E →ₗ[𝕜] G) (L : E →ₗ[𝕜] E) (B Bhat : G →ₗ[𝕜] G) :
    R.comp L-Bhat.comp R = (R.comp L-B.comp R)+(B-Bhat).comp R := by
  ext x
  simp only [LinearMap.sub_apply, LinearMap.add_apply, LinearMap.comp_apply]
  abel

end Komorebi.LSM.Stability
