import KomorebiLSM.BayesianClosure
import Mathlib.Data.Matrix.Mul

/-! P12's fixed-prior defect, including empty prior-mass blocks. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteBayes
open scoped BigOperators
universe u v
variable {I : Type u} {A : Type v}
variable [Fintype I] [Fintype A] [DecidableEq A]

noncomputable def effectiveLikelihood (c : I → A) (p l : I → ℝ) (a : A) : ℝ :=
  aggregate c (fun i => p i * l i) a / aggregate c p a

omit [Fintype A] in
theorem zero_mass_weight (c : I → A) (p l : I → ℝ) (hp : ∀ i, 0 ≤ p i)
    (a : A) (hz : aggregate c p a = 0) : aggregate c (fun i => p i * l i) a = 0 := by
  have hpoint : ∀ i, c i = a → p i = 0 := by
    intro i hi
    have hn : ∀ j ∈ (Finset.univ : Finset I), 0 ≤ (if c j = a then p j else 0) := by
      intro j _; split_ifs; exact hp j; exact le_rfl
    have hh := Finset.single_le_sum hn (Finset.mem_univ i)
    change (if c i = a then p i else 0) ≤ aggregate c p a at hh
    rw [hz] at hh
    exact le_antisymm (by simpa [hi] using hh) (hp i)
  apply Finset.sum_eq_zero
  intro i _
  by_cases hi : c i = a
  · simp [hi, hpoint i hi]
  · simp [hi]

omit [Fintype A] in
theorem effectiveLikelihood_product (c : I → A) (p l : I → ℝ)
    (hp : ∀ i, 0 ≤ p i) (a : A) :
    aggregate c p a * effectiveLikelihood c p l a = aggregate c (fun i => p i * l i) a := by
  by_cases h : aggregate c p a = 0
  · rw [h, zero_mul, zero_mass_weight c p l hp a h]
  · unfold effectiveLikelihood
    field_simp

theorem effectiveLikelihood_evidence (c : I → A) (p l : I → ℝ)
    (hp : ∀ i, 0 ≤ p i) :
    evidence (aggregate c p) (effectiveLikelihood c p l) = evidence p l := by
  simp only [evidence, effectiveLikelihood_product c p l hp, aggregate_sum]

theorem aggregate_posterior_effective (c : I → A) (p l : I → ℝ)
    (hp : ∀ i, 0 ≤ p i) :
    aggregate c (posterior p l) = posterior (aggregate c p) (effectiveLikelihood c p l) := by
  unfold posterior
  rw [aggregate_div, effectiveLikelihood_evidence c p l hp]
  funext a
  rw [effectiveLikelihood_product c p l hp]

omit [Fintype A] [DecidableEq A] in
theorem posterior_difference (p r b : I → ℝ)
    (hr : evidence p r ≠ 0) (hb : evidence p b ≠ 0) (i : I) :
    posterior p r i - posterior p b i =
      (p i * (r i - b i) - posterior p b i * (∑ j, p j * (r j - b j))) / evidence p r := by
  have he : (∑ j, p j * (r j - b j)) = evidence p r - evidence p b := by
    simp [evidence, mul_sub, Finset.sum_sub_distrib]
  rw [he]
  unfold posterior
  field_simp
  ring

theorem bayesian_coarsening_defect (c : I → A) (p l : I → ℝ) (b : A → ℝ)
    (hp : ∀ i, 0 ≤ p i) (hlz : evidence p l ≠ 0)
    (hbz : evidence (aggregate c p) b ≠ 0) (a : A) :
    aggregate c (posterior p l) a - posterior (aggregate c p) b a =
      (aggregate c p a * (effectiveLikelihood c p l a - b a) -
        posterior (aggregate c p) b a *
          (∑ k, aggregate c p k * (effectiveLikelihood c p l k - b k))) /
          evidence (aggregate c p) (effectiveLikelihood c p l) := by
  rw [aggregate_posterior_effective c p l hp]
  exact posterior_difference (aggregate c p) (effectiveLikelihood c p l) b
    (by rwa [effectiveLikelihood_evidence c p l hp]) hbz a

omit [Fintype I] in
noncomputable def informationLossMatrix (p b : A → ℝ) : Matrix A A ℝ :=
  Matrix.diagonal p - Matrix.vecMulVec (posterior p b) p

omit [Fintype I] in
theorem informationLossMatrix_apply (p b d : A → ℝ) (a : A) :
    (informationLossMatrix p b).mulVec d a =
      p a * d a - posterior p b a * (∑ k, p k * d k) := by
  simp [informationLossMatrix, Matrix.mulVec, dotProduct, sub_mul,
    Finset.sum_sub_distrib, Matrix.diagonal, Matrix.vecMulVec, mul_assoc, ← Finset.mul_sum]

theorem bayesian_coarsening_matrix_defect (c : I → A) (p l : I → ℝ) (b : A → ℝ)
    (hp : ∀ i, 0 ≤ p i) (hlz : evidence p l ≠ 0)
    (hbz : evidence (aggregate c p) b ≠ 0) :
    (fun a => aggregate c (posterior p l) a - posterior (aggregate c p) b a) =
      fun a => ((informationLossMatrix (aggregate c p) b).mulVec
        (fun k => effectiveLikelihood c p l k - b k)) a /
          evidence (aggregate c p) (effectiveLikelihood c p l) := by
  funext a
  rw [informationLossMatrix_apply]
  exact bayesian_coarsening_defect c p l b hp hlz hbz a

omit [Fintype I] in
theorem informationLossMatrix_scale_null (p b : A → ℝ) (hz : evidence p b ≠ 0) :
    (informationLossMatrix p b).mulVec b = 0 := by
  funext a
  rw [informationLossMatrix_apply]
  change p a * b a - (p a * b a / evidence p b) * evidence p b = 0
  rw [div_mul_cancel₀ _ hz, sub_self]

end Komorebi.LSM.FiniteBayes
