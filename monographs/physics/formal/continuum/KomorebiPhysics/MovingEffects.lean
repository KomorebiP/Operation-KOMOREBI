module

public import KomorebiPhysics.PositiveEffects

/-! Chapter 5.2, (5.11)--(5.16). Actual operator derivatives of a moving
positive resolution; zero total source is deduced by differentiation.
Unitary transport is constructed and differentiated in operator norm. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators

section Derivative
variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]

/-- The derivative of a Hermitian operator curve is Hermitian; not assumed. -/
theorem differentiated_selfAdjoint (F : ℝ → H →L[ℂ] H) (dF : H →L[ℂ] H) (t : ℝ)
    (hF : HasDerivAt F dF t)
    (hsym : ∀ s x y, inner ℂ (F s x) y = inner ℂ x (F s y)) :
    ∀ x y, inner ℂ (dF x) y = inner ℂ x (dF y) := by
  intro x y
  have hx := MovingAtlas.hasDerivAt_operator_apply F (fun _ => x) dF 0 t
    hF (hasDerivAt_const t x)
  have hy := MovingAtlas.hasDerivAt_operator_apply F (fun _ => y) dF 0 t
    hF (hasDerivAt_const t y)
  simp only [map_zero, add_zero] at hx hy
  have hl := hx.inner ℂ (hasDerivAt_const t y)
  have hr := (hasDerivAt_const t x).inner ℂ hy
  simp only [inner_zero_right, inner_zero_left, zero_add, add_zero] at hl hr
  have he : (fun s => inner ℂ (F s x) y) = fun s => inner ℂ x (F s y) :=
    funext (fun s => hsym s x y)
  rw [he] at hl
  exact hl.unique hr

end Derivative

namespace EffectAtlas
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H] [Fintype I]

/-- Source is the expectation of the actual effect velocity. -/
def source (D : I → H →L[ℂ] H) (ψ : H) (i : I) : ℝ := effectExpectation (D i) ψ

/-- Differentiate the actual partition of unity, rather than imposing zero source. -/
theorem derivative_sum (F : ℝ → EffectAtlas H I) (D : I → H →L[ℂ] H) (t : ℝ)
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t) : ∑ i, D i = 0 := by
  have h := HasDerivAt.fun_sum (u := Finset.univ) (fun i _ => hF i)
  have he : (fun s => ∑ i, (F s).effect i) = fun _ => (1 : H →L[ℂ] H) :=
    funext (fun s => (F s).sum_effect)
  rw [he] at h
  exact h.unique (hasDerivAt_const t _)

theorem source_sum (F : ℝ → EffectAtlas H I) (D : I → H →L[ℂ] H) (t : ℝ)
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t) (ψ : H) :
    (∑ i, source D ψ i) = 0 := by
  have hD := derivative_sum F D t hF
  simp only [source, effectExpectation, ← Complex.re_sum, ← inner_sum, ← sum_apply,
    hD, zero_apply, inner_zero_right, Complex.zero_re]

theorem source_real (F : ℝ → EffectAtlas H I) (D : I → H →L[ℂ] H) (t : ℝ)
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t) (ψ : H) (i : I) :
    (inner ℂ ψ (D i ψ)).im = 0 :=
  effectExpectation_real _ (differentiated_selfAdjoint _ _ t (hF i)
    (fun s => (F s).selfAdjoint i)) ψ

theorem source_cast (F : ℝ → EffectAtlas H I) (D : I → H →L[ℂ] H) (t : ℝ)
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t) (ψ : H) (i : I) :
    (source D ψ i : ℂ) = inner ℂ ψ (D i ψ) :=
  effectExpectation_cast _ (differentiated_selfAdjoint _ _ t (hF i)
    (fun s => (F s).selfAdjoint i)) ψ

/-- Both contributions are conclusions from the original two derivatives. -/
theorem hasDerivAt_moving_probability (F : ℝ → EffectAtlas H I)
    (D : I → H →L[ℂ] H) (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ}
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t)
    (hψ : HasDerivAt ψ (A (ψ t)) t) (i : I) :
    HasDerivAt (fun s => (F s).probability (ψ s) i)
      (source D (ψ t) i + ∑ j, (F t).current A (ψ t) i j) t := by
  have h := hasDerivAt_effectExpectation (fun s => (F s).effect i) ψ (D i) (A (ψ t)) t
    (hF i) hψ ((F t).selfAdjoint i)
  simpa only [source, probability, (F t).current_row_sum_skew A hA] using h

theorem hasDerivAt_moving_total (F : ℝ → EffectAtlas H I)
    (D : I → H →L[ℂ] H) (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ}
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t)
    (hψ : HasDerivAt ψ (A (ψ t)) t) :
    HasDerivAt (fun s => ∑ i, (F s).probability (ψ s) i) 0 t := by
  have h := HasDerivAt.fun_sum (u := Finset.univ)
    (fun i _ => hasDerivAt_moving_probability F D A hA hF hψ i)
  simpa only [Finset.sum_add_distrib, source_sum F D t hF, (F t).total_current_zero,
    add_zero] using h

theorem hasDerivAt_moving_subset [DecidableEq I] (F : ℝ → EffectAtlas H I)
    (D : I → H →L[ℂ] H) (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ}
    (hF : ∀ i, HasDerivAt (fun s => (F s).effect i) (D i) t)
    (hψ : HasDerivAt ψ (A (ψ t)) t) (C : Finset I) :
    HasDerivAt (fun s => ∑ i ∈ C, (F s).probability (ψ s) i)
      ((∑ i ∈ C, source D (ψ t) i) +
       ∑ i ∈ C, ∑ j ∈ Cᶜ, (F t).current A (ψ t) i j) t :=
  UniversalBalance.hasDerivAt_subset
    (fun i => hasDerivAt_moving_probability F D A hA hF hψ i)
    ((F t).current_antisymm A (ψ t)) C

/-- Moving effect probabilities have the conserved total along an actual all-time flow. -/
theorem moving_total_constant (F : ℝ → EffectAtlas H I) (A : ℝ → H →L[ℂ] H)
    (ψ : ℝ → H) (hA : ∀ t, IsSkew (A t))
    (hψ : ∀ t, HasDerivAt ψ (A t (ψ t)) t) (s t : ℝ) :
    (∑ i, (F s).probability (ψ s) i) = ∑ i, (F t).probability (ψ t) i := by
  simp only [probability_sum]
  exact is_const_of_deriv_eq_zero
    (fun u => (hasDerivAt_total_energy (A u) (hA u) (hψ u)).differentiableAt)
    (fun u => (hasDerivAt_total_energy (A u) (hA u) (hψ u)).deriv) s t

section Unitary
variable [CompleteSpace H]

/-- Conjugation is positive even without sharpness. Only the identity needed
for completeness is required in this algebraic constructor. -/
def conjugate (F : EffectAtlas H I) (U : H →L[ℂ] H) (hright : U * star U = 1) :
    EffectAtlas H I where
  effect i := U * F.effect i * star U
  sum_effect := by rw [← Finset.sum_mul, ← Finset.mul_sum, F.sum_effect, mul_one, hright]
  selfAdjoint := by
    intro i x y
    change inner ℂ (U (F.effect i (star U x))) y = inner ℂ x (U (F.effect i (star U y)))
    rw [← U.adjoint_inner_right]
    change inner ℂ (F.effect i (star U x)) (star U y) = _
    rw [F.selfAdjoint]
    exact U.adjoint_inner_left (F.effect i (star U y)) x
  nonnegative := by
    intro i x
    change 0 ≤ (inner ℂ x (U (F.effect i (star U x)))).re
    rw [← U.adjoint_inner_left]
    exact F.nonnegative i (star U x)

theorem conjugate_probability (F : EffectAtlas H I) (U : H →L[ℂ] H)
    (hright : U * star U = 1) (ψ : H) (i : I) :
    (F.conjugate U hright).probability ψ i = F.probability (star U ψ) i := by
  change (inner ℂ ψ (U (F.effect i (star U ψ)))).re = _
  rw [← U.adjoint_inner_left]
  rfl

/-- The operator's actual unitary deformation derivative, with K=dU U*. -/
theorem hasDerivAt_conjugate_effect (F : EffectAtlas H I) (U : ℝ → H →L[ℂ] H)
    (dU : H →L[ℂ] H) (t : ℝ) (hU : HasDerivAt U dU t)
    (hleft : star (U t) * U t = 1) (hright : ∀ s, U s * star (U s) = 1) (i : I) :
    HasDerivAt (fun s => (F.conjugate (U s) (hright s)).effect i)
      (Deformation.comm (dU * star (U t)) ((F.conjugate (U t) (hright t)).effect i)) t :=
  MovingAtlas.hasDerivAt_unitary_projector U dU (F.effect i) t hU hleft hright

/-- The laboratory-frame angular velocity really is skew. -/
theorem conjugate_velocity_skew (U : ℝ → H →L[ℂ] H) (dU : H →L[ℂ] H) (t : ℝ)
    (hU : HasDerivAt U dU t) (hright : ∀ s, U s * star (U s) = 1) :
    IsSkew (dU * star (U t)) :=
  MovingAtlas.isSkew_of_star _ (MovingAtlas.right_velocity_skew U dU t hU hright)

/-- Equations (5.13)--(5.16) with the source commutator derived, not assumed. -/
theorem hasDerivAt_conjugate_probability (F : EffectAtlas H I) (U : ℝ → H →L[ℂ] H)
    (dU A : H →L[ℂ] H) (hA : IsSkew A) {ψ : ℝ → H} {t : ℝ}
    (hU : HasDerivAt U dU t) (hψ : HasDerivAt ψ (A (ψ t)) t)
    (hleft : star (U t) * U t = 1) (hright : ∀ s, U s * star (U s) = 1) (i : I) :
    HasDerivAt (fun s => (F.conjugate (U s) (hright s)).probability (ψ s) i)
      (effectExpectation (Deformation.comm (dU * star (U t))
          ((F.conjugate (U t) (hright t)).effect i)) (ψ t) +
       ∑ j, (F.conjugate (U t) (hright t)).current A (ψ t) i j) t :=
  hasDerivAt_moving_probability (fun s => F.conjugate (U s) (hright s)) _ A hA
    (hasDerivAt_conjugate_effect F U dU t hU hleft hright) hψ i

/-- The commutator sources sum to zero for the actual transported resolution. -/
theorem conjugate_source_sum (F : EffectAtlas H I) (U : ℝ → H →L[ℂ] H)
    (dU : H →L[ℂ] H) (t : ℝ) (hU : HasDerivAt U dU t)
    (hleft : star (U t) * U t = 1) (hright : ∀ s, U s * star (U s) = 1) (ψ : H) :
    (∑ i, effectExpectation (Deformation.comm (dU * star (U t))
       ((F.conjugate (U t) (hright t)).effect i)) ψ) = 0 :=
  source_sum (fun s => F.conjugate (U s) (hright s)) _ t
    (hasDerivAt_conjugate_effect F U dU t hU hleft hright) ψ

end Unitary
end EffectAtlas
end KomorebiPhysics
