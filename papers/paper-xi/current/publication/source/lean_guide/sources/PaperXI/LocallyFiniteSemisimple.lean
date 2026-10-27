import Mathlib.RepresentationTheory.Maschke
import PaperXI.QuotientRepresentation

/-! Semisimplicity from finite quotient actions on local invariant subspaces.
The representation may have arbitrary dimension; the local pieces supply the
semisimple submodules whose supremum is the whole group-algebra module. -/

set_option autoImplicit false
noncomputable section

namespace PaperXI.LocallyFiniteSemisimple

open Representation
open scoped MonoidAlgebra

section LocalModules

variable {R M : Type*} [Ring R] [AddCommGroup M] [Module R M]

/-- A module covered by semisimple submodules is semisimple. -/
theorem module_of_locally_semisimple
    (h : ∀ x : M, ∃ S : Submodule R M, x ∈ S ∧ IsSemisimpleModule R S) :
    IsSemisimpleModule R M := by
  classical
  choose S hx hS using h
  apply isSemisimpleModule_of_isSemisimpleModule_submodule' hS
  apply top_unique
  intro x _
  exact (le_iSup S x) (hx x)

end LocalModules

section Representations

variable {k G Q V W : Type*} [Field k] [Group G] [Group Q]
  [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]

/-- Surjective pullback preserves semisimplicity. -/
theorem semisimple_comp_iff (q : G →* Q) (hq : Function.Surjective q)
    (σ : Representation k Q V) :
    IsSemisimpleRepresentation (σ.comp q) ↔ IsSemisimpleRepresentation σ :=
  (QuotientRepresentation.subrepresentationEquiv q hq σ).complementedLattice_iff

/-- An action factoring through a finite group is semisimple in characteristic zero. -/
theorem semisimple_finite_pullback [CharZero k] [Finite Q]
    (q : G →* Q) (hq : Function.Surjective q) (σ : Representation k Q V) :
    IsSemisimpleRepresentation (σ.comp q) := by
  have : NeZero (Nat.card Q : k) := ⟨by exact_mod_cast (Nat.card_pos (α := Q)).ne'⟩
  exact (semisimple_comp_iff q hq σ).mpr inferInstance

/-- A finite quotient by an actual subgroup of the kernel gives semisimplicity. -/
theorem semisimple_of_finite_quotient [CharZero k]
    (τ : Representation k G V) (N : Subgroup G) [N.Normal] [Finite (G ⧸ N)]
    (hN : N ≤ τ.ker) : IsSemisimpleRepresentation τ :=
  semisimple_finite_pullback (QuotientGroup.mk' N) QuotientGroup.mk_surjective
    (QuotientRepresentation.descend N τ hN)

/-- A semisimple invariant subspace gives a semisimple group-algebra submodule. -/
theorem semisimple_asSubmodule (τ : Representation k G W) (S : Subrepresentation τ)
    [IsSemisimpleRepresentation S.toRepresentation] :
    IsSemisimpleModule k[G] S.asSubmodule := by
  let : IsSemisimpleModule k[G] S.toRepresentation.asModule :=
    (isSemisimpleRepresentation_iff_isSemisimpleModule_asModule S.toRepresentation).mp
      inferInstance
  let incl : IntertwiningMap S.toRepresentation τ :=
    { toLinearMap := S.toSubmodule.subtype
      isIntertwining' := by intro g; ext v; rfl }
  let j := IntertwiningMap.equivLinearMapAsModule S.toRepresentation τ incl
  have hj : LinearMap.range j = S.asSubmodule := by
    ext x
    constructor
    · rintro ⟨y, rfl⟩
      exact y.property
    · intro hx
      exact ⟨⟨x, hx⟩, rfl⟩
  rw [← hj]
  exact IsSemisimpleModule.range j

/-- An arbitrary-dimensional representation is semisimple if each vector belongs
to a semisimple invariant subspace. -/
theorem semisimple_of_locally_semisimple (τ : Representation k G W)
    (h : ∀ w : W, ∃ S : Subrepresentation τ,
      w ∈ S ∧ IsSemisimpleRepresentation S.toRepresentation) :
    IsSemisimpleRepresentation τ := by
  apply (isSemisimpleRepresentation_iff_isSemisimpleModule_asModule τ).mpr
  apply module_of_locally_semisimple
  intro w
  obtain ⟨S, hw, hS⟩ := h w
  let : IsSemisimpleRepresentation S.toRepresentation := hS
  exact ⟨S.asSubmodule, hw, semisimple_asSubmodule τ S⟩

/-- Local finite quotient actions imply semisimplicity, without a global finite
quotient or a finite-dimensionality hypothesis. -/
theorem semisimple_of_locally_finite_quotient [CharZero k]
    (τ : Representation k G W)
    (h : ∀ w : W, ∃ S : Subrepresentation τ, w ∈ S ∧
      ∃ N : Subgroup G, N.Normal ∧ Finite (G ⧸ N) ∧ N ≤ S.toRepresentation.ker) :
    IsSemisimpleRepresentation τ := by
  apply semisimple_of_locally_semisimple τ
  intro w
  obtain ⟨S, hw, N, hN, hfin, hker⟩ := h w
  let : N.Normal := hN
  let : Finite (G ⧸ N) := hfin
  exact ⟨S, hw, semisimple_of_finite_quotient S.toRepresentation N hker⟩

end Representations

end PaperXI.LocallyFiniteSemisimple
