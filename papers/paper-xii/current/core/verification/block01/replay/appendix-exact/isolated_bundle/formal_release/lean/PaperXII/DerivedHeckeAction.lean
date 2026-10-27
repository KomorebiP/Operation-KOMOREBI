import PaperXII.PerfectDerivedSupport
import PaperXII.HeckeFibers
import Mathlib.Algebra.Homology.Linear
import Mathlib.Algebra.Homology.ShortComplex.Linear

/-!
# Hecke operators on actual specialized cohomology

The operator starts as multiplication on the original cochain complex. We
extend that cochain map, localize it into the actual derived category, and
apply the actual cohomology functor. The scalar formula is proved from the
tensor relation and the natural comparison with cochain homology.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits
open scoped TensorProduct

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.DerivedHeckeAction

open ComplexBaseChange PerfectDerivedSupport

variable {T E : Type u} [CommRing T] [Field E]

/-- The original multiplication endomorphism of the whole cochain complex. -/
def cochainOperator (C : CochainComplex (ModuleCat.{u} T) ℤ) (t : T) : C ⟶ C :=
  t • 𝟙 C

/-- Extension of the original module endomorphism satisfies the tensor scalar relation. -/
theorem extendScalars_smul_id (y : T →+* E) (M : ModuleCat.{u} T) (t : T) :
    (ModuleCat.extendScalars y).map (t • 𝟙 M) =
      y t • 𝟙 ((ModuleCat.extendScalars y).obj M) := by
  let : Algebra T E := y.toAlgebra
  apply ModuleCat.hom_ext
  change HeckeFibers.heckeOperator (H := M) y t = y t • LinearMap.id
  exact HeckeFibers.heckeOperator_eq_scalar y t

/-- The specialized cochain map is proved to be scalar multiplication in every degree. -/
theorem baseChange_cochainOperator (C : CochainComplex (ModuleCat.{u} T) ℤ)
    (y : T →+* E) (t : T) :
    (complexFunctor y).map (cochainOperator C t) = y t • 𝟙 (baseChange y C) := by
  apply HomologicalComplex.Hom.ext
  funext n
  exact extendScalars_smul_id y (C.X n) t

/-- Homology of an actual cochain map preserves scalar multiplication. -/
theorem homologyMap_smul {C D : CochainComplex (ModuleCat.{u} E) ℤ}
    (f : C ⟶ D) (a : E) (n : ℤ) :
    HomologicalComplex.homologyMap (a • f) n =
      a • HomologicalComplex.homologyMap f n := by
  unfold HomologicalComplex.homologyMap
  change ShortComplex.homologyMap
    (a • (HomologicalComplex.shortComplexFunctor (ModuleCat E) (.up ℤ) n).map f) = _
  exact ShortComplex.homologyMap_smul _ _

/-- The actual derived cohomology of the specialized complex. -/
abbrev specializedCohomology (C : CochainComplex (ModuleCat.{u} T) ℤ)
    (y : T →+* E) (n : ℤ) : ModuleCat.{u} E :=
  (DerivedCategory.homologyFunctor (ModuleCat E) n).obj
    (DerivedCategory.Q.obj (baseChange y C))

/-- Apply scalar extension, derived localization, then cohomology to the original operator. -/
def cohomologyOperator (C : CochainComplex (ModuleCat.{u} T) ℤ)
    (y : T →+* E) (n : ℤ) (t : T) :
    specializedCohomology C y n ⟶ specializedCohomology C y n :=
  (DerivedCategory.homologyFunctor (ModuleCat E) n).map
    (DerivedCategory.Q.map ((complexFunctor y).map (cochainOperator C t)))

/-- The induced operator on actual derived cohomology is the prescribed scalar. -/
theorem cohomologyOperator_eq_scalar (C : CochainComplex (ModuleCat.{u} T) ℤ)
    (y : T →+* E) (n : ℤ) (t : T) :
    cohomologyOperator C y n t = y t • 𝟙 (specializedCohomology C y n) := by
  unfold cohomologyOperator
  rw [baseChange_cochainOperator]
  apply (cancel_mono ((DerivedCategory.homologyFunctorFactors (ModuleCat E) n).hom.app
    (baseChange y C))).mp
  rw [DerivedCategory.homologyFunctorFactors_hom_naturality, homologyMap_smul,
    HomologicalComplex.homologyMap_id]
  ext v
  exact map_smul ((DerivedCategory.homologyFunctorFactors (ModuleCat E) n).hom.app
    (baseChange y C)).hom (y t) v |>.symm

/-- Every actual specialized cohomology vector has the resulting common eigenvalues. -/
theorem cohomologyOperator_apply (C : CochainComplex (ModuleCat.{u} T) ℤ)
    (y : T →+* E) (n : ℤ) (t : T) (v : specializedCohomology C y n) :
    cohomologyOperator C y n t v = y t • v := by
  rw [cohomologyOperator_eq_scalar]
  rfl

/-- The same induced operator for a perfect derived object, using its projective model. -/
abbrev perfectCohomologyOperator (P : PerfectComplex T) (y : T →+* E)
    (n : ℤ) (t : T) :
    (DerivedCategory.homologyFunctor (ModuleCat E) n).obj (P.baseChange y).object ⟶
      (DerivedCategory.homologyFunctor (ModuleCat E) n).obj (P.baseChange y).object :=
  cohomologyOperator P.model.complex y n t

/-- The actual operator on a perfect derived fiber is scalar on its cohomology. -/
theorem perfectCohomologyOperator_eq_scalar (P : PerfectComplex T) (y : T →+* E)
    (n : ℤ) (t : T) :
    perfectCohomologyOperator P y n t = y t •
      𝟙 ((DerivedCategory.homologyFunctor (ModuleCat E) n).obj (P.baseChange y).object) :=
  cohomologyOperator_eq_scalar P.model.complex y n t

/-- Vector form of the perfect derived specialization formula. -/
theorem perfectCohomologyOperator_apply (P : PerfectComplex T) (y : T →+* E)
    (n : ℤ) (t : T)
    (v : (DerivedCategory.homologyFunctor (ModuleCat E) n).obj (P.baseChange y).object) :
    perfectCohomologyOperator P y n t v = y t • v :=
  cohomologyOperator_apply P.model.complex y n t v

end PaperXII.DerivedHeckeAction
