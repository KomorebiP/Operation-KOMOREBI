import PaperXI.TensorIntertwining107
import Mathlib.LinearAlgebra.FiniteDimensional.Basic

/-! A linear equivalence of actual intertwining spaces on the same embedded
compact group. Identification with a smaller integral subgroup is separate. -/
set_option autoImplicit false
set_option maxHeartbeats 100000
noncomputable section
namespace PaperXI.IntertwiningSpace107
open Representation IntertwiningAlong105 TensorIntertwining107 TensorSlices107
open scoped TensorProduct
variable {k K G Q W U V : Type*} [Field k] [Group K] [Group G] [Group Q]
  [AddCommGroup W] [Module k W] [AddCommGroup U] [Module k U]
  [AddCommGroup V] [Module k V]

def space (ι : K →* G) (ρ : Representation k K V) (g : G) :
    Submodule k (V →ₗ[k] V) where
  carrier := {T | Along ι ρ g T}
  zero_mem' := by intro x y hxy v; simp
  add_mem' := by
    intro A B hA hB x y hxy v
    simp only [LinearMap.add_apply, map_add, hA x y hxy v, hB x y hxy v]
  smul_mem' := by
    intro c A hA x y hxy v
    simp only [LinearMap.smul_apply, map_smul, hA x y hxy v]

variable (ι : K →* G) (N : Subgroup K) (q : K →* Q) (hN : N ≤ q.ker)
  (κ : Representation k K W) (σ : Representation k Q U)
  (g : G) (S : W →ₗ[k] W) (hS : S ≠ 0) (hs : Along ι κ g S)
  (hline : ∀ A : W →ₗ[k] W,
    Along (ι.comp N.subtype) (κ.comp N.subtype) g A → ∃ c : k, A = c • S)

def tensorMap : space ι (σ.comp q) g →ₗ[k] space ι (κ.tprod (σ.comp q)) g where
  toFun R := ⟨TensorProduct.map S R, map_along ι q κ σ g S hs R R.property⟩
  map_add' R R' := by
    apply Subtype.ext
    exact TensorProduct.map_add_right S (R : U →ₗ[k] U) (R' : U →ₗ[k] U)
  map_smul' c R := by
    apply Subtype.ext
    exact TensorProduct.map_smul_right c S (R : U →ₗ[k] U)

/-- Literal operator spaces, with forward map R ↦ S ⊗ R. -/
def equivalence : space ι (σ.comp q) g ≃ₗ[k] space ι (κ.tprod (σ.comp q)) g :=
  LinearEquiv.ofBijective (tensorMap ι q κ σ g S hs) ⟨by
    intro R R' h
    apply Subtype.ext
    apply map_left_injective S hS
    exact congrArg Subtype.val h, by
    intro T
    obtain ⟨R, hr, hR⟩ := factor_along ι N q hN κ σ g S hS hs hline T T.property
    exact ⟨⟨R, hR⟩, Subtype.ext hr.symm⟩⟩

include hN hS hs hline in
theorem finrank_eq :
    Module.finrank k (space ι (σ.comp q) g) =
      Module.finrank k (space ι (κ.tprod (σ.comp q)) g) :=
  (equivalence ι N q hN κ σ g S hS hs hline).finrank_eq

/-- The line certificate follows from the literal dimension-one statement and
the defining centralizer-intertwining property of a beta extension. -/
theorem line_of_dimension
    (hdim : Module.finrank k (space (ι.comp N.subtype) (κ.comp N.subtype) g) = 1)
    (hκ : ExistsAt ι κ g) :
    ∃ S : W →ₗ[k] W, S ≠ 0 ∧ Along ι κ g S ∧
      ∀ A : W →ₗ[k] W,
        Along (ι.comp N.subtype) (κ.comp N.subtype) g A → ∃ c : k, A = c • S := by
  obtain ⟨S, hn, hs⟩ := hκ
  have hsr : Along (ι.comp N.subtype) (κ.comp N.subtype) g S := by
    intro x y hxy w
    exact hs x y hxy w
  let v : space (ι.comp N.subtype) (κ.comp N.subtype) g := ⟨S, hsr⟩
  have hv : v ≠ 0 := by
    intro h
    exact hn (congrArg Subtype.val h)
  refine ⟨S, hn, hs, ?_⟩
  intro A hA
  obtain ⟨c, hc⟩ := exists_smul_eq_of_finrank_eq_one hdim hv
    (⟨A, hA⟩ : space (ι.comp N.subtype) (κ.comp N.subtype) g)
  exact ⟨c, (congrArg Subtype.val hc).symm⟩

end PaperXI.IntertwiningSpace107
