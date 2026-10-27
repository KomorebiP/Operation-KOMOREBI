import Mathlib.RepresentationTheory.Semisimple
import PaperXI.RepresentationStability

/-! A multiplicity-one summand of a semisimple representation is preserved by
every invariant subspace.  The splitting used here is obtained from semisimplicity,
not imposed as an additional assumption on the invariant subspace. -/

set_option autoImplicit false
noncomputable section

namespace PaperXI.SemisimpleProjection

section Modules

variable {R M N : Type*} [Ring R] [AddCommGroup M] [Module R M]
  [AddCommGroup N] [Module R N] [IsSemisimpleModule R M] [IsSimpleModule R N]

/-- A submodule meeting a simple quotient nontrivially contains its unique section. -/
theorem module_range_le_of_nonzero
    (i : N →ₗ[R] M) (p : M →ₗ[R] N) (hi : ∀ x, p (i x) = x)
    (hno : ∀ f : N →ₗ[R] M, (∀ x, p (f x) = 0) → f = 0)
    (S : Submodule R M) (hS : ∃ x ∈ S, p x ≠ 0) :
    LinearMap.range i ≤ S := by
  let q : S →ₗ[R] N := p.comp S.subtype
  have hq : q ≠ 0 := by
    rintro heq
    obtain ⟨x, hx, hpx⟩ := hS
    exact hpx (LinearMap.congr_fun heq ⟨x, hx⟩)
  obtain ⟨s, hs⟩ := IsSemisimpleModule.lifting_property q
    (LinearMap.surjective_of_ne_zero hq) (LinearMap.id : N →ₗ[R] N)
  have hsi : S.subtype.comp s = i := by
    apply sub_eq_zero.mp
    apply hno
    intro x
    change p ((s x : M) - i x) = 0
    rw [map_sub, hi]
    exact sub_eq_zero.mpr (LinearMap.congr_fun hs x)
  rintro x ⟨y, rfl⟩
  rw [← hsi]
  exact (s y).property

/-- The associated projection preserves every submodule. -/
theorem module_projection_mem
    (i : N →ₗ[R] M) (p : M →ₗ[R] N) (hi : ∀ x, p (i x) = x)
    (hno : ∀ f : N →ₗ[R] M, (∀ x, p (f x) = 0) → f = 0)
    (S : Submodule R M) {x : M} (hx : x ∈ S) : i (p x) ∈ S := by
  by_cases hpx : p x = 0
  · simp [hpx]
  · exact module_range_le_of_nonzero i p hi hno S ⟨x, hx, hpx⟩ ⟨p x, rfl⟩

end Modules

section Representations

open Representation
open scoped MonoidAlgebra

variable {k G V W : Type*} [Field k] [Group G]
  [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]
  (σ : Representation k G V) (τ : Representation k G W)
  [IsIrreducible σ] [IsSemisimpleRepresentation τ]

/-- For a semisimple representation, a stable subspace whose projection to a
simple summand is nonzero contains that summand, provided the complementary
kernel has no copy of the simple representation. -/
theorem range_le_of_nonzero
    (i : IntertwiningMap σ τ) (p : IntertwiningMap τ σ)
    (hi : ∀ v, p (i v) = v)
    (hno : ∀ f : IntertwiningMap σ τ, (∀ v, p (f v) = 0) → f = 0)
    (S : Submodule k W) (hS : RepresentationStability.Stable τ S)
    (hne : ∃ w ∈ S, p w ≠ 0) : LinearMap.range i.toLinearMap ≤ S := by
  let : IsSemisimpleModule k[G] τ.asModule :=
    (isSemisimpleRepresentation_iff_isSemisimpleModule_asModule τ).mp inferInstance
  let T : Subrepresentation τ := ⟨S, hS⟩
  let im := IntertwiningMap.equivLinearMapAsModule σ τ i
  let pm := IntertwiningMap.equivLinearMapAsModule τ σ p
  have hn : ∀ f : σ.asModule →ₗ[k[G]] τ.asModule,
      (∀ v, pm (f v) = 0) → f = 0 := by
    intro f hf
    have hh := hno ((IntertwiningMap.equivLinearMapAsModule σ τ).symm f) hf
    exact (IntertwiningMap.equivLinearMapAsModule σ τ).symm.injective
      (by simpa using hh)
  exact module_range_le_of_nonzero im pm hi hn T.asSubmodule hne

/-- The canonical projection onto the unique simple summand preserves each
stable subspace of the semisimple representation. -/
theorem projection_mem
    (i : IntertwiningMap σ τ) (p : IntertwiningMap τ σ)
    (hi : ∀ v, p (i v) = v)
    (hno : ∀ f : IntertwiningMap σ τ, (∀ v, p (f v) = 0) → f = 0)
    (S : Submodule k W) (hS : RepresentationStability.Stable τ S)
    {w : W} (hw : w ∈ S) : i (p w) ∈ S := by
  by_cases hpw : p w = 0
  · simp [hpw]
  · exact range_le_of_nonzero σ τ i p hi hno S hS ⟨w, hw, hpw⟩ ⟨p w, rfl⟩

end Representations

end PaperXI.SemisimpleProjection
