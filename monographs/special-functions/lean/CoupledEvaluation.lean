import CoupledOperator

/-! # Arbitrary-radius disk and Taylor evaluation certificates -/

set_option autoImplicit false
set_option maxHeartbeats 2500000

noncomputable section
open Filter Set
open scoped Topology Matrix

namespace Komorebi.SpecialFunctions.Coupled.Scales

theorem component_real_hasSum (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) (R : ℝ) :
    HasSum (fun n => s.componentCoefficient i n * R ^ (2*n+1)) (s.realComponent i R) := by
  have h := s.real_series_hasSum hs hc R
  fin_cases i
  · exact h.1
  · exact h.2

theorem component_norm_summable (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) (z : ℂ) :
    Summable (fun n => ‖(s.componentCoefficient i n : ℂ) * z ^ (2*n+1)‖) := by
  have h := s.coefficient_series_entire hs hc z
  fin_cases i
  · exact h.1
  · exact h.2

theorem component_real_nonneg (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) {R : ℝ}
    (hR : 0 ≤ R) : 0 ≤ s.realComponent i R := by
  have h := s.real_axis_nonneg hs hc hR
  fin_cases i
  · exact h.1
  · exact h.2

theorem component_real_mono (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R S : ℝ} (hR : 0 ≤ R) (hRS : R ≤ S) : s.realComponent i R ≤ s.realComponent i S := by
  have h := s.real_axis_strictMono hs hc
  fin_cases i
  · exact h.1.monotoneOn hR (hR.trans hRS) hRS
  · exact h.2.monotoneOn hR (hR.trans hRS) hRS

theorem component_at_real (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) (x : ℝ) :
    s.complexComponent i (x : ℂ) = (s.realComponent i x : ℂ) := by
  have h := s.real_axis_identification hs hc x
  fin_cases i
  · exact h.1
  · exact h.2

def realPairMax (s : Scales) (R : ℝ) : ℝ := max (s.UReal R) (s.VReal R)

theorem component_le_pairMax (s : Scales) (i : Fin 2) (R : ℝ) :
    s.realComponent i R ≤ s.realPairMax R := by
  fin_cases i
  · exact le_max_left _ _
  · exact le_max_right _ _

theorem realPairMax_nonneg (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 0 ≤ R) :
    0 ≤ s.realPairMax R :=
  (s.real_axis_nonneg hs hc hR).1.trans (le_max_left _ _)

theorem realPairMax_recurrence (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 0 ≤ R) :
    s.realPairMax R ≤ R * (1 + s.realPairMax (s.maxScale * R) ^ 2) := by
  have harg {p : ℝ} (hp : 0 ≤ p) (hpQ : p ≤ s.maxScale) (i : Fin 2) :
      s.realComponent i (p * R) ≤ s.realPairMax (s.maxScale * R) :=
    (s.component_real_mono hs hc i (mul_nonneg hp hR)
      (mul_le_mul_of_nonneg_right hpQ hR)).trans (s.component_le_pairMax i _)
  have hq := harg hs.1.le s.maxScale_bounds.1 0
  have hr := harg hs.2.1.le s.maxScale_bounds.2.1 1
  have ha := harg hs.2.2.1.le s.maxScale_bounds.2.2.1 0
  have hb := harg hs.2.2.2.le s.maxScale_bounds.2.2.2 1
  have hM := s.realPairMax_nonneg hs hc (mul_nonneg (s.maxScale_positive hs).le hR)
  have hvr := (s.real_axis_nonneg hs hc (mul_nonneg hs.2.1.le hR)).2
  have hvb := (s.real_axis_nonneg hs hc (mul_nonneg hs.2.2.2.le hR)).2
  have hU : s.UReal (s.q * R) * s.VReal (s.r * R) ≤ s.realPairMax (s.maxScale * R)^2 := by
    simpa only [realComponent, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
      pow_two] using mul_le_mul hq hr hvr hM
  have hV : s.UReal (s.a * R) * s.VReal (s.b * R) ≤ s.realPairMax (s.maxScale * R)^2 := by
    simpa only [realComponent, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons,
      pow_two] using mul_le_mul ha hb hvb hM
  have hf := s.real_axis_full_upper hs hc hR
  exact max_le (hf.1.trans (mul_le_mul_of_nonneg_left (add_le_add le_rfl hU) hR))
    (hf.2.trans (mul_le_mul_of_nonneg_left (add_le_add le_rfl hV) hR))

theorem component_coefficient_le_one (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) (n : ℕ) :
    s.componentCoefficient i n ≤ 1 := by
  apply (s.component_coefficient_majorant hs hc i n).2.trans
  exact pow_le_one₀ (by norm_num) (by norm_num)

theorem component_small_disk_bound (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R : ℝ} (hR : 0 ≤ R) (hR1 : R < 1) : s.realComponent i R ≤ R / (1 - R^2) := by
  have hg : HasSum (fun n : ℕ => R * (R^2)^n) (R / (1-R^2)) := by
    simpa only [div_eq_mul_inv] using
      (hasSum_geometric_of_lt_one (sq_nonneg R) (by nlinarith only [hR, hR1])).mul_left R
  apply hasSum_le _ (s.component_real_hasSum hs hc i R) hg
  intro n
  calc
    _ ≤ 1 * R^(2*n+1) := mul_le_mul_of_nonneg_right
      (s.component_coefficient_le_one hs hc i n) (pow_nonneg hR _)
    _ = R * (R^2)^n := by ring

theorem pair_small_disk_bound (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {R : ℝ} (hR : 0 ≤ R) (hR1 : R < 1) : s.realPairMax R ≤ R / (1-R^2) :=
  max_le (s.component_small_disk_bound hs hc 0 hR hR1)
    (s.component_small_disk_bound hs hc 1 hR hR1)

def diskMajorant (Q : ℝ) : ℕ → ℝ → ℝ
  | 0, R => R / (1-R^2)
  | n+1, R => if R < 1 then R / (1-R^2) else R * (1 + diskMajorant Q n (Q*R)^2)

theorem diskMajorant_of_small (Q : ℝ) (n : ℕ) {R : ℝ} (hR : R < 1) :
    diskMajorant Q n R = R / (1-R^2) := by cases n <;> simp [diskMajorant, hR]

theorem pair_le_diskMajorant (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (n : ℕ)
    {R : ℝ} (hR : 0 ≤ R) (ht : s.maxScale^n * R < 1) :
    s.realPairMax R ≤ diskMajorant s.maxScale n R := by
  induction n generalizing R with
  | zero => exact s.pair_small_disk_bound hs hc hR (by simpa using ht)
  | succ n ih =>
    by_cases hsmall : R < 1
    · rw [diskMajorant_of_small _ _ hsmall]
      exact s.pair_small_disk_bound hs hc hR hsmall
    · simp only [diskMajorant, ite_eq_right hsmall]
      have hQR := mul_nonneg (s.maxScale_positive hs).le hR
      have ht' : s.maxScale^n * (s.maxScale*R) < 1 := by
        convert ht using 1
        ring
      have hh := ih hQR ht'
      have hp := s.realPairMax_nonneg hs hc hQR
      exact (s.realPairMax_recurrence hs hc hR).trans
        (mul_le_mul_of_nonneg_left
          (add_le_add le_rfl (pow_le_pow_left₀ hp hh 2)) hR)

theorem exists_diskMajorant_fuel (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (R : ℝ) :
    ∃ n : ℕ, s.maxScale^n * R < 1 := by
  have ht : Tendsto (fun n : ℕ => s.maxScale^n * R) atTop (𝓝 0) := by
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one (s.maxScale_positive hs).le
      (s.maxScale_lt_one hc)).mul_const R
  exact (ht.eventually_lt_const (by norm_num : (0 : ℝ) < 1)).exists

theorem component_disk_majorant (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R : ℝ} (hR : 0 ≤ R) (n : ℕ) (ht : s.maxScale^n * R < 1)
    {z : ℂ} (hz : ‖z‖ ≤ R) : ‖s.complexComponent i z‖ ≤ diskMajorant s.maxScale n R := by
  have h := s.complex_norm_le_real_axis hs hc hz
  have hh : ‖s.complexComponent i z‖ ≤ s.realComponent i R := by
    fin_cases i
    · exact h.1
    · exact h.2
  exact hh.trans ((s.component_le_pairMax i R).trans (s.pair_le_diskMajorant hs hc n hR ht))

theorem disk_majorant_exists (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 0 ≤ R) :
    ∃ n : ℕ, s.maxScale^n * R < 1 ∧ ∀ i : Fin 2, ∀ z : ℂ, ‖z‖ ≤ R →
      ‖s.complexComponent i z‖ ≤ diskMajorant s.maxScale n R := by
  obtain ⟨n, hn⟩ := s.exists_diskMajorant_fuel hs hc R
  exact ⟨n, hn, fun i _ hz => s.component_disk_majorant hs hc i hR n hn hz⟩

theorem outer_power_comparison {R S : ℝ} (hR : 0 ≤ R) (hRS : R < S)
    {k m : ℕ} (hkm : k ≤ m) : R^m ≤ (R/S)^k * S^m := by
  have hS : 0 < S := hR.trans_lt hRS
  have hb0 := div_nonneg hR hS.le
  have hb1 : R/S ≤ 1 := (div_le_one hS).mpr hRS.le
  have hp := pow_le_pow_of_le_one hb0 hb1 hkm
  calc
    _ = ((R/S)*S)^m := by rw [div_mul_cancel₀ _ (ne_of_gt hS)]
    _ = (R/S)^m * S^m := mul_pow _ _ _
    _ ≤ _ := mul_le_mul_of_nonneg_right hp (pow_nonneg hS.le _)

theorem positive_odd_outer_remainder {c : ℕ → ℝ} (hc : ∀ n, 0 ≤ c n)
    {z : ℂ} {R S F : ℝ} (hR : 0 ≤ R) (hRS : R < S) (hz : ‖z‖ ≤ R)
    (hZ : Summable (fun n => (c n : ℂ) * z^(2*n+1)))
    (hS : HasSum (fun n => c n * S^(2*n+1)) F) (N : ℕ) :
    ‖oddSum c z - ∑ n ∈ Finset.range (N+1), (c n : ℂ)*z^(2*n+1)‖ ≤
      F * (R/S)^(2*N+3) := by
  rw [oddSum_truncation_eq_tail hZ (N+1)]
  have hS0 : 0 ≤ S := (hR.trans hRS.le)
  have hfac : 0 ≤ (R/S)^(2*N+3) := pow_nonneg (div_nonneg hR hS0) _
  have hTS : Summable (fun n => c (n+(N+1)) * S^(2*(n+(N+1))+1)) :=
    (summable_nat_add_iff (N+1)).mpr hS.summable
  have hTZ : Summable (fun n => (c (n+(N+1)) : ℂ) * z^(2*(n+(N+1))+1)) :=
    (summable_nat_add_iff (N+1)).mpr hZ
  have hterm (n : ℕ) : ‖(c (n+(N+1)) : ℂ) * z^(2*(n+(N+1))+1)‖ ≤
      (R/S)^(2*N+3) * (c (n+(N+1)) * S^(2*(n+(N+1))+1)) := by
    rw [norm_mul, Complex.norm_of_nonneg (hc _), norm_pow]
    calc
      _ ≤ c (n+(N+1)) * R^(2*(n+(N+1))+1) :=
        mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (norm_nonneg z) hz _) (hc _)
      _ ≤ c (n+(N+1)) * ((R/S)^(2*N+3) * S^(2*(n+(N+1))+1)) :=
        mul_le_mul_of_nonneg_left (outer_power_comparison hR hRS (by omega)) (hc _)
      _ = _ := by ring
  have hn := hTZ.hasSum.norm_le_of_bounded (hTS.hasSum.mul_left ((R/S)^(2*N+3))) hterm
  have hsplit := hS.summable.sum_add_tsum_nat_add (N+1)
  have hprefix : 0 ≤ ∑ n ∈ Finset.range (N+1), c n * S^(2*n+1) :=
    Finset.sum_nonneg (fun n _ => mul_nonneg (hc n) (pow_nonneg hS0 _))
  have ht : (∑' n, c (n+(N+1)) * S^(2*(n+(N+1))+1)) ≤ F := by
    rw [hS.tsum_eq] at hsplit
    linarith only [hsplit, hprefix]
  exact hn.trans (by simpa only [mul_comm] using mul_le_mul_of_nonneg_left ht hfac)

def oddPolynomial (s : Scales) (i : Fin 2) (N : ℕ) (z : ℂ) : ℂ :=
  ∑ n ∈ Finset.range (N+1), (s.componentCoefficient i n : ℂ)*z^(2*n+1)

def realOddPolynomial (s : Scales) (i : Fin 2) (N : ℕ) (x : ℝ) : ℝ :=
  ∑ n ∈ Finset.range (N+1), s.componentCoefficient i n * x^(2*n+1)

theorem oddPolynomial_at_real (s : Scales) (i : Fin 2) (N : ℕ) (x : ℝ) :
    s.oddPolynomial i N (x : ℂ) = (s.realOddPolynomial i N x : ℂ) := by
  simp only [oddPolynomial, realOddPolynomial, Complex.ofReal_sum, Complex.ofReal_mul,
    Complex.ofReal_pow]

theorem canonical_outer_remainder (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R S B : ℝ} (hR : 0 ≤ R) (hRS : R < S) (hB : s.realComponent i S ≤ B)
    (N : ℕ) {z : ℂ} (hz : ‖z‖ ≤ R) :
    ‖s.complexComponent i z - s.oddPolynomial i N z‖ ≤ B * (R/S)^(2*N+3) := by
  rw [s.component_oddSum i z]
  have h := positive_odd_outer_remainder
    (fun n => (s.component_coefficient_majorant hs hc i n).1) hR hRS hz
    (s.component_norm_summable hs hc i z).of_norm (s.component_real_hasSum hs hc i S) N
  exact h.trans (mul_le_mul_of_nonneg_right hB (pow_nonneg (div_nonneg hR (hR.trans hRS.le)) _))

theorem canonical_ladder_remainder (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R S : ℝ} (hR : 0 ≤ R) (hRS : R < S) (fuel : ℕ)
    (ht : s.maxScale^fuel * S < 1) (N : ℕ) {z : ℂ} (hz : ‖z‖ ≤ R) :
    ‖s.complexComponent i z - s.oddPolynomial i N z‖ ≤
      diskMajorant s.maxScale fuel S * (R/S)^(2*N+3) :=
  s.canonical_outer_remainder hs hc i hR hRS
    ((s.component_le_pairMax i S).trans (s.pair_le_diskMajorant hs hc fuel (hR.trans hRS.le) ht)) N hz

theorem real_polynomial_le_component (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {x : ℝ} (hx : 0 ≤ x) (N : ℕ) : s.realOddPolynomial i N x ≤ s.realComponent i x := by
  exact sum_le_hasSum (Finset.range (N+1))
    (fun n _ => mul_nonneg (s.component_coefficient_majorant hs hc i n).1 (pow_nonneg hx _))
    (s.component_real_hasSum hs hc i x)

theorem real_evaluation_enclosure (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {x S B : ℝ} (hx : 0 ≤ x) (hxS : x < S) (hB : s.realComponent i S ≤ B) (N : ℕ) :
    s.realOddPolynomial i N x ≤ s.realComponent i x ∧
      s.realComponent i x ≤ s.realOddPolynomial i N x + B*(x/S)^(2*N+3) := by
  refine ⟨s.real_polynomial_le_component hs hc i hx N, ?_⟩
  have he := s.canonical_outer_remainder hs hc i hx hxS hB N
    (z := (x : ℂ)) (by rw [Complex.norm_of_nonneg hx])
  rw [s.component_at_real hs hc i x, s.oddPolynomial_at_real i N x,
    ← Complex.ofReal_sub] at he
  have hh : s.realComponent i x - s.realOddPolynomial i N x ≤ B*(x/S)^(2*N+3) :=
    (le_abs_self _).trans (by simpa only [Complex.norm_real, Real.norm_eq_abs] using he)
  linarith only [hh]

theorem real_ladder_enclosure (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {x S : ℝ} (hx : 0 ≤ x) (hxS : x < S) (fuel : ℕ)
    (ht : s.maxScale^fuel * S < 1) (N : ℕ) :
    s.realOddPolynomial i N x ≤ s.realComponent i x ∧
      s.realComponent i x ≤ s.realOddPolynomial i N x +
        diskMajorant s.maxScale fuel S * (x/S)^(2*N+3) :=
  s.real_evaluation_enclosure hs hc i hx hxS
    ((s.component_le_pairMax i S).trans (s.pair_le_diskMajorant hs hc fuel (hx.trans hxS.le) ht)) N

def rationalDiskMajorant (Q : ℚ) : ℕ → ℚ → ℚ
  | 0, R => R / (1-R^2)
  | n+1, R => if R < 1 then R / (1-R^2) else R * (1 + rationalDiskMajorant Q n (Q*R)^2)

theorem rationalDiskMajorant_cast (Q : ℚ) (fuel : ℕ) (R : ℚ) :
    (rationalDiskMajorant Q fuel R : ℝ) = diskMajorant (Q : ℝ) fuel (R : ℝ) := by
  induction fuel generalizing R with
  | zero => simp only [rationalDiskMajorant, diskMajorant, Rat.cast_div, Rat.cast_sub,
      Rat.cast_one, Rat.cast_pow]
  | succ n ih =>
    by_cases hR : R < 1
    · have hRR : (R : ℝ) < 1 := by exact_mod_cast hR
      simp only [rationalDiskMajorant, diskMajorant, ite_eq_left hR, ite_eq_left hRR,
        Rat.cast_div, Rat.cast_sub, Rat.cast_one, Rat.cast_pow]
    · have hRR : ¬(R : ℝ) < 1 := by exact_mod_cast hR
      simp only [rationalDiskMajorant, diskMajorant, ite_eq_right hR, ite_eq_right hRR,
        Rat.cast_mul, Rat.cast_add, Rat.cast_one, Rat.cast_pow, ih]

theorem rational_disk_majorant_sound (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (Q R : ℚ)
    (hQ : (Q : ℝ) = s.maxScale) (hR : 0 ≤ R) (fuel : ℕ) (ht : Q^fuel * R < 1)
    (i : Fin 2) {z : ℂ} (hz : ‖z‖ ≤ (R : ℝ)) :
    ‖s.complexComponent i z‖ ≤ (rationalDiskMajorant Q fuel R : ℝ) := by
  rw [rationalDiskMajorant_cast, hQ]
  exact s.component_disk_majorant hs hc i (by exact_mod_cast hR) fuel
    (by rw [← hQ]; exact_mod_cast ht) hz

theorem rational_outer_remainder (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (Q R S : ℚ)
    (hQ : (Q : ℝ) = s.maxScale) (hR : 0 ≤ R) (hRS : R < S)
    (fuel : ℕ) (ht : Q^fuel * S < 1) (N : ℕ) (i : Fin 2)
    {z : ℂ} (hz : ‖z‖ ≤ (R : ℝ)) :
    ‖s.complexComponent i z - s.oddPolynomial i N z‖ ≤
      ((rationalDiskMajorant Q fuel S * (R/S)^(2*N+3) : ℚ) : ℝ) := by
  have h := s.canonical_ladder_remainder hs hc i
    (by exact_mod_cast hR : (0 : ℝ) ≤ R) (by exact_mod_cast hRS : (R : ℝ) < S)
    fuel (by rw [← hQ]; exact_mod_cast ht) N hz
  simpa only [Rat.cast_mul, Rat.cast_pow, Rat.cast_div, rationalDiskMajorant_cast, hQ] using h

theorem rational_real_enclosure (s : Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (Q x S : ℚ)
    (hQ : (Q : ℝ) = s.maxScale) (hx : 0 ≤ x) (hxS : x < S)
    (fuel : ℕ) (ht : Q^fuel * S < 1) (N : ℕ) (i : Fin 2) :
    s.realOddPolynomial i N (x : ℝ) ≤ s.realComponent i (x : ℝ) ∧
      s.realComponent i (x : ℝ) ≤ s.realOddPolynomial i N (x : ℝ) +
        ((rationalDiskMajorant Q fuel S * (x/S)^(2*N+3) : ℚ) : ℝ) := by
  have h := s.real_ladder_enclosure hs hc i
    (by exact_mod_cast hx : (0 : ℝ) ≤ x) (by exact_mod_cast hxS : (x : ℝ) < S)
    fuel (by rw [← hQ]; exact_mod_cast ht) N
  simpa only [Rat.cast_mul, Rat.cast_pow, Rat.cast_div, rationalDiskMajorant_cast, hQ] using h

structure RationalScales where
  q : ℚ
  r : ℚ
  a : ℚ
  b : ℚ

def RationalScales.toReal (p : RationalScales) : Scales := ⟨p.q, p.r, p.a, p.b⟩

def RationalScales.coefficients (p : RationalScales) : ℕ → ℚ × ℚ
  | 0 => (1, 1)
  | n+1 =>
    ((∑ i : Fin (n+1), p.q^(2*i.val+1) * p.r^(2*(n-i.val)+1) *
      (p.coefficients i.val).1 * (p.coefficients (n-i.val)).2) / (2*(n : ℚ)+3),
     (∑ i : Fin (n+1), p.a^(2*i.val+1) * p.b^(2*(n-i.val)+1) *
      (p.coefficients i.val).1 * (p.coefficients (n-i.val)).2) / (2*(n : ℚ)+3))
termination_by n => n
decreasing_by all_goals omega

theorem rational_coefficients_cast (p : RationalScales) (n : ℕ) :
    (((p.coefficients n).1 : ℝ), ((p.coefficients n).2 : ℝ)) = p.toReal.coefficients n := by
  have hsol : p.toReal.IsCoefficientSolution
      (fun k => (((p.coefficients k).1 : ℝ), ((p.coefficients k).2 : ℝ))) := by
    constructor
    · change (((p.coefficients 0).1 : ℝ), ((p.coefficients 0).2 : ℝ)) = (1,1)
      have hz : p.coefficients 0 = (1,1) := by rw [RationalScales.coefficients.eq_def]
      rw [hz]
      norm_num
    · intro k
      change (((p.coefficients (k+1)).1 : ℝ), ((p.coefficients (k+1)).2 : ℝ)) = _
      have hk : p.coefficients (k+1) =
          ((∑ i : Fin (k+1), p.q^(2*i.val+1) * p.r^(2*(k-i.val)+1) *
            (p.coefficients i.val).1 * (p.coefficients (k-i.val)).2) / (2*(k : ℚ)+3),
           (∑ i : Fin (k+1), p.a^(2*i.val+1) * p.b^(2*(k-i.val)+1) *
            (p.coefficients i.val).1 * (p.coefficients (k-i.val)).2) / (2*(k : ℚ)+3)) := by
        rw [RationalScales.coefficients.eq_def]
      rw [hk]
      simp only [nextCoefficient, RationalScales.toReal, Rat.cast_div, Rat.cast_sum,
        Rat.cast_mul, Rat.cast_pow, Rat.cast_add, Rat.cast_ofNat, Rat.cast_natCast]
  exact congrFun (coefficient_solution_unique hsol p.toReal.coefficients_solution) n

def RationalScales.componentCoefficient (p : RationalScales) (i : Fin 2) (n : ℕ) : ℚ :=
  ![(p.coefficients n).1, (p.coefficients n).2] i

theorem rational_component_coefficient_cast (p : RationalScales) (i : Fin 2) (n : ℕ) :
    (p.componentCoefficient i n : ℝ) = p.toReal.componentCoefficient i n := by
  have h := rational_coefficients_cast p n
  fin_cases i
  · exact congrArg Prod.fst h
  · exact congrArg Prod.snd h

def RationalScales.polynomial (p : RationalScales) (i : Fin 2) (N : ℕ) (x : ℚ) : ℚ :=
  ∑ n ∈ Finset.range (N+1), p.componentCoefficient i n * x^(2*n+1)

theorem rational_polynomial_cast (p : RationalScales) (i : Fin 2) (N : ℕ) (x : ℚ) :
    (p.polynomial i N x : ℝ) = p.toReal.realOddPolynomial i N (x : ℝ) := by
  simp only [RationalScales.polynomial, realOddPolynomial, Rat.cast_sum, Rat.cast_mul,
    Rat.cast_pow, rational_component_coefficient_cast]

def RationalScales.maxScale (p : RationalScales) : ℚ := max (max p.q p.r) (max p.a p.b)

theorem rational_maxScale_cast (p : RationalScales) :
    (p.maxScale : ℝ) = p.toReal.maxScale := by
  simp only [RationalScales.maxScale, maxScale, RationalScales.toReal, Rat.cast_max]

theorem rational_fuel_exists (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1) (S : ℚ) :
    ∃ fuel : ℕ, p.maxScale^fuel * S < 1 := by
  obtain ⟨fuel, hf⟩ := p.toReal.exists_diskMajorant_fuel hs hc (S : ℝ)
  refine ⟨fuel, ?_⟩
  rw [← rational_maxScale_cast p] at hf
  exact_mod_cast hf

theorem rational_endpoint_enclosure (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (x S : ℚ) (hx : 0 ≤ x) (hxS : x < S) (fuel : ℕ) (ht : p.maxScale^fuel*S < 1)
    (N : ℕ) (i : Fin 2) :
    (p.polynomial i N x : ℝ) ≤ p.toReal.realComponent i (x : ℝ) ∧
      p.toReal.realComponent i (x : ℝ) ≤
        ((p.polynomial i N x + rationalDiskMajorant p.maxScale fuel S *
          (x/S)^(2*N+3) : ℚ) : ℝ) := by
  have h := p.toReal.rational_real_enclosure hs hc p.maxScale x S
    (rational_maxScale_cast p) hx hxS fuel ht N i
  simpa only [Rat.cast_add, rational_polynomial_cast] using h

theorem unequal_last_thirty_tail_rational :
    rationalDiskMajorant (7/10) 2 2 * (1/2 : ℚ)^63 < 16/100000000000000 := by
  norm_num [rationalDiskMajorant]

theorem unequal_last_thirty_error (i : Fin 2) (z : ℂ) (hz : ‖z‖ ≤ 1) :
    ‖unequalScales.complexComponent i z - unequalScales.oddPolynomial i 30 z‖ <
      (16/100000000000000 : ℝ) := by
  have he := unequalScales.rational_outer_remainder unequalScales_positive unequalScales_strict
    (7/10) 1 2 (by norm_num [maxScale, unequalScales]) (by norm_num) (by norm_num)
    2 (by norm_num) 30 i (by simpa using hz)
  have hb : ((rationalDiskMajorant (7/10) 2 2 * (1/2 : ℚ)^63 : ℚ) : ℝ) <
      (16/100000000000000 : ℝ) := by
    have h := (Rat.cast_lt (K := ℝ)).mpr unequal_last_thirty_tail_rational
    norm_num only [Rat.cast_div, Rat.cast_ofNat] at h ⊢
    exact h
  exact he.trans_lt (by simpa using hb)

end Komorebi.SpecialFunctions.Coupled.Scales
