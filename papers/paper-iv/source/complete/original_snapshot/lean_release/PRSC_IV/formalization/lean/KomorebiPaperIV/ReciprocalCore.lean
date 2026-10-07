/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.FormalExponential
import KomorebiPaperIV.SectionCycles
import Mathlib.RingTheory.PowerSeries.Log

/-!
# Manuscript-facing reciprocal core

This file names the reduced denominator, its formal negative logarithm, and
the reciprocal parameter family used in Paper IV.  It closes the semantic gap
between the generic family `formalExpFamily L r` and the manuscript's exact
specialization `L = -log Delta_N`.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- The reduced denominator `Delta_N(w) = sum (-1)^n w^n / (Nn)!`. -/
def reducedDenominator (N : ℕ) : R⟦X⟧ :=
  PowerSeries.mk fun n =>
    algebraMap ℚ R ((-1 : ℚ) ^ n / ((N * n).factorial : ℚ))

@[simp]
theorem coeff_reducedDenominator (N n : ℕ) :
    PowerSeries.coeff n (reducedDenominator (R := R) N) =
      algebraMap ℚ R ((-1 : ℚ) ^ n / ((N * n).factorial : ℚ)) := by
  simp [reducedDenominator]

@[simp]
theorem constantCoeff_reducedDenominator (N : ℕ) :
    PowerSeries.constantCoeff (reducedDenominator (R := R) N) = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff]
  simp

/-- The signed denominator in the `z` variable is obtained from the reduced
denominator by the substitution `w = z^N`. -/
theorem signedSection_zero_eq_expand_reducedDenominator {N : ℕ} (hN : 0 < N) :
    signedSection (R := R) N 0 =
      (reducedDenominator (R := R) N).expand N hN.ne' := by
  ext n
  rw [coeff_signedSection, PowerSeries.coeff_expand]
  by_cases hdvd : N ∣ n
  · have hmod : n % N = 0 := Nat.dvd_iff_mod_eq_zero.mp hdvd
    have hmul : N * (n / N) = n := Nat.mul_div_cancel' hdvd
    simp only [hdvd, ↓reduceIte, signedSectionCoeff, hmod]
    rw [coeff_reducedDenominator, hmul]
    simp only [div_eq_mul_inv, map_mul, map_pow, map_neg, map_one]
    ring
  · have hmod : n % N ≠ 0 := by
      simpa [Nat.dvd_iff_mod_eq_zero] using hdvd
    simp [hdvd, signedSectionCoeff, hmod]

/-- The formal series `-log Delta_N`, normalized to have constant term zero. -/
def negativeLogDenominator (N : ℕ) : R⟦X⟧ :=
  -PowerSeries.logOf (reducedDenominator (R := R) N)

@[simp]
theorem constantCoeff_negativeLogDenominator (N : ℕ) :
    PowerSeries.constantCoeff (negativeLogDenominator (R := R) N) = 0 := by
  simp [negativeLogDenominator, PowerSeries.constantCoeff_logOf]

/-- Exponentiating the formal logarithm of a unit-constant series returns the
series.  This bridge is not provided as a named general theorem by the pinned
PowerSeries API. -/
theorem exp_subst_logOf {f : R⟦X⟧} (hf : f.constantCoeff = 1) :
    (PowerSeries.exp R).subst (PowerSeries.logOf f) = f := by
  have hzero : (f - 1).constantCoeff = 0 := by
    rw [map_sub, map_one, hf, sub_self]
  let hsub : PowerSeries.HasSubst (f - 1) :=
    PowerSeries.HasSubst.of_constantCoeff_zero' hzero
  rw [PowerSeries.logOf_eq]
  rw [← PowerSeries.subst_comp_subst_apply PowerSeries.HasSubst.log hsub]
  rw [PowerSeries.subst_exp_log]
  rw [PowerSeries.subst_add hsub, PowerSeries.subst_X hsub]
  rw [← PowerSeries.coe_substAlgHom hsub, map_one]
  ring

/-- Formal logarithmic differentiation for a unit-constant series. -/
theorem mul_derivative_logOf {f : R⟦X⟧} (hf : f.constantCoeff = 1) :
    f * PowerSeries.derivative R (PowerSeries.logOf f) =
      PowerSeries.derivative R f := by
  have hlog : (PowerSeries.logOf f).constantCoeff = 0 :=
    PowerSeries.constantCoeff_logOf hf
  let hsub : PowerSeries.HasSubst (PowerSeries.logOf f) :=
    PowerSeries.HasSubst.of_constantCoeff_zero' hlog
  have h := congrArg (PowerSeries.derivative R) (exp_subst_logOf hf)
  rw [PowerSeries.derivative_subst hsub, PowerSeries.derivative_exp] at h
  rwa [exp_subst_logOf hf] at h

/-- A zero-constant exponential family is `exp (rL)` as a single
substitution. -/
theorem formalExpFamily_eq_exp_subst {L : R⟦X⟧} (hL : L.constantCoeff = 0)
    (r : R) :
    formalExpFamily L r = (PowerSeries.exp R).subst (PowerSeries.C r * L) := by
  let hLsub : PowerSeries.HasSubst L :=
    PowerSeries.HasSubst.of_constantCoeff_zero' hL
  rw [formalExpFamily, PowerSeries.rescale_eq_subst]
  rw [PowerSeries.subst_comp_subst_apply (PowerSeries.HasSubst.smul_X' r) hLsub]
  rw [PowerSeries.subst_smul hLsub, PowerSeries.subst_X hLsub]
  rw [PowerSeries.smul_eq_C_mul]

/-- Paper IV's formal reciprocal family `Delta_N(w)^(-r)`. -/
def reciprocalSeries (N : ℕ) (r : R) : R⟦X⟧ :=
  formalExpFamily (negativeLogDenominator (R := R) N) r

@[simp]
theorem constantCoeff_reciprocalSeries (N : ℕ) (r : R) :
    PowerSeries.constantCoeff (reciprocalSeries N r) = 1 := by
  rw [reciprocalSeries, formalExpFamily]
  change MvPowerSeries.constantCoeff
      ((PowerSeries.rescale r (PowerSeries.exp R)).subst
        (negativeLogDenominator N)) = 1
  rw [PowerSeries.constantCoeff_subst_of_constantCoeff_zero
    (constantCoeff_negativeLogDenominator N)]
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, PowerSeries.coeff_rescale]
  simp

@[simp]
theorem reciprocalSeries_zero (N : ℕ) :
    reciprocalSeries (R := R) N 0 = 1 := by
  exact formalExpFamily_zero (constantCoeff_negativeLogDenominator N)

/-- Parameter `-1` recovers the denominator itself. -/
theorem reciprocalSeries_neg_one (N : ℕ) :
    reciprocalSeries (R := R) N (-1) = reducedDenominator N := by
  rw [reciprocalSeries,
    formalExpFamily_eq_exp_subst (constantCoeff_negativeLogDenominator N)]
  rw [negativeLogDenominator]
  have h := exp_subst_logOf (constantCoeff_reducedDenominator (R := R) N)
  simpa using h

/-- Exact additive parameter law for the manuscript's named reciprocal family. -/
theorem reciprocalSeries_add (N : ℕ) (r s : R) :
    reciprocalSeries N r * reciprocalSeries N s = reciprocalSeries N (r + s) := by
  exact formalExpFamily_semigroup (constantCoeff_negativeLogDenominator N) r s

section Field

variable {K : Type*} [Field K] [Algebra ℚ K]

/-- Parameter `1` is exactly the formal inverse of `Delta_N`. -/
theorem reciprocalSeries_one_eq_inverse (N : ℕ) :
    reciprocalSeries (R := K) N 1 = (reducedDenominator N)⁻¹ := by
  apply (PowerSeries.eq_inv_iff_mul_eq_one
    (by simp : PowerSeries.constantCoeff (reducedDenominator (R := K) N) ≠ 0)).2
  rw [← reciprocalSeries_neg_one (R := K) N]
  rw [reciprocalSeries_add, add_neg_cancel, reciprocalSeries_zero]

end Field

/-- Factorially normalized coefficients `P_{N,n}(r)`. -/
def reciprocalCoeff (N n : ℕ) (r : R) : R :=
  blockCoeff N n (reciprocalSeries N r)

/-- Ordinary `w`-coefficient `b_{N,n}(r) = P_{N,n}(r)/(Nn)!`. -/
def reciprocalOrdCoeff (N n : ℕ) (r : R) : R :=
  PowerSeries.coeff n (reciprocalSeries N r)

@[simp]
theorem reciprocalCoeff_zero_parameter (N : ℕ) :
    reciprocalCoeff (R := R) N 0 0 = 1 := by
  simp [reciprocalCoeff, blockCoeff]

theorem reciprocalCoeff_zero_parameter_of_pos (N : ℕ) {n : ℕ} (hn : 0 < n) :
    reciprocalCoeff (R := R) N n 0 = 0 := by
  simp [reciprocalCoeff, blockCoeff, hn.ne']

/-- Exact block-convolution law for `P_{N,n}(r+s)`. -/
theorem reciprocalCoeff_addition (N n : ℕ) (r s : R) :
    reciprocalCoeff N n (r + s) =
      ∑ q ∈ Finset.range (n + 1),
        ((N * n).choose (N * q) : R) *
          reciprocalCoeff N q r * reciprocalCoeff N (n - q) s := by
  exact reciprocal_block_convolution
    (constantCoeff_negativeLogDenominator N) N n r s

/-- Logarithmic coefficients in the normalization
`-log Delta_N = sum kappa_{N,m} X^m / m`.

The value at `m = 0` is harmless and is not used by the manuscript.
-/
def kappaCoeff (N m : ℕ) : R :=
  (m : R) * PowerSeries.coeff m (negativeLogDenominator (R := R) N)

/-- Reduced logarithmic derivative `-Delta_N'/Delta_N`. -/
def reducedTangentSeries (N : ℕ) : R⟦X⟧ :=
  PowerSeries.derivative R (negativeLogDenominator (R := R) N)

@[simp]
theorem coeff_reducedTangentSeries (N n : ℕ) :
    PowerSeries.coeff n (reducedTangentSeries (R := R) N) =
      kappaCoeff N (n + 1) := by
  rw [reducedTangentSeries, PowerSeries.coeff_derivative, kappaCoeff]
  simp only [Nat.cast_add, Nat.cast_one]
  ring

/-- Exact formal logarithmic-derivative identity for the reduced denominator. -/
theorem reducedDenominator_mul_reducedTangentSeries (N : ℕ) :
    reducedDenominator (R := R) N * reducedTangentSeries N =
      -PowerSeries.derivative R (reducedDenominator N) := by
  rw [reducedTangentSeries, negativeLogDenominator, map_neg]
  simpa using
    congrArg Neg.neg
      (mul_derivative_logOf (constantCoeff_reducedDenominator (R := R) N))

/-- Coefficient recurrence obtained from
`Delta_N * (-Delta_N' / Delta_N) = -Delta_N'`. -/
theorem reducedTangent_coefficient_convolution (N n : ℕ) :
    (∑ p ∈ Finset.antidiagonal n,
        PowerSeries.coeff p.1 (reducedDenominator (R := R) N) *
          kappaCoeff N (p.2 + 1)) =
      -(PowerSeries.coeff (n + 1) (reducedDenominator N) * (n + 1 : R)) := by
  have h := congrArg (PowerSeries.coeff (R := R) n)
    (reducedDenominator_mul_reducedTangentSeries (R := R) N)
  rw [PowerSeries.coeff_mul, map_neg, PowerSeries.coeff_derivative] at h
  simpa only [coeff_reducedTangentSeries] using h

/-- The generic formal derivative theorem specialized to `Delta_N^(-r)`. -/
theorem derivative_reciprocalSeries (N : ℕ) (r : R) :
    PowerSeries.derivative R (reciprocalSeries N r) =
      PowerSeries.C r * reciprocalSeries N r *
        PowerSeries.derivative R (negativeLogDenominator N) := by
  exact derivative_formalExpFamily (constantCoeff_negativeLogDenominator N) r

/-- Finite Newton recurrence specialized to the named reciprocal family. -/
theorem reciprocalSeries_coefficient_recurrence (N : ℕ) (r : R) (n : ℕ) :
    (n + 1 : R) * PowerSeries.coeff (n + 1) (reciprocalSeries N r) =
      r * ∑ p ∈ Finset.antidiagonal n,
        PowerSeries.coeff p.1 (reciprocalSeries N r) *
          ((p.2 + 1 : R) *
            PowerSeries.coeff (p.2 + 1) (negativeLogDenominator N)) := by
  exact formalExpFamily_coefficient_recurrence
    (constantCoeff_negativeLogDenominator N) r n

/-- Manuscript Newton recurrence in an equivalent antidiagonal indexing. -/
theorem reciprocalOrdCoeff_newton (N : ℕ) (r : R) (n : ℕ) :
    (n + 1 : R) * reciprocalOrdCoeff N (n + 1) r =
      r * ∑ p ∈ Finset.antidiagonal n,
        reciprocalOrdCoeff N p.1 r * kappaCoeff N (p.2 + 1) := by
  simpa [reciprocalOrdCoeff, kappaCoeff] using
    reciprocalSeries_coefficient_recurrence (R := R) N r n

end

end Komorebi.PaperIV
