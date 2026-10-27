import LeanChecker

/-
Invoke the pinned official LeanChecker.replayFromImports function for exactly
one module. Unlike the tool's prefix-scanning CLI, this wrapper cannot start
concurrent replays of descendants or of the entire search path.
This is same-kernel replay against cached imports, not an external verifier.
-/
#eval (show IO Unit from do
  let some target ← IO.getEnv "KOMOREBI_REPLAY_MODULE"
    | throw <| IO.userError "KOMOREBI_REPLAY_MODULE must name exactly one module"
  let module := target.toName
  if module.isAnonymous then
    throw <| IO.userError "Empty module name is not a replay target"
  IO.println s!"REPLAY_EXACT_BEGIN {module}"
  replayFromImports module
  IO.println s!"REPLAY_EXACT_PASS {module}"
)
