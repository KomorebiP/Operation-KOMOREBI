import PaperXI.RepresentationStability
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.RingTheory.Finiteness.Basic

/-! Finite dimension is derived from the actual finite group action.
The generic input is the cyclicity of a nonzero simple module, not a
semisimple decomposition or an assumed target dimension. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteRepresentation

variable {k : Type*} [Field k]

/-- A simple module over a finite-dimensional algebra is finite-dimensional
over the ground field, by the actual cyclic action map. -/
theorem simple_finiteDimensional (R M : Type*) [Ring R] [Algebra k R]
    [FiniteDimensional k R] [AddCommGroup M] [Module R M] [Module k M]
    [IsScalarTower k R M] [IsSimpleModule R M] : FiniteDimensional k M := by
  let : Nontrivial M := IsSimpleModule.nontrivial R M
  obtain ⟨m, hm⟩ := exists_ne (0 : M)
  exact Module.Finite.of_surjective
    ((LinearMap.toSpanSingleton R M m).restrictScalars k)
    (IsSimpleModule.toSpanSingleton_surjective R hm)

/-- Every actual irreducible representation of a finite group has finite dimension. -/
theorem finiteDimensional {G W : Type*} [Group G] [Finite G]
    [AddCommGroup W] [Module k W]
    (ρ : Representation k G W) [Representation.IsIrreducible ρ] :
    FiniteDimensional k W := by
  let : FiniteDimensional k ρ.asModule :=
    simple_finiteDimensional (k := k) (MonoidAlgebra k G) ρ.asModule
  exact Module.Finite.equiv ρ.asModuleEquiv

/-- Such an irreducible representation has strictly positive dimension. -/
theorem finrank_pos {G W : Type*} [Group G] [Finite G]
    [AddCommGroup W] [Module k W]
    (ρ : Representation k G W) [Representation.IsIrreducible ρ] :
    0 < Module.finrank k W := by
  let : FiniteDimensional k W := finiteDimensional ρ
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space ρ
  exact Module.finrank_pos

end PaperXI.FiniteRepresentation
