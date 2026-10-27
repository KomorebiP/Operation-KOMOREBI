module

public import KomorebiPhysics.WeightedEffects
public import KomorebiPhysics.Examples
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Deriv
public import Mathlib.Tactic.FinCases

/-! Exact positive, overlapping, nonprojector witnesses. The moving scalar
atlas is positive for every real time. The affine vector-flow example is
only a local derivative witness at zero. All arithmetic is kernel checked. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.EffectExamples
open scoped BigOperators
open Examples

/-- A nonbinary column-stochastic smearing of a sharp two-sector atlas. -/
def softWeights (a i : Fin 2) : ℝ := if a = i then 3/4 else 1/4

theorem softWeights_nonnegative (a i : Fin 2) : 0 ≤ softWeights a i := by
  unfold softWeights
  split_ifs <;> norm_num

theorem softWeights_columns (i : Fin 2) : (∑ a, softWeights a i) = 1 := by
  fin_cases i <;> norm_num [softWeights, Fin.sum_univ_two]

def softAtlas : EffectAtlas (EuclideanSpace ℂ (Fin 2)) (Fin 2) :=
  (EffectAtlas.ofAtlas (coordinateAtlas (Fin 2))).postprocess softWeights
    softWeights_nonnegative softWeights_columns

theorem soft_effect_apply (i k : Fin 2) (v : EuclideanSpace ℂ (Fin 2)) :
    softAtlas.effect i v k = (if i = k then (3/4 : ℂ) else 1/4) * v k := by
  fin_cases i <;> fin_cases k <;>
    simp [softAtlas, EffectAtlas.postprocess, EffectAtlas.ofAtlas,
      coordinateAtlas, softWeights, Fin.sum_univ_two, coordinateMap_apply]

/-- A rational, exactly normalized state with both coordinates populated. -/
def softState : EuclideanSpace ℂ (Fin 2) :=
  (3/5 : ℂ) • PiLp.single 2 0 1 + (4/5 : ℂ) • PiLp.single 2 1 1

theorem softState_normalized : ‖softState‖ = 1 := by
  have h : ‖softState‖ ^ 2 = 1 := by
    calc
      _ = (inner ℂ softState softState).re := (inner_self_eq_norm_sq (𝕜 := ℂ) _).symm
      _ = 1 := by
        rw [EuclideanSpace.inner_eq_star_dotProduct]
        norm_num [softState, dotProduct, Fin.sum_univ_two, PiLp.single_apply]
  nlinarith [norm_nonneg softState]

theorem soft_probabilities :
    softAtlas.probability softState 0 = 43/100 ∧
    softAtlas.probability softState 1 = 57/100 := by
  constructor <;>
    norm_num [EffectAtlas.probability, effectExpectation,
      EuclideanSpace.inner_eq_star_dotProduct, dotProduct, Fin.sum_univ_two,
      soft_effect_apply, softState, PiLp.single_apply]

theorem soft_squared_effect_norm : ‖softAtlas.effect 0 softState‖ ^ 2 = 97/400 := by
  calc
    _ = (inner ℂ (softAtlas.effect 0 softState) (softAtlas.effect 0 softState)).re :=
      (inner_self_eq_norm_sq (𝕜 := ℂ) _).symm
    _ = _ := by
      rw [EuclideanSpace.inner_eq_star_dotProduct]
      norm_num [dotProduct, Fin.sum_univ_two, soft_effect_apply, softState, PiLp.single_apply, map_ofNat]

/-- Born probabilities cannot be replaced by squared effected-vector norms. -/
theorem soft_probability_not_squared_norm :
    softAtlas.probability softState 0 ≠ ‖softAtlas.effect 0 softState‖ ^ 2 := by
  rw [soft_probabilities.1, soft_squared_effect_norm]
  norm_num

/-- The positive effect really fails idempotence. -/
theorem soft_not_idempotent : softAtlas.effect 0 * softAtlas.effect 0 ≠ softAtlas.effect 0 := by
  intro h
  have he := congrArg (fun T : EuclideanSpace ℂ (Fin 2) →L[ℂ] EuclideanSpace ℂ (Fin 2) =>
    T softState 0) h
  norm_num [mul_apply_eq_comp, soft_effect_apply, softState, PiLp.single_apply] at he

/-- Nonzero operator overlap, calculated exactly. -/
theorem soft_overlap : softAtlas.effect 0 * softAtlas.effect 1 =
    (3/16 : ℂ) • (1 : EuclideanSpace ℂ (Fin 2) →L[ℂ] EuclideanSpace ℂ (Fin 2)) := by
  ext v k
  fin_cases k <;> simp [mul_apply_eq_comp, soft_effect_apply] <;> ring

theorem soft_not_orthogonal : softAtlas.effect 0 * softAtlas.effect 1 ≠ 0 := by
  intro h
  have he := congrArg (fun T : EuclideanSpace ℂ (Fin 2) →L[ℂ] EuclideanSpace ℂ (Fin 2) =>
    T softState 0) h
  norm_num [mul_apply_eq_comp, soft_effect_apply, softState, PiLp.single_apply] at he

theorem soft_current_nonzero :
    softAtlas.current rotation2 softState 0 1 = -12/25 ∧
    softAtlas.current rotation2 softState 1 0 = 12/25 := by
  constructor <;>
    norm_num [EffectAtlas.current, effectExchange, rotation2,
      EuclideanSpace.inner_eq_star_dotProduct, dotProduct, Fin.sum_univ_two,
      soft_effect_apply, softState, PiLp.single_apply, map_ofNat]

/-- A local flow witness, not asserted to solve the ODE away from zero. -/
def softCurve (t : ℝ) : EuclideanSpace ℂ (Fin 2) := softState + t • rotation2 softState

theorem softCurve_zero : softCurve 0 = softState := by simp [softCurve]

theorem softCurve_hasDerivAt : HasDerivAt softCurve (rotation2 (softCurve 0)) 0 := by
  have h := ((hasDerivAt_id (0 : ℝ)).smul_const (rotation2 softState)).const_add softState
  change HasDerivAt (fun t : ℝ => softState + t • rotation2 softState)
    (1 • rotation2 softState) 0 at h
  unfold softCurve
  simpa only [zero_smul, add_zero, one_smul] using h

/-- Apply the general vector-flow theorem to this nonprojector atlas. -/
theorem soft_probability_hasDerivAt :
    HasDerivAt (fun t => softAtlas.probability (softCurve t) 0) (-12/25) 0 := by
  have h := softAtlas.hasDerivAt_probability rotation2 rotation2_skew softCurve_hasDerivAt 0
  simpa only [softCurve_zero, Fin.sum_univ_two, softAtlas.current_diagonal,
    soft_current_nonzero.1, zero_add] using h

/-- Positive scalar resolutions provide all-time moving nonprojector examples. -/
def scalarAtlas {I : Type*} [Fintype I] (w : I → ℝ)
    (hw : ∀ i, 0 ≤ w i) (hsum : ∑ i, w i = 1) : EffectAtlas ℂ I where
  effect i := (w i : ℂ) • (1 : ℂ →L[ℂ] ℂ)
  sum_effect := by
    rw [← Finset.sum_smul, ← Complex.ofReal_sum, hsum]
    simp
  selfAdjoint := by
    intro i x y
    simp only [smul_apply, one_apply_eq_self, inner_smul_left, inner_smul_right]
    simp
  nonnegative := by
    intro i x
    simp only [smul_apply, one_apply_eq_self, inner_smul_right, Complex.mul_re,
      Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero]
    exact mul_nonneg (hw i) (inner_self_nonneg (𝕜 := ℂ))

theorem scalarAtlas_probability {I : Type*} [Fintype I] (w : I → ℝ)
    (hw : ∀ i, 0 ≤ w i) (hsum : ∑ i, w i = 1) (i : I) :
    (scalarAtlas w hw hsum).probability 1 i = w i := by
  norm_num [EffectAtlas.probability, effectExpectation, scalarAtlas]

def oscillatingWeight (t : ℝ) (i : Fin 2) : ℝ :=
  if i = 0 then (1 + Real.sin t)/2 else (1 - Real.sin t)/2

theorem oscillatingWeight_nonneg (t : ℝ) (i : Fin 2) : 0 ≤ oscillatingWeight t i := by
  unfold oscillatingWeight
  split_ifs
  · linarith [Real.neg_one_le_sin t]
  · linarith [Real.sin_le_one t]

theorem oscillatingWeight_sum (t : ℝ) : (∑ i, oscillatingWeight t i) = 1 := by
  simp only [Fin.sum_univ_two, oscillatingWeight]
  norm_num
  ring

def oscillatingAtlas (t : ℝ) : EffectAtlas ℂ (Fin 2) :=
  scalarAtlas (oscillatingWeight t) (oscillatingWeight_nonneg t) (oscillatingWeight_sum t)

def oscillatingVelocity (i : Fin 2) : ℂ →L[ℂ] ℂ :=
  (if i = 0 then (1/2 : ℂ) else -1/2) • (1 : ℂ →L[ℂ] ℂ)

theorem oscillatingWeight_derivative (i : Fin 2) :
    HasDerivAt (fun t => oscillatingWeight t i) (if i = 0 then (1/2 : ℝ) else -1/2) 0 := by
  fin_cases i
  · simpa [oscillatingWeight] using
      ((hasDerivAt_const (0 : ℝ) 1).add (Real.hasDerivAt_sin 0)).div_const 2
  · simpa [oscillatingWeight] using
      ((hasDerivAt_const (0 : ℝ) 1).sub (Real.hasDerivAt_sin 0)).div_const 2

/-- The velocity is derived from the differentiable effect operators themselves. -/
theorem oscillatingAtlas_derivative (i : Fin 2) :
    HasDerivAt (fun t => (oscillatingAtlas t).effect i) (oscillatingVelocity i) 0 := by
  have h := Complex.ofRealCLM.hasFDerivAt.comp_hasDerivAt 0 (oscillatingWeight_derivative i)
  have hs := h.smul_const (1 : ℂ →L[ℂ] ℂ)
  have he : Complex.ofRealCLM (if i = 0 then (1/2 : ℝ) else -1/2) =
      (if i = 0 then (1/2 : ℂ) else -1/2) := by
    by_cases hi : i = 0 <;> simp [hi]
  rw [he] at hs
  exact hs

theorem oscillating_sources :
    EffectAtlas.source oscillatingVelocity 1 0 = 1/2 ∧
    EffectAtlas.source oscillatingVelocity 1 1 = -1/2 := by
  constructor <;> norm_num [EffectAtlas.source, effectExpectation, oscillatingVelocity]

theorem zero_generator_skew : IsSkew (0 : ℂ →L[ℂ] ℂ) := by
  intro x y
  simp

/-- A fixed state has nonzero probability velocity purely from moving effects. -/
theorem oscillating_probability_hasDerivAt :
    HasDerivAt (fun t => (oscillatingAtlas t).probability 1 0) (1/2) 0 := by
  have h := EffectAtlas.hasDerivAt_moving_probability oscillatingAtlas oscillatingVelocity
    (0 : ℂ →L[ℂ] ℂ) zero_generator_skew
    oscillatingAtlas_derivative (ψ := fun _ => (1 : ℂ)) (hasDerivAt_const 0 1) 0
  simpa only [oscillating_sources.1, EffectAtlas.current, effectExchange,
    zero_apply, inner_zero_right, Complex.zero_re, sub_self, Finset.sum_const_zero, add_zero] using h

theorem oscillating_derivative_not_zero :
    ¬ HasDerivAt (fun t => (oscillatingAtlas t).probability 1 0) 0 0 := by
  intro h
  have he := oscillating_probability_hasDerivAt.unique h
  norm_num at he

/-- The effect current remains antisymmetric without skewness, but no longer
represents the state's probability derivative. -/
theorem identity_effect_current_zero (i j : Fin 2) :
    (oscillatingAtlas 0).current (1 : ℂ →L[ℂ] ℂ) 1 i j = 0 := by
  fin_cases i <;> fin_cases j <;>
    norm_num [EffectAtlas.current, effectExchange, oscillatingAtlas, scalarAtlas, oscillatingWeight]

theorem identity_probability_derivative :
    HasDerivAt (fun t : ℝ => (oscillatingAtlas 0).probability (1 + (t : ℂ)) 0) 1 0 := by
  have hp : HasDerivAt (fun t : ℝ => (1 : ℂ) + (t : ℂ)) 1 0 := by
    have hc := Complex.ofRealCLM.hasFDerivAt.comp_hasDerivAt 0 (hasDerivAt_id (0 : ℝ))
    have hh := hc.const_add (1 : ℂ)
    simpa only [Complex.ofRealCLM_apply, Complex.ofReal_one, Function.comp_def, id_eq] using hh
  have h := hasDerivAt_effectExpectation (fun _ => (oscillatingAtlas 0).effect 0)
    (fun t : ℝ => (1 : ℂ) + (t : ℂ)) 0 1 0 (hasDerivAt_const 0 _) hp
    ((oscillatingAtlas 0).selfAdjoint 0)
  simpa [EffectAtlas.probability, effectExpectation, oscillatingAtlas, scalarAtlas,
    oscillatingWeight] using h

/-- Duplicating the identity is positive but not a normalized effect atlas. -/
theorem duplicated_identity_not_complete :
    (∑ _i : Fin 2, (1 : ℂ →L[ℂ] ℂ)) ≠ 1 := by
  intro h
  have he := congrArg (fun T : ℂ →L[ℂ] ℂ => T 1) h
  norm_num [Fin.sum_univ_two] at he

/-- Column normalization alone does not repair signed negative effects. -/
theorem signed_effect_negative :
    effectExpectation ((-1 : ℂ) • (1 : ℂ →L[ℂ] ℂ)) 1 = -1 := by
  norm_num [effectExpectation]

end KomorebiPhysics.EffectExamples
