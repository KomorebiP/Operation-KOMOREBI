import AVOC.RobustQuoteExamples
open Lean Elab Command
run_cmd do
  let env ← getEnv
  for (name, info) in env.constants.toList do
    if name.toString.startsWith "_private.AVOC.RobustQuoteExamples" then
      if let .thmInfo _ := info then
        logInfo m!"{name}"
