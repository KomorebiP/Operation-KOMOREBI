import PaperXI.HenselianGaloisResidue
import Mathlib.RingTheory.DedekindDomain.IntegralClosure
import Mathlib.RingTheory.Valuation.Integral
import Mathlib.RingTheory.Flat.TorsionFree

/-! Integral closure and finiteness of an invariant valuation ring. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ValuationIntegralModel
open IsLocalRing
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L)
abbrev base := A.comap (algebraMap K L)

instance baseAlgebra : Algebra (base K A) A :=
  (ValuationResidueEmbedding.inclusion A (algebraMap K L)).toAlgebra
instance baseTower : IsScalarTower (base K A) A L :=
  IsScalarTower.of_algebraMap_eq' rfl
instance baseFieldTower : IsScalarTower (base K A) K L :=
  IsScalarTower.of_algebraMap_eq' rfl
instance baseLocal : IsLocalHom (algebraMap (base K A) A) :=
  ValuationResidueEmbedding.inclusion_local A (algebraMap K L)

variable (stable : ∀ g : L ≃ₐ[K] L, g ∈ A.decompositionSubgroup K)
@[instance_reducible] def ringAction : MulSemiringAction (L ≃ₐ[K] L) A :=
  MulSemiringAction.compHom A (HenselianGaloisResidue.decompositionMap K A stable)

variable [FiniteDimensional K L] [IsGalois K L]

/-- Fixed integral elements belong to the literally restricted base valuation ring. -/
theorem invariant : letI := ringAction K A stable
    Algebra.IsInvariant (base K A) A (L ≃ₐ[K] L) := by
  let := ringAction K A stable
  constructor
  intro x hx
  have hxK : (x : L) ∈ (⊥ : IntermediateField K L) := by
    rw [IsGalois.mem_bot_iff_fixed]
    intro g
    exact congrArg (fun a : A => (a : L)) (hx g)
  obtain ⟨b, hb⟩ := IntermediateField.mem_bot.mp hxK
  have hbA : b ∈ base K A := by
    change algebraMap K L b ∈ A
    rw [hb]
    exact x.property
  exact ⟨⟨b, hbA⟩, Subtype.ext hb⟩

include stable

/-- Integrality is derived from the finite Galois action. -/
theorem integral : Algebra.IsIntegral (base K A) A := by
  let := ringAction K A stable
  let := invariant K A stable
  exact Algebra.IsInvariant.isIntegral (base K A) A (L ≃ₐ[K] L)

/-- The invariant valuation ring is the actual integral closure of its base. -/
theorem integralClosure : IsIntegralClosure A (base K A) L := by
  let := integral K A stable
  infer_instance

/-- No module-finiteness certificate is assumed: derive it from separability
and a Noetherian base valuation ring. -/
theorem finite [IsNoetherianRing (base K A)] : Module.Finite (base K A) A := by
  let := integralClosure K A stable
  exact IsIntegralClosure.finite (base K A) K L A

/-- A DVR base provides the standard integral rank comparison. -/
theorem rank [IsDiscreteValuationRing (base K A)] :
    Module.finrank (base K A) A = Module.finrank K L := by
  let := integralClosure K A stable
  exact IsIntegralClosure.rank (base K A) K L A

end PaperXI.ValuationIntegralModel
