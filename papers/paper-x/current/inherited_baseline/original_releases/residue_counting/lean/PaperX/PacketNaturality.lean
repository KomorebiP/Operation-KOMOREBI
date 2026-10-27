import PaperX.PacketCohomology

/-! The decomposition is compatible with maps intertwining the supplied projectors. -/
set_option autoImplicit false
namespace PaperX.PacketNaturality

open PaperX.Cohomology PaperX.PacketCohomology
open scoped BigOperators
universe u v w
variable {R : Type u} [CommRing R] {C D : Triple.{u,v} R}

/-- A cochain map preserving the projectors restricts to their actual image complexes. -/
def transport (f : ChainMap C D) (p : ChainMap C C) (q : ChainMap D D)
    (h₀ : f.left.comp p.left = q.left.comp f.left)
    (h₁ : f.middle.comp p.middle = q.middle.comp f.middle)
    (h₂ : f.right.comp p.right = q.right.comp f.right) :
    ChainMap (packet p) (packet q) where
  left := rangeMap f.left p.left q.left h₀
  middle := rangeMap f.middle p.middle q.middle h₁
  right := rangeMap f.right p.right q.right h₂
  comm₀ := by
    ext x
    apply Subtype.ext
    exact LinearMap.congr_fun f.comm₀ x.val
  comm₁ := by
    ext x
    apply Subtype.ext
    exact LinearMap.congr_fun f.comm₁ x.val

theorem projection_natural (f : ChainMap C D) (p : ChainMap C C) (q : ChainMap D D)
    (h₀ : f.left.comp p.left = q.left.comp f.left)
    (h₁ : f.middle.comp p.middle = q.middle.comp f.middle)
    (h₂ : f.right.comp p.right = q.right.comp f.right) (z : H C) :
    hmap (projection q) (hmap f z) =
      hmap (transport f p q h₀ h₁ h₂) (hmap (projection p) z) := by
  obtain ⟨x, rfl⟩ := classOf_surjective C z
  simp only [hmap_classOf]
  congr 1
  apply Subtype.ext
  apply Subtype.ext
  exact (LinearMap.congr_fun h₁ x.val).symm

/-- The square between total cohomology and all packet cohomologies commutes. -/
theorem decomposition_natural {ι : Type w} [Fintype ι]
    (P : Resolution C ι) (Q : Resolution D ι) (f : ChainMap C D)
    (h₀ : ∀ i, f.left.comp (P.projectors i).left = (Q.projectors i).left.comp f.left)
    (h₁ : ∀ i, f.middle.comp (P.projectors i).middle = (Q.projectors i).middle.comp f.middle)
    (h₂ : ∀ i, f.right.comp (P.projectors i).right = (Q.projectors i).right.comp f.right)
    (z : H C) (i : ι) :
    cohomologyPiEquiv Q (hmap f z) i =
      hmap (transport f (P.projectors i) (Q.projectors i) (h₀ i) (h₁ i) (h₂ i))
        (cohomologyPiEquiv P z i) :=
  projection_natural f _ _ (h₀ i) (h₁ i) (h₂ i) z

end PaperX.PacketNaturality
