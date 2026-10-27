import PaperX.AbsoluteFrobeniusWitnesses
import PaperX.FrobeniusChoiceIndependence
import PaperX.NumberFieldPrimeRestriction
import PaperX.NumberFieldFrobeniusRestriction
import PaperX.UnramifiedFrobeniusUniqueness
import PaperX.NumberFieldWitnessIndependence
import PaperX.RestrictionEmbeddingConjugacy
import PaperX.GeneralArithmeticCoverage
import Lean
open Lean Elab Command
run_cmd do
  let env ← getEnv
  let wanted := #[`PaperX.AbsoluteFrobeniusWitnesses, `PaperX.FrobeniusChoiceIndependence, `PaperX.NumberFieldPrimeRestriction, `PaperX.NumberFieldFrobeniusRestriction, `PaperX.UnramifiedFrobeniusUniqueness, `PaperX.NumberFieldWitnessIndependence, `PaperX.RestrictionEmbeddingConjugacy, `PaperX.GeneralArithmeticCoverage]
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let mod := env.header.moduleNames[idx.toNat]!
      if wanted.contains mod then
        let axs ← liftCoreM <| Lean.collectAxioms name
        logInfo m!"AUDIT_DECL {mod} {name} {axs}"
#check @PaperX.NumberFieldFrobeniusRestriction.exists_simultaneous_frobenius
#check @PaperX.NumberFieldWitnessIndependence.restricted_witnesses_conjugate
#check @PaperX.UnramifiedFrobeniusUniqueness.inertia_card_eq_ramificationIdx
#check @PaperX.UnramifiedFrobeniusUniqueness.finite_ramified_primes
#check @PaperX.RestrictionEmbeddingConjugacy.restriction_intertwines
#check @PaperX.GeneralArithmeticCoverage.finiteFieldCoverage_iff_cofiniteQuotientCoverage
#check @PaperX.GeneralArithmeticCoverage.existentialArithmeticCoverage_iff_arithmeticCoverage
