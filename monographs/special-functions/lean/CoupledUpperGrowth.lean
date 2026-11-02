import CoupledLowerGrowth

/-! # Explicit upper comparison for the canonical coupled functions -/

set_option autoImplicit false
set_option maxHeartbeats 2500000

noncomputable section
open Set
open scoped Topology Matrix

namespace Komorebi.SpecialFunctions.Coupled.Scales

theorem full_radius_upper_from_deriv {f g h : ℝ → ℝ} {p q R : ℝ}
    (hf : Differentiable ℝ f) (hf0 : f 0 = 0)
    (hg0 : ∀ x, 0 ≤ x → 0 ≤ g x) (hh0 : ∀ x, 0 ≤ x → 0 ≤ h x)
    (hgm : MonotoneOn g (Ici 0)) (hhm : MonotoneOn h (Ici 0))
    (hd : ∀ x, deriv f x = 1 + g (p * x) * h (q * x))
    (hp : 0 ≤ p) (hq : 0 ≤ q) (hR : 0 ≤ R) :
    f R ≤ R * (1 + g (p * R) * h (q * R)) := by
  have hbound : ∀ x ∈ interior (Icc 0 R),
      deriv f x ≤ 1 + g (p * R) * h (q * R) := by
    intro x hx
    have hxI : x ∈ Icc 0 R := interior_subset hx
    have hgp := hgm (mul_nonneg hp hxI.1) (mul_nonneg hp hR)
      (mul_le_mul_of_nonneg_left hxI.2 hp)
    have hhq := hhm (mul_nonneg hq hxI.1) (mul_nonneg hq hR)
      (mul_le_mul_of_nonneg_left hxI.2 hq)
    rw [hd x]
    exact add_le_add le_rfl (mul_le_mul hgp hhq
      (hh0 _ (mul_nonneg hq hxI.1)) (hg0 _ (mul_nonneg hp hR)))
  have hc := (convex_Icc 0 R).image_sub_le_mul_sub_of_deriv_le
    hf.continuous.continuousOn hf.differentiableOn hbound
    0 ⟨le_rfl, hR⟩ R ⟨hR, le_rfl⟩ hR
  simpa only [hf0, sub_zero, mul_comm] using hc

theorem real_axis_full_upper (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {R : ℝ} (hR : 0 ≤ R) :
    s.UReal R ≤ R * (1 + s.UReal (s.q * R) * s.VReal (s.r * R)) ∧
    s.VReal R ≤ R * (1 + s.UReal (s.a * R) * s.VReal (s.b * R)) := by
  have hd := s.real_axis_differentiable hs hstrict
  have hm := s.real_axis_strictMono hs hstrict
  have hu0 : ∀ x : ℝ, 0 ≤ x → 0 ≤ s.UReal x :=
    fun x hx => (s.real_axis_nonneg hs hstrict hx).1
  have hv0 : ∀ x : ℝ, 0 ≤ x → 0 ≤ s.VReal x :=
    fun x hx => (s.real_axis_nonneg hs hstrict hx).2
  exact ⟨full_radius_upper_from_deriv hd.1 s.real_axis_zero.1 hu0 hv0
      hm.1.monotoneOn hm.2.monotoneOn
      (fun x => (s.real_axis_hasDerivAt hs hstrict x).1.deriv) hs.1.le hs.2.1.le hR,
    full_radius_upper_from_deriv hd.2 s.real_axis_zero.2 hu0 hv0
      hm.1.monotoneOn hm.2.monotoneOn
      (fun x => (s.real_axis_hasDerivAt hs hstrict x).2.deriv) hs.2.2.1.le hs.2.2.2.le hR⟩

theorem real_axis_at_one_le_two (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.UReal 1 ≤ 2 ∧ s.VReal 1 ≤ 2 := by
  have hf := s.real_series_hasSum hs hstrict 1
  simp only [one_pow, mul_one] at hf
  have hg : HasSum (fun n : ℕ => (1 / 2 : ℝ) ^ n) 2 := by
    convert hasSum_geometric_of_lt_one (by norm_num : 0 ≤ (1 / 2 : ℝ)) (by norm_num) using 1
    norm_num
  have hsmall := And.intro hstrict.1.le
    (And.intro hstrict.2.1.le (And.intro hstrict.2.2.1.le hstrict.2.2.2.le))
  exact ⟨hasSum_le (fun n => (s.coefficients_le_geometric hs hsmall n).1) hf.1 hg,
    hasSum_le (fun n => (s.coefficients_le_geometric hs hsmall n).2) hf.2 hg⟩

def upperRadius (s : Scales) (n : ℕ) : ℝ := (1 / s.maxScale) ^ n
def upperSeed (s : Scales) : ℕ → ℝ
  | 0 => 2
  | n + 1 => s.upperRadius (n + 1) * (1 + s.upperSeed n ^ 2)
def upperLogSeed (s : Scales) (n : ℕ) : ℝ :=
  ((2 : ℝ) ^ (n + 1) - 1) * Real.log 2 +
    ((2 : ℝ) ^ (n + 1) - (n : ℝ) - 2) * Real.log (1 / s.maxScale)

theorem upperRadius_ge_one (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (n : ℕ) :
    1 ≤ s.upperRadius n := by
  exact one_le_pow₀ ((one_le_div (s.maxScale_positive hs)).mpr
    (s.maxScale_lt_one hstrict).le)

theorem upperRadius_child (s : Scales) (hs : s.positive)
    {p : ℝ} (hp : p ≤ s.maxScale) (n : ℕ) :
    p * s.upperRadius (n + 1) ≤ s.upperRadius n := by
  have hQ := s.maxScale_positive hs
  have he : s.maxScale * s.upperRadius (n + 1) = s.upperRadius n := by
    dsimp [upperRadius]
    rw [pow_succ]
    field_simp
  exact (mul_le_mul_of_nonneg_right hp (by dsimp [upperRadius]; positivity)).trans he.le

theorem upperSeed_ge_one (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (n : ℕ) :
    1 ≤ s.upperSeed n := by
  cases n with
  | zero => norm_num [upperSeed]
  | succ n =>
    have hr := s.upperRadius_ge_one hs hstrict (n + 1)
    have hz := sq_nonneg (s.upperSeed n)
    dsimp [upperSeed]
    nlinarith

theorem real_axis_upper_ladder (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (n : ℕ) :
    s.UReal (s.upperRadius n) ≤ s.upperSeed n ∧
    s.VReal (s.upperRadius n) ≤ s.upperSeed n := by
  induction n with
  | zero => simpa [upperRadius, upperSeed] using s.real_axis_at_one_le_two hs hstrict
  | succ n ih =>
    have hR := (s.upperRadius_ge_one hs hstrict (n + 1)).trans' (by norm_num : (0 : ℝ) ≤ 1)
    have hm := s.real_axis_strictMono hs hstrict
    have hb := s.maxScale_bounds
    have hchild (p : ℝ) (hp : 0 ≤ p) (hpQ : p ≤ s.maxScale) :
        s.UReal (p * s.upperRadius (n + 1)) ≤ s.upperSeed n ∧
        s.VReal (p * s.upperRadius (n + 1)) ≤ s.upperSeed n :=
      ⟨(hm.1.monotoneOn (mul_nonneg hp hR)
        (show 0 ≤ s.upperRadius n from (by norm_num : (0 : ℝ) ≤ 1).trans (s.upperRadius_ge_one hs hstrict n))
        (s.upperRadius_child hs hpQ n)).trans ih.1,
       (hm.2.monotoneOn (mul_nonneg hp hR)
        (show 0 ≤ s.upperRadius n from (by norm_num : (0 : ℝ) ≤ 1).trans (s.upperRadius_ge_one hs hstrict n))
        (s.upperRadius_child hs hpQ n)).trans ih.2⟩
    have hu := s.real_axis_full_upper hs hstrict hR
    have hz := (s.upperSeed_ge_one hs hstrict n).trans' (by norm_num : (0 : ℝ) ≤ 1)
    have hprod (p p' : ℝ) (hp : 0 ≤ p) (hp' : 0 ≤ p')
        (hpQ : p ≤ s.maxScale) (hpQ' : p' ≤ s.maxScale) :
        s.UReal (p * s.upperRadius (n + 1)) * s.VReal (p' * s.upperRadius (n + 1)) ≤
          s.upperSeed n ^ 2 := by
      have ha := (hchild p hp hpQ).1
      have hb' := (hchild p' hp' hpQ').2
      have hn := (s.real_axis_nonneg hs hstrict (mul_nonneg hp' hR)).2
      simpa only [pow_two] using mul_le_mul ha hb' hn hz
    constructor
    · exact hu.1.trans (mul_le_mul_of_nonneg_left
        (add_le_add le_rfl (hprod s.q s.r hs.1.le hs.2.1.le hb.1 hb.2.1)) hR)
    · exact hu.2.trans (mul_le_mul_of_nonneg_left
        (add_le_add le_rfl (hprod s.a s.b hs.2.2.1.le hs.2.2.2.le hb.2.2.1 hb.2.2.2)) hR)

theorem upperLogSeed_recurrence (s : Scales) (n : ℕ) :
    s.upperLogSeed (n + 1) = (n + 1 : ℝ) * Real.log (1 / s.maxScale) +
      Real.log 2 + 2 * s.upperLogSeed n := by
  simp only [upperLogSeed, Nat.cast_add, Nat.cast_one, pow_succ]
  ring

theorem upperSeed_log_le (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (n : ℕ) :
    Real.log (s.upperSeed n) ≤ s.upperLogSeed n := by
  induction n with
  | zero => norm_num [upperSeed, upperLogSeed]
  | succ n ih =>
    have hz := s.upperSeed_ge_one hs hstrict n
    have hz0 : 0 < s.upperSeed n := by linarith
    have hr : 0 < s.upperRadius (n + 1) :=
      lt_of_lt_of_le (by norm_num) (s.upperRadius_ge_one hs hstrict (n + 1))
    have harg : 0 < 1 + s.upperSeed n ^ 2 := by positivity
    have hh : 1 + s.upperSeed n ^ 2 ≤ 2 * s.upperSeed n ^ 2 := by nlinarith
    have hl := Real.log_le_log harg hh
    rw [Real.log_mul (by norm_num) (ne_of_gt (sq_pos_of_pos hz0)), Real.log_pow] at hl
    norm_num only [Nat.cast_ofNat] at hl
    rw [upperSeed, Real.log_mul (ne_of_gt hr) (ne_of_gt harg)]
    have hrlog : Real.log (s.upperRadius (n + 1)) =
        (n + 1 : ℝ) * Real.log (1 / s.maxScale) := by
      simp [upperRadius, Real.log_pow]
    rw [hrlog, s.upperLogSeed_recurrence]
    linarith only [ih, hl]

def scaleDelay (p : ℝ) : ℝ := Real.log (1 / p)
def upperDelay (s : Scales) : ℝ := scaleDelay s.minScale
def upperCorrection (s : Scales) : ℝ :=
  max (scaleDelay (s.q * s.r)) (scaleDelay (s.a * s.b)) + Real.log 2
def upperSeedBudget (s : Scales) (n : ℕ) : ℝ :=
  s.upperLogSeed n + 1 + s.upperDelay + s.upperCorrection
def upperPowerConstant (s : Scales) (n : ℕ) (ρ : ℝ) (w : Fin 2 → ℝ) : ℝ :=
  Real.exp (-ρ) * s.upperSeedBudget n / min (w 0) (w 1)
def UpperPowerAt (s : Scales) (n : ℕ) (ρ : ℝ) (w : Fin 2 → ℝ) (t : ℝ) : Prop :=
  Real.log (s.UReal (Real.exp t)) + t + s.upperCorrection ≤
    s.upperPowerConstant n ρ w * w 0 * Real.exp (ρ * t) ∧
  Real.log (s.VReal (Real.exp t)) + t + s.upperCorrection ≤
    s.upperPowerConstant n ρ w * w 1 * Real.exp (ρ * t)

theorem scaleDelay_positive {p : ℝ} (hp : 0 < p) (hp1 : p < 1) :
    0 < scaleDelay p := by
  exact Real.log_pos ((one_lt_div hp).mpr hp1)

theorem scaleDelay_bounds (s : Scales) (hs : s.positive)
    {p : ℝ} (hmp : s.minScale ≤ p) (hpQ : p ≤ s.maxScale) :
    scaleDelay s.maxScale ≤ scaleDelay p ∧ scaleDelay p ≤ s.upperDelay := by
  have hm := s.minScale_positive hs
  have hp := hm.trans_le hmp
  have hQ := s.maxScale_positive hs
  constructor
  · exact Real.log_le_log (by positivity) (one_div_le_one_div_of_le hp hpQ)
  · exact Real.log_le_log (by positivity) (one_div_le_one_div_of_le hm hmp)

theorem upperCorrection_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    0 < s.upperCorrection := by
  have hh := mul_lt_mul_of_pos_right hstrict.1 hs.2.1
  have hqr : s.q * s.r < 1 := by nlinarith only [hh, hstrict.2.1]
  have hd := scaleDelay_positive (mul_pos hs.1 hs.2.1) hqr
  have hm := le_max_left (scaleDelay (s.q * s.r)) (scaleDelay (s.a * s.b))
  dsimp [upperCorrection]
  linarith [Real.log_pos (by norm_num : (1 : ℝ) < 2)]

theorem upperCorrection_rows (s : Scales) (hs : s.positive) :
    scaleDelay s.q + scaleDelay s.r + Real.log 2 ≤ s.upperCorrection ∧
    scaleDelay s.a + scaleDelay s.b + Real.log 2 ≤ s.upperCorrection := by
  have he (p p' : ℝ) (hp : 0 < p) (hp' : 0 < p') :
      scaleDelay (p * p') = scaleDelay p + scaleDelay p' := by
    simp only [scaleDelay, one_div, mul_inv_rev, Real.log_mul
      (inv_ne_zero (ne_of_gt hp')) (inv_ne_zero (ne_of_gt hp))]
    ring
  rw [upperCorrection, he s.q s.r hs.1 hs.2.1, he s.a s.b hs.2.2.1 hs.2.2.2]
  exact ⟨add_le_add (le_max_left _ _) le_rfl, add_le_add (le_max_right _ _) le_rfl⟩

theorem exp_one_lt_three : Real.exp 1 < 3 := by
  have hh := Real.exp_bound_div_one_sub_of_interval
    (by norm_num : (0 : ℝ) ≤ 1 / 6) (by norm_num : (1 / 6 : ℝ) < 1)
  norm_num at hh
  have hp := pow_le_pow_left₀ (Real.exp_pos (1 / 6)).le hh 6
  have he : Real.exp 1 = Real.exp (1 / 6) ^ 6 := by
    convert Real.exp_nat_mul (1 / 6) 6 using 1
    norm_num
  rw [← he] at hp
  norm_num at hp ⊢
  linarith only [hp]

theorem exists_upper_seed_index (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ∃ n : ℕ, 3 / s.minScale ≤ s.upperRadius n := by
  obtain ⟨n, hn⟩ := pow_unbounded_of_one_lt (3 / s.minScale)
    ((one_lt_div (s.maxScale_positive hs)).mpr (s.maxScale_lt_one hstrict))
  exact ⟨n, hn.le⟩

theorem upper_seed_exp_radius (s : Scales) (hs : s.positive)
    {n : ℕ} (hn : 3 / s.minScale ≤ s.upperRadius n) {t : ℝ}
    (ht : t ≤ 1 + s.upperDelay) : Real.exp t ≤ s.upperRadius n := by
  have hm := s.minScale_positive hs
  have he : Real.exp (1 + s.upperDelay) = Real.exp 1 / s.minScale := by
    rw [Real.exp_add]
    dsimp [upperDelay, scaleDelay]
    rw [Real.exp_log (by positivity)]
    ring
  calc
    Real.exp t ≤ Real.exp (1 + s.upperDelay) := Real.exp_le_exp.mpr ht
    _ = Real.exp 1 / s.minScale := he
    _ ≤ 3 / s.minScale := (div_le_div_of_nonneg_right exp_one_lt_three.le hm.le)
    _ ≤ s.upperRadius n := hn

theorem real_axis_upper_log_seed (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {n : ℕ} (hn : 3 / s.minScale ≤ s.upperRadius n) {t : ℝ}
    (ht : t ≤ 1 + s.upperDelay) :
    Real.log (s.UReal (Real.exp t)) ≤ s.upperLogSeed n ∧
    Real.log (s.VReal (Real.exp t)) ≤ s.upperLogSeed n := by
  have hR := s.upper_seed_exp_radius hs hn ht
  have hm := s.real_axis_strictMono hs hstrict
  have hl := s.real_axis_upper_ladder hs hstrict n
  have hpos := s.real_axis_lower_linear hs hstrict (Real.exp_pos t).le
  have hRn : 0 ≤ s.upperRadius n :=
    (by norm_num : (0 : ℝ) ≤ 1).trans (s.upperRadius_ge_one hs hstrict n)
  constructor
  · exact (Real.log_le_log (lt_of_lt_of_le (Real.exp_pos t) hpos.1)
      ((hm.1.monotoneOn (Real.exp_pos t).le hRn hR).trans hl.1)).trans
      (s.upperSeed_log_le hs hstrict n)
  · exact (Real.log_le_log (lt_of_lt_of_le (Real.exp_pos t) hpos.2)
      ((hm.2.monotoneOn (Real.exp_pos t).le hRn hR).trans hl.2)).trans
      (s.upperSeed_log_le hs hstrict n)

theorem log_upper_from_full {f u v R : ℝ} (hf : 0 < f) (hR : 0 < R)
    (hu : 1 ≤ u) (hv : 1 ≤ v) (hfull : f ≤ R * (1 + u * v)) :
    Real.log f ≤ Real.log R + Real.log 2 + Real.log u + Real.log v := by
  have hu0 : 0 < u := by linarith
  have hv0 : 0 < v := by linarith
  have hprod : 1 ≤ u * v := one_le_mul_of_one_le_of_one_le hu hv
  have hf' : f ≤ R * (2 * (u * v)) := by nlinarith only [hfull, hprod, hR]
  have hh := Real.log_le_log hf hf'
  rw [Real.log_mul (ne_of_gt hR) (by positivity),
    Real.log_mul (by norm_num) (by positivity),
    Real.log_mul (ne_of_gt hu0) (ne_of_gt hv0)] at hh
  linarith only [hh]

theorem real_axis_log_full_upper (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {R : ℝ} (hR : 0 < R) (hmR : 1 ≤ s.minScale * R) :
    Real.log (s.UReal R) ≤ Real.log R + Real.log 2 +
      Real.log (s.UReal (s.q * R)) + Real.log (s.VReal (s.r * R)) ∧
    Real.log (s.VReal R) ≤ Real.log R + Real.log 2 +
      Real.log (s.UReal (s.a * R)) + Real.log (s.VReal (s.b * R)) := by
  have hb := s.minScale_bounds
  have hl := s.real_axis_lower_linear hs hstrict hR.le
  have hp (p : ℝ) (hmp : s.minScale ≤ p) :
      1 ≤ s.UReal (p * R) ∧ 1 ≤ s.VReal (p * R) := by
    have hpR : 1 ≤ p * R := hmR.trans (mul_le_mul_of_nonneg_right hmp hR.le)
    have hx := s.real_axis_lower_linear hs hstrict (by linarith : 0 ≤ p * R)
    exact ⟨hpR.trans hx.1, hpR.trans hx.2⟩
  have hu := s.real_axis_full_upper hs hstrict hR.le
  exact ⟨log_upper_from_full (hR.trans_le hl.1) hR (hp s.q hb.1).1 (hp s.r hb.2.1).2 hu.1,
    log_upper_from_full (hR.trans_le hl.2) hR (hp s.a hb.2.2.1).1 (hp s.b hb.2.2.2).2 hu.2⟩

theorem upperSeedBudget_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (n : ℕ) :
    0 < s.upperSeedBudget n := by
  have hW := (Real.log_nonneg (s.upperSeed_ge_one hs hstrict n)).trans
    (s.upperSeed_log_le hs hstrict n)
  have hΔ := scaleDelay_positive (s.minScale_positive hs)
    (s.minScale_bounds.1.trans_lt hstrict.1)
  change 0 < s.upperDelay at hΔ
  have hD := s.upperCorrection_positive hs hstrict
  dsimp [upperSeedBudget]
  linarith only [hW, hΔ, hD]

theorem upperPowerConstant_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (n : ℕ) (ρ : ℝ) {w : Fin 2 → ℝ} (hw : ∀ i, 0 < w i) :
    0 < s.upperPowerConstant n ρ w :=
  div_pos (mul_pos (Real.exp_pos _) (s.upperSeedBudget_positive hs hstrict n))
    (lt_min (hw 0) (hw 1))

theorem upper_power_seed (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {n : ℕ} (hn : 3 / s.minScale ≤ s.upperRadius n)
    {ρ : ℝ} (hρ : 0 < ρ) {w : Fin 2 → ℝ} (hw : ∀ i, 0 < w i)
    {t : ℝ} (ht : 1 ≤ t) (htB : t ≤ 1 + s.upperDelay) :
    s.UpperPowerAt n ρ w t := by
  have hS := s.upperSeedBudget_positive hs hstrict n
  have hm : 0 < min (w 0) (w 1) := lt_min (hw 0) (hw 1)
  have hl := s.real_axis_upper_log_seed hs hstrict hn htB
  have hmin (i : Fin 2) : min (w 0) (w 1) ≤ w i := by
    fin_cases i
    · exact min_le_left _ _
    · exact min_le_right _ _
  have hweight (i : Fin 2) : s.upperSeedBudget n ≤
      s.upperSeedBudget n / min (w 0) (w 1) * w i := by
    calc
      _ = s.upperSeedBudget n / min (w 0) (w 1) * min (w 0) (w 1) :=
        (div_mul_cancel₀ _ (ne_of_gt hm)).symm
      _ ≤ _ := mul_le_mul_of_nonneg_left (hmin i) (div_nonneg hS.le hm.le)
  have he : 1 ≤ Real.exp (-ρ) * Real.exp (ρ * t) := by
    rw [← Real.exp_add]
    exact Real.one_le_exp_iff.mpr (by nlinarith only [hρ, ht])
  have hbound (i : Fin 2) : s.upperSeedBudget n ≤
      s.upperPowerConstant n ρ w * w i * Real.exp (ρ * t) := by
    calc
      _ ≤ s.upperSeedBudget n / min (w 0) (w 1) * w i := hweight i
      _ ≤ (s.upperSeedBudget n / min (w 0) (w 1) * w i) *
          (Real.exp (-ρ) * Real.exp (ρ * t)) :=
        le_mul_of_one_le_right (le_trans hS.le (hweight i)) he
      _ = _ := by dsimp [upperPowerConstant]; ring
  constructor
  · exact (show Real.log (s.UReal (Real.exp t)) + t + s.upperCorrection ≤
        s.upperSeedBudget n from by dsimp [upperSeedBudget]; linarith only [hl.1, htB]).trans (hbound 0)
  · exact (show Real.log (s.VReal (Real.exp t)) + t + s.upperCorrection ≤
        s.upperSeedBudget n from by dsimp [upperSeedBudget]; linarith only [hl.2, htB]).trans (hbound 1)

theorem exp_sub_scaleDelay {p : ℝ} (hp : 0 < p) (t : ℝ) :
    Real.exp (t - scaleDelay p) = p * Real.exp t := by
  rw [Real.exp_sub]
  dsimp [scaleDelay]
  rw [Real.exp_log (by positivity : 0 < 1 / p)]
  field_simp

theorem real_axis_log_delayed_upper (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {t : ℝ} (ht : 1 + s.upperDelay ≤ t) :
    Real.log (s.UReal (Real.exp t)) + t + s.upperCorrection ≤
      (Real.log (s.UReal (Real.exp (t - scaleDelay s.q))) + (t - scaleDelay s.q) + s.upperCorrection) +
      (Real.log (s.VReal (Real.exp (t - scaleDelay s.r))) + (t - scaleDelay s.r) + s.upperCorrection) ∧
    Real.log (s.VReal (Real.exp t)) + t + s.upperCorrection ≤
      (Real.log (s.UReal (Real.exp (t - scaleDelay s.a))) + (t - scaleDelay s.a) + s.upperCorrection) +
      (Real.log (s.VReal (Real.exp (t - scaleDelay s.b))) + (t - scaleDelay s.b) + s.upperCorrection) := by
  have hm := s.minScale_positive hs
  have hchild : 1 ≤ s.minScale * Real.exp t := by
    rw [← exp_sub_scaleDelay hm t]
    exact Real.one_le_exp_iff.mpr (by change 0 ≤ t - s.upperDelay; linarith only [ht])
  have hh := s.real_axis_log_full_upper hs hstrict (Real.exp_pos t) hchild
  rw [Real.log_exp, ← exp_sub_scaleDelay hs.1 t, ← exp_sub_scaleDelay hs.2.1 t,
    ← exp_sub_scaleDelay hs.2.2.1 t, ← exp_sub_scaleDelay hs.2.2.2 t] at hh
  have hD := s.upperCorrection_rows hs
  constructor
  · linarith only [hh.1, hD.1]
  · linarith only [hh.2, hD.2]

theorem exp_weight_shift {p ρ t : ℝ} (hp : 0 < p) :
    Real.exp (ρ * (t - scaleDelay p)) = p ^ ρ * Real.exp (ρ * t) := by
  rw [Real.rpow_def_of_pos hp, ← Real.exp_add]
  congr 1
  simp only [scaleDelay, one_div, Real.log_inv]
  ring

theorem real_log_delay_induction {P : ℝ → Prop} {B d : ℝ} (hd : 0 < d)
    (hseed : ∀ t, 1 ≤ t → t ≤ B → P t)
    (hstep : ∀ t, 1 ≤ t → B < t → (∀ u, 1 ≤ u → u ≤ t - d → P u) → P t) :
    ∀ t, 1 ≤ t → P t := by
  have h := real_radius_descent_induction (P := fun R => P (R - 1))
    (B := B + 1) (d := d) hd
    (fun R hR hRB => hseed (R - 1) (by linarith only [hR]) (by linarith only [hRB]))
    (fun R hR hBR hIH => hstep (R - 1) (by linarith only [hR])
      (by linarith only [hBR]) (fun u hu hud => by
        have hh := hIH (u + 1) (by linarith only [hu]) (by linarith only [hud])
        simpa only [add_sub_cancel_right] using hh))
  intro t ht
  have hh := h (t + 1) (by linarith only [ht])
  simpa only [add_sub_cancel_right] using hh

theorem upper_power_step (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (n : ℕ) (ρ : ℝ) (w : Fin 2 → ℝ)
    (he : s.characteristicMatrix ρ *ᵥ w = w) {t : ℝ}
    (ht : 1 + s.upperDelay < t)
    (hIH : ∀ u, 1 ≤ u → u ≤ t - scaleDelay s.maxScale → s.UpperPowerAt n ρ w u) :
    s.UpperPowerAt n ρ w t := by
  have hb := s.minScale_bounds
  have hQ := s.maxScale_bounds
  have hchild (p : ℝ) (hmp : s.minScale ≤ p) (hpQ : p ≤ s.maxScale) :
      s.UpperPowerAt n ρ w (t - scaleDelay p) := by
    have hh := s.scaleDelay_bounds hs hmp hpQ
    exact hIH _ (by linarith only [ht, hh.2]) (by linarith only [hh.1])
  have hq := hchild s.q hb.1 hQ.1
  have hr := hchild s.r hb.2.1 hQ.2.1
  have ha := hchild s.a hb.2.2.1 hQ.2.2.1
  have hB := hchild s.b hb.2.2.2 hQ.2.2.2
  have hh := s.real_axis_log_delayed_upper hs hstrict ht.le
  have hu := hh.1.trans (add_le_add hq.1 hr.2)
  have hv := hh.2.trans (add_le_add ha.1 hB.2)
  rw [exp_weight_shift hs.1, exp_weight_shift hs.2.1] at hu
  rw [exp_weight_shift hs.2.2.1, exp_weight_shift hs.2.2.2] at hv
  have he0 := congrFun he 0
  have he1 := congrFun he 1
  norm_num [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two] at he0 he1
  have h0 := congrArg (fun x : ℝ => s.upperPowerConstant n ρ w * x * Real.exp (ρ * t)) he0
  have h1 := congrArg (fun x : ℝ => s.upperPowerConstant n ρ w * x * Real.exp (ρ * t)) he1
  constructor
  · nlinarith only [hu, h0]
  · nlinarith only [hv, h1]

theorem coupled_upper_log_power (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {n : ℕ} (hn : 3 / s.minScale ≤ s.upperRadius n)
    {ρ : ℝ} (hρ : 0 < ρ) {w : Fin 2 → ℝ} (hw : ∀ i, 0 < w i)
    (he : s.characteristicMatrix ρ *ᵥ w = w) :
    ∀ t, 1 ≤ t → s.UpperPowerAt n ρ w t := by
  exact real_log_delay_induction (B := 1 + s.upperDelay)
    (d := scaleDelay s.maxScale) (scaleDelay_positive (s.maxScale_positive hs) (s.maxScale_lt_one hstrict))
    (fun t ht htB => s.upper_power_seed hs hstrict hn hρ hw ht htB)
    (fun t _ ht hIH => s.upper_power_step hs hstrict n ρ w he ht hIH)

theorem canonical_upper_log_power (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {n : ℕ} (hn : 3 / s.minScale ≤ s.upperRadius n)
    {R : ℝ} (hR : Real.exp 1 ≤ R) :
    Real.log (s.UReal R) ≤ s.upperPowerConstant n (s.characteristicExponent hs hstrict)
      (s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict)) *
      s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) 0 *
      R ^ (s.characteristicExponent hs hstrict) - Real.log R - s.upperCorrection ∧
    Real.log (s.VReal R) ≤ s.upperPowerConstant n (s.characteristicExponent hs hstrict)
      (s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict)) *
      s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) 1 *
      R ^ (s.characteristicExponent hs hstrict) - Real.log R - s.upperCorrection := by
  have hR0 := (Real.exp_pos 1).trans_le hR
  have ht : 1 ≤ Real.log R := (Real.le_log_iff_exp_le hR0).mpr hR
  have hρ := s.characteristicExponent_spec hs hstrict
  have hh := s.coupled_upper_log_power hs hstrict hn hρ.1
    (s.normalizedCharacteristicVector_positive hs hstrict.1 hρ.1)
    (s.normalized_characteristic_eigenvector hs hρ.2) (Real.log R) ht
  dsimp [UpperPowerAt] at hh
  rw [Real.exp_log hR0] at hh
  have he : Real.exp (s.characteristicExponent hs hstrict * Real.log R) =
      R ^ (s.characteristicExponent hs hstrict) := by
    rw [Real.rpow_def_of_pos hR0, mul_comm]
  rw [he] at hh
  constructor
  · linarith only [hh.1]
  · linarith only [hh.2]

def upperSeedIndex (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : ℕ :=
  Nat.find (s.exists_upper_seed_index hs hstrict)

theorem upperSeedIndex_spec (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    3 / s.minScale ≤ s.upperRadius (s.upperSeedIndex hs hstrict) :=
  Nat.find_spec (s.exists_upper_seed_index hs hstrict)

def canonicalUpperCoefficient (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) : ℝ :=
  s.upperPowerConstant (s.upperSeedIndex hs hstrict) (s.characteristicExponent hs hstrict)
    (s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict)) *
    s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) i

theorem canonicalUpperCoefficient_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    0 < s.canonicalUpperCoefficient hs hstrict i := by
  have hρ := s.characteristicExponent_spec hs hstrict
  have hw := s.normalizedCharacteristicVector_positive hs hstrict.1 hρ.1
  exact mul_pos (s.upperPowerConstant_positive hs hstrict _ _ hw) (hw i)

theorem canonical_upper_growth_ratio (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {R : ℝ} (hR : Real.exp 1 ≤ R) :
    Real.log (s.UReal R) / R ^ (s.characteristicExponent hs hstrict) ≤
      s.canonicalUpperCoefficient hs hstrict 0 ∧
    Real.log (s.VReal R) / R ^ (s.characteristicExponent hs hstrict) ≤
      s.canonicalUpperCoefficient hs hstrict 1 := by
  have hR0 := (Real.exp_pos 1).trans_le hR
  have hp := Real.rpow_pos_of_pos hR0 (s.characteristicExponent hs hstrict)
  have hh := s.canonical_upper_log_power hs hstrict (s.upperSeedIndex_spec hs hstrict) hR
  have hlog : 1 ≤ Real.log R := (Real.le_log_iff_exp_le hR0).mpr hR
  have hD := s.upperCorrection_positive hs hstrict
  constructor
  · apply (div_le_iff₀ hp).mpr
    change Real.log (s.UReal R) ≤
      (s.upperPowerConstant (s.upperSeedIndex hs hstrict) (s.characteristicExponent hs hstrict)
        (s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict)) *
        s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) 0) *
        R ^ (s.characteristicExponent hs hstrict)
    linarith only [hh.1, hlog, hD]
  · apply (div_le_iff₀ hp).mpr
    change Real.log (s.VReal R) ≤
      (s.upperPowerConstant (s.upperSeedIndex hs hstrict) (s.characteristicExponent hs hstrict)
        (s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict)) *
        s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) 1) *
        R ^ (s.characteristicExponent hs hstrict)
    linarith only [hh.2, hlog, hD]

theorem canonical_two_sided_growth_ratio (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {R : ℝ} (hR : Real.exp 1 ≤ R) :
    (s.canonicalLowerCoefficient hs hstrict 0 ≤
      Real.log (s.UReal R) / R ^ (s.characteristicExponent hs hstrict) ∧
      Real.log (s.UReal R) / R ^ (s.characteristicExponent hs hstrict) ≤
        s.canonicalUpperCoefficient hs hstrict 0) ∧
    (s.canonicalLowerCoefficient hs hstrict 1 ≤
      Real.log (s.VReal R) / R ^ (s.characteristicExponent hs hstrict) ∧
      Real.log (s.VReal R) / R ^ (s.characteristicExponent hs hstrict) ≤
        s.canonicalUpperCoefficient hs hstrict 1) := by
  have h2 : (2 : ℝ) ≤ Real.exp 1 := by simpa only [one_add_one_eq_two] using Real.add_one_le_exp (1 : ℝ)
  have hl := s.canonical_lower_growth_ratio hs hstrict (h2.trans hR)
  have hu := s.canonical_upper_growth_ratio hs hstrict hR
  exact ⟨⟨hl.1, hu.1⟩, ⟨hl.2, hu.2⟩⟩

theorem canonical_upper_norm_power (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {R : ℝ} (hR : Real.exp 1 ≤ R) :
    Real.log ‖s.U (R : ℂ)‖ ≤ s.canonicalUpperCoefficient hs hstrict 0 *
      R ^ (s.characteristicExponent hs hstrict) - Real.log R - s.upperCorrection ∧
    Real.log ‖s.V (R : ℂ)‖ ≤ s.canonicalUpperCoefficient hs hstrict 1 *
      R ^ (s.characteristicExponent hs hstrict) - Real.log R - s.upperCorrection := by
  have hR0 := (Real.exp_pos 1).trans_le hR
  have he := s.real_axis_norm hs hstrict hR0.le
  rw [he.1, he.2]
  exact s.canonical_upper_log_power hs hstrict (s.upperSeedIndex_spec hs hstrict) hR

end Komorebi.SpecialFunctions.Coupled.Scales
