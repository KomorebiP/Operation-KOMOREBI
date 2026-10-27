module
public import KomorebiInformation.OptimalRepair
public import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
public import Mathlib.Tactic
@[expose] public section

namespace KomorebiInformation.Linear
variable {K V O Y : Type*} [DivisionRing K]
variable [AddCommGroup V] [Module K V]
variable [AddCommGroup O] [Module K O]
variable [AddCommGroup Y] [Module K Y]

/-- Nested subtype bookkeeping for the common kernel. -/
def restrictedKernelEquiv (R : V →ₗ[K] O) (F : V →ₗ[K] Y) :
    (F.domRestrict R.ker).ker ≃ₗ[K] ↥(R.ker ⊓ F.ker) where
  toFun v := ⟨v.val.val, v.val.property, v.property⟩
  invFun v := ⟨⟨v.val, v.property.1⟩, v.property.2⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- The obstruction dimension is exactly the rank increment of the stacked map. -/
theorem obstruction_finrank_eq_rank_increment [FiniteDimensional K V]
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) :
    Module.finrank K (ObstructionSpace R F) =
      Module.finrank K (R.prod F).range - Module.finrank K R.range := by
  have h0 := (F.domRestrict R.ker).finrank_range_add_finrank_ker
  have h1 := R.finrank_range_add_finrank_ker
  have h2 := (R.prod F).finrank_range_add_finrank_ker
  rw [(restrictedKernelEquiv R F).finrank_eq] at h0
  rw [LinearMap.ker_prod] at h2
  change Module.finrank K (ObstructionSpace R F) +
    Module.finrank K ↥(R.ker ⊓ F.ker) = Module.finrank K R.ker at h0
  omega

/-- The q^d bound with d expressed in the stacked-map rank form of the paper. -/
theorem rank_increment_alphabet_lower_bound [Fintype K] [FiniteDimensional K V]
    {E : Type*} [AddCommGroup E] [Module K E]
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E)
    {Message : Type*} [Fintype Message] [Fintype (ObstructionSpace R F)]
    {h : E → Message} {g : O × Message → Y}
    (hrep : Repair R F U h g) :
    Fintype.card K ^
      (Module.finrank K (R.prod F).range - Module.finrank K R.range) ≤
      Fintype.card Message := by
  rw [← obstruction_finrank_eq_rank_increment R F]
  exact power_finrank_le_any_repair R F U hrep
end KomorebiInformation.Linear
