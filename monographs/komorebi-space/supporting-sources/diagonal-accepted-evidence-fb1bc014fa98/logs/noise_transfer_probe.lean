import Mathlib.Analysis.InnerProductSpace.LaxMilgram
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Abel
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Tactic


set_option autoImplicit false

noncomputable section
universe u v
namespace KomorebiSpace.RegularizedHilbertRepair
open scoped RealInnerProductSpace
variable {H : Type u} {Y : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable (T : H →L[ℝ] Y) (α : ℝ)

def normal : H →L[ℝ] H := T.adjoint.comp T + α • ContinuousLinearMap.id ℝ H

@[simp] theorem normal_apply (a : H) : normal T α a = T.adjoint (T a) + α • a := rfl

@[simp] theorem normal_inner (a b : H) :
    ⟪normal T α a, b⟫ = ⟪T a, T b⟫ + α * ⟪a, b⟫ := by
  simp only [normal_apply, inner_add_left, real_inner_smul_left,
    ContinuousLinearMap.adjoint_inner_left]

def energyBilin : H →L[ℝ] H →L[ℝ] ℝ := (innerSL ℝ).comp (normal T α)

@[simp] theorem energyBilin_apply (a b : H) :
    energyBilin T α a b = ⟪T a, T b⟫ + α * ⟪a, b⟫ := by
  change ⟪normal T α a, b⟫ = _
  exact normal_inner T α a b

theorem energyBilin_coercive (hα : 0 < α) : IsCoercive (energyBilin T α) := by
  refine ⟨α, hα, ?_⟩
  intro a
  rw [energyBilin_apply, real_inner_self_eq_norm_sq, real_inner_self_eq_norm_sq]
  nlinarith [sq_nonneg ‖T a‖]

def normalEquiv (hα : 0 < α) : H ≃L[ℝ] H :=
  (energyBilin_coercive T α hα).continuousLinearEquivOfBilin

@[simp] theorem normalEquiv_apply (hα : 0 < α) (a : H) :
    normalEquiv T α hα a = normal T α a := by
  apply ext_inner_right ℝ
  intro b
  exact (IsCoercive.continuousLinearEquivOfBilin_apply (energyBilin_coercive T α hα) a b).trans
    (show energyBilin T α a b = ⟪normal T α a,b⟫ from rfl)

def correction (hα : 0 < α) (r : Y) : H :=
  (normalEquiv T α hα).symm (T.adjoint r)

@[simp] theorem normal_correction (hα : 0 < α) (r : Y) :
    normal T α (correction T α hα r) = T.adjoint r := by
  rw [← normalEquiv_apply T α hα]
  exact (normalEquiv T α hα).apply_symm_apply _

def objective (r : Y) (a : H) : ℝ := ‖T a - r‖^2 + α * ‖a‖^2

def gradient (r : Y) (a : H) : H := normal T α a - T.adjoint r

@[simp] theorem gradient_correction (hα : 0 < α) (r : Y) :
    gradient T α r (correction T α hα r) = 0 := by
  rw [gradient, normal_correction, sub_self]

theorem normal_equation (hα : 0 < α) (r : Y) :
    T.adjoint (r - T (correction T α hα r)) = α • correction T α hα r := by
  have h := normal_correction T α hα r
  rw [normal_apply] at h
  rw [map_sub, ← h]
  abel

theorem objective_expansion (r : Y) (a h : H) :
    objective T α r (a+h) = objective T α r a +
      2 * ⟪gradient T α r a,h⟫ + ‖T h‖^2 + α * ‖h‖^2 := by
  have hm : T (a+h)-r = (T a-r)+T h := by rw [map_add]; abel
  simp only [objective, hm, norm_add_sq_real, gradient, inner_sub_left,
    normal_inner, ContinuousLinearMap.adjoint_inner_left, inner_sub_left]
  ring

theorem energy_identity (hα : 0 < α) (r : Y) (a : H) :
    objective T α r a - objective T α r (correction T α hα r) =
      ‖T (a-correction T α hα r)‖^2 + α * ‖a-correction T α hα r‖^2 := by
  have he := objective_expansion T α r (correction T α hα r) (a-correction T α hα r)
  rw [add_sub_cancel, gradient_correction, inner_zero_left] at he
  linarith

/-- The constructed minimizer is global, not only a stationary point. -/
theorem correction_best (hα : 0 < α) (r : Y) (a : H) :
    objective T α r (correction T α hα r) ≤ objective T α r a := by
  have he := energy_identity T α hα r a
  have hn := mul_nonneg hα.le (sq_nonneg ‖a-correction T α hα r‖)
  nlinarith [sq_nonneg ‖T (a-correction T α hα r)‖]

theorem correction_unique (hα : 0 < α) (r : Y) (a : H)
    (ha : objective T α r a ≤ objective T α r (correction T α hα r)) :
    a = correction T α hα r := by
  have he := energy_identity T α hα r a
  have hz : ‖a-correction T α hα r‖^2 = 0 := by
    nlinarith [sq_nonneg ‖T (a-correction T α hα r)‖,
      sq_nonneg ‖a-correction T α hα r‖]
  exact sub_eq_zero.mp (norm_eq_zero.mp (sq_eq_zero_iff.mp hz))

theorem exists_unique_minimizer (hα : 0 < α) (r : Y) :
    ∃! a : H, ∀ b : H, objective T α r a ≤ objective T α r b := by
  refine ⟨correction T α hα r, correction_best T α hα r, ?_⟩
  intro a ha
  exact correction_unique T α hα r a (ha _)

theorem normal_unique (hα : 0 < α) (r : Y) (a : H)
    (ha : normal T α a = T.adjoint r) : a = correction T α hα r := by
  apply (normalEquiv T α hα).injective
  rw [normalEquiv_apply, normalEquiv_apply, normal_correction]
  exact ha

theorem gradient_zero_iff (hα : 0 < α) (r : Y) (a : H) :
    gradient T α r a = 0 ↔ a = correction T α hα r := by
  constructor
  · intro ha
    exact normal_unique T α hα r a (sub_eq_zero.mp ha)
  · rintro rfl
    exact gradient_correction T α hα r

@[simp] theorem correction_zero (hα : 0 < α) : correction T α hα 0 = 0 := by
  symm
  apply normal_unique
  simp

theorem gradient_error (hα : 0 < α) (r : Y) (a : H) :
    gradient T α r a = normal T α (a-correction T α hα r) := by
  rw [map_sub, normal_correction]
  rfl

theorem normal_bound (a : H) :
    α * ‖a‖ ≤ ‖normal T α a‖ := by
  by_cases hz : a = 0
  · simp [hz]
  · have hp : 0 < ‖a‖ := norm_pos_iff.mpr hz
    have hi := real_inner_le_norm (normal T α a) a
    rw [normal_inner, real_inner_self_eq_norm_sq, real_inner_self_eq_norm_sq] at hi
    nlinarith [sq_nonneg ‖T a‖]

/-- Actual normal-equation error certifies correction error at the same parameter. -/
theorem correction_error_bound (hα : 0 < α) (r : Y) (a : H) :
    ‖a-correction T α hα r‖ ≤ ‖gradient T α r a‖ / α := by
  apply (le_div_iff₀ hα).2
  rw [gradient_error]
  simpa [mul_comm] using normal_bound T α (a-correction T α hα r)

theorem gap_as_inner (hα : 0 < α) (r : Y) (a : H) :
    objective T α r a - objective T α r (correction T α hα r) =
      ⟪gradient T α r a, a-correction T α hα r⟫ := by
  rw [energy_identity, gradient_error, normal_inner,
    real_inner_self_eq_norm_sq, real_inner_self_eq_norm_sq]

theorem objective_gap_bound (hα : 0 < α) (r : Y) (a : H) :
    objective T α r a - objective T α r (correction T α hα r) ≤
      ‖gradient T α r a‖^2 / α := by
  rw [gap_as_inner]
  calc
    ⟪gradient T α r a, a-correction T α hα r⟫ ≤
        ‖gradient T α r a‖ * ‖a-correction T α hα r‖ := real_inner_le_norm _ _
    _ ≤ ‖gradient T α r a‖ * (‖gradient T α r a‖/α) :=
      mul_le_mul_of_nonneg_left (correction_error_bound T α hα r a) (norm_nonneg _)
    _ = ‖gradient T α r a‖^2/α := by ring

/-- A norm budget does not silently become a penalty on protected data. -/
theorem residual_best_at_budget (hα : 0 < α) (r : Y) (a : H)
    (ha : ‖a‖ ≤ ‖correction T α hα r‖) :
    ‖T (correction T α hα r)-r‖ ≤ ‖T a-r‖ := by
  have hb := correction_best T α hα r a
  unfold objective at hb
  have hm : ‖a‖^2 ≤ ‖correction T α hα r‖^2 := by
    nlinarith [norm_nonneg a, norm_nonneg (correction T α hα r)]
  have hp := mul_le_mul_of_nonneg_left hm hα.le
  nlinarith [norm_nonneg (T (correction T α hα r)-r), norm_nonneg (T a-r)]

theorem parameter_norm_antitone (hα : 0 < α) (γ : ℝ) (hγ : 0 < γ) (h : α < γ)
    (r : Y) : ‖correction T γ hγ r‖ ≤ ‖correction T α hα r‖ := by
  have h1 := correction_best T α hα r (correction T γ hγ r)
  have h2 := correction_best T γ hγ r (correction T α hα r)
  unfold objective at h1 h2
  have hs : ‖correction T γ hγ r‖^2 ≤ ‖correction T α hα r‖^2 := by nlinarith
  nlinarith [norm_nonneg (correction T γ hγ r), norm_nonneg (correction T α hα r)]

theorem parameter_residual_monotone (hα : 0 < α) (γ : ℝ) (hγ : 0 < γ) (h : α < γ)
    (r : Y) : ‖T (correction T α hα r)-r‖ ≤ ‖T (correction T γ hγ r)-r‖ := by
  exact residual_best_at_budget T α hα r _ (parameter_norm_antitone T α hα γ hγ h r)

theorem correction_data_energy (hα : 0 < α) (r s : Y) :
    ‖T (correction T α hα r-correction T α hα s)‖^2 +
      α * ‖correction T α hα r-correction T α hα s‖^2 =
      ⟪r-s,T (correction T α hα r-correction T α hα s)⟫ := by
  have hn : normal T α (correction T α hα r-correction T α hα s) =
      T.adjoint (r-s) := by rw [map_sub, normal_correction, normal_correction, map_sub]
  have hi := congrArg (fun z => ⟪z,correction T α hα r-correction T α hα s⟫) hn
  simpa only [normal_inner, real_inner_self_eq_norm_sq,
    ContinuousLinearMap.adjoint_inner_left] using hi

theorem data_noise_squared (hα : 0 < α) (r s : Y) :
    4*α*‖correction T α hα r-correction T α hα s‖^2 ≤ ‖r-s‖^2 := by
  have he := correction_data_energy T α hα r s
  have hi := real_inner_le_norm (r-s) (T (correction T α hα r-correction T α hα s))
  nlinarith [sq_nonneg (2*‖T (correction T α hα r-correction T α hα s)‖-‖r-s‖)]

theorem data_noise_bound (hα : 0 < α) (r s : Y) :
    ‖correction T α hα r-correction T α hα s‖ ≤ ‖r-s‖/(2*Real.sqrt α) := by
  have hsq := data_noise_squared T α hα r s
  have hs := Real.sq_sqrt hα.le
  have hp := Real.sqrt_pos.2 hα
  apply (le_div_iff₀ (by positivity : 0 < 2*Real.sqrt α)).2
  have hn := norm_nonneg (correction T α hα r-correction T α hα s)
  have hd := norm_nonneg (r-s)
  nlinarith [sq_nonneg (‖r-s‖-2*Real.sqrt α*‖correction T α hα r-correction T α hα s‖)]

theorem data_fitted_bound (hα : 0 < α) (r s : Y) :
    ‖T (correction T α hα r-correction T α hα s)‖ ≤ ‖r-s‖ := by
  have he := correction_data_energy T α hα r s
  have hi := real_inner_le_norm (r-s) (T (correction T α hα r-correction T α hα s))
  have hn := mul_nonneg hα.le (sq_nonneg ‖correction T α hα r-correction T α hα s‖)
  nlinarith [norm_nonneg (T (correction T α hα r-correction T α hα s)), norm_nonneg (r-s)]

/-- Solver error in the fitted data has the sharp universal square-root gain. -/
theorem fitted_error_squared (hα : 0 < α) (r : Y) (a : H) :
    4*α*‖T (a-correction T α hα r)‖^2 ≤ ‖gradient T α r a‖^2 := by
  have he := gap_as_inner T α hα r a
  rw [energy_identity] at he
  have hi := real_inner_le_norm (gradient T α r a) (a-correction T α hα r)
  nlinarith [sq_nonneg (2*α*‖a-correction T α hα r‖-‖gradient T α r a‖)]

theorem fitted_error_bound (hα : 0 < α) (r : Y) (a : H) :
    ‖T (a-correction T α hα r)‖ ≤ ‖gradient T α r a‖/(2*Real.sqrt α) := by
  have hsq := fitted_error_squared T α hα r a
  have hs := Real.sq_sqrt hα.le
  have hp := Real.sqrt_pos.2 hα
  apply (le_div_iff₀ (by positivity : 0 < 2*Real.sqrt α)).2
  have hn := norm_nonneg (T (a-correction T α hα r))
  have hd := norm_nonneg (gradient T α r a)
  nlinarith [sq_nonneg (‖gradient T α r a‖-2*Real.sqrt α*‖T (a-correction T α hα r)‖)]

/-- Numerical solver error and measured-data error are separate terms. -/
theorem solver_and_data_bound (hα : 0 < α) (r s : Y) (a : H) :
    ‖a-correction T α hα r‖ ≤
      ‖gradient T α s a‖/α + ‖s-r‖/(2*Real.sqrt α) := by
  have he : a-correction T α hα r =
      (a-correction T α hα s)+(correction T α hα s-correction T α hα r) := by abel
  calc
    ‖a-correction T α hα r‖ =
        ‖(a-correction T α hα s)+(correction T α hα s-correction T α hα r)‖ := by rw [he]
    _ ≤ ‖a-correction T α hα s‖+‖correction T α hα s-correction T α hα r‖ := norm_add_le _ _
    _ ≤ ‖gradient T α s a‖/α + ‖s-r‖/(2*Real.sqrt α) :=
      add_le_add (correction_error_bound T α hα s a) (data_noise_bound T α hα s r)

end KomorebiSpace.RegularizedHilbertRepair

set_option autoImplicit false
noncomputable section

namespace KomorebiSpace.DiagonalRegularization

/-- The literal integer schedule in Corollary 30.3; the exponents are real. -/
def noiseSchedule (δ : ℝ) : ℕ := Nat.ceil (δ ^ (-(2 : ℝ) / 3))

/-- Positivity of the noise level makes the chosen integer positive. -/
theorem noiseSchedule_pos {δ : ℝ} (hδ : 0 < δ) : 0 < noiseSchedule δ := by
  exact Nat.ceil_pos.mpr (Real.rpow_pos_of_pos hδ _)

theorem one_le_noiseSchedule {δ : ℝ} (hδ : 0 < δ) : 1 ≤ noiseSchedule δ :=
  noiseSchedule_pos hδ

private theorem noise_rpow_mul {δ : ℝ} (hδ : 0 < δ) :
    δ * δ ^ (-(2 : ℝ) / 3) = δ ^ ((1 : ℝ) / 3) := by
  calc
    δ * δ ^ (-(2 : ℝ) / 3) =
        δ ^ (1 : ℝ) * δ ^ (-(2 : ℝ) / 3) := by rw [Real.rpow_one]
    _ = δ ^ ((1 : ℝ) + -(2 : ℝ) / 3) := (Real.rpow_add hδ _ _).symm
    _ = δ ^ ((1 : ℝ) / 3) := by norm_num

private theorem noise_rpow_sq {δ : ℝ} (hδ : 0 < δ) :
    δ ^ (-(2 : ℝ) / 3) * (δ ^ ((1 : ℝ) / 3)) ^ 2 = 1 := by
  have hs : (δ ^ ((1 : ℝ) / 3)) ^ 2 = δ ^ ((2 : ℝ) / 3) := by
    rw [← Real.rpow_natCast, ← Real.rpow_mul hδ.le]
    norm_num
  rw [hs, ← Real.rpow_add hδ]
  norm_num

/-- Both ceiling bounds retain the full rounding factor. -/
theorem noiseSchedule_bounds {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    δ ^ (-(2 : ℝ) / 3) ≤ (noiseSchedule δ : ℝ) ∧
      (noiseSchedule δ : ℝ) ≤ 2 * δ ^ (-(2 : ℝ) / 3) := by
  have hu : 1 ≤ δ ^ (-(2 : ℝ) / 3) := by
    exact Real.one_le_rpow_of_pos_of_le_one_of_nonpos hδ hδ₁ (by norm_num)
  constructor
  · exact Nat.le_ceil _
  · have hc := Nat.ceil_lt_add_one (show 0 ≤ δ ^ (-(2 : ℝ) / 3) from
      (Real.rpow_pos_of_pos hδ _).le)
    dsimp [noiseSchedule]
    linarith

/-- The exact-data term after rounding. -/
theorem noiseSchedule_bias_bound {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    Real.sqrt (2 / (noiseSchedule δ : ℝ)) ≤
      Real.sqrt 2 * δ ^ ((1 : ℝ) / 3) := by
  have hm : 0 < (noiseSchedule δ : ℝ) := by exact_mod_cast noiseSchedule_pos hδ
  have hq : 0 < δ ^ ((1 : ℝ) / 3) := Real.rpow_pos_of_pos hδ _
  have hmul := mul_le_mul_of_nonneg_right (noiseSchedule_bounds hδ hδ₁).1
    (sq_nonneg (δ ^ ((1 : ℝ) / 3)))
  rw [noise_rpow_sq hδ] at hmul
  have hquot : 2 / (noiseSchedule δ : ℝ) ≤ 2 * (δ ^ ((1 : ℝ) / 3)) ^ 2 := by
    apply (div_le_iff₀ hm).2
    nlinarith
  have hleft := Real.sq_sqrt (show 0 ≤ 2 / (noiseSchedule δ : ℝ) by positivity)
  have hright : (Real.sqrt 2 * δ ^ ((1 : ℝ) / 3)) ^ 2 =
      2 * (δ ^ ((1 : ℝ) / 3)) ^ 2 := by
    rw [mul_pow, Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)]
  have hn := Real.sqrt_nonneg (2 / (noiseSchedule δ : ℝ))
  have hn' : 0 ≤ Real.sqrt 2 * δ ^ ((1 : ℝ) / 3) := by positivity
  apply (sq_le_sq₀ hn hn').mp
  rw [hleft, hright]
  exact hquot

/-- The propagated-noise term after rounding. -/
theorem noiseSchedule_noise_bound {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    δ * (noiseSchedule δ : ℝ) / 2 ≤ δ ^ ((1 : ℝ) / 3) := by
  have h := mul_le_mul_of_nonneg_left (noiseSchedule_bounds hδ hδ₁).2 hδ.le
  have he := noise_rpow_mul hδ
  nlinarith

/-- The scalar part of Corollary 30.3, with the literal ceiling schedule. -/
theorem noiseSchedule_rate {δ : ℝ} (hδ : 0 < δ) (hδ₁ : δ ≤ 1) :
    Real.sqrt (2 / (noiseSchedule δ : ℝ)) + δ * (noiseSchedule δ : ℝ) / 2 ≤
      (Real.sqrt 2 + 1) * δ ^ ((1 : ℝ) / 3) := by
  have hb := noiseSchedule_bias_bound hδ hδ₁
  have hn := noiseSchedule_noise_bound hδ hδ₁
  nlinarith

/-- The sharp universal noise estimate at the inverse-square parameter.
This lemma deliberately retains its exact-data bias hypothesis. -/
theorem noisy_error_of_bias_bound
    {H Y : Type*} [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r s : Y) (aMin : H) (m : ℕ) (hm : 1 ≤ m)
    {δ : ℝ} (hdata : ‖s - r‖ ≤ δ)
    (hα : 0 < ((m : ℝ) ^ 2)⁻¹)
    (hbias : ‖RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα r -
      aMin‖ ≤ Real.sqrt (2 / (m : ℝ))) :
    ‖RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα s - aMin‖ ≤
      Real.sqrt (2 / (m : ℝ)) + δ * (m : ℝ) / 2 := by
  have hmpos : 0 < (m : ℝ) := by exact_mod_cast (lt_of_lt_of_le Nat.zero_lt_one hm)
  have hsqrt : Real.sqrt (((m : ℝ) ^ 2)⁻¹) = (m : ℝ)⁻¹ := by
    rw [Real.sqrt_inv, Real.sqrt_sq hmpos.le]
  have hnoise := (RegularizedHilbertRepair.data_noise_bound T
    (((m : ℝ) ^ 2)⁻¹) hα s r).trans
      (div_le_div_of_nonneg_right hdata (by positivity))
  rw [hsqrt] at hnoise
  have hquot : δ / (2 * (m : ℝ)⁻¹) = δ * (m : ℝ) / 2 := by
    field_simp [ne_of_gt hmpos]
  rw [hquot] at hnoise
  have he : RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα s - aMin =
      (RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα s -
        RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα r) +
      (RegularizedHilbertRepair.correction T (((m : ℝ) ^ 2)⁻¹) hα r - aMin) := by
    abel
  rw [he]
  exact (norm_add_le _ _).trans ((add_le_add hnoise hbias).trans_eq (add_comm _ _))

/-- The ceiling schedule transfers an assumed exact-data bias bound to a noisy rate.
The concrete diagonal corollary additionally needs its proved bias identity. -/
theorem noisy_rounded_rate_of_bias_bound
    {H Y : Type*} [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r s : Y) (aMin : H) {δ : ℝ}
    (hδ : 0 < δ) (hδ₁ : δ ≤ 1) (hdata : ‖s - r‖ ≤ δ)
    (hα : 0 < ((noiseSchedule δ : ℝ) ^ 2)⁻¹)
    (hbias : ‖RegularizedHilbertRepair.correction T
      (((noiseSchedule δ : ℝ) ^ 2)⁻¹) hα r - aMin‖ ≤
        Real.sqrt (2 / (noiseSchedule δ : ℝ))) :
    ‖RegularizedHilbertRepair.correction T (((noiseSchedule δ : ℝ) ^ 2)⁻¹) hα s -
      aMin‖ ≤ (Real.sqrt 2 + 1) * δ ^ ((1 : ℝ) / 3) := by
  exact (noisy_error_of_bias_bound T r s aMin (noiseSchedule δ)
    (one_le_noiseSchedule hδ) hdata hα hbias).trans (noiseSchedule_rate hδ hδ₁)

end KomorebiSpace.DiagonalRegularization
