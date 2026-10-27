import PaperXII.ComplexBaseChange
import Mathlib.Algebra.Homology.DerivedCategory.HomologySequence
import Mathlib.Algebra.Homology.ShortComplex.ModuleCat
import Mathlib.RingTheory.Flat.FaithfullyFlat.Basic
import Mathlib.LinearAlgebra.Basis.VectorSpace

/-!
# Field extension detects cohomology and derived nonvanishing

These statements use actual cochain complexes and the localization functor to
Mathlib's derived category. Reflection is proved through faithful flatness of
a field extension; no homology comparison or nonvanishing axiom is assumed.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits
open PaperXII.ComplexBaseChange

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.ComplexFieldFibers

variable {R : Type u} [CommRing R]

/-- A derived object vanishes exactly when all its actual cohomology objects vanish. -/
theorem derived_isZero_iff_homology (D : DerivedCategory (ModuleCat.{u} R)) :
    IsZero D ↔ ∀ n : ℤ, IsZero ((DerivedCategory.homologyFunctor (ModuleCat R) n).obj D) := by
  constructor
  · intro h n
    exact (DerivedCategory.homologyFunctor (ModuleCat R) n).map_isZero h
  · intro h
    have hz : IsIso (0 : D ⟶ D) := by
      rw [DerivedCategory.isIso_iff]
      intro n
      rw [Functor.map_zero]
      exact (isIsoZero_iff_source_target_isZero _ _).mpr ⟨h n, h n⟩
    exact ((isIsoZero_iff_source_target_isZero _ _).mp hz).1

/-- Localization kills precisely the acyclic cochain complexes. -/
theorem isZero_Q_iff_acyclic (C : CochainComplex (ModuleCat.{u} R) ℤ) :
    IsZero (DerivedCategory.Q.obj C) ↔ C.Acyclic := by
  rw [derived_isZero_iff_homology, HomologicalComplex.acyclic_iff]
  apply forall_congr'
  intro n
  rw [HomologicalComplex.exactAt_iff_isZero_homology]
  exact ((DerivedCategory.homologyFunctorFactors (ModuleCat R) n).app C).isZero_iff

/-- Nonzero derived complexes have a nonzero cohomology object in some degree. -/
theorem exists_nonzero_homology_of_not_isZero
    (C : CochainComplex (ModuleCat.{u} R) ℤ) (h : ¬ IsZero (DerivedCategory.Q.obj C)) :
    ∃ n : ℤ, ¬ IsZero (C.homology n) := by
  contrapose! h
  rw [isZero_Q_iff_acyclic, HomologicalComplex.acyclic_iff]
  intro n
  exact (HomologicalComplex.exactAt_iff_isZero_homology C n).mpr (h n)

/-- A nonzero cohomology object witnesses nonvanishing in the derived category. -/
theorem not_isZero_Q_iff_exists_nonzero_homology
    (C : CochainComplex (ModuleCat.{u} R) ℤ) :
    ¬ IsZero (DerivedCategory.Q.obj C) ↔ ∃ n : ℤ, ¬ IsZero (C.homology n) := by
  constructor
  · exact exists_nonzero_homology_of_not_isZero C
  · rintro ⟨n, hn⟩ h
    exact hn (((isZero_Q_iff_acyclic C).mp h n).isZero_homology)

variable {k K : Type u} [Field k] [Field K]

/-- Extending the coefficient field preserves and reflects exactness in every degree. -/
theorem exactAt_baseChange_iff (f : k →+* K)
    (C : CochainComplex (ModuleCat.{u} k) ℤ) (n : ℤ) :
    (baseChange f C).ExactAt n ↔ C.ExactAt n := by
  let : Algebra k K := f.toAlgebra
  rw [HomologicalComplex.exactAt_iff, HomologicalComplex.exactAt_iff,
    ShortComplex.ShortExact.moduleCat_exact_iff_function_exact,
    ShortComplex.ShortExact.moduleCat_exact_iff_function_exact]
  change Function.Exact ((C.sc n).f.hom.lTensor K) ((C.sc n).g.hom.lTensor K) ↔
    Function.Exact (C.sc n).f.hom (C.sc n).g.hom
  exact Module.FaithfullyFlat.lTensor_exact_iff_exact k K _ _

/-- A field extension preserves and reflects acyclicity of arbitrary cochain complexes. -/
theorem acyclic_baseChange_iff (f : k →+* K)
    (C : CochainComplex (ModuleCat.{u} k) ℤ) :
    (baseChange f C).Acyclic ↔ C.Acyclic := by
  simp only [HomologicalComplex.acyclic_iff, exactAt_baseChange_iff]

/-- A field extension preserves and reflects zero objects after actual derived localization. -/
theorem isZero_baseChange_iff (f : k →+* K)
    (C : CochainComplex (ModuleCat.{u} k) ℤ) :
    IsZero (DerivedCategory.Q.obj (baseChange f C)) ↔ IsZero (DerivedCategory.Q.obj C) := by
  rw [isZero_Q_iff_acyclic, isZero_Q_iff_acyclic, acyclic_baseChange_iff]

/-- Derived nonvanishing survives every extension of the coefficient field. -/
theorem not_isZero_baseChange_iff (f : k →+* K)
    (C : CochainComplex (ModuleCat.{u} k) ℤ) :
    ¬ IsZero (DerivedCategory.Q.obj (baseChange f C)) ↔ ¬ IsZero (DerivedCategory.Q.obj C) :=
  not_congr (isZero_baseChange_iff f C)

/-- Each individual cohomology degree vanishes after field extension exactly when it did before. -/
theorem homology_isZero_baseChange_iff (f : k →+* K)
    (C : CochainComplex (ModuleCat.{u} k) ℤ) (n : ℤ) :
    IsZero ((baseChange f C).homology n) ↔ IsZero (C.homology n) := by
  rw [← HomologicalComplex.exactAt_iff_isZero_homology,
    ← HomologicalComplex.exactAt_iff_isZero_homology, exactAt_baseChange_iff]

end PaperXII.ComplexFieldFibers
