import PaperICompletion5.GeometricSeedFormula

/-! # The unconditional geometric cyclic criterion over algebraically closed fields
The nonzero-space guard is retained when cyclicity is stated as seed rank one.
The one-invariant-factor clause is represented by an actual polynomial-module
quotient equivalence, not by a supplied numerical invariant-factor count.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperICompletion5.CyclicGeometricCriterion
open Polynomial
open Komorebi.PaperICompletion5.GeometricSeedFormula
open Komorebi.PaperICompletion.CyclicClassification
open Komorebi.SeedRankBasics
open Komorebi.SingleOperatorGraph
universe u v
variable {k : Type u} [Field k]
variable {V : Type v} [AddCommGroup V] [Module k V]

/-- A spectral value has strictly positive geometric multiplicity. -/
theorem eigenspace_finrank_pos_iff_mem_spectrum [FiniteDimensional k V]
    (T : Module.End k V) (a : k) :
    0 < Module.finrank k (T.eigenspace a) ↔ a ∈ spectrum k T := by
  rw [Module.finrank_pos_iff, Submodule.nontrivial_iff_ne_bot,
    ← Module.End.hasEigenvalue_iff, Module.End.hasEigenvalue_iff_mem_spectrum]

/-- The geometric maximum cannot vanish on a nonzero space over an algebraically closed field. -/
theorem geometricSeedMaximum_pos [FiniteDimensional k V] [IsAlgClosed k]
    [Nontrivial V] (T : Module.End k V) : 0 < geometricSeedMaximum T := by
  by_contra h
  have hg : geometricSeedMaximum T = 0 := Nat.eq_zero_of_not_pos h
  have hz : seedRank (operatorAlgebra T) V = 0 := by
    rw [operator_seedRank_eq_geometricSeedMaximum, hg]
    rfl
  exact not_subsingleton V ((seedRank_eq_zero_iff (operatorAlgebra T) V).mp hz)

/-- On a nonzero space, a maximum-attaining scalar is an actual spectral value. -/
theorem spectralSeedMaximum_attained [FiniteDimensional k V] [IsAlgClosed k]
    [Nontrivial V] (T : Module.End k V) :
    ∃ a : k, a ∈ spectrum k T ∧ Module.finrank k (T.eigenspace a) = spectralSeedMaximum T := by
  obtain ⟨a, ha⟩ := geometricSeedMaximum_attained T
  refine ⟨a, ?_, ha.trans (geometricSeedMaximum_eq_spectralSeedMaximum T)⟩
  apply (eigenspace_finrank_pos_iff_mem_spectrum T a).mp
  rw [ha]
  exact geometricSeedMaximum_pos T

/-- Rank-one maximum is equivalent to multiplicity one at every actual eigenvalue. -/
theorem geometricSeedMaximum_eq_one_iff [FiniteDimensional k V] [IsAlgClosed k]
    [Nontrivial V] (T : Module.End k V) :
    geometricSeedMaximum T = 1 ↔
      ∀ a : k, a ∈ spectrum k T → Module.finrank k (T.eigenspace a) = 1 := by
  constructor
  · intro h a ha
    have hpos := (eigenspace_finrank_pos_iff_mem_spectrum T a).mpr ha
    have hle : Module.finrank k (T.eigenspace a) ≤ geometricSeedMaximum T :=
      le_csSup (geometricMultiplicityValues_bddAbove T) ⟨a, rfl⟩
    omega
  · intro h
    have hle : geometricSeedMaximum T ≤ 1 := by
      apply csSup_le (geometricMultiplicityValues_nonempty T)
      rintro n ⟨a, rfl⟩
      change Module.finrank k (T.eigenspace a) ≤ 1
      by_cases ha : a ∈ spectrum k T
      · rw [h a ha]
      · rw [eigenspace_finrank_eq_zero_of_not_mem_spectrum T a ha]
        exact Nat.zero_le _
    have hp := geometricSeedMaximum_pos T
    omega

/-- Cyclicity and the actual geometric maximum agree, with no spectral certificate. -/
theorem hasCyclicVector_iff_geometricSeedMaximum_one
    [FiniteDimensional k V] [IsAlgClosed k] [Nontrivial V] (T : Module.End k V) :
    HasCyclicVector T ↔ geometricSeedMaximum T = 1 := by
  have h := (hasCyclicVector_iff_minpoly_eq_charpoly T).trans
    (operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly T).symm
  rw [operator_seedRank_eq_geometricSeedMaximum] at h
  exact h.trans (by norm_cast)

/-- The full geometric cyclic criterion at native algebraically closed scope. -/
theorem hasCyclicVector_iff_all_spectral_multiplicities_one
    [FiniteDimensional k V] [IsAlgClosed k] [Nontrivial V] (T : Module.End k V) :
    HasCyclicVector T ↔
      ∀ a : k, a ∈ spectrum k T → Module.finrank k (T.eigenspace a) = 1 :=
  (hasCyclicVector_iff_geometricSeedMaximum_one T).trans (geometricSeedMaximum_eq_one_iff T)

/-- Polynomial equality has the same unconditional geometric characterization. -/
theorem minpoly_eq_charpoly_iff_all_spectral_multiplicities_one
    [FiniteDimensional k V] [IsAlgClosed k] [Nontrivial V] (T : Module.End k V) :
    minpoly k T = T.charpoly ↔
      ∀ a : k, a ∈ spectrum k T → Module.finrank k (T.eigenspace a) = 1 :=
  (hasCyclicVector_iff_minpoly_eq_charpoly T).symm.trans
    (hasCyclicVector_iff_all_spectral_multiplicities_one T)

/-- A cyclic operator has the actual one-factor polynomial-module presentation. -/
def cyclicMinpolyQuotientEquiv (T : Module.End k V) (x : V)
    (hx : Function.Surjective (orbitMap T x)) :
    Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {minpoly k T} :=
  ((minpolyQuotientEquivOrbit T x (orbitMap_ker_eq_annihilator_of_surjective T x hx)).trans
    (LinearEquiv.ofTop (orbitMap T x).range (LinearMap.range_eq_top.mpr hx))).symm

/-- Cyclicity constructs a one-factor presentation, rather than receiving a count certificate. -/
theorem hasCyclicVector_iff_minpoly_quotient_presentation (T : Module.End k V) :
    HasCyclicVector T ↔ Nonempty (Module.AEval' T ≃ₗ[k[X]] k[X] ⧸ Ideal.span {minpoly k T}) := by
  constructor
  · intro h
    obtain ⟨x, hx⟩ := (hasCyclicVector_iff_exists_surjective T).mp h
    exact ⟨cyclicMinpolyQuotientEquiv T x hx⟩
  · rintro ⟨e⟩
    let z : Module.AEval' T := e.symm (Ideal.Quotient.mk _ 1)
    apply (hasCyclicVector_iff_exists_surjective T).mpr
    refine ⟨(Module.AEval'.of T).symm z, ?_⟩
    intro y
    obtain ⟨p, hp⟩ := Ideal.Quotient.mk_surjective (e y)
    refine ⟨p, ?_⟩
    apply e.injective
    change e (p • z) = e y
    rw [e.map_smul]
    simp only [z, e.apply_symm_apply, Algebra.smul_def, mul_one]
    exact hp

end Komorebi.PaperICompletion5.CyclicGeometricCriterion
