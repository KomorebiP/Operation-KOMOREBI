import KomorebiSpace.ViewSections

set_option autoImplicit false

/-!
# Gluing sections over a cover which includes transitions

A cover of view objects alone is insufficient. The sufficient cover hypothesis
below requires every arrow's endpoints to occur together in some patch.
Under this combinatorial condition, matching local sections glue uniquely.
This is a strict set-valued gluing theorem, not a general higher-stack assertion.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory
namespace ViewSystem
variable {V : Type u} [Category.{v} V]
variable (F : ViewSystem.{u,v,w} V) {I : Type z} (U : I → Set V)

/-- Every view is seen somewhere. This alone need not suffice for gluing. -/
def ObjectCover : Prop := ∀ a : V, ∃ i, a ∈ U i

/-- Every transition is seen with both endpoints in one patch. -/
def TransitionCover : Prop :=
  ∀ (a b : V) (_ : a ⟶ b), ∃ i, a ∈ U i ∧ b ∈ U i

theorem TransitionCover.objectCover (h : TransitionCover U) : ObjectCover U := by
  intro a
  obtain ⟨i, ha, _⟩ := h a a (𝟙 a)
  exact ⟨i, ha⟩

/-- Values agree on every common view, not only up to an unspecified relation. -/
structure Matching where
  localSection : ∀ i, F.Partial (U i)
  agree : ∀ i j a (hi : a ∈ U i) (hj : a ∈ U j),
    (localSection i).val ⟨a, hi⟩ = (localSection j).val ⟨a, hj⟩

namespace Matching
variable {F U}

@[ext] theorem ext {m n : Matching F U}
    (h : ∀ i, m.localSection i = n.localSection i) : m = n := by
  cases m with
  | mk ml ma =>
    cases n with
    | mk nl na =>
      have he : ml = nl := funext h
      cases he
      rfl

noncomputable def assemble (h : ObjectCover U) (m : Matching F U) : ∀ a, F.Obj a :=
  fun a => (m.localSection (Classical.choose (h a))).val
    ⟨a, Classical.choose_spec (h a)⟩

theorem assemble_local (h : ObjectCover U) (m : Matching F U)
    (i : I) (a : V) (ha : a ∈ U i) :
    m.assemble h a = (m.localSection i).val ⟨a, ha⟩ := by
  exact m.agree _ i a _ ha

/-- Assembly becomes coherent because the cover also sees every transition. -/
theorem assemble_coherent (h : TransitionCover U) (m : Matching F U)
    (a b : V) (f : a ⟶ b) :
    F.pull f (m.assemble (TransitionCover.objectCover U h) b) = m.assemble (TransitionCover.objectCover U h) a := by
  obtain ⟨i, ha, hb⟩ := h a b f
  rw [m.assemble_local (TransitionCover.objectCover U h) i b hb, m.assemble_local (TransitionCover.objectCover U h) i a ha]
  exact (m.localSection i).property ⟨a, ha⟩ ⟨b, hb⟩ f

noncomputable def glue (h : TransitionCover U) (m : Matching F U) : F.Ambient :=
  ⟨m.assemble (TransitionCover.objectCover U h), m.assemble_coherent h⟩

@[simp] theorem glue_restrict (h : TransitionCover U) (m : Matching F U) (i : I) :
    F.restrict (U i) (m.glue h) = m.localSection i := by
  apply Partial.ext
  intro a
  exact m.assemble_local (TransitionCover.objectCover U h) i a.val a.property

theorem glue_unique (h : TransitionCover U) (m : Matching F U) (s : F.Ambient)
    (hs : ∀ i, F.restrict (U i) s = m.localSection i) : s = m.glue h := by
  apply Ambient.ext
  intro a
  obtain ⟨i, ha⟩ := (TransitionCover.objectCover U h) a
  have hv := congrArg (fun x : F.Partial (U i) => x.val ⟨a, ha⟩) (hs i)
  exact hv.trans (m.assemble_local (TransitionCover.objectCover U h) i a ha).symm

theorem exists_unique_glue (h : TransitionCover U) (m : Matching F U) :
    ∃! s : F.Ambient, ∀ i, F.restrict (U i) s = m.localSection i := by
  refine ⟨m.glue h, fun i => m.glue_restrict h i, ?_⟩
  intro s hs
  exact m.glue_unique h s hs
end Matching

/-- Restriction gives a matching family without any cover hypothesis. -/
def toMatching (s : F.Ambient) : Matching F U where
  localSection := fun i => F.restrict (U i) s
  agree := by intros; rfl

/-- A proved local/global equivalence for the specified transition-covered patches. -/
noncomputable def gluingEquiv (h : TransitionCover U) :
    F.Ambient ≃ Matching F U where
  toFun := F.toMatching U
  invFun := fun m => m.glue h
  left_inv := by
    intro s
    exact ((F.toMatching U s).glue_unique h s (fun _ => rfl)).symm
  right_inv := by
    intro m
    apply Matching.ext
    intro i
    exact m.glue_restrict h i

/-- Global equality needs only coverage of views; global existence needs more. -/
theorem restrict_jointly_injective (h : ObjectCover U) {s t : F.Ambient}
    (hst : ∀ i, F.restrict (U i) s = F.restrict (U i) t) : s = t := by
  apply Ambient.ext
  intro a
  obtain ⟨i, ha⟩ := h a
  exact congrArg (fun x : F.Partial (U i) => x.val ⟨a, ha⟩) (hst i)

end ViewSystem
end KomorebiSpace
