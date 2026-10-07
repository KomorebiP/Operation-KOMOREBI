import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Ring

/-!
# Finite exact algebra for the Quadratic-Form Engine

These definitions use exact real arithmetic. They model a factor A with sample
coordinates i and variant coordinates k. No floating-point implementation or
probability-distribution theorem is asserted by this module.
-/

namespace KomorebiQCOS

open scoped BigOperators

variable {Row Variant : Type*} [Fintype Row] [DecidableEq Variant]

/- An entry of the sample Gram matrix A_s A_sᵀ. -/
def gramEntry (s : Finset Variant) (A : Row → Variant → ℝ) (i j : Row) : ℝ :=
  ∑ k ∈ s, A i k * A j k

/- Exact action of a finite sample-coordinate matrix on a vector. -/
def matrixAction (K : Row → Row → ℝ) (v : Row → ℝ) (i : Row) : ℝ :=
  ∑ j, K i j * v j

/- Factor action evaluated one variant coordinate at a time. -/
def streamedAction (s : Finset Variant) (A : Row → Variant → ℝ)
    (v : Row → ℝ) (i : Row) : ℝ :=
  ∑ k ∈ s, A i k * (∑ j, A j k * v j)

/- Exact real quadratic form vᵀKv. -/
def quadraticForm (K : Row → Row → ℝ) (v : Row → ℝ) : ℝ :=
  ∑ i, v i * matrixAction K v i

/- Sum of squares of factor-coordinate projections. -/
def factorEnergy (s : Finset Variant) (A : Row → Variant → ℝ)
    (v : Row → ℝ) : ℝ :=
  ∑ k ∈ s, (∑ i, A i k * v i) ^ 2

omit [Fintype Row] [DecidableEq Variant] in
@[simp] theorem gramEntry_empty (A : Row → Variant → ℝ) (i j : Row) :
    gramEntry ∅ A i j = 0 := by
  simp [gramEntry]

omit [Fintype Row] [DecidableEq Variant] in
@[simp] theorem gramEntry_singleton (k : Variant) (A : Row → Variant → ℝ)
    (i j : Row) : gramEntry {k} A i j = A i k * A j k := by
  simp [gramEntry]

omit [Fintype Row] [DecidableEq Variant] in
theorem gramEntry_symm (s : Finset Variant) (A : Row → Variant → ℝ)
    (i j : Row) : gramEntry s A i j = gramEntry s A j i := by
  simp [gramEntry, mul_comm]

/- Splitting a variant block into disjoint children preserves each Gram entry. -/
omit [Fintype Row] in
theorem gramEntry_union (s t : Finset Variant) (h : Disjoint s t)
    (A : Row → Variant → ℝ) (i j : Row) :
    gramEntry (s ∪ t) A i j = gramEntry s A i j + gramEntry t A i j := by
  simp only [gramEntry, Finset.sum_union h]

/- A bijection of variant coordinates, with factor columns moved along it,
preserves the exact sample Gram entry. -/
omit [Fintype Row] [DecidableEq Variant] in
theorem gramEntry_reindex (s : Finset Variant) (e : Variant ≃ Variant)
    (A : Row → Variant → ℝ) (i j : Row) :
    gramEntry (s.map e.toEmbedding) (fun i k => A i (e.symm k)) i j =
      gramEntry s A i j := by
  simp [gramEntry, Finset.sum_map]

/- Streamed factor multiplication agrees with multiplication by A_s A_sᵀ. -/
omit [DecidableEq Variant] in
theorem matrixAction_gram_eq_streamed (s : Finset Variant)
    (A : Row → Variant → ℝ) (v : Row → ℝ) (i : Row) :
    matrixAction (gramEntry s A) v i = streamedAction s A v i := by
  simp only [matrixAction, gramEntry, streamedAction,
    Finset.sum_mul, Finset.mul_sum, mul_assoc]
  rw [Finset.sum_comm]

theorem matrixAction_add (K L : Row → Row → ℝ) (v : Row → ℝ) (i : Row) :
    matrixAction (fun i j => K i j + L i j) v i =
      matrixAction K v i + matrixAction L v i := by
  simp [matrixAction, add_mul, Finset.sum_add_distrib]

/- Refinement also preserves every streamed sample-coordinate action. -/
theorem matrixAction_gram_union (s t : Finset Variant) (h : Disjoint s t)
    (A : Row → Variant → ℝ) (v : Row → ℝ) (i : Row) :
    matrixAction (gramEntry (s ∪ t) A) v i =
      matrixAction (gramEntry s A) v i + matrixAction (gramEntry t A) v i := by
  simp only [matrixAction, gramEntry_union s t h, add_mul,
    Finset.sum_add_distrib]

theorem streamedAction_union (s t : Finset Variant) (h : Disjoint s t)
    (A : Row → Variant → ℝ) (v : Row → ℝ) (i : Row) :
    streamedAction (s ∪ t) A v i =
      streamedAction s A v i + streamedAction t A v i := by
  simp only [streamedAction, Finset.sum_union h]

theorem quadraticForm_add (K L : Row → Row → ℝ) (v : Row → ℝ) :
    quadraticForm (fun i j => K i j + L i j) v =
      quadraticForm K v + quadraticForm L v := by
  simp [quadraticForm, matrixAction_add, mul_add, Finset.sum_add_distrib]

/- The quadratic form of a Gram matrix equals a sum of squares. -/
omit [DecidableEq Variant] in
theorem quadraticForm_gram_eq_energy (s : Finset Variant)
    (A : Row → Variant → ℝ) (v : Row → ℝ) :
    quadraticForm (gramEntry s A) v = factorEnergy s A v := by
  simp only [quadraticForm, matrixAction_gram_eq_streamed,
    streamedAction, factorEnergy, pow_two, Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro k hk
  apply Finset.sum_congr rfl
  intro i hi
  apply Finset.sum_congr rfl
  intro j hj
  ring

/- Positive semidefiniteness of the exact Gram form. -/
omit [DecidableEq Variant] in
theorem quadraticForm_gram_nonneg (s : Finset Variant)
    (A : Row → Variant → ℝ) (v : Row → ℝ) :
    0 ≤ quadraticForm (gramEntry s A) v := by
  rw [quadraticForm_gram_eq_energy]
  exact Finset.sum_nonneg (fun k hk => sq_nonneg (∑ i, A i k * v i))

/- Splitting a block preserves the exact quadratic statistic as well. -/
theorem quadraticForm_gram_union (s t : Finset Variant) (h : Disjoint s t)
    (A : Row → Variant → ℝ) (v : Row → ℝ) :
    quadraticForm (gramEntry (s ∪ t) A) v =
      quadraticForm (gramEntry s A) v + quadraticForm (gramEntry t A) v := by
  simp only [quadraticForm, matrixAction_gram_union s t h, mul_add,
    Finset.sum_add_distrib]

/- A supplied diagonal spectral form. No diagonalization theorem is assumed. -/
def weightedSquares (s : Finset Variant) (coeff z : Variant → ℝ) : ℝ :=
  ∑ k ∈ s, coeff k * z k ^ 2

/- Coefficient intervals give pointwise order for supplied diagonal forms.
This statement even permits signed coefficients; the squared coordinates are
nonnegative. -/
omit [Fintype Row] [DecidableEq Variant] in
theorem weightedSquares_mono (s : Finset Variant)
    (lower upper z : Variant → ℝ) (h : ∀ k ∈ s, lower k ≤ upper k) :
    weightedSquares s lower z ≤ weightedSquares s upper z := by
  apply Finset.sum_le_sum
  intro k hk
  exact mul_le_mul_of_nonneg_right (h k hk) (sq_nonneg (z k))

omit [Fintype Row] [DecidableEq Variant] in
theorem weightedSquares_nonneg (s : Finset Variant)
    (coeff z : Variant → ℝ) (h : ∀ k ∈ s, 0 ≤ coeff k) :
    0 ≤ weightedSquares s coeff z := by
  exact Finset.sum_nonneg (fun k hk => mul_nonneg (h k hk) (sq_nonneg (z k)))

/- A pointwise tail-event implication. Passing to probabilities requires a
separate measure-theoretic monotonicity argument. -/
omit [Fintype Row] [DecidableEq Variant] in
theorem weightedSquares_tail_imp (s : Finset Variant)
    (lower upper z : Variant → ℝ) (q : ℝ)
    (h : ∀ k ∈ s, lower k ≤ upper k)
    (htail : q ≤ weightedSquares s lower z) :
    q ≤ weightedSquares s upper z := by
  exact htail.trans (weightedSquares_mono s lower upper z h)

end KomorebiQCOS
