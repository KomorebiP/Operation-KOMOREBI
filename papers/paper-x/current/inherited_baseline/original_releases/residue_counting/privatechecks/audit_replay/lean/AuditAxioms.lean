import PaperX.IdealClassCharacterSum
import PaperX.IdealClassCharacterBound
import PaperX.IdealCharacterMellinMeasurable
import PaperX.IdealCharacterMellin
import PaperX.NormSignGeometry
import PaperX.IdealCharacterMellinPole
import PaperX.NormSignFormula
import PaperX.NormResidueAlgebra
import PaperX.NormResidueArithmetic
import PaperX.NormResidueIdealFilter
import PaperX.NormResidueBoundary
import PaperX.NormResidueCharacter
import PaperX.ResidueLatticeFibers
import PaperX.ResidueLatticeIdeal
import PaperX.ResidueLatticeIdealPoints
import PaperX.ResidueLatticePointSums
import PaperX.IdealNormFilterAttachment
import PaperX.NormSignArithmetic
import PaperX.NormResidueLatticeMap
import PaperX.ResidueLatticeWeights
import PaperX.IdealResidueUnitAction
import PaperX.ResidueLatticeIdealWeights
import PaperX.IdealResidueUnitActionMean
import PaperX.ResidueLatticeNormCounts
import PaperX.IdealNormWeightedAttachment
import PaperX.IdealNormCharacterBound
import PaperX.NormSignResidueCounting
import PaperX.NormResidueGeneratorAttachment
import PaperX.NormSignDilation
import PaperX.NormSignPartition
import PaperX.NormResidueWeightedCounting
import PaperX.NormResidueGeneratorSum
import PaperX.NormResidueUnitCounting
import PaperX.NormResidueCharacterCounting
import Lean.Util.CollectAxioms
open Lean Elab Command in
run_cmd do
  let targetModules : Array Name := #[`PaperX.IdealClassCharacterSum, `PaperX.IdealClassCharacterBound, `PaperX.IdealCharacterMellinMeasurable, `PaperX.IdealCharacterMellin, `PaperX.NormSignGeometry, `PaperX.IdealCharacterMellinPole, `PaperX.NormSignFormula, `PaperX.NormResidueAlgebra, `PaperX.NormResidueArithmetic, `PaperX.NormResidueIdealFilter, `PaperX.NormResidueBoundary, `PaperX.NormResidueCharacter, `PaperX.ResidueLatticeFibers, `PaperX.ResidueLatticeIdeal, `PaperX.ResidueLatticeIdealPoints, `PaperX.ResidueLatticePointSums, `PaperX.IdealNormFilterAttachment, `PaperX.NormSignArithmetic, `PaperX.NormResidueLatticeMap, `PaperX.ResidueLatticeWeights, `PaperX.IdealResidueUnitAction, `PaperX.ResidueLatticeIdealWeights, `PaperX.IdealResidueUnitActionMean, `PaperX.ResidueLatticeNormCounts, `PaperX.IdealNormWeightedAttachment, `PaperX.IdealNormCharacterBound, `PaperX.NormSignResidueCounting, `PaperX.NormResidueGeneratorAttachment, `PaperX.NormSignDilation, `PaperX.NormSignPartition, `PaperX.NormResidueWeightedCounting, `PaperX.NormResidueGeneratorSum, `PaperX.NormResidueUnitCounting, `PaperX.NormResidueCharacterCounting]
  let env ← getEnv
  let mut count : Nat := 0
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      if targetModules.contains env.header.moduleNames[idx.toNat]! then
        let axioms ← Lean.collectAxioms name
        for ax in axioms do
          unless #[`Classical.choice, `Quot.sound, `propext].contains ax do
            throwError "Unapproved axiom {ax} in {name}"
        logInfo m!"AUDIT_DECL {name}: {axioms}"
        count := count + 1
  logInfo m!"AUDIT_DECLARATION_COUNT {count}"
