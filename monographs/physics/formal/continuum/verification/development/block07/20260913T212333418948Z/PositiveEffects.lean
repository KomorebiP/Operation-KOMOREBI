module

public import KomorebiPhysics.MovingAtlas
public import KomorebiPhysics.UniversalBalance

/-!
Master Chapter 5.1, (5.1)--(5.10). Finite positive resolutions by bounded
operators on a complex inner-product space. No idempotence, orthogonality,
commutation, or finite-dimensionality is imposed on the effects.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators

section Pairing
variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]

/-- Antisymmetrized real exchange, with receiving index first. -/
def effectExchange (A : H →L[ℂ] H) (x y : H) : ℝ :=
  (inner ℂ x (A y)).re - (inner ℂ y (A x)).re

theorem effectExchange_antisymm (A : H →L[ℂ] H) (x y : H) :
    effectExchange A x y = -effectExchange A y x := by
  unfold effectExchange
  ring

theorem effectExchange_self (A : H →L[ℂ] H) (x : H) :
    effectExchange A x x = 0 := sub_self _

/-- Skewness reduces the two-term source definition to twice one pairing. -/
theorem effectExchange_eq_pairCurrent (A : H →L[ℂ] H) (hA : IsSkew A) (x y : H) :
    effectExchange A x y = pairCurrent A x y := by
  have h := pairCurrent_antisymm A hA x y
  unfold effectExchange pairCurrent at *
  linarith

theorem effectExchange_sum_left {I : Type*} (A : H →L[ℂ] H)
    (s : Finset I) (x : I → H) (y : H) :
    effectExchange A (∑ i ∈ s, x i) y = ∑ i ∈ s, effectExchange A (x i) y := by
  simp only [effectExchange, sum_inner, map_sum, inner_sum, Complex.re_sum,
    Finset.sum_sub_distrib]

theorem effectExchange_sum_right {I : Type*} (A : H →L[ℂ] H)
    (s : Finset I) (x : H) (y : I → H) :
    effectExchange A x (∑ i ∈ s, y i) = ∑ i ∈ s, effectExchange A x (y i) := by
  simp only [effectExchange, sum_inner, map_sum, inner_sum, Complex.re_sum,
    Finset.sum_sub_distrib]

/-- The Born expectation, not the squared norm of the effected vector. -/
def effectExpectation (F : H →L[ℂ] H) (ψ : H) : ℝ := (inner ℂ ψ (F ψ)).re

/-- Reality follows from the operator's Hermitian pairing identity. -/
theorem effectExpectation_real (F : H →L[ℂ] H)
    (hF : ∀ x y, inner ℂ (F x) y = inner ℂ x (F y)) (ψ : H) :
    (inner ℂ ψ (F ψ)).im = 0 := by
  have h := congrArg Complex.im (inner_conj_symm (𝕜 := ℂ) ψ (F ψ))
  rw [hF] at h
  simp only [Complex.conj_im] at h
  linarith

theorem effectExpectation_cast (F : H →L[ℂ] H)
    (hF : ∀ x y, inner ℂ (F x) y = inner ℂ x (F y)) (ψ : H) :
    (effectExpectation F ψ : ℂ) = inner ℂ ψ (F ψ) := by
  apply Complex.ext
  · rfl
  · simpa using (effectExpectation_real F hF ψ).symm

/-- Actual derivative with both moving-state and moving-effect contributions. -/
theorem hasDerivAt_effectExpectation (F : ℝ → H →L[ℂ] H) (ψ : ℝ → H)
    (dF : H →L[ℂ] H) (v : H) (t : ℝ)
    (hF : HasDerivAt F dF t) (hψ : HasDerivAt ψ v t)
    (hsym : ∀ x y, inner ℂ (F t x) y = inner ℂ x (F t y)) :
    HasDerivAt (fun s => effectExpectation (F s) (ψ s))
      (effectExpectation dF (ψ t) + 2 * (inner ℂ (F t (ψ t)) v).re) t := by
  have ha := MovingAtlas.hasDerivAt_operator_apply F ψ dF v t hF hψ
  have hi := Complex.reCLM.hasFDerivAt.comp_hasDerivAt t (hψ.inner ℂ ha)
  have hs := hsym (ψ t) v
  have hr := inner_re_symm (𝕜 := ℂ) v (F t (ψ t))
  have he : Complex.reCLM (inner ℂ (ψ t) (dF (ψ t) + F t v) +
      inner ℂ v (F t (ψ t))) =
      effectExpectation dF (ψ t) + 2 * (inner ℂ (F t (ψ t)) v).re := by
    simp only [Complex.reCLM_apply, inner_add_right, Complex.add_re, effectExpectation]
    rw [← hs]
    change (inner ℂ v (F t (ψ t))).re = (inner ℂ (F t (ψ t)) v).re at hr
    linarith
  rw [he] at hi
  exact hi

end Pairing

/-- Only positive Hermitian effects and their resolution law are fields.
Probabilities, derivatives and current balance are not assumed. -/
structure EffectAtlas (H I : Type*) [NormedAddCommGroup H] [InnerProductSpace ℂ H]
    [Fintype I] where
  effect : I → H →L[ℂ] H
  selfAdjoint : ∀ i x y, inner ℂ (effect i x) y = inner ℂ x (effect i y)
  nonnegative : ∀ i x, 0 ≤ (inner ℂ x (effect i x)).re
  sum_effect : ∑ i, effect i = 1

namespace EffectAtlas
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H] [Fintype I]
variable (F : EffectAtlas H I)

/-- Literal (5.2), real by a separate theorem. -/
def probability (ψ : H) (i : I) : ℝ := effectExpectation (F.effect i) ψ

/-- Literal (5.3), no sharp-projector substitution. -/
def current (A : H →L[ℂ] H) (ψ : H) (i j : I) : ℝ :=
  effectExchange A (F.effect i ψ) (F.effect j ψ)

theorem reconstruct (ψ : H) : (∑ i, F.effect i ψ) = ψ := by
  have h := congrArg (fun T : H →L[ℂ] H => T ψ) F.sum_effect
  simpa only [sum_apply, one_apply_eq_self] using h

theorem probability_real (ψ : H) (i : I) : (inner ℂ ψ (F.effect i ψ)).im = 0 :=
  effectExpectation_real _ (F.selfAdjoint i) ψ

theorem probability_cast (ψ : H) (i : I) :
    (F.probability ψ i : ℂ) = inner ℂ ψ (F.effect i ψ) :=
  effectExpectation_cast _ (F.selfAdjoint i) ψ

theorem probability_nonneg (ψ : H) (i : I) : 0 ≤ F.probability ψ i :=
  F.nonnegative i ψ

theorem probability_sum (ψ : H) : (∑ i, F.probability ψ i) = ‖ψ‖ ^ 2 := by
  simp only [probability, effectExpectation, ← Complex.re_sum, ← inner_sum,
    F.reconstruct]
  exact inner_self_eq_norm_sq (𝕜 := ℂ) ψ

theorem probability_le_norm_sq (ψ : H) (i : I) : F.probability ψ i ≤ ‖ψ‖ ^ 2 := by
  rw [← F.probability_sum]
  exact Finset.single_le_sum (fun j _ => F.probability_nonneg ψ j) (Finset.mem_univ i)

theorem normalized (ψ : H) (hψ : ‖ψ‖ = 1) :
    (∑ i, F.probability ψ i) = 1 ∧ ∀ i, 0 ≤ F.probability ψ i ∧ F.probability ψ i ≤ 1 := by
  constructor
  · rw [F.probability_sum, hψ, one_pow]
  · intro i
    exact ⟨F.probability_nonneg ψ i, by simpa [hψ] using F.probability_le_norm_sq ψ i⟩

theorem current_antisymm (A : H →L[ℂ] H) (ψ : H) (i j : I) :
    F.current A ψ i j = -F.current A ψ j i := effectExchange_antisymm A _ _

theorem current_diagonal (A : H →L[ℂ] H) (ψ : H) (i : I) :
    F.current A ψ i i = 0 := effectExchange_self A _

theorem current_row_sum (A : H →L[ℂ] H) (ψ : H) (i : I) :
    (∑ j, F.current A ψ i j) = effectExchange A (F.effect i ψ) ψ := by
  simp only [current, ← effectExchange_sum_right, F.reconstruct]

theorem current_row_sum_skew (A : H →L[ℂ] H) (hA : IsSkew A) (ψ : H) (i : I) :
    (∑ j, F.current A ψ i j) = 2 * (inner ℂ (F.effect i ψ) (A ψ)).re := by
  rw [F.current_row_sum, effectExchange_eq_pairCurrent A hA]
  rfl

/-- The actual Born derivative is deduced from the original vector flow. -/
theorem hasDerivAt_probability (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (A (ψ t)) t) (i : I) :
    HasDerivAt (fun s => F.probability (ψ s) i) (∑ j, F.current A (ψ t) i j) t := by
  have h := hasDerivAt_effectExpectation (fun _ => F.effect i) ψ 0 (A (ψ t)) t
    (hasDerivAt_const t _) hψ (F.selfAdjoint i)
  simpa only [probability, effectExpectation, zero_apply, inner_zero_right,
    Complex.zero_re, zero_add, F.current_row_sum_skew A hA] using h

theorem total_current_zero (A : H →L[ℂ] H) (ψ : H) :
    (∑ i, ∑ j, F.current A ψ i j) = 0 :=
  antisymmetric_sum_zero _ Finset.univ (fun i _ j _ => F.current_antisymm A ψ i j)

theorem hasDerivAt_total (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (A (ψ t)) t) :
    HasDerivAt (fun s => ∑ i, F.probability (ψ s) i) 0 t := by
  have h := HasDerivAt.fun_sum (u := Finset.univ) (fun i _ => F.hasDerivAt_probability A hA hψ i)
  rwa [F.total_current_zero] at h

/-- Only boundary exchange survives in a finite subsystem. -/
theorem hasDerivAt_subset [DecidableEq I] (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (A (ψ t)) t) (C : Finset I) :
    HasDerivAt (fun s => ∑ i ∈ C, F.probability (ψ s) i)
      (∑ i ∈ C, ∑ j ∈ Cᶜ, F.current A (ψ t) i j) t := by
  have h := HasDerivAt.fun_sum (u := C) (fun i _ => F.hasDerivAt_probability A hA hψ i)
  rwa [UniversalBalance.boundary_sum _ (F.current_antisymm A (ψ t)) C] at h

/-- The sharp case is a constructed special case, not an assumption on effects. -/
def ofAtlas [DecidableEq I] (P : Atlas H I) : EffectAtlas H I where
  effect := P.proj
  selfAdjoint := P.selfAdjoint
  sum_effect := P.sum_proj
  nonnegative := by
    intro i x
    have h : (inner ℂ x (P.proj i x)).re = ‖P.packet x i‖ ^ 2 := by
      have hr : (inner ℂ x (P.proj i x)).re = (inner ℂ (P.proj i x) x).re :=
        inner_re_symm (𝕜 := ℂ) x (P.proj i x)
      rw [hr]
      change (inner ℂ (P.packet x i) x).re = _
      rw [← P.inner_packet_project]
      exact inner_self_eq_norm_sq (𝕜 := ℂ) (P.packet x i)
    rw [h]
    positivity

theorem ofAtlas_probability [DecidableEq I] (P : Atlas H I) (ψ : H) (i : I) :
    (ofAtlas P).probability ψ i = P.energy ψ i := by
  change (inner ℂ ψ (P.proj i ψ)).re = ‖P.packet ψ i‖ ^ 2
  have hr : (inner ℂ ψ (P.proj i ψ)).re = (inner ℂ (P.proj i ψ) ψ).re :=
    inner_re_symm (𝕜 := ℂ) ψ (P.proj i ψ)
  rw [hr]
  change (inner ℂ (P.packet ψ i) ψ).re = _
  rw [← P.inner_packet_project]
  exact inner_self_eq_norm_sq (𝕜 := ℂ) (P.packet ψ i)

theorem ofAtlas_current [DecidableEq I] (P : Atlas H I) (A : H →L[ℂ] H)
    (hA : IsSkew A) (ψ : H) (i j : I) :
    (ofAtlas P).current A ψ i j = P.current A ψ i j :=
  effectExchange_eq_pairCurrent A hA _ _

end EffectAtlas
end KomorebiPhysics
