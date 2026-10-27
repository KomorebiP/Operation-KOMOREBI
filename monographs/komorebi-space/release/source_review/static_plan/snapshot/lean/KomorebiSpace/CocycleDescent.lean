import KomorebiSpace.GaugeDescent

set_option autoImplicit false

/-!
# Strict descent of cocycle objects

Local cocycle labels on full view patches glue when they agree literally on
overlap arrows. To verify the cocycle law after gluing, every composable pair
must be visible inside one patch; this is stronger than covering arrows one at
a time. The result is an explicit equivalence between global cocycles and
strictly matching local cocycles under that cover hypothesis.

This is strict object descent. Local cocycles related only by gauge
isomorphisms are not yet glued here.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem

variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable {I : Type z}
variable (F : GroupViewSystem V G)

/-- Cocycle data restricted to one full patch of view objects. -/
structure PatchCocycle (S : Set V) where
  edge : ∀ {a b : S}, (a.val ⟶ b.val) → G a.val
  edge_id : ∀ a : S, edge (𝟙 a.val) = 1
  edge_comp : ∀ {a b c : S} (f : a.val ⟶ b.val) (g : b.val ⟶ c.val),
    edge (f ≫ g) = edge f * F.pull f (edge g)

namespace PatchCocycle
variable {F}

@[ext] theorem ext {S : Set V} {c d : F.PatchCocycle S}
    (h : ∀ (a b : S) (f : a.val ⟶ b.val), c.edge f = d.edge f) : c = d := by
  cases c with
  | mk ce ci cc =>
    cases d with
    | mk de di dc =>
      have he : @ce = @de := by
        funext a b f
        exact h a b f
      cases he
      rfl

end PatchCocycle

/-- Restrict an already-global cocycle to a full patch. -/
def restrictCocycle (c : F.Cocycle) (S : Set V) : F.PatchCocycle S where
  edge := fun f => c.edge f
  edge_id := fun a => c.edge_id a.val
  edge_comp := fun f g => c.edge_comp f g

/-- Local cocycles which agree literally on every arrow visible in two patches. -/
structure CocycleMatching (U : I → Set V) where
  patch : ∀ i, F.PatchCocycle (U i)
  agree : ∀ (i j : I) (a b : V) (hai : a ∈ U i) (hbi : b ∈ U i)
      (haj : a ∈ U j) (hbj : b ∈ U j) (f : a ⟶ b),
    (patch i).edge (a := ⟨a, hai⟩) (b := ⟨b, hbi⟩) f =
      (patch j).edge (a := ⟨a, haj⟩) (b := ⟨b, hbj⟩) f

namespace CocycleMatching
variable {F} {U : I → Set V}

@[ext] theorem ext {m n : F.CocycleMatching U}
    (h : ∀ i, m.patch i = n.patch i) : m = n := by
  cases m with
  | mk mp ma =>
    cases n with
    | mk np na =>
      have he : mp = np := funext h
      cases he
      rfl

end CocycleMatching

/-- Every composable pair is contained in one patch. -/
def CompositionCover (U : I → Set V) : Prop :=
  ∀ (a b c : V) (_ : a ⟶ b) (_ : b ⟶ c),
    ∃ i, a ∈ U i ∧ b ∈ U i ∧ c ∈ U i

namespace CompositionCover
variable {U : I → Set V}

/-- A composition cover in particular covers every individual transition. -/
theorem transitionCover (h : CompositionCover U) : ViewSystem.TransitionCover U := by
  intro a b f
  obtain ⟨i, ha, hb, _⟩ := h a b b f (𝟙 b)
  exact ⟨i, ha, hb⟩

end CompositionCover

namespace CocycleMatching
variable {F} {U : I → Set V}

/-- Assemble one global edge label using any patch which sees that arrow. -/
noncomputable def assembleEdge (h : ViewSystem.TransitionCover U)
    (m : F.CocycleMatching U) {a b : V} (f : a ⟶ b) : G a :=
  let witness := Classical.choose (h a b f)
  let spec := Classical.choose_spec (h a b f)
  (m.patch witness).edge
    (a := ⟨a, spec.1⟩) (b := ⟨b, spec.2⟩) f

/-- Assembly agrees with the label in every patch containing the arrow. -/
theorem assembleEdge_local (h : ViewSystem.TransitionCover U)
    (m : F.CocycleMatching U) (i : I) (a b : V)
    (ha : a ∈ U i) (hb : b ∈ U i) (f : a ⟶ b) :
    m.assembleEdge h f =
      (m.patch i).edge (a := ⟨a, ha⟩) (b := ⟨b, hb⟩) f := by
  unfold assembleEdge
  let j := Classical.choose (h a b f)
  let hs := Classical.choose_spec (h a b f)
  exact m.agree j i a b hs.1 hs.2 ha hb f

/-- Strictly matching local cocycles glue to a global cocycle. -/
noncomputable def glue (h : CompositionCover U) (m : F.CocycleMatching U) : F.Cocycle where
  edge := fun f => m.assembleEdge h.transitionCover f
  edge_id := by
    intro a
    obtain ⟨i, ha⟩ := ViewSystem.TransitionCover.objectCover U h.transitionCover a
    rw [m.assembleEdge_local h.transitionCover i a a ha ha (𝟙 a)]
    exact (m.patch i).edge_id ⟨a, ha⟩
  edge_comp := by
    intro a b c f g
    obtain ⟨i, ha, hb, hc⟩ := h a b c f g
    rw [m.assembleEdge_local h.transitionCover i a c ha hc (f ≫ g),
        m.assembleEdge_local h.transitionCover i a b ha hb f,
        m.assembleEdge_local h.transitionCover i b c hb hc g]
    exact (m.patch i).edge_comp (a := ⟨a, ha⟩) (b := ⟨b, hb⟩) (c := ⟨c, hc⟩) f g

/-- A global cocycle gives a strictly matching family on every patch. -/
def ofGlobal (c : F.Cocycle) : F.CocycleMatching U where
  patch := fun i => F.restrictCocycle c (U i)
  agree := by intros; rfl

/-- Gluing the restrictions of a global cocycle returns that cocycle. -/
theorem glue_ofGlobal (h : CompositionCover U) (c : F.Cocycle) :
    (ofGlobal (U := U) c).glue h = c := by
  apply Cocycle.ext
  intro a b f
  obtain ⟨i, ha, hb⟩ := h.transitionCover a b f
  exact (ofGlobal (U := U) c).assembleEdge_local h.transitionCover i a b ha hb f

/-- Restricting a glued strict matching family returns the original family. -/
theorem ofGlobal_glue (h : CompositionCover U) (m : F.CocycleMatching U) :
    ofGlobal (U := U) (m.glue h) = m := by
  apply CocycleMatching.ext
  intro i
  apply PatchCocycle.ext
  intro a b f
  exact m.assembleEdge_local h.transitionCover i a.val b.val a.property b.property f

/-- Strict cocycle descent equivalence under a composable-triple cover. -/
noncomputable def descentEquiv (h : CompositionCover U) :
    F.Cocycle ≃ F.CocycleMatching U where
  toFun := ofGlobal (U := U)
  invFun := fun m => m.glue h
  left_inv := glue_ofGlobal h
  right_inv := ofGlobal_glue h

end CocycleMatching
end GroupViewSystem
end KomorebiSpace
