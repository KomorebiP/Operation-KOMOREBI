import KomorebiLSM.MemoryStability

/-! The coefficient, tail and initialization budgets used by P19.
Zero prehistory and horizons shorter than the memory length are explicit. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Stability
universe u v w
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {X : Type v} [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable {Y : Type w} [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]

def memoryKernel (B : Y →L[𝕜] X) (C : X →L[𝕜] Y) (D : Y →L[𝕜] Y)
    (k : ℕ) : X →L[𝕜] X := B.comp ((D^k).comp C)

/-- Padding a shorter history by zeros has no artificial contribution. -/
theorem padded_sum_split (f : ℕ → X) (t H : ℕ) (zero_tail : ∀ k, t ≤ k → f k=0) :
    (∑ k ∈ Finset.range t, f k) =
      (∑ k ∈ Finset.range H, f k)+(∑ k ∈ Finset.Ico H t, f k) := by
  by_cases h : H ≤ t
  · exact (Finset.sum_range_add_sum_Ico f h).symm
  · have ht : t ≤ H := by omega
    rw [Finset.Ico_eq_empty_of_le ht, Finset.sum_empty, add_zero]
    apply Finset.sum_subset (Finset.range_mono ht)
    intro k _ hk
    exact zero_tail k (by simpa only [Finset.mem_range, not_lt] using hk)

theorem initialized_memory_split (K : ℕ → X →L[𝕜] X) (z : ℤ → X)
    (zero_past : ∀ s : ℤ, s < 0 → z s=0) (t H : ℕ) :
    (∑ k ∈ Finset.range t, K k (z ((t:ℤ)-1-(k:ℤ)))) =
      (∑ k ∈ Finset.range H, K k (z ((t:ℤ)-1-(k:ℤ))))+
      (∑ k ∈ Finset.Ico H t, K k (z ((t:ℤ)-1-(k:ℤ)))) := by
  apply padded_sum_split
  intro k hk
  rw [zero_past _ (by omega), map_zero]

theorem memory_defect_identity (A Ahat : X →L[𝕜] X)
    (K Khat : ℕ → X →L[𝕜] X) (z : ℤ → X) (f g : ℕ → X)
    (zero_past : ∀ s : ℤ, s < 0 → z s=0) (H t : ℕ)
    (step : z ((t:ℤ)+1)=A (z t)+
      (∑ k ∈ Finset.range t, K k (z ((t:ℤ)-1-(k:ℤ))))+f t) :
    z ((t:ℤ)+1)-(finiteMemory Ahat Khat H z t+g t) =
      (A-Ahat) (z t)+
      (∑ k ∈ Finset.range H, (K k-Khat k) (z ((t:ℤ)-1-(k:ℤ))))+
      (∑ k ∈ Finset.Ico H t, K k (z ((t:ℤ)-1-(k:ℤ))))+(f t-g t) := by
  rw [step, initialized_memory_split K z zero_past t H]
  simp only [finiteMemory, sub_apply, Finset.sum_sub_distrib]
  abel

theorem bounded_with_zero_prehistory (z : ℤ → X) {Z : ℝ} (hZ : 0 ≤ Z)
    (zero_past : ∀ s : ℤ, s < 0 → z s=0)
    (bounded : ∀ s : ℤ, 0 ≤ s → ‖z s‖ ≤ Z) (s : ℤ) : ‖z s‖ ≤ Z := by
  by_cases hs : 0 ≤ s
  · exact bounded s hs
  · rw [zero_past s (lt_of_not_ge hs), norm_zero]
    exact hZ

theorem integer_memory_tail_bound (B : Y →L[𝕜] X) (C : X →L[𝕜] Y)
    (D : Y →L[𝕜] Y) (z : ℤ → X) {rho Z : ℝ}
    (hrho : 0 ≤ rho) (hsmall : rho < 1) (hD : ‖D‖ ≤ rho) (hZ : 0 ≤ Z)
    (bounded : ∀ s, ‖z s‖ ≤ Z) (H t : ℕ) :
    ‖∑ k ∈ Finset.Ico H t, memoryKernel B C D k (z ((t:ℤ)-1-(k:ℤ)))‖ ≤
      (‖B‖*‖C‖*Z)*(rho^H/(1-rho)) := by
  calc
    ‖∑ k ∈ Finset.Ico H t, memoryKernel B C D k (z ((t:ℤ)-1-(k:ℤ)))‖ ≤
        ∑ k ∈ Finset.Ico H t, ‖memoryKernel B C D k (z ((t:ℤ)-1-(k:ℤ)))‖ := norm_sum_le _ _
    _ ≤ ∑ k ∈ Finset.Ico H t, (‖B‖*‖C‖*Z)*rho^k := by
      apply Finset.sum_le_sum
      intro k _
      exact memory_kernel_bound B C D hrho hD _ (bounded _) k
    _ = (‖B‖*‖C‖*Z)*∑ k ∈ Finset.Ico H t, rho^k := by rw [Finset.mul_sum]
    _ ≤ _ := mul_le_mul_of_nonneg_left (geometric_interval_bound hrho hsmall H t)
      (mul_nonneg (mul_nonneg (norm_nonneg _) (norm_nonneg _)) hZ)

/-- This is the full Delta formula, with a separately bounded forcing error.
It covers H=0 and times t<H, not only a settled memory window. -/
theorem memory_approximation_defect_bound (A Ahat : X →L[𝕜] X)
    (B : Y →L[𝕜] X) (C : X →L[𝕜] Y) (D : Y →L[𝕜] Y)
    (Khat : ℕ → X →L[𝕜] X) (z : ℤ → X) (f g : ℕ → X)
    {rho Z F0 : ℝ} (hrho : 0 ≤ rho) (hsmall : rho < 1) (hD : ‖D‖ ≤ rho)
    (hZ : 0 ≤ Z) (zero_past : ∀ s : ℤ, s < 0 → z s=0)
    (bounded : ∀ s : ℤ, 0 ≤ s → ‖z s‖ ≤ Z)
    (forcing : ∀ t, ‖f t-g t‖ ≤ F0) (H t : ℕ)
    (step : z ((t:ℤ)+1)=A (z t)+
      (∑ k ∈ Finset.range t, memoryKernel B C D k (z ((t:ℤ)-1-(k:ℤ))))+f t) :
    ‖z ((t:ℤ)+1)-(finiteMemory Ahat Khat H z t+g t)‖ ≤
      Z*(‖A-Ahat‖+∑ k ∈ Finset.range H, ‖memoryKernel B C D k-Khat k‖)+
      (‖B‖*‖C‖*Z)*(rho^H/(1-rho))+F0 := by
  rw [memory_defect_identity A Ahat (memoryKernel B C D) Khat z f g zero_past H t step]
  have hz := bounded_with_zero_prehistory z hZ zero_past bounded
  have hfirst : ‖(A-Ahat) (z t)‖ ≤ ‖A-Ahat‖*Z :=
    ((A-Ahat).le_opNorm _).trans (mul_le_mul_of_nonneg_left (hz t) (norm_nonneg _))
  have hcoeff :
      ‖∑ k ∈ Finset.range H, (memoryKernel B C D k-Khat k) (z ((t:ℤ)-1-(k:ℤ)))‖ ≤
      (∑ k ∈ Finset.range H, ‖memoryKernel B C D k-Khat k‖)*Z := by
    apply (norm_sum_le _ _).trans
    rw [Finset.sum_mul]
    apply Finset.sum_le_sum
    intro k _
    exact ((memoryKernel B C D k-Khat k).le_opNorm _).trans
      (mul_le_mul_of_nonneg_left (hz _) (norm_nonneg _))
  have htail := integer_memory_tail_bound B C D z hrho hsmall hD hZ hz H t
  have hnorm := norm_add_le
    ((A-Ahat) (z t)+(∑ k ∈ Finset.range H, (memoryKernel B C D k-Khat k) (z ((t:ℤ)-1-(k:ℤ))))+
      (∑ k ∈ Finset.Ico H t, memoryKernel B C D k (z ((t:ℤ)-1-(k:ℤ))))) (f t-g t)
  have hnorm2 := norm_add_le
    ((A-Ahat) (z t)+(∑ k ∈ Finset.range H, (memoryKernel B C D k-Khat k) (z ((t:ℤ)-1-(k:ℤ)))))
    (∑ k ∈ Finset.Ico H t, memoryKernel B C D k (z ((t:ℤ)-1-(k:ℤ))))
  have hnorm3 := norm_add_le ((A-Ahat) (z t))
    (∑ k ∈ Finset.range H, (memoryKernel B C D k-Khat k) (z ((t:ℤ)-1-(k:ℤ))))
  calc
    _ ≤ (‖A-Ahat‖*Z+(∑ k ∈ Finset.range H, ‖memoryKernel B C D k-Khat k‖)*Z)+
        (‖B‖*‖C‖*Z)*(rho^H/(1-rho))+F0 := by linarith [forcing t]
    _ = _ := by ring

theorem discarded_initialized_forcing_bound (B : Y →L[𝕜] X) (D : Y →L[𝕜] Y)
    {rho : ℝ} (hrho : 0 ≤ rho) (hsmall : rho < 1) (hD : ‖D‖ ≤ rho)
    (q0 : Y) (t : ℕ) : ‖B ((D^t) q0)-(0 : X)‖ ≤ ‖B‖*‖q0‖ := by
  rw [sub_zero]
  apply (unresolved_initial_bound B D hrho hD q0 t).trans
  calc
    ‖B‖*rho^t*‖q0‖ ≤ ‖B‖*1*‖q0‖ :=
      mul_le_mul_of_nonneg_right
        (mul_le_mul_of_nonneg_left (pow_le_one₀ hrho hsmall.le) (norm_nonneg _)) (norm_nonneg _)
    _ = _ := by ring

/-- Retaining the exact initialization forcing removes its contribution. -/
theorem retained_initialized_forcing_bound (f : ℕ → X) (t : ℕ) : ‖f t-f t‖ ≤ (0 : ℝ) := by simp

/-- The coefficient/tail budget is inserted into the recursive, not same-history,
prediction theorem. -/
theorem certified_memory_truncation (A Ahat : X →L[𝕜] X)
    (B : Y →L[𝕜] X) (C : X →L[𝕜] Y) (D : Y →L[𝕜] Y)
    (Khat : ℕ → X →L[𝕜] X) (H : ℕ) (z w : ℤ → X) (f g : ℕ → X)
    {rho Z F0 E0 : ℝ} (hrho : 0 ≤ rho) (hsmall : rho < 1) (hD : ‖D‖ ≤ rho)
    (hZ : 0 ≤ Z) (hE0 : 0 ≤ E0)
    (zero_past : ∀ s : ℤ, s < 0 → z s=0)
    (bounded : ∀ s : ℤ, 0 ≤ s → ‖z s‖ ≤ Z)
    (forcing : ∀ t, ‖f t-g t‖ ≤ F0)
    (true_step : ∀ t : ℕ, z ((t:ℤ)+1)=A (z t)+
      (∑ k ∈ Finset.range t, memoryKernel B C D k (z ((t:ℤ)-1-(k:ℤ))))+f t)
    (pred_step : ∀ t : ℕ, w ((t:ℤ)+1)=finiteMemory Ahat Khat H w t+g t)
    (initial : ∀ s : ℤ, -(H:ℤ) ≤ s → s ≤ 0 → ‖z s-w s‖ ≤ E0)
    (stable : memoryGain Ahat Khat H < 1) :
    sSup (Set.range (fun t : ℕ => ‖z t-w t‖)) ≤
      max E0 ((Z*(‖A-Ahat‖+∑ k ∈ Finset.range H, ‖memoryKernel B C D k-Khat k‖)+
        (‖B‖*‖C‖*Z)*(rho^H/(1-rho))+F0)/(1-memoryGain Ahat Khat H)) := by
  apply finite_memory_uniform_prediction_bound Ahat Khat H z w g stable hE0 initial pred_step
  intro t
  exact memory_approximation_defect_bound A Ahat B C D Khat z f g hrho hsmall hD hZ
    zero_past bounded forcing H t (true_step t)

end Komorebi.LSM.Stability
