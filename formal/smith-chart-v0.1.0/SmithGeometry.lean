import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

/-! Cayley geometry for the finite impedance and open reflection disk. -/

namespace SmithGeometry

noncomputable def impedance (t : ℂ) : ℂ := (1 + t) / (1 - t)
noncomputable def reflection (z : ℂ) : ℂ := (z - 1) / (z + 1)

theorem impedance_realpart (t : ℂ) :
    (impedance t).re = (1 - ‖t‖ ^ 2) / Complex.normSq (1 - t) := by
  simp only [impedance, Complex.div_re, Complex.add_re, Complex.sub_re,
    Complex.add_im, Complex.sub_im, Complex.one_re, Complex.one_im,
    Complex.sq_norm, Complex.normSq_apply, zero_add, zero_sub]
  ring

theorem impedance_positive_real {t : ℂ} (ht : ‖t‖ < 1) :
    0 < (impedance t).re := by
  rw [impedance_realpart]
  have ht1 : t ≠ 1 := by
    intro he
    rw [he, norm_one] at ht
    exact (lt_irrefl 1) ht
  have hdenom : 1 - t ≠ 0 := sub_ne_zero.mpr ht1.symm
  have hn : 0 < 1 - ‖t‖ ^ 2 := by nlinarith [norm_nonneg t]
  exact div_pos hn (Complex.normSq_pos.mpr hdenom)

theorem impedance_nonnegative_real {t : ℂ} (ht : ‖t‖ ≤ 1) (ht1 : t ≠ 1) :
    0 ≤ (impedance t).re := by
  rw [impedance_realpart]
  have hdenom : 1 - t ≠ 0 := sub_ne_zero.mpr ht1.symm
  have hn : 0 ≤ 1 - ‖t‖ ^ 2 := by nlinarith [norm_nonneg t]
  exact div_nonneg hn (Complex.normSq_pos.mpr hdenom).le

theorem reflection_normSq (z : ℂ) :
    Complex.normSq (reflection z) = Complex.normSq (z - 1) / Complex.normSq (z + 1) := by
  exact Complex.normSq_div _ _

theorem reflection_open_disk {z : ℂ} (hz : 0 < z.re) : ‖reflection z‖ < 1 := by
  have hz1 : z + 1 ≠ 0 := by
    intro h
    have hr := congrArg Complex.re h
    simp only [Complex.add_re, Complex.one_re, Complex.zero_re] at hr
    linarith
  have hd : 0 < Complex.normSq (z + 1) := Complex.normSq_pos.mpr hz1
  have hdiff : Complex.normSq (z - 1) < Complex.normSq (z + 1) := by
    simp only [Complex.normSq_apply, Complex.sub_re, Complex.add_re,
      Complex.sub_im, Complex.add_im, Complex.one_re, Complex.one_im, sub_zero, add_zero]
    nlinarith
  have hsq : ‖reflection z‖ ^ 2 < 1 := by
    rw [Complex.sq_norm, reflection_normSq]
    exact (div_lt_one hd).mpr hdiff
  nlinarith [norm_nonneg (reflection z)]

theorem reflection_closed_disk {z : ℂ} (hz : 0 ≤ z.re) : ‖reflection z‖ ≤ 1 := by
  have hz1 : z + 1 ≠ 0 := by
    intro h
    have hr := congrArg Complex.re h
    simp only [Complex.add_re, Complex.one_re, Complex.zero_re] at hr
    linarith
  have hd : 0 < Complex.normSq (z + 1) := Complex.normSq_pos.mpr hz1
  have hdiff : Complex.normSq (z - 1) ≤ Complex.normSq (z + 1) := by
    simp only [Complex.normSq_apply, Complex.sub_re, Complex.add_re,
      Complex.sub_im, Complex.add_im, Complex.one_re, Complex.one_im, sub_zero, add_zero]
    nlinarith
  have hsq : ‖reflection z‖ ^ 2 ≤ 1 := by
    rw [Complex.sq_norm, reflection_normSq]
    exact (div_le_one hd).mpr hdiff
  nlinarith [norm_nonneg (reflection z)]

theorem impedance_reflection_of_denominator {z : ℂ} (hz1 : z + 1 ≠ 0) :
    impedance (reflection z) = z := by
  unfold impedance reflection
  field_simp [hz1]; ring

theorem impedance_reflection {z : ℂ} (hz : 0 < z.re) :
    impedance (reflection z) = z := by
  have hz1 : z + 1 ≠ 0 := by
    intro h
    have hr := congrArg Complex.re h
    simp only [Complex.add_re, Complex.one_re, Complex.zero_re] at hr
    linarith
  exact impedance_reflection_of_denominator hz1

theorem reflection_impedance {t : ℂ} (ht : ‖t‖ < 1) :
    reflection (impedance t) = t := by
  have ht1 : t ≠ 1 := by
    intro he
    rw [he, norm_one] at ht
    exact (lt_irrefl 1) ht
  have hd : 1 - t ≠ 0 := sub_ne_zero.mpr ht1.symm
  unfold impedance reflection
  field_simp [hd]; ring

/-- The finite chart is a bijection between the open disk and right half-plane. -/
theorem right_half_plane_iff_open_disk {z : ℂ} (hz1 : z + 1 ≠ 0) :
    0 < z.re ↔ ‖reflection z‖ < 1 := by
  constructor
  · exact reflection_open_disk
  · intro ht
    have hp := impedance_positive_real ht
    rw [impedance_reflection_of_denominator hz1] at hp
    exact hp

/-- This includes finite lossless loads on the unit circle; the open is t = 1. -/
theorem nonnegative_real_iff_closed_disk {z : ℂ} (hz1 : z + 1 ≠ 0) :
    0 ≤ z.re ↔ ‖reflection z‖ ≤ 1 := by
  constructor
  · exact reflection_closed_disk
  · intro ht
    have ht1 : reflection z ≠ 1 := by
      intro he
      have he' : z - 1 = z + 1 := (div_eq_one_iff_eq hz1).1 he
      have hr := congrArg Complex.re he'
      simp only [Complex.sub_re, Complex.add_re, Complex.one_re] at hr
      linarith
    have hp := impedance_nonnegative_real ht ht1
    rw [impedance_reflection_of_denominator hz1] at hp
    exact hp

end SmithGeometry
