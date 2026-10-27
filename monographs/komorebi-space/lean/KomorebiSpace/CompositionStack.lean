import KomorebiSpace.StandardDescentBridge

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# The ordinary cocycle stack on the composition site

The actual patch pseudofunctor is shown to satisfy mathlib's standard
IsStack predicate. The proof translates standard overlap data to the
already checked concrete nonabelian descent construction, then retains
all morphisms through a proved inverse to standard restriction.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory Opposite Bicategory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)
namespace StandardDescent
variable {I : Type z} {W : Set V} {U : I → Set V} (hU : ∀ i, U i ⊆ W)

/-- The concrete effectuation supplies a standard local gauge comparison. -/
def localRealizationHom {D : Data F hU} (E : (toConcrete F hU D).Effectuation) (i : I) :
    (F.patchRestrict (hU i)).obj E.object ⟶ D.obj i where
  change := ⟨fun x => E.compare i ⟨⟨x.val,hU i x.property⟩,x.property⟩, by
    intro x; exact False.elim x.property⟩
  target := by
    apply Cocycle.ext
    intro x y f
    exact E.local_eq i ⟨⟨x.val,hU i x.property⟩,x.property⟩
      ⟨⟨y.val,hU i y.property⟩,y.property⟩ (InducedCategory.homMk f.hom)

@[simp] theorem localRealizationHom_value {D : Data F hU}
    (E : (toConcrete F hU D).Effectuation) (i : I) (x : PatchViews (U i)) :
    (localRealizationHom F hU E i).change.val x =
      E.compare i ⟨⟨x.val,hU i x.property⟩,x.property⟩ := rfl

/-- The local identifications respect every standard overlap pullback. -/
def realizationIso {D : Data F hU} (E : (toConcrete F hU D).Effectuation) :
    (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj E.object ≅ D := by
  refine Pseudofunctor.DescentData.isoMk
    (fun i => (Groupoid.isoEquivHom (C := (F.onPatch (U i)).GaugeObject ∅) _ _).symm (localRealizationHom F hU E i)) ?_
  intro Y q i j fi fj hfi hfj
  apply GaugeObject.Hom.ext
  apply Subtype.ext
  funext x
  dsimp only [Groupoid.isoEquivHom, Equiv.symm, Equiv.coe_fn_mk]
  change (D.hom q fi fj hfi hfj).change.val x *
    ((F.patchRestrict (leOfHom fi)).map (localRealizationHom F hU E i)).change.val x =
    ((F.patchRestrict (leOfHom fj)).map (localRealizationHom F hU E j)).change.val x *
    ((Pseudofunctor.DescentData.ofObj (F := F.patchPseudofunctor)
      (f := fun i => homOfLE (hU i)) E.object).hom q fi fj hfi hfj).change.val x
  rw [ofObj_hom_value F hU E.object q fi fj x, mul_one]
  change (D.hom q fi fj hfi hfj).change.val x *
    E.compare i ⟨⟨x.val,leOfHom q x.property⟩,leOfHom fi x.property⟩ =
    E.compare j ⟨⟨x.val,leOfHom q x.property⟩,leOfHom fj x.property⟩
  rw [hom_value F hU D q fi fj x]
  exact (E.overlap i j ⟨x.val,leOfHom q x.property⟩
    (leOfHom fi x.property) (leOfHom fj x.property)).symm

/-- Essential surjectivity in the standard library's descent category. -/
theorem essentially_surjective (h : CompositionSite.FamilyCovers W U) (D : Data F hU) :
    ∃ c : (F.onPatch W).GaugeObject ∅,
      Nonempty ((F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj c ≅ D) := by
  let E := (toConcrete F hU D).effectuate
    ((CompositionSite.familyCovers_iff_compositionCover W U).mp h)
  exact ⟨E.object, ⟨realizationIso F hU E⟩⟩

/-- Standard descent arrows yield matching gauge values on the original view patches. -/
def restrictedMatching {c d : (F.onPatch W).GaugeObject ∅}
    (b : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj c ⟶
      (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj d) :
    GaugeMatching (G := fun x : PatchViews W => G x.val) (CompositionSite.inside W U) where
  value i x := (b.hom i).change.val ⟨x.val.val,x.property⟩
  agree := by
    intro i j x hi hj
    let q := singletonInclusion x.property
    let fi := singletonInclusion (show x.val ∈ U i from hi)
    let fj := singletonInclusion (show x.val ∈ U j from hj)
    have hc := b.comm q fi fj (Subsingleton.elim _ _) (Subsingleton.elim _ _)
    have he := congrArg (fun a => a.change.val ⟨x.val,Set.mem_singleton x.val⟩) hc
    change
      ((Pseudofunctor.DescentData.ofObj (F := F.patchPseudofunctor)
        (f := fun i => homOfLE (hU i)) d).hom q fi fj (Subsingleton.elim _ _) (Subsingleton.elim _ _)).change.val ⟨x.val,Set.mem_singleton x.val⟩ *
          (b.hom i).change.val ⟨x.val,hi⟩ =
      (b.hom j).change.val ⟨x.val,hj⟩ *
        ((Pseudofunctor.DescentData.ofObj (F := F.patchPseudofunctor)
          (f := fun i => homOfLE (hU i)) c).hom q fi fj (Subsingleton.elim _ _) (Subsingleton.elim _ _)).change.val ⟨x.val,Set.mem_singleton x.val⟩ at he
    rw [ofObj_hom_value F hU d, ofObj_hom_value F hU c, one_mul, mul_one] at he
    exact he

/-- The standard local morphisms satisfy the earlier actual gauge-descent equations. -/
def restrictedFramedDescent {c d : (F.onPatch W).GaugeObject ∅}
    (b : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj c ⟶
      (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj d) :
    GaugeMatching.FramedDescent (F.onPatch W) (CompositionSite.inside W U) ∅ c d where
  matching := restrictedMatching F hU b
  relates := by
    intro i x y f
    exact congrArg (fun z => z.edge
      (a := (⟨x.val.val,x.property⟩ : PatchViews (U i)))
      (b := (⟨y.val.val,y.property⟩ : PatchViews (U i)))
      (InducedCategory.homMk f.hom)) (b.hom i).target
  based := by intro i x hi hx; exact False.elim hx

/-- Lift a standard descent arrow to a genuine global gauge. -/
noncomputable def liftHom (h : CompositionSite.FamilyCovers W U)
    {c d : (F.onPatch W).GaugeObject ∅}
    (b : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj c ⟶
      (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj d) : c ⟶ d :=
  (restrictedFramedDescent F hU b).glueHom
    ((CompositionSite.familyCovers_iff_compositionCover W U).mp h).transitionCover

@[simp] theorem liftHom_local (h : CompositionSite.FamilyCovers W U)
    {c d : (F.onPatch W).GaugeObject ∅}
    (b : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj c ⟶
      (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj d)
    (i : I) (x : PatchViews (U i)) :
    (liftHom F hU h b).change.val ⟨x.val,hU i x.property⟩ =
      (b.hom i).change.val x :=
  (restrictedFramedDescent F hU b).glueHom_local
    ((CompositionSite.familyCovers_iff_compositionCover W U).mp h).transitionCover
    i ⟨x.val,hU i x.property⟩ x.property

/-- Standard restriction loses no global gauge on a composition cover. -/
theorem restriction_injective (h : CompositionSite.FamilyCovers W U)
    {c d : (F.onPatch W).GaugeObject ∅} (a b : c ⟶ d)
    (he : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).map a =
      (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).map b) : a = b := by
  apply GaugeObject.Hom.ext
  apply Subtype.ext
  funext x
  obtain ⟨i,hi⟩ := CompositionSite.covers_objects h x.property
  exact congrArg (fun z => (z.hom i).change.val ⟨x.val,hi⟩) he

@[simp] theorem restrict_liftHom (h : CompositionSite.FamilyCovers W U)
    {c d : (F.onPatch W).GaugeObject ∅}
    (b : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj c ⟶
      (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).obj d) :
    (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).map
      (liftHom F hU h b) = b := by
  apply Pseudofunctor.DescentData.hom_ext
  intro i
  apply GaugeObject.Hom.ext
  apply Subtype.ext
  funext x
  exact liftHom_local F hU h b i x

@[simp] theorem liftHom_restrict (h : CompositionSite.FamilyCovers W U)
    {c d : (F.onPatch W).GaugeObject ∅} (a : c ⟶ d) :
    liftHom F hU h
      ((F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).map a) = a := by
  apply restriction_injective F hU h
  exact restrict_liftHom F hU h _

/-- An explicit inverse on the Hom sets of the standard descent functor. -/
noncomputable def fullyFaithful (h : CompositionSite.FamilyCovers W U) :
    (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).FullyFaithful where
  preimage := liftHom F hU h
  map_preimage := restrict_liftHom F hU h
  preimage_map := liftHom_restrict F hU h

/-- Effective descent is now an equivalence for the actual mathlib descent interface. -/
theorem restriction_isEquivalence (h : CompositionSite.FamilyCovers W U) :
    (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).IsEquivalence := by
  let ff := fullyFaithful F hU h
  let : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).Full := ff.full
  let : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).Faithful := ff.faithful
  let : (F.patchPseudofunctor.toDescentData (fun i => homOfLE (hU i))).EssSurj :=
    ⟨essentially_surjective F hU h⟩
  exact {}

end StandardDescent

/-- The cocycle pseudofunctor is an ordinary stack for the actual composition topology. -/
theorem patch_isStack : F.patchPseudofunctor.IsStack (CompositionSite.topology V) := by
  apply Pseudofunctor.IsStack.of_isStackFor
  intro W s hs
  rw [Pseudofunctor.isStackFor_iff]
  let U : s.arrows.category → Set V := fun t => t.obj.left
  let hU : ∀ t, U t ⊆ W := fun t => leOfHom t.obj.hom
  have hc : CompositionSite.FamilyCovers W U := by
    intro q hq
    let t : s.arrows.category := s.arrows.categoryMk (homOfLE hq) (hs q hq)
    exact ⟨t, Set.Subset.refl q.support⟩
  exact StandardDescent.restriction_isEquivalence F hU hc

end GroupViewSystem
end KomorebiSpace
