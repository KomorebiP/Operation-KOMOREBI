/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.FiniteAnalytic
import Mathlib.RingTheory.MvPowerSeries.Basic

/-!
# Early algebraic completion for Paper IV

This file supplies formal-power-series counterparts of the early algebraic
results that were not included in checkpoint 0.2.0: the covariance
characterization of cyclic packets, the transfer and signed addition laws, and
the coefficient-level rotational and conjugation symmetries of the signed
denominator.

The addition laws are identities in two-variable formal power series.  The
definition `bivariateExponentialGeneratingSeries` is precisely the formal
expansion of an exponential generating series after replacing its variable by
`X₀ + X₁`; `separatedExponentialGeneratingSeries` is the separated product in
the two variables.  No analytic convergence or pointwise evaluation is used.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

/-! ## Formal covariance -/

/-- A formal series is fixed by the `j`th cyclic projector exactly when it has
weight `j` under rescaling by a primitive `N`th root of unity. -/
theorem cyclicProjector_fixed_iff_rescale_covariant {N j : ℕ} (hN : 0 < N)
    (hjN : j < N) {omega : ℂ} (homega : IsPrimitiveRoot omega N)
    (f : ℂ⟦X⟧) :
    cyclicProjector N j f = f ↔
      PowerSeries.rescale omega f = PowerSeries.C (omega ^ j) * f := by
  constructor
  · intro hfixed
    ext n
    have hcoeff := congrArg (PowerSeries.coeff n) hfixed
    rw [coeff_cyclicProjector, Nat.mod_eq_of_lt hjN] at hcoeff
    rw [PowerSeries.coeff_rescale, PowerSeries.coeff_C_mul]
    by_cases hres : n % N = j
    · have hpow : omega ^ n = omega ^ j := by
        apply (homega.isOfFinOrder hN.ne').pow_eq_pow_iff_modEq.mpr
        rw [← homega.eq_orderOf]
        exact hres.trans (Nat.mod_eq_of_lt hjN).symm
      rw [hpow]
    · simp [hres] at hcoeff
      simp [hcoeff]
  · intro hcov
    ext n
    rw [coeff_cyclicProjector, Nat.mod_eq_of_lt hjN]
    by_cases hres : n % N = j
    · simp [hres]
    · simp only [hres, ↓reduceIte]
      have hcoeff := congrArg (PowerSeries.coeff n) hcov
      rw [PowerSeries.coeff_rescale, PowerSeries.coeff_C_mul] at hcoeff
      have hpow : omega ^ n ≠ omega ^ j := by
        intro heq
        have hmodeq :=
          (homega.isOfFinOrder hN.ne').pow_eq_pow_iff_modEq.mp heq
        have hmod : n % N = j % N := by
          simpa only [homega.eq_orderOf, Nat.ModEq] using hmodeq
        exact hres (by simpa [Nat.mod_eq_of_lt hjN] using hmod)
      have hzero : (omega ^ n - omega ^ j) * PowerSeries.coeff n f = 0 := by
        rw [sub_mul, hcoeff, sub_self]
      exact ((mul_eq_zero.mp hzero).resolve_left (sub_ne_zero.mpr hpow)).symm

/-- Range formulation of the formal covariance characterization. -/
theorem cyclicProjector_mem_range_iff_rescale_covariant {N j : ℕ} (hN : 0 < N)
    (hjN : j < N) {omega : ℂ} (homega : IsPrimitiveRoot omega N)
    (f : ℂ⟦X⟧) :
    (∃ g : ℂ⟦X⟧, cyclicProjector N j g = f) ↔
      PowerSeries.rescale omega f = PowerSeries.C (omega ^ j) * f := by
  rw [← cyclicProjector_fixed_iff_rescale_covariant hN hjN homega]
  constructor
  · rintro ⟨g, rfl⟩
    exact cyclicProjector_idempotent N j g
  · intro hfixed
    exact ⟨f, hfixed⟩

/-! ## Two-variable exponential-generating series -/

/-- The two-variable formal expansion of an EGF after the substitution
`X ↦ X₀ + X₁`. -/
def bivariateExponentialGeneratingSeries {R : Type*} [CommRing R] [Algebra ℚ R]
    (a : ℕ → R) : MvPowerSeries (Fin 2) R :=
  fun d =>
    a (d 0 + d 1) * algebraMap ℚ R (1 / (d 0).factorial : ℚ) *
      algebraMap ℚ R (1 / (d 1).factorial : ℚ)

@[simp]
theorem coeff_bivariateExponentialGeneratingSeries {R : Type*}
    [CommRing R] [Algebra ℚ R] (a : ℕ → R) (d : Fin 2 →₀ ℕ) :
    MvPowerSeries.coeff d (bivariateExponentialGeneratingSeries a) =
      a (d 0 + d 1) * algebraMap ℚ R (1 / (d 0).factorial : ℚ) *
        algebraMap ℚ R (1 / (d 1).factorial : ℚ) :=
  rfl

/-- The product of two EGFs placed in the two separate formal variables. -/
def separatedExponentialGeneratingSeries {R : Type*} [CommRing R] [Algebra ℚ R]
    (a b : ℕ → R) : MvPowerSeries (Fin 2) R :=
  fun d =>
    (a (d 0) * algebraMap ℚ R (1 / (d 0).factorial : ℚ)) *
      (b (d 1) * algebraMap ℚ R (1 / (d 1).factorial : ℚ))

@[simp]
theorem coeff_separatedExponentialGeneratingSeries {R : Type*}
    [CommRing R] [Algebra ℚ R] (a b : ℕ → R) (d : Fin 2 →₀ ℕ) :
    MvPowerSeries.coeff d (separatedExponentialGeneratingSeries a b) =
      (a (d 0) * algebraMap ℚ R (1 / (d 0).factorial : ℚ)) *
        (b (d 1) * algebraMap ℚ R (1 / (d 1).factorial : ℚ)) :=
  rfl

/-! ## Transfer addition -/

private theorem transferSectionCoeff_addition {R : Type*} [CommRing R]
    {N k : ℕ} (hN : 0 < N) (lambda : R) (a b : ℕ) :
    transferSectionCoeff N k lambda (a + b) =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k then
          transferSectionCoeff N i lambda a * transferSectionCoeff N j lambda b
        else 0 := by
  rw [Finset.sum_eq_single (a % N)]
  · rw [Finset.sum_eq_single (b % N)]
    · simp only [transferSectionCoeff]
      change (if (a + b) % N = k then lambda ^ (a + b) else 0) =
        if (a % N + b % N) % N = k then lambda ^ a * lambda ^ b else 0
      rw [← Nat.add_mod, pow_add]
    · intro j hj hne
      have hb : b % N ≠ j := by simpa [eq_comm] using hne
      simp [transferSectionCoeff, hb]
    · exact fun hmem => (hmem (Finset.mem_range.mpr (Nat.mod_lt b hN))).elim
  · intro i hi hne
    have ha : a % N ≠ i := by simpa [eq_comm] using hne
    simp [transferSectionCoeff, ha]
  · exact fun hmem => (hmem (Finset.mem_range.mpr (Nat.mod_lt a hN))).elim

/-- Exact bivariate formal-power-series addition law for transfer sections. -/
theorem transferSection_addition {R : Type*} [CommRing R] [Algebra ℚ R]
    {N k : ℕ} (hN : 0 < N) (_hkN : k < N) (lambda : R) :
    bivariateExponentialGeneratingSeries (transferSectionCoeff N k lambda) =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k then
          separatedExponentialGeneratingSeries
            (transferSectionCoeff N i lambda) (transferSectionCoeff N j lambda)
        else 0 := by
  ext d
  simp only [coeff_bivariateExponentialGeneratingSeries, map_sum]
  rw [transferSectionCoeff_addition hN]
  simp only [Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  by_cases hlabel : (i + j) % N = k
  · simp [hlabel, coeff_separatedExponentialGeneratingSeries]
    ring
  · simp [hlabel]

/-! ## Signed addition -/

private theorem signedSectionCoeff_addition {R : Type*} [CommRing R]
    {N k : ℕ} (hN : 0 < N) (a b : ℕ) :
    signedSectionCoeff (R := R) N k (a + b) =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k then
          (-1 : R) ^ ((i + j) / N) *
            signedSectionCoeff (R := R) N i a *
              signedSectionCoeff (R := R) N j b
        else 0 := by
  rw [Finset.sum_eq_single (a % N)]
  · rw [Finset.sum_eq_single (b % N)]
    · simp only [signedSectionCoeff]
      change (if (a + b) % N = k then (-1 : R) ^ ((a + b) / N) else 0) =
        if (a % N + b % N) % N = k then
          (-1 : R) ^ ((a % N + b % N) / N) *
            (-1 : R) ^ (a / N) * (-1 : R) ^ (b / N)
        else 0
      rw [← Nat.add_mod]
      by_cases hres : (a + b) % N = k
      · simp only [hres, ↓reduceIte]
        rw [Nat.add_div hN]
        by_cases hcarry : N ≤ a % N + b % N
        · simp only [hcarry, ↓reduceIte]
          have hq : (a % N + b % N) / N = 1 := by
            apply Nat.le_antisymm
            · exact Nat.div_le_iff_le_mul hN |>.2 (by
                have ha := Nat.mod_lt a hN
                have hb := Nat.mod_lt b hN
                omega)
            · exact Nat.le_div_iff_mul_le hN |>.2 (by simpa using hcarry)
          rw [hq, pow_add, pow_add]
          ring
        · simp only [hcarry, ↓reduceIte]
          have hq : (a % N + b % N) / N = 0 :=
            Nat.div_eq_of_lt (Nat.lt_of_not_ge hcarry)
          simp only [hq, pow_zero, mul_one, pow_add]
          ring
      · simp only [hres, ↓reduceIte]
    · intro j hj hne
      have hb : b % N ≠ j := by simpa [eq_comm] using hne
      simp [signedSectionCoeff, hb]
    · exact fun hmem => (hmem (Finset.mem_range.mpr (Nat.mod_lt b hN))).elim
  · intro i hi hne
    have ha : a % N ≠ i := by simpa [eq_comm] using hne
    simp [signedSectionCoeff, ha]
  · exact fun hmem => (hmem (Finset.mem_range.mpr (Nat.mod_lt a hN))).elim

/-- Exact bivariate formal-power-series twisted addition law for signed
sections.  Since `i,j < N`, the displayed exponent `(i+j)/N` is the manuscript's
carry `⌊(i+j)/N⌋`, hence is either zero or one. -/
theorem signedSection_addition {R : Type*} [CommRing R] [Algebra ℚ R]
    {N k : ℕ} (hN : 0 < N) (_hkN : k < N) :
    bivariateExponentialGeneratingSeries
        (signedSectionCoeff (R := R) N k) =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k then
          MvPowerSeries.C ((-1 : R) ^ ((i + j) / N)) *
            separatedExponentialGeneratingSeries
              (signedSectionCoeff (R := R) N i)
              (signedSectionCoeff (R := R) N j)
        else 0 := by
  ext d
  simp only [coeff_bivariateExponentialGeneratingSeries, map_sum]
  rw [signedSectionCoeff_addition hN]
  simp only [Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  by_cases hlabel : (i + j) % N = k
  · simp only [hlabel, ↓reduceIte]
    rw [MvPowerSeries.coeff_C_mul,
      coeff_separatedExponentialGeneratingSeries]
    ring
  · simp only [hlabel, ↓reduceIte, MvPowerSeries.coeff_zero]
    ring

/-! ## Distinguished-denominator symmetries -/

/-- Coefficient-level rotational invariance of the signed denominator. -/
theorem signedDenominator_rescale_of_pow_eq_one {R : Type*} [CommRing R]
    [Algebra ℚ R] {N : ℕ} {omega : R}
    (homega : omega ^ N = 1) :
    PowerSeries.rescale omega (signedSection (R := R) N 0) =
      signedSection (R := R) N 0 := by
  ext n
  rw [PowerSeries.coeff_rescale, coeff_signedSection]
  rw [signedSectionCoeff]
  by_cases hres : n % N = 0
  · simp only [hres, ↓reduceIte]
    have hn : n = N * (n / N) := by
      simpa [hres] using (Nat.div_add_mod n N).symm
    rw [hn, pow_mul, homega, one_pow, one_mul]
  · simp [hres]

/-- Coefficientwise complex conjugation fixes the signed denominator. -/
theorem signedDenominator_map_conj (N : ℕ) :
    PowerSeries.map (starRingEnd ℂ)
        (signedSection (R := ℂ) N 0) =
      signedSection (R := ℂ) N 0 := by
  ext n
  rw [PowerSeries.coeff_map, coeff_signedSection]
  by_cases hres : n % N = 0
  · simp [signedSectionCoeff, hres]
  · simp [signedSectionCoeff, hres]

end

end Komorebi.PaperIV
