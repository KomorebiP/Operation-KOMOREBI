import KomorebiSpace.ResidualSampling

set_option autoImplicit false

/-!
# Levelwise residual decay under cofinal bounded-gap resampling

The hypothesis concerns norms of adjacent operators at growing resolution,
not a sequence of entire candidates converging in the sup norm. The conclusion
is one-way: cancellation prevents a converse in general.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace BanachTower
open Filter
open scoped Topology
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)
variable (hX : ∀ n, ‖X.down n‖ ≤ 1) (hY : ∀ n, ‖Y.down n‖ ≤ 1)
include hX hY

/-- A block whose component residual norms are bounded by e has budget length * e. -/
theorem blockSum_local_bound (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n)
    {i j : ℕ} (h : i ≤ j) (e : ℝ) (he : ∀ k, i ≤ k → k < j → ‖r k‖ ≤ e) :
    ‖blockSum X Y r h‖ ≤ (j-i : ℕ)*e := by
  apply (blockSum_norm X Y hX hY r h).trans
  calc
    (∑ k ∈ Finset.Ico i j, ‖r k‖) ≤ ∑ _k ∈ Finset.Ico i j, e := by
      apply Finset.sum_le_sum
      intro k hk
      exact he k (Finset.mem_Ico.mp hk).1 (Finset.mem_Ico.mp hk).2
    _ = (j-i : ℕ)*e := by simp

/-- Cofinal bounded-gap sampling preserves levelwise decay of actual operator residuals. -/
theorem blockSum_cofinal_vanish (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n)
    (hr : Tendsto (fun n => ‖r n‖) atTop (𝓝 0))
    (φ : ℕ → ℕ) (hφ : Monotone φ) (hc : Resolution.UnboundedSchedule φ)
    (M : ℕ) (hgap : ∀ n, φ (n+1)-φ n ≤ M) :
    Tendsto (fun n => ‖blockSum X Y r (hφ (Nat.le_succ n))‖) atTop (𝓝 0) := by
  apply Metric.tendsto_atTop.2
  intro ε hε
  have hden : 0 < (M : ℝ)+1 := by positivity
  have he : 0 < ε/((M : ℝ)+1) := div_pos hε hden
  have ht : ∀ᶠ k in atTop, ‖r k‖ < ε/((M : ℝ)+1) :=
    (tendsto_order.1 hr).2 _ he
  obtain ⟨N, hN⟩ := eventually_atTop.1 ht
  obtain ⟨K, hK⟩ := hc N
  refine ⟨K, ?_⟩
  intro n hn
  have hφN : N ≤ φ n := hK.trans (hφ hn)
  have hb := blockSum_local_bound X Y hX hY r (hφ (Nat.le_succ n))
    (ε/((M : ℝ)+1)) (fun k hk _ => (hN k (hφN.trans hk)).le)
  have hle : ‖blockSum X Y r (hφ (Nat.le_succ n))‖ ≤
      (M : ℝ)*(ε/((M : ℝ)+1)) :=
    hb.trans (mul_le_mul_of_nonneg_right (by exact_mod_cast hgap n) he.le)
  have heq : ε/((M : ℝ)+1)*((M : ℝ)+1)=ε := div_mul_cancel₀ ε (ne_of_gt hden)
  have hlt : ‖blockSum X Y r (hφ (Nat.le_succ n))‖ < ε := by nlinarith
  simpa only [Real.dist_eq, sub_zero, abs_of_nonneg (norm_nonneg _)] using hlt

/-- Specialization to a single bounded candidate with asymptotically vanishing fine defects. -/
theorem sampled_levelwise_residual_vanish (f : Candidates X Y)
    (hf : Tendsto (fun n => ‖differential X Y f n‖) atTop (𝓝 0))
    (φ : ℕ → ℕ) (hφ : Monotone φ) (hc : Resolution.UnboundedSchedule φ)
    (M : ℕ) (hgap : ∀ n, φ (n+1)-φ n ≤ M) :
    Tendsto (fun n => ‖differential (resample X hX φ hφ) (resample Y hY φ hφ)
      (sampleCLM X Y hX hY φ hφ f) n‖) atTop (𝓝 0) := by
  have h := blockSum_cofinal_vanish X Y hX hY (differential X Y f) hf φ hφ hc M hgap
  simpa only [blockSum_differential, sampled_differential_coordinate] using h

end BanachTower
end KomorebiSpace
end
