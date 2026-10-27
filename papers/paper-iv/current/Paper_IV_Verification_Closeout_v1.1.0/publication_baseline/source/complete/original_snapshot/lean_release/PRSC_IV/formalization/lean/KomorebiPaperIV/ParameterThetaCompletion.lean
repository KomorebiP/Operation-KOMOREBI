/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.AlgebraicCompletion
import KomorebiPaperIV.ThetaCore
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Algebra.Polynomial.Degree.Operations

/-!
# Parameter and theta completion for Paper IV

This file supplies manuscript-facing arbitrary-parameter versions of the
normalized-residue reciprocal and Appell constructions.  It also packages the
theta coefficients as honest polynomials in the parameter and proves the
formal Newton recurrence.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

section Naturality

variable {R S : Type*} [CommRing R] [Algebra ℚ R]
  [CommRing S] [Algebra ℚ S]

/-- A normalized residue section over an arbitrary rational algebra.  This is
the rational-coefficient form of `normalizedResidueSection`. -/
def normalizedResidueSectionAlg (N j : ℕ) : R⟦X⟧ :=
  PowerSeries.mk fun n =>
    algebraMap ℚ R ((j.factorial : ℚ) / ((N * n + j).factorial : ℚ))

@[simp]
theorem coeff_normalizedResidueSectionAlg (N j n : ℕ) :
    PowerSeries.coeff n (normalizedResidueSectionAlg (R := R) N j) =
      algebraMap ℚ R
        ((j.factorial : ℚ) / ((N * n + j).factorial : ℚ)) := by
  simp [normalizedResidueSectionAlg]

@[simp]
theorem constantCoeff_normalizedResidueSectionAlg (N j : ℕ) :
    (normalizedResidueSectionAlg (R := R) N j).constantCoeff = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff]
  rw [coeff_normalizedResidueSectionAlg]
  simp only [Nat.mul_zero, zero_add]
  have hj : (j.factorial : ℚ) ≠ 0 := by positivity
  rw [div_self hj, map_one]

theorem normalizedResidueSectionAlg_eq_normalizedResidueSection
    {K : Type*} [Field K] [CharZero K] (N j : ℕ) :
    normalizedResidueSectionAlg (R := K) N j =
      normalizedResidueSection (K := K) N j := by
  ext n
  rw [coeff_normalizedResidueSectionAlg, coeff_normalizedResidueSection]
  simp

theorem map_normalizedResidueSectionAlg (φ : R →ₐ[ℚ] S) (N j : ℕ) :
    PowerSeries.map (φ : R →+* S) (normalizedResidueSectionAlg (R := R) N j) =
      normalizedResidueSectionAlg (R := S) N j := by
  ext n
  simp

/-- Formal negative logarithm of the normalized residue section. -/
def normalizedResidueNegativeLog (N j : ℕ) : R⟦X⟧ :=
  -PowerSeries.logOf (normalizedResidueSectionAlg (R := R) N j)

@[simp]
theorem constantCoeff_normalizedResidueNegativeLog (N j : ℕ) :
    (normalizedResidueNegativeLog (R := R) N j).constantCoeff = 0 := by
  simp [normalizedResidueNegativeLog,
    PowerSeries.constantCoeff_logOf,
    constantCoeff_normalizedResidueSectionAlg]

/-- `logOf` commutes with morphisms of rational algebras on unit-constant
series. -/
theorem map_logOf_of_constantCoeff_one (φ : R →ₐ[ℚ] S) {f : R⟦X⟧}
    (hf : f.constantCoeff = 1) :
    PowerSeries.map (φ : R →+* S) (PowerSeries.logOf f) =
      PowerSeries.logOf (PowerSeries.map (φ : R →+* S) f) := by
  rw [PowerSeries.logOf_eq, PowerSeries.logOf_eq]
  have hzero : (f - 1).constantCoeff = 0 := by simp [hf]
  let hsub : PowerSeries.HasSubst (f - 1) :=
    PowerSeries.HasSubst.of_constantCoeff_zero' hzero
  change ((PowerSeries.log R).subst (f - 1)).map (φ : R →+* S) = _
  rw [PowerSeries.map_subst hsub]
  rw [PowerSeries.map_log]
  have hmap : MvPowerSeries.map (φ : R →+* S) (f - 1) =
      PowerSeries.map (φ : R →+* S) f - 1 := by
    rw [map_sub, map_one]
    rfl
  rw [hmap]

theorem map_normalizedResidueNegativeLog (φ : R →ₐ[ℚ] S) (N j : ℕ) :
    PowerSeries.map (φ : R →+* S)
        (normalizedResidueNegativeLog (R := R) N j) =
      normalizedResidueNegativeLog (R := S) N j := by
  rw [normalizedResidueNegativeLog, normalizedResidueNegativeLog, map_neg,
    map_logOf_of_constantCoeff_one φ
      (constantCoeff_normalizedResidueSectionAlg (R := R) N j),
    map_normalizedResidueSectionAlg]

/-- Naturality of a zero-constant formal exponential parameter family. -/
theorem map_formalExpFamily (φ : R →ₐ[ℚ] S) {L : R⟦X⟧}
    (hL : L.constantCoeff = 0) (r : R) :
    PowerSeries.map (φ : R →+* S) (formalExpFamily L r) =
      formalExpFamily (PowerSeries.map (φ : R →+* S) L) (φ r) := by
  let hsub : PowerSeries.HasSubst L :=
    PowerSeries.HasSubst.of_constantCoeff_zero' hL
  rw [formalExpFamily, formalExpFamily]
  change ((PowerSeries.rescale r (PowerSeries.exp R)).subst L).map
      (φ : R →+* S) = _
  rw [PowerSeries.map_subst hsub]
  rw [← PowerSeries.rescale_map (φ : R →+* S), PowerSeries.map_exp]
  have hmap : MvPowerSeries.map (φ : R →+* S) L =
      PowerSeries.map (φ : R →+* S) L := rfl
  rw [hmap]
  rfl

@[simp]
theorem constantCoeff_formalExpFamily_of_zero {L : R⟦X⟧}
    (hL : L.constantCoeff = 0) (r : R) :
    (formalExpFamily L r).constantCoeff = 1 := by
  rw [formalExpFamily]
  change MvPowerSeries.constantCoeff
      ((PowerSeries.rescale r (PowerSeries.exp R)).subst L) = 1
  rw [PowerSeries.constantCoeff_subst_of_constantCoeff_zero hL]
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, PowerSeries.coeff_rescale]
  simp

end Naturality

section ResidueParameter

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- The exact formal family `Phi_(N,j)(w)^(-r)`. -/
def residuePowerSeries (N j : ℕ) (r : R) : R⟦X⟧ :=
  formalExpFamily (normalizedResidueNegativeLog (R := R) N j) r

@[simp]
theorem constantCoeff_residuePowerSeries (N j : ℕ) (r : R) :
    (residuePowerSeries N j r).constantCoeff = 1 := by
  rw [residuePowerSeries, formalExpFamily]
  change MvPowerSeries.constantCoeff
      ((PowerSeries.rescale r (PowerSeries.exp R)).subst
        (normalizedResidueNegativeLog N j)) = 1
  rw [PowerSeries.constantCoeff_subst_of_constantCoeff_zero
    (constantCoeff_normalizedResidueNegativeLog N j)]
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, PowerSeries.coeff_rescale]
  simp

@[simp]
theorem residuePowerSeries_zero (N j : ℕ) :
    residuePowerSeries (R := R) N j 0 = 1 := by
  exact formalExpFamily_zero (constantCoeff_normalizedResidueNegativeLog N j)

theorem residuePowerSeries_neg_one (N j : ℕ) :
    residuePowerSeries (R := R) N j (-1) =
      normalizedResidueSectionAlg N j := by
  rw [residuePowerSeries,
    formalExpFamily_eq_exp_subst
      (constantCoeff_normalizedResidueNegativeLog (R := R) N j)]
  rw [normalizedResidueNegativeLog]
  have h := exp_subst_logOf
    (constantCoeff_normalizedResidueSectionAlg (R := R) N j)
  simpa using h

theorem residuePowerSeries_add (N j : ℕ) (r s : R) :
    residuePowerSeries N j r * residuePowerSeries N j s =
      residuePowerSeries N j (r + s) := by
  exact formalExpFamily_semigroup
    (constantCoeff_normalizedResidueNegativeLog N j) r s

theorem map_residuePowerSeries {S : Type*} [CommRing S] [Algebra ℚ S]
    (φ : R →ₐ[ℚ] S) (N j : ℕ) (r : R) :
    PowerSeries.map (φ : R →+* S) (residuePowerSeries N j r) =
      residuePowerSeries N j (φ r) := by
  rw [residuePowerSeries, map_formalExpFamily φ
    (constantCoeff_normalizedResidueNegativeLog N j),
    map_normalizedResidueNegativeLog]
  rfl

section Field

variable {K : Type*} [Field K] [CharZero K]

theorem residuePowerSeries_one_eq_inverse (N j : ℕ) :
    residuePowerSeries (R := K) N j 1 =
      (normalizedResidueSectionAlg N j)⁻¹ := by
  apply (PowerSeries.eq_inv_iff_mul_eq_one
    (by simp : (normalizedResidueSectionAlg (R := K) N j).constantCoeff ≠ 0)).2
  rw [← residuePowerSeries_neg_one (R := K) N j]
  rw [residuePowerSeries_add, add_neg_cancel, residuePowerSeries_zero]

end Field

/-- Paper IV's arbitrary-order coefficient `C_(N,j,n)(r)`. -/
def residuePowerCoeff (N j n : ℕ) (r : R) : R :=
  blockCoeff N n (residuePowerSeries N j r)

@[simp]
theorem residuePowerCoeff_zero (N j : ℕ) (r : R) :
    residuePowerCoeff N j 0 r = 1 := by
  simp [residuePowerCoeff, blockCoeff]

theorem residuePowerCoeff_addition (N j n : ℕ) (r s : R) :
    residuePowerCoeff N j n (r + s) =
      ∑ q ∈ Finset.range (n + 1),
        ((N * n).choose (N * q) : R) *
          residuePowerCoeff N j q r * residuePowerCoeff N j (n - q) s := by
  exact reciprocal_block_convolution
    (constantCoeff_normalizedResidueNegativeLog N j) N n r s

theorem residuePowerCoeff_one_eq_residueInverseCoeff
    {K : Type*} [Field K] [CharZero K] (N j n : ℕ) :
    residuePowerCoeff (R := K) N j n 1 =
      residueInverseCoeff (K := K) N j n := by
  rw [residuePowerCoeff, residueInverseCoeff,
    residuePowerSeries_one_eq_inverse,
    normalizedResidueSectionAlg_eq_normalizedResidueSection]
  rfl

section PolynomialParameter

variable {K : Type*} [Field K] [CharZero K]

/-- The coefficient `C_(N,j,n)(r)` lifted to an honest polynomial in `r`. -/
def residuePowerCoeffPolynomial (N j n : ℕ) : Polynomial K :=
  residuePowerCoeff (R := Polynomial K) N j n Polynomial.X

/-- Evaluation of the polynomial lift recovers the arbitrary scalar
parameter coefficient. -/
theorem eval_residuePowerCoeffPolynomial (N j n : ℕ) (r : K) :
    (residuePowerCoeffPolynomial (K := K) N j n).eval r =
      residuePowerCoeff (R := K) N j n r := by
  let φ : Polynomial K →ₐ[ℚ] K :=
    (Polynomial.aeval r).restrictScalars ℚ
  change φ (residuePowerCoeff
      (R := Polynomial K) N j n Polynomial.X) = _
  rw [residuePowerCoeff, residuePowerCoeff, blockCoeff, blockCoeff]
  simp only [map_mul, map_natCast]
  congr 1
  change PowerSeries.coeff n
      (PowerSeries.map (φ : Polynomial K →+* K)
        (residuePowerSeries N j Polynomial.X)) = _
  rw [map_residuePowerSeries φ]
  simp [φ]

/-- Coefficients of `exp (X L)` have parameter degree at most their series
index when the coefficients of `L` are scalar constants. -/
theorem natDegree_coeff_formalExpFamily_map_C_le
    (L : K⟦X⟧) (hL : L.constantCoeff = 0) (n : ℕ) :
    (PowerSeries.coeff n
      (formalExpFamily (PowerSeries.map Polynomial.C L) Polynomial.X)).natDegree ≤ n := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
      cases n with
      | zero =>
          rw [PowerSeries.coeff_zero_eq_constantCoeff]
          rw [constantCoeff_formalExpFamily_of_zero]
          · simp
          · change Polynomial.C (PowerSeries.constantCoeff L) = 0
            rw [hL, map_zero]
      | succ k =>
          let LC : (Polynomial K)⟦X⟧ := PowerSeries.map Polynomial.C L
          have hLC : LC.constantCoeff = 0 := by
            change Polynomial.C (PowerSeries.constantCoeff L) = 0
            rw [hL, map_zero]
          have hrec := formalExpFamily_coefficient_recurrence
            hLC Polynomial.X k
          have hsum :
              (∑ p ∈ Finset.antidiagonal k,
                PowerSeries.coeff p.1 (formalExpFamily LC Polynomial.X) *
                  ((p.2 + 1 : Polynomial K) *
                    PowerSeries.coeff (p.2 + 1) LC)).natDegree ≤ k := by
            apply Polynomial.natDegree_sum_le_of_forall_le
            intro p hp
            have hpadd : p.1 + p.2 = k := Finset.mem_antidiagonal.mp hp
            have hp_lt : p.1 < k + 1 := by omega
            have hpdeg :
                (PowerSeries.coeff p.1
                  (formalExpFamily LC Polynomial.X)).natDegree ≤ p.1 := by
              simpa [LC] using ih p.1 hp_lt
            have hconst :
                (((p.2 + 1 : Polynomial K) *
                  PowerSeries.coeff (p.2 + 1) LC)).natDegree ≤ 0 := by
              have ha : (p.2 + 1 : Polynomial K).natDegree ≤ 0 := by
                change (Polynomial.C (p.2 : K) + Polynomial.C 1).natDegree ≤ 0
                rw [← map_add]
                simp
              have hb : (PowerSeries.coeff (p.2 + 1) LC).natDegree ≤ 0 := by
                rw [show PowerSeries.coeff (p.2 + 1) LC =
                    Polynomial.C (PowerSeries.coeff (p.2 + 1) L) by
                      simp [LC]]
                simp
              exact Polynomial.natDegree_mul_le_of_le ha hb
            exact (Polynomial.natDegree_mul_le_of_le hpdeg hconst).trans (by omega)
          have hrhs :
              (Polynomial.X *
                ∑ p ∈ Finset.antidiagonal k,
                  PowerSeries.coeff p.1 (formalExpFamily LC Polynomial.X) *
                    ((p.2 + 1 : Polynomial K) *
                      PowerSeries.coeff (p.2 + 1) LC)).natDegree ≤ k + 1 := by
            exact (Polynomial.natDegree_mul_le_of_le Polynomial.natDegree_X_le hsum).trans
              (by omega)
          have hscalar : (k + 1 : Polynomial K) =
              Polynomial.C (k + 1 : K) := by simp
          have hscalar_ne : (k + 1 : K) ≠ 0 := by
            exact_mod_cast Nat.succ_ne_zero k
          rw [hscalar] at hrec
          have hdeg_left :
              (Polynomial.C (k + 1 : K) *
                PowerSeries.coeff (k + 1)
                  (formalExpFamily LC Polynomial.X)).natDegree =
                (PowerSeries.coeff (k + 1)
                  (formalExpFamily LC Polynomial.X)).natDegree := by
            rw [Polynomial.natDegree_C_mul hscalar_ne]
          rw [← hdeg_left]
          rw [hrec]
          simpa only [LC] using hrhs

/-- The top parameter coefficient of `exp (X L)` comes only from the nth
power of the linear term of `L`. -/
theorem coeff_parameterDegree_formalExpFamily_map_C
    (L : K⟦X⟧) (hL : L.constantCoeff = 0) (n : ℕ) :
    (PowerSeries.coeff n
      (formalExpFamily (PowerSeries.map Polynomial.C L) Polynomial.X)).coeff n =
      (PowerSeries.coeff 1 L) ^ n / (n.factorial : K) := by
  induction n with
  | zero =>
      rw [PowerSeries.coeff_zero_eq_constantCoeff,
        constantCoeff_formalExpFamily_of_zero]
      · simp
      · change Polynomial.C (PowerSeries.constantCoeff L) = 0
        rw [hL, map_zero]
  | succ k ih =>
      let LC : (Polynomial K)⟦X⟧ := PowerSeries.map Polynomial.C L
      have hLC : LC.constantCoeff = 0 := by
        change Polynomial.C (PowerSeries.constantCoeff L) = 0
        rw [hL, map_zero]
      have hrec := formalExpFamily_coefficient_recurrence
        hLC Polynomial.X k
      rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at hrec
      have hsumCoeff :
          (fun p : Polynomial K => p.coeff k)
              (∑ q ∈ Finset.range (k + 1),
                PowerSeries.coeff q (formalExpFamily LC Polynomial.X) *
                  ((((k - q : ℕ) : Polynomial K) + 1) *
                    PowerSeries.coeff (k - q + 1) LC)) =
            (PowerSeries.coeff k
              (formalExpFamily LC Polynomial.X)).coeff k *
                PowerSeries.coeff 1 L := by
        change
          (∑ q ∈ Finset.range (k + 1),
            PowerSeries.coeff q (formalExpFamily LC Polynomial.X) *
              ((((k - q : ℕ) : Polynomial K) + 1) *
                PowerSeries.coeff (k - q + 1) LC)).coeff k = _
        rw [Polynomial.finsetSum_coeff, Finset.sum_range_succ]
        have hvanish :
            ∑ q ∈ Finset.range k,
                (fun p : Polynomial K => p.coeff k)
                  (PowerSeries.coeff q (formalExpFamily LC Polynomial.X) *
                    ((((k - q : ℕ) : Polynomial K) + 1) *
                      PowerSeries.coeff (k - q + 1) LC)) = 0 := by
          apply Finset.sum_eq_zero
          intro q hq
          have hqk : q < k := Finset.mem_range.mp hq
          have hqdeg :
              (PowerSeries.coeff q
                (formalExpFamily LC Polynomial.X)).natDegree ≤ q := by
            simpa [LC] using natDegree_coeff_formalExpFamily_map_C_le L hL q
          have hconst :
              (((((k - q : ℕ) : Polynomial K) + 1) *
                PowerSeries.coeff (k - q + 1) LC)).natDegree ≤ 0 := by
            have ha : (((k - q : ℕ) : Polynomial K) + 1).natDegree ≤ 0 := by
              simp
            have hb :
                (PowerSeries.coeff (k - q + 1) LC).natDegree ≤ 0 := by
              rw [show PowerSeries.coeff (k - q + 1) LC =
                  Polynomial.C (PowerSeries.coeff (k - q + 1) L) by
                    simp [LC]]
              simp
            exact Polynomial.natDegree_mul_le_of_le ha hb
          exact Polynomial.coeff_eq_zero_of_natDegree_lt
            ((Polynomial.natDegree_mul_le_of_le hqdeg hconst).trans_lt (by omega))
        rw [hvanish, zero_add]
        simp only [Nat.sub_self, zero_add]
        rw [show PowerSeries.coeff 1 LC =
            Polynomial.C (PowerSeries.coeff 1 L) by simp [LC]]
        simp [Polynomial.coeff_mul_C]
      have hpoly := congrArg (fun p : Polynomial K => p.coeff (k + 1)) hrec
      rw [show (k + 1 : Polynomial K) =
          Polynomial.C (k + 1 : K) by simp,
        Polynomial.coeff_C_mul, Polynomial.coeff_X_mul] at hpoly
      simp only [Nat.succ_eq_add_one] at hpoly
      have hsumCoeffEq :
          (∑ q ∈ Finset.range (k + 1),
            PowerSeries.coeff q (formalExpFamily LC Polynomial.X) *
              ((((k - q : ℕ) : Polynomial K) + 1) *
                PowerSeries.coeff (k - q + 1) LC)).coeff k =
            (PowerSeries.coeff k
              (formalExpFamily LC Polynomial.X)).coeff k *
                PowerSeries.coeff 1 L := hsumCoeff
      rw [hsumCoeffEq] at hpoly
      change (k + 1 : K) *
          (PowerSeries.coeff (k + 1)
            (formalExpFamily LC Polynomial.X)).coeff (k + 1) = _ at hpoly
      rw [show PowerSeries.coeff k (formalExpFamily LC Polynomial.X) =
          PowerSeries.coeff k
            (formalExpFamily (PowerSeries.map Polynomial.C L) Polynomial.X) by rfl,
        ih] at hpoly
      rw [show PowerSeries.coeff (k + 1)
          (formalExpFamily (PowerSeries.map Polynomial.C L) Polynomial.X) =
          PowerSeries.coeff (k + 1)
            (formalExpFamily LC Polynomial.X) by rfl]
      have hfac : (k.factorial : K) ≠ 0 := by
        exact_mod_cast k.factorial_pos.ne'
      have hsuccfac : ((k + 1).factorial : K) ≠ 0 := by
        exact_mod_cast (k + 1).factorial_pos.ne'
      apply (eq_div_iff hsuccfac).2
      rw [Nat.factorial_succ, Nat.cast_mul]
      rw [Nat.cast_add, Nat.cast_one]
      calc
        (PowerSeries.coeff (k + 1)
              (formalExpFamily LC Polynomial.X)).coeff (k + 1) *
            ((k + 1 : K) * (k.factorial : K)) =
          ((k + 1 : K) *
            (PowerSeries.coeff (k + 1)
              (formalExpFamily LC Polynomial.X)).coeff (k + 1)) *
                (k.factorial : K) := by ring
        _ = (((PowerSeries.coeff 1 L) ^ k / (k.factorial : K)) *
              PowerSeries.coeff 1 L) * (k.factorial : K) := by rw [hpoly]
        _ = (PowerSeries.coeff 1 L) ^ (k + 1) := by
          rw [pow_succ]
          field_simp

theorem coeff_one_logOf_of_constantCoeff_one {f : K⟦X⟧}
    (hf : f.constantCoeff = 1) :
    PowerSeries.coeff 1 (PowerSeries.logOf f) = PowerSeries.coeff 1 f := by
  have h := congrArg (PowerSeries.coeff (R := K) 0)
    (mul_derivative_logOf hf)
  rw [PowerSeries.coeff_mul, Finset.Nat.antidiagonal_zero] at h
  simp [PowerSeries.coeff_derivative, hf] at h
  exact h

theorem coeff_one_normalizedResidueNegativeLog (N j : ℕ) :
    PowerSeries.coeff 1 (normalizedResidueNegativeLog (R := K) N j) =
      -(j.factorial : K) / ((N + j).factorial : K) := by
  rw [normalizedResidueNegativeLog, map_neg,
    coeff_one_logOf_of_constantCoeff_one
      (constantCoeff_normalizedResidueSectionAlg (R := K) N j),
    coeff_normalizedResidueSectionAlg]
  simp only [Nat.mul_one]
  rw [show N + j = N * 1 + j by simp]
  simp
  ring

/-- Exact leading coefficient asserted in Theorem 9.4. -/
theorem coeff_residuePowerCoeffPolynomial_parameterDegree (N j n : ℕ) :
    (residuePowerCoeffPolynomial (K := K) N j n).coeff n =
      ((N * n).factorial : K) / (n.factorial : K) *
        (-(j.factorial : K) / ((N + j).factorial : K)) ^ n := by
  let L : K⟦X⟧ := normalizedResidueNegativeLog (R := K) N j
  let Cφ : K →ₐ[ℚ] Polynomial K :=
    (Polynomial.CAlgHom : K →ₐ[K] Polynomial K).restrictScalars ℚ
  have hmapL : PowerSeries.map (Cφ : K →+* Polynomial K) L =
      normalizedResidueNegativeLog (R := Polynomial K) N j := by
    simpa [L, Cφ] using map_normalizedResidueNegativeLog Cφ N j
  have hmapC : PowerSeries.map (Cφ : K →+* Polynomial K) L =
      PowerSeries.map Polynomial.C L := by
    ext q
    simp [Cφ]
  rw [residuePowerCoeffPolynomial, residuePowerCoeff, blockCoeff,
    residuePowerSeries, ← hmapL]
  rw [show ((N * n).factorial : Polynomial K) =
      Polynomial.C ((N * n).factorial : K) by simp]
  rw [hmapC]
  rw [Polynomial.coeff_C_mul,
    coeff_parameterDegree_formalExpFamily_map_C L
      (constantCoeff_normalizedResidueNegativeLog N j),
    coeff_one_normalizedResidueNegativeLog]
  field_simp

theorem natDegree_residuePowerCoeffPolynomial_le (N j n : ℕ) :
    (residuePowerCoeffPolynomial (K := K) N j n).natDegree ≤ n := by
  let L : K⟦X⟧ := normalizedResidueNegativeLog (R := K) N j
  let Cφ : K →ₐ[ℚ] Polynomial K :=
    (Polynomial.CAlgHom : K →ₐ[K] Polynomial K).restrictScalars ℚ
  have hmapL : PowerSeries.map (Cφ : K →+* Polynomial K) L =
      normalizedResidueNegativeLog (R := Polynomial K) N j := by
    simpa [L, Cφ] using map_normalizedResidueNegativeLog Cφ N j
  have hdeg := natDegree_coeff_formalExpFamily_map_C_le L
    (constantCoeff_normalizedResidueNegativeLog N j) n
  rw [residuePowerCoeffPolynomial, residuePowerCoeff, blockCoeff,
    residuePowerSeries, ← hmapL]
  exact (Polynomial.natDegree_C_mul_le _ _).trans hdeg

/-- The parameter degree in Theorem 9.4 is exact. -/
theorem natDegree_residuePowerCoeffPolynomial (N j n : ℕ) :
    (residuePowerCoeffPolynomial (K := K) N j n).natDegree = n := by
  apply Polynomial.natDegree_eq_of_le_of_coeff_ne_zero
    (natDegree_residuePowerCoeffPolynomial_le N j n)
  rw [coeff_residuePowerCoeffPolynomial_parameterDegree]
  have hNn : ((N * n).factorial : K) ≠ 0 := by
    exact_mod_cast (N * n).factorial_pos.ne'
  have hn : (n.factorial : K) ≠ 0 := by
    exact_mod_cast n.factorial_pos.ne'
  have hj : (j.factorial : K) ≠ 0 := by
    exact_mod_cast j.factorial_pos.ne'
  have hNj : ((N + j).factorial : K) ≠ 0 := by
    exact_mod_cast (N + j).factorial_pos.ne'
  exact mul_ne_zero (div_ne_zero hNn hn)
    (pow_ne_zero n (div_ne_zero (neg_ne_zero.mpr hj) hNj))

end PolynomialParameter

end ResidueParameter

section ResidueAppellParameter

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- The normalized-residue logarithm after the substitution `w = z^N`. -/
def expandedResidueNegativeLog (N j : ℕ) (hN : 0 < N) : R⟦X⟧ :=
  PowerSeries.expand N hN.ne'
    (normalizedResidueNegativeLog (R := R) N j)

@[simp]
theorem constantCoeff_expandedResidueNegativeLog (N j : ℕ) (hN : 0 < N) :
    (expandedResidueNegativeLog (R := R) N j hN).constantCoeff = 0 := by
  simp [expandedResidueNegativeLog]

/-- Expanding the reduced arbitrary-order reciprocal commutes with its formal
exponential construction. -/
theorem expand_residuePowerSeries (N j : ℕ) (hN : 0 < N) (r : R) :
    PowerSeries.expand N hN.ne' (residuePowerSeries N j r) =
      formalExpFamily (expandedResidueNegativeLog N j hN) r := by
  rw [residuePowerSeries, formalExpFamily, expandedResidueNegativeLog]
  let hsub : PowerSeries.HasSubst
      (normalizedResidueNegativeLog (R := R) N j) :=
    PowerSeries.HasSubst.of_constantCoeff_zero'
      (constantCoeff_normalizedResidueNegativeLog N j)
  exact PowerSeries.expand_subst N hN.ne' hsub
    (PowerSeries.rescale r (PowerSeries.exp R))

/-- The EGF coefficients of the expanded reciprocal are precisely the sparse
block sequence attached to `C_(N,j,n)(r)`. -/
theorem egfCoeff_expand_residuePowerSeries (N j q : ℕ) (hN : 0 < N)
    (r : R) :
    egfCoeff q (PowerSeries.expand N hN.ne' (residuePowerSeries N j r)) =
      blockCoefficientSequence N (fun n => residuePowerCoeff N j n r) q := by
  by_cases hdvd : N ∣ q
  · have hmul : N * (q / N) = q := Nat.mul_div_cancel' hdvd
    simp [egfCoeff, blockCoefficientSequence, residuePowerCoeff, blockCoeff,
      PowerSeries.coeff_expand, hdvd, hmul]
  · simp [egfCoeff, blockCoefficientSequence, PowerSeries.coeff_expand, hdvd]

/-- The exact arbitrary-order residue Appell polynomial
`E_m^(N,j,r)(x)`. -/
def residueAppellPolynomialParam (N j : ℕ) (hN : 0 < N)
    (r : R) (m : ℕ) : Polynomial R :=
  formalAppellPolynomial (expandedResidueNegativeLog N j hN) r m

theorem residueAppellPolynomialParam_eq_block (N j : ℕ) (hN : 0 < N)
    (r : R) (m : ℕ) :
    residueAppellPolynomialParam N j hN r m =
      appellPolynomial
        (blockCoefficientSequence N (fun n => residuePowerCoeff N j n r)) m := by
  rw [residueAppellPolynomialParam, formalAppellPolynomial]
  congr 1
  funext q
  rw [← expand_residuePowerSeries N j hN r]
  exact egfCoeff_expand_residuePowerSeries N j q hN r

/-- The manuscript's finite explicit sum, now specialized at arbitrary
reciprocal order `r`. -/
theorem residueAppellPolynomialParam_explicit (N j : ℕ) (hN : 0 < N)
    (r : R) (m : ℕ) :
    residueAppellPolynomialParam N j hN r m =
      ∑ n ∈ Finset.range (m / N + 1),
        Polynomial.C
            ((m.choose (N * n) : R) * residuePowerCoeff N j n r) *
          Polynomial.X ^ (m - N * n) := by
  rw [residueAppellPolynomialParam_eq_block]
  exact appellPolynomial_eq_block_sum N m hN _

/-- Exact Appell lowering law for every residue order. -/
theorem derivative_residueAppellPolynomialParam (N j : ℕ) (hN : 0 < N)
    (r : R) (m : ℕ) :
    Polynomial.derivative (residueAppellPolynomialParam N j hN r (m + 1)) =
      Polynomial.C (m + 1 : R) * residueAppellPolynomialParam N j hN r m := by
  exact derivative_formalAppellPolynomial
    (expandedResidueNegativeLog N j hN) r m

/-- Exact Appell translation law in the manuscript's arbitrary-order
normalized-residue specialization. -/
theorem eval_residueAppellPolynomialParam_add (N j : ℕ) (hN : 0 < N)
    (r x y : R) (m : ℕ) :
    (residueAppellPolynomialParam N j hN r m).eval (x + y) =
      ∑ p ∈ Finset.antidiagonal m,
        (m.choose p.1 : R) *
          (residueAppellPolynomialParam N j hN r p.1).eval x * y ^ p.2 := by
  let L : R⟦X⟧ := expandedResidueNegativeLog N j hN
  have hL : L.constantCoeff = 0 := by simp [L]
  have h := appell_addition hL r x y m
  simpa [residueAppellPolynomialParam, L, eval_formalAppellPolynomial] using h

/-- Exact joint convolution in space and residue order. -/
theorem eval_residueAppellPolynomialParam_two_parameter
    (N j : ℕ) (hN : 0 < N) (r s x y : R) (m : ℕ) :
    (residueAppellPolynomialParam N j hN (r + s) m).eval (x + y) =
      ∑ p ∈ Finset.antidiagonal m,
        (m.choose p.1 : R) *
          (residueAppellPolynomialParam N j hN r p.1).eval x *
          (residueAppellPolynomialParam N j hN s p.2).eval y := by
  let L : R⟦X⟧ := expandedResidueNegativeLog N j hN
  have hL : L.constantCoeff = 0 := by simp [L]
  have h := appell_two_parameter_convolution hL r s x y m
  simpa [residueAppellPolynomialParam, L, eval_formalAppellPolynomial] using h

/-- The arbitrary-order residue Appell polynomial is monic of exact degree
`m`. -/
theorem residueAppellPolynomialParam_isMonicOfDegree [Nontrivial R]
    (N j : ℕ) (hN : 0 < N) (r : R) (m : ℕ) :
    Polynomial.IsMonicOfDegree
      (residueAppellPolynomialParam N j hN r m) m := by
  rw [residueAppellPolynomialParam_eq_block]
  apply blockAppellPolynomial_isMonicOfDegree
  simp [residuePowerCoeff_zero]

/-- The exact root-of-unity covariance at arbitrary residue order. -/
theorem eval_residueAppellPolynomialParam_covariance
    (N j : ℕ) (hN : 0 < N) (r ω x : R) (hω : ω ^ N = 1) (m : ℕ) :
    (residueAppellPolynomialParam N j hN r m).eval (ω * x) =
      ω ^ m * (residueAppellPolynomialParam N j hN r m).eval x := by
  rw [residueAppellPolynomialParam_eq_block]
  exact eval_appellPolynomial_block_covariance N m hN _ ω x hω

/-- First half of the differential-operator representation: the arbitrary
residue symbol acting on `X^m` is the named Appell polynomial. -/
theorem egfConstantCoeffAction_residuePowerSeries_X_pow
    (N j : ℕ) (hN : 0 < N) (r : R) (m : ℕ) [Nontrivial R] :
    egfConstantCoeffAction
        (fun q => egfCoeff q
          (PowerSeries.expand N hN.ne' (residuePowerSeries N j r)))
        (Polynomial.X ^ m) =
      residueAppellPolynomialParam N j hN r m := by
  rw [egfConstantCoeffAction_X_pow]
  rw [residueAppellPolynomialParam_eq_block]
  congr 1
  funext q
  exact egfCoeff_expand_residuePowerSeries N j q hN r

/-- Arbitrary formal powers with opposite orders give inverse finite
differential operators on every polynomial of degree at most `d`. -/
theorem truncatedDifferentialOperator_residuePowerSeries_inverse
    (N j : ℕ) (hN : 0 < N) (r : R) (d : ℕ)
    {p : Polynomial R} (hp : p.natDegree ≤ d) :
    (truncatedDifferentialOperator d
        (PowerSeries.expand N hN.ne' (residuePowerSeries N j (-r))) *
      truncatedDifferentialOperator d
        (PowerSeries.expand N hN.ne' (residuePowerSeries N j r))) p = p := by
  apply truncatedDifferentialOperator_mul_apply_of_natDegree_le hp
  rw [← map_mul, residuePowerSeries_add, neg_add_cancel,
    residuePowerSeries_zero, map_one]

end ResidueAppellParameter

section ThetaPolynomial

variable {R S : Type*} [CommRing R] [Algebra ℚ R]
  [CommRing S] [Algebra ℚ S]

theorem map_reducedDenominator (φ : R →ₐ[ℚ] S) (N : ℕ) :
    PowerSeries.map (φ : R →+* S) (reducedDenominator (R := R) N) =
      reducedDenominator (R := S) N := by
  ext n
  simp [reducedDenominator]

theorem map_negativeLogDenominator (φ : R →ₐ[ℚ] S) (N : ℕ) :
    PowerSeries.map (φ : R →+* S)
        (negativeLogDenominator (R := R) N) =
      negativeLogDenominator (R := S) N := by
  rw [negativeLogDenominator, negativeLogDenominator, map_neg,
    map_logOf_of_constantCoeff_one φ
      (constantCoeff_reducedDenominator (R := R) N),
    map_reducedDenominator]

theorem map_reciprocalSeries (φ : R →ₐ[ℚ] S) (N : ℕ) (r : R) :
    PowerSeries.map (φ : R →+* S) (reciprocalSeries N r) =
      reciprocalSeries N (φ r) := by
  rw [reciprocalSeries, map_formalExpFamily φ
    (constantCoeff_negativeLogDenominator N), map_negativeLogDenominator]
  rfl

theorem map_thetaSeries (φ : R →ₐ[ℚ] S) (N : ℕ) (u : R) :
    PowerSeries.map (φ : R →+* S) (thetaSeries N u) =
      thetaSeries N (φ u) := by
  rw [thetaSeries, thetaSeries, map_mul]
  rw [← PowerSeries.rescale_map (φ : R →+* S),
    ← PowerSeries.rescale_map (φ : R →+* S)]
  rw [map_reciprocalSeries, map_reciprocalSeries]
  simp

section Field

variable {K : Type*} [Field K] [CharZero K]

/-- Paper IV's theta coefficient as a polynomial in its parameter. -/
def thetaPolynomial (N n : ℕ) : Polynomial K :=
  thetaCoeff (R := Polynomial K) N n Polynomial.X

/-- The reciprocal coefficient `P_(N,n)(u)` as a polynomial in `u`. -/
def reciprocalCoeffPolynomialOver (N n : ℕ) : Polynomial K :=
  reciprocalCoeff (R := Polynomial K) N n Polynomial.X

theorem eval_reciprocalCoeffPolynomialOver (N n : ℕ) (u : K) :
    (reciprocalCoeffPolynomialOver (K := K) N n).eval u =
      reciprocalCoeff (R := K) N n u := by
  let φ : Polynomial K →ₐ[ℚ] K :=
    (Polynomial.aeval u).restrictScalars ℚ
  change φ (reciprocalCoeff
      (R := Polynomial K) N n Polynomial.X) = _
  rw [reciprocalCoeff, reciprocalCoeff, blockCoeff, blockCoeff]
  simp only [map_mul, map_natCast]
  congr 1
  change PowerSeries.coeff n
      (PowerSeries.map (φ : Polynomial K →+* K)
        (reciprocalSeries N Polynomial.X)) = _
  rw [map_reciprocalSeries φ]
  simp [φ]

theorem natDegree_reciprocalCoeffPolynomialOver_le (N n : ℕ) :
    (reciprocalCoeffPolynomialOver (K := K) N n).natDegree ≤ n := by
  let L : K⟦X⟧ := negativeLogDenominator (R := K) N
  let Cφ : K →ₐ[ℚ] Polynomial K :=
    (Polynomial.CAlgHom : K →ₐ[K] Polynomial K).restrictScalars ℚ
  have hmapL : PowerSeries.map (Cφ : K →+* Polynomial K) L =
      negativeLogDenominator (R := Polynomial K) N := by
    simpa [L, Cφ] using map_negativeLogDenominator Cφ N
  have hdeg := natDegree_coeff_formalExpFamily_map_C_le L
    (constantCoeff_negativeLogDenominator N) n
  rw [reciprocalCoeffPolynomialOver, reciprocalCoeff, blockCoeff,
    reciprocalSeries, ← hmapL]
  exact (Polynomial.natDegree_C_mul_le _ _).trans hdeg

theorem reciprocalCoeff_polynomial_one_eq_C (N n : ℕ) :
    reciprocalCoeff (R := Polynomial K) N n 1 =
      Polynomial.C (reciprocalCoeff (R := K) N n 1) := by
  let Cφ : K →ₐ[ℚ] Polynomial K :=
    (Polynomial.CAlgHom : K →ₐ[K] Polynomial K).restrictScalars ℚ
  have hs := congrArg (PowerSeries.coeff (R := Polynomial K) n)
    (map_reciprocalSeries Cφ N (1 : K))
  rw [PowerSeries.coeff_map] at hs
  simp [Cφ] at hs
  rw [reciprocalCoeff, reciprocalCoeff, blockCoeff, blockCoeff, ← hs]
  simp

theorem eval_thetaPolynomial (N n : ℕ) (u : K) :
    (thetaPolynomial (K := K) N n).eval u = thetaCoeff N n u := by
  let φ : Polynomial K →ₐ[ℚ] K :=
    (Polynomial.aeval u).restrictScalars ℚ
  change φ (thetaCoeff (R := Polynomial K) N n Polynomial.X) = _
  rw [thetaCoeff, thetaCoeff, blockCoeff, blockCoeff]
  simp only [map_mul, map_natCast]
  congr 1
  change PowerSeries.coeff n
      (PowerSeries.map (φ : Polynomial K →+* K)
        (thetaSeries N Polynomial.X)) = _
  rw [map_thetaSeries φ]
  simp [φ]

/-- The reconstruction theorem gives the manuscript degree bound on the
theta polynomial. -/
theorem natDegree_thetaPolynomial_le (N n : ℕ) (hN : 0 < N) :
    (thetaPolynomial (K := K) N n).natDegree ≤ N * n := by
  rw [thetaPolynomial, thetaCoeff_reconstruction]
  have hsum :
      (∑ q ∈ Finset.range (n + 1),
        ((N * n).choose (N * q) : Polynomial K) *
          reciprocalCoeff N q 1 * Polynomial.X ^ (N * q) *
            reciprocalCoeff N (n - q) Polynomial.X).natDegree ≤ N * n := by
    apply Polynomial.natDegree_sum_le_of_forall_le
    intro q hq
    have hqn : q ≤ n := Nat.le_of_lt_succ (Finset.mem_range.mp hq)
    have hconstChoose :
        ((N * n).choose (N * q) : Polynomial K).natDegree ≤ 0 := by simp
    have hconstOne :
        (reciprocalCoeff (R := Polynomial K) N q 1).natDegree ≤ 0 := by
      rw [reciprocalCoeff_polynomial_one_eq_C]
      simp
    have hX : (Polynomial.X ^ (N * q) : Polynomial K).natDegree ≤ N * q :=
      Polynomial.natDegree_X_pow_le (N * q)
    have hparam :
        (reciprocalCoeff (R := Polynomial K) N (n - q) Polynomial.X).natDegree ≤
          n - q := by
      exact natDegree_reciprocalCoeffPolynomialOver_le N (n - q)
    have hterm :
        (((N * n).choose (N * q) : Polynomial K) *
          reciprocalCoeff N q 1 * Polynomial.X ^ (N * q) *
            reciprocalCoeff N (n - q) Polynomial.X).natDegree ≤
          N * q + (n - q) := by
      have hbase :
          (((N * n).choose (N * q) : Polynomial K) *
            reciprocalCoeff N q 1).natDegree ≤ 0 := by
        simpa using Polynomial.natDegree_mul_le_of_le hconstChoose hconstOne
      have hwithX :
          (((N * n).choose (N * q) : Polynomial K) *
            reciprocalCoeff N q 1 * Polynomial.X ^ (N * q)).natDegree ≤
              N * q := by
        simpa using Polynomial.natDegree_mul_le_of_le hbase hX
      exact Polynomial.natDegree_mul_le_of_le hwithX hparam
    have hone : 1 ≤ N := hN
    have hrest : n - q ≤ N * (n - q) := by
      calc
        n - q = 1 * (n - q) := by simp
        _ ≤ N * (n - q) := Nat.mul_le_mul_right (n - q) hone
    have hsplit : N * q + N * (n - q) = N * n := by
      rw [← Nat.mul_add, Nat.add_sub_of_le hqn]
    exact hterm.trans (by omega)
  have hsign : ((-1 : Polynomial K) ^ n).natDegree ≤ 0 := by
    have hneg : (-1 : Polynomial K).natDegree ≤ 0 := by simp
    simpa only [Nat.mul_zero] using Polynomial.natDegree_pow_le_of_le n hneg
  simpa using Polynomial.natDegree_mul_le_of_le hsign hsum

/-- The first trivial theta factor, now as literal polynomial divisibility. -/
theorem X_dvd_thetaPolynomial (N n : ℕ) (hN : 0 < N) (hn : 0 < n) :
    Polynomial.X ∣ thetaPolynomial (K := K) N n := by
  rw [Polynomial.X_dvd_iff, Polynomial.coeff_zero_eq_eval_zero,
    eval_thetaPolynomial]
  exact thetaCoeff_zero_parameter_of_pos N hN hn

/-- For even block size, the second trivial theta factor is literal
divisibility by `X + 1`. -/
theorem X_add_one_dvd_thetaPolynomial_of_even
    (N n : ℕ) (_hN : 0 < N) (heven : Even N) (hn : 0 < n) :
    Polynomial.X + 1 ∣ thetaPolynomial (K := K) N n := by
  have hroot : (thetaPolynomial (K := K) N n).IsRoot (-1) := by
    rw [Polynomial.IsRoot, eval_thetaPolynomial]
    exact thetaCoeff_neg_one_of_even_of_pos N heven hn
  have hdvd := Polynomial.dvd_iff_isRoot.mpr hroot
  simpa [sub_neg_eq_add] using hdvd

end Field

end ThetaPolynomial

section ThetaNewton

variable {R : Type*} [CommRing R] [Algebra ℚ R]

omit [Algebra ℚ R] in
/-- Formal differentiation commutes with rescaling up to the chain-rule
factor. -/
theorem derivative_rescale_series (a : R) (f : R⟦X⟧) :
    PowerSeries.derivative R (PowerSeries.rescale a f) =
      PowerSeries.C a *
        PowerSeries.rescale a (PowerSeries.derivative R f) := by
  ext n
  rw [PowerSeries.coeff_derivative, PowerSeries.coeff_C_mul,
    PowerSeries.coeff_rescale, PowerSeries.coeff_rescale,
    PowerSeries.coeff_derivative, pow_succ]
  ring

omit [Algebra ℚ R] in
theorem rescale_C_series (a r : R) :
    PowerSeries.rescale a (PowerSeries.C r) = PowerSeries.C r := by
  ext (_ | n)
  · simp
  · simp

/-- Logarithmic-derivative factor for a rescaled reciprocal family. -/
def scaledReciprocalLogDerivative (N : ℕ) (a r : R) : R⟦X⟧ :=
  PowerSeries.C (a * r) *
    PowerSeries.rescale a
      (PowerSeries.derivative R (negativeLogDenominator N))

theorem derivative_rescale_reciprocalSeries (N : ℕ) (a r : R) :
    PowerSeries.derivative R
        (PowerSeries.rescale a (reciprocalSeries N r)) =
      PowerSeries.rescale a (reciprocalSeries N r) *
        scaledReciprocalLogDerivative N a r := by
  rw [derivative_rescale_series, derivative_reciprocalSeries]
  rw [map_mul, map_mul]
  rw [rescale_C_series]
  rw [scaledReciprocalLogDerivative]
  rw [map_mul]
  ring

/-- The logarithmic derivative multiplying the theta series. -/
def thetaLogDerivativeSeries (N : ℕ) (u : R) : R⟦X⟧ :=
  scaledReciprocalLogDerivative N (-u ^ N) 1 +
    scaledReciprocalLogDerivative N (-1) u

theorem derivative_thetaSeries (N : ℕ) (u : R) :
    PowerSeries.derivative R (thetaSeries N u) =
      thetaSeries N u * thetaLogDerivativeSeries N u := by
  rw [thetaSeries, thetaLogDerivativeSeries,
    (PowerSeries.derivative R).leibniz]
  simp only [smul_eq_mul]
  rw [
    derivative_rescale_reciprocalSeries,
    derivative_rescale_reciprocalSeries]
  ring

@[simp]
theorem coeff_thetaLogDerivativeSeries (N k : ℕ) (u : R) :
    PowerSeries.coeff k (thetaLogDerivativeSeries N u) =
      (-1 : R) ^ (k + 1) * kappaCoeff N (k + 1) *
        (u ^ (N * (k + 1)) + u) := by
  rw [thetaLogDerivativeSeries, map_add, scaledReciprocalLogDerivative,
    scaledReciprocalLogDerivative, PowerSeries.coeff_C_mul,
    PowerSeries.coeff_C_mul, PowerSeries.coeff_rescale,
    PowerSeries.coeff_rescale, PowerSeries.coeff_derivative, kappaCoeff]
  rw [neg_pow, neg_pow, ← pow_mul]
  rw [Nat.cast_add, Nat.cast_one]
  ring

/-- Ordinary reduced-variable theta coefficient.  This is the manuscript's
`theta_(N,n)(u) = Theta_(N,n)(u)/(Nn)!`. -/
def thetaOrdCoeff (N n : ℕ) (u : R) : R :=
  PowerSeries.coeff n (thetaSeries N u)

@[simp]
theorem thetaOrdCoeff_zero (N : ℕ) (u : R) :
    thetaOrdCoeff N 0 u = 1 := by
  rw [thetaOrdCoeff, thetaSeries, PowerSeries.coeff_mul,
    Finset.Nat.antidiagonal_zero]
  simp

/-- Theta Newton recurrence in exact antidiagonal indexing.  Replacing
`k + 1` by `n` and `p.2 + 1` by `m` gives the displayed manuscript sum
from `m = 1` through `m = n`. -/
theorem thetaOrdCoeff_newton (N k : ℕ) (u : R) :
    (k + 1 : R) * thetaOrdCoeff N (k + 1) u =
      ∑ p ∈ Finset.antidiagonal k,
        thetaOrdCoeff N p.1 u *
          ((-1 : R) ^ (p.2 + 1) * kappaCoeff N (p.2 + 1) *
            (u ^ (N * (p.2 + 1)) + u)) := by
  have h := congrArg (PowerSeries.coeff (R := R) k)
    (derivative_thetaSeries (R := R) N u)
  rw [PowerSeries.coeff_derivative, PowerSeries.coeff_mul] at h
  simp only [coeff_thetaLogDerivativeSeries] at h
  simpa [thetaOrdCoeff, mul_comm] using h

/-- The normalization of the first logarithmic coefficient used in the
closed form for the first theta polynomial. -/
theorem factorial_mul_kappaCoeff_one (N : ℕ) :
    (N.factorial : R) * kappaCoeff N 1 = 1 := by
  have hlog := mul_derivative_logOf
    (constantCoeff_reducedDenominator (R := R) N)
  have hcoeff := congrArg (PowerSeries.coeff (R := R) 0) hlog
  rw [PowerSeries.coeff_mul, PowerSeries.coeff_derivative] at hcoeff
  rw [Finset.Nat.antidiagonal_zero] at hcoeff
  simp at hcoeff
  have hcoeff' :
      PowerSeries.coeff 1 (PowerSeries.logOf
        (reducedDenominator (R := R) N)) =
        algebraMap ℚ R ((-1 : ℚ) / (N.factorial : ℚ)) := by
    rw [← hcoeff]
    rw [← PowerSeries.coeff_zero_eq_constantCoeff,
      PowerSeries.coeff_derivative]
    simp
  rw [kappaCoeff, negativeLogDenominator]
  simp only [Nat.cast_one, one_mul, map_neg]
  rw [hcoeff']
  rw [show (N.factorial : R) =
    algebraMap ℚ R (N.factorial : ℚ) by simp]
  rw [← map_neg, ← map_mul]
  have hfac : (N.factorial : ℚ) ≠ 0 := by positivity
  field_simp
  simp

/-- The first theta coefficient from Proposition 10.4. -/
theorem thetaCoeff_one (N : ℕ) (u : R) :
    thetaCoeff N 1 u = -(u ^ N + u) := by
  have hrec := thetaOrdCoeff_newton (R := R) N 0 u
  simp only [Nat.cast_zero, zero_add, one_mul,
    Finset.Nat.antidiagonal_zero, Finset.sum_singleton,
    thetaOrdCoeff_zero, pow_one, Nat.mul_one] at hrec
  rw [thetaCoeff, blockCoeff]
  simp only [Nat.mul_one]
  change (N.factorial : R) * thetaOrdCoeff N 1 u = _
  rw [hrec]
  have hk := factorial_mul_kappaCoeff_one (R := R) N
  calc
    (N.factorial : R) *
        ((-1 : R) * kappaCoeff N 1 * (u ^ N + u)) =
      -((N.factorial : R) * kappaCoeff N 1) * (u ^ N + u) := by ring
    _ = -(u ^ N + u) := by rw [hk]; ring

end ThetaNewton

end

end Komorebi.PaperIV
