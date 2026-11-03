import CoupledTypeProportions
import Mathlib.Analysis.Complex.Trigonometric
import Mathlib.Analysis.SpecialFunctions.ExpDeriv

/-! # Exact scalar reduction and explicit symmetric coupled functions -/

set_option autoImplicit false
set_option maxHeartbeats 2000000

noncomputable section
open Filter Set
open scoped Topology Matrix

namespace Komorebi.SpecialFunctions.Coupled.Scales

def sameUnorderedRows (s : Scales) : Prop :=
  (s.q = s.a ∧ s.r = s.b) ∨ (s.q = s.b ∧ s.r = s.a)

theorem positive_pair_from_product_and_square_sum {q r a b : ℝ}
    (hq : 0 < q) (hr : 0 < r) (ha : 0 < a) (hb : 0 < b)
    (hp : q * r = a * b) (hsq : q ^ 2 + r ^ 2 = a ^ 2 + b ^ 2) :
    (q = a ∧ r = b) ∨ (q = b ∧ r = a) := by
  have hf : (q + r - (a + b)) * (q + r + (a + b)) = 0 := by
    nlinarith only [hp, hsq]
  have hsum : q + r = a + b := sub_eq_zero.mp
    ((mul_eq_zero.mp hf).resolve_right (ne_of_gt (by linarith only [hq, hr, ha, hb])))
  have hmul := congrArg (fun t : ℝ => q * t) hsum
  have hfactor : (q - a) * (q - b) = 0 := by nlinarith only [hp, hmul]
  rcases mul_eq_zero.mp hfactor with h | h
  · left
    have hqa := sub_eq_zero.mp h
    exact ⟨hqa, by linarith only [hsum, hqa]⟩
  · right
    have hqb := sub_eq_zero.mp h
    exact ⟨hqb, by linarith only [hsum, hqb]⟩

theorem equal_components_coefficients (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (he : s.U = s.V) (n : ℕ) : (s.coefficients n).1 = (s.coefficients n).2 := by
  have h := s.rescaling_coefficient_identity hs hstrict
    (A := (1 : ℂ)) (B := (1 : ℂ)) (by intro z; simpa using congrFun he.symm z) n
  have hh : ((s.coefficients n).2 : ℂ) = ((s.coefficients n).1 : ℂ) := by simpa using h
  exact (Complex.ofReal_inj.mp hh).symm

theorem equal_components_product (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (he : s.U = s.V) :
    s.p = s.k := by
  have h := s.equal_components_coefficients hs hstrict he 1
  simp only [coefficients_one, u1, v1] at h
  linarith only [h]

theorem equal_components_square_sum (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (he : s.U = s.V) :
    s.q ^ 2 + s.r ^ 2 = s.a ^ 2 + s.b ^ 2 := by
  have hp : 0 < s.p := mul_pos hs.1 hs.2.1
  have hpk := s.equal_components_product hs hstrict he
  have h := s.equal_components_coefficients hs hstrict he 2
  simp only [coefficients_two, u2, v2, ← hpk] at h
  have hh : s.p * (s.p * (s.q ^ 2 + s.r ^ 2)) =
      s.p * (s.p * (s.a ^ 2 + s.b ^ 2)) := by nlinarith only [h]
  exact mul_left_cancel₀ (ne_of_gt hp) (mul_left_cancel₀ (ne_of_gt hp) hh)

theorem equal_components_unordered_rows (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (he : s.U = s.V) :
    s.sameUnorderedRows :=
  positive_pair_from_product_and_square_sum hs.1 hs.2.1 hs.2.2.1 hs.2.2.2
    (s.equal_components_product hs hstrict he) (s.equal_components_square_sum hs hstrict he)

theorem scalar_pair_solution (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (hrows : s.sameUnorderedRows) :
    s.IsEntireSolution (scalarT s.q s.r) (scalarT s.q s.r) := by
  have hT := scalarT_solution hs.1 hs.2.1 hstrict.1 hstrict.2.1
  refine ⟨hT.1, hT.1, fun z => ⟨hT.2 z, ?_⟩⟩
  rcases hrows with h | h
  · simpa only [← h.1, ← h.2] using hT.2 z
  · simpa only [← h.1, ← h.2, mul_comm] using hT.2 z

theorem unordered_rows_scalar_representation (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (hrows : s.sameUnorderedRows) :
    s.U = scalarT s.q s.r ∧ s.V = scalarT s.q s.r := by
  have he := s.entire_solution_eq hs hstrict (s.scalar_pair_solution hs hstrict hrows)
  exact ⟨he.1.symm, he.2.symm⟩

theorem components_equal_iff_unordered_rows (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.U = s.V ↔ s.sameUnorderedRows := by
  refine ⟨s.equal_components_unordered_rows hs hstrict, ?_⟩
  intro hrows
  have he := s.unordered_rows_scalar_representation hs hstrict hrows
  exact he.1.trans he.2.symm

theorem components_equal_iff_scale_pair_set (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.U = s.V ↔ ({s.q, s.r} : Set ℝ) = {s.a, s.b} := by
  rw [s.components_equal_iff_unordered_rows hs hstrict, Set.pair_eq_pair_iff]
  rfl

theorem characteristicExponent_eq_of_balance (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {t : ℝ} (ht : 0 < t)
    (he : (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t) :
    s.characteristicExponent hs hstrict = t :=
  ((Classical.choose_spec (s.characteristic_exponent_exists_unique hs hstrict)).2 t ⟨ht, he⟩).symm

theorem scalar_characteristic_balance_iff (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (hrows : s.sameUnorderedRows)
    {t : ℝ} (ht : 0 < t) :
    (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t ↔ s.q ^ t + s.r ^ t = 1 := by
  rw [Real.mul_rpow hs.2.2.1.le hs.2.1.le]
  rcases hrows with h | h
  · rw [← h.1, ← h.2]
    constructor <;> intro he <;> nlinarith only [he]
  · rw [← h.1, ← h.2]
    have hq := (rpow_contraction_bounds hs.1 hstrict.1 ht).2
    have hr := Real.rpow_pos_of_pos hs.2.1 t
    constructor
    · intro he
      have hh : (1 - s.q ^ t - s.r ^ t) * (1 - s.q ^ t + s.r ^ t) = 0 := by
        nlinarith only [he]
      have hz := (mul_eq_zero.mp hh).resolve_right (ne_of_gt (by linarith only [hq, hr]))
      linarith only [hz]
    · intro he
      have hh : 1 - s.q ^ t = s.r ^ t := by linarith only [he]
      rw [hh]

theorem scalar_characteristic_order (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (hrows : s.sameUnorderedRows) :
    s.q ^ (s.characteristicExponent hs hstrict) +
      s.r ^ (s.characteristicExponent hs hstrict) = 1 :=
  (s.scalar_characteristic_balance_iff hs hstrict hrows
    (s.characteristicExponent_spec hs hstrict).1).mp
      (s.characteristicExponent_spec hs hstrict).2

theorem characteristic_order_invariant (s v : Scales) (hs : s.positive) (hv : v.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (vstrict : v.q < 1 ∧ v.r < 1 ∧ v.a < 1 ∧ v.b < 1)
    (hq : s.q = v.q) (hb : s.b = v.b) (hcross : s.a * s.r = v.a * v.r) :
    s.characteristicExponent hs hstrict = v.characteristicExponent hv vstrict := by
  have he := v.characteristicExponent_spec hv vstrict
  apply s.characteristicExponent_eq_of_balance hs hstrict he.1
  rw [hq, hb, hcross]
  exact he.2

theorem complex_sinh_hasDerivAt (z : ℂ) : HasDerivAt Complex.sinh (Complex.cosh z) z := by
  simp only [Complex.cosh, div_eq_mul_inv]
  convert!
    ((Complex.hasDerivAt_exp z).sub (hasDerivAt_id z).fun_neg.cexp).mul_const (2 : ℂ)⁻¹ using 1
  rw [id, mul_neg_one, sub_eq_add_neg, neg_neg]

theorem sinh_half_derivative_identity {c : ℂ} (hc : c ^ 2 = 2) (z : ℂ) :
    Complex.cosh (c⁻¹ * z) =
      1 + (c * Complex.sinh (c⁻¹ * ((1 / 2 : ℂ) * z))) *
        (c * Complex.sinh (c⁻¹ * ((1 / 2 : ℂ) * z))) := by
  let x := c⁻¹ * ((1 / 2 : ℂ) * z)
  have hx : 2 * x = c⁻¹ * z := by dsimp [x]; ring
  change Complex.cosh (c⁻¹ * z) = 1 + (c * Complex.sinh x) * (c * Complex.sinh x)
  calc
    _ = Complex.cosh x ^ 2 + Complex.sinh x ^ 2 := by rw [← hx, Complex.cosh_two_mul]
    _ = 1 + 2 * Complex.sinh x ^ 2 := by
      linear_combination Complex.cosh_sq_sub_sinh_sq x
    _ = 1 + (c * Complex.sinh x) * (c * Complex.sinh x) := by
      linear_combination -(Complex.sinh x ^ 2) * hc

theorem scaled_sinh_half_equation {c : ℂ} (hc : c ^ 2 = 2) (z : ℂ) :
    HasDerivAt (fun z : ℂ => c * Complex.sinh (c⁻¹ * z))
      (1 + (c * Complex.sinh (c⁻¹ * ((1 / 2 : ℂ) * z))) *
        (c * Complex.sinh (c⁻¹ * ((1 / 2 : ℂ) * z)))) z := by
  have hc0 : c ≠ 0 := by intro hz; simp [hz] at hc
  have hd := ((complex_sinh_hasDerivAt (c⁻¹ * z)).comp z
    ((hasDerivAt_id z).const_mul c⁻¹)).const_mul c
  convert! hd using 1
  rw [← sinh_half_derivative_identity hc z]
  field_simp [hc0]

def halfScales : Scales := ⟨1 / 2, 1 / 2, 1 / 2, 1 / 2⟩

theorem halfScales_positive : halfScales.positive := by norm_num [positive, halfScales]

theorem halfScales_strict :
    halfScales.q < 1 ∧ halfScales.r < 1 ∧ halfScales.a < 1 ∧ halfScales.b < 1 := by
  norm_num [halfScales]

theorem scaled_sinh_half_solution {c : ℂ} (hc : c ^ 2 = 2) :
    halfScales.IsEntireSolution (fun z : ℂ => c * Complex.sinh (c⁻¹ * z))
      (fun z : ℂ => c * Complex.sinh (c⁻¹ * z)) := by
  refine ⟨by simp, by simp, fun z => ?_⟩
  have hh := scaled_sinh_half_equation hc z
  exact ⟨by simpa [halfScales] using hh, by simpa [halfScales] using hh⟩

theorem sqrt_two_complex_square : ((Real.sqrt 2 : ℝ) : ℂ) ^ 2 = 2 := by
  exact_mod_cast Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)

theorem canonical_half_sinh (z : ℂ) :
    halfScales.U z = (Real.sqrt 2 : ℂ) * Complex.sinh (z / (Real.sqrt 2 : ℂ)) ∧
    halfScales.V z = (Real.sqrt 2 : ℂ) * Complex.sinh (z / (Real.sqrt 2 : ℂ)) := by
  have he := halfScales.entire_solution_eq halfScales_positive halfScales_strict
    (scaled_sinh_half_solution sqrt_two_complex_square)
  exact ⟨by simpa only [div_eq_inv_mul] using congrFun he.1.symm z,
    by simpa only [div_eq_inv_mul] using congrFun he.2.symm z⟩

theorem half_characteristic_order :
    halfScales.characteristicExponent halfScales_positive halfScales_strict = 1 := by
  apply halfScales.characteristicExponent_eq_of_balance halfScales_positive halfScales_strict
    (by norm_num : (0 : ℝ) < 1)
  norm_num [halfScales]

theorem half_radial_order (i : Fin 2) : halfScales.radialOrder i = 1 := by
  rw [halfScales.canonical_radial_order halfScales_positive halfScales_strict, half_characteristic_order]

def unequalScales : Scales := ⟨1 / 5, 2 / 5, 3 / 5, 7 / 10⟩

theorem unequalScales_positive : unequalScales.positive := by norm_num [positive, unequalScales]

theorem unequalScales_strict :
    unequalScales.q < 1 ∧ unequalScales.r < 1 ∧ unequalScales.a < 1 ∧ unequalScales.b < 1 := by
  norm_num [unequalScales]

theorem unequal_characteristic_order :
    unequalScales.characteristicExponent unequalScales_positive unequalScales_strict = 1 := by
  apply unequalScales.characteristicExponent_eq_of_balance unequalScales_positive unequalScales_strict
    (by norm_num : (0 : ℝ) < 1)
  norm_num [unequalScales]

theorem unequal_radial_order (i : Fin 2) : unequalScales.radialOrder i = 1 := by
  rw [unequalScales.canonical_radial_order unequalScales_positive unequalScales_strict,
    unequal_characteristic_order]

theorem unequal_normalized_vector :
    unequalScales.normalizedCharacteristicVector
      (unequalScales.characteristicExponent unequalScales_positive unequalScales_strict) = ![1 / 2, 1] := by
  rw [unequal_characteristic_order]
  funext i
  fin_cases i <;> norm_num [normalizedCharacteristicVector, characteristicNormalizer,
    characteristicVector, unequalScales]

theorem unequal_type_proportions :
    unequalScales.lowerType unequalScales_positive unequalScales_strict 1 =
      2 * unequalScales.lowerType unequalScales_positive unequalScales_strict 0 ∧
    unequalScales.upperType unequalScales_positive unequalScales_strict 1 =
      2 * unequalScales.upperType unequalScales_positive unequalScales_strict 0 := by
  have hh := unequalScales.canonical_type_proportions unequalScales_positive unequalScales_strict
  rw [unequal_normalized_vector] at hh
  have hl0 := congrFun hh.2.2.1 0
  have hl1 := congrFun hh.2.2.1 1
  have hu0 := congrFun hh.2.2.2 0
  have hu1 := congrFun hh.2.2.2 1
  simp only [Pi.smul_apply, smul_eq_mul, Matrix.cons_val_zero, Matrix.cons_val_one,
    Matrix.cons_val_fin_one, mul_one] at hl0 hl1 hu0 hu1
  constructor <;> linarith only [hl0, hl1, hu0, hu1]

theorem unequal_components_different : unequalScales.U ≠ unequalScales.V := by
  intro he
  have hh := (unequalScales.components_equal_iff_unordered_rows
    unequalScales_positive unequalScales_strict).mp he
  norm_num [sameUnorderedRows, unequalScales] at hh

theorem unequal_coefficients_through_seven :
    unequalScales.coefficients 0 = (1, 1) ∧
    unequalScales.coefficients 1 = (2 / 75, 7 / 50) ∧
    unequalScales.coefficients 2 = (88 / 234375, 8211 / 1250000) ∧
    unequalScales.coefficients 3 = (18814 / 8544921875, 85664601 / 625000000000) := by
  norm_num [coefficients_zero, coefficients_one, coefficients_two, coefficients_three,
    u1, v1, u2, v2, u3, v3, p, k, unequalScales]

theorem unequal_row_sums :
    unequalScales.q + unequalScales.r = 3 / 5 ∧
    unequalScales.a + unequalScales.b = 13 / 10 ∧
    (unequalScales.q + unequalScales.r + unequalScales.a + unequalScales.b) / 2 = 19 / 20 := by
  norm_num [unequalScales]

theorem unequal_lower_constants :
    unequalScales.minScale = 1 / 5 ∧ unequalScales.maxScale = 7 / 10 ∧
    unequalScales.lowerThreshold = 11 ∧ unequalScales.lowerShift = 7 / 3 ∧
    unequalScales.lowerPowerConstant 1 = 3 * Real.log 2 / 40 := by
  norm_num [minScale, maxScale, lowerThreshold, lowerShift, lowerPowerConstant, unequalScales]
  ring

theorem unequal_explicit_lower_growth {R : ℝ} (hR : 2 ≤ R) :
    3 * Real.log 2 / 80 * (R + 7 / 3) ≤ Real.log (unequalScales.UReal R) ∧
    3 * Real.log 2 / 40 * (R + 7 / 3) ≤ Real.log (unequalScales.VReal R) := by
  have hh := unequalScales.canonical_lower_log_power unequalScales_positive unequalScales_strict hR
  change unequalScales.lowerPowerConstant _ * _ * _ ≤ _ ∧
    unequalScales.lowerPowerConstant _ * _ * _ ≤ _ at hh
  rw [unequal_normalized_vector, unequal_characteristic_order] at hh
  rw [unequal_lower_constants.2.2.2.1, unequal_lower_constants.2.2.2.2] at hh
  norm_num at hh
  ring_nf at hh ⊢
  exact hh

def surfaceCrossScale (q r b t : ℝ) : ℝ :=
  ((1 - q ^ t) * (1 - b ^ t)) ^ (1 / t) / r

theorem surface_cross_scale_contract {q r b t : ℝ}
    (hq : 0 < q) (hr : 0 < r) (hb : 0 < b) (hq1 : q < 1) (hb1 : b < 1)
    (ht : 0 < t) (hbudget : (1 - q ^ t) * (1 - b ^ t) < r ^ t) :
    0 < surfaceCrossScale q r b t ∧ surfaceCrossScale q r b t < 1 ∧
      (surfaceCrossScale q r b t * r) ^ t = (1 - q ^ t) * (1 - b ^ t) := by
  let d := (1 - q ^ t) * (1 - b ^ t)
  have hd : 0 < d := mul_pos (sub_pos.mpr (rpow_contraction_bounds hq hq1 ht).2)
    (sub_pos.mpr (rpow_contraction_bounds hb hb1 ht).2)
  have hroot : 0 < d ^ (1 / t) := Real.rpow_pos_of_pos hd _
  have hlt := Real.rpow_lt_rpow hd.le hbudget (one_div_pos.mpr ht)
  rw [one_div, Real.rpow_rpow_inv hr.le (ne_of_gt ht)] at hlt
  have hcancel : (d ^ (1 / t)) ^ t = d := by
    rw [one_div, Real.rpow_inv_rpow hd.le (ne_of_gt ht)]
  refine ⟨div_pos hroot hr, ?_, ?_⟩
  · change d ^ (1 / t) / r < 1
    exact (div_lt_one hr).mpr (by simpa only [one_div] using hlt)
  · change (d ^ (1 / t) / r * r) ^ t = d
    rw [div_mul_cancel₀ _ (ne_of_gt hr)]
    exact hcancel

def orderSurfaceScales (q r b t : ℝ) : Scales := ⟨q, r, surfaceCrossScale q r b t, b⟩

theorem order_surface_realization {q r b t : ℝ}
    (hq : 0 < q) (hr : 0 < r) (hb : 0 < b)
    (hq1 : q < 1) (hr1 : r < 1) (hb1 : b < 1) (ht : 0 < t)
    (hbudget : (1 - q ^ t) * (1 - b ^ t) < r ^ t) :
    ∃ hs : (orderSurfaceScales q r b t).positive,
      ∃ hc : (orderSurfaceScales q r b t).q < 1 ∧ (orderSurfaceScales q r b t).r < 1 ∧
        (orderSurfaceScales q r b t).a < 1 ∧ (orderSurfaceScales q r b t).b < 1,
      (orderSurfaceScales q r b t).characteristicExponent hs hc = t ∧
        ∀ i : Fin 2, (orderSurfaceScales q r b t).radialOrder i = t := by
  have ha := surface_cross_scale_contract hq hr hb hq1 hb1 ht hbudget
  have hs : (orderSurfaceScales q r b t).positive := ⟨hq, hr, ha.1, hb⟩
  have hc : (orderSurfaceScales q r b t).q < 1 ∧ (orderSurfaceScales q r b t).r < 1 ∧
      (orderSurfaceScales q r b t).a < 1 ∧ (orderSurfaceScales q r b t).b < 1 :=
    ⟨hq1, hr1, ha.2.1, hb1⟩
  have he : (orderSurfaceScales q r b t).characteristicExponent hs hc = t :=
    (orderSurfaceScales q r b t).characteristicExponent_eq_of_balance hs hc ht ha.2.2.symm
  refine ⟨hs, hc, he, fun i => ?_⟩
  rw [(orderSurfaceScales q r b t).canonical_radial_order hs hc, he]

def componentCoefficient (s : Scales) (i : Fin 2) (n : ℕ) : ℝ :=
  ![(s.coefficients n).1, (s.coefficients n).2] i

theorem component_oddSum (s : Scales) (i : Fin 2) (z : ℂ) :
    s.complexComponent i z = oddSum (s.componentCoefficient i) z := by
  fin_cases i <;> rfl

theorem component_coefficient_majorant (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) (n : ℕ) :
    0 ≤ s.componentCoefficient i n ∧ s.componentCoefficient i n ≤ (1 / 2 : ℝ) ^ n := by
  have hp := s.coefficients_positive hs n
  have hb := s.coefficients_le_geometric hs
    ⟨hstrict.1.le, hstrict.2.1.le, hstrict.2.2.1.le, hstrict.2.2.2.le⟩ n
  fin_cases i
  · exact ⟨hp.1.le, hb.1⟩
  · exact ⟨hp.2.le, hb.2⟩

theorem oddSum_truncation_eq_tail {c : ℕ → ℝ} {z : ℂ}
    (hc : Summable (fun n => (c n : ℂ) * z ^ (2 * n + 1))) (N : ℕ) :
    oddSum c z - ∑ n ∈ Finset.range N, (c n : ℂ) * z ^ (2 * n + 1) =
      ∑' n, (c (n + N) : ℂ) * z ^ (2 * (n + N) + 1) := by
  have hh := hc.sum_add_tsum_nat_add N
  dsimp [oddSum]
  rw [← hh]
  ring

theorem canonical_complex_truncation_bound (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    (z : ℂ) (hz : ‖z‖ ^ 2 < 2) (N : ℕ) :
    ‖s.complexComponent i z -
      ∑ n ∈ Finset.range N, (s.componentCoefficient i n : ℂ) * z ^ (2 * n + 1)‖ ≤
        ‖z‖ * (‖z‖ ^ 2 / 2) ^ N / (1 - ‖z‖ ^ 2 / 2) := by
  have hc := s.component_coefficient_majorant hs hstrict i
  have hsum := odd_series_summable hc z hz
  rw [s.component_oddSum i z, oddSum_truncation_eq_tail hsum N]
  exact odd_series_tail_bound hc z hz N

theorem canonical_four_term_remainder (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    (z : ℂ) (hz : ‖z‖ ≤ 1) :
    ‖s.complexComponent i z -
      ∑ n ∈ Finset.range 4, (s.componentCoefficient i n : ℂ) * z ^ (2 * n + 1)‖ ≤
        ‖z‖ ^ 9 / 8 := by
  have hn := norm_nonneg z
  have hsq : ‖z‖ ^ 2 ≤ 1 := by nlinarith only [hn, hz]
  have hh := s.canonical_complex_truncation_bound hs hstrict i z (by linarith only [hsq]) 4
  apply hh.trans
  have hd : 0 < 1 - ‖z‖ ^ 2 / 2 := by linarith only [hsq]
  apply (div_le_iff₀ hd).mpr
  have hbound : 0 ≤ ‖z‖ ^ 9 * (1 - ‖z‖ ^ 2) :=
    mul_nonneg (pow_nonneg hn _) (sub_nonneg.mpr hsq)
  nlinarith only [hbound]

theorem unequal_degree_seven_polynomials (z : ℂ) :
    (∑ n ∈ Finset.range 4, (unequalScales.componentCoefficient 0 n : ℂ) * z ^ (2 * n + 1)) =
      z + (2 / 75 : ℂ) * z ^ 3 + (88 / 234375 : ℂ) * z ^ 5 +
        (18814 / 8544921875 : ℂ) * z ^ 7 ∧
    (∑ n ∈ Finset.range 4, (unequalScales.componentCoefficient 1 n : ℂ) * z ^ (2 * n + 1)) =
      z + (7 / 50 : ℂ) * z ^ 3 + (8211 / 1250000 : ℂ) * z ^ 5 +
        (85664601 / 625000000000 : ℂ) * z ^ 7 := by
  constructor <;>
    norm_num [Finset.sum_range_succ, componentCoefficient, coefficients_zero, coefficients_one,
      coefficients_two, coefficients_three, u1, v1, u2, v2, u3, v3, p, k, unequalScales]

theorem unequal_degree_seven_error (z : ℂ) (hz : ‖z‖ ≤ 1) :
    ‖unequalScales.U z - (z + (2 / 75 : ℂ) * z ^ 3 + (88 / 234375 : ℂ) * z ^ 5 +
      (18814 / 8544921875 : ℂ) * z ^ 7)‖ ≤ ‖z‖ ^ 9 / 8 ∧
    ‖unequalScales.V z - (z + (7 / 50 : ℂ) * z ^ 3 + (8211 / 1250000 : ℂ) * z ^ 5 +
      (85664601 / 625000000000 : ℂ) * z ^ 7)‖ ≤ ‖z‖ ^ 9 / 8 := by
  have h0 := unequalScales.canonical_four_term_remainder unequalScales_positive unequalScales_strict 0 z hz
  have h1 := unequalScales.canonical_four_term_remainder unequalScales_positive unequalScales_strict 1 z hz
  rw [(unequal_degree_seven_polynomials z).1] at h0
  rw [(unequal_degree_seven_polynomials z).2] at h1
  exact ⟨h0, h1⟩

end Komorebi.SpecialFunctions.Coupled.Scales
