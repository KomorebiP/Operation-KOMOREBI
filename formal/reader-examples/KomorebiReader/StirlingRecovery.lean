import Mathlib.Algebra.Polynomial.OfFn
import Mathlib.Algebra.Polynomial.Roots
import Mathlib.Combinatorics.Enumerative.Stirling
import Mathlib.RingTheory.Polynomial.Pochhammer
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# Full polynomial recovery and the two-summary obstruction

Formal companion to Section 7 of
`docs/demonstrations/STIRLING_BELL_FUBINI.md`. A profile has `n + 1`
rational coordinates, indexed from zero. Its factorial-weighted representation
is an actual polynomial over the rationals. Coefficient division recovers every
coordinate, and evaluation at `n + 1` distinct rational points determines the
profile uniquely. The latter is a uniqueness theorem, not an implementation of
the displayed Newton interpolation formula.

The explicit profiles `(0,1,7,6,1)` and `(0,5,2,7,1)` prove that the two
fixed scalar summaries are not injective, despite injectivity of the full
polynomial representation. The second profile is not another Stirling row.

The final polynomial identity lifts Mathlib's classical natural-number theorem
`Nat.pow_eq_sum_stirlingSecond_mul_descFactorial` to an identity in `ℚ[X]`.
It supplies the classical falling-factorial expansion in Section 3 of that
demonstration and Sections 1 and 3 of
`docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md`. No novelty, exponential
generating-function identity, moment integral, signed Stirling inversion, or
roots-of-unity identity is asserted by this module.
-/

set_option autoImplicit false

open scoped BigOperators
open Polynomial

namespace Komorebi.Reader.StirlingRecovery

/-- Preserve all factorial-weighted coordinates as polynomial coefficients. -/
noncomputable def weightedPolynomial {n : ℕ} (x : Fin (n + 1) → ℚ) : ℚ[X] :=
  ∑ k : Fin (n + 1), monomial k.val ((Nat.factorial k.val : ℚ) * x k)

/-- The retained coefficient is exactly the original coordinate times `k!`. -/
theorem weightedPolynomial_coeff {n : ℕ} (x : Fin (n + 1) → ℚ)
    (k : Fin (n + 1)) :
    (weightedPolynomial x).coeff k.val = (Nat.factorial k.val : ℚ) * x k := by
  simp [weightedPolynomial, Polynomial.finsetSum_coeff, Polynomial.coeff_monomial,
    Fin.val_inj]

/-- Factorials are nonzero in `ℚ`, so coefficient division recovers the input. -/
theorem recover_coordinate {n : ℕ} (x : Fin (n + 1) → ℚ)
    (k : Fin (n + 1)) :
    (weightedPolynomial x).coeff k.val / (Nat.factorial k.val : ℚ) = x k := by
  rw [weightedPolynomial_coeff]
  exact mul_div_cancel_left₀ _ (Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero k.val))

/-- Retaining the complete weighted polynomial loses no rational coordinate. -/
theorem weightedPolynomial_injective (n : ℕ) :
    Function.Injective (weightedPolynomial (n := n)) := by
  intro x y h
  funext k
  calc
    x k = (weightedPolynomial x).coeff k.val / (Nat.factorial k.val : ℚ) :=
      (recover_coordinate x k).symm
    _ = (weightedPolynomial y).coeff k.val / (Nat.factorial k.val : ℚ) := by rw [h]
    _ = y k := recover_coordinate y k

/-- The profile polynomial has degree at most `n`, including the zero profile. -/
theorem weightedPolynomial_natDegree_lt {n : ℕ} (x : Fin (n + 1) → ℚ) :
    (weightedPolynomial x).natDegree < n + 1 := by
  simpa [weightedPolynomial, Polynomial.ofFn_eq_sum_monomial] using
    (Polynomial.ofFn_natDegree_lt (Nat.succ_le_succ (Nat.zero_le n))
      (fun k : Fin (n + 1) => (Nat.factorial k.val : ℚ) * x k))

/-- Exactly `n + 1` distinct rational sample addresses suffice for uniqueness.
Distinctness and the fixed finite profile size are explicit hypotheses. -/
theorem finite_samples_determine_profile {n : ℕ}
    (addresses : Fin (n + 1) → ℚ) (distinct : Function.Injective addresses)
    (x y : Fin (n + 1) → ℚ)
    (samples : ∀ j, (weightedPolynomial x).eval (addresses j) =
      (weightedPolynomial y).eval (addresses j)) : x = y := by
  apply weightedPolynomial_injective n
  apply Polynomial.eq_of_natDegree_lt_card_of_eval_eq
    (weightedPolynomial x) (weightedPolynomial y) distinct samples
  simpa only [Fintype.card_fin] using
    max_lt_iff.mpr ⟨weightedPolynomial_natDegree_lt x, weightedPolynomial_natDegree_lt y⟩

/-- Evaluation of the actual polynomial agrees with the finite weighted sum. -/
theorem weightedPolynomial_eval {n : ℕ} (x : Fin (n + 1) → ℚ) (a : ℚ) :
    (weightedPolynomial x).eval a =
      ∑ k : Fin (n + 1), (Nat.factorial k.val : ℚ) * x k * a ^ k.val := by
  simp only [weightedPolynomial, Polynomial.eval_finsetSum, Polynomial.eval_monomial]

/-- The two scalar measurements from Section 7 of the reading edition. -/
def summaries {n : ℕ} (x : Fin (n + 1) → ℚ) : ℚ × ℚ :=
  (∑ k : Fin (n + 1), x k, ∑ k : Fin (n + 1), (Nat.factorial k.val : ℚ) * x k)

/-- The genuine row of Stirling numbers of the second kind at index four. -/
def genuineProfile : Fin 5 → ℚ := ![0, 1, 7, 6, 1]

/-- A different nonnegative integral profile, not a second Stirling row. -/
def candidateProfile : Fin 5 → ℚ := ![0, 5, 2, 7, 1]

/-- Exact correspondence of the displayed genuine profile with Mathlib's
recursively defined Stirling numbers. This is a finite data check. -/
theorem genuineProfile_stirling :
    genuineProfile = fun k : Fin 5 => (Nat.stirlingSecond 4 k.val : ℚ) := by
  funext k
  fin_cases k <;> norm_num [genuineProfile, Nat.stirlingSecond]

/-- The reading edition's explicit nonnegative witness, with both exact outputs.
These finite facts are separate from the universal recovery theorems. -/
theorem summary_obstruction :
    genuineProfile ≠ candidateProfile ∧
    summaries genuineProfile = (15, 75) ∧
    summaries candidateProfile = (15, 75) ∧
    (∀ k, 0 ≤ genuineProfile k ∧ 0 ≤ candidateProfile k) := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro h
    have h1 := congrFun h (1 : Fin 5)
    norm_num [genuineProfile, candidateProfile] at h1
  · norm_num [summaries, genuineProfile, Fin.sum_univ_succ, Nat.factorial]
  · norm_num [summaries, candidateProfile, Fin.sum_univ_succ, Nat.factorial]
  · intro k
    fin_cases k <;> norm_num [genuineProfile, candidateProfile]

/-- The two summaries fail to recover arbitrary five-coordinate rational data. -/
theorem summaries_not_injective : ¬ Function.Injective (summaries (n := 4)) := by
  intro injective
  exact summary_obstruction.1
    (injective (summary_obstruction.2.1.trans summary_obstruction.2.2.1.symm))

/-- An additional address separates these particular profiles. This finite
example does not claim that one additional sample always recovers a profile. -/
theorem obstruction_polynomials_at_two :
    (weightedPolynomial genuineProfile).eval 2 = 730 ∧
    (weightedPolynomial candidateProfile).eval 2 = 746 := by
  constructor <;> rw [weightedPolynomial_eval] <;>
    norm_num [genuineProfile, candidateProfile, Fin.sum_univ_succ, Nat.factorial]

/-- The classical Stirling expansion as an actual identity of rational
polynomials. Its natural-number evaluations use the existing Mathlib theorem
`Nat.pow_eq_sum_stirlingSecond_mul_descFactorial`; polynomial equality follows
because those evaluation addresses form an infinite set. -/
theorem classical_power_stirling_expansion (n : ℕ) :
    (X : ℚ[X]) ^ n = ∑ k ∈ Finset.range (n + 1),
      C (Nat.stirlingSecond n k : ℚ) * descPochhammer ℚ k := by
  apply Polynomial.eq_of_infinite_eval_eq
  apply (Set.infinite_range_of_injective
    (Nat.cast_injective : Function.Injective (fun m : ℕ => (m : ℚ)))).mono
  rintro a ⟨m, rfl⟩
  simpa only [Set.mem_ofPred_eq, Polynomial.eval_pow, Polynomial.eval_X, Polynomial.eval_finsetSum,
    Polynomial.eval_mul, Polynomial.eval_C, descPochhammer_eval_eq_descFactorial,
    Nat.cast_sum, Nat.cast_mul, Nat.cast_pow] using
    congrArg (fun v : ℕ => (v : ℚ)) (Nat.pow_eq_sum_stirlingSecond_mul_descFactorial m n)

end Komorebi.Reader.StirlingRecovery
