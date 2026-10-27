import PaperXII.PerfectDerivedSupport

/-!
# Cohomological range of perfect scalar specializations

The endpoints are the actual bounds of a bounded finite-projective model.
Vanishing is transported to the arbitrary represented derived object through
its model isomorphism. After any scalar extension the same endpoints bound
the actual derived cohomology. A nonzero fiber therefore contains a nonzero
cohomology vector in that interval.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.PerfectCohomology

open PerfectDerivedSupport

variable {R S : Type u} [CommRing R] [CommRing S]

/-- The actual module-valued derived cohomology of the represented object. -/
abbrev cohomology (P : PerfectComplex R) (n : ℤ) : ModuleCat.{u} R :=
  (DerivedCategory.homologyFunctor (ModuleCat R) n).obj P.object

/-- The represented derived cohomology agrees with that of its chosen model. -/
def cohomologyModelIso (P : PerfectComplex R) (n : ℤ) :
    cohomology P n ≅ P.model.complex.homology n :=
  (DerivedCategory.homologyFunctor (ModuleCat R) n).mapIso P.modelIso.symm ≪≫
    (DerivedCategory.homologyFunctorFactors (ModuleCat R) n).app P.model.complex

/-- Actual derived cohomology vanishes below the model's lower bound. -/
theorem isZero_cohomology_below (P : PerfectComplex R) (n : ℤ)
    (hn : n < P.model.lower) : IsZero (cohomology P n) :=
  (P.model.complex.isZero_of_isGE P.model.lower n hn).of_iso (cohomologyModelIso P n)

/-- Actual derived cohomology vanishes above the model's upper bound. -/
theorem isZero_cohomology_above (P : PerfectComplex R) (n : ℤ)
    (hn : P.model.upper < n) : IsZero (cohomology P n) :=
  (P.model.complex.isZero_of_isLE P.model.upper n hn).of_iso (cohomologyModelIso P n)

/-- Every nonzero actual cohomology object lies in the model's closed interval. -/
theorem cohomology_degree_bounds (P : PerfectComplex R) (n : ℤ)
    (hn : ¬IsZero (cohomology P n)) : P.model.lower ≤ n ∧ n ≤ P.model.upper := by
  constructor
  · by_contra h
    exact hn (isZero_cohomology_below P n (lt_of_not_ge h))
  · by_contra h
    exact hn (isZero_cohomology_above P n (lt_of_not_ge h))

/-- Scalar extension keeps the lower cohomological bound without a flatness assumption. -/
theorem isZero_baseChange_cohomology_below (P : PerfectComplex R) (f : R →+* S)
    (n : ℤ) (hn : n < P.model.lower) : IsZero (cohomology (P.baseChange f) n) :=
  isZero_cohomology_below (P.baseChange f) n hn

/-- Scalar extension keeps the upper cohomological bound without a flatness assumption. -/
theorem isZero_baseChange_cohomology_above (P : PerfectComplex R) (f : R →+* S)
    (n : ℤ) (hn : P.model.upper < n) : IsZero (cohomology (P.baseChange f) n) :=
  isZero_cohomology_above (P.baseChange f) n hn

/-- Every surviving specialized degree is in the original model's interval. -/
theorem baseChange_cohomology_degree_bounds (P : PerfectComplex R) (f : R →+* S)
    (n : ℤ) (hn : ¬IsZero (cohomology (P.baseChange f) n)) :
    P.model.lower ≤ n ∧ n ≤ P.model.upper :=
  cohomology_degree_bounds (P.baseChange f) n hn

/-- A nonzero module object has an actual nonzero element. -/
theorem exists_nonzero_vector (M : ModuleCat.{u} R) (h : ¬IsZero M) :
    ∃ v : M, v ≠ 0 := by
  by_contra! hv
  apply h
  rw [ModuleCat.isZero_iff_subsingleton]
  exact ⟨fun a b => (hv a).trans (hv b).symm⟩

/-- A nonzero specialized derived object has cohomology in the bounded interval. -/
theorem exists_nonzero_cohomology_in_range (P : PerfectComplex R) (f : R →+* S)
    (h : ¬IsZero (P.baseChange f).object) :
    ∃ n : ℤ, P.model.lower ≤ n ∧ n ≤ P.model.upper ∧
      ¬IsZero (cohomology (P.baseChange f) n) := by
  have hex : ∃ n : ℤ, ¬IsZero (cohomology (P.baseChange f) n) := by
    contrapose! h
    exact (ComplexFieldFibers.derived_isZero_iff_homology _).mpr h
  obtain ⟨n, hn⟩ := hex
  obtain ⟨hlo, hhi⟩ := baseChange_cohomology_degree_bounds P f n hn
  exact ⟨n, hlo, hhi, hn⟩

/-- A surviving scalar specialization gives a nonzero actual cohomology vector
in a degree bounded by the original finite-projective model. -/
theorem exists_nonzero_vector_in_range (P : PerfectComplex R) (f : R →+* S)
    (h : ¬IsZero (P.baseChange f).object) :
    ∃ (n : ℤ), P.model.lower ≤ n ∧ n ≤ P.model.upper ∧
      ∃ v : cohomology (P.baseChange f) n, v ≠ 0 := by
  obtain ⟨n, hlo, hhi, hn⟩ := exists_nonzero_cohomology_in_range P f h
  exact ⟨n, hlo, hhi, exists_nonzero_vector _ hn⟩

/-- Every field-valued point of a full-support perfect complex has such a vector. -/
theorem exists_nonzero_fiber_vector_in_range {K : Type u} [Field K]
    (P : PerfectComplex R) (x : R →+* K) (h : FullSupport P) :
    ∃ (n : ℤ), P.model.lower ≤ n ∧ n ≤ P.model.upper ∧
      ∃ v : cohomology (P.baseChange x) n, v ≠ 0 :=
  exists_nonzero_vector_in_range P x (nonzero_fiber_of_fullSupport P x h)

end PaperXII.PerfectCohomology
