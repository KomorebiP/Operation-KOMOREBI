module

public import KomorebiPhysics.SquareRootDilation

/-! Added bridges: the constructed dilation preserves actual skew-flow currents.
Arbitrary ambient compression is not silently treated as multiplicative. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators
open ContinuousLinearMap
namespace ParsevalFamily
variable {H I : Type*} {K : I → Type*}
  [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H] [Fintype I]
  [∀ i, NormedAddCommGroup (K i)] [∀ i, InnerProductSpace ℂ (K i)]
  [∀ i, CompleteSpace (K i)] (V : ParsevalFamily H I K)

/-- Compression of an arbitrary operator on the larger Hilbert space. -/
def compressOperator (X : PiLp 2 K →L[ℂ] PiLp 2 K) : H →L[ℂ] H :=
  V.synthesis.comp (X.comp V.analysis)

theorem compressOperator_one : V.compressOperator 1 = 1 := by
  ext x
  exact congrArg (fun T : H →L[ℂ] H => T x) V.synthesis_analysis

theorem compressOperator_lift (X : H →L[ℂ] H) :
    V.compressOperator (V.liftOperator X) = X := V.liftOperator_recover X

/-- The exact multiplicativity defect retains the missing range projector. -/
theorem compress_mul_defect (X Y : PiLp 2 K →L[ℂ] PiLp 2 K) :
    V.compressOperator (X * Y) - V.compressOperator X * V.compressOperator Y =
    V.synthesis.comp (X.comp ((1 - V.rangeProjection).comp (Y.comp V.analysis))) := by
  ext x
  simp only [compressOperator, comp_apply, sub_apply, mul_apply_eq_comp,
    rangeProjection, one_apply_eq_self, map_sub]

theorem compress_coordinate [DecidableEq I] (i : I) :
    V.compressOperator (ChannelDilation.coordinate K i) = V.effectAtlas.effect i := by
  unfold compressOperator
  rw [V.synthesis_eq_adjoint]
  exact V.effect_compression i

theorem effect_square_defect [DecidableEq I] (i : I) :
    V.effectAtlas.effect i - V.effectAtlas.effect i * V.effectAtlas.effect i =
    V.synthesis.comp ((ChannelDilation.coordinate K i).comp
      ((1 - V.rangeProjection).comp ((ChannelDilation.coordinate K i).comp V.analysis))) := by
  have h := V.compress_mul_defect (ChannelDilation.coordinate K i) (ChannelDilation.coordinate K i)
  rwa [ChannelDilation.coordinate_idempotent, V.compress_coordinate] at h

/-- The lifted generator is skew whenever the original generator is skew. -/
theorem liftOperator_skew (A : H →L[ℂ] H) (hA : IsSkew A) : IsSkew (V.liftOperator A) := by
  intro x y
  change inner ℂ (V.analysis (A (V.synthesis x))) y =
    -inner ℂ x (V.analysis (A (V.synthesis y)))
  rw [← V.adjoint_synthesis]
  rw [adjoint_inner_left, adjoint_inner_right]
  exact hA _ _

theorem lifted_flow {ψ : ℝ → H} {t : ℝ} (A : H →L[ℂ] H)
    (hψ : HasDerivAt ψ (A (ψ t)) t) :
    HasDerivAt (fun s => V.analysis (ψ s))
      (V.liftOperator A (V.analysis (ψ t))) t := by
  have h := V.hasDerivAt_analysis hψ
  have he : V.synthesis (V.analysis (ψ t)) = ψ t :=
    congrArg (fun T : H →L[ℂ] H => T (ψ t)) V.synthesis_analysis
  simpa only [liftOperator, comp_apply, he] using h

/-- Equality of the full sharp enlarged-space and positive-effect currents. -/
theorem dilated_current [DecidableEq I] (A : H →L[ℂ] H) (hA : IsSkew A)
    (ψ : H) (i j : I) :
    (ChannelDilation.coordinateAtlas K).current (V.liftOperator A) (V.analysis ψ) i j =
      V.effectAtlas.current A ψ i j := by
  rw [EffectAtlas.current, effectExchange_eq_pairCurrent A hA]
  change 2 * (inner ℂ (ChannelDilation.coordinate K i (V.analysis ψ))
    (V.analysis (A (V.synthesis (ChannelDilation.coordinate K j (V.analysis ψ)))))).re =
      2 * (inner ℂ (V.effectAtlas.effect i ψ) (A (V.effectAtlas.effect j ψ))).re
  rw [← V.adjoint_synthesis, adjoint_inner_right]
  have he (k : I) : V.synthesis (ChannelDilation.coordinate K k (V.analysis ψ)) =
      V.effectAtlas.effect k ψ := by
    exact congrArg (fun T : H →L[ℂ] H => T ψ) (V.compress_coordinate k)
  rw [V.adjoint_synthesis, he i, he j]

/-- Local dilation identity also transfers the actual channel probability derivative. -/
theorem hasDerivAt_dilated_probability [DecidableEq I] (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (A (ψ t)) t) (i : I) :
    HasDerivAt (fun s => (ChannelDilation.coordinateAtlas K).energy (V.analysis (ψ s)) i)
      (∑ j, V.effectAtlas.current A (ψ t) i j) t := by
  simpa only [V.compressed_probability] using V.effectAtlas.hasDerivAt_probability A hA hψ i

/-- Residual quadratic form, establishing positivity of the projection complement. -/
theorem residual_norm_sq (y : PiLp 2 K) :
    (inner ℂ y (y - V.rangeProjection y)).re = ‖y - V.rangeProjection y‖ ^ 2 := by
  have ho := V.residual_orthogonal (V.synthesis y) y
  change inner ℂ (V.rangeProjection y) (y - V.rangeProjection y) = 0 at ho
  have he : inner ℂ (y - V.rangeProjection y) (y - V.rangeProjection y) =
      inner ℂ y (y - V.rangeProjection y) := by
    rw [inner_sub_left, ho, sub_zero]
  rw [← he]
  exact inner_self_eq_norm_sq (𝕜 := ℂ) _

/-- Unsharpness is exactly leakage of a projected dilation vector out of the isometric range. -/
theorem effect_defect_norm [DecidableEq I] (ψ : H) (i : I) :
    effectExpectation (V.effectAtlas.effect i - V.effectAtlas.effect i * V.effectAtlas.effect i) ψ =
    ‖ChannelDilation.coordinate K i (V.analysis ψ) -
      V.rangeProjection (ChannelDilation.coordinate K i (V.analysis ψ))‖ ^ 2 := by
  rw [V.effect_square_defect]
  unfold effectExpectation
  simp only [comp_apply, sub_apply, one_apply_eq_self]
  rw [V.synthesis_eq_adjoint, adjoint_inner_right,
    ← ChannelDilation.coordinate_selfAdjoint]
  exact V.residual_norm_sq _

theorem effect_defect_nonnegative [DecidableEq I] (ψ : H) (i : I) :
    0 ≤ effectExpectation (V.effectAtlas.effect i - V.effectAtlas.effect i * V.effectAtlas.effect i) ψ := by
  rw [V.effect_defect_norm]
  positivity

end ParsevalFamily
end KomorebiPhysics
