import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum

/-! An exact positive one-inductor realization for the affine Schur limit. -/
namespace SmithFirstOrderRL

noncomputable def seriesR {K : Type*} [Field K] (a b : K) : K := (1 + a - b) / (1 - a + b)
noncomputable def parallelR {K : Type*} [Field K] (a b : K) : K := 4 * b / ((1 - a - b) * (1 - a + b))
noncomputable def inductance {K : Type*} [Field K] (a b : K) : K := 4 * b / (1 - a + b)^2
noncomputable def reflection {K : Type*} [Field K] (a b s : K) : K := a + b * ((s - 1) / (s + 1))
noncomputable def impedance {K : Type*} [Field K] (a b s : K) : K :=
  (1 + reflection a b s) / (1 - reflection a b s)
noncomputable def circuit {K : Type*} [Field K] (a b s : K) : K :=
  seriesR a b + parallelR a b * (s * inductance a b) / (parallelR a b + s * inductance a b)

/-- Rational equality over any field, including complex frequency, away from poles. -/
theorem rational_identity {K : Type*} [Field K] {a b s : K}
    (hs : s + 1 ≠ 0) (hc : 1 - a - b ≠ 0) (hd : 1 - a + b ≠ 0)
    (hden : 1 - reflection a b s ≠ 0)
    (hbranch : parallelR a b + s * inductance a b ≠ 0) :
    impedance a b s = circuit a b s := by
  unfold impedance circuit
  field_simp [hden, hbranch]
  unfold reflection seriesR parallelR inductance
  field_simp; ring

theorem coefficients_positive {a b : ℝ} (hb : 0 < b) (hbound : b < 1 - |a|) :
    0 < seriesR a b ∧ 0 < parallelR a b ∧ 0 < inductance a b := by
  have hpos : a ≤ |a| := le_abs_self a
  have hneg : -a ≤ |a| := neg_le_abs a
  have hB : 0 < 1 + a - b := by linarith
  have hC : 0 < 1 - a - b := by linarith
  have hD : 0 < 1 - a + b := by linarith
  constructor
  · unfold seriesR; positivity
  constructor
  · unfold parallelR; positivity
  · unfold inductance; positivity

theorem exact_realization {a b s : ℝ} (hb : 0 < b) (hbound : b < 1 - |a|)
    (hs : 0 ≤ s) : impedance a b s = circuit a b s := by
  have hpos : a ≤ |a| := le_abs_self a
  have hC : 0 < 1 - a - b := by linarith
  have hD : 0 < 1 - a + b := by linarith
  have hs1 : s + 1 ≠ 0 := by linarith
  have hlinear : 0 < (1 - a - b) * s + (1 - a + b) := by positivity
  have hden_eq : 1 - reflection a b s = ((1 - a - b) * s + (1 - a + b)) / (s + 1) := by
    unfold reflection
    field_simp; ring
  have hden : 1 - reflection a b s ≠ 0 := by rw [hden_eq]; positivity
  obtain ⟨_, hr, hl⟩ := coefficients_positive hb hbound
  have hbranch : parallelR a b + s * inductance a b ≠ 0 := by positivity
  unfold impedance circuit
  field_simp [hden, hbranch]
  unfold reflection seriesR parallelR inductance
  field_simp; ring

/-- On the closed right half-plane the circuit denominators are nonzero. -/
theorem complex_realization {a b : ℝ} {s : ℂ} (hb : 0 < b)
    (hbound : b < 1 - |a|) (hs : 0 ≤ s.re) :
    impedance (a : ℂ) (b : ℂ) s = circuit (a : ℂ) (b : ℂ) s := by
  have hpos : a ≤ |a| := le_abs_self a
  have hC : 0 < 1 - a - b := by linarith
  have hD : 0 < 1 - a + b := by linarith
  have hc : 1 - (a : ℂ) - (b : ℂ) ≠ 0 := by exact_mod_cast (ne_of_gt hC)
  have hd : 1 - (a : ℂ) + (b : ℂ) ≠ 0 := by exact_mod_cast (ne_of_gt hD)
  have hs1 : s + 1 ≠ 0 := by
    intro h
    have hh := congrArg Complex.re h
    simp only [Complex.add_re, Complex.one_re, Complex.zero_re] at hh
    linarith
  have hlinear_re : (((1 - (a : ℂ) - (b : ℂ)) * s + (1 - (a : ℂ) + (b : ℂ))).re) =
      (1 - a - b) * s.re + (1 - a + b) := by
    simp [Complex.add_re, Complex.sub_re, Complex.mul_re]
  have hlinear_pos : 0 < (((1 - (a : ℂ) - (b : ℂ)) * s + (1 - (a : ℂ) + (b : ℂ))).re) := by
    rw [hlinear_re]
    positivity
  have hlinear_ne : (1 - (a : ℂ) - (b : ℂ)) * s + (1 - (a : ℂ) + (b : ℂ)) ≠ 0 := by
    intro h
    have hh := congrArg Complex.re h
    simp only [Complex.zero_re] at hh
    linarith
  have hden_eq : 1 - reflection (a : ℂ) (b : ℂ) s =
      ((1 - (a : ℂ) - (b : ℂ)) * s + (1 - (a : ℂ) + (b : ℂ))) / (s + 1) := by
    unfold reflection
    field_simp; ring
  have hden : 1 - reflection (a : ℂ) (b : ℂ) s ≠ 0 := by
    rw [hden_eq]
    exact div_ne_zero hlinear_ne hs1
  obtain ⟨_, hr, hl⟩ := coefficients_positive hb hbound
  have hR : parallelR (a : ℂ) (b : ℂ) = ((parallelR a b : ℝ) : ℂ) := by simp [parallelR]
  have hL : inductance (a : ℂ) (b : ℂ) = ((inductance a b : ℝ) : ℂ) := by simp [inductance]
  have hbranch_pos : 0 < (parallelR (a : ℂ) (b : ℂ) + s * inductance (a : ℂ) (b : ℂ)).re := by
    rw [hR, hL]
    simp
    positivity
  have hbranch : parallelR (a : ℂ) (b : ℂ) + s * inductance (a : ℂ) (b : ℂ) ≠ 0 := by
    intro h
    have hh := congrArg Complex.re h
    simp only [Complex.zero_re] at hh
    linarith
  exact rational_identity hs1 hc hd hden hbranch

/-- The mask parameters in the archived theorem satisfy the circuit hypotheses. -/
theorem mask_parameters_admissible {a ρ : ℝ} (ha : |a| < 1)
    (hρ : 0 < ρ) (hρhalf : ρ < 1/2) :
    0 < (1 - a^2) * ρ ∧ (1 - a^2) * ρ < 1 - |a| := by
  have hleft : 0 < 1 - |a| := by linarith
  have hright : 0 < 1 + |a| := by positivity
  have hfactor : 1 - a^2 = (1 - |a|) * (1 + |a|) := by nlinarith [sq_abs a]
  have hprod : ρ * (1 + |a|) < 1 := by
    have hh := mul_lt_mul_of_pos_left ha hρ
    nlinarith
  constructor
  · rw [hfactor]; positivity
  · rw [hfactor]
    calc
      (1 - |a|) * (1 + |a|) * ρ = (1 - |a|) * (ρ * (1 + |a|)) := by ring
      _ < (1 - |a|) * 1 := mul_lt_mul_of_pos_left hprod hleft
      _ = 1 - |a| := by ring

/-- The circuit components are strictly positive throughout the mask range. -/
theorem mask_components_positive {a ρ : ℝ} (ha : |a| < 1)
    (hρ : 0 < ρ) (hρhalf : ρ < 1/2) :
    0 < seriesR a ((1 - a^2) * ρ) ∧
    0 < parallelR a ((1 - a^2) * ρ) ∧
    0 < inductance a ((1 - a^2) * ρ) := by
  obtain ⟨hb, hbound⟩ := mask_parameters_admissible ha hρ hρhalf
  exact coefficients_positive hb hbound

/-- A positive RL one-port realizes the affine limit on the nonnegative real axis. -/
theorem mask_limit_realization {a ρ s : ℝ} (ha : |a| < 1)
    (hρ : 0 < ρ) (hρhalf : ρ < 1/2) (hs : 0 ≤ s) :
    impedance a ((1 - a^2) * ρ) s = circuit a ((1 - a^2) * ρ) s := by
  obtain ⟨hb, hbound⟩ := mask_parameters_admissible ha hρ hρhalf
  exact exact_realization hb hbound hs


/-- The archive's affine limit has this circuit throughout the closed right half-plane. -/
theorem mask_complex_realization {a ρ : ℝ} {s : ℂ} (ha : |a| < 1)
    (hρ : 0 < ρ) (hρhalf : ρ < 1/2) (hs : 0 ≤ s.re) :
    impedance (a : ℂ) (((1 - a^2) * ρ : ℝ) : ℂ) s =
      circuit (a : ℂ) (((1 - a^2) * ρ : ℝ) : ℂ) s := by
  obtain ⟨hb, hbound⟩ := mask_parameters_admissible ha hρ hρhalf
  exact complex_realization hb hbound hs

theorem normalized_example :
    seriesR (1/3 : ℝ) (2/9) = 5/4 ∧
    parallelR (1/3 : ℝ) (2/9) = 9/4 ∧
    inductance (1/3 : ℝ) (2/9) = 9/8 := by
  norm_num [seriesR, parallelR, inductance]

end SmithFirstOrderRL
