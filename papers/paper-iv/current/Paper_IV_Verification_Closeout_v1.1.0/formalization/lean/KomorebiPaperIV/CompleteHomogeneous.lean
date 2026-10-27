/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ThetaZeroBell

namespace Komorebi.PaperIV
noncomputable section
open scoped Classical

def powerSumLog (q : ℕ → ℂ) : PowerSeries ℂ :=
  PowerSeries.mk (fun n => if n = 0 then 0 else q n / (n : ℂ))

@[simp] theorem powerSumLog_constantCoeff (q : ℕ → ℂ) : (powerSumLog q).constantCoeff = 0 := by
  simp [powerSumLog]

@[simp] theorem powerSumLog_derivative_coeff (q : ℕ → ℂ) (n : ℕ) :
    PowerSeries.coeff n (PowerSeries.derivative ℂ (powerSumLog q)) = q (n + 1) := by
  simp only [powerSumLog, PowerSeries.coeff_derivative, PowerSeries.coeff_mk, Nat.succ_ne_zero, ↓reduceIte, Nat.cast_add, Nat.cast_one]
  exact div_mul_cancel₀ _ (by exact_mod_cast Nat.succ_ne_zero n)

def homogeneousSeries (q : ℕ → ℂ) : PowerSeries ℂ := formalExpFamily (powerSumLog q) 1

def homogeneousCoeff (q : ℕ → ℂ) (n : ℕ) : ℂ := PowerSeries.coeff n (homogeneousSeries q)

@[simp] theorem homogeneousSeries_constantCoeff (q : ℕ → ℂ) : (homogeneousSeries q).constantCoeff = 1 := by
  exact constantCoeff_formalExpFamily_of_zero (powerSumLog_constantCoeff q) 1

theorem homogeneousSeries_derivative (q : ℕ → ℂ) :
    PowerSeries.derivative ℂ (homogeneousSeries q) =
      homogeneousSeries q * PowerSeries.derivative ℂ (powerSumLog q) := by
  simpa [homogeneousSeries] using derivative_formalExpFamily (powerSumLog_constantCoeff q) (1 : ℂ)

theorem homogeneousCoeff_recurrence (q : ℕ → ℂ) (n : ℕ) :
    (n + 1 : ℂ) * homogeneousCoeff q (n + 1) =
      ∑ k ∈ Finset.range (n + 1), homogeneousCoeff q k * q (n - k + 1) := by
  have h := congrArg (PowerSeries.coeff n) (homogeneousSeries_derivative q)
  rw [PowerSeries.coeff_derivative, PowerSeries.coeff_mul,
    Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at h
  simpa [homogeneousCoeff, mul_comm] using h

def homogeneousGeometric (a : ℂ) : PowerSeries ℂ := PowerSeries.mk (fun n => a ^ n)

@[simp] theorem homogeneousGeometric_coeff (a : ℂ) (n : ℕ) :
    PowerSeries.coeff n (homogeneousGeometric a) = a ^ n := by simp [homogeneousGeometric]

@[simp] theorem homogeneousGeometric_constantCoeff (a : ℂ) :
    (homogeneousGeometric a).constantCoeff = 1 := by simp [homogeneousGeometric]

theorem homogeneousGeometric_inverse (a : ℂ) :
    homogeneousGeometric a * (1 - PowerSeries.C a * PowerSeries.X) = 1 := by
  have h := congrArg (PowerSeries.rescale a) (PowerSeries.mk_one_mul_one_sub_eq_one ℂ)
  simpa [PowerSeries.rescale_mk, homogeneousGeometric] using h

theorem homogeneousGeometric_derivative (a : ℂ) :
    PowerSeries.derivative ℂ (homogeneousGeometric a) =
      homogeneousGeometric a * (PowerSeries.C a * homogeneousGeometric a) := by
  have h := congrArg (PowerSeries.derivative ℂ) (homogeneousGeometric_inverse a)
  simp [Derivation.leibniz, smul_eq_mul] at h
  have he : PowerSeries.derivative ℂ (homogeneousGeometric a) *
      (1 - PowerSeries.C a * PowerSeries.X) = homogeneousGeometric a * PowerSeries.C a := by
    linear_combination h
  calc
    _ = PowerSeries.derivative ℂ (homogeneousGeometric a) *
        ((1 - PowerSeries.C a * PowerSeries.X) * homogeneousGeometric a) := by
      rw [mul_comm (1 - PowerSeries.C a * PowerSeries.X), homogeneousGeometric_inverse, mul_one]
    _ = (PowerSeries.derivative ℂ (homogeneousGeometric a) *
        (1 - PowerSeries.C a * PowerSeries.X)) * homogeneousGeometric a := by ring
    _ = (homogeneousGeometric a * PowerSeries.C a) * homogeneousGeometric a := by rw [he]
    _ = _ := by ring

def finiteHomogeneousSeries {ι : Type*} (a : ι → ℂ) (S : Finset ι) : PowerSeries ℂ :=
  ∏ i ∈ S, homogeneousGeometric (a i)

@[simp] theorem finiteHomogeneousSeries_constantCoeff {ι : Type*} (a : ι → ℂ) (S : Finset ι) :
    (finiteHomogeneousSeries a S).constantCoeff = 1 := by simp [finiteHomogeneousSeries]

theorem finiteHomogeneousSeries_derivative {ι : Type*} (a : ι → ℂ) (S : Finset ι) :
    PowerSeries.derivative ℂ (finiteHomogeneousSeries a S) =
      finiteHomogeneousSeries a S * ∑ i ∈ S, PowerSeries.C (a i) * homogeneousGeometric (a i) := by
  induction S using Finset.induction_on with
  | empty => simp [finiteHomogeneousSeries]
  | @insert i S hi ih =>
      simp only [finiteHomogeneousSeries, Finset.prod_insert hi] at ih ⊢
      rw [Derivation.leibniz, homogeneousGeometric_derivative, ih, Finset.sum_insert hi]
      ring

theorem finiteHomogeneousSeries_eq_homogeneous {ι : Type*} (a : ι → ℂ) (S : Finset ι) :
    finiteHomogeneousSeries a S = homogeneousSeries (fun m => ∑ i ∈ S, a i ^ m) := by
  have he : (∑ i ∈ S, PowerSeries.C (a i) * homogeneousGeometric (a i)) =
      PowerSeries.derivative ℂ (powerSumLog (fun m => ∑ i ∈ S, a i ^ m)) := by
    ext n
    simp [pow_succ, mul_comm]
  apply powerSeries_linear_ode_unique (H := PowerSeries.derivative ℂ (powerSumLog (fun m => ∑ i ∈ S, a i ^ m)))
  · simp
  · rw [finiteHomogeneousSeries_derivative, he]
  · exact homogeneousSeries_derivative _

/-- The finite coefficients are precisely the complete homogeneous monomial sums. -/
theorem finiteHomogeneousSeries_monomials {ι : Type*} (a : ι → ℂ) (S : Finset ι) (n : ℕ) :
    PowerSeries.coeff n (finiteHomogeneousSeries a S) =
      ∑ l ∈ S.finsuppAntidiag n, ∏ i ∈ S, a i ^ (l i) := by
  simp [finiteHomogeneousSeries, PowerSeries.coeff_prod]

end
end Komorebi.PaperIV
