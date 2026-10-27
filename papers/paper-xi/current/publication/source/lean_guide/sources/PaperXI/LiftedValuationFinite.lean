import PaperXI.ValuationIntegralModel
import PaperXI.LiftedFullResidue
import Mathlib.FieldTheory.Normal.Basic

/-! The Hensel-generated field has the actual finite integral valuation ring. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LiftedValuationFinite
open scoped Pointwise
open IsLocalRing PaperXI.LiftedResidueDegree PaperXI.LiftedFullResidue
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [HenselianLocalRing A] [Fintype (ResidueField A)]
variable [FiniteDimensional K L] [IsGalois K L]
variable (stable : ∀ g : L ≃ₐ[K] L, g ∈ A.decompositionSubgroup K)
variable (s : IntermediateField (BaseResidue K A) (ResidueField A))

instance baseAlgebra : Algebra (A.comap (algebraMap K L)) (valuation K A s) := by
  change Algebra (ValuationIntegralModel.base K (valuation K A s)) (valuation K A s)
  infer_instance
instance baseTower : IsScalarTower (A.comap (algebraMap K L)) (valuation K A s) (field K A s) := by
  change IsScalarTower (ValuationIntegralModel.base K (valuation K A s)) (valuation K A s) (field K A s)
  infer_instance
instance baseFieldTower : IsScalarTower (A.comap (algebraMap K L)) K (field K A s) := by
  change IsScalarTower (ValuationIntegralModel.base K (valuation K A s)) K (field K A s)
  infer_instance
instance baseLocal : IsLocalHom (algebraMap (A.comap (algebraMap K L)) (valuation K A s)) := by
  change IsLocalHom (algebraMap (ValuationIntegralModel.base K (valuation K A s)) (valuation K A s))
  infer_instance

include stable

/-- Every automorphism of the constructed field preserves its restricted valuation.
Extend it to L; no additional valuation-invariance input for E is supplied. -/
theorem stable_valuation (σ : field K A s ≃ₐ[K] field K A s) :
    σ ∈ (valuation K A s).decompositionSubgroup K := by
  let := galois K A stable s
  rw [MulAction.mem_stabilizer_iff]
  apply ValuationSubring.ext
  intro x
  rw [ValuationSubring.mem_pointwise_smul_iff_inv_smul_mem]
  change algebraMap (field K A s) L (σ.symm x) ∈ A ↔
    algebraMap (field K A s) L x ∈ A
  let g := σ.symm.liftNormal L
  rw [← σ.symm.liftNormal_commutes L x]
  have hg : g • A = A := (MulAction.mem_stabilizer_iff).mp (stable g)
  simpa only [hg, AlgEquiv.smul_def, g] using
    (ValuationSubring.smul_mem_pointwise_smul_iff
      (g := g) (S := A) (x := algebraMap (field K A s) L x))

/-- The literal ring C=A intersect E is the integral closure of B=A intersect K. -/
theorem integralClosure : IsIntegralClosure (valuation K A s)
    (A.comap (algebraMap K L)) (field K A s) := by
  let := galois K A stable s
  exact ValuationIntegralModel.integralClosure K (valuation K A s)
    (stable_valuation K A stable s)

/-- Finiteness is proved from a Noetherian base, not assumed for C. -/
theorem finite [IsNoetherianRing (A.comap (algebraMap K L))] :
    Module.Finite (A.comap (algebraMap K L)) (valuation K A s) := by
  let := galois K A stable s
  have : IsNoetherianRing (ValuationIntegralModel.base K (valuation K A s)) := by
    change IsNoetherianRing (A.comap (algebraMap K L))
    infer_instance
  exact ValuationIntegralModel.finite K (valuation K A s)
    (stable_valuation K A stable s)

/-- The integral rank is the already derived field degree. -/
theorem rank [IsDiscreteValuationRing (A.comap (algebraMap K L))] :
    Module.finrank (A.comap (algebraMap K L)) (valuation K A s) =
      Module.finrank K (field K A s) := by
  let := galois K A stable s
  have : IsDiscreteValuationRing (ValuationIntegralModel.base K (valuation K A s)) := by
    change IsDiscreteValuationRing (A.comap (algebraMap K L))
    infer_instance
  exact ValuationIntegralModel.rank K (valuation K A s)
    (stable_valuation K A stable s)

end PaperXI.LiftedValuationFinite
