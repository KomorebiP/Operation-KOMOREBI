import PaperX.SemilinearScalarExtension
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.Basis.VectorSpace

/-! Actual scalar-extended eigenspaces and their finite-copy decomposition.
The eigenspace is defined by the Galois action, not by a supplied weight label.
Identifying its dimension with a coordinate multiplicity requires arithmetic
invariant-space results and is not asserted in this file. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SemilinearPeriods
open TensorProduct PaperX.CarrierSummands PaperX.SemilinearScalarExtension
variable {R B G : Type*} [Field R] [Field B] [Algebra R B] [Group G]
variable (σ : G →* (B ≃ₐ[R] B)) (tate : ℤ → G →* Rˣ)
variable {V : Type*} [AddCommGroup V] [Module R V]

/-- Eigenperiods of exponent z in the actual scalar extension. With tate(z)=chi^z,
this is the invariant space of the negatively twisted representation. -/
def periodSpace (ρ : Representation R G V) (z : ℤ) : Submodule R (B ⊗[R] V) where
  carrier x := ∀ g, tensorRep σ ρ g x = (tate z g : R) • x
  zero_mem' := by intro g; simp
  add_mem' := by intro x y hx hy g; simp [map_add, hx g, hy g, smul_add]
  smul_mem' := by
    intro r x hx g
    rw [map_smul, hx g, smul_smul, smul_smul, mul_comm]

@[simp] theorem mem_periodSpace (ρ : Representation R G V) (z : ℤ) (x : B ⊗[R] V) :
    x ∈ periodSpace σ tate ρ z ↔ ∀ g, tensorRep σ ρ g x = (tate z g : R) • x := Iff.rfl

variable {I : Type*} [Fintype I]
variable {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module R (W i)]
variable (ρ : ∀ i, Representation R G (W i)) (m : I → ℕ) (z : ℤ)

theorem copiesEquiv_smul (r : R) (x : B ⊗[R] Copies W m) :
    copiesEquiv (R := R) (B := B) m (r • x) =
      r • copiesEquiv (R := R) (B := B) m x :=
  ((copiesEquiv (R := R) (B := B) m).restrictScalars R).map_smul r x

/-- The actual fixed-equation subspace is exactly the finite product of the
constituent fixed-equation subspaces. No constituent comparison is required. -/
def periodCopiesEquiv :
    periodSpace σ tate (copiesRep ρ m) z ≃ₗ[R]
      Copies (fun i => periodSpace σ tate (ρ i) z) m where
  toFun x i k := ⟨copiesEquiv (R := R) (B := B) m x.val i k, by
    intro g
    have h := congrArg (fun y => copiesEquiv (R := R) (B := B) m y i k) (x.property g)
    simpa only [copiesEquiv_equivariant, copiesRep_apply, copiesEquiv_smul,
      Pi.smul_apply] using h⟩
  invFun y := ⟨(copiesEquiv (R := R) (B := B) m).symm (fun i k => (y i k).val), by
    intro g
    apply (copiesEquiv (R := R) (B := B) m).injective
    rw [copiesEquiv_equivariant, LinearMapClass.map_smul_of_tower, LinearEquiv.apply_symm_apply]
    funext i k
    exact (y i k).property g⟩
  left_inv x := by
    apply Subtype.ext
    exact (copiesEquiv (R := R) (B := B) m).symm_apply_apply x.val
  right_inv y := by
    funext i k
    apply Subtype.ext
    exact congrArg (fun v => v i k)
      ((copiesEquiv (R := R) (B := B) m).apply_symm_apply (fun i k => (y i k).val))
  map_add' x y := by
    funext i k
    apply Subtype.ext
    exact congrArg (fun v => v i k)
      ((copiesEquiv (R := R) (B := B) m).map_add x.val y.val)
  map_smul' r x := by
    funext i k
    apply Subtype.ext
    exact congrArg (fun v => v i k)
      (LinearMapClass.map_smul_of_tower (copiesEquiv (R := R) (B := B) m) r x.val)

@[simp] theorem periodCopiesEquiv_apply
    (x : periodSpace σ tate (copiesRep ρ m) z) (i : I) (k : Fin (m i)) :
    (periodCopiesEquiv σ tate ρ m z x i k).val =
      copiesEquiv (R := R) (B := B) m x.val i k := rfl

set_option backward.isDefEq.respectTransparency false in
/-- Intrinsic eigenperiod dimension additivity when the constituent period
spaces are finite dimensional. Finiteness is not smuggled in via a weight label. -/
theorem period_finrank_copies
    [∀ i, FiniteDimensional R (periodSpace σ tate (ρ i) z)] :
    Module.finrank R (periodSpace σ tate (copiesRep ρ m) z) =
      ∑ i, m i * Module.finrank R (periodSpace σ tate (ρ i) z) := by
  classical
  let (i : I) : AddCommGroup (B ⊗[R] W i) := inferInstance
  let (i : I) : AddCommGroup (periodSpace σ tate (ρ i) z) := inferInstance
  rw [(periodCopiesEquiv σ tate ρ m z).finrank_eq]
  change Module.finrank R ((i : I) → Fin (m i) → periodSpace σ tate (ρ i) z) = _
  rw [Module.finrank_pi_fintype R]
  apply Finset.sum_congr rfl
  intro i _
  rw [Module.finrank_pi_fintype, Finset.sum_const, Finset.card_univ, Fintype.card_fin,
    nsmul_eq_mul]
  rfl

end PaperX.SemilinearPeriods
