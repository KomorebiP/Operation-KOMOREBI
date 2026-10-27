import PaperIRelease.GrammarEquivalence
import Mathlib.RingTheory.TwoSidedIdeal.Basic
import Mathlib.Algebra.Category.ModuleCat.ChangeOfRings

/-!
Literal two-sided-ideal specialization.  The path algebra uses its standard
vertex/arrow presentation.  The final algebra is identified with the quotient
of that algebra by an arbitrary two-sided ideal, with the comparison maps and
their inverse identities proved from the quotient universal properties.
-/

set_option autoImplicit false
set_option maxHeartbeats 4000000
set_option linter.unusedVariables false
set_option linter.unnecessarySimpa false
set_option linter.unusedSimpArgs false

noncomputable section

namespace Komorebi.PaperIRelease.GrammarAlgebra

open CategoryTheory
universe u
variable {K V E : Type u} [Field K] [Fintype V]

def freeGrammar (s t : E → V) : Grammar K V E where
  source := s
  target := t
  equations := fun _ _ => False

/-- The finite-vertex path algebra, in its standard generators-and-relations presentation. -/
abbrev PathAlgebra (s t : E → V) := Algebra (freeGrammar (K := K) s t)

variable (s t : E → V)
variable (I : TwoSidedIdeal (PathAlgebra (K := K) s t))

/-- All representatives of ideal relations are imposed in the free presentation. -/
def idealGrammar : Grammar K V E where
  source := s
  target := t
  equations x y := I.ringCon (quotient (freeGrammar s t) x) (quotient (freeGrammar s t) y)

abbrev IdealQuotient := RingQuot (fun x y : PathAlgebra (K := K) s t => I.ringCon x y)

def idealQuotientMap : PathAlgebra (K := K) s t →ₐ[K] IdealQuotient s t I :=
  RingQuot.mkAlgHom K _

def freeToIdeal : Free K V E →ₐ[K] IdealQuotient s t I :=
  (idealQuotientMap s t I).comp (quotient (freeGrammar s t))

theorem freeToIdeal_respects {x y : Free K V E} (h : Relation (idealGrammar s t I) x y) :
    freeToIdeal s t I x = freeToIdeal s t I y := by
  cases h with
  | vertex_idempotent v =>
      exact congrArg (idealQuotientMap s t I)
        (RingQuot.mkAlgHom_rel K (Relation.vertex_idempotent (G := freeGrammar s t) v))
  | vertex_orthogonal v w h =>
      exact congrArg (idealQuotientMap s t I)
        (RingQuot.mkAlgHom_rel K (Relation.vertex_orthogonal (G := freeGrammar s t) v w h))
  | vertex_complete =>
      exact congrArg (idealQuotientMap s t I)
        (RingQuot.mkAlgHom_rel K (Relation.vertex_complete (G := freeGrammar s t)))
  | arrow_corner a =>
      exact congrArg (idealQuotientMap s t I)
        (RingQuot.mkAlgHom_rel K (Relation.arrow_corner (G := freeGrammar s t) a))
  | declared h =>
      exact RingQuot.mkAlgHom_rel K (s := fun x y : PathAlgebra (K := K) s t => I.ringCon x y) h

def presentedToIdeal : Algebra (idealGrammar s t I) →ₐ[K] IdealQuotient s t I :=
  RingQuot.liftAlgHom K ⟨freeToIdeal s t I, fun _ _ h => freeToIdeal_respects s t I h⟩

@[simp] theorem presentedToIdeal_quotient (x : Free K V E) :
    presentedToIdeal s t I (quotient (idealGrammar s t I) x) = freeToIdeal s t I x :=
  RingQuot.liftAlgHom_mkAlgHom_apply K _ _ x

theorem base_respects {x y : Free K V E} (h : Relation (freeGrammar s t) x y) :
    quotient (idealGrammar s t I) x = quotient (idealGrammar s t I) y := by
  apply RingQuot.mkAlgHom_rel
  cases h with
  | vertex_idempotent v => exact Relation.vertex_idempotent v
  | vertex_orthogonal v w h => exact Relation.vertex_orthogonal v w h
  | vertex_complete => exact Relation.vertex_complete
  | arrow_corner a => exact Relation.arrow_corner a
  | declared h => exact h.elim

def baseToPresented : PathAlgebra (K := K) s t →ₐ[K] Algebra (idealGrammar s t I) :=
  RingQuot.liftAlgHom K ⟨quotient (idealGrammar s t I), fun _ _ h => base_respects s t I h⟩

@[simp] theorem baseToPresented_quotient (x : Free K V E) :
    baseToPresented s t I (quotient (freeGrammar s t) x) = quotient (idealGrammar s t I) x :=
  RingQuot.liftAlgHom_mkAlgHom_apply K _ _ x

theorem baseToPresented_respects {x y : PathAlgebra (K := K) s t} (h : I.ringCon x y) :
    baseToPresented s t I x = baseToPresented s t I y := by
  obtain ⟨x, rfl⟩ := RingQuot.mkAlgHom_surjective K (Relation (freeGrammar s t)) x
  obtain ⟨y, rfl⟩ := RingQuot.mkAlgHom_surjective K (Relation (freeGrammar s t)) y
  change baseToPresented s t I (quotient (freeGrammar s t) x) =
    baseToPresented s t I (quotient (freeGrammar s t) y)
  rw [baseToPresented_quotient, baseToPresented_quotient]
  exact declared_relation (idealGrammar s t I) h

def idealToPresented : IdealQuotient s t I →ₐ[K] Algebra (idealGrammar s t I) :=
  RingQuot.liftAlgHom K ⟨baseToPresented s t I, fun _ _ h => baseToPresented_respects s t I h⟩

@[simp] theorem idealToPresented_quotient (x : PathAlgebra (K := K) s t) :
    idealToPresented s t I (idealQuotientMap s t I x) = baseToPresented s t I x :=
  RingQuot.liftAlgHom_mkAlgHom_apply K _ _ x

/-- The iterated quotient and the single generator presentation are actually isomorphic. -/
def idealPresentationEquiv : Algebra (idealGrammar s t I) ≃ₐ[K] IdealQuotient s t I :=
  AlgEquiv.ofAlgHom (presentedToIdeal s t I) (idealToPresented s t I)
    (by
      apply RingQuot.ringQuot_ext'
      apply RingQuot.ringQuot_ext'
      apply AlgHom.ext
      intro x
      change presentedToIdeal s t I
        (idealToPresented s t I (idealQuotientMap s t I (quotient (freeGrammar s t) x))) =
        idealQuotientMap s t I (quotient (freeGrammar s t) x)
      rw [idealToPresented_quotient, baseToPresented_quotient, presentedToIdeal_quotient]
      rfl)
    (by
      apply RingQuot.ringQuot_ext'
      apply AlgHom.ext
      intro x
      change idealToPresented s t I (presentedToIdeal s t I (quotient (idealGrammar s t I) x)) =
        quotient (idealGrammar s t I) x
      rw [presentedToIdeal_quotient]
      change idealToPresented s t I (idealQuotientMap s t I (quotient (freeGrammar s t) x)) = _
      rw [idealToPresented_quotient, baseToPresented_quotient])

/-- The manuscript's actual quotient by a two-sided ideal, with a genuine module category target. -/
def typedIdealModuleEquivalence :
    TypedRealization (G := idealGrammar s t I) ≌ ModuleCat.{u} (IdealQuotient s t I) :=
  typedModuleEquivalence.trans
    (ModuleCat.restrictScalarsEquivalenceOfRingEquiv (idealPresentationEquiv s t I).symm.toRingEquiv)

end Komorebi.PaperIRelease.GrammarAlgebra
