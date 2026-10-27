import KomorebiVerification.ProjectorCore

/-!
# Paper I: operator-level block completion

This file upgrades the pointwise transfer-block formulas in `ProjectorCore` to
equalities of linear maps.  It also records sharp converses for support of the
ordinary identity matrix and closure of ordinary supported matrices under
multiplication.
-/

set_option autoImplicit false

namespace Komorebi

namespace Foundation

universe u v w x y z

variable {R : Type u} {M : Type v} {N : Type w} {L : Type x}
variable {ι : Type y} {κ : Type z} {τ : Type*}
variable [Semiring R]
variable [AddCommMonoid M] [Module R M]
variable [AddCommMonoid N] [Module R N]
variable [AddCommMonoid L] [Module R L]
variable [Fintype ι] [Fintype κ] [Fintype τ]

/-- A linear map is the finite sum of all of its transfer blocks. -/
theorem transferBlock_reconstruction_linearMap
    (P : LinearProjectorFamily R M ι)
    (Q : LinearProjectorFamily R N κ)
    (T : M →ₗ[R] N) :
    (∑ j, ∑ i, transferBlock P Q T j i) = T := by
  ext x
  simp only [LinearMap.sum_apply]
  exact transferBlock_reconstruction P Q T x

/-- Endomorphism-specialized operator-level transfer-block reconstruction. -/
theorem transferBlock_reconstruction_end
    (P : LinearProjectorFamily R M ι) (T : Module.End R M) :
    (∑ j, ∑ i, transferBlock P P T j i) = T :=
  transferBlock_reconstruction_linearMap P P T

/--
The `(k,i)` transfer block of a composite is the sum, over the intermediate
packet, of the corresponding composites of transfer blocks.
-/
theorem transferBlock_comp_linearMap
    (P : LinearProjectorFamily R M ι)
    (Q : LinearProjectorFamily R N κ)
    (S : LinearProjectorFamily R L τ)
    (T : M →ₗ[R] N) (U : N →ₗ[R] L)
    (k : τ) (i : ι) :
    transferBlock P S (U.comp T) k i =
      ∑ j, (transferBlock Q S U k j).comp (transferBlock P Q T j i) := by
  ext x
  simp only [LinearMap.sum_apply, transferBlock, LinearMap.comp_apply,
    Q.idempotent]
  exact transferBlock_comp P Q S T U k i x

/-- Endomorphism-specialized block multiplication formula. -/
theorem transferBlock_comp_end
    (P : LinearProjectorFamily R M ι)
    (T U : Module.End R M) (k i : ι) :
    transferBlock P P (U.comp T) k i =
      ∑ j, (transferBlock P P U k j).comp (transferBlock P P T j i) :=
  transferBlock_comp_linearMap P P P T U k i

/-- Reconstruct a composite endomorphism from its blockwise products. -/
theorem end_comp_eq_sum_transferBlock_comps
    (P : LinearProjectorFamily R M ι) (T U : Module.End R M) :
    U.comp T =
      ∑ k, ∑ i, ∑ j,
        (transferBlock P P U k j).comp (transferBlock P P T j i) := by
  rw [← transferBlock_reconstruction_end P (U.comp T)]
  apply Finset.sum_congr rfl
  intro k hk
  apply Finset.sum_congr rfl
  intro i hi
  exact transferBlock_comp_end P T U k i

end Foundation

namespace Algebra

universe u v

/-- Closure of relation-supported ordinary square matrices under multiplication. -/
def MatrixSupportMulClosed
    {ι : Type u} {A : Type v}
    [Fintype ι] [DecidableEq ι] [Semiring A]
    (rel : ι → ι → Prop) : Prop :=
  ∀ M N : Matrix ι ι A,
    MatrixSupported rel M → MatrixSupported rel N → MatrixSupported rel (M * N)

/-- The ordinary identity matrix has support in `rel` exactly when `rel` is reflexive. -/
theorem matrixSupported_one_iff_reflexive
    {ι : Type u} {A : Type v}
    [DecidableEq ι] [Semiring A] [Nontrivial A]
    (rel : ι → ι → Prop) :
    MatrixSupported rel (1 : Matrix ι ι A) ↔ ∀ i, rel i i := by
  constructor
  · intro h i
    by_contra hii
    have hzero : (1 : Matrix ι ι A) i i = 0 := h i i hii
    rw [Matrix.one_apply, ite_eq_left rfl] at hzero
    exact (one_ne_zero : (1 : A) ≠ 0) hzero
  · intro hrefl i j hij
    have hne : i ≠ j := by
      intro h
      subst j
      exact hij (hrefl i)
    simp [hne]

/--
Supported ordinary matrices are closed under multiplication exactly when the
support relation is transitive.  `Nontrivial A` is needed for the converse so
that matrix units can detect a missing composite edge.
-/
theorem matrixSupportMulClosed_iff_transitive
    {ι : Type u} {A : Type v}
    [Fintype ι] [DecidableEq ι] [Semiring A] [Nontrivial A]
    (rel : ι → ι → Prop) :
    MatrixSupportMulClosed (A := A) rel ↔
      ∀ i j k, rel i j → rel j k → rel i k := by
  constructor
  · intro hclosed i j k hij hjk
    let Eij : Matrix ι ι A := Matrix.single i j 1
    let Ejk : Matrix ι ι A := Matrix.single j k 1
    have hEij : MatrixSupported rel Eij := by
      intro a b hab
      change (if i = a ∧ j = b then (1 : A) else 0) = 0
      split_ifs with h
      · rcases h with ⟨rfl, rfl⟩
        exact (hab hij).elim
      · rfl
    have hEjk : MatrixSupported rel Ejk := by
      intro a b hab
      change (if j = a ∧ k = b then (1 : A) else 0) = 0
      split_ifs with h
      · rcases h with ⟨rfl, rfl⟩
        exact (hab hjk).elim
      · rfl
    by_contra hik
    have hzero : (Eij * Ejk) i k = 0 :=
      hclosed Eij Ejk hEij hEjk i k hik
    have hone : (Eij * Ejk) i k = 1 := by
      simp [Eij, Ejk, Matrix.mul_apply, Matrix.single_apply]
    exact (one_ne_zero : (1 : A) ≠ 0) (hone.symm.trans hzero)
  · intro htrans M N hM hN
    exact MatrixSupported.mul htrans hM hN

end Algebra

end Komorebi
