module
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.Analysis.Calculus.Deriv.Star
public import Mathlib.Analysis.Calculus.Deriv.Add
public import Mathlib.Algebra.Star.BigOperators
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Tactic.NormNum
/-! Author: Komorebi P. Paper VII second block, Theorem 6.3.
The differential identities are derived from actual derivatives. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVII.Connection
open scoped BigOperators
section Algebra
variable {R I : Type*} [Ring R] [Fintype I] [DecidableEq I]
def canonical (P D : I → R) : R := ∑ a, D a * P a

theorem canonical_right (P D : I → R)
    (hmul : ∀ a b, P a * P b = if a = b then P a else 0) (b : I) :
    canonical P D * P b = D b * P b := by
  simp [canonical, Finset.sum_mul, mul_assoc, hmul, mul_ite]

theorem canonical_left_relation (P D : I → R)
    (hmul : ∀ a b, P a * P b = if a = b then P a else 0)
    (hsum : ∑ a, P a = 1)
    (hjet : ∀ a b, D a * P b + P a * D b = if a = b then D a else 0)
    (b : I) : D b + P b * canonical P D = D b * P b := by
  have term (a : I) : D b * P a + P b * (D a * P a) =
      if b = a then D b * P b else 0 := by
    calc
      _ = (D b * P a + P b * D a) * P a := by
        simp only [add_mul, mul_assoc, hmul a a, ite_true]
      _ = _ := by rw [hjet]; split_ifs with h <;> simp_all
  calc
    _ = ∑ a, (D b * P a + P b * (D a * P a)) := by
      simp only [Finset.sum_add_distrib, ← Finset.mul_sum, hsum, mul_one, canonical]
    _ = D b * P b := by simp_rw [term]; simp

theorem canonical_commutator (P D : I → R)
    (hmul : ∀ a b, P a * P b = if a = b then P a else 0)
    (hsum : ∑ a, P a = 1)
    (hjet : ∀ a b, D a * P b + P a * D b = if a = b then D a else 0)
    (b : I) : canonical P D * P b - P b * canonical P D = D b := by
  rw [canonical_right P D hmul, ← canonical_left_relation P D hmul hsum hjet b]
  abel

omit [DecidableEq I] in
theorem canonical_skewAdjoint [StarRing R] (P D : I → R)
    (hstarP : ∀ a, star (P a) = P a) (hstarD : ∀ a, star (D a) = D a)
    (hsumD : ∑ a, D a = 0)
    (hdiag : ∀ a, D a * P a + P a * D a = D a) :
    star (canonical P D) = -canonical P D := by
  have h : canonical P D + star (canonical P D) = 0 := by
    simp only [canonical, star_sum, star_mul, hstarP, hstarD,
      ← Finset.sum_add_distrib, hdiag, hsumD]
  exact (add_eq_zero_iff_eq_neg).mp (by simpa only [add_comm] using h)

omit [DecidableEq I] in
theorem canonical_half_commutator [Algebra ℝ R] (P D : I → R)
    (hsumD : ∑ a, D a = 0)
    (hdiag : ∀ a, D a * P a + P a * D a = D a) :
    (1 / 2 : ℝ) • (∑ a, (D a * P a - P a * D a)) = canonical P D := by
  have h : (∑ a, D a * P a) + (∑ a, P a * D a) = 0 := by
    simp only [← Finset.sum_add_distrib, hdiag, hsumD]
  have hneg : (∑ a, P a * D a) = -(∑ a, D a * P a) :=
    (add_eq_zero_iff_eq_neg).mp (by simpa only [add_comm] using h)
  rw [Finset.sum_sub_distrib, hneg, sub_neg_eq_add, ← two_smul ℝ, smul_smul]
  norm_num [canonical]
end Algebra

section Derivatives
variable {R I : Type*} [NormedRing R] [NormedAlgebra ℝ R]
variable [StarRing R] [StarModule ℝ R] [ContinuousStar R]
variable [Fintype I] [DecidableEq I]
variable (P : I → ℝ → R) (D : I → R) (t : ℝ)

omit [StarRing R] [StarModule ℝ R] [ContinuousStar R] [Fintype I] in
theorem differentiated_orthogonality
    (hd : ∀ a, HasDerivAt (P a) (D a) t)
    (hmul : ∀ s a b, P a s * P b s = if a = b then P a s else 0)
    (a b : I) : D a * P b t + P a t * D b = if a = b then D a else 0 := by
  have h := (hd a).mul (hd b)
  change HasDerivAt (fun s => P a s * P b s) (D a * P b t + P a t * D b) t at h
  by_cases hab : a = b
  · subst b
    have heq : (fun s => P a s * P a s) = P a := by
      funext s
      simpa only [ite_true] using hmul s a a
    rw [heq] at h
    simpa only [ite_true] using h.unique (hd a)
  · have heq : (fun s => P a s * P b s) = fun _ => (0 : R) := by
      funext s
      simpa only [hab, ite_false] using hmul s a b
    rw [heq] at h
    simpa only [hab, ite_false] using h.unique (hasDerivAt_const t (0 : R))

omit [StarRing R] [StarModule ℝ R] [ContinuousStar R] [DecidableEq I] in
theorem differentiated_completeness
    (hd : ∀ a, HasDerivAt (P a) (D a) t)
    (hsum : ∀ s, ∑ a, P a s = 1) : ∑ a, D a = 0 := by
  have h := HasDerivAt.fun_sum (u := Finset.univ) (fun a _ => hd a)
  simp_rw [hsum] at h
  exact h.unique (hasDerivAt_const t (1 : R))

omit [Fintype I] [DecidableEq I] in
theorem differentiated_selfAdjoint
    (hd : ∀ a, HasDerivAt (P a) (D a) t)
    (hstar : ∀ s a, star (P a s) = P a s) (a : I) : star (D a) = D a := by
  have h := (hd a).star
  simp_rw [hstar] at h
  exact h.unique (hd a)

theorem canonical_connection_of_hasDerivAt
    (hd : ∀ a, HasDerivAt (P a) (D a) t)
    (hmul : ∀ s a b, P a s * P b s = if a = b then P a s else 0)
    (hsum : ∀ s, ∑ a, P a s = 1)
    (hstar : ∀ s a, star (P a s) = P a s) :
    let C := canonical (fun a => P a t) D
    star C = -C ∧
      (∀ b, C * P b t - P b t * C = D b) ∧
      (1 / 2 : ℝ) • (∑ a, (D a * P a t - P a t * D a)) = C := by
  dsimp only
  have hj := differentiated_orthogonality P D t hd hmul
  have hdiag (a : I) : D a * P a t + P a t * D a = D a := by
    simpa only [ite_true] using hj a a
  have hz := differentiated_completeness P D t hd hsum
  refine ⟨?_, ?_, ?_⟩
  · exact canonical_skewAdjoint _ _ (hstar t)
      (differentiated_selfAdjoint P D t hd hstar) hz hdiag
  · exact canonical_commutator _ _ (hmul t) (hsum t) hj
  · exact canonical_half_commutator _ _ hz hdiag
end Derivatives
end KomorebiPaperVII.Connection

#print axioms KomorebiPaperVII.Connection.canonical_right
#print axioms KomorebiPaperVII.Connection.canonical_left_relation
#print axioms KomorebiPaperVII.Connection.canonical_commutator
#print axioms KomorebiPaperVII.Connection.canonical_skewAdjoint
#print axioms KomorebiPaperVII.Connection.canonical_half_commutator
#print axioms KomorebiPaperVII.Connection.differentiated_orthogonality
#print axioms KomorebiPaperVII.Connection.differentiated_completeness
#print axioms KomorebiPaperVII.Connection.differentiated_selfAdjoint
#print axioms KomorebiPaperVII.Connection.canonical_connection_of_hasDerivAt
