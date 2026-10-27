module
public import Euler.Dyadic
@[expose] public section
noncomputable section
set_option linter.unusedSimpArgs false
namespace Komorebi.Euler
open PowerSeries
abbrev Series := PowerSeries D

/-- The unit ratio with one exact closest-neighbor factor.  The seed has
constant coefficient one; `rescale 4` encodes the remaining weighted tail. -/
def oneRatio (r ε : D) (e : Series) : Series :=
  C r * ((1 + C (2*ε) * X) * rescale (4 : D) e)

/-- The unit ratio with both exact, symmetric closest-neighbor factors. -/
def twoRatio (r : D) (e : Series) : Series :=
  C r * ((1 - C (4 : D) * X^2) * rescale (4 : D) e)

/-- Exact division-free identity defining the averaged collision core. -/
def IsHalfCore (R H : Series) (z : D) : Prop :=
  C (2 : D) * H = X * (1 + R) - C z

lemma oneRatio_coeff (r ε : D) (e : Series) (n : ℕ) :
    coeff (n+1) (oneRatio r ε e) =
      r * (4^(n+1)*coeff (n+1) e + 2*ε*(4^n*coeff n e)) := by
  simp only [oneRatio, add_mul, one_mul, mul_assoc, coeff_C_mul,
    map_add, coeff_succ_X_mul, coeff_rescale]

lemma twoRatio_coeff (r : D) (e : Series) (n : ℕ) :
    coeff (n+2) (twoRatio r e) =
      r * (4^(n+2)*coeff (n+2) e - 4*(4^n*coeff n e)) := by
  simp only [twoRatio, sub_mul, one_mul, mul_assoc, coeff_C_mul,
    map_sub, coeff_X_pow_mul', coeff_rescale]
  simp

lemma halfCore_coeff (R H : Series) (z : D) (h : IsHalfCore R H z) (n : ℕ) :
    2*coeff (n+2) H = coeff (n+1) R := by
  have hc := congrArg (coeff (n+2)) h
  simpa only [map_sub, coeff_C_mul, show n+2 = (n+1)+1 by omega,
    coeff_succ_X_mul, map_add, coeff_succ_C, coeff_one,
    Nat.add_eq_zero_iff, Nat.one_ne_zero, and_false, ite_false, zero_add, sub_zero] using hc

/-- Exact all-order coefficient formula, not just a parity estimate. -/
theorem oneNeighbor_coeff (r ε : D) (e H : Series) (z : D)
    (h : IsHalfCore (oneRatio r ε e) H z) (n : ℕ) :
    coeff (n+2) H = 4^n*r*(2*coeff (n+1) e + ε*coeff n e) := by
  apply cancel_two
  rw [halfCore_coeff _ _ _ h, oneRatio_coeff, pow_succ]
  ring

/-- Exact cubic-tail formula for the symmetric two-neighbor ratio. -/
theorem twoNeighbor_coeff (r : D) (e H : Series) (z : D)
    (h : IsHalfCore (twoRatio r e) H z) (n : ℕ) :
    coeff (n+3) H = 2*4^n*r*(4*coeff (n+2) e - coeff n e) := by
  apply cancel_two
  have hc := halfCore_coeff _ _ _ h (n+1)
  rw [show n+1+2=n+3 by omega, show n+1+1=n+2 by omega,
    twoRatio_coeff] at hc
  rw [hc, pow_add]
  norm_num
  ring

lemma twoNeighbor_coeff_two (r : D) (e H : Series) (z : D)
    (h : IsHalfCore (twoRatio r e) H z) :
    coeff 2 H = 2*r*coeff 1 e := by
  apply cancel_two
  rw [halfCore_coeff _ _ _ h 0]
  simp only [twoRatio, sub_mul, one_mul, mul_assoc, coeff_C_mul,
    map_sub, coeff_rescale, pow_one]
  have hx : coeff 1 ((X : Series)^2 * rescale (4 : D) e) = 0 := by
    rw [coeff_X_pow_mul']
    norm_num
  rw [hx]
  ring

theorem oneNeighbor_lastOdd (r ε : D) (e H : Series) (z : D)
    (hr : red r = 1) (hε : red ε = 1) (he : coeff 0 e = 1)
    (h : IsHalfCore (oneRatio r ε e) H z) : LastOdd H 2 := by
  constructor
  · rw [oneNeighbor_coeff _ _ _ _ _ h 0]
    simp [he, hr, hε]
  · intro n hn
    obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le (show 2 ≤ n by omega)
    rw [show 2+m=m+2 by omega, oneNeighbor_coeff _ _ _ _ _ h]
    have hm : m ≠ 0 := by omega
    simp [hm]

/-- Before any additional division, a two-neighbor core has no odd coefficient
at degree two or higher. -/
theorem twoNeighbor_high_even (r : D) (e H : Series) (z : D)
    (h : IsHalfCore (twoRatio r e) H z) :
    ∀ n, 2 ≤ n → red (coeff n H) = 0 := by
  intro n hn
  by_cases heq : n=2
  · subst n
    rw [twoNeighbor_coeff_two _ _ _ _ h]
    simp
  · obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le (show 3 ≤ n by omega)
    rw [show 3+m=m+3 by omega, twoNeighbor_coeff _ _ _ _ h]
    simp

/-- If the fully formed two-neighbor core is even, dividing it once gives
exactly a cubic reduction; there can be no second hidden common factor. -/
theorem twoNeighbor_divided_lastOdd (r : D) (e H F : Series) (z : D)
    (hr : red r = 1) (he : coeff 0 e = 1)
    (h : IsHalfCore (twoRatio r e) H z) (hF : C (2 : D)*F=H) :
    LastOdd F 3 := by
  have hc (n : ℕ) : coeff (n+3) F = 4^n*r*(4*coeff (n+2) e-coeff n e) := by
    apply cancel_two
    have hf := congrArg (coeff (n+3)) hF
    rw [coeff_C_mul, twoNeighbor_coeff _ _ _ _ h] at hf
    simpa only [mul_assoc] using hf
  constructor
  · rw [hc 0]
    simp [he, hr]
  · intro n hn
    obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le (show 3 ≤ n by omega)
    rw [show 3+m=m+3 by omega, hc]
    have hm : m ≠ 0 := by omega
    simp [hm]

/-- Coefficientwise even formal series can be divided by two inside Z₂. -/
theorem divide_even_series (H : Series) (he : ∀ n, red (coeff n H) = 0) :
    ∃ F : Series, C (2 : D)*F=H := by
  choose a ha using fun n => (red_eq_zero_iff (coeff n H)).mp (he n)
  refine ⟨mk a, ?_⟩
  ext n
  simpa only [coeff_C_mul, coeff_mk] using (ha n).symm

/-- The full two-neighbor coefficient dichotomy, including existence of the
once-divided cubic.  No Weierstrass or convergence theorem is assumed here. -/
theorem twoNeighbor_dichotomy (r : D) (e H : Series) (z : D)
    (hr : red r = 1) (he : coeff 0 e = 1)
    (h : IsHalfCore (twoRatio r e) H z) :
    LastOdd H 0 ∨ LastOdd H 1 ∨
      ∃ F : Series, C (2 : D)*F=H ∧ LastOdd F 3 := by
  have high := twoNeighbor_high_even _ _ _ _ h
  by_cases h1 : red (coeff 1 H) = 0
  · by_cases h0 : red (coeff 0 H) = 0
    · obtain ⟨F,hF⟩ := divide_even_series H (by
        intro n
        rcases n with _ | n
        · exact h0
        rcases n with _ | n
        · exact h1
        · exact high _ (by omega))
      exact Or.inr (Or.inr ⟨F,hF,twoNeighbor_divided_lastOdd r e H F z hr he h hF⟩)
    · refine Or.inl ⟨red_not_zero_eq_one _ h0, ?_⟩
      intro n hn
      by_cases hn1 : n=1
      · simpa [hn1] using h1
      · exact high n (by omega)
  · exact Or.inr (Or.inl ⟨red_not_zero_eq_one _ h1,
      fun n hn => high n (by omega)⟩)

/-- Multiplication by a series with constant reduction one preserves all
residue coefficients, not just its highest nonzero one. -/
theorem unitReduction_mul_coeff (B H : Series)
    (hB : PowerSeries.map red B = 1) (n : ℕ) :
    red (coeff n (B*H)) = red (coeff n H) := by
  rw [← coeff_map, map_mul, hB, one_mul, coeff_map]

theorem lastOdd_mul_unitReduction (B H : Series) (d : ℕ)
    (hB : PowerSeries.map red B = 1) : LastOdd (B*H) d ↔ LastOdd H d := by
  simp only [LastOdd, unitReduction_mul_coeff B H hB]

/-- First formal target corresponding to v12: after the exact half-core
identity, one closest neighbor forces quadratic reduction even after restoring
the analytic-unit factor. -/
theorem full_oneNeighbor_quadratic (r ε : D) (e H B : Series) (z : D)
    (hr : red r=1) (hε : red ε=1) (he : coeff 0 e=1)
    (h : IsHalfCore (oneRatio r ε e) H z)
    (hB : PowerSeries.map red B=1) : LastOdd (B*H) 2 :=
  (lastOdd_mul_unitReduction B H 2 hB).mpr
    (oneNeighbor_lastOdd r ε e H z hr hε he h)

/-- Restoring the analytic unit after the single extra division preserves the
cubic reduction. -/
theorem full_twoNeighbor_cubic (r : D) (e H F B : Series) (z : D)
    (hr : red r=1) (he : coeff 0 e=1)
    (h : IsHalfCore (twoRatio r e) H z) (hF : C (2:D)*F=H)
    (hB : PowerSeries.map red B=1) : LastOdd (B*F) 3 :=
  (lastOdd_mul_unitReduction B F 3 hB).mpr
    (twoNeighbor_divided_lastOdd r e H F z hr he h hF)

end Komorebi.Euler
