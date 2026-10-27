import Mathlib.Algebra.Category.ModuleCat.ChangeOfRings
import Mathlib.Algebra.Category.ModuleCat.Abelian
import Mathlib.Algebra.Homology.Homotopy

/-!
# Scalar extension of actual cochain complexes

The functor below applies module scalar extension in every degree. Its
composition isomorphism is induced by the module tensor associator, including
its compatibility with the differentials. For a projective complex this is
the model used for derived scalar extension in `PerfectModels`.
-/

noncomputable section

open CategoryTheory

universe u

namespace PaperXII.ComplexBaseChange

variable {R S T : Type u} [CommRing R] [CommRing S] [CommRing T]

/-- Tensor extension is additive on module morphisms. -/
instance extendScalarsAdditive (f : R →+* S) :
    (ModuleCat.extendScalars.{u, u, u} f).Additive := by
  let := Limits.preservesBinaryBiproducts_of_preservesBinaryCoproducts
    (ModuleCat.extendScalars.{u, u, u} f)
  exact Functor.additive_of_preservesBinaryBiproducts (ModuleCat.extendScalars.{u, u, u} f)

/-- Degreewise tensor extension, with the induced differentials. -/
abbrev complexFunctor (f : R →+* S) :
    CochainComplex (ModuleCat.{u} R) ℤ ⥤ CochainComplex (ModuleCat.{u} S) ℤ :=
  (ModuleCat.extendScalars f).mapHomologicalComplex (.up ℤ)

/-- The actual specialized cochain complex. -/
abbrev baseChange (f : R →+* S) (K : CochainComplex (ModuleCat.{u} R) ℤ) :=
  (complexFunctor f).obj K

/-- The module in degree `n` is the scalar extension of that degree. -/
theorem baseChange_X (f : R →+* S) (K : CochainComplex (ModuleCat.{u} R) ℤ) (n : ℤ) :
    (baseChange f K).X n = (ModuleCat.extendScalars f).obj (K.X n) := rfl

/-- The specialized differential is obtained from the original differential. -/
theorem baseChange_d (f : R →+* S) (K : CochainComplex (ModuleCat.{u} R) ℤ) (i j : ℤ) :
    (baseChange f K).d i j = (ModuleCat.extendScalars f).map (K.d i j) := rfl

/-- Scalar extension by a composite agrees with successive scalar extensions. -/
def complexFunctorCompIso (f : R →+* S) (g : S →+* T) :
    complexFunctor f ⋙ complexFunctor g ≅ complexFunctor (g.comp f) :=
  Functor.mapHomologicalComplexCompIso (ModuleCat.extendScalarsComp f g).symm (.up ℤ)

/-- The actual tensor association isomorphism, including all differentials. -/
def baseChangeCompIso (f : R →+* S) (g : S →+* T)
    (K : CochainComplex (ModuleCat.{u} R) ℤ) :
    baseChange g (baseChange f K) ≅ baseChange (g.comp f) K :=
  (complexFunctorCompIso f g).app K

/-- The tensor association isomorphism commutes with every cochain map. -/
theorem baseChangeCompIso_naturality (f : R →+* S) (g : S →+* T)
    {K L : CochainComplex (ModuleCat.{u} R) ℤ} (φ : K ⟶ L) :
    (complexFunctor g).map ((complexFunctor f).map φ) ≫
      (baseChangeCompIso f g L).hom =
    (baseChangeCompIso f g K).hom ≫ (complexFunctor (g.comp f)).map φ :=
  (complexFunctorCompIso f g).hom.naturality φ

/-- Scalar extension by the identity recovers the original complex. -/
def baseChangeIdIso (K : CochainComplex (ModuleCat.{u} R) ℤ) :
    baseChange (RingHom.id R) K ≅ K :=
  ((NatIso.mapHomologicalComplex (ModuleCat.extendScalarsId R) (.up ℤ)) ≪≫
    Functor.mapHomologicalComplexIdIso (ModuleCat.{u} R) (.up ℤ)).app K

/-- Every module scalar extension preserves a supplied cochain homotopy. -/
def baseChangeHomotopy (f : R →+* S)
    {K L : CochainComplex (ModuleCat.{u} R) ℤ} {φ ψ : K ⟶ L}
    (h : Homotopy φ ψ) :
    Homotopy ((complexFunctor f).map φ) ((complexFunctor f).map ψ) :=
  (ModuleCat.extendScalars f).mapHomotopy h

/-- Arbitrary scalar extension preserves homotopy equivalence, without flatness. -/
def baseChangeHomotopyEquiv (f : R →+* S)
    {K L : CochainComplex (ModuleCat.{u} R) ℤ} (h : HomotopyEquiv K L) :
    HomotopyEquiv (baseChange f K) (baseChange f L) :=
  (ModuleCat.extendScalars f).mapHomotopyEquiv h

end PaperXII.ComplexBaseChange
