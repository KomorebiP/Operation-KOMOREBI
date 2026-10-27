import KomorebiSpace.CocycleGaugeGroupoid
import KomorebiSpace.SectionGluing

set_option autoImplicit false

/-!
# Descent of gauge transformations across a view cover

This module proves the morphism half of a stack-like descent statement for the
existing nonabelian cocycle groupoid. Local gauge changes which agree on
view-overlaps glue to one global gauge. If each local gauge carries one fixed
cocycle to another on every transition visible in its patch, then the glued
gauge carries the first global cocycle to the second globally, provided the
patches cover transitions. A framed version produces an actual morphism in the
existing `GaugeObject` groupoid.

The cocycle objects in this theorem are already global. Thus this is descent of
morphisms, not yet effective descent of locally supplied cocycle objects.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem

variable {V : Type u}
variable {G : V → Type w}
variable {I : Type z}

/-- A family of local gauge values which agrees literally on common views. -/
structure GaugeMatching (U : I → Set V) where
  value : ∀ (i : I) (a : U i), G a.val
  agree : ∀ (i j : I) (a : V) (hi : a ∈ U i) (hj : a ∈ U j),
    value i ⟨a, hi⟩ = value j ⟨a, hj⟩

namespace GaugeMatching
variable {U : I → Set V}

@[ext] theorem ext {m n : GaugeMatching (G := G) U}
    (h : ∀ i a, m.value i a = n.value i a) : m = n := by
  cases m with
  | mk ml ma =>
    cases n with
    | mk nl na =>
      have he : ml = nl := by
        funext i a
        exact h i a
      cases he
      rfl

/-- Assemble a global gauge family from locally matching values. -/
noncomputable def assemble (h : ViewSystem.ObjectCover U) (m : GaugeMatching (G := G) U) :
    ∀ a, G a :=
  fun a => m.value (Classical.choose (h a))
    ⟨a, Classical.choose_spec (h a)⟩

theorem assemble_local (h : ViewSystem.ObjectCover U) (m : GaugeMatching (G := G) U)
    (i : I) (a : V) (ha : a ∈ U i) :
    m.assemble h a = m.value i ⟨a, ha⟩ := by
  exact m.agree _ i a _ ha

variable [Category.{v} V] [∀ a, Group (G a)]

/-- Local gauge equations relating two global cocycles. -/
def Relates (F : GroupViewSystem V G) (m : GaugeMatching (G := G) U)
    (c d : F.Cocycle) : Prop :=
  ∀ (i : I) (a b : U i) (f : a.val ⟶ b.val),
    m.value i a * c.edge f * (F.pull f (m.value i b))⁻¹ = d.edge f

/-- A transition-covered matching of local gauges gives one global gauge equation. -/
theorem assemble_relates (F : GroupViewSystem V G) (m : GaugeMatching (G := G) U)
    (c d : F.Cocycle) (hcover : ViewSystem.TransitionCover U)
    (hrel : Relates F m c d) :
    F.gauge (m.assemble (ViewSystem.TransitionCover.objectCover U hcover)) c = d := by
  apply Cocycle.ext
  intro a b f
  obtain ⟨i, ha, hb⟩ := hcover a b f
  change m.assemble (ViewSystem.TransitionCover.objectCover U hcover) a * c.edge f *
      (F.pull f (m.assemble (ViewSystem.TransitionCover.objectCover U hcover) b))⁻¹ = d.edge f
  rw [m.assemble_local (ViewSystem.TransitionCover.objectCover U hcover) i a ha,
      m.assemble_local (ViewSystem.TransitionCover.objectCover U hcover) i b hb]
  exact hrel i ⟨a, ha⟩ ⟨b, hb⟩ f

/-- Local identity on a framing domain survives assembly. -/
def BasedOn (m : GaugeMatching (G := G) U) (B : Set V) : Prop :=
  ∀ (i : I) (a : V) (ha : a ∈ U i), a ∈ B → m.value i ⟨a, ha⟩ = 1

/-- The assembled family is a member of the existing based gauge subgroup. -/
noncomputable def assembleBased (F : GroupViewSystem V G)
    (m : GaugeMatching (G := G) U) (B : Set V)
    (hcover : ViewSystem.ObjectCover U) (hbased : BasedOn m B) : F.basedGauge B :=
  ⟨m.assemble hcover, by
    intro a
    obtain ⟨i, ha⟩ := hcover a.val
    rw [m.assemble_local hcover i a.val ha]
    exact hbased i a.val ha a.property⟩

@[simp] theorem assembleBased_val (F : GroupViewSystem V G)
    (m : GaugeMatching (G := G) U) (B : Set V)
    (hcover : ViewSystem.ObjectCover U) (hbased : BasedOn m B) (a : V) :
    (assembleBased F m B hcover hbased).val a = m.assemble hcover a := rfl

/-- Descent data for a framed gauge morphism between two already-global cocycles. -/
structure FramedDescent (F : GroupViewSystem V G) (U : I → Set V)
    (B : Set V) (c d : F.GaugeObject B) where
  matching : GaugeMatching (G := G) U
  relates : Relates F matching c.labels d.labels
  based : BasedOn matching B

namespace FramedDescent
variable {F : GroupViewSystem V G} {U : I → Set V}

/-- Glue compatible local framed gauges to an actual morphism of gauge objects. -/
noncomputable def glueHom {B : Set V} {c d : F.GaugeObject B}
    (D : FramedDescent F U B c d) (hcover : ViewSystem.TransitionCover U) : c ⟶ d :=
  ⟨assembleBased F D.matching B (ViewSystem.TransitionCover.objectCover U hcover) D.based,
    assemble_relates F D.matching c.labels d.labels hcover D.relates⟩

@[simp] theorem glueHom_change_value {B : Set V} {c d : F.GaugeObject B}
    (D : FramedDescent F U B c d) (hcover : ViewSystem.TransitionCover U)
    (a : V) :
    (D.glueHom hcover).change.val a = D.matching.assemble (ViewSystem.TransitionCover.objectCover U hcover) a := rfl

/-- The glued morphism restricts to every specified local gauge value. -/
theorem glueHom_local {B : Set V} {c d : F.GaugeObject B}
    (D : FramedDescent F U B c d) (hcover : ViewSystem.TransitionCover U)
    (i : I) (a : V) (ha : a ∈ U i) :
    (D.glueHom hcover).change.val a = D.matching.value i ⟨a, ha⟩ := by
  rw [glueHom_change_value]
  exact D.matching.assemble_local (ViewSystem.TransitionCover.objectCover U hcover) i a ha

/-- A global framed gauge morphism agreeing with all local gauges is unique. -/
theorem glueHom_unique {B : Set V} {c d : F.GaugeObject B}
    (D : FramedDescent F U B c d) (hcover : ViewSystem.TransitionCover U)
    (a : c ⟶ d)
    (ha : ∀ i (x : U i), a.change.val x.val = D.matching.value i x) :
    a = D.glueHom hcover := by
  apply GaugeObject.Hom.ext
  apply Subtype.ext
  funext x
  obtain ⟨i, hx⟩ := (ViewSystem.TransitionCover.objectCover U hcover) x
  calc
    a.change.val x = D.matching.value i ⟨x, hx⟩ := ha i ⟨x, hx⟩
    _ = (D.glueHom hcover).change.val x := (D.glueHom_local hcover i x hx).symm

/-- Existence and uniqueness of a global morphism realizing a fixed matching family. -/
theorem exists_unique_glued_hom {B : Set V} {c d : F.GaugeObject B}
    (D : FramedDescent F U B c d) (hcover : ViewSystem.TransitionCover U) :
    ∃! a : c ⟶ d, ∀ i (x : U i), a.change.val x.val = D.matching.value i x := by
  refine ⟨D.glueHom hcover, ?_, ?_⟩
  · intro i x
    exact D.glueHom_local hcover i x.val x.property
  · intro a ha
    exact D.glueHom_unique hcover a ha

end FramedDescent
end GaugeMatching
end GroupViewSystem
end KomorebiSpace
