import KomorebiSpace.MarkedTransport
import KomorebiSpace.PatchViewEquivalence

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Presentation-independent relative cocycle realizations

The boundary object belongs to the existing unframed patch groupoid. A global
realization includes an isomorphism from its actual restricted cocycle to that
boundary. The proved square of patch pullbacks supplies a concrete comparison
of these groupoids under equivalent views and saturated domains.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem W G)

/-- Actual relative reconstruction fiber, retaining the chosen boundary identification. -/
abbrev RelativeRealization {U T : Set W} (h : U ⊆ T)
    (b : (F.onPatch U).GaugeObject ∅) := MarkedRealization (F.patchRestrict h) b

/-- Restriction and actual view pullback form the square used in fiber transport. -/
def relativeSquare (H : V ⥤ W) {U T : Set W} (h : U ⊆ T) :
    F.patchRestrict h ⋙ F.patchPullback H U ≅
      F.patchPullback H T ⋙ (F.reindex H).patchRestrict (Set.preimage_mono h) :=
  Iso.refl _

/-- The direct functor keeps the actual pulled-back cocycle and boundary arrow. -/
def relativePullback (H : V ⥤ W) {U T : Set W} (h : U ⊆ T)
    (b : (F.onPatch U).GaugeObject ∅) :
    F.RelativeRealization h b ⥤
      (F.reindex H).RelativeRealization (Set.preimage_mono h)
        ((F.patchPullback H U).obj b) :=
  MarkedRealization.transport (F.patchPullback H T) (F.patchPullback H U)
    (F.relativeSquare H h) b

@[simp] theorem relativePullback_object (H : V ⥤ W) {U T : Set W} (h : U ⊆ T)
    (b : (F.onPatch U).GaugeObject ∅) (x : F.RelativeRealization h b) :
    ((F.relativePullback H h b).obj x).obj = (F.patchPullback H T).obj x.obj := rfl

@[simp] theorem relativePullback_identification (H : V ⥤ W) {U T : Set W} (h : U ⊆ T)
    (b : (F.onPatch U).GaugeObject ∅) (x : F.RelativeRealization h b) :
    ((F.relativePullback H h b).obj x).identify =
      (F.patchPullback H U).map x.identify := by
  change 𝟙 _ ≫ (F.patchPullback H U).map x.identify = _
  exact Category.id_comp _

/-- Both presentations of the same relative reconstruction problem are equivalent. -/
noncomputable def relativeCocycleEquivalence (e : V ≌ W) {U T : Set W}
    (h : U ⊆ T) (hU : CompositionSite.IsoClosed U) (hT : CompositionSite.IsoClosed T)
    (b : (F.onPatch U).GaugeObject ∅) :
    F.RelativeRealization h b ≌
      (F.reindex e.functor).RelativeRealization (Set.preimage_mono h)
        ((F.patchPullback e.functor U).obj b) := by
  letI : (F.patchPullback e.functor T).IsEquivalence := by
    change (F.saturatedPatchCocycleEquivalence e T hT).functor.IsEquivalence
    infer_instance
  letI : (F.patchPullback e.functor U).IsEquivalence := by
    change (F.saturatedPatchCocycleEquivalence e U hU).functor.IsEquivalence
    infer_instance
  exact MarkedRealization.transportEquivalence
    (F.patchPullback e.functor T) (F.patchPullback e.functor U)
    (F.relativeSquare e.functor h) b

@[simp] theorem relativeCocycleEquivalence_functor (e : V ≌ W) {U T : Set W}
    (h : U ⊆ T) (hU : CompositionSite.IsoClosed U) (hT : CompositionSite.IsoClosed T)
    (b : (F.onPatch U).GaugeObject ∅) :
    (F.relativeCocycleEquivalence e h hU hT b).functor =
      F.relativePullback e.functor h b := rfl

/-- Empty and nonempty relative realization groupoids are distinguished invariantly. -/
theorem relative_cocycle_nonempty_iff (e : V ≌ W) {U T : Set W}
    (h : U ⊆ T) (hU : CompositionSite.IsoClosed U) (hT : CompositionSite.IsoClosed T)
    (b : (F.onPatch U).GaugeObject ∅) :
    Nonempty (F.RelativeRealization h b) ↔
      Nonempty ((F.reindex e.functor).RelativeRealization (Set.preimage_mono h)
        ((F.patchPullback e.functor U).obj b)) := by
  let q := F.relativeCocycleEquivalence e h hU hT b
  exact ⟨fun ⟨x⟩ => ⟨q.functor.obj x⟩, fun ⟨x⟩ => ⟨q.inverse.obj x⟩⟩

/-- Boundary-preserving comparisons and automorphisms are transported, not quotiented away. -/
noncomputable def relativeCocycleHomEquiv (e : V ≌ W) {U T : Set W}
    (h : U ⊆ T) (hU : CompositionSite.IsoClosed U) (hT : CompositionSite.IsoClosed T)
    (b : (F.onPatch U).GaugeObject ∅) (x y : F.RelativeRealization h b) :
    (x ⟶ y) ≃
      ((F.relativePullback e.functor h b).obj x ⟶
        (F.relativePullback e.functor h b).obj y) :=
  (F.relativeCocycleEquivalence e h hU hT b).fullyFaithfulFunctor.homEquiv

end GroupViewSystem
end KomorebiSpace
