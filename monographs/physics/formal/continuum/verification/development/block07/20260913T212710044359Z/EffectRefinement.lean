module

public import KomorebiPhysics.MovingEffects

/-! Chapter 5.3, (5.17)--(5.21). Genuine address-map coarsening of positive,
possibly overlapping effects. Coarse positivity, source terms and currents
are derived from the actual operators. No pairwise orthogonality is used. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.EffectAtlas
open scoped BigOperators Matrix
variable {H I J : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
  [Fintype I] [Fintype J] [DecidableEq J]

/-- Each fine effect is assigned exactly once. Empty coarse cells are allowed. -/
def coarsen (F : EffectAtlas H I) (f : I → J) : EffectAtlas H J where
  effect a := ∑ i ∈ Atlas.fiber f a, F.effect i
  sum_effect := by
    simp_rw [← RefinementTower.push_eq_fiber]
    rw [RefinementTower.sum_push, F.sum_effect]
  selfAdjoint := by
    intro a x y
    simp only [sum_apply, sum_inner, inner_sum]
    exact Finset.sum_congr rfl (fun i _ => F.selfAdjoint i x y)
  nonnegative := by
    intro a x
    simp only [sum_apply, inner_sum, Complex.re_sum]
    exact Finset.sum_nonneg (fun i _ => F.nonnegative i x)

theorem coarsen_effect (F : EffectAtlas H I) (f : I → J) (a : J) :
    (F.coarsen f).effect a = ∑ i ∈ Atlas.fiber f a, F.effect i := rfl

theorem coarsen_probability (F : EffectAtlas H I) (f : I → J) (ψ : H) (a : J) :
    (F.coarsen f).probability ψ a = ∑ i ∈ Atlas.fiber f a, F.probability ψ i := by
  simp only [probability, effectExpectation, coarsen_effect, sum_apply, inner_sum, Complex.re_sum]

/-- Arbitrary generators retain the exact two-sided current aggregation. -/
theorem coarsen_current (F : EffectAtlas H I) (f : I → J) (A : H →L[ℂ] H)
    (ψ : H) (a b : J) :
    (F.coarsen f).current A ψ a b =
      ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, F.current A ψ i j := by
  simp only [current, coarsen_effect, sum_apply, effectExchange_sum_left,
    effectExchange_sum_right]
  rw [Finset.sum_comm]

/-- Finite grouping of actual effect velocities. -/
def coarseVelocity (D : I → H →L[ℂ] H) (f : I → J) (a : J) : H →L[ℂ] H :=
  ∑ i ∈ Atlas.fiber f a, D i

theorem coarsen_source (D : I → H →L[ℂ] H) (f : I → J) (ψ : H) (a : J) :
    source (coarseVelocity D f) ψ a = ∑ i ∈ Atlas.fiber f a, source D ψ i := by
  simp only [source, coarseVelocity, effectExpectation, sum_apply, inner_sum, Complex.re_sum]

/-- Coarse operator differentiation is derived by the actual finite-sum rule. -/
theorem hasDerivAt_coarsen_effect (F : ℝ → EffectAtlas H I)
    (D : I → H →L[ℂ] H) (f : I → J) (t : ℝ)
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t) (a : J) :
    HasDerivAt (fun s => ((F s).coarsen f).effect a) (coarseVelocity D f a) t :=
  HasDerivAt.fun_sum (u := Atlas.fiber f a) (fun i _ => hF i)

theorem hasDerivAt_coarse_probability (F : EffectAtlas H I) (f : I → J)
    (A : H →L[ℂ] H) (hA : IsSkew A) {ψ : ℝ → H} {t : ℝ}
    (hψ : HasDerivAt ψ (A (ψ t)) t) (a : J) :
    HasDerivAt (fun s => (F.coarsen f).probability (ψ s) a)
      (∑ b, ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b,
        F.current A (ψ t) i j) t := by
  simpa only [coarsen_current] using (F.coarsen f).hasDerivAt_probability A hA hψ a

/-- Literal coarse moving balance with all sources and fine currents retained. -/
theorem hasDerivAt_moving_coarse_probability (F : ℝ → EffectAtlas H I)
    (D : I → H →L[ℂ] H) (f : I → J) (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ}
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t)
    (hψ : HasDerivAt ψ (A (ψ t)) t) (a : J) :
    HasDerivAt (fun s => ((F s).coarsen f).probability (ψ s) a)
      ((∑ i ∈ Atlas.fiber f a, source D (ψ t) i) +
       ∑ b, ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b,
        (F t).current A (ψ t) i j) t := by
  have h := hasDerivAt_moving_probability (fun s => (F s).coarsen f)
    (coarseVelocity D f) A hA (hasDerivAt_coarsen_effect F D f t hF) hψ a
  simpa only [coarsen_source, coarsen_current] using h

/-- The same identity as a literal incidence-matrix operation p^c=Rp. -/
theorem coarsen_probability_incidence (F : EffectAtlas H I) (f : I → J) (ψ : H) :
    (F.coarsen f).probability ψ = RefinementTower.incidence f *ᵥ F.probability ψ := by
  rw [← RefinementTower.push_eq_mulVec]
  funext a
  rw [coarsen_probability, RefinementTower.push_eq_fiber]

theorem coarsen_source_incidence (D : I → H →L[ℂ] H) (f : I → J) (ψ : H) :
    source (coarseVelocity D f) ψ = RefinementTower.incidence f *ᵥ source D ψ := by
  rw [← RefinementTower.push_eq_mulVec]
  funext a
  rw [coarsen_source, RefinementTower.push_eq_fiber]

theorem coarsen_current_incidence (F : EffectAtlas H I) (f : I → J)
    (A : H →L[ℂ] H) (ψ : H) :
    Matrix.of ((F.coarsen f).current A ψ) =
      RefinementTower.aggregateCurrent (RefinementTower.incidence f) (Matrix.of (F.current A ψ)) := by
  ext a b
  change (F.coarsen f).current A ψ a b = _
  rw [coarsen_current, RefinementTower.aggregateCurrent_entry]
  rfl

/-- Sequential and composed coarsening agree at the operator level. -/
theorem coarsen_comp_effect {K : Type*} [Fintype K] [DecidableEq K]
    (F : EffectAtlas H I) (f : I → J) (g : J → K) (c : K) :
    ((F.coarsen f).coarsen g).effect c = (F.coarsen (g ∘ f)).effect c := by
  simp only [coarsen_effect, ← RefinementTower.push_eq_fiber]
  exact congrFun (RefinementTower.push_comp f g F.effect) c

theorem coarsen_comp_probability {K : Type*} [Fintype K] [DecidableEq K]
    (F : EffectAtlas H I) (f : I → J) (g : J → K) (ψ : H) (c : K) :
    ((F.coarsen f).coarsen g).probability ψ c = (F.coarsen (g ∘ f)).probability ψ c := by
  simp only [probability, coarsen_comp_effect]

theorem coarsen_comp_current {K : Type*} [Fintype K] [DecidableEq K]
    (F : EffectAtlas H I) (f : I → J) (g : J → K) (A : H →L[ℂ] H)
    (ψ : H) (c d : K) :
    ((F.coarsen f).coarsen g).current A ψ c d = (F.coarsen (g ∘ f)).current A ψ c d := by
  simp only [current, coarsen_comp_effect]

/-- Grouping commutes with actual conjugation, not merely with scalar probabilities. -/
theorem coarsen_conjugate_effect [CompleteSpace H] (F : EffectAtlas H I) (f : I → J)
    (U : H →L[ℂ] H) (hU : U * star U = 1) (a : J) :
    ((F.conjugate U hU).coarsen f).effect a = ((F.coarsen f).conjugate U hU).effect a := by
  simp only [coarsen_effect, conjugate, Finset.mul_sum, Finset.sum_mul]

end KomorebiPhysics.EffectAtlas
