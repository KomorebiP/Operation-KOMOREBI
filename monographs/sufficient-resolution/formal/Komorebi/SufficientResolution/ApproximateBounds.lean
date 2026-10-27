import Komorebi.SufficientResolution.ApproximateAlgebra
import Mathlib.Analysis.Normed.Operator.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
# Quantitative approximate behavioral sufficiency

Bounds are for entire continuous linear maps, not sampled states. No finite
 dimension, completeness, invertibility or surjectivity of `q` is required.
Per-letter norm/defect bounds may differ, and words retain chronological order.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.ApproximateBounds

universe uK uX uZ uY uI
variable {𝕜 : Type uK} [NontriviallyNormedField 𝕜]
variable {X : Type uX} [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable {Z : Type uZ} [NormedAddCommGroup Z] [NormedSpace 𝕜 Z]
variable {Y : Type uY} [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]
variable {I : Type uI}

/-- Chronological word in continuous linear operators. -/
def word (T : I → X →L[𝕜] X) : List I → X →L[𝕜] X
  | [] => ContinuousLinearMap.id 𝕜 X
  | i :: w => (word T w).comp (T i)

@[simp] theorem word_nil (T : I → X →L[𝕜] X) :
    word T [] = ContinuousLinearMap.id 𝕜 X := rfl

@[simp] theorem word_cons (T : I → X →L[𝕜] X) (i : I) (w : List I) :
    word T (i :: w) = (word T w).comp (T i) := rfl

/-- The analytic operator is the same word as the prior algebraic construction. -/
theorem word_toLinearMap (T : I → X →L[𝕜] X) (w : List I) :
    (word T w).toLinearMap = Behavioral.wordOp (fun i => (T i).toLinearMap) w := by
  induction w with
  | nil => rfl
  | cons i w ih =>
    simp only [word_cons, ContinuousLinearMap.toLinearMap_comp, ih, Behavioral.wordOp_cons]
    rfl

theorem word_append (T : I → X →L[𝕜] X) (u v : List I) :
    word T (u ++ v) = (word T v).comp (word T u) := by
  induction u with
  | nil => ext x; rfl
  | cons i u ih => simp only [List.cons_append, word_cons, ih, ContinuousLinearMap.comp_assoc]

/-- One-step discrepancy. -/
def stepError (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (i : I) : X →L[𝕜] Z :=
  q.comp (T i) - (U i).comp q

/-- Whole-word discrepancy. -/
def wordError (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (w : List I) : X →L[𝕜] Z :=
  q.comp (word T w) - (word U w).comp q

/-- Output error with the coarse state initialized by q. -/
def outputError (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (w : List I) : X →L[𝕜] Y :=
  O.comp (word T w) - V.comp ((word U w).comp q)

@[simp] theorem wordError_nil (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) : wordError q T U [] = 0 := by
  ext x
  simp [wordError]

theorem wordError_toLinearMap (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (w : List I) :
    (wordError q T U w).toLinearMap = ApproximateAlgebra.wordDefect q.toLinearMap
      (fun i => (T i).toLinearMap) (fun i => (U i).toLinearMap) w := by
  simp only [wordError, ApproximateAlgebra.wordDefect,
    ContinuousLinearMap.toLinearMap_sub, ContinuousLinearMap.toLinearMap_comp,
    word_toLinearMap]

theorem wordError_cons (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (i : I) (w : List I) :
    wordError q T U (i :: w) = (wordError q T U w).comp (T i) +
      (word U w).comp (stepError q T U i) := by
  ext x
  simp only [wordError, stepError, word_cons, sub_apply,
    add_apply, ContinuousLinearMap.comp_apply, map_sub]
  abel

theorem wordError_append (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (u v : List I) :
    wordError q T U (u ++ v) = (wordError q T U v).comp (word T u) +
      (word U v).comp (wordError q T U u) := by
  ext x
  simp only [wordError, word_append, sub_apply,
    add_apply, ContinuousLinearMap.comp_apply, map_sub]
  abel

theorem outputError_decomposition (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y) (w : List I) :
    outputError q T U O V w = (O - V.comp q).comp (word T w) +
      V.comp (wordError q T U w) := by
  ext x
  simp only [outputError, wordError, sub_apply,
    add_apply, ContinuousLinearMap.comp_apply, map_sub]
  abel

/-- Product majorant in chronological order (real scalars commute). -/
def gain (a : I → ℝ) : List I → ℝ
  | [] => 1
  | i :: w => gain a w * a i

/-- Transport-aware accumulation of per-letter modeling defects. -/
def budget (a b ε : I → ℝ) : List I → ℝ
  | [] => 0
  | i :: w => budget a b ε w * a i + gain b w * ε i

theorem gain_nonneg (a : I → ℝ) (ha : ∀ i, 0 ≤ a i) (w : List I) :
    0 ≤ gain a w := by
  induction w with
  | nil => norm_num [gain]
  | cons i w ih => exact mul_nonneg ih (ha i)

theorem gain_append (a : I → ℝ) (u v : List I) :
    gain a (u ++ v) = gain a v * gain a u := by
  induction u with
  | nil => simp [gain]
  | cons i u ih => simp only [List.cons_append, gain, ih]; ring

theorem budget_nonneg (a b ε : I → ℝ)
    (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i) (he : ∀ i, 0 ≤ ε i) (w : List I) :
    0 ≤ budget a b ε w := by
  induction w with
  | nil => rfl
  | cons i w ih => exact add_nonneg (mul_nonneg ih (ha i)) (mul_nonneg (gain_nonneg b hb w) (he i))

/-- The scalar budget obeys exactly the same two-sided concatenation law. -/
theorem budget_append (a b ε : I → ℝ) (u v : List I) :
    budget a b ε (u ++ v) = budget a b ε v * gain a u +
      gain b v * budget a b ε u := by
  induction u with
  | nil => simp [budget, gain]
  | cons i u ih =>
    simp only [List.cons_append, budget, gain, ih, gain_append]
    ring

theorem norm_word_le_gain (T : I → X →L[𝕜] X) (a : I → ℝ)
    (ha : ∀ i, 0 ≤ a i) (hT : ∀ i, ‖T i‖ ≤ a i) (w : List I) :
    ‖word T w‖ ≤ gain a w := by
  induction w with
  | nil => exact ContinuousLinearMap.norm_id_le
  | cons i w ih =>
    exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
      (mul_le_mul ih (hT i) (norm_nonneg _) (gain_nonneg a ha w))

/-- Main heterogeneous all-word estimate. -/
theorem norm_wordError_le_budget (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (a b ε : I → ℝ)
    (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i) (he : ∀ i, 0 ≤ ε i)
    (hT : ∀ i, ‖T i‖ ≤ a i) (hU : ∀ i, ‖U i‖ ≤ b i)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε i) (w : List I) :
    ‖wordError q T U w‖ ≤ budget a b ε w := by
  induction w with
  | nil => simp [budget]
  | cons i w ih =>
    rw [wordError_cons]
    calc
      _ ≤ ‖(wordError q T U w).comp (T i)‖ +
          ‖(word U w).comp (stepError q T U i)‖ := norm_add_le _ _
      _ ≤ ‖wordError q T U w‖ * ‖T i‖ + ‖word U w‖ * ‖stepError q T U i‖ :=
        add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _)
      _ ≤ budget a b ε w * a i + gain b w * ε i :=
        add_le_add
          (mul_le_mul ih (hT i) (norm_nonneg _) (budget_nonneg a b ε ha hb he w))
          (mul_le_mul (norm_word_le_gain U b hb hU w) (hd i)
            (norm_nonneg _) (gain_nonneg b hb w))
      _ = budget a b ε (i :: w) := rfl

/-- Output error includes a separately declared observation defect. -/
theorem norm_outputError_le (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (O : X →L[𝕜] Y) (V : Z →L[𝕜] Y)
    (a b ε : I → ℝ) (η : ℝ)
    (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i) (he : ∀ i, 0 ≤ ε i) (hη : 0 ≤ η)
    (hT : ∀ i, ‖T i‖ ≤ a i) (hU : ∀ i, ‖U i‖ ≤ b i)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε i) (ho : ‖O - V.comp q‖ ≤ η) (w : List I) :
    ‖outputError q T U O V w‖ ≤ η * gain a w + ‖V‖ * budget a b ε w := by
  rw [outputError_decomposition]
  calc
    _ ≤ ‖(O - V.comp q).comp (word T w)‖ + ‖V.comp (wordError q T U w)‖ := norm_add_le _ _
    _ ≤ ‖O - V.comp q‖ * ‖word T w‖ + ‖V‖ * ‖wordError q T U w‖ :=
      add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _)
    _ ≤ η * gain a w + ‖V‖ * budget a b ε w :=
      add_le_add (mul_le_mul ho (norm_word_le_gain T a ha hT w) (norm_nonneg _) hη)
        (mul_le_mul_of_nonneg_left (norm_wordError_le_budget q T U a b ε ha hb he hT hU hd w)
          (norm_nonneg _))

/-- An imperfect coarse initial state contributes an additional propagated error. -/
theorem state_error_decomposition (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (w : List I) (x : X) (z : Z) :
    q (word T w x) - word U w z = wordError q T U w x + word U w (q x - z) := by
  simp only [wordError, sub_apply, ContinuousLinearMap.comp_apply, map_sub]
  abel

theorem norm_state_error_le (q : X →L[𝕜] Z) (T : I → X →L[𝕜] X)
    (U : I → Z →L[𝕜] Z) (a b ε : I → ℝ)
    (ha : ∀ i, 0 ≤ a i) (hb : ∀ i, 0 ≤ b i) (he : ∀ i, 0 ≤ ε i)
    (hT : ∀ i, ‖T i‖ ≤ a i) (hU : ∀ i, ‖U i‖ ≤ b i)
    (hd : ∀ i, ‖stepError q T U i‖ ≤ ε i) (w : List I) (x : X) (z : Z) :
    ‖q (word T w x) - word U w z‖ ≤
      budget a b ε w * ‖x‖ + gain b w * ‖q x - z‖ := by
  rw [state_error_decomposition]
  calc
    _ ≤ ‖wordError q T U w x‖ + ‖word U w (q x - z)‖ := norm_add_le _ _
    _ ≤ ‖wordError q T U w‖ * ‖x‖ + ‖word U w‖ * ‖q x - z‖ :=
      add_le_add (ContinuousLinearMap.le_opNorm _ _) (ContinuousLinearMap.le_opNorm _ _)
    _ ≤ _ := add_le_add
      (mul_le_mul_of_nonneg_right (norm_wordError_le_budget q T U a b ε ha hb he hT hU hd w)
        (norm_nonneg _))
      (mul_le_mul_of_nonneg_right (norm_word_le_gain U b hb hU w) (norm_nonneg _))

end Komorebi.SufficientResolution.ApproximateBounds
