import Komorebi.SufficientResolution.StableApproximation

/-!
# Multilevel error transport and coordinate conditioning

Successive approximate models retain both stages' defects. A split coordinate
embedding changes operator bounds but not represented outputs on embedded states.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.ApproximateComposition

open ApproximateBounds

universe uK uX uZ uW uY uI
variable {𝕜 : Type uK} [NontriviallyNormedField 𝕜]
variable {X : Type uX} [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable {Z : Type uZ} [NormedAddCommGroup Z] [NormedSpace 𝕜 Z]
variable {W : Type uW} [NormedAddCommGroup W] [NormedSpace 𝕜 W]
variable {Y : Type uY} [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]
variable {I : Type uI}

theorem wordError_two_stage (q : X →L[𝕜] Z) (p : Z →L[𝕜] W)
    (T : I → X →L[𝕜] X) (U : I → Z →L[𝕜] Z) (S : I → W →L[𝕜] W) (w : List I) :
    wordError (p.comp q) T S w =
      p.comp (wordError q T U w) + (wordError p U S w).comp q := by
  ext x
  simp only [wordError, sub_apply, add_apply, ContinuousLinearMap.comp_apply, map_sub]
  abel

theorem stepError_two_stage (q : X →L[𝕜] Z) (p : Z →L[𝕜] W)
    (T : I → X →L[𝕜] X) (U : I → Z →L[𝕜] Z) (S : I → W →L[𝕜] W) (i : I) :
    stepError (p.comp q) T S i =
      p.comp (stepError q T U i) + (stepError p U S i).comp q := by
  ext x
  simp only [stepError, sub_apply, add_apply, ContinuousLinearMap.comp_apply, map_sub]
  abel

theorem norm_wordError_two_stage (q : X →L[𝕜] Z) (p : Z →L[𝕜] W)
    (T : I → X →L[𝕜] X) (U : I → Z →L[𝕜] Z) (S : I → W →L[𝕜] W)
    (w : List I) (ε₁ ε₂ : ℝ)
    (h₁ : ‖wordError q T U w‖ ≤ ε₁) (h₂ : ‖wordError p U S w‖ ≤ ε₂) :
    ‖wordError (p.comp q) T S w‖ ≤ ‖p‖ * ε₁ + ε₂ * ‖q‖ := by
  rw [wordError_two_stage q p T U S]
  exact (norm_add_le _ _).trans ((add_le_add (ContinuousLinearMap.opNorm_comp_le _ _)
    (ContinuousLinearMap.opNorm_comp_le _ _)).trans
      (add_le_add (mul_le_mul_of_nonneg_left h₁ (norm_nonneg _))
        (mul_le_mul_of_nonneg_right h₂ (norm_nonneg _))))

theorem norm_stepError_two_stage (q : X →L[𝕜] Z) (p : Z →L[𝕜] W)
    (T : I → X →L[𝕜] X) (U : I → Z →L[𝕜] Z) (S : I → W →L[𝕜] W)
    (i : I) (ε₁ ε₂ : ℝ)
    (h₁ : ‖stepError q T U i‖ ≤ ε₁) (h₂ : ‖stepError p U S i‖ ≤ ε₂) :
    ‖stepError (p.comp q) T S i‖ ≤ ‖p‖ * ε₁ + ε₂ * ‖q‖ := by
  rw [stepError_two_stage q p T U S]
  exact (norm_add_le _ _).trans ((add_le_add (ContinuousLinearMap.opNorm_comp_le _ _)
    (ContinuousLinearMap.opNorm_comp_le _ _)).trans
      (add_le_add (mul_le_mul_of_nonneg_left h₁ (norm_nonneg _))
        (mul_le_mul_of_nonneg_right h₂ (norm_nonneg _))))

theorem readout_two_stage (q : X →L[𝕜] Z) (p : Z →L[𝕜] W)
    (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y) (H : W →L[𝕜] Y) :
    O - H.comp (p.comp q) = (O - V.comp q) + (V - H.comp p).comp q := by
  ext x
  simp only [sub_apply, add_apply, ContinuousLinearMap.comp_apply]
  abel

theorem norm_readout_two_stage (q : X →L[𝕜] Z) (p : Z →L[𝕜] W)
    (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y) (H : W →L[𝕜] Y)
    (η₁ η₂ : ℝ) (h₁ : ‖O - V.comp q‖ ≤ η₁) (h₂ : ‖V - H.comp p‖ ≤ η₂) :
    ‖O - H.comp (p.comp q)‖ ≤ η₁ + η₂ * ‖q‖ := by
  rw [readout_two_stage q p O V H]
  exact (norm_add_le _ _).trans (add_le_add h₁
    ((ContinuousLinearMap.opNorm_comp_le _ _).trans
      (mul_le_mul_of_nonneg_right h₂ (norm_nonneg _))))

/-- Re-encode a model with a continuous split coordinate embedding. -/
def reencode (S : Z →L[𝕜] W) (J : W →L[𝕜] Z) (U : I → Z →L[𝕜] Z) :
    I → W →L[𝕜] W := fun i => S.comp ((U i).comp J)

/-- Only J S = id is needed on the embedded state; no hidden surjectivity is assumed. -/
theorem reencode_word (S : Z →L[𝕜] W) (J : W →L[𝕜] Z)
    (hJS : J.comp S = ContinuousLinearMap.id 𝕜 Z)
    (U : I → Z →L[𝕜] Z) (w : List I) :
    (word (reencode S J U) w).comp S = S.comp (word U w) := by
  have hs (z : Z) : J (S z) = z := congrArg (fun f : Z →L[𝕜] Z => f z) hJS
  induction w with
  | nil => ext z; rfl
  | cons i w ih =>
    ext z
    have hh (z' : Z) := congrArg (fun f : Z →L[𝕜] W => f z') ih
    simp only [word_cons, reencode, ContinuousLinearMap.comp_apply, hs]
    exact hh (U i z)

theorem reencode_wordError (q : X →L[𝕜] Z) (S : Z →L[𝕜] W) (J : W →L[𝕜] Z)
    (hJS : J.comp S = ContinuousLinearMap.id 𝕜 Z)
    (T : I → X →L[𝕜] X) (U : I → Z →L[𝕜] Z) (w : List I) :
    wordError (S.comp q) T (reencode S J U) w = S.comp (wordError q T U w) := by
  have h := reencode_word S J hJS U w
  ext x
  have hx := congrArg (fun f : Z →L[𝕜] W => f (q x)) h
  simp only [ContinuousLinearMap.comp_apply] at hx
  simp only [wordError, sub_apply, ContinuousLinearMap.comp_apply, map_sub, hx]

theorem norm_reencode_wordError (q : X →L[𝕜] Z) (S : Z →L[𝕜] W) (J : W →L[𝕜] Z)
    (hJS : J.comp S = ContinuousLinearMap.id 𝕜 Z)
    (T : I → X →L[𝕜] X) (U : I → Z →L[𝕜] Z) (w : List I) :
    ‖wordError (S.comp q) T (reencode S J U) w‖ ≤ ‖S‖ * ‖wordError q T U w‖ := by
  rw [reencode_wordError q S J hJS T U w]
  exact ContinuousLinearMap.opNorm_comp_le _ _

/-- Re-encoding changes norm constants through both analysis and synthesis. -/
theorem norm_reencode (S : Z →L[𝕜] W) (J : W →L[𝕜] Z)
    (U : I → Z →L[𝕜] Z) (i : I) :
    ‖reencode S J U i‖ ≤ ‖S‖ * (‖U i‖ * ‖J‖) := by
  exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
    (mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _))

/-- The represented physical output is unchanged, despite changed norm certificates. -/
theorem reencode_outputError (q : X →L[𝕜] Z) (S : Z →L[𝕜] W) (J : W →L[𝕜] Z)
    (hJS : J.comp S = ContinuousLinearMap.id 𝕜 Z)
    (T : I → X →L[𝕜] X) (U : I → Z →L[𝕜] Z)
    (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y) (w : List I) :
    outputError (S.comp q) T (reencode S J U) O (V.comp J) w =
      outputError q T U O V w := by
  have hw := reencode_word S J hJS U w
  have hs (z : Z) : J (S z) = z := congrArg (fun f : Z →L[𝕜] Z => f z) hJS
  ext x
  have hx := congrArg (fun f : Z →L[𝕜] W => f (q x)) hw
  simp only [ContinuousLinearMap.comp_apply] at hx
  simp only [outputError, sub_apply, ContinuousLinearMap.comp_apply, hx, hs]

end Komorebi.SufficientResolution.ApproximateComposition
