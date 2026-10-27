/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroSequenceAsymptotics
import Mathlib.Data.Set.Card
import Mathlib.Order.Interval.Set.Nat

namespace Komorebi.PaperIV
noncomputable section
open Set Metric

/-- Number of entries of a real sequence at or below a real cutoff. -/
def sequenceCounting (f : ℕ → ℝ) (R : ℝ) : ℕ := {m | f m ≤ R}.ncard

/-- A finite counting estimate for any sequence trapped in bounded lattice windows. -/
theorem lattice_window_counting {A : ℝ} (hA : 0 < A) (B : ℕ) (f : ℕ → ℝ)
    (hf : ∀ m, A * m ≤ f m ∧ f m ≤ A * ((m : ℝ) + B))
    {R : ℝ} (hR : 0 ≤ R) :
    {m | f m ≤ R}.Finite ∧ |(sequenceCounting f R : ℝ) - R / A| ≤ B + 2 := by
  let k := Nat.floor (R / A)
  have hupper : {m | f m ≤ R} ⊆ Iio (k + 1) := by
    intro m hm
    change f m ≤ R at hm
    have hh : (m : ℝ) ≤ R / A := (le_div_iff₀ hA).mpr (by nlinarith [(hf m).1])
    have hk : m ≤ k := Nat.le_floor hh
    exact Nat.lt_succ_of_le hk
  have hfinite := (finite_Iio (k + 1)).subset hupper
  have hlower : Iio (k - B) ⊆ {m | f m ≤ R} := by
    intro m hm
    have hm' : m + B ≤ k := by simp only [mem_Iio] at hm; omega
    have hmreal : (m : ℝ) + B ≤ k := by exact_mod_cast hm'
    have hk : (k : ℝ) ≤ R / A := Nat.floor_le (div_nonneg hR hA.le)
    have hh : A * ((m : ℝ) + B) ≤ R := by
      have := (le_div_iff₀ hA).mp (hmreal.trans hk)
      nlinarith
    exact (hf m).2.trans hh
  have hcupper : sequenceCounting f R ≤ k + 1 := by
    simpa [sequenceCounting] using ncard_le_ncard hupper
  have hclower : k - B ≤ sequenceCounting f R := by
    simpa [sequenceCounting] using ncard_le_ncard hlower hfinite
  have hklower : k ≤ sequenceCounting f R + B := by omega
  have hcu : (sequenceCounting f R : ℝ) ≤ k + 1 := by exact_mod_cast hcupper
  have hcl : (k : ℝ) ≤ sequenceCounting f R + B := by exact_mod_cast hklower
  have hfloorlo : (k : ℝ) ≤ R / A := Nat.floor_le (div_nonneg hR hA.le)
  have hfloorhi : R / A < (k : ℝ) + 1 := Nat.lt_floor_add_one _
  exact ⟨hfinite, abs_le.mpr ⟨by linarith, by have := Nat.cast_nonneg (α := ℝ) B; linarith⟩⟩

theorem signedPositiveZero_lattice_windows {N : ℕ} (hN : 3 ≤ N) :
    ∃ m0 : ℕ, ∀ m : ℕ,
      (Real.pi / Real.sin (Real.pi / N)) * m ≤ signedPositiveZero N (m + m0) ∧
      signedPositiveZero N (m + m0) ≤
        (Real.pi / Real.sin (Real.pi / N)) * ((m : ℝ) + (m0 + 1 : ℕ)) := by
  obtain ⟨C, _, m0, hm0⟩ := signedPositiveZero_local_strings hN
  refine ⟨m0, ?_⟩
  intro m
  have hb := (hm0 (m + m0) (by omega)).1.2.2
  have he : |signedPositiveZero N (m + m0) - signedZeroCenter N (m + m0)| ≤
      1 / ‖signedZeroFrequency N‖ := by
    simpa only [mem_closedBall, dist_eq_norm, ← Complex.ofReal_sub, Complex.norm_real, Real.norm_eq_abs] using hb
  have hr := signedZeroCenter_ge_radius (by omega : 2 ≤ N) 0
  have ha : 0 < Real.pi / Real.sin (Real.pi / N) := div_pos Real.pi_pos (signed_sine_pos (by omega))
  rw [abs_le] at he
  simp only [signedZeroCenter, Nat.cast_zero, zero_add] at hr
  simp only [signedZeroCenter, Nat.cast_add, Nat.cast_one] at he ⊢
  have hm0' := Nat.cast_nonneg (α := ℝ) m0
  constructor <;> nlinarith

/-- The positive zero tail has density `sin(pi/N)/pi` with a uniform bounded counting error. -/
theorem signedPositiveZero_tail_counting {N : ℕ} (hN : 3 ≤ N) :
    ∃ m0 : ℕ, ∃ K : ℝ, 0 < K ∧ ∀ R : ℝ, 0 ≤ R →
      {m | signedPositiveZero N (m + m0) ≤ R}.Finite ∧
      |(sequenceCounting (fun m => signedPositiveZero N (m + m0)) R : ℝ) -
        (Real.sin (Real.pi / N) / Real.pi) * R| ≤ K := by
  obtain ⟨m0, hm0⟩ := signedPositiveZero_lattice_windows hN
  refine ⟨m0, (m0 + 1 : ℕ) + 2, by positivity, ?_⟩
  intro R hR
  have h := lattice_window_counting (div_pos Real.pi_pos (signed_sine_pos (by omega)))
    (m0 + 1) (fun m => signedPositiveZero N (m + m0)) hm0 hR
  convert h using 2
  field_simp

end
end Komorebi.PaperIV
