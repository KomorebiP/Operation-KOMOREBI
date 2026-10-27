/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.Appell
import Mathlib.Data.Nat.Choose.Cast
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Algebra.Polynomial.Degree.IsMonicOfDegree
import Mathlib.Algebra.Polynomial.HasseDeriv
import Mathlib.RingTheory.PowerSeries.Expand
import Mathlib.Algebra.Polynomial.Div

/-!
# Algebraic completion for Paper IV

This file records branch-free algebraic statements from Paper IV that were not
part of the initial checkpoint.  In particular, it proves the exact
factorial-rescaled triangular inverse system used for the normalized residue
sections.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

section ResidueInverse

variable {K : Type*} [Field K] [CharZero K]

/-- The reduced normalized residue section
`j! * sum_n X^n / (N n + j)!`. -/
def normalizedResidueSection (N j : ℕ) : K⟦X⟧ :=
  PowerSeries.mk fun n =>
    (j.factorial : K) / ((N * n + j).factorial : K)

omit [CharZero K] in
@[simp]
theorem coeff_normalizedResidueSection (N j n : ℕ) :
    PowerSeries.coeff n (normalizedResidueSection (K := K) N j) =
      (j.factorial : K) / ((N * n + j).factorial : K) := by
  simp [normalizedResidueSection]

@[simp]
theorem constantCoeff_normalizedResidueSection (N j : ℕ) :
    (normalizedResidueSection (K := K) N j).constantCoeff = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff]
  rw [coeff_normalizedResidueSection]
  have hj : (j.factorial : K) ≠ 0 := by
    exact_mod_cast j.factorial_pos.ne'
  simpa using div_self hj

/-- Paper IV's coefficient `C_{N,j}(n)`, including its `(N n)!` scaling. -/
def residueInverseCoeff (N j n : ℕ) : K :=
  ((N * n).factorial : K) *
    PowerSeries.coeff n (normalizedResidueSection (K := K) N j)⁻¹

/-- The exact factorial-rescaled triangular inverse identity of Theorem 9.2. -/
theorem residueInverseCoeff_triangular (N j n : ℕ) :
    (∑ q ∈ Finset.range (n + 1),
        ((N * n + j).choose (N * q) : K) *
          residueInverseCoeff (K := K) N j q) =
      if n = 0 then 1 else 0 := by
  let D : K⟦X⟧ := normalizedResidueSection (K := K) N j
  have hD : D.constantCoeff = 1 := by
    simp [D]
  have hunit : D.constantCoeff ≠ 0 := by simp [hD]
  have hinv : D⁻¹ * D = 1 := by
    rw [mul_comm]
    exact PowerSeries.mul_inv_cancel D hunit
  have hcoeff := congrArg (PowerSeries.coeff (R := K) n) hinv
  rw [PowerSeries.coeff_mul,
    Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at hcoeff
  simp only [PowerSeries.coeff_one] at hcoeff
  let scale : K := ((N * n + j).factorial : K) / (j.factorial : K)
  have hterm (q : ℕ) (hq : q ∈ Finset.range (n + 1)) :
      scale *
          (PowerSeries.coeff q D⁻¹ * PowerSeries.coeff (n - q) D) =
        ((N * n + j).choose (N * q) : K) *
          residueInverseCoeff (K := K) N j q := by
    have hqn : q ≤ n := Nat.le_of_lt_succ (Finset.mem_range.mp hq)
    have hmul : N * q ≤ N * n := Nat.mul_le_mul_left N hqn
    have hle : N * q ≤ N * n + j := hmul.trans (Nat.le_add_right _ _)
    have hsplit : N * q + N * (n - q) = N * n := by
      rw [← Nat.mul_add, Nat.add_sub_of_le hqn]
    have hsub : N * n + j - N * q = N * (n - q) + j := by omega
    have hfacj : (j.factorial : K) ≠ 0 := by
      exact_mod_cast j.factorial_pos.ne'
    have hfacq : ((N * q).factorial : K) ≠ 0 := by
      exact_mod_cast (N * q).factorial_pos.ne'
    have hfacrest : ((N * (n - q) + j).factorial : K) ≠ 0 := by
      exact_mod_cast (N * (n - q) + j).factorial_pos.ne'
    rw [show PowerSeries.coeff (n - q) D =
        (j.factorial : K) / ((N * (n - q) + j).factorial : K) by
      simp [D]]
    rw [residueInverseCoeff]
    rw [Nat.cast_choose K hle, hsub]
    dsimp [scale]
    field_simp
    ring
  calc
    (∑ q ∈ Finset.range (n + 1),
        ((N * n + j).choose (N * q) : K) *
          residueInverseCoeff (K := K) N j q) =
        ∑ q ∈ Finset.range (n + 1),
          scale * (PowerSeries.coeff q D⁻¹ * PowerSeries.coeff (n - q) D) := by
            apply Finset.sum_congr rfl
            intro q hq
            exact (hterm q hq).symm
    _ = scale *
        ∑ q ∈ Finset.range (n + 1),
          PowerSeries.coeff q D⁻¹ * PowerSeries.coeff (n - q) D := by
            rw [Finset.mul_sum]
    _ = scale * (if n = 0 then 1 else 0) := by rw [hcoeff]
    _ = if n = 0 then 1 else 0 := by
      by_cases hn : n = 0
      · subst n
        have hj : (j.factorial : K) ≠ 0 := by
          exact_mod_cast j.factorial_pos.ne'
        simp [scale, hj]
      · simp [hn]

@[simp]
theorem residueInverseCoeff_zero (N j : ℕ) :
    residueInverseCoeff (K := K) N j 0 = 1 := by
  simpa using residueInverseCoeff_triangular (K := K) N j 0

/-- The solved triangular recurrence displayed in Theorem 9.2. -/
theorem residueInverseCoeff_recurrence (N j n : ℕ) (hn : 0 < n) :
    residueInverseCoeff (K := K) N j n =
      -(∑ q ∈ Finset.range n,
          ((N * n + j).choose (N * q) : K) *
            residueInverseCoeff (K := K) N j q) /
        ((N * n + j).choose (N * n) : K) := by
  have hsum := residueInverseCoeff_triangular (K := K) N j n
  have hn0 : n ≠ 0 := Nat.ne_of_gt hn
  simp only [hn0, ↓reduceIte] at hsum
  rw [Finset.sum_range_succ] at hsum
  have hle : N * n ≤ N * n + j := by omega
  have hden : ((N * n + j).choose (N * n) : K) ≠ 0 := by
    exact_mod_cast (Nat.choose_pos hle).ne'
  apply (eq_div_iff hden).2
  linear_combination hsum

end ResidueInverse

section SparseAppell

variable {R : Type*} [CommRing R]

/-- Inflate block coefficients to the full EGF index set, putting zero away
from indices divisible by `N`. -/
def blockCoefficientSequence (N : ℕ) (c : ℕ → R) (q : ℕ) : R :=
  if N ∣ q then c (q / N) else 0

@[simp]
theorem blockCoefficientSequence_mul (N : ℕ) (hN : 0 < N)
    (c : ℕ → R) (n : ℕ) :
    blockCoefficientSequence N c (N * n) = c n := by
  simp [blockCoefficientSequence, Nat.mul_div_cancel_left n hN]

/-- A sparse Appell polynomial contains only the coefficient indices in the
specified congruence block. -/
theorem appellPolynomial_eq_sparse_sum (N m : ℕ) (c : ℕ → R) :
    appellPolynomial (blockCoefficientSequence N c) m =
      ∑ q ∈ (Finset.range (m + 1)).filter (fun q => N ∣ q),
        Polynomial.C
            ((m.choose q : R) * blockCoefficientSequence N c q) *
          Polynomial.X ^ (m - q) := by
  rw [appellPolynomial]
  symm
  refine Finset.sum_subset (Finset.filter_subset _ _) ?_
  intro q hq hqfilter
  have hnot : ¬N ∣ q := by
    intro hdiv
    apply hqfilter
    exact Finset.mem_filter.mpr ⟨hq, hdiv⟩
  rw [blockCoefficientSequence]
  simp [hnot]

/-- Proposition 9.7 in exact block form: only the indices `N n ≤ m`
contribute to the Appell polynomial. -/
theorem appellPolynomial_eq_block_sum (N m : ℕ) (hN : 0 < N)
    (c : ℕ → R) :
    appellPolynomial (blockCoefficientSequence N c) m =
      ∑ n ∈ Finset.range (m / N + 1),
        Polynomial.C ((m.choose (N * n) : R) * c n) *
          Polynomial.X ^ (m - N * n) := by
  rw [appellPolynomial_eq_sparse_sum]
  symm
  refine Finset.sum_bij (fun n _ => N * n) ?_ ?_ ?_ ?_
  · intro n hn
    apply Finset.mem_filter.mpr
    constructor
    · apply Finset.mem_range.mpr
      have hnle : n ≤ m / N := Nat.le_of_lt_succ (Finset.mem_range.mp hn)
      have hmul : n * N ≤ m := (Nat.le_div_iff_mul_le hN).mp hnle
      simpa [Nat.mul_comm] using Nat.lt_succ_of_le hmul
    · exact dvd_mul_right N n
  · intro n₁ _ n₂ _ heq
    exact Nat.mul_left_cancel hN heq
  · intro q hq
    rcases Finset.mem_filter.mp hq with ⟨hqrange, hdiv⟩
    rcases hdiv with ⟨n, rfl⟩
    refine ⟨n, ?_, rfl⟩
    apply Finset.mem_range.mpr
    rw [Nat.lt_add_one_iff]
    apply (Nat.le_div_iff_mul_le hN).mpr
    have hNm : N * n ≤ m := Nat.le_of_lt_succ (Finset.mem_range.mp hqrange)
    simpa [Nat.mul_comm] using hNm
  · intro n hn
    simp [blockCoefficientSequence_mul N hN]

/-- Every Appell polynomial with unit zeroth base coefficient is monic of its
displayed degree. -/
theorem appellPolynomial_isMonicOfDegree [Nontrivial R] (a : ℕ → R) (m : ℕ)
    (ha : a 0 = 1) :
    Polynomial.IsMonicOfDegree (appellPolynomial a m) m := by
  rw [Polynomial.isMonicOfDegree_iff]
  constructor
  · rw [appellPolynomial]
    apply Polynomial.natDegree_sum_le_of_forall_le
    intro q hq
    exact (Polynomial.natDegree_C_mul_X_pow_le _ _).trans (Nat.sub_le m q)
  · rw [appellPolynomial, Polynomial.finsetSum_coeff]
    rw [Finset.sum_eq_single 0]
    · simp [ha]
    · intro q hq hq0
      rw [Polynomial.coeff_C_mul, Polynomial.coeff_X_pow]
      have hqm : q ≤ m := Nat.le_of_lt_succ (Finset.mem_range.mp hq)
      have hne : m ≠ m - q := by omega
      simp [hne]
    · simp

/-- The block form of Proposition 9.7 is monic when its zeroth reciprocal
coefficient is one. -/
theorem blockAppellPolynomial_isMonicOfDegree [Nontrivial R]
    (N m : ℕ) (c : ℕ → R) (hc : c 0 = 1) :
    Polynomial.IsMonicOfDegree
      (appellPolynomial (blockCoefficientSequence N c) m) m := by
  apply appellPolynomial_isMonicOfDegree
  simp [blockCoefficientSequence, hc]

/-- Corollary 9.10: block-supported Appell polynomials transform by the
character `omega^m` whenever `omega^N = 1`. -/
theorem eval_appellPolynomial_block_covariance (N m : ℕ) (hN : 0 < N)
    (c : ℕ → R) (omega x : R) (homega : omega ^ N = 1) :
    (appellPolynomial (blockCoefficientSequence N c) m).eval (omega * x) =
      omega ^ m *
        (appellPolynomial (blockCoefficientSequence N c) m).eval x := by
  rw [appellPolynomial_eq_block_sum N m hN c,
    Polynomial.eval_finsetSum, Polynomial.eval_finsetSum]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro n hn
  have hnle : n ≤ m / N := Nat.le_of_lt_succ (Finset.mem_range.mp hn)
  have hmul : N * n ≤ m := by
    have : n * N ≤ m := (Nat.le_div_iff_mul_le hN).mp hnle
    simpa [Nat.mul_comm] using this
  simp only [Polynomial.eval_mul, Polynomial.eval_C, Polynomial.eval_pow,
    Polynomial.eval_X]
  rw [mul_pow]
  have hpow : omega ^ (m - N * n) = omega ^ m := by
    calc
      omega ^ (m - N * n) = omega ^ (m - N * n) * 1 := by rw [mul_one]
      _ = omega ^ (m - N * n) * (omega ^ N) ^ n := by rw [homega, one_pow]
      _ = omega ^ (m - N * n) * omega ^ (N * n) := by rw [pow_mul]
      _ = omega ^ (m - N * n + N * n) := by rw [pow_add]
      _ = omega ^ m := by rw [Nat.sub_add_cancel hmul]
  rw [hpow]
  ring

section ResidueAppell

variable {K : Type*} [Field K] [CharZero K]

omit [CharZero K] in
/-- Proposition 9.7 specialized to the reciprocal of the normalized residue
section from Theorem 9.2. -/
theorem residueAppellPolynomial_explicit (N j m : ℕ) (hN : 0 < N) :
    appellPolynomial
        (blockCoefficientSequence N
          (residueInverseCoeff (K := K) N j)) m =
      ∑ n ∈ Finset.range (m / N + 1),
        Polynomial.C
            ((m.choose (N * n) : K) * residueInverseCoeff (K := K) N j n) *
          Polynomial.X ^ (m - N * n) := by
  exact appellPolynomial_eq_block_sum N m hN _

/-- The residue-section Appell polynomial is monic of degree `m`. -/
theorem residueAppellPolynomial_isMonicOfDegree (N j m : ℕ) (_hN : 0 < N) :
    Polynomial.IsMonicOfDegree
      (appellPolynomial
        (blockCoefficientSequence N
          (residueInverseCoeff (K := K) N j)) m) m := by
  exact blockAppellPolynomial_isMonicOfDegree N m _
    (residueInverseCoeff_zero (K := K) N j)

omit [CharZero K] in
/-- Corollary 9.10 specialized to the normalized residue-section reciprocal. -/
theorem eval_residueAppellPolynomial_covariance (N j m : ℕ) (hN : 0 < N)
    (omega x : K) (homega : omega ^ N = 1) :
    (appellPolynomial
        (blockCoefficientSequence N
          (residueInverseCoeff (K := K) N j)) m).eval (omega * x) =
      omega ^ m *
        (appellPolynomial
          (blockCoefficientSequence N
            (residueInverseCoeff (K := K) N j)) m).eval x := by
  exact eval_appellPolynomial_block_covariance N m hN _ omega x homega

end ResidueAppell

end SparseAppell

section DifferentialOperator

variable {R : Type*} [CommRing R]

/-- The finite action of a constant-coefficient formal symbol whose exponential
generating coefficients are `a`.  Hasse derivatives encode the factors
`derivative^q / q!` without any characteristic-zero assumption. -/
def egfConstantCoeffAction (a : ℕ → R) (f : Polynomial R) : Polynomial R :=
  ∑ q ∈ Finset.range (f.natDegree + 1),
    Polynomial.C (a q) * Polynomial.hasseDeriv q f

/-- The first operator identity of Proposition 9.9: applying the formal symbol
with EGF coefficients `a` to `X^m` gives its Appell polynomial exactly. -/
theorem egfConstantCoeffAction_X_pow [Nontrivial R] (a : ℕ → R) (m : ℕ) :
    egfConstantCoeffAction a (Polynomial.X ^ m) = appellPolynomial a m := by
  rw [egfConstantCoeffAction, Polynomial.natDegree_X_pow, appellPolynomial]
  apply Finset.sum_congr rfl
  intro q _hq
  rw [Polynomial.X_pow_eq_monomial, Polynomial.hasseDeriv_monomial]
  simp only [mul_one, ← Polynomial.C_mul_X_pow_eq_monomial]
  rw [← mul_assoc, ← map_mul]
  congr 1
  exact congrArg Polynomial.C (mul_comm (a q) (m.choose q : R))

/-- Proposition 9.9 specialized to the normalized residue-section reciprocal:
the corresponding finite constant-coefficient action produces the Appell
polynomial from `X^m`. -/
theorem egfConstantCoeffAction_residue_X_pow
    {K : Type*} [Field K] [CharZero K] (N j m : ℕ) :
    egfConstantCoeffAction
        (blockCoefficientSequence N
          (residueInverseCoeff (K := K) N j))
        (Polynomial.X ^ m) =
      appellPolynomial
        (blockCoefficientSequence N
          (residueInverseCoeff (K := K) N j)) m := by
  exact egfConstantCoeffAction_X_pow _ m

end DifferentialOperator

section TruncatedOperatorInversion

variable {S : Type*} [CommRing S]

/-- Polynomial differential symbols evaluated at the formal derivative. -/
def polynomialDifferentialEval :
    Polynomial S →+* Module.End S (Polynomial S) :=
  Polynomial.eval₂RingHom' (algebraMap S (Module.End S (Polynomial S)))
    Polynomial.derivative
    fun a => Algebra.commute_algebraMap_left a Polynomial.derivative

@[simp]
theorem polynomialDifferentialEval_X :
    polynomialDifferentialEval (S := S) Polynomial.X = Polynomial.derivative := by
  simp [polynomialDifferentialEval]

/-- The degree-`d` truncation of a formal differential symbol. -/
def truncatedDifferentialOperator (d : ℕ) (A : S⟦X⟧) :
    Module.End S (Polynomial S) :=
  polynomialDifferentialEval (PowerSeries.trunc (d + 1) A)

theorem coeff_trunc_mul_trunc_of_lt (A B : S⟦X⟧) {d q : ℕ} (hq : q < d + 1) :
    (PowerSeries.trunc (d + 1) A * PowerSeries.trunc (d + 1) B).coeff q =
      PowerSeries.coeff q (A * B) := by
  rw [Polynomial.coeff_mul, PowerSeries.coeff_mul]
  apply Finset.sum_congr rfl
  intro p hp
  have hpadd : p.1 + p.2 = q := Finset.mem_antidiagonal.mp hp
  have hp1 : p.1 < d + 1 := by omega
  have hp2 : p.2 < d + 1 := by omega
  simp only [PowerSeries.coeff_trunc, hp1, hp2, ↓reduceIte]

/-- If two formal symbols multiply to one, their degree-`d` truncations multiply
to one modulo `X^(d+1)`. -/
theorem X_pow_dvd_trunc_mul_trunc_sub_one {A B : S⟦X⟧} (d : ℕ)
    (hAB : A * B = 1) :
    Polynomial.X ^ (d + 1) ∣
      PowerSeries.trunc (d + 1) A * PowerSeries.trunc (d + 1) B - 1 := by
  rw [Polynomial.X_pow_dvd_iff]
  intro q hq
  rw [Polynomial.coeff_sub, coeff_trunc_mul_trunc_of_lt A B hq]
  rw [hAB]
  simp [PowerSeries.coeff_one, Polynomial.coeff_one]

/-- Constant-coefficient operator inversion on polynomials: if `A * B = 1`,
then the degree-`d` truncations of `A(∂)` and `B(∂)` compose to the
identity on every polynomial of degree at most `d`. -/
theorem truncatedDifferentialOperator_mul_apply_of_natDegree_le
    {A B : S⟦X⟧} {d : ℕ} {p : Polynomial S} (hp : p.natDegree ≤ d)
    (hAB : A * B = 1) :
    (truncatedDifferentialOperator d A * truncatedDifferentialOperator d B) p = p := by
  obtain ⟨Q, hQ⟩ := X_pow_dvd_trunc_mul_trunc_sub_one (S := S) d hAB
  have hQ' :
      PowerSeries.trunc (d + 1) A * PowerSeries.trunc (d + 1) B - 1 =
        Q * Polynomial.X ^ (d + 1) := by
    rw [hQ, mul_comm]
  have heval := congrArg polynomialDifferentialEval hQ'
  simp only [map_sub, map_mul, map_pow, map_one] at heval
  have hderiv :
      ((Polynomial.derivative : Module.End S (Polynomial S)) ^ (d + 1)) p = 0 := by
    rw [Module.End.pow_apply]
    exact Polynomial.iterate_derivative_eq_zero
      (lt_of_le_of_lt hp (Nat.lt_succ_self d))
  have happ := congrArg (fun T : Module.End S (Polynomial S) => T p) heval
  rw [LinearMap.sub_apply, Module.End.mul_apply, Module.End.mul_apply,
    Module.End.one_apply] at happ
  rw [polynomialDifferentialEval_X] at happ
  change
    polynomialDifferentialEval (PowerSeries.trunc (d + 1) A)
          (polynomialDifferentialEval (PowerSeries.trunc (d + 1) B) p) - p =
      polynomialDifferentialEval Q
        (((Polynomial.derivative : Module.End S (Polynomial S)) ^ (d + 1)) p) at happ
  rw [hderiv, LinearMap.map_zero] at happ
  change
    (polynomialDifferentialEval (PowerSeries.trunc (d + 1) A) *
      polynomialDifferentialEval (PowerSeries.trunc (d + 1) B)) p = p
  exact sub_eq_zero.mp happ

/-- The `r = 1` inverse-operator relation of Proposition 9.9 for a normalized
residue section.  `expand N` performs the substitution `w = z^N`; hence the
two displayed symbols are `Φₙ,ⱼ(z^N)` and its reciprocal. -/
theorem truncatedDifferentialOperator_normalizedResidueSection_inverse
    {K : Type*} [Field K] [CharZero K] (N j d : ℕ) (hN : 0 < N)
    {p : Polynomial K} (hp : p.natDegree ≤ d) :
    (truncatedDifferentialOperator d
        (PowerSeries.expand N hN.ne'
          (normalizedResidueSection (K := K) N j)) *
      truncatedDifferentialOperator d
        (PowerSeries.expand N hN.ne'
          (normalizedResidueSection (K := K) N j)⁻¹)) p = p := by
  apply truncatedDifferentialOperator_mul_apply_of_natDegree_le hp
  rw [← map_mul]
  rw [PowerSeries.mul_inv_cancel]
  · exact map_one _
  · simp

end TruncatedOperatorInversion

end

end Komorebi.PaperIV
