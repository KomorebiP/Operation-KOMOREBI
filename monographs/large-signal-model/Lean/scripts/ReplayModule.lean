import LeanChecker

/-! Call the pinned upstream replay function directly. This is verification
infrastructure, never imported by the theorem library. No theorem is added.
The general CLI scans all dependency directories, which is unnecessary here. -/
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  let some moduleName ← IO.getEnv "KOMOREBI_REPLAY_MODULE"
    | throw <| IO.userError "KOMOREBI_REPLAY_MODULE is required"
  replayFromImports moduleName.toName
  IO.println s!"KERNEL_REPLAY_PASS {moduleName}"
