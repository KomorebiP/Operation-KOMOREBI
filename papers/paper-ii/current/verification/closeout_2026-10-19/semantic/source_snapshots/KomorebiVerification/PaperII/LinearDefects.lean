/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Analysis.Normed.Ring.Basic
import Mathlib.Tactic.NoncommRing

/-!
# Paper II: algebraic linear defects

Author: Komorebi P.

This module records the noncommutative telescoping identity for a one-step
intertwining defect.  The identity is valid in every ring and for every
natural power, including power zero.  It also gives the corresponding norm
estimate in a normed ring and proves the inverse-sandwich identity from
explicit left- and right-inverse equations.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.LinearDefects

open scoped BigOperators

universe u

/-! ## Power defects -/

/-- The one-step defect of `C` with respect to the fine operator `Tf` and
the coarse operator `Tc`. -/
def defect {R : Type u} [Ring R] (C Tf Tc : R) : R :=
  C * Tf - Tc * C

/-- The power-defect telescoping identity, including the case `n = 0`.

No factors are commuted: the coarse powers remain on the left of the defect
and the fine powers remain on its right.
-/
theorem power_defect_identity_all {R : Type u} [Ring R]
    (C Tf Tc : R) (n : ℕ) :
    C * Tf ^ n - Tc ^ n * C =
      ∑ k ∈ Finset.range n,
        Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k := by
  induction n with
  | zero => simp [defect]
  | succ n ih =>
      rw [Finset.sum_range_succ]
      calc
        C * Tf ^ (n + 1) - Tc ^ (n + 1) * C =
            Tc * (C * Tf ^ n - Tc ^ n * C) + defect C Tf Tc * Tf ^ n := by
              simp only [defect, pow_succ']
              noncomm_ring
        _ = Tc * (∑ k ∈ Finset.range n,
              Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k) +
              defect C Tf Tc * Tf ^ n := by rw [ih]
        _ = (∑ k ∈ Finset.range n,
              Tc ^ ((n + 1) - 1 - k) * defect C Tf Tc * Tf ^ k) +
              Tc ^ ((n + 1) - 1 - n) * defect C Tf Tc * Tf ^ n := by
              congr 1
              · rw [Finset.mul_sum]
                apply Finset.sum_congr rfl
                intro k hk
                have hklt : k < n := Finset.mem_range.mp hk
                have hexponent : n - 1 - k + 1 = n - k := by omega
                calc
                  Tc * (Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k) =
                      (Tc * Tc ^ (n - 1 - k)) * defect C Tf Tc * Tf ^ k := by
                        simp only [mul_assoc]
                  _ = Tc ^ (n - 1 - k + 1) * defect C Tf Tc * Tf ^ k := by
                        rw [← pow_succ']
                  _ = Tc ^ (n - k) * defect C Tf Tc * Tf ^ k := by
                        rw [hexponent]
                  _ = Tc ^ ((n + 1) - 1 - k) * defect C Tf Tc * Tf ^ k := by
                        have hsucc : (n + 1) - 1 - k = n - k := by omega
                        rw [hsucc]
              · simp

/-- The positive-power form used in Paper II. -/
theorem power_defect_identity {R : Type u} [Ring R]
    (C Tf Tc : R) (n : ℕ) (_hn : 0 < n) :
    C * Tf ^ n - Tc ^ n * C =
      ∑ k ∈ Finset.range n,
        Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k :=
  power_defect_identity_all C Tf Tc n

/-- Submultiplicativity turns the exact telescoping formula into the usual
power-defect estimate with the norms of the actual powers.  This form needs
only a `NormedRing`; neither completeness nor normalization of `‖1‖` is
required. -/
theorem norm_power_defect_le_raw {R : Type u} [NormedRing R]
    (C Tf Tc : R) (n : ℕ) :
    ‖C * Tf ^ n - Tc ^ n * C‖ ≤
      ∑ k ∈ Finset.range n,
        ‖defect C Tf Tc‖ *
          (‖Tc ^ (n - 1 - k)‖ * ‖Tf ^ k‖) := by
  rw [power_defect_identity_all]
  calc
    ‖∑ k ∈ Finset.range n,
        Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k‖ ≤
        ∑ k ∈ Finset.range n,
          ‖Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k‖ :=
      norm_sum_le _ _
    _ ≤ ∑ k ∈ Finset.range n,
          ‖defect C Tf Tc‖ *
            (‖Tc ^ (n - 1 - k)‖ * ‖Tf ^ k‖) := by
      apply Finset.sum_le_sum
      intro k _hk
      calc
        ‖Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k‖ ≤
            ‖Tc ^ (n - 1 - k) * defect C Tf Tc‖ * ‖Tf ^ k‖ :=
          norm_mul_le _ _
        _ ≤ (‖Tc ^ (n - 1 - k)‖ * ‖defect C Tf Tc‖) * ‖Tf ^ k‖ :=
          mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _)
        _ = ‖defect C Tf Tc‖ *
            (‖Tc ^ (n - 1 - k)‖ * ‖Tf ^ k‖) := by
          ac_rfl

/-- For a normalized norm, the raw estimate becomes the power bound displayed
in Paper II.  Completeness is not required. -/
theorem norm_power_defect_le {R : Type u} [NormedRing R] [NormOneClass R]
    (C Tf Tc : R) (n : ℕ) :
    ‖C * Tf ^ n - Tc ^ n * C‖ ≤
      ‖defect C Tf Tc‖ *
        ∑ k ∈ Finset.range n, ‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k := by
  rw [power_defect_identity_all]
  calc
    ‖∑ k ∈ Finset.range n,
        Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k‖ ≤
        ∑ k ∈ Finset.range n,
          ‖Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k‖ :=
      norm_sum_le _ _
    _ ≤ ∑ k ∈ Finset.range n,
          ‖defect C Tf Tc‖ *
            (‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k) := by
      apply Finset.sum_le_sum
      intro k _hk
      calc
        ‖Tc ^ (n - 1 - k) * defect C Tf Tc * Tf ^ k‖ ≤
            ‖Tc ^ (n - 1 - k) * defect C Tf Tc‖ * ‖Tf ^ k‖ :=
          norm_mul_le _ _
        _ ≤ (‖Tc ^ (n - 1 - k)‖ * ‖defect C Tf Tc‖) * ‖Tf ^ k‖ :=
          mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _)
        _ ≤ (‖Tc‖ ^ (n - 1 - k) * ‖defect C Tf Tc‖) * ‖Tf ^ k‖ :=
          mul_le_mul_of_nonneg_right
            (mul_le_mul_of_nonneg_right (norm_pow_le _ _) (norm_nonneg _))
            (norm_nonneg _)
        _ ≤ (‖Tc‖ ^ (n - 1 - k) * ‖defect C Tf Tc‖) * ‖Tf‖ ^ k :=
          mul_le_mul_of_nonneg_left (norm_pow_le _ _)
            (mul_nonneg (pow_nonneg (norm_nonneg _) _) (norm_nonneg _))
        _ = ‖defect C Tf Tc‖ *
            (‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k) := by
          ac_rfl
    _ = ‖defect C Tf Tc‖ *
          ∑ k ∈ Finset.range n, ‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k := by
      rw [Finset.mul_sum]

/-! ## Explicit inverse witnesses -/

/-- `xinv` is an explicitly supplied two-sided inverse of `x`.

Both equations are retained because the ambient ring need not be
commutative.
-/
structure TwoSidedInverse {R : Type u} [Mul R] [One R]
    (x xinv : R) : Prop where
  left_inv : xinv * x = 1
  right_inv : x * xinv = 1

/-- The inverse-sandwich identity for two independently supplied inverse
witnesses. -/
theorem inverse_sandwich_identity {R : Type u} [Ring R]
    (A Ainv B Binv C : R)
    (hA : TwoSidedInverse A Ainv)
    (hB : TwoSidedInverse B Binv) :
    C * Binv - Ainv * C =
      Ainv * (A * C - C * B) * Binv := by
  calc
    C * Binv - Ainv * C =
        (Ainv * A) * (C * Binv) - (Ainv * C) * (B * Binv) := by
          rw [hA.left_inv, hB.right_inv]
          simp
    _ = Ainv * (A * C - C * B) * Binv := by
      noncomm_ring

/-- The resolvent-defect identity in a possibly noncommutative ring.

The hypothesis `Commute z C` expresses exactly the centrality needed of the
scalar shift.  In a commutative ring it is automatic.
-/
theorem resolvent_defect_identity {R : Type u} [Ring R]
    (z C Tf Tc Rf Rc : R)
    (hf : TwoSidedInverse (z - Tf) Rf)
    (hc : TwoSidedInverse (z - Tc) Rc)
    (hzC : Commute z C) :
    C * Rf - Rc * C = Rc * defect C Tf Tc * Rf := by
  have hmiddle : (z - Tc) * C - C * (z - Tf) = defect C Tf Tc := by
    simp only [defect, sub_mul, mul_sub]
    rw [hzC.eq]
    noncomm_ring
  calc
    C * Rf - Rc * C =
        Rc * ((z - Tc) * C - C * (z - Tf)) * Rf :=
      inverse_sandwich_identity (z - Tc) Rc (z - Tf) Rf C hc hf
    _ = Rc * defect C Tf Tc * Rf := by rw [hmiddle]

end Komorebi.PaperII.LinearDefects
