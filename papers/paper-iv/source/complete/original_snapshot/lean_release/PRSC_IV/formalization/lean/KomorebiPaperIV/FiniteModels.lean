/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.SectionCycles
import Mathlib.RingTheory.AdjoinRoot
import Mathlib.Analysis.Normed.Algebra.MatrixExponential

/-!
# Finite algebra and companion-matrix models

This file formalizes the finite models from Section 6 of Paper IV.  The
quotient-algebra exponential identities are identities of formal power series.
The companion matrix is treated both algebraically, through an exact formula
for every matrix power, and analytically through the finite-dimensional matrix
exponential.

No determinant-of-exponential theorem is assumed here.  The pinned Mathlib
matrix-exponential API explicitly leaves that general theorem as future work.
-/

namespace Komorebi.PaperIV

open Polynomial NormedSpace
open scoped PowerSeries

noncomputable section

/-! ## The two finite quotient algebras -/

/-- The polynomial defining the cyclic algebra `R[xi] / (xi^N - 1)`. -/
def cyclicAlgebraPolynomial (R : Type*) [CommRing R] (N : ℕ) : R[X] :=
  X ^ N - 1

/-- The polynomial defining the signed cyclic algebra `R[xi] / (xi^N + 1)`. -/
def signedCyclicAlgebraPolynomial (R : Type*) [CommRing R] (N : ℕ) : R[X] :=
  X ^ N + 1

/-- The finite cyclic quotient algebra `R[xi] / (xi^N - 1)`. -/
abbrev CyclicAlgebra (R : Type*) [CommRing R] (N : ℕ) :=
  AdjoinRoot (cyclicAlgebraPolynomial R N)

/-- The finite signed quotient algebra `R[xi] / (xi^N + 1)`. -/
abbrev SignedCyclicAlgebra (R : Type*) [CommRing R] (N : ℕ) :=
  AdjoinRoot (signedCyclicAlgebraPolynomial R N)

/-- The distinguished generator of the cyclic quotient algebra. -/
def cyclicGenerator (R : Type*) [CommRing R] (N : ℕ) : CyclicAlgebra R N :=
  AdjoinRoot.root (cyclicAlgebraPolynomial R N)

/-- The distinguished generator of the signed quotient algebra. -/
def signedCyclicGenerator (R : Type*) [CommRing R] (N : ℕ) : SignedCyclicAlgebra R N :=
  AdjoinRoot.root (signedCyclicAlgebraPolynomial R N)

@[simp]
theorem cyclicGenerator_pow (R : Type*) [CommRing R] (N : ℕ) :
    cyclicGenerator R N ^ N = 1 := by
  have h := AdjoinRoot.eval₂_root (cyclicAlgebraPolynomial R N)
  rw [cyclicAlgebraPolynomial, Polynomial.eval₂_sub, Polynomial.eval₂_pow,
    Polynomial.eval₂_X, Polynomial.eval₂_one] at h
  exact sub_eq_zero.mp h

@[simp]
theorem signedCyclicGenerator_pow (R : Type*) [CommRing R] (N : ℕ) :
    signedCyclicGenerator R N ^ N = -1 := by
  have h := AdjoinRoot.eval₂_root (signedCyclicAlgebraPolynomial R N)
  rw [signedCyclicAlgebraPolynomial, Polynomial.eval₂_add, Polynomial.eval₂_pow,
    Polynomial.eval₂_X, Polynomial.eval₂_one] at h
  exact eq_neg_of_add_eq_zero_left h

/-- Reduction of powers in the cyclic quotient algebra. -/
theorem cyclicGenerator_pow_eq_mod (R : Type*) [CommRing R] (N m : ℕ) :
    cyclicGenerator R N ^ m = cyclicGenerator R N ^ (m % N) := by
  calc
    cyclicGenerator R N ^ m =
        cyclicGenerator R N ^ (m % N + N * (m / N)) := by
          rw [Nat.mod_add_div]
    _ = cyclicGenerator R N ^ (m % N) *
        (cyclicGenerator R N ^ N) ^ (m / N) := by
          rw [pow_add, pow_mul]
    _ = cyclicGenerator R N ^ (m % N) := by simp

/-- Reduction of powers in the signed quotient algebra, including every
wraparound sign. -/
theorem signedCyclicGenerator_pow_eq_mod (R : Type*) [CommRing R] (N m : ℕ) :
    signedCyclicGenerator R N ^ m =
      (-1 : SignedCyclicAlgebra R N) ^ (m / N) *
        signedCyclicGenerator R N ^ (m % N) := by
  calc
    signedCyclicGenerator R N ^ m =
        signedCyclicGenerator R N ^ (m % N + N * (m / N)) := by
          rw [Nat.mod_add_div]
    _ = signedCyclicGenerator R N ^ (m % N) *
        (signedCyclicGenerator R N ^ N) ^ (m / N) := by
          rw [pow_add, pow_mul]
    _ = signedCyclicGenerator R N ^ (m % N) *
        (-1 : SignedCyclicAlgebra R N) ^ (m / N) := by
          rw [signedCyclicGenerator_pow]
    _ = _ := by ring

/-- A power basis witnessing the unique representative of degree below `N`
in the cyclic quotient algebra. -/
def cyclicAlgebraPowerBasis (R : Type*) [CommRing R] (N : ℕ) (hN : 0 < N) :
    PowerBasis R (CyclicAlgebra R N) :=
  AdjoinRoot.powerBasis'
    (by simpa [cyclicAlgebraPolynomial] using
      (Polynomial.monic_X_pow_sub_C (1 : R) hN.ne'))

/-- A power basis witnessing the unique representative of degree below `N`
in the signed quotient algebra. -/
def signedCyclicAlgebraPowerBasis (R : Type*) [CommRing R] (N : ℕ) (hN : 0 < N) :
    PowerBasis R (SignedCyclicAlgebra R N) :=
  AdjoinRoot.powerBasis'
    (by simpa [signedCyclicAlgebraPolynomial] using
      (Polynomial.monic_X_pow_add_C (1 : R) hN.ne'))

@[simp]
theorem cyclicAlgebraPowerBasis_dim (R : Type*) [CommRing R] [Nontrivial R]
    (N : ℕ) (hN : 0 < N) :
    (cyclicAlgebraPowerBasis R N hN).dim = N := by
  rw [cyclicAlgebraPowerBasis, AdjoinRoot.powerBasis'_dim]
  simpa [cyclicAlgebraPolynomial] using
    (Polynomial.natDegree_X_pow_sub_C (R := R) (n := N) (r := 1))

@[simp]
theorem signedCyclicAlgebraPowerBasis_dim (R : Type*) [CommRing R] [Nontrivial R]
    (N : ℕ) (hN : 0 < N) :
    (signedCyclicAlgebraPowerBasis R N hN).dim = N := by
  rw [signedCyclicAlgebraPowerBasis, AdjoinRoot.powerBasis'_dim]
  simp [signedCyclicAlgebraPolynomial]

section FormalAlgebraExponential

variable (R : Type*) [CommRing R] [Algebra ℚ R]

/-- The formal exponential `exp(lambda X xi)` in the cyclic quotient algebra. -/
def cyclicAlgebraExponentialSeries (N : ℕ) (lambda : R) :
    (CyclicAlgebra R N)⟦X⟧ :=
  PowerSeries.rescale
    (algebraMap R (CyclicAlgebra R N) lambda * cyclicGenerator R N)
    (PowerSeries.exp (CyclicAlgebra R N))

/-- The formal exponential `exp(X xi)` in the signed quotient algebra. -/
def signedCyclicAlgebraExponentialSeries (N : ℕ) :
    (SignedCyclicAlgebra R N)⟦X⟧ :=
  PowerSeries.rescale (signedCyclicGenerator R N)
    (PowerSeries.exp (SignedCyclicAlgebra R N))

/-- Exact formal version of
`exp(lambda z xi) = sum_j E_{N,j}(lambda z) xi^j` in `xi^N = 1`. -/
theorem cyclicAlgebra_exponential_eq_sections (N : ℕ) (hN : 0 < N) (lambda : R) :
    cyclicAlgebraExponentialSeries R N lambda =
      ∑ j : Fin N,
        PowerSeries.C (cyclicGenerator R N ^ j.val) *
          transferSection N j.val (algebraMap R (CyclicAlgebra R N) lambda) := by
  classical
  ext m
  rw [cyclicAlgebraExponentialSeries, PowerSeries.coeff_rescale, map_sum]
  simp only [PowerSeries.coeff_exp, PowerSeries.coeff_C_mul, coeff_transferSection,
    transferSectionCoeff]
  rw [mul_pow, cyclicGenerator_pow_eq_mod]
  have hm : m % N < N := Nat.mod_lt m hN
  rw [Finset.sum_eq_single (⟨m % N, hm⟩ : Fin N)]
  · simp only [ite_true]
    ring
  · intro b _hb hne
    have hval : m % N ≠ b.val := by
      intro heq
      apply hne
      apply Fin.ext
      simpa using heq.symm
    simp [hval]
  · simp

/-- Exact formal version of
`exp(z xi) = sum_j D_{N,j}(z) xi^j` in `xi^N = -1`. -/
theorem signedCyclicAlgebra_exponential_eq_sections (N : ℕ) (hN : 0 < N) :
    signedCyclicAlgebraExponentialSeries R N =
      ∑ j : Fin N,
        PowerSeries.C (signedCyclicGenerator R N ^ j.val) *
          signedSection (R := SignedCyclicAlgebra R N) N j.val := by
  classical
  ext m
  rw [signedCyclicAlgebraExponentialSeries, PowerSeries.coeff_rescale, map_sum]
  simp only [PowerSeries.coeff_exp, PowerSeries.coeff_C_mul, coeff_signedSection,
    signedSectionCoeff]
  rw [signedCyclicGenerator_pow_eq_mod]
  have hm : m % N < N := Nat.mod_lt m hN
  rw [Finset.sum_eq_single (⟨m % N, hm⟩ : Fin N)]
  · simp only [ite_true]
    ring
  · intro b _hb hne
    have hval : m % N ≠ b.val := by
      intro heq
      apply hne
      apply Fin.ext
      simpa using heq.symm
    simp [hval]
  · simp

end FormalAlgebraExponential

/-! ## The signed cyclic shift and all of its powers -/

section SignedShift

variable {R : Type*} [CommRing R]

/-- Closed form for the `k`th signed cyclic shift.  There is one nonzero entry
in each column, and its sign records the number of crossings of the signed
edge. -/
def signedShiftPowerMatrix (N k : ℕ) : Matrix (Fin N) (Fin N) R :=
  fun p q =>
    if p.val = (q.val + k) % N then
      (-1 : R) ^ ((q.val + k) / N)
    else 0

/-- The signed cyclic shift `J_N`; column `q` is sent to column `q+1`, with a
minus sign at the wraparound. -/
def signedShiftMatrix (N : ℕ) : Matrix (Fin N) (Fin N) R :=
  signedShiftPowerMatrix N 1

@[simp]
theorem signedShiftPowerMatrix_apply (N k : ℕ) (p q : Fin N) :
    signedShiftPowerMatrix (R := R) N k p q =
      if p.val = (q.val + k) % N then
        (-1 : R) ^ ((q.val + k) / N)
      else 0 := rfl

@[simp]
theorem signedShiftPowerMatrix_zero (N : ℕ) :
    signedShiftPowerMatrix (R := R) N 0 = 1 := by
  ext p q
  rw [Matrix.one_apply]
  by_cases hpq : p = q
  · subst p
    simp [signedShiftPowerMatrix, Nat.mod_eq_of_lt q.isLt, Nat.div_eq_of_lt q.isLt]
  · have hval : p.val ≠ q.val := fun h => hpq (Fin.ext h)
    simp [signedShiftPowerMatrix, Nat.mod_eq_of_lt q.isLt, hpq, hval]

private theorem add_mod_after_mod (N t a : ℕ) :
    (t % N + a) % N = (t + a) % N := by
  calc
    (t % N + a) % N = (t % N % N + a % N) % N := Nat.add_mod _ _ _
    _ = (t % N + a % N) % N := by rw [Nat.mod_mod]
    _ = (t + a) % N := (Nat.add_mod _ _ _).symm

private theorem add_div_after_mod (N t a : ℕ) (hN : 0 < N) :
    (t % N + a) / N + t / N = (t + a) / N := by
  rw [← Nat.add_mul_div_left (t % N + a) (t / N) hN]
  congr 1
  calc
    t % N + a + N * (t / N) = (t % N + N * (t / N)) + a := by omega
    _ = t + a := by rw [Nat.mod_add_div]

/-- The closed signed shifts form an additive one-parameter semigroup. -/
theorem signedShiftPowerMatrix_mul (N a b : ℕ) (hN : 0 < N) :
    signedShiftPowerMatrix (R := R) N a * signedShiftPowerMatrix N b =
      signedShiftPowerMatrix N (a + b) := by
  classical
  ext p q
  rw [Matrix.mul_apply]
  let x : Fin N := ⟨(q.val + b) % N, Nat.mod_lt _ hN⟩
  rw [Finset.sum_eq_single x]
  · simp only [signedShiftPowerMatrix]
    have hmod : (x.val + a) % N = (q.val + (a + b)) % N := by
      change ((q.val + b) % N + a) % N = _
      rw [add_mod_after_mod]
      congr 1
      omega
    have hdiv :
        (x.val + a) / N + (q.val + b) / N =
          (q.val + (a + b)) / N := by
      change ((q.val + b) % N + a) / N + (q.val + b) / N = _
      rw [add_div_after_mod N (q.val + b) a hN]
      congr 1
      omega
    rw [show x.val = (q.val + b) % N by rfl]
    simp only [ite_true]
    rw [hmod]
    by_cases hp : p.val = (q.val + (a + b)) % N
    · simp only [hp, ite_true]
      rw [← pow_add, hdiv]
    · simp [hp]
  · intro y _hy hyx
    simp only [signedShiftPowerMatrix]
    have hval : y.val ≠ (q.val + b) % N := by
      intro h
      apply hyx
      apply Fin.ext
      exact h
    simp [hval]
  · simp

/-- Every matrix power of `J_N` has the closed signed-shift form. -/
theorem signedShiftMatrix_pow (N k : ℕ) (hN : 0 < N) :
    signedShiftMatrix (R := R) N ^ k = signedShiftPowerMatrix N k := by
  induction k with
  | zero => simp
  | succ k ih =>
      rw [pow_succ, ih, signedShiftMatrix, signedShiftPowerMatrix_mul N k 1 hN]

/-- Exact entry formula for every power of the signed shift. -/
theorem signedShiftMatrix_pow_apply (N k : ℕ) (hN : 0 < N) (p q : Fin N) :
    (signedShiftMatrix (R := R) N ^ k) p q =
      if p.val = (q.val + k) % N then
        (-1 : R) ^ ((q.val + k) / N)
      else 0 := by
  rw [signedShiftMatrix_pow N k hN]
  rfl

private theorem signedShiftPowerMatrix_period (N : ℕ) (hN : 0 < N) :
    signedShiftPowerMatrix (R := R) N N = -1 := by
  ext p q
  rw [Matrix.neg_apply, Matrix.one_apply]
  have hmod : (q.val + N) % N = q.val := by
    rw [Nat.add_mod_right, Nat.mod_eq_of_lt q.isLt]
  have hdiv : (q.val + N) / N = 1 := by
    simpa [Nat.div_eq_of_lt q.isLt] using Nat.add_mul_div_left q.val 1 hN
  by_cases hpq : p = q
  · subst p
    simp [signedShiftPowerMatrix, hmod, hdiv]
  · have hval : p.val ≠ q.val := fun h => hpq (Fin.ext h)
    simp [signedShiftPowerMatrix, hmod, hpq, hval]

/-- The companion relation `J_N^N = -I`. -/
theorem signedShiftMatrix_pow_order (N : ℕ) (hN : 0 < N) :
    signedShiftMatrix (R := R) N ^ N = -1 := by
  rw [signedShiftMatrix_pow N N hN, signedShiftPowerMatrix_period N hN]

end SignedShift

/-! ## The analytic finite-dimensional fundamental matrix -/

/-- The fundamental matrix `U_N(z) = exp(z J_N)`. -/
def signedFundamentalMatrix (N : ℕ) (z : ℂ) : Matrix (Fin N) (Fin N) ℂ :=
  exp (z • signedShiftMatrix (R := ℂ) N)

/-- The matrix exponential obeys the addition law. -/
theorem signedFundamentalMatrix_add (N : ℕ) (z w : ℂ) :
    signedFundamentalMatrix N (z + w) =
      signedFundamentalMatrix N z * signedFundamentalMatrix N w := by
  rw [signedFundamentalMatrix, add_smul]
  exact Matrix.exp_add_of_commute _ _
    (((Commute.refl (signedShiftMatrix (R := ℂ) N)).smul_left z).smul_right w)

/-- Negating the parameter gives the matrix inverse. -/
theorem signedFundamentalMatrix_neg (N : ℕ) (z : ℂ) :
    signedFundamentalMatrix N (-z) = (signedFundamentalMatrix N z)⁻¹ := by
  rw [signedFundamentalMatrix, signedFundamentalMatrix, neg_smul]
  exact Matrix.exp_neg _

/-- Two opposite parameters multiply to the identity matrix. -/
theorem signedFundamentalMatrix_mul_neg (N : ℕ) (z : ℂ) :
    signedFundamentalMatrix N z * signedFundamentalMatrix N (-z) = 1 := by
  rw [← signedFundamentalMatrix_add, add_neg_cancel]
  simp [signedFundamentalMatrix]

/-- The fundamental matrix is a unit for every parameter. -/
theorem signedFundamentalMatrix_isUnit (N : ℕ) (z : ℂ) :
    IsUnit (signedFundamentalMatrix N z) := by
  exact Matrix.isUnit_exp _

end

end Komorebi.PaperIV
