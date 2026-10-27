import KomorebiSpace.ViewSections

set_option autoImplicit false

/-!
# Extension through an intermediate domain of views

The total extension set is the dependent sum of extension fibers over every
compatible intermediate choice. This does not say every intermediate choice
can be extended, nor does it assert an infinite dependent-choice theorem.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace ViewSystem
variable {V : Type u} [Category.{v} V]
variable (F : ViewSystem.{u,v,w} V)

/-- Compatible choices of an intermediate partial section. -/
def Intermediate {U W : Set V} (h : U ⊆ W) (s : F.Partial U) :=
  {t : F.Partial W // F.restrictPartial h t = s}

@[simp] theorem restrict_restrictPartial {U W : Set V} (h : U ⊆ W)
    (x : F.Ambient) :
    F.restrictPartial h (F.restrict W x) = F.restrict U x := rfl

/-- An actual equivalence, retaining all possible intermediate choices. -/
def extensionStages {U W : Set V} (h : U ⊆ W) (s : F.Partial U) :
    F.Extensions U s ≃ Σ t : F.Intermediate h s, F.Extensions W t.val where
  toFun x := ⟨⟨F.restrict W x.val,x.property⟩,⟨x.val,rfl⟩⟩
  invFun z := ⟨z.2.val,by
    have he := congrArg (F.restrictPartial h) z.2.property
    exact he.trans z.1.property⟩
  left_inv x := rfl
  right_inv z := by
    rcases z with ⟨⟨t,ht⟩,x,hx⟩
    dsimp at hx
    subst t
    rfl

@[simp] theorem extensionStages_global {U W : Set V} (h : U ⊆ W)
    (s : F.Partial U) (x : F.Extensions U s) :
    (F.extensionStages h s x).2.val = x.val := rfl

@[simp] theorem extensionStages_intermediate {U W : Set V} (h : U ⊆ W)
    (s : F.Partial U) (x : F.Extensions U s) :
    (F.extensionStages h s x).1.val = F.restrict W x.val := rfl

/-- At least one intermediate choice must remain extendable. -/
theorem extension_nonempty_iff_intermediate {U W : Set V} (h : U ⊆ W)
    (s : F.Partial U) :
    Nonempty (F.Extensions U s) ↔
      ∃ t : F.Intermediate h s, Nonempty (F.Extensions W t.val) := by
  constructor
  · rintro ⟨x⟩
    exact ⟨(F.extensionStages h s x).1,⟨(F.extensionStages h s x).2⟩⟩
  · rintro ⟨t,⟨x⟩⟩
    exact ⟨(F.extensionStages h s).symm ⟨t,x⟩⟩

/-- Restriction of an existing global extension gives an intermediate choice. -/
def intermediateOfExtension {U W : Set V} (h : U ⊆ W)
    (s : F.Partial U) (x : F.Extensions U s) : F.Intermediate h s :=
  (F.extensionStages h s x).1

end ViewSystem
end KomorebiSpace
