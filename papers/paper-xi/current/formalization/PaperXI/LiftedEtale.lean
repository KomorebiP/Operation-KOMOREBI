import PaperXI.LiftedValuationFinite
import PaperXI.LocalResidueRank

/-! Actual finite-etale and ramification-index endpoints for the Hensel-generated
field over a DVR base. All ring/module properties are derived. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LiftedEtale
open IsLocalRing PaperXI.LiftedResidueDegree PaperXI.LiftedFullResidue
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [HenselianLocalRing A] [Fintype (ResidueField A)]
variable [FiniteDimensional K L] [IsGalois K L]
variable (stable : ∀ g : L ≃ₐ[K] L, g ∈ A.decompositionSubgroup K)
variable (s : IntermediateField (BaseResidue K A) (ResidueField A))
variable [IsDiscreteValuationRing (A.comap (algebraMap K L))]

include stable

/-- Construct a finite free integral valuation ring over the actual DVR base. -/
theorem free : Module.Free (A.comap (algebraMap K L)) (valuation K A s) := by
  let := galois K A stable s
  let := LiftedValuationFinite.integralClosure K A stable s
  exact IsIntegralClosure.module_free (A.comap (algebraMap K L)) K
    (field K A s) (valuation K A s)

/-- Full residue equivalence for the canonical quotient module action.
This explicitly resolves the residue-module versus algebra-module typeclass path. -/
def canonicalResidueLinearEquiv :
    ResidueField (valuation K A s) ≃ₗ[BaseResidue K A] s :=
  { (residueEquiv K A s stable).toAddEquiv with
    map_smul' := fun a x => by
      obtain ⟨a, rfl⟩ := residue_surjective a
      obtain ⟨x, rfl⟩ := residue_surjective x
      apply Subtype.ext
      rfl }

/-- Field degree and full residue degree exhaust the integral rank. -/
theorem rank_residue :
    Module.finrank (A.comap (algebraMap K L)) (valuation K A s) =
      Module.finrank (BaseResidue K A) (ResidueField (valuation K A s)) := by
  rw [(canonicalResidueLinearEquiv K A stable s).finrank_eq]
  exact (LiftedValuationFinite.rank K A stable s).trans (degree K A stable s)

/-- The actual maximal ideal is the extension of the base maximal ideal. -/
theorem maximalIdeal_map :
    (maximalIdeal (A.comap (algebraMap K L))).map
      (algebraMap (A.comap (algebraMap K L)) (valuation K A s)) =
    maximalIdeal (valuation K A s) := by
  let := LiftedValuationFinite.finite K A stable s
  let := free K A stable s
  exact LocalResidueRank.map_maximal_of_rank _ _ (rank_residue K A stable s)

/-- Algebra.Etale is instantiated on the actual restricted valuation rings. -/
theorem etale : Algebra.Etale (A.comap (algebraMap K L)) (valuation K A s) := by
  let := LiftedValuationFinite.finite K A stable s
  let := free K A stable s
  have : Finite (BaseResidue K A) := Finite.of_injective
    (ValuationResidueEmbedding.residueMap A (algebraMap K L))
    (ValuationResidueEmbedding.residueMap_injective A (algebraMap K L))
  let : Algebra.FinitePresentation (A.comap (algebraMap K L)) (valuation K A s) :=
    Algebra.FinitePresentation.of_finiteType.mp inferInstance
  exact LocalResidueRank.etale _ _ (rank_residue K A stable s)

/-- The library ramification index, not a new predicate with that name. -/
theorem ramificationIdx_one :
    (maximalIdeal (valuation K A s)).ramificationIdx
      (A.comap (algebraMap K L)) = 1 := by
  let := etale K A stable s
  exact Ideal.ramificationIdx_eq_one _ _

/-- Every chosen generator of the base maximal ideal remains a generator upstairs. -/
theorem uniformizer_ideal (π : A.comap (algebraMap K L))
    (hπ : Ideal.span {π} = maximalIdeal (A.comap (algebraMap K L))) :
    Ideal.span {algebraMap (A.comap (algebraMap K L)) (valuation K A s) π} =
      maximalIdeal (valuation K A s) := by
  rw [← maximalIdeal_map K A stable s, ← hπ, Ideal.map_span, Set.image_singleton]

/-- A genuine monogenic finite-etale presentation exists; its derivative is a unit.
The generator and polynomial are derived, not passed in as certificates. -/
theorem monogenic : ∃ β : valuation K A s,
    Algebra.adjoin (A.comap (algebraMap K L)) {β} = ⊤ ∧
    IsUnit (Polynomial.aeval β (minpoly (A.comap (algebraMap K L)) β).derivative) := by
  let := LiftedValuationFinite.finite K A stable s
  let := etale K A stable s
  have : FaithfulSMul (A.comap (algebraMap K L)) (valuation K A s) :=
    (faithfulSMul_iff_algebraMap_injective _ _).mpr
      (by
        intro x y h
        apply Subtype.ext
        exact (algebraMap K (field K A s)).injective (congrArg (fun a : valuation K A s => (a : field K A s)) h))
  obtain ⟨β, hβ⟩ := IsLocalRing.exists_adjoin_eq_top
    (R := A.comap (algebraMap K L)) (S := valuation K A s)
  exact ⟨β, hβ, IsLocalRing.isUnit_aeval_derivative_minpoly_of_adjoin_eq_top hβ⟩

end PaperXI.LiftedEtale
