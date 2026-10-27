import PaperX.CyclotomicAbsoluteSamples
import PaperX.CyclotomicAbsoluteSeparation
import PaperX.CyclotomicInertiaBridge
import Lean
open Lean Elab Command
run_cmd do
  let env ← getEnv
  let wanted := #[`PaperX.CyclotomicAbsoluteSamples, `PaperX.CyclotomicAbsoluteSeparation,
    `PaperX.CyclotomicInertiaBridge]
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let mod := env.header.moduleNames[idx.toNat]!
      if wanted.contains mod then
        let axs ← liftCoreM <| Lean.collectAxioms name
        logInfo m!"AUDIT_DECL {mod} {name} {axs}"
#check @PaperX.CyclotomicAbsoluteSeparation.finite_absolute_system_separator
#check @PaperX.CyclotomicInertiaBridge.restriction_eq_one_of_coprime_inertia
#check @PaperX.CyclotomicInertiaBridge.pullback_on_arithmeticFrobenius
