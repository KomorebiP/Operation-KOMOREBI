import PaperXI.DualityLinear
import PaperXI.SchurScalar

/-! Exact Hom dimensions for actual irreducible complex representations. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchurHom
open Representation
open scoped Classical
variable {G V W : Type*} [Group G]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- An equivalence transports Hom(V,W) to End(V), linearly. -/
def postcomposeEquiv (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    (e : Representation.Equiv ρ σ) :
    Representation.IntertwiningMap ρ σ ≃ₗ[ℂ] Representation.IntertwiningMap ρ ρ where
  toFun f := e.symm.toIntertwiningMap.comp f
  invFun f := e.toIntertwiningMap.comp f
  left_inv f := by ext x; exact e.toLinearEquiv.apply_symm_apply (f x)
  right_inv f := by ext x; exact e.toLinearEquiv.symm_apply_apply (f x)
  map_add' f g := by ext x; exact e.toLinearEquiv.symm.map_add (f x) (g x)
  map_smul' c f := by ext x; exact e.toLinearEquiv.symm.map_smul c (f x)

/-- The Schur zero-or-one statement uses isomorphism, not an assumed dimension. -/
theorem finrank_eq_indicator [FiniteDimensional ℂ V]
    (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ] :
    Module.finrank ℂ (Representation.IntertwiningMap ρ σ) =
      if Nonempty (Representation.Equiv ρ σ) then 1 else 0 := by
  classical
  by_cases h : Nonempty (Representation.Equiv ρ σ)
  · rw [ite_eq_left h]
    obtain ⟨e⟩ := h
    rw [(postcomposeEquiv ρ σ e).finrank_eq]
    exact Representation.IsIrreducible.finrank_intertwiningMap_self ρ
  · let : IsEmpty (Representation.Equiv ρ σ) := ⟨fun e => h ⟨e⟩⟩
    rw [ite_eq_right h]
    exact Module.finrank_zero_of_subsingleton

theorem finrank_zero_or_one [FiniteDimensional ℂ V]
    (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ] :
    Module.finrank ℂ (Representation.IntertwiningMap ρ σ) = 0 ∨
      Module.finrank ℂ (Representation.IntertwiningMap ρ σ) = 1 := by
  classical
  rw [finrank_eq_indicator ρ σ]
  split_ifs <;> simp

theorem finrank_one_iff_equiv [FiniteDimensional ℂ V]
    (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ] :
    Module.finrank ℂ (Representation.IntertwiningMap ρ σ) = 1 ↔
      Nonempty (Representation.Equiv ρ σ) := by
  classical
  rw [finrank_eq_indicator ρ σ]
  split_ifs <;> simp_all

/-- There cannot be two independent invariant tensors for irreducible inputs. -/
theorem tensor_invariants_zero_or_one [FiniteDimensional ℂ V] [FiniteDimensional ℂ W]
    (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ] :
    Module.finrank ℂ (ρ.tprod σ).invariants = 0 ∨
      Module.finrank ℂ (ρ.tprod σ).invariants = 1 := by
  let : Representation.IsIrreducible ρ.dual := PaperXI.DualityLinear.dual_irreducible ρ
  rw [← PaperXI.DualityLinear.hom_finrank_eq_tensor_invariants ρ σ]
  exact finrank_zero_or_one ρ.dual σ

end PaperXI.SchurHom
