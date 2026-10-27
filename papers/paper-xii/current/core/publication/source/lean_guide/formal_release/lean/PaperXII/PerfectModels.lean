import Mathlib.Algebra.Homology.DerivedCategory.KProjective
import Mathlib.Algebra.Category.ModuleCat.Projective
import Mathlib.Algebra.Category.ModuleCat.Abelian
import Mathlib.RingTheory.Finiteness.Basic
import Mathlib.RingTheory.TensorProduct.Finite
import PaperXII.ComplexBaseChange

/-!
# Bounded finite projective models

These models contain actual cochain complexes.  Their derived objects are formed
using Mathlib's localization at quasi-isomorphisms.  A derived isomorphism between
such models is lifted to a homotopy equivalence, rather than assumed to survive
an arbitrary extension of scalars.
-/

noncomputable section

open CategoryTheory

namespace PaperXII.PerfectModels

universe u

attribute [local instance] HasDerivedCategory.standard

/-- A bounded complex whose terms are finitely generated projective modules. -/
structure PerfectModel (R : Type u) [CommRing R] where
  complex : CochainComplex (ModuleCat.{u} R) ℤ
  lower : ℤ
  upper : ℤ
  boundedBelow : complex.IsStrictlyGE lower
  boundedAbove : complex.IsStrictlyLE upper
  finite (i : ℤ) : Module.Finite R (complex.X i)
  projective (i : ℤ) : Module.Projective R (complex.X i)

attribute [instance] PerfectModel.boundedBelow PerfectModel.boundedAbove
  PerfectModel.finite PerfectModel.projective

variable {R : Type u} [CommRing R]

/-- The object of the actual derived category represented by this model. -/
abbrev PerfectModel.derivedObject (P : PerfectModel R) : DerivedCategory (ModuleCat.{u} R) :=
  DerivedCategory.Q.obj P.complex

instance PerfectModel.isKProjective (P : PerfectModel R) : P.complex.IsKProjective :=
  CochainComplex.isKProjective_of_projective P.complex P.upper

/-- Full faithfulness on K-projective sources lifts an actual derived isomorphism
between two bounded projective models to an isomorphism in the homotopy category. -/
def homotopyCategoryIsoOfDerivedIso (P Q : PerfectModel R)
    (e : P.derivedObject ≅ Q.derivedObject) :
    (HomotopyCategory.quotient _ _).obj P.complex ≅
      (HomotopyCategory.quotient _ _).obj Q.complex := by
  let e' := (DerivedCategory.quotientCompQhIso (ModuleCat.{u} R)).app P.complex ≪≫ e ≪≫
    ((DerivedCategory.quotientCompQhIso (ModuleCat.{u} R)).app Q.complex).symm
  let hfExists := (CochainComplex.IsKProjective.Qh_map_bijective P.complex
    ((HomotopyCategory.quotient _ _).obj Q.complex)).surjective e'.hom
  let hgExists := (CochainComplex.IsKProjective.Qh_map_bijective Q.complex
    ((HomotopyCategory.quotient _ _).obj P.complex)).surjective e'.inv
  let f := Classical.choose hfExists
  let g := Classical.choose hgExists
  have hf : DerivedCategory.Qh.map f = e'.hom := Classical.choose_spec hfExists
  have hg : DerivedCategory.Qh.map g = e'.inv := Classical.choose_spec hgExists
  refine ⟨f, g, ?_, ?_⟩
  · apply (CochainComplex.IsKProjective.Qh_map_bijective P.complex
      ((HomotopyCategory.quotient _ _).obj P.complex)).injective
    simp only [Functor.map_comp, hf, hg, Iso.hom_inv_id]
    exact (DerivedCategory.Qh.map_id _).symm
  · apply (CochainComplex.IsKProjective.Qh_map_bijective Q.complex
      ((HomotopyCategory.quotient _ _).obj Q.complex)).injective
    simp only [Functor.map_comp, hf, hg, Iso.inv_hom_id]
    exact (DerivedCategory.Qh.map_id _).symm

/-- Derived-isomorphic bounded projective models are genuinely homotopy equivalent. -/
def homotopyEquivOfDerivedIso (P Q : PerfectModel R)
    (e : P.derivedObject ≅ Q.derivedObject) : HomotopyEquiv P.complex Q.complex :=
  HomotopyCategory.homotopyEquivOfIso (homotopyCategoryIsoOfDerivedIso P Q e)

/-- A homotopy equivalence gives an isomorphism of actual derived objects. -/
def derivedIsoOfHomotopyEquiv {C D : CochainComplex (ModuleCat.{u} R) ℤ}
    (e : HomotopyEquiv C D) : DerivedCategory.Q.obj C ≅ DerivedCategory.Q.obj D :=
  ((DerivedCategory.quotientCompQhIso (ModuleCat.{u} R)).app C).symm ≪≫
    DerivedCategory.Qh.mapIso (HomotopyCategory.isoOfHomotopyEquiv e) ≪≫
    (DerivedCategory.quotientCompQhIso (ModuleCat.{u} R)).app D

variable {S : Type u} [CommRing S]

/-- Finite generation survives arbitrary scalar extension. -/
theorem finite_extendScalars (f : R →+* S) (M : ModuleCat.{u} R)
    [Module.Finite R M] : Module.Finite S ((ModuleCat.extendScalars f).obj M) := by
  let : Algebra R S := f.toAlgebra
  change Module.Finite S (TensorProduct R S M)
  infer_instance

/-- Projectivity survives arbitrary scalar extension. -/
theorem projective_extendScalars (f : R →+* S) (M : ModuleCat.{u} R)
    [Module.Projective R M] : Module.Projective S ((ModuleCat.extendScalars f).obj M) := by
  let : Algebra R S := f.toAlgebra
  change Module.Projective S (TensorProduct R S M)
  infer_instance

/-- Extension of scalars preserves the entire bounded finite-projective class. -/
def PerfectModel.baseChange (P : PerfectModel R) (f : R →+* S) : PerfectModel S where
  complex := ComplexBaseChange.baseChange f P.complex
  lower := P.lower
  upper := P.upper
  boundedBelow := by dsimp [ComplexBaseChange.baseChange, ComplexBaseChange.complexFunctor]; infer_instance
  boundedAbove := by dsimp [ComplexBaseChange.baseChange, ComplexBaseChange.complexFunctor]; infer_instance
  finite i := finite_extendScalars f (P.complex.X i)
  projective i := projective_extendScalars f (P.complex.X i)

/-- Independence of the projective model after arbitrary scalar extension.
The given isomorphism is in Mathlib's actual derived category; its homotopy lift
is preserved before taking the target derived category. No flatness is assumed. -/
def baseChange_derivedIso (f : R →+* S) (P Q : PerfectModel R)
    (e : P.derivedObject ≅ Q.derivedObject) :
    (P.baseChange f).derivedObject ≅ (Q.baseChange f).derivedObject :=
  derivedIsoOfHomotopyEquiv
    (ComplexBaseChange.baseChangeHomotopyEquiv f (homotopyEquivOfDerivedIso P Q e))

end PaperXII.PerfectModels
