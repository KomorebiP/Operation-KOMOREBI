import KomorebiSpace.MarkedRealization

set_option autoImplicit false

/-!
# Transport of identified-boundary groupoids

A square commuting by a specified natural isomorphism induces a functor on
identified-boundary realizations. Full faithfulness and essential surjectivity
are proved by explicitly lifting morphisms and objects; the fiber equivalence
is not an assumption. The square may be non-strict.
-/
universe u₁ u₂ u₃ u₄ v₁ v₂ v₃ v₄
namespace KomorebiSpace
open CategoryTheory
namespace MarkedRealization
variable {C : Type u₁} [Groupoid.{v₁} C]
variable {D : Type u₂} [Groupoid.{v₂} D]
variable {C' : Type u₃} [Groupoid.{v₃} C']
variable {D' : Type u₄} [Groupoid.{v₄} D']
variable {F : C ⥤ D} {F' : C' ⥤ D'}

/-- The comparison isomorphism transports the boundary along the square. -/
def transport (E : C ⥤ C') (K : D ⥤ D') (s : F ⋙ K ≅ E ⋙ F') (b : D) :
    MarkedRealization F b ⥤ MarkedRealization F' (K.obj b) where
  obj x := ⟨E.obj x.obj, s.inv.app x.obj ≫ K.map x.identify⟩
  map := fun {x y} f =>
    ⟨E.map f.val, by
      change F'.map (E.map f.val) ≫ (s.inv.app y.obj ≫ K.map y.identify) =
        s.inv.app x.obj ≫ K.map x.identify
      have hs : F'.map (E.map f.val) ≫ s.inv.app y.obj =
          s.inv.app x.obj ≫ K.map (F.map f.val) := s.inv.naturality f.val
      rw [← Category.assoc, hs, Category.assoc, ← K.map_comp, f.comm]⟩
  map_id := by intro x; apply Hom.ext; exact E.map_id x.obj
  map_comp := by intro x y z f g; apply Hom.ext; exact E.map_comp f.val g.val

@[simp] theorem transport_obj (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) (x : MarkedRealization F b) :
    ((transport E K s b).obj x).obj = E.obj x.obj := rfl

@[simp] theorem transport_identify (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) (x : MarkedRealization F b) :
    ((transport E K s b).obj x).identify = s.inv.app x.obj ≫ K.map x.identify := rfl

@[simp] theorem transport_map (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) {x y : MarkedRealization F b} (f : x ⟶ y) :
    ((transport E K s b).map f).val = E.map f.val := rfl

/-- Lift an actual fiber morphism and reflect its boundary equation. -/
noncomputable def liftHom (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.Full] [E.Faithful] [K.Faithful]
    {x y : MarkedRealization F b}
    (a : (transport E K s b).obj x ⟶ (transport E K s b).obj y) : x ⟶ y where
  val := E.preimage a.val
  comm := by
    apply K.map_injective
    apply (cancel_epi (s.inv.app x.obj)).mp
    have hs : F'.map (E.map (E.preimage a.val)) ≫ s.inv.app y.obj =
        s.inv.app x.obj ≫ K.map (F.map (E.preimage a.val)) :=
      s.inv.naturality (E.preimage a.val)
    calc
      s.inv.app x.obj ≫ K.map (F.map (E.preimage a.val) ≫ y.identify) =
          F'.map (E.map (E.preimage a.val)) ≫ (s.inv.app y.obj ≫ K.map y.identify) := by
            rw [K.map_comp, ← Category.assoc, ← hs, Category.assoc]
      _ = s.inv.app x.obj ≫ K.map x.identify := by
        rw [E.map_preimage a.val]
        exact a.comm

noncomputable def transportFullyFaithful (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.Full] [E.Faithful] [K.Faithful] :
    (transport E K s b).FullyFaithful where
  preimage := liftHom E K s b
  map_preimage := by intro x y a; apply Hom.ext; exact E.map_preimage a.val
  preimage_map := by intro x y a; apply Hom.ext; exact E.preimage_map a.val

/-- Chosen global preimage and a lifted identification, not an assumed fiber preimage. -/
noncomputable def chosenPreimage (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.EssSurj] [K.Full]
    (y : MarkedRealization F' (K.obj b)) : MarkedRealization F b where
  obj := E.objPreimage y.obj
  identify := K.preimage (s.hom.app (E.objPreimage y.obj) ≫
    F'.map (E.objObjPreimageIso y.obj).hom ≫ y.identify)

/-- Essential surjectivity includes compatibility of the chosen boundary mark. -/
noncomputable def chosenComparison (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.EssSurj] [K.Full]
    (y : MarkedRealization F' (K.obj b)) :
    (transport E K s b).obj (chosenPreimage E K s b y) ⟶ y where
  val := (E.objObjPreimageIso y.obj).hom
  comm := by
    change F'.map (E.objObjPreimageIso y.obj).hom ≫ y.identify =
      s.inv.app (E.objPreimage y.obj) ≫ K.map
        (K.preimage (s.hom.app (E.objPreimage y.obj) ≫
          F'.map (E.objObjPreimageIso y.obj).hom ≫ y.identify))
    rw [K.map_preimage]
    simp

/-- Proved essential surjectivity on the identified-boundary groupoid. -/
theorem transport_essentially_surjective (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.EssSurj] [K.Full] :
    (transport E K s b).EssSurj := by
  constructor
  intro y
  exact ⟨chosenPreimage E K s b y,
    ⟨(Groupoid.isoEquivHom _ _).symm (chosenComparison E K s b y)⟩⟩

/-- Equivalence of presentations preserves the full identified-boundary groupoid. -/
theorem transport_isEquivalence (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.IsEquivalence] [K.IsEquivalence] :
    (transport E K s b).IsEquivalence := by
  let ff := transportFullyFaithful E K s b
  let : (transport E K s b).Full := ff.full
  let : (transport E K s b).Faithful := ff.faithful
  let : (transport E K s b).EssSurj := transport_essentially_surjective E K s b
  exact {}

noncomputable def transportEquivalence (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.IsEquivalence] [K.IsEquivalence] :
    MarkedRealization F b ≌ MarkedRealization F' (K.obj b) := by
  letI := transport_isEquivalence E K s b
  exact (transport E K s b).asEquivalence

@[simp] theorem transportEquivalence_functor (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.IsEquivalence] [K.IsEquivalence] :
    (transportEquivalence E K s b).functor = transport E K s b := rfl

/-- Every boundary-preserving Hom, including automorphisms, is retained. -/
noncomputable def transportHomEquiv (E : C ⥤ C') (K : D ⥤ D')
    (s : F ⋙ K ≅ E ⋙ F') (b : D) [E.Full] [E.Faithful] [K.Faithful]
    (x y : MarkedRealization F b) :
    (x ⟶ y) ≃ ((transport E K s b).obj x ⟶ (transport E K s b).obj y) :=
  (transportFullyFaithful E K s b).homEquiv

end MarkedRealization
end KomorebiSpace
