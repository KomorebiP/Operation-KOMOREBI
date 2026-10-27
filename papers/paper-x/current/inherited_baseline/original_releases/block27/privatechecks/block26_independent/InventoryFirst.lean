import PaperX.AbsoluteGaloisRestriction
import PaperX.SurjectiveRepresentationPullback
import PaperX.SurjectivePullbackBoundary
import Lean
open Lean Elab Command
run_cmd do
  let env ← getEnv
  let wanted := #[`PaperX.AbsoluteGaloisRestriction, `PaperX.SurjectiveRepresentationPullback,
    `PaperX.SurjectivePullbackBoundary]
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let mod := env.header.moduleNames[idx.toNat]!
      if wanted.contains mod then
        let axs ← liftCoreM <| Lean.collectAxioms name
        logInfo m!"AUDIT_DECL {mod} {name} {axs}"
