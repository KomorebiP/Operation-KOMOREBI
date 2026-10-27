/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.SectionCycles
import Mathlib.Data.Nat.Factorial.BigOperators
import Mathlib.RingTheory.Polynomial.Pochhammer
import Mathlib.RingTheory.PowerSeries.Expand

/-!
# Hypergeometric coefficient completion for Paper IV

This file proves the factorial/Pochhammer normalization behind the
hypergeometric form of the transfer sections.  The proof is elementary and
coefficient-level: it groups each factorial block into the `N` rational
parameters `(j+a+1)/N`, for `0 ≤ a < N`.

The full parameter lattice contains one parameter equal to `1` when `j < N`.
Its Pochhammer symbol is `q!`; deleting that entry therefore gives exactly the
usual denominator-parameter list for the manuscript's ordinary
`₀F_{N-1}`.  We package the ordinary hypergeometric coefficient directly as a
formal power series, avoiding analytic convergence claims and the regularized
Gamma normalization used by Mathlib's analytic generalized hypergeometric
function.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

/-- Product of the `N` Pochhammer factors in the full residue-parameter
lattice.  For `j < N`, the factor indexed by `N-j-1` is `(1)_q = q!`. -/
def residuePochhammerProduct (N j q : ℕ) : ℚ :=
  ∏ a ∈ Finset.range N,
    (ascPochhammer ℚ q).eval (((j + a + 1 : ℕ) : ℚ) / (N : ℚ))

private theorem scaled_parameter_step_product {N : ℕ} (hN : 0 < N)
    (j q : ℕ) :
    (N : ℚ) ^ N *
        ∏ a ∈ Finset.range N,
          (((j + a + 1 : ℕ) : ℚ) / (N : ℚ) + (q : ℚ)) =
      ((j + N * q + 1).ascFactorial N : ℚ) := by
  have hNq : (N : ℚ) ≠ 0 := by exact_mod_cast hN.ne'
  simp_rw [show ∀ a : ℕ,
      ((j + a + 1 : ℕ) : ℚ) / (N : ℚ) + (q : ℚ) =
        ((j + N * q + 1 + a : ℕ) : ℚ) / (N : ℚ) by
    intro a
    field_simp
    push_cast
    ring]
  rw [Finset.prod_div_distrib]
  simp only [Finset.prod_const, Finset.card_range]
  field_simp
  rw [Nat.ascFactorial_eq_prod_range, Nat.cast_prod]

/-- Exact factorial split used in the proof of the hypergeometric form:
`(Nq+j)! = j! N^(Nq) ∏ₐ ((j+a+1)/N)_q`. -/
theorem factorial_eq_residuePochhammerProduct {N : ℕ} (hN : 0 < N)
    (j q : ℕ) :
    (j.factorial : ℚ) * (N : ℚ) ^ (N * q) *
        residuePochhammerProduct N j q =
      ((N * q + j).factorial : ℚ) := by
  induction q with
  | zero => simp [residuePochhammerProduct]
  | succ q ih =>
      rw [residuePochhammerProduct]
      simp_rw [ascPochhammer_succ_right, Polynomial.eval_mul,
        Polynomial.eval_add, Polynomial.eval_X, Polynomial.eval_natCast]
      rw [Finset.prod_mul_distrib]
      rw [Nat.mul_succ, pow_add]
      change
        (j.factorial : ℚ) * ((N : ℚ) ^ (N * q) * (N : ℚ) ^ N) *
            (residuePochhammerProduct N j q *
              ∏ a ∈ Finset.range N,
                (((j + a + 1 : ℕ) : ℚ) / (N : ℚ) + (q : ℚ))) =
          (((N * q + N) + j).factorial : ℚ)
      calc
        _ = ((j.factorial : ℚ) * (N : ℚ) ^ (N * q) *
              residuePochhammerProduct N j q) *
            ((N : ℚ) ^ N *
              ∏ a ∈ Finset.range N,
                (((j + a + 1 : ℕ) : ℚ) / (N : ℚ) + (q : ℚ))) := by ring
        _ = ((N * q + j).factorial : ℚ) *
            ((j + N * q + 1).ascFactorial N : ℚ) := by
              rw [ih, scaled_parameter_step_product hN]
        _ = (((N * q + N) + j).factorial : ℚ) := by
              norm_cast
              simpa [add_assoc, add_comm, add_left_comm] using
                Nat.factorial_mul_ascFactorial (N * q + j) N

/-- The coefficient of the ordinary `₀F_{N-1}` after retaining the full
parameter lattice.  The unique `(1)_q=q!` factor is already present in
`residuePochhammerProduct`, so no additional factorial occurs here. -/
def residueZeroFCoeff (N j q : ℕ) : ℚ :=
  (residuePochhammerProduct N j q)⁻¹

/-- Formal hypergeometric series in the compressed variable. -/
def residueZeroFSeries (N j : ℕ) : ℚ⟦X⟧ :=
  PowerSeries.mk fun q => residueZeroFCoeff N j q

@[simp]
theorem coeff_residueZeroFSeries (N j q : ℕ) :
    PowerSeries.coeff q (residueZeroFSeries N j) =
      residueZeroFCoeff N j q := by
  simp [residueZeroFSeries]

/-- Coefficient form of the manuscript's hypergeometric identity.  It states
that the `q`th compressed hypergeometric term, including `j!` and `N^(Nq)`,
is exactly the factorial denominator of the transfer section. -/
theorem residueZeroFCoeff_normalization {N : ℕ} (hN : 0 < N)
    (j q : ℕ) :
    (j.factorial : ℚ)⁻¹ * ((N : ℚ) ^ (N * q))⁻¹ *
        residueZeroFCoeff N j q =
      (((N * q + j).factorial : ℚ))⁻¹ := by
  rw [residueZeroFCoeff]
  rw [← mul_inv, ← mul_inv]
  rw [factorial_eq_residuePochhammerProduct hN]

/-- The omitted manuscript parameter is exactly `1`. -/
theorem residueParameter_eq_one {N j : ℕ} (hN : 0 < N) (hjN : j < N) :
    (((j + (N - j - 1) + 1 : ℕ) : ℚ) / (N : ℚ)) = 1 := by
  have hindex : j + (N - j - 1) + 1 = N := by omega
  rw [hindex]
  norm_num [show (N : ℚ) ≠ 0 by exact_mod_cast hN.ne']

/-- The Pochhammer factor at the omitted parameter is `q!`. -/
theorem omitted_residuePochhammer_eq_factorial {N j : ℕ} (hN : 0 < N)
    (hjN : j < N) (q : ℕ) :
    (ascPochhammer ℚ q).eval
        (((j + (N - j - 1) + 1 : ℕ) : ℚ) / (N : ℚ)) =
      (q.factorial : ℚ) := by
  rw [residueParameter_eq_one hN hjN]
  exact ascPochhammer_eval_one ℚ q

/-- Exact formal-power-series version of the manuscript's hypergeometric
formula, over the rational coefficient field.  The right side is

`(λX)^j / j! · ₀F_{N-1}(; A_{N,j}; (λX)^N / N^N)`,

with `residueZeroFSeries` carrying the ordinary hypergeometric coefficients.
-/
theorem transferSection_eq_residueZeroFSeries {N j : ℕ} (hN : 0 < N)
    (hjN : j < N) (lambda : ℚ) :
    transferSection N j lambda =
      PowerSeries.C (lambda ^ j * (j.factorial : ℚ)⁻¹) *
        (PowerSeries.X ^ j *
          (PowerSeries.rescale
              (lambda ^ N * ((N : ℚ) ^ N)⁻¹)
              (residueZeroFSeries N j)).expand N hN.ne') := by
  ext n
  rw [coeff_transferSection, PowerSeries.coeff_C_mul]
  rw [PowerSeries.coeff_X_pow_mul']
  by_cases hres : n % N = j
  · have hjle : j ≤ n := by
      rw [← hres]
      exact Nat.mod_le n N
    have hn : n = N * (n / N) + j := by
      calc
        n = N * (n / N) + n % N := (Nat.div_add_mod n N).symm
        _ = N * (n / N) + j := by rw [hres]
    have hsub : n - j = N * (n / N) := by omega
    have hdvd : N ∣ n - j := ⟨n / N, hsub⟩
    have hdiv : (n - j) / N = n / N := by
      rw [hsub, Nat.mul_div_cancel_left _ hN]
    simp only [transferSectionCoeff, hres, ↓reduceIte, hjle,
      PowerSeries.coeff_expand, hdvd, hdiv, PowerSeries.coeff_rescale,
      coeff_residueZeroFSeries]
    calc
      lambda ^ n * (1 / (n.factorial : ℚ)) =
          lambda ^ (N * (n / N) + j) *
            (((N * (n / N) + j).factorial : ℚ))⁻¹ := by
              rw [← hn]
              simp only [one_div]
      _ = (lambda ^ j * (j.factorial : ℚ)⁻¹) *
          ((lambda ^ N * ((N : ℚ) ^ N)⁻¹) ^ (n / N) *
            residueZeroFCoeff N j (n / N)) := by
              symm
              calc
                _ = lambda ^ (N * (n / N) + j) *
                    ((j.factorial : ℚ)⁻¹ *
                      ((N : ℚ) ^ (N * (n / N)))⁻¹ *
                        residueZeroFCoeff N j (n / N)) := by
                          simp only [mul_pow, inv_pow, ← pow_mul]
                          ring
                _ = _ := by rw [residueZeroFCoeff_normalization hN]
  · by_cases hjle : j ≤ n
    · have hzero : ¬N ∣ n - j := by
        intro hdvd
        apply hres
        calc
          n % N = ((n - j) + j) % N := by rw [Nat.sub_add_cancel hjle]
          _ = ((n - j) % N + j % N) % N := Nat.add_mod _ _ _
          _ = j := by
            rw [Nat.dvd_iff_mod_eq_zero.mp hdvd, zero_add,
              Nat.mod_eq_of_lt hjN, Nat.mod_eq_of_lt hjN]
      simp [transferSectionCoeff, hres, hjle, PowerSeries.coeff_expand, hzero]
    · simp [transferSectionCoeff, hres, hjle]

end

end Komorebi.PaperIV
