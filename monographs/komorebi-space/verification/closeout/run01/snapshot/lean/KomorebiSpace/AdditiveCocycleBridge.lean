import KomorebiSpace.NonabelianExtensionFibers
import KomorebiSpace.SectionObstruction
import Mathlib.Algebra.Group.TypeTags.Hom

set_option autoImplicit false

/-!
# The additive extension obstruction is recovered by the nonabelian model

This bridge uses the actual earlier view system and section types. It compares
vanishing criteria, not the entire abelian quotient with a group on a general
nonabelian orbit set.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace AdditiveViewSystem
variable {V : Type u} [Category.{v} V]
variable {A : V → Type w} [∀ a, AddCommGroup (A a)]
variable (F : AdditiveViewSystem V A)

/-- The same restriction maps with multiplicative type tags. -/
def multiplicativeViews : GroupViewSystem V (fun v => Multiplicative (A v)) where
  pull := fun f => (F.pull f).toMultiplicative
  pull_id := by intro v x; exact congrArg Multiplicative.ofAdd (F.pull_id v x.toAdd)
  pull_comp := by intro v w z f g x; exact congrArg Multiplicative.ofAdd (F.pull_comp f g x.toAdd)

/-- Trivial cocycles recover the previous coherent additive sections. -/
def multiplicativeAmbientEquiv : F.views.Ambient ≃
    (F.multiplicativeViews.twistedViews F.multiplicativeViews.trivial).Ambient where
  toFun x := ⟨fun v => Multiplicative.ofAdd (x.val v), by
    intro v w f
    change 1 * Multiplicative.ofAdd (F.pull f (x.val w)) = Multiplicative.ofAdd (x.val v)
    rw [one_mul]
    exact congrArg Multiplicative.ofAdd (x.property v w f)⟩
  invFun x := ⟨fun v => (x.val v).toAdd, by
    intro v w f
    have he := x.property v w f
    change 1 * Multiplicative.ofAdd (F.pull f (x.val w).toAdd) = x.val v at he
    rw [one_mul] at he
    exact congrArg Multiplicative.toAdd he⟩
  left_inv _ := rfl
  right_inv _ := rfl

def multiplicativePartial (U : Set V) (s : F.views.Partial U) :
    (F.multiplicativeViews.twistedViews F.multiplicativeViews.trivial).Partial U :=
  ⟨fun v => Multiplicative.ofAdd (s.val v), by
    intro v w f
    change 1 * Multiplicative.ofAdd (F.pull f (s.val w)) = Multiplicative.ofAdd (s.val v)
    rw [one_mul]
    exact congrArg Multiplicative.ofAdd (s.property v w f)⟩

def multiplicativeExtensionsEquiv (U : Set V) (s : F.views.Partial U) :
    F.views.Extensions U s ≃
    (F.multiplicativeViews.twistedViews F.multiplicativeViews.trivial).Extensions U
      (F.multiplicativePartial U s) where
  toFun x := ⟨F.multiplicativeAmbientEquiv x.val, by
    apply ViewSystem.Partial.ext
    intro v
    change Multiplicative.ofAdd (x.val.val v.val) = Multiplicative.ofAdd (s.val v)
    exact congrArg Multiplicative.ofAdd
      (congrArg (fun t : F.views.Partial U => t.val v) x.property)⟩
  invFun x := ⟨F.multiplicativeAmbientEquiv.symm x.val, by
    apply ViewSystem.Partial.ext
    intro v
    have he := congrArg
      (fun t : (F.multiplicativeViews.twistedViews F.multiplicativeViews.trivial).Partial U => t.val v)
      x.property
    exact congrArg Multiplicative.toAdd he⟩
  left_inv _ := rfl
  right_inv _ := rfl

/-- The normalized multiplicative edge is exactly the old additive differential. -/
theorem normalization_is_additive_defect (q : ∀ v, A v) {v w : V} (f : v ⟶ w) :
    ((F.multiplicativeViews.normalize F.multiplicativeViews.trivial
      (fun a => Multiplicative.ofAdd (q a))).edge f).toAdd = F.differential q v w f := by
  rw [GroupViewSystem.normalize_edge]
  change -q v + 0 + F.pull f (q w) = F.pull f (q w) - q v
  abel

/-- Neutrality in the orbit model agrees with vanishing of the original quotient obstruction. -/
theorem orbit_neutral_iff_additive_zero (U : Set V) (s : F.views.Partial U) :
    F.multiplicativeViews.extensionOrbit F.multiplicativeViews.trivial U
      (F.multiplicativePartial U s) = F.multiplicativeViews.neutralClass U ↔
      F.extensionClass U s = 0 := by
  rw [GroupViewSystem.extensionOrbit_neutral_iff, F.extensionClass_zero_iff]
  constructor
  · rintro ⟨x⟩; exact ⟨(F.multiplicativeExtensionsEquiv U s).symm x⟩
  · rintro ⟨x⟩; exact ⟨F.multiplicativeExtensionsEquiv U s x⟩

end AdditiveViewSystem
end KomorebiSpace
