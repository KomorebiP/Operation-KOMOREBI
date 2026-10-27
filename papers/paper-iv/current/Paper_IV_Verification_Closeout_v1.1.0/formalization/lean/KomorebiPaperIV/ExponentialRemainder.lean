/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ExponentialBounds

/-! # Exact finite exponential remainders and strip estimates

The estimates are derived from explicit real-part gaps. The regular-polygon
gap and the global exclusion of other sectors are separate obligations.
-/

namespace Komorebi.PaperIV
noncomputable section

/-- Derivative jets of the actual normalized finite exponential remainder. -/
def finiteExponentialRemainder (s : Finset ℕ) (a : ℕ → ℂ) (b : ℂ)
    (q : ℕ) (z : ℂ) : ℂ :=
  ∑ l ∈ s, (a l - b) ^ q * Complex.exp ((a l - b) * z)

theorem analyticAt_finiteExponentialRemainder (s : Finset ℕ) (a : ℕ → ℂ)
    (b : ℂ) (q : ℕ) (z : ℂ) :
    AnalyticAt ℂ (finiteExponentialRemainder s a b q) z := by
  unfold finiteExponentialRemainder
  fun_prop

theorem hasDerivAt_finiteExponentialRemainder (s : Finset ℕ) (a : ℕ → ℂ)
    (b : ℂ) (q : ℕ) (z : ℂ) :
    HasDerivAt (finiteExponentialRemainder s a b q)
      (finiteExponentialRemainder s a b (q + 1) z) z := by
  have h := HasDerivAt.fun_sum (u := s) (fun l _ =>
    (((hasDerivAt_id z).const_mul (a l - b)).cexp).const_mul ((a l - b) ^ q))
  have he : (∑ l ∈ s, (a l - b) ^ q * (Complex.exp ((a l - b) * id z) * ((a l - b) * 1))) =
      finiteExponentialRemainder s a b (q + 1) z := by
    apply Finset.sum_congr rfl
    intro l _
    simp only [pow_succ, id_eq]
    ring
  rw [he] at h
  convert h using 1 <;> rfl

theorem iteratedDeriv_finiteExponentialRemainder (s : Finset ℕ) (a : ℕ → ℂ)
    (b : ℂ) (q : ℕ) :
    deriv^[q] (finiteExponentialRemainder s a b 0) =
      finiteExponentialRemainder s a b q := by
  induction q with
  | zero => rfl
  | succ q ih =>
    rw [Function.iterate_succ_apply', ih]
    exact funext (fun z => (hasDerivAt_finiteExponentialRemainder s a b q z).deriv)

/-- All derivative orders satisfy an explicit uniform strip bound. -/
theorem finiteExponentialRemainder_strip_bound {s : Finset ℕ} {a : ℕ → ℂ}
    {b : ℂ} {γ M A Y : ℝ} (hA : 0 ≤ A) (hM : 0 ≤ M)
    (hgap : ∀ l ∈ s, (a l - b).re ≤ -γ)
    (him : ∀ l ∈ s, |(a l - b).im| ≤ M)
    (hnorm : ∀ l ∈ s, ‖a l - b‖ ≤ A)
    {z : ℂ} (hx : 0 ≤ z.re) (hy : |z.im| ≤ Y) (q : ℕ) :
    ‖finiteExponentialRemainder s a b q z‖ ≤
      (s.card : ℝ) * A ^ q * Real.exp (-γ * z.re + M * Y) := by
  have ht (l : ℕ) (hl : l ∈ s) :
      ‖(a l - b) ^ q * Complex.exp ((a l - b) * z)‖ ≤
        A ^ q * Real.exp (-γ * z.re + M * Y) := by
    rw [norm_mul, norm_pow, Complex.norm_exp]
    apply mul_le_mul (pow_le_pow_left₀ (norm_nonneg _) (hnorm l hl) q) _
      (Real.exp_nonneg _) (pow_nonneg hA q)
    apply Real.exp_le_exp.mpr
    rw [Complex.mul_re]
    have hreal := mul_le_mul_of_nonneg_right (hgap l hl) hx
    have hib : -((a l - b).im * z.im) ≤ M * Y := by
      calc
        _ ≤ |(a l - b).im * z.im| := neg_le_abs _
        _ = |(a l - b).im| * |z.im| := abs_mul _ _
        _ ≤ M * Y := mul_le_mul (him l hl) hy (abs_nonneg _) hM
    linarith
  calc
    _ ≤ ∑ l ∈ s, ‖(a l - b) ^ q * Complex.exp ((a l - b) * z)‖ := norm_sum_le _ _
    _ ≤ ∑ _l ∈ s, A ^ q * Real.exp (-γ * z.re + M * Y) := Finset.sum_le_sum ht
    _ = _ := by simp [mul_assoc]

/-- Exact decomposition into two selected exponentials and the actual remainder. -/
theorem finite_two_term_normalization {s : Finset ℕ} {a : ℕ → ℂ}
    {j k : ℕ} (hj : j ∈ s) (hk : k ∈ s) (hjk : j ≠ k) (z : ℂ) :
    Complex.exp (-(a k * z)) * (∑ l ∈ s, Complex.exp (a l * z)) =
      1 + Complex.exp ((a j - a k) * z) +
        finiteExponentialRemainder ((s.erase j).erase k) a (a k) 0 z := by
  have hk' : k ∈ s.erase j := Finset.mem_erase.mpr ⟨Ne.symm hjk, hk⟩
  have hsum := Finset.sum_erase_add (s := s) (a := j) (f := fun l => Complex.exp (a l * z)) hj
  have hsum' := Finset.sum_erase_add (s := s.erase j) (a := k)
    (f := fun l => Complex.exp (a l * z)) hk'
  rw [← hsum, ← hsum', mul_add, mul_add]
  have he (v : ℂ) : Complex.exp (-(a k * z)) * Complex.exp (v * z) =
      Complex.exp ((v - a k) * z) := by rw [← Complex.exp_add]; congr 1; ring
  rw [he, he, sub_self, zero_mul, Complex.exp_zero]
  rw [Finset.mul_sum]
  have hs : (∑ l ∈ (s.erase j).erase k,
      Complex.exp (-(a k * z)) * Complex.exp (a l * z)) =
      finiteExponentialRemainder ((s.erase j).erase k) a (a k) 0 z := by
    unfold finiteExponentialRemainder
    simp only [pow_zero, one_mul, he]
  rw [hs]
  ring

/-- Paper IV's normalized remainder, including every derivative jet. -/
def signedExponentialRemainder (N : ℕ) (omega rho : ℂ) (q : ℕ) (z : ℂ) : ℂ :=
  finiteExponentialRemainder (((Finset.range N).erase 0).erase (N - 1))
    (fun l => rho * omega ^ l) (rho * omega ^ (N - 1)) q z

theorem signed_two_term_normalization {N : ℕ} (hN : 2 ≤ N)
    (omega rho z : ℂ) :
    (N : ℂ) * Complex.exp (-(rho * omega ^ (N - 1) * z)) *
      entireSigned N 0 omega rho z =
      1 + Complex.exp ((rho - rho * omega ^ (N - 1)) * z) +
        signedExponentialRemainder N omega rho 0 z := by
  rw [entireSigned_zero_eq_average]
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast (show N ≠ 0 by omega)
  have he : (N : ℂ) * Complex.exp (-(rho * omega ^ (N - 1) * z)) *
      ((N : ℂ)⁻¹ * ∑ l ∈ Finset.range N, Complex.exp (rho * omega ^ l * z)) =
      Complex.exp (-(rho * omega ^ (N - 1) * z)) *
        ∑ l ∈ Finset.range N, Complex.exp (rho * omega ^ l * z) := by field_simp
  rw [he]
  simpa [signedExponentialRemainder] using finite_two_term_normalization
    (a := fun l => rho * omega ^ l)
    (Finset.mem_range.mpr (show 0 < N by omega))
    (Finset.mem_range.mpr (show N - 1 < N by omega)) (show 0 ≠ N - 1 by omega) z

/-- The normalized and original signed denominators have exactly the same zeros. -/
theorem signed_two_term_zero_iff {N : ℕ} (hN : 2 ≤ N) (omega rho z : ℂ) :
    entireSigned N 0 omega rho z = 0 ↔
      1 + Complex.exp ((rho - rho * omega ^ (N - 1)) * z) +
        signedExponentialRemainder N omega rho 0 z = 0 := by
  rw [← signed_two_term_normalization hN omega rho z]
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast (show N ≠ 0 by omega)
  simp [hn, Complex.exp_ne_zero]

end
end Komorebi.PaperIV
