import Mathlib.Algebra.Polynomial.Basis
import Mathlib.Algebra.Polynomial.Sequence
import Mathlib.Combinatorics.Enumerative.Stirling
import Mathlib.RingTheory.Polynomial.Pochhammer
import Mathlib.Algebra.Polynomial.Roots

/-!
# The falling-factorial change of basis on rational polynomials

The forward linear equivalence sends `X ^ n` to the descending Pochhammer
polynomial. Both sides are ordinary polynomials with finite support.
The inverse monomial formula is the classical second-Stirling expansion,
transported from Mathlib's natural-number falling-factorial identity.
-/

set_option autoImplicit false

open Polynomial
open scoped BigOperators

namespace Komorebi.Polynomial.FallingFactorial

/-- The descending Pochhammer polynomials form a polynomial sequence. -/
noncomputable def fallingSequence : Polynomial.Sequence ℚ where
  elems' := descPochhammer ℚ
  degree_eq' n := by
    rw [degree_eq_natDegree (monic_descPochhammer ℚ n).ne_zero,
      descPochhammer_natDegree]

/-- Every element of the falling sequence has unit leading coefficient. -/
theorem fallingSequence_leadingCoeff (n : ℕ) :
    IsUnit (fallingSequence n).leadingCoeff := by
  change IsUnit (descPochhammer ℚ n).leadingCoeff
  rw [(monic_descPochhammer ℚ n).leadingCoeff]
  exact isUnit_one

/-- The actual falling-factorial basis of `ℚ[X]`. -/
noncomputable def fallingBasis : Module.Basis ℕ ℚ ℚ[X] :=
  fallingSequence.basis fallingSequence_leadingCoeff

@[simp] theorem fallingBasis_apply (n : ℕ) :
    fallingBasis n = descPochhammer ℚ n := by
  simp [fallingBasis, fallingSequence]

/-- The document's map `Φ`, oriented from powers to falling factorials. -/
noncomputable def fallingEquiv : ℚ[X] ≃ₗ[ℚ] ℚ[X] :=
  (basisMonomials ℚ).equiv fallingBasis (Equiv.refl ℕ)

@[simp] theorem fallingEquiv_X_pow (n : ℕ) :
    fallingEquiv ((X : ℚ[X]) ^ n) = descPochhammer ℚ n := by
  simpa only [fallingEquiv, coe_basisMonomials, monomial_one_right_eq_X_pow,
    Equiv.refl_apply, fallingBasis_apply] using
    (Module.Basis.equiv_apply (basisMonomials ℚ) n fallingBasis (Equiv.refl ℕ))

@[simp] theorem fallingEquiv_symm_descPochhammer (n : ℕ) :
    fallingEquiv.symm (descPochhammer ℚ n) = (X : ℚ[X]) ^ n := by
  rw [← fallingEquiv_X_pow, LinearEquiv.symm_apply_apply]

/-- Arbitrary monomials are transported with their rational coefficient. -/
theorem fallingEquiv_monomial (n : ℕ) (a : ℚ) :
    fallingEquiv (monomial n a) = a • descPochhammer ℚ n := by
  rw [← C_mul_X_pow_eq_monomial, ← smul_eq_C_mul,
    map_smul, fallingEquiv_X_pow]

/-- The map is the finite coefficient sum specified by `Φ`. -/
theorem fallingEquiv_eq_sum (p : ℚ[X]) :
    fallingEquiv p = ∑ n ∈ p.support, p.coeff n • descPochhammer ℚ n := by
  conv_lhs => rw [← sum_monomial_eq p]
  simp only [sum_def, map_sum, fallingEquiv_monomial]

/-- All constant polynomials, including zero, are fixed. -/
@[simp] theorem fallingEquiv_C (a : ℚ) : fallingEquiv (C a) = C a := by
  simpa only [monomial_zero_left, descPochhammer_zero, smul_eq_C_mul, mul_one]
    using fallingEquiv_monomial 0 a

/-- No leading term is lost in this monic triangular change of basis. -/
theorem fallingEquiv_natDegree (p : ℚ[X]) :
    (fallingEquiv p).natDegree = p.natDegree := by
  have hterm (n : ℕ) (hn : n ∈ p.support) :
      (p.coeff n • descPochhammer ℚ n).natDegree = n := by
    rw [natDegree_smul _ (mem_support_iff.mp hn), descPochhammer_natDegree]
  rw [fallingEquiv_eq_sum, natDegree_sum_eq_of_disjoint]
  · calc
      p.support.sup (fun n => (p.coeff n • descPochhammer ℚ n).natDegree) =
          p.support.sup id := Finset.sup_congr rfl hterm
      _ = p.natDegree := by
        apply le_antisymm
        · exact Finset.sup_le (fun n hn => le_natDegree_of_mem_supp n hn)
        · by_cases hp : p = 0
          · simp [hp]
          · exact Finset.le_sup (f := id) (natDegree_mem_support_of_nonzero hp)
  · intro i hi j hj hij
    simpa only [Function.onFun, Function.comp_apply, hterm i hi.1, hterm j hj.1] using hij

/-- Degree preservation also distinguishes the zero polynomial's degree `⊥`. -/
theorem fallingEquiv_degree (p : ℚ[X]) :
    (fallingEquiv p).degree = p.degree := by
  by_cases hp : p = 0
  · simp [hp]
  · have hφ : fallingEquiv p ≠ 0 := by
      intro h
      apply hp
      apply fallingEquiv.injective
      simpa using h
    rw [degree_eq_natDegree hφ, degree_eq_natDegree hp, fallingEquiv_natDegree]

/-- Mathlib's classical second-Stirling identity, lifted from its values on
natural numbers to an equality of rational polynomials. -/
theorem power_eq_stirling_sum (n : ℕ) :
    (X : ℚ[X]) ^ n = ∑ k ∈ Finset.range (n + 1),
      C (Nat.stirlingSecond n k : ℚ) * descPochhammer ℚ k := by
  apply Polynomial.eq_of_infinite_eval_eq
  apply (Set.infinite_range_of_injective
    (Nat.cast_injective : Function.Injective (fun m : ℕ => (m : ℚ)))).mono
  rintro a ⟨m, rfl⟩
  simpa only [Set.mem_ofPred_eq, Polynomial.eval_pow, Polynomial.eval_X,
    Polynomial.eval_finsetSum, Polynomial.eval_mul, Polynomial.eval_C,
    descPochhammer_eval_eq_descFactorial, Nat.cast_sum, Nat.cast_mul,
    Nat.cast_pow] using
    congrArg (fun v : ℕ => (v : ℚ))
      (Nat.pow_eq_sum_stirlingSecond_mul_descFactorial m n)

/-- The inverse of `Φ` on powers is the second-Stirling polynomial. -/
theorem fallingEquiv_symm_X_pow (n : ℕ) :
    fallingEquiv.symm ((X : ℚ[X]) ^ n) =
      ∑ k ∈ Finset.range (n + 1), C (Nat.stirlingSecond n k : ℚ) * X ^ k := by
  conv_lhs => rw [power_eq_stirling_sum n]
  simp only [map_sum, ← smul_eq_C_mul, map_smul,
    fallingEquiv_symm_descPochhammer]

/-- `Φ` is linear but does not preserve multiplication, already on `X * X`. -/
theorem fallingEquiv_not_multiplicative :
    fallingEquiv ((X : ℚ[X]) * X) ≠ fallingEquiv X * fallingEquiv X := by
  intro h
  have hX : fallingEquiv (X : ℚ[X]) = X := by
    simpa using fallingEquiv_X_pow 1
  rw [← pow_two, fallingEquiv_X_pow, hX,
    descPochhammer_succ_right ℚ 1, descPochhammer_one] at h
  have heval := congrArg (fun p : ℚ[X] => p.eval 1) h
  norm_num at heval

end Komorebi.Polynomial.FallingFactorial
