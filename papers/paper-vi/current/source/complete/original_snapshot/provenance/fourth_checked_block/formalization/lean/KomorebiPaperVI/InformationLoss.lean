import KomorebiPaperVI.Coarsening

/-! Author: Komorebi P. Literal information-loss matrix and the fine-to-coarse loss estimate. -/
namespace KomorebiPaperVI.InformationLoss
open KomorebiPaperVI.FiniteBayes KomorebiPaperVI.Coarsening
open scoped BigOperators
variable {I A : Type*} [Fintype I] [Fintype A] [DecidableEq A]

def lossMatrix (P b : A → ℝ) : Matrix A A ℝ :=
  fun a j => (if a=j then P a else 0)-b a*P j

theorem lossMatrix_apply (P b d : A → ℝ) (a : A) :
    (lossMatrix P b).mulVec d a=P a*d a-b a*(∑ j, P j*d j) := by
  simp [lossMatrix, Matrix.mulVec, dotProduct, sub_mul, Finset.sum_sub_distrib,
    ite_mul, mul_assoc, ← Finset.mul_sum]

theorem information_loss_matrix (f : I → A) (p l : I → ℝ) (k : A → ℝ)
    (hp : ∀ i, 0 ≤ p i) (hz : evidence p l ≠ 0)
    (hk : evidence (coarsen f p) k ≠ 0) (a : A) :
    coarsen f (update p l) a-update (coarsen f p) k a =
      (lossMatrix (coarsen f p) (update (coarsen f p) k)).mulVec
        (fun j => effective f p l j-k j) a/evidence p l := by
  rw [effective_factorization f p l hp, lossMatrix_apply]
  have he := posterior_difference (coarsen f p) (effective f p l) k
    (by rwa [effective_evidence f p l hp]) hk a
  simpa only [effective_evidence f p l hp] using he

theorem information_loss_null (P k : A → ℝ) (hk : evidence P k ≠ 0) :
    (lossMatrix P (update P k)).mulVec k=0 := by
  funext a
  rw [lossMatrix_apply]
  exact scale_null_direction P k hk a

omit [Fintype A] in
theorem fiber_loss_bound (f : I → A) (p l : I → ℝ) (k : A → ℝ)
    (hp : ∀ i, 0 ≤ p i) (a : A) :
    coarsen f p a*|effective f p l a-k a| ≤
      coarsen f (fun i => p i*|l i-k (f i)|) a := by
  have he : (effective f p l a-k a)*coarsen f p a =
      ∑ i, if f i=a then p i*(l i-k (f i)) else 0 := by
    rw [sub_mul,effective_weight f p l hp]
    simp only [coarsen, Finset.mul_sum, ← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro i _
    by_cases hi : f i=a
    · simp only [hi,ite_true]; ring
    · simp [hi]
  calc
    _ = |(effective f p l a-k a)*coarsen f p a| := by
      rw [abs_mul, abs_of_nonneg (coarsen_nonnegative f p hp a), mul_comm]
    _ ≤ ∑ i, |if f i=a then p i*(l i-k (f i)) else 0| := by
      rw [he]; exact Finset.abs_sum_le_sum_abs _ _
    _ = _ := by
      apply Finset.sum_congr rfl
      intro i _
      by_cases hi : f i=a
      · simp [hi, abs_mul, abs_of_nonneg (hp i)]
      · simp [hi]

theorem total_loss_bound (f : I → A) (p l : I → ℝ) (k : A → ℝ)
    (hp : ∀ i, 0 ≤ p i) :
    (∑ a, coarsen f p a*|effective f p l a-k a|) ≤ ∑ i, p i*|l i-k (f i)| := by
  calc
    _ ≤ ∑ a, coarsen f (fun i => p i*|l i-k (f i)|) a :=
      Finset.sum_le_sum (fun a _ => fiber_loss_bound f p l k hp a)
    _ = _ := coarsen_mass f _

theorem information_loss_norm (f : I → A) (p l : I → ℝ) (k : A → ℝ)
    (hp : ∀ i, 0 ≤ p i) (hl : ∀ i, 0 ≤ l i) (hk : ∀ a, 0 ≤ k a)
    (hz : 0 < evidence p l) (hzk : 0 < evidence (coarsen f p) k) :
    l1 (fun a => coarsen f (update p l) a-update (coarsen f p) k a) ≤
      2*(∑ a, coarsen f p a*|effective f p l a-k a|)/
        min (evidence p l) (evidence (coarsen f p) k) := by
  rw [effective_factorization f p l hp]
  have he := likelihood_perturbation_bound (coarsen f p) (effective f p l) k
    (coarsen_nonnegative f p hp) (effective_nonnegative f p l hp hl) hk
    (by rwa [effective_evidence f p l hp]) hzk
  simpa only [effective_evidence f p l hp, mul_comm] using he

end KomorebiPaperVI.InformationLoss
