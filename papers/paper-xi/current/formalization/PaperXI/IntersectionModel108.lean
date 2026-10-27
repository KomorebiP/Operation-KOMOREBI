import PaperXI.IntertwiningSpace107
import PaperXI.QuotientRepresentation
import PaperXI.CharacterPairing108

/-! The literal conjugate-intersection operator space and its exact finite
quotient model. No identification of distinct Hom spaces is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.IntersectionModel108
open Representation IntertwiningAlong105
variable {k K G W U Q : Type*} [Field k] [Group K] [Group G] [Group Q]
  [AddCommGroup W] [Module k W] [AddCommGroup U] [Module k U]

/-- Both original elements are retained; this also works before injectivity of
`ι` is known. -/
def pairs (ι : K →* G) (g : G) : Subgroup (K × K) :=
  (ι.comp (MonoidHom.snd K K)).eqLocus
    ((MulAut.conj g).toMonoidHom.comp (ι.comp (MonoidHom.fst K K)))

def left (ι : K →* G) (g : G) : pairs ι g →* K :=
  (MonoidHom.fst K K).comp (pairs ι g).subtype

def right (ι : K →* G) (g : G) : pairs ι g →* K :=
  (MonoidHom.snd K K).comp (pairs ι g).subtype

/-- Identity on underlying linear maps. -/
def spaceEquiv (ι : K →* G) (ρ : Representation k K W) (g : G) :
    IntertwiningSpace107.space ι ρ g ≃ₗ[k]
      IntertwiningMap (ρ.comp (left ι g)) (ρ.comp (right ι g)) where
  toFun T := (T : W →ₗ[k] W).intertwiningMap_of_isIntertwiningMap _ _
    (fun x w => T.property x.val.1 x.val.2 x.property w)
  invFun T := ⟨T.toLinearMap, fun x y hxy w => IntertwiningMap.isIntertwining _ _ T ⟨(x, y), hxy⟩ w⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- Surjective pullback is a linear equivalence of actual intertwining maps. -/
def pullbackEquiv (q : K →* Q) (hq : Function.Surjective q)
    (ρ : Representation k Q W) (σ : Representation k Q U) :
    IntertwiningMap ρ σ ≃ₗ[k] IntertwiningMap (ρ.comp q) (σ.comp q) where
  toFun T := T.toLinearMap.intertwiningMap_of_isIntertwiningMap _ _
    (fun x w => IntertwiningMap.isIntertwining _ _ T (q x) w)
  invFun T := T.toLinearMap.intertwiningMap_of_isIntertwiningMap _ _
    ((QuotientRepresentation.intertwines_comp_iff q hq ρ σ T.toLinearMap).mp
      (fun x w => IntertwiningMap.isIntertwining _ _ T x w))
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- A specified finite quotient must identify both actions pointwise. -/
theorem finrank_model (ι : K →* G) (ρ : Representation k K W) (g : G)
    (q : pairs ι g →* Q) (hq : Function.Surjective q)
    (ρ₁ ρ₂ : Representation k Q W)
    (h₁ : ρ₁.comp q = ρ.comp (left ι g)) (h₂ : ρ₂.comp q = ρ.comp (right ι g)) :
    Module.finrank k (IntertwiningSpace107.space ι ρ g) =
      Module.finrank k (IntertwiningMap ρ₁ ρ₂) := by
  rw [(spaceEquiv ι ρ g).finrank_eq, ← h₁, ← h₂]
  exact (pullbackEquiv q hq ρ₁ ρ₂).finrank_eq.symm

end PaperXI.IntersectionModel108
