import PaperX.AbsoluteIntegralFrobenius
import PaperX.CyclotomicIntegralFrobenius
import PaperX.CyclotomicAbsoluteArithmeticSeparation
import Lean
open Lean Elab Command
run_cmd do
  let env ← getEnv
  let wanted := #[`PaperX.AbsoluteIntegralFrobenius, `PaperX.CyclotomicIntegralFrobenius,
    `PaperX.CyclotomicAbsoluteArithmeticSeparation]
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      let mod := env.header.moduleNames[idx.toNat]!
      if wanted.contains mod then
        let axs ← liftCoreM <| Lean.collectAxioms name
        logInfo m!"AUDIT_DECL {mod} {name} {axs}"
#check @PaperX.AbsoluteIntegralFrobenius.exists_frobenius_at
#check @PaperX.AbsoluteIntegralFrobenius.exists_frobenius
#check @PaperX.CyclotomicAbsoluteArithmeticSeparation.finite_arithmetic_system_separator
