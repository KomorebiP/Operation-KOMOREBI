import PaperXI.IntersectionModel108
import Mathlib.GroupTheory.Index

/-! The pair group is identified with the first-coordinate intersection.
The orientation is literal: `ι b = g * ι a * g⁻¹`. The intersection in `K`
therefore contains the `a` whose conjugated image remains in `ι(K)`.
All results are generic group and index results; no arithmetic identity is assumed. -/

set_option autoImplicit false
noncomputable section

namespace PaperXI.PairIndex110

open IntersectionModel108

variable {K G : Type*} [Group K] [Group G]

/-- The original element is the first coordinate of the pair model. -/
def intersection (ι : K →* G) (g : G) : Subgroup K :=
  ι.range.comap ((MulAut.conj g).toMonoidHom.comp ι)

/-- Both the first coordinate and its conjugated image lie in the scalar subgroup. -/
def scalarIntersection (ι : K →* G) (H : Subgroup K) (g : G) : Subgroup K :=
  H ⊓ (H.map ι).comap ((MulAut.conj g).toMonoidHom.comp ι)

theorem scalarIntersection_le (ι : K →* G) (H : Subgroup K) (g : G) :
    scalarIntersection ι H g ≤ H := inf_le_left

theorem scalarIntersection_le_intersection (ι : K →* G) (H : Subgroup K) (g : G) :
    scalarIntersection ι H g ≤ intersection ι g := by
  intro a ha
  exact (H.map_le_range ι) ha.2

/-- The ambient intersection has the same first-coordinate orientation. -/
theorem intersection_image (ι : K →* G) (g : G) :
    (intersection ι g).map ι =
      ι.range ⊓ ι.range.comap (MulAut.conj g).toMonoidHom := by
  ext x
  constructor
  · rintro ⟨a, ha, rfl⟩
    exact ⟨⟨a, rfl⟩, ha⟩
  · intro hx
    rcases hx.1 with ⟨a, rfl⟩
    exact ⟨a, hx.2, rfl⟩

/-- The two scalar membership conditions commute with embedding into `G`. -/
theorem scalarIntersection_image (ι : K →* G) (H : Subgroup K) (g : G) :
    (scalarIntersection ι H g).map ι =
      H.map ι ⊓ (H.map ι).comap (MulAut.conj g).toMonoidHom := by
  ext x
  constructor
  · rintro ⟨a, ha, rfl⟩
    exact ⟨⟨a, ha.1, rfl⟩, ha.2⟩
  · intro hx
    rcases hx.1 with ⟨a, ha, rfl⟩
    exact ⟨a, ⟨ha, hx.2⟩, rfl⟩

theorem left_mem_intersection (ι : K →* G) (g : G) (x : pairs ι g) :
    left ι g x ∈ intersection ι g := by
  exact ⟨x.val.2, x.property⟩

theorem left_range (ι : K →* G) (g : G) :
    (left ι g).range = intersection ι g := by
  apply le_antisymm
  · rintro a ⟨x, rfl⟩
    exact left_mem_intersection ι g x
  · intro a ha
    rcases ha with ⟨b, hb⟩
    exact ⟨⟨(a, b), hb⟩, rfl⟩

theorem left_injective (ι : K →* G) (g : G) (hι : Function.Injective ι) :
    Function.Injective (left ι g) := by
  intro x y hxy
  apply Subtype.ext
  apply Prod.ext
  · exact hxy
  · apply hι
    exact x.property.trans ((congrArg ((MulAut.conj g).toMonoidHom ∘ ι) hxy).trans
      y.property.symm)

/-- The formal group equivalence retaining the first-coordinate orientation. -/
def pairEquivIntersection (ι : K →* G) (g : G) (hι : Function.Injective ι) :
    pairs ι g ≃* intersection ι g :=
  MulEquiv.ofBijective
    ((left ι g).codRestrict (intersection ι g) (left_mem_intersection ι g))
    ⟨fun x y hxy => left_injective ι g hι (congrArg Subtype.val hxy),
      fun a => by
        rcases a.property with ⟨b, hb⟩
        exact ⟨⟨(a.val, b), hb⟩, rfl⟩⟩

theorem pairSupport_eq_comap (ι : K →* G) (H : Subgroup K) (g : G)
    (hι : Function.Injective ι) :
    H.comap (left ι g) ⊓ H.comap (right ι g) =
      (scalarIntersection ι H g).comap (left ι g) := by
  ext x
  constructor
  · intro hx
    exact ⟨hx.1, ⟨right ι g x, hx.2, x.property⟩⟩
  · intro hx
    rcases hx.2 with ⟨b, hb, he⟩
    have hbr : b = right ι g x := hι (he.trans x.property.symm)
    exact ⟨hx.1, show right ι g x ∈ H from hbr ▸ hb⟩

/-- The exact transport from the pair-support index to `[I:C]`.
It also holds when one of the indices is infinite (represented by zero). -/
theorem pairSupport_index (ι : K →* G) (H : Subgroup K) (g : G)
    (hι : Function.Injective ι) :
    (H.comap (left ι g) ⊓ H.comap (right ι g)).index =
      (scalarIntersection ι H g).relIndex (intersection ι g) := by
  rw [pairSupport_eq_comap ι H g hι, Subgroup.index_comap, left_range]

/-- The same index may be expressed in the literal ambient intersections. -/
theorem pairSupport_index_ambient (ι : K →* G) (H : Subgroup K) (g : G)
    (hι : Function.Injective ι) :
    (H.comap (left ι g) ⊓ H.comap (right ι g)).index =
      (H.map ι ⊓ (H.map ι).comap (MulAut.conj g).toMonoidHom).relIndex
        (ι.range ⊓ ι.range.comap (MulAut.conj g).toMonoidHom) := by
  rw [pairSupport_index ι H g hι, ← scalarIntersection_image,
    ← intersection_image]
  exact (Subgroup.relIndex_map_map_of_injective _ _ hι).symm

end PaperXI.PairIndex110
