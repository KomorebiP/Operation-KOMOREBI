import PaperICompletion5

/-! # Cyclicity of the literal intrinsic primary components
Principality is a one-element spanning statement on the actual polynomial
module. In particular it is not an assumed primary multiplicity certificate.
-/
set_option autoImplicit false
noncomputable section
open scoped Pointwise
namespace Komorebi.PaperICompletion6.PrimaryCyclicCriterion
open Polynomial
open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion.CyclicClassification
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula
universe u v
variable {k : Type u} [Field k] {V : Type v} [AddCommGroup V] [Module k V]

/-- The polynomial-module notion is exactly the original orbit notion of cyclicity. -/
theorem hasCyclicVector_iff_polynomialModule_cyclic (T : Module.End k V) :
    Komorebi.SingleOperatorGraph.HasCyclicVector T ↔ Cyclic k[X] (Module.AEval' T) := by
  rw [hasCyclicVector_iff_exists_surjective, cyclic_iff_exists_surjective_oneSeedMap]
  constructor
  · rintro ⟨x, hx⟩
    exact ⟨Module.AEval'.of T x, hx⟩
  · rintro ⟨x, hx⟩
    exact ⟨(Module.AEval'.of T).symm x, hx⟩

/-- A submodule of a cyclic polynomial module is cyclic, by principality of its preimage. -/
theorem submodule_cyclic_of_hasCyclicVector (T : Module.End k V)
    (hT : Komorebi.SingleOperatorGraph.HasCyclicVector T)
    (P : Submodule k[X] (Module.AEval' T)) : Cyclic k[X] P := by
  obtain ⟨x, hx⟩ := (hasCyclicVector_iff_exists_surjective T).mp hT
  have hp : P.IsPrincipal := Submodule.IsPrincipal.of_comap (orbitMap T x) hx P
  exact (cyclic_iff_top_isPrincipal k[X] P).mpr (Module.isPrincipal_submodule_iff.mpr hp)

/-- The literal intrinsic primary components of a cyclic operator are cyclic. -/
theorem primary_cyclic_of_hasCyclicVector (T : Module.End k V)
    (hT : Komorebi.SingleOperatorGraph.HasCyclicVector T) (p : k[X]) :
    Cyclic k[X] (primarySubmodule (Module.AEval' T) p) :=
  submodule_cyclic_of_hasCyclicVector T hT _

/-- A cyclic primary component has intrinsic residue dimension at most one. -/
theorem intrinsicMultiplicity_le_one_of_primary_cyclic (T : Module.End k V)
    (p : k[X]) (hp : Irreducible p)
    (h : Cyclic k[X] (primarySubmodule (Module.AEval' T) p)) :
    intrinsicMultiplicity T p ≤ 1 := by
  classical
  let : (Ideal.span {p}).IsMaximal := PrincipalIdealRing.isMaximal_of_irreducible hp
  let : Field (k[X] ⧸ Ideal.span {p}) := Ideal.Quotient.field _
  let P := primarySubmodule (Module.AEval' T) p
  let Q : Submodule k[X] P := p • ⊤
  obtain ⟨x, hx⟩ := h
  have hs : FamilyGenerates k[X] P (fun _ : Fin 1 => x) := by
    simpa [FamilyGenerates, Generates, Set.range_const] using hx
  have hb := residue_finrank_le_card_of_generates (K := k[X] ⧸ Ideal.span {p})
    Q.mkQ Q.mkQ_surjective (fun _ : Fin 1 => x) hs
  simpa [intrinsicMultiplicity, P, Q] using hb

/-- No nonzero-space cyclicity assertion is needed for a zero component. -/
theorem cyclic_of_subsingleton {R : Type*} [Semiring R]
    {M : Type*} [AddCommMonoid M] [Module R M] [Subsingleton M] : Cyclic R M := by
  refine ⟨0, ?_⟩
  exact Subsingleton.elim _ _

/-- The original operator is cyclic exactly when every nonzero intrinsic primary component is. -/
theorem hasCyclicVector_iff_nonzero_primary_cyclic [FiniteDimensional k V] [Nontrivial V]
    (T : Module.End k V) :
    Komorebi.SingleOperatorGraph.HasCyclicVector T ↔
      ∀ p : k[X], Irreducible p →
        Nontrivial (primarySubmodule (Module.AEval' T) p) →
        Cyclic k[X] (primarySubmodule (Module.AEval' T) p) := by
  constructor
  · intro h p _ _
    exact primary_cyclic_of_hasCyclicVector T h p
  · intro h
    have hb : ∀ p : k[X], Irreducible p → intrinsicMultiplicity T p ≤ 1 := by
      intro p hp
      apply intrinsicMultiplicity_le_one_of_primary_cyclic T p hp
      cases subsingleton_or_nontrivial (primarySubmodule (Module.AEval' T) p) with
      | inl hs => let := hs; exact cyclic_of_subsingleton
      | inr hn => exact h p hp hn
    have hm : intrinsicSeedMaximum T ≤ 1 := by
      apply csSup_le (monicPrimaryMultiplicityValues_nonempty T)
      rintro n ⟨p, _hp, hi, rfl⟩
      exact hb p hi
    have hz : intrinsicSeedMaximum T ≠ 0 := by
      intro he
      have hr : seedRank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = 0 := by
        rw [operator_seedRank_eq_intrinsicSeedMaximum, he]
        rfl
      exact not_subsingleton V ((seedRank_eq_zero_iff _ _).mp hr)
    have hr : seedRank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = 1 := by
      rw [operator_seedRank_eq_intrinsicSeedMaximum, show intrinsicSeedMaximum T = 1 by omega]
      rfl
    exact (hasCyclicVector_iff_minpoly_eq_charpoly T).mpr
      ((operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly T).mp hr)

end Komorebi.PaperICompletion6.PrimaryCyclicCriterion
