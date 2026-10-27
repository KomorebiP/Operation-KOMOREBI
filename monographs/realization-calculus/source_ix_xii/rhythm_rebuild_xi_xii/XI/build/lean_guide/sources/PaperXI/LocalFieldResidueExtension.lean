import PaperXI.FiniteFreeCompletion
import Mathlib.FieldTheory.Finite.Extension
import Mathlib.NumberTheory.LocalField.Basic

/-! Specialization at the actual ring of integers of a nonarchimedean local field.
The output ring, its residue and degree are constructed for every positive degree.
Absolute Weil groups and their smooth induction remain separate attachments. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LocalFieldResidueExtension
open IsLocalRing ValuativeRel
variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s] [FiniteDimensional 𝓀[K] s]

abbrev ring := ResidueExtensionRealization.ring 𝒪[K] s
abbrev field := ResidueExtensionRealization.field 𝒪[K] s

instance baseAlgebra : Algebra K (field K s) :=
  (IsFractionRing.lift (K := K) (FaithfulSMul.algebraMap_injective 𝒪[K] (field K s))).toAlgebra

instance baseTower : IsScalarTower 𝒪[K] K (field K s) :=
  .of_algebraMap_eq fun x =>
    (IsFractionRing.lift_algebraMap
      (K := K) (FaithfulSMul.algebraMap_injective 𝒪[K] (field K s)) x).symm

omit [IsUniformAddGroup K] in
theorem degree : Module.finrank K (field K s) = Module.finrank 𝓀[K] s := by
  rw [IsFractionRing.finrank_eq 𝒪[K] K (ring K s) (field K s)]
  exact ResidueExtensionRealization.rank 𝒪[K] s

instance finiteExtension : FiniteDimensional K (field K s) :=
  .of_finrank_pos ((degree K s).symm ▸ Module.finrank_pos)

theorem source :
    Module.Finite 𝒪[K] (ring K s) ∧
    IsDiscreteValuationRing (ring K s) ∧
    Algebra.Etale 𝒪[K] (ring K s) ∧
    IsAdicComplete (maximalIdeal (ring K s)) (ring K s) ∧
    Nonempty (ResidueField (ring K s) ≃ₐ[𝓀[K]] s) ∧
    Module.finrank K (field K s) = Module.finrank 𝓀[K] s ∧
    (maximalIdeal (ring K s)).ramificationIdx 𝒪[K] = 1 :=
  ⟨inferInstance, inferInstance, ResidueExtensionRealization.etale 𝒪[K] s,
    CompleteResidueRealization.complete 𝒪[K] s,
    ⟨ResidueExtensionRealization.residueEquiv 𝒪[K] s⟩,
    degree K s, ResidueExtensionRealization.ramificationIdx_one 𝒪[K] s⟩

variable (p n : ℕ) [Fact p.Prime] [CharP 𝓀[K] p] [NeZero n]

abbrev residueExtension := FiniteField.Extension 𝓀[K] p n

theorem every_positive_degree :
    Module.finrank K (field K (residueExtension K p n)) = n ∧
    Algebra.Etale 𝒪[K] (ring K (residueExtension K p n)) ∧
    IsAdicComplete (maximalIdeal (ring K (residueExtension K p n)))
      (ring K (residueExtension K p n)) ∧
    (maximalIdeal (ring K (residueExtension K p n))).ramificationIdx 𝒪[K] = 1 := by
  exact ⟨(degree K _).trans (FiniteField.finrank_extension 𝓀[K] p n),
    ResidueExtensionRealization.etale 𝒪[K] _,
    CompleteResidueRealization.complete 𝒪[K] _,
    ResidueExtensionRealization.ramificationIdx_one 𝒪[K] _⟩

end PaperXI.LocalFieldResidueExtension
