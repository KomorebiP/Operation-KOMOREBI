import Komorebi.SufficientResolution.ScalarBudgets

/-!
# Growth-controlled approximate sufficiency

All hypotheses are operator-norm bounds. The scalar rates are upper bounds, not
spectral radii. Conclusions hold for every finite word, not just test trajectories.
No dimension or finiteness of the alphabet is assumed.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.StableApproximation

open ApproximateBounds ScalarBudgets

universe uK uX uZ uY uI
variable {𝕜 : Type uK} [NontriviallyNormedField 𝕜]
variable {X : Type uX} [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable {Z : Type uZ} [NormedAddCommGroup Z] [NormedSpace 𝕜 Z]
variable {Y : Type uY} [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]
variable {I : Type uI}

theorem norm_word_uniform (T : I → X →L[𝕜] X) (a : ℝ)
    (ha : 0 ≤ a) (hT : ∀ i, ‖T i‖ ≤ a) (w : List I) :
    ‖word T w‖ ≤ a ^ w.length := by
  simpa using norm_word_le_gain T (fun _ => a) (fun _ => ha) hT w

/-- General two-rate perturbation theorem. -/
theorem norm_wordError_uniform (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (a b ε : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (he : 0 ≤ ε)
    (hT : ∀ i, ‖T i‖ ≤ a) (hU : ∀ i, ‖U i‖ ≤ b)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (w : List I) :
    ‖wordError q T U w‖ ≤ ε * response a b w.length := by
  simpa using norm_wordError_le_budget q T U (fun _ => a) (fun _ => b) (fun _ => ε)
    (fun _ => ha) (fun _ => hb) (fun _ => he) hT hU hd w

/-- Main output certificate, with separate readout defect and amplification constant. -/
theorem norm_outputError_uniform (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (a b ε η : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (he : 0 ≤ ε) (hη : 0 ≤ η)
    (hT : ∀ i, ‖T i‖ ≤ a) (hU : ∀ i, ‖U i‖ ≤ b)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (ho : ‖O - V.comp q‖ ≤ η) (w : List I) :
    ‖outputError q T U O V w‖ ≤ η * a ^ w.length + ‖V‖ * (ε * response a b w.length) := by
  simpa using norm_outputError_le q T U O V (fun _ => a) (fun _ => b) (fun _ => ε) η
    (fun _ => ha) (fun _ => hb) (fun _ => he) hη hT hU hd ho w

/-- Nonexpansiveness alone permits linear, not uniformly bounded, accumulation. -/
theorem norm_wordError_nonexpansive (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (ε : ℝ) (he : 0 ≤ ε)
    (hT : ∀ i, ‖T i‖ ≤ 1) (hU : ∀ i, ‖U i‖ ≤ 1)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (w : List I) :
    ‖wordError q T U w‖ ≤ ε * w.length := by
  simpa using norm_wordError_uniform q T U 1 1 ε (by norm_num) (by norm_num) he hT hU hd w

theorem norm_outputError_nonexpansive (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (ε η : ℝ) (he : 0 ≤ ε) (hη : 0 ≤ η)
    (hT : ∀ i, ‖T i‖ ≤ 1) (hU : ∀ i, ‖U i‖ ≤ 1)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (ho : ‖O - V.comp q‖ ≤ η) (w : List I) :
    ‖outputError q T U O V w‖ ≤ η + ‖V‖ * (ε * w.length) := by
  simpa using norm_outputError_uniform q T U O V 1 1 ε η
    (by norm_num) (by norm_num) he hη hT hU hd ho w

/-- A uniform all-word state bound under a contractive reduced model. -/
theorem norm_wordError_contractive (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (b ε : ℝ)
    (hb : 0 ≤ b) (hb1 : b < 1) (he : 0 ≤ ε)
    (hT : ∀ i, ‖T i‖ ≤ 1) (hU : ∀ i, ‖U i‖ ≤ b)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (w : List I) :
    ‖wordError q T U w‖ ≤ ε / (1 - b) := by
  calc
    _ ≤ ε * response 1 b w.length :=
      norm_wordError_uniform q T U 1 b ε (by norm_num) hb he hT hU hd w
    _ ≤ ε * (1 / (1 - b)) :=
      mul_le_mul_of_nonneg_left (response_uniform 1 b (by norm_num) hb (by norm_num) hb1 w.length) he
    _ = ε / (1 - b) := by ring

theorem norm_outputError_contractive (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (b ε η : ℝ) (hb : 0 ≤ b) (hb1 : b < 1) (he : 0 ≤ ε) (hη : 0 ≤ η)
    (hT : ∀ i, ‖T i‖ ≤ 1) (hU : ∀ i, ‖U i‖ ≤ b)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (ho : ‖O - V.comp q‖ ≤ η) (w : List I) :
    ‖outputError q T U O V w‖ ≤ η + ‖V‖ * (ε / (1 - b)) := by
  have h := norm_outputError_uniform q T U O V 1 b ε η
    (by norm_num) hb he hη hT hU hd ho w
  simp only [one_pow, mul_one] at h
  apply h.trans
  apply add_le_add le_rfl
  apply mul_le_mul_of_nonneg_left _ (norm_nonneg V)
  calc
    ε * response 1 b w.length ≤ ε * (1 / (1 - b)) :=
      mul_le_mul_of_nonneg_left (response_uniform 1 b (by norm_num) hb (by norm_num) hb1 w.length) he
    _ = ε / (1 - b) := by ring

/-- Equal-rate estimate has no singular denominator, including rate zero. -/
theorem norm_wordError_same_rate (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (a ε : ℝ) (ha : 0 ≤ a) (he : 0 ≤ ε)
    (hT : ∀ i, ‖T i‖ ≤ a) (hU : ∀ i, ‖U i‖ ≤ a)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (w : List I) (n : ℕ) (hn : w.length = n + 1) :
    ‖wordError q T U w‖ ≤ ε * ((n + 1 : ℕ) * a ^ n) := by
  have h := norm_wordError_uniform q T U a a ε ha ha he hT hU hd w
  rwa [hn, response_same_succ] at h

/-- Different true states represented by the same coarse state remain approximately indistinguishable. -/
theorem same_coarse_future_bound (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (w : List I) (x y : X) (hxy : q x = q y) (E : ℝ)
    (hE : ‖outputError q T U O V w‖ ≤ E) :
    ‖O (word T w x) - O (word T w y)‖ ≤ E * ‖x - y‖ := by
  have heq : O (word T w x) - O (word T w y) = outputError q T U O V w (x - y) := by
    simp [outputError, map_sub, hxy]
  rw [heq]
  exact (ContinuousLinearMap.le_opNorm _ _).trans
    (mul_le_mul_of_nonneg_right hE (norm_nonneg _))

/-- Output discrepancy for an arbitrary, possibly mismatched, reduced initial state. -/
theorem output_initial_decomposition (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (w : List I) (x : X) (z : Z) :
    O (word T w x) - V (word U w z) =
      outputError q T U O V w x + V (word U w (q x - z)) := by
  simp only [outputError, sub_apply, ContinuousLinearMap.comp_apply, map_sub]
  abel

theorem norm_output_initial_le (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (w : List I) (x : X) (z : Z) (E B : ℝ)
    (hE : ‖outputError q T U O V w‖ ≤ E) (hB : ‖word U w‖ ≤ B) :
    ‖O (word T w x) - V (word U w z)‖ ≤
      E * ‖x‖ + ‖V‖ * (B * ‖q x - z‖) := by
  rw [output_initial_decomposition]
  calc
    _ ≤ ‖outputError q T U O V w x‖ + ‖V (word U w (q x - z))‖ := norm_add_le _ _
    _ ≤ E * ‖x‖ + ‖V‖ * (B * ‖q x - z‖) := by
      apply add_le_add
      · exact (ContinuousLinearMap.le_opNorm _ _).trans
          (mul_le_mul_of_nonneg_right hE (norm_nonneg _))
      · apply (ContinuousLinearMap.le_opNorm _ _).trans
        apply mul_le_mul_of_nonneg_left _ (norm_nonneg V)
        exact (ContinuousLinearMap.le_opNorm _ _).trans
          (mul_le_mul_of_nonneg_right hB (norm_nonneg _))

/-- Uniform model error plus exponentially decaying initialization error. -/
theorem norm_output_initial_contractive (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (b ε η : ℝ) (hb : 0 ≤ b) (hb1 : b < 1) (he : 0 ≤ ε) (hη : 0 ≤ η)
    (hT : ∀ i, ‖T i‖ ≤ 1) (hU : ∀ i, ‖U i‖ ≤ b)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε) (ho : ‖O - V.comp q‖ ≤ η)
    (w : List I) (x : X) (z : Z) :
    ‖O (word T w x) - V (word U w z)‖ ≤
      (η + ‖V‖ * (ε / (1 - b))) * ‖x‖ + ‖V‖ * (b ^ w.length * ‖q x - z‖) :=
  norm_output_initial_le q T U O V w x z _ _
    (norm_outputError_contractive q T U O V b ε η hb hb1 he hη hT hU hd ho w)
    (norm_word_uniform U b hb hU w)

end Komorebi.SufficientResolution.StableApproximation
