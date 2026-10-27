import Mathlib.Analysis.Normed.Algebra.MatrixExponential
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Tactic

/-! Author: Komorebi P. Entrywise positivity and column conservation for actual matrix exponentials. -/
namespace KomorebiPaperVI.MarkovSemigroup
open scoped BigOperators Matrix.Norms.Operator
open NormedSpace
set_option backward.isDefEq.respectTransparency false
variable {I : Type*} [Fintype I] [DecidableEq I]

theorem matrix_powers_nonnegative (M : Matrix I I ℝ) (hM : ∀ i j, 0 ≤ M i j)
    (n : ℕ) (i j : I) : 0 ≤ (M^n) i j := by
  induction n generalizing i j with
  | zero => simp only [pow_zero,Matrix.one_apply]; split_ifs <;> norm_num
  | succ n ih =>
    rw [pow_succ,Matrix.mul_apply]
    exact Finset.sum_nonneg (fun k _ => mul_nonneg (ih i k) (hM k j))

theorem exponential_nonnegative (M : Matrix I I ℝ) (hM : ∀ i j, 0 ≤ M i j) (i j : I) :
    0 ≤ exp M i j := by
  have hm := expSeries_summable' (𝕂 := ℝ) M
  rw [exp_eq_tsum ℝ]
  change 0 ≤ (∑' n : ℕ, ((n.factorial:ℝ)⁻¹) • M^n) i j
  rw [Pi.tsum_apply hm,Pi.tsum_apply (Pi.summable.mp hm i)]
  simp only [Matrix.smul_apply,smul_eq_mul]
  exact tsum_nonneg (fun n => mul_nonneg (by positivity) (matrix_powers_nonnegative M hM n i j))

theorem shifted_generator_nonnegative (Q : Matrix I I ℝ)
    (hQ : ∀ i j, i≠j → 0 ≤ Q i j) :
    ∀ i j, 0 ≤ (Q+(∑ k, |Q k k|) • (1 : Matrix I I ℝ)) i j := by
  intro i j
  by_cases hij : i=j
  · subst j
    have h := Finset.single_le_sum (fun k _ => abs_nonneg (Q k k)) (Finset.mem_univ i)
    simp only [Matrix.add_apply,Matrix.smul_apply,Matrix.one_apply_eq,smul_eq_mul,mul_one]
    linarith [neg_le_abs (Q i i)]
  · simpa [hij] using hQ i j hij

theorem scalar_exponential (s : ℝ) : exp (s • (1 : Matrix I I ℝ))=Real.exp s • 1 := by
  have he : s • (1 : Matrix I I ℝ)=Matrix.diagonal (fun _ => s) := by
    ext i j; by_cases hij : i=j <;> simp [hij,Matrix.diagonal]
  rw [he,Matrix.exp_diagonal]
  ext i j
  simp only [Pi.coe_exp,← Real.exp_eq_exp_ℝ,Matrix.diagonal_apply,Matrix.smul_apply,Matrix.one_apply,smul_eq_mul]
  split_ifs <;> simp

theorem markov_nonnegative (Q : Matrix I I ℝ) (hQ : ∀ i j, i≠j → 0 ≤ Q i j)
    (t : ℝ) (ht : 0 ≤ t) (i j : I) : 0 ≤ exp (t • Q) i j := by
  let a := ∑ k, |Q k k|
  let B := Q+a • (1 : Matrix I I ℝ)
  have hb : ∀ i j, 0 ≤ (t • B) i j :=
    fun i j => mul_nonneg ht (shifted_generator_nonnegative Q hQ i j)
  have he : t • Q=(-t*a) • (1 : Matrix I I ℝ)+t • B := by
    dsimp [B]
    module
  have hc : Commute ((-t*a) • (1 : Matrix I I ℝ)) (t • B) :=
    (Commute.one_left _).smul_left _
  rw [he,Matrix.exp_add_of_commute _ _ hc,scalar_exponential]
  simp only [Algebra.smul_mul_assoc,one_mul,Matrix.smul_apply,smul_eq_mul]
  exact mul_nonneg (Real.exp_pos _).le (exponential_nonnegative (t • B) hb i j)

theorem generator_power_columns (Q : Matrix I I ℝ) (hQ : ∀ j, ∑ i, Q i j=0)
    (n : ℕ) (j : I) : (∑ i, (Q^n) i j)=if n=0 then 1 else 0 := by
  cases n with
  | zero => simp [Matrix.one_apply]
  | succ n =>
    simp only [pow_succ',Matrix.mul_apply,Finset.sum_comm,← Finset.sum_mul,hQ,zero_mul,
      Finset.sum_const_zero,Nat.add_eq_zero_iff,Nat.one_ne_zero,and_false,ite_false]

theorem markov_column_sum (Q : Matrix I I ℝ) (hQ : ∀ j, ∑ i, Q i j=0)
    (t : ℝ) (j : I) : (∑ i, exp (t • Q) i j)=1 := by
  have hc : ∀ j, ∑ i, (t • Q) i j=0 := by
    intro j; simp [Matrix.smul_apply,smul_eq_mul,← Finset.mul_sum,hQ]
  have hm := expSeries_summable' (𝕂 := ℝ) (t • Q)
  rw [exp_eq_tsum ℝ]
  simp only [Pi.tsum_apply hm,Pi.tsum_apply (Pi.summable.mp hm _),Matrix.smul_apply,smul_eq_mul]
  have hs (i : I) : Summable (fun n : ℕ => ((n.factorial:ℝ)⁻¹)*((t • Q)^n) i j) := by
    exact Pi.summable.mp (Pi.summable.mp hm i) j
  rw [← Summable.tsum_finsetSum (s := Finset.univ) (fun i _ => hs i)]
  simp only [← Finset.mul_sum,generator_power_columns _ hc]
  simp

theorem markov_probability (Q : Matrix I I ℝ) (hpos : ∀ i j, i≠j → 0 ≤ Q i j)
    (hcol : ∀ j, ∑ i, Q i j=0) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i)
    (hpsum : ∑ i, p i=1) (t : ℝ) (ht : 0 ≤ t) :
    (∀ i, 0 ≤ (exp (t • Q)).mulVec p i) ∧ ∑ i, (exp (t • Q)).mulVec p i=1 := by
  constructor
  · intro i
    exact Finset.sum_nonneg (fun j _ => mul_nonneg (markov_nonnegative Q hpos t ht i j) (hp j))
  · simp only [Matrix.mulVec,dotProduct,Finset.sum_comm,← Finset.sum_mul,markov_column_sum Q hcol,
      one_mul,hpsum]

end KomorebiPaperVI.MarkovSemigroup
