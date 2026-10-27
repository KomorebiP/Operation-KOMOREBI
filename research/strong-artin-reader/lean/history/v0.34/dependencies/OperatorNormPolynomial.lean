import Mathlib.Algebra.Polynomial.AlgebraMap
import Mathlib.Algebra.Polynomial.Div
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.Algebra.Ring.GeomSum
import Mathlib.LinearAlgebra.Dual.Lemmas

/-! Exact geometric norm identities for arbitrary endomorphisms. -/
noncomputable section
namespace Komorebi.StrongArtin.NonsemisimpleNorm
open Polynomial
open scoped BigOperators
variable {k V : Type*} [Field k] [AddCommGroup V] [Module k V]

def normPolynomial (k : Type*) [Semiring k] (d : ℕ) : k[X] :=
  ∑ j ∈ Finset.range d, X ^ j

def operatorNorm (T : Module.End k V) (d : ℕ) : Module.End k V :=
  ∑ j ∈ Finset.range d, T ^ j

@[simp] theorem normPolynomial_mul_X_sub_one (d : ℕ) :
    normPolynomial k d * (X - 1) = X ^ d - 1 := by
  exact geom_sum_mul (X : k[X]) d

@[simp] theorem aeval_normPolynomial (T : Module.End k V) (d : ℕ) :
    aeval T (normPolynomial k d) = operatorNorm T d := by
  simp [normPolynomial, operatorNorm]

@[simp] theorem operatorNorm_zero (T : Module.End k V) : operatorNorm T 0 = 0 := by
  simp [operatorNorm]

@[simp] theorem operatorNorm_succ (T : Module.End k V) (d : ℕ) :
    operatorNorm T (d+1) = operatorNorm T d + T^d := by
  simp [operatorNorm, Finset.sum_range_succ]

/-- Cancel in k[X], not in the endomorphism ring. -/
theorem normPolynomial_primePower (p a : ℕ) [Fact (Nat.Prime p)] [CharP k p] :
    normPolynomial k (p^a) = (X - 1)^(p^a - 1) := by
  have hp : 0 < p^a := pow_pos (Fact.out : Nat.Prime p).pos a
  apply mul_right_cancel₀ (by simpa using (X_sub_C_ne_zero (1 : k)))
  rw [normPolynomial_mul_X_sub_one, ← pow_succ, Nat.sub_add_cancel hp]
  rw [sub_pow_char_pow]
  simp

/-- No diagonalization, finite-dimensionality or nilpotence assumption. -/
theorem operatorNorm_primePower (T : Module.End k V)
    (p a : ℕ) [Fact (Nat.Prime p)] [CharP k p] :
    operatorNorm T (p^a) = (T - 1)^(p^a - 1) := by
  have h := congrArg (aeval T) (normPolynomial_primePower (k := k) p a)
  simpa using h

theorem operatorNorm_prime (T : Module.End k V)
    (p : ℕ) [Fact (Nat.Prime p)] [CharP k p] :
    operatorNorm T p = (T - 1)^(p - 1) := by
  simpa using operatorNorm_primePower T p 1

/-- Isolate the p-power part of an arbitrary degree. -/
theorem normPolynomial_mixed_degree (m p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] :
    normPolynomial k (m * p^a) =
      (X - 1)^(p^a - 1) * (normPolynomial k m)^(p^a) := by
  have hp : 0 < p^a := pow_pos (Fact.out : Nat.Prime p).pos a
  apply mul_right_cancel₀ (by simpa using (X_sub_C_ne_zero (1 : k)))
  rw [normPolynomial_mul_X_sub_one]
  calc
    (X : k[X])^(m * p^a) - 1 = (X^m - 1)^(p^a) := by
      rw [sub_pow_char_pow, ← pow_mul, one_pow]
    _ = (normPolynomial k m * (X - 1))^(p^a) := by rw [normPolynomial_mul_X_sub_one]
    _ = (X - 1)^(p^a - 1) * normPolynomial k m ^ (p^a) * (X - 1) := by
      have he : (X - 1 : k[X])^(p^a) = (X - 1)^(p^a - 1) * (X - 1) := by
        rw [← pow_succ, Nat.sub_add_cancel hp]
      rw [mul_pow, he]
      ring

theorem operatorNorm_mixed_degree (T : Module.End k V) (m p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] :
    operatorNorm T (m * p^a) =
      (T - 1)^(p^a-1) * (operatorNorm T m)^(p^a) := by
  have h := congrArg (aeval T) (normPolynomial_mixed_degree (k := k) m p a)
  simpa using h

end Komorebi.StrongArtin.NonsemisimpleNorm
