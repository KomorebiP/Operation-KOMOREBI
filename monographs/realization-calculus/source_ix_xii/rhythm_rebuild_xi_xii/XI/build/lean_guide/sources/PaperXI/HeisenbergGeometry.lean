import Mathlib.LinearAlgebra.BilinearForm.Orthogonal
import Mathlib.FieldTheory.Finiteness
import Mathlib.Tactic

/-!
# Maximal isotropic subspaces

Maximality is by inclusion among subspaces on which the alternating form vanishes.
The equality with the orthogonal complement is derived from that hypothesis.
-/

set_option autoImplicit false

namespace PaperXI.HeisenbergGeometry

open Module

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- A subspace on which the form vanishes identically. -/
def IsIsotropic (B : LinearMap.BilinForm K V) (L : Submodule K V) : Prop :=
  ∀ u ∈ L, ∀ v ∈ L, B u v = 0

/-- Maximality among isotropic subspaces, ordered by inclusion. -/
def IsMaximalIsotropic (B : LinearMap.BilinForm K V) (L : Submodule K V) : Prop :=
  IsIsotropic B L ∧ ∀ M : Submodule K V, IsIsotropic B M → L ≤ M → M = L

theorem isotropic_iff_le_orthogonal (B : LinearMap.BilinForm K V)
    (L : Submodule K V) : IsIsotropic B L ↔ L ≤ B.orthogonal L := by
  constructor
  · intro h v hv u hu
    exact h u hu v hv
  · intro h u hu v hv
    exact h hv u hu

/-- Adjoining an orthogonal vector preserves isotropy for an alternating form. -/
theorem isotropic_sup_span (B : LinearMap.BilinForm K V) (hB : B.IsAlt)
    (L : Submodule K V) (hL : IsIsotropic B L) (x : V)
    (hx : x ∈ B.orthogonal L) : IsIsotropic B (L ⊔ K ∙ x) := by
  intro u hu v hv
  obtain ⟨l, hl, z, hz, rfl⟩ := Submodule.mem_sup.mp hu
  obtain ⟨a, rfl⟩ := Submodule.mem_span_singleton.mp hz
  obtain ⟨m, hm, w, hw, rfl⟩ := Submodule.mem_sup.mp hv
  obtain ⟨c, rfl⟩ := Submodule.mem_span_singleton.mp hw
  have hxl : B x m = 0 := hB.isRefl _ _ (hx m hm)
  simp [map_add, map_smul, LinearMap.add_apply, LinearMap.smul_apply,
    hL l hl m hm, hx l hl, hxl, hB x]

/-- Maximality supplies the reverse inclusion in the orthogonal complement. -/
theorem orthogonal_eq (B : LinearMap.BilinForm K V) (hB : B.IsAlt)
    (L : Submodule K V) (hL : IsMaximalIsotropic B L) : B.orthogonal L = L := by
  apply le_antisymm
  · intro x hx
    have hsup := hL.2 (L ⊔ K ∙ x) (isotropic_sup_span B hB L hL.1 x hx) le_sup_left
    rw [← hsup]
    exact (show K ∙ x ≤ L ⊔ K ∙ x from le_sup_right)
      (Submodule.mem_span_singleton_self x)
  · exact (isotropic_iff_le_orthogonal B L).mp hL.1

theorem maximal_iff_orthogonal_eq (B : LinearMap.BilinForm K V) (hB : B.IsAlt)
    (L : Submodule K V) : IsMaximalIsotropic B L ↔ B.orthogonal L = L := by
  refine ⟨orthogonal_eq B hB L, fun h => ?_⟩
  refine ⟨(isotropic_iff_le_orthogonal B L).mpr h.ge, ?_⟩
  intro M hM hLM
  apply le_antisymm _ hLM
  calc
    M ≤ B.orthogonal M := (isotropic_iff_le_orthogonal B M).mp hM
    _ ≤ B.orthogonal L := LinearMap.BilinForm.orthogonal_le hLM
    _ = L := h

/-- Every maximal isotropic subspace has half the dimension of a nondegenerate space. -/
theorem two_mul_finrank [FiniteDimensional K V]
    (B : LinearMap.BilinForm K V) (hB : B.IsAlt) (hnd : B.Nondegenerate)
    (L : Submodule K V) (hL : IsMaximalIsotropic B L) :
    2 * finrank K L = finrank K V := by
  have h := LinearMap.BilinForm.finrank_add_finrank_orthogonal hB.isRefl L
  rw [orthogonal_eq B hB L hL,
    LinearMap.BilinForm.orthogonal_top_eq_bot hnd, inf_bot_eq,
    finrank_bot, add_zero] at h
  omega

end PaperXI.HeisenbergGeometry
