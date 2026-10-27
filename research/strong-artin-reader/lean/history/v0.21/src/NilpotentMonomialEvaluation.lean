import ScalarPowerDivisibility
import Mathlib.Data.Finsupp.Weight

/-!
# Monomial evaluation in a principal nilpotent ideal

If every coordinate is divisible by `pi`, a monomial of total degree `d`
is divisible by `pi^d`.  Hence all monomials of total degree at least the
nilpotence exponent vanish.
-/

namespace Komorebi.StrongArtin.NilpotentMonomialEvaluation

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.ScalarPowerDivisibility

variable {R ι α : Type*} [CommRing R]

/-- A depth-one divisible scalar has its `n`th power at depth `n`. -/
theorem powDivisible_pow_of_depth_one {pi x : R}
    (hx : PowDivisible pi 1 x) (n : ℕ) :
    PowDivisible pi n (x ^ n) := by
  obtain ⟨a, ha⟩ := hx
  have hx' : pi * a = x := by simpa [pow_one, smul_eq_mul] using ha
  refine ⟨a ^ n, ?_⟩
  simp only [smul_eq_mul]
  rw [← mul_pow, hx']

/-- Finite products add the filtration depths of their factors. -/
theorem powDivisible_finset_prod (pi : R) (s : Finset α)
    (depth : α → ℕ) (f : α → R)
    (hf : ∀ a ∈ s, PowDivisible pi (depth a) (f a)) :
    PowDivisible pi (∑ a ∈ s, depth a) (∏ a ∈ s, f a) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert a s ha ih =>
      rw [Finset.sum_insert ha, Finset.prod_insert ha]
      exact powDivisible_mul (hf a (by simp))
        (ih (fun b hb => hf b (by simp [hb])))

/-- The value of a monomial at depth-one coordinates has filtration depth
its total degree. -/
theorem monomialValue_powDivisible_degree (pi : R) (x : ι → R)
    (hx : ∀ i, PowDivisible pi 1 (x i)) (d : ι →₀ ℕ) :
    PowDivisible pi d.degree (d.prod fun i n => x i ^ n) := by
  classical
  simpa [Finsupp.prod, Finsupp.degree_apply] using
    powDivisible_finset_prod pi d.support (fun i => d i)
      (fun i => x i ^ d i)
      (fun i hi => powDivisible_pow_of_depth_one (hx i) (d i))

/-- Monomials at or above the nilpotence exponent vanish. -/
theorem monomialValue_eq_zero_of_nilpotent_depth
    (pi : R) (N : ℕ) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i))
    (d : ι →₀ ℕ) (hd : N ≤ d.degree) :
    d.prod (fun i n => x i ^ n) = 0 := by
  apply eq_zero_of_pow_eq_zero
    ((monomialValue_powDivisible_degree pi x hx d).mono hd)
    hpi

/-- A coefficient times a high-degree monomial also vanishes. -/
theorem coeff_mul_monomialValue_eq_zero_of_nilpotent_depth
    (pi : R) (N : ℕ) (hpi : pi ^ N = 0)
    (x : ι → R) (hx : ∀ i, PowDivisible pi 1 (x i))
    (c : R) (d : ι →₀ ℕ) (hd : N ≤ d.degree) :
    c * d.prod (fun i n => x i ^ n) = 0 := by
  rw [monomialValue_eq_zero_of_nilpotent_depth pi N hpi x hx d hd, mul_zero]

end Komorebi.StrongArtin.NilpotentMonomialEvaluation

#print axioms Komorebi.StrongArtin.NilpotentMonomialEvaluation.monomialValue_powDivisible_degree
#print axioms Komorebi.StrongArtin.NilpotentMonomialEvaluation.monomialValue_eq_zero_of_nilpotent_depth
