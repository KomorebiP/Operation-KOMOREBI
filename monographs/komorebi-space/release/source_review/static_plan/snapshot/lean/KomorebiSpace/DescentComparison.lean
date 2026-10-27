import KomorebiSpace.EffectiveCocycleDescent

set_option autoImplicit false

/-!
# Uniqueness and choice-independence of effectuation

Two globalizations of the same specified descent datum have a unique global
gauge compatible with their local identifications. This does not discard
ordinary automorphisms of the underlying global cocycle.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable {I : Type z} {F : GroupViewSystem V G} {U : I → Set V}
namespace CocycleDescentData
namespace Effectuation
variable {D : F.CocycleDescentData U}

/-- Underlying object in the existing unframed gauge groupoid. -/
def object (E : D.Effectuation) : F.GaugeObject (∅ : Set V) := ⟨E.global⟩

/-- Patchwise quotient of the two sets of local identifications. -/
def comparisonMatching (E E' : D.Effectuation) : GaugeMatching (G := G) U where
  value := fun i x => (E'.compare i x)⁻¹ * E.compare i x
  agree := by
    intro i j x hi hj
    rw [E.overlap i j x hi hj, E'.overlap i j x hi hj]
    group

/-- The quotient gauge really carries one global cocycle to the other. -/
theorem comparison_relates (E E' : D.Effectuation) :
    GaugeMatching.Relates F (E.comparisonMatching E') E.global E'.global := by
  intro i x y f
  change ((E'.compare i x)⁻¹ * E.compare i x) * E.global.edge f *
    (F.pull f ((E'.compare i y)⁻¹ * E.compare i y))⁻¹ = E'.global.edge f
  rw [E.global_local i x y f, E'.global_local i x y f, map_mul, map_inv]
  group

/-- Assemble the comparison through the already checked morphism descent. -/
def comparisonDescent (E E' : D.Effectuation) :
    GaugeMatching.FramedDescent F U (∅ : Set V) E.object E'.object where
  matching := E.comparisonMatching E'
  relates := E.comparison_relates E'
  based := by intro i x hi hx; exact False.elim hx

noncomputable def comparisonHom (E E' : D.Effectuation)
    (h : ViewSystem.TransitionCover U) : E.object ⟶ E'.object :=
  (E.comparisonDescent E').glueHom h

@[simp] theorem comparisonHom_local (E E' : D.Effectuation)
    (h : ViewSystem.TransitionCover U) (i : I) (x : U i) :
    (E.comparisonHom E' h).change.val x.val = (E'.compare i x)⁻¹ * E.compare i x :=
  (E.comparisonDescent E').glueHom_local h i x.val x.property

/-- A comparison must respect the chosen local identifications. -/
def Compatible (E E' : D.Effectuation) (a : E.object ⟶ E'.object) : Prop :=
  ∀ i (x : U i), E'.compare i x * a.change.val x.val = E.compare i x

theorem comparisonHom_compatible (E E' : D.Effectuation)
    (h : ViewSystem.TransitionCover U) : E.Compatible E' (E.comparisonHom E' h) := by
  intro i x
  rw [comparisonHom_local]
  group

theorem comparisonHom_unique (E E' : D.Effectuation)
    (h : ViewSystem.TransitionCover U) (a : E.object ⟶ E'.object)
    (ha : E.Compatible E' a) : a = E.comparisonHom E' h := by
  apply (E.comparisonDescent E').glueHom_unique h a
  intro i x
  change a.change.val x.val = (E'.compare i x)⁻¹ * E.compare i x
  rw [← ha i x]
  group

/-- Existence and uniqueness are for a fixed descent datum with its identifications. -/
theorem exists_unique_comparison (E E' : D.Effectuation)
    (h : ViewSystem.TransitionCover U) :
    ∃! a : E.object ⟶ E'.object, E.Compatible E' a := by
  refine ⟨E.comparisonHom E' h, E.comparisonHom_compatible E' h, ?_⟩
  intro a ha
  exact E.comparisonHom_unique E' h a ha

noncomputable def comparisonIso (E E' : D.Effectuation)
    (h : ViewSystem.TransitionCover U) : E.object ≅ E'.object :=
  (Groupoid.isoEquivHom E.object E'.object).symm (E.comparisonHom E' h)

theorem orbit_independent (E E' : D.Effectuation) (h : ViewSystem.TransitionCover U) :
    F.orbitClass ∅ E.global = F.orbitClass ∅ E'.global :=
  (F.morphism_nonempty_iff_class ∅ E.object E'.object).mp ⟨E.comparisonHom E' h⟩

theorem comparisonHom_self (E : D.Effectuation) (h : ViewSystem.TransitionCover U) :
    E.comparisonHom E h = 𝟙 E.object := by
  symm
  apply E.comparisonHom_unique E h
  intro i x
  change E.compare i x * 1 = E.compare i x
  exact mul_one _

theorem comparisonHom_comp (E E' E'' : D.Effectuation)
    (h : ViewSystem.TransitionCover U) :
    E.comparisonHom E' h ≫ E'.comparisonHom E'' h = E.comparisonHom E'' h := by
  apply E.comparisonHom_unique E'' h
  intro i x
  change E''.compare i x *
    ((E'.comparisonHom E'' h).change.val x.val * (E.comparisonHom E' h).change.val x.val) = _
  rw [comparisonHom_local, comparisonHom_local]
  group

end Effectuation

/-- Effective descent, including uniqueness of each compatible global comparison. -/
theorem effective_descent (D : F.CocycleDescentData U) (h : CompositionCover U) :
    ∃ E : D.Effectuation, ∀ E' : D.Effectuation,
      ∃! a : E.object ⟶ E'.object, E.Compatible E' a := by
  refine ⟨D.effectuate h, ?_⟩
  intro E'
  exact (D.effectuate h).exists_unique_comparison E' h.transitionCover

end CocycleDescentData
end GroupViewSystem
end KomorebiSpace
