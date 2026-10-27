import PaperIRelease.GrammarTyped
import PaperIRelease.GrammarModules

set_option autoImplicit false
set_option maxHeartbeats 4000000
set_option linter.unusedVariables false
set_option linter.unnecessarySimpa false
set_option linter.unusedSimpArgs false
set_option linter.unusedSectionVars false

noncomputable section

namespace Komorebi.PaperIRelease.GrammarAlgebra

open CategoryTheory GrammarModules
open scoped BigOperators

universe u
variable {K V E : Type u} [Field K] [Fintype V]
variable {G : Grammar K V E}

attribute [local instance] Classical.propDecidable

/-- The manuscript's vertexwise maps, satisfying each arrow square. -/
structure TypedHom (X Y : TypedRealization (G := G)) where
  map : ∀ v, X.space v →ₗ[K] Y.space v
  natural : ∀ a x, map (G.target a) (X.arrow a x) = Y.arrow a (map (G.source a) x)

@[ext] theorem TypedHom.ext {X Y : TypedRealization (G := G)}
    (f g : TypedHom X Y) (h : f.map = g.map) : f = g := by
  cases f
  cases g
  cases h
  rfl

instance typedCategory : Category (TypedRealization (G := G)) where
  Hom := TypedHom
  id X := ⟨fun _ => LinearMap.id, fun _ _ => rfl⟩
  comp f g := ⟨fun v => (g.map v).comp (f.map v), by
    intro a x
    simp only [LinearMap.comp_apply]
    rw [f.natural, g.natural]⟩
  id_comp f := by apply TypedHom.ext; rfl
  comp_id f := by apply TypedHom.ext; rfl
  assoc f g h := by apply TypedHom.ext; rfl

def TypedHom.total {X Y : TypedRealization (G := G)} (f : TypedHom X Y) :
    X.total →ₗ[K] Y.total :=
  LinearMap.pi (fun v => (f.map v).comp (LinearMap.proj v))

@[simp] theorem TypedHom.total_apply {X Y : TypedRealization (G := G)}
    (f : TypedHom X Y) (x : X.total) (v : V) : f.total x v = f.map v (x v) := rfl

theorem TypedHom.total_single {X Y : TypedRealization (G := G)}
    (f : TypedHom X Y) (v : V) (x : X.space v) :
    f.total (Pi.single v x) = Pi.single v (f.map v x) := by
  ext w
  by_cases h : w = v
  · subst w
    simp
  · simp [Pi.single_eq_of_ne h]

theorem TypedHom.vertex_natural {X Y : TypedRealization (G := G)}
    (f : TypedHom X Y) (v : V) (x : X.total) :
    f.total (X.vertexOperator v x) = Y.vertexOperator v (f.total x) := by
  exact f.total_single v (x v)

theorem TypedHom.arrow_natural {X Y : TypedRealization (G := G)}
    (f : TypedHom X Y) (a : E) (x : X.total) :
    f.total (X.arrowOperator a x) = Y.arrowOperator a (f.total x) := by
  change f.total (Pi.single (G.target a) (X.arrow a (x (G.source a)))) =
    Pi.single (G.target a) (Y.arrow a (f.map (G.source a) (x (G.source a))))
  rw [f.total_single, f.natural]

theorem TypedHom.freeAction_natural {X Y : TypedRealization (G := G)}
    (f : TypedHom X Y) (a : Free K V E) (x : X.total) :
    f.total (X.freeAction a x) = Y.freeAction a (f.total x) := by
  induction a using FreeAlgebra.induction generalizing x with
  | grade0 c => simp
  | grade1 s =>
      cases s with
      | inl v => simpa [TypedData.freeAction] using f.vertex_natural v x
      | inr a => simpa [TypedData.freeAction] using f.arrow_natural a x
  | mul a b ha hb => simp only [map_mul, Module.End.mul_apply]; rw [ha, hb]
  | add a b ha hb => simp only [map_add, LinearMap.add_apply]; rw [ha, hb]

theorem TypedHom.action_natural {X Y : TypedRealization (G := G)}
    (f : TypedHom X Y) (a : Algebra G) (x : X.total) :
    f.total (X.collapse.action a x) = Y.collapse.action a (f.total x) := by
  obtain ⟨a, rfl⟩ := RingQuot.mkAlgHom_surjective K (Relation G) a
  change f.total (X.collapse.action (quotient G a) x) =
    Y.collapse.action (quotient G a) (f.total x)
  rw [CollapsedRealization.action_quotient, CollapsedRealization.action_quotient]
  exact f.freeAction_natural a x

/-- Collapse both the typed objects and their vertexwise morphisms. -/
abbrev collapseFunctor : TypedRealization (G := G) ⥤ ActionObject K (Algebra G) where
  obj X := ⟨ModuleCat.of K X.total, X.collapse.action⟩
  map f := ⟨f.total, f.action_natural⟩
  map_id X := by apply ActionHom.ext; rfl
  map_comp f g := by apply ActionHom.ext; rfl

instance collapse_faithful : (collapseFunctor (G := G)).Faithful where
  map_injective {X Y} f g h := by
    apply TypedHom.ext
    funext v
    apply LinearMap.ext
    intro x
    have hh := congrArg (fun q : ActionHom (collapseFunctor.obj X) (collapseFunctor.obj Y) =>
      q.linearMap (Pi.single v x) v) h
    change f.total (Pi.single v x) v = g.total (Pi.single v x) v at hh
    simpa only [TypedHom.total_apply, Pi.single_eq_same] using hh

theorem actionHom_vertex {X Y : TypedRealization (G := G)}
    (f : ActionHom (collapseFunctor.obj X) (collapseFunctor.obj Y)) (v : V) (x : X.total) :
    f.linearMap (X.vertexOperator v x) = Y.vertexOperator v (f.linearMap x) := by
  have h := f.commute (vertex G v) x
  change f.linearMap (X.collapse.action (vertex G v) x) =
    Y.collapse.action (vertex G v) (f.linearMap x) at h
  simpa only [CollapsedRealization.action_vertex] using h

theorem actionHom_arrow {X Y : TypedRealization (G := G)}
    (f : ActionHom (collapseFunctor.obj X) (collapseFunctor.obj Y)) (a : E) (x : X.total) :
    f.linearMap (X.arrowOperator a x) = Y.arrowOperator a (f.linearMap x) := by
  have h := f.commute (arrow G a) x
  change f.linearMap (X.collapse.action (arrow G a) x) =
    Y.collapse.action (arrow G a) (f.linearMap x) at h
  simpa only [CollapsedRealization.action_arrow] using h

/-- Recover each vertex map from an arbitrary algebra intertwiner. -/
def liftActionHom {X Y : TypedRealization (G := G)}
    (f : ActionHom (collapseFunctor.obj X) (collapseFunctor.obj Y)) : TypedHom X Y where
  map v := (LinearMap.proj v).comp (f.linearMap.comp (LinearMap.single K X.space v))
  natural a x := by
    have h := congrFun (actionHom_arrow f a (Pi.single (G.source a) x)) (G.target a)
    change f.linearMap (Pi.single (G.target a) (X.arrow a x)) (G.target a) =
      Y.arrow a (f.linearMap (Pi.single (G.source a) x) (G.source a))
    simpa only [TypedData.arrowOperator, LinearMap.comp_apply, LinearMap.single_apply,
      LinearMap.proj_apply, Pi.single_eq_same] using h

theorem total_liftActionHom {X Y : TypedRealization (G := G)}
    (f : ActionHom (collapseFunctor.obj X) (collapseFunctor.obj Y)) :
    (liftActionHom f).total = f.linearMap := by
  apply LinearMap.ext
  intro x
  funext v
  have h := congrFun (actionHom_vertex f v x) v
  simpa [TypedData.vertexOperator, liftActionHom] using h

instance collapse_full : (collapseFunctor (G := G)).Full where
  map_surjective f := ⟨liftActionHom f, ActionHom.ext _ _ (total_liftActionHom f)⟩

theorem CollapsedRealization.coordinates_action
    {M : Type u} [AddCommGroup M] [Module K M] (X : CollapsedRealization G M)
    (a : Algebra G) (x : M) :
    X.coordinates (X.action a x) = X.split.collapse.action a (X.coordinates x) := by
  obtain ⟨a, rfl⟩ := RingQuot.mkAlgHom_surjective K (Relation G) a
  change X.coordinates (X.action (quotient G a) x) =
    X.split.collapse.action (quotient G a) (X.coordinates x)
  rw [CollapsedRealization.action_quotient, CollapsedRealization.action_quotient]
  exact X.coordinates_freeAction a x

/-- The comparison isomorphism is the actual finite sum of vertex-range vectors. -/
def splitActionIso (X : ActionObject K (Algebra G)) :
    collapseFunctor.obj ((ofAction X.action).split) ≅ X where
  hom :=
    { linearMap := (ofAction X.action).coordinates.symm.toLinearMap
      commute a x := by
        apply (ofAction X.action).coordinates.injective
        change (ofAction X.action).coordinates
          ((ofAction X.action).coordinates.symm ((ofAction X.action).split.collapse.action a x)) =
          (ofAction X.action).coordinates (X.action a ((ofAction X.action).coordinates.symm x))
        rw [LinearEquiv.apply_symm_apply]
        have h := (ofAction X.action).coordinates_action a
          ((ofAction X.action).coordinates.symm x)
        rw [action_ofAction, LinearEquiv.apply_symm_apply] at h
        exact h.symm }
  inv :=
    { linearMap := (ofAction X.action).coordinates.toLinearMap
      commute a x := by
        have h := (ofAction X.action).coordinates_action a x
        rw [action_ofAction] at h
        exact h }
  hom_inv_id := by
    apply ActionHom.ext
    apply LinearMap.ext
    intro x
    exact (ofAction X.action).coordinates.apply_symm_apply x
  inv_hom_id := by
    apply ActionHom.ext
    apply LinearMap.ext
    intro x
    exact (ofAction X.action).coordinates.symm_apply_apply x

instance collapse_essSurj : (collapseFunctor (G := G)).EssSurj where
  mem_essImage X := ⟨(ofAction X.action).split, ⟨splitActionIso X⟩⟩

instance collapse_isEquivalence : (collapseFunctor (G := G)).IsEquivalence where

/-- The typed realization category and the constructed quotient-action category are equivalent. -/
def typedActionEquivalence : TypedRealization (G := G) ≌ ActionObject K (Algebra G) :=
  collapseFunctor.asEquivalence

/-- PSC-I-T-TYPED-MODULE-EQUIVALENCE: typed arrow realizations versus unital modules. -/
def typedModuleEquivalence : TypedRealization (G := G) ≌ ModuleCat.{u} (Algebra G) :=
  typedActionEquivalence.trans actionModuleEquivalence

end Komorebi.PaperIRelease.GrammarAlgebra
