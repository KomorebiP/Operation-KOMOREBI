module
public import Mathlib.LinearAlgebra.Matrix.ConjTranspose
public import Mathlib.Algebra.BigOperators.Ring.Finset
public import Mathlib.Data.Fintype.Pi
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Analysis.Complex.Basic
/-! Author: Komorebi P. Paper VII second block, Theorem 3.2.
Arbitrary finite tensor products and regrouping by total residue. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVII.TensorRefinement
open scoped BigOperators
section Tensor
variable {F : Type*} [Fintype F] [DecidableEq F]
  {D : F → Type*} [∀ i, Fintype (D i)]
def tensor (A : (i : F) → Matrix (D i) (D i) ℂ) :
    Matrix ((i : F) → D i) ((i : F) → D i) ℂ :=
  fun x y => ∏ i, A i (x i) (y i)

theorem tensor_mul (A B : (i : F) → Matrix (D i) (D i) ℂ) :
    tensor (fun i => A i * B i) = tensor A * tensor B := by
  ext x y
  simp only [tensor, Matrix.mul_apply]
  rw [Fintype.prod_sum]
  apply Finset.sum_congr rfl
  intro z _
  exact Finset.prod_mul_distrib

omit [∀ i, Fintype (D i)] [DecidableEq F] in
theorem tensor_one [∀ i, DecidableEq (D i)] :
    tensor (fun i => (1 : Matrix (D i) (D i) ℂ)) = 1 := by
  classical
  ext x y
  by_cases h : x = y
  · subst y
    simp [tensor]
  · simp only [tensor, Matrix.one_apply, h, ite_false]
    obtain ⟨i, hi⟩ := Function.ne_iff.mp h
    exact Finset.prod_eq_zero (Finset.mem_univ i) (by simp [hi])

omit [∀ i, Fintype (D i)] in
theorem tensor_sum {J : F → Type*} [∀ i, Fintype (J i)]
    (P : (i : F) → J i → Matrix (D i) (D i) ℂ) :
    (∑ a : (i : F) → J i, tensor (fun i => P i (a i))) =
      tensor (fun i => ∑ j, P i j) := by
  ext x y
  simp only [Matrix.sum_apply]
  change (∑ a : (i : F) → J i, ∏ i, P i (a i) (x i) (y i)) =
    ∏ i, (∑ j, P i j) (x i) (y i)
  simp only [Matrix.sum_apply]
  exact (Fintype.prod_sum (fun i j => P i j (x i) (y i))).symm

omit [∀ i, Fintype (D i)] [DecidableEq F] in
theorem tensor_adjoint (A : (i : F) → Matrix (D i) (D i) ℂ) :
    (tensor A).conjTranspose = tensor (fun i => (A i).conjTranspose) := by
  ext x y
  simp [tensor, Matrix.conjTranspose_apply]
end Tensor

section Fine
variable {F : Type*} [Fintype F] [DecidableEq F] {D J : F → Type*}
variable [∀ i, Fintype (D i)] [∀ i, DecidableEq (D i)]
variable [∀ i, Fintype (J i)] [∀ i, DecidableEq (J i)]
variable (P : (i : F) → J i → Matrix (D i) (D i) ℂ)

omit [∀ i, DecidableEq (D i)] [∀ i, Fintype (J i)] in
theorem fine_mul
    (hmul : ∀ i j k, P i j * P i k = if j = k then P i j else 0)
    (a b : (i : F) → J i) :
    tensor (fun i => P i (a i)) * tensor (fun i => P i (b i)) =
      if a = b then tensor (fun i => P i (a i)) else 0 := by
  classical
  rw [← tensor_mul]
  by_cases h : a = b
  · subst b
    simp only [ite_true, hmul]
  · simp only [h, ite_false]
    obtain ⟨i, hi⟩ := Function.ne_iff.mp h
    ext x y
    simp only [tensor, Matrix.zero_apply]
    apply Finset.prod_eq_zero (Finset.mem_univ i)
    simp only [hmul, hi, ite_false]
    rfl

omit [∀ i, Fintype (D i)] [∀ i, DecidableEq (J i)] in
theorem fine_complete (hsum : ∀ i, ∑ j, P i j = 1) :
    (∑ a : (i : F) → J i, tensor (fun i => P i (a i))) = 1 := by
  rw [tensor_sum]
  simp_rw [hsum]
  exact tensor_one

omit [DecidableEq F] [∀ i, Fintype (D i)] [∀ i, DecidableEq (D i)]
  [∀ i, Fintype (J i)] [∀ i, DecidableEq (J i)] in
theorem fine_selfAdjoint (hstar : ∀ i j, (P i j).conjTranspose = P i j)
    (a : (i : F) → J i) :
    (tensor (fun i => P i (a i))).conjTranspose = tensor (fun i => P i (a i)) := by
  rw [tensor_adjoint]
  simp_rw [hstar]
end Fine

section Coarse
variable {R I J : Type*} [Ring R] [Fintype I] [DecidableEq I]
variable [Fintype J] [DecidableEq J]
def coarse (P : I → R) (address : I → J) (r : J) : R :=
  ∑ a, if address a = r then P a else 0

omit [Fintype J] in
theorem coarse_mul (P : I → R) (address : I → J)
    (hmul : ∀ a b, P a * P b = if a = b then P a else 0) (r s : J) :
    coarse P address r * coarse P address s =
      if r = s then coarse P address r else 0 := by
  unfold coarse
  simp only [Finset.sum_mul, Finset.mul_sum]
  have term (a b : I) :
      (if address a = r then P a else 0) * (if address b = s then P b else 0) =
      if a = b then (if address a = r ∧ r = s then P a else 0) else 0 := by
    by_cases hab : a = b
    · subst b
      by_cases hr : address a = r <;> by_cases hs : r = s <;>
        simp_all
    · simp [hmul, hab, ite_mul, mul_ite]
  simp_rw [term]
  by_cases hrs : r = s <;> simp [hrs]

omit [DecidableEq I] in
theorem coarse_complete (P : I → R) (address : I → J) (hsum : ∑ a, P a = 1) :
    (∑ r, coarse P address r) = 1 := by
  unfold coarse
  rw [Finset.sum_comm]
  simpa using hsum

omit [DecidableEq I] [Fintype J] in
theorem coarse_selfAdjoint [StarRing R] (P : I → R) (address : I → J)
    (hstar : ∀ a, star (P a) = P a) (r : J) :
    star (coarse P address r) = coarse P address r := by
  simp [coarse, star_sum, apply_ite, hstar]
end Coarse

theorem tensor_polyphase_refinement {F : Type*} [Fintype F] [DecidableEq F] {D : F → Type*}
    [∀ i, Fintype (D i)] [∀ i, DecidableEq (D i)]
    (N : ℕ) [NeZero N] (P : (i : F) → ZMod N → Matrix (D i) (D i) ℂ)
    (hmul : ∀ i j k, P i j * P i k = if j = k then P i j else 0)
    (hsum : ∀ i, ∑ j, P i j = 1)
    (hstar : ∀ i j, (P i j).conjTranspose = P i j) :
    let Q := fun a : F → ZMod N => tensor (fun i => P i (a i))
    let C := coarse Q (fun a => ∑ i, a i)
    (∀ r s, C r * C s = if r = s then C r else 0) ∧
      (∑ r, C r) = 1 ∧ (∀ r, (C r).conjTranspose = C r) := by
  classical
  dsimp only
  refine ⟨?_, ?_, ?_⟩
  · exact coarse_mul _ _ (fine_mul P hmul)
  · exact coarse_complete _ _ (fine_complete P hsum)
  · exact coarse_selfAdjoint _ _ (fine_selfAdjoint P hstar)
end KomorebiPaperVII.TensorRefinement

#print axioms KomorebiPaperVII.TensorRefinement.tensor_mul
#print axioms KomorebiPaperVII.TensorRefinement.tensor_one
#print axioms KomorebiPaperVII.TensorRefinement.tensor_sum
#print axioms KomorebiPaperVII.TensorRefinement.tensor_adjoint
#print axioms KomorebiPaperVII.TensorRefinement.fine_mul
#print axioms KomorebiPaperVII.TensorRefinement.fine_complete
#print axioms KomorebiPaperVII.TensorRefinement.fine_selfAdjoint
#print axioms KomorebiPaperVII.TensorRefinement.coarse_mul
#print axioms KomorebiPaperVII.TensorRefinement.coarse_complete
#print axioms KomorebiPaperVII.TensorRefinement.coarse_selfAdjoint
#print axioms KomorebiPaperVII.TensorRefinement.tensor_polyphase_refinement
