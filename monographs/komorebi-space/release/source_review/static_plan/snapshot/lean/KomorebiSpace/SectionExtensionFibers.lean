import KomorebiSpace.SectionObstruction
import KomorebiSpace.ExtensionFibers

set_option autoImplicit false

/-! # Classification and uniqueness of actual ambient extensions -/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace AdditiveViewSystem
variable {V : Type u} [Category.{v} V]
variable {A : V → Type w} [∀ a, AddCommGroup (A a)]
variable (F : AdditiveViewSystem V A)

/-- Coherent ambient changes invisible on the prescribed views. -/
def ambiguity (U : Set V) : AddSubgroup (∀ a, A a) := (F.problem U).homogeneous

@[simp] theorem mem_ambiguity (U : Set V) (x : ∀ a, A a) :
    x ∈ F.ambiguity U ↔ F.differential x = 0 ∧ F.observation U x = 0 := Iff.rfl

def extensionsFiberEquiv (U : Set V) (s : F.views.Partial U) :
    F.views.Extensions U s ≃ (F.problem U).ExactFiber s.val where
  toFun x := ⟨x.val.val, by
    constructor
    · exact (F.differential_zero_iff _).mpr x.val.property
    · exact congrArg Subtype.val x.property⟩
  invFun x := ⟨⟨x.val, (F.differential_zero_iff _).mp x.property.1⟩, by
    apply ViewSystem.Partial.ext
    intro a
    exact congrFun x.property.2 a⟩
  left_inv x := by apply Subtype.ext; apply Subtype.ext; rfl
  right_inv x := by apply Subtype.ext; rfl

/-- A chosen global extension supplies affine coordinates on every extension. -/
def extensionParameters (U : Set V) (s : F.views.Partial U)
    (base : F.views.Extensions U s) : F.ambiguity U ≃ F.views.Extensions U s :=
  ((F.problem U).fiberParameters (F.extensionsFiberEquiv U s base)).trans
    (F.extensionsFiberEquiv U s).symm

@[simp] theorem extensionParameters_coordinate (U : Set V) (s : F.views.Partial U)
    (base : F.views.Extensions U s) (h : F.ambiguity U) (a : V) :
    (F.extensionParameters U s base h).val.val a = (show A a from base.val.val a) + h.val a := rfl

/-- Difference coordinates use the actual values in every view. -/
@[simp] theorem extensionParameters_inverse (U : Set V) (s : F.views.Partial U)
    (base x : F.views.Extensions U s) (a : V) :
    ((F.extensionParameters U s base).symm x).val a = (show A a from x.val.val a) - (show A a from base.val.val a) := rfl

theorem extension_subsingleton_iff (U : Set V) (s : F.views.Partial U)
    (base : F.views.Extensions U s) :
    Subsingleton (F.views.Extensions U s) ↔ F.ambiguity U = ⊥ := by
  have e := F.extensionsFiberEquiv U s
  rw [show F.ambiguity U = (F.problem U).homogeneous from rfl]
  rw [← (F.problem U).fiber_subsingleton_iff (e base)]
  constructor
  · intro h
    exact ⟨fun x y => e.symm.injective (h.elim _ _)⟩
  · intro h
    exact ⟨fun x y => e.injective (h.elim _ _)⟩

/-- Solvability and uniqueness are independent obligations. -/
theorem unique_extension_iff (U : Set V) (s : F.views.Partial U) :
    (∃! x : F.views.Ambient, F.views.restrict U x = s) ↔
      F.extensionClass U s = 0 ∧ F.ambiguity U = ⊥ := by
  constructor
  · rintro ⟨x,hx,hu⟩
    let base : F.views.Extensions U s := ⟨x,hx⟩
    refine ⟨(F.extensionClass_zero_iff U s).mpr ⟨base⟩, ?_⟩
    apply (F.extension_subsingleton_iff U s base).mp
    refine ⟨fun a b => ?_⟩
    apply Subtype.ext
    exact (hu a.val a.property).trans (hu b.val b.property).symm
  · rintro ⟨ho,hh⟩
    obtain ⟨base⟩ := (F.extensionClass_zero_iff U s).mp ho
    have hs := (F.extension_subsingleton_iff U s base).mpr hh
    refine ⟨base.val, base.property, ?_⟩
    intro x hx
    exact congrArg Subtype.val (hs.elim (⟨x,hx⟩ : F.views.Extensions U s) base)

/-- More prescribed views leave fewer homogeneous changes. -/
theorem ambiguity_antitone {U W : Set V} (h : U ⊆ W) :
    F.ambiguity W ≤ F.ambiguity U := by
  intro x hx
  refine ⟨hx.1, ?_⟩
  change F.observation U x = 0
  funext a
  exact congrFun hx.2 (⟨a.val,h a.property⟩ : W)

end AdditiveViewSystem

namespace ViewSystem
variable {V : Type u} [Category.{v} V]
variable (F : ViewSystem.{u,v,w} V)

/-- Each view can be detected by an injective restriction into a prescribed view. -/
theorem restrict_injective_of_detecting_views (U : Set V)
    (detect : ∀ b : V, ∃ a : U, ∃ f : a.val ⟶ b, Function.Injective (F.pull f)) :
    Function.Injective (F.restrict U) := by
  intro x y h
  apply Ambient.ext
  intro b
  obtain ⟨a,f,hf⟩ := detect b
  apply hf
  rw [x.property, y.property]
  exact congrArg (fun s : F.Partial U => s.val a) h

end ViewSystem
end KomorebiSpace
