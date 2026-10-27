import KomorebiLSM.MemoryBounds
import KomorebiLSM.DefectPropagation

/-! P19: the finite-memory predictor is evaluated on its own recursively
computed history. Integer indices retain explicit initialization. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Stability
universe u v
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {X : Type v} [NormedAddCommGroup X] [NormedSpace 𝕜 X]

/-- The finite-memory transition before any added, shared forcing. -/
def finiteMemory (A : X →L[𝕜] X) (K : ℕ → X →L[𝕜] X) (H : ℕ)
    (z : ℤ → X) (t : ℤ) : X := A (z t)+∑ k ∈ Finset.range H, K k (z (t-1-(k:ℤ)))

noncomputable def memoryGain (A : X →L[𝕜] X) (K : ℕ → X →L[𝕜] X) (H : ℕ) : ℝ :=
  ‖A‖+∑ k ∈ Finset.range H, ‖K k‖

theorem memoryGain_nonneg (A : X →L[𝕜] X) (K : ℕ → X →L[𝕜] X) (H : ℕ) :
    0 ≤ memoryGain A K H :=
  add_nonneg (norm_nonneg _) (Finset.sum_nonneg (fun _ _ => norm_nonneg _))

theorem finiteMemory_sub (A : X →L[𝕜] X) (K : ℕ → X →L[𝕜] X) (H : ℕ)
    (z w : ℤ → X) (t : ℤ) :
    finiteMemory A K H z t-finiteMemory A K H w t =
      A (z t-w t)+∑ k ∈ Finset.range H, K k (z (t-1-(k:ℤ))-w (t-1-(k:ℤ))) := by
  simp only [finiteMemory, map_sub, Finset.sum_sub_distrib]
  abel

theorem finiteMemory_error_bound (A : X →L[𝕜] X) (K : ℕ → X →L[𝕜] X)
    (H : ℕ) (z w : ℤ → X) (t : ℤ) {E : ℝ}
    (window : ∀ s, t-(H:ℤ) ≤ s → s ≤ t → ‖z s-w s‖ ≤ E) :
    ‖finiteMemory A K H z t-finiteMemory A K H w t‖ ≤ memoryGain A K H*E := by
  rw [finiteMemory_sub]
  calc
    ‖A (z t-w t)+∑ k ∈ Finset.range H, K k (z (t-1-(k:ℤ))-w (t-1-(k:ℤ)))‖ ≤
        ‖A (z t-w t)‖+∑ k ∈ Finset.range H, ‖K k (z (t-1-(k:ℤ))-w (t-1-(k:ℤ)))‖ :=
      (norm_add_le _ _).trans (add_le_add le_rfl (norm_sum_le _ _))
    _ ≤ ‖A‖*E+∑ k ∈ Finset.range H, ‖K k‖*E := by
      apply add_le_add
      · exact (A.le_opNorm _).trans
          (mul_le_mul_of_nonneg_left (window t (by omega) le_rfl) (norm_nonneg A))
      · apply Finset.sum_le_sum
        intro k hk
        have hk' := Finset.mem_range.mp hk
        exact ((K k).le_opNorm _).trans (mul_le_mul_of_nonneg_left
          (window _ (by omega) (by omega)) (norm_nonneg _))
    _ = _ := by rw [memoryGain, add_mul, Finset.sum_mul]

/-- The common invariant error radius, including the initial window. -/
theorem invariant_error_radius {a E0 D : ℝ} (ha : a < 1) (hE0 : 0 ≤ E0) :
    let E := max E0 (D/(1-a))
    0 ≤ E ∧ E0 ≤ E ∧ a*E+D ≤ E := by
  dsimp
  have hd : D ≤ max E0 (D/(1-a))*(1-a) :=
    (div_le_iff₀ (sub_pos.mpr ha)).mp (le_max_right _ _)
  exact ⟨hE0.trans (le_max_left _ _), le_max_left _ _, by nlinarith⟩

/-- Defects are evaluated on the true history; the conclusion concerns the
approximate recurrence's own history, including its separate initialization. -/
theorem finite_memory_prediction_bound (A : X →L[𝕜] X) (K : ℕ → X →L[𝕜] X)
    (H : ℕ) (z w : ℤ → X) (g : ℕ → X) {D E0 : ℝ}
    (stable : memoryGain A K H < 1) (hE0 : 0 ≤ E0)
    (initial : ∀ s : ℤ, -(H:ℤ) ≤ s → s ≤ 0 → ‖z s-w s‖ ≤ E0)
    (pred_step : ∀ t : ℕ, w ((t:ℤ)+1)=finiteMemory A K H w t+g t)
    (defect : ∀ t : ℕ, ‖z ((t:ℤ)+1)-(finiteMemory A K H z t+g t)‖ ≤ D)
    (T : ℕ) :
    ‖z T-w T‖ ≤ max E0 (D/(1-memoryGain A K H)) := by
  let E := max E0 (D/(1-memoryGain A K H))
  obtain ⟨_, hinit, hinv⟩ := invariant_error_radius stable hE0
  have invariant : ∀ t : ℕ, ∀ s : ℤ, -(H:ℤ) ≤ s → s ≤ (t:ℤ) → ‖z s-w s‖ ≤ E := by
    intro t
    induction t with
    | zero =>
      intro s hs ht
      exact (initial s hs (by simpa using ht)).trans hinit
    | succ t ih =>
      intro s hs ht
      by_cases hold : s ≤ (t:ℤ)
      · exact ih s hs hold
      · have heq : s=(t:ℤ)+1 := by omega
        rw [heq, pred_step]
        have hmem := finiteMemory_error_bound A K H z w (t:ℤ)
          (fun j hj htop => ih j (by omega) htop)
        have htri := norm_add_le
          (z ((t:ℤ)+1)-(finiteMemory A K H z t+g t))
          (finiteMemory A K H z t-finiteMemory A K H w t)
        have hid : (z ((t:ℤ)+1)-(finiteMemory A K H z t+g t))+
            (finiteMemory A K H z t-finiteMemory A K H w t) =
            z ((t:ℤ)+1)-(finiteMemory A K H w t+g t) := by abel
        rw [hid] at htri
        exact (htri.trans (add_le_add (defect t) hmem)).trans
          (by dsimp [E] at *; linarith)
  exact invariant T T (by omega) le_rfl

/-- The pointwise result yields the stated supremum over nonnegative time. -/
theorem finite_memory_uniform_prediction_bound (A : X →L[𝕜] X)
    (K : ℕ → X →L[𝕜] X) (H : ℕ) (z w : ℤ → X) (g : ℕ → X) {D E0 : ℝ}
    (stable : memoryGain A K H < 1) (hE0 : 0 ≤ E0)
    (initial : ∀ s : ℤ, -(H:ℤ) ≤ s → s ≤ 0 → ‖z s-w s‖ ≤ E0)
    (pred_step : ∀ t : ℕ, w ((t:ℤ)+1)=finiteMemory A K H w t+g t)
    (defect : ∀ t : ℕ, ‖z ((t:ℤ)+1)-(finiteMemory A K H z t+g t)‖ ≤ D) :
    sSup (Set.range (fun t : ℕ => ‖z t-w t‖)) ≤ max E0 (D/(1-memoryGain A K H)) := by
  apply csSup_le (Set.range_nonempty _)
  rintro _ ⟨t, rfl⟩
  exact finite_memory_prediction_bound A K H z w g stable hE0 initial pred_step defect t

end Komorebi.LSM.Stability
