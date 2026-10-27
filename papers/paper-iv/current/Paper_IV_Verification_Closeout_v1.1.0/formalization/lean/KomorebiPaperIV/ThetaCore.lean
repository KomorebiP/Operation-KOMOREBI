/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.ReciprocalCore

/-!
# Scaled reciprocal coupling and theta coefficients

This file gives a branch-free formal-series definition of the theta family
from Paper IV and proves its exact reconstruction from the named reciprocal
coefficients.  The reduced variable is `w = z^N`.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

variable {R : Type*} [CommRing R] [Algebra ℚ R]

omit [Algebra ℚ R] in
/-- Block coefficients commute with rescaling in the expected way. -/
theorem blockCoeff_rescale (N n : ℕ) (a : R) (f : R⟦X⟧) :
    blockCoeff N n (PowerSeries.rescale a f) = a ^ n * blockCoeff N n f := by
  rw [blockCoeff, PowerSeries.coeff_rescale, blockCoeff]
  ring

/-- The reduced theta generating series
`Delta_N(-u^N w)^(-1) Delta_N(-w)^(-u)`.

Because `H_N(z) = Delta_N(-z^N)`, this is exactly the formal version of
`H_N(uz)^(-1) H_N(z)^(-u)` after putting `w = z^N`.
-/
def thetaSeries (N : ℕ) (u : R) : R⟦X⟧ :=
  PowerSeries.rescale (-u ^ N) (reciprocalSeries N 1) *
    PowerSeries.rescale (-1) (reciprocalSeries N u)

/-- Factorially normalized theta coefficient `Theta_{N,n}(u)`. -/
def thetaCoeff (N n : ℕ) (u : R) : R :=
  blockCoeff N n (thetaSeries N u)

@[simp]
theorem thetaSeries_zero (N : ℕ) (hN : 0 < N) :
    thetaSeries (R := R) N 0 = 1 := by
  simp [thetaSeries, hN.ne']

@[simp]
theorem thetaCoeff_zero_parameter (N : ℕ) (hN : 0 < N) :
    thetaCoeff (R := R) N 0 0 = 1 := by
  rw [thetaCoeff, thetaSeries_zero N hN]
  simp [blockCoeff]

theorem thetaCoeff_zero_parameter_of_pos (N : ℕ) (hN : 0 < N)
    {n : ℕ} (hn : 0 < n) :
    thetaCoeff (R := R) N n 0 = 0 := by
  rw [thetaCoeff, thetaSeries_zero N hN]
  simp [blockCoeff, PowerSeries.coeff_one, hn.ne']

/-- Exact theta reconstruction before extracting the common sign. -/
theorem thetaCoeff_reconstruction_unfactored (N n : ℕ) (u : R) :
    thetaCoeff N n u =
      ∑ q ∈ Finset.range (n + 1),
        ((N * n).choose (N * q) : R) *
          (-u ^ N) ^ q * reciprocalCoeff N q 1 *
          (-1 : R) ^ (n - q) * reciprocalCoeff N (n - q) u := by
  rw [thetaCoeff, thetaSeries, blockCoeff_mul]
  apply Finset.sum_congr rfl
  intro q hq
  rw [blockCoeff_rescale, blockCoeff_rescale]
  simp only [reciprocalCoeff]
  ring

/-- Paper IV's theta reconstruction formula. -/
theorem thetaCoeff_reconstruction (N n : ℕ) (u : R) :
    thetaCoeff N n u =
      (-1 : R) ^ n *
        ∑ q ∈ Finset.range (n + 1),
          ((N * n).choose (N * q) : R) *
            reciprocalCoeff N q 1 * u ^ (N * q) *
              reciprocalCoeff N (n - q) u := by
  rw [thetaCoeff_reconstruction_unfactored, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro q hq
  have hqn : q ≤ n := Nat.le_of_lt_succ (Finset.mem_range.mp hq)
  have hsign : (-1 : R) ^ q * (-1 : R) ^ (n - q) = (-1 : R) ^ n := by
    rw [← pow_add, Nat.add_sub_of_le hqn]
  rw [neg_pow]
  have hpow : (u ^ N) ^ q = u ^ (N * q) := by rw [← pow_mul]
  rw [hpow]
  calc
    ((N * n).choose (N * q) : R) *
          ((-1 : R) ^ q * u ^ (N * q)) * reciprocalCoeff N q 1 *
          (-1 : R) ^ (n - q) * reciprocalCoeff N (n - q) u =
        ((-1 : R) ^ q * (-1 : R) ^ (n - q)) *
          (((N * n).choose (N * q) : R) * reciprocalCoeff N q 1 *
            u ^ (N * q) * reciprocalCoeff N (n - q) u) := by ring
    _ = (-1 : R) ^ n *
          (((N * n).choose (N * q) : R) * reciprocalCoeff N q 1 *
            u ^ (N * q) * reciprocalCoeff N (n - q) u) := by rw [hsign]

/-- For even `N`, the theta generating series also specializes to one at
`u = -1`.  This is the formal source of the manuscript's `u + 1` factor. -/
theorem thetaSeries_neg_one_of_even (N : ℕ) (hN : Even N) :
    thetaSeries (R := R) N (-1) = 1 := by
  rw [thetaSeries, hN.neg_one_pow]
  rw [← map_mul, reciprocalSeries_add, add_neg_cancel, reciprocalSeries_zero]
  simp

theorem thetaCoeff_neg_one_of_even_of_pos (N : ℕ) (hN : Even N)
    {n : ℕ} (hn : 0 < n) :
    thetaCoeff (R := R) N n (-1) = 0 := by
  rw [thetaCoeff, thetaSeries_neg_one_of_even N hN]
  simp [blockCoeff, PowerSeries.coeff_one, hn.ne']

end

end Komorebi.PaperIV
