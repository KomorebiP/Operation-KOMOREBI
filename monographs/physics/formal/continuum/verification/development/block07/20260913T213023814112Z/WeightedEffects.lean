module

public import KomorebiPhysics.EffectRefinement

/-! Added strengthening: column-stochastic classical postprocessing of a
positive effect atlas. These hypotheses replace binary incidence explicitly;
arbitrary overlapping or signed aggregation is not declared physical. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators Matrix

section Pair
variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]

theorem effectExchange_real_smul (A : H →L[ℂ] H) (x y : H) (r s : ℝ) :
    effectExchange A ((r : ℂ) • x) ((s : ℂ) • y) = r * s * effectExchange A x y := by
  simp only [effectExchange, map_smul, inner_smul_left, inner_smul_right]
  simp [Complex.mul_re, Complex.mul_im]
  ring

end Pair
namespace EffectAtlas
variable {H I J : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
  [Fintype I] [Fintype J]

/-- Positive column-normalized weights define genuine coarse effects. -/
def postprocess (F : EffectAtlas H I) (R : J → I → ℝ)
    (hR : ∀ a i, 0 ≤ R a i) (hcol : ∀ i, ∑ a, R a i = 1) : EffectAtlas H J where
  effect a := ∑ i, (R a i : ℂ) • F.effect i
  sum_effect := by
    rw [Finset.sum_comm]
    simp only [← Finset.sum_smul, ← Complex.ofReal_sum, hcol, Complex.ofReal_one, one_smul]
    exact F.sum_effect
  selfAdjoint := by
    intro a x y
    simp only [sum_apply, sum_inner, inner_sum, smul_apply]
    apply Finset.sum_congr rfl
    intro i _
    rw [inner_smul_left, inner_smul_right, F.selfAdjoint]
    simp
  nonnegative := by
    intro a x
    simp only [sum_apply, inner_sum, Complex.re_sum, smul_apply, inner_smul_right]
    apply Finset.sum_nonneg
    intro i _
    simpa [Complex.mul_re] using mul_nonneg (hR a i) (F.nonnegative i x)

theorem postprocess_probability (F : EffectAtlas H I) (R : J → I → ℝ)
    (hR : ∀ a i, 0 ≤ R a i) (hcol : ∀ i, ∑ a, R a i = 1) (ψ : H) (a : J) :
    (F.postprocess R hR hcol).probability ψ a = ∑ i, R a i * F.probability ψ i := by
  simp only [probability, effectExpectation, postprocess, sum_apply, smul_apply, inner_sum,
    Complex.re_sum, inner_smul_right, Complex.mul_re, Complex.ofReal_re,
    Complex.ofReal_im, zero_mul, sub_zero]

theorem postprocess_current (F : EffectAtlas H I) (R : J → I → ℝ)
    (hR : ∀ a i, 0 ≤ R a i) (hcol : ∀ i, ∑ a, R a i = 1)
    (A : H →L[ℂ] H) (ψ : H) (a b : J) :
    (F.postprocess R hR hcol).current A ψ a b =
      ∑ i, ∑ j, R a i * R b j * F.current A ψ i j := by
  simp only [current, postprocess, sum_apply, smul_apply,
    effectExchange_sum_left, effectExchange_sum_right, effectExchange_real_smul]
  rw [Finset.sum_comm]

/-- The source's R J R^T formula extends to genuine stochastic weights. -/
theorem postprocess_current_matrix (F : EffectAtlas H I) (R : Matrix J I ℝ)
    (hR : ∀ a i, 0 ≤ R a i) (hcol : ∀ i, ∑ a, R a i = 1)
    (A : H →L[ℂ] H) (ψ : H) :
    Matrix.of ((F.postprocess R hR hcol).current A ψ) =
      RefinementTower.aggregateCurrent R (Matrix.of (F.current A ψ)) := by
  ext a b
  change (F.postprocess R hR hcol).current A ψ a b = _
  have hp := postprocess_current F (fun a i => R a i) hR hcol A ψ a b
  calc
    _ = ∑ i, ∑ j, R a i * R b j * F.current A ψ i j := hp
    _ = _ := by
      simp only [RefinementTower.aggregateCurrent, Matrix.mul_apply, Matrix.transpose_apply,
        Matrix.of_apply, Finset.sum_mul]
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro i _
      apply Finset.sum_congr rfl
      intro j _
      ring

/-- Actual velocity of a fixed postprocessing of a moving effect atlas. -/
def postprocessVelocity (R : J → I → ℝ) (D : I → H →L[ℂ] H) (a : J) : H →L[ℂ] H :=
  ∑ i, (R a i : ℂ) • D i

theorem hasDerivAt_postprocess_effect (F : ℝ → EffectAtlas H I) (D : I → H →L[ℂ] H)
    (R : J → I → ℝ) (hR : ∀ a i, 0 ≤ R a i) (hcol : ∀ i, ∑ a, R a i = 1)
    (t : ℝ) (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t) (a : J) :
    HasDerivAt (fun s => ((F s).postprocess R hR hcol).effect a)
      (postprocessVelocity R D a) t :=
  HasDerivAt.fun_sum (u := Finset.univ) (fun i _ => (hF i).const_smul (R a i : ℂ))

omit [Fintype J] in
theorem postprocess_source (R : J → I → ℝ) (D : I → H →L[ℂ] H) (ψ : H) (a : J) :
    source (postprocessVelocity R D) ψ a = ∑ i, R a i * source D ψ i := by
  simp only [source, effectExpectation, postprocessVelocity, sum_apply, smul_apply, inner_sum,
    Complex.re_sum, inner_smul_right, Complex.mul_re, Complex.ofReal_re,
    Complex.ofReal_im, zero_mul, sub_zero]

/-- Original vector and operator derivatives imply stochastic coarse continuity. -/
theorem hasDerivAt_postprocess_probability (F : ℝ → EffectAtlas H I)
    (D : I → H →L[ℂ] H) (R : J → I → ℝ)
    (hR : ∀ a i, 0 ≤ R a i) (hcol : ∀ i, ∑ a, R a i = 1)
    (A : H →L[ℂ] H) (hA : IsSkew A) {ψ : ℝ → H} {t : ℝ}
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t)
    (hψ : HasDerivAt ψ (A (ψ t)) t) (a : J) :
    HasDerivAt (fun s => ((F s).postprocess R hR hcol).probability (ψ s) a)
      ((∑ i, R a i * source D (ψ t) i) +
       ∑ b, ∑ i, ∑ j, R a i * R b j * (F t).current A (ψ t) i j) t := by
  have h := hasDerivAt_moving_probability (fun s => (F s).postprocess R hR hcol)
    (postprocessVelocity R D) A hA
    (hasDerivAt_postprocess_effect F D R hR hcol t hF) hψ a
  simpa only [postprocess_source, postprocess_current] using h

omit [Fintype I] in
/-- Column-normalized nonnegative postprocessings compose without losing positivity. -/
theorem postprocess_weights_comp {K : Type*} [Fintype K]
    (R : Matrix J I ℝ) (S : Matrix K J ℝ)
    (hR : ∀ a i, 0 ≤ R a i) (hS : ∀ c a, 0 ≤ S c a)
    (hr : ∀ i, ∑ a, R a i = 1) (hs : ∀ a, ∑ c, S c a = 1) :
    (∀ c i, 0 ≤ (S * R) c i) ∧ ∀ i, ∑ c, (S * R) c i = 1 := by
  constructor
  · intro c i
    exact Finset.sum_nonneg (fun a _ => mul_nonneg (hS c a) (hR a i))
  · intro i
    simp only [Matrix.mul_apply]
    rw [Finset.sum_comm]
    simp only [← Finset.sum_mul, hs, one_mul, hr]

/-- The actual sequentially postprocessed operators equal the composed weights. -/
theorem postprocess_comp_effect {K : Type*} [Fintype K]
    (F : EffectAtlas H I) (R : Matrix J I ℝ) (S : Matrix K J ℝ)
    (hR : ∀ a i, 0 ≤ R a i) (hS : ∀ c a, 0 ≤ S c a)
    (hr : ∀ i, ∑ a, R a i = 1) (hs : ∀ a, ∑ c, S c a = 1) (c : K) :
    ((F.postprocess R hR hr).postprocess S hS hs).effect c =
      (F.postprocess (S * R) (postprocess_weights_comp R S hR hS hr hs).1
        (postprocess_weights_comp R S hR hS hr hs).2).effect c := by
  simp only [postprocess, Finset.smul_sum, smul_smul, Matrix.mul_apply,
    Complex.ofReal_sum, Complex.ofReal_mul, Finset.sum_smul]
  rw [Finset.sum_comm]

end EffectAtlas
end KomorebiPhysics
