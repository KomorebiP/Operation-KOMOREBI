import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Tactic.Ring
import Lean.Elab.Tactic.Omega
import Mathlib.Algebra.CharP.Basic

/-!
# Finite negative-binomial reciprocal over a commutative ring

The proof is finite algebra. No convergence, analytic inverse, or field hypothesis
is used. The q=0 coefficients are handled separately by natural binomial conventions.
-/
namespace KomorebiPadic
open Finset

/-- Signed coefficients of (1+x)^(-q). -/
def negativeBinomialCoeff (q k : ℕ) : ℤ :=
  (-1) ^ k * ((q + k - 1).choose k : ℤ)

@[simp] theorem negativeBinomialCoeff_zero_order (q : ℕ) :
    negativeBinomialCoeff q 0 = 1 := by simp [negativeBinomialCoeff]

/-- Pascal's relation, with signs, is the exact finite telescoping rule. -/
theorem negativeBinomialCoeff_pascal (q k : ℕ) :
    negativeBinomialCoeff (q + 1) (k + 1) + negativeBinomialCoeff (q + 1) k =
      negativeBinomialCoeff q (k + 1) := by
  have h1 : q + 1 + (k + 1) - 1 = q + k + 1 := by omega
  have h2 : q + 1 + k - 1 = q + k := by omega
  have h3 : q + (k + 1) - 1 = q + k := by omega
  simp only [negativeBinomialCoeff, h1, h2, h3, Nat.choose_succ_succ,
    Nat.cast_add, pow_succ]
  ring

/-- For q=0 the finite reciprocal is the constant series 1. -/
theorem negativeBinomialCoeff_zero_quotient (k : ℕ) :
    negativeBinomialCoeff 0 k = if k = 0 then 1 else 0 := by
  by_cases hk : k = 0
  · simp [hk]
  · have hlt : k - 1 < k := Nat.sub_lt (Nat.pos_of_ne_zero hk) (by decide)
    simp [negativeBinomialCoeff, hk, Nat.choose_eq_zero_of_lt hlt]

variable {R : Type*} [CommRing R]

/-- Finite truncation of the negative-binomial reciprocal. -/
def finiteNegativeBinomial (q r : ℕ) (x : R) : R :=
  ∑ k ∈ range r, (negativeBinomialCoeff q k : R) * x ^ k

theorem finiteNegativeBinomial_succ (q r : ℕ) (x : R) :
    finiteNegativeBinomial q (r + 1) x =
      finiteNegativeBinomial q r x + (negativeBinomialCoeff q r : R) * x ^ r := by
  exact sum_range_succ _ _

/-- Exact finite remainder before imposing nilpotence. -/
theorem finiteNegativeBinomial_remainder (q n : ℕ) (x : R) :
    (1 + x) * finiteNegativeBinomial (q + 1) (n + 1) x =
      finiteNegativeBinomial q (n + 1) x +
        (negativeBinomialCoeff (q + 1) n : R) * x ^ (n + 1) := by
  induction n with
  | zero => simp [finiteNegativeBinomial]
  | succ n ih =>
    rw [finiteNegativeBinomial_succ (q + 1) (n + 1), mul_add, ih,
      finiteNegativeBinomial_succ q (n + 1)]
    have hc : (negativeBinomialCoeff (q + 1) (n + 1) : R) +
        (negativeBinomialCoeff (q + 1) n : R) =
        (negativeBinomialCoeff q (n + 1) : R) := by
      simpa only [Int.cast_add] using
        congrArg (fun a : ℤ => (a : R)) (negativeBinomialCoeff_pascal q n)
    rw [← hc, pow_succ x (n + 1)]
    ring

/-- Nilpotence kills the remainder exactly. -/
theorem finiteNegativeBinomial_step (q r : ℕ) (x : R) (hr : 0 < r) (hx : x ^ r = 0) :
    (1 + x) * finiteNegativeBinomial (q + 1) r x = finiteNegativeBinomial q r x := by
  obtain ⟨n, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hr.ne'
  simpa [hx] using finiteNegativeBinomial_remainder q n x

@[simp] theorem finiteNegativeBinomial_zero_quotient (r : ℕ) (x : R) (hr : 0 < r) :
    finiteNegativeBinomial 0 r x = 1 := by
  simp [finiteNegativeBinomial, negativeBinomialCoeff_zero_quotient, hr.ne']

/-- The finite negative-binomial sum is a two-sided reciprocal of (1+x)^q. -/
theorem finiteNegativeBinomial_inverse (q r : ℕ) (x : R) (hr : 0 < r) (hx : x ^ r = 0) :
    (1 + x) ^ q * finiteNegativeBinomial q r x = 1 := by
  induction q with
  | zero => simp [hr]
  | succ q ih =>
    rw [pow_succ, mul_assoc, finiteNegativeBinomial_step q r x hr hx]
    exact ih

/-- The denominator-normalized finite correction expansion. -/
def finiteCorrectionInverse (q r : ℕ) (u : Rˣ) (D : R) : R :=
  ∑ k ∈ range r, (negativeBinomialCoeff q k : R) * D ^ k * (↑(u⁻¹) : R) ^ (q + k)

/-- Distribute the unit denominator to recover the explicit correction summands. -/
theorem finiteCorrectionInverse_factor (q r : ℕ) (u : Rˣ) (D : R) :
    finiteCorrectionInverse q r u D =
      (↑(u⁻¹) : R) ^ q * finiteNegativeBinomial q r (D * ↑(u⁻¹)) := by
  simp only [finiteCorrectionInverse, finiteNegativeBinomial, mul_sum]
  apply sum_congr rfl
  intro k _
  rw [mul_pow, pow_add]
  ring

/-- Exact reciprocal expansion for a unit denominator perturbed by a nilpotent. -/
theorem finiteCorrectionInverse_spec (q r : ℕ) (u : Rˣ) (D : R)
    (hr : 0 < r) (hD : D ^ r = 0) :
    (↑u + D) ^ q * finiteCorrectionInverse q r u D = 1 := by
  have hx : (D * (↑(u⁻¹) : R)) ^ r = 0 := by rw [mul_pow, hD, zero_mul]
  have hfac : (↑u : R) + D = ↑u * (1 + D * ↑(u⁻¹)) := by
    calc
      (↑u : R) + D = ↑u + D * (↑u * ↑(u⁻¹)) := by simp
      _ = ↑u * (1 + D * ↑(u⁻¹)) := by ring
  rw [hfac, mul_pow, finiteCorrectionInverse_factor]
  calc
    (↑u : R) ^ q * (1 + D * ↑(u⁻¹)) ^ q *
        ((↑(u⁻¹) : R) ^ q * finiteNegativeBinomial q r (D * ↑(u⁻¹))) =
      ((↑u : R) * ↑(u⁻¹)) ^ q *
        ((1 + D * ↑(u⁻¹)) ^ q * finiteNegativeBinomial q r (D * ↑(u⁻¹))) := by
          rw [mul_pow]; ring
    _ = 1 := by rw [finiteNegativeBinomial_inverse q r _ hr hx]; simp

/-- In characteristic p^r every p-multiple has r-th power zero. -/
theorem primePower_multiple_nilpotent (p r : ℕ) [CharP R (p ^ r)] (E : R) :
    ((p : R) * E) ^ r = 0 := by
  rw [mul_pow, ← Nat.cast_pow, CharP.cast_eq_zero R (p ^ r), zero_mul]

/-- Specialization to characteristic p^r. Primality is not needed for this algebraic step. -/
theorem primePower_finiteCorrectionInverse (p q r : ℕ) [CharP R (p ^ r)]
    (u : Rˣ) (E : R) (hr : 0 < r) :
    (↑u + (p : R) * E) ^ q * finiteCorrectionInverse q r u ((p : R) * E) = 1 := by
  exact finiteCorrectionInverse_spec q r u _ hr (primePower_multiple_nilpotent p r E)

end KomorebiPadic
