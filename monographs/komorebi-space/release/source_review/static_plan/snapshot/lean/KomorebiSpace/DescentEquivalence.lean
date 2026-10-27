import KomorebiSpace.DescentDataGroupoid

set_option autoImplicit false

/-!
# An actual equivalence of the global gauge and descent-data groupoids

Restriction is fully faithful under transition coverage and essentially
surjective under composition coverage. The equivalence is between the
specified strict coefficient/cocycle groupoids. No Grothendieck topology or
arbitrary higher-stack descent is asserted.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable {I : Type z} {F : GroupViewSystem V G} {U : I → Set V}
namespace CocycleDescentData

/-- A descent arrow between two restricted global cocycles has literally matching values. -/
def restrictedMatching {c d : F.GaugeObject (∅ : Set V)}
    (b : ofGlobal (U := U) c.labels ⟶ ofGlobal d.labels) : GaugeMatching (G := G) U where
  value := b.value
  agree := by
    intro i j x hi hj
    have he := b.overlap i j x hi hj
    change b.value j ⟨x,hj⟩ * 1 = 1 * b.value i ⟨x,hi⟩ at he
    simpa only [mul_one, one_mul] using he.symm

/-- The previous morphism-descent record, instantiated with the actual local arrow. -/
def restrictedDescent {c d : F.GaugeObject (∅ : Set V)}
    (b : ofGlobal (U := U) c.labels ⟶ ofGlobal d.labels) :
    GaugeMatching.FramedDescent F U (∅ : Set V) c d where
  matching := restrictedMatching b
  relates := b.local_eq
  based := by intro i x hi hx; exact False.elim hx

noncomputable def liftRestrictedHom (h : ViewSystem.TransitionCover U)
    {c d : F.GaugeObject (∅ : Set V)}
    (b : ofGlobal (U := U) c.labels ⟶ ofGlobal d.labels) : c ⟶ d :=
  (restrictedDescent b).glueHom h

@[simp] theorem liftRestrictedHom_value (h : ViewSystem.TransitionCover U)
    {c d : F.GaugeObject (∅ : Set V)}
    (b : ofGlobal (U := U) c.labels ⟶ ofGlobal d.labels) (i : I) (x : U i) :
    (liftRestrictedHom h b).change.val x.val = b.value i x :=
  (restrictedDescent b).glueHom_local h i x.val x.property

/-- Restriction loses no arrow when the patches cover all view objects. -/
theorem restriction_injective (h : ViewSystem.ObjectCover U)
    {c d : F.GaugeObject (∅ : Set V)}
    (a b : c ⟶ d) (he : (restrictionFunctor F U).map a = (restrictionFunctor F U).map b) :
    a = b := by
  apply GaugeObject.Hom.ext
  apply Subtype.ext
  funext x
  obtain ⟨i,hi⟩ := h x
  exact congrArg (fun z : ofGlobal (U := U) c.labels ⟶ ofGlobal d.labels =>
    z.value i ⟨x,hi⟩) he

@[simp] theorem restrict_lift (h : ViewSystem.TransitionCover U)
    {c d : F.GaugeObject (∅ : Set V)}
    (b : ofGlobal (U := U) c.labels ⟶ ofGlobal d.labels) :
    (restrictionFunctor F U).map (liftRestrictedHom h b) = b := by
  apply Hom.ext
  intro i x
  exact liftRestrictedHom_value h b i x

@[simp] theorem lift_restrict (h : ViewSystem.TransitionCover U)
    {c d : F.GaugeObject (∅ : Set V)} (a : c ⟶ d) :
    liftRestrictedHom h ((restrictionFunctor F U).map a) = a := by
  apply restriction_injective (ViewSystem.TransitionCover.objectCover U h)
  exact restrict_lift h _

/-- Explicit inverse on every Hom set. -/
noncomputable def restrictionFullyFaithful (h : ViewSystem.TransitionCover U) :
    (restrictionFunctor F U).FullyFaithful where
  preimage := liftRestrictedHom h
  map_preimage := restrict_lift h
  preimage_map := lift_restrict h

/-- Morphisms, including automorphisms, are retained by descent. -/
noncomputable def restrictionHomEquiv (h : ViewSystem.TransitionCover U)
    (c d : F.GaugeObject (∅ : Set V)) :
    (c ⟶ d) ≃ ((restrictionFunctor F U).obj c ⟶ (restrictionFunctor F U).obj d) where
  toFun := (restrictionFunctor F U).map
  invFun := liftRestrictedHom h
  left_inv := lift_restrict h
  right_inv := restrict_lift h

/-- Full, faithful, and essentially surjective are all proved under the stated cover. -/
theorem restriction_isEquivalence (h : CompositionCover U) :
    (restrictionFunctor F U).IsEquivalence := by
  let ff := restrictionFullyFaithful (F := F) h.transitionCover
  let : (restrictionFunctor F U).Full := ff.full
  let : (restrictionFunctor F U).Faithful := ff.faithful
  let : (restrictionFunctor F U).EssSurj :=
    ⟨restriction_essentially_surjective h⟩
  exact {}

/-- Effective groupoid descent with genuine overlap isomorphisms. -/
noncomputable def descentEquivalence (F : GroupViewSystem V G)
    (U : I → Set V) (h : CompositionCover U) :
    F.GaugeObject (∅ : Set V) ≌ F.CocycleDescentData U := by
  letI := restriction_isEquivalence (F := F) h
  exact (restrictionFunctor F U).asEquivalence

/-- The forward functor is the explicitly defined restriction functor. -/
@[simp] theorem descentEquivalence_functor (h : CompositionCover U) :
    (descentEquivalence F U h).functor = restrictionFunctor F U := rfl

end CocycleDescentData
end GroupViewSystem
end KomorebiSpace
