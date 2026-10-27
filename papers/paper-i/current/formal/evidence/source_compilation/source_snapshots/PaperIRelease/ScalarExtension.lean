import KomorebiVerification.SeedRankOperations
set_option autoImplicit false
set_option linter.unusedSectionVars false
set_option linter.unnecessarySimpa false
noncomputable section
namespace Komorebi.PaperIRelease.ScalarExtension
open Komorebi.SeedRankBasics
open scoped TensorProduct
universe u

-- Natural action construction retained from the verified tensor-operator interface.
section TensorProduct

variable (k A B X Y : Type u)
variable [CommSemiring k]
variable [Semiring A] [Algebra k A]
variable [Semiring B] [Algebra k B]
variable [AddCommMonoid X] [Module k X] [Module A X]
variable [IsScalarTower k A X] [SMulCommClass k A X]
variable [AddCommMonoid Y] [Module k Y] [Module B Y]
variable [IsScalarTower k B Y] [SMulCommClass k B Y]

/-- The action of `B` on the right tensor factor. -/
@[instance_reducible] def tensorRightModule :
    Module B (TensorProduct k X Y) := by
  let e : TensorProduct k X Y ≃ₗ[k] TensorProduct k Y X :=
    TensorProduct.comm k X Y
  letI : Module B (TensorProduct k Y X) := TensorProduct.leftModule
  exact
    { smul := fun b z ↦ e.symm (b • e z)
      one_smul := fun z ↦ by
        change e.symm ((1 : B) • e z) = z
        rw [one_smul, e.symm_apply_apply]
      mul_smul := fun b c z ↦ by
        change e.symm ((b * c) • e z) =
          e.symm (b • e (e.symm (c • e z)))
        rw [mul_smul, e.apply_symm_apply]
      smul_add := fun b z w ↦ by
        change e.symm (b • e (z + w)) =
          e.symm (b • e z) + e.symm (b • e w)
        rw [e.map_add, smul_add, e.symm.map_add]
      add_smul := fun b c z ↦ by
        change e.symm ((b + c) • e z) =
          e.symm (b • e z) + e.symm (c • e z)
        rw [add_smul, e.symm.map_add]
      zero_smul := fun z ↦ by
        change e.symm ((0 : B) • e z) = 0
        rw [zero_smul, map_zero]
      smul_zero := fun b ↦ by
        change e.symm (b • e 0) = 0
        rw [map_zero, smul_zero, map_zero] }

local instance (priority := 50) tensorRightModuleInstance :
    Module B (TensorProduct k X Y) :=
  tensorRightModule k B X Y

@[simp] theorem tensorRight_smul_tmul (b : B) (x : X) (y : Y) :
    b • (x ⊗ₜ[k] y) = x ⊗ₜ[k] (b • y) := by
  change (TensorProduct.comm k X Y).symm
      (b • (TensorProduct.comm k X Y) (x ⊗ₜ[k] y)) = _
  rw [TensorProduct.comm_tmul, TensorProduct.smul_tmul',
    TensorProduct.comm_symm_tmul]

local instance tensorRightTower :
    IsScalarTower k B (TensorProduct k X Y) where
  smul_assoc r b z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y => simp [smul_assoc]
    | add z w hz hw => simp [smul_add, hz, hw]

local instance tensorLeftTower :
    IsScalarTower k A (TensorProduct k X Y) where
  smul_assoc r a z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y => simp [TensorProduct.smul_tmul', smul_assoc]
    | add z w hz hw => simp [smul_add, hz, hw]

local instance tensorActionsCommute :
    SMulCommClass A B (TensorProduct k X Y) where
  smul_comm a b z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y => simp [TensorProduct.smul_tmul']
    | add z w hz hw => simp [smul_add, hz, hw]

attribute [local instance 2000] tensorLeftTower tensorRightTower tensorActionsCommute

local instance tensorLeftTowerInstalled :
    IsScalarTower k A (TensorProduct k X Y) :=
  tensorLeftTower k A X Y

local instance tensorRightTowerInstalled :
    IsScalarTower k B (TensorProduct k X Y) :=
  tensorRightTower k B X Y

local instance tensorActionsCommuteInstalled :
    SMulCommClass A B (TensorProduct k X Y) :=
  tensorActionsCommute k A B X Y

/-- The natural `(A ⊗[k] B)` action on `X ⊗[k] Y`. -/
local instance tensorOperatorModule :
    Module (A ⊗[k] B) (TensorProduct k X Y) :=
  TensorProduct.Algebra.module

/-- Pure operator tensors act componentwise on pure vector tensors. -/
@[simp] theorem tensorOperator_smul_tmul
    (a : A) (b : B) (x : X) (y : Y) :
    (a ⊗ₜ[k] b : A ⊗[k] B) • (x ⊗ₜ[k] y) =
      (a • x) ⊗ₜ[k] (b • y) := by
  change TensorProduct.Algebra.moduleAux (a ⊗ₜ[k] b) (x ⊗ₜ[k] y) = _
  rw [TensorProduct.Algebra.moduleAux_apply]
  simp [TensorProduct.smul_tmul']


end TensorProduct

section ScalarExtension
variable (k K A M : Type u) [Field k] [Field K] [Algebra k K]
variable [Ring A] [Algebra k A] [AddCommGroup M] [Module k M] [Module A M]
variable [IsScalarTower k A M] [SMulCommClass k A M]

local instance (priority := 2000) : Module K (K ⊗[k] M) := TensorProduct.leftModule
local instance (priority := 50) : Module A (K ⊗[k] M) := tensorRightModule k A K M
local instance : IsScalarTower k A (K ⊗[k] M) := tensorRightTower k A K M
local instance (priority := 2000) : IsScalarTower k K (K ⊗[k] M) := tensorLeftTower k K K M
local instance : SMulCommClass K A (K ⊗[k] M) := tensorActionsCommute k K A K M
local instance : Module (K ⊗[k] A) (K ⊗[k] M) := TensorProduct.Algebra.module

/-- The literal family `1 tensor S` generates after extension of scalars. -/
theorem one_tmul_generates (s : Set M) (hs : Generates A M s) :
    Generates (K ⊗[k] A) (K ⊗[k] M) ((fun m => (1 : K) ⊗ₜ[k] m) '' s) := by
  let p : Submodule (K ⊗[k] A) (K ⊗[k] M) :=
    Submodule.span (K ⊗[k] A) ((fun m => (1 : K) ⊗ₜ[k] m) '' s)
  change p = ⊤
  have hunit : ∀ m : M, (1 : K) ⊗ₜ[k] m ∈ p := by
    intro m
    have hm : m ∈ Submodule.span A s := by rw [hs]; trivial
    refine Submodule.span_induction (p := fun m _ => (1 : K) ⊗ₜ[k] m ∈ p) ?_ ?_ ?_ ?_ hm
    · intro x hx
      exact Submodule.subset_span ⟨x, hx, rfl⟩
    · simpa using p.zero_mem
    · intro x y _ _ hx hy
      simpa [TensorProduct.tmul_add] using p.add_mem hx hy
    · intro a x _ hx
      have h := p.smul_mem ((1 : K) ⊗ₜ[k] a) hx
      simpa only [tensorOperator_smul_tmul, smul_eq_mul, one_mul] using h
  apply top_unique
  intro z _
  refine TensorProduct.induction_on z p.zero_mem ?_ (fun _ _ hx hy => p.add_mem hx hy)
  intro c m
  have h := p.smul_mem (c ⊗ₜ[k] (1 : A)) (hunit m)
  simpa only [tensorOperator_smul_tmul, smul_eq_mul, mul_one, one_smul] using h

/-- Scalar extension cannot increase the cardinal seed rank. -/
theorem scalar_extension_seedRank_le :
    seedRank (K ⊗[k] A) (K ⊗[k] M) ≤ seedRank A M := by
  obtain ⟨s, hs, hc⟩ := exists_generating_set_card_eq_seedRank A M
  calc
    seedRank (K ⊗[k] A) (K ⊗[k] M) ≤ Cardinal.mk ((fun m => (1 : K) ⊗ₜ[k] m) '' s) :=
      seedRank_le_mk_of_generates _ _ (one_tmul_generates k K A M s hs)
    _ ≤ Cardinal.mk s := Cardinal.mk_image_le
    _ = seedRank A M := hc

end ScalarExtension
end Komorebi.PaperIRelease.ScalarExtension
