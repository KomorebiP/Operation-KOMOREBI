import PaperX.GeneralFrobeniusOccurrence
import PaperX.ChebotarevExternalAPIAdapter

/-! The original Paper X API instantiated by the checked general occurrence
construction. No CebotarevDensity.Main mock or density axiom is imported. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ConstructedChebotarevBridge
open NumberField
open PaperX.AbsoluteIntegralFrobenius
open PaperX.ChebotarevExternalAPIAdapter

local instance (L : FiniteGaloisIntermediateField ℚ Qbar) : NumberField L := ⟨⟩

def constructedAPI : API where
  UnramifiedIn := fun L p => Chebotarev.UnramifiedIn ℚ L p
  frobeniusClass := fun L p => Chebotarev.frobeniusClass ℚ L p
  unramified_ne_bot := fun L p h => Chebotarev.UnramifiedIn.ne_bot ℚ L h
  unramified_at := fun _ _ h P hP hOver => h.2 P hP hOver
  frobeniusClass_eq_mk_of_isArithFrobAt := fun L p hp hUnr τ P hP hτ hOver => by
    let : p.IsPrime := hp
    let : P.IsPrime := hP
    exact Chebotarev.frobeniusClass_eq_mk_of_isArithFrobAt ℚ L p hUnr τ P hτ hOver
  infinite_setOf_frobenius_class := fun L C =>
    PaperX.GeneralFrobeniusOccurrence.infinite_setOf_frobenius_class ℚ L C

theorem existentialArithmeticCoverage :
    PaperX.GeneralArithmeticCoverage.ExistentialArithmeticCoverage :=
  existentialArithmeticCoverage_of_API constructedAPI
end PaperX.ConstructedChebotarevBridge
