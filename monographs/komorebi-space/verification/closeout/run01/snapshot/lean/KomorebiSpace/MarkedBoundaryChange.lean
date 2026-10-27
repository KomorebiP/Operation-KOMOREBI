import KomorebiSpace.MarkedTransport

set_option autoImplicit false

/-!
# Replacing the boundary by an isomorphic object

The boundary is fixed as an object with specified identification, rather than
an independently frozen frame at every view. Changing its representative by
an isomorphism preserves the realization groupoid. For the identity restriction,
the identified-boundary fiber has a unique morphism between every pair of objects.
-/
universe u₁ u₂ v₁ v₂
namespace KomorebiSpace
open CategoryTheory
namespace MarkedRealization
variable {C : Type u₁} [Groupoid.{v₁} C]
variable {D : Type u₂} [Groupoid.{v₂} D]
variable {F : C ⥤ D} {b b' : D}

def changeBoundary (F : C ⥤ D) (i : b ≅ b') :
    MarkedRealization F b ⥤ MarkedRealization F b' where
  obj x := ⟨x.obj,x.identify ≫ i.hom⟩
  map f := ⟨f.val, by rw [← Category.assoc, f.comm]⟩
  map_id := by intro x; rfl
  map_comp := by intro x y z f g; rfl

@[simp] theorem changeBoundary_identify (i : b ≅ b') (x : MarkedRealization F b) :
    ((changeBoundary F i).obj x).identify = x.identify ≫ i.hom := rfl

/-- The round trip is identified by the identity of the original global object. -/
def boundaryRoundTrip (F : C ⥤ D) (i : b ≅ b') :
    changeBoundary F i ⋙ changeBoundary F i.symm ≅ 𝟭 (MarkedRealization F b) :=
  NatIso.ofComponents (fun x => (Groupoid.isoEquivHom _ _).symm
    (⟨𝟙 x.obj, by
      change F.map (𝟙 x.obj) ≫ x.identify = (x.identify ≫ i.hom) ≫ i.inv
      simp⟩ : (changeBoundary F i ⋙ changeBoundary F i.symm).obj x ⟶ x))
    (by
      intro x y a
      apply Hom.ext
      change a.val ≫ 𝟙 y.obj = 𝟙 x.obj ≫ a.val
      simp)

def boundaryEquivalence (F : C ⥤ D) (i : b ≅ b') :
    MarkedRealization F b ≌ MarkedRealization F b' :=
  CategoryTheory.Equivalence.mk (changeBoundary F i) (changeBoundary F i.symm)
    (boundaryRoundTrip F i).symm (boundaryRoundTrip F i.symm)

@[simp] theorem boundaryEquivalence_functor (i : b ≅ b') :
    (boundaryEquivalence F i).functor = changeBoundary F i := rfl

/-- A full boundary still allows different representatives, but fixes their identification. -/
def identityCenter (b : D) : MarkedRealization (𝟭 D) b := ⟨b,𝟙 b⟩

def identityFiberArrow (x y : MarkedRealization (𝟭 D) b) : x ⟶ y :=
  ⟨x.identify ≫ Groupoid.inv y.identify, by
    change (x.identify ≫ Groupoid.inv y.identify) ≫ y.identify = x.identify
    simp⟩

/-- There is no spurious ambiguity from different representatives of an entirely fixed boundary. -/
theorem identityFiberArrow_unique (x y : MarkedRealization (𝟭 D) b) (a : x ⟶ y) :
    a = identityFiberArrow x y := by
  apply Hom.ext
  apply (cancel_mono y.identify).mp
  change a.val ≫ y.identify = (x.identify ≫ Groupoid.inv y.identify) ≫ y.identify
  simpa using a.comm

/-- Nonempty identity fibers are contractible as groupoids, not singletons as object types. -/
theorem identityFiber_unique_hom (x y : MarkedRealization (𝟭 D) b) :
    ∃! _a : x ⟶ y, True := by
  refine ⟨identityFiberArrow x y, trivial, ?_⟩
  intro a ha
  exact identityFiberArrow_unique x y a

end MarkedRealization
end KomorebiSpace
