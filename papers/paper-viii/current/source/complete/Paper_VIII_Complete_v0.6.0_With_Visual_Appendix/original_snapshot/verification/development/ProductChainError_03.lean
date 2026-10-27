module
public import PacketPerturbation
import all PacketPerturbation
public import Mathlib.Analysis.Normed.Ring.Basic
public import Mathlib.Algebra.BigOperators.Intervals
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 5.8, 5.9 and 8.3. Actual noncommutative products and actual
recompressed iterates, with closed finite-sum error certificates.
Indices are zero based: factor j in Lean is manuscript factor j+1.
No commutativity of operators or implementation rounding model is assumed.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators

/-- The left-accumulated product A(n-1) ... A(0). -/
def chainProduct {R : Type*} [Monoid R] (A : ℕ → R) : ℕ → R
  | 0 => 1
  | n + 1 => A n * chainProduct A n

/-- An actual iteration that introduces additive error after each product. -/
def recompressedProduct {R : Type*} [Ring R] (A E : ℕ → R) : ℕ → R
  | 0 => 1
  | n + 1 => A n * recompressedProduct A E n + E n

/-- Scalar propagation, independent of the operator iterates. -/
def propagatedError (a e : ℕ → ℝ) : ℕ → ℝ
  | 0 => 0
  | n + 1 => a n * propagatedError a e n + e n

/-- Closed form, with empty suffix products equal to one. -/
theorem propagatedError_eq_sum (a e : ℕ → ℝ) (n : ℕ) :
    propagatedError a e n =
      ∑ j ∈ Finset.range n, (∏ i ∈ Finset.Ico (j + 1) n, a i) * e j := by
  induction n with
  | zero => simp [propagatedError]
  | succ n ih =>
    rw [propagatedError, ih, Finset.sum_range_succ, Finset.mul_sum]
    congr 1
    · apply Finset.sum_congr rfl
      intro j hj
      have hjn : j + 1 ≤ n := Finset.mem_range.mp hj
      rw [Finset.prod_Ico_succ_top hjn]
      ring
    · simp

/-- Monotonicity in certified local error budgets. -/
theorem propagatedError_mono (a e d : ℕ → ℝ) (ha : ∀ n, 0 ≤ a n)
    (hed : ∀ n, e n ≤ d n) (n : ℕ) :
    propagatedError a e n ≤ propagatedError a d n := by
  induction n with
  | zero => exact le_rfl
  | succ n ih =>
    exact add_le_add (mul_le_mul_of_nonneg_left ih (ha n)) (hed n)

/-- A nonnegative gain recurrence dominates actual norm errors. -/
theorem norm_recurrence_bound {R : Type*} [SeminormedAddCommGroup R]
    (D : ℕ → R) (a e : ℕ → ℝ) (hzero : D 0 = 0) (ha : ∀ n, 0 ≤ a n)
    (hstep : ∀ n, ‖D (n + 1)‖ ≤ a n * ‖D n‖ + e n) (n : ℕ) :
    ‖D n‖ ≤ propagatedError a e n := by
  induction n with
  | zero => simp [hzero, propagatedError]
  | succ n ih =>
    exact (hstep n).trans (add_le_add (mul_le_mul_of_nonneg_left ih (ha n)) le_rfl)

section Ring
variable {R : Type*} [Ring R]

/-- The discrepancy recursion is derived from multiplication, not assumed. -/
theorem product_discrepancy_step (A B : ℕ → R) (n : ℕ) :
    chainProduct B (n + 1) - chainProduct A (n + 1) =
      B n * (chainProduct B n - chainProduct A n) +
      (B n - A n) * chainProduct A n := by
  simp only [chainProduct]
  noncomm_ring

/-- The corresponding exact identity for additive post-product recompression. -/
theorem recompression_discrepancy_step (A E : ℕ → R) (n : ℕ) :
    recompressedProduct A E (n + 1) - chainProduct A (n + 1) =
      A n * (recompressedProduct A E n - chainProduct A n) + E n := by
  simp only [recompressedProduct, chainProduct]
  noncomm_ring

/-- Constant-factor products are the actual ring power. -/
theorem chainProduct_const (A : R) (n : ℕ) : chainProduct (fun _ => A) n = A ^ n := by
  induction n with
  | zero => simp [chainProduct]
  | succ n ih => simp [chainProduct, ih, pow_succ']
end Ring

section NormedRing
variable {R : Type*} [NormedRing R]

/-- Theorem 5.9, including a user-supplied bound on every recompression residual. -/
theorem repeated_recompression_bound (A E : ℕ → R) (δ : ℕ → ℝ)
    (hδ : ∀ j, ‖E j‖ ≤ δ j) (n : ℕ) :
    ‖recompressedProduct A E n - chainProduct A n‖ ≤
      ∑ j ∈ Finset.range n, (∏ i ∈ Finset.Ico (j + 1) n, ‖A i‖) * δ j := by
  rw [← propagatedError_eq_sum]
  apply norm_recurrence_bound
      (fun k => recompressedProduct A E k - chainProduct A k)
      (fun k => ‖A k‖) δ (by simp [chainProduct, recompressedProduct])
      (fun k => norm_nonneg _)
  intro k
  rw [recompression_discrepancy_step]
  exact (norm_add_le _ _).trans (add_le_add (norm_mul_le _ _) (hδ k))

/-- Theorem 5.9 with the actual residual norms, with no uniform-tolerance assumption. -/
theorem repeated_recompression_actual_error (A E : ℕ → R) (n : ℕ) :
    ‖recompressedProduct A E n - chainProduct A n‖ ≤
      ∑ j ∈ Finset.range n, (∏ i ∈ Finset.Ico (j + 1) n, ‖A i‖) * ‖E j‖ :=
  repeated_recompression_bound A E (fun j => ‖E j‖) (fun _ => le_rfl) n

/-- Exact products have the expected product-of-norms bound. -/
theorem chainProduct_norm_bound [NormOneClass R] (A : ℕ → R) (n : ℕ) :
    ‖chainProduct A n‖ ≤ ∏ j ∈ Finset.range n, ‖A j‖ := by
  induction n with
  | zero => simp [chainProduct]
  | succ n ih =>
    rw [chainProduct, Finset.prod_range_succ]
    exact (norm_mul_le _ _).trans (by nlinarith [norm_nonneg (A n)])

/-- Theorem 5.8, with arbitrary certified per-factor operator errors. -/
theorem product_chain_error_bound [NormOneClass R] (A B : ℕ → R) (δ : ℕ → ℝ)
    (hδ : ∀ j, ‖B j - A j‖ ≤ δ j) (n : ℕ) :
    ‖chainProduct B n - chainProduct A n‖ ≤
      ∑ j ∈ Finset.range n,
        (∏ i ∈ Finset.Ico (j + 1) n, ‖B i‖) *
          (δ j * ∏ i ∈ Finset.range j, ‖A i‖) := by
  rw [← propagatedError_eq_sum]
  apply norm_recurrence_bound (fun k => chainProduct B k - chainProduct A k)
    (fun k => ‖B k‖) (fun k => δ k * ∏ i ∈ Finset.range k, ‖A i‖)
    (by simp [chainProduct]) (fun k => norm_nonneg _)
  intro k
  rw [product_discrepancy_step]
  apply (norm_add_le _ _).trans
  apply add_le_add (norm_mul_le _ _)
  apply (norm_mul_le _ _).trans
  exact mul_le_mul (hδ k) (chainProduct_norm_bound A k) (norm_nonneg _)
    ((norm_nonneg _).trans (hδ k))

/-- The displayed product-chain bound, for actual additive perturbations. -/
theorem product_chain_perturbation [NormOneClass R] (A E : ℕ → R) (n : ℕ) :
    ‖chainProduct (fun j => A j + E j) n - chainProduct A n‖ ≤
      ∑ j ∈ Finset.range n,
        (∏ i ∈ Finset.Ico (j + 1) n, ‖A i + E i‖) *
          ‖E j‖ * (∏ i ∈ Finset.range j, ‖A i‖) := by
  simpa only [add_sub_cancel_left, mul_assoc] using
    product_chain_error_bound A (fun j => A j + E j) (fun j => ‖E j‖)
      (fun j => by simp) n
end NormedRing

section PacketChains
variable {K X I E : Type*} [NontriviallyNormedField K]
variable [NormedAddCommGroup X] [NormedSpace K X] [Nontrivial X] [Fintype E]

/-- Corollary 8.3, with the preceding packet certificate substituted stage by stage.
This is an operator-norm certificate, not a vector-specific error used as one. -/
theorem mixed_precision_product_chain
    (P : ℕ → I → X →L[K] X) (src : ℕ → E → I)
    (A Δ : ℕ → E → X →L[K] X)
    (hΔ : ∀ j e, Δ j e = (Δ j e).comp (P j (src j e))) (n : ℕ) :
    ‖chainProduct (fun j => ∑ e, (A j e + Δ j e)) n -
      chainProduct (fun j => ∑ e, A j e) n‖ ≤
      ∑ j ∈ Finset.range n,
        (∏ i ∈ Finset.Ico (j + 1) n, ‖∑ e, (A i e + Δ i e)‖) *
          ((∑ e, ‖Δ j e‖ * ‖P j (src j e)‖) *
            (∏ i ∈ Finset.range j, ‖∑ e, A i e‖)) := by
  exact product_chain_error_bound (R := X →L[K] X)
    (fun j => ∑ e, A j e) (fun j => ∑ e, (A j e + Δ j e))
    (fun j => ∑ e, ‖Δ j e‖ * ‖P j (src j e)‖)
    (fun j => packet_operator_perturbation_bound (P j) (src j) (A j) (Δ j) (hΔ j)) n

/-- The final vector error follows from the verified operator bound. -/
theorem chain_action_error {K X : Type*} [NontriviallyNormedField K]
    [NormedAddCommGroup X] [NormedSpace K X]
    (A B : ℕ → X →L[K] X) (n : ℕ) (C : ℝ)
    (h : ‖chainProduct B n - chainProduct A n‖ ≤ C) (x : X) :
    ‖chainProduct B n x - chainProduct A n x‖ ≤ C * ‖x‖ := by
  exact ((chainProduct B n - chainProduct A n).le_opNorm x).trans
    (mul_le_mul_of_nonneg_right h (norm_nonneg x))
end PacketChains
end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.propagatedError_eq_sum
#print axioms KomorebiPaperVIII.propagatedError_mono
#print axioms KomorebiPaperVIII.norm_recurrence_bound
#print axioms KomorebiPaperVIII.product_discrepancy_step
#print axioms KomorebiPaperVIII.recompression_discrepancy_step
#print axioms KomorebiPaperVIII.chainProduct_const
#print axioms KomorebiPaperVIII.repeated_recompression_bound
#print axioms KomorebiPaperVIII.repeated_recompression_actual_error
#print axioms KomorebiPaperVIII.chainProduct_norm_bound
#print axioms KomorebiPaperVIII.product_chain_error_bound
#print axioms KomorebiPaperVIII.product_chain_perturbation
#print axioms KomorebiPaperVIII.mixed_precision_product_chain
#print axioms KomorebiPaperVIII.chain_action_error
