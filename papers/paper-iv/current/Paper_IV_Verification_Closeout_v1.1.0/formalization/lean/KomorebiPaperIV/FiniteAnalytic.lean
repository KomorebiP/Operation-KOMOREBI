/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.CyclicFilters
import KomorebiPaperIV.SectionCycles
import Mathlib.RingTheory.RootsOfUnity.Complex

/-!
# Finite root-of-unity representations

This file connects the coefficient-defined cyclic projector used elsewhere in
the Paper IV checkpoint to the explicit finite Fourier average over a primitive
root of unity.  Specializing the input series to the formal exponential gives
the transfer sections.  Rescaling by an `N`th root of `-1` gives the signed
sections and, in residue zero, the distinguished denominator representation.

The results here are identities of formal power series.  They do not assert
analytic convergence, holomorphy, or pointwise evaluation of those series.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

/-- The finite Fourier average of a formal power series over powers of `omega`. -/
def finiteRootAverage (N j : ℕ) (omega : ℂ) (f : ℂ⟦X⟧) : ℂ⟦X⟧ :=
  PowerSeries.C ((N : ℂ)⁻¹) *
    ∑ ell ∈ Finset.range N,
      PowerSeries.C (((omega ^ j)⁻¹) ^ ell) *
        PowerSeries.rescale (omega ^ ell) f

private theorem finite_geometric_sum_filter {N j n : ℕ} (hN : 0 < N)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) :
    ∑ ell ∈ Finset.range N,
        (((omega ^ j)⁻¹) ^ ell * (omega ^ ell) ^ n) =
      if n % N = j % N then (N : ℂ) else 0 := by
  let b : ℂ := (omega ^ j)⁻¹ * omega ^ n
  have homega0 : omega ≠ 0 := homega.ne_zero hN.ne'
  have hsummand (ell : ℕ) :
      ((omega ^ j)⁻¹) ^ ell * (omega ^ ell) ^ n = b ^ ell := by
    simp only [b, ← pow_mul, mul_pow]
    rw [Nat.mul_comm ell n]
  simp_rw [hsummand]
  have hb_one_iff : b = 1 ↔ n % N = j % N := by
    rw [show b = (omega ^ j)⁻¹ * omega ^ n by rfl,
      inv_mul_eq_one₀ (pow_ne_zero j homega0)]
    rw [eq_comm]
    simpa only [homega.eq_orderOf, Nat.ModEq] using
      (homega.isOfFinOrder hN.ne').pow_eq_pow_iff_modEq (n := n) (m := j)
  have hbpow : b ^ N = 1 := by
    simp only [b, mul_pow, inv_pow, ← pow_mul]
    rw [mul_comm j N, mul_comm n N, pow_mul, pow_mul, homega.pow_eq_one]
    simp
  by_cases hres : n % N = j % N
  · have hb : b = 1 := hb_one_iff.2 hres
    simp [hres, hb]
  · have hbne : b ≠ 1 := fun hb => hres (hb_one_iff.1 hb)
    have hmul : (b - 1) * ∑ ell ∈ Finset.range N, b ^ ell = 0 := by
      rw [mul_geom_sum, hbpow, sub_self]
    have hsum : ∑ ell ∈ Finset.range N, b ^ ell = 0 :=
      (mul_eq_zero.mp hmul).resolve_left (sub_ne_zero.mpr hbne)
    simp [hres, hsum]

@[simp]
theorem coeff_finiteRootAverage {N : ℕ} (hN : 0 < N) (j n : ℕ)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) (f : ℂ⟦X⟧) :
    PowerSeries.coeff n (finiteRootAverage N j omega f) =
      if n % N = j % N then PowerSeries.coeff n f else 0 := by
  rw [finiteRootAverage, PowerSeries.coeff_C_mul, map_sum]
  simp only [PowerSeries.coeff_C_mul, PowerSeries.coeff_rescale]
  simp_rw [← mul_assoc]
  rw [← Finset.sum_mul]
  rw [finite_geometric_sum_filter hN homega]
  by_cases hres : n % N = j % N
  · simp [hres, Nat.cast_ne_zero.mpr hN.ne']
  · simp [hres]

/-- The explicit finite root average agrees with the coefficient projector. -/
theorem finiteRootAverage_eq_cyclicProjector {N : ℕ} (hN : 0 < N) (j : ℕ)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) (f : ℂ⟦X⟧) :
    finiteRootAverage N j omega f = cyclicProjector N j f := by
  ext n
  rw [coeff_finiteRootAverage hN j n homega, coeff_cyclicProjector]

/-- Root-of-unity averaging of the formal exponential gives a transfer section. -/
theorem finiteRootAverage_exp_eq_transferSection {N : ℕ} (hN : 0 < N)
    {j : ℕ} (hjN : j < N) {omega : ℂ} (homega : IsPrimitiveRoot omega N) :
    finiteRootAverage N j omega (PowerSeries.exp ℂ) =
      transferSection N j (1 : ℂ) := by
  ext n
  rw [coeff_finiteRootAverage hN j n homega, coeff_transferSection]
  simp only [PowerSeries.coeff_exp, transferSectionCoeff]
  rw [Nat.mod_eq_of_lt hjN]
  by_cases hres : n % N = j
  · simp [hres]
  · simp [hres]

/-- Root-of-unity averaging of a rescaled formal exponential gives the
corresponding transfer section. -/
theorem finiteRootAverage_rescale_exp_eq_transferSection {N : ℕ} (hN : 0 < N)
    {j : ℕ} (hjN : j < N) {omega : ℂ} (homega : IsPrimitiveRoot omega N)
    (rho : ℂ) :
    finiteRootAverage N j omega
        (PowerSeries.rescale rho (PowerSeries.exp ℂ)) =
      transferSection N j rho := by
  ext n
  rw [coeff_finiteRootAverage hN j n homega, coeff_transferSection]
  simp only [PowerSeries.coeff_rescale, PowerSeries.coeff_exp, transferSectionCoeff]
  rw [Nat.mod_eq_of_lt hjN]
  by_cases hres : n % N = j
  · simp [hres]
  · simp [hres]

private theorem signedSectionCoeff_eq_inv_pow_mul_transferSectionCoeff
    {N j n : ℕ} (hN : 0 < N) (hjN : j < N) {rho : ℂ}
    (hrho : rho ^ N = -1) :
    signedSectionCoeff (R := ℂ) N j n =
      (rho ^ j)⁻¹ * transferSectionCoeff N j rho n := by
  have hrho0 : rho ≠ 0 := by
    intro hzero
    subst rho
    simp [hN.ne'] at hrho
  rw [signedSectionCoeff, transferSectionCoeff]
  by_cases hres : n % N = j
  · simp only [hres, ↓reduceIte]
    have hn : n = N * (n / N) + j := by
      calc
        n = N * (n / N) + n % N := (Nat.div_add_mod n N).symm
        _ = N * (n / N) + j := by rw [hres]
    have hdiv : (N * (n / N) + j) / N = n / N := by
      rw [Nat.add_comm, Nat.add_mul_div_left j (n / N) hN,
        Nat.div_eq_of_lt hjN, zero_add]
    rw [hn, hdiv, pow_add, pow_mul, hrho]
    field_simp
  · simp [hres]

/-- A chosen `N`th root of `-1` converts transfer sections into signed
sections, including the normalizing factor `rho ^ (-j)`. -/
theorem signedSection_eq_inv_pow_mul_transferSection {N : ℕ} (hN : 0 < N)
    {j : ℕ} (hjN : j < N) {rho : ℂ} (hrho : rho ^ N = -1) :
    signedSection (R := ℂ) N j =
      PowerSeries.C ((rho ^ j)⁻¹) * transferSection N j rho := by
  ext n
  rw [PowerSeries.coeff_C_mul, coeff_signedSection, coeff_transferSection,
    signedSectionCoeff_eq_inv_pow_mul_transferSectionCoeff hN hjN hrho]
  rw [mul_assoc]

/-- The general formal finite exponential representation of a signed section. -/
theorem signedSection_eq_finiteRootAverage_rescale_exp {N : ℕ} (hN : 0 < N)
    {j : ℕ} (hjN : j < N) {omega rho : ℂ}
    (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1) :
    signedSection (R := ℂ) N j =
      PowerSeries.C ((rho ^ j)⁻¹) *
        finiteRootAverage N j omega
          (PowerSeries.rescale rho (PowerSeries.exp ℂ)) := by
  rw [signedSection_eq_inv_pow_mul_transferSection hN hjN hrho,
    finiteRootAverage_rescale_exp_eq_transferSection hN hjN homega]

/-- Residue zero expands as the unweighted average over the `N` roots
`rho * omega ^ ell` of `-1`, the formal counterpart of the distinguished
denominator's finite exponential representation. -/
theorem signedSection_zero_eq_finite_exponential_average {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1) :
    signedSection (R := ℂ) N 0 =
      PowerSeries.C ((N : ℂ)⁻¹) *
        ∑ ell ∈ Finset.range N,
          PowerSeries.rescale (rho * omega ^ ell) (PowerSeries.exp ℂ) := by
  rw [signedSection_eq_finiteRootAverage_rescale_exp hN (Nat.zero_lt_of_lt hN)
    homega hrho]
  simp [finiteRootAverage, PowerSeries.rescale_rescale]

end

end Komorebi.PaperIV
